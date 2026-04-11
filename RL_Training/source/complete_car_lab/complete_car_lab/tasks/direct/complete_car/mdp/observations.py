"""观测拼接逻辑。"""

from __future__ import annotations

import torch
from isaaclab.utils import configclass
from isaaclab.utils.noise import NoiseCfg

from ..utils.math_utils import wrap_to_pi_tensor


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

    base_lin_vel = robot.data.root_com_lin_vel_b * scales.base_lin_vel
    base_ang_vel = robot.data.root_com_ang_vel_b * scales.base_ang_vel
    projected_gravity = robot.data.projected_gravity_b * scales.projected_gravity
    ball_joint_pos = wrap_to_pi_tensor(robot.data.joint_pos[:, ball_joint_ids]) * scales.ball_joint_pos
    ball_joint_vel = robot.data.joint_vel[:, ball_joint_ids] * scales.ball_joint_vel

    pieces = [
        base_lin_vel,
        base_ang_vel,
        projected_gravity,
        ball_joint_pos,
        ball_joint_vel,
        commands * scales.commands,
        last_actions * scales.last_action,
    ]
    if sensor_features:
        pieces.extend(sensor_features)

    return torch.cat(pieces, dim=-1)
