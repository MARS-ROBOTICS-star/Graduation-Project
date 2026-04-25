"""Stage0: 平地 baseline。"""

from __future__ import annotations

import math

from isaaclab.utils import configclass

from ..assets.robot_cfg import build_complete_car_robot_cfg
from ..base.complete_car_cfg import CompleteCarEnvCfg


@configclass
class CompleteCarStage0EnvCfg(CompleteCarEnvCfg):
    stage_name: str = "stage0"

    def __post_init__(self) -> None:
        # Stage0 keeps a full local copy of the active tunables so future tuning can
        # stay inside this file without bouncing back to the base template.
        self.stage_name = "stage0"
        self.episode_length_s = 40.0
        self.decimation = 2

        self.scene.num_envs = 64
        self.scene.env_spacing = 4.0
        self.scene.replicate_physics = True
        self.scene.clone_in_fabric = True

        self.commands.num_commands = 4
        self.commands.num_waypoints_per_episode = 2
        self.commands.resampling_time = 40.0
        self.commands.goal_distance = 10.0
        self.commands.goal_direction_max_deg = 30.0
        self.commands.goal_heading_delta_max_deg = 0.0
        self.commands.zero_command = False
        self.commands.rel_standing_envs = 0.0

        self.control.sim_dt = 1.0 / 120.0
        self.control.decimation = 2
        self.control.control_dt = 1.0 / 60.0
        self.control.ball_joint_planner_gains = (10.0, 10.0, 10.0, 10.0, 10.0, 10.0)
        self.control.base_forward_velocity_max = 2.0
        self.control.base_yaw_rate_max = 2.0
        self.control.base_allow_reverse = True
        self.control.ball_joint_stiffness = 8000.0
        self.control.ball_joint_damping = 1000.0
        self.control.ball_joint_effort_limit_sim = 20.0
        self.control.ball_joint_velocity_limit_sim = 1.0
        self.control.ball_joint_planner_qdot_limits = (1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
        self.control.wheel_joint_stiffness = 0.0
        self.control.wheel_joint_damping = 0.0
        self.control.wheel_joint_effort_limit_sim = 15.0
        self.control.wheel_joint_velocity_limit_sim = 20.0
        self.control.low_slip_lambda_tracking = 1.0
        self.control.low_slip_lambda_lateral = 10.0
        self.control.contact_force_off_threshold = 0.01
        self.control.contact_force_on_threshold = 0.08
        self.control.wheel_torque_tracking_gain = 1.5
        self.control.wheel_slip_feedback_gain = 8.0
        self.control.wheel_slip_velocity_epsilon = 0.1

        self.observations.use_history = False
        self.observations.history_length = 1
        self.observations.clip_observations = 100.0
        self.observations.wheel_slip_epsilon = 0.1
        self.observations.scales.base_lin_vel = 1.0
        self.observations.scales.base_ang_vel = 1.0
        self.observations.scales.projected_gravity = 1.0
        self.observations.scales.ball_joint_pos = 1.0
        self.observations.scales.ball_joint_vel = 1.0
        self.observations.scales.ball_joint_target_error = 1.0
        self.observations.scales.module_roll_pitch = 1.0
        self.observations.scales.wheel_joint_vel = 1.0
        self.observations.scales.wheel_longitudinal_slip = 1.0
        self.observations.scales.wheel_slip_angle = 1.0
        self.observations.scales.wheel_normal_contact_force = 1.0
        self.observations.scales.commands = 1.0
        self.observations.scales.last_action = 1.0
        self.observations.noise.enabled = False
        self.observations.noise.level = 1.0
        self.observations.noise.base_lin_vel = 0.1
        self.observations.noise.base_ang_vel = 0.2
        self.observations.noise.projected_gravity = 0.02
        self.observations.noise.ball_joint_pos = 0.01
        self.observations.noise.ball_joint_vel = 0.05
        self.observations.noise.ball_joint_target_error = 0.01
        self.observations.noise.module_roll_pitch = 0.02
        self.observations.noise.wheel_joint_vel = 0.05
        self.observations.noise.wheel_longitudinal_slip = 0.0
        self.observations.noise.wheel_slip_angle = 0.0
        self.observations.noise.wheel_normal_contact_force = 0.0
        self.observations.noise.commands = 0.0

        self.rewards.only_positive_rewards = False
        self.rewards.params.target_position_tolerance = 0.5
        self.rewards.params.target_yaw_tolerance_deg = math.degrees(0.1)
        self.rewards.params.distance_to_target_denominator_scale = 0.01
        self.rewards.params.distance_to_target_weight = 6.0
        self.rewards.params.progress_to_target_clip_m = 0.25
        self.rewards.params.progress_to_target_relax_radius_m = 4.0
        self.rewards.params.progress_to_target_weight = 8.0
        self.rewards.params.reached_target_base_reward = 2.0
        self.rewards.params.reached_target_weight = 6.0
        self.rewards.params.far_from_target_margin = 6.0
        self.rewards.params.far_from_target_weight = -2.0
        self.rewards.params.angle_diff_weight = 6.0
        self.rewards.params.turn_speed_penalty_weight = -2.0
        self.rewards.params.slip_penalty_weight = -2.0
        self.rewards.params.slip_angle_penalty_ratio = 6.0
        self.rewards.params.progress_gate_longitudinal_k = 3.0
        self.rewards.params.progress_gate_slip_angle_scale_rad = 1.5
        self.rewards.params.progress_gate_min_multiplier = 0.10
        self.rewards.params.progress_gate_max_multiplier = 1.5
        self.rewards.params.low_slip_longitudinal_threshold = 1.0
        self.rewards.params.low_slip_angle_threshold_rad = 0.35

        self.terminations.orientation_limit_deg = 30.0
        self.terminations.head_tail_roll_limit_deg = 35.0
        self.terminations.ball_joint_pos_lower_limits = (-0.6, -1.0, -0.5, -0.6, -1.0, -0.5)
        self.terminations.ball_joint_pos_upper_limits = (0.6, 0.4, 0.5, 0.6, 0.4, 0.5)

        self.resets.root_pos = (0.0, 0.0, 0.30)
        self.resets.root_lin_vel = (0.0, 0.0, 0.0)
        self.resets.root_ang_vel = (0.0, 0.0, 0.0)
        self.resets.root_x_range = (-1.0, 1.0)
        self.resets.root_y_range = (-1.0, 1.0)
        self.resets.root_yaw_range = (0.0 * math.pi, 0.0 * math.pi)
        self.resets.ball_joint_pos_range = (0.0, 0.0)
        self.resets.ball_joint_vel_range = (0.0, 0.0)
        self.resets.wheel_joint_pos_range = (0.0, 0.0)
        self.resets.wheel_joint_vel_range = (0.0, 0.0)

        self.randomization.enable_action_randomization = False
        self.randomization.joint_position_noise_scale = 0.0
        self.randomization.action_noise_std = 0.0
        self.randomization.action_bias_std = 0.0

        self.curriculum.enabled = False
        self.curriculum.max_init_terrain_level = 0
        self.curriculum.default_terrain_name = "flat"
        self.curriculum.move_up_distance_ratio = 0.5
        self.curriculum.move_down_command_ratio = 0.5

        self.terrain.enabled = False
        self.terrain.mode = "plane"
        self.terrain.prim_path = "/World/terrain/stage1"
        self.terrain.diffuse_color = (0.42, 0.38, 0.30)
        self.terrain.static_friction = 1.0
        self.terrain.dynamic_friction = 1.0
        self.terrain.restitution = 0.0
        self.terrain.measure_heights = False
        self.terrain.patch_front_extent = 0.942209
        self.terrain.patch_rear_extent = 0.942209
        self.terrain.patch_half_width = 0.280374
        self.terrain.patch_preview_length = 1.0
        self.terrain.patch_rear_margin = 0.40
        self.terrain.patch_side_margin = 1.0
        self.terrain.patch_origin_offset_xy = (0.0, 0.0)
        self.terrain.patch_resolution_x = 0.10
        self.terrain.patch_resolution_y = 0.10
        self.terrain.height_scanner_update_period = 0.02
        self.terrain.height_scanner_offset = (0.0, 0.0, 20.0)
        self.terrain.step_spawn_back_range = (2.0, 3.0)
        self.terrain.gap_spawn_back_range = (0.0, 0.4)
        self.terrain.other_spawn_xy_range = (-0.5, 0.5)

        self.sensors.imu.enabled = False
        self.sensors.stereo_camera.enabled = False
        self.sensors.lidar.enabled = False
        self.sensors.enable_height_scanner = False
        self.sensors.height_scanner_debug_vis = False

        self.debug.enable_debug_draw = False
        self.debug.log_sensor_outputs = True

        super().__post_init__()

        self.sim.dt = self.control.sim_dt
        self.sim.render_interval = self.decimation
        self.sim.gravity = (0.0, 0.0, -9.81)
        self.sim.use_fabric = True
        self.sim.physics_material.static_friction = self.terrain.static_friction
        self.sim.physics_material.dynamic_friction = self.terrain.dynamic_friction
        self.sim.physics_material.restitution = self.terrain.restitution
        self.sim.physx.solver_type = 1
        self.sim.physx.max_position_iteration_count = 8
        self.sim.physx.max_velocity_iteration_count = 4
        self.sim.physx.bounce_threshold_velocity = 0.2
        self.sim.physx.friction_offset_threshold = 0.04
        self.sim.physx.friction_correlation_distance = 0.025
        self.sim.physx.enable_stabilization = True
        self.sim.physx.enable_external_forces_every_iteration = True

        self.robot = build_complete_car_robot_cfg(self.control, self.resets)
