"""终止条件计算。"""

from __future__ import annotations

import torch

from ..utils.math_utils import quaternion_to_rpy, wrap_to_pi_tensor


def compute_done_terms(
    cfg,
    robot,
    commands: torch.Tensor,
    ball_joint_ids,
    head_car_body_id: int,
    tail_car_body_id: int,
    episode_length_buf: torch.Tensor,
    max_episode_length: int,
) -> dict[str, torch.Tensor]:
    ball_joint_pos = wrap_to_pi_tensor(robot.data.joint_pos[:, ball_joint_ids])
    current_goal_distance = torch.linalg.vector_norm(commands[:, :2], dim=1)
    goal_yaw_error = wrap_to_pi_tensor(commands[:, 2])
    middle_roll = quaternion_to_rpy(robot.data.root_link_quat_w)[:, 0]
    head_rpy = quaternion_to_rpy(robot.data.body_quat_w[:, head_car_body_id])
    tail_rpy = quaternion_to_rpy(robot.data.body_quat_w[:, tail_car_body_id])
    head_roll = head_rpy[:, 0]
    tail_roll = tail_rpy[:, 0]
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
    goal_reached = (
        (current_goal_distance < cfg.rewards.params.target_position_tolerance)
        & (torch.abs(goal_yaw_error) < torch.deg2rad(goal_yaw_error.new_full(goal_yaw_error.shape, cfg.rewards.params.target_yaw_tolerance_deg)))
    )

    return {
        "goal_reached": goal_reached,
        "bad_orientation": bad_orientation,
        "head_tail_roll_out_of_bounds": head_tail_roll_out_of_bounds,
        "ball_joint_out_of_bounds": ball_joint_out_of_bounds,
        "time_out": time_out,
    }


def compute_dones(
    cfg,
    robot,
    commands: torch.Tensor,
    ball_joint_ids,
    head_car_body_id: int,
    tail_car_body_id: int,
    episode_length_buf: torch.Tensor,
    max_episode_length: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    done_terms = compute_done_terms(
        cfg,
        robot,
        commands,
        ball_joint_ids,
        head_car_body_id,
        tail_car_body_id,
        episode_length_buf,
        max_episode_length,
    )
    terminated = (
        done_terms["goal_reached"]
        | done_terms["bad_orientation"]
        | done_terms["head_tail_roll_out_of_bounds"]
        | done_terms["ball_joint_out_of_bounds"]
    )
    return terminated, done_terms["time_out"]
