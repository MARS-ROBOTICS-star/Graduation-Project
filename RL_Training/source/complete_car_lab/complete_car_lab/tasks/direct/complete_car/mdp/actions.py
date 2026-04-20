"""动作预处理与动作映射。"""

from __future__ import annotations

import torch


def preprocess_policy_actions(actions: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """返回策略输出动作与环境内部待映射动作。"""

    policy_actions = actions.clone()
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


def apply_wheel_velocity_targets(
    wheel_ang_vel_targets: torch.Tensor,
    wheel_joint_ids,
    wheel_targets: torch.Tensor,
    wheel_velocity_limit: float | torch.Tensor,
) -> torch.Tensor:
    clamped_targets = torch.clamp(wheel_targets, min=-wheel_velocity_limit, max=wheel_velocity_limit)
    wheel_ang_vel_targets[:, wheel_joint_ids] = clamped_targets
    return wheel_ang_vel_targets
