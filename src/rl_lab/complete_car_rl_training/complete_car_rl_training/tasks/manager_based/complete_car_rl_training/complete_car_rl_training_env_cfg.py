# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import math
from pathlib import Path

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass
from isaaclab.terrains import TerrainImporterCfg
from . import mdp

##
# Asset configuration
##

_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = next(parent for parent in _THIS_FILE.parents if (parent / "AGENTS.md").exists())
_COMPLETE_CAR_USD = _PROJECT_ROOT / "USD" / "complete_car.usd"

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
        usd_path=str(_COMPLETE_CAR_USD),
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
            stiffness=80.0,
            damping=8.0,
        ),
        "wheel_joints": ImplicitActuatorCfg(
            joint_names_expr=WHEEL_JOINT_NAMES,
            effort_limit_sim=80.0,
            velocity_limit_sim=20.0,
            stiffness=0.0,
            damping=10.0,
        ),
    },
)


##
# Scene definition
##


@configclass
class CompleteCarRlTrainingSceneCfg(InteractiveSceneCfg):
    """Configuration for the articulated complete-car scene."""
    terrain = TerrainImporterCfg(
        prim_path="/World/terrain",
        terrain_type="plane",
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction = 1.0,
            dynamic_friction = 1.0,
            restitution = 0.0,
        ),
    )

    dome_light = AssetBaseCfg(
        prim_path="/World/skyLight",
        spawn=sim_utils.DomeLightCfg(
            intensity=2000.0,
            color=(0.75, 0.75, 0.75),
        ),
    )

    robot: ArticulationCfg = COMPLETE_CAR_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")


##
# MDP settings
##


@configclass
class CommandsCfg:
    """Command specifications for the MDP."""

    base_velocity = mdp.UniformVelocityCommandCfg(
        asset_name="robot",
        resampling_time_range=(4.0, 4.0),
        rel_standing_envs=0.0,
        rel_heading_envs=0.0,
        heading_command=False,
        debug_vis=False,
        ranges=mdp.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(-1.0, 1.0),
            lin_vel_y=(0.0, 0.0),
            ang_vel_z=(0.0, 0.0),
        ),
    )


@configclass
class ActionsCfg:
    """Action specifications for the MDP."""

    ball_joint_pos = mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=BALL_JOINT_NAMES,
        scale=0.25,
        use_default_offset=True,
        preserve_order=True,
    )
    wheel_joint_vel = mdp.JointVelocityActionCfg(
        asset_name="robot",
        joint_names=WHEEL_JOINT_NAMES,
        scale=8.0,
        use_default_offset=True,
        preserve_order=True,
    )


@configclass
class ObservationsCfg:
    """Observation specifications for the MDP."""

    @configclass
    class PolicyCfg(ObsGroup):
        """Observations for the policy."""

        base_lin_vel = ObsTerm(func=mdp.base_lin_vel)
        base_ang_vel = ObsTerm(func=mdp.base_ang_vel)
        projected_gravity = ObsTerm(func=mdp.projected_gravity)
        velocity_commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"})
        ball_joint_pos_rel = ObsTerm(
            func=mdp.joint_pos_rel,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=BALL_JOINT_NAMES)},
        )
        ball_joint_vel_rel = ObsTerm(
            func=mdp.joint_vel_rel,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=BALL_JOINT_NAMES)},
        )
        wheel_joint_vel_rel = ObsTerm(
            func=mdp.joint_vel_rel,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=WHEEL_JOINT_NAMES)},
        )
        actions = ObsTerm(func=mdp.last_action)

        def __post_init__(self) -> None:
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()


@configclass
class EventCfg:
    """Configuration for reset events."""

    reset_base = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {
                "x": (-0.25, 0.25),
                "y": (-0.25, 0.25),
                "yaw": (-0.25 * math.pi, 0.25 * math.pi),
            },
            "velocity_range": {
                "x": (-0.2, 0.2),
                "y": (-0.2, 0.2),
                "z": (-0.1, 0.1),
                "roll": (-0.1, 0.1),
                "pitch": (-0.1, 0.1),
                "yaw": (-0.2, 0.2),
            },
        },
    )

    reset_ball_joints = EventTerm(
        func=mdp.reset_joints_by_offset,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot", joint_names=BALL_JOINT_NAMES),
            "position_range": (-0.15, 0.15),
            "velocity_range": (-0.1, 0.1),
        },
    )

    reset_wheel_joints = EventTerm(
        func=mdp.reset_joints_by_offset,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot", joint_names=WHEEL_JOINT_NAMES),
            "position_range": (0.0, 0.0),
            "velocity_range": (0.0, 0.0),
        },
    )


@configclass
class RewardsCfg:
    """Reward terms for the articulated car."""

    alive = RewTerm(func=mdp.is_alive, weight=0.5)
    terminating = RewTerm(func=mdp.is_terminated, weight=-2.0)
    track_lin_vel_xy_exp = RewTerm(
        func=mdp.track_lin_vel_xy_exp,
        weight=2.0,
        params={"command_name": "base_velocity", "std": math.sqrt(0.25)},
    )
    track_ang_vel_z_exp = RewTerm(
        func=mdp.track_ang_vel_z_exp,
        weight=0.5,
        params={"command_name": "base_velocity", "std": math.sqrt(0.25)},
    )
    flat_orientation = RewTerm(func=mdp.flat_orientation_l2, weight=-1.0)
    lin_vel_z = RewTerm(func=mdp.lin_vel_z_l2, weight=-0.5)
    ang_vel_xy = RewTerm(func=mdp.ang_vel_xy_l2, weight=-0.05)
    ball_joint_deviation = RewTerm(
        func=mdp.joint_deviation_l1,
        weight=-0.05,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=BALL_JOINT_NAMES)},
    )
    ball_joint_vel = RewTerm(
        func=mdp.joint_vel_l1,
        weight=-0.01,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=BALL_JOINT_NAMES)},
    )
    action_rate_l2 = RewTerm(func=mdp.action_rate_l2, weight=-0.005)


@configclass
class TerminationsCfg:
    """Termination terms for the articulated car."""

    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    bad_orientation = DoneTerm(func=mdp.bad_orientation, params={"limit_angle": math.radians(60.0)})
    root_too_low = DoneTerm(func=mdp.root_height_below_minimum, params={"minimum_height": 0.10})
    ball_joint_out_of_bounds = DoneTerm(
        func=mdp.joint_pos_out_of_manual_limit,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=BALL_JOINT_NAMES), "bounds": (-0.8, 0.8)},
    )


##
# Environment configuration
##


@configclass
class CompleteCarRlTrainingEnvCfg(ManagerBasedRLEnvCfg):
    scene: CompleteCarRlTrainingSceneCfg = CompleteCarRlTrainingSceneCfg(num_envs=4096, env_spacing=4.0)
    commands: CommandsCfg = CommandsCfg()
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    events: EventCfg = EventCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()

    def __post_init__(self) -> None:
        """Post initialization."""
        self.decimation = 2
        self.episode_length_s = 8.0
        self.viewer.eye = (8.0, 0.0, 5.0)
        self.sim.dt = 1 / 120
        self.sim.render_interval = self.decimation
