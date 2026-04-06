# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Manager-based RL task registration for the complete-car project."""

import gymnasium as gym

from . import agents

##
# Register Gym environments.
##


gym.register(
    id="Complete-Car-Rl-Training-v0",
    entry_point=f"{__name__}.complete_car_stage1_terrain_env:CompleteCarStage1TerrainEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.complete_car_env_cfg:CompleteCarRlTrainingEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:PPORunnerCfg",
    },
)
