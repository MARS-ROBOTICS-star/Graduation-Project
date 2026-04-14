"""动作预处理与动作映射。"""

from __future__ import annotations

import torch


def preprocess_policy_actions(actions: torch.Tensor, clip_actions: float, motor_strength: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """返回限幅后的标准化动作与施加随机化后的实际动作。"""

    policy_actions = actions.clone().clamp(-clip_actions, clip_actions)
    processed_actions = (policy_actions * motor_strength).clamp(-clip_actions, clip_actions)
    return policy_actions, processed_actions


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
    allocator,
    robot,
    joint_vel_targets: torch.Tensor,
    ball_joint_ids,
    wheel_joint_ids,
    commands: torch.Tensor,
) -> torch.Tensor:
    wheel_targets = allocator.compute_wheel_speed_targets_from_planar_command(
        ball_joint_pos=robot.data.joint_pos[:, ball_joint_ids],
        ball_joint_vel=robot.data.joint_vel[:, ball_joint_ids],
        planar_command=commands,
    )
    joint_vel_targets[:, wheel_joint_ids] = wheel_targets
    return joint_vel_targets
