from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class CurriculumState:
    terrain_levels: np.ndarray
    terrain_types: np.ndarray
    env_origins: np.ndarray
    max_terrain_level: int


def initialize_curriculum(num_envs: int, cfg, terrain, rng: np.random.Generator | None = None) -> CurriculumState:
    if rng is None:
        rng = np.random.default_rng()
    max_init_level = cfg.max_init_terrain_level if cfg.curriculum else cfg.num_rows - 1
    terrain_levels = rng.integers(0, max_init_level + 1, size=num_envs, endpoint=False)
    terrain_types = np.floor(np.arange(num_envs) / (num_envs / cfg.num_cols)).astype(np.int64)
    terrain_types = np.clip(terrain_types, 0, cfg.num_cols - 1)
    terrain_origins = np.asarray(terrain.env_origins, dtype=np.float32)
    env_origins = terrain_origins[terrain_levels, terrain_types]
    return CurriculumState(
        terrain_levels=terrain_levels.astype(np.int64),
        terrain_types=terrain_types,
        env_origins=env_origins.copy(),
        max_terrain_level=int(cfg.num_rows),
    )


def update_curriculum(
    state: CurriculumState,
    terrain,
    distances: np.ndarray,
    command_xy_norms: np.ndarray,
    max_episode_length_s: float,
    rng: np.random.Generator | None = None,
) -> CurriculumState:
    if rng is None:
        rng = np.random.default_rng()
    move_up = distances > (terrain.env_length / 2.0)
    move_down = (distances < command_xy_norms * max_episode_length_s * 0.5) & (~move_up)
    state.terrain_levels = state.terrain_levels + move_up.astype(np.int64) - move_down.astype(np.int64)
    overflow = state.terrain_levels >= state.max_terrain_level
    if np.any(overflow):
        state.terrain_levels[overflow] = rng.integers(0, state.max_terrain_level, size=int(np.sum(overflow)), endpoint=False)
    state.terrain_levels = np.clip(state.terrain_levels, 0, state.max_terrain_level - 1)
    terrain_origins = np.asarray(terrain.env_origins, dtype=np.float32)
    state.env_origins = terrain_origins[state.terrain_levels, state.terrain_types]
    return state
