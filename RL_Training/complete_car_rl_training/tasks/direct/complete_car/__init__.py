# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Direct task registration for the complete-car project."""

from __future__ import annotations

import gymnasium as gym

from .agents.ppo_cfg import Stage0FlatPPoCfg, Stage1TerrainPPoCfg, Stage2PerceptionPPoCfg
from .complete_car_env import CompleteCarEnv
from .stage0_flat_cfg import Stage0FlatEnvCfg
from .stage1_terrain_cfg import Stage1TerrainEnvCfg
from .stage2_perception_cfg import Stage2PerceptionEnvCfg


gym.register(
    id="Complete-Car-Stage0-Flat-Direct-v0",
    entry_point=f"{CompleteCarEnv.__module__}:CompleteCarEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{Stage0FlatEnvCfg.__module__}:Stage0FlatEnvCfg",
        "rsl_rl_cfg_entry_point": f"{Stage0FlatPPoCfg.__module__}:Stage0FlatPPoCfg",
    },
)

gym.register(
    id="Complete-Car-Stage1-Terrain-Direct-v0",
    entry_point=f"{CompleteCarEnv.__module__}:CompleteCarEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{Stage1TerrainEnvCfg.__module__}:Stage1TerrainEnvCfg",
        "rsl_rl_cfg_entry_point": f"{Stage1TerrainPPoCfg.__module__}:Stage1TerrainPPoCfg",
    },
)

gym.register(
    id="Complete-Car-Stage2-Perception-Direct-v0",
    entry_point=f"{CompleteCarEnv.__module__}:CompleteCarEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{Stage2PerceptionEnvCfg.__module__}:Stage2PerceptionEnvCfg",
        "rsl_rl_cfg_entry_point": f"{Stage2PerceptionPPoCfg.__module__}:Stage2PerceptionPPoCfg",
    },
)


__all__ = [
    "CompleteCarEnv",
    "Stage0FlatEnvCfg",
    "Stage1TerrainEnvCfg",
    "Stage2PerceptionEnvCfg",
    "Stage0FlatPPoCfg",
    "Stage1TerrainPPoCfg",
    "Stage2PerceptionPPoCfg",
]
