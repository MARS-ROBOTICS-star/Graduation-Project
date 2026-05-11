"""Terrain curriculum 的初始化和升级/降级逻辑。"""

from __future__ import annotations

import math

import torch


def _terrain_type_indices_for_names(terrain_runtime, terrain_types: torch.Tensor) -> torch.Tensor:
    row0 = torch.zeros_like(terrain_types, dtype=torch.long, device=terrain_runtime.device)
    return terrain_runtime.get_tile_type_indices(row0, terrain_types.to(torch.long))


def _apply_per_name_level_limits(
    levels: torch.Tensor,
    per_name_limits: dict[str, int],
    terrain_runtime,
    terrain_types: torch.Tensor,
) -> torch.Tensor:
    if not per_name_limits:
        return levels

    terrain_names = tuple(getattr(terrain_runtime._terrain_cfg, "terrain_names", ()))
    terrain_type_indices = _terrain_type_indices_for_names(terrain_runtime, terrain_types)
    max_level = terrain_runtime._terrain_cfg.num_rows - 1
    for terrain_name, terrain_level in per_name_limits.items():
        if terrain_name not in terrain_names:
            continue
        terrain_index = terrain_names.index(terrain_name)
        terrain_level = min(max(int(terrain_level), 0), max_level)
        levels = torch.where(
            terrain_type_indices == terrain_index,
            torch.full_like(levels, terrain_level),
            levels,
        )
    return levels


def get_min_initial_terrain_levels(curriculum_cfg, terrain_runtime, terrain_types: torch.Tensor) -> torch.Tensor:
    min_levels = torch.zeros_like(terrain_types, dtype=torch.long, device=terrain_runtime.device)
    per_name_min_limits = (
        getattr(curriculum_cfg, "initial_min_terrain_level_by_name", {}) or {}
        if curriculum_cfg.enabled
        else {}
    )
    return _apply_per_name_level_limits(min_levels, per_name_min_limits, terrain_runtime, terrain_types)


def sample_initial_terrain_levels(curriculum_cfg, terrain_runtime, terrain_types: torch.Tensor) -> torch.Tensor:
    max_init_level = min(curriculum_cfg.max_init_terrain_level, terrain_runtime._terrain_cfg.num_rows - 1)
    if not curriculum_cfg.enabled:
        max_init_level = terrain_runtime._terrain_cfg.num_rows - 1
    max_levels = torch.full_like(terrain_types, max_init_level, dtype=torch.long, device=terrain_runtime.device)
    min_levels = get_min_initial_terrain_levels(curriculum_cfg, terrain_runtime, terrain_types)
    per_name_max_limits = (
        getattr(curriculum_cfg, "initial_max_terrain_level_by_name", {}) or {}
        if curriculum_cfg.enabled
        else {}
    )
    if per_name_max_limits:
        terrain_names = tuple(getattr(terrain_runtime._terrain_cfg, "terrain_names", ()))
        terrain_type_indices = _terrain_type_indices_for_names(terrain_runtime, terrain_types)
        for terrain_name, terrain_max_level in per_name_max_limits.items():
            if terrain_name not in terrain_names:
                continue
            terrain_index = terrain_names.index(terrain_name)
            terrain_max_level = min(max(int(terrain_max_level), 0), terrain_runtime._terrain_cfg.num_rows - 1)
            max_levels = torch.where(
                terrain_type_indices == terrain_index,
                torch.full_like(max_levels, terrain_max_level),
                max_levels,
            )
    max_levels = torch.maximum(max_levels, min_levels)
    u = torch.rand(terrain_types.shape, device=terrain_runtime.device)
    level_span = (max_levels - min_levels).clamp(min=0)
    return min_levels + torch.floor(u * (level_span.float() + 1.0)).to(torch.long)


def _build_initial_terrain_types(terrain_runtime) -> torch.Tensor:
    env_ids = torch.arange(terrain_runtime.num_envs, device=terrain_runtime.device, dtype=torch.long)
    terrain_types = env_ids * terrain_runtime._terrain_cfg.num_cols // terrain_runtime.num_envs
    return terrain_types.clamp_(max=terrain_runtime._terrain_cfg.num_cols - 1)


def compute_terrain_column_counts(terrain_types: torch.Tensor, num_cols: int) -> torch.Tensor:
    """Count envs or completions per terrain column."""

    num_cols = max(int(num_cols), 1)
    if terrain_types.numel() == 0:
        return torch.zeros(num_cols, dtype=torch.long, device=terrain_types.device)
    terrain_types = terrain_types.to(dtype=torch.long).clamp(min=0, max=num_cols - 1)
    return torch.bincount(terrain_types, minlength=num_cols)[:num_cols].to(dtype=torch.long)


