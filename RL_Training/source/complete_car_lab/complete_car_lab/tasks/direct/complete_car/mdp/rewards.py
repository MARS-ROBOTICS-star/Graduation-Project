"""奖励项计算。"""

from __future__ import annotations

import torch

from ..utils.math_utils import quaternion_to_rpy, wrap_to_pi_tensor


REWARD_TERM_NAMES = (
    "tracking_lin_vel",
    "tracking_ang_vel",
    "tracking_heading",
    "orientation",
    "lin_vel_z",
    "ang_vel_xy",
    "ball_joint_deviation",
    "ball_joint_swing",
    "action_rate",
    "termination",
)


def compute_tracking_terms(cfg, robot, commands: torch.Tensor) -> dict[str, torch.Tensor]:
    base_lin_vel = robot.data.root_com_lin_vel_b
    base_ang_vel = robot.data.root_com_ang_vel_b
    yaw = quaternion_to_rpy(robot.data.root_link_quat_w)[:, 2]

    lin_vel_error = torch.sum(torch.square(commands[:, :2] - base_lin_vel[:, :2]), dim=1)
    tracking_lin_vel = torch.exp(-lin_vel_error / max(cfg.rewards.tracking_lin_vel_std**2, 1.0e-6))

    yaw_rate_error = torch.square(commands[:, 2] - base_ang_vel[:, 2])
    tracking_ang_vel = torch.exp(-yaw_rate_error / max(cfg.rewards.tracking_ang_vel_std**2, 1.0e-6))

    heading_error = wrap_to_pi_tensor(commands[:, 3] - yaw)
    tracking_heading = torch.exp(-torch.square(heading_error) / max(cfg.rewards.tracking_heading_std**2, 1.0e-6))
    return {
        "tracking_lin_vel": tracking_lin_vel,
        "tracking_ang_vel": tracking_ang_vel,
        "tracking_heading": tracking_heading,
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

    base_lin_vel = robot.data.root_com_lin_vel_b
    base_ang_vel = robot.data.root_com_ang_vel_b
    projected_gravity = robot.data.projected_gravity_b
    ball_joint_pos = wrap_to_pi_tensor(robot.data.joint_pos[:, ball_joint_ids])
    ball_joint_vel = robot.data.joint_vel[:, ball_joint_ids]

    tracking_terms = compute_tracking_terms(cfg, robot, commands)
    orientation = torch.sum(torch.square(projected_gravity[:, :2]), dim=1)
    lin_vel_z = torch.square(base_lin_vel[:, 2])
    ang_vel_xy = torch.sum(torch.square(base_ang_vel[:, :2]), dim=1)
    ball_joint_deviation = torch.sum(torch.square(ball_joint_pos - cfg.rewards.ball_joint_target), dim=1)
    ball_joint_swing = torch.sum(torch.abs(ball_joint_vel), dim=1)
    action_rate = torch.sum(torch.square(actions - last_actions), dim=1)
    termination = reset_terminated.float()

    components = {
        "tracking_lin_vel": scales.tracking_lin_vel * tracking_terms["tracking_lin_vel"],
        "tracking_ang_vel": scales.tracking_ang_vel * tracking_terms["tracking_ang_vel"],
        "tracking_heading": scales.tracking_heading * tracking_terms["tracking_heading"],
        "orientation": scales.orientation * orientation,
        "lin_vel_z": scales.lin_vel_z * lin_vel_z,
        "ang_vel_xy": scales.ang_vel_xy * ang_vel_xy,
        "ball_joint_deviation": scales.ball_joint_deviation * ball_joint_deviation,
        "ball_joint_swing": scales.ball_joint_swing * ball_joint_swing,
        "action_rate": scales.action_rate * action_rate,
        "termination": scales.termination * termination,
    }
    total_reward = torch.stack(tuple(components.values()), dim=0).sum(dim=0)
    if cfg.rewards.only_positive_rewards:
        total_reward = torch.clamp(total_reward, min=0.0)
    return total_reward, components
