"""reset 逻辑拆分。"""

from __future__ import annotations

import torch

from ..assets.robot_cfg import BALL_JOINT_NAMES, WHEEL_JOINT_NAMES
from ..utils.math_utils import quat_mul, sample_uniform_tensor, yaw_quaternion
from .randomization import apply_joint_position_noise


def build_root_state(cfg, robot, scene, terrain_runtime, env_ids: torch.Tensor, device: torch.device) -> torch.Tensor:
    root_state = robot.data.default_root_state[env_ids].clone()
    root_state[:, :3] += scene.env_origins[env_ids]
    root_state[:, 0] += sample_uniform_tensor(cfg.resets.root_x_range, (env_ids.numel(),), device)
    root_state[:, 1] += sample_uniform_tensor(cfg.resets.root_y_range, (env_ids.numel(),), device)
    yaw_delta = sample_uniform_tensor(cfg.resets.root_yaw_range, (env_ids.numel(),), device)
    root_state[:, 3:7] = quat_mul(root_state[:, 3:7], yaw_quaternion(yaw_delta))
    root_state[:, 7:10] = torch.tensor(cfg.resets.root_lin_vel, device=device).unsqueeze(0).repeat(env_ids.numel(), 1)
    root_state[:, 10:13] = torch.tensor(cfg.resets.root_ang_vel, device=device).unsqueeze(0).repeat(env_ids.numel(), 1)
    if terrain_runtime is not None:
        root_state = terrain_runtime.apply_spawn_offsets(root_state, env_ids)
    return root_state


def build_joint_state(cfg, robot, ball_joint_ids, wheel_joint_ids, env_ids: torch.Tensor, device: torch.device):
    joint_pos = robot.data.default_joint_pos[env_ids].clone()
    joint_vel = robot.data.default_joint_vel[env_ids].clone()
    joint_pos[:, ball_joint_ids] += sample_uniform_tensor(
        cfg.resets.ball_joint_pos_range,
        (env_ids.numel(), len(BALL_JOINT_NAMES)),
        device,
    )
    joint_vel[:, ball_joint_ids] += sample_uniform_tensor(
        cfg.resets.ball_joint_vel_range,
        (env_ids.numel(), len(BALL_JOINT_NAMES)),
        device,
    )
    joint_pos[:, wheel_joint_ids] += sample_uniform_tensor(
        cfg.resets.wheel_joint_pos_range,
        (env_ids.numel(), len(WHEEL_JOINT_NAMES)),
        device,
    )
    joint_vel[:, wheel_joint_ids] += sample_uniform_tensor(
        cfg.resets.wheel_joint_vel_range,
        (env_ids.numel(), len(WHEEL_JOINT_NAMES)),
        device,
    )
    return apply_joint_position_noise(cfg, joint_pos), joint_vel
