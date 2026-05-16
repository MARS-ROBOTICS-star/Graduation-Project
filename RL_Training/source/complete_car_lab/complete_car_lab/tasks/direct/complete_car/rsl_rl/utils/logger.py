# Copyright (c) 2021-2026, ETH Zurich and NVIDIA CORPORATION
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause


from __future__ import annotations

import git
import os
import pathlib
import statistics
import time
import torch
from collections import deque

import rsl_rl


TENSORBOARD_TAG_ALIASES = {
    "Termination/success_rate": "00_Behavior/00_termination_success_rate",
    "Tracking/active_waypoint_pos_error": "00_Behavior/02_active_waypoint_pos_error",
    "Tracking/active_waypoint_bearing_abs": "00_Behavior/03_active_waypoint_bearing_abs",
    "Tracking/active_segment_completion_pct": "00_Behavior/04_active_segment_completion_pct",
    "Observation/wheel_longitudinal_slip_abs_mean_raw": "00_Behavior/05_wheel_longitudinal_slip_abs_mean_raw",
    "Observation/wheel_slip_angle_abs_mean_raw": "00_Behavior/06_wheel_slip_angle_abs_mean_raw",
    "LowSlip/combined_pass_rate": "00_Behavior/24_low_slip_combined_pass_rate",
    "LowSlip/longitudinal_slip_pass_rate": "00_Behavior/25_low_slip_longitudinal_pass_rate",
    "LowSlip/slip_angle_pass_rate": "00_Behavior/26_low_slip_angle_pass_rate",
    "LowSlip/longitudinal_slip_margin": "00_Behavior/27_low_slip_longitudinal_margin",
    "LowSlip/slip_angle_margin": "00_Behavior/28_low_slip_angle_margin",
    "ProgressGate/combined_gate": "00_Behavior/29_progress_gate_combined",
    "ProgressGate/multiplier": "00_Behavior/30_progress_gate_multiplier",
    "ProgressGate/longitudinal_gate": "00_Behavior/31_progress_gate_longitudinal",
    "ProgressGate/slip_angle_gate": "00_Behavior/32_progress_gate_slip_angle",
    "ProgressGate/positive_progress_raw": "00_Behavior/33_progress_positive_raw",
    "ProgressGate/negative_progress_raw": "00_Behavior/34_progress_negative_raw",
    "ProgressGate/ungated_progress_raw": "00_Behavior/35_progress_ungated_raw",
    "ProgressGate/pitch_gate": "00_Behavior/39_progress_pitch_gate",
    "Action/wheel_speed_reference_abs_mean_raw": "00_Behavior/07_wheel_speed_reference_abs_mean_raw",
    "Action/wheel_torque_target_abs_mean_raw": "00_Behavior/20_wheel_torque_target_abs_mean_raw",
    "Reward/total": "00_Behavior/08_reward_total",
    "Reward/reached_target": "00_Behavior/09_reached_target",
    "Reward/distance_to_target": "00_Behavior/10_distance_to_target",
    "Reward/angle_diff": "00_Behavior/11_angle_diff",
    "Reward/progress_to_target": "00_Behavior/13_progress_to_target",
    "Termination/time_out_rate": "00_Behavior/15_time_out_rate",
    "Termination/far_from_target_rate": "00_Behavior/16_far_from_target_rate",
    "Termination/ball_joint_limit_rate": "00_Behavior/17_ball_joint_limit_rate",
    "Observation/wheel_normal_contact_force_sum_raw": "00_Behavior/18_wheel_normal_contact_force_sum_raw",
    "Observation/roll_deg": "00_Behavior/36_roll_deg",
    "Observation/pitch_deg": "00_Behavior/37_pitch_deg",
    "Tracking/waypoints_completed_mean": "00_Behavior/21_waypoints_completed_mean",
    "Tracking/episode_completion_pct": "00_Behavior/22_episode_completion_pct",
    "Tracking/active_waypoint_index_mean": "00_Behavior/23_active_waypoint_index_mean",
    "Tracking/terrain_target_advances_mean": "00_Behavior/38_terrain_target_advances_mean",
    "Terrain/current_level_mean": "Terrain/00_current_level_mean",
    "Terrain/forward_x_from_current_tile_origin_mean": "Terrain/01_forward_x_from_current_tile_origin_mean",
    "Train/mean_episode_length": "Train/00_mean_episode_length",
    "Train/mean_reward": "Train/01_mean_reward",
    "Train/mean_episode_length/time": "Train/00_mean_episode_length/time",
    "Train/mean_reward/time": "Train/01_mean_reward/time",
    "Loss/value": "Loss/00_value",
    "Loss/learning_rate": "Loss/01_learning_rate",
    "Loss/entropy": "Loss/02_entropy",
    "Loss/surrogate": "Loss/03_surrogate",
    "Policy/mean_std": "Policy/00_mean_std",
    "Perf/total_fps": "Perf/00_total_fps",
    "Perf/collection_time": "Perf/01_collection_time",
    "Perf/learning_time": "Perf/02_learning_time",
    "Observation/ball_joint_vel_abs_mean_raw": "Observation/00_ball_joint_vel_abs_mean_raw",
    "Observation/ball_joint_vel_limit_rate_raw": "Observation/01_ball_joint_vel_limit_rate_raw",
    "Action/policy_abs_mean": "Action/00_policy_abs_mean",
    "Action/policy_std": "Action/01_policy_std",
    "Action/ball_joint_desired_delta_abs_mean_raw": "Action/02_ball_joint_desired_delta_abs_mean_raw",
    "Action/ball_joint_desired_delta_l2_raw": "Action/03_ball_joint_desired_delta_l2_raw",
    "Action/desired_planar_command_abs_mean_raw": "Action/06_desired_planar_command_abs_mean_raw",
    "Action/shaped_planar_command_abs_mean_raw": "Action/07_shaped_planar_command_abs_mean_raw",
    "Action/planar_command_shaping_delta_abs_mean_raw": "Action/08_planar_command_shaping_delta_abs_mean_raw",
    "Action/desired_planar_vx_raw": "Action/09_desired_planar_vx_raw",
    "Action/desired_planar_wz_raw": "Action/10_desired_planar_wz_raw",
    "Action/shaped_planar_vx_raw": "Action/11_shaped_planar_vx_raw",
    "Action/shaped_planar_wz_raw": "Action/12_shaped_planar_wz_raw",
    "Action/planar_command_delta_vx_raw": "Action/13_planar_command_delta_vx_raw",
    "Action/planar_command_delta_wz_raw": "Action/14_planar_command_delta_wz_raw",
    "LowLevel/v_parallel_abs_mean_raw": "LowLevel/00_v_parallel_abs_mean_raw",
    "LowLevel/v_perp_abs_mean_raw": "LowLevel/01_v_perp_abs_mean_raw",
    "LowLevel/delta_v_abs_mean_raw": "LowLevel/02_delta_v_abs_mean_raw",
    "LowLevel/tau0_abs_mean_raw": "LowLevel/03_tau0_abs_mean_raw",
    "LowLevel/tau1_abs_mean_raw": "LowLevel/05_tau1_abs_mean_raw",
    "Reward/slip_penalty": "Reward/21_slip_penalty",
    "Command/goal_rel_x": "Command/00_goal_rel_x",
    "Command/goal_rel_y": "Command/01_goal_rel_y",
    "Command/goal_rel_z": "Command/02_goal_rel_z",
    "Command/goal_rel_heading": "Command/03_goal_rel_heading",
    "Command/goal_direction_offset_deg": "Command/08_goal_direction_offset_deg",
    "Command/goal_heading_offset_deg": "Command/09_goal_heading_offset_deg",
}

