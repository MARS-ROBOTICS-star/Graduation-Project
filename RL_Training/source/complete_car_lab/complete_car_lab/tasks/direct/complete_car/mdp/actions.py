"""动作映射与关节目标写入。"""

from __future__ import annotations

import torch


def map_base_actions_to_planar_command(
    normalized_base_actions: torch.Tensor,
    forward_velocity_max: float | torch.Tensor,
    yaw_rate_max: float | torch.Tensor,
    *,
    allow_reverse: bool | torch.Tensor,
) -> torch.Tensor:
    """Map normalized base actions to physical planar commands [vx, yaw_rate]."""

    if normalized_base_actions.shape[1] != 2:
        raise ValueError("Base planar action branch must have shape (N, 2).")

    forward_action = normalized_base_actions[:, 0]
    yaw_action = normalized_base_actions[:, 1]

    forward_velocity_max_tensor = torch.as_tensor(
        forward_velocity_max,
        device=normalized_base_actions.device,
        dtype=normalized_base_actions.dtype,
    )
    yaw_rate_max_tensor = torch.as_tensor(
        yaw_rate_max,
        device=normalized_base_actions.device,
        dtype=normalized_base_actions.dtype,
    )
    allow_reverse_tensor = torch.as_tensor(
        allow_reverse,
        device=normalized_base_actions.device,
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


def map_ball_joint_actions_to_desired_positions(
    default_targets: torch.Tensor,
    normalized_actions: torch.Tensor,
    lower_limits: tuple[float, ...],
    upper_limits: tuple[float, ...],
) -> torch.Tensor:
    """Map normalized policy outputs to desired ball-joint posture references q^d."""

    lower = normalized_actions.new_tensor(lower_limits).unsqueeze(0)
    upper = normalized_actions.new_tensor(upper_limits).unsqueeze(0)

    if lower.shape[1] != normalized_actions.shape[1] or upper.shape[1] != normalized_actions.shape[1]:
        raise ValueError("Ball-joint action limit dimensions do not match the number of controlled joints.")

    positive_span = upper - default_targets
    negative_span = default_targets - lower
    if torch.any(positive_span < 0.0) or torch.any(negative_span < 0.0):
        raise ValueError("Default ball-joint targets must lie within the configured action lower/upper limits.")

    positive_actions = torch.clamp(normalized_actions, min=0.0, max=1.0)
    negative_actions = torch.clamp(normalized_actions, min=-1.0, max=0.0)
    desired_targets = (
        default_targets
        + positive_actions * positive_span
        + negative_actions * negative_span
    )
    return desired_targets


def apply_ball_joint_position_targets(
    joint_pos_targets: torch.Tensor,
    ball_joint_ids,
    ball_joint_position_targets: torch.Tensor,
) -> torch.Tensor:
    """Write planned position commands q^{cmd} into the global joint target tensor."""

    joint_pos_targets[:, ball_joint_ids] = ball_joint_position_targets
    return joint_pos_targets


def apply_wheel_effort_targets(
    joint_effort_targets: torch.Tensor,
    wheel_joint_ids,
    wheel_torque_targets: torch.Tensor,
    wheel_effort_limit: float | torch.Tensor,
) -> torch.Tensor:
    clamped_targets = torch.clamp(wheel_torque_targets, min=-wheel_effort_limit, max=wheel_effort_limit)
    joint_effort_targets[:, wheel_joint_ids] = clamped_targets
    return joint_effort_targets
