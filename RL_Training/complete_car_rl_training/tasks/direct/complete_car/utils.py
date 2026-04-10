"""Small tensor utilities shared by the direct complete-car task."""

from __future__ import annotations

import torch

from .assets.robot_cfg import BALL_JOINT_NAMES, WHEEL_JOINT_NAMES


def sample_uniform_tensor(value_range: tuple[float, float], shape: tuple[int, ...], device: torch.device) -> torch.Tensor:
    low, high = value_range
    return torch.empty(shape, device=device).uniform_(low, high)


def wrap_to_pi_tensor(angles: torch.Tensor) -> torch.Tensor:
    return torch.atan2(torch.sin(angles), torch.cos(angles))


def yaw_quaternion(yaw: torch.Tensor) -> torch.Tensor:
    quat = torch.zeros((yaw.shape[0], 4), device=yaw.device, dtype=yaw.dtype)
    quat[:, 0] = torch.cos(0.5 * yaw)
    quat[:, 3] = torch.sin(0.5 * yaw)
    return quat


def quat_mul(q0: torch.Tensor, q1: torch.Tensor) -> torch.Tensor:
    w0, x0, y0, z0 = q0.unbind(dim=-1)
    w1, x1, y1, z1 = q1.unbind(dim=-1)
    return torch.stack(
        (
            w0 * w1 - x0 * x1 - y0 * y1 - z0 * z1,
            w0 * x1 + x0 * w1 + y0 * z1 - z0 * y1,
            w0 * y1 - x0 * z1 + y0 * w1 + z0 * x1,
            w0 * z1 + x0 * y1 - y0 * x1 + z0 * w1,
        ),
        dim=-1,
    )


def update_history(history_buffer: torch.Tensor | None, current_obs: torch.Tensor) -> torch.Tensor:
    if history_buffer is None:
        return current_obs
    history_buffer[:, :-1] = history_buffer[:, 1:].clone()
    history_buffer[:, -1] = current_obs
    return history_buffer.reshape(current_obs.shape[0], -1)


def compute_policy_obs_dim(cfg) -> int:
    proprio_dim = 3 + 3 + 3 + len(BALL_JOINT_NAMES) + len(BALL_JOINT_NAMES) + len(WHEEL_JOINT_NAMES) + 3 + (
        len(BALL_JOINT_NAMES) + len(WHEEL_JOINT_NAMES)
    )
    height_dim = len(cfg.terrain.measured_points_x) * len(cfg.terrain.measured_points_y) if cfg.terrain.measure_heights else 0
    return proprio_dim + height_dim + cfg.sensors.policy_feature_dim


__all__ = [
    "compute_policy_obs_dim",
    "quat_mul",
    "sample_uniform_tensor",
    "update_history",
    "wrap_to_pi_tensor",
    "yaw_quaternion",
]
