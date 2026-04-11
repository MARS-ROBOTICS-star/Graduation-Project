"""地形运行时配置。"""

from __future__ import annotations

from dataclasses import field

from isaaclab.sensors import RayCasterCfg, patterns
from isaaclab.utils import configclass

from .terrain_builder import STAGE1_TERRAIN_CLASS_GAP, STAGE1_TERRAIN_CLASS_OTHER, STAGE1_TERRAIN_CLASS_STEP, Stage1TerrainCfg


@configclass
class CompleteCarTerrainRuntimeCfg:
    """训练阶段统一使用的 terrain 绑定配置。"""

    enabled: bool = False
    mode: str = "plane"
    prim_path: str = "/World/terrain/stage1"
    diffuse_color: tuple[float, float, float] = (0.42, 0.38, 0.30)
    static_friction: float = 1.0
    dynamic_friction: float = 1.0
    restitution: float = 0.0
    measure_heights: bool = False
    measured_points_x: list[float] = field(
        default_factory=lambda: [
            -0.8,
            -0.7,
            -0.6,
            -0.5,
            -0.4,
            -0.3,
            -0.2,
            -0.1,
            0.0,
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
        ]
    )
    measured_points_y: list[float] = field(
        default_factory=lambda: [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    )
    height_scanner_prim_path: str = "{ENV_REGEX_NS}/Robot/body_car_chassis"
    height_scanner_update_period: float = 0.02
    height_scanner_offset: tuple[float, float, float] = (0.0, 0.0, 20.0)
    flat_only_reset: bool = False
    curriculum: bool = False
    max_init_terrain_level: int = 0
    default_terrain_name: str = "flat"
    move_up_distance_ratio: float = 0.5
    move_down_command_ratio: float = 0.5
    step_spawn_back_range: tuple[float, float] = (2.0, 3.0)
    gap_spawn_back_range: tuple[float, float] = (0.0, 0.4)
    other_spawn_xy_range: tuple[float, float] = (-0.5, 0.5)
    generator: Stage1TerrainCfg = Stage1TerrainCfg()

    def build_height_scanner_cfg(self, ground_prim_path: str) -> RayCasterCfg:
        size_x = max(self.measured_points_x) - min(self.measured_points_x)
        size_y = max(self.measured_points_y) - min(self.measured_points_y)
        resolution_x = size_x / max(len(self.measured_points_x) - 1, 1)
        resolution_y = size_y / max(len(self.measured_points_y) - 1, 1)
        resolution = min(resolution_x, resolution_y)
        return RayCasterCfg(
            prim_path=self.height_scanner_prim_path,
            update_period=self.height_scanner_update_period,
            offset=RayCasterCfg.OffsetCfg(pos=self.height_scanner_offset),
            ray_alignment="yaw",
            pattern_cfg=patterns.GridPatternCfg(resolution=resolution, size=[size_x, size_y]),
            debug_vis=False,
            mesh_prim_paths=[ground_prim_path],
        )


__all__ = [
    "CompleteCarTerrainRuntimeCfg",
    "STAGE1_TERRAIN_CLASS_GAP",
    "STAGE1_TERRAIN_CLASS_OTHER",
    "STAGE1_TERRAIN_CLASS_STEP",
    "Stage1TerrainCfg",
]
