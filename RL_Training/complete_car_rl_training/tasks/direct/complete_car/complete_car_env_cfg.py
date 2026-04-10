# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Direct-workflow config trunk for the complete-car task."""

from __future__ import annotations

import math
from dataclasses import field

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnvCfg, ViewerCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass

from .assets.robot_cfg import BALL_JOINT_NAMES, COMPLETE_CAR_CFG, CONTROLLED_JOINT_NAMES, WHEEL_JOINT_NAMES
from .sensors.sensor_runtime import CompleteCarSensorRuntimeCfg
from .terrain.terrain_runtime import CompleteCarTerrainRuntimeCfg
from .utils import compute_policy_obs_dim


@configclass
class CompleteCarCommandRangesCfg:
    lin_vel_x: tuple[float, float] = (-2.0, 2.0)
    lin_vel_y: tuple[float, float] = (0.0, 0.0)
    ang_vel_z: tuple[float, float] = (-1.0, 1.0)
    heading: tuple[float, float] = (-math.pi, math.pi)
    curvature: tuple[float, float] = (-0.5, 0.5)


@configclass
class CompleteCarCommandCfg:
    num_commands: int = 3
    resampling_time: float = 4.0
    heading_command: bool = False
    zero_command: bool = False
    rel_standing_envs: float = 0.0
    rel_heading_envs: float = 0.0
    debug_vis: bool = False
    turn_lin_vel_threshold: float = 0.1
    ranges: CompleteCarCommandRangesCfg = CompleteCarCommandRangesCfg()


@configclass
class CompleteCarControlCfg:
    decimation: int = 2
    ball_joint_action_scale: float = 0.25
    wheel_velocity_action_scale: float = 8.0
    ball_joint_stiffness: float = 100.0
    ball_joint_damping: float = 10.0
    ball_joint_effort_limit_sim: float = 120.0
    ball_joint_velocity_limit_sim: float = 6.0
    wheel_joint_stiffness: float = 0.0
    wheel_joint_damping: float = 1.0e3
    wheel_joint_effort_limit_sim: float = 80.0
    wheel_joint_velocity_limit_sim: float = 20.0


@configclass
class CompleteCarObservationScalesCfg:
    lin_vel: float = 2.0
    ang_vel: float = 0.25
    gravity: float = 1.0
    ball_joint_pos: float = 1.0
    ball_joint_vel: float = 0.05
    wheel_joint_vel: float = 0.05
    commands: float = 1.0
    last_action: float = 1.0
    height_measurements: float = 5.0


@configclass
class CompleteCarObservationNoiseScalesCfg:
    ball_joint_pos: float = 0.01
    ball_joint_vel: float = 0.05
    wheel_joint_vel: float = 0.05
    lin_vel: float = 0.1
    ang_vel: float = 0.2
    gravity: float = 0.05
    height_measurements: float = 0.1
    commands: float = 0.0


@configclass
class CompleteCarObservationCfg:
    use_history: bool = False
    history_length: int = 1
    clip_observations: float = 100.0
    clip_actions: float = 100.0
    add_noise: bool = False
    noise_level: float = 1.0
    scales: CompleteCarObservationScalesCfg = CompleteCarObservationScalesCfg()
    noise_scales: CompleteCarObservationNoiseScalesCfg = CompleteCarObservationNoiseScalesCfg()


@configclass
class CompleteCarRewardScalesCfg:
    termination: float = -2.0
    tracking_lin_vel: float = 2.0
    tracking_ang_vel: float = 2.0
    lin_vel_z: float = -2.0
    ang_vel_xy: float = -1.0
    orientation: float = -5.0
    ball_joint_deviation: float = -0.2
    ball_joint_swing: float = -0.1
    action_rate: float = -0.01


@configclass
class CompleteCarRewardCfg:
    scales: CompleteCarRewardScalesCfg = CompleteCarRewardScalesCfg()
    only_positive_rewards: bool = False
    tracking_lin_vel_std: float = math.sqrt(0.5)
    tracking_ang_vel_std: float = math.sqrt(0.25)
    ball_joint_target: float = 0.0
    soft_ball_joint_pos_limit: float = 0.8
    orientation_limit_deg: float = 45.0
    base_height_target: float = 0.30


@configclass
class CompleteCarResetCfg:
    pos: tuple[float, float, float] = (0.0, 0.0, 0.30)
    lin_vel: tuple[float, float, float] = (0.0, 0.0, 0.0)
    ang_vel: tuple[float, float, float] = (0.0, 0.0, 0.0)
    root_x_range: tuple[float, float] = (-0.25, 0.25)
    root_y_range: tuple[float, float] = (-0.25, 0.25)
    root_yaw_range: tuple[float, float] = (-0.25 * math.pi, 0.25 * math.pi)
    default_ball_joint_angles: dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in BALL_JOINT_NAMES})
    default_wheel_joint_pos: dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in WHEEL_JOINT_NAMES})
    default_ball_joint_vel: dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in BALL_JOINT_NAMES})
    default_wheel_joint_vel: dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in WHEEL_JOINT_NAMES})
    ball_joint_pos_range: tuple[float, float] = (0.0, 0.0)
    ball_joint_vel_range: tuple[float, float] = (0.0, 0.0)
    wheel_joint_pos_range: tuple[float, float] = (0.0, 0.0)
    wheel_joint_vel_range: tuple[float, float] = (0.0, 0.0)
    minimum_root_height: float | None = None


