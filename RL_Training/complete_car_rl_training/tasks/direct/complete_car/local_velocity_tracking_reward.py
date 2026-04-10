"""Project-local velocity tracking reward kernels for complete-car direct tasks."""

from __future__ import annotations

import torch

from .utils import quaternion_to_rpy, wrap_to_pi_tensor


def compute_velocity_tracking_terms(cfg, robot, commands: torch.Tensor) -> dict[str, torch.Tensor]:
    """Compute the command-tracking reward terms from project-local kernels."""

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


__all__ = ["compute_velocity_tracking_terms"]
