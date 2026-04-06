# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Curriculum term implementations and aliases."""

from __future__ import annotations

from collections.abc import Sequence

import torch

from isaaclab.envs.mdp import modify_env_param, modify_reward_weight, modify_term_cfg


def update_stage1_terrain_curriculum(
    env,
    env_ids: Sequence[int] | torch.Tensor,
    *,
    command_name: str,
    move_up_distance_ratio: float,
    move_down_command_ratio: float,
) -> dict[str, float] | None:
    """Update terrain levels and env origins using the current runtime terrain state."""
    if not getattr(env.cfg.stage1, "curriculum", False):
        return None
    if getattr(env.cfg.stage1, "flat_only_reset", False):
        return None
    if not getattr(env, "_terrain_curriculum_ready", False):
        return None

    if not isinstance(env_ids, torch.Tensor):
        env_ids = torch.tensor(env_ids, device=env.device, dtype=torch.long)
    elif env_ids.numel() == 0:
        return None

    root_pos = env.scene["robot"].data.root_pos_w[env_ids]
    env_origins = env.scene.env_origins[env_ids]
    distance = torch.norm(root_pos[:, :2] - env_origins[:, :2], dim=1)
    commands = env.command_manager.get_command(command_name)[env_ids]
    required_distance = torch.norm(commands[:, :2], dim=1) * env.cfg.episode_length_s * move_down_command_ratio

    move_up = distance > env._terrain_cfg.terrain_length * move_up_distance_ratio
    move_down = (distance < required_distance) & ~move_up

    env._terrain_levels[env_ids] += move_up.to(torch.long) - move_down.to(torch.long)
    env._terrain_levels[env_ids] = torch.where(
        env._terrain_levels[env_ids] >= env._max_terrain_level,
        torch.randint_like(env._terrain_levels[env_ids], env._max_terrain_level),
        env._terrain_levels[env_ids].clamp_(min=0),
    )
    env.sync_env_origins_from_terrain_state(env_ids)

    return {
        "terrain_level": float(torch.mean(env._terrain_levels.float()).item()),
        "move_up_ratio": float(torch.mean(move_up.float()).item()),
        "move_down_ratio": float(torch.mean(move_down.float()).item()),
    }


__all__ = [
    "modify_env_param",
    "modify_reward_weight",
    "modify_term_cfg",
    "update_stage1_terrain_curriculum",
]
