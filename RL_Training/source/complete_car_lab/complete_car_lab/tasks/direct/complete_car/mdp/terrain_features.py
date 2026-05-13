"""Deterministic low-dimensional terrain features for Stage1."""

from __future__ import annotations

import torch


TERRAIN_FEATURE_NAMES = (
    "h_front_mean_m",
    "h_front_max_m",
    "h_front_min_m",
    "front_slope",
    "front_roughness_m",
    "step_up_height_m",
    "drop_depth_m",
    "step_up_distance_norm",
    "drop_distance_norm",
    "gap_width_norm",
    "left_track_height_mean_m",
    "right_track_height_mean_m",
    "left_track_step_height_m",
    "right_track_step_height_m",
    "left_track_drop_depth_m",
    "right_track_drop_depth_m",
    "left_right_height_diff_m",
    "front_support_height_m",
    "middle_support_height_m",
    "rear_support_height_m",
    "front_middle_height_diff_m",
    "middle_rear_height_diff_m",
    "support_height_std_m",
    "g_step_up",
    "g_step_down",
    "g_gap",
    "g_rough",
    "g_flat",
)
TERRAIN_FEATURE_DIM = len(TERRAIN_FEATURE_NAMES)


def _finite_tensor(value: torch.Tensor) -> torch.Tensor:
    return torch.nan_to_num(value, nan=0.0, posinf=0.0, neginf=0.0)


def _axis_points(cfg, axis: str, device: torch.device, dtype: torch.dtype) -> torch.Tensor:
    if axis == "x":
        points = cfg.terrain._get_measured_points_x()
        offset = float(getattr(cfg.terrain, "patch_origin_offset_xy", (0.0, 0.0))[0])
    elif axis == "y":
        points = cfg.terrain._get_measured_points_y()
        offset = float(getattr(cfg.terrain, "patch_origin_offset_xy", (0.0, 0.0))[1])
    else:
        raise ValueError(f"Unknown terrain feature axis: {axis}")
    return torch.as_tensor(points, device=device, dtype=dtype) + offset


def _nonempty_mask(mask: torch.Tensor, points: torch.Tensor, *, center: float | None = None) -> torch.Tensor:
    if torch.any(mask):
        return mask
    fallback = torch.zeros_like(mask, dtype=torch.bool)
    if points.numel() == 0:
        return fallback
    if center is None:
        fallback[:] = True
    else:
        fallback[torch.argmin(torch.abs(points - center))] = True
    return fallback


def _masked_mean_2d(values: torch.Tensor, x_mask: torch.Tensor, y_mask: torch.Tensor) -> torch.Tensor:
    x_mask = _nonempty_mask(x_mask, torch.arange(x_mask.numel(), device=values.device, dtype=values.dtype))
    y_mask = _nonempty_mask(y_mask, torch.arange(y_mask.numel(), device=values.device, dtype=values.dtype))
    return values[:, x_mask][:, :, y_mask].mean(dim=(1, 2))


