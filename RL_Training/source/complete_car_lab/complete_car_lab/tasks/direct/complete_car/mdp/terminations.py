"""终止条件计算。"""

from __future__ import annotations

import torch

from ..utils.math_utils import wrap_to_pi_tensor


def compute_done_terms(
    cfg,
    robot,
    commands: torch.Tensor,
    active_waypoint_index: torch.Tensor,
    ball_joint_ids,
    episode_length_buf: torch.Tensor,
    max_episode_length: int,
) -> dict[str, torch.Tensor]:
    ball_joint_pos = wrap_to_pi_tensor(robot.data.joint_pos[:, ball_joint_ids])
    current_goal_distance = torch.linalg.vector_norm(commands[:, :2], dim=1)
    waypoint_hit = current_goal_distance < cfg.rewards.params.target_position_tolerance
    last_waypoint_index = max(int(getattr(cfg.commands, "num_waypoints_per_episode", 1)) - 1, 0)
    is_success = waypoint_hit & (active_waypoint_index >= last_waypoint_index)
    time_out = (episode_length_buf >= max_episode_length - 1) & ~is_success
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
    far_from_target = current_goal_distance > (
        cfg.commands.goal_distance + cfg.rewards.params.far_from_target_margin
    )

    return {
        "waypoint_hit": waypoint_hit,
        "is_success": is_success,
        "far_from_target": far_from_target,
        "ball_joint_out_of_bounds": ball_joint_out_of_bounds,
        "time_out": time_out,
    }


def compute_dones(
    cfg,
    robot,
    commands: torch.Tensor,
    active_waypoint_index: torch.Tensor,
    ball_joint_ids,
    episode_length_buf: torch.Tensor,
    max_episode_length: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    done_terms = compute_done_terms(
        cfg,
        robot,
        commands,
        active_waypoint_index,
        ball_joint_ids,
        episode_length_buf,
        max_episode_length,
    )
    terminated = (
        done_terms["is_success"]
        | done_terms["far_from_target"]
        | done_terms["ball_joint_out_of_bounds"]
    )
    return terminated, done_terms["time_out"]
