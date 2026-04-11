"""动作预处理与动作映射。"""

from __future__ import annotations

import torch


def preprocess_policy_actions(actions: torch.Tensor, clip_actions: float, motor_strength: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """返回裁剪后的 policy 动作与施加随机化后的实际动作。"""

    policy_actions = actions.clone().clamp(-clip_actions, clip_actions)
    processed_actions = policy_actions * motor_strength
    return policy_actions, processed_actions


def apply_ball_joint_targets(
    robot,
    joint_pos_targets: torch.Tensor,
    ball_joint_ids,
    processed_actions: torch.Tensor,
    action_scale: float,
) -> torch.Tensor:
    joint_pos_targets[:, ball_joint_ids] = robot.data.default_joint_pos[:, ball_joint_ids] + processed_actions * action_scale
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
