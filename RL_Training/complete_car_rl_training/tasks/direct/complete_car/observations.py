"""Observation helpers for the direct complete-car task."""

from __future__ import annotations

import torch

from .utils import sample_uniform_tensor, wrap_to_pi_tensor


def _maybe_add_uniform_noise(obs: torch.Tensor, magnitude: float) -> torch.Tensor:
    if magnitude <= 0.0:
        return obs
    return obs + sample_uniform_tensor((-magnitude, magnitude), obs.shape, obs.device)


def compute_policy_observation(
    cfg,
    robot,
    ball_joint_ids,
    wheel_joint_ids,
    commands: torch.Tensor,
    last_actions: torch.Tensor,
    height_features: torch.Tensor | None,
    sensor_features: list[torch.Tensor],
) -> torch.Tensor:
    scales = cfg.observations.scales
    noise_scales = cfg.observations.noise_scales
    noise_level = cfg.observations.noise_level if cfg.observations.add_noise else 0.0

    base_lin_vel = robot.data.root_com_lin_vel_b * scales.lin_vel
    base_ang_vel = robot.data.root_com_ang_vel_b * scales.ang_vel
    projected_gravity = robot.data.projected_gravity_b * scales.gravity
    ball_joint_pos = wrap_to_pi_tensor(robot.data.joint_pos[:, ball_joint_ids]) * scales.ball_joint_pos
    ball_joint_vel = robot.data.joint_vel[:, ball_joint_ids] * scales.ball_joint_vel
    wheel_joint_vel = robot.data.joint_vel[:, wheel_joint_ids] * scales.wheel_joint_vel
    velocity_commands = commands * scales.commands
    scaled_last_action = last_actions * scales.last_action

    pieces = [
        _maybe_add_uniform_noise(base_lin_vel, noise_level * noise_scales.lin_vel),
        _maybe_add_uniform_noise(base_ang_vel, noise_level * noise_scales.ang_vel),
        _maybe_add_uniform_noise(projected_gravity, noise_level * noise_scales.gravity),
        _maybe_add_uniform_noise(ball_joint_pos, noise_level * noise_scales.ball_joint_pos),
        _maybe_add_uniform_noise(ball_joint_vel, noise_level * noise_scales.ball_joint_vel),
        _maybe_add_uniform_noise(wheel_joint_vel, noise_level * noise_scales.wheel_joint_vel),
        _maybe_add_uniform_noise(velocity_commands, noise_level * noise_scales.commands),
        scaled_last_action,
    ]

    if height_features is not None:
        scaled_heights = height_features * scales.height_measurements
        pieces.append(_maybe_add_uniform_noise(scaled_heights, noise_level * noise_scales.height_measurements))

    if sensor_features:
        pieces.extend(sensor_features)

    obs = torch.cat(pieces, dim=-1)
    return obs.clamp(-cfg.observations.clip_observations, cfg.observations.clip_observations)


__all__ = ["compute_policy_observation"]
