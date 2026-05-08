"""Stage1 terrain-column evaluation metrics."""

from __future__ import annotations

import torch


STAGE1_TERRAIN_COLUMNS: tuple[tuple[int, str], ...] = (
    (0, "col00_flat"),
    (1, "col01_slope_down"),
    (2, "col02_slope_up"),
    (3, "col03_rough"),
    (4, "col04_rough"),
    (5, "col05_stairs_down"),
    (6, "col06_stairs_down"),
    (7, "col07_stairs_up"),
    (8, "col08_stairs_up"),
    (9, "col09_obstacles"),
)

STAGE1_FLAT_REFERENCE_SPEED = 1.18


def _clean(values: torch.Tensor) -> torch.Tensor:
    return torch.nan_to_num(values.float(), nan=0.0, posinf=0.0, neginf=0.0)


def _safe_float(value: torch.Tensor | float) -> float:
    if not isinstance(value, torch.Tensor):
        value = torch.tensor(float(value), dtype=torch.float32)
    value = value.float().reshape(-1)
    if value.numel() == 0:
        return 0.0
    return float(torch.nan_to_num(torch.mean(value), nan=0.0, posinf=0.0, neginf=0.0).item())


def _masked_mean(values: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    if values.numel() == 0 or mask.numel() == 0 or not torch.any(mask):
        return torch.zeros((), device=values.device if isinstance(values, torch.Tensor) else mask.device)
    return torch.mean(_clean(values[mask]))


def _masked_max(values: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    if values.numel() == 0 or mask.numel() == 0 or not torch.any(mask):
        return torch.zeros((), device=values.device)
    return torch.max(_clean(values[mask]))


def _group_stats(
    mask: torch.Tensor,
    *,
    terrain_levels: torch.Tensor,
    forward_x: torch.Tensor,
    rows_advanced: torch.Tensor,
    max_row_reached_mask: torch.Tensor,
    valid_target_masked: torch.Tensor,
    far_mask: torch.Tensor,
    ball_joint_limit_mask: torch.Tensor,
    timeout_mask: torch.Tensor,
    v_forward: torch.Tensor,
    v_lateral_abs: torch.Tensor,
    lateral_velocity_ratio: torch.Tensor,
    yaw_rate_abs: torch.Tensor,
    longitudinal_slip_abs_mean: torch.Tensor,
    slip_angle_abs_mean: torch.Tensor,
    combined_low_slip_mask: torch.Tensor,
    slip_bad_mask: torch.Tensor,
    contact_loss_per_env: torch.Tensor,
    normal_force_sum: torch.Tensor,
    roll_abs_deg: torch.Tensor,
    pitch_abs_deg: torch.Tensor,
    attitude_bad_mask: torch.Tensor,
    ball_joint_limit_usage_per_env: torch.Tensor,
    joint_bad_mask: torch.Tensor,
    action_abs_mean: torch.Tensor,
    action_rate_abs_mean: torch.Tensor,
    action_saturation_mask: torch.Tensor,
    stagnation_mask: torch.Tensor,
    backward_mask: torch.Tensor,
    stuck_time_s: torch.Tensor,
    stuck_timeout_mask: torch.Tensor,
    pitch_rate_abs: torch.Tensor,
    vz_down: torch.Tensor,
    speed_limit_active_mask: torch.Tensor,
) -> dict[str, float]:
    far_rate = _masked_mean(far_mask.float(), mask)
    ball_limit_rate = _masked_mean(ball_joint_limit_mask.float(), mask)
    return {
        "env_count": _safe_float(mask.float().sum()),
        "rows_advanced_mean": _safe_float(_masked_mean(rows_advanced.float(), mask)),
        "row_advance_rate": _safe_float(_masked_mean((rows_advanced > 0).float(), mask)),
        "max_row_reached_rate": _safe_float(_masked_mean(max_row_reached_mask.float(), mask)),
        "valid_target_masked": _safe_float(_masked_mean(valid_target_masked.float(), mask)),
        "forward_x_mean": _safe_float(_masked_mean(forward_x, mask)),
        "current_level_mean": _safe_float(_masked_mean(terrain_levels.float(), mask)),
        "effective_failure_rate": _safe_float(far_rate + ball_limit_rate),
        "far_rate": _safe_float(far_rate),
        "ball_joint_limit_rate": _safe_float(ball_limit_rate),
        "timeout_rate": _safe_float(_masked_mean(timeout_mask.float(), mask)),
        "stuck_time_mean": _safe_float(_masked_mean(stuck_time_s, mask)),
        "stuck_timeout_rate": _safe_float(_masked_mean(stuck_timeout_mask.float(), mask)),
        "stagnation_rate": _safe_float(_masked_mean(stagnation_mask.float(), mask)),
        "backward_rate": _safe_float(_masked_mean(backward_mask.float(), mask)),
        "v_forward_mean": _safe_float(_masked_mean(v_forward, mask)),
        "speed_limit_active_rate": _safe_float(_masked_mean(speed_limit_active_mask.float(), mask)),
        "v_lateral_abs_mean": _safe_float(_masked_mean(v_lateral_abs, mask)),
        "lateral_velocity_ratio": _safe_float(_masked_mean(lateral_velocity_ratio, mask)),
        "yaw_rate_abs_mean": _safe_float(_masked_mean(yaw_rate_abs, mask)),
        "longitudinal_slip_abs_mean": _safe_float(_masked_mean(longitudinal_slip_abs_mean, mask)),
        "slip_angle_abs_mean": _safe_float(_masked_mean(slip_angle_abs_mean, mask)),
        "combined_low_slip_pass_rate": _safe_float(_masked_mean(combined_low_slip_mask.float(), mask)),
        "slip_bad_rate": _safe_float(_masked_mean(slip_bad_mask.float(), mask)),
        "contact_loss_rate": _safe_float(_masked_mean(contact_loss_per_env, mask)),
        "normal_force_sum_mean": _safe_float(_masked_mean(normal_force_sum, mask)),
        "roll_abs_mean": _safe_float(_masked_mean(roll_abs_deg, mask)),
        "pitch_abs_mean": _safe_float(_masked_mean(pitch_abs_deg, mask)),
        "pitch_rate_abs_mean": _safe_float(_masked_mean(pitch_rate_abs, mask)),
        "vz_down_mean": _safe_float(_masked_mean(vz_down, mask)),
        "attitude_bad_rate": _safe_float(_masked_mean(attitude_bad_mask.float(), mask)),
        "ball_joint_limit_usage_max": _safe_float(_masked_max(ball_joint_limit_usage_per_env, mask)),
        "joint_bad_rate": _safe_float(_masked_mean(joint_bad_mask.float(), mask)),
        "action_abs_mean": _safe_float(_masked_mean(action_abs_mean, mask)),
        "action_rate_abs_mean": _safe_float(_masked_mean(action_rate_abs_mean, mask)),
        "action_saturation_rate": _safe_float(_masked_mean(action_saturation_mask.float(), mask)),
    }


def _difficulty_score(stats: dict[str, float], flat_rows_advanced_mean: float) -> float:
    if stats.get("env_count", 0.0) <= 0.0:
        return 0.0
    p_hat = max(0.0, min(stats["rows_advanced_mean"] / max(flat_rows_advanced_mean, 1.0e-6), 1.0))
    score = (
        0.35 * (1.0 - p_hat)
        + 0.20 * stats["effective_failure_rate"]
        + 0.15 * stats["stagnation_rate"]
        + 0.10 * stats["slip_bad_rate"]
        + 0.10 * stats["attitude_bad_rate"]
        + 0.05 * stats["joint_bad_rate"]
        + 0.05 * stats["action_saturation_rate"]
    )
    return float(max(0.0, min(score, 1.0)))


def _retention_score(flat_stats: dict[str, float], v_ref: float) -> float:
    score = (
        0.30 * flat_stats["row_advance_rate"]
        + 0.25 * max(0.0, min(flat_stats["v_forward_mean"] / max(v_ref, 1.0e-6), 1.0))
        + 0.20 * (1.0 - max(0.0, min(flat_stats["effective_failure_rate"] / 0.10, 1.0)))
        + 0.10 * (1.0 - max(0.0, min(flat_stats["lateral_velocity_ratio"] / 0.20, 1.0)))
        + 0.10 * (1.0 - max(0.0, min(flat_stats["stagnation_rate"] / 0.30, 1.0)))
        + 0.05 * (1.0 - max(0.0, min(flat_stats["action_saturation_rate"], 1.0)))
    )
    return float(max(0.0, min(score, 1.0)))


def compute_stage1_eval_metrics(
    *,
    terrain_types: torch.Tensor,
    terrain_levels: torch.Tensor,
    forward_x_from_current_tile_start: torch.Tensor,
    rows_advanced: torch.Tensor,
    max_row_reached_mask: torch.Tensor,
    valid_target_masked: torch.Tensor,
    tile_start_x: torch.Tensor,
    tile_origin_x: torch.Tensor,
    tile_end_x: torch.Tensor,
    root_x: torch.Tensor,
    target_x: torch.Tensor,
    far_mask: torch.Tensor,
    ball_joint_limit_mask: torch.Tensor,
    timeout_mask: torch.Tensor,
    base_lin_vel: torch.Tensor,
    base_ang_vel: torch.Tensor,
    wheel_longitudinal_slip: torch.Tensor,
    wheel_slip_angle: torch.Tensor,
    wheel_normal_contact_force: torch.Tensor,
    roll_deg: torch.Tensor,
    pitch_deg: torch.Tensor,
    ball_joint_limit_usage: torch.Tensor,
    actions: torch.Tensor,
    last_actions: torch.Tensor,
    active_waypoint_distance: torch.Tensor,
    terrain_length: float = 8.0,
    flat_reference_speed: float = STAGE1_FLAT_REFERENCE_SPEED,
    train_active_mask: torch.Tensor | None = None,
    stuck_time_s: torch.Tensor | None = None,
    stuck_timeout_mask: torch.Tensor | None = None,
    pitch_rate_abs: torch.Tensor | None = None,
    vz_down: torch.Tensor | None = None,
    speed_limit_active_mask: torch.Tensor | None = None,
) -> dict[str, float]:
    """Compute NaN-safe Stage1Eval scalars for terrain-column training."""

    if terrain_types.numel() == 0:
        return {}

    terrain_types = terrain_types.to(dtype=torch.long)
    terrain_levels = _clean(terrain_levels)
    rows_advanced = _clean(rows_advanced)
    max_row_reached_mask = max_row_reached_mask.to(dtype=torch.bool)
    valid_target_masked = valid_target_masked.to(dtype=torch.bool)
    forward_x = _clean(forward_x_from_current_tile_start).clamp(0.0, float(terrain_length))
    tile_start_x = _clean(tile_start_x)
    tile_origin_x = _clean(tile_origin_x)
    tile_end_x = _clean(tile_end_x)
    root_x = _clean(root_x)
    target_x = _clean(target_x)
    base_lin_vel = _clean(base_lin_vel)
    base_ang_vel = _clean(base_ang_vel)
    wheel_longitudinal_slip = _clean(wheel_longitudinal_slip)
    wheel_slip_angle = _clean(wheel_slip_angle)
    wheel_normal_contact_force = _clean(wheel_normal_contact_force)
    roll_abs_deg = torch.abs(_clean(roll_deg))
    pitch_abs_deg = torch.abs(_clean(pitch_deg))
    ball_joint_limit_usage = _clean(ball_joint_limit_usage)
    actions = _clean(actions)
    last_actions = _clean(last_actions)
    active_waypoint_distance = _clean(active_waypoint_distance)
    if stuck_time_s is None:
        stuck_time_s = torch.zeros_like(terrain_levels)
    else:
        stuck_time_s = _clean(stuck_time_s)
    if stuck_timeout_mask is None:
        stuck_timeout_mask = torch.zeros_like(terrain_types, dtype=torch.bool)
    else:
        stuck_timeout_mask = stuck_timeout_mask.to(device=terrain_types.device, dtype=torch.bool)
    if pitch_rate_abs is None:
        pitch_rate_abs = torch.zeros_like(terrain_levels)
    else:
        pitch_rate_abs = _clean(pitch_rate_abs)
    if vz_down is None:
        vz_down = torch.zeros_like(terrain_levels)
    else:
        vz_down = _clean(vz_down)
    if speed_limit_active_mask is None:
        speed_limit_active_mask = torch.zeros_like(terrain_types, dtype=torch.bool)
    else:
        speed_limit_active_mask = speed_limit_active_mask.to(device=terrain_types.device, dtype=torch.bool)
    if train_active_mask is None:
        train_active_mask = torch.ones_like(terrain_types, dtype=torch.bool)
    else:
        train_active_mask = train_active_mask.to(device=terrain_types.device, dtype=torch.bool)

    v_forward = base_lin_vel[:, 0]
    v_lateral_abs = torch.abs(base_lin_vel[:, 1])
    lateral_velocity_ratio = v_lateral_abs / (torch.abs(v_forward) + 0.1)
    yaw_rate_abs = torch.abs(base_ang_vel[:, 2])
    longitudinal_slip_abs_mean = torch.mean(torch.abs(wheel_longitudinal_slip), dim=1)
    slip_angle_abs_mean = torch.mean(torch.abs(wheel_slip_angle), dim=1)
    combined_low_slip_mask = (longitudinal_slip_abs_mean < 1.0) & (slip_angle_abs_mean < 0.35)
    slip_bad_mask = (longitudinal_slip_abs_mean > 1.0) | (slip_angle_abs_mean > 0.35)
    contact_loss_per_env = torch.mean((wheel_normal_contact_force < 0.02).float(), dim=1)
    normal_force_sum = torch.sum(wheel_normal_contact_force, dim=1)
    ball_joint_limit_usage_per_env = torch.max(ball_joint_limit_usage, dim=1).values
    action_abs_mean = torch.mean(torch.abs(actions), dim=1)
    action_rate_abs_mean = torch.mean(torch.abs(actions - last_actions), dim=1)
    action_saturation_mask = torch.any(torch.abs(actions) > 0.95, dim=1)
    stagnation_mask = (torch.abs(v_forward) < 0.1) & (active_waypoint_distance > 1.0)
    backward_mask = v_forward < -0.1
    attitude_bad_mask = (roll_abs_deg > 15.0) | (pitch_abs_deg > 20.0)
    joint_bad_mask = ball_joint_limit_mask | (ball_joint_limit_usage_per_env > 0.9)

    all_mask = train_active_mask
    common_kwargs = {
        "terrain_levels": terrain_levels,
        "forward_x": forward_x,
        "rows_advanced": rows_advanced,
        "max_row_reached_mask": max_row_reached_mask,
        "valid_target_masked": valid_target_masked,
        "far_mask": far_mask,
        "ball_joint_limit_mask": ball_joint_limit_mask,
        "timeout_mask": timeout_mask,
        "v_forward": v_forward,
        "v_lateral_abs": v_lateral_abs,
        "lateral_velocity_ratio": lateral_velocity_ratio,
        "yaw_rate_abs": yaw_rate_abs,
        "longitudinal_slip_abs_mean": longitudinal_slip_abs_mean,
        "slip_angle_abs_mean": slip_angle_abs_mean,
        "combined_low_slip_mask": combined_low_slip_mask,
        "slip_bad_mask": slip_bad_mask,
        "contact_loss_per_env": contact_loss_per_env,
        "normal_force_sum": normal_force_sum,
        "roll_abs_deg": roll_abs_deg,
        "pitch_abs_deg": pitch_abs_deg,
        "attitude_bad_mask": attitude_bad_mask,
        "ball_joint_limit_usage_per_env": ball_joint_limit_usage_per_env,
        "joint_bad_mask": joint_bad_mask,
        "action_abs_mean": action_abs_mean,
        "action_rate_abs_mean": action_rate_abs_mean,
        "action_saturation_mask": action_saturation_mask,
        "stagnation_mask": stagnation_mask,
        "backward_mask": backward_mask,
        "stuck_time_s": stuck_time_s,
        "stuck_timeout_mask": stuck_timeout_mask,
        "pitch_rate_abs": pitch_rate_abs,
        "vz_down": vz_down,
        "speed_limit_active_mask": speed_limit_active_mask,
    }
    global_stats = _group_stats(all_mask, **common_kwargs)
    column_stats: dict[int, dict[str, float]] = {}
    for col_index, _col_name in STAGE1_TERRAIN_COLUMNS:
        column_stats[col_index] = _group_stats((terrain_types == col_index) & all_mask, **common_kwargs)

    flat_stats = column_stats[0]
    flat_rows_mean = flat_stats["rows_advanced_mean"]
    flat_retention_score = _retention_score(flat_stats, flat_reference_speed)

    metrics: dict[str, float] = {
        "Stage1Eval/global/rows_advanced_mean": global_stats["rows_advanced_mean"],
        "Stage1Eval/global/row_advance_rate": global_stats["row_advance_rate"],
        "Stage1Eval/global/max_row_reached_rate": global_stats["max_row_reached_rate"],
        "Stage1Eval/global/valid_target_masked": global_stats["valid_target_masked"],
        "Stage1Eval/global/env_count": global_stats["env_count"],
        "Stage1Eval/global/current_level_mean": global_stats["current_level_mean"],
        "Stage1Eval/global/forward_x_mean": global_stats["forward_x_mean"],
        "Stage1Eval/global/tile_start_x_mean": _safe_float(_masked_mean(tile_start_x, all_mask)),
        "Stage1Eval/global/tile_origin_x_mean": _safe_float(_masked_mean(tile_origin_x, all_mask)),
        "Stage1Eval/global/tile_end_x_mean": _safe_float(_masked_mean(tile_end_x, all_mask)),
        "Stage1Eval/global/root_x_mean": _safe_float(_masked_mean(root_x, all_mask)),
        "Stage1Eval/global/target_x_mean": _safe_float(_masked_mean(target_x, all_mask)),
        "Stage1Eval/global/effective_failure_rate": global_stats["effective_failure_rate"],
        "Stage1Eval/global/far_rate": global_stats["far_rate"],
        "Stage1Eval/global/ball_joint_limit_rate": global_stats["ball_joint_limit_rate"],
        "Stage1Eval/global/timeout_rate": global_stats["timeout_rate"],
        "Stage1Eval/global/stuck_time_mean": global_stats["stuck_time_mean"],
        "Stage1Eval/global/stuck_timeout_rate": global_stats["stuck_timeout_rate"],
        "Stage1Eval/global/stagnation_rate": global_stats["stagnation_rate"],
        "Stage1Eval/global/v_forward_mean": global_stats["v_forward_mean"],
        "Stage1Eval/global/speed_limit_active_rate": global_stats["speed_limit_active_rate"],
        "Stage1Eval/global/v_lateral_abs_mean": global_stats["v_lateral_abs_mean"],
        "Stage1Eval/global/lateral_velocity_ratio": global_stats["lateral_velocity_ratio"],
        "Stage1Eval/global/longitudinal_slip_abs_mean": global_stats["longitudinal_slip_abs_mean"],
        "Stage1Eval/global/slip_angle_abs_mean": global_stats["slip_angle_abs_mean"],
        "Stage1Eval/global/combined_low_slip_pass_rate": global_stats["combined_low_slip_pass_rate"],
        "Stage1Eval/global/contact_loss_rate": global_stats["contact_loss_rate"],
        "Stage1Eval/global/normal_force_sum_mean": global_stats["normal_force_sum_mean"],
        "Stage1Eval/global/roll_abs_mean": global_stats["roll_abs_mean"],
        "Stage1Eval/global/pitch_abs_mean": global_stats["pitch_abs_mean"],
        "Stage1Eval/global/pitch_rate_abs_mean": global_stats["pitch_rate_abs_mean"],
        "Stage1Eval/global/vz_down_mean": global_stats["vz_down_mean"],
        "Stage1Eval/global/ball_joint_limit_usage_max": global_stats["ball_joint_limit_usage_max"],
        "Stage1Eval/global/action_abs_mean": global_stats["action_abs_mean"],
        "Stage1Eval/global/action_rate_abs_mean": global_stats["action_rate_abs_mean"],
        "Stage1Eval/global/action_saturation_rate": global_stats["action_saturation_rate"],
        "Stage1Eval/flat/retention_score": flat_retention_score,
    }

    flat_fields = (
        "rows_advanced_mean",
        "row_advance_rate",
        "env_count",
        "max_row_reached_rate",
        "valid_target_masked",
        "forward_x_mean",
        "v_forward_mean",
        "v_lateral_abs_mean",
        "lateral_velocity_ratio",
        "effective_failure_rate",
        "far_rate",
        "ball_joint_limit_rate",
        "stuck_time_mean",
        "stuck_timeout_rate",
        "stagnation_rate",
        "speed_limit_active_rate",
        "longitudinal_slip_abs_mean",
        "slip_angle_abs_mean",
        "combined_low_slip_pass_rate",
        "pitch_abs_mean",
        "pitch_rate_abs_mean",
        "vz_down_mean",
        "roll_abs_mean",
        "ball_joint_limit_usage_max",
        "action_saturation_rate",
    )
    for field_name in flat_fields:
        metrics[f"Stage1Eval/flat/{field_name}"] = flat_stats[field_name]

    difficulty_by_col: dict[int, float] = {}
    per_column_fields = (
        "env_count",
        "rows_advanced_mean",
        "row_advance_rate",
        "max_row_reached_rate",
        "valid_target_masked",
        "forward_x_mean",
        "current_level_mean",
        "effective_failure_rate",
        "far_rate",
        "ball_joint_limit_rate",
        "timeout_rate",
        "stuck_time_mean",
        "stuck_timeout_rate",
        "stagnation_rate",
        "backward_rate",
        "v_forward_mean",
        "speed_limit_active_rate",
        "v_lateral_abs_mean",
        "lateral_velocity_ratio",
        "yaw_rate_abs_mean",
        "longitudinal_slip_abs_mean",
        "slip_angle_abs_mean",
        "combined_low_slip_pass_rate",
        "contact_loss_rate",
        "normal_force_sum_mean",
        "roll_abs_mean",
        "pitch_abs_mean",
        "pitch_rate_abs_mean",
        "vz_down_mean",
        "ball_joint_limit_usage_max",
        "action_abs_mean",
        "action_rate_abs_mean",
        "action_saturation_rate",
    )
    for col_index, col_name in STAGE1_TERRAIN_COLUMNS:
        stats = column_stats[col_index]
        difficulty = 0.0 if col_index == 0 else _difficulty_score(stats, flat_rows_mean)
        difficulty_by_col[col_index] = difficulty
        for field_name in per_column_fields:
            metrics[f"Stage1Eval/{col_name}/{field_name}"] = stats[field_name]
        metrics[f"Stage1Eval/{col_name}/difficulty_score"] = difficulty

    hardest_col_index = 1
    hardest_col_score = difficulty_by_col[hardest_col_index]
    for col_index, _col_name in STAGE1_TERRAIN_COLUMNS[1:]:
        if difficulty_by_col[col_index] > hardest_col_score:
            hardest_col_index = col_index
            hardest_col_score = difficulty_by_col[col_index]

    metrics["Stage1Eval/global/hardest_col_index"] = float(hardest_col_index)
    metrics["Stage1Eval/global/hardest_col_difficulty_score"] = float(hardest_col_score)

    flat_v_forward = flat_stats["v_forward_mean"]
    overspeed_threshold = max(1.5, flat_v_forward + 0.3)
    for col_index, col_name in STAGE1_TERRAIN_COLUMNS:
        if col_name not in {"col01_slope_down", "col05_stairs_down", "col06_stairs_down"}:
            continue
        col_mask = (terrain_types == col_index) & all_mask
        overspeed_rate = _masked_mean((v_forward > overspeed_threshold).float(), col_mask)
        metrics[f"Debug/Stage1/{col_name}/overspeed_rate"] = _safe_float(overspeed_rate)

    return metrics


__all__ = [
    "STAGE1_FLAT_REFERENCE_SPEED",
    "STAGE1_TERRAIN_COLUMNS",
    "compute_stage1_eval_metrics",
]
