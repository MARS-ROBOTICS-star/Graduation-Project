"""终止条件计算。"""

from __future__ import annotations

import torch

from ..utils.math_utils import quaternion_to_rpy, wrap_to_pi_tensor


def compute_done_terms(
    cfg,
    robot,
    ball_joint_ids,
    head_car_body_id: int,
    tail_car_body_id: int,
    episode_length_buf: torch.Tensor,
    max_episode_length: int,
    success_hold_steps: torch.Tensor,
) -> dict[str, torch.Tensor]:
    ball_joint_pos = wrap_to_pi_tensor(robot.data.joint_pos[:, ball_joint_ids])
    middle_roll = quaternion_to_rpy(robot.data.root_link_quat_w)[:, 0]
    head_roll = quaternion_to_rpy(robot.data.body_quat_w[:, head_car_body_id])[:, 0]
    tail_roll = quaternion_to_rpy(robot.data.body_quat_w[:, tail_car_body_id])[:, 0]
    base_lin_vel = robot.data.root_com_lin_vel_b[:, :2]
    planar_speed = torch.linalg.vector_norm(base_lin_vel, dim=1)
    yaw_rate_abs = torch.abs(robot.data.root_com_ang_vel_b[:, 2])

    time_out = episode_length_buf >= max_episode_length - 1
    middle_roll_abs = torch.abs(middle_roll)
    bad_orientation = middle_roll_abs > torch.deg2rad(
        torch.full_like(middle_roll_abs, cfg.terminations.orientation_limit_deg, dtype=torch.float)
    )
    head_tail_roll_limit_rad = torch.deg2rad(
        torch.full_like(middle_roll_abs, cfg.terminations.head_tail_roll_limit_deg, dtype=torch.float)
    )
    head_tail_roll_out_of_bounds = (torch.abs(head_roll) > head_tail_roll_limit_rad) | (
        torch.abs(tail_roll) > head_tail_roll_limit_rad
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
    success = (
        success_hold_steps >= max(int(cfg.terminations.success_dwell_steps), 1)
    ) & (
        planar_speed < cfg.terminations.success_planar_speed_tolerance
    ) & (
        yaw_rate_abs < cfg.terminations.success_yaw_rate_tolerance
    )

    return {
        "bad_orientation": bad_orientation,
        "head_tail_roll_out_of_bounds": head_tail_roll_out_of_bounds,
        "ball_joint_out_of_bounds": ball_joint_out_of_bounds,
        "success": success,
        "time_out": time_out,
    }


def compute_dones(
    cfg,
    robot,
    ball_joint_ids,
    head_car_body_id: int,
    tail_car_body_id: int,
    episode_length_buf: torch.Tensor,
    max_episode_length: int,
    success_hold_steps: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    done_terms = compute_done_terms(
        cfg,
        robot,
        ball_joint_ids,
        head_car_body_id,
        tail_car_body_id,
        episode_length_buf,
        max_episode_length,
        success_hold_steps,
    )
    terminated = (
        done_terms["bad_orientation"]
        | done_terms["head_tail_roll_out_of_bounds"]
        | done_terms["ball_joint_out_of_bounds"]
        | done_terms["success"]
    )
    return terminated, done_terms["time_out"]
