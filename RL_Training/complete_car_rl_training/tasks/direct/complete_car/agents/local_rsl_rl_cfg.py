"""Project-local RSL-RL config classes for direct complete-car training."""

from __future__ import annotations

from dataclasses import MISSING
from typing import Literal

from isaaclab.utils import configclass


@configclass
class LocalGaussianDistributionCfg:
    """Local copy of the Gaussian policy distribution config."""

    class_name: str = "GaussianDistribution"
    init_std: float = MISSING
    std_type: Literal["scalar", "log"] = "scalar"


@configclass
class LocalMlpModelCfg:
    """Local copy of the MLP model config used by RSL-RL."""

    class_name: str = "MLPModel"
    hidden_dims: list[int] = MISSING
    activation: str = MISSING
    obs_normalization: bool = False
    distribution_cfg: LocalGaussianDistributionCfg | None = None


@configclass
class LocalPpoAlgorithmCfg:
    """Project-local PPO algorithm config."""

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
    """Project-local on-policy runner config."""

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
    neptune_project: str = "isaaclab"
    wandb_project: str = "isaaclab"
    resume: bool = False
    load_run: str = ".*"
    load_checkpoint: str = "model_.*.pt"
    actor: LocalMlpModelCfg = MISSING
    critic: LocalMlpModelCfg = MISSING
    algorithm: LocalPpoAlgorithmCfg = MISSING


__all__ = [
    "LocalGaussianDistributionCfg",
    "LocalMlpModelCfg",
    "LocalOnPolicyRunnerCfg",
    "LocalPpoAlgorithmCfg",
]
