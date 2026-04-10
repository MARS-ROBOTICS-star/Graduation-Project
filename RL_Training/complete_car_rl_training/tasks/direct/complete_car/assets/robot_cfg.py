# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Robot asset configuration shared by direct complete-car tasks."""

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg

from complete_car_rl_training.paths import COMPLETE_CAR_USD


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

CONTROLLED_JOINT_NAMES = BALL_JOINT_NAMES + WHEEL_JOINT_NAMES

COMPLETE_CAR_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=str(COMPLETE_CAR_USD),
        activate_contact_sensors=False,
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
            solver_velocity_iteration_count=0,
            sleep_threshold=0.005,
            stabilization_threshold=0.001,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.30),
        joint_pos={name: 0.0 for name in CONTROLLED_JOINT_NAMES},
        joint_vel={name: 0.0 for name in CONTROLLED_JOINT_NAMES},
    ),
    actuators={
        "ball_joints": ImplicitActuatorCfg(
            joint_names_expr=BALL_JOINT_NAMES,
            effort_limit_sim=120.0,
            velocity_limit_sim=6.0,
            stiffness=100.0,
            damping=10.0,
        ),
        "wheel_joints": ImplicitActuatorCfg(
            joint_names_expr=WHEEL_JOINT_NAMES,
            effort_limit_sim=80.0,
            velocity_limit_sim=20.0,
            stiffness=0.0,
            damping=1.0e3,
        ),
    },
)
