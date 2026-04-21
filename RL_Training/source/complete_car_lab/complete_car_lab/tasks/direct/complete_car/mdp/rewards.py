"""目标导向奖励项计算。"""

from __future__ import annotations

import math

import torch

from ..utils.math_utils import wrap_to_pi_tensor

REWARD_TERM_NAMES = (
    "distance_to_target",
    "reached_target",
    "angle_to_target",
    "far_from_target",
    "angle_diff",
)


def compute_reward_terms(
    cfg,
    commands: torch.Tensor,
    episode_length_buf: torch.Tensor,
    max_episode_length: int,
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    params = cfg.rewards.params
    max_episode_length_f = float(max(max_episode_length, 1))
    current_goal_distance = torch.linalg.vector_norm(commands[:, :2], dim=1)
    goal_heading_error = wrap_to_pi_tensor(commands[:, 3])
    angle_to_target = torch.atan2(commands[:, 1], commands[:, 0])
    reward_scale = (max_episode_length_f - episode_length_buf.float()) / max_episode_length_f

    reached_target_mask = (
        (current_goal_distance < params.target_position_tolerance)
        & (torch.abs(goal_heading_error) < math.radians(params.target_yaw_tolerance_deg))
    )

    distance_to_target = (
        1.0
        / (1.0 + params.distance_to_target_denominator_scale * torch.square(current_goal_distance))
        / max_episode_length_f
    )
    reached_target = reached_target_mask.float() * params.reached_target_base_reward * reward_scale
    angle_to_target_penalty = torch.where(
        torch.abs(angle_to_target) > params.angle_to_target_threshold_rad,
        torch.abs(angle_to_target) / max_episode_length_f,
        torch.zeros_like(angle_to_target),
    )
    far_from_target_threshold = cfg.commands.goal_distance + params.far_from_target_margin
    far_from_target = torch.where(
        current_goal_distance > far_from_target_threshold,
        torch.ones_like(current_goal_distance),
        torch.zeros_like(current_goal_distance),
    )
    angle_diff = (
        (1.0 / (1.0 + current_goal_distance))
        * (1.0 / (1.0 + torch.abs(goal_heading_error)))
        / max_episode_length_f
    )

    components = {
        "distance_to_target": distance_to_target * params.distance_to_target_weight,
        "reached_target": reached_target * params.reached_target_weight,
        "angle_to_target": angle_to_target_penalty * params.angle_to_target_weight,
        "far_from_target": far_from_target * params.far_from_target_weight,
        "angle_diff": angle_diff * params.angle_diff_weight,
    }
    total_reward = sum(components.values())
    if cfg.rewards.only_positive_rewards:
        total_reward = torch.clamp(total_reward, min=0.0)
    return total_reward, components
