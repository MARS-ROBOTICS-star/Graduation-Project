"""奖励项计算。"""

from __future__ import annotations

import torch

REWARD_TERM_NAMES = (
    "tracking_lin_vel",
    "tracking_ang_vel",
    "orientation",
    "action_rate",
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
    termination = reset_terminated.float()

    components = {
        "tracking_lin_vel": scales.tracking_lin_vel * tracking_terms["tracking_lin_vel"],
        "tracking_ang_vel": scales.tracking_ang_vel * tracking_terms["tracking_ang_vel"],
        "orientation": scales.orientation * orientation,
        "action_rate": scales.action_rate * action_rate,
        "termination": scales.termination * termination,
    }
    total_reward = torch.stack(tuple(components.values()), dim=0).sum(dim=0)
    if cfg.rewards.only_positive_rewards:
        total_reward = torch.clamp(total_reward, min=0.0)
    return total_reward, components
