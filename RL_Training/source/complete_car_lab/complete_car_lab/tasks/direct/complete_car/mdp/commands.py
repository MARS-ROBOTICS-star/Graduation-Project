"""Goal-conditioned command sampling and relative-goal conversion."""

from __future__ import annotations

import math
from collections.abc import Callable

import torch

from ..utils.math_utils import wrap_to_pi_tensor, world_xy_to_body_xy


def _sample_direction_offsets(
    num_samples: int,
    max_offset_rad: float,
    *,
    device: torch.device | str,
    dtype: torch.dtype,
) -> torch.Tensor:
    """Sample signed offsets with edge-biased magnitude."""

    u = torch.rand(num_samples, device=device, dtype=dtype)
    signs = torch.where(
        torch.rand(num_samples, device=device) < 0.5,
        -torch.ones(num_samples, device=device, dtype=dtype),
        torch.ones(num_samples, device=device, dtype=dtype),
    )
    return signs * max_offset_rad * torch.sqrt(u)


def _sample_direction_offsets_with_min_abs(
    num_samples: int,
    max_offset_rad: float,
    min_abs_offset_rad: float,
    *,
    device: torch.device | str,
    dtype: torch.dtype,
) -> torch.Tensor:
    """Sample signed offsets whose magnitude stays in ``[min_abs_offset_rad, max_offset_rad]``."""

    if max_offset_rad <= 0.0:
        return torch.zeros(num_samples, device=device, dtype=dtype)

    clamped_min = min(max(min_abs_offset_rad, 0.0), max_offset_rad)
    if clamped_min <= 0.0:
        return _sample_direction_offsets(num_samples, max_offset_rad, device=device, dtype=dtype)

    if clamped_min >= max_offset_rad:
        magnitudes = torch.full((num_samples,), max_offset_rad, device=device, dtype=dtype)
    else:
        u = torch.rand(num_samples, device=device, dtype=dtype)
        magnitudes = clamped_min + (max_offset_rad - clamped_min) * torch.sqrt(u)

    signs = torch.where(
        torch.rand(num_samples, device=device) < 0.5,
        -torch.ones(num_samples, device=device, dtype=dtype),
        torch.ones(num_samples, device=device, dtype=dtype),
    )
    return signs * magnitudes


def _sample_direction_offsets_with_min_abs_per_sample(
    min_abs_offsets_rad: torch.Tensor,
    max_offset_rad: float,
    *,
    device: torch.device | str,
    dtype: torch.dtype,
) -> torch.Tensor:
    """Sample signed offsets with per-environment minimum absolute magnitudes."""

    num_samples = min_abs_offsets_rad.numel()
    if max_offset_rad <= 0.0:
        return torch.zeros(num_samples, device=device, dtype=dtype)

    min_abs_offsets_rad = torch.clamp(min_abs_offsets_rad.to(device=device, dtype=dtype), min=0.0, max=max_offset_rad)
    u = torch.rand(num_samples, device=device, dtype=dtype)
    magnitudes = min_abs_offsets_rad + (max_offset_rad - min_abs_offsets_rad) * torch.sqrt(u)
    signs = torch.where(
        torch.rand(num_samples, device=device) < 0.5,
        -torch.ones(num_samples, device=device, dtype=dtype),
        torch.ones(num_samples, device=device, dtype=dtype),
    )
    return signs * magnitudes


