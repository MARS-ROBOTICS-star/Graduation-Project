"""奖励项计算。"""

from __future__ import annotations

import torch

from ..utils.math_utils import wrap_to_pi_tensor

REWARD_TERM_NAMES = (
    "tracking_lin_vel",
    "tracking_ang_vel",
    "orientation",
    "action_rate",
    "ball_joint_limit_soft",
    "termination",
)


def compute_tracking_terms(cfg, robot, commands: torch.Tensor) -> dict[str, torch.Tensor]:
    base_lin_vel = robot.data.root_com_lin_vel_b
    base_ang_vel = robot.data.root_com_ang_vel_b

    lin_vel_error = torch.square(commands[:, 0] - base_lin_vel[:, 0])
    tracking_lin_vel = torch.exp(-lin_vel_error / max(cfg.rewards.tracking_lin_vel_std**2, 1.0e-6))

    yaw_rate_error = torch.square(commands[:, 1] - base_ang_vel[:, 2])
    tracking_ang_vel = torch.exp(-yaw_rate_error / max(cfg.rewards.tracking_ang_vel_std**2, 1.0e-6))
    return {
        "tracking_lin_vel": tracking_lin_vel,
        "tracking_ang_vel": tracking_ang_vel,
    }


def compute_ball_joint_limit_soft_penalty(cfg, robot, ball_joint_ids) -> torch.Tensor:
    """Penalize only the last margin near the configured hard joint limits.

    The penalty stays at zero in the safe zone and rises smoothly only when a joint
    uses more than ``ball_joint_limit_soft_start_ratio`` of its available range from
    the default pose toward either the lower or upper hard limit.
    """

    ball_joint_pos = wrap_to_pi_tensor(robot.data.joint_pos[:, ball_joint_ids])
    default_joint_pos = robot.data.default_joint_pos[:, ball_joint_ids]

    lower_limits = ball_joint_pos.new_tensor(cfg.terminations.ball_joint_pos_lower_limits).unsqueeze(0)
    upper_limits = ball_joint_pos.new_tensor(cfg.terminations.ball_joint_pos_upper_limits).unsqueeze(0)

    positive_span = torch.clamp(upper_limits - default_joint_pos, min=1.0e-6)
    negative_span = torch.clamp(default_joint_pos - lower_limits, min=1.0e-6)

    positive_utilization = torch.clamp((ball_joint_pos - default_joint_pos) / positive_span, min=0.0)
    negative_utilization = torch.clamp((default_joint_pos - ball_joint_pos) / negative_span, min=0.0)
    utilization = positive_utilization + negative_utilization

    start_ratio = cfg.rewards.ball_joint_limit_soft_start_ratio
    active_margin = max(1.0 - start_ratio, 1.0e-6)
    normalized_overuse = torch.clamp((utilization - start_ratio) / active_margin, min=0.0)
    return torch.mean(normalized_overuse.pow(cfg.rewards.ball_joint_limit_soft_power), dim=1)


def compute_reward_terms(
    cfg,
    robot,
    ball_joint_ids,
    commands: torch.Tensor,
    actions: torch.Tensor,
    last_actions: torch.Tensor,
    reset_terminated: torch.Tensor,
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    scales = cfg.rewards.scales

    projected_gravity = robot.data.projected_gravity_b

    tracking_terms = compute_tracking_terms(cfg, robot, commands)
    orientation = torch.sum(torch.square(projected_gravity[:, :2]), dim=1)
    action_rate = torch.sum(torch.square(actions - last_actions), dim=1)
    ball_joint_limit_soft = compute_ball_joint_limit_soft_penalty(cfg, robot, ball_joint_ids)
    termination = reset_terminated.float()

    components = {
        "tracking_lin_vel": scales.tracking_lin_vel * tracking_terms["tracking_lin_vel"],
        "tracking_ang_vel": scales.tracking_ang_vel * tracking_terms["tracking_ang_vel"],
        "orientation": scales.orientation * orientation,
        "action_rate": scales.action_rate * action_rate,
        "ball_joint_limit_soft": scales.ball_joint_limit_soft * ball_joint_limit_soft,
        "termination": scales.termination * termination,
    }
    total_reward = torch.stack(tuple(components.values()), dim=0).sum(dim=0)
    if cfg.rewards.only_positive_rewards:
        total_reward = torch.clamp(total_reward, min=0.0)
    return total_reward, components
