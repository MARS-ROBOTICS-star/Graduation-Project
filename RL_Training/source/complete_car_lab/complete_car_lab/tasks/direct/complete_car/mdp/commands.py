"""命令采样与命令时钟推进。"""

from __future__ import annotations

import torch

from ..kinematics.wheel_speed_allocator import PLANAR_COMMAND_TRANSFORM
from ..utils.math_utils import sample_uniform_tensor


def transform_planar_command_torch(planar_command: torch.Tensor) -> torch.Tensor:
    planar_command = (
        planar_command
        if torch.is_tensor(planar_command)
        else torch.as_tensor(planar_command)
    )
    if planar_command.ndim == 1:
        if planar_command.shape[0] != 2:
            raise ValueError("planar_command must have shape (2,).")
        planar_command_2d = planar_command.reshape(1, -1)
        squeeze_output = True
    elif planar_command.ndim == 2 and planar_command.shape[1] == 2:
        planar_command_2d = planar_command
        squeeze_output = False
    else:
        raise ValueError("planar_command must have shape (N, 2).")

    transform = planar_command_2d.new_tensor(PLANAR_COMMAND_TRANSFORM)
    planar_command_xyz = torch.zeros((planar_command_2d.shape[0], 3), device=planar_command_2d.device, dtype=planar_command_2d.dtype)
    planar_command_xyz[:, 0] = planar_command_2d[:, 0]
    planar_command_xyz[:, 2] = planar_command_2d[:, 1]
    transformed_xyz = planar_command_xyz @ transform.transpose(0, 1)
    transformed = torch.stack((transformed_xyz[:, 0], transformed_xyz[:, 2]), dim=1)
    return transformed.reshape(-1) if squeeze_output else transformed


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
    commands[env_ids, 1] = sample_uniform_tensor(cfg.ranges.ang_vel_yaw, (env_ids.numel(),), device)
    commands[env_ids] = transform_planar_command_torch(commands[env_ids])

    if cfg.rel_standing_envs > 0.0:
        standing_mask = torch.rand(env_ids.numel(), device=device) < cfg.rel_standing_envs
        commands[env_ids[standing_mask]] = 0.0
    if cfg.zero_command:
        commands[env_ids] = 0.0

    command_time_left[env_ids] = cfg.resampling_time


def step_command_timer(command_time_left: torch.Tensor, step_dt: float) -> torch.Tensor:
    command_time_left -= step_dt
    return torch.nonzero(command_time_left <= 0.0, as_tuple=False).flatten()
