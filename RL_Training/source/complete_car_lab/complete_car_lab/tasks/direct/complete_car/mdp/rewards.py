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
    "slip_penalty",
    "action_rate_penalty",
    "contact_support_penalty",
    "edge_speed_penalty",
    "terrain_aware_edge_speed_penalty",
    "stuck_penalty",
    "no_progress_penalty",
    "airborne_spin_penalty",
    "hard_terrain_spin_penalty",
    "action_soft_limit_penalty",
    "step_up_front_posture_penalty",
    "step_up_module_progress_reward",
    "rear_follow_reward",
    "rear_follow_penalty",
    "quality_row_advance_reward",
    "recovery_reward",
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


def _terrain_value(
    terrain_gates: dict[str, torch.Tensor] | None,
    name: str,
    reference: torch.Tensor,
    *,
    default: float = 0.0,
) -> torch.Tensor:
    if terrain_gates is None or name not in terrain_gates:
        return torch.full_like(reference, float(default))
    return _optional_vector(terrain_gates[name], reference, default=default)


def _reward_weight_enabled(params, name: str) -> bool:
    return abs(float(getattr(params, name, 0.0))) > 0.0


def _decreasing_distance_weight(
    distance_m: torch.Tensor,
    *,
    enter_start_m: float,
    enter_full_m: float,
) -> torch.Tensor:
    enter_span = max(float(enter_start_m) - float(enter_full_m), 1.0e-6)
    return torch.clamp((float(enter_start_m) - distance_m) / enter_span, min=0.0, max=1.0)


def compute_stage1_phase_speed_safe(
    cfg,
    reference: torch.Tensor,
    g_step_up: torch.Tensor,
    g_step_down: torch.Tensor,
    g_gap: torch.Tensor,
    step_up_distance_m: torch.Tensor,
    *,
    obstacle_gate: torch.Tensor | None = None,
) -> torch.Tensor:
    """Compute the Stage1 terrain/phase positive vx limit used by control and reward."""

    flat_speed_limit = max(float(cfg.control.base_forward_velocity_max), 1.0e-6)
    fallback_speed = min(max(float(getattr(cfg.control, "terrain_speed_limit_mps", 0.50)), 0.0), flat_speed_limit)
    v_up_approach = min(
        max(float(getattr(cfg.control, "terrain_speed_step_up_approach_mps", fallback_speed)), 0.0),
        flat_speed_limit,
    )
    v_up_climb = min(
        max(float(getattr(cfg.control, "terrain_speed_step_up_climb_mps", fallback_speed)), 0.0),
        flat_speed_limit,
    )
    v_down = min(
        max(float(getattr(cfg.control, "terrain_speed_step_down_mps", fallback_speed)), 0.0),
        flat_speed_limit,
    )
    v_obstacle = min(
        max(float(getattr(cfg.control, "terrain_speed_obstacle_mps", fallback_speed)), 0.0),
        flat_speed_limit,
    )
    params = cfg.rewards.params
    approach_min = float(getattr(params, "step_up_approach_distance_min_m", 0.20))
    approach_max = float(getattr(params, "step_up_approach_distance_max_m", 1.20))
    g_step_up_approach = g_step_up * ((step_up_distance_m > approach_min) & (step_up_distance_m < approach_max)).float()
    g_step_up_climb = g_step_up * (step_up_distance_m <= approach_min).float()
    if obstacle_gate is None:
        obstacle_gate = torch.zeros_like(reference)
    else:
        obstacle_gate = torch.clamp(_optional_vector(obstacle_gate, reference), min=0.0, max=1.0)
    g_obstacle_approach = obstacle_gate * torch.clamp(1.0 - g_step_up_climb, min=0.0, max=1.0)

    v_safe = torch.full_like(reference, flat_speed_limit)
    v_safe = torch.minimum(v_safe, flat_speed_limit - g_step_up_approach * (flat_speed_limit - v_up_approach))
    v_safe = torch.minimum(v_safe, flat_speed_limit - g_step_up_climb * (flat_speed_limit - v_up_climb))
    v_safe = torch.minimum(v_safe, flat_speed_limit - g_step_down * (flat_speed_limit - v_down))
    v_safe = torch.minimum(v_safe, flat_speed_limit - g_gap * (flat_speed_limit - v_obstacle))
    v_safe = torch.minimum(v_safe, flat_speed_limit - g_obstacle_approach * (flat_speed_limit - v_obstacle))
    return torch.clamp(_finite_tensor(v_safe), min=0.0, max=flat_speed_limit)


