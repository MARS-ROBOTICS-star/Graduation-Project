"""目标导向奖励项计算。"""

from __future__ import annotations

import math

import torch

from ..utils.math_utils import wrap_to_pi_tensor

REWARD_TERM_NAMES = (
    "target_bonus",
    "progress",
    "heading_gate",
    "gated_progress",
)


def _compute_target_bonus_value(cfg) -> float:
    progress_horizon = cfg.commands.goal_distance / max(cfg.control.control_dt, 1.0e-6)
    ratio = cfg.rewards.params.target_bonus_ratio
    return progress_horizon * ratio / max(1.0 - ratio, 1.0e-6)


def compute_reward_terms(
    cfg,
    robot,
    commands: torch.Tensor,
    previous_goal_distance: torch.Tensor,
    raw_obs_terms: dict[str, torch.Tensor],
    processed_actions: torch.Tensor,
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    params = cfg.rewards.params
    current_goal_distance = torch.linalg.vector_norm(commands[:, :2], dim=1)
    goal_yaw_error = wrap_to_pi_tensor(commands[:, 2])

    goal_reached = (
        (current_goal_distance < params.target_position_tolerance)
        & (torch.abs(goal_yaw_error) < math.radians(params.target_yaw_tolerance_deg))
    )
    target_bonus = goal_reached.float() * _compute_target_bonus_value(cfg)

    control_frequency = 1.0 / max(cfg.control.control_dt, 1.0e-6)
    progress = (previous_goal_distance - current_goal_distance) * control_frequency

    heading_denominator = torch.clamp(
        current_goal_distance / max(params.heading_distance_scale, 1.0e-6),
        min=1.0e-6,
    )
    heading_gate = torch.exp(-0.5 * torch.square(goal_yaw_error / heading_denominator))
    gated_progress = progress * heading_gate

    components = {
        "target_bonus": target_bonus,
        "progress": progress,
        "heading_gate": heading_gate,
        "gated_progress": gated_progress,
    }
    total_reward = target_bonus + gated_progress
    if cfg.rewards.only_positive_rewards:
        total_reward = torch.clamp(total_reward, min=0.0)
    return total_reward, components
