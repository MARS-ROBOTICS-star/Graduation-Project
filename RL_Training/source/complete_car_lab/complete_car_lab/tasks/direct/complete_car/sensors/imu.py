"""IMU 传感器适配器。"""

from __future__ import annotations

import torch

from isaaclab.sensors import Imu, ImuCfg
from isaaclab.utils import configclass


@configclass
class ImuSensorCfg:
    enabled: bool = False
    prim_path: str = "{ENV_REGEX_NS}/Robot/body_car_chassis/IMU_body"
    update_period: float = 0.0
    gravity_bias: tuple[float, float, float] = (0.0, 0.0, 0.0)
    debug_vis: bool = False
    include_in_policy: bool = True

    @property
    def policy_feature_dim(self) -> int:
        return 12 if self.enabled and self.include_in_policy else 0

    def build_cfg(self) -> ImuCfg:
        return ImuCfg(
            prim_path=self.prim_path,
            update_period=self.update_period,
            gravity_bias=self.gravity_bias,
            debug_vis=self.debug_vis,
        )


class ImuSensorAdapter:
    def __init__(self, cfg: ImuSensorCfg):
        self.cfg = cfg
        self.sensor: Imu | None = None

    def build(self, scene) -> None:
        if not self.cfg.enabled:
            return
        self.sensor = Imu(self.cfg.build_cfg())
        scene.sensors["imu"] = self.sensor

    def reset(self, env_ids=None) -> None:
        if self.sensor is not None:
            self.sensor.reset(env_ids)

    def policy_features(self):
        if self.sensor is None or not self.cfg.include_in_policy:
            return None
        return torch.cat(
            [
                self.sensor.data.lin_vel_b,
                self.sensor.data.ang_vel_b,
                self.sensor.data.lin_acc_b,
                self.sensor.data.ang_acc_b,
            ],
            dim=-1,
        )
