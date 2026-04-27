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
    "timeout_penalty",
    "angle_diff",
    "action_rate_penalty",
    "load_equalization",
)


def compute_reward_terms(
    cfg,
    commands: torch.Tensor,
    previous_goal_distance: torch.Tensor,
    episode_length_buf: torch.Tensor,
    max_episode_length: int,
    actions: torch.Tensor,
    previous_actions: torch.Tensor,
    wheel_longitudinal_slip: torch.Tensor,
    wheel_slip_angle: torch.Tensor,
    wheel_normal_contact_force: torch.Tensor,
    waypoint_hit_mask: torch.Tensor,
    time_out_mask: torch.Tensor,
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
    progress_delta = previous_goal_distance - current_goal_distance
    progress_delta = torch.clamp(
        progress_delta,
        min=-params.progress_to_target_clip_m,
        max=params.progress_to_target_clip_m,
    )
    if params.progress_to_target_relax_radius_m > 0.0:
        near_goal_mask = current_goal_distance <= params.progress_to_target_relax_radius_m
        progress_delta = torch.where(near_goal_mask, torch.clamp(progress_delta, min=0.0), progress_delta)
    goal_distance_f = max(float(cfg.commands.goal_distance), 1.0e-6)
    positive_progress = torch.clamp(progress_delta, min=0.0) / goal_distance_f
    negative_progress = torch.clamp(progress_delta, max=0.0) / goal_distance_f
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
    progress_gate = torch.minimum(longitudinal_gate, slip_angle_gate)
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
    timeout_remaining_distance = time_out_mask.float() * current_goal_distance
    timeout_penalty = -time_out_mask.float() * (
        params.timeout_fixed_penalty
        + params.timeout_distance_penalty_scale * current_goal_distance
    )
    angle_diff = (
        (1.0 / (1.0 + torch.abs(goal_heading_error)))
        / max_episode_length_f
    )
    action_delta = actions - previous_actions
    base_action_delta_cost = torch.mean(torch.square(action_delta[:, :2]), dim=1)
    if action_delta.shape[1] > 2:
        joint_action_delta_cost = torch.mean(torch.square(action_delta[:, 2:]), dim=1)
    else:
        joint_action_delta_cost = torch.zeros_like(base_action_delta_cost)
    action_rate_penalty = -(
        params.action_rate_base_weight * base_action_delta_cost
        + params.action_rate_joint_weight * joint_action_delta_cost
    ) / max_episode_length_f
    load_total = torch.sum(wheel_normal_contact_force, dim=1, keepdim=True)
    load_shares = wheel_normal_contact_force / torch.clamp(load_total, min=1.0e-6)
    load_targets = wheel_normal_contact_force.new_tensor(params.load_equalization_target_shares)
    if load_targets.numel() != wheel_normal_contact_force.shape[1]:
        raise ValueError(
            "Reward load-equalization target shares must match the number of wheel contact-force terms."
        )
    load_targets = load_targets / torch.clamp(torch.sum(load_targets), min=1.0e-6)
    load_equalization_error = torch.sum(torch.square(load_shares - load_targets.unsqueeze(0)), dim=1)
    load_equalization_raw = torch.exp(
        -max(float(params.load_equalization_k), 0.0) * load_equalization_error
    )
    # Convert the uniformity score into a penalty magnitude:
    # uniform loads -> 0, uneven loads -> 1.
    load_equalization = (1.0 - load_equalization_raw) / max_episode_length_f

    components = {
        "distance_to_target": distance_to_target * params.distance_to_target_weight,
        "progress_to_target": progress_to_target * params.progress_to_target_weight,
        "reached_target": reached_target * params.reached_target_weight,
        "far_from_target": far_from_target * params.far_from_target_weight,
        "timeout_penalty": timeout_penalty,
        "angle_diff": angle_diff * params.angle_diff_weight,
        "action_rate_penalty": action_rate_penalty,
        "load_equalization": load_equalization * params.load_equalization_weight,
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
        "timeout_remaining_distance": timeout_remaining_distance,
        "action_rate_base_cost": base_action_delta_cost,
        "action_rate_joint_cost": joint_action_delta_cost,
        "load_equalization_error": load_equalization_error,
        "load_equalization_raw": load_equalization_raw,
    }
    return total_reward, components, diagnostics
