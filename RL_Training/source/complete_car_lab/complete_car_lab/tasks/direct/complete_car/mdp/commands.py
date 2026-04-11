"""命令采样与命令时钟推进。"""

from __future__ import annotations

import torch

from ..utils.math_utils import sample_uniform_tensor


def resample_velocity_commands(
    commands: torch.Tensor,
    command_time_left: torch.Tensor,
    env_ids: torch.Tensor,
    cfg,
) -> None:
    if env_ids.numel() == 0:
        return

    device = commands.device
    commands[env_ids, 0] = sample_uniform_tensor(cfg.ranges.lin_vel_x, (env_ids.numel(),), device)
    commands[env_ids, 1] = sample_uniform_tensor(cfg.ranges.lin_vel_y, (env_ids.numel(),), device)
    commands[env_ids, 2] = sample_uniform_tensor(cfg.ranges.ang_vel_yaw, (env_ids.numel(),), device)
    commands[env_ids, 3] = sample_uniform_tensor(cfg.ranges.heading, (env_ids.numel(),), device)

    if cfg.rel_standing_envs > 0.0:
        standing_mask = torch.rand(env_ids.numel(), device=device) < cfg.rel_standing_envs
        commands[env_ids[standing_mask]] = 0.0
    if cfg.zero_command:
        commands[env_ids] = 0.0

    command_time_left[env_ids] = cfg.resampling_time


def step_command_timer(command_time_left: torch.Tensor, step_dt: float) -> torch.Tensor:
    command_time_left -= step_dt
    return torch.nonzero(command_time_left <= 0.0, as_tuple=False).flatten()