CONSOLE_PRIORITY_TAGS = (
    "Action/policy_abs_mean",
    "Action/policy_std",
    "Action/ball_joint_desired_delta_abs_mean_raw",
    "Observation/ball_joint_vel_limit_rate_raw",
    "Observation/ball_joint_target_error_abs_mean_raw",
    "Action/wheel_speed_reference_abs_mean_raw",
    "Action/wheel_torque_target_abs_mean_raw",
    "Action/desired_planar_command_abs_mean_raw",
    "Action/shaped_planar_command_abs_mean_raw",
    "Action/planar_command_shaping_delta_abs_mean_raw",
    "Reward/total",
    "Reward/reached_target",
    "Reward/distance_to_target",
    "Reward/progress_to_target",
    "Reward/angle_diff",
    "Reward/slip_penalty",
    "Observation/wheel_longitudinal_slip_abs_mean_raw",
    "Observation/wheel_slip_angle_abs_mean_raw",
    "LowSlip/combined_pass_rate",
    "LowSlip/longitudinal_slip_pass_rate",
    "LowSlip/slip_angle_pass_rate",
    "LowSlip/longitudinal_slip_margin",
    "LowSlip/slip_angle_margin",
    "ProgressGate/combined_gate",
    "ProgressGate/multiplier",
    "ProgressGate/longitudinal_gate",
    "ProgressGate/slip_angle_gate",
    "ProgressGate/pitch_gate",
    "Observation/wheel_normal_contact_force_sum_raw",
    "Observation/pitch_deg",
    "Observation/ball_joint_vel_abs_mean_raw",
    "LowLevel/v_parallel_abs_mean_raw",
    "LowLevel/v_perp_abs_mean_raw",
    "LowLevel/delta_v_abs_mean_raw",
    "LowLevel/tau0_abs_mean_raw",
    "LowLevel/tau1_abs_mean_raw",
    "Termination/success_rate",
    "Termination/time_out_rate",
    "Termination/far_from_target_rate",
    "Termination/ball_joint_limit_rate",
    "Termination/terminated_rate",
    "Tracking/active_waypoint_pos_error",
    "Tracking/active_waypoint_bearing_abs",
    "Tracking/active_segment_completion_pct",
    "Tracking/terrain_target_advances_mean",
    "Terrain/current_level_mean",
    "Terrain/forward_x_from_current_tile_origin_mean",
    "Tracking/waypoints_completed_mean",
    "Tracking/episode_completion_pct",
)

