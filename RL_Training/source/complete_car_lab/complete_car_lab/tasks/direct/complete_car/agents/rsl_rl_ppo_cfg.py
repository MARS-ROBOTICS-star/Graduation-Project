"""RSL-RL PPO 配置入口。"""

from __future__ import annotations

from dataclasses import MISSING
from typing import Literal

from isaaclab.utils import configclass


@configclass
class LocalSquashedGaussianDistributionCfg:
    class_name: str = "SquashedGaussianDistribution"
    init_std: float = MISSING
    log_std_min: float = -5.0
    log_std_max: float = 2.0


@configclass
class LocalMlpModelCfg:
    class_name: str = "MLPModel"
    hidden_dims: list[int] = MISSING
    activation: str = MISSING
    obs_normalization: bool = True
    distribution_cfg: LocalSquashedGaussianDistributionCfg | None = None


@configclass
class LocalPpoAlgorithmCfg:
    class_name: str = "PPO"
    num_learning_epochs: int = MISSING
    num_mini_batches: int = MISSING
    learning_rate: float = MISSING
    adam_eps: float = MISSING
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
    num_steps_per_env = 512
    max_iterations = 700
    save_interval = 25
    experiment_name = "complete_car_direct"
    run_name = ""
    obs_groups = {"actor": ["actor"], "critic": ["critic"]}
    resume = False
    load_run = ".*"
    load_checkpoint = "model_.*.pt"
    clip_actions = None

    actor = LocalMlpModelCfg(
        hidden_dims=[256, 256],
        activation="relu",
        obs_normalization=True,
        distribution_cfg=LocalSquashedGaussianDistributionCfg(init_std=0.20, log_std_min=-4.0, log_std_max=0.0),
    )
    critic = LocalMlpModelCfg(
        hidden_dims=[256, 256],
        activation="relu",
        obs_normalization=True,
        distribution_cfg=None,
    )
    algorithm = LocalPpoAlgorithmCfg(
        value_loss_coef=0.5,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=5.0e-4,
        num_learning_epochs=5,
        num_mini_batches=16,
        learning_rate=1.0e-4,
        adam_eps=1.0e-5,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.008,
        max_grad_norm=0.5,
    )


@configclass
class CompleteCarStage0PPORunnerCfg(CompleteCarBasePPORunnerCfg):
    experiment_name = "complete_car_stage0"
    run_name = "best_baseline"


@configclass
class CompleteCarStage1PPORunnerCfg(CompleteCarBasePPORunnerCfg):
    experiment_name = "complete_car_stage1"
    algorithm = LocalPpoAlgorithmCfg(
        value_loss_coef=0.5,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=5.0e-4,
        num_learning_epochs=3,
        num_mini_batches=16,
        learning_rate=1.0e-5,
        adam_eps=1.0e-5,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.008,
        max_grad_norm=0.5,
    )


@configclass
class CompleteCarStage2PPORunnerCfg(CompleteCarBasePPORunnerCfg):
    experiment_name = "complete_car_stage2"
