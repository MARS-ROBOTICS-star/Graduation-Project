"""张量数学工具。"""

from __future__ import annotations

import torch

from ..assets.robot_cfg import BALL_JOINT_NAMES, WHEEL_JOINT_NAMES


def sample_uniform_tensor(value_range: tuple[float, float], shape: tuple[int, ...], device: torch.device) -> torch.Tensor:
    low, high = value_range
    return torch.empty(shape, device=device).uniform_(low, high)

#角度归整到[-pi,pi]
def wrap_to_pi_tensor(angles: torch.Tensor) -> torch.Tensor:
    return torch.atan2(torch.sin(angles), torch.cos(angles))


def world_xy_to_body_xy(delta_xy_w: torch.Tensor, yaw_w: torch.Tensor) -> torch.Tensor:
    cos_yaw = torch.cos(yaw_w)
    sin_yaw = torch.sin(yaw_w)
    x_rel = cos_yaw * delta_xy_w[:, 0] + sin_yaw * delta_xy_w[:, 1]
    y_rel = -sin_yaw * delta_xy_w[:, 0] + cos_yaw * delta_xy_w[:, 1]
    return torch.stack((x_rel, y_rel), dim=-1)

# 四元数转换为欧拉角
def quaternion_to_rpy(quat_wxyz: torch.Tensor) -> torch.Tensor:
    w, x, y, z = quat_wxyz.unbind(dim=-1)

    sin_roll = 2.0 * (w * x + y * z)
    cos_roll = 1.0 - 2.0 * (x * x + y * y)
    roll = torch.atan2(sin_roll, cos_roll)

    sin_pitch = 2.0 * (w * y - z * x)
    sin_pitch = torch.clamp(sin_pitch, min=-1.0, max=1.0)
    pitch = torch.asin(sin_pitch)

    sin_yaw = 2.0 * (w * z + x * y)
    cos_yaw = 1.0 - 2.0 * (y * y + z * z)
    yaw = torch.atan2(sin_yaw, cos_yaw)

    return torch.stack((roll, pitch, yaw), dim=-1)


def body_ang_vel_to_rpy_rates(rpy: torch.Tensor, ang_vel_b: torch.Tensor) -> torch.Tensor:
    roll = rpy[:, 0]
    pitch = rpy[:, 1]
    roll_rate_input = ang_vel_b[:, 0]
    pitch_rate_input = ang_vel_b[:, 1]
    yaw_rate_input = ang_vel_b[:, 2]

    sin_roll = torch.sin(roll)
    cos_roll = torch.cos(roll)
    tan_pitch = torch.tan(pitch)
    cos_pitch = torch.cos(pitch)
    safe_cos_pitch = torch.where(cos_pitch >= 0.0, torch.full_like(cos_pitch, 1.0e-4), torch.full_like(cos_pitch, -1.0e-4))
    cos_pitch = torch.where(torch.abs(cos_pitch) < 1.0e-4, safe_cos_pitch, cos_pitch)

    roll_rate = roll_rate_input + sin_roll * tan_pitch * pitch_rate_input + cos_roll * tan_pitch * yaw_rate_input
    pitch_rate = cos_roll * pitch_rate_input - sin_roll * yaw_rate_input
    yaw_rate = (sin_roll * pitch_rate_input + cos_roll * yaw_rate_input) / cos_pitch
    return torch.stack((roll_rate, pitch_rate, yaw_rate), dim=-1)


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


def quat_rotate(quat_wxyz: torch.Tensor, vectors: torch.Tensor) -> torch.Tensor:
    quat_vec = quat_wxyz[..., 1:]
    uv = torch.cross(quat_vec, vectors, dim=-1)
    uuv = torch.cross(quat_vec, uv, dim=-1)
    return vectors + 2.0 * (quat_wxyz[..., :1] * uv + uuv)


def update_history(history_buffer: torch.Tensor | None, current_obs: torch.Tensor) -> torch.Tensor:
    if history_buffer is None:
        return current_obs
    history_buffer[:, :-1] = history_buffer[:, 1:].clone()
    history_buffer[:, -1] = current_obs
    return history_buffer.reshape(current_obs.shape[0], -1)


def compute_policy_obs_noise_magnitudes(cfg) -> list[float]:
    noise_cfg = cfg.observations.noise
    noise_level = noise_cfg.level if noise_cfg.enabled else 0.0
    magnitudes: list[float] = []

    magnitudes.extend([noise_level * noise_cfg.base_lin_vel] * 3)
    magnitudes.extend([noise_level * noise_cfg.base_ang_vel] * 3)
    magnitudes.extend([noise_level * noise_cfg.projected_gravity] * 3)
    magnitudes.extend([noise_level * noise_cfg.ball_joint_pos] * len(BALL_JOINT_NAMES))
    magnitudes.extend([noise_level * noise_cfg.wheel_longitudinal_slip] * len(WHEEL_JOINT_NAMES))
    magnitudes.extend([noise_level * noise_cfg.wheel_slip_angle] * len(WHEEL_JOINT_NAMES))
    magnitudes.extend([noise_level * noise_cfg.wheel_normal_contact_force] * len(WHEEL_JOINT_NAMES))
    magnitudes.extend([noise_level * noise_cfg.commands] * cfg.commands.num_commands)
    magnitudes.extend([0.0] * cfg.action_space)

    return magnitudes


def compute_policy_obs_dim(cfg) -> int:
    proprio_dim = (
        3+ 3+ 3
        + len(BALL_JOINT_NAMES)
        + len(WHEEL_JOINT_NAMES)
        + len(WHEEL_JOINT_NAMES)
        + len(WHEEL_JOINT_NAMES)
        + cfg.commands.num_commands
        + cfg.action_space
    )
    return proprio_dim

__all__ = [
    "body_ang_vel_to_rpy_rates",
    "compute_policy_obs_dim",
    "compute_policy_obs_noise_magnitudes",
    "quat_rotate",
    "quat_mul",
    "quaternion_to_rpy",
    "sample_uniform_tensor",
    "update_history",
    "wrap_to_pi_tensor",
    "world_xy_to_body_xy",
    "yaw_quaternion",
]
