"""Complete-car direct tasks and gym registration."""

from __future__ import annotations

import gymnasium as gym


ENV_ENTRY_POINT = "complete_car_lab.tasks.direct.complete_car.base.env:CompleteCarDirectEnv"
RSL_RL_CFG_MODULE = "complete_car_lab.tasks.direct.complete_car.agents.rsl_rl_ppo_cfg"


gym.register(
    id="CompleteCar-Stage0",
    entry_point=ENV_ENTRY_POINT,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": (
            "complete_car_lab.tasks.direct.complete_car.baseline.complete_car_stage0_cfg:CompleteCarStage0EnvCfg"
        ),
        "rsl_rl_cfg_entry_point": f"{RSL_RL_CFG_MODULE}:CompleteCarStage0PPORunnerCfg",
    },
)

gym.register(
    id="CompleteCar-Stage1",
    entry_point=ENV_ENTRY_POINT,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": (
            "complete_car_lab.tasks.direct.complete_car.baseline.complete_car_stage1_cfg:CompleteCarStage1EnvCfg"
        ),
        "rsl_rl_cfg_entry_point": f"{RSL_RL_CFG_MODULE}:CompleteCarStage1PPORunnerCfg",
    },
)

gym.register(
    id="CompleteCar-Stage2",
    entry_point=ENV_ENTRY_POINT,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": (
            "complete_car_lab.tasks.direct.complete_car.environment_adaptive.complete_car_stage2_cfg:"
            "CompleteCarStage2EnvCfg"
        ),
        "rsl_rl_cfg_entry_point": f"{RSL_RL_CFG_MODULE}:CompleteCarStage2PPORunnerCfg",
    },
)


__all__ = ["ENV_ENTRY_POINT", "RSL_RL_CFG_MODULE"]
