# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Reward term implementations and aliases."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from isaaclab.envs.mdp import (
    action_rate_l2,
    ang_vel_xy_l2,
    flat_orientation_l2,
    is_terminated,
    joint_deviation_l1,
    joint_vel_l1,
    lin_vel_z_l2,
    track_ang_vel_z_exp,
    track_lin_vel_xy_exp,
)
from isaaclab.assets import Articulation
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils.math import wrap_to_pi

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


def joint_pos_target_l2(env: ManagerBasedRLEnv, target: float, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    """Penalize joint position deviation from a target value."""
    asset: Articulation = env.scene[asset_cfg.name]
    joint_pos = wrap_to_pi(asset.data.joint_pos[:, asset_cfg.joint_ids])
    return torch.sum(torch.square(joint_pos - target), dim=1)


def chassis_collision(
    env: ManagerBasedRLEnv,
    sensor_names: tuple[str, ...],
    threshold: float = 5.0,
) -> torch.Tensor:
    """Binary penalty for chassis collisions detected by contact sensors."""
    collision_mask = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
    for sensor_name in sensor_names:
        sensor = env.scene[sensor_name]
        net_forces_w = sensor.data.net_forces_w
        if net_forces_w is None:
            continue
        contact_force_norm = torch.linalg.vector_norm(net_forces_w, dim=-1)
        if contact_force_norm.ndim > 1:
            contact_force_norm = torch.amax(contact_force_norm, dim=1)
        collision_mask |= contact_force_norm > threshold
    return collision_mask.float()


__all__ = [
    "action_rate_l2",
    "ang_vel_xy_l2",
    "chassis_collision",
    "flat_orientation_l2",
    "is_terminated",
    "joint_deviation_l1",
    "joint_pos_target_l2",
    "joint_vel_l1",
    "lin_vel_z_l2",
    "track_ang_vel_z_exp",
    "track_lin_vel_xy_exp",
]
