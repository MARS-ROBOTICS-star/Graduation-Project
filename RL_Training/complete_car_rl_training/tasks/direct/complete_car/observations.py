"""Observation helpers for the direct complete-car task."""

from __future__ import annotations

import torch
from isaaclab.utils import configclass
from isaaclab.utils.noise import NoiseCfg

from .utils import body_ang_vel_to_rpy_rates, quaternion_to_rpy, wrap_to_pi_tensor


def per_component_uniform_noise(data: torch.Tensor, cfg: "PerComponentUniformNoiseCfg") -> torch.Tensor:
    if isinstance(cfg.n_min, tuple):
        cfg.n_min = torch.tensor(cfg.n_min, device=data.device, dtype=data.dtype)
    if isinstance(cfg.n_max, tuple):
        cfg.n_max = torch.tensor(cfg.n_max, device=data.device, dtype=data.dtype)

    if cfg.operation == "add":
        return data + torch.rand_like(data) * (cfg.n_max - cfg.n_min) + cfg.n_min
    if cfg.operation == "scale":
        return data * (torch.rand_like(data) * (cfg.n_max - cfg.n_min) + cfg.n_min)
    if cfg.operation == "abs":
        return torch.rand_like(data) * (cfg.n_max - cfg.n_min) + cfg.n_min
    raise ValueError(f"Unknown operation in noise: {cfg.operation}")


@configclass
class PerComponentUniformNoiseCfg(NoiseCfg):
    func = per_component_uniform_noise

    n_min: tuple[float, ...] = ()
    n_max: tuple[float, ...] = ()


def compute_policy_observation(
    cfg,
    robot,
    ball_joint_ids,
    commands: torch.Tensor,
    last_actions: torch.Tensor,
    sensor_features: list[torch.Tensor],
) -> torch.Tensor:
    scales = cfg.observations.scales

    attitude = quaternion_to_rpy(robot.data.root_link_quat_w)
    attitude_rates = body_ang_vel_to_rpy_rates(attitude, robot.data.root_com_ang_vel_b)
    ball_joint_pos = wrap_to_pi_tensor(robot.data.joint_pos[:, ball_joint_ids]) * scales.ball_joint_pos
    ball_joint_vel = robot.data.joint_vel[:, ball_joint_ids] * scales.ball_joint_vel
    scaled_attitude = attitude * scales.attitude
    scaled_attitude_rates = attitude_rates * scales.attitude_rate
    command_obs = commands * scales.commands
    scaled_last_action = last_actions * scales.last_action

    pieces = [
        scaled_attitude,
        scaled_attitude_rates,
        ball_joint_pos,
        ball_joint_vel,
        command_obs,
        scaled_last_action,
    ]

    if sensor_features:
        pieces.extend(sensor_features)

    obs = torch.cat(pieces, dim=-1)
    return obs.clamp(-cfg.observations.clip_observations, cfg.observations.clip_observations)


__all__ = ["PerComponentUniformNoiseCfg", "compute_policy_observation", "per_component_uniform_noise"]
