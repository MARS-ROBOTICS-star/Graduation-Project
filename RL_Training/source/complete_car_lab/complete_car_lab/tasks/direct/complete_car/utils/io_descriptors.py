"""Observation / action / state 描述器。"""

from __future__ import annotations

from ..assets.robot_cfg import WHEEL_JOINT_NAMES


def build_action_descriptor(cfg) -> list[tuple[str, int]]:
    return [
        ("wheel_velocity_targets", len(cfg.control.wheel_joint_names)),
    ]


def build_observation_descriptor(cfg) -> list[tuple[str, int]]:
    descriptor = [
        ("wheel_joint_vel", len(WHEEL_JOINT_NAMES)),
        ("goal_relative_command", cfg.commands.num_commands),
        ("last_action", cfg.action_space),
    ]
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
