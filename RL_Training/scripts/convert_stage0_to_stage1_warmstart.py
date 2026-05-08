"""Convert a Stage0 PPO checkpoint into a Stage1 warm-start checkpoint."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch


DEFAULT_SOURCE = (
    "logs/rsl_rl/complete_car_stage0/2026-04-28_15-28-38_best_baseline_2/model_699.pt"
)
DEFAULT_OUTPUT = "logs/rsl_rl/complete_car_stage1/warmstart_best_baseline_2_terrain_features/model_0.pt"
DEFAULT_TARGET_ACTOR_OBS_DIM = 82
DEFAULT_TARGET_CRITIC_OBS_DIM = 660


def _expand_obs_vector(value: torch.Tensor, target_obs_dim: int, *, fill_value: float) -> torch.Tensor:
    if value.ndim != 2 or value.shape[0] != 1:
        raise ValueError(f"Expected normalizer tensor with shape (1, D), got {tuple(value.shape)}.")
    source_obs_dim = value.shape[1]
    if source_obs_dim > target_obs_dim:
        raise ValueError(f"Source obs dim {source_obs_dim} is larger than target obs dim {target_obs_dim}.")
    expanded = value.new_full((1, target_obs_dim), fill_value)
    expanded[:, :source_obs_dim] = value
    return expanded


def _expand_first_linear_weight(
    value: torch.Tensor,
    source_obs_dim: int,
    target_obs_dim: int,
) -> torch.Tensor:
    if value.ndim != 2 or value.shape[1] != source_obs_dim:
        raise ValueError(
            f"Expected first linear weight with input dim {source_obs_dim}, got shape {tuple(value.shape)}."
        )
    expanded = value.new_zeros((value.shape[0], target_obs_dim))
    expanded[:, :source_obs_dim] = value
    return expanded


def _convert_model_state_dict(
    state_dict: dict[str, torch.Tensor],
    target_obs_dim: int,
) -> tuple[dict[str, torch.Tensor], int]:
    source_obs_dim = state_dict["obs_normalizer._mean"].shape[1]
    converted = dict(state_dict)
    converted["obs_normalizer._mean"] = _expand_obs_vector(
        state_dict["obs_normalizer._mean"],
        target_obs_dim,
        fill_value=0.0,
    )
    converted["obs_normalizer._var"] = _expand_obs_vector(
        state_dict["obs_normalizer._var"],
        target_obs_dim,
        fill_value=1.0,
    )
    converted["obs_normalizer._std"] = _expand_obs_vector(
        state_dict["obs_normalizer._std"],
        target_obs_dim,
        fill_value=1.0,
    )
    converted["mlp.0.weight"] = _expand_first_linear_weight(
        state_dict["mlp.0.weight"],
        source_obs_dim,
        target_obs_dim,
    )
    return converted, source_obs_dim


def convert_checkpoint(
    source_checkpoint: Path,
    output_checkpoint: Path,
    target_actor_obs_dim: int,
    target_critic_obs_dim: int,
) -> None:
    checkpoint = torch.load(source_checkpoint, map_location="cpu", weights_only=False)
    actor_state_dict = checkpoint["actor_state_dict"]
    critic_state_dict = checkpoint["critic_state_dict"]
    converted_actor, source_actor_dim = _convert_model_state_dict(actor_state_dict, target_actor_obs_dim)
    converted_critic, source_critic_dim = _convert_model_state_dict(critic_state_dict, target_critic_obs_dim)

    converted = {
        "actor_state_dict": converted_actor,
        "critic_state_dict": converted_critic,
        "iter": 0,
        "infos": {
            "warmstart": True,
            "source_checkpoint": str(source_checkpoint),
            "source_actor_obs_dim": int(source_actor_dim),
            "source_critic_obs_dim": int(source_critic_dim),
            "target_actor_obs_dim": int(target_actor_obs_dim),
            "target_critic_obs_dim": int(target_critic_obs_dim),
            "source_iter": int(checkpoint.get("iter", -1)),
        },
    }
    output_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save(converted, output_checkpoint)
    print(f"source_checkpoint={source_checkpoint}")
    print(f"output_checkpoint={output_checkpoint}")
    print(f"source_actor_obs_dim={source_actor_dim}")
    print(f"source_critic_obs_dim={source_critic_dim}")
    print(f"target_actor_obs_dim={target_actor_obs_dim}")
    print(f"target_critic_obs_dim={target_critic_obs_dim}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source_checkpoint", type=Path, default=Path(DEFAULT_SOURCE))
    parser.add_argument("--output_checkpoint", type=Path, default=Path(DEFAULT_OUTPUT))
    parser.add_argument(
        "--target_actor_obs_dim",
        type=int,
        default=DEFAULT_TARGET_ACTOR_OBS_DIM,
        help="Target Stage1 actor observation dimension. Current terrain-feature Stage1 default is 82.",
    )
    parser.add_argument(
        "--target_critic_obs_dim",
        type=int,
        default=DEFAULT_TARGET_CRITIC_OBS_DIM,
        help="Target Stage1 critic observation dimension. Current terrain-feature Stage1 default is 660.",
    )
    args = parser.parse_args()

    convert_checkpoint(
        source_checkpoint=args.source_checkpoint.expanduser().resolve(),
        output_checkpoint=args.output_checkpoint.expanduser().resolve(),
        target_actor_obs_dim=args.target_actor_obs_dim,
        target_critic_obs_dim=args.target_critic_obs_dim,
    )


if __name__ == "__main__":
    main()
