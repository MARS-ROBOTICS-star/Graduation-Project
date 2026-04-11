"""传感器配置与运行时装配。"""

from __future__ import annotations

from dataclasses import field

import torch
from isaaclab.sensors import RayCaster, RayCasterCfg
from isaaclab.utils import configclass

from .imu import ImuSensorAdapter, ImuSensorCfg
from .lidar import LidarSensorAdapter, LidarSensorCfg
from .stereo_camera import StereoCameraAdapter, StereoCameraSensorCfg


@configclass
class CompleteCarSensorSuiteCfg:
    """集中描述 Stage0/1/2 需要绑定的传感器集合。"""

    imu: ImuSensorCfg = ImuSensorCfg()
    stereo_camera: StereoCameraSensorCfg = StereoCameraSensorCfg()
    lidar: LidarSensorCfg = LidarSensorCfg()
    enable_height_scanner: bool = False
    height_scanner_debug_vis: bool = False

    @property
    def policy_feature_dim(self) -> int:
        return self.imu.policy_feature_dim + self.stereo_camera.policy_feature_dim + self.lidar.policy_feature_dim

    def policy_descriptor(self) -> list[tuple[str, int]]:
        descriptor: list[tuple[str, int]] = []
        if self.imu.policy_feature_dim:
            descriptor.append(("imu", self.imu.policy_feature_dim))
        if self.stereo_camera.policy_feature_dim:
            descriptor.append(("stereo_camera", self.stereo_camera.policy_feature_dim))
        if self.lidar.policy_feature_dim:
            descriptor.append(("lidar", self.lidar.policy_feature_dim))
        return descriptor


class CompleteCarSensorSuiteRuntime:
    """统一封装传感器 runtime，env 只与这一层交互。"""

    def __init__(self, cfg: CompleteCarSensorSuiteCfg, terrain_cfg, ground_prim_path: str):
        self.cfg = cfg
        self.terrain_cfg = terrain_cfg
        self.ground_prim_path = ground_prim_path

        self.imu = ImuSensorAdapter(cfg.imu)
        self.stereo_camera = StereoCameraAdapter(cfg.stereo_camera)
        self.lidar = LidarSensorAdapter(cfg.lidar, ground_prim_path)
        self.height_scanner: RayCaster | None = None
        self._raw_output: dict[str, torch.Tensor | dict[str, torch.Tensor]] = {}

    def build_scene_entities(self, scene) -> None:
        self.imu.build(scene)
        self.stereo_camera.build(scene)
        self.lidar.build(scene)

        if self.cfg.enable_height_scanner:
            height_cfg: RayCasterCfg = self.terrain_cfg.build_height_scanner_cfg(self.ground_prim_path)
            height_cfg.debug_vis = self.cfg.height_scanner_debug_vis
            self.height_scanner = RayCaster(height_cfg)
            scene.sensors["height_scanner"] = self.height_scanner

    def reset(self, env_ids: torch.Tensor | None = None) -> None:
        self.imu.reset(env_ids)
        self.stereo_camera.reset(env_ids)
        self.lidar.reset(env_ids)
        if self.height_scanner is not None:
            self.height_scanner.reset(env_ids)

    def get_height_features(self) -> torch.Tensor | None:
        if self.height_scanner is None:
            return None
        ray_hits_w = self.height_scanner.data.ray_hits_w
        pos_w = self.height_scanner.data.pos_w.unsqueeze(1)
        relative_height = pos_w[..., 2] - ray_hits_w[..., 2] - self.terrain_cfg.height_scanner_offset[2]
        height_features = torch.nan_to_num(relative_height, nan=0.0, posinf=0.0, neginf=0.0)
        self._raw_output["height_scanner"] = height_features
        return height_features

    def get_policy_features(self) -> list[torch.Tensor]:
        features: list[torch.Tensor] = []

        imu_feature = self.imu.policy_features()
        if imu_feature is not None:
            self._raw_output["imu"] = imu_feature
            features.append(imu_feature)

        camera_feature, camera_raw = self.stereo_camera.policy_features()
        if camera_feature is not None:
            self._raw_output["stereo_camera"] = camera_raw
            features.append(camera_feature)

        lidar_feature, lidar_raw = self.lidar.policy_features()
        if lidar_feature is not None:
            self._raw_output["lidar"] = lidar_raw
            features.append(lidar_feature)

        return features

    def get_raw_output(self) -> dict[str, torch.Tensor | dict[str, torch.Tensor]]:
        return dict(self._raw_output)
