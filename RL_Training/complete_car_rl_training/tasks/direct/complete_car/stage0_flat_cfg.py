# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Stage 0 flat-ground direct config for the complete-car task."""

from isaaclab.utils import configclass

from .complete_car_env_cfg import CompleteCarEnvCfg


@configclass
class Stage0FlatEnvCfg(CompleteCarEnvCfg):
    def _apply_stage_overrides(self) -> None:
        self.terrain.enabled = False
        self.terrain.mode = "plane"
        self.terrain.curriculum = False
        self.terrain.flat_only_reset = True

        self.sensors.imu.enabled = False
        self.sensors.camera.enabled = False
        self.sensors.lidar.enabled = False

    def __post_init__(self) -> None:
        self._apply_stage_overrides()
        CompleteCarEnvCfg.__post_init__(self)


__all__ = ["Stage0FlatEnvCfg"]
