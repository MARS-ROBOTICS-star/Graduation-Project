"""机器人 USD 资产与关节命名定义。"""

from __future__ import annotations

from pathlib import Path

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg

from .actuators_cfg import build_complete_car_actuators_cfg


BALL_JOINT_NAMES = [
    "spm1_platform_joint_z",
    "spm1_platform_joint_y",
    "spm1_platform_joint_x",
    "spm2_platform_joint_z",
    "spm2_platform_joint_y",
    "spm2_platform_joint_x",
]

WHEEL_JOINT_NAMES = [
    "body_car_wheel_left_joint",
    "body_car_wheel_right_joint",
    "head_car_wheel_left_joint",
    "head_car_wheel_right_joint",
    "tail_car_wheel_left_joint",
    "tail_car_wheel_right_joint",
]

WHEEL_BODY_NAMES = [
    "body_car_wheel_left",
    "body_car_wheel_right",
    "head_car_wheel_left",
    "head_car_wheel_right",
    "tail_car_wheel_left",
    "tail_car_wheel_right",
]

WHEEL_RADIUS = 0.19

LEFT_WHEEL_JOINT_NAMES = [
    "body_car_wheel_left_joint",
    "head_car_wheel_left_joint",
    "tail_car_wheel_left_joint",
]

RIGHT_WHEEL_JOINT_NAMES = [
    "body_car_wheel_right_joint",
    "head_car_wheel_right_joint",
    "tail_car_wheel_right_joint",
]

ALL_JOINT_NAMES = BALL_JOINT_NAMES + WHEEL_JOINT_NAMES
CONTROLLED_JOINT_NAMES = ALL_JOINT_NAMES
COMPLETE_CAR_ARTICULATION_ROOT_PRIM_PATH = "/complete_car_alternative/body_car_chassis"


def _find_repo_root(start: Path) -> Path:
    for parent in (start, *start.parents):
        if (parent / "RL_Training").is_dir() and (parent / "USD" / "complete_car.usd").is_file():
            return parent
    raise RuntimeError(f"Failed to locate repository root from {start}.")


REPO_ROOT = _find_repo_root(Path(__file__).resolve())
COMPLETE_CAR_USD_PATH = REPO_ROOT / "USD" / "complete_car.usd"


def build_complete_car_robot_cfg(
    control_cfg=None,
    reset_cfg=None,
    *,
    prim_path: str = "/World/envs/env_.*/Robot",
) -> ArticulationCfg:
    """根据 control/reset 配置生成机器人 articulation 配置。"""

    default_joint_pos = {name: 0.0 for name in ALL_JOINT_NAMES}
    default_joint_vel = {name: 0.0 for name in ALL_JOINT_NAMES}
    root_pos = (0.0, 0.0, 0.30)

    if reset_cfg is not None:
        default_joint_pos.update(reset_cfg.default_ball_joint_angles)
        default_joint_pos.update(reset_cfg.default_wheel_joint_pos)
        default_joint_vel.update(reset_cfg.default_ball_joint_vel)
        default_joint_vel.update(reset_cfg.default_wheel_joint_vel)
        root_pos = tuple(reset_cfg.root_pos)

    return ArticulationCfg(
        spawn=sim_utils.UsdFileCfg(
            usd_path=str(COMPLETE_CAR_USD_PATH),
            activate_contact_sensors=True,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                rigid_body_enabled=True,
                disable_gravity=False,
                max_linear_velocity=1000.0,
                max_angular_velocity=1000.0,
                max_depenetration_velocity=100.0,
                enable_gyroscopic_forces=True,
            ),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=False,
                solver_position_iteration_count=8,
                solver_velocity_iteration_count=4,
                sleep_threshold=0.005,
                stabilization_threshold=0.001,
            ),
        ),
        prim_path=prim_path,
        articulation_root_prim_path=COMPLETE_CAR_ARTICULATION_ROOT_PRIM_PATH,
        init_state=ArticulationCfg.InitialStateCfg(
            pos=root_pos,
            joint_pos=default_joint_pos,
            joint_vel=default_joint_vel,
        ),
        actuators=build_complete_car_actuators_cfg(control_cfg) if control_cfg is not None else {},
    )


__all__ = [
    "ALL_JOINT_NAMES",
    "BALL_JOINT_NAMES",
    "COMPLETE_CAR_ARTICULATION_ROOT_PRIM_PATH",
    "COMPLETE_CAR_USD_PATH",
    "CONTROLLED_JOINT_NAMES",
    "LEFT_WHEEL_JOINT_NAMES",
    "RIGHT_WHEEL_JOINT_NAMES",
    "WHEEL_BODY_NAMES",
    "WHEEL_JOINT_NAMES",
    "WHEEL_RADIUS",
    "build_complete_car_robot_cfg",
]