def sample_waypoint_command_sequences(
    waypoint_targets_w: torch.Tensor,
    env_ids: torch.Tensor,
    start_pos_xy_w: torch.Tensor,
    start_heading_w: torch.Tensor,
    cfg,
    sample_height_fn: Callable[[torch.Tensor], torch.Tensor] | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Sample a short waypoint queue for every environment in ``env_ids``.

    Each waypoint is sampled relative to the previous segment heading so a single
    episode forms a short piecewise-linear path instead of unrelated point jumps.
    """

    if env_ids.numel() == 0:
        empty = torch.empty((0, 0), device=waypoint_targets_w.device, dtype=waypoint_targets_w.dtype)
        return empty, empty

    device = waypoint_targets_w.device
    dtype = waypoint_targets_w.dtype
    num_envs = env_ids.numel()
    num_waypoints = waypoint_targets_w.shape[1]
    goal_direction_max = math.radians(cfg.goal_direction_max_deg)
    min_segment_turn = math.radians(getattr(cfg, "min_segment_turn_deg", 0.0))

    direction_offsets = torch.zeros((num_envs, num_waypoints), device=device, dtype=dtype)
    heading_offsets = torch.zeros_like(direction_offsets)

    anchor_xy_w = start_pos_xy_w
    anchor_heading_w = start_heading_w

    standing_mask = torch.rand(num_envs, device=device) < cfg.rel_standing_envs if cfg.rel_standing_envs > 0.0 else None
    zero_mask = torch.ones(num_envs, dtype=torch.bool, device=device) if cfg.zero_command else None

    for waypoint_index in range(num_waypoints):
        if waypoint_index > 0:
            previous_abs_turn = torch.abs(direction_offsets[:, waypoint_index - 1])
            min_abs_turn = torch.clamp(previous_abs_turn + torch.finfo(dtype).eps, min=min_segment_turn)
            phi = _sample_direction_offsets_with_min_abs_per_sample(
                min_abs_turn,
                goal_direction_max,
                device=device,
                dtype=dtype,
            )
        else:
            phi = _sample_direction_offsets(num_envs, goal_direction_max, device=device, dtype=dtype)
        theta_los = wrap_to_pi_tensor(anchor_heading_w + phi)

        target_xy_w = torch.stack(
            (
                anchor_xy_w[:, 0] + cfg.goal_distance * torch.cos(theta_los),
                anchor_xy_w[:, 1] + cfg.goal_distance * torch.sin(theta_los),
            ),
            dim=-1,
        )
        target_heading_w = theta_los

        if sample_height_fn is None:
            target_z_w = torch.zeros(num_envs, device=device, dtype=dtype)
        else:
            target_z_w = sample_height_fn(target_xy_w).to(device=device, dtype=dtype)

        if standing_mask is not None and torch.any(standing_mask):
            target_xy_w = torch.where(standing_mask.unsqueeze(-1), anchor_xy_w, target_xy_w)
            target_z_w = torch.where(standing_mask, torch.zeros_like(target_z_w), target_z_w)
            target_heading_w = torch.where(standing_mask, anchor_heading_w, target_heading_w)
            phi = torch.where(standing_mask, torch.zeros_like(phi), phi)

        if zero_mask is not None:
            target_xy_w = torch.where(zero_mask.unsqueeze(-1), start_pos_xy_w, target_xy_w)
            target_z_w = torch.where(zero_mask, torch.zeros_like(target_z_w), target_z_w)
            target_heading_w = torch.where(zero_mask, start_heading_w, target_heading_w)
            phi = torch.where(zero_mask, torch.zeros_like(phi), phi)

        waypoint_targets_w[env_ids, waypoint_index, 0:2] = target_xy_w
        waypoint_targets_w[env_ids, waypoint_index, 2] = target_z_w
        waypoint_targets_w[env_ids, waypoint_index, 3] = target_heading_w
        direction_offsets[:, waypoint_index] = phi

        anchor_xy_w = target_xy_w
        anchor_heading_w = target_heading_w

    return direction_offsets, heading_offsets


def sample_terrain_column_waypoint_command_sequences(
    waypoint_targets_w: torch.Tensor,
    env_ids: torch.Tensor,
    start_pos_xy_w: torch.Tensor,
    start_heading_w: torch.Tensor,
    cfg,
    terrain_runtime,
    sample_height_fn: Callable[[torch.Tensor], torch.Tensor] | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Sample Stage1 targets in the same terrain column and ahead along world +x."""

    if env_ids.numel() == 0:
        empty = torch.empty((0, 0), device=waypoint_targets_w.device, dtype=waypoint_targets_w.dtype)
        return empty, empty

    if (
        terrain_runtime is None
        or not terrain_runtime.generator_enabled
        or terrain_runtime.terrain_levels is None
        or terrain_runtime.terrain_types is None
    ):
        raise RuntimeError("Terrain-column targets require an initialized generated terrain runtime.")

    device = waypoint_targets_w.device
    dtype = waypoint_targets_w.dtype
    num_envs = env_ids.numel()
    num_waypoints = waypoint_targets_w.shape[1]

    min_row_offset = max(int(getattr(cfg, "terrain_goal_min_row_offset", 1)), 1)
    max_row_offset = max(int(getattr(cfg, "terrain_goal_max_row_offset", 2)), min_row_offset)
    max_target_level = max(int(terrain_runtime.max_terrain_level) - 1, 0)

    terrain_types = terrain_runtime.terrain_types[env_ids].to(torch.long)
    anchor_levels = terrain_runtime.terrain_levels[env_ids].to(torch.long)
    anchor_xy_w = start_pos_xy_w
    anchor_heading_w = start_heading_w

    tile_half_width = 0.5 * float(terrain_runtime._terrain_cfg.terrain_width)
    lateral_range = min(max(float(getattr(cfg, "terrain_goal_lateral_range_m", 3.0)), 0.0), max(tile_half_width, 0.0))
    excluded_lateral_names = set(getattr(cfg, "terrain_goal_lateral_offset_excluded_names", ()))
    terrain_names = tuple(getattr(terrain_runtime._terrain_cfg, "terrain_names", ()))
    excluded_lateral_type_indices = tuple(
        terrain_idx for terrain_idx, terrain_name in enumerate(terrain_names) if terrain_name in excluded_lateral_names
    )

    direction_offsets = torch.zeros((num_envs, num_waypoints), device=device, dtype=dtype)
    heading_offsets = torch.zeros_like(direction_offsets)

    for waypoint_index in range(num_waypoints):
        row_offsets = torch.randint(
            min_row_offset,
            max_row_offset + 1,
            (num_envs,),
            device=device,
            dtype=torch.long,
        )
        target_levels = torch.clamp(anchor_levels + row_offsets, max=max_target_level)
        target_origins = terrain_runtime.get_tile_origins(target_levels, terrain_types).to(device=device, dtype=dtype)
        target_xy_w = target_origins[:, :2].clone()
        if lateral_range > 0.0:
            lateral_offsets = torch.empty(num_envs, device=device, dtype=dtype).uniform_(
                -lateral_range,
                lateral_range,
            )
            if excluded_lateral_type_indices:
                target_type_indices = terrain_runtime.get_tile_type_indices(target_levels, terrain_types)
                no_lateral_mask = torch.zeros(num_envs, device=device, dtype=torch.bool)
                for terrain_type_idx in excluded_lateral_type_indices:
                    no_lateral_mask |= target_type_indices == int(terrain_type_idx)
                lateral_offsets = torch.where(no_lateral_mask, torch.zeros_like(lateral_offsets), lateral_offsets)
            target_xy_w[:, 1] += lateral_offsets

        if sample_height_fn is None:
            target_z_w = torch.zeros(num_envs, device=device, dtype=dtype)
        else:
            target_z_w = sample_height_fn(target_xy_w).to(device=device, dtype=dtype)

        target_heading_w = torch.zeros(num_envs, device=device, dtype=dtype)
        target_delta_xy_w = target_xy_w - anchor_xy_w
        theta_los = torch.atan2(target_delta_xy_w[:, 1], target_delta_xy_w[:, 0])
        direction_offsets[:, waypoint_index] = wrap_to_pi_tensor(theta_los - anchor_heading_w)
        heading_offsets[:, waypoint_index] = wrap_to_pi_tensor(target_heading_w - anchor_heading_w)

        waypoint_targets_w[env_ids, waypoint_index, 0:2] = target_xy_w
        waypoint_targets_w[env_ids, waypoint_index, 2] = target_z_w
        waypoint_targets_w[env_ids, waypoint_index, 3] = target_heading_w

        anchor_levels = target_levels
        anchor_xy_w = target_xy_w
        anchor_heading_w = target_heading_w

    return direction_offsets, heading_offsets


def resample_goal_commands(
    command_targets_w: torch.Tensor,
    command_time_left: torch.Tensor,
    env_ids: torch.Tensor,
    base_pos_xy_w: torch.Tensor,
    base_yaw_w: torch.Tensor,
    cfg,
    sample_height_fn: Callable[[torch.Tensor], torch.Tensor] | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    if env_ids.numel() == 0:
        empty = torch.empty(0, device=command_targets_w.device, dtype=command_targets_w.dtype)
        return empty, empty

    device = command_targets_w.device
    dtype = command_targets_w.dtype
    num_envs = env_ids.numel()

    goal_direction_max = math.radians(cfg.goal_direction_max_deg)
    goal_heading_delta_max = math.radians(cfg.goal_heading_delta_max_deg)

    u = torch.rand(num_envs, device=device, dtype=dtype) #[0,1)均匀分布
    signs = torch.where(
        torch.rand(num_envs, device=device) < 0.5,
        -torch.ones(num_envs, device=device, dtype=dtype),
        torch.ones(num_envs, device=device, dtype=dtype),
    ) #以 50% 的概率生成 +1 或 -1

    phi = signs * goal_direction_max * torch.sqrt(u)# 使用 phi = s * phi_max * sqrt(u) 实现边缘强化采样。
    theta_los = wrap_to_pi_tensor(base_yaw_w + phi) #目标点在世界坐标系下的绝对方位角
    delta = torch.empty(num_envs, device=device, dtype=dtype).uniform_(-goal_heading_delta_max, goal_heading_delta_max)#生成目标航向的随机偏差 delta
    psi_target = wrap_to_pi_tensor(theta_los + delta) #计算最终要求小车到达目标点时的车头朝向 psi

    command_targets_w[env_ids, 0] = base_pos_xy_w[:, 0] + cfg.goal_distance * torch.cos(theta_los)
    command_targets_w[env_ids, 1] = base_pos_xy_w[:, 1] + cfg.goal_distance * torch.sin(theta_los)
    target_xy_w = command_targets_w[env_ids, :2]
    if sample_height_fn is None:
        command_targets_w[env_ids, 2] = 0.0
    else:
        command_targets_w[env_ids, 2] = sample_height_fn(target_xy_w)
    command_targets_w[env_ids, 3] = psi_target
    # 按概率让一部分小车的目标点就是它当前的位置，让它们练习“原地保持不动”.
    if cfg.rel_standing_envs > 0.0:
        standing_mask = torch.rand(num_envs, device=device) < cfg.rel_standing_envs
        if torch.any(standing_mask):
            command_targets_w[env_ids[standing_mask], 0] = base_pos_xy_w[standing_mask, 0]
            command_targets_w[env_ids[standing_mask], 1] = base_pos_xy_w[standing_mask, 1]
            command_targets_w[env_ids[standing_mask], 2] = 0.0
            command_targets_w[env_ids[standing_mask], 3] = base_yaw_w[standing_mask]
            phi = torch.where(standing_mask, torch.zeros_like(phi), phi)
            delta = torch.where(standing_mask, torch.zeros_like(delta), delta)
    # 强制所有小车的目标点设为当前位置
    if cfg.zero_command:
        command_targets_w[env_ids, 0] = base_pos_xy_w[:, 0]
        command_targets_w[env_ids, 1] = base_pos_xy_w[:, 1]
        command_targets_w[env_ids, 2] = 0.0
        command_targets_w[env_ids, 3] = base_yaw_w
        phi.zero_()
        delta.zero_()

    command_time_left[env_ids] = cfg.resampling_time
    return phi, delta


# 计算在小车坐标系下的目标位置及当前 active waypoint 的视线方向误差
def compute_relative_goal_commands(
    command_targets_w: torch.Tensor,
    base_pos_xy_w: torch.Tensor,
    base_yaw_w: torch.Tensor,
    base_pos_z_w: torch.Tensor,
) -> torch.Tensor:
    delta_xy_w = command_targets_w[:, :2] - base_pos_xy_w
    relative_xy_b = world_xy_to_body_xy(delta_xy_w, base_yaw_w)
    relative_z = (command_targets_w[:, 2] - base_pos_z_w).unsqueeze(-1)
    relative_heading = torch.atan2(relative_xy_b[:, 1], relative_xy_b[:, 0]).unsqueeze(-1)
    return torch.cat((relative_xy_b, relative_z, relative_heading), dim=-1)


def step_command_timer(command_time_left: torch.Tensor, step_dt: float) -> torch.Tensor:
    command_time_left -= step_dt
    return torch.nonzero(command_time_left <= 0.0, as_tuple=False).flatten()
