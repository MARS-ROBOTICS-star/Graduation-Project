"""终止条件计算。"""

from __future__ import annotations

import torch

from ..utils.math_utils import wrap_to_pi_tensor


def compute_dones(cfg, robot, ball_joint_ids, episode_length_buf: torch.Tensor, max_episode_length: int) -> tuple[torch.Tensor, torch.Tensor]:
    projected_gravity = robot.data.projected_gravity_b
    ball_joint_pos = wrap_to_pi_tensor(robot.data.joint_pos[:, ball_joint_ids])

    time_out = episode_length_buf >= max_episode_length - 1
    tilt_angle = torch.acos(torch.clamp(-projected_gravity[:, 2], -1.0, 1.0))
    bad_orientation = tilt_angle > torch.deg2rad(
        torch.full_like(tilt_angle, cfg.terminations.orientation_limit_deg, dtype=torch.float)
    )
    ball_joint_out_of_bounds = torch.any(
        torch.abs(ball_joint_pos) > cfg.terminations.soft_ball_joint_pos_limit,
        dim=1,
    )

    root_too_low = torch.zeros_like(time_out)
    if cfg.terminations.minimum_root_height is not None:
        root_too_low = robot.data.root_link_pos_w[:, 2] < cfg.terminations.minimum_root_height

    return bad_orientation | ball_joint_out_of_bounds | root_too_low, time_out