TENSORBOARD_EXTRA_TAGS = {
    "Termination/success_rate",
    "Tracking/active_waypoint_pos_error",
    "Tracking/active_waypoint_bearing_abs",
    "Tracking/active_segment_completion_pct",
    "Tracking/active_waypoint_index_mean",
    "Tracking/waypoints_completed_mean",
    "Tracking/terrain_target_advances_mean",
    "Tracking/episode_completion_pct",
    "Terrain/current_level_mean",
    "Terrain/forward_x_from_current_tile_origin_mean",
    "Observation/wheel_longitudinal_slip_abs_mean_raw",
    "Observation/wheel_slip_angle_abs_mean_raw",
    "LowSlip/combined_pass_rate",
    "LowSlip/longitudinal_slip_pass_rate",
    "LowSlip/slip_angle_pass_rate",
    "LowSlip/longitudinal_slip_margin",
    "LowSlip/slip_angle_margin",
    "ProgressGate/combined_gate",
    "ProgressGate/multiplier",
    "ProgressGate/longitudinal_gate",
    "ProgressGate/slip_angle_gate",
    "ProgressGate/positive_progress_raw",
    "ProgressGate/negative_progress_raw",
    "ProgressGate/ungated_progress_raw",
    "ProgressGate/pitch_gate",
    "Action/wheel_speed_reference_abs_mean_raw",
    "Action/wheel_torque_target_abs_mean_raw",
    "Reward/total",
    "Reward/reached_target",
    "Reward/distance_to_target",
    "Reward/progress_to_target",
    "Reward/angle_diff",
    "Reward/slip_penalty",
    "Termination/time_out_rate",
    "Termination/far_from_target_rate",
    "Termination/ball_joint_limit_rate",
    "Observation/wheel_normal_contact_force_sum_raw",
    "Observation/roll_deg",
    "Observation/pitch_deg",
    "Action/policy_abs_mean",
    "Action/policy_std",
    "Action/contact_weight_mean_raw",
    "Action/desired_planar_command_abs_mean_raw",
    "Action/shaped_planar_command_abs_mean_raw",
    "Action/planar_command_shaping_delta_abs_mean_raw",
    "Action/desired_planar_vx_raw",
    "Action/desired_planar_wz_raw",
    "Action/shaped_planar_vx_raw",
    "Action/shaped_planar_wz_raw",
    "Action/planar_command_delta_vx_raw",
    "Action/planar_command_delta_wz_raw",
    "LowLevel/v_parallel_abs_mean_raw",
    "LowLevel/v_perp_abs_mean_raw",
    "LowLevel/delta_v_abs_mean_raw",
    "LowLevel/tau0_abs_mean_raw",
    "LowLevel/tau1_abs_mean_raw",
    "Command/goal_rel_x",
    "Command/goal_rel_y",
    "Command/goal_rel_z",
    "Command/goal_rel_heading",
    "Command/goal_direction_offset_deg",
    "Command/goal_heading_offset_deg",
    "Observation/ball_joint_vel_abs_mean_raw",
    "Observation/ball_joint_vel_limit_rate_raw",
    "Action/ball_joint_desired_delta_abs_mean_raw",
    "Action/ball_joint_desired_delta_l2_raw",
    "Observation/ball_joint_pos_abs_mean_raw",
    "Observation/ball_joint_target_error_abs_mean_raw",
    "Observation/base_lin_vel_y_raw",
    "Observation/projected_gravity_xy_norm_raw",
    "Observation/wheel_joint_vel_abs_mean_raw",
    "Observation/spm1_platform_joint_x_limit_usage_max_raw",
    "Observation/spm1_platform_joint_x_limit_usage_mean_raw",
    "Observation/spm1_platform_joint_x_pos_raw",
    "Observation/spm1_platform_joint_y_limit_usage_max_raw",
    "Observation/spm1_platform_joint_y_limit_usage_mean_raw",
    "Observation/spm1_platform_joint_y_pos_raw",
    "Observation/spm1_platform_joint_z_limit_usage_max_raw",
    "Observation/spm1_platform_joint_z_limit_usage_mean_raw",
    "Observation/spm1_platform_joint_z_pos_raw",
    "Observation/spm2_platform_joint_x_limit_usage_max_raw",
    "Observation/spm2_platform_joint_x_limit_usage_mean_raw",
    "Observation/spm2_platform_joint_x_pos_raw",
    "Observation/spm2_platform_joint_y_limit_usage_max_raw",
    "Observation/spm2_platform_joint_y_limit_usage_mean_raw",
    "Observation/spm2_platform_joint_y_pos_raw",
    "Observation/spm2_platform_joint_z_limit_usage_max_raw",
    "Observation/spm2_platform_joint_z_limit_usage_mean_raw",
    "Observation/spm2_platform_joint_z_pos_raw",
    "episode/angle_diff",
    "episode/distance_to_target",
    "episode/far_from_target",
    "episode/progress_to_target",
    "episode/slip_penalty",
    "episode/goal_direction_offset_deg",
    "episode/goal_heading_offset_deg",
    "episode/goal_target_heading_world",
    "episode/goal_target_x_world",
    "episode/goal_target_y_world",
    "episode/goal_target_z_world",
    "episode/waypoints_completed",
    "episode/waypoint_completion_pct",
    "episode/waypoint_hit_rate",
    "episode/end_active_waypoint_pos_error",
    "episode/end_active_waypoint_bearing_abs",
    "episode/waypoint_hit_pos_error",
    "episode/success_hit_pos_error",
    "episode/reached_target",
    "episode/return",
    "episode/return_per_step",
    "episode_per_step/angle_diff",
    "episode_per_step/distance_to_target",
    "episode_per_step/far_from_target",
    "episode_per_step/progress_to_target",
    "episode_per_step/slip_penalty",
    "episode_per_step/reached_target",
}

STAGE1_TERRAIN_COLUMNS = (
    "col00_flat",
    "col01_slope_down",
    "col02_slope_up",
    "col03_rough",
    "col04_rough",
    "col05_stairs_down",
    "col06_stairs_down",
    "col07_stairs_down",
    "col08_obstacles",
    "col09_obstacles",
)

STAGE1_GLOBAL_EVAL_FIELDS = (
    "env_count",
    "rows_advanced_mean",
    "row_advance_rate",
    "max_row_reached_rate",
    "valid_target_masked",
    "train_active_rate",
    "train_retired_rate",
    "train_sample_rate",
    "completed_column_rate",
    "unfinished_column_count",
    "recycled_env_ever_rate",
    "completed_column_retention_target_rate",
    "completed_column_active_env_count",
    "completed_column_active_rate",
    "completed_column_active_ratio_of_active",
    "active_envs_per_completed_column_mean",
    "active_envs_per_unfinished_column_mean",
    "current_level_mean",
    "forward_x_mean",
    "tile_start_x_mean",
    "tile_origin_x_mean",
    "tile_end_x_mean",
    "root_x_mean",
    "target_x_mean",
    "effective_failure_rate",
    "far_rate",
    "ball_joint_limit_rate",
    "timeout_rate",
    "stuck_time_mean",
    "stuck_timeout_rate",
    "stuck_penalty_active_rate",
    "no_progress_active_rate",
    "stagnation_rate",
    "v_forward_mean",
    "speed_limit_active_rate",
    "vx_cmd_raw",
    "vx_cmd_limited",
    "vx_actual",
    "v_lateral_abs_mean",
    "lateral_velocity_ratio",
    "longitudinal_slip_abs_mean",
    "slip_angle_abs_mean",
    "combined_low_slip_pass_rate",
    "contact_loss_rate",
    "normal_force_sum_mean",
    "roll_abs_mean",
    "pitch_abs_mean",
    "pitch_rate_abs_mean",
    "vz_down_mean",
    "wheel_spin_airborne_mean",
    "quality_row_advance_rate",
    "hard_quality_advance_rate",
    "low_quality_hit_rate",
    "raw_hard_hit_rate",
    "row_advance_without_quality_rate",
    "quality_advance_score",
    "phase_module_progress_score",
    "front_climb_success_rate",
    "middle_climb_success_rate",
    "rear_follow_success_rate",
    "actual_overspeed_near_edge_rate",
    "row_contact_support_min",
    "row_stuck_time_max",
    "recovery_active_rate",
    "recovery_reverse_rate",
    "recovery_success_rate",
    "ball_joint_limit_usage_max",
    "action_abs_mean",
    "action_rate_abs_mean",
    "action_saturation_rate",
    "hardest_col_index",
    "hardest_col_difficulty_score",
)

