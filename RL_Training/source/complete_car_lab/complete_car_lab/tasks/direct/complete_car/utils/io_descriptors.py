"""Observation / action / state 描述器。"""

from __future__ import annotations

from ..assets.robot_cfg import BALL_JOINT_NAMES


def build_action_descriptor(cfg) -> list[tuple[str, int]]:
    return [("ball_joint_targets", len(cfg.control.ball_joint_names))]


def build_observation_descriptor(cfg) -> list[tuple[str, int]]:
    descriptor = [
        ("base_lin_vel_b", 3),
        ("base_ang_vel_b", 3),
        ("projected_gravity_b", 3),
        ("ball_joint_pos", len(BALL_JOINT_NAMES)),
        ("ball_joint_vel", len(BALL_JOINT_NAMES)),
        ("commands", cfg.commands.num_commands),
        ("last_action", len(BALL_JOINT_NAMES)),
    ]
    descriptor.extend(cfg.sensors.policy_descriptor())
    return descriptor


def build_state_descriptor(_cfg) -> list[tuple[str, int]]:
    return []


def total_dim(descriptor: list[tuple[str, int]]) -> int:
    return sum(dim for _, dim in descriptor)
