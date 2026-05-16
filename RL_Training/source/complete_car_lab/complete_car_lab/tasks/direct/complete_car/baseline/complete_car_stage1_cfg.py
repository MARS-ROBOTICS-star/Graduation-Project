"""Stage1: terrain curriculum."""

from __future__ import annotations

import math

from isaaclab.utils import configclass

from ..assets.robot_cfg import build_complete_car_robot_cfg
from ..base.complete_car_cfg import CompleteCarEnvCfg


@configclass
class CompleteCarStage1EnvCfg(CompleteCarEnvCfg):
    stage_name: str = "stage1"

    def __post_init__(self) -> None:
        # Stage1 keeps a full local copy of the active tunables so future terrain
        # training changes can stay inside this file without editing the base cfg.
        self.stage_name = "stage1"
        self.episode_length_s = 40.0
        self.is_finite_horizon = False
        self.decimation = 4

        self.scene.num_envs = 32
        self.scene.env_spacing = 2.0
        self.scene.replicate_physics = True
        self.scene.clone_in_fabric = True

        self.commands.num_commands = 4
        self.commands.num_waypoints_per_episode = 1
        self.commands.use_terrain_column_targets = True
        self.commands.terrain_goal_min_row_offset = 1
        self.commands.terrain_goal_max_row_offset = 1
        self.commands.terrain_goal_lateral_range_m = 3.0
        self.commands.terrain_goal_lateral_offset_excluded_names = (
            "stairs down",
            "discrete obstacles",
        )

        self.control.sim_dt = 1.0 / 120.0
        self.control.decimation = 4
        self.control.control_dt = 1.0 / 30.0
        self.control.base_forward_velocity_max = 2.0
        self.control.base_yaw_rate_max = 2.0
        self.control.base_allow_reverse = True
        self.control.ball_joint_stiffness = 120.0
        self.control.ball_joint_damping = 10.0
        self.control.ball_joint_effort_limit_sim = 60.0
        self.control.ball_joint_velocity_limit_sim = 2.0
        self.control.ball_joint_qdot_alloc_filter_tau_s = 0.04
        self.control.wheel_joint_stiffness = 0.0
        self.control.wheel_joint_damping = 0.0
        self.control.wheel_joint_effort_limit_sim = 20.0
        self.control.wheel_joint_velocity_limit_sim = 20.0
        self.control.low_slip_lambda_tracking = 1.0
        self.control.low_slip_lambda_lateral = 5.0
        self.control.contact_force_off_threshold = 0.01
        self.control.contact_force_on_threshold = 0.08
        self.control.wheel_torque_tracking_gain = 2.0
        self.control.wheel_slip_feedback_gain = 4.0
        self.control.wheel_slip_velocity_epsilon = 0.1
        self.control.terrain_speed_limit_enabled = True
        self.control.terrain_speed_limit_mps = 0.50
        self.control.terrain_speed_step_up_approach_mps = 0.45
        self.control.terrain_speed_step_up_climb_mps = 0.75
        self.control.terrain_speed_step_down_mps = 0.35
        self.control.terrain_speed_obstacle_mps = 0.40

        self.observations.use_history = True
        self.observations.history_length = 4
        self.observations.clip_observations = 100.0
        self.observations.wheel_slip_epsilon = 0.1
        self.observations.wheel_slip_angle_clip_rad = math.pi / 2.0
        self.observations.terrain_feature_height_scale_m = 0.25
        self.observations.scales.base_lin_vel = 1.0
        self.observations.scales.base_ang_vel = 1.0
        self.observations.scales.ball_joint_pos = 1.0
        self.observations.scales.ball_joint_vel = 1.0
        self.observations.scales.wheel_joint_vel = 1.0
        self.observations.scales.wheel_longitudinal_slip = 1.0
        self.observations.scales.wheel_slip_angle = 1.0
        self.observations.scales.wheel_normal_contact_force = 1.0
        self.observations.scales.commands = 1.0
        self.observations.scales.last_action = 1.0
        self.observations.noise.enabled = True
        self.observations.noise.level = 1.0
        self.observations.noise.base_lin_vel = 0.05
        self.observations.noise.base_ang_vel = 0.10
        self.observations.noise.projected_gravity = 0.01
        self.observations.noise.ball_joint_pos = 0.01
        self.observations.noise.ball_joint_vel = 0.05
        self.observations.noise.ball_joint_target_error = 0.01
        self.observations.noise.module_roll_pitch = 0.02
        self.observations.noise.wheel_joint_vel = 0.05
        self.observations.noise.wheel_longitudinal_slip = 0.0
        self.observations.noise.wheel_slip_angle = 0.0
        self.observations.noise.wheel_normal_contact_force = 0.02
        self.observations.noise.commands = 0.0

        self.rewards.only_positive_rewards = False
        self.rewards.params.target_position_tolerance = 0.5
        self.rewards.params.distance_to_target_denominator_scale = 0.01
        self.rewards.params.distance_to_target_weight = 10.0
        self.rewards.params.nominal_goal_distance_m = 8.0
        self.rewards.params.progress_to_target_clip_m = 0.25
        self.rewards.params.progress_to_target_relax_radius_m = 0.6
        self.rewards.params.progress_to_target_weight = 8.0
        self.rewards.params.reached_target_base_reward = 2.0
        self.rewards.params.reached_target_weight = 6.0
        self.rewards.params.far_from_target_margin = 3.0
        self.rewards.params.angle_diff_weight = 14.0
        self.rewards.params.slip_penalty_weight = -2.0
        self.rewards.params.slip_longitudinal_penalty_ratio = 2.0
        self.rewards.params.slip_angle_penalty_ratio = 1.0
        self.rewards.params.action_rate_penalty_weight = -10.0
        self.rewards.params.action_rate_base_ratio = 0.5
        self.rewards.params.action_rate_joint_ratio = 1.0
        self.rewards.params.contact_support_penalty_weight = -20.0
        self.rewards.params.contact_support_min_weight = 0.3
        self.rewards.params.contact_support_lr_balance_ratio = 0.15
        self.rewards.params.step_up_support_mid_ratio = 0.4
        self.rewards.params.step_up_support_rear_ratio = 0.6
        self.rewards.params.edge_height_low_threshold_m = 0.04
        self.rewards.params.edge_height_high_threshold_m = 0.10
        self.rewards.params.terrain_aware_edge_speed_penalty_weight = -80.0
        self.rewards.params.stuck_penalty_weight = -3.0
        self.rewards.params.stuck_gate_threshold = 0.3
        self.rewards.params.stuck_speed_threshold_mps = 0.10
        self.rewards.params.stuck_goal_ahead_threshold_m = 0.5
        self.rewards.params.stuck_penalty_grace_s = 0.5
        self.rewards.params.stuck_timeout_s = 4.0
        self.rewards.params.no_progress_penalty_weight = -1.0
        self.rewards.params.no_progress_min_delta_m = 0.003
        self.rewards.params.no_progress_hard_gate_threshold = 0.3
        self.rewards.params.airborne_spin_penalty_weight = -1.0
        self.rewards.params.airborne_spin_velocity_scale_radps = 20.0
        self.rewards.params.hard_terrain_spin_penalty_weight = -1.0
        self.rewards.params.hard_terrain_spin_speed_threshold_mps = 0.40
        self.rewards.params.hard_terrain_spin_slip_threshold = 3.0
        self.rewards.params.hard_terrain_spin_slip_scale = 3.0
        self.rewards.params.step_up_front_posture_penalty_weight = -12.0
        self.rewards.params.front_pitch_height_gain_rad_per_m = 3.0
        self.rewards.params.front_pitch_max_ref_rad = 0.30
        self.rewards.params.front_pitch_sigma_rad = 0.20
        self.rewards.params.step_up_approach_distance_min_m = 0.20
        self.rewards.params.step_up_approach_distance_max_m = 1.20
        self.rewards.params.step_up_posture_front_gap_start_m = 0.90
        self.rewards.params.step_up_posture_front_gap_full_m = 0.25
        self.rewards.params.step_up_goal_ahead_threshold_m = 0.5
        self.rewards.params.step_up_progress_quality_min_multiplier = 0.2
        self.rewards.params.progress_quality_slip_scale = 4.0
        self.rewards.params.progress_quality_pitch_rate_sigma_radps = 1.0
        self.rewards.params.progress_quality_stuck_time_scale_s = 2.0
        self.rewards.params.step_up_module_progress_reward_weight = 40.0
        self.rewards.params.step_up_module_height_progress_scale_m = 0.05
        self.rewards.params.step_up_module_progress_front_ratio = 0.15
        self.rewards.params.step_up_module_progress_middle_ratio = 0.35
        self.rewards.params.step_up_module_progress_rear_ratio = 0.50
        self.rewards.params.rear_follow_reward_weight = 8.0
        self.rewards.params.rear_follow_penalty_weight = -36.0
        self.rewards.params.rear_follow_progress_scale_m = 0.03
        self.rewards.params.rear_follow_deficit_scale_m = 0.05
        self.rewards.params.rear_follow_front_middle_threshold_m = 0.03
        self.rewards.params.rear_follow_hold_min_score = 0.70
        self.rewards.params.rear_follow_hold_reward_ratio = 0.25
        self.rewards.params.quality_row_advance_reward_weight = 1.0
        self.rewards.params.quality_row_advance_min_score = 0.3
        self.rewards.params.quality_gated_terrain_advance = False
        self.rewards.params.quality_advance_min_score = 0.35
        self.rewards.params.quality_advance_actual_overspeed_margin_mps = 0.10
        self.rewards.params.quality_advance_contact_min = 0.70
        self.rewards.params.quality_advance_module_progress_min = 0.35
        self.rewards.params.quality_advance_front_progress_threshold_m = 0.03
        self.rewards.params.quality_advance_middle_progress_threshold_m = 0.03
        self.rewards.params.quality_advance_rear_progress_threshold_m = 0.02
        self.rewards.params.terrain_actual_overspeed_penalty_ratio = 3.0
        self.rewards.params.recovery_stuck_time_threshold_s = 0.5
        self.rewards.params.recovery_reverse_cmd_threshold_mps = 0.05
        self.rewards.params.recovery_reverse_reward_window_s = 1.0
        self.rewards.params.recovery_min_reverse_time_s = 0.10
        self.rewards.params.recovery_success_step_progress_m = 0.005
        self.rewards.params.recovery_success_progress_m = 0.03
        self.rewards.params.recovery_success_forward_speed_mps = 0.08
        self.rewards.params.recovery_reverse_reward_weight = 0.2
        self.rewards.params.recovery_success_reward_weight = 1.0
        self.rewards.params.drop_anti_dive_penalty_weight = -40.0
        self.rewards.params.drop_guard_gate_threshold = 0.3
        self.rewards.params.drop_guard_release_front_support = 0.7
        self.rewards.params.drop_guard_release_pitch_rate_radps = 0.5
        self.rewards.params.drop_guard_release_vz_down_mps = 0.15
        self.rewards.params.drop_guard_release_time_s = 0.20
        self.rewards.params.drop_guard_latch_penalty_ratio = 1.5
        self.rewards.params.drop_theta_safe_rad = 0.0
        self.rewards.params.drop_pitch_sigma_rad = 0.20
        self.rewards.params.drop_pitch_rate_sigma_radps = 1.0
        self.rewards.params.drop_vz_down_sigma_mps = 0.5
        self.rewards.params.progress_gate_longitudinal_k = 3.0
        self.rewards.params.progress_gate_slip_angle_scale_rad = 1.5
        self.rewards.params.progress_gate_min_multiplier = 0.25
        self.rewards.params.progress_gate_max_multiplier = 1.5
        self.rewards.params.progress_pitch_gate_deadband_deg = 1.0
        self.rewards.params.progress_pitch_gate_k_rad = 0.0
        self.rewards.params.low_slip_longitudinal_threshold = 1.0
        self.rewards.params.low_slip_angle_threshold_rad = 0.35

        self.terminations.orientation_limit_deg = 35.0
        self.terminations.ball_joint_pos_lower_limits = (-0.7, -0.8, -0.5, -0.7, -1.0, -0.5)
        self.terminations.ball_joint_pos_upper_limits = (0.7, 0.5, 0.5, 0.7, 0.9, 0.5)
        self.control.ball_joint_action_position_lower_limits = (-0.7, -0.8, -0.5, -0.7, -1.0, -0.5)
        self.control.ball_joint_action_position_upper_limits = (0.7, 0.5, 0.5, 0.7, 0.8, 0.5)

        self.resets.root_pos = (0.0, 0.0, 0.30)
        self.resets.root_lin_vel = (0.0, 0.0, 0.0)
        self.resets.root_ang_vel = (0.0, 0.0, 0.0)
        self.resets.root_x_range = (-1.0, 1.0)
        self.resets.root_y_range = (-1.0, 1.0)
        self.resets.root_yaw_range = (0.0, 0.0)
        self.resets.ball_joint_pos_range = (-0.02, 0.02)
        self.resets.ball_joint_vel_range = (-0.05, 0.05)
        self.resets.wheel_joint_pos_range = (0.0, 0.0)
        self.resets.wheel_joint_vel_range = (-0.5, 0.5)

        self.randomization.enable_action_randomization = True
        self.randomization.joint_position_noise_scale = 0.0
        self.randomization.action_noise_std = 0.015
        self.randomization.action_bias_std = 0.005
        self.randomization.enable_actuator_scale_randomization = True
        self.randomization.ball_joint_stiffness_scale_range = (0.80, 1.20)
        self.randomization.ball_joint_damping_scale_range = (0.80, 1.20)
        self.randomization.ball_joint_effort_limit_scale_range = (0.85, 1.15)
        self.randomization.ball_joint_velocity_limit_scale_range = (0.90, 1.10)
        self.randomization.wheel_joint_effort_limit_scale_range = (0.85, 1.15)
        self.randomization.enable_wheel_friction_randomization = True
        self.randomization.wheel_static_friction_range = (0.80, 1.20)
        self.randomization.wheel_dynamic_friction_range = (0.70, 1.10)

        self.terrain.enabled = True
        self.terrain.mode = "generator"
        self.terrain.prim_path = "/World/terrain/stage1"
        self.terrain.diffuse_color = (0.0, 0.0, 0.0)
        self.terrain.static_friction = 1.0
        self.terrain.dynamic_friction = 1.0
        self.terrain.restitution = 0.0
        self.terrain.measure_heights = True
        self.terrain.patch_front_extent = 0.942209
        self.terrain.patch_rear_extent = 0.942209
        self.terrain.patch_half_width = 0.280374
        self.terrain.patch_preview_length = 1.0
        self.terrain.patch_rear_margin = 0.40
        self.terrain.patch_side_margin = 0.5
        self.terrain.patch_origin_offset_xy = (0.0, 0.0)
        self.terrain.patch_resolution_x = 0.10
        self.terrain.patch_resolution_y = 0.10
        self.terrain.measured_points_x = []
        self.terrain.measured_points_y = []
        self.terrain.height_scanner_prim_path = "{ENV_REGEX_NS}/Robot/complete_car_alternative/body_car_chassis"
        self.terrain.height_scanner_update_period = 0.02
        self.terrain.height_scanner_offset = (0.0, 0.0, 20.0)
        self.terrain.step_spawn_back_range = (2.0, 3.0)
        self.terrain.base_spawn_clearance = 0.30
        self.terrain.gap_spawn_back_range = (0.0, 0.4)
        self.terrain.other_spawn_xy_range = (-0.5, 0.5)
        self.terrain.generator.horizontal_scale = 0.1
        self.terrain.generator.vertical_scale = 0.005
        self.terrain.generator.border_size = 25.0
        self.terrain.generator.terrain_length = 8.0
        self.terrain.generator.terrain_width = 8.0
        self.terrain.generator.num_rows = 20
        self.terrain.generator.num_cols = 10
        self.terrain.generator.slope_threshold = 0.75
        self.terrain.generator.add_roughness = False
        self.terrain.generator.roughness_height_range = (0.01, 0.04)
        self.terrain.generator.roughness_downsampled_scale = 0.2
        self.terrain.generator.terrain_dict = {
            "flat": 0.10,
            "slope down": 0.10,
            "slope up": 0.10,
            "uneven rough": 0.20,
            "stairs down": 0.30,
            "discrete obstacles": 0.20,
        }

        self.curriculum.enabled = True
        self.curriculum.max_init_terrain_level = 5
        self.curriculum.initial_min_terrain_level_by_name = {
            "stairs down": 0,
            "discrete obstacles": 0,
        }
        self.curriculum.initial_max_terrain_level_by_name = {
            "stairs down": 4,
            "discrete obstacles": 4,
        }
        self.curriculum.default_terrain_name = "flat"
        self.curriculum.terrain_column_move_down_progress_ratio = 0.30
        self.curriculum.terrain_column_recycle_completed_envs = True
        self.curriculum.terrain_column_completed_retention_ratio = 0.20
        self.curriculum.terrain_column_stop_when_all_completed = False
        self.curriculum.terrain_column_hard_completion_success_count = 100
        self.curriculum.terrain_column_full_pass_completion_columns = (8, 9)
        self.curriculum.terrain_column_full_pass_start_level = 4
        self.curriculum.terrain_column_full_pass_success_count = 100
        self.curriculum.terrain_column_full_pass_start_level_by_name = {
            "stairs down": 14,
        }
        self.curriculum.terrain_column_full_pass_success_count_by_name = {
            "stairs down": 100,
        }
        self.curriculum.terrain_column_completed_hard_window_start_level = 4
        self.curriculum.terrain_column_completed_hard_window_start_level_by_name = {
            "stairs down": 14,
            "discrete obstacles": 4,
        }

        self.sensors.imu.enabled = False
        self.sensors.stereo_camera.enabled = False
        self.sensors.lidar.enabled = False
        self.sensors.enable_height_scanner = False
        self.sensors.height_scanner_debug_vis = False
        self.sensors.wheel_contact_max_points_per_env = 128

        self.logging.enable_stage1_per_wheel_debug = False
        self.logging.step_metrics_interval = 64

        self.debug.enable_debug_draw = False
        self.debug.visualize_goal_position = False
        self.debug.visualize_goal_heading = False
        self.debug.visualize_wheel_slip = False
        self.debug.visualize_height_patch = False
        self.debug.height_patch_visualization_env_indices = (0,)
        self.debug.height_patch_marker_radius = 0.035
        self.debug.height_patch_marker_height_offset = 0.035
        self.debug.height_patch_color_range_m = 0.30
        self.debug.visualize_height_patch_positive_y_axis = False
        self.debug.create_follow_views = False
        self.debug.follow_view_chase_env_indices = ()
        self.debug.follow_view_top_height = 8.0
        self.debug.follow_view_chase_env_index = 0
        self.debug.follow_view_chase_offset_b = (-4.0, -3.0, 2.4)
        self.debug.follow_view_chase_target_offset_b = (1.0, 0.0, 0.4)
        self.debug.follow_view_forward_height_m = 3.0
        self.debug.follow_view_forward_distance_m = 4.0
        self.debug.log_sensor_outputs = False

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
        self.sim.physx.enable_external_forces_every_iteration = False

        self.robot = build_complete_car_robot_cfg(self.control, self.resets)
