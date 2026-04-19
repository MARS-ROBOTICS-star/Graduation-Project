"""目标导向奖励项计算。"""

from __future__ import annotations

import math

import torch

from ..utils.math_utils import wrap_to_pi_tensor

REWARD_TERM_NAMES = (
    "distance_progress",
    "goal_direction_reward",
    "goal_heading_reward",
    "stop_reward",
    "near_goal_gate",
    "success_bonus",
    "time_penalty",
)


def compute_reward_terms(
    cfg,
    commands: torch.Tensor,
    previous_goal_distance: torch.Tensor,
    raw_obs_terms: dict[str, torch.Tensor],
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    params = cfg.rewards.params
    current_goal_distance = torch.linalg.vector_norm(commands[:, :2], dim=1)
    goal_yaw_error = wrap_to_pi_tensor(commands[:, 2])
    goal_direction_error = wrap_to_pi_tensor(torch.atan2(commands[:, 1], commands[:, 0]))
    planar_speed_sq = torch.sum(torch.square(raw_obs_terms["base_lin_vel"][:, :2]), dim=1)

    goal_reached = (
        (current_goal_distance < params.target_position_tolerance)
        & (torch.abs(goal_yaw_error) < math.radians(params.target_yaw_tolerance_deg))
    )

    distance_progress = (previous_goal_distance - current_goal_distance) / cfg.control.control_dt
    near_goal_gate = torch.sigmoid(
        params.near_goal_gate_sharpness * (params.near_goal_gate_distance - current_goal_distance)
    )
    stop_gate = torch.sigmoid(
        params.near_goal_gate_sharpness * (params.stop_gate_distance - current_goal_distance)
    )
    safe_goal_direction_scale = max(params.goal_direction_error_scale, 1.0e-6)
    safe_goal_heading_scale = max(params.goal_heading_error_scale, 1.0e-6)
    safe_stop_speed_scale = max(params.stop_speed_squared_scale, 1.0e-6)
    safe_stop_speed_scale_sq = safe_stop_speed_scale * safe_stop_speed_scale
    goal_direction_reward = params.goal_direction_reward_weight * torch.exp(
        -torch.abs(goal_direction_error) / safe_goal_direction_scale
    )
    goal_heading_reward = params.goal_heading_reward_weight * near_goal_gate * torch.exp(
        -torch.abs(goal_yaw_error) / safe_goal_heading_scale
    )
    stop_reward = params.stop_reward_weight * stop_gate * torch.exp(
        -planar_speed_sq / safe_stop_speed_scale_sq
    )
    success_bonus = goal_reached.float() * params.success_bonus
    time_penalty = torch.full_like(distance_progress, params.time_penalty)

    components = {
        "distance_progress": distance_progress,
        "goal_direction_reward": goal_direction_reward,
        "goal_heading_reward": goal_heading_reward,
        "stop_reward": stop_reward,
        "near_goal_gate": near_goal_gate,
        "success_bonus": success_bonus,
        "time_penalty": time_penalty,
    }
    total_reward = (
        distance_progress
        + goal_direction_reward
        + goal_heading_reward
        + stop_reward
        + success_bonus
        - time_penalty
    )
    if cfg.rewards.only_positive_rewards:
        total_reward = torch.clamp(total_reward, min=0.0)
    return total_reward, components
