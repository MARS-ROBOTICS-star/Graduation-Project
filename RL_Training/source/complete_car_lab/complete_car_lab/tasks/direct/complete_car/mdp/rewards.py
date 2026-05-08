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
    "terrain_aware_edge_speed_penalty",
    "stuck_penalty",
    "airborne_spin_penalty",
    "hard_terrain_spin_penalty",
    "action_soft_limit_penalty",
    "step_up_front_posture_penalty",
    "drop_anti_dive_penalty",
)


def _finite_tensor(value: torch.Tensor) -> torch.Tensor:
    return torch.nan_to_num(value, nan=0.0, posinf=0.0, neginf=0.0)


def _optional_vector(
    value: torch.Tensor | None,
    reference: torch.Tensor,
    *,
    default: float = 0.0,
) -> torch.Tensor:
    if value is None:
        return torch.full_like(reference, float(default))
    return _finite_tensor(value.to(device=reference.device, dtype=reference.dtype).reshape(reference.shape))


def _optional_matrix(
    value: torch.Tensor | None,
    reference: torch.Tensor,
    *,
    default: float = 0.0,
) -> torch.Tensor:
    if value is None:
        return torch.full_like(reference, float(default))
    return _finite_tensor(value.to(device=reference.device, dtype=reference.dtype))