STAGE1_FLAT_EVAL_FIELDS = (
    "retention_score",
    "env_count",
    "rows_advanced_mean",
    "row_advance_rate",
    "max_row_reached_rate",
    "valid_target_masked",
    "forward_x_mean",
    "v_forward_mean",
    "v_lateral_abs_mean",
    "lateral_velocity_ratio",
    "effective_failure_rate",
    "far_rate",
    "ball_joint_limit_rate",
    "stuck_time_mean",
    "stuck_timeout_rate",
    "stuck_penalty_active_rate",
    "no_progress_active_rate",
    "stagnation_rate",
    "speed_limit_active_rate",
    "vx_cmd_raw",
    "vx_cmd_limited",
    "vx_actual",
    "longitudinal_slip_abs_mean",
    "slip_angle_abs_mean",
    "combined_low_slip_pass_rate",
    "pitch_abs_mean",
    "pitch_rate_abs_mean",
    "vz_down_mean",
    "wheel_spin_airborne_mean",
    "quality_row_advance_rate",
    "hard_quality_advance_rate",
    "low_quality_hit_rate",
    "raw_hard_hit_rate",
    "row_advance_without_quality_rate",
    "quality_advance_score",
    "phase_module_progress_score",
    "front_climb_success_rate",
    "middle_climb_success_rate",
    "rear_follow_success_rate",
    "actual_overspeed_near_edge_rate",
    "row_contact_support_min",
    "row_stuck_time_max",
    "roll_abs_mean",
    "ball_joint_limit_usage_max",
    "action_saturation_rate",
)

STAGE1_PER_COLUMN_EVAL_FIELDS = (
    "env_count",
    "rows_advanced_mean",
    "row_advance_rate",
    "max_row_reached_rate",
    "valid_target_masked",
    "forward_x_mean",
    "current_level_mean",
    "effective_failure_rate",
    "far_rate",
    "ball_joint_limit_rate",
    "timeout_rate",
    "stuck_time_mean",
    "stuck_timeout_rate",
    "stuck_penalty_active_rate",
    "no_progress_active_rate",
    "stagnation_rate",
    "backward_rate",
    "v_forward_mean",
    "speed_limit_active_rate",
    "vx_cmd_raw",
    "vx_cmd_limited",
    "vx_actual",
    "v_lateral_abs_mean",
    "lateral_velocity_ratio",
    "yaw_rate_abs_mean",
    "longitudinal_slip_abs_mean",
    "slip_angle_abs_mean",
    "combined_low_slip_pass_rate",
    "contact_loss_rate",
    "normal_force_sum_mean",
    "roll_abs_mean",
    "pitch_abs_mean",
    "pitch_rate_abs_mean",
    "vz_down_mean",
    "front_pitch_ref",
    "front_pitch_actual",
    "rear_pitch_actual",
    "wheel_spin_airborne_mean",
    "quality_row_advance_rate",
    "hard_quality_advance_rate",
    "low_quality_hit_rate",
    "raw_hard_hit_rate",
    "row_advance_without_quality_rate",
    "quality_advance_score",
    "phase_module_progress_score",
    "front_climb_success_rate",
    "middle_climb_success_rate",
    "rear_follow_success_rate",
    "actual_overspeed_near_edge_rate",
    "row_contact_support_min",
    "row_stuck_time_max",
    "recovery_active_rate",
    "recovery_reverse_rate",
    "recovery_success_rate",
    "ball_joint_limit_usage_max",
    "action_abs_mean",
    "action_rate_abs_mean",
    "action_saturation_rate",
    "difficulty_score",
)

STAGE1_COMPLETION_COLUMNS = tuple(f"col{idx:02d}" for idx in range(len(STAGE1_TERRAIN_COLUMNS)))
STAGE1_COLUMN_COMPLETION_FIELDS = (
    "max_row_success_count",
    "max_row_attempt_count",
    "recent_max_row_attempt_count",
    "recent_max_row_success_rate",
    "success_per_attempt",
    "recent_success_per_attempt",
    "consecutive_max_row_success",
    "max_row_success_with_quality_count",
    "completion_target",
    "completion_fraction",
    "completed",
)
STAGE1_HARD_CONSOLE_COLUMNS = (
    "col05_stairs_down",
    "col06_stairs_down",
    "col07_stairs_down",
    "col08_obstacles",
    "col09_obstacles",
)
STAGE1_HARD_CONSOLE_COLUMN_FIELDS = (
    "current_level_mean",
    "row_advance_rate",
    "max_row_reached_rate",
    "valid_target_masked",
    "rear_follow_success_rate",
    "row_contact_support_min",
    "actual_overspeed_near_edge_rate",
    "stagnation_rate",
    "stuck_timeout_rate",
    "difficulty_score",
)
STAGE1_HARD_CONSOLE_COMPLETION_COLUMNS = (
    "col05",
    "col06",
    "col07",
    "col08",
    "col09",
)

STAGE1_TENSORBOARD_EXTRA_TAGS = (
    {f"Stage1Eval/global/{field}" for field in STAGE1_GLOBAL_EVAL_FIELDS}
    | {f"Stage1Eval/flat/{field}" for field in STAGE1_FLAT_EVAL_FIELDS}
    | {
        f"Stage1Eval/{column}/{field}"
        for column in STAGE1_TERRAIN_COLUMNS
        for field in STAGE1_PER_COLUMN_EVAL_FIELDS
    }
    | {
        f"Stage1Eval/{column}/{field}"
        for column in STAGE1_COMPLETION_COLUMNS
        for field in STAGE1_COLUMN_COMPLETION_FIELDS
    }
)
STAGE1_DENSE_ZERO_TAGS = {
    f"Stage1Eval/{column}/{field}"
    for column in STAGE1_COMPLETION_COLUMNS
    for field in STAGE1_COLUMN_COMPLETION_FIELDS
}
STAGE1_DENSE_ZERO_TAGS.update(
    {
        "Stage1Eval/global/max_row_reached_rate",
        "Stage1Eval/global/raw_hard_hit_rate",
        "Stage1Eval/global/hard_quality_advance_rate",
        "Stage1Eval/global/low_quality_hit_rate",
        "Stage1Eval/global/row_advance_without_quality_rate",
    }
)

