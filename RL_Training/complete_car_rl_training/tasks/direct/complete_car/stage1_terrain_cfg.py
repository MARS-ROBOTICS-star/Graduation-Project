# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Stage 1 terrain direct config for the complete-car task."""

from isaaclab.utils import configclass

from .complete_car_env_cfg import CompleteCarEnvCfg
from .stage0_flat_cfg import Stage0FlatEnvCfg


@configclass
class Stage1TerrainEnvCfg(Stage0FlatEnvCfg):
    def _apply_stage_overrides(self) -> None:
        super()._apply_stage_overrides()
        self.terrain.enabled = True
        self.terrain.mode = "generator"
        self.terrain.curriculum = True
        self.terrain.flat_only_reset = False
        self.terrain.max_init_terrain_level = 5
        self.terrain.default_terrain_name = "flat"
        self.terrain.measure_heights = False

    def __post_init__(self) -> None:
        self._apply_stage_overrides()
        CompleteCarEnvCfg.__post_init__(self)


__all__ = ["Stage1TerrainEnvCfg"]