@configclass
class CompleteCarRandomizationCfg:
    randomize_motor_strength: bool = False
    motor_strength_range: tuple[float, float] = (0.9, 1.1)
    joint_position_noise_scale: float = 0.0
    action_noise_std: float = 0.0
    action_bias_std: float = 0.0


@configclass
class CompleteCarEnvCfg(DirectRLEnvCfg):
    """Base direct-workflow config for the complete-car task."""

    decimation: int = 2
    episode_length_s: float = 16.0
    action_space: int = len(CONTROLLED_JOINT_NAMES)
    observation_space: int = 42
    state_space: int = 0

    sim: sim_utils.SimulationCfg = sim_utils.SimulationCfg()
    viewer: ViewerCfg = ViewerCfg(
        eye=(-53.885, 43.696, 64.903),
        lookat=(-53.054, 43.698, 64.346),
    )
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=512,
        env_spacing=4.0,
        replicate_physics=True,
        clone_in_fabric=True,
    )
    robot_cfg: ArticulationCfg = COMPLETE_CAR_CFG.replace(prim_path="/World/envs/env_.*/Robot")

    control: CompleteCarControlCfg = CompleteCarControlCfg()
    commands: CompleteCarCommandCfg = CompleteCarCommandCfg()
    observations: CompleteCarObservationCfg = CompleteCarObservationCfg()
    rewards: CompleteCarRewardCfg = CompleteCarRewardCfg()
    reset: CompleteCarResetCfg = CompleteCarResetCfg()
    randomization: CompleteCarRandomizationCfg = CompleteCarRandomizationCfg()
    terrain: CompleteCarTerrainRuntimeCfg = CompleteCarTerrainRuntimeCfg()
    sensors: CompleteCarSensorRuntimeCfg = CompleteCarSensorRuntimeCfg()

    def __post_init__(self) -> None:
        super().__post_init__()

        self.decimation = self.control.decimation
        self.action_space = len(CONTROLLED_JOINT_NAMES)
        base_obs_dim = compute_policy_obs_dim(self)
        if self.observations.use_history and self.observations.history_length > 1:
            self.observation_space = base_obs_dim * self.observations.history_length
        else:
            self.observation_space = base_obs_dim
        self.state_space = 0

        self.sim.dt = 1.0 / 120.0
        self.sim.render_interval = self.decimation
        self.sim.gravity = (0.0, 0.0, -9.81)
        self.sim.use_fabric = True
        self.sim.physics_material.static_friction = self.terrain.static_friction
        self.sim.physics_material.dynamic_friction = self.terrain.dynamic_friction
        self.sim.physics_material.restitution = self.terrain.restitution
        self.sim.physx.solver_type = 1
        self.sim.physx.max_position_iteration_count = 8
        self.sim.physx.max_velocity_iteration_count = 0
        self.sim.physx.bounce_threshold_velocity = 0.2
        self.sim.physx.friction_offset_threshold = 0.04
        self.sim.physx.friction_correlation_distance = 0.025
        self.sim.physx.enable_stabilization = True
        self.sim.physx.gpu_max_rigid_contact_count = 2**23
        self.sim.physx.gpu_max_rigid_patch_count = 5 * 2**15
        self.sim.physx.gpu_found_lost_pairs_capacity = 2**21
        self.sim.physx.gpu_found_lost_aggregate_pairs_capacity = 2**25
        self.sim.physx.gpu_total_aggregate_pairs_capacity = 2**21
        self.sim.physx.gpu_heap_capacity = 2**26
        self.sim.physx.gpu_temp_buffer_capacity = 2**24

        self.robot_cfg.spawn.usd_path = str(self.robot_cfg.spawn.usd_path)
        self.robot_cfg.init_state.pos = self.reset.pos
        self.robot_cfg.init_state.joint_pos = {
            **self.reset.default_ball_joint_angles,
            **self.reset.default_wheel_joint_pos,
        }
        self.robot_cfg.init_state.joint_vel = {
            **self.reset.default_ball_joint_vel,
            **self.reset.default_wheel_joint_vel,
        }
        self.robot_cfg.actuators["ball_joints"].stiffness = self.control.ball_joint_stiffness
        self.robot_cfg.actuators["ball_joints"].damping = self.control.ball_joint_damping
        self.robot_cfg.actuators["ball_joints"].effort_limit_sim = self.control.ball_joint_effort_limit_sim
        self.robot_cfg.actuators["ball_joints"].velocity_limit_sim = self.control.ball_joint_velocity_limit_sim
        self.robot_cfg.actuators["wheel_joints"].stiffness = self.control.wheel_joint_stiffness
        self.robot_cfg.actuators["wheel_joints"].damping = self.control.wheel_joint_damping
        self.robot_cfg.actuators["wheel_joints"].effort_limit_sim = self.control.wheel_joint_effort_limit_sim
        self.robot_cfg.actuators["wheel_joints"].velocity_limit_sim = self.control.wheel_joint_velocity_limit_sim


__all__ = ["CompleteCarEnvCfg"]
