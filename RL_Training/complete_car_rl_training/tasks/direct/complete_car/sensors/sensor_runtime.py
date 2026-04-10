"""Sensor runtime helper for direct complete-car tasks."""

from __future__ import annotations

from dataclasses import field

import torch

import isaaclab.sim as sim_utils
from isaaclab.sensors import Camera, CameraCfg, Imu, ImuCfg, RayCaster, RayCasterCfg, patterns
from isaaclab.utils import configclass


@configclass
class CompleteCarImuSensorCfg:
    enabled: bool = False
    prim_path: str = "{ENV_REGEX_NS}/Robot/body_car_chassis/IMU_body"
    update_period: float = 0.0
    gravity_bias: tuple[float, float, float] = (0.0, 0.0, 0.0)
    debug_vis: bool = False
    include_in_policy: bool = True

    def build_cfg(self) -> ImuCfg:
        return ImuCfg(
            prim_path=self.prim_path,
            update_period=self.update_period,
            gravity_bias=self.gravity_bias,
            debug_vis=self.debug_vis,
        )

    @property
    def policy_feature_dim(self) -> int:
        return 12 if self.enabled and self.include_in_policy else 0


@configclass
class CompleteCarCameraSensorCfg:
    enabled: bool = False
    prim_path: str = "{ENV_REGEX_NS}/Robot/head_car_chassis/Stereo_rig/left_camera"
    update_period: float = 0.1
    height: int = 64
    width: int = 64
    data_types: list[str] = field(default_factory=lambda: ["rgb"])
    focal_length: float = 24.0
    focus_distance: float = 400.0
    horizontal_aperture: float = 20.955
    clipping_range: tuple[float, float] = (0.1, 1.0e5)
    offset_pos: tuple[float, float, float] = (0.6, 0.0, 0.2)
    offset_rot: tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)
    offset_convention: str = "ros"
    include_in_policy: bool = True

    def build_cfg(self) -> CameraCfg:
        return CameraCfg(
            prim_path=self.prim_path,
            update_period=self.update_period,
            height=self.height,
            width=self.width,
            data_types=list(self.data_types),
            spawn=sim_utils.PinholeCameraCfg(
                focal_length=self.focal_length,
                focus_distance=self.focus_distance,
                horizontal_aperture=self.horizontal_aperture,
                clipping_range=self.clipping_range,
            ),
            offset=CameraCfg.OffsetCfg(
                pos=self.offset_pos,
                rot=self.offset_rot,
                convention=self.offset_convention,
            ),
        )

    @property
    def policy_feature_dim(self) -> int:
        if not self.enabled or not self.include_in_policy:
            return 0
        dim = 0
        for data_type in self.data_types:
            if data_type == "rgb":
                dim += 3
            elif data_type == "rgba":
                dim += 4
            else:
                dim += 1
        return dim


@configclass
class CompleteCarLidarSensorCfg:
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

    @property
    def policy_feature_dim(self) -> int:
        return self.policy_num_bins if self.enabled and self.include_in_policy else 0


@configclass
class CompleteCarSensorRuntimeCfg:
    imu: CompleteCarImuSensorCfg = CompleteCarImuSensorCfg()
    camera: CompleteCarCameraSensorCfg = CompleteCarCameraSensorCfg()
    lidar: CompleteCarLidarSensorCfg = CompleteCarLidarSensorCfg()

    @property
    def policy_feature_dim(self) -> int:
        return self.imu.policy_feature_dim + self.camera.policy_feature_dim + self.lidar.policy_feature_dim


class CompleteCarSensorRuntime:
    """Owns optional sensors and exposes policy-friendly feature tensors."""

    def __init__(self, cfg: CompleteCarSensorRuntimeCfg, terrain_cfg, ground_prim_path: str):
        self.cfg = cfg
        self.terrain_cfg = terrain_cfg
        self.ground_prim_path = ground_prim_path

        self.imu: Imu | None = None
        self.camera: Camera | None = None
        self.lidar: RayCaster | None = None
        self.height_scanner: RayCaster | None = None
        self._raw_output: dict[str, torch.Tensor | dict[str, torch.Tensor]] = {}

    def build_scene_entities(self, scene) -> None:
        if self.cfg.imu.enabled:
            self.imu = Imu(self.cfg.imu.build_cfg())
            scene.sensors["imu"] = self.imu

        if self.cfg.camera.enabled:
            self.camera = Camera(self.cfg.camera.build_cfg())
            scene.sensors["camera"] = self.camera

        if self.cfg.lidar.enabled:
            self.lidar = RayCaster(self.cfg.lidar.build_cfg(self.ground_prim_path))
            scene.sensors["lidar"] = self.lidar

        if getattr(self.terrain_cfg, "measure_heights", False):
            self.height_scanner = RayCaster(self.terrain_cfg.build_height_scanner_cfg(self.ground_prim_path))
            scene.sensors["height_scanner"] = self.height_scanner

    def reset(self, env_ids: torch.Tensor | None = None) -> None:
        for sensor in (self.imu, self.camera, self.lidar, self.height_scanner):
            if sensor is not None:
                sensor.reset(env_ids)

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

        if self.imu is not None and self.cfg.imu.include_in_policy:
            imu_feature = torch.cat(
                [
                    self.imu.data.lin_vel_b,
                    self.imu.data.ang_vel_b,
                    self.imu.data.lin_acc_b,
                    self.imu.data.ang_acc_b,
                ],
                dim=-1,
            )
            self._raw_output["imu"] = imu_feature
            features.append(imu_feature)

        if self.camera is not None and self.cfg.camera.include_in_policy:
            camera_features = []
            camera_output = self.camera.data.output
            for data_type in self.cfg.camera.data_types:
                data = camera_output[data_type].float()
                if data.ndim == 4:
                    camera_features.append(data.mean(dim=(1, 2)))
                elif data.ndim == 3:
                    camera_features.append(data.mean(dim=(1, 2)).unsqueeze(-1))
                else:
                    camera_features.append(data.reshape(data.shape[0], -1).mean(dim=1, keepdim=True))
            camera_feature = torch.cat(camera_features, dim=-1)
            self._raw_output["camera"] = camera_output
            features.append(camera_feature)

        if self.lidar is not None and self.cfg.lidar.include_in_policy:
            ray_hits_w = self.lidar.data.ray_hits_w
            pos_w = self.lidar.data.pos_w.unsqueeze(1)
            distances = torch.linalg.norm(ray_hits_w - pos_w, dim=-1)
            distances = torch.nan_to_num(distances, nan=self.cfg.lidar.max_range, posinf=self.cfg.lidar.max_range)
            pooled_chunks = torch.chunk(distances, self.cfg.lidar.policy_num_bins, dim=1)
            lidar_feature = torch.cat([chunk.mean(dim=1, keepdim=True) for chunk in pooled_chunks], dim=1)
            self._raw_output["lidar"] = distances
            features.append(lidar_feature)

        return features

    def get_raw_output(self) -> dict[str, torch.Tensor | dict[str, torch.Tensor]]:
        return dict(self._raw_output)


__all__ = ["CompleteCarSensorRuntime", "CompleteCarSensorRuntimeCfg"]