def _track_step_and_drop(track_profile_m: torch.Tensor, transition_mask: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    d_track = track_profile_m[:, 1:] - track_profile_m[:, :-1]
    transition_mask = _nonempty_mask(
        transition_mask,
        torch.arange(d_track.shape[1], device=d_track.device, dtype=d_track.dtype),
    )
    d_track = d_track[:, transition_mask]
    step_height = torch.relu(d_track).amax(dim=1)
    drop_depth = torch.relu(-d_track).amax(dim=1)
    return step_height, drop_depth


def _nearest_distance_norm(
    jumps_m: torch.Tensor,
    transition_x: torch.Tensor,
    threshold_m: float,
) -> torch.Tensor:
    if jumps_m.numel() == 0:
        return torch.zeros(jumps_m.shape[0], device=jumps_m.device, dtype=jumps_m.dtype)
    max_distance = torch.clamp(transition_x.max(), min=1.0e-6)
    detected = jumps_m > threshold_m
    far_distance = torch.full((jumps_m.shape[0],), max_distance, device=jumps_m.device, dtype=jumps_m.dtype)
    candidate = torch.where(detected, transition_x.unsqueeze(0).expand_as(jumps_m), max_distance + 1.0)
    nearest = torch.amin(candidate, dim=1)
    nearest = torch.where(torch.any(detected, dim=1), nearest, far_distance)
    return torch.clamp(nearest / max_distance, min=0.0, max=1.0)


def compute_terrain_features(
    cfg,
    height_patch: torch.Tensor | None,
) -> tuple[torch.Tensor | None, dict[str, torch.Tensor]]:
    """Compute 28 deterministic terrain features from ``D_patch = root_z - terrain_z``.

    Height-like outputs in ``terrain_features`` are scaled by ``height_scale_m`` for actor learning.
    Diagnostics keep physical meters for TensorBoard interpretation.
    """

    if height_patch is None:
        return None, {}

    num_envs = height_patch.shape[0]
    x_points = _axis_points(cfg, "x", height_patch.device, height_patch.dtype)
    y_points = _axis_points(cfg, "y", height_patch.device, height_patch.dtype)
    nx = int(x_points.numel())
    ny = int(y_points.numel())
    expected_dim = nx * ny
    if height_patch.shape[-1] != expected_dim:
        raise ValueError(
            f"Height patch dim {height_patch.shape[-1]} does not match terrain grid {nx} * {ny} = {expected_dim}."
        )

    d_patch = _finite_tensor(height_patch).reshape(num_envs, nx, ny)

    center_x = _nonempty_mask((x_points >= -0.30) & (x_points <= 0.30), x_points, center=0.0)
    center_y = _nonempty_mask(torch.abs(y_points) <= 0.20, y_points, center=0.0)
    d_ref = d_patch[:, center_x][:, :, center_y].median(dim=2).values.median(dim=1).values.view(num_envs, 1, 1)

    h_rel_m = _finite_tensor(d_ref - d_patch)
    height_scale_m = float(getattr(cfg.observations, "terrain_feature_height_scale_m", 0.25))
    height_scale_m = max(height_scale_m, 1.0e-6)
    h_norm = torch.clamp(h_rel_m / height_scale_m, min=-1.0, max=1.0)

    front_preview = _nonempty_mask(x_points > float(cfg.terrain.patch_front_extent), x_points)
    x_nonnegative = _nonempty_mask(x_points >= 0.0, x_points, center=0.0)
    center_track = _nonempty_mask(torch.abs(y_points) <= 0.20, y_points, center=0.0)
    left_track = _nonempty_mask((y_points >= 0.15) & (y_points <= 0.45), y_points, center=0.25)
    right_track = _nonempty_mask((y_points <= -0.15) & (y_points >= -0.45), y_points, center=-0.25)
    support_y = _nonempty_mask(
        torch.abs(y_points) <= float(cfg.terrain.patch_half_width) + 0.05,
        y_points,
        center=0.0,
    )

    front_m = h_rel_m[:, front_preview]
    h_front_mean_m = front_m.mean(dim=(1, 2))
    h_front_max_m = front_m.amax(dim=(1, 2))
    h_front_min_m = front_m.amin(dim=(1, 2))
    front_roughness_m = front_m.std(dim=(1, 2), unbiased=False)

    profile_m = h_rel_m[:, :, center_track].median(dim=2).values
    d_profile_m = profile_m[:, 1:] - profile_m[:, :-1]
    transition_x = 0.5 * (x_points[1:] + x_points[:-1])
    future_transition = _nonempty_mask(transition_x >= 0.0, transition_x, center=0.0)
    future_d_profile_m = d_profile_m[:, future_transition]
    future_transition_x = torch.clamp(transition_x[future_transition], min=0.0)

    step_up_jumps_m = torch.relu(future_d_profile_m)
    drop_jumps_m = torch.relu(-future_d_profile_m)
    step_up_height_m = step_up_jumps_m.amax(dim=1)
    drop_depth_m = drop_jumps_m.amax(dim=1)
    edge_distance_threshold_m = 0.02
    step_up_distance_norm = _nearest_distance_norm(step_up_jumps_m, future_transition_x, edge_distance_threshold_m)
    drop_distance_norm = _nearest_distance_norm(drop_jumps_m, future_transition_x, edge_distance_threshold_m)

    front_profile_m = profile_m[:, x_nonnegative]
    gap_depth_threshold_m = 0.06
    gap_width_norm = torch.mean((front_profile_m < -gap_depth_threshold_m).float(), dim=1)

    front_profile_x = x_points[x_nonnegative]
    front_x_span = torch.clamp(front_profile_x[-1] - front_profile_x[0], min=1.0e-6)
    front_slope = torch.clamp((front_profile_m[:, -1] - front_profile_m[:, 0]) / front_x_span, min=-1.0, max=1.0)

    left_profile_m = h_rel_m[:, :, left_track].mean(dim=2)
    right_profile_m = h_rel_m[:, :, right_track].mean(dim=2)
    left_track_height_mean_m = left_profile_m[:, front_preview].mean(dim=1)
    right_track_height_mean_m = right_profile_m[:, front_preview].mean(dim=1)
    left_track_step_height_m, left_track_drop_depth_m = _track_step_and_drop(left_profile_m, future_transition)
    right_track_step_height_m, right_track_drop_depth_m = _track_step_and_drop(right_profile_m, future_transition)
    left_right_height_diff_m = left_track_height_mean_m - right_track_height_mean_m

    rear_mask = _nonempty_mask(
        (x_points >= -float(cfg.terrain.patch_rear_extent)) & (x_points < -0.30),
        x_points,
        center=-0.60,
    )
    mid_mask = _nonempty_mask((x_points >= -0.30) & (x_points <= 0.30), x_points, center=0.0)
    front_mask = _nonempty_mask(
        (x_points > 0.30) & (x_points <= float(cfg.terrain.patch_front_extent)),
        x_points,
        center=0.60,
    )
    rear_support_height_m = _masked_mean_2d(h_rel_m, rear_mask, support_y)
    middle_support_height_m = _masked_mean_2d(h_rel_m, mid_mask, support_y)
    front_support_height_m = _masked_mean_2d(h_rel_m, front_mask, support_y)
    front_middle_height_diff_m = front_support_height_m - middle_support_height_m
    middle_rear_height_diff_m = middle_support_height_m - rear_support_height_m
    support_height_std_m = torch.stack(
        (front_support_height_m, middle_support_height_m, rear_support_height_m),
        dim=1,
    ).std(dim=1, unbiased=False)

    gate_sigma_m = 0.02
    rough_sigma_m = 0.01
    g_step_up = torch.sigmoid((step_up_height_m - 0.05) / gate_sigma_m)
    g_step_down = torch.sigmoid((drop_depth_m - 0.08) / gate_sigma_m)
    g_gap = g_step_down * torch.sigmoid((gap_width_norm - 0.15) / 0.05)
    g_rough = torch.sigmoid((front_roughness_m - 0.03) / rough_sigma_m)
    g_flat = 1.0 - torch.clamp(g_step_up + g_step_down + g_gap + g_rough, min=0.0, max=1.0)

    def h_feature(value_m: torch.Tensor) -> torch.Tensor:
        return torch.clamp(value_m / height_scale_m, min=-1.0, max=1.0)

    terrain_features = torch.stack(
        (
            h_feature(h_front_mean_m),
            h_feature(h_front_max_m),
            h_feature(h_front_min_m),
            front_slope,
            h_feature(front_roughness_m),
            h_feature(step_up_height_m),
            h_feature(drop_depth_m),
            step_up_distance_norm,
            drop_distance_norm,
            torch.clamp(gap_width_norm, min=0.0, max=1.0),
            h_feature(left_track_height_mean_m),
            h_feature(right_track_height_mean_m),
            h_feature(left_track_step_height_m),
            h_feature(right_track_step_height_m),
            h_feature(left_track_drop_depth_m),
            h_feature(right_track_drop_depth_m),
            h_feature(left_right_height_diff_m),
            h_feature(front_support_height_m),
            h_feature(middle_support_height_m),
            h_feature(rear_support_height_m),
            h_feature(front_middle_height_diff_m),
            h_feature(middle_rear_height_diff_m),
            h_feature(support_height_std_m),
            g_step_up,
            g_step_down,
            g_gap,
            g_rough,
            g_flat,
        ),
        dim=1,
    )

    diagnostics = {
        "h_front_mean_m": h_front_mean_m,
        "h_front_max_m": h_front_max_m,
        "h_front_min_m": h_front_min_m,
        "front_slope": front_slope,
        "front_roughness_m": front_roughness_m,
        "step_up_height_m": step_up_height_m,
        "drop_depth_m": drop_depth_m,
        "step_up_distance_norm": step_up_distance_norm,
        "drop_distance_norm": drop_distance_norm,
        "gap_width_norm": gap_width_norm,
        "left_track_height_mean_m": left_track_height_mean_m,
        "right_track_height_mean_m": right_track_height_mean_m,
        "left_track_step_height_m": left_track_step_height_m,
        "right_track_step_height_m": right_track_step_height_m,
        "left_track_drop_depth_m": left_track_drop_depth_m,
        "right_track_drop_depth_m": right_track_drop_depth_m,
        "left_right_height_diff_m": left_right_height_diff_m,
        "front_support_height_m": front_support_height_m,
        "middle_support_height_m": middle_support_height_m,
        "rear_support_height_m": rear_support_height_m,
        "front_middle_height_diff_m": front_middle_height_diff_m,
        "middle_rear_height_diff_m": middle_rear_height_diff_m,
        "support_height_std_m": support_height_std_m,
        "g_step_up": g_step_up,
        "g_step_down": g_step_down,
        "g_gap": g_gap,
        "g_rough": g_rough,
        "g_flat": g_flat,
    }
    return _finite_tensor(terrain_features), {name: _finite_tensor(value) for name, value in diagnostics.items()}


__all__ = [
    "TERRAIN_FEATURE_DIM",
    "TERRAIN_FEATURE_NAMES",
    "compute_terrain_features",
]
