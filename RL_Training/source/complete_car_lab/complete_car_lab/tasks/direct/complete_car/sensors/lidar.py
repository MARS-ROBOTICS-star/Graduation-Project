"""LiDAR 传感器适配器。"""

from __future__ import annotations

from isaaclab.sensors import RayCaster, RayCasterCfg, patterns
from isaaclab.utils import configclass


@configclass
class LidarSensorCfg:
    enabled: bool = False
    prim_path: str = "{ENV_REGEX_NS}/Robot/head_car_chassis/Example_Rotary"
    update_period: float = 0.1
    horizontal_fov_range: tuple[float, float] = (-60.0, 60.0)
    vertical_fov_range: tuple[float, float] = (-10.0, 10.0)
    horizontal_res: float = 2.0
    channels: int = 16
    min_range: float = 0.2
    max_range: float = 30.0
    debug_vis: bool = False
    offset_pos: tuple[float, float, float] = (0.4, 0.0, 0.2)
    offset_rot: tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)
    policy_num_bins: int = 16
    include_in_policy: bool = True

    @property
    def policy_feature_dim(self) -> int:
        return self.policy_num_bins if self.enabled and self.include_in_policy else 0

    def build_cfg(self, ground_prim_path: str) -> RayCasterCfg:
        return RayCasterCfg(
            prim_path=self.prim_path,
            update_period=self.update_period,
            offset=RayCasterCfg.OffsetCfg(pos=self.offset_pos, rot=self.offset_rot),
            ray_alignment="world",
            pattern_cfg=patterns.LidarPatternCfg(
                channels=self.channels,
                vertical_fov_range=list(self.vertical_fov_range),
                horizontal_fov_range=list(self.horizontal_fov_range),
                horizontal_res=self.horizontal_res,
            ),
            debug_vis=self.debug_vis,
            mesh_prim_paths=[ground_prim_path],
        )


class LidarSensorAdapter:
    def __init__(self, cfg: LidarSensorCfg, ground_prim_path: str):
        self.cfg = cfg
        self.ground_prim_path = ground_prim_path
        self.sensor: RayCaster | None = None

    def build(self, scene) -> None:
        if not self.cfg.enabled:
            return
        self.sensor = RayCaster(self.cfg.build_cfg(self.ground_prim_path))
        scene.sensors["lidar"] = self.sensor

    def reset(self, env_ids=None) -> None:
        if self.sensor is not None:
            self.sensor.reset(env_ids)

    def policy_features(self):
        if self.sensor is None or not self.cfg.include_in_policy:
            return None, None

        import torch

        ray_hits_w = self.sensor.data.ray_hits_w
        pos_w = self.sensor.data.pos_w.unsqueeze(1)
        distances = torch.linalg.norm(ray_hits_w - pos_w, dim=-1)
        distances = torch.nan_to_num(distances, nan=self.cfg.max_range, posinf=self.cfg.max_range)
        pooled_chunks = torch.chunk(distances, self.cfg.policy_num_bins, dim=1)
        lidar_feature = torch.cat([chunk.mean(dim=1, keepdim=True) for chunk in pooled_chunks], dim=1)
        return lidar_feature, distances