def get_nominal_goal_distance(cfg) -> float:
    """Return the reward/termination distance scale without tying Stage1 to waypoint sampling fields."""

    value = float(getattr(cfg.rewards.params, "nominal_goal_distance_m", 0.0))
    if value > 0.0:
        return value
    return float(cfg.commands.goal_distance)


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
    previous_module_support_heights: torch.Tensor | None = None,
    row_module_support_height_baseline: torch.Tensor | None = None,
    row_module_progress_max: torch.Tensor | None = None,
    obstacle_gate: torch.Tensor | None = None,
    recovery_active: torch.Tensor | None = None,
    recovery_reverse_now: torch.Tensor | None = None,
    recovery_success: torch.Tensor | None = None,
    middle_pitch_rad: torch.Tensor | None = None,
    drop_guard_active: torch.Tensor | None = None,
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
    zero_reward_term = torch.zeros_like(current_goal_distance)

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
    pitch_gate_k_rad = float(getattr(params, "progress_pitch_gate_k_rad", 0.0))
    if pitch_gate_k_rad > 0.0:
        pitch_abs_rad = torch.abs(_optional_vector(middle_pitch_rad, current_goal_distance))
        pitch_deadband_deg = max(float(getattr(params, "progress_pitch_gate_deadband_deg", 0.0)), 0.0)
        pitch_deadband_rad = math.radians(pitch_deadband_deg)
        pitch_gate = torch.where(
            pitch_abs_rad > pitch_deadband_rad,
            torch.exp(-0.5 * torch.square(pitch_abs_rad / max(pitch_gate_k_rad, 1.0e-6))),
            torch.ones_like(pitch_abs_rad),
        )
    else:
        pitch_gate = torch.ones_like(current_goal_distance)
    progress_multiplier = progress_multiplier * pitch_gate
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
    step_up_mid_ratio = max(float(getattr(params, "step_up_support_mid_ratio", 0.4)), 0.0)
    step_up_rear_ratio = max(float(getattr(params, "step_up_support_rear_ratio", 0.6)), 0.0)
    step_up_support_den = max(step_up_mid_ratio + step_up_rear_ratio, 1.0e-6)
    step_up_support_penalty = (
        step_up_mid_ratio * mid_deficit_sq
        + step_up_rear_ratio * rear_deficit_sq
    ) / step_up_support_den
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
    edge_safe_speed = torch.full_like(current_goal_distance, flat_speed_limit)
    edge_speed_excess = zero_reward_term
    edge_speed_penalty = zero_reward_term
    if _reward_weight_enabled(params, "edge_speed_penalty_weight"):
        edge_speed_limit = min(max(float(params.edge_speed_limit_mps), 0.0), flat_speed_limit)
        edge_safe_speed = flat_speed_limit - edge_strength * (flat_speed_limit - edge_speed_limit)
        edge_speed_excess = torch.clamp(forward_speed - edge_safe_speed, min=0.0)
        edge_speed_penalty = edge_strength * torch.square(edge_speed_excess / flat_speed_limit) / max_episode_length_f

    if terrain_speed_safe is None:
        step_up_distance_m = step_up_distance_norm * max(
            float(getattr(cfg.terrain, "patch_front_extent", 0.0))
            + float(getattr(cfg.terrain, "patch_preview_length", 1.0)),
            1.0e-6,
        )
        terrain_speed_safe = compute_stage1_phase_speed_safe(
            cfg,
            current_goal_distance,
            g_step_up,
            g_step_down,
            g_gap,
            step_up_distance_m,
            obstacle_gate=obstacle_gate,
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
            + float(getattr(params, "terrain_actual_overspeed_penalty_ratio", 0.5))
            * torch.square(terrain_actual_excess / flat_speed_limit)
        )
        / max_episode_length_f
    )
    if terrain_speed_limit_active is None:
        terrain_speed_limit_active = (terrain_raw_excess > 1.0e-4) & (g_edge > 0.05)
    terrain_speed_limit_active_f = _optional_vector(
        terrain_speed_limit_active.float() if isinstance(terrain_speed_limit_active, torch.Tensor) else None,
        current_goal_distance,
    )

    control_dt = max(float(getattr(cfg.control, "control_dt", 1.0 / 60.0)), 1.0e-6)
    hard_gate = torch.maximum(g_step_up, torch.maximum(g_step_down, g_gap))
    hard_gate_active = hard_gate > float(getattr(params, "no_progress_hard_gate_threshold", 0.3))
    target_ahead = commands[:, 0] > float(getattr(params, "stuck_goal_ahead_threshold_m", 0.5))
    no_progress_min_delta_m = max(float(getattr(params, "no_progress_min_delta_m", 0.003)), 1.0e-6)
    no_progress_deficit = torch.clamp(no_progress_min_delta_m - progress_delta, min=0.0) / no_progress_min_delta_m
    no_progress_active = (hard_gate_active & target_ahead).float()
    no_progress_penalty = no_progress_active * torch.clamp(no_progress_deficit, min=0.0, max=2.0) * control_dt
    no_progress_gate = torch.clamp(no_progress_penalty / control_dt, min=0.0, max=1.0)

    stuck_time_s = _optional_vector(stuck_time_s, current_goal_distance)
    stuck_penalty_active = (stuck_time_s > float(params.stuck_penalty_grace_s)).float()
    stuck_penalty = stuck_penalty_active * control_dt

    airborne_spin_penalty = zero_reward_term
    wheel_spin_airborne_mean = zero_reward_term
    if _reward_weight_enabled(params, "airborne_spin_penalty_weight"):
        wheel_joint_vel = _optional_matrix(wheel_joint_vel, wheel_contact_weights)
        wheel_spin_airborne_mean = torch.mean((1.0 - wheel_contact_weights) * torch.abs(wheel_joint_vel), dim=1)
        airborne_spin_penalty = (
            wheel_spin_airborne_mean
            / max(float(params.airborne_spin_velocity_scale_radps), 1.0e-6)
            / max_episode_length_f
        )

    hard_terrain_spin_gate = zero_reward_term
    hard_terrain_low_speed = zero_reward_term
    hard_terrain_slip_excess = zero_reward_term
    hard_terrain_spin_penalty = zero_reward_term
    if _reward_weight_enabled(params, "hard_terrain_spin_penalty_weight"):
        hard_terrain_spin_gate = hard_gate
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
            * torch.maximum(hard_terrain_low_speed, no_progress_gate)
            * torch.square(hard_terrain_slip_excess)
            / max_episode_length_f
        )

    action_soft_limit_penalty = zero_reward_term
    if _reward_weight_enabled(params, "action_soft_limit_penalty_weight"):
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
    rear_pitch_actual = ball_joint_pos[:, 4] if ball_joint_pos.shape[1] > 4 else torch.zeros_like(current_goal_distance)
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
    step_up_front_gap_m = step_up_distance_m - float(getattr(cfg.terrain, "patch_front_extent", 0.0))
    step_up_posture_phase_weight = _decreasing_distance_weight(
        step_up_front_gap_m,
        enter_start_m=float(getattr(params, "step_up_posture_front_gap_start_m", 0.60)),
        enter_full_m=float(getattr(params, "step_up_posture_front_gap_full_m", 0.15)),
    )
    step_up_posture_target_ahead = commands[:, 0] > float(params.step_up_goal_ahead_threshold_m)
    step_up_posture_weight = g_step_up * step_up_posture_target_ahead.float() * step_up_posture_phase_weight
    front_pitch_error = front_pitch_actual - front_pitch_ref
    step_up_posture_badness = torch.clamp(
        front_pitch_error / max(float(params.front_pitch_sigma_rad), 1.0e-6),
        min=0.0,
        max=1.0,
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

    slip_quality = torch.clamp(
        1.0
        - torch.clamp(
            (masked_longitudinal_slip - float(params.low_slip_longitudinal_threshold))
            / max(float(getattr(params, "progress_quality_slip_scale", 4.0)), 1.0e-6),
            min=0.0,
            max=1.0,
        ),
        min=0.0,
        max=1.0,
    )
    overspeed_quality = torch.clamp(1.0 - terrain_raw_excess / flat_speed_limit, min=0.0, max=1.0)
    pitch_rate_quality = torch.clamp(
        1.0
        - torch.clamp(
            pitch_rate_abs / max(float(getattr(params, "progress_quality_pitch_rate_sigma_radps", 1.0)), 1.0e-6),
            min=0.0,
            max=1.0,
        ),
        min=0.0,
        max=1.0,
    )
    step_up_posture_quality = torch.clamp(1.0 - step_up_posture_weight * step_up_posture_badness, min=0.0, max=1.0)
    drop_posture_badness = torch.clamp(
        0.5 * drop_front_pitch_excess / max(float(params.drop_pitch_sigma_rad), 1.0e-6)
        + 0.3 * pitch_rate_abs / max(float(params.drop_pitch_rate_sigma_radps), 1.0e-6)
        + 0.2 * vz_down / max(float(params.drop_vz_down_sigma_mps), 1.0e-6),
        min=0.0,
        max=1.0,
    )
    drop_guard_active_f = _optional_vector(
        drop_guard_active.float() if isinstance(drop_guard_active, torch.Tensor) else None,
        current_goal_distance,
    )
    drop_guard_weight = torch.maximum(g_drop, drop_guard_active_f)
    posture_quality = torch.minimum(
        step_up_posture_quality,
        torch.clamp(1.0 - drop_guard_weight * drop_posture_badness, min=0.0),
    )
    contact_quality = torch.clamp((mid_support + rear_support) / 2.0, min=0.0, max=1.0)
    not_stuck_quality = torch.clamp(
        1.0
        - stuck_time_s / max(float(getattr(params, "progress_quality_stuck_time_scale_s", 2.0)), 1.0e-6),
        min=0.0,
        max=1.0,
    )
    progress_quality_score = torch.minimum(
        torch.minimum(slip_quality, overspeed_quality),
        torch.minimum(torch.minimum(posture_quality, pitch_rate_quality), torch.minimum(contact_quality, not_stuck_quality)),
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
    hard_quality_multiplier = step_up_progress_quality_min + (1.0 - step_up_progress_quality_min) * progress_quality_score
    step_up_progress_quality_multiplier = 1.0 - hard_gate * (1.0 - hard_quality_multiplier)
    progress_to_target = torch.where(
        progress_to_target > 0.0,
        progress_to_target * step_up_progress_quality_multiplier,
        progress_to_target,
    )
    step_up_front_posture_penalty = (
        step_up_posture_weight
        * torch.square(front_pitch_error / max(float(params.front_pitch_sigma_rad), 1.0e-6))
        / max_episode_length_f
    )

    support_heights = torch.stack(
        (
            _terrain_value(terrain_gates, "front_support_height_m", current_goal_distance),
            _terrain_value(terrain_gates, "middle_support_height_m", current_goal_distance),
            _terrain_value(terrain_gates, "rear_support_height_m", current_goal_distance),
        ),
        dim=1,
    )
    previous_module_support_heights = _optional_matrix(previous_module_support_heights, support_heights)
    row_module_support_height_baseline = _optional_matrix(row_module_support_height_baseline, support_heights)
    row_module_progress_max = _optional_matrix(
        row_module_progress_max,
        torch.zeros_like(support_heights),
    )
    module_height_delta = support_heights - previous_module_support_heights
    step_module_height_progress = torch.clamp(module_height_delta, min=0.0)
    row_module_progress = torch.clamp(support_heights - row_module_support_height_baseline, min=0.0)
    module_height_progress = torch.clamp(row_module_progress - row_module_progress_max, min=0.0)
    climb_phase = g_step_up * (step_up_distance_m <= float(params.step_up_approach_distance_min_m)).float() * target_ahead.float()
    crest_phase = g_step_up * (step_up_distance_m > float(params.step_up_approach_distance_min_m)).float() * target_ahead.float()
    module_front_ratio = max(float(getattr(params, "step_up_module_progress_front_ratio", 0.15)), 0.0)
    module_middle_ratio = max(float(getattr(params, "step_up_module_progress_middle_ratio", 0.35)), 0.0)
    module_rear_ratio = max(float(getattr(params, "step_up_module_progress_rear_ratio", 0.50)), 0.0)
    module_ratio_den = max(module_front_ratio + module_middle_ratio + module_rear_ratio, 1.0e-6)
    module_progress_score = torch.clamp(
        (
            module_front_ratio * module_height_progress[:, 0]
            + module_middle_ratio * module_height_progress[:, 1]
            + module_rear_ratio * module_height_progress[:, 2]
        )
        / module_ratio_den
        / max(float(getattr(params, "step_up_module_height_progress_scale_m", 0.05)), 1.0e-6),
        min=0.0,
        max=1.0,
    )
    front_middle_progress_min = torch.minimum(row_module_progress[:, 0], row_module_progress[:, 1])
    rear_follow_deficit_m = torch.clamp(front_middle_progress_min - row_module_progress[:, 2], min=0.0)
    rear_follow_deficit_score = torch.clamp(
        rear_follow_deficit_m / max(float(getattr(params, "rear_follow_deficit_scale_m", 0.05)), 1.0e-6),
        min=0.0,
        max=1.0,
    )
    rear_follow_progress_score = torch.clamp(
        module_height_progress[:, 2] / max(float(getattr(params, "rear_follow_progress_scale_m", 0.03)), 1.0e-6),
        min=0.0,
        max=1.0,
    )
    front_middle_high = (
        front_middle_progress_min >= float(getattr(params, "rear_follow_front_middle_threshold_m", 0.03))
    ).float()
    rear_follow_phase = g_step_up * target_ahead.float() * front_middle_high
    rear_follow_score = torch.clamp(row_module_progress[:, 2] / torch.clamp(front_middle_progress_min, min=1.0e-6), min=0.0, max=1.0)
    front_middle_high_rear_low = rear_follow_phase * (rear_follow_deficit_score > 0.5).float()
    rear_follow_reward = rear_follow_phase * rear_follow_progress_score * rear_support * control_dt
    rear_follow_penalty = rear_follow_phase * rear_follow_deficit_score * (1.0 + torch.clamp(1.0 - rear_support, min=0.0)) * control_dt
    module_support_phase_score = torch.clamp((mid_support + rear_support) / 2.0, min=0.0, max=1.0)
    step_up_module_progress_reward = (
        torch.maximum(climb_phase, 0.5 * crest_phase)
        * module_progress_score
        * module_support_phase_score
        * control_dt
    )

    quality_row_advance_mask = (
        waypoint_hit_mask.float()
        * hard_gate
        * (progress_quality_score >= float(getattr(params, "quality_row_advance_min_score", 0.3))).float()
    )
    quality_row_advance_reward = quality_row_advance_mask * progress_quality_score

    recovery_active = _optional_vector(
        recovery_active.float() if isinstance(recovery_active, torch.Tensor) else None,
        current_goal_distance,
    )
    recovery_reverse_now = _optional_vector(
        recovery_reverse_now.float() if isinstance(recovery_reverse_now, torch.Tensor) else None,
        current_goal_distance,
    )
    recovery_success = _optional_vector(
        recovery_success.float() if isinstance(recovery_success, torch.Tensor) else None,
        current_goal_distance,
    )
    recovery_reward = recovery_success + recovery_reverse_now * recovery_active * control_dt

    drop_anti_dive_penalty = (
        drop_guard_weight
        * (
            0.5 * torch.square(drop_front_pitch_excess / max(float(params.drop_pitch_sigma_rad), 1.0e-6))
            + 0.2 * torch.square(pitch_rate_abs / max(float(params.drop_pitch_rate_sigma_radps), 1.0e-6))
            + 0.5 * torch.square(vz_down / max(float(params.drop_vz_down_sigma_mps), 1.0e-6))
        )
        * (1.0 + float(getattr(params, "drop_guard_latch_penalty_ratio", 1.5)) * drop_guard_active_f)
        / max_episode_length_f
    )

    components = {
        "distance_to_target": distance_to_target * params.distance_to_target_weight,
        "progress_to_target": progress_to_target * params.progress_to_target_weight,
        "reached_target": reached_target * params.reached_target_weight,
        "far_from_target": far_from_target * params.far_from_target_weight,
        "angle_diff": angle_diff * params.angle_diff_weight,
        "slip_penalty": slip_penalty * params.slip_penalty_weight,
        "action_rate_penalty": action_rate_penalty * params.action_rate_penalty_weight,
        "contact_support_penalty": contact_support_penalty * params.contact_support_penalty_weight,
        "edge_speed_penalty": edge_speed_penalty * params.edge_speed_penalty_weight,
        "terrain_aware_edge_speed_penalty": (
            terrain_aware_edge_speed_penalty * params.terrain_aware_edge_speed_penalty_weight
        ),
        "stuck_penalty": stuck_penalty * params.stuck_penalty_weight,
        "no_progress_penalty": no_progress_penalty * params.no_progress_penalty_weight,
        "airborne_spin_penalty": airborne_spin_penalty * params.airborne_spin_penalty_weight,
        "hard_terrain_spin_penalty": hard_terrain_spin_penalty * params.hard_terrain_spin_penalty_weight,
        "action_soft_limit_penalty": action_soft_limit_penalty * params.action_soft_limit_penalty_weight,
        "step_up_front_posture_penalty": (
            step_up_front_posture_penalty * params.step_up_front_posture_penalty_weight
        ),
        "step_up_module_progress_reward": (
            step_up_module_progress_reward * params.step_up_module_progress_reward_weight
        ),
        "rear_follow_reward": rear_follow_reward * params.rear_follow_reward_weight,
        "rear_follow_penalty": rear_follow_penalty * params.rear_follow_penalty_weight,
        "quality_row_advance_reward": quality_row_advance_reward * params.quality_row_advance_reward_weight,
        "recovery_reward": (
            recovery_success * params.recovery_success_reward_weight
            + recovery_reverse_now * recovery_active * control_dt * params.recovery_reverse_penalty_weight
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
        "progress_pitch_gate": pitch_gate,
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
        "stuck_penalty_active": stuck_penalty_active,
        "no_progress_active": no_progress_active,
        "no_progress_deficit": no_progress_deficit,
        "no_progress_penalty_raw": no_progress_penalty,
        "airborne_spin_penalty_raw": airborne_spin_penalty,
        "wheel_spin_airborne_mean": wheel_spin_airborne_mean,
        "hard_terrain_spin_gate": hard_terrain_spin_gate,
        "hard_terrain_low_speed": hard_terrain_low_speed,
        "hard_terrain_slip_excess": hard_terrain_slip_excess,
        "hard_terrain_spin_penalty_raw": hard_terrain_spin_penalty,
        "action_soft_limit_penalty_raw": action_soft_limit_penalty,
        "front_pitch_ref": front_pitch_ref,
        "front_pitch_actual": front_pitch_actual,
        "rear_pitch_actual": rear_pitch_actual,
        "front_pitch_error": front_pitch_error,
        "step_up_distance_m": step_up_distance_m,
        "step_up_front_gap_m": step_up_front_gap_m,
        "step_up_posture_phase_weight": step_up_posture_phase_weight,
        "step_up_posture_weight": step_up_posture_weight,
        "step_up_posture_badness": step_up_posture_badness,
        "progress_quality_slip": slip_quality,
        "progress_quality_overspeed": overspeed_quality,
        "progress_quality_pitch": posture_quality,
        "progress_quality_contact": contact_quality,
        "progress_quality_not_stuck": not_stuck_quality,
        "progress_quality_score": progress_quality_score,
        "step_up_progress_quality_multiplier": step_up_progress_quality_multiplier,
        "step_up_front_posture_penalty_raw": step_up_front_posture_penalty,
        "front_module_height_progress": row_module_progress[:, 0],
        "middle_module_height_progress": row_module_progress[:, 1],
        "rear_module_height_progress": row_module_progress[:, 2],
        "front_module_step_height_progress": step_module_height_progress[:, 0],
        "middle_module_step_height_progress": step_module_height_progress[:, 1],
        "rear_module_step_height_progress": step_module_height_progress[:, 2],
        "front_module_new_height_progress": module_height_progress[:, 0],
        "middle_module_new_height_progress": module_height_progress[:, 1],
        "rear_module_new_height_progress": module_height_progress[:, 2],
        "module_support_phase_score": module_support_phase_score,
        "step_up_climb_phase": climb_phase,
        "step_up_crest_phase": crest_phase,
        "step_up_module_progress_score": module_progress_score,
        "step_up_module_progress_reward_raw": step_up_module_progress_reward,
        "quality_row_advance_mask": quality_row_advance_mask,
        "quality_row_advance_reward_raw": quality_row_advance_reward,
        "recovery_active": recovery_active,
        "recovery_reverse_now": recovery_reverse_now,
        "recovery_success": recovery_success,
        "recovery_reward_raw": recovery_reward,
        "drop_pitch_rate_abs": pitch_rate_abs,
        "drop_vz_down": vz_down,
        "drop_guard_active": drop_guard_active_f,
        "drop_anti_dive_penalty_raw": drop_anti_dive_penalty,
        "rear_follow_score": rear_follow_score,
        "rear_follow_progress_score": rear_follow_progress_score,
        "rear_follow_deficit_m": rear_follow_deficit_m,
        "rear_follow_deficit_score": rear_follow_deficit_score,
        "rear_follow_reward_raw": rear_follow_reward,
        "rear_follow_penalty_raw": rear_follow_penalty,
        "front_middle_high_rear_low": front_middle_high_rear_low,
    }
    diagnostics = {name: _finite_tensor(value) for name, value in diagnostics.items()}
    return total_reward, components, diagnostics
