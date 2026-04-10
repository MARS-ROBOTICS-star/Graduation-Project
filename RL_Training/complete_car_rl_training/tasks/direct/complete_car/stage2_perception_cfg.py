# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Stage 2 perception direct config for the complete-car task."""

from isaaclab.utils import configclass

from .complete_car_env_cfg import CompleteCarEnvCfg
from .stage1_terrain_cfg import Stage1TerrainEnvCfg


@configclass
class Stage2PerceptionEnvCfg(Stage1TerrainEnvCfg):
    def _apply_stage_overrides(self) -> None:
        super()._apply_stage_overrides()
        self.sensors.imu.enabled = True
        self.sensors.camera.enabled = True
        self.sensors.camera.data_types = ["rgb", "distance_to_image_plane"]
        self.sensors.lidar.enabled = True
        self.scene.num_envs = 256

    def __post_init__(self) -> None:
        self._apply_stage_overrides()
        CompleteCarEnvCfg.__post_init__(self)


__all__ = ["Stage2PerceptionEnvCfg"]
