"""Convert a Stage0 PPO checkpoint into a Stage1 warm-start checkpoint."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch


DEFAULT_SOURCE = (
    "logs/rsl_rl/complete_car_stage0/best_baseline5/model_75.pt"
)
DEFAULT_OUTPUT = "logs/rsl_rl/complete_car_stage1/warmstart_best_baseline5_model75_terrain_features/model_0.pt"
DEFAULT_TARGET_ACTOR_OBS_DIM = 82
DEFAULT_TARGET_CRITIC_OBS_DIM = 660

OLD_BALL_JOINT_ORDER = ("spm1_z", "spm2_z", "spm1_y", "spm2_y", "spm1_x", "spm2_x")
NEW_BALL_JOINT_ORDER = ("spm1_z", "spm1_y", "spm1_x", "spm2_z", "spm2_y", "spm2_x")
ACTOR_OBS_NEW_FROM_OLD = (
    0,
    2,
    4,
    1,
    3,
    5,
    6,
    8,
    10,
    7,
    9,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    49,
    51,
    48,
    50,
    52,
    53,
    54,
    55,
    56,
    57,
    58,
    59,
    60,
    61,
    62,
    63,
    64,
    65,
    66,
    67,
    68,
    69,
    70,
    71,
    72,
    73,
    74,
    75,
    76,
    77,
    78,
    79,
    80,
    81,
)
ACTION_NEW_FROM_OLD = (0, 1, 2, 4, 6, 3, 5, 7)


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


def _permute_observation_channels(
    state_dict: dict[str, torch.Tensor],
    obs_new_from_old: tuple[int, ...],
) -> dict[str, torch.Tensor]:
    target_obs_dim = len(obs_new_from_old)
    index = torch.tensor(obs_new_from_old, dtype=torch.long)
    converted = dict(state_dict)
    for key in ("obs_normalizer._mean", "obs_normalizer._var", "obs_normalizer._std"):
        value = converted[key]
        if value.shape[1] != target_obs_dim:
            raise ValueError(f"{key} has obs dim {value.shape[1]}, expected {target_obs_dim}.")
        converted[key] = value.index_select(1, index)
    first_weight = converted["mlp.0.weight"]
    if first_weight.shape[1] != target_obs_dim:
        raise ValueError(f"mlp.0.weight has input dim {first_weight.shape[1]}, expected {target_obs_dim}.")
    converted["mlp.0.weight"] = first_weight.index_select(1, index)
    return converted


def _permute_actor_output_channels(
    state_dict: dict[str, torch.Tensor],
    action_new_from_old: tuple[int, ...],
) -> dict[str, torch.Tensor]:
    num_actions = len(action_new_from_old)
    index = torch.tensor(action_new_from_old, dtype=torch.long)
    converted = dict(state_dict)
    for key in ("distribution.log_std_param", "mlp.4.bias"):
        value = converted[key]
        if value.shape[0] != num_actions:
            raise ValueError(f"{key} has action dim {value.shape[0]}, expected {num_actions}.")
        converted[key] = value.index_select(0, index)
    final_weight = converted["mlp.4.weight"]
    if final_weight.shape[0] != num_actions:
        raise ValueError(f"mlp.4.weight has action dim {final_weight.shape[0]}, expected {num_actions}.")
    converted["mlp.4.weight"] = final_weight.index_select(0, index)
    return converted


def _apply_orderfix_io(
    actor_state_dict: dict[str, torch.Tensor],
    critic_state_dict: dict[str, torch.Tensor],
    target_actor_obs_dim: int,
    target_critic_obs_dim: int,
) -> tuple[dict[str, torch.Tensor], dict[str, torch.Tensor]]:
    if target_actor_obs_dim != len(ACTOR_OBS_NEW_FROM_OLD):
        raise ValueError(
            f"orderfix_io expects actor obs dim {len(ACTOR_OBS_NEW_FROM_OLD)}, got {target_actor_obs_dim}."
        )
    if target_critic_obs_dim < target_actor_obs_dim:
        raise ValueError("Critic obs dim must be at least actor obs dim for Stage1 orderfix_io.")
    critic_obs_new_from_old = ACTOR_OBS_NEW_FROM_OLD + tuple(range(target_actor_obs_dim, target_critic_obs_dim))
    actor_state_dict = _permute_observation_channels(actor_state_dict, ACTOR_OBS_NEW_FROM_OLD)
    actor_state_dict = _permute_actor_output_channels(actor_state_dict, ACTION_NEW_FROM_OLD)
    critic_state_dict = _permute_observation_channels(critic_state_dict, critic_obs_new_from_old)
    return actor_state_dict, critic_state_dict


def convert_checkpoint(
    source_checkpoint: Path,
    output_checkpoint: Path,
    target_actor_obs_dim: int,
    target_critic_obs_dim: int,
    *,
    apply_orderfix_io: bool,
) -> None:
    checkpoint = torch.load(source_checkpoint, map_location="cpu", weights_only=False)
    actor_state_dict = checkpoint["actor_state_dict"]
    critic_state_dict = checkpoint["critic_state_dict"]
    converted_actor, source_actor_dim = _convert_model_state_dict(actor_state_dict, target_actor_obs_dim)
    converted_critic, source_critic_dim = _convert_model_state_dict(critic_state_dict, target_critic_obs_dim)
    if apply_orderfix_io:
        converted_actor, converted_critic = _apply_orderfix_io(
            converted_actor,
            converted_critic,
            target_actor_obs_dim,
            target_critic_obs_dim,
        )

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
            "ball_joint_order_fix": bool(apply_orderfix_io),
            "ball_joint_order_fix_io": bool(apply_orderfix_io),
            "source_joint_order_assumption": "legacy_implicit_order" if apply_orderfix_io else "current_preserve_order",
            "old_ball_order": list(OLD_BALL_JOINT_ORDER),
            "new_ball_order": list(NEW_BALL_JOINT_ORDER),
            "actor_obs_new_from_old": list(ACTOR_OBS_NEW_FROM_OLD) if apply_orderfix_io else None,
            "action_new_from_old": list(ACTION_NEW_FROM_OLD) if apply_orderfix_io else None,
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
    parser.add_argument(
        "--apply_orderfix_io",
        action="store_true",
        default=False,
        help=(
            "Apply the legacy best_baseline_2 old->new joint-order permutation. "
            "Do not use this for Stage0 checkpoints trained after preserve_order=True."
        ),
    )
    args = parser.parse_args()

    convert_checkpoint(
        source_checkpoint=args.source_checkpoint.expanduser().resolve(),
        output_checkpoint=args.output_checkpoint.expanduser().resolve(),
        target_actor_obs_dim=args.target_actor_obs_dim,
        target_critic_obs_dim=args.target_critic_obs_dim,
        apply_orderfix_io=args.apply_orderfix_io,
    )


if __name__ == "__main__":
    main()