def _terrain_gate(
    terrain_gates: dict[str, torch.Tensor] | None,
    name: str,
    reference: torch.Tensor,
    *,
    default: float = 0.0,
) -> torch.Tensor:
    if terrain_gates is None or name not in terrain_gates:
        return torch.full_like(reference, float(default))
    return torch.clamp(_optional_vector(terrain_gates[name], reference, default=default), min=0.0, max=1.0)


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
    terrain_gates: dict[str, torch.Tensor] | None = None,
    raw_planar_command: torch.Tensor | None = None,
    limited_planar_command: torch.Tensor | None = None,
    terrain_speed_safe: torch.Tensor | None = None,
    terrain_speed_limit_active: torch.Tensor | None = None,
    wheel_joint_vel: torch.Tensor | None = None,
    ball_joint_pos: torch.Tensor | None = None,
    root_lin_vel_w: torch.Tensor | None = None,
    root_ang_vel_b: torch.Tensor | None = None,
    stuck_time_s: torch.Tensor | None = None,
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
    g_step_up = _terrain_gate(terrain_gates, "g_step_up", current_goal_distance)
    g_step_down = _terrain_gate(terrain_gates, "g_step_down", current_goal_distance)
    g_gap = _terrain_gate(terrain_gates, "g_gap", current_goal_distance)
    g_rough = _terrain_gate(terrain_gates, "g_rough", current_goal_distance)
    g_flat = _terrain_gate(terrain_gates, "g_flat", current_goal_distance, default=1.0)
    g_drop = torch.maximum(g_step_down, g_gap)
    g_edge = torch.maximum(g_step_up, g_drop)
    step_up_height_m = _terrain_gate(terrain_gates, "step_up_height_m", current_goal_distance)
    step_up_distance_norm = _terrain_gate(terrain_gates, "step_up_distance_norm", current_goal_distance, default=1.0)
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
    front_deficit_sq = torch.square(contact_deficit[:, 0])
    mid_deficit_sq = torch.square(contact_deficit[:, 1])
    rear_deficit_sq = torch.square(contact_deficit[:, 2])
    all_module_penalty = (front_deficit_sq + mid_deficit_sq + rear_deficit_sq) / 3.0
    step_up_support_penalty = (mid_deficit_sq + 0.5 * rear_deficit_sq) / 1.5
    drop_support_penalty = (mid_deficit_sq + rear_deficit_sq) / 2.0
    g_support_all = torch.maximum(g_flat, g_rough)
    support_weight_sum = torch.clamp(g_support_all + g_step_up + g_drop, min=1.0e-6)
    contact_w_all = g_support_all / support_weight_sum
    contact_w_up = g_step_up / support_weight_sum
    contact_w_drop = g_drop / support_weight_sum
    front_lr_balance = torch.abs(wheel_contact_weights[:, 2] - wheel_contact_weights[:, 3])
    mid_lr_balance = torch.abs(wheel_contact_weights[:, 0] - wheel_contact_weights[:, 1])
    rear_lr_balance = torch.abs(wheel_contact_weights[:, 4] - wheel_contact_weights[:, 5])
    contact_lr_balance = g_edge * (0.2 * front_lr_balance + 0.5 * mid_lr_balance + 0.3 * rear_lr_balance)
    contact_support_penalty = (
        contact_w_all * all_module_penalty
        + contact_w_up * step_up_support_penalty
        + contact_w_drop * drop_support_penalty
        + float(params.contact_support_lr_balance_ratio) * contact_lr_balance
    ) / max_episode_length_f
    forward_speed = torch.clamp(base_lin_vel_b[:, 0], min=0.0)
    flat_speed_limit = max(float(cfg.control.base_forward_velocity_max), 1.0e-6)
    edge_speed_limit = min(max(float(params.edge_speed_limit_mps), 0.0), flat_speed_limit)
    edge_safe_speed = flat_speed_limit - edge_strength * (flat_speed_limit - edge_speed_limit)
    edge_speed_excess = torch.clamp(forward_speed - edge_safe_speed, min=0.0)
    edge_speed_penalty = edge_strength * torch.square(edge_speed_excess / flat_speed_limit) / max_episode_length_f

    if terrain_speed_safe is None:
        v_up = min(max(float(getattr(cfg.control, "terrain_speed_step_up_mps", 0.50)), 0.0), flat_speed_limit)
        v_up_climb = min(
            max(float(getattr(cfg.control, "terrain_speed_step_up_climb_mps", 0.80)), 0.0),
            flat_speed_limit,
        )
        v_down = min(max(float(getattr(cfg.control, "terrain_speed_step_down_mps", 0.35)), 0.0), flat_speed_limit)
        v_gap = min(max(float(getattr(cfg.control, "terrain_speed_gap_mps", 0.40)), 0.0), flat_speed_limit)
        step_up_distance_m = step_up_distance_norm * max(
            float(getattr(cfg.terrain, "patch_front_extent", 0.0))
            + float(getattr(cfg.terrain, "patch_preview_length", 1.0)),
            1.0e-6,
        )
        g_step_up_approach = g_step_up * (
            (step_up_distance_m > float(params.step_up_approach_distance_min_m))
            & (step_up_distance_m < float(params.step_up_approach_distance_max_m))
        ).float()
        g_step_up_climb = g_step_up * (step_up_distance_m <= float(params.step_up_approach_distance_min_m)).float()
        v_safe_up = torch.minimum(
            flat_speed_limit - g_step_up_approach * (flat_speed_limit - v_up),
            flat_speed_limit - g_step_up_climb * (flat_speed_limit - v_up_climb),
        )
        terrain_speed_safe = torch.minimum(
            torch.minimum(
                v_safe_up,
                flat_speed_limit - g_step_down * (flat_speed_limit - v_down),
            ),
            flat_speed_limit - g_gap * (flat_speed_limit - v_gap),
        )
    terrain_speed_safe = torch.clamp(_optional_vector(terrain_speed_safe, current_goal_distance, default=flat_speed_limit), min=0.0)
    raw_planar_command = _optional_matrix(
        raw_planar_command,
        torch.zeros((current_goal_distance.shape[0], 2), device=current_goal_distance.device, dtype=current_goal_distance.dtype),
    )
    if limited_planar_command is None:
        limited_planar_command = raw_planar_command
    else:
        limited_planar_command = _optional_matrix(limited_planar_command, raw_planar_command)
    raw_vx_cmd = raw_planar_command[:, 0]
    limited_vx_cmd = limited_planar_command[:, 0]
    terrain_raw_excess = torch.clamp(raw_vx_cmd - terrain_speed_safe, min=0.0)
    terrain_actual_excess = torch.clamp(forward_speed - terrain_speed_safe, min=0.0)
    terrain_aware_edge_speed_penalty = (
        g_edge
        * (
            torch.square(terrain_raw_excess / flat_speed_limit)
            + 0.5 * torch.square(terrain_actual_excess / flat_speed_limit)
        )
        / max_episode_length_f
    )
    if terrain_speed_limit_active is None:
        terrain_speed_limit_active = (terrain_raw_excess > 1.0e-4) & (g_edge > 0.05)
    terrain_speed_limit_active_f = _optional_vector(
        terrain_speed_limit_active.float() if isinstance(terrain_speed_limit_active, torch.Tensor) else None,
        current_goal_distance,
    )

    stuck_time_s = _optional_vector(stuck_time_s, current_goal_distance)
    stuck_penalty = (stuck_time_s > float(params.stuck_penalty_grace_s)).float() / max_episode_length_f

    wheel_joint_vel = _optional_matrix(wheel_joint_vel, wheel_contact_weights)
    airborne_spin_penalty = (
        torch.mean((1.0 - wheel_contact_weights) * torch.abs(wheel_joint_vel), dim=1)
        / max(float(params.airborne_spin_velocity_scale_radps), 1.0e-6)
        / max_episode_length_f
    )

    hard_terrain_spin_gate = torch.maximum(g_step_up, g_gap)
    hard_terrain_low_speed = torch.clamp(
        (
            float(params.hard_terrain_spin_speed_threshold_mps)
            - torch.clamp(base_lin_vel_b[:, 0], min=0.0)
        )
        / max(float(params.hard_terrain_spin_speed_threshold_mps), 1.0e-6),
        min=0.0,
        max=1.0,
    )
    hard_terrain_slip_excess = torch.clamp(
        (masked_longitudinal_slip - float(params.hard_terrain_spin_slip_threshold))
        / max(float(params.hard_terrain_spin_slip_scale), 1.0e-6),
        min=0.0,
        max=2.0,
    )
    hard_terrain_spin_penalty = (
        hard_terrain_spin_gate
        * hard_terrain_low_speed
        * torch.square(hard_terrain_slip_excess)
        / max_episode_length_f
    )

    soft_limit_actions = actions[:, 2:] if actions.shape[1] > 2 else actions
    action_soft_limit_penalty = torch.mean(
        torch.square(torch.clamp(torch.abs(soft_limit_actions) - float(params.action_soft_limit_threshold), min=0.0)),
        dim=1,
    ) / max_episode_length_f

    ball_joint_pos = _optional_matrix(
        ball_joint_pos,
        torch.zeros((current_goal_distance.shape[0], 6), device=current_goal_distance.device, dtype=current_goal_distance.dtype),
    )
    front_pitch_actual = ball_joint_pos[:, 1] if ball_joint_pos.shape[1] > 1 else torch.zeros_like(current_goal_distance)
    max_preview_distance_m = max(
        float(getattr(cfg.terrain, "patch_front_extent", 0.0)) + float(getattr(cfg.terrain, "patch_preview_length", 1.0)),
        1.0e-6,
    )
    step_up_distance_m = step_up_distance_norm * max_preview_distance_m
    front_pitch_ref = -torch.clamp(
        float(params.front_pitch_height_gain_rad_per_m) * step_up_height_m,
        min=0.0,
        max=float(params.front_pitch_max_ref_rad),
    )
    approach_mask = (
        (step_up_distance_m > float(params.step_up_approach_distance_min_m))
        & (step_up_distance_m < float(params.step_up_approach_distance_max_m))
        & (commands[:, 0] > float(params.step_up_goal_ahead_threshold_m))
    ).float()
    front_pitch_error = front_pitch_actual - front_pitch_ref
    step_up_posture_badness = torch.clamp(
        front_pitch_error / max(float(params.front_pitch_sigma_rad), 1.0e-6),
        min=0.0,
        max=1.0,
    )
    step_up_progress_quality_min = torch.clamp(
        torch.as_tensor(
            float(params.step_up_progress_quality_min_multiplier),
            device=current_goal_distance.device,
            dtype=current_goal_distance.dtype,
        ),
        min=0.0,
        max=1.0,
    )
    step_up_progress_quality_multiplier = 1.0 - (
        approach_mask
        * g_step_up
        * (1.0 - step_up_progress_quality_min)
        * step_up_posture_badness
    )
    progress_to_target = torch.where(
        progress_to_target > 0.0,
        progress_to_target * step_up_progress_quality_multiplier,
        progress_to_target,
    )
    step_up_front_posture_penalty = (
        approach_mask
        * g_step_up
        * torch.square(front_pitch_error / max(float(params.front_pitch_sigma_rad), 1.0e-6))
        / max_episode_length_f
    )

    root_ang_vel_b = _optional_matrix(
        root_ang_vel_b,
        torch.zeros((current_goal_distance.shape[0], 3), device=current_goal_distance.device, dtype=current_goal_distance.dtype),
    )
    root_lin_vel_w = _optional_matrix(
        root_lin_vel_w,
        torch.zeros((current_goal_distance.shape[0], 3), device=current_goal_distance.device, dtype=current_goal_distance.dtype),
    )
    pitch_rate_abs = torch.abs(root_ang_vel_b[:, 1])
    vz_down = torch.clamp(-root_lin_vel_w[:, 2], min=0.0)
    drop_front_pitch_excess = torch.clamp(front_pitch_actual - float(params.drop_theta_safe_rad), min=0.0)
    drop_anti_dive_penalty = (
        g_drop
        * (
            0.5 * torch.square(drop_front_pitch_excess / max(float(params.drop_pitch_sigma_rad), 1.0e-6))
            + 0.2 * torch.square(pitch_rate_abs / max(float(params.drop_pitch_rate_sigma_radps), 1.0e-6))
            + 0.5 * torch.square(vz_down / max(float(params.drop_vz_down_sigma_mps), 1.0e-6))
        )
        / max_episode_length_f
    )

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
        "terrain_aware_edge_speed_penalty": (
            terrain_aware_edge_speed_penalty * params.terrain_aware_edge_speed_penalty_weight
        ),
        "stuck_penalty": stuck_penalty * params.stuck_penalty_weight,
        "airborne_spin_penalty": airborne_spin_penalty * params.airborne_spin_penalty_weight,
        "hard_terrain_spin_penalty": hard_terrain_spin_penalty * params.hard_terrain_spin_penalty_weight,
        "action_soft_limit_penalty": action_soft_limit_penalty * params.action_soft_limit_penalty_weight,
        "step_up_front_posture_penalty": (
            step_up_front_posture_penalty * params.step_up_front_posture_penalty_weight
        ),
        "drop_anti_dive_penalty": drop_anti_dive_penalty * params.drop_anti_dive_penalty_weight,
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
        "contact_support_w_all": contact_w_all,
        "contact_support_w_up": contact_w_up,
        "contact_support_w_drop": contact_w_drop,
        "contact_support_lr_balance": contact_lr_balance,
        "contact_support_all_module_penalty": all_module_penalty,
        "contact_support_step_up_penalty": step_up_support_penalty,
        "contact_support_drop_penalty": drop_support_penalty,
        "edge_strength": edge_strength,
        "edge_height_jump": edge_height_jump,
        "edge_safe_speed": edge_safe_speed,
        "edge_forward_speed": forward_speed,
        "edge_speed_excess": edge_speed_excess,
        "terrain_gate_step_up": g_step_up,
        "terrain_gate_step_down": g_step_down,
        "terrain_gate_gap": g_gap,
        "terrain_gate_rough": g_rough,
        "terrain_gate_flat": g_flat,
        "terrain_gate_edge": g_edge,
        "terrain_speed_safe": terrain_speed_safe,
        "terrain_speed_raw_vx": raw_vx_cmd,
        "terrain_speed_limited_vx": limited_vx_cmd,
        "terrain_speed_actual_vx": forward_speed,
        "terrain_speed_raw_excess": terrain_raw_excess,
        "terrain_speed_actual_excess": terrain_actual_excess,
        "terrain_speed_limit_active": terrain_speed_limit_active_f,
        "stuck_time_s": stuck_time_s,
        "stuck_penalty_active": (stuck_time_s > float(params.stuck_penalty_grace_s)).float(),
        "airborne_spin_penalty_raw": airborne_spin_penalty,
        "hard_terrain_spin_gate": hard_terrain_spin_gate,
        "hard_terrain_low_speed": hard_terrain_low_speed,
        "hard_terrain_slip_excess": hard_terrain_slip_excess,
        "hard_terrain_spin_penalty_raw": hard_terrain_spin_penalty,
        "action_soft_limit_penalty_raw": action_soft_limit_penalty,
        "front_pitch_ref": front_pitch_ref,
        "front_pitch_actual": front_pitch_actual,
        "front_pitch_error": front_pitch_error,
        "step_up_distance_m": step_up_distance_m,
        "step_up_approach_mask": approach_mask,
        "step_up_posture_badness": step_up_posture_badness,
        "step_up_progress_quality_multiplier": step_up_progress_quality_multiplier,
        "step_up_front_posture_penalty_raw": step_up_front_posture_penalty,
        "drop_pitch_rate_abs": pitch_rate_abs,
        "drop_vz_down": vz_down,
        "drop_anti_dive_penalty_raw": drop_anti_dive_penalty,
    }
    diagnostics = {name: _finite_tensor(value) for name, value in diagnostics.items()}
    return total_reward, components, diagnostics
