"""观测拼接逻辑。"""

from __future__ import annotations

import torch
from isaaclab.utils import configclass
from isaaclab.utils.noise import NoiseCfg

from ..utils.math_utils import quat_rotate, quaternion_to_rpy, wrap_to_pi_tensor


def _compute_wheel_contact_observations(
    wheel_body_lin_vel_w: torch.Tensor,
    wheel_body_quat_w: torch.Tensor,
    wheel_joint_vel: torch.Tensor,
    wheel_contact_forces_w: torch.Tensor,
    wheel_radius: float,
    slip_velocity_epsilon: float,
    wheel_longitudinal_slip_clip: float,
    total_vehicle_weight: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    x_axis_local = torch.zeros_like(wheel_body_lin_vel_w)
    x_axis_local[..., 0] = 1.0
    y_axis_local = torch.zeros_like(wheel_body_lin_vel_w)
    y_axis_local[..., 1] = 1.0

    wheel_forward_axis_w = quat_rotate(wheel_body_quat_w, x_axis_local)
    wheel_lateral_axis_w = quat_rotate(wheel_body_quat_w, y_axis_local)

    v_x = torch.sum(wheel_body_lin_vel_w * wheel_forward_axis_w, dim=-1)
    v_y = torch.sum(wheel_body_lin_vel_w * wheel_lateral_axis_w, dim=-1)
    v_surface = wheel_radius * wheel_joint_vel

    safe_longitudinal_speed = torch.maximum(torch.abs(v_x), torch.full_like(v_x, slip_velocity_epsilon))

    # Reflect wheel-ground traction state, including tire spin, braking slip, and obstacle-climb adhesion loss.
    wheel_longitudinal_slip = (v_x - v_surface) / safe_longitudinal_speed
    wheel_longitudinal_slip = torch.clamp(
        wheel_longitudinal_slip,
        min=-wheel_longitudinal_slip_clip,
        max=wheel_longitudinal_slip_clip,
    )

    # Describe the mismatch angle between wheel heading and actual travel direction.
    wheel_slip_angle = torch.atan2(v_y, torch.abs(v_x) + slip_velocity_epsilon)

    # The runtime sensor path reconstructs one wheel-ground normal-force resultant vector in world frame
    # by summing all contact-point (normal_force_scalar * contact_normal_vector) terms for each wheel.
    wheel_normal_contact_force = torch.linalg.vector_norm(wheel_contact_forces_w, dim=-1) / total_vehicle_weight

    return wheel_longitudinal_slip, wheel_slip_angle, wheel_normal_contact_force


def collect_raw_observation_terms(
    cfg,
    robot,
    ball_joint_ids,
    wheel_joint_ids,
    wheel_body_ids,
    head_car_body_id: int,
    tail_car_body_id: int,
    wheel_contact_forces_w: torch.Tensor,
    total_vehicle_weight: torch.Tensor,
    ball_joint_targets: torch.Tensor,
    relative_goal_commands: torch.Tensor,
    last_actions: torch.Tensor,
) -> dict[str, torch.Tensor]:
    """返回未乘 observation scale 的原始观测分量。"""

    ball_joint_pos = wrap_to_pi_tensor(robot.data.joint_pos[:, ball_joint_ids])
    wheel_joint_vel = robot.data.joint_vel[:, wheel_joint_ids]
    wheel_body_lin_vel_w = robot.data.body_lin_vel_w[:, wheel_body_ids]
    wheel_body_quat_w = robot.data.body_quat_w[:, wheel_body_ids]
    wheel_longitudinal_slip, wheel_slip_angle, wheel_normal_contact_force = _compute_wheel_contact_observations(
        wheel_body_lin_vel_w=wheel_body_lin_vel_w,
        wheel_body_quat_w=wheel_body_quat_w,
        wheel_joint_vel=wheel_joint_vel,
        wheel_contact_forces_w=wheel_contact_forces_w,
        wheel_radius=cfg.control.wheel_radius,
        slip_velocity_epsilon=cfg.observations.wheel_slip_epsilon,
        wheel_longitudinal_slip_clip=cfg.observations.wheel_longitudinal_slip_clip,
        total_vehicle_weight=total_vehicle_weight,
    )

    return {
        "base_lin_vel": robot.data.root_com_lin_vel_b,
        "base_ang_vel": robot.data.root_com_ang_vel_b,
        "projected_gravity": robot.data.projected_gravity_b,
        "ball_joint_pos": ball_joint_pos,
        "ball_joint_vel": robot.data.joint_vel[:, ball_joint_ids],
        "ball_joint_target_error": wrap_to_pi_tensor(ball_joint_targets - ball_joint_pos),
        "head_roll_pitch": quaternion_to_rpy(robot.data.body_quat_w[:, head_car_body_id])[:, :2],
        "tail_roll_pitch": quaternion_to_rpy(robot.data.body_quat_w[:, tail_car_body_id])[:, :2],
        "wheel_joint_vel": wheel_joint_vel,
        "wheel_longitudinal_slip": wheel_longitudinal_slip,
        "wheel_slip_angle": wheel_slip_angle,
        "wheel_normal_contact_force": wheel_normal_contact_force,
        "relative_goal_commands": relative_goal_commands,
        "last_actions": last_actions,
    }


def compute_actor_observation(
    cfg,
    robot,
    ball_joint_ids,
    wheel_joint_ids,
    wheel_body_ids,
    head_car_body_id: int,
    tail_car_body_id: int,
    wheel_contact_forces_w: torch.Tensor,
    total_vehicle_weight: torch.Tensor,
    ball_joint_targets: torch.Tensor,
    relative_goal_commands: torch.Tensor,
    last_actions: torch.Tensor,
) -> torch.Tensor:
    """构造 Actor 观测；当前 Critic 观测与其保持一致。"""

    scales = cfg.observations.scales
    raw_terms = collect_raw_observation_terms(
        cfg,
        robot,
        ball_joint_ids,
        wheel_joint_ids,
        wheel_body_ids,
        head_car_body_id,
        tail_car_body_id,
        wheel_contact_forces_w,
        total_vehicle_weight,
        ball_joint_targets,
        relative_goal_commands,
        last_actions,
    )

    return torch.cat(
        [
            raw_terms["wheel_joint_vel"] * scales.wheel_joint_vel,
            raw_terms["relative_goal_commands"] * scales.commands,
            raw_terms["last_actions"] * scales.last_action,
        ],
        dim=-1,
    )


def compute_critic_observation(actor_obs: torch.Tensor, height_patch: torch.Tensor | None) -> torch.Tensor:
    """构造 Critic 观测；当前只在 Actor 基础上追加显式地形高度 patch。"""

    if height_patch is None:
        return actor_obs
    return torch.cat((actor_obs, height_patch), dim=-1)

# 传感器噪声注入
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
