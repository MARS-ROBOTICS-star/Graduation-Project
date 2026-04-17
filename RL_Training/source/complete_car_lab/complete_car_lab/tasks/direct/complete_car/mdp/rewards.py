"""目标导向奖励项计算。"""

from __future__ import annotations

import math

import torch

from ..utils.math_utils import quaternion_to_rpy, wrap_to_pi_tensor

REWARD_TERM_NAMES = (
    "target_bonus",
    "progress",
    "heading_gate",
    "longitudinal_slip_gate",
    "lateral_slip_gate",
    "longitudinal_slip_cost",
    "lateral_slip_cost",
    "slip_cost_penalty",
    "composite_gate",
    "roll_gate",
    "gated_progress",
    "capture_reward",
    "capture_phase",
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
    processed_actions: torch.Tensor,
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    params = cfg.rewards.params
    current_goal_distance = torch.linalg.vector_norm(commands[:, :2], dim=1)
    goal_yaw_error = wrap_to_pi_tensor(commands[:, 2])
    planar_speed = torch.linalg.vector_norm(raw_obs_terms["base_lin_vel"][:, :2], dim=1)
    yaw_rate_abs = torch.abs(raw_obs_terms["base_ang_vel"][:, 2])
    capture_phase = current_goal_distance < cfg.terminations.capture_switch_distance

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

    longitudinal_slip_cost = torch.mean(torch.abs(raw_obs_terms["wheel_longitudinal_slip"]), dim=1)
    lateral_slip_cost = torch.mean(torch.abs(raw_obs_terms["wheel_slip_angle"]), dim=1)

    if params.use_slip_gates:
        longitudinal_slip_gate_scale = max(params.longitudinal_slip_gate_scale, 1.0e-6)
        longitudinal_slip_gate_per_wheel = torch.exp(
            -0.5 * torch.square(raw_obs_terms["wheel_longitudinal_slip"] / longitudinal_slip_gate_scale)
        )
        longitudinal_slip_gate = torch.prod(longitudinal_slip_gate_per_wheel, dim=1)

        lateral_slip_gate_scale = max(params.lateral_slip_gate_scale, 1.0e-6)
        lateral_slip_clip_rad = math.pi / lateral_slip_gate_scale
        clipped_wheel_slip_angle = torch.clamp(
            raw_obs_terms["wheel_slip_angle"],
            min=-lateral_slip_clip_rad,
            max=lateral_slip_clip_rad,
        )
        lateral_slip_gate_per_wheel = 0.5 * torch.cos(lateral_slip_gate_scale * clipped_wheel_slip_angle) + 0.5
        lateral_slip_gate = torch.prod(lateral_slip_gate_per_wheel, dim=1)
        composite_gate = (heading_gate + longitudinal_slip_gate + lateral_slip_gate) / 3.0
    else:
        longitudinal_slip_gate = torch.ones_like(progress)
        lateral_slip_gate = torch.ones_like(progress)
        composite_gate = heading_gate

    middle_roll = quaternion_to_rpy(robot.data.root_link_quat_w)[:, 0]
    roll_gate = torch.ones_like(progress)
    roll_gate_activation_roll_rad = math.radians(params.roll_gate_activation_roll_deg)
    roll_gate_mask = torch.abs(middle_roll) > roll_gate_activation_roll_rad
    roll_gate_heading_scale = max(params.body_car_roll_gate, 1.0e-6)
    gated_roll_value = torch.exp(-0.5 * torch.square(goal_yaw_error / roll_gate_heading_scale))
    roll_gate = torch.where(roll_gate_mask, gated_roll_value, roll_gate)
    gated_progress = progress * composite_gate * roll_gate
    slip_cost_penalty = torch.zeros_like(progress)
    if params.use_explicit_slip_cost:
        slip_cost_penalty = (
            params.longitudinal_slip_cost_weight * longitudinal_slip_cost
            + params.lateral_slip_cost_weight * lateral_slip_cost
        )

    capture_distance_sigma = max(params.capture_distance_sigma, 1.0e-6)
    capture_yaw_sigma = max(math.radians(params.capture_yaw_sigma_deg), 1.0e-6)
    capture_planar_speed_sigma = max(params.capture_planar_speed_sigma, 1.0e-6)
    capture_yaw_rate_sigma = max(params.capture_yaw_rate_sigma, 1.0e-6)
    capture_distance_gate = torch.exp(-0.5 * torch.square(current_goal_distance / capture_distance_sigma))
    capture_yaw_gate = torch.exp(-0.5 * torch.square(goal_yaw_error / capture_yaw_sigma))
    capture_planar_speed_gate = torch.exp(-0.5 * torch.square(planar_speed / capture_planar_speed_sigma))
    capture_yaw_rate_gate = torch.exp(-0.5 * torch.square(yaw_rate_abs / capture_yaw_rate_sigma))
    capture_reward = params.capture_reward_scale * (
        capture_distance_gate + capture_yaw_gate + capture_planar_speed_gate + capture_yaw_rate_gate
    ) / 4.0
    capture_reward = torch.where(capture_phase, capture_reward, torch.zeros_like(capture_reward))

    components = {
        "target_bonus": target_bonus,
        "progress": progress,
        "heading_gate": heading_gate,
        "longitudinal_slip_gate": longitudinal_slip_gate,
        "lateral_slip_gate": lateral_slip_gate,
        "longitudinal_slip_cost": longitudinal_slip_cost,
        "lateral_slip_cost": lateral_slip_cost,
        "slip_cost_penalty": slip_cost_penalty,
        "composite_gate": composite_gate,
        "roll_gate": roll_gate,
        "gated_progress": gated_progress,
        "capture_reward": capture_reward,
        "capture_phase": capture_phase.float(),
    }
    tracking_reward = gated_progress - slip_cost_penalty
    total_reward = target_bonus + torch.where(capture_phase, capture_reward, tracking_reward)
    if cfg.rewards.only_positive_rewards:
        total_reward = torch.clamp(total_reward, min=0.0)
    return total_reward, components