STAGE1_CONSOLE_PRIORITY_TAGS = (
    "Stage1Eval/flat/retention_score",
    "Stage1Eval/flat/row_advance_rate",
    "Stage1Eval/flat/v_forward_mean",
    "Stage1Eval/flat/effective_failure_rate",
    "Stage1Eval/global/train_active_rate",
    "Stage1Eval/global/train_retired_rate",
    "Stage1Eval/global/train_sample_rate",
    "Stage1Eval/global/completed_column_rate",
    "Stage1Eval/global/unfinished_column_count",
    "Stage1Eval/global/recycled_env_ever_rate",
    "Stage1Eval/global/completed_column_retention_target_rate",
    "Stage1Eval/global/completed_column_active_rate",
    "Stage1Eval/global/completed_column_active_ratio_of_active",
    "Stage1Eval/global/active_envs_per_completed_column_mean",
    "Stage1Eval/global/active_envs_per_unfinished_column_mean",
    "Stage1Eval/global/rows_advanced_mean",
    "Stage1Eval/global/max_row_reached_rate",
    "Stage1Eval/global/valid_target_masked",
    "Stage1Eval/global/current_level_mean",
    "Stage1Eval/global/forward_x_mean",
    "Stage1Eval/global/tile_start_x_mean",
    "Stage1Eval/global/tile_origin_x_mean",
    "Stage1Eval/global/tile_end_x_mean",
    "Stage1Eval/global/root_x_mean",
    "Stage1Eval/global/target_x_mean",
    "Stage1Eval/global/effective_failure_rate",
    "Stage1Eval/global/stagnation_rate",
    "Stage1Eval/global/stuck_timeout_rate",
    "Stage1Eval/global/speed_limit_active_rate",
    "Stage1Eval/global/longitudinal_slip_abs_mean",
    "Stage1Eval/global/slip_angle_abs_mean",
    "Stage1Eval/global/combined_low_slip_pass_rate",
    "Stage1Eval/global/contact_loss_rate",
    "Stage1Eval/global/pitch_abs_mean",
    "Stage1Eval/global/pitch_rate_abs_mean",
    "Stage1Eval/global/vz_down_mean",
    "Stage1Eval/global/roll_abs_mean",
    "Stage1Eval/global/action_saturation_rate",
    "Stage1Eval/global/hard_quality_advance_rate",
    "Stage1Eval/global/low_quality_hit_rate",
    "Stage1Eval/global/raw_hard_hit_rate",
    "Stage1Eval/global/row_advance_without_quality_rate",
    "Stage1Eval/global/quality_advance_score",
    "Stage1Eval/global/phase_module_progress_score",
    "Stage1Eval/global/front_climb_success_rate",
    "Stage1Eval/global/middle_climb_success_rate",
    "Stage1Eval/global/rear_follow_success_rate",
    "Stage1Eval/global/actual_overspeed_near_edge_rate",
    "Stage1Eval/global/row_contact_support_min",
    "Stage1Eval/global/row_stuck_time_max",
    "Stage1Eval/global/hardest_col_index",
    "Stage1Eval/global/hardest_col_difficulty_score",
    "Stage1Eval/col01_slope_down/difficulty_score",
    "Stage1Eval/col02_slope_up/difficulty_score",
    "Stage1Eval/col03_rough/difficulty_score",
    "Stage1Eval/col04_rough/difficulty_score",
    "Stage1Eval/col05_stairs_down/difficulty_score",
    "Stage1Eval/col06_stairs_down/difficulty_score",
    "Stage1Eval/col07_stairs_down/difficulty_score",
    "Stage1Eval/col08_obstacles/difficulty_score",
    "Stage1Eval/col09_obstacles/difficulty_score",
) + tuple(
    f"Stage1Eval/{column}/{field}"
    for column in STAGE1_HARD_CONSOLE_COLUMNS
    for field in STAGE1_HARD_CONSOLE_COLUMN_FIELDS
) + tuple(
    f"Stage1Eval/{column}/{field}"
    for column in STAGE1_HARD_CONSOLE_COMPLETION_COLUMNS
    for field in STAGE1_COLUMN_COMPLETION_FIELDS
)

STAGE1_CONSOLE_VISIBLE_TAGS = set(STAGE1_CONSOLE_PRIORITY_TAGS)
STAGE1_CONSOLE_TAG_ORDER = {tag: idx for idx, tag in enumerate(STAGE1_CONSOLE_PRIORITY_TAGS)}
STAGE1_PER_WHEEL_DEBUG_FIELDS = {
    "normal_force",
    "longitudinal_slip",
    "slip_angle",
    "v_parallel",
    "v_perp",
    "wheel_torque_target",
    "wheel_speed_reference",
}

CONSOLE_VISIBLE_TAGS = set(CONSOLE_PRIORITY_TAGS)
CONSOLE_TAG_ORDER = {tag: idx for idx, tag in enumerate(CONSOLE_PRIORITY_TAGS)}

