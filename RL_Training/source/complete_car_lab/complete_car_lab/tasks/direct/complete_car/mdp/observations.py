"""观测拼接逻辑。"""

from __future__ import annotations

import torch
from isaaclab.utils import configclass
from isaaclab.utils.noise import NoiseCfg

from ..utils.math_utils import quaternion_to_rpy, wrap_to_pi_tensor


def compute_actor_observation(
    cfg,
    robot,
    ball_joint_ids,
    wheel_joint_ids,
    head_car_body_id: int,
    tail_car_body_id: int,
    ball_joint_targets: torch.Tensor,
    commands: torch.Tensor,
    last_actions: torch.Tensor,
) -> torch.Tensor:
    """构造 Actor 观测；当前 Critic 观测与其保持一致。"""

    scales = cfg.observations.scales

    base_lin_vel = robot.data.root_com_lin_vel_b * scales.base_lin_vel
    base_ang_vel = robot.data.root_com_ang_vel_b * scales.base_ang_vel
    projected_gravity = robot.data.projected_gravity_b * scales.projected_gravity
    ball_joint_pos = wrap_to_pi_tensor(robot.data.joint_pos[:, ball_joint_ids]) * scales.ball_joint_pos
    ball_joint_vel = robot.data.joint_vel[:, ball_joint_ids] * scales.ball_joint_vel
    ball_joint_target_error = (
        wrap_to_pi_tensor(ball_joint_targets - robot.data.joint_pos[:, ball_joint_ids]) * scales.ball_joint_target_error
    )
    head_roll_pitch = quaternion_to_rpy(robot.data.body_quat_w[:, head_car_body_id])[:, :2] * scales.module_roll_pitch
    tail_roll_pitch = quaternion_to_rpy(robot.data.body_quat_w[:, tail_car_body_id])[:, :2] * scales.module_roll_pitch
    wheel_joint_vel = robot.data.joint_vel[:, wheel_joint_ids] * scales.wheel_joint_vel

    return torch.cat(
        [
            base_lin_vel,
            base_ang_vel,
            projected_gravity,
            ball_joint_pos,
            ball_joint_vel,
            ball_joint_target_error,
            head_roll_pitch,
            tail_roll_pitch,
            wheel_joint_vel,
            commands * scales.commands,
            last_actions * scales.last_action,
        ],
        dim=-1,
    )


def compute_critic_observation(actor_obs: torch.Tensor, height_patch: torch.Tensor | None) -> torch.Tensor:
    """构造 Critic 观测；当前只在 Actor 基础上追加显式地形高度 patch。"""

    if height_patch is None:
        return actor_obs
    return torch.cat((actor_obs, height_patch), dim=-1)


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
