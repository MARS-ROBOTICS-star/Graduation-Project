"""动作预处理与动作映射。"""

from __future__ import annotations

import math

import torch

from ..kinematics.wheel_speed_allocator import PLANAR_COMMAND_TRANSFORM


def preprocess_policy_actions(actions: torch.Tensor, clip_actions: float) -> tuple[torch.Tensor, torch.Tensor]:
    """返回限幅后的标准化动作与实际执行动作。"""

    policy_actions = actions.clone().clamp(-clip_actions, clip_actions)
    processed_actions = policy_actions.clone()
    return policy_actions, processed_actions


def map_base_actions_to_planar_command(
    processed_base_actions: torch.Tensor,
    forward_velocity_max: float | torch.Tensor,
    yaw_rate_max: float | torch.Tensor,
    *,
    allow_reverse: bool | torch.Tensor,
) -> torch.Tensor:
    """Map normalized base actions to physical planar commands [vx, yaw_rate]."""

    if processed_base_actions.shape[1] != 2:
        raise ValueError("Base planar action branch must have shape (N, 2).")

    forward_action = processed_base_actions[:, 0]
    yaw_action = processed_base_actions[:, 1]

    forward_velocity_max_tensor = torch.as_tensor(
        forward_velocity_max,
        device=processed_base_actions.device,
        dtype=processed_base_actions.dtype,
    )
    yaw_rate_max_tensor = torch.as_tensor(
        yaw_rate_max,
        device=processed_base_actions.device,
        dtype=processed_base_actions.dtype,
    )
    allow_reverse_tensor = torch.as_tensor(
        allow_reverse,
        device=processed_base_actions.device,
        dtype=torch.bool,
    )

    if forward_velocity_max_tensor.ndim == 0:
        forward_velocity_max_tensor = forward_velocity_max_tensor.expand_as(forward_action)
    if yaw_rate_max_tensor.ndim == 0:
        yaw_rate_max_tensor = yaw_rate_max_tensor.expand_as(yaw_action)
    if allow_reverse_tensor.ndim == 0:
        allow_reverse_tensor = allow_reverse_tensor.expand_as(forward_action)

    reverse_enabled_vx = forward_action * forward_velocity_max_tensor
    forward_only_vx = 0.5 * (forward_action + 1.0) * forward_velocity_max_tensor
    vx_cmd = torch.where(allow_reverse_tensor, reverse_enabled_vx, forward_only_vx)

    yaw_rate_cmd = yaw_action * yaw_rate_max_tensor
    return torch.stack((vx_cmd, yaw_rate_cmd), dim=-1)


def transform_planar_command(planar_command: torch.Tensor) -> torch.Tensor:
    """Apply the measured planar-command transform expected by the wheel allocator."""

    if planar_command.shape[1] != 2:
        raise ValueError("Planar command tensor must have shape (N, 2).")

    planar_command_xyz = torch.zeros(
        (planar_command.shape[0], 3),
        device=planar_command.device,
        dtype=planar_command.dtype,
    )
    planar_command_xyz[:, 0] = planar_command[:, 0]
    planar_command_xyz[:, 2] = planar_command[:, 1]
    transform = torch.as_tensor(
        PLANAR_COMMAND_TRANSFORM,
        device=planar_command.device,
        dtype=planar_command.dtype,
    )
    transformed_xyz = planar_command_xyz @ transform.T
    return torch.stack((transformed_xyz[:, 0], transformed_xyz[:, 2]), dim=1)


