"""RSL-RL PPO 配置入口。"""

from __future__ import annotations

from dataclasses import MISSING
from typing import Literal

from isaaclab.utils import configclass


@configclass
class LocalGaussianDistributionCfg:
    class_name: str = "GaussianDistribution"
    init_std: float = MISSING
    std_type: Literal["scalar", "log"] = "scalar"


@configclass
class LocalMlpModelCfg:
    class_name: str = "MLPModel"
    hidden_dims: list[int] = MISSING
    activation: str = MISSING
    obs_normalization: bool = True
    distribution_cfg: LocalGaussianDistributionCfg | None = None


@configclass
class LocalPpoAlgorithmCfg:
    class_name: str = "PPO"
    num_learning_epochs: int = MISSING
    num_mini_batches: int = MISSING
    learning_rate: float = MISSING
    schedule: str = MISSING
    gamma: float = MISSING
    lam: float = MISSING
    entropy_coef: float = MISSING
    desired_kl: float = MISSING
    max_grad_norm: float = MISSING
    value_loss_coef: float = MISSING
    use_clipped_value_loss: bool = MISSING
    clip_param: float = MISSING


@configclass
class LocalOnPolicyRunnerCfg:
    class_name: str = "OnPolicyRunner"
    seed: int = 42
    device: str = "cuda:0"
    num_steps_per_env: int = MISSING
    max_iterations: int = MISSING
    obs_groups: dict[str, list[str]] = MISSING
    clip_actions: float | None = None
    check_for_nan: bool = True
    save_interval: int = MISSING
    experiment_name: str = MISSING
    run_name: str = ""
    logger: Literal["tensorboard", "neptune", "wandb"] = "tensorboard"
    neptune_project: str = "complete_car"
    wandb_project: str = "complete_car"
    resume: bool = False
    load_run: str = ".*"
    load_checkpoint: str = "model_.*.pt"
    actor: LocalMlpModelCfg = MISSING
    critic: LocalMlpModelCfg = MISSING
    algorithm: LocalPpoAlgorithmCfg = MISSING


@configclass
class CompleteCarBasePPORunnerCfg(LocalOnPolicyRunnerCfg):
    seed = 1
    num_steps_per_env = 96
    max_iterations = 1000
    save_interval = 200
    experiment_name = "complete_car_direct"
    run_name = ""
    obs_groups = {"actor": ["actor"], "critic": ["critic"]}
    resume = False
    load_run = ".*"
    load_checkpoint = "model_.*.pt"
    clip_actions = 1.0

    actor = LocalMlpModelCfg(
        hidden_dims=[256, 128, 64],
        activation="elu",
        obs_normalization=True,
        distribution_cfg=LocalGaussianDistributionCfg(init_std=0.4, std_type="scalar"),
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
        entropy_coef=0.003,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=3.0e-4,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
    )


@configclass
class CompleteCarStage0PPORunnerCfg(CompleteCarBasePPORunnerCfg):
    experiment_name = "complete_car_stage0"


@configclass
class CompleteCarStage1PPORunnerCfg(CompleteCarBasePPORunnerCfg):
    experiment_name = "complete_car_stage1"


@configclass
class CompleteCarStage2PPORunnerCfg(CompleteCarBasePPORunnerCfg):
    experiment_name = "complete_car_stage2"
