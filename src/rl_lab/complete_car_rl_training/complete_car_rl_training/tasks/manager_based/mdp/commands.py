# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Custom command terms for the complete-car manager-based RL task."""

from __future__ import annotations

from collections.abc import Sequence

import torch

from isaaclab.envs.mdp.commands.commands_cfg import UniformVelocityCommandCfg as _UniformVelocityCommandCfg
from isaaclab.envs.mdp.commands.velocity_command import UniformVelocityCommand
from isaaclab.utils import configclass


class CompleteCarUniformVelocityCommand(UniformVelocityCommand):
    """Velocity command with extra root-height metrics for logging."""

    def __init__(self, cfg: _UniformVelocityCommandCfg, env):
        super().__init__(cfg, env)
        self._root_height_sum = torch.zeros(self.num_envs, device=self.device)
        self._root_height_min = torch.full((self.num_envs,), float("inf"), device=self.device)

    def _update_metrics(self):
        super()._update_metrics()
        root_height = self.robot.data.root_pos_w[:, 2]
        self._root_height_sum += root_height
        self._root_height_min = torch.minimum(self._root_height_min, root_height)

    def _resample_command(self, env_ids: Sequence[int]):
        """Sample commands with optional curvature-based yaw generation."""
        if self.cfg.curvature_range is None:
            return super()._resample_command(env_ids)

        r = torch.empty(len(env_ids), device=self.device)

        lin_vel_x = r.uniform_(*self.cfg.ranges.lin_vel_x)
        self.vel_command_b[env_ids, 0] = lin_vel_x
        self.vel_command_b[env_ids, 1] = r.uniform_(*self.cfg.ranges.lin_vel_y)

        curvature = r.uniform_(*self.cfg.curvature_range)
        yaw_vel = lin_vel_x * curvature
        yaw_vel = torch.where(
            torch.abs(lin_vel_x) < self.cfg.turn_lin_vel_threshold, torch.zeros_like(yaw_vel), yaw_vel
        )
        self.vel_command_b[env_ids, 2] = yaw_vel

        if self.cfg.heading_command:
            self.heading_target[env_ids] = r.uniform_(*self.cfg.ranges.heading)
            self.is_heading_env[env_ids] = r.uniform_(0.0, 1.0) <= self.cfg.rel_heading_envs

        self.is_standing_env[env_ids] = r.uniform_(0.0, 1.0) <= self.cfg.rel_standing_envs

    def reset(self, env_ids: Sequence[int] | None = None) -> dict[str, float]:
        """Reset the command generator and log velocity plus root-height metrics."""
        if env_ids is None:
            env_ids = slice(None)

        extras = {}
        for metric_name, metric_value in self.metrics.items():
            extras[metric_name] = torch.mean(metric_value[env_ids]).item()
            metric_value[env_ids] = 0.0

        episode_lengths = self._env.episode_length_buf[env_ids].float().clamp(min=1.0)
        root_height_mean = self._root_height_sum[env_ids] / episode_lengths
        current_root_height = self.robot.data.root_pos_w[env_ids, 2]
        root_height_min = torch.where(torch.isfinite(self._root_height_min[env_ids]), self._root_height_min[env_ids], current_root_height)

        extras["root_height_mean"] = torch.mean(root_height_mean).item()
        extras["root_height_min"] = torch.mean(root_height_min).item()

        self._root_height_sum[env_ids] = 0.0
        self._root_height_min[env_ids] = float("inf")

        self.command_counter[env_ids] = 0
        self._resample(env_ids)
        return extras


@configclass
class UniformVelocityCommandCfg(_UniformVelocityCommandCfg):
    """Complete-car velocity command config with root-height logging."""

    class_type: type = CompleteCarUniformVelocityCommand
    curvature_range: tuple[float, float] | None = None
    turn_lin_vel_threshold: float = 0.0
