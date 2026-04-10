"""Command sampling helpers for the direct complete-car task."""

from __future__ import annotations

import torch

from .utils import sample_uniform_tensor


def resample_velocity_commands(
    commands: torch.Tensor,
    command_time_left: torch.Tensor,
    env_ids: torch.Tensor,
    cfg,
) -> None:
    if env_ids.numel() == 0:
        return

    device = commands.device
    lin_vel_x = sample_uniform_tensor(cfg.ranges.lin_vel_x, (env_ids.numel(),), device)
    lin_vel_y = sample_uniform_tensor(cfg.ranges.lin_vel_y, (env_ids.numel(),), device)
    ang_vel_yaw = sample_uniform_tensor(cfg.ranges.ang_vel_yaw, (env_ids.numel(),), device)
    heading = sample_uniform_tensor(cfg.ranges.heading, (env_ids.numel(),), device)

    commands[env_ids, 0] = lin_vel_x
    commands[env_ids, 1] = lin_vel_y
    commands[env_ids, 2] = ang_vel_yaw
    commands[env_ids, 3] = heading

    if cfg.rel_standing_envs > 0.0:
        standing_mask = torch.rand(env_ids.numel(), device=device) < cfg.rel_standing_envs
        commands[env_ids[standing_mask]] = 0.0

    if cfg.zero_command:
        commands[env_ids] = 0.0

    command_time_left[env_ids] = cfg.resampling_time


def step_command_timer(command_time_left: torch.Tensor, step_dt: float) -> torch.Tensor:
    command_time_left -= step_dt
    return torch.nonzero(command_time_left <= 0.0, as_tuple=False).flatten()


__all__ = ["resample_velocity_commands", "step_command_timer"]
