# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""RSL-RL configs for the direct complete-car task family."""

from isaaclab.utils import configclass

from .local_rsl_rl_cfg import LocalGaussianDistributionCfg, LocalMlpModelCfg, LocalOnPolicyRunnerCfg, LocalPpoAlgorithmCfg


@configclass
class CompleteCarPPoCfg(LocalOnPolicyRunnerCfg):
    seed = 1

    num_steps_per_env = 24
    max_iterations = 500
    save_interval = 100
    experiment_name = "complete_car_direct"
    run_name = ""
    obs_groups = {
        "actor": ["policy"],
        "critic": ["policy"],
    }
    resume = False
    load_run = -1
    load_checkpoint = -1

    actor = LocalMlpModelCfg(
        hidden_dims=[256, 128, 64],
        activation="elu",
        obs_normalization=True,
        distribution_cfg=LocalGaussianDistributionCfg(init_std=1.0, std_type="scalar"),
    )
    critic = LocalMlpModelCfg(
        hidden_dims=[256, 128, 64],
        activation="elu",
        obs_normalization=True,
        distribution_cfg=None,
    )
    algorithm = LocalPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.005,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=3.0e-3,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
    )


@configclass
class Stage0FlatPPoCfg(CompleteCarPPoCfg):
    experiment_name = "complete_car_stage0_flat_direct"


@configclass
class Stage1TerrainPPoCfg(CompleteCarPPoCfg):
    experiment_name = "complete_car_stage1_terrain_direct"


@configclass
class Stage2PerceptionPPoCfg(CompleteCarPPoCfg):
    experiment_name = "complete_car_stage2_perception_direct"


__all__ = [
    "CompleteCarPPoCfg",
    "Stage0FlatPPoCfg",
    "Stage1TerrainPPoCfg",
    "Stage2PerceptionPPoCfg",
]
