"""Terrain curriculum 的初始化和升级/降级逻辑。"""

from __future__ import annotations

import torch


def sample_initial_terrain_levels(curriculum_cfg, terrain_runtime, terrain_types: torch.Tensor) -> torch.Tensor:
    max_init_level = min(curriculum_cfg.max_init_terrain_level, terrain_runtime._terrain_cfg.num_rows - 1)
    if not curriculum_cfg.enabled:
        max_init_level = terrain_runtime._terrain_cfg.num_rows - 1
    max_levels = torch.full_like(terrain_types, max_init_level, dtype=torch.long, device=terrain_runtime.device)
    per_name_limits = (
        getattr(curriculum_cfg, "initial_max_terrain_level_by_name", {}) or {}
        if curriculum_cfg.enabled
        else {}
    )
    if per_name_limits:
        terrain_names = tuple(getattr(terrain_runtime._terrain_cfg, "terrain_names", ()))
        row0 = torch.zeros_like(terrain_types, dtype=torch.long, device=terrain_runtime.device)
        terrain_type_indices = terrain_runtime.get_tile_type_indices(row0, terrain_types.to(torch.long))
        for terrain_name, terrain_max_level in per_name_limits.items():
            if terrain_name not in terrain_names:
                continue
            terrain_index = terrain_names.index(terrain_name)
            terrain_max_level = min(max(int(terrain_max_level), 0), terrain_runtime._terrain_cfg.num_rows - 1)
            max_levels = torch.where(
                terrain_type_indices == terrain_index,
                torch.full_like(max_levels, terrain_max_level),
                max_levels,
            )
    u = torch.rand(terrain_types.shape, device=terrain_runtime.device)
    return torch.floor(u * (max_levels.float() + 1.0)).to(torch.long).clamp(min=0)


def _build_initial_terrain_types(terrain_runtime) -> torch.Tensor:
    env_ids = torch.arange(terrain_runtime.num_envs, device=terrain_runtime.device, dtype=torch.long)
    terrain_types = env_ids * terrain_runtime._terrain_cfg.num_cols // terrain_runtime.num_envs
    return terrain_types.clamp_(max=terrain_runtime._terrain_cfg.num_cols - 1)


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


__all__ = ["initialize_terrain_curriculum", "sample_initial_terrain_levels", "update_terrain_curriculum"]