def apply_ball_joint_targets(
    robot,
    joint_pos_targets: torch.Tensor,
    ball_joint_ids,
    processed_actions: torch.Tensor,
    lower_limits: tuple[float, ...],
    upper_limits: tuple[float, ...],
) -> torch.Tensor:
    default_targets = robot.data.default_joint_pos[:, ball_joint_ids]
    lower = processed_actions.new_tensor(lower_limits).unsqueeze(0)
    upper = processed_actions.new_tensor(upper_limits).unsqueeze(0)

    if lower.shape[1] != processed_actions.shape[1] or upper.shape[1] != processed_actions.shape[1]:
        raise ValueError("Ball-joint action limit dimensions do not match the number of controlled joints.")

    positive_span = upper - default_targets
    negative_span = default_targets - lower
    if torch.any(positive_span < 0.0) or torch.any(negative_span < 0.0):
        raise ValueError("Default ball-joint targets must lie within the configured action lower/upper limits.")

    positive_actions = torch.clamp(processed_actions, min=0.0, max=1.0)
    negative_actions = torch.clamp(processed_actions, min=-1.0, max=0.0)
    joint_pos_targets[:, ball_joint_ids] = (
        default_targets
        + positive_actions * positive_span
        + negative_actions * negative_span
    )
    return joint_pos_targets


def _decreasing_limit_scale(
    values_abs: torch.Tensor,
    start: float,
    full: float,
    min_scale: float,
) -> torch.Tensor:
    start_value = max(start, 0.0)
    full_value = max(full, start_value + 1.0e-6)
    ratio = (values_abs - start_value) / (full_value - start_value)
    ratio = torch.clamp(ratio, min=0.0, max=1.0)
    return 1.0 - ratio * (1.0 - min_scale)


def _increasing_limit_scale(
    values: torch.Tensor,
    low: float,
    high: float,
    min_scale: float,
) -> torch.Tensor:
    low_value = max(low, 0.0)
    high_value = max(high, low_value + 1.0e-6)
    ratio = (values - low_value) / (high_value - low_value)
    ratio = torch.clamp(ratio, min=0.0, max=1.0)
    return min_scale + ratio * (1.0 - min_scale)


def compute_traction_aware_wheel_velocity_limit(
    wheel_longitudinal_slip: torch.Tensor,
    wheel_slip_angle: torch.Tensor,
    wheel_normal_contact_force: torch.Tensor,
    nominal_wheel_velocity_limit: float,
    *,
    enabled: bool,
    min_scale: float,
    longitudinal_slip_start: float,
    longitudinal_slip_full: float,
    slip_angle_start_deg: float,
    slip_angle_full_deg: float,
    contact_force_low: float,
    contact_force_high: float,
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    nominal_limit = torch.full_like(wheel_longitudinal_slip, nominal_wheel_velocity_limit)

    if not enabled:
        unity = torch.ones_like(wheel_longitudinal_slip)
        return nominal_limit, {
            "combined_scale": unity,
            "longitudinal_scale": unity,
            "lateral_scale": unity,
            "contact_scale": unity,
        }

    bounded_min_scale = min(max(min_scale, 0.0), 1.0)
    longitudinal_scale = _decreasing_limit_scale(
        torch.abs(wheel_longitudinal_slip),
        start=longitudinal_slip_start,
        full=longitudinal_slip_full,
        min_scale=bounded_min_scale,
    )
    lateral_scale = _decreasing_limit_scale(
        torch.abs(wheel_slip_angle),
        start=math.radians(slip_angle_start_deg),
        full=math.radians(slip_angle_full_deg),
        min_scale=bounded_min_scale,
    )
    contact_scale = _increasing_limit_scale(
        wheel_normal_contact_force,
        low=contact_force_low,
        high=contact_force_high,
        min_scale=bounded_min_scale,
    )
    combined_scale = torch.minimum(torch.minimum(longitudinal_scale, lateral_scale), contact_scale)
    traction_aware_limit = nominal_limit * combined_scale
    return traction_aware_limit, {
        "combined_scale": combined_scale,
        "longitudinal_scale": longitudinal_scale,
        "lateral_scale": lateral_scale,
        "contact_scale": contact_scale,
    }


def apply_wheel_velocity_targets(
    wheel_ang_vel_targets: torch.Tensor,
    wheel_joint_ids,
    wheel_targets: torch.Tensor,
    wheel_velocity_limit: float | torch.Tensor,
) -> torch.Tensor:
    clamped_targets = torch.clamp(wheel_targets, min=-wheel_velocity_limit, max=wheel_velocity_limit)
    wheel_ang_vel_targets[:, wheel_joint_ids] = clamped_targets
    return wheel_ang_vel_targets