def assign_recycled_terrain_columns(
    active_counts: torch.Tensor,
    unfinished_columns: torch.Tensor,
    num_recycle: int,
    *,
    start_offset: int = 0,
) -> torch.Tensor:
    """Assign recycled envs to unfinished columns while keeping column counts balanced."""

    num_recycle = max(int(num_recycle), 0)
    if num_recycle == 0:
        return torch.empty(0, dtype=torch.long, device=active_counts.device)

    active_counts = active_counts.to(dtype=torch.long).clone()
    unfinished_columns = unfinished_columns.to(device=active_counts.device, dtype=torch.bool)
    available_columns = torch.nonzero(unfinished_columns, as_tuple=False).flatten()
    if available_columns.numel() == 0:
        return torch.empty(0, dtype=torch.long, device=active_counts.device)

    assignments = torch.empty(num_recycle, dtype=torch.long, device=active_counts.device)
    offset = int(start_offset) % int(available_columns.numel())
    for i in range(num_recycle):
        available_counts = active_counts[available_columns]
        min_count = torch.min(available_counts)
        candidate_positions = torch.nonzero(available_counts == min_count, as_tuple=False).flatten()
        chosen_position = candidate_positions[(offset + i) % int(candidate_positions.numel())]
        chosen_column = available_columns[chosen_position]
        assignments[i] = chosen_column
        active_counts[chosen_column] += 1
    return assignments


def compute_completed_column_retention_count(
    active_counts: torch.Tensor,
    completed_columns: torch.Tensor,
    num_envs: int,
    retention_ratio: float,
    candidate_count: int,
) -> int:
    """Return how many recycle candidates should stay on completed columns."""

    candidate_count = max(int(candidate_count), 0)
    if candidate_count == 0:
        return 0

    ratio = min(max(float(retention_ratio), 0.0), 1.0)
    if ratio <= 0.0:
        return 0

    active_counts = active_counts.to(dtype=torch.long)
    completed_columns = completed_columns.to(device=active_counts.device, dtype=torch.bool)
    if not torch.any(completed_columns):
        return 0

    target_retained = int(math.ceil(max(int(num_envs), 0) * ratio))
    target_retained = min(max(target_retained, 0), max(int(num_envs), 0))
    current_retained = int(torch.sum(active_counts[completed_columns]).item())
    retention_needed = max(target_retained - current_retained, 0)
    return min(retention_needed, candidate_count)


def initialize_terrain_curriculum(curriculum_cfg, terrain_runtime, scene) -> None:
    if not terrain_runtime.generator_enabled:
        return

    terrain_runtime.terrain_types = _build_initial_terrain_types(terrain_runtime)
    terrain_runtime.terrain_levels = sample_initial_terrain_levels(
        curriculum_cfg,
        terrain_runtime,
        terrain_runtime.terrain_types,
    )
    terrain_runtime.terrain_classes = torch.zeros(
        terrain_runtime.num_envs,
        dtype=torch.long,
        device=terrain_runtime.device,
    )
    terrain_runtime.sync_env_origins(scene)


def update_terrain_curriculum(curriculum_cfg, terrain_runtime, scene, robot, env_ids: torch.Tensor, commands: torch.Tensor, episode_length_s: float):
    if not terrain_runtime.generator_enabled or not curriculum_cfg.enabled or not terrain_runtime.curriculum_ready:
        return None
    if env_ids.numel() == 0:
        return None

    root_pos = robot.data.root_link_pos_w[env_ids]
    env_origins = scene.env_origins[env_ids]
    if getattr(curriculum_cfg, "move_up_uses_forward_x", False):
        distance = root_pos[:, 0] - env_origins[:, 0]
        required_distance = terrain_runtime._terrain_cfg.terrain_length * curriculum_cfg.move_down_command_ratio
    else:
        distance = torch.norm(root_pos[:, :2] - env_origins[:, :2], dim=1)
        required_distance = torch.norm(commands[env_ids, :2], dim=1) * curriculum_cfg.move_down_command_ratio
    del episode_length_s

    move_up = distance > terrain_runtime._terrain_cfg.terrain_length * curriculum_cfg.move_up_distance_ratio
    move_down = (distance < required_distance) & ~move_up

    terrain_runtime.terrain_levels[env_ids] += move_up.to(torch.long) - move_down.to(torch.long)
    terrain_runtime.terrain_levels[env_ids] = torch.where(
        terrain_runtime.terrain_levels[env_ids] >= terrain_runtime.max_terrain_level,
        torch.randint_like(terrain_runtime.terrain_levels[env_ids], terrain_runtime.max_terrain_level),
        terrain_runtime.terrain_levels[env_ids].clamp_(min=0),
    )
    terrain_runtime.sync_env_origins(scene, env_ids)

    return {
        "terrain_level": float(torch.mean(terrain_runtime.terrain_levels.float()).item()),
        "move_up_ratio": float(torch.mean(move_up.float()).item()),
        "move_down_ratio": float(torch.mean(move_down.float()).item()),
    }


__all__ = [
    "assign_recycled_terrain_columns",
    "compute_completed_column_retention_count",
    "compute_terrain_column_counts",
    "get_min_initial_terrain_levels",
    "initialize_terrain_curriculum",
    "sample_initial_terrain_levels",
    "update_terrain_curriculum",
]