class Logger:
    """Logger to save the learning metrics to different logging services."""

    @staticmethod
    def _format_duration(seconds: float) -> str:
        seconds = max(0, int(round(seconds)))
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    @staticmethod
    def _build_time_progress_bar(elapsed_seconds: float, eta_seconds: float, width: int = 28) -> tuple[str, float]:
        total_estimated = max(elapsed_seconds + max(eta_seconds, 0.0), 1e-9)
        progress = min(max(elapsed_seconds / total_estimated, 0.0), 1.0)
        filled = int(round(progress * width))
        bar = "#" * filled + "-" * max(width - filled, 0)
        return bar, progress

    @staticmethod
    def _get_cfg_value(cfg: dict | object | None, key: str, default=None):
        if cfg is None:
            return default
        if isinstance(cfg, dict):
            return cfg.get(key, default)
        return getattr(cfg, key, default)

    @classmethod
    def _get_nested_cfg_value(cls, cfg: dict | object | None, keys: tuple[str, ...], default=None):
        value = cfg
        for key in keys:
            value = cls._get_cfg_value(value, key, default)
            if value is default:
                return default
        return value

    def _infer_stage_name(self) -> str:
        stage_name = self._get_cfg_value(self.env_cfg, "stage_name", None)
        if isinstance(stage_name, str) and stage_name.lower() in {"stage0", "stage1"}:
            return stage_name.lower()

        candidates = (
            self.cfg.get("task"),
            self.cfg.get("experiment_name"),
            self.cfg.get("run_name"),
        )
        for candidate in candidates:
            candidate_lower = str(candidate or "").lower()
            if candidate_lower in {"completecar-stage0", "complete_car_stage0"} or "stage0" in candidate_lower:
                return "stage0"
            if candidate_lower in {"completecar-stage1", "complete_car_stage1"} or "stage1" in candidate_lower:
                return "stage1"
        return "unknown"

    def _update_stage_name_from_metrics(self, metrics: dict) -> None:
        if self.stage_name in {"stage0", "stage1"}:
            return
        stage_id = metrics.get("Meta/stage_id")
        if stage_id is None:
            return
        try:
            stage_id_float = float(stage_id)
        except (TypeError, ValueError):
            return
        if abs(stage_id_float - 1.0) < 0.5:
            self.stage_name = "stage1"
        elif abs(stage_id_float) < 0.5:
            self.stage_name = "stage0"

    def __init__(
        self,
        log_dir: str | None,
        cfg: dict,
        env_cfg: dict | object,
        num_envs: int,
        is_distributed: bool,
        gpu_world_size: int,
        gpu_global_rank: int,
        device: str,
    ) -> None:
        """Initialize buffers and logging state for a training run."""
        self.log_dir = log_dir
        self.cfg = cfg
        self.env_cfg = env_cfg
        self.num_envs = num_envs
        self.gpu_world_size = gpu_world_size
        self.device = device
        self.git_status_repos = [rsl_rl.__file__]
        self.tot_timesteps = 0
        self.tot_time = 0
        self.stage_name = self._infer_stage_name()
        self.enable_stage1_per_wheel_debug = bool(
            self._get_nested_cfg_value(self.env_cfg, ("logging", "enable_stage1_per_wheel_debug"), False)
        )

        # Create buffers
        self.ep_extras = []
        self.step_extras = []
        self.rewbuffer = deque(maxlen=100)
        self.lenbuffer = deque(maxlen=100)
        self.cur_reward_sum = torch.zeros(self.num_envs, dtype=torch.float, device=self.device)
        self.cur_episode_length = torch.zeros(self.num_envs, dtype=torch.float, device=self.device)
        self._activated_sparse_zero_scalars: set[str] = set()
        self._pending_sparse_zero_scalars: dict[str, list[tuple[int, float]]] = {}

        # Create RND buffers
        if self.cfg["algorithm"]["rnd_cfg"]:
            self.erewbuffer = deque(maxlen=100)
            self.irewbuffer = deque(maxlen=100)
            self.cur_ereward_sum = torch.zeros(self.num_envs, dtype=torch.float, device=self.device)
            self.cur_ireward_sum = torch.zeros(self.num_envs, dtype=torch.float, device=self.device)

        # Decide whether to disable logging
        # Note: We only log from the process with rank 0 (main process)
        self.disable_logs = is_distributed and gpu_global_rank != 0

    def init_logging_writer(self) -> None:
        """Initialize the logging writer, which can be either Tensorboard, W&B or Neptune and save the code state.

        If the writer is either W&B or Neptune, the configuration and code state are uploaded as well.
        """
        if self.log_dir is not None and not self.disable_logs:
            self.logger_type = self.cfg.get("logger", "tensorboard")
            self.logger_type = self.logger_type.lower()
            if self.logger_type == "neptune":
                from rsl_rl.utils.neptune_utils import NeptuneSummaryWriter

                self.writer = NeptuneSummaryWriter(log_dir=self.log_dir, flush_secs=10, cfg=self.cfg)
            elif self.logger_type == "wandb":
                from rsl_rl.utils.wandb_utils import WandbSummaryWriter

                self.writer = WandbSummaryWriter(log_dir=self.log_dir, flush_secs=10, cfg=self.cfg)
            elif self.logger_type == "tensorboard":
                from torch.utils.tensorboard import SummaryWriter

                self.writer = SummaryWriter(log_dir=self.log_dir, flush_secs=10)
            else:
                raise ValueError("Logger type not found. Please choose 'wandb', 'neptune', or 'tensorboard'.")
        else:
            self.writer = None

        # Save code state
        files_to_upload = self._store_code_state()

        # Upload configuration and code state to external logging service if applicable
        if self.writer is not None and self.logger_type in ["wandb", "neptune"]:
            self.writer.store_config(self.env_cfg, self.cfg)  # type: ignore
            for path in files_to_upload:
                self.writer.save_file(path)  # type: ignore

    def process_env_step(
        self,
        rewards: torch.Tensor,
        dones: torch.Tensor,
        extras: dict,
        intrinsic_rewards: torch.Tensor | None = None,
    ) -> None:
        """Add metrics from the environment step to the buffers."""
        if self.writer is not None:
            rewards = torch.nan_to_num(rewards, nan=0.0, posinf=0.0, neginf=0.0)
            if intrinsic_rewards is not None:
                intrinsic_rewards = torch.nan_to_num(intrinsic_rewards, nan=0.0, posinf=0.0, neginf=0.0)
            if "episode" in extras:
                self.ep_extras.append(extras["episode"])
            elif "log" in extras:
                self.ep_extras.append(extras["log"])
            if "metrics" in extras:
                self._update_stage_name_from_metrics(extras["metrics"])
                self.step_extras.append(extras["metrics"])

            # Update rewards and episode length
            if intrinsic_rewards is not None:
                self.cur_ereward_sum += rewards
                self.cur_ireward_sum += intrinsic_rewards
                self.cur_reward_sum += rewards + intrinsic_rewards
            else:
                self.cur_reward_sum += rewards
            self.cur_episode_length += 1

            # Clear data for completed episodes
            new_ids = (dones > 0).nonzero(as_tuple=False)
            self.rewbuffer.extend(self.cur_reward_sum[new_ids][:, 0].cpu().numpy().tolist())
            self.lenbuffer.extend(self.cur_episode_length[new_ids][:, 0].cpu().numpy().tolist())
            self.cur_reward_sum[new_ids] = 0
            self.cur_episode_length[new_ids] = 0
            if intrinsic_rewards is not None:
                self.erewbuffer.extend(self.cur_ereward_sum[new_ids][:, 0].cpu().numpy().tolist())
                self.irewbuffer.extend(self.cur_ireward_sum[new_ids][:, 0].cpu().numpy().tolist())
                self.cur_ereward_sum[new_ids] = 0
                self.cur_ireward_sum[new_ids] = 0

    def log(
        self,
        it: int,
        start_it: int,
        total_it: int,
        collect_time: float,
        learn_time: float,
        loss_dict: dict,
        learning_rate: float,
        action_std: torch.Tensor,
        rnd_weight: float | None,
        print_minimal: bool = False,
        width: int = 80,
        pad: int = 40,
    ) -> None:
        """Log the training metrics to the logging service and print them to the console.

        If videos are available, they are uploaded to the logging service (W&B) as well.
        """
        if self.writer is not None:
            collection_size = self.cfg["num_steps_per_env"] * self.num_envs * self.gpu_world_size
            iteration_time = collect_time + learn_time
            self.tot_timesteps += collection_size
            self.tot_time += iteration_time

            extras_string = ""
            episode_scalars: dict[str, float] = {}
            step_scalars: dict[str, float] = {}
            if self.ep_extras:
                episode_scalars = self._aggregate_scalar_dicts(self.ep_extras)
                for key, value in episode_scalars.items():
                    if self._should_write_tensorboard_extra(key):
                        self._write_tensorboard_scalar(key, value, it)

            if self.step_extras:
                step_scalars = self._aggregate_scalar_dicts(self.step_extras)
                for key, value in step_scalars.items():
                    if self._should_write_tensorboard_extra(key):
                        self._write_tensorboard_scalar(key, value, it)

            console_scalars = dict(episode_scalars)
            console_scalars.update(step_scalars)
            for key, value in self._ordered_scalar_items(console_scalars):
                if not print_minimal and self._should_print_scalar(key):
                    extras_string += f"""{f"{key}:":>{pad}} {value:.4f}\n"""
            action_std_mean = float(
                torch.nan_to_num(action_std.mean(), nan=0.0, posinf=0.0, neginf=0.0).item()
            )

            # Log losses
            for key, value in loss_dict.items():
                self._write_tensorboard_scalar(f"Loss/{key}", value, it)
            self._write_tensorboard_scalar("Loss/learning_rate", learning_rate, it)

            # Log std
            self._write_tensorboard_scalar("Policy/mean_std", action_std_mean, it)

            # Log performance
            fps = int(collection_size / (collect_time + learn_time))
            self._write_tensorboard_scalar("Perf/total_fps", fps, it)
            self._write_tensorboard_scalar("Perf/collection_time", collect_time, it)
            self._write_tensorboard_scalar("Perf/learning_time", learn_time, it)

            # Log rewards and episode length
            if len(self.rewbuffer) > 0:
                if self.cfg["algorithm"]["rnd_cfg"]:
                    self._write_tensorboard_scalar("Rnd/mean_extrinsic_reward", statistics.mean(self.erewbuffer), it)
                    self._write_tensorboard_scalar("Rnd/mean_intrinsic_reward", statistics.mean(self.irewbuffer), it)
                    self._write_tensorboard_scalar("Rnd/weight", rnd_weight, it)  # type: ignore[arg-type]
                self._write_tensorboard_scalar("Train/mean_reward", statistics.mean(self.rewbuffer), it)
                self._write_tensorboard_scalar("Train/mean_episode_length", statistics.mean(self.lenbuffer), it)
                if self.logger_type != "wandb":
                    self._write_tensorboard_scalar(
                        "Train/mean_reward/time", statistics.mean(self.rewbuffer), int(self.tot_time)
                    )
                    self._write_tensorboard_scalar(
                        "Train/mean_episode_length/time", statistics.mean(self.lenbuffer), int(self.tot_time)
                    )

            # Print to console
            log_string = f"""{"#" * width}\n"""
            log_string += f"""\033[1m{f" Learning iteration {it}/{total_it} ".center(width)}\033[0m \n\n"""

            # Print run name if provided
            run_name = self.cfg.get("run_name")
            log_string += f"""{"Run name:":>{pad}} {run_name}\n""" if run_name else ""

            # Print performance
            log_string += (
                f"""{"Total steps:":>{pad}} {self.tot_timesteps} \n"""
                f"""{"Steps per second:":>{pad}} {fps:.0f} \n"""
                f"""{"Collection time:":>{pad}} {collect_time:.3f}s \n"""
                f"""{"Learning time:":>{pad}} {learn_time:.3f}s \n"""
            )

            # Print losses
            for key, value in loss_dict.items():
                log_string += f"""{f"Mean {key} loss:":>{pad}} {value:.4f}\n"""

            # Print rewards and episode length
            if len(self.rewbuffer) > 0:
                if self.cfg["algorithm"]["rnd_cfg"]:
                    log_string += f"""{"Mean extrinsic reward:":>{pad}} {statistics.mean(self.erewbuffer):.2f}\n"""
                    log_string += f"""{"Mean intrinsic reward:":>{pad}} {statistics.mean(self.irewbuffer):.2f}\n"""
                log_string += f"""{"Mean reward:":>{pad}} {statistics.mean(self.rewbuffer):.2f}\n"""
                log_string += f"""{"Mean episode length:":>{pad}} {statistics.mean(self.lenbuffer):.2f}\n"""

            # Print std
            log_string += f"""{"Mean action std:":>{pad}} {action_std_mean:.2f}\n"""

            # Print episode extras
            if not print_minimal:
                log_string += extras_string

            # Print footer
            done_it = it + 1 - start_it
            remaining_it = total_it - start_it - done_it
            eta = self.tot_time / done_it * remaining_it
            progress_bar, progress_ratio = self._build_time_progress_bar(self.tot_time, eta)
            total_estimated_time = self.tot_time + eta
            log_string += (
                f"""{"-" * width}\n"""
                f"""{"Iteration time:":>{pad}} {iteration_time:.2f}s\n"""
                f"""{"Time progress:":>{pad}} [{progress_bar}] {progress_ratio * 100:5.1f}%\n"""
                f"""{"Time elapsed:":>{pad}} {self._format_duration(self.tot_time)}\n"""
                f"""{"ETA:":>{pad}} {self._format_duration(eta)}\n"""
                f"""{"Est. total time:":>{pad}} {self._format_duration(total_estimated_time)}\n"""
            )
            print(log_string)

            # Upload available videos
            if self.logger_type == "wandb":
                for video in pathlib.Path(self.log_dir).rglob("*.mp4"):  # type: ignore
                    self.writer.save_video(video, it)  # type: ignore

            # Clear extras buffer
            self.ep_extras.clear()
            self.step_extras.clear()

    def save_model(self, path: str, it: int) -> None:
        """Save the model to external logging services if specified."""
        if self.writer is not None and self.logger_type in ["neptune", "wandb"]:
            self.writer.save_model(path, it)  # type: ignore

    def stop_logging_writer(self) -> None:
        """Stop the logging writer."""
        if self.writer is not None and self.logger_type in ["neptune", "wandb"]:
            self.writer.stop()  # type: ignore

    def _store_code_state(self) -> list[str]:
        """Store the current git diff of the code repositories involved in the experiment."""
        files_to_upload = []
        if self.log_dir is not None and not self.disable_logs:
            git_log_dir = os.path.join(self.log_dir, "git")
            os.makedirs(git_log_dir, exist_ok=True)
            # Iterate over all repositories to log
            for repository_file_path in self.git_status_repos:
                try:
                    repo = git.Repo(repository_file_path, search_parent_directories=True)
                    t = repo.head.commit.tree
                    commit_hash = repo.head.commit.hexsha
                except Exception:
                    print(f"Could not find git repository in {repository_file_path}. Skipping.")
                    continue
                # Get the name of the repository
                repo_name = pathlib.Path(repo.working_dir).name
                diff_file_name = os.path.join(git_log_dir, f"{repo_name}.diff")
                # Check if the diff file already exists
                if os.path.isfile(diff_file_name):
                    continue
                # Write the diff file
                print(f"Storing git diff for '{repo_name}' in: {diff_file_name}")
                with open(diff_file_name, "x", encoding="utf-8") as f:
                    content = (
                        f"--- git commit ---\n{commit_hash}\n\n\n"
                        f"--- git status ---\n{repo.git.status()} \n\n\n"
                        f"--- git diff ---\n{repo.git.diff(t)}"
                    )
                    f.write(content)
                # Add the file path to the list of files to be uploaded
                files_to_upload.append(diff_file_name)
        return files_to_upload

    def _aggregate_scalar_dicts(self, info_dicts: list[dict]) -> dict[str, float]:
        """Aggregate a list of scalar dictionaries into per-key means."""
        aggregated: dict[str, float] = {}
        all_keys = sorted({key for info in info_dicts for key in info})
        for key in all_keys:
            values = []
            for info in info_dicts:
                if key not in info:
                    continue
                value = info[key]
                if not isinstance(value, torch.Tensor):
                    value = torch.tensor([value], device=self.device, dtype=torch.float32)
                else:
                    value = value.to(self.device, dtype=torch.float32)
                if value.ndim == 0:
                    value = value.unsqueeze(0)
                values.append(torch.nan_to_num(value.reshape(-1), nan=0.0, posinf=0.0, neginf=0.0))
            if values:
                aggregated[key] = float(torch.mean(torch.cat(values)).item())
        return aggregated

    def _tensorboard_tag(self, tag: str) -> str:
        """Map selected tags to prefixed aliases so important charts appear first in TensorBoard."""
        return TENSORBOARD_TAG_ALIASES.get(tag, tag)

    def _write_tensorboard_scalar(self, tag: str, value: float, step: int) -> None:
        """Write scalars to TensorBoard while suppressing blank series until they activate."""
        if self.writer is None:
            return
        if isinstance(value, torch.Tensor):
            tensor_value = value.detach().float().reshape(-1)
        else:
            tensor_value = torch.as_tensor(value, dtype=torch.float32).reshape(-1)
        if tensor_value.numel() == 0:
            value = 0.0
        else:
            value = float(torch.nan_to_num(torch.mean(tensor_value), nan=0.0, posinf=0.0, neginf=0.0).item())

        tensorboard_tag = self._tensorboard_tag(tag)
        if self.stage_name == "stage1" and tag in STAGE1_DENSE_ZERO_TAGS:
            self.writer.add_scalar(tensorboard_tag, value, step)  # type: ignore
            return
        if tag not in self._activated_sparse_zero_scalars:
            if abs(float(value)) <= 1.0e-12:
                self._pending_sparse_zero_scalars.setdefault(tag, []).append((step, float(value)))
                return
            self._activated_sparse_zero_scalars.add(tag)
            for pending_step, pending_value in self._pending_sparse_zero_scalars.pop(tag, []):
                self.writer.add_scalar(tensorboard_tag, pending_value, pending_step)  # type: ignore

        self.writer.add_scalar(tensorboard_tag, value, step)  # type: ignore

    def _should_print_scalar(self, tag: str) -> bool:
        """Only print the highest-signal scalar subset to the training console."""
        if self.stage_name == "stage1":
            return tag in STAGE1_CONSOLE_VISIBLE_TAGS
        return tag in CONSOLE_VISIBLE_TAGS

    def _should_write_tensorboard_extra(self, tag: str) -> bool:
        """Only keep the curated extra-scalar subset in TensorBoard."""
        if self.stage_name == "stage1":
            return (
                tag in STAGE1_TENSORBOARD_EXTRA_TAGS
                or tag.startswith("TerrainFeature/")
                or tag.startswith("TerrainGate/")
                or tag.startswith("Debug/Stage1/")
                or self._should_write_stage1_per_wheel_debug(tag)
            )
        return tag in TENSORBOARD_EXTRA_TAGS or tag.startswith("PerWheel/")

    def _should_write_stage1_per_wheel_debug(self, tag: str) -> bool:
        if not self.enable_stage1_per_wheel_debug or not tag.startswith("PerWheel/"):
            return False
        parts = tag.split("/")
        return len(parts) == 3 and parts[2] in STAGE1_PER_WHEEL_DEBUG_FIELDS

    def _ordered_scalar_items(self, scalar_dict: dict[str, float]) -> list[tuple[str, float]]:
        """Sort scalar tags so the same high-signal subset stays near the top in console output."""
        tag_order = STAGE1_CONSOLE_TAG_ORDER if self.stage_name == "stage1" else CONSOLE_TAG_ORDER
        return sorted(
            scalar_dict.items(),
            key=lambda item: (tag_order.get(item[0], len(tag_order)), item[0]),
        )
