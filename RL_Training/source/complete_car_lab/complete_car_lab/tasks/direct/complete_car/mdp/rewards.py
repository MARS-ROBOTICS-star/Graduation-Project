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
    "action_rate_penalty",
    "contact_support_penalty",
    "edge_speed_penalty",
)


def _finite_tensor(value: torch.Tensor) -> torch.Tensor:
    return torch.nan_to_num(value, nan=0.0, posinf=0.0, neginf=0.0)


def get_nominal_goal_distance(cfg) -> float:
    """Return the reward/termination distance scale without tying Stage1 to waypoint sampling fields."""

    value = float(getattr(cfg.rewards.params, "nominal_goal_distance_m", 0.0))
    if value > 0.0:
        return value
    return float(cfg.commands.goal_distance)


def get_turn_speed_angle_scale_rad(cfg) -> float:
    """Return the turn-speed penalty angle scale.

    Negative values preserve the legacy behavior of reading the command sampler's
    free-waypoint direction range.
    """

    value = float(getattr(cfg.rewards.params, "turn_speed_angle_scale_deg", -1.0))
    if value >= 0.0:
        return math.radians(value)
    return math.radians(cfg.commands.goal_direction_max_deg)


def compute_reward_terms(
    cfg,
    commands: torch.Tensor,
    previous_goal_distance: torch.Tensor,
    episode_length_buf: torch.Tensor,
    max_episode_length: int,
    actions: torch.Tensor,
    last_actions: torch.Tensor,
    base_lin_vel_b: torch.Tensor,
    wheel_longitudinal_slip: torch.Tensor,
    wheel_slip_angle: torch.Tensor,
    wheel_contact_weights: torch.Tensor,
    edge_strength: torch.Tensor,
    edge_height_jump: torch.Tensor,
    waypoint_hit_mask: torch.Tensor,
) -> tuple[torch.Tensor, dict[str, torch.Tensor], dict[str, torch.Tensor]]:
    params = cfg.rewards.params
    commands = _finite_tensor(commands)
    previous_goal_distance = _finite_tensor(previous_goal_distance)
    episode_length_buf = _finite_tensor(episode_length_buf.float())
    actions = _finite_tensor(actions)
    last_actions = _finite_tensor(last_actions)
    base_lin_vel_b = _finite_tensor(base_lin_vel_b)
    wheel_longitudinal_slip = _finite_tensor(wheel_longitudinal_slip)
    wheel_slip_angle = _finite_tensor(wheel_slip_angle)
    wheel_contact_weights = torch.clamp(_finite_tensor(wheel_contact_weights), min=0.0, max=1.0)
    edge_strength = torch.clamp(_finite_tensor(edge_strength), min=0.0, max=1.0)
    edge_height_jump = torch.clamp(_finite_tensor(edge_height_jump), min=0.0)
    max_episode_length_f = float(max(max_episode_length, 1))
    current_goal_distance = torch.linalg.vector_norm(commands[:, :2], dim=1)
    goal_heading_error = wrap_to_pi_tensor(commands[:, 3])
    reward_scale = (max_episode_length_f - episode_length_buf) / max_episode_length_f

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
    goal_distance_f = max(get_nominal_goal_distance(cfg), 1.0e-6)
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
    progress_gate = 0.5 * (longitudinal_gate + slip_angle_gate)
    progress_multiplier = (
        params.progress_gate_min_multiplier
        + (params.progress_gate_max_multiplier - params.progress_gate_min_multiplier) * progress_gate
    )
    ungated_progress_to_target = positive_progress + negative_progress
    progress_to_target = progress_multiplier * positive_progress + negative_progress
    reached_target = waypoint_hit_mask.float() * params.reached_target_base_reward * reward_scale
    far_from_target_threshold = goal_distance_f + params.far_from_target_margin
    far_from_target = torch.where(
        current_goal_distance > far_from_target_threshold,
        torch.ones_like(current_goal_distance),
        torch.zeros_like(current_goal_distance),
    )
    angle_diff = (
        (1.0 / (1.0 + torch.abs(goal_heading_error)))
        / max_episode_length_f
    )
    turn_angle_scale = max(get_turn_speed_angle_scale_rad(cfg), 1.0e-6)
    turn_intensity = torch.clamp(torch.abs(goal_heading_error) / turn_angle_scale, min=0.0, max=1.0)
    planar_speed = torch.linalg.vector_norm(base_lin_vel_b[:, :2], dim=1)
    normalized_planar_speed = planar_speed / max(float(cfg.control.base_forward_velocity_max), 1.0e-6)
    turn_speed_penalty = turn_intensity * normalized_planar_speed / max_episode_length_f
    contact_weight_sum = torch.clamp(torch.sum(wheel_contact_weights, dim=1), min=1.0)
    masked_longitudinal_slip = (
        torch.sum(wheel_contact_weights * torch.abs(wheel_longitudinal_slip), dim=1) / contact_weight_sum
    )
    masked_slip_angle = torch.sum(wheel_contact_weights * torch.abs(wheel_slip_angle), dim=1) / contact_weight_sum
    slip_penalty = (
        params.slip_longitudinal_penalty_ratio * masked_longitudinal_slip
        + params.slip_angle_penalty_ratio * masked_slip_angle
    ) / max_episode_length_f
    if actions.shape[1] > 0:
        action_delta = actions - last_actions
        action_weights = torch.full_like(action_delta, float(params.action_rate_joint_ratio))
        base_action_dim = min(action_delta.shape[1], 2)
        if base_action_dim > 0:
            action_weights[:, :base_action_dim] = float(params.action_rate_base_ratio)
        action_rate_penalty = torch.mean(action_weights * torch.square(action_delta), dim=1) / max_episode_length_f
    else:
        action_rate_penalty = torch.zeros_like(current_goal_distance)
    front_support = torch.max(wheel_contact_weights[:, 2], wheel_contact_weights[:, 3])
    mid_support = torch.max(wheel_contact_weights[:, 0], wheel_contact_weights[:, 1])
    rear_support = torch.max(wheel_contact_weights[:, 4], wheel_contact_weights[:, 5])
    module_support = torch.stack((front_support, mid_support, rear_support), dim=1)
    contact_min = max(float(params.contact_support_min_weight), 1.0e-6)
    contact_deficit = torch.clamp((contact_min - module_support) / contact_min, min=0.0, max=1.0)
    contact_support_penalty = torch.mean(torch.square(contact_deficit), dim=1) / max_episode_length_f
    forward_speed = torch.clamp(base_lin_vel_b[:, 0], min=0.0)
    flat_speed_limit = max(float(cfg.control.base_forward_velocity_max), 1.0e-6)
    edge_speed_limit = min(max(float(params.edge_speed_limit_mps), 0.0), flat_speed_limit)
    edge_safe_speed = flat_speed_limit - edge_strength * (flat_speed_limit - edge_speed_limit)
    edge_speed_excess = torch.clamp(forward_speed - edge_safe_speed, min=0.0)
    edge_speed_penalty = edge_strength * torch.square(edge_speed_excess / flat_speed_limit) / max_episode_length_f

    components = {
        "distance_to_target": distance_to_target * params.distance_to_target_weight,
        "progress_to_target": progress_to_target * params.progress_to_target_weight,
        "reached_target": reached_target * params.reached_target_weight,
        "far_from_target": far_from_target * params.far_from_target_weight,
        "angle_diff": angle_diff * params.angle_diff_weight,
        "turn_speed_penalty": turn_speed_penalty * params.turn_speed_penalty_weight,
        "slip_penalty": slip_penalty * params.slip_penalty_weight,
        "action_rate_penalty": action_rate_penalty * params.action_rate_penalty_weight,
        "contact_support_penalty": contact_support_penalty * params.contact_support_penalty_weight,
        "edge_speed_penalty": edge_speed_penalty * params.edge_speed_penalty_weight,
    }
    components = {name: _finite_tensor(value) for name, value in components.items()}
    total_reward = sum(components.values())
    if cfg.rewards.only_positive_rewards:
        total_reward = torch.clamp(total_reward, min=0.0)
    total_reward = _finite_tensor(total_reward)
    diagnostics = {
        "progress_ungated": ungated_progress_to_target,
        "progress_positive": positive_progress,
        "progress_negative": negative_progress,
        "progress_longitudinal_gate": longitudinal_gate,
        "progress_slip_angle_gate": slip_angle_gate,
        "progress_gate": progress_gate,
        "progress_multiplier": progress_multiplier,
        "slip_contact_weight_sum": contact_weight_sum,
        "slip_masked_longitudinal": masked_longitudinal_slip,
        "slip_masked_angle": masked_slip_angle,
        "contact_support_front": front_support,
        "contact_support_mid": mid_support,
        "contact_support_rear": rear_support,
        "contact_support_score": torch.mean(module_support, dim=1),
        "edge_strength": edge_strength,
        "edge_height_jump": edge_height_jump,
        "edge_safe_speed": edge_safe_speed,
        "edge_forward_speed": forward_speed,
        "edge_speed_excess": edge_speed_excess,
    }
    diagnostics = {name: _finite_tensor(value) for name, value in diagnostics.items()}
    return total_reward, components, diagnostics
