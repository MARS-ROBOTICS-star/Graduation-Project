"""地形运行时配置。"""

from __future__ import annotations

from dataclasses import field

from isaaclab.sensors import RayCasterCfg, patterns
from isaaclab.utils import configclass

from .terrain_builder import STAGE1_TERRAIN_CLASS_GAP, STAGE1_TERRAIN_CLASS_OTHER, STAGE1_TERRAIN_CLASS_STEP, Stage1TerrainCfg

import torch

# 输入轴范围和目标分辨率，输出该轴采样点列表
def _build_axis_points(min_value: float, max_value: float, target_resolution: float) -> list[float]:
    num_points = int(round((max_value - min_value) / target_resolution)) + 1
    if num_points < 2:
        return [round(min_value, 6)]
    step = (max_value - min_value) / (num_points - 1)
    return [round(min_value + i * step, 6) for i in range(num_points)]

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
    patch_front_extent: float = 0.942209  # 中车参考点到整车前端的覆盖长度。
    patch_rear_extent: float = 0.942209  # 中车参考点到整车后端的覆盖长度。
    patch_half_width: float = 0.280374  # 半车宽。

    patch_preview_length: float = 0.40  # 车头前方多看出去的 preview。
    patch_rear_margin: float = 0.40  # 车尾后面多留一点余量。
    patch_side_margin: float = 0.04  # 左右多留一点余量。

    patch_origin_offset_xy: tuple[float, float] = (0.0, 0.0)  # patch 相对中车参考点的平移偏置。

    patch_resolution_x: float = 0.10
    patch_resolution_y: float = 0.10  # patch 网格分辨率。
    measured_points_x: list[float] = field(default_factory=list)
    measured_points_y: list[float] = field(default_factory=list)  # 最终生成后的采样坐标。

    height_scanner_prim_path: str = "{ENV_REGEX_NS}/Robot/body_car_chassis"
    height_scanner_update_period: float = 0.02
    height_scanner_offset: tuple[float, float, float] = (0.0, 0.0, 20.0)
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

    def __post_init__(self):
        if not self.measured_points_x:
            x_min = -(self.patch_rear_extent + self.patch_rear_margin)
            x_max = self.patch_front_extent + self.patch_preview_length
            self.measured_points_x = _build_axis_points(x_min, x_max, self.patch_resolution_x)

        if not self.measured_points_y:
            y_min = -(self.patch_half_width + self.patch_side_margin)
            y_max = self.patch_half_width + self.patch_side_margin
            self.measured_points_y = _build_axis_points(y_min, y_max, self.patch_resolution_y)


    @property
    def num_height_points(self) -> int:
        """返回 patch 中总采样点数。"""

        return len(self.measured_points_x) * len(self.measured_points_y)

    def build_patch_local_points(self, device, dtype):
        """返回中车局部坐标系下的 patch 采样点张量。"""

        x = torch.tensor(self.measured_points_x, device=device, dtype=dtype)
        y = torch.tensor(self.measured_points_y, device=device, dtype=dtype)
        grid_x, grid_y = torch.meshgrid(x, y, indexing="ij")
        points = torch.stack((grid_x.reshape(-1), grid_y.reshape(-1)), dim=-1)
        offset = torch.tensor(self.patch_origin_offset_xy, device=device, dtype=dtype)

        return points + offset
__all__ = [
    "CompleteCarTerrainRuntimeCfg",
    "STAGE1_TERRAIN_CLASS_GAP",
    "STAGE1_TERRAIN_CLASS_OTHER",
    "STAGE1_TERRAIN_CLASS_STEP",
    "Stage1TerrainCfg",
]
