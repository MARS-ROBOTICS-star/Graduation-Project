"""终止条件计算。"""

from __future__ import annotations

import torch

from ..utils.math_utils import wrap_to_pi_tensor


def compute_done_terms(
    cfg,
    robot,
    ball_joint_ids,
    episode_length_buf: torch.Tensor,
    max_episode_length: int,
) -> dict[str, torch.Tensor]:
    projected_gravity = robot.data.projected_gravity_b
    ball_joint_pos = wrap_to_pi_tensor(robot.data.joint_pos[:, ball_joint_ids])

    time_out = episode_length_buf >= max_episode_length - 1
    tilt_angle = torch.acos(torch.clamp(-projected_gravity[:, 2], -1.0, 1.0))
    bad_orientation = tilt_angle > torch.deg2rad(
        torch.full_like(tilt_angle, cfg.terminations.orientation_limit_deg, dtype=torch.float)
    )
    lower_limits = ball_joint_pos.new_tensor(cfg.terminations.ball_joint_pos_lower_limits)
    upper_limits = ball_joint_pos.new_tensor(cfg.terminations.ball_joint_pos_upper_limits)
    if lower_limits.numel() != ball_joint_pos.shape[1] or upper_limits.numel() != ball_joint_pos.shape[1]:
        raise ValueError(
            "Termination ball-joint limit dimensions do not match the number of controlled ball joints."
        )
    ball_joint_out_of_bounds = torch.any(
        (ball_joint_pos < lower_limits) | (ball_joint_pos > upper_limits),
        dim=1,
    )

    root_too_low = torch.zeros_like(time_out)
    if cfg.terminations.minimum_root_height is not None:
        root_too_low = robot.data.root_link_pos_w[:, 2] < cfg.terminations.minimum_root_height

    return {
        "bad_orientation": bad_orientation,
        "ball_joint_out_of_bounds": ball_joint_out_of_bounds,
        "root_too_low": root_too_low,
        "time_out": time_out,
    }


def compute_dones(cfg, robot, ball_joint_ids, episode_length_buf: torch.Tensor, max_episode_length: int) -> tuple[torch.Tensor, torch.Tensor]:
    done_terms = compute_done_terms(cfg, robot, ball_joint_ids, episode_length_buf, max_episode_length)
    terminated = (
        done_terms["bad_orientation"]
        | done_terms["ball_joint_out_of_bounds"]
        | done_terms["root_too_low"]
    )
    return terminated, done_terms["time_out"]
