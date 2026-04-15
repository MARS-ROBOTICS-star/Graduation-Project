"""目标导向奖励项计算。"""

from __future__ import annotations

import math

import torch

from ..utils.math_utils import quaternion_to_rpy, wrap_to_pi_tensor

REWARD_TERM_NAMES = (
    "target_bonus",
    "progress",
    "roll_gate",
    "speed_gate",
    "force_gate",
    "heading_gate",
    "longitudinal_slip_gate",
    "lateral_slip_gate",
    "composite_gate",
    "gated_progress",
)


def _compute_target_bonus_value(cfg) -> float:
    progress_horizon = cfg.commands.goal_distance / max(cfg.control.control_dt, 1.0e-6)
    ratio = cfg.rewards.params.target_bonus_ratio
    return progress_horizon * ratio / max(1.0 - ratio, 1.0e-6)


def compute_reward_terms(
    cfg,
    robot,
    commands: torch.Tensor,
    previous_goal_distance: torch.Tensor,
    raw_obs_terms: dict[str, torch.Tensor],
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    params = cfg.rewards.params
    current_goal_distance = torch.linalg.vector_norm(commands[:, :2], dim=1)
    goal_yaw_error = wrap_to_pi_tensor(commands[:, 2])

    goal_reached = (
        (current_goal_distance < params.target_position_tolerance)
        & (torch.abs(goal_yaw_error) < math.radians(params.target_yaw_tolerance_deg))
    )
    target_bonus = goal_reached.float() * _compute_target_bonus_value(cfg)

    control_frequency = 1.0 / max(cfg.control.control_dt, 1.0e-6)
    progress = (previous_goal_distance - current_goal_distance) * control_frequency

    heading_denominator = torch.clamp(
        current_goal_distance / max(params.heading_distance_scale, 1.0e-6),
        min=1.0e-6,
    )
    heading_gate = torch.exp(-0.5 * torch.square(goal_yaw_error / heading_denominator))

    middle_roll = quaternion_to_rpy(robot.data.root_link_quat_w)[:, 0]
    abs_middle_roll = torch.abs(middle_roll)
    free_roll_band = math.radians(params.roll_free_deg)
    roll_gate = torch.where(
        abs_middle_roll <= free_roll_band,
        torch.ones_like(abs_middle_roll),
        torch.exp(-0.5 * torch.square(abs_middle_roll / max(params.roll_gaussian_scale, 1.0e-6))),
    )

    horizontal_speed = torch.linalg.vector_norm(robot.data.root_link_lin_vel_w[:, :2], dim=1)
    speed_gate = torch.minimum(
        torch.ones_like(horizontal_speed),
        torch.exp(params.speed_gain * (params.speed_limit - horizontal_speed)),
    )

    normalized_wheel_forces = raw_obs_terms["wheel_normal_contact_force"]
    force_std = torch.std(normalized_wheel_forces, dim=1, unbiased=False)
    force_gate = torch.exp(-0.5 * torch.square(force_std / max(params.force_std_scale, 1.0e-6)))

    wheel_longitudinal_slip = raw_obs_terms["wheel_longitudinal_slip"]
    longitudinal_slip_gate = torch.prod(
        torch.exp(-0.5 * torch.square(wheel_longitudinal_slip / max(params.longitudinal_slip_scale, 1.0e-6))),
        dim=1,
    )

    wheel_slip_angle = raw_obs_terms["wheel_slip_angle"]
    slip_angle_limit = math.pi / max(params.lateral_slip_gain, 1.0e-6)
    clipped_slip_angle = torch.clamp(wheel_slip_angle, -slip_angle_limit, slip_angle_limit)
    lateral_slip_terms = 0.5 * torch.cos(params.lateral_slip_gain * clipped_slip_angle) + 0.5
    lateral_slip_terms = torch.where(
        torch.abs(wheel_slip_angle) <= slip_angle_limit,
        lateral_slip_terms,
        torch.zeros_like(lateral_slip_terms),
    )
    lateral_slip_gate = torch.prod(lateral_slip_terms, dim=1)

    composite_gate = (heading_gate + longitudinal_slip_gate + lateral_slip_gate) / 3.0
    gated_progress = progress * roll_gate * speed_gate * force_gate * composite_gate

    components = {
        "target_bonus": target_bonus,
        "progress": progress,
        "roll_gate": roll_gate,
        "speed_gate": speed_gate,
        "force_gate": force_gate,
        "heading_gate": heading_gate,
        "longitudinal_slip_gate": longitudinal_slip_gate,
        "lateral_slip_gate": lateral_slip_gate,
        "composite_gate": composite_gate,
        "gated_progress": gated_progress,
    }
    total_reward = target_bonus + gated_progress
    if cfg.rewards.only_positive_rewards:
        total_reward = torch.clamp(total_reward, min=0.0)
    return total_reward, components
