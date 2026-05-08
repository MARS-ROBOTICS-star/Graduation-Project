"""Observation / action / state 描述器。"""

from __future__ import annotations

from ..assets.robot_cfg import WHEEL_JOINT_NAMES
from ..mdp.terrain_features import TERRAIN_FEATURE_DIM


def build_action_descriptor(cfg) -> list[tuple[str, int]]:
    return [
        ("base_planar_command", 2),
        ("ball_joint_posture_reference", len(cfg.control.ball_joint_names)),
    ]


def build_observation_descriptor(cfg) -> list[tuple[str, int]]:
    descriptor = [
        ("ball_joint_pos", len(cfg.control.ball_joint_names)),
        ("ball_joint_vel", len(cfg.control.ball_joint_names)),
        ("base_lin_vel", 3),
        ("base_ang_vel", 3),
        ("wheel_joint_vel", len(WHEEL_JOINT_NAMES)),
        ("wheel_longitudinal_slip", len(WHEEL_JOINT_NAMES)),
        ("wheel_slip_angle", len(WHEEL_JOINT_NAMES)),
        ("wheel_normal_contact_force", len(WHEEL_JOINT_NAMES)),
        ("goal_relative_command", cfg.commands.num_commands),
        ("last_action", cfg.action_space),
    ]
    if cfg.terrain.measure_heights:
        descriptor.append(("terrain_features", TERRAIN_FEATURE_DIM))
    return descriptor


def build_critic_observation_descriptor(cfg) -> list[tuple[str, int]]:
    descriptor = build_observation_descriptor(cfg).copy()
    if cfg.terrain.measure_heights:
        descriptor.append(("terrain_height_patch", cfg.terrain.get_num_height_points()))
    return descriptor


def build_state_descriptor(_cfg) -> list[tuple[str, int]]:
    return []


def total_dim(descriptor: list[tuple[str, int]]) -> int:
    return sum(dim for _, dim in descriptor)
