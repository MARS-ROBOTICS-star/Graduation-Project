"""双目相机适配器。"""

from __future__ import annotations

from dataclasses import field

import isaaclab.sim as sim_utils
from isaaclab.sensors import Camera, CameraCfg
from isaaclab.utils import configclass


@configclass
class StereoCameraSensorCfg:
    enabled: bool = False
    prim_path: str = "{ENV_REGEX_NS}/Robot/complete_car_alternative/head_car_chassis/Stereo_Vision_Camera/Camera_left"
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

    def get_policy_feature_dim(self) -> int:
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


class StereoCameraAdapter:
    def __init__(self, cfg: StereoCameraSensorCfg):
        self.cfg = cfg
        self.sensor: Camera | None = None

    def build(self, scene) -> None:
        if not self.cfg.enabled:
            return
        self.sensor = Camera(self.cfg.build_cfg())
        scene.sensors["stereo_camera"] = self.sensor

    def reset(self, env_ids=None) -> None:
        if self.sensor is not None:
            self.sensor.reset(env_ids)

    def policy_features(self):
        if self.sensor is None or not self.cfg.include_in_policy:
            return None, None

        import torch

        camera_features = []
        camera_output = self.sensor.data.output
        for data_type in self.cfg.data_types:
            data = camera_output[data_type].float()
            if data.ndim == 4:
                camera_features.append(data.mean(dim=(1, 2)))
            elif data.ndim == 3:
                camera_features.append(data.mean(dim=(1, 2)).unsqueeze(-1))
            else:
                camera_features.append(data.reshape(data.shape[0], -1).mean(dim=1, keepdim=True))
        return torch.cat(camera_features, dim=-1), camera_output
