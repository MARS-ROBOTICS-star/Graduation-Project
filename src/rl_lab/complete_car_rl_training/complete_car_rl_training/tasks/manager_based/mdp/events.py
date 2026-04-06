# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Event term implementations and aliases."""

from __future__ import annotations

from collections.abc import Sequence

import torch

from isaaclab.envs.mdp import reset_joints_by_offset, reset_root_state_uniform

from ..stage1_terrain import (
    STAGE1_TERRAIN_CLASS_GAP,
    STAGE1_TERRAIN_CLASS_OTHER,
    STAGE1_TERRAIN_CLASS_STEP,
)


def _sample_uniform(value_range: tuple[float, float], shape: tuple[int, ...], device: torch.device) -> torch.Tensor:
    low, high = value_range
    return torch.empty(shape, device=device).uniform_(low, high)


def apply_stage1_spawn_offsets(
    env,
    env_ids: Sequence[int] | torch.Tensor,
    *,
    step_spawn_back_range: tuple[float, float],
    gap_spawn_back_range: tuple[float, float],
    other_spawn_xy_range: tuple[float, float],
) -> None:
    """Apply terrain-class-specific spawn offsets after reset."""
    if not isinstance(env_ids, torch.Tensor):
        env_ids = torch.tensor(env_ids, device=env.device, dtype=torch.long)
    elif env_ids.numel() == 0:
        return

    robot = env.scene["robot"]
    root_pos = robot.data.root_pos_w.clone()

    default_root_state = robot.data.default_root_state
    root_quat = getattr(robot.data, "root_quat_w", default_root_state[:, 3:7]).clone()
    root_lin_vel = getattr(robot.data, "root_lin_vel_w", default_root_state[:, 7:10]).clone()
    root_ang_vel = getattr(robot.data, "root_ang_vel_w", default_root_state[:, 10:13]).clone()

    env_classes = env._terrain_classes[env_ids]
    env_ids_step = env_ids[env_classes == STAGE1_TERRAIN_CLASS_STEP]
    env_ids_gap = env_ids[env_classes == STAGE1_TERRAIN_CLASS_GAP]
    env_ids_other = env_ids[env_classes == STAGE1_TERRAIN_CLASS_OTHER]

    if len(env_ids_step) > 0:
        root_pos[env_ids_step, 0:1] -= _sample_uniform(step_spawn_back_range, (len(env_ids_step), 1), env.device)
    if len(env_ids_gap) > 0:
        root_pos[env_ids_gap, 0:1] -= _sample_uniform(gap_spawn_back_range, (len(env_ids_gap), 1), env.device)
    if len(env_ids_other) > 0:
        root_pos[env_ids_other, :2] += _sample_uniform(other_spawn_xy_range, (len(env_ids_other), 2), env.device)

    root_pose = torch.cat((root_pos, root_quat), dim=1)
    root_velocity = torch.cat((root_lin_vel, root_ang_vel), dim=1)
    robot.write_root_pose_to_sim(root_pose)
    robot.write_root_velocity_to_sim(root_velocity)


__all__ = [
    "apply_stage1_spawn_offsets",
    "reset_joints_by_offset",
    "reset_root_state_uniform",
]
