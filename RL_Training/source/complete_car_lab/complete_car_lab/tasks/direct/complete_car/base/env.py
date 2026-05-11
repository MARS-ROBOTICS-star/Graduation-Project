"""Complete-car direct workflow 环境主类。"""

from __future__ import annotations

import math
from collections.abc import Sequence

import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation
from isaaclab.envs import DirectRLEnv
from isaaclab.sim.spawners.from_files import GroundPlaneCfg, spawn_ground_plane

from ..assets.robot_cfg import BALL_JOINT_NAMES, WHEEL_BODY_NAMES, WHEEL_JOINT_NAMES
from ..kinematics.wheel_speed_allocator import TorchWheelSpeedAllocator
from ..mdp import actions as mdp_actions
from ..mdp import commands as mdp_commands
from ..mdp import curriculum as mdp_curriculum
from ..mdp import resets as mdp_resets
from ..mdp.observations import (
    collect_raw_observation_terms,
    compute_actor_observation_from_raw_terms,
    compute_critic_observation,
    compute_wheel_motion_observations,
)
from ..mdp.rewards import REWARD_TERM_NAMES, compute_reward_terms, compute_stage1_phase_speed_safe
from ..mdp.stage1_eval import compute_stage1_eval_metrics
from ..mdp.terrain_features import compute_terrain_features
from ..mdp.terminations import compute_done_terms
from ..sensors.sensor_cfg import CompleteCarSensorSuiteRuntime
from ..terrain.terrain_cfg import STAGE1_TERRAIN_CLASS_STEP
from ..terrain.terrain_runtime import CompleteCarTerrainRuntime
from ..utils.debug_draw import CompleteCarDebugDraw
from ..utils.math_utils import quat_rotate, quaternion_to_rpy, update_history, wrap_to_pi_tensor
from .complete_car_cfg import CompleteCarEnvCfg


