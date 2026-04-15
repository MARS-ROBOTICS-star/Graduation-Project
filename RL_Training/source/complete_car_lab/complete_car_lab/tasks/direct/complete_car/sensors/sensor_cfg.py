"""传感器配置与运行时装配。"""

from __future__ import annotations

from dataclasses import field

import torch
from isaaclab.sensors import ContactSensor, ContactSensorCfg, RayCaster, RayCasterCfg
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

    def get_policy_feature_dim(self) -> int:
        return (
            self.imu.get_policy_feature_dim()
            + self.stereo_camera.get_policy_feature_dim()
            + self.lidar.get_policy_feature_dim()
        )

    def policy_descriptor(self) -> list[tuple[str, int]]:
        descriptor: list[tuple[str, int]] = []
        imu_dim = self.imu.get_policy_feature_dim()
        stereo_dim = self.stereo_camera.get_policy_feature_dim()
        lidar_dim = self.lidar.get_policy_feature_dim()
        if imu_dim:
            descriptor.append(("imu", imu_dim))
        if stereo_dim:
            descriptor.append(("stereo_camera", stereo_dim))
        if lidar_dim:
            descriptor.append(("lidar", lidar_dim))
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
        self.wheel_contact_sensor: ContactSensor | None = None
        self._wheel_contact_body_ids: torch.Tensor | None = None
        self._raw_output: dict[str, torch.Tensor | dict[str, torch.Tensor]] = {}

    def build_scene_entities(self, scene) -> None:
        self.imu.build(scene)
        self.stereo_camera.build(scene)
        self.lidar.build(scene)

        self.wheel_contact_sensor = ContactSensor(
            ContactSensorCfg(
                prim_path=(
                    "{ENV_REGEX_NS}/Robot/"
                    "(body_car_wheel_left|body_car_wheel_right|"
                    "head_car_wheel_left|head_car_wheel_right|"
                    "tail_car_wheel_left|tail_car_wheel_right)"
                ),
                update_period=0.0,
                history_length=1,
                debug_vis=False,
            )
        )
        scene.sensors["wheel_contact_sensor"] = self.wheel_contact_sensor

        if self.cfg.enable_height_scanner:
            height_cfg: RayCasterCfg = self.terrain_cfg.build_height_scanner_cfg(self.ground_prim_path)
            height_cfg.debug_vis = self.cfg.height_scanner_debug_vis
            self.height_scanner = RayCaster(height_cfg)
            scene.sensors["height_scanner"] = self.height_scanner

    def reset(self, env_ids: torch.Tensor | None = None) -> None:
        self.imu.reset(env_ids)
        self.stereo_camera.reset(env_ids)
        self.lidar.reset(env_ids)
        if self.wheel_contact_sensor is not None:
            self.wheel_contact_sensor.reset(env_ids)
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

    def get_wheel_contact_forces_w(self, wheel_body_names: list[str]) -> torch.Tensor:
        if self.wheel_contact_sensor is None:
            raise RuntimeError("Wheel contact sensor has not been created.")

        if self._wheel_contact_body_ids is None:
            body_ids, _ = self.wheel_contact_sensor.find_bodies(wheel_body_names, preserve_order=True)
            self._wheel_contact_body_ids = torch.as_tensor(
                body_ids,
                device=self.wheel_contact_sensor.data.net_forces_w.device,
                dtype=torch.long,
            )

        net_forces_w = self.wheel_contact_sensor.data.net_forces_w[:, self._wheel_contact_body_ids]
        self._raw_output["wheel_contact_forces_w"] = net_forces_w
        return net_forces_w

    def get_raw_output(self) -> dict[str, torch.Tensor | dict[str, torch.Tensor]]:
        return dict(self._raw_output)
