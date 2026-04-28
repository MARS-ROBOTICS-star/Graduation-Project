"""目标导向奖励项计算。"""

from __future__ import annotations

import math

import torch

from ..utils.math_utils import wrap_to_pi_tensor

REWARD_TERM_NAMES = (
    "distance_to_target",
    "progress_to_target",
    "reached_target",
    "far_from_target",
    "angle_diff",
    "turn_speed_penalty",
    "slip_penalty",
)


def compute_reward_terms(
    cfg,
    commands: torch.Tensor,
    previous_goal_distance: torch.Tensor,
    episode_length_buf: torch.Tensor,
    max_episode_length: int,
    base_lin_vel_b: torch.Tensor,
    wheel_longitudinal_slip: torch.Tensor,
    wheel_slip_angle: torch.Tensor,
    waypoint_hit_mask: torch.Tensor,
) -> tuple[torch.Tensor, dict[str, torch.Tensor], dict[str, torch.Tensor]]:
    params = cfg.rewards.params
    max_episode_length_f = float(max(max_episode_length, 1))
    current_goal_distance = torch.linalg.vector_norm(commands[:, :2], dim=1)
    goal_heading_error = wrap_to_pi_tensor(commands[:, 3])
    reward_scale = (max_episode_length_f - episode_length_buf.float()) / max_episode_length_f

    distance_to_target = (
        1.0
        / (1.0 + params.distance_to_target_denominator_scale * torch.square(current_goal_distance))
        / max_episode_length_f
    )
    progress_delta = torch.clamp(
        previous_goal_distance - current_goal_distance,
        min=-params.progress_to_target_clip_m,
        max=params.progress_to_target_clip_m,
    )
    if params.progress_to_target_relax_radius_m > 0.0:
        near_goal_mask = current_goal_distance <= params.progress_to_target_relax_radius_m
        progress_delta = torch.where(near_goal_mask, torch.clamp(progress_delta, min=0.0), progress_delta)
    goal_distance_f = max(float(cfg.commands.goal_distance), 1.0e-6)
    positive_progress = torch.clamp(progress_delta, min=0.0) / goal_distance_f
    negative_progress = torch.clamp(progress_delta, max=0.0) / goal_distance_f
    mean_longitudinal_slip = torch.mean(torch.abs(wheel_longitudinal_slip), dim=1)
    longitudinal_gate = torch.exp(
        -0.5
        * torch.sum(
            torch.square(wheel_longitudinal_slip / max(float(params.progress_gate_longitudinal_k), 1.0e-6)),
            dim=1,
        )
    )
    slip_angle_phase = torch.clamp(
        math.pi * torch.abs(wheel_slip_angle) / max(float(params.progress_gate_slip_angle_scale_rad), 1.0e-6),
        min=0.0,
        max=math.pi,
    )
    slip_angle_gate = torch.prod(0.5 * torch.cos(slip_angle_phase) + 0.5, dim=1)
    progress_gate = 0.5 * (longitudinal_gate + slip_angle_gate)
    progress_multiplier = (
        params.progress_gate_min_multiplier
        + (params.progress_gate_max_multiplier - params.progress_gate_min_multiplier) * progress_gate
    )
    ungated_progress_to_target = positive_progress + negative_progress
    progress_to_target = progress_multiplier * positive_progress + negative_progress
    reached_target = waypoint_hit_mask.float() * params.reached_target_base_reward * reward_scale
    far_from_target_threshold = cfg.commands.goal_distance + params.far_from_target_margin
    far_from_target = torch.where(
        current_goal_distance > far_from_target_threshold,
        torch.ones_like(current_goal_distance),
        torch.zeros_like(current_goal_distance),
    )
    angle_diff = (
        (1.0 / (1.0 + torch.abs(goal_heading_error)))
        / max_episode_length_f
    )
    turn_angle_scale = max(math.radians(cfg.commands.goal_direction_max_deg), 1.0e-6)
    turn_intensity = torch.clamp(torch.abs(goal_heading_error) / turn_angle_scale, min=0.0, max=1.0)
    planar_speed = torch.linalg.vector_norm(base_lin_vel_b[:, :2], dim=1)
    normalized_planar_speed = planar_speed / max(float(cfg.control.base_forward_velocity_max), 1.0e-6)
    turn_speed_penalty = turn_intensity * normalized_planar_speed / max_episode_length_f
    slip_penalty = (
        mean_longitudinal_slip + params.slip_angle_penalty_ratio * torch.mean(torch.abs(wheel_slip_angle), dim=1)
    ) / max_episode_length_f

    components = {
        "distance_to_target": distance_to_target * params.distance_to_target_weight,
        "progress_to_target": progress_to_target * params.progress_to_target_weight,
        "reached_target": reached_target * params.reached_target_weight,
        "far_from_target": far_from_target * params.far_from_target_weight,
        "angle_diff": angle_diff * params.angle_diff_weight,
        "turn_speed_penalty": turn_speed_penalty * params.turn_speed_penalty_weight,
        "slip_penalty": slip_penalty * params.slip_penalty_weight,
    }
    total_reward = sum(components.values())
    if cfg.rewards.only_positive_rewards:
        total_reward = torch.clamp(total_reward, min=0.0)
    diagnostics = {
        "progress_ungated": ungated_progress_to_target,
        "progress_positive": positive_progress,
        "progress_negative": negative_progress,
        "progress_longitudinal_gate": longitudinal_gate,
        "progress_slip_angle_gate": slip_angle_gate,
        "progress_gate": progress_gate,
        "progress_multiplier": progress_multiplier,
    }
    return total_reward, components, diagnostics
