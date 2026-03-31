from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class TerrainConfig:
    mesh_type: str = "mix"
    horizontal_scale: float = 0.1
    vertical_scale: float = 0.005
    curriculum: bool = True
    static_friction: float = 1.0
    dynamic_friction: float = 1.0
    restitution: float = 0.0
    measure_heights: bool = True
    custom_origins: bool = True
    measured_points_x: np.ndarray = field(default_factory=lambda: np.array([]))
    measured_points_y: np.ndarray = field(default_factory=lambda: np.array([]))
    num_point_x: int = 0
    num_point_y: int = 0
    max_difficulty: bool = False
    add_roughness: bool = False
    selected: bool = False
    terrain_kwargs: dict | None = None
    flat_wall: object | None = None
    max_init_terrain_level: int = 5
    terrain_length: float = 8.0
    terrain_width: float = 8.0
    num_rows: int = 10
    num_cols: int = 10
    terrain_proportions: list[float] = field(default_factory=list)
    border_size: float = 25.0
    slope_treshold: float = 0.75
    hf2mesh_method: str = "grid"
    max_error: float = 0.1
    max_error_camera: float | None = None
    y_range: object | None = None
    edge_width_thresh: float | None = None
    height: list[float] | None = None
    simplify_grid: bool = False
    gap_size: object | None = None
    stepping_stone_distance: object | None = None
    downsampled_scale: float | None = None
    all_vertical: object | None = None
    no_flat: object | None = None
    terrain_dict: dict[str, float] | None = None
    origin_zero_z: object | None = None
    num_goals: int | None = None
    add_air_beam: bool = True
    add_air_stone: bool = True


def _set_measured_points(cfg: TerrainConfig, x_min: float, x_max: float, x_step: float, y_min: float, y_max: float, y_step: float) -> TerrainConfig:
    cfg.measured_points_x = np.round(np.arange(x_min, x_max, x_step), 2)
    cfg.measured_points_y = np.round(np.arange(y_min, y_max, y_step), 2)
    cfg.num_point_x = int(cfg.measured_points_x.shape[0])
    cfg.num_point_y = int(cfg.measured_points_y.shape[0])
    return cfg


def make_stage1_cfg() -> TerrainConfig:
    cfg = TerrainConfig()
    cfg.mesh_type = "mix"
    cfg.measure_heights = True
    cfg.terrain_dict = {
        "slope down": 0.2,
        "pyramid": 0.2,
        "stairs down": 0.2,
        "stairs up": 0.2,
        "discrete obstacles": 1.1,
        "hurdle": 0.2,
        "gap": 1.2,
        "ramp": 1.1,
        "bream": 0.0,
        "new stairs down": 0.3,
        "pit": 1.0,
    }
    cfg.terrain_proportions = list(cfg.terrain_dict.values())
    cfg.terrain_length = 8.0
    cfg.terrain_width = 8.0
    cfg.num_rows = 20
    cfg.num_cols = 10
    cfg.edge_width_thresh = 0.05
    cfg.simplify_grid = True
    return _set_measured_points(cfg, -0.40, 1.30, 0.1, -0.50, 0.60, 0.1)


def make_stage2_cfg() -> TerrainConfig:
    cfg = TerrainConfig()
    cfg.mesh_type = "gap_parkour"
    cfg.measure_heights = True
    cfg.terrain_dict = {
        "plane": 0.0,
        "up_stairs": 0.0,
        "down_stairs": 0.0,
        "single-gap": 0.002,
        "step-stone": 0.101,
        "Stones-2Rows": 0.101,
        "balance-2Stones": 0.0,
        "stones-1Rows": 0.101,
        "single-bridge": 0.101,
        "step-Beams": 0.0,
        "Rotation-Beams": 0.0,
        "narrow-Beams": 0.0,
        "cross-Beams": 0.0,
        "air-Beams": 0.101,
        "air_stone": 0.101,
        "hurdle": 0.101,
        "ramp": 0.101,
        "corridor": 1.1,
    }
    cfg.terrain_proportions = list(cfg.terrain_dict.values())
    cfg.horizontal_scale = 0.05
    cfg.vertical_scale = 0.005
    cfg.simplify_grid = True
    cfg.edge_width_thresh = 0.05
    cfg.border_size = 5.0
    cfg.add_roughness = True
    cfg.height = [0.01, 0.04]
    cfg.downsampled_scale = 0.5
    cfg.terrain_length = 10.0
    cfg.terrain_width = 4.0
    cfg.num_goals = 10
    cfg.num_rows = 10
    cfg.num_cols = 10
    cfg.add_air_beam = True
    cfg.add_air_stone = True
    return _set_measured_points(cfg, -0.40, 1.30, 0.1, -0.50, 0.60, 0.1)