class CompleteCarDirectEnv(DirectRLEnv):
    """三个 Stage 共享的 direct 环境主类。"""

    cfg: CompleteCarEnvCfg
    # 内存预分配
    def __init__(self, cfg: CompleteCarEnvCfg, render_mode: str | None = None, **kwargs):
        self._terrain_runtime: CompleteCarTerrainRuntime | None = None
        self._sensor_runtime: CompleteCarSensorSuiteRuntime | None = None
        self._debug_draw = CompleteCarDebugDraw(
            cfg.debug.enable_debug_draw,
            visualize_goal_position=cfg.debug.visualize_goal_position,
            visualize_goal_heading=cfg.debug.visualize_goal_heading,
            height_patch_marker_radius=cfg.debug.height_patch_marker_radius,
        )
        super().__init__(cfg, render_mode, **kwargs)

        self._ball_joint_ids, _ = self.robot.find_joints(BALL_JOINT_NAMES, preserve_order=True)
        self._wheel_joint_ids, _ = self.robot.find_joints(WHEEL_JOINT_NAMES, preserve_order=True)
        self._wheel_body_ids, _ = self.robot.find_bodies(WHEEL_BODY_NAMES, preserve_order=True)
        gravity_magnitude = abs(float(self.cfg.sim.gravity[2]))
        self._total_vehicle_weight = (
            self.robot.data.default_mass.sum(dim=1, keepdim=True).to(device=self.device) * gravity_magnitude
        )
        self._wheel_speed_allocator = TorchWheelSpeedAllocator(
            device=self.device,
            dtype=self.robot.data.joint_pos.dtype,
        )

        self.actions = torch.zeros((self.num_envs, self.cfg.action_space), device=self.device)
        self.last_actions = torch.zeros_like(self.actions)
        self._num_waypoints_per_episode = max(int(getattr(self.cfg.commands, "num_waypoints_per_episode", 1)), 1)
        self.commands = torch.zeros((self.num_envs, self.cfg.commands.num_commands), device=self.device)
        self.command_targets_w = torch.zeros_like(self.commands)
        self._waypoint_targets_w = torch.zeros(
            (self.num_envs, self._num_waypoints_per_episode, self.cfg.commands.num_commands),
            device=self.device,
        )
        self._command_time_left = torch.zeros(self.num_envs, device=self.device)
        self._goal_direction_offsets = torch.zeros(self.num_envs, device=self.device)
        self._goal_heading_offsets = torch.zeros(self.num_envs, device=self.device)
        self._waypoint_direction_offsets = torch.zeros(
            (self.num_envs, self._num_waypoints_per_episode),
            device=self.device,
        )
        self._waypoint_heading_offsets = torch.zeros_like(self._waypoint_direction_offsets)
        self._active_waypoint_index = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self._episode_waypoints_completed = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self._episode_terrain_target_advances = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self._last_stage1_max_row_reached = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._last_stage1_valid_target_masked = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._stage1_training_active = torch.ones(self.num_envs, dtype=torch.bool, device=self.device)
        self._stage1_transition_train_mask = torch.ones(self.num_envs, dtype=torch.bool, device=self.device)
        num_stage1_terrain_cols = max(int(getattr(self.cfg.terrain.generator, "num_cols", 1)), 1)
        self._stage1_column_completion_counts = torch.zeros(
            num_stage1_terrain_cols,
            dtype=torch.long,
            device=self.device,
        )
        self._stage1_column_completion_targets = torch.ones_like(self._stage1_column_completion_counts)
        self._stage1_completed_terrain_columns = torch.zeros(
            num_stage1_terrain_cols,
            dtype=torch.bool,
            device=self.device,
        )
        self._stage1_recycled_envs_ever = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._stage1_last_recycled_env_mask = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._stage1_recycle_cursor = 0
        self._initialize_stage1_column_completion_tracking()
        self._stage1_row_quality_baseline_ready = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._stage1_row_module_support_height_baseline = torch.zeros((self.num_envs, 3), device=self.device)
        self._stage1_row_module_progress_max = torch.zeros_like(self._stage1_row_module_support_height_baseline)
        self._stage1_row_contact_support_min = torch.ones(self.num_envs, device=self.device)
        self._stage1_row_stuck_time_max = torch.zeros(self.num_envs, device=self.device)
        self._stage1_row_actual_overspeed_near_edge_max = torch.zeros(self.num_envs, device=self.device)
        self._stage1_row_actual_overspeed_near_edge_ever = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._stage1_row_phase_module_progress_max = torch.zeros(self.num_envs, device=self.device)
        self._last_stage1_quality_advance_score = torch.zeros(self.num_envs, device=self.device)
        self._last_stage1_quality_advance_mask = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._last_stage1_low_quality_hit = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._last_stage1_raw_hard_hit = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._last_stage1_row_advance_without_quality = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._last_stage1_progress_hit_mask = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._last_stage1_advance_mask = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._last_stage1_max_row_reached_mask = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._previous_goal_distance = torch.zeros(self.num_envs, device=self.device)
        self._active_goal_start_distance = torch.ones(self.num_envs, device=self.device)

        self._joint_pos_targets = self.robot.data.default_joint_pos.clone()
        self._joint_effort_targets = torch.zeros_like(self.robot.data.default_joint_vel)
        self._last_ball_joint_desired_targets = torch.zeros((self.num_envs, len(BALL_JOINT_NAMES)), device=self.device)
        self._last_ball_joint_desired_delta_abs_mean = torch.zeros(self.num_envs, device=self.device)
        self._last_ball_joint_desired_delta_l2 = torch.zeros(self.num_envs, device=self.device)
        self._last_ball_joint_rate_targets = torch.zeros_like(self._last_ball_joint_desired_targets)
        self._ball_joint_qdot_alloc = torch.zeros_like(self._last_ball_joint_desired_targets)
        self._last_wheel_speed_reference = torch.zeros((self.num_envs, len(WHEEL_JOINT_NAMES)), device=self.device)
        self._last_wheel_torque_targets = torch.zeros_like(self._last_wheel_speed_reference)
        self._last_raw_planar_command = torch.zeros((self.num_envs, 2), device=self.device)
        self._last_limited_planar_command = torch.zeros_like(self._last_raw_planar_command)
        self._last_terrain_speed_safe = torch.full(
            (self.num_envs,),
            float(self.cfg.control.base_forward_velocity_max),
            device=self.device,
        )
        self._last_terrain_speed_limit_active = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._last_desired_planar_command = torch.zeros((self.num_envs, 2), device=self.device)
        self._last_shaped_planar_command = torch.zeros((self.num_envs, 2), device=self.device)
        self._last_contact_weights = torch.zeros_like(self._last_wheel_speed_reference)
        self._last_wheel_v_parallel = torch.zeros_like(self._last_wheel_speed_reference)
        self._last_wheel_v_perp = torch.zeros_like(self._last_wheel_speed_reference)
        self._last_wheel_delta_v = torch.zeros_like(self._last_wheel_speed_reference)
        self._last_wheel_tau0 = torch.zeros_like(self._last_wheel_speed_reference)
        self._last_wheel_tau1 = torch.zeros_like(self._last_wheel_speed_reference)
        self._episode_sums = {name: torch.zeros(self.num_envs, device=self.device) for name in REWARD_TERM_NAMES}
        self._last_reward_components = {name: torch.zeros(self.num_envs, device=self.device) for name in REWARD_TERM_NAMES}
        self._last_reward_diagnostics = {
            "progress_ungated": torch.zeros(self.num_envs, device=self.device),
            "progress_positive": torch.zeros(self.num_envs, device=self.device),
            "progress_negative": torch.zeros(self.num_envs, device=self.device),
            "progress_longitudinal_gate": torch.zeros(self.num_envs, device=self.device),
            "progress_slip_angle_gate": torch.zeros(self.num_envs, device=self.device),
            "progress_gate": torch.zeros(self.num_envs, device=self.device),
            "progress_multiplier": torch.zeros(self.num_envs, device=self.device),
            "slip_contact_weight_sum": torch.zeros(self.num_envs, device=self.device),
            "slip_masked_longitudinal": torch.zeros(self.num_envs, device=self.device),
            "slip_masked_angle": torch.zeros(self.num_envs, device=self.device),
            "contact_support_front": torch.zeros(self.num_envs, device=self.device),
            "contact_support_mid": torch.zeros(self.num_envs, device=self.device),
            "contact_support_rear": torch.zeros(self.num_envs, device=self.device),
            "contact_support_score": torch.zeros(self.num_envs, device=self.device),
            "contact_support_w_all": torch.zeros(self.num_envs, device=self.device),
            "contact_support_w_up": torch.zeros(self.num_envs, device=self.device),
            "contact_support_w_drop": torch.zeros(self.num_envs, device=self.device),
            "contact_support_lr_balance": torch.zeros(self.num_envs, device=self.device),
            "contact_support_all_module_penalty": torch.zeros(self.num_envs, device=self.device),
            "contact_support_step_up_penalty": torch.zeros(self.num_envs, device=self.device),
            "contact_support_drop_penalty": torch.zeros(self.num_envs, device=self.device),
            "edge_strength": torch.zeros(self.num_envs, device=self.device),
            "edge_height_jump": torch.zeros(self.num_envs, device=self.device),
            "edge_safe_speed": torch.zeros(self.num_envs, device=self.device),
            "edge_forward_speed": torch.zeros(self.num_envs, device=self.device),
            "edge_speed_excess": torch.zeros(self.num_envs, device=self.device),
            "terrain_gate_step_up": torch.zeros(self.num_envs, device=self.device),
            "terrain_gate_step_down": torch.zeros(self.num_envs, device=self.device),
            "terrain_gate_gap": torch.zeros(self.num_envs, device=self.device),
            "terrain_gate_rough": torch.zeros(self.num_envs, device=self.device),
            "terrain_gate_flat": torch.ones(self.num_envs, device=self.device),
            "terrain_gate_edge": torch.zeros(self.num_envs, device=self.device),
            "terrain_speed_safe": torch.zeros(self.num_envs, device=self.device),
            "terrain_speed_raw_vx": torch.zeros(self.num_envs, device=self.device),
            "terrain_speed_limited_vx": torch.zeros(self.num_envs, device=self.device),
            "terrain_speed_actual_vx": torch.zeros(self.num_envs, device=self.device),
            "terrain_speed_raw_excess": torch.zeros(self.num_envs, device=self.device),
            "terrain_speed_actual_excess": torch.zeros(self.num_envs, device=self.device),
            "terrain_speed_limit_active": torch.zeros(self.num_envs, device=self.device),
            "stuck_time_s": torch.zeros(self.num_envs, device=self.device),
            "stuck_penalty_active": torch.zeros(self.num_envs, device=self.device),
            "no_progress_active": torch.zeros(self.num_envs, device=self.device),
            "no_progress_deficit": torch.zeros(self.num_envs, device=self.device),
            "no_progress_penalty_raw": torch.zeros(self.num_envs, device=self.device),
            "airborne_spin_penalty_raw": torch.zeros(self.num_envs, device=self.device),
            "wheel_spin_airborne_mean": torch.zeros(self.num_envs, device=self.device),
            "hard_terrain_spin_gate": torch.zeros(self.num_envs, device=self.device),
            "hard_terrain_low_speed": torch.zeros(self.num_envs, device=self.device),
            "hard_terrain_slip_excess": torch.zeros(self.num_envs, device=self.device),
            "hard_terrain_spin_penalty_raw": torch.zeros(self.num_envs, device=self.device),
            "action_soft_limit_penalty_raw": torch.zeros(self.num_envs, device=self.device),
            "front_pitch_ref": torch.zeros(self.num_envs, device=self.device),
            "front_pitch_actual": torch.zeros(self.num_envs, device=self.device),
            "rear_pitch_actual": torch.zeros(self.num_envs, device=self.device),
            "front_pitch_error": torch.zeros(self.num_envs, device=self.device),
            "step_up_distance_m": torch.zeros(self.num_envs, device=self.device),
            "step_up_approach_mask": torch.zeros(self.num_envs, device=self.device),
            "step_up_posture_badness": torch.zeros(self.num_envs, device=self.device),
            "progress_quality_slip": torch.ones(self.num_envs, device=self.device),
            "progress_quality_overspeed": torch.ones(self.num_envs, device=self.device),
            "progress_quality_pitch": torch.ones(self.num_envs, device=self.device),
            "progress_quality_contact": torch.ones(self.num_envs, device=self.device),
            "progress_quality_not_stuck": torch.ones(self.num_envs, device=self.device),
            "progress_quality_score": torch.ones(self.num_envs, device=self.device),
            "step_up_progress_quality_multiplier": torch.ones(self.num_envs, device=self.device),
            "step_up_front_posture_penalty_raw": torch.zeros(self.num_envs, device=self.device),
            "front_module_height_progress": torch.zeros(self.num_envs, device=self.device),
            "middle_module_height_progress": torch.zeros(self.num_envs, device=self.device),
            "rear_module_height_progress": torch.zeros(self.num_envs, device=self.device),
            "front_module_step_height_progress": torch.zeros(self.num_envs, device=self.device),
            "middle_module_step_height_progress": torch.zeros(self.num_envs, device=self.device),
            "rear_module_step_height_progress": torch.zeros(self.num_envs, device=self.device),
            "front_module_new_height_progress": torch.zeros(self.num_envs, device=self.device),
            "middle_module_new_height_progress": torch.zeros(self.num_envs, device=self.device),
            "rear_module_new_height_progress": torch.zeros(self.num_envs, device=self.device),
            "module_support_phase_score": torch.zeros(self.num_envs, device=self.device),
            "step_up_climb_phase": torch.zeros(self.num_envs, device=self.device),
            "step_up_crest_phase": torch.zeros(self.num_envs, device=self.device),
            "step_up_module_progress_score": torch.zeros(self.num_envs, device=self.device),
            "step_up_module_progress_reward_raw": torch.zeros(self.num_envs, device=self.device),
            "quality_advance_score": torch.zeros(self.num_envs, device=self.device),
            "hard_quality_advance": torch.zeros(self.num_envs, device=self.device),
            "raw_hard_hit": torch.zeros(self.num_envs, device=self.device),
            "low_quality_hit": torch.zeros(self.num_envs, device=self.device),
            "row_advance_without_quality": torch.zeros(self.num_envs, device=self.device),
            "row_contact_support_min": torch.ones(self.num_envs, device=self.device),
            "row_stuck_time_max": torch.zeros(self.num_envs, device=self.device),
            "phase_module_progress_score": torch.zeros(self.num_envs, device=self.device),
            "actual_overspeed_near_edge": torch.zeros(self.num_envs, device=self.device),
            "actual_overspeed_near_edge_rate": torch.zeros(self.num_envs, device=self.device),
            "front_climb_success": torch.zeros(self.num_envs, device=self.device),
            "middle_climb_success": torch.zeros(self.num_envs, device=self.device),
            "rear_follow_success": torch.zeros(self.num_envs, device=self.device),
            "quality_row_advance_mask": torch.zeros(self.num_envs, device=self.device),
            "quality_row_advance_reward_raw": torch.zeros(self.num_envs, device=self.device),
            "recovery_active": torch.zeros(self.num_envs, device=self.device),
            "recovery_reverse_now": torch.zeros(self.num_envs, device=self.device),
            "recovery_success": torch.zeros(self.num_envs, device=self.device),
            "recovery_reward_raw": torch.zeros(self.num_envs, device=self.device),
            "drop_pitch_rate_abs": torch.zeros(self.num_envs, device=self.device),
            "drop_vz_down": torch.zeros(self.num_envs, device=self.device),
            "drop_anti_dive_penalty_raw": torch.zeros(self.num_envs, device=self.device),
        }
        self._last_total_reward = torch.zeros(self.num_envs, device=self.device)
        self._episode_total_reward_sum = torch.zeros(self.num_envs, device=self.device)
        self._last_active_waypoint_pos_error = torch.zeros(self.num_envs, device=self.device)
        self._last_active_waypoint_bearing_abs = torch.zeros(self.num_envs, device=self.device)
        self._last_done_terms = {
            "waypoint_hit": torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
            "is_success": torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
            "far_from_target": torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
            "ball_joint_out_of_bounds": torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
            "time_out": torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
            "stuck_timeout": torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
            "terrain_column_completed": torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
            "low_quality_terrain_hit": torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
        }
        self._stage1_stuck_time = torch.zeros(self.num_envs, device=self.device)
        self._last_stage1_stuck_now = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._prev_stage1_module_support_heights = torch.zeros((self.num_envs, 3), device=self.device)
        self._stage1_recovery_active = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._stage1_recovery_reverse_time_s = torch.zeros(self.num_envs, device=self.device)
        self._stage1_recovery_start_goal_distance = torch.zeros(self.num_envs, device=self.device)
        self._last_stage1_recovery_reverse_now = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._last_stage1_recovery_success = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._last_critic_height_patch: torch.Tensor | None = None
        self._last_terrain_features: torch.Tensor | None = None
        self._last_terrain_feature_diagnostics: dict[str, torch.Tensor] = {}
        self._cached_step_raw_obs_terms: dict[str, torch.Tensor] | None = None
        self._cached_step_relative_goal_commands: torch.Tensor | None = None
        self._pre_reset_relative_goal_commands: torch.Tensor | None = None
        self._pre_reset_critic_height_patch: torch.Tensor | None = None
        self._height_patch_cache_invalid_envs = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._cached_wheel_contact_forces_w: torch.Tensor | None = None
        self._cached_wheel_contact_forces_phase: str | None = None
        self._step_metrics_counter = 0

        self._obs_history = None
        if self.cfg.observations.use_history and self.cfg.observations.history_length > 1:
            history_dim = int(self.cfg.observation_space["actor"] / self.cfg.observations.history_length)
            self._obs_history = torch.zeros(
                (self.num_envs, self.cfg.observations.history_length, history_dim),
                device=self.device,
            )

        if not hasattr(self, "extras"):
            self.extras = {}
        self.extras.setdefault("log", {})

        self._critic_height_patch_local = self.cfg.terrain.build_patch_local_points(
            device= self.device,
            dtype = self.robot.data.root_link_pos_w.dtype,
        )
        self._height_patch_x_points = torch.unique(self._critic_height_patch_local[:, 0], sorted=True)
        self._height_patch_y_points = torch.unique(self._critic_height_patch_local[:, 1], sorted=True)
        edge_preview_x_min = float(self.cfg.terrain.patch_front_extent)
        edge_preview_x_max = edge_preview_x_min + float(self.cfg.terrain.patch_preview_length)
        edge_preview_y_limit = float(self.cfg.terrain.patch_half_width) + float(self.cfg.terrain.patch_side_margin)
        edge_eps = 1.0e-6
        self._edge_preview_x_indices = torch.nonzero(
            (self._height_patch_x_points >= edge_preview_x_min - edge_eps)
            & (self._height_patch_x_points <= edge_preview_x_max + edge_eps),
            as_tuple=False,
        ).flatten()
        self._edge_preview_y_indices = torch.nonzero(
            torch.abs(self._height_patch_y_points) <= edge_preview_y_limit + edge_eps,
            as_tuple=False,
        ).flatten()

    def step(self, action: torch.Tensor):
        self._clear_wheel_contact_force_cache()
        self._cached_step_raw_obs_terms = None
        self._cached_step_relative_goal_commands = None
        self._pre_reset_relative_goal_commands = None
        self._pre_reset_critic_height_patch = None
        self._height_patch_cache_invalid_envs.zero_()
        if self._uses_stage1_train_retirement():
            self._stage1_transition_train_mask.copy_(self._stage1_training_active)
        else:
            self._stage1_transition_train_mask.fill_(True)
        observations, rewards, terminated, time_outs, extras = super().step(action)
        for group_name in ("actor", "critic"):
            observations[group_name] = torch.nan_to_num(
                observations[group_name].clamp(
                    -self.cfg.observations.clip_observations,
                    self.cfg.observations.clip_observations,
                ),
                nan=0.0,
                posinf=self.cfg.observations.clip_observations,
                neginf=-self.cfg.observations.clip_observations,
            )
        rewards = torch.nan_to_num(rewards, nan=0.0, posinf=0.0, neginf=0.0)
        if self._debug_draw.enabled and (
            self.cfg.debug.visualize_goal_position or self.cfg.debug.visualize_goal_heading
        ):
            self._debug_draw.draw_goal_pose(
                goal_positions_w=self.command_targets_w[:, :3],
                goal_headings_w=self.command_targets_w[:, 3],
            )
        if self.cfg.debug.visualize_wheel_slip:
            wheel_body_quat_w = self.robot.data.body_quat_w[:, self._wheel_body_ids]
            wheel_forward_axis_local = torch.zeros_like(self.robot.data.body_lin_vel_w[:, self._wheel_body_ids])
            wheel_forward_axis_local[..., 0] = 1.0
            self._debug_draw.draw_wheel_motion(
                wheel_positions_w=self.robot.data.body_pos_w[:, self._wheel_body_ids],
                wheel_forward_axis_w=quat_rotate(wheel_body_quat_w, wheel_forward_axis_local),
                wheel_velocity_w=self.robot.data.body_lin_vel_w[:, self._wheel_body_ids],
            )
        if self.cfg.debug.visualize_height_patch:
            self._draw_height_patch()
        if self.cfg.debug.create_follow_views:
            self._update_follow_views()
        next_train_mask = (
            self._stage1_training_active.clone()
            if self._uses_stage1_train_retirement()
            else torch.ones_like(self._stage1_transition_train_mask)
        )
        extras["train_mask"] = self._stage1_transition_train_mask.clone()
        extras["next_train_mask"] = next_train_mask
        all_train_envs_retired = bool(
            (not torch.any(next_train_mask).item()) or self._all_stage1_terrain_columns_completed()
        )
        extras["all_train_envs_retired"] = all_train_envs_retired
        metrics_interval = max(int(getattr(self.cfg.logging, "step_metrics_interval", 1)), 1)
        if self._step_metrics_counter % metrics_interval == 0 or all_train_envs_retired:
            extras["metrics"] = self._collect_step_metrics()
        self._step_metrics_counter += 1
        self._last_stage1_max_row_reached.zero_()
        self._last_stage1_valid_target_masked.zero_()
        return observations, rewards, terminated, time_outs, extras

    # 场景构建 (初始化阶段)
    def _setup_scene(self) -> None:
        self.robot = Articulation(self.cfg.robot)
        self.scene.articulations["robot"] = self.robot

        self._terrain_runtime = CompleteCarTerrainRuntime(self.cfg.terrain, self.cfg.curriculum, self.device, self.cfg.scene.num_envs)
        ground_prim_path = self._terrain_runtime.setup_scene()
        if not self._terrain_runtime.generator_enabled:
            spawn_ground_plane(prim_path=ground_prim_path, cfg=GroundPlaneCfg())

        self._sensor_runtime = CompleteCarSensorSuiteRuntime(self.cfg.sensors, self.cfg.terrain, ground_prim_path)

        self.scene.clone_environments(copy_from_source=False)
        if str(self.device) == "cpu":
            self.scene.filter_collisions(global_prim_paths=[])

        self._sensor_runtime.build_scene_entities(self.scene)

        if self._terrain_runtime.generator_enabled:
            mdp_curriculum.initialize_terrain_curriculum(self.cfg.curriculum, self._terrain_runtime, self.scene)
        else:
            self._terrain_runtime.initialize_plane_after_scene_clone(self.scene)

        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)

    def _clear_wheel_contact_force_cache(self) -> None:
        self._cached_wheel_contact_forces_w = None
        self._cached_wheel_contact_forces_phase = None

    def _get_wheel_contact_forces_w_cached(self, phase: str) -> torch.Tensor:
        cached_forces = getattr(self, "_cached_wheel_contact_forces_w", None)
        cached_phase = getattr(self, "_cached_wheel_contact_forces_phase", None)
        if cached_forces is not None and cached_phase == phase:
            return cached_forces

        if self._sensor_runtime is not None:
            wheel_contact_forces_w = self._sensor_runtime.get_wheel_contact_forces_w(WHEEL_BODY_NAMES)
        else:
            wheel_contact_forces_w = torch.zeros(
                (self.num_envs, len(self._wheel_body_ids), 3),
                device=self.device,
                dtype=self.robot.data.root_link_pos_w.dtype,
            )
        self._cached_wheel_contact_forces_w = wheel_contact_forces_w
        self._cached_wheel_contact_forces_phase = phase
        return wheel_contact_forces_w

    # 执行动作预处理，刷新目标，运输动作输出到关节目标
    def _pre_physics_step(self, actions: torch.Tensor) -> None:
        self.last_actions.copy_(self.actions)
        self.actions.copy_(torch.nan_to_num(actions, nan=0.0, posinf=1.0, neginf=-1.0))
        if self._uses_stage1_train_retirement():
            self.actions[~self._stage1_training_active] = 0.0

        if (
            not self.cfg.commands.use_terrain_column_targets
            and self._num_waypoints_per_episode == 1
            and self.cfg.commands.resampling_time < self.cfg.episode_length_s
        ):
            resample_env_ids = mdp_commands.step_command_timer(self._command_time_left, self.step_dt)
            if resample_env_ids.numel() > 0:
                base_pos_xy_w = self.robot.data.root_link_pos_w[resample_env_ids, :2]
                base_yaw_w = quaternion_to_rpy(self.robot.data.root_link_quat_w[resample_env_ids])[:, 2]
                self._active_waypoint_index[resample_env_ids] = 0
                self._episode_waypoints_completed[resample_env_ids] = 0
                self._sample_waypoint_queue(
                    resample_env_ids,
                    base_pos_xy_w,
                    base_yaw_w,
                )
                self._previous_goal_distance[resample_env_ids] = torch.linalg.vector_norm(
                    self.command_targets_w[resample_env_ids, :2] - base_pos_xy_w,
                    dim=1,
                )

        planar_actions = self.actions[:, :2]
        ball_joint_actions = self.actions[:, 2:]
        ball_joint_lower_limits = self.cfg.terminations.ball_joint_pos_lower_limits
        ball_joint_upper_limits = self.cfg.terminations.ball_joint_pos_upper_limits

        wheel_contact_forces_w = self._get_wheel_contact_forces_w_cached("pre_physics")
        wheel_normal_contact_force = torch.linalg.vector_norm(wheel_contact_forces_w, dim=-1) / self._total_vehicle_weight
        wheel_body_lin_vel_w = self.robot.data.body_lin_vel_w[:, self._wheel_body_ids]
        wheel_body_quat_w = self.robot.data.body_quat_w[:, self._wheel_body_ids]
        x_axis_local = torch.zeros_like(wheel_body_lin_vel_w)
        x_axis_local[..., 0] = 1.0
        z_axis_local = torch.zeros_like(wheel_body_lin_vel_w)
        z_axis_local[..., 2] = 1.0
        wheel_forward_axis_w = quat_rotate(wheel_body_quat_w, x_axis_local)
        wheel_lateral_axis_w = quat_rotate(wheel_body_quat_w, z_axis_local)
        rolling_speed_actual = torch.sum(wheel_body_lin_vel_w * wheel_forward_axis_w, dim=-1)
        lateral_speed_actual = torch.sum(wheel_body_lin_vel_w * wheel_lateral_axis_w, dim=-1)

        desired_ball_joint_targets = mdp_actions.map_ball_joint_actions_to_desired_positions(
            self.robot.data.default_joint_pos[:, self._ball_joint_ids],
            ball_joint_actions,
            ball_joint_lower_limits,
            ball_joint_upper_limits,
        )
        desired_ball_joint_delta = wrap_to_pi_tensor(desired_ball_joint_targets - self._last_ball_joint_desired_targets)
        self._last_ball_joint_desired_delta_abs_mean.copy_(torch.mean(torch.abs(desired_ball_joint_delta), dim=1))
        self._last_ball_joint_desired_delta_l2.copy_(torch.linalg.vector_norm(desired_ball_joint_delta, dim=1))
        self._last_ball_joint_desired_targets.copy_(desired_ball_joint_targets)

        planar_command = mdp_actions.map_base_actions_to_planar_command(
            planar_actions,
            self.cfg.control.base_forward_velocity_max,
            self.cfg.control.base_yaw_rate_max,
            allow_reverse=self.cfg.control.base_allow_reverse,
        )
        planar_command = self._apply_stage1_terrain_speed_limit(planar_command)
        ball_joint_pos = self.robot.data.joint_pos[:, self._ball_joint_ids]
        ball_joint_vel = self.robot.data.joint_vel[:, self._ball_joint_ids]
        tau_v = float(self.cfg.control.ball_joint_qdot_alloc_filter_tau_s)
        alpha_v = 1.0 if tau_v <= 0.0 else 1.0 - math.exp(-float(self.cfg.control.control_dt) / tau_v)
        self._ball_joint_qdot_alloc.mul_(1.0 - alpha_v).add_(ball_joint_vel, alpha=alpha_v)
        qdot_limit = abs(float(self.cfg.control.ball_joint_velocity_limit_sim))
        self._ball_joint_qdot_alloc.clamp_(min=-qdot_limit, max=qdot_limit)
        wheel_joint_vel = self.robot.data.joint_vel[:, self._wheel_joint_ids]
        low_level_outputs = self._wheel_speed_allocator.compute_low_slip_control_targets(
            ball_joint_pos=ball_joint_pos,
            desired_ball_joint_pos=desired_ball_joint_targets,
            ball_joint_rate_targets=self._ball_joint_qdot_alloc,
            desired_planar_command=planar_command,
            wheel_normal_contact_force=wheel_normal_contact_force,
            wheel_joint_vel=wheel_joint_vel,
            rolling_speed_actual=rolling_speed_actual,
            lateral_speed_actual=lateral_speed_actual,
            q_lower_limits=ball_joint_lower_limits,
            q_upper_limits=ball_joint_upper_limits,
            lambda_tracking=self.cfg.control.low_slip_lambda_tracking,
            lambda_lateral=self.cfg.control.low_slip_lambda_lateral,
            planar_command_limits=(
                self.cfg.control.base_forward_velocity_max,
                self.cfg.control.base_yaw_rate_max,
            ),
            contact_force_off_threshold=self.cfg.control.contact_force_off_threshold,
            contact_force_on_threshold=self.cfg.control.contact_force_on_threshold,
            torque_tracking_gain=self.cfg.control.wheel_torque_tracking_gain,
            slip_feedback_gain=self.cfg.control.wheel_slip_feedback_gain,
            wheel_torque_limit=self.cfg.control.wheel_joint_effort_limit_sim,
            slip_velocity_epsilon=self.cfg.control.wheel_slip_velocity_epsilon,
        )
        self._last_desired_planar_command.copy_(planar_command)
        self._last_ball_joint_rate_targets.copy_(low_level_outputs.ball_joint_rate_targets)
        self._last_shaped_planar_command.copy_(low_level_outputs.shaped_planar_command)
        self._last_contact_weights.copy_(low_level_outputs.contact_weights)
        self._last_wheel_v_parallel.copy_(low_level_outputs.rolling_speed_actual)
        self._last_wheel_v_perp.copy_(low_level_outputs.lateral_speed_actual)
        self._last_wheel_delta_v.copy_(low_level_outputs.wheel_delta_speed)
        self._last_wheel_tau0.copy_(low_level_outputs.base_torque_targets)
        self._last_wheel_tau1.copy_(low_level_outputs.conditioned_torque_targets)
        self._joint_pos_targets = mdp_actions.apply_ball_joint_position_targets(
            self._joint_pos_targets,
            self._ball_joint_ids,
            low_level_outputs.ball_joint_position_targets,
        )
        self._last_wheel_speed_reference.copy_(low_level_outputs.wheel_speed_reference)
        self._last_wheel_torque_targets.copy_(low_level_outputs.wheel_torque_targets)
        self._joint_effort_targets.zero_()
        self._joint_effort_targets = mdp_actions.apply_wheel_effort_targets(
            self._joint_effort_targets,
            self._wheel_joint_ids,
            low_level_outputs.wheel_torque_targets,
            self.cfg.control.wheel_joint_effort_limit_sim,
        )

    # 球铰下发位置目标；车轮下发低层力矩目标。
    def _apply_action(self) -> None:
        self.robot.set_joint_position_target(self._joint_pos_targets[:, self._ball_joint_ids], joint_ids=self._ball_joint_ids)
        self.robot.set_joint_effort_target(self._joint_effort_targets[:, self._wheel_joint_ids], joint_ids=self._wheel_joint_ids)

    def _compute_relative_goal_commands(self, env_ids: torch.Tensor | None = None) -> torch.Tensor:
        if env_ids is None:
            base_pos_xy_w = self.robot.data.root_link_pos_w[:, :2]
            base_pos_z_w = self.robot.data.root_link_pos_w[:, 2]
            base_yaw_w = quaternion_to_rpy(self.robot.data.root_link_quat_w)[:, 2]
            return mdp_commands.compute_relative_goal_commands(self.command_targets_w, base_pos_xy_w, base_yaw_w, base_pos_z_w)

        base_pos_xy_w = self.robot.data.root_link_pos_w[env_ids, :2]
        base_pos_z_w = self.robot.data.root_link_pos_w[env_ids, 2]
        base_yaw_w = quaternion_to_rpy(self.robot.data.root_link_quat_w[env_ids])[:, 2]
        return mdp_commands.compute_relative_goal_commands(
            self.command_targets_w[env_ids], base_pos_xy_w, base_yaw_w, base_pos_z_w
        )

    def _sample_goal_target_heights(self, target_xy_w: torch.Tensor) -> torch.Tensor:
        if self._terrain_runtime is None:
            return torch.zeros(target_xy_w.shape[:-1], device=self.device, dtype=self.robot.data.root_link_pos_w.dtype)
        target_z_w = self._terrain_runtime.sample_heights_world_xy(target_xy_w)
        return torch.nan_to_num(target_z_w, nan=0.0, posinf=0.0, neginf=0.0)

    def _sync_active_waypoint_targets(self, env_ids: torch.Tensor) -> None:
        if env_ids.numel() == 0:
            return
        active_indices = self._active_waypoint_index[env_ids]
        self.command_targets_w[env_ids] = self._waypoint_targets_w[env_ids, active_indices]
        self._goal_direction_offsets[env_ids] = self._waypoint_direction_offsets[env_ids, active_indices]
        self._goal_heading_offsets[env_ids] = self._waypoint_heading_offsets[env_ids, active_indices]

    def _sample_waypoint_queue(
        self,
        env_ids: torch.Tensor,
        start_pos_xy_w: torch.Tensor,
        start_heading_w: torch.Tensor,
    ) -> None:
        if self.cfg.commands.use_terrain_column_targets:
            direction_offsets, heading_offsets = mdp_commands.sample_terrain_column_waypoint_command_sequences(
                self._waypoint_targets_w,
                env_ids,
                start_pos_xy_w,
                start_heading_w,
                self.cfg.commands,
                self._terrain_runtime,
                self._sample_goal_target_heights,
            )
        else:
            direction_offsets, heading_offsets = mdp_commands.sample_waypoint_command_sequences(
                self._waypoint_targets_w,
                env_ids,
                start_pos_xy_w,
                start_heading_w,
                self.cfg.commands,
                self._sample_goal_target_heights,
            )
        self._waypoint_direction_offsets[env_ids] = direction_offsets
        self._waypoint_heading_offsets[env_ids] = heading_offsets
        self._command_time_left[env_ids] = self.cfg.commands.resampling_time
        self._sync_active_waypoint_targets(env_ids)
        self._set_active_goal_start_distance(env_ids, start_pos_xy_w)

    def _set_active_goal_start_distance(self, env_ids: torch.Tensor, start_pos_xy_w: torch.Tensor) -> None:
        if env_ids.numel() == 0:
            return
        start_distance = torch.linalg.vector_norm(
            self.command_targets_w[env_ids, :2] - start_pos_xy_w,
            dim=1,
        )
        self._active_goal_start_distance[env_ids] = torch.nan_to_num(
            start_distance,
            nan=1.0,
            posinf=1.0,
            neginf=1.0,
        ).clamp(min=1.0e-6)

    def _compute_active_goal_progress(self, env_ids: torch.Tensor) -> torch.Tensor:
        if env_ids.numel() == 0:
            return torch.empty(0, device=self.device)
        current_distance = torch.linalg.vector_norm(
            self.command_targets_w[env_ids, :2] - self.robot.data.root_link_pos_w[env_ids, :2],
            dim=1,
        )
        start_distance = self._active_goal_start_distance[env_ids].clamp(min=1.0e-6)
        row_progress = (start_distance - current_distance) / start_distance
        return torch.nan_to_num(
            row_progress.clamp(min=0.0, max=1.0),
            nan=0.0,
            posinf=1.0,
            neginf=0.0,
        )

    def _get_terrain_column_tile_x_values(self) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        if (
            not self._uses_stage1_train_retirement()
            or self._terrain_runtime is None
            or not self._terrain_runtime.generator_enabled
            or self._terrain_runtime.terrain_levels is None
            or self._terrain_runtime.terrain_types is None
        ):
            zeros = torch.zeros(self.num_envs, device=self.device, dtype=self.robot.data.root_link_pos_w.dtype)
            return zeros, zeros, zeros, zeros, zeros, zeros

        tile_start_x, tile_origin_x, tile_end_x = self._terrain_runtime.get_tile_x_bounds(
            self._terrain_runtime.terrain_levels,
            self._terrain_runtime.terrain_types,
        )
        root_x = self.robot.data.root_link_pos_w[:, 0]
        target_x = self.command_targets_w[:, 0]
        forward_x = root_x - tile_start_x
        return tile_start_x, tile_origin_x, tile_end_x, root_x, target_x, forward_x

    def _compute_terrain_column_progress_masks(
        self,
        relative_goal_commands: torch.Tensor,
        done_terms: dict[str, torch.Tensor] | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        if (
            not self.cfg.commands.use_terrain_column_targets
            or self._terrain_runtime is None
            or not self._terrain_runtime.generator_enabled
            or self._terrain_runtime.terrain_levels is None
        ):
            empty_mask = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
            return empty_mask, empty_mask, empty_mask

        waypoint_hit = torch.linalg.vector_norm(relative_goal_commands[:, :2], dim=1) < self.cfg.rewards.params.target_position_tolerance
        min_row_offset = max(int(getattr(self.cfg.commands, "terrain_goal_min_row_offset", 1)), 1)
        max_target_level = max(int(self._terrain_runtime.max_terrain_level) - 1, 0)
        max_advance_source_level = max(max_target_level - min_row_offset, 0)
        can_advance = self._terrain_runtime.terrain_levels < max_advance_source_level
        reaches_max_row = self._terrain_runtime.terrain_levels >= max_advance_source_level
        if done_terms is None:
            done_terms = self._last_done_terms
        blocked = (
            done_terms["far_from_target"]
            | done_terms["ball_joint_out_of_bounds"]
            | done_terms["time_out"]
            | done_terms.get("stuck_timeout", torch.zeros_like(waypoint_hit))
            | done_terms.get("low_quality_terrain_hit", torch.zeros_like(waypoint_hit))
        )
        if self._uses_stage1_train_retirement():
            active_mask = self._stage1_training_active
        else:
            active_mask = torch.ones_like(waypoint_hit)
        progress_hit = waypoint_hit & ~blocked & active_mask
        quality_ok, _quality_advance, _low_quality_hit, _row_advance_without_quality = (
            self._compute_stage1_quality_advance_mask(progress_hit, can_advance)
        )
        progress_hit = progress_hit & quality_ok
        advance_mask = progress_hit & can_advance
        max_row_reached_mask = progress_hit & reaches_max_row
        self._last_stage1_progress_hit_mask.copy_(progress_hit)
        self._last_stage1_advance_mask.copy_(advance_mask)
        self._last_stage1_max_row_reached_mask.copy_(max_row_reached_mask)
        return progress_hit, advance_mask, max_row_reached_mask

    def _get_terrain_column_progress_advance_env_ids(self, relative_goal_commands: torch.Tensor) -> torch.Tensor:
        _progress_hit, advance_mask, _max_row_reached_mask = self._compute_terrain_column_progress_masks(
            relative_goal_commands
        )
        return torch.nonzero(advance_mask, as_tuple=False).flatten()

    def _advance_terrain_column_targets(self, env_ids: torch.Tensor) -> None:
        if (
            env_ids.numel() == 0
            or self._terrain_runtime is None
            or not self._terrain_runtime.generator_enabled
            or self._terrain_runtime.terrain_levels is None
        ):
            return

        self._terrain_runtime.terrain_levels[env_ids] = torch.clamp(
            self._terrain_runtime.terrain_levels[env_ids] + 1,
            max=max(int(self._terrain_runtime.max_terrain_level) - 1, 0),
        )
        min_row_offset = max(int(getattr(self.cfg.commands, "terrain_goal_min_row_offset", 1)), 1)
        max_target_level = max(int(self._terrain_runtime.max_terrain_level) - 1, 0)
        max_advance_source_level = max(max_target_level - min_row_offset, 0)
        self._last_stage1_valid_target_masked[env_ids] = (
            self._terrain_runtime.terrain_levels[env_ids] >= max_advance_source_level
        )
        self._terrain_runtime.sync_env_origins(self.scene, env_ids)

        base_pos_xy_w = self.robot.data.root_link_pos_w[env_ids, :2]
        base_yaw_w = quaternion_to_rpy(self.robot.data.root_link_quat_w[env_ids])[:, 2]
        self._active_waypoint_index[env_ids] = 0
        self._sample_waypoint_queue(env_ids, base_pos_xy_w, base_yaw_w)
        next_relative_goal_commands = self._compute_relative_goal_commands(env_ids)
        self.commands[env_ids] = next_relative_goal_commands
        self._previous_goal_distance[env_ids] = torch.linalg.vector_norm(
            next_relative_goal_commands[:, :2],
            dim=1,
        )
        self._episode_terrain_target_advances[env_ids] += 1
        self._reset_stage1_quality_advance_state(env_ids)
        self._height_patch_cache_invalid_envs[env_ids] = True
        self._cached_step_relative_goal_commands = None
        self._cached_step_raw_obs_terms = None

    def _advance_active_waypoints(self, env_ids: torch.Tensor) -> None:
        if env_ids.numel() == 0:
            return
        self._active_waypoint_index[env_ids] += 1
        self._sync_active_waypoint_targets(env_ids)
        self._set_active_goal_start_distance(env_ids, self.robot.data.root_link_pos_w[env_ids, :2])


    def _get_observations(self) -> dict:
        wheel_contact_forces_w = self._get_wheel_contact_forces_w_cached("post_physics")

        relative_goal_commands = self._compute_relative_goal_commands()
        self.commands.copy_(relative_goal_commands)
        raw_obs_terms = collect_raw_observation_terms(
            self.cfg,
            self.robot,
            self._ball_joint_ids,
            self._wheel_joint_ids,
            self._wheel_body_ids,
            wheel_contact_forces_w,
            self._total_vehicle_weight,
            self._joint_pos_targets[:, self._ball_joint_ids],
            relative_goal_commands,
            self.actions,
        )
        self._cached_step_relative_goal_commands = relative_goal_commands
        self._cached_step_raw_obs_terms = raw_obs_terms
        terrain_height_patch = self._get_observation_height_patch()
        self._last_critic_height_patch = terrain_height_patch
        terrain_features, terrain_feature_diagnostics = compute_terrain_features(self.cfg, terrain_height_patch)
        self._last_terrain_features = terrain_features
        self._last_terrain_feature_diagnostics = terrain_feature_diagnostics
        current_actor_obs = compute_actor_observation_from_raw_terms(self.cfg, raw_obs_terms, terrain_features)
        actor_obs = update_history(self._obs_history, current_actor_obs)
        critic_obs = compute_critic_observation(actor_obs, terrain_height_patch)
        if self._sensor_runtime is not None and self.cfg.debug.log_sensor_outputs:
            self.extras["sensors"] = self._sensor_runtime.get_raw_output()
        return {"actor": actor_obs, "critic": critic_obs}

    def _compute_critic_height_patch(self, env_ids: torch.Tensor | None = None) -> torch.Tensor | None:
        if not self.cfg.terrain.measure_heights or self._terrain_runtime is None:
            return None

        if env_ids is None:
            num_patch_envs = self.num_envs
            root_pos_w = self.robot.data.root_link_pos_w
            root_quat_w = self.robot.data.root_link_quat_w
        else:
            num_patch_envs = int(env_ids.numel())
            if num_patch_envs == 0:
                return torch.empty(
                    (0, self._critic_height_patch_local.shape[0]),
                    device=self.device,
                    dtype=self.robot.data.root_link_pos_w.dtype,
                )
            root_pos_w = self.robot.data.root_link_pos_w.index_select(0, env_ids)
            root_quat_w = self.robot.data.root_link_quat_w.index_select(0, env_ids)

        local_points = self._critic_height_patch_local.unsqueeze(0).expand(num_patch_envs, -1, -1)
        yaw = quaternion_to_rpy(root_quat_w)[:, 2]

        cos_yaw = torch.cos(yaw).unsqueeze(1)
        sin_yaw = torch.sin(yaw).unsqueeze(1)

        x_local = local_points[..., 0]
        y_local = local_points[..., 1]

        x_world = root_pos_w[:, 0:1] + cos_yaw * x_local - sin_yaw * y_local
        y_world = root_pos_w[:, 1:2] + sin_yaw * x_local + cos_yaw * y_local

        patch_points_xy_w = torch.stack((x_world, y_world), dim=-1)
        terrain_height = self._terrain_runtime.sample_heights_world_xy(patch_points_xy_w)

        relative_height = root_pos_w[:, 2:3] - terrain_height
        return torch.nan_to_num(relative_height, nan=0.0, posinf=0.0, neginf=0.0)

    def _get_observation_height_patch(self) -> torch.Tensor | None:
        if self.cfg.events:
            self._pre_reset_critic_height_patch = None
            return self._compute_critic_height_patch()

        terrain_height_patch = self._pre_reset_critic_height_patch
        self._pre_reset_critic_height_patch = None
        if terrain_height_patch is None:
            return self._compute_critic_height_patch()

        invalid_mask = self.reset_buf.clone()
        invalid_mask |= self._height_patch_cache_invalid_envs
        invalid_env_ids = torch.nonzero(invalid_mask, as_tuple=False).flatten()
        if invalid_env_ids.numel() == 0:
            return terrain_height_patch

        terrain_height_patch = terrain_height_patch.clone()
        refreshed_patch = self._compute_critic_height_patch(invalid_env_ids)
        if refreshed_patch is not None:
            terrain_height_patch[invalid_env_ids] = refreshed_patch
        self._height_patch_cache_invalid_envs.zero_()
        return terrain_height_patch

    def _compute_height_patch_world_points(self, relative_height_patch: torch.Tensor) -> torch.Tensor:
        local_points = self._critic_height_patch_local.unsqueeze(0).expand(self.num_envs, -1, -1)

        root_pos_w = self.robot.data.root_link_pos_w
        yaw = quaternion_to_rpy(self.robot.data.root_link_quat_w)[:, 2]

        cos_yaw = torch.cos(yaw).unsqueeze(1)
        sin_yaw = torch.sin(yaw).unsqueeze(1)

        x_local = local_points[..., 0]
        y_local = local_points[..., 1]

        x_world = root_pos_w[:, 0:1] + cos_yaw * x_local - sin_yaw * y_local
        y_world = root_pos_w[:, 1:2] + sin_yaw * x_local + cos_yaw * y_local
        z_world = root_pos_w[:, 2:3] - relative_height_patch

        patch_points_w = torch.stack((x_world, y_world, z_world), dim=-1)
        return torch.nan_to_num(patch_points_w, nan=0.0, posinf=0.0, neginf=0.0)

    def _draw_height_patch(self) -> None:
        if self._last_critic_height_patch is None or not self.cfg.terrain.measure_heights:
            return

        configured_env_indices = tuple(int(i) for i in self.cfg.debug.height_patch_visualization_env_indices)
        if configured_env_indices:
            valid_env_indices = [i for i in configured_env_indices if 0 <= i < self.num_envs]
            if not valid_env_indices:
                return
            env_ids = torch.tensor(valid_env_indices, device=self.device, dtype=torch.long)
        else:
            env_ids = torch.arange(self.num_envs, device=self.device, dtype=torch.long)

        patch_points_w = self._compute_height_patch_world_points(self._last_critic_height_patch).index_select(0, env_ids)
        positive_y_axis_w = None
        if self.cfg.debug.visualize_height_patch_positive_y_axis:
            root_yaw = quaternion_to_rpy(self.robot.data.root_link_quat_w.index_select(0, env_ids))[:, 2]
            positive_y_axis_w = torch.stack(
                (
                    -torch.sin(root_yaw),
                    torch.cos(root_yaw),
                    torch.zeros_like(root_yaw),
                ),
                dim=1,
            )
        self._debug_draw.draw_height_patch(
            patch_points_w,
            height_offset=float(self.cfg.debug.height_patch_marker_height_offset),
            color_range_m=float(self.cfg.debug.height_patch_color_range_m),
            positive_y_axis_w=positive_y_axis_w,
        )

    def _compute_edge_preview(
        self,
        terrain_height_patch: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        zeros = torch.zeros(self.num_envs, device=self.device, dtype=self.robot.data.root_link_pos_w.dtype)
        if terrain_height_patch is None:
            terrain_height_patch = self._compute_critic_height_patch()
        if terrain_height_patch is None:
            return zeros, zeros
        if self._edge_preview_x_indices.numel() < 2 or self._edge_preview_y_indices.numel() < 2:
            return zeros, zeros

        patch_grid = terrain_height_patch.reshape(
            self.num_envs,
            self._height_patch_x_points.numel(),
            self._height_patch_y_points.numel(),
        )
        preview_grid = patch_grid.index_select(1, self._edge_preview_x_indices).index_select(
            2,
            self._edge_preview_y_indices,
        )
        dx_jump = torch.abs(preview_grid[:, 1:, :] - preview_grid[:, :-1, :])
        dy_jump = torch.abs(preview_grid[:, :, 1:] - preview_grid[:, :, :-1])
        edge_height_jump = torch.maximum(
            torch.amax(dx_jump.reshape(self.num_envs, -1), dim=1),
            torch.amax(dy_jump.reshape(self.num_envs, -1), dim=1),
        )
        edge_low = float(self.cfg.rewards.params.edge_height_low_threshold_m)
        edge_high = float(self.cfg.rewards.params.edge_height_high_threshold_m)
        edge_denominator = max(edge_high - edge_low, 1.0e-6)
        edge_strength = torch.clamp((edge_height_jump - edge_low) / edge_denominator, min=0.0, max=1.0)
        return torch.nan_to_num(edge_strength, nan=0.0), torch.nan_to_num(edge_height_jump, nan=0.0)

    def _get_rewards(self) -> torch.Tensor:
        relative_goal_commands = self._pre_reset_relative_goal_commands
        if relative_goal_commands is None:
            relative_goal_commands = self._compute_relative_goal_commands()
        self.commands.copy_(relative_goal_commands)
        wheel_longitudinal_slip, wheel_slip_angle = compute_wheel_motion_observations(
            wheel_body_lin_vel_w=self.robot.data.body_lin_vel_w[:, self._wheel_body_ids],
            wheel_body_quat_w=self.robot.data.body_quat_w[:, self._wheel_body_ids],
            wheel_joint_vel=self.robot.data.joint_vel[:, self._wheel_joint_ids],
            wheel_radius=self.cfg.control.wheel_radius,
            slip_velocity_epsilon=self.cfg.observations.wheel_slip_epsilon,
        )
        wheel_slip_angle = torch.clamp(
            wheel_slip_angle,
            min=-self.cfg.observations.wheel_slip_angle_clip_rad,
            max=self.cfg.observations.wheel_slip_angle_clip_rad,
        )
        wheel_contact_forces_w = self._get_wheel_contact_forces_w_cached("post_physics")
        wheel_normal_contact_force = torch.linalg.vector_norm(wheel_contact_forces_w, dim=-1) / self._total_vehicle_weight
        wheel_contact_weights = self._wheel_speed_allocator.compute_contact_weights(
            wheel_normal_contact_force,
            self.cfg.control.contact_force_off_threshold,
            self.cfg.control.contact_force_on_threshold,
        )
        terrain_height_patch = self._compute_critic_height_patch()
        self._pre_reset_critic_height_patch = terrain_height_patch
        edge_strength, edge_height_jump = self._compute_edge_preview(terrain_height_patch)
        middle_pitch_rad = quaternion_to_rpy(self.robot.data.root_link_quat_w)[:, 1]
        self._prepare_stage1_quality_advance_baseline()
        reward_waypoint_hit_mask = self._last_done_terms["waypoint_hit"]
        if "low_quality_terrain_hit" in self._last_done_terms:
            reward_waypoint_hit_mask = reward_waypoint_hit_mask & ~self._last_done_terms["low_quality_terrain_hit"]
        total_reward, components, diagnostics = compute_reward_terms(
            self.cfg,
            relative_goal_commands,
            self._previous_goal_distance,
            self.episode_length_buf,
            self.max_episode_length,
            self.actions,
            self.last_actions,
            self.robot.data.root_com_lin_vel_b,
            wheel_longitudinal_slip,
            wheel_slip_angle,
            wheel_contact_weights,
            edge_strength,
            edge_height_jump,
            reward_waypoint_hit_mask,
            terrain_gates=self._last_terrain_feature_diagnostics,
            raw_planar_command=self._last_raw_planar_command,
            limited_planar_command=self._last_limited_planar_command,
            terrain_speed_safe=self._last_terrain_speed_safe,
            terrain_speed_limit_active=self._last_terrain_speed_limit_active,
            wheel_joint_vel=self.robot.data.joint_vel[:, self._wheel_joint_ids],
            ball_joint_pos=self.robot.data.joint_pos[:, self._ball_joint_ids],
            root_lin_vel_w=self._root_lin_vel_w(),
            root_ang_vel_b=self.robot.data.root_com_ang_vel_b,
            stuck_time_s=self._stage1_stuck_time,
            previous_module_support_heights=self._prev_stage1_module_support_heights,
            row_module_support_height_baseline=self._stage1_row_module_support_height_baseline,
            row_module_progress_max=self._stage1_row_module_progress_max,
            obstacle_gate=self._stage1_terrain_name_gate("discrete obstacles"),
            recovery_active=self._stage1_recovery_active,
            recovery_reverse_now=self._last_stage1_recovery_reverse_now,
            recovery_success=self._last_stage1_recovery_success,
            middle_pitch_rad=middle_pitch_rad,
        )
        self._update_stage1_quality_advance_state(diagnostics)
        if self._uses_stage1_train_retirement():
            inactive_mask = ~self._stage1_training_active
            if torch.any(inactive_mask):
                total_reward = total_reward.clone()
                total_reward[inactive_mask] = 0.0
                for name, value in tuple(components.items()):
                    masked_value = value.clone()
                    masked_value[inactive_mask] = 0.0
                    components[name] = masked_value
        self._previous_goal_distance.copy_(torch.linalg.vector_norm(relative_goal_commands[:, :2], dim=1))
        if self.cfg.commands.use_terrain_column_targets:
            advance_env_ids = torch.nonzero(self._last_stage1_advance_mask, as_tuple=False).flatten()
            quality_reward_raw = self._last_stage1_quality_advance_mask.float() * self._last_stage1_quality_advance_score
            old_quality_component = components["quality_row_advance_reward"]
            new_quality_component = (
                quality_reward_raw * float(getattr(self.cfg.rewards.params, "quality_row_advance_reward_weight", 0.0))
            )
            components["quality_row_advance_reward"] = new_quality_component
            diagnostics["quality_row_advance_mask"] = self._last_stage1_quality_advance_mask.float()
            diagnostics["quality_row_advance_reward_raw"] = quality_reward_raw
            diagnostics["quality_advance_score"] = self._last_stage1_quality_advance_score
            diagnostics["hard_quality_advance"] = self._last_stage1_quality_advance_mask.float()
            diagnostics["raw_hard_hit"] = self._last_stage1_raw_hard_hit.float()
            diagnostics["low_quality_hit"] = self._last_stage1_low_quality_hit.float()
            diagnostics["row_advance_without_quality"] = self._last_stage1_row_advance_without_quality.float()
            diagnostics["row_contact_support_min"] = self._stage1_row_contact_support_min
            diagnostics["row_stuck_time_max"] = self._stage1_row_stuck_time_max
            diagnostics["phase_module_progress_score"] = self._stage1_row_phase_module_progress_max
            diagnostics["actual_overspeed_near_edge"] = self._stage1_row_actual_overspeed_near_edge_max
            diagnostics["actual_overspeed_near_edge_rate"] = self._stage1_row_actual_overspeed_near_edge_ever.float()
            front_threshold = max(
                float(getattr(self.cfg.rewards.params, "quality_advance_front_progress_threshold_m", 0.03)),
                1.0e-6,
            )
            middle_threshold = max(
                float(getattr(self.cfg.rewards.params, "quality_advance_middle_progress_threshold_m", 0.03)),
                1.0e-6,
            )
            rear_threshold = max(
                float(getattr(self.cfg.rewards.params, "quality_advance_rear_progress_threshold_m", 0.02)),
                1.0e-6,
            )
            diagnostics["front_climb_success"] = (
                self._stage1_row_module_progress_max[:, 0] >= front_threshold
            ).float()
            diagnostics["middle_climb_success"] = (
                self._stage1_row_module_progress_max[:, 1] >= middle_threshold
            ).float()
            diagnostics["rear_follow_success"] = (
                self._stage1_row_module_progress_max[:, 2] >= rear_threshold
            ).float()
            total_reward = total_reward + new_quality_component - old_quality_component
        for name, value in components.items():
            self._episode_sums[name] += value
            self._last_reward_components[name].copy_(value)
        for name, value in diagnostics.items():
            if name not in self._last_reward_diagnostics:
                self._last_reward_diagnostics[name] = torch.zeros_like(value)
            self._last_reward_diagnostics[name].copy_(value)
        self._prev_stage1_module_support_heights.copy_(self._stage1_module_support_heights())

        self._episode_total_reward_sum += total_reward
        self._last_total_reward.copy_(total_reward)
        if self.cfg.commands.use_terrain_column_targets:
            if advance_env_ids.numel() > 0:
                self._advance_terrain_column_targets(advance_env_ids)
            return total_reward

        advance_env_ids = torch.nonzero(
            self._last_done_terms["waypoint_hit"]
            & ~self._last_done_terms["is_success"]
            & ~self._last_done_terms["far_from_target"]
            & ~self._last_done_terms["ball_joint_out_of_bounds"]
            & ~self._last_done_terms["time_out"]
            & ~self._last_done_terms["stuck_timeout"],
            as_tuple=False,
        ).flatten()
        if advance_env_ids.numel() > 0:
            self._advance_active_waypoints(advance_env_ids)
            next_relative_goal_commands = self._compute_relative_goal_commands(advance_env_ids)
            self.commands[advance_env_ids] = next_relative_goal_commands
            self._previous_goal_distance[advance_env_ids] = torch.linalg.vector_norm(
                next_relative_goal_commands[:, :2],
                dim=1,
            )
            self._cached_step_relative_goal_commands = None
            self._cached_step_raw_obs_terms = None
        return total_reward

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        relative_goal_commands = self._compute_relative_goal_commands()
        self.commands.copy_(relative_goal_commands)
        self._pre_reset_relative_goal_commands = relative_goal_commands
        self._last_active_waypoint_pos_error.copy_(torch.linalg.vector_norm(relative_goal_commands[:, :2], dim=1))
        self._last_active_waypoint_bearing_abs.copy_(torch.abs(relative_goal_commands[:, 3]))
        done_terms = compute_done_terms(
            self.cfg,
            self.robot,
            relative_goal_commands,
            self._active_waypoint_index,
            self._ball_joint_ids,
            self.episode_length_buf,
            self.max_episode_length,
        )
        done_terms.setdefault(
            "terrain_column_completed",
            torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
        )
        done_terms.setdefault(
            "low_quality_terrain_hit",
            torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
        )
        done_terms["stuck_timeout"] = self._update_stage1_stuck_state(relative_goal_commands)
        already_retired_mask = (
            ~self._stage1_training_active
            if self._uses_stage1_train_retirement()
            else torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        )
        self._last_stage1_max_row_reached.zero_()
        self._last_stage1_valid_target_masked.zero_()
        if (
            self.cfg.commands.use_terrain_column_targets
            and self._terrain_runtime is not None
            and self._terrain_runtime.generator_enabled
            and self._terrain_runtime.terrain_levels is not None
        ):
            min_row_offset = max(int(getattr(self.cfg.commands, "terrain_goal_min_row_offset", 1)), 1)
            max_target_level = max(int(self._terrain_runtime.max_terrain_level) - 1, 0)
            max_advance_source_level = max(max_target_level - min_row_offset, 0)
            self._last_stage1_valid_target_masked.copy_(
                self._terrain_runtime.terrain_levels >= max_advance_source_level
            )
            _progress_hit, _advance_mask, max_row_reached_mask = self._compute_terrain_column_progress_masks(
                relative_goal_commands,
                done_terms,
            )
            done_terms["low_quality_terrain_hit"] = self._last_stage1_low_quality_hit.clone()
            if torch.any(max_row_reached_mask):
                done_terms["terrain_column_completed"] = max_row_reached_mask
                self._episode_terrain_target_advances[max_row_reached_mask] += 1
                self._last_stage1_max_row_reached.copy_(max_row_reached_mask)
                self._record_stage1_column_completions(max_row_reached_mask)
                self._stage1_training_active[max_row_reached_mask] = False
        if self._uses_stage1_train_retirement():
            if torch.any(already_retired_mask):
                for value in done_terms.values():
                    value[already_retired_mask] = False
        waypoint_hit_count_mask = done_terms["waypoint_hit"] & ~done_terms["low_quality_terrain_hit"]
        waypoint_hit_env_ids = torch.nonzero(waypoint_hit_count_mask, as_tuple=False).flatten()
        if waypoint_hit_env_ids.numel() > 0:
            self._episode_waypoints_completed[waypoint_hit_env_ids] += 1
        for key, value in done_terms.items():
            self._last_done_terms[key].copy_(value)
        terminated = (
            done_terms["is_success"]
            | done_terms["far_from_target"]
            | done_terms["ball_joint_out_of_bounds"]
            | done_terms["stuck_timeout"]
            | done_terms["terrain_column_completed"]
            | done_terms["low_quality_terrain_hit"]
        )
        return terminated, done_terms["time_out"]


    def _collect_episode_logs(self, env_ids: torch.Tensor, terrain_metrics: dict[str, float] | None):
        extras = {}
        if env_ids.numel() == 0:
            return extras

        episode_lengths = self.episode_length_buf[env_ids].float().clamp(min=1.0)
        for name, buffer in self._episode_sums.items():
            extras[f"episode/{name}"] = float(torch.mean(buffer[env_ids]).item())
            extras[f"episode_per_step/{name}"] = float(torch.mean(buffer[env_ids] / episode_lengths).item())
        total_episode_reward = self._episode_total_reward_sum[env_ids]
        extras["episode/return"] = float(torch.mean(total_episode_reward).item())
        extras["episode/return_per_step"] = float(torch.mean(total_episode_reward / episode_lengths).item())
        extras["episode/goal_target_x_world"] = float(torch.mean(self.command_targets_w[env_ids, 0]).item())
        extras["episode/goal_target_y_world"] = float(torch.mean(self.command_targets_w[env_ids, 1]).item())
        extras["episode/goal_target_z_world"] = float(torch.mean(self.command_targets_w[env_ids, 2]).item())
        extras["episode/goal_target_heading_world"] = float(torch.mean(self.command_targets_w[env_ids, 3]).item())
        extras["episode/goal_direction_offset_deg"] = float(torch.mean(torch.rad2deg(self._goal_direction_offsets[env_ids])).item())
        extras["episode/goal_heading_offset_deg"] = float(torch.mean(torch.rad2deg(self._goal_heading_offsets[env_ids])).item())
        extras["episode/waypoints_completed"] = float(torch.mean(self._episode_waypoints_completed[env_ids].float()).item())
        extras["episode/terrain_target_advances"] = float(
            torch.mean(self._episode_terrain_target_advances[env_ids].float()).item()
        )
        extras["episode/waypoint_completion_pct"] = float(
            torch.mean(self._episode_waypoints_completed[env_ids].float() / float(self._num_waypoints_per_episode) * 100.0).item()
        )
        extras["episode/end_active_waypoint_pos_error"] = float(
            torch.mean(self._last_active_waypoint_pos_error[env_ids]).item()
        )
        extras["episode/end_active_waypoint_bearing_abs"] = float(
            torch.mean(self._last_active_waypoint_bearing_abs[env_ids]).item()
        )
        waypoint_hit_mask = self._last_done_terms["waypoint_hit"][env_ids]
        extras["episode/waypoint_hit_rate"] = float(torch.mean(waypoint_hit_mask.float()).item())
        if torch.any(waypoint_hit_mask):
            extras["episode/waypoint_hit_pos_error"] = float(
                torch.mean(self._last_active_waypoint_pos_error[env_ids][waypoint_hit_mask]).item()
            )
        success_mask = self._last_done_terms["is_success"][env_ids]
        if torch.any(success_mask):
            extras["episode/success_hit_pos_error"] = float(
                torch.mean(self._last_active_waypoint_pos_error[env_ids][success_mask]).item()
            )
        terminated = (
            self._last_done_terms["is_success"][env_ids]
            | self._last_done_terms["far_from_target"][env_ids]
            | self._last_done_terms["ball_joint_out_of_bounds"][env_ids]
            | self._last_done_terms["stuck_timeout"][env_ids]
            | self._last_done_terms["terrain_column_completed"][env_ids]
            | self._last_done_terms["low_quality_terrain_hit"][env_ids]
        )
        extras["Termination/terminated_rate"] = float(torch.mean(terminated.float()).item())
        extras["Termination/success_rate"] = float(torch.mean(self._last_done_terms["is_success"][env_ids].float()).item())
        extras["Termination/time_out_rate"] = float(torch.mean(self._last_done_terms["time_out"][env_ids].float()).item())
        extras["Termination/stuck_timeout_rate"] = float(
            torch.mean(self._last_done_terms["stuck_timeout"][env_ids].float()).item()
        )
        extras["Termination/terrain_column_completed_rate"] = float(
            torch.mean(self._last_done_terms["terrain_column_completed"][env_ids].float()).item()
        )
        extras["Termination/low_quality_terrain_hit_rate"] = float(
            torch.mean(self._last_done_terms["low_quality_terrain_hit"][env_ids].float()).item()
        )
        extras["Termination/far_from_target_rate"] = float(
            torch.mean(self._last_done_terms["far_from_target"][env_ids].float()).item()
        )
        extras["Termination/ball_joint_limit_rate"] = float(
            torch.mean(self._last_done_terms["ball_joint_out_of_bounds"][env_ids].float()).item()
        )
        if terrain_metrics is not None:
            extras.update({f"terrain/{key}": value for key, value in terrain_metrics.items()})
        return self._sanitize_scalar_metrics(extras)

    def _is_stage1(self) -> bool:
        return str(getattr(self.cfg, "stage_name", "")).lower() == "stage1"

    def _uses_stage1_train_retirement(self) -> bool:
        return self._is_stage1() and bool(getattr(self.cfg.commands, "use_terrain_column_targets", False))

    def _uses_stage1_completed_env_recycling(self) -> bool:
        return self._uses_stage1_train_retirement() and bool(
            getattr(self.cfg.curriculum, "terrain_column_recycle_completed_envs", False)
        )

    def _initialize_stage1_column_completion_tracking(self) -> None:
        if (
            not self._uses_stage1_train_retirement()
            or self._terrain_runtime is None
            or self._terrain_runtime.terrain_types is None
        ):
            return
        targets = mdp_curriculum.compute_terrain_column_counts(
            self._terrain_runtime.terrain_types,
            self._stage1_column_completion_targets.numel(),
        )
        self._stage1_column_completion_targets.copy_(targets)
        self._stage1_column_completion_counts.zero_()
        self._stage1_completed_terrain_columns.copy_(targets <= 0)

    def _record_stage1_column_completions(self, completed_env_mask: torch.Tensor) -> None:
        if (
            not self._uses_stage1_train_retirement()
            or self._terrain_runtime is None
            or self._terrain_runtime.terrain_types is None
            or completed_env_mask.numel() == 0
            or not torch.any(completed_env_mask)
        ):
            return
        completed_types = self._terrain_runtime.terrain_types[completed_env_mask]
        completion_counts = mdp_curriculum.compute_terrain_column_counts(
            completed_types,
            self._stage1_column_completion_counts.numel(),
        )
        self._stage1_column_completion_counts += completion_counts
        target_met = self._stage1_column_completion_counts >= self._stage1_column_completion_targets
        has_target = self._stage1_column_completion_targets > 0
        self._stage1_completed_terrain_columns |= target_met & has_target

    def _all_stage1_terrain_columns_completed(self) -> bool:
        if not self._uses_stage1_train_retirement():
            return False
        has_target = self._stage1_column_completion_targets > 0
        if not torch.any(has_target):
            return True
        unfinished = (~self._stage1_completed_terrain_columns) & has_target
        return bool(not torch.any(unfinished).item())

    def _sample_stage1_recycled_levels(self, assigned_terrain_types: torch.Tensor) -> torch.Tensor:
        if (
            self._terrain_runtime is None
            or self._terrain_runtime.terrain_levels is None
            or self._terrain_runtime.terrain_types is None
            or assigned_terrain_types.numel() == 0
        ):
            return torch.empty(0, dtype=torch.long, device=self.device)

        new_levels = torch.empty_like(assigned_terrain_types, dtype=torch.long, device=self.device)
        for terrain_type in torch.unique(assigned_terrain_types):
            target_mask = assigned_terrain_types == terrain_type
            target_count = int(target_mask.sum().item())
            active_source_mask = self._stage1_training_active & (self._terrain_runtime.terrain_types == terrain_type)
            source_levels = self._terrain_runtime.terrain_levels[active_source_mask]
            if source_levels.numel() > 0:
                sample_ids = torch.randint(source_levels.numel(), (target_count,), device=self.device)
                new_levels[target_mask] = source_levels[sample_ids]
            else:
                new_levels[target_mask] = mdp_curriculum.sample_initial_terrain_levels(
                    self.cfg.curriculum,
                    self._terrain_runtime,
                    assigned_terrain_types[target_mask],
                )
        return new_levels

    def _sample_stage1_completed_retention_levels(self, assigned_terrain_types: torch.Tensor) -> torch.Tensor:
        if (
            self._terrain_runtime is None
            or assigned_terrain_types.numel() == 0
        ):
            return torch.empty(0, dtype=torch.long, device=self.device)
        return mdp_curriculum.sample_initial_terrain_levels(
            self.cfg.curriculum,
            self._terrain_runtime,
            assigned_terrain_types,
        )

    def _recycle_stage1_completed_envs(self, env_ids: torch.Tensor) -> torch.Tensor:
        if (
            not self._uses_stage1_completed_env_recycling()
            or env_ids.numel() == 0
            or self._terrain_runtime is None
            or self._terrain_runtime.terrain_levels is None
            or self._terrain_runtime.terrain_types is None
        ):
            return torch.empty(0, dtype=torch.long, device=self.device)

        self._stage1_training_active[env_ids] = False
        has_target = self._stage1_column_completion_targets > 0
        unfinished_columns = (~self._stage1_completed_terrain_columns) & has_target
        completed_columns = self._stage1_completed_terrain_columns & has_target
        if not torch.any(unfinished_columns):
            return torch.empty(0, dtype=torch.long, device=self.device)

        active_counts = mdp_curriculum.compute_terrain_column_counts(
            self._terrain_runtime.terrain_types[self._stage1_training_active],
            self._stage1_column_completion_counts.numel(),
        )
        retention_ratio = float(getattr(self.cfg.curriculum, "terrain_column_completed_retention_ratio", 0.0))
        num_retention = mdp_curriculum.compute_completed_column_retention_count(
            active_counts,
            completed_columns,
            self.num_envs,
            retention_ratio,
            int(env_ids.numel()),
        )

        assigned_chunks: list[torch.Tensor] = []
        level_chunks: list[torch.Tensor] = []
        recycled_env_chunks: list[torch.Tensor] = []
        recycle_offset = int(self._stage1_recycle_cursor)

        if num_retention > 0:
            retention_types = mdp_curriculum.assign_recycled_terrain_columns(
                active_counts,
                completed_columns,
                num_retention,
                start_offset=recycle_offset,
            )
            if retention_types.numel() > 0:
                retention_env_ids = env_ids[: retention_types.numel()]
                retention_levels = self._sample_stage1_completed_retention_levels(retention_types)
                assigned_chunks.append(retention_types)
                level_chunks.append(retention_levels)
                recycled_env_chunks.append(retention_env_ids)
                active_counts += mdp_curriculum.compute_terrain_column_counts(
                    retention_types,
                    self._stage1_column_completion_counts.numel(),
                )
                recycle_offset += int(retention_types.numel())

        assigned_so_far = sum(int(chunk.numel()) for chunk in assigned_chunks)
        remaining_count = max(int(env_ids.numel()) - assigned_so_far, 0)
        if remaining_count > 0:
            unfinished_types = mdp_curriculum.assign_recycled_terrain_columns(
                active_counts,
                unfinished_columns,
                remaining_count,
                start_offset=recycle_offset,
            )
            if unfinished_types.numel() > 0:
                unfinished_env_ids = env_ids[assigned_so_far : assigned_so_far + unfinished_types.numel()]
                unfinished_levels = self._sample_stage1_recycled_levels(unfinished_types)
                assigned_chunks.append(unfinished_types)
                level_chunks.append(unfinished_levels)
                recycled_env_chunks.append(unfinished_env_ids)
                recycle_offset += int(unfinished_types.numel())

        if not assigned_chunks:
            return torch.empty(0, dtype=torch.long, device=self.device)

        assigned_types = torch.cat(assigned_chunks, dim=0)
        new_levels = torch.cat(level_chunks, dim=0)
        recycled_env_ids = torch.cat(recycled_env_chunks, dim=0)
        self._terrain_runtime.terrain_types[recycled_env_ids] = assigned_types
        self._terrain_runtime.terrain_levels[recycled_env_ids] = new_levels
        self._stage1_training_active[recycled_env_ids] = True
        self._stage1_recycled_envs_ever[recycled_env_ids] = True
        self._stage1_last_recycled_env_mask[recycled_env_ids] = True
        self._stage1_recycle_cursor = (
            self._stage1_recycle_cursor + int(assigned_types.numel())
        ) % max(int(self._stage1_column_completion_counts.numel()), 1)
        return recycled_env_ids

    def _stage1_terrain_feature_value(self, name: str, *, default: float = 0.0) -> torch.Tensor:
        value = self._last_terrain_feature_diagnostics.get(name)
        if value is None:
            return torch.full((self.num_envs,), float(default), device=self.device)
        return torch.nan_to_num(value.to(device=self.device).reshape(self.num_envs), nan=0.0, posinf=0.0, neginf=0.0)

    def _stage1_terrain_name_gate(self, terrain_name: str) -> torch.Tensor:
        gate = torch.zeros(self.num_envs, device=self.device)
        if (
            not self._is_stage1()
            or self._terrain_runtime is None
            or self._terrain_runtime.terrain_levels is None
            or self._terrain_runtime.terrain_types is None
        ):
            return gate
        terrain_names = tuple(getattr(self._terrain_runtime._terrain_cfg, "terrain_names", ()))
        if terrain_name not in terrain_names:
            return gate
        terrain_type_idx = terrain_names.index(terrain_name)
        tile_type_indices = self._terrain_runtime.get_tile_type_indices(
            self._terrain_runtime.terrain_levels,
            self._terrain_runtime.terrain_types,
        )
        return (tile_type_indices == terrain_type_idx).float()

    def _stage1_module_support_heights(self) -> torch.Tensor:
        return torch.stack(
            (
                self._stage1_terrain_feature_value("front_support_height_m"),
                self._stage1_terrain_feature_value("middle_support_height_m"),
                self._stage1_terrain_feature_value("rear_support_height_m"),
            ),
            dim=1,
        )

    def _reset_stage1_quality_advance_state(self, env_ids: torch.Tensor) -> None:
        if env_ids.numel() == 0:
            return
        self._stage1_row_quality_baseline_ready[env_ids] = False
        self._stage1_row_module_support_height_baseline[env_ids] = 0.0
        self._stage1_row_module_progress_max[env_ids] = 0.0
        self._stage1_row_contact_support_min[env_ids] = 1.0
        self._stage1_row_stuck_time_max[env_ids] = 0.0
        self._stage1_row_actual_overspeed_near_edge_max[env_ids] = 0.0
        self._stage1_row_actual_overspeed_near_edge_ever[env_ids] = False
        self._stage1_row_phase_module_progress_max[env_ids] = 0.0
        self._last_stage1_quality_advance_score[env_ids] = 0.0
        self._last_stage1_quality_advance_mask[env_ids] = False
        self._last_stage1_low_quality_hit[env_ids] = False
        self._last_stage1_raw_hard_hit[env_ids] = False
        self._last_stage1_row_advance_without_quality[env_ids] = False
        self._last_stage1_progress_hit_mask[env_ids] = False
        self._last_stage1_advance_mask[env_ids] = False
        self._last_stage1_max_row_reached_mask[env_ids] = False

    def _prepare_stage1_quality_advance_baseline(self) -> None:
        if not self._is_stage1():
            return
        not_ready = ~self._stage1_row_quality_baseline_ready
        if not torch.any(not_ready):
            return
        support_heights = self._stage1_module_support_heights()
        self._stage1_row_module_support_height_baseline[not_ready] = support_heights[not_ready]
        self._stage1_row_quality_baseline_ready[not_ready] = True

    def _stage1_hard_terrain_mask(self) -> torch.Tensor:
        hard_mask = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        if (
            not self._is_stage1()
            or self._terrain_runtime is None
            or self._terrain_runtime.terrain_classes is None
        ):
            return hard_mask
        return self._terrain_runtime.terrain_classes == STAGE1_TERRAIN_CLASS_STEP

    def _update_stage1_quality_advance_state(self, diagnostics: dict[str, torch.Tensor]) -> None:
        if not self._is_stage1():
            return
        active_mask = (
            self._stage1_training_active
            if self._uses_stage1_train_retirement()
            else torch.ones(self.num_envs, dtype=torch.bool, device=self.device)
        )
        hard_mask = self._stage1_hard_terrain_mask() & active_mask
        if not torch.any(hard_mask):
            return

        edge_gate = torch.clamp(diagnostics.get("terrain_gate_edge", torch.zeros(self.num_envs, device=self.device)), 0.0, 1.0)
        near_edge = hard_mask & (edge_gate > 0.05)
        contact_score = torch.clamp(
            diagnostics.get("module_support_phase_score", diagnostics.get("contact_support_score", torch.ones(self.num_envs, device=self.device))),
            0.0,
            1.0,
        )
        self._stage1_row_contact_support_min[near_edge] = torch.minimum(
            self._stage1_row_contact_support_min[near_edge],
            contact_score[near_edge],
        )
        self._stage1_row_stuck_time_max[hard_mask] = torch.maximum(
            self._stage1_row_stuck_time_max[hard_mask],
            self._stage1_stuck_time[hard_mask],
        )
        actual_excess = torch.clamp(
            diagnostics.get("terrain_speed_actual_excess", torch.zeros(self.num_envs, device=self.device)),
            min=0.0,
        )
        self._stage1_row_actual_overspeed_near_edge_max[near_edge] = torch.maximum(
            self._stage1_row_actual_overspeed_near_edge_max[near_edge],
            actual_excess[near_edge],
        )
        margin = max(float(getattr(self.cfg.rewards.params, "quality_advance_actual_overspeed_margin_mps", 0.10)), 1.0e-6)
        self._stage1_row_actual_overspeed_near_edge_ever |= near_edge & (actual_excess > margin)

        front_progress = torch.clamp(diagnostics.get("front_module_height_progress", torch.zeros(self.num_envs, device=self.device)), min=0.0)
        middle_progress = torch.clamp(diagnostics.get("middle_module_height_progress", torch.zeros(self.num_envs, device=self.device)), min=0.0)
        rear_progress = torch.clamp(diagnostics.get("rear_module_height_progress", torch.zeros(self.num_envs, device=self.device)), min=0.0)
        row_progress = torch.stack((front_progress, middle_progress, rear_progress), dim=1)
        self._stage1_row_module_progress_max[hard_mask] = torch.maximum(
            self._stage1_row_module_progress_max[hard_mask],
            row_progress[hard_mask],
        )
        module_progress_scale = max(
            float(getattr(self.cfg.rewards.params, "step_up_module_height_progress_scale_m", 0.05)),
            1.0e-6,
        )
        module_progress_score = torch.clamp(
            (
                0.2 * self._stage1_row_module_progress_max[:, 0]
                + 0.5 * self._stage1_row_module_progress_max[:, 1]
                + 0.3 * self._stage1_row_module_progress_max[:, 2]
            )
            / module_progress_scale,
            min=0.0,
            max=1.0,
        )
        self._stage1_row_phase_module_progress_max[hard_mask] = torch.maximum(
            self._stage1_row_phase_module_progress_max[hard_mask],
            module_progress_score[hard_mask],
        )

    def _compute_stage1_quality_advance_mask(
        self,
        progress_hit: torch.Tensor,
        can_advance: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        hard_hit = progress_hit & self._stage1_hard_terrain_mask()
        margin = max(float(getattr(self.cfg.rewards.params, "quality_advance_actual_overspeed_margin_mps", 0.10)), 1.0e-6)
        contact_min = max(float(getattr(self.cfg.rewards.params, "quality_advance_contact_min", 0.70)), 1.0e-6)
        module_min = max(float(getattr(self.cfg.rewards.params, "quality_advance_module_progress_min", 0.35)), 1.0e-6)
        stuck_scale = max(float(getattr(self.cfg.rewards.params, "progress_quality_stuck_time_scale_s", 2.0)), 1.0e-6)
        speed_quality = torch.clamp(1.0 - self._stage1_row_actual_overspeed_near_edge_max / margin, min=0.0, max=1.0)
        contact_quality = torch.clamp(self._stage1_row_contact_support_min / contact_min, min=0.0, max=1.0)
        not_stuck_quality = torch.clamp(1.0 - self._stage1_row_stuck_time_max / stuck_scale, min=0.0, max=1.0)

        obstacle_mask = self._stage1_terrain_name_gate("discrete obstacles") > 0.5
        module_quality = torch.where(
            obstacle_mask,
            torch.clamp(self._stage1_row_phase_module_progress_max / module_min, min=0.0, max=1.0),
            torch.ones_like(speed_quality),
        )
        quality_score = torch.minimum(
            torch.minimum(speed_quality, contact_quality),
            torch.minimum(not_stuck_quality, module_quality),
        )
        min_score = float(getattr(self.cfg.rewards.params, "quality_advance_min_score", 0.35))
        contact_ok = self._stage1_row_contact_support_min >= contact_min
        quality_ok = (quality_score >= min_score) & contact_ok
        quality_advance = hard_hit & quality_ok
        quality_gate_enabled = bool(getattr(self.cfg.rewards.params, "quality_gated_terrain_advance", False))
        low_quality_hit = hard_hit & ~quality_ok if quality_gate_enabled else torch.zeros_like(hard_hit)
        row_advance_without_quality = hard_hit & can_advance & ~quality_ok

        self._last_stage1_quality_advance_score.copy_(quality_score)
        self._last_stage1_quality_advance_mask.copy_(quality_advance)
        self._last_stage1_low_quality_hit.copy_(low_quality_hit)
        self._last_stage1_raw_hard_hit.copy_(hard_hit)
        self._last_stage1_row_advance_without_quality.copy_(row_advance_without_quality)
        if quality_gate_enabled:
            advance_allowed = quality_ok | ~self._stage1_hard_terrain_mask()
        else:
            advance_allowed = torch.ones_like(progress_hit)
        return advance_allowed, quality_advance, low_quality_hit, row_advance_without_quality

    def _compute_stage1_terrain_speed_safe(self) -> tuple[torch.Tensor, torch.Tensor]:
        flat_speed_limit = max(float(self.cfg.control.base_forward_velocity_max), 1.0e-6)
        if not (self._is_stage1() and bool(getattr(self.cfg.control, "terrain_speed_limit_enabled", False))):
            return (
                torch.full((self.num_envs,), flat_speed_limit, device=self.device),
                torch.zeros(self.num_envs, device=self.device),
            )
        g_step_up = torch.clamp(self._stage1_terrain_feature_value("g_step_up"), min=0.0, max=1.0)
        g_step_down = torch.clamp(self._stage1_terrain_feature_value("g_step_down"), min=0.0, max=1.0)
        g_gap = torch.clamp(self._stage1_terrain_feature_value("g_gap"), min=0.0, max=1.0)
        max_preview_distance_m = max(
            float(getattr(self.cfg.terrain, "patch_front_extent", 0.0))
            + float(getattr(self.cfg.terrain, "patch_preview_length", 1.0)),
            1.0e-6,
        )
        step_up_distance_m = self._stage1_terrain_feature_value("step_up_distance_norm", default=1.0) * max_preview_distance_m
        reference = g_step_up
        v_safe = compute_stage1_phase_speed_safe(
            self.cfg,
            reference,
            g_step_up,
            g_step_down,
            g_gap,
            step_up_distance_m,
            obstacle_gate=self._stage1_terrain_name_gate("discrete obstacles"),
        )
        g_edge = torch.maximum(g_step_up, torch.maximum(g_step_down, g_gap))
        return torch.nan_to_num(v_safe, nan=flat_speed_limit, posinf=flat_speed_limit, neginf=0.0), g_edge

    def _apply_stage1_terrain_speed_limit(self, planar_command: torch.Tensor) -> torch.Tensor:
        raw_planar_command = planar_command.clone()
        v_safe, g_edge = self._compute_stage1_terrain_speed_safe()
        limited_planar_command = planar_command.clone()
        if self._is_stage1() and bool(getattr(self.cfg.control, "terrain_speed_limit_enabled", False)):
            vx_cmd_raw = raw_planar_command[:, 0]
            vx_forward = torch.clamp(vx_cmd_raw, min=0.0)
            vx_reverse = torch.clamp(vx_cmd_raw, max=0.0)
            vx_forward_limited = torch.minimum(vx_forward, v_safe)
            limited_planar_command[:, 0] = vx_forward_limited + vx_reverse
            self._last_terrain_speed_limit_active.copy_(
                (vx_forward > vx_forward_limited + 1.0e-4) & (g_edge > 0.05)
            )
        else:
            self._last_terrain_speed_limit_active.zero_()
        self._last_raw_planar_command.copy_(raw_planar_command)
        self._last_limited_planar_command.copy_(limited_planar_command)
        self._last_terrain_speed_safe.copy_(v_safe)
        return limited_planar_command

    def _root_lin_vel_w(self) -> torch.Tensor:
        root_lin_vel_w = getattr(self.robot.data, "root_com_lin_vel_w", None)
        if root_lin_vel_w is None:
            root_lin_vel_w = getattr(self.robot.data, "root_link_lin_vel_w", None)
        if root_lin_vel_w is None:
            return torch.zeros_like(self.robot.data.root_com_lin_vel_b)
        return torch.nan_to_num(root_lin_vel_w, nan=0.0, posinf=0.0, neginf=0.0)

    def _update_stage1_stuck_state(self, relative_goal_commands: torch.Tensor) -> torch.Tensor:
        if not self._is_stage1():
            self._stage1_stuck_time.zero_()
            self._last_stage1_stuck_now.zero_()
            self._stage1_recovery_active.zero_()
            self._stage1_recovery_reverse_time_s.zero_()
            self._last_stage1_recovery_reverse_now.zero_()
            self._last_stage1_recovery_success.zero_()
            return torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        params = self.cfg.rewards.params
        timeout_s = float(getattr(params, "stuck_timeout_s", 0.0))
        g_step_up = torch.clamp(self._stage1_terrain_feature_value("g_step_up"), min=0.0, max=1.0)
        g_step_down = torch.clamp(self._stage1_terrain_feature_value("g_step_down"), min=0.0, max=1.0)
        g_gap = torch.clamp(self._stage1_terrain_feature_value("g_gap"), min=0.0, max=1.0)
        hard_gate = torch.maximum(g_step_up, torch.maximum(g_step_down, g_gap))
        v_forward = self.robot.data.root_com_lin_vel_b[:, 0]
        low_forward_speed = torch.abs(v_forward) < float(getattr(params, "stuck_speed_threshold_mps", 0.05))
        target_still_ahead = relative_goal_commands[:, 0] > float(
            getattr(params, "stuck_goal_ahead_threshold_m", 0.5)
        )
        current_goal_distance = torch.linalg.vector_norm(relative_goal_commands[:, :2], dim=1)
        active_mask = self._stage1_training_active if self._uses_stage1_train_retirement() else torch.ones(
            self.num_envs,
            dtype=torch.bool,
            device=self.device,
        )
        stuck_now = (
            (hard_gate > float(getattr(params, "stuck_gate_threshold", 0.3)))
            & low_forward_speed
            & target_still_ahead
            & active_mask
        )
        previous_recovery_active = self._stage1_recovery_active.clone()
        recovery_start_threshold_s = float(getattr(params, "recovery_stuck_time_threshold_s", 0.5))
        recovery_start = (self._stage1_stuck_time >= recovery_start_threshold_s) & stuck_now
        recovery_continue = (
            previous_recovery_active
            & (hard_gate > float(getattr(params, "stuck_gate_threshold", 0.3)))
            & target_still_ahead
            & active_mask
        )
        recovery_active = recovery_start | recovery_continue
        recovery_starting = recovery_start & ~previous_recovery_active
        self._stage1_recovery_start_goal_distance.copy_(
            torch.where(recovery_starting, current_goal_distance, self._stage1_recovery_start_goal_distance)
        )
        reverse_threshold = float(getattr(params, "recovery_reverse_cmd_threshold_mps", 0.05))
        reverse_now = recovery_active & (
            (self._last_limited_planar_command[:, 0] < -reverse_threshold)
            | (v_forward < -reverse_threshold)
        )
        self._stage1_recovery_reverse_time_s.copy_(
            torch.where(
                recovery_active & reverse_now,
                self._stage1_recovery_reverse_time_s + self.step_dt,
                torch.where(
                    recovery_active,
                    self._stage1_recovery_reverse_time_s,
                    torch.zeros_like(self._stage1_recovery_reverse_time_s),
                ),
            )
        )
        recovery_success = recovery_active & (
            (self._stage1_recovery_start_goal_distance - current_goal_distance)
            > float(getattr(params, "recovery_success_progress_m", 0.10))
        )
        stuck_tracking_now = stuck_now | (recovery_active & ~recovery_success)
        self._stage1_stuck_time.copy_(
            torch.where(
                stuck_tracking_now,
                self._stage1_stuck_time + self.step_dt,
                torch.zeros_like(self._stage1_stuck_time),
            )
        )
        self._stage1_stuck_time[recovery_success] = 0.0
        self._stage1_recovery_active.copy_(recovery_active & ~recovery_success)
        self._last_stage1_recovery_reverse_now.copy_(reverse_now)
        self._last_stage1_recovery_success.copy_(recovery_success)
        self._last_stage1_stuck_now.copy_(stuck_now)
        if timeout_s <= 0.0:
            return torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        return self._stage1_stuck_time > timeout_s

    @staticmethod
    def _sanitize_scalar_metrics(metrics: dict[str, float]) -> dict[str, float]:
        sanitized: dict[str, float] = {}
        for key, value in metrics.items():
            if isinstance(value, torch.Tensor):
                tensor_value = value.detach().float().reshape(-1)
            else:
                tensor_value = torch.as_tensor(value, dtype=torch.float32).reshape(-1)
            if tensor_value.numel() == 0:
                sanitized[key] = 0.0
            else:
                sanitized[key] = float(
                    torch.nan_to_num(torch.mean(tensor_value), nan=0.0, posinf=0.0, neginf=0.0).item()
                )
        return sanitized

    def _add_stage1_debug_metrics(self, metrics: dict[str, float]) -> None:
        if not self._is_stage1():
            return
        debug_prefixes = (
            "Reward/",
            "ProgressGate/",
            "ContactSupport/",
            "Slip/",
            "EdgeSpeed/",
            "Stuck/",
            "HardTerrainSpin/",
            "Posture/",
            "Drop/",
            "Action/",
            "LowLevel/",
            "Command/",
            "Terrain/",
        )
        for key, value in tuple(metrics.items()):
            if key.startswith(debug_prefixes):
                metrics[f"Debug/Stage1/{key}"] = value

    def _should_collect_per_wheel_metrics(self) -> bool:
        if not self._is_stage1():
            return True
        return bool(getattr(self.cfg.logging, "enable_stage1_per_wheel_debug", False))

    def _apply_stage1_terrain_column_reset_curriculum(self, env_ids: torch.Tensor) -> dict[str, float] | None:
        if (
            not self._is_stage1()
            or not self.cfg.commands.use_terrain_column_targets
            or self._terrain_runtime is None
            or not self._terrain_runtime.generator_enabled
            or self._terrain_runtime.terrain_levels is None
            or self._terrain_runtime.terrain_types is None
        ):
            return None
        if env_ids.numel() == 0:
            return None

        self._stage1_last_recycled_env_mask[env_ids] = False
        levels = self._terrain_runtime.terrain_levels[env_ids]
        terrain_types = self._terrain_runtime.terrain_types[env_ids]
        min_row_offset = max(int(getattr(self.cfg.commands, "terrain_goal_min_row_offset", 1)), 1)
        max_target_level = max(int(self._terrain_runtime.max_terrain_level) - 1, 0)
        max_advance_source_level = max(max_target_level - min_row_offset, 0)
        completed = self._last_done_terms["terrain_column_completed"][env_ids]
        column_completed = self._stage1_completed_terrain_columns[terrain_types]
        closed_column_reset = column_completed & self._uses_stage1_completed_env_recycling()
        recycle_candidate = completed | (closed_column_reset & self._stage1_training_active[env_ids])
        clamp_to_last_source = levels > max_advance_source_level
        row_progress = self._compute_active_goal_progress(env_ids)
        stuck_timeout = self._last_done_terms["stuck_timeout"][env_ids]
        min_levels = mdp_curriculum.get_min_initial_terrain_levels(
            self.cfg.curriculum,
            self._terrain_runtime,
            self._terrain_runtime.terrain_types[env_ids],
        )
        row_failed = (
            (
                self._last_done_terms["far_from_target"][env_ids]
                | self._last_done_terms["ball_joint_out_of_bounds"][env_ids]
                | self._last_done_terms["time_out"][env_ids]
                | stuck_timeout
            )
            & ~self._last_done_terms["waypoint_hit"][env_ids]
            & ~recycle_candidate
            & ~clamp_to_last_source
        )
        move_down_threshold = float(getattr(self.cfg.curriculum, "terrain_column_move_down_progress_ratio", 0.30))
        progress_move_down = row_failed & (row_progress < move_down_threshold)
        stuck_move_down = stuck_timeout & ~recycle_candidate & ~clamp_to_last_source
        move_down = (progress_move_down | stuck_move_down) & (levels > min_levels)

        if torch.any(clamp_to_last_source):
            clamp_env_ids = env_ids[clamp_to_last_source]
            self._terrain_runtime.terrain_levels[clamp_env_ids] = max_advance_source_level
        if torch.any(move_down):
            move_down_env_ids = env_ids[move_down]
            self._terrain_runtime.terrain_levels[move_down_env_ids] = torch.clamp(
                self._terrain_runtime.terrain_levels[move_down_env_ids] - 1,
                min=min_levels[move_down],
            )

        recycled_env_ids = self._recycle_stage1_completed_envs(env_ids[recycle_candidate])
        recycled_after_reset = recycle_candidate & self._stage1_training_active[env_ids]
        retired_after_reset = recycle_candidate & ~self._stage1_training_active[env_ids]
        terrain_types_after_reset = self._terrain_runtime.terrain_types[env_ids]
        recycled_to_retired_columns = recycled_after_reset & self._stage1_completed_terrain_columns[
            terrain_types_after_reset
        ]
        recycled_to_unfinished_columns = recycled_after_reset & ~self._stage1_completed_terrain_columns[
            terrain_types_after_reset
        ]
        has_target_columns = self._stage1_column_completion_targets > 0
        completed_columns = self._stage1_completed_terrain_columns & has_target_columns
        completed_column_rate = (
            torch.mean(self._stage1_completed_terrain_columns[has_target_columns].float())
            if torch.any(has_target_columns)
            else torch.ones((), device=self.device)
        )
        unfinished_column_count = torch.sum((~self._stage1_completed_terrain_columns) & has_target_columns).float()
        active_column_counts = mdp_curriculum.compute_terrain_column_counts(
            self._terrain_runtime.terrain_types[self._stage1_training_active],
            self._stage1_column_completion_counts.numel(),
        )
        completed_column_active_count = (
            torch.sum(active_column_counts[completed_columns]).float()
            if torch.any(completed_columns)
            else torch.zeros((), device=self.device)
        )

        self._terrain_runtime.sync_env_origins(self.scene, env_ids)
        return self._sanitize_scalar_metrics(
            {
                "terrain/row_progress_at_reset": row_progress,
                "terrain/move_down_ratio": move_down.float(),
                "terrain/stuck_move_down_ratio": stuck_move_down.float(),
                "terrain/terrain_column_completed_ratio": completed.float(),
                "terrain/recycle_candidate_ratio": recycle_candidate.float(),
                "terrain/recycled_env_ratio": recycled_after_reset.float(),
                "terrain/recycled_to_retired_column_ratio": recycled_to_retired_columns.float(),
                "terrain/recycled_to_unfinished_column_ratio": recycled_to_unfinished_columns.float(),
                "terrain/retired_no_recycle_target_ratio": retired_after_reset.float(),
                "terrain/recycled_env_count": float(recycled_env_ids.numel()),
                "terrain/recycled_to_retired_column_count": float(torch.sum(recycled_to_retired_columns).item()),
                "terrain/recycled_to_unfinished_column_count": float(
                    torch.sum(recycled_to_unfinished_columns).item()
                ),
                "terrain/completed_column_rate": completed_column_rate,
                "terrain/unfinished_column_count": unfinished_column_count,
                "terrain/completed_column_active_env_count": completed_column_active_count,
                "terrain/clamp_to_last_source_ratio": clamp_to_last_source.float(),
                "terrain/level_after_reset": self._terrain_runtime.terrain_levels[env_ids].float(),
            }
        )

    def _collect_step_metrics(self) -> dict[str, float]:
        relative_goal_commands = self._cached_step_relative_goal_commands
        raw_obs_terms = self._cached_step_raw_obs_terms
        if relative_goal_commands is None or raw_obs_terms is None:
            relative_goal_commands = self._compute_relative_goal_commands()
            wheel_contact_forces_w = self._get_wheel_contact_forces_w_cached("post_physics")
            raw_obs_terms = collect_raw_observation_terms(
                self.cfg,
                self.robot,
                self._ball_joint_ids,
                self._wheel_joint_ids,
                self._wheel_body_ids,
                wheel_contact_forces_w,
                self._total_vehicle_weight,
                self._joint_pos_targets[:, self._ball_joint_ids],
                relative_goal_commands,
                self.actions,
            )
        self.commands.copy_(relative_goal_commands)
        wheel_contact_forces_w_for_metrics = self._get_wheel_contact_forces_w_cached("post_physics")
        wheel_normal_force_n = torch.linalg.vector_norm(wheel_contact_forces_w_for_metrics, dim=-1)
        middle_rpy = quaternion_to_rpy(self.robot.data.root_link_quat_w)
        middle_roll_deg = torch.rad2deg(middle_rpy[:, 0])
        middle_pitch_deg = torch.rad2deg(middle_rpy[:, 1])
        root_lin_vel_w = self._root_lin_vel_w()
        pitch_rate_abs = torch.abs(raw_obs_terms["base_ang_vel"][:, 1])
        vz_down = torch.clamp(-root_lin_vel_w[:, 2], min=0.0)
        active_waypoint_pos_error = torch.linalg.vector_norm(relative_goal_commands[:, :2], dim=1)
        active_waypoint_bearing_abs = torch.abs(relative_goal_commands[:, 3])
        active_goal_start_distance = self._active_goal_start_distance.clamp(min=1.0e-6)
        active_segment_distance_covered = torch.clamp(active_goal_start_distance - active_waypoint_pos_error, min=0.0)
        active_segment_completion_pct = 100.0 * active_segment_distance_covered / torch.clamp(
            active_goal_start_distance,
            min=1.0e-6,
        )
        episode_completion_pct = self._episode_waypoints_completed.float() / float(self._num_waypoints_per_episode) * 100.0
        wheel_longitudinal_slip_abs = torch.abs(raw_obs_terms["wheel_longitudinal_slip"])
        wheel_slip_angle_abs = torch.abs(raw_obs_terms["wheel_slip_angle"])
        longitudinal_slip_abs_mean_per_env = torch.mean(wheel_longitudinal_slip_abs, dim=1)
        slip_angle_abs_mean_per_env = torch.mean(wheel_slip_angle_abs, dim=1)
        low_longitudinal_slip_mask = (
            longitudinal_slip_abs_mean_per_env <= self.cfg.rewards.params.low_slip_longitudinal_threshold
        )
        low_slip_angle_mask = slip_angle_abs_mean_per_env <= self.cfg.rewards.params.low_slip_angle_threshold_rad
        low_slip_mask = low_longitudinal_slip_mask & low_slip_angle_mask
        ball_joint_pos = raw_obs_terms["ball_joint_pos"]
        ball_joint_lower_limits = ball_joint_pos.new_tensor(self.cfg.terminations.ball_joint_pos_lower_limits).unsqueeze(0)
        ball_joint_upper_limits = ball_joint_pos.new_tensor(self.cfg.terminations.ball_joint_pos_upper_limits).unsqueeze(0)
        active_ball_joint_limits = torch.where(
            ball_joint_pos >= 0.0,
            ball_joint_upper_limits,
            torch.abs(ball_joint_lower_limits),
        )
        ball_joint_limit_usage = torch.abs(ball_joint_pos) / torch.clamp(active_ball_joint_limits, min=1.0e-6)
        # TensorBoard command traces are intentionally anchored to env_0 instead of the
        # cross-env mean so the curve reflects one concrete command trajectory.
        command_env_id = 0
        planar_command_delta = self._last_shaped_planar_command - self._last_desired_planar_command

        metrics = {
            "Meta/stage_id": 1.0 if self._is_stage1() else 0.0,
            "Reward/total": float(torch.mean(self._last_total_reward).item()),
            "Reward/distance_to_target": float(torch.mean(self._last_reward_components["distance_to_target"]).item()),
            "Reward/progress_to_target": float(torch.mean(self._last_reward_components["progress_to_target"]).item()),
            "Reward/reached_target": float(torch.mean(self._last_reward_components["reached_target"]).item()),
            "Reward/far_from_target": float(torch.mean(self._last_reward_components["far_from_target"]).item()),
            "Reward/angle_diff": float(torch.mean(self._last_reward_components["angle_diff"]).item()),
            "Reward/slip_penalty": float(torch.mean(self._last_reward_components["slip_penalty"]).item()),
            "Reward/action_rate_penalty": float(
                torch.mean(self._last_reward_components["action_rate_penalty"]).item()
            ),
            "Reward/contact_support_penalty": float(
                torch.mean(self._last_reward_components["contact_support_penalty"]).item()
            ),
            "Reward/edge_speed_penalty": float(
                torch.mean(self._last_reward_components["edge_speed_penalty"]).item()
            ),
            "Reward/terrain_aware_edge_speed_penalty": float(
                torch.mean(self._last_reward_components["terrain_aware_edge_speed_penalty"]).item()
            ),
            "Reward/stuck_penalty": float(torch.mean(self._last_reward_components["stuck_penalty"]).item()),
            "Reward/no_progress_penalty": float(torch.mean(self._last_reward_components["no_progress_penalty"]).item()),
            "Reward/airborne_spin_penalty": float(
                torch.mean(self._last_reward_components["airborne_spin_penalty"]).item()
            ),
            "Reward/hard_terrain_spin_penalty": float(
                torch.mean(self._last_reward_components["hard_terrain_spin_penalty"]).item()
            ),
            "Reward/action_soft_limit_penalty": float(
                torch.mean(self._last_reward_components["action_soft_limit_penalty"]).item()
            ),
            "Reward/step_up_front_posture_penalty": float(
                torch.mean(self._last_reward_components["step_up_front_posture_penalty"]).item()
            ),
            "Reward/step_up_module_progress_reward": float(
                torch.mean(self._last_reward_components["step_up_module_progress_reward"]).item()
            ),
            "Reward/quality_row_advance_reward": float(
                torch.mean(self._last_reward_components["quality_row_advance_reward"]).item()
            ),
            "Reward/recovery_reward": float(torch.mean(self._last_reward_components["recovery_reward"]).item()),
            "Reward/drop_anti_dive_penalty": float(
                torch.mean(self._last_reward_components["drop_anti_dive_penalty"]).item()
            ),
            "ProgressGate/ungated_progress_raw": float(
                torch.mean(self._last_reward_diagnostics["progress_ungated"]).item()
            ),
            "ProgressGate/positive_progress_raw": float(
                torch.mean(self._last_reward_diagnostics["progress_positive"]).item()
            ),
            "ProgressGate/negative_progress_raw": float(
                torch.mean(self._last_reward_diagnostics["progress_negative"]).item()
            ),
            "ProgressGate/longitudinal_gate": float(
                torch.mean(self._last_reward_diagnostics["progress_longitudinal_gate"]).item()
            ),
            "ProgressGate/slip_angle_gate": float(
                torch.mean(self._last_reward_diagnostics["progress_slip_angle_gate"]).item()
            ),
            "ProgressGate/pitch_gate": float(
                torch.mean(self._last_reward_diagnostics["progress_pitch_gate"]).item()
            ),
            "ProgressGate/combined_gate": float(torch.mean(self._last_reward_diagnostics["progress_gate"]).item()),
            "ProgressGate/multiplier": float(torch.mean(self._last_reward_diagnostics["progress_multiplier"]).item()),
            "ContactSupport/front_raw": float(
                torch.mean(self._last_reward_diagnostics["contact_support_front"]).item()
            ),
            "ContactSupport/mid_raw": float(
                torch.mean(self._last_reward_diagnostics["contact_support_mid"]).item()
            ),
            "ContactSupport/rear_raw": float(
                torch.mean(self._last_reward_diagnostics["contact_support_rear"]).item()
            ),
            "ContactSupport/score_raw": float(
                torch.mean(self._last_reward_diagnostics["contact_support_score"]).item()
            ),
            "ContactSupport/w_all": float(torch.mean(self._last_reward_diagnostics["contact_support_w_all"]).item()),
            "ContactSupport/w_up": float(torch.mean(self._last_reward_diagnostics["contact_support_w_up"]).item()),
            "ContactSupport/w_drop": float(torch.mean(self._last_reward_diagnostics["contact_support_w_drop"]).item()),
            "ContactSupport/lr_balance_raw": float(
                torch.mean(self._last_reward_diagnostics["contact_support_lr_balance"]).item()
            ),
            "Slip/masked_longitudinal_abs_mean_raw": float(
                torch.mean(self._last_reward_diagnostics["slip_masked_longitudinal"]).item()
            ),
            "Slip/masked_angle_abs_mean_raw": float(
                torch.mean(self._last_reward_diagnostics["slip_masked_angle"]).item()
            ),
            "Slip/contact_weight_sum_raw": float(
                torch.mean(self._last_reward_diagnostics["slip_contact_weight_sum"]).item()
            ),
            "EdgeSpeed/strength_raw": float(torch.mean(self._last_reward_diagnostics["edge_strength"]).item()),
            "EdgeSpeed/height_jump_m_raw": float(torch.mean(self._last_reward_diagnostics["edge_height_jump"]).item()),
            "EdgeSpeed/safe_speed_mps_raw": float(torch.mean(self._last_reward_diagnostics["edge_safe_speed"]).item()),
            "EdgeSpeed/forward_speed_mps_raw": float(
                torch.mean(self._last_reward_diagnostics["edge_forward_speed"]).item()
            ),
            "EdgeSpeed/excess_speed_mps_raw": float(
                torch.mean(self._last_reward_diagnostics["edge_speed_excess"]).item()
            ),
            "EdgeSpeed/g_step_up": float(torch.mean(self._last_reward_diagnostics["terrain_gate_step_up"]).item()),
            "EdgeSpeed/g_step_down": float(torch.mean(self._last_reward_diagnostics["terrain_gate_step_down"]).item()),
            "EdgeSpeed/g_gap": float(torch.mean(self._last_reward_diagnostics["terrain_gate_gap"]).item()),
            "EdgeSpeed/g_edge": float(torch.mean(self._last_reward_diagnostics["terrain_gate_edge"]).item()),
            "EdgeSpeed/v_safe": float(torch.mean(self._last_reward_diagnostics["terrain_speed_safe"]).item()),
            "EdgeSpeed/vx_cmd_raw": float(torch.mean(self._last_reward_diagnostics["terrain_speed_raw_vx"]).item()),
            "EdgeSpeed/vx_cmd_limited": float(
                torch.mean(self._last_reward_diagnostics["terrain_speed_limited_vx"]).item()
            ),
            "EdgeSpeed/vx_actual": float(torch.mean(self._last_reward_diagnostics["terrain_speed_actual_vx"]).item()),
            "EdgeSpeed/raw_excess": float(torch.mean(self._last_reward_diagnostics["terrain_speed_raw_excess"]).item()),
            "EdgeSpeed/actual_excess": float(
                torch.mean(self._last_reward_diagnostics["terrain_speed_actual_excess"]).item()
            ),
            "EdgeSpeed/speed_limit_active_rate": float(
                torch.mean(self._last_terrain_speed_limit_active.float()).item()
            ),
            "Stuck/stuck_time_mean": float(torch.mean(self._stage1_stuck_time).item()),
            "Stuck/stuck_now_rate": float(torch.mean(self._last_stage1_stuck_now.float()).item()),
            "Stuck/stuck_penalty_active_rate": float(
                torch.mean(self._last_reward_diagnostics["stuck_penalty_active"]).item()
            ),
            "Stuck/no_progress_active_rate": float(
                torch.mean(self._last_reward_diagnostics["no_progress_active"]).item()
            ),
            "Stuck/no_progress_deficit": float(
                torch.mean(self._last_reward_diagnostics["no_progress_deficit"]).item()
            ),
            "Stuck/no_progress_penalty_raw": float(
                torch.mean(self._last_reward_diagnostics["no_progress_penalty_raw"]).item()
            ),
            "Stuck/recovery_active_rate": float(torch.mean(self._stage1_recovery_active.float()).item()),
            "Stuck/recovery_reverse_rate": float(torch.mean(self._last_stage1_recovery_reverse_now.float()).item()),
            "Stuck/recovery_success_rate": float(torch.mean(self._last_stage1_recovery_success.float()).item()),
            "HardTerrainSpin/gate": float(torch.mean(self._last_reward_diagnostics["hard_terrain_spin_gate"]).item()),
            "HardTerrainSpin/low_speed": float(
                torch.mean(self._last_reward_diagnostics["hard_terrain_low_speed"]).item()
            ),
            "HardTerrainSpin/slip_excess": float(
                torch.mean(self._last_reward_diagnostics["hard_terrain_slip_excess"]).item()
            ),
            "HardTerrainSpin/penalty_raw": float(
                torch.mean(self._last_reward_diagnostics["hard_terrain_spin_penalty_raw"]).item()
            ),
            "HardTerrainSpin/wheel_spin_airborne_mean": float(
                torch.mean(self._last_reward_diagnostics["wheel_spin_airborne_mean"]).item()
            ),
            "Termination/stuck_timeout_rate": float(torch.mean(self._last_done_terms["stuck_timeout"].float()).item()),
            "Posture/front_pitch_ref": float(torch.mean(self._last_reward_diagnostics["front_pitch_ref"]).item()),
            "Posture/front_pitch_actual": float(
                torch.mean(self._last_reward_diagnostics["front_pitch_actual"]).item()
            ),
            "Posture/rear_pitch_actual": float(
                torch.mean(self._last_reward_diagnostics["rear_pitch_actual"]).item()
            ),
            "Posture/front_pitch_error": float(torch.mean(self._last_reward_diagnostics["front_pitch_error"]).item()),
            "Posture/step_up_distance_m": float(torch.mean(self._last_reward_diagnostics["step_up_distance_m"]).item()),
            "Posture/approach_mask_rate": float(
                torch.mean(self._last_reward_diagnostics["step_up_approach_mask"]).item()
            ),
            "Posture/step_up_posture_badness": float(
                torch.mean(self._last_reward_diagnostics["step_up_posture_badness"]).item()
            ),
            "Posture/progress_quality_multiplier": float(
                torch.mean(self._last_reward_diagnostics["step_up_progress_quality_multiplier"]).item()
            ),
            "Posture/progress_quality_score": float(
                torch.mean(self._last_reward_diagnostics["progress_quality_score"]).item()
            ),
            "Posture/module_support_phase_score": float(
                torch.mean(self._last_reward_diagnostics["module_support_phase_score"]).item()
            ),
            "Posture/front_module_height_progress": float(
                torch.mean(self._last_reward_diagnostics["front_module_height_progress"]).item()
            ),
            "Posture/middle_module_height_progress": float(
                torch.mean(self._last_reward_diagnostics["middle_module_height_progress"]).item()
            ),
            "Posture/rear_module_height_progress": float(
                torch.mean(self._last_reward_diagnostics["rear_module_height_progress"]).item()
            ),
            "Posture/quality_row_advance_rate": float(
                torch.mean(self._last_reward_diagnostics["quality_row_advance_mask"]).item()
            ),
            "Posture/hard_quality_advance_rate": float(
                torch.mean(self._last_reward_diagnostics["hard_quality_advance"]).item()
            ),
            "Posture/low_quality_hit_rate": float(torch.mean(self._last_done_terms["low_quality_terrain_hit"].float()).item()),
            "Posture/raw_hard_hit_rate": float(torch.mean(self._last_reward_diagnostics["raw_hard_hit"]).item()),
            "Posture/row_advance_without_quality_rate": float(
                torch.mean(self._last_reward_diagnostics["row_advance_without_quality"]).item()
            ),
            "Posture/quality_advance_score": float(
                torch.mean(self._last_reward_diagnostics["quality_advance_score"]).item()
            ),
            "Posture/front_climb_success_rate": float(
                torch.mean(self._last_reward_diagnostics["front_climb_success"]).item()
            ),
            "Posture/middle_climb_success_rate": float(
                torch.mean(self._last_reward_diagnostics["middle_climb_success"]).item()
            ),
            "Posture/rear_follow_success_rate": float(
                torch.mean(self._last_reward_diagnostics["rear_follow_success"]).item()
            ),
            "Posture/actual_overspeed_near_edge_rate": float(
                torch.mean(self._last_reward_diagnostics["actual_overspeed_near_edge_rate"]).item()
            ),
            "Posture/row_contact_support_min": float(
                torch.mean(self._last_reward_diagnostics["row_contact_support_min"]).item()
            ),
            "Posture/row_stuck_time_max": float(
                torch.mean(self._last_reward_diagnostics["row_stuck_time_max"]).item()
            ),
            "Posture/posture_penalty_raw": float(
                torch.mean(self._last_reward_diagnostics["step_up_front_posture_penalty_raw"]).item()
            ),
            "Posture/module_progress_reward_raw": float(
                torch.mean(self._last_reward_diagnostics["step_up_module_progress_reward_raw"]).item()
            ),
            "Drop/pitch_rate_abs_mean": float(torch.mean(self._last_reward_diagnostics["drop_pitch_rate_abs"]).item()),
            "Drop/vz_down_mean": float(torch.mean(self._last_reward_diagnostics["drop_vz_down"]).item()),
            "Drop/anti_dive_penalty_raw": float(
                torch.mean(self._last_reward_diagnostics["drop_anti_dive_penalty_raw"]).item()
            ),
            "Tracking/active_waypoint_pos_error": float(torch.mean(active_waypoint_pos_error).item()),
            "Tracking/active_waypoint_bearing_abs": float(torch.mean(active_waypoint_bearing_abs).item()),
            "Tracking/active_segment_completion_pct": float(torch.mean(active_segment_completion_pct).item()),
            "Tracking/active_waypoint_index_mean": float(torch.mean(self._active_waypoint_index.float()).item()),
            "Tracking/waypoints_completed_mean": float(torch.mean(self._episode_waypoints_completed.float()).item()),
            "Tracking/terrain_target_advances_mean": float(
                torch.mean(self._episode_terrain_target_advances.float()).item()
            ),
            "Tracking/episode_completion_pct": float(torch.mean(episode_completion_pct).item()),
            "Action/policy_abs_mean": float(torch.mean(torch.abs(self.actions)).item()),
            "Action/policy_std": float(self.actions.std(unbiased=False).item()),
            "Action/wheel_speed_reference_abs_mean_raw": float(
                torch.mean(torch.abs(self._last_wheel_speed_reference)).item()
            ),
            "Action/wheel_torque_target_abs_mean_raw": float(
                torch.mean(torch.abs(self._last_wheel_torque_targets)).item()
            ),
            "Action/desired_planar_command_abs_mean_raw": float(
                torch.mean(torch.abs(self._last_desired_planar_command)).item()
            ),
            "Action/raw_planar_command_abs_mean_raw": float(torch.mean(torch.abs(self._last_raw_planar_command)).item()),
            "Action/limited_planar_command_abs_mean_raw": float(
                torch.mean(torch.abs(self._last_limited_planar_command)).item()
            ),
            "Action/shaped_planar_command_abs_mean_raw": float(
                torch.mean(torch.abs(self._last_shaped_planar_command)).item()
            ),
            "Action/planar_command_shaping_delta_abs_mean_raw": float(
                torch.mean(torch.abs(planar_command_delta)).item()
            ),
            "Action/desired_planar_vx_raw": float(torch.mean(self._last_desired_planar_command[:, 0]).item()),
            "Action/raw_planar_vx_raw": float(torch.mean(self._last_raw_planar_command[:, 0]).item()),
            "Action/limited_planar_vx_raw": float(torch.mean(self._last_limited_planar_command[:, 0]).item()),
            "Action/desired_planar_wz_raw": float(torch.mean(self._last_desired_planar_command[:, 1]).item()),
            "Action/raw_planar_wz_raw": float(torch.mean(self._last_raw_planar_command[:, 1]).item()),
            "Action/limited_planar_wz_raw": float(torch.mean(self._last_limited_planar_command[:, 1]).item()),
            "Action/shaped_planar_vx_raw": float(torch.mean(self._last_shaped_planar_command[:, 0]).item()),
            "Action/shaped_planar_wz_raw": float(torch.mean(self._last_shaped_planar_command[:, 1]).item()),
            "Action/planar_command_delta_vx_raw": float(torch.mean(planar_command_delta[:, 0]).item()),
            "Action/planar_command_delta_wz_raw": float(torch.mean(planar_command_delta[:, 1]).item()),
            "Action/contact_weight_mean_raw": float(
                torch.mean(self._last_contact_weights).item()
            ),
            "Command/goal_rel_x": float(relative_goal_commands[command_env_id, 0].item()),
            "Command/goal_rel_y": float(relative_goal_commands[command_env_id, 1].item()),
            "Command/goal_rel_z": float(relative_goal_commands[command_env_id, 2].item()),
            "Command/goal_rel_heading": float(relative_goal_commands[command_env_id, 3].item()),
            "Command/goal_direction_offset_deg": float(
                torch.rad2deg(self._goal_direction_offsets[command_env_id]).item()
            ),
            "Command/goal_heading_offset_deg": float(torch.rad2deg(self._goal_heading_offsets[command_env_id]).item()),
            "Observation/base_lin_vel_y_raw": float(torch.mean(raw_obs_terms["base_lin_vel"][:, 1]).item()),
            "Observation/roll_deg": float(torch.mean(middle_roll_deg).item()),
            "Observation/pitch_deg": float(torch.mean(middle_pitch_deg).item()),
            "Observation/projected_gravity_xy_norm_raw": float(
                torch.mean(torch.linalg.vector_norm(raw_obs_terms["projected_gravity"][:, :2], dim=1)).item()
            ),
            "Observation/ball_joint_pos_abs_mean_raw": float(torch.mean(torch.abs(raw_obs_terms["ball_joint_pos"])).item()),
            "Observation/ball_joint_vel_abs_mean_raw": float(torch.mean(torch.abs(raw_obs_terms["ball_joint_vel"])).item()),
            "Observation/ball_joint_vel_limit_rate_raw": float(
                torch.mean(
                    (
                        torch.abs(raw_obs_terms["ball_joint_vel"])
                        >= 0.95 * abs(float(self.cfg.control.ball_joint_velocity_limit_sim))
                    ).float()
                ).item()
            ),
            "Observation/ball_joint_target_error_abs_mean_raw": float(
                torch.mean(torch.abs(raw_obs_terms["ball_joint_target_error"])).item()
            ),
            "Action/ball_joint_desired_delta_abs_mean_raw": float(
                torch.mean(self._last_ball_joint_desired_delta_abs_mean).item()
            ),
            "Action/ball_joint_desired_delta_l2_raw": float(
                torch.mean(self._last_ball_joint_desired_delta_l2).item()
            ),
            "Observation/wheel_joint_vel_abs_mean_raw": float(
                torch.mean(torch.abs(raw_obs_terms["wheel_joint_vel"])).item()
            ),
            "Observation/wheel_longitudinal_slip_abs_mean_raw": float(
                torch.mean(wheel_longitudinal_slip_abs).item()
            ),
            "Observation/wheel_slip_angle_abs_mean_raw": float(
                torch.mean(wheel_slip_angle_abs).item()
            ),
            "LowSlip/longitudinal_slip_pass_rate": float(
                torch.mean(low_longitudinal_slip_mask.float()).item()
            ),
            "LowSlip/slip_angle_pass_rate": float(
                torch.mean(low_slip_angle_mask.float()).item()
            ),
            "LowSlip/combined_pass_rate": float(
                torch.mean(low_slip_mask.float()).item()
            ),
            "LowSlip/longitudinal_slip_margin": float(
                torch.mean(self.cfg.rewards.params.low_slip_longitudinal_threshold - longitudinal_slip_abs_mean_per_env).item()
            ),
            "LowSlip/slip_angle_margin": float(
                torch.mean(self.cfg.rewards.params.low_slip_angle_threshold_rad - slip_angle_abs_mean_per_env).item()
            ),
            "Observation/wheel_normal_contact_force_sum_raw": float(
                torch.mean(torch.sum(raw_obs_terms["wheel_normal_contact_force"], dim=1)).item()
            ),
            "LowLevel/v_parallel_abs_mean_raw": float(torch.mean(torch.abs(self._last_wheel_v_parallel)).item()),
            "LowLevel/v_perp_abs_mean_raw": float(torch.mean(torch.abs(self._last_wheel_v_perp)).item()),
            "LowLevel/delta_v_abs_mean_raw": float(torch.mean(torch.abs(self._last_wheel_delta_v)).item()),
            "LowLevel/tau0_abs_mean_raw": float(torch.mean(torch.abs(self._last_wheel_tau0)).item()),
            "LowLevel/tau1_abs_mean_raw": float(torch.mean(torch.abs(self._last_wheel_tau1)).item()),
        }

        for name, value in self._last_terrain_feature_diagnostics.items():
            if name.startswith("g_"):
                metrics[f"TerrainGate/{name.removeprefix('g_')}"] = float(torch.mean(value).item())
            else:
                metrics[f"TerrainFeature/{name}"] = float(torch.mean(value).item())

        if (
            self._is_stage1()
            and self._terrain_runtime is not None
            and self._terrain_runtime.terrain_types is not None
            and self._terrain_runtime.terrain_levels is not None
        ):
            (
                tile_start_x,
                tile_origin_x,
                tile_end_x,
                root_x,
                target_x,
                forward_x_from_current_tile_start,
            ) = self._get_terrain_column_tile_x_values()
            metrics.update(
                compute_stage1_eval_metrics(
                    terrain_types=self._terrain_runtime.terrain_types,
                    terrain_levels=self._terrain_runtime.terrain_levels,
                    forward_x_from_current_tile_start=forward_x_from_current_tile_start,
                    rows_advanced=self._episode_terrain_target_advances.float(),
                    max_row_reached_mask=self._last_stage1_max_row_reached,
                    valid_target_masked=self._last_stage1_valid_target_masked,
                    tile_start_x=tile_start_x,
                    tile_origin_x=tile_origin_x,
                    tile_end_x=tile_end_x,
                    root_x=root_x,
                    target_x=target_x,
                    far_mask=self._last_done_terms["far_from_target"],
                    ball_joint_limit_mask=self._last_done_terms["ball_joint_out_of_bounds"],
                    timeout_mask=self._last_done_terms["time_out"],
                    base_lin_vel=raw_obs_terms["base_lin_vel"],
                    base_ang_vel=raw_obs_terms["base_ang_vel"],
                    wheel_longitudinal_slip=raw_obs_terms["wheel_longitudinal_slip"],
                    wheel_slip_angle=raw_obs_terms["wheel_slip_angle"],
                    wheel_normal_contact_force=raw_obs_terms["wheel_normal_contact_force"],
                    roll_deg=middle_roll_deg,
                    pitch_deg=middle_pitch_deg,
                    ball_joint_limit_usage=ball_joint_limit_usage,
                    actions=self.actions,
                    last_actions=self.last_actions,
                    active_waypoint_distance=active_waypoint_pos_error,
                    terrain_length=float(self._terrain_runtime._terrain_cfg.terrain_length),
                    train_active_mask=self._stage1_transition_train_mask,
                    stuck_time_s=self._stage1_stuck_time,
                    stuck_timeout_mask=self._last_done_terms["stuck_timeout"],
                    pitch_rate_abs=pitch_rate_abs,
                    vz_down=vz_down,
                    speed_limit_active_mask=self._last_terrain_speed_limit_active,
                    stuck_penalty_active_mask=self._last_reward_diagnostics["stuck_penalty_active"] > 0.5,
                    no_progress_active_mask=self._last_reward_diagnostics["no_progress_active"] > 0.5,
                    vx_cmd_raw=self._last_reward_diagnostics["terrain_speed_raw_vx"],
                    vx_cmd_limited=self._last_reward_diagnostics["terrain_speed_limited_vx"],
                    vx_actual=self._last_reward_diagnostics["terrain_speed_actual_vx"],
                    front_pitch_ref=self._last_reward_diagnostics["front_pitch_ref"],
                    front_pitch_actual=self._last_reward_diagnostics["front_pitch_actual"],
                    rear_pitch_actual=self._last_reward_diagnostics["rear_pitch_actual"],
                    wheel_spin_airborne_mean=self._last_reward_diagnostics["wheel_spin_airborne_mean"],
                    quality_row_advance_mask=self._last_reward_diagnostics["quality_row_advance_mask"] > 1.0e-6,
                    hard_quality_advance_mask=self._last_reward_diagnostics["hard_quality_advance"] > 0.5,
                    low_quality_hit_mask=self._last_done_terms["low_quality_terrain_hit"],
                    raw_hard_hit_mask=self._last_reward_diagnostics["raw_hard_hit"] > 0.5,
                    row_advance_without_quality_mask=self._last_reward_diagnostics["row_advance_without_quality"] > 0.5,
                    quality_advance_score=self._last_reward_diagnostics["quality_advance_score"],
                    phase_module_progress_score=self._last_reward_diagnostics["phase_module_progress_score"],
                    front_climb_success_mask=self._last_reward_diagnostics["front_climb_success"] > 0.5,
                    middle_climb_success_mask=self._last_reward_diagnostics["middle_climb_success"] > 0.5,
                    rear_follow_success_mask=self._last_reward_diagnostics["rear_follow_success"] > 0.5,
                    actual_overspeed_near_edge_mask=self._last_reward_diagnostics["actual_overspeed_near_edge_rate"] > 0.5,
                    row_contact_support_min=self._last_reward_diagnostics["row_contact_support_min"],
                    row_stuck_time_max=self._last_reward_diagnostics["row_stuck_time_max"],
                    recovery_active_mask=self._stage1_recovery_active,
                    recovery_reverse_mask=self._last_stage1_recovery_reverse_now,
                    recovery_success_mask=self._last_stage1_recovery_success,
                )
            )
            metrics["Stage1Eval/global/train_active_rate"] = float(
                torch.mean(self._stage1_training_active.float()).item()
            )
            metrics["Stage1Eval/global/train_retired_rate"] = float(
                torch.mean((~self._stage1_training_active).float()).item()
            )
            metrics["Stage1Eval/global/train_sample_rate"] = float(
                torch.mean(self._stage1_transition_train_mask.float()).item()
            )
            has_target_columns = self._stage1_column_completion_targets > 0
            unfinished_columns = (~self._stage1_completed_terrain_columns) & has_target_columns
            completed_columns = self._stage1_completed_terrain_columns & has_target_columns
            active_column_counts = mdp_curriculum.compute_terrain_column_counts(
                self._terrain_runtime.terrain_types[self._stage1_training_active],
                self._stage1_column_completion_counts.numel(),
            )
            completed_column_active_env_count = float(
                torch.sum(active_column_counts[completed_columns]).item()
                if torch.any(completed_columns)
                else 0.0
            )
            active_env_count = float(torch.sum(self._stage1_training_active).item())
            retention_target_rate = min(
                max(float(getattr(self.cfg.curriculum, "terrain_column_completed_retention_ratio", 0.0)), 0.0),
                1.0,
            )
            metrics["Stage1Eval/global/completed_column_rate"] = float(
                torch.mean(self._stage1_completed_terrain_columns[has_target_columns].float()).item()
                if torch.any(has_target_columns)
                else 1.0
            )
            metrics["Stage1Eval/global/unfinished_column_count"] = float(torch.sum(unfinished_columns).item())
            metrics["Stage1Eval/global/recycled_env_ever_rate"] = float(
                torch.mean(self._stage1_recycled_envs_ever.float()).item()
            )
            metrics["Stage1Eval/global/completed_column_retention_target_rate"] = retention_target_rate
            metrics["Stage1Eval/global/completed_column_active_env_count"] = completed_column_active_env_count
            metrics["Stage1Eval/global/completed_column_active_rate"] = completed_column_active_env_count / max(
                float(self.num_envs),
                1.0,
            )
            metrics["Stage1Eval/global/completed_column_active_ratio_of_active"] = (
                completed_column_active_env_count / max(active_env_count, 1.0)
            )
            metrics["Stage1Eval/global/active_envs_per_completed_column_mean"] = float(
                torch.mean(active_column_counts[completed_columns].float()).item()
                if torch.any(completed_columns)
                else 0.0
            )
            metrics["Stage1Eval/global/active_envs_per_unfinished_column_mean"] = float(
                torch.mean(active_column_counts[unfinished_columns].float()).item()
                if torch.any(unfinished_columns)
                else 0.0
            )
        self._add_stage1_debug_metrics(metrics)

        per_wheel_metric_sources = {
            "wheel_joint_vel": raw_obs_terms["wheel_joint_vel"],
            "wheel_speed_reference": self._last_wheel_speed_reference,
            "wheel_torque_target": self._last_wheel_torque_targets,
            "contact_weight": self._last_contact_weights,
            "normal_force": wheel_normal_force_n,
            "v_parallel": self._last_wheel_v_parallel,
            "v_perp": self._last_wheel_v_perp,
            "delta_v": self._last_wheel_delta_v,
            "tau0": self._last_wheel_tau0,
            "tau1": self._last_wheel_tau1,
            "longitudinal_slip": raw_obs_terms["wheel_longitudinal_slip"],
            "slip_angle": raw_obs_terms["wheel_slip_angle"],
        }
        if self._is_stage1():
            stage1_per_wheel_fields = {
                "normal_force",
                "longitudinal_slip",
                "slip_angle",
                "v_parallel",
                "v_perp",
                "wheel_torque_target",
                "wheel_speed_reference",
            }
            per_wheel_metric_sources = {
                key: value for key, value in per_wheel_metric_sources.items() if key in stage1_per_wheel_fields
            }
        if self._should_collect_per_wheel_metrics():
            for wheel_index, wheel_name in enumerate(WHEEL_JOINT_NAMES):
                wheel_log_name = wheel_name.removesuffix("_joint")
                for metric_name, values in per_wheel_metric_sources.items():
                    metrics[f"PerWheel/{wheel_log_name}/{metric_name}"] = float(
                        torch.mean(values[:, wheel_index]).item()
                    )
        for joint_index, joint_name in enumerate(BALL_JOINT_NAMES):
            metrics[f"Observation/{joint_name}_pos_raw"] = float(torch.mean(ball_joint_pos[:, joint_index]).item())
            metrics[f"Observation/{joint_name}_target_error_raw"] = float(
                torch.mean(raw_obs_terms["ball_joint_target_error"][:, joint_index]).item()
            )
            metrics[f"Action/{joint_name}_policy_raw"] = float(
                torch.mean(self.actions[:, 2 + joint_index]).item()
            )
            metrics[f"Action/{joint_name}_desired_target_raw"] = float(
                torch.mean(self._last_ball_joint_desired_targets[:, joint_index]).item()
            )
            metrics[f"Action/{joint_name}_rate_target_raw"] = float(
                torch.mean(self._last_ball_joint_rate_targets[:, joint_index]).item()
            )
            metrics[f"Action/{joint_name}_position_target_raw"] = float(
                torch.mean(self._joint_pos_targets[:, self._ball_joint_ids[joint_index]]).item()
            )
            metrics[f"Debug/Stage1/BallJoint/{joint_name}/policy_action"] = float(
                torch.mean(self.actions[:, 2 + joint_index]).item()
            )
            metrics[f"Debug/Stage1/BallJoint/{joint_name}/desired_target"] = float(
                torch.mean(self._last_ball_joint_desired_targets[:, joint_index]).item()
            )
            metrics[f"Debug/Stage1/BallJoint/{joint_name}/rate_target"] = float(
                torch.mean(self._last_ball_joint_rate_targets[:, joint_index]).item()
            )
            metrics[f"Debug/Stage1/BallJoint/{joint_name}/position_target"] = float(
                torch.mean(self._joint_pos_targets[:, self._ball_joint_ids[joint_index]]).item()
            )
            metrics[f"Debug/Stage1/BallJoint/{joint_name}/actual_pos"] = float(
                torch.mean(ball_joint_pos[:, joint_index]).item()
            )
            metrics[f"Debug/Stage1/BallJoint/{joint_name}/target_error"] = float(
                torch.mean(raw_obs_terms["ball_joint_target_error"][:, joint_index]).item()
            )
            metrics[f"Observation/{joint_name}_limit_usage_mean_raw"] = float(
                torch.mean(ball_joint_limit_usage[:, joint_index]).item()
            )
            metrics[f"Observation/{joint_name}_limit_usage_max_raw"] = float(
                torch.max(ball_joint_limit_usage[:, joint_index]).item()
            )
        if (
            self._uses_stage1_train_retirement()
            and self._terrain_runtime is not None
            and self._terrain_runtime.generator_enabled
            and self._terrain_runtime.terrain_levels is not None
        ):
            (
                tile_start_x,
                tile_origin_x,
                tile_end_x,
                root_x,
                target_x,
                forward_x_from_current_tile_start,
            ) = self._get_terrain_column_tile_x_values()
            forward_x_from_current_tile_origin = root_x - tile_origin_x
            metrics["Terrain/current_level_mean"] = float(torch.mean(self._terrain_runtime.terrain_levels.float()).item())
            metrics["Terrain/tile_start_x_mean"] = float(torch.mean(tile_start_x).item())
            metrics["Terrain/tile_origin_x_mean"] = float(torch.mean(tile_origin_x).item())
            metrics["Terrain/tile_end_x_mean"] = float(torch.mean(tile_end_x).item())
            metrics["Terrain/root_x_mean"] = float(torch.mean(root_x).item())
            metrics["Terrain/target_x_mean"] = float(torch.mean(target_x).item())
            metrics["Terrain/forward_x_from_current_tile_start_mean"] = float(
                torch.mean(forward_x_from_current_tile_start).item()
            )
            metrics["Terrain/forward_x_from_current_tile_origin_mean"] = float(
                torch.mean(forward_x_from_current_tile_origin).item()
            )
            metrics["Terrain/active_goal_start_distance_mean"] = float(
                torch.mean(self._active_goal_start_distance).item()
            )
            metrics["Terrain/active_goal_progress_mean"] = float(
                torch.mean(
                    self._compute_active_goal_progress(
                        torch.arange(self.num_envs, device=self.device),
                    )
                ).item()
            )
        return self._sanitize_scalar_metrics(metrics)

    def _reset_idx(self, env_ids: Sequence[int] | None):
        if env_ids is None:
            env_ids = self.robot._ALL_INDICES
        env_ids = torch.as_tensor(env_ids, device=self.device, dtype=torch.long)
        if env_ids.numel() == 0:
            return

        terrain_metrics = None
        if self._terrain_runtime is not None:
            self.commands.copy_(self._compute_relative_goal_commands())
            if not self.cfg.commands.use_terrain_column_targets:
                terrain_metrics = mdp_curriculum.update_terrain_curriculum(
                    self.cfg.curriculum,
                    self._terrain_runtime,
                    self.scene,
                    self.robot,
                    env_ids,
                    self.commands,
                    self.cfg.episode_length_s,
                )
        self.extras["log"] = self._collect_episode_logs(env_ids, terrain_metrics)
        super()._reset_idx(env_ids)
        stage1_reset_metrics = self._apply_stage1_terrain_column_reset_curriculum(env_ids)
        if stage1_reset_metrics is not None:
            self.extras["log"].update(stage1_reset_metrics)

        if self._sensor_runtime is not None:
            self._sensor_runtime.reset(env_ids)

        root_state = mdp_resets.build_root_state(
            self.cfg, self.robot, self.scene, self._terrain_runtime, env_ids, self.device
        )
        joint_pos, joint_vel = mdp_resets.build_joint_state(
            self.cfg, self.robot, self._ball_joint_ids, self._wheel_joint_ids, env_ids, self.device
        )

        self.robot.write_root_pose_to_sim(root_state[:, :7], env_ids)
        self.robot.write_root_velocity_to_sim(root_state[:, 7:], env_ids)
        self.robot.write_joint_state_to_sim(joint_pos, joint_vel, None, env_ids)

        reset_pos_xy_w = root_state[:, :2]
        reset_yaw_w = quaternion_to_rpy(root_state[:, 3:7])[:, 2]
        self._active_waypoint_index[env_ids] = 0
        self._episode_waypoints_completed[env_ids] = 0
        self._episode_terrain_target_advances[env_ids] = 0
        if self._uses_stage1_train_retirement():
            active_reset_mask = self._stage1_training_active[env_ids]
        else:
            active_reset_mask = torch.ones(env_ids.numel(), dtype=torch.bool, device=self.device)
        active_env_ids = env_ids[active_reset_mask]
        if active_env_ids.numel() > 0:
            self._sample_waypoint_queue(
                active_env_ids,
                reset_pos_xy_w[active_reset_mask],
                reset_yaw_w[active_reset_mask],
            )
        retired_reset_mask = ~active_reset_mask
        retired_env_ids = env_ids[retired_reset_mask]
        if retired_env_ids.numel() > 0:
            parked_targets = torch.zeros(
                (retired_env_ids.numel(), self.cfg.commands.num_commands),
                device=self.device,
                dtype=self.command_targets_w.dtype,
            )
            parked_targets[:, :2] = reset_pos_xy_w[retired_reset_mask]
            if self.cfg.commands.num_commands > 2:
                parked_targets[:, 2] = root_state[retired_reset_mask, 2]
            if self.cfg.commands.num_commands > 3:
                parked_targets[:, 3] = reset_yaw_w[retired_reset_mask]
            self._waypoint_targets_w[retired_env_ids] = parked_targets.unsqueeze(1).expand(
                -1,
                self._num_waypoints_per_episode,
                -1,
            )
            self._waypoint_direction_offsets[retired_env_ids] = 0.0
            self._waypoint_heading_offsets[retired_env_ids] = 0.0
            self._goal_direction_offsets[retired_env_ids] = 0.0
            self._goal_heading_offsets[retired_env_ids] = 0.0
            self._command_time_left[retired_env_ids] = 0.0
            self.command_targets_w[retired_env_ids] = parked_targets
            self._active_goal_start_distance[retired_env_ids] = 1.0e-6
        self.commands[env_ids] = mdp_commands.compute_relative_goal_commands(
            self.command_targets_w[env_ids],
            reset_pos_xy_w,
            reset_yaw_w,
            root_state[:, 2],
        )
        self._previous_goal_distance[env_ids] = torch.linalg.vector_norm(self.commands[env_ids, :2], dim=1)
        self._last_active_waypoint_pos_error[env_ids] = self._previous_goal_distance[env_ids]
        self._last_active_waypoint_bearing_abs[env_ids] = torch.abs(self.commands[env_ids, 3])

        self.actions[env_ids] = 0.0
        self.last_actions[env_ids] = 0.0
        self._joint_pos_targets[env_ids] = joint_pos
        self._joint_effort_targets[env_ids] = 0.0
        self._last_ball_joint_desired_targets[env_ids] = joint_pos[:, self._ball_joint_ids]
        self._last_ball_joint_desired_delta_abs_mean[env_ids] = 0.0
        self._last_ball_joint_desired_delta_l2[env_ids] = 0.0
        self._last_ball_joint_rate_targets[env_ids] = 0.0
        self._ball_joint_qdot_alloc[env_ids] = 0.0
        self._last_wheel_speed_reference[env_ids] = 0.0
        self._last_wheel_torque_targets[env_ids] = 0.0
        self._last_raw_planar_command[env_ids] = 0.0
        self._last_limited_planar_command[env_ids] = 0.0
        self._last_terrain_speed_safe[env_ids] = float(self.cfg.control.base_forward_velocity_max)
        self._last_terrain_speed_limit_active[env_ids] = False
        self._last_desired_planar_command[env_ids] = 0.0
        self._last_shaped_planar_command[env_ids] = 0.0
        self._last_contact_weights[env_ids] = 0.0
        self._last_wheel_v_parallel[env_ids] = 0.0
        self._last_wheel_v_perp[env_ids] = 0.0
        self._last_wheel_delta_v[env_ids] = 0.0
        self._last_wheel_tau0[env_ids] = 0.0
        self._last_wheel_tau1[env_ids] = 0.0
        self._stage1_stuck_time[env_ids] = 0.0
        self._last_stage1_stuck_now[env_ids] = False
        self._prev_stage1_module_support_heights[env_ids] = 0.0
        self._reset_stage1_quality_advance_state(env_ids)
        self._stage1_recovery_active[env_ids] = False
        self._stage1_recovery_reverse_time_s[env_ids] = 0.0
        self._stage1_recovery_start_goal_distance[env_ids] = self._previous_goal_distance[env_ids]
        self._last_stage1_recovery_reverse_now[env_ids] = False
        self._last_stage1_recovery_success[env_ids] = False
        for key in self._last_done_terms:
            self._last_done_terms[key][env_ids] = False

        if self._obs_history is not None:
            self._obs_history[env_ids] = 0.0
        for name in REWARD_TERM_NAMES:
            self._episode_sums[name][env_ids] = 0.0
        self._episode_total_reward_sum[env_ids] = 0.0
        self._cached_step_relative_goal_commands = None
        self._cached_step_raw_obs_terms = None
        self._clear_wheel_contact_force_cache()
        if self._terrain_runtime is not None:
            self._terrain_runtime.curriculum_ready = True

        self._debug_draw.draw_reset_points(env_ids=env_ids, env_origins=self.scene.env_origins[env_ids])
        self._debug_draw.draw_goal_pose(
            goal_positions_w=self.command_targets_w[:, :3],
            goal_headings_w=self.command_targets_w[:, 3],
        )
        if self.cfg.debug.create_follow_views:
            self._update_follow_views(root_positions_w=root_state[:, :3], root_yaws_w=reset_yaw_w, env_ids=env_ids)

    def _update_follow_views(
        self,
        root_positions_w: torch.Tensor | None = None,
        root_yaws_w: torch.Tensor | None = None,
        env_ids: torch.Tensor | None = None,
    ) -> None:
        if root_positions_w is None:
            root_positions_w = self.robot.data.root_link_pos_w
        elif env_ids is not None and root_positions_w.shape[0] != self.num_envs:
            full_root_positions_w = self.robot.data.root_link_pos_w.clone()
            full_root_positions_w[env_ids] = root_positions_w
            root_positions_w = full_root_positions_w

        if root_yaws_w is None:
            root_yaws_w = quaternion_to_rpy(self.robot.data.root_link_quat_w)[:, 2]
        elif env_ids is not None and root_yaws_w.shape[0] != self.num_envs:
            full_root_yaws_w = quaternion_to_rpy(self.robot.data.root_link_quat_w)[:, 2]
            full_root_yaws_w[env_ids] = root_yaws_w
            root_yaws_w = full_root_yaws_w

        self._debug_draw.update_follow_views(
            self.sim,
            root_positions_w,
            root_yaws_w,
            top_height=self.cfg.debug.follow_view_top_height,
            chase_env_index=self.cfg.debug.follow_view_chase_env_index,
            chase_env_indices=self.cfg.debug.follow_view_chase_env_indices,
            chase_offset_b=self.cfg.debug.follow_view_chase_offset_b,
            chase_target_offset_b=self.cfg.debug.follow_view_chase_target_offset_b,
            forward_height_m=self.cfg.debug.follow_view_forward_height_m,
            forward_distance_m=self.cfg.debug.follow_view_forward_distance_m,
            right_side_distance_m=self.cfg.debug.follow_view_right_side_distance_m,
        )


__all__ = ["CompleteCarDirectEnv"]
