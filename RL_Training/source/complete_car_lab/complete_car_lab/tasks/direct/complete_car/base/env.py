"""Complete-car direct workflow 环境主类。"""

from __future__ import annotations

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
from ..mdp.rewards import REWARD_TERM_NAMES, compute_reward_terms
from ..mdp.stage1_eval import compute_stage1_eval_metrics
from ..mdp.terminations import compute_done_terms
from ..sensors.sensor_cfg import CompleteCarSensorSuiteRuntime
from ..terrain.terrain_runtime import CompleteCarTerrainRuntime
from ..utils.debug_draw import CompleteCarDebugDraw
from ..utils.math_utils import quat_rotate, quaternion_to_rpy, update_history
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
            visualize_goal_heading=cfg.debug.visualize_goal_heading,
            height_patch_marker_radius=cfg.debug.height_patch_marker_radius,
        )
        super().__init__(cfg, render_mode, **kwargs)

        self._ball_joint_ids, _ = self.robot.find_joints(BALL_JOINT_NAMES)
        self._wheel_joint_ids, _ = self.robot.find_joints(WHEEL_JOINT_NAMES)
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
        self._previous_goal_distance = torch.zeros(self.num_envs, device=self.device)
        self._active_goal_start_distance = torch.ones(self.num_envs, device=self.device)

        self._joint_pos_targets = self.robot.data.default_joint_pos.clone()
        self._joint_effort_targets = torch.zeros_like(self.robot.data.default_joint_vel)
        self._last_ball_joint_desired_targets = torch.zeros((self.num_envs, len(BALL_JOINT_NAMES)), device=self.device)
        self._last_ball_joint_rate_targets = torch.zeros_like(self._last_ball_joint_desired_targets)
        self._last_wheel_speed_reference = torch.zeros((self.num_envs, len(WHEEL_JOINT_NAMES)), device=self.device)
        self._last_wheel_torque_targets = torch.zeros_like(self._last_wheel_speed_reference)
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
            "edge_strength": torch.zeros(self.num_envs, device=self.device),
            "edge_height_jump": torch.zeros(self.num_envs, device=self.device),
            "edge_safe_speed": torch.zeros(self.num_envs, device=self.device),
            "edge_forward_speed": torch.zeros(self.num_envs, device=self.device),
            "edge_speed_excess": torch.zeros(self.num_envs, device=self.device),
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
            "terrain_column_completed": torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
        }
        self._last_critic_height_patch: torch.Tensor | None = None
        self._cached_step_raw_obs_terms: dict[str, torch.Tensor] | None = None
        self._cached_step_relative_goal_commands: torch.Tensor | None = None

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
        extras["metrics"] = self._collect_step_metrics()
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

    # 执行动作预处理，刷新目标，运输动作输出到关节目标
    def _pre_physics_step(self, actions: torch.Tensor) -> None:
        self.last_actions.copy_(self.actions)
        self.actions.copy_(torch.nan_to_num(actions, nan=0.0, posinf=1.0, neginf=-1.0))

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

        if self._sensor_runtime is not None:
            wheel_contact_forces_w = self._sensor_runtime.get_wheel_contact_forces_w(WHEEL_BODY_NAMES)
        else:
            wheel_contact_forces_w = torch.zeros(
                (self.num_envs, len(self._wheel_body_ids), 3),
                device=self.device,
                dtype=self.robot.data.root_link_pos_w.dtype,
            )
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
        self._last_ball_joint_desired_targets.copy_(desired_ball_joint_targets)

        planar_command = mdp_actions.map_base_actions_to_planar_command(
            planar_actions,
            self.cfg.control.base_forward_velocity_max,
            self.cfg.control.base_yaw_rate_max,
            allow_reverse=self.cfg.control.base_allow_reverse,
        )
        ball_joint_pos = self.robot.data.joint_pos[:, self._ball_joint_ids]
        wheel_joint_vel = self.robot.data.joint_vel[:, self._wheel_joint_ids]
        low_level_outputs = self._wheel_speed_allocator.compute_low_slip_control_targets(
            ball_joint_pos=ball_joint_pos,
            desired_ball_joint_pos=desired_ball_joint_targets,
            desired_planar_command=planar_command,
            wheel_normal_contact_force=wheel_normal_contact_force,
            wheel_joint_vel=wheel_joint_vel,
            rolling_speed_actual=rolling_speed_actual,
            lateral_speed_actual=lateral_speed_actual,
            control_dt=self.cfg.control.control_dt,
            planner_gains=self.cfg.control.ball_joint_planner_gains,
            planner_qdot_limits=self.cfg.control.ball_joint_planner_qdot_limits,
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
            self._terrain_runtime is None
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
        )
        progress_hit = waypoint_hit & ~blocked
        advance_mask = progress_hit & can_advance
        max_row_reached_mask = progress_hit & reaches_max_row
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
        self._cached_step_relative_goal_commands = None
        self._cached_step_raw_obs_terms = None

    def _advance_active_waypoints(self, env_ids: torch.Tensor) -> None:
        if env_ids.numel() == 0:
            return
        self._active_waypoint_index[env_ids] += 1
        self._sync_active_waypoint_targets(env_ids)
        self._set_active_goal_start_distance(env_ids, self.robot.data.root_link_pos_w[env_ids, :2])


    def _get_observations(self) -> dict:
        if self._sensor_runtime is not None:
            wheel_contact_forces_w = self._sensor_runtime.get_wheel_contact_forces_w(WHEEL_BODY_NAMES)
        else:
            wheel_contact_forces_w = torch.zeros(
                (self.num_envs, len(self._wheel_body_ids), 3),
                device=self.device,
                dtype=self.robot.data.root_link_pos_w.dtype,
            )

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
        terrain_height_patch = self._compute_critic_height_patch()
        self._last_critic_height_patch = terrain_height_patch
        current_actor_obs = compute_actor_observation_from_raw_terms(self.cfg, raw_obs_terms, terrain_height_patch)
        actor_obs = update_history(self._obs_history, current_actor_obs)
        critic_obs = compute_critic_observation(actor_obs)
        if self._sensor_runtime is not None and self.cfg.debug.log_sensor_outputs:
            self.extras["sensors"] = self._sensor_runtime.get_raw_output()
        return {"actor": actor_obs, "critic": critic_obs}

    def _compute_critic_height_patch(self) -> torch.Tensor | None:
        if not self.cfg.terrain.measure_heights or self._terrain_runtime is None:
            return None

        local_points = self._critic_height_patch_local.unsqueeze(0).expand(self.num_envs, -1, -1)

        root_pos_w = self.robot.data.root_link_pos_w
        yaw = quaternion_to_rpy(self.robot.data.root_link_quat_w)[:, 2]

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
        self._debug_draw.draw_height_patch(
            patch_points_w,
            height_offset=float(self.cfg.debug.height_patch_marker_height_offset),
            color_range_m=float(self.cfg.debug.height_patch_color_range_m),
        )

    def _compute_edge_preview(self) -> tuple[torch.Tensor, torch.Tensor]:
        zeros = torch.zeros(self.num_envs, device=self.device, dtype=self.robot.data.root_link_pos_w.dtype)
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
        if self._sensor_runtime is not None:
            wheel_contact_forces_w = self._sensor_runtime.get_wheel_contact_forces_w(WHEEL_BODY_NAMES)
        else:
            wheel_contact_forces_w = torch.zeros(
                (self.num_envs, len(self._wheel_body_ids), 3),
                device=self.device,
                dtype=self.robot.data.root_link_pos_w.dtype,
            )
        wheel_normal_contact_force = torch.linalg.vector_norm(wheel_contact_forces_w, dim=-1) / self._total_vehicle_weight
        wheel_contact_weights = self._wheel_speed_allocator.compute_contact_weights(
            wheel_normal_contact_force,
            self.cfg.control.contact_force_off_threshold,
            self.cfg.control.contact_force_on_threshold,
        )
        edge_strength, edge_height_jump = self._compute_edge_preview()
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
            self._last_done_terms["waypoint_hit"],
        )
        self._previous_goal_distance.copy_(torch.linalg.vector_norm(relative_goal_commands[:, :2], dim=1))
        for name, value in components.items():
            self._episode_sums[name] += value
            self._last_reward_components[name].copy_(value)
        for name, value in diagnostics.items():
            self._last_reward_diagnostics[name].copy_(value)

        self._episode_total_reward_sum += total_reward
        self._last_total_reward.copy_(total_reward)
        if self.cfg.commands.use_terrain_column_targets:
            advance_env_ids = self._get_terrain_column_progress_advance_env_ids(relative_goal_commands)
            if advance_env_ids.numel() > 0:
                self._advance_terrain_column_targets(advance_env_ids)
            return total_reward

        advance_env_ids = torch.nonzero(
            self._last_done_terms["waypoint_hit"]
            & ~self._last_done_terms["is_success"]
            & ~self._last_done_terms["far_from_target"]
            & ~self._last_done_terms["ball_joint_out_of_bounds"]
            & ~self._last_done_terms["time_out"],
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
            if torch.any(max_row_reached_mask):
                done_terms["terrain_column_completed"] = max_row_reached_mask
                done_terms["time_out"] = done_terms["time_out"] | max_row_reached_mask
                self._episode_terrain_target_advances[max_row_reached_mask] += 1
                self._last_stage1_max_row_reached.copy_(max_row_reached_mask)
        waypoint_hit_env_ids = torch.nonzero(done_terms["waypoint_hit"], as_tuple=False).flatten()
        if waypoint_hit_env_ids.numel() > 0:
            self._episode_waypoints_completed[waypoint_hit_env_ids] += 1
        for key, value in done_terms.items():
            self._last_done_terms[key].copy_(value)
        terminated = (
            done_terms["is_success"]
            | done_terms["far_from_target"]
            | done_terms["ball_joint_out_of_bounds"]
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
        )
        extras["Termination/terminated_rate"] = float(torch.mean(terminated.float()).item())
        extras["Termination/success_rate"] = float(torch.mean(self._last_done_terms["is_success"][env_ids].float()).item())
        extras["Termination/time_out_rate"] = float(torch.mean(self._last_done_terms["time_out"][env_ids].float()).item())
        extras["Termination/terrain_column_completed_rate"] = float(
            torch.mean(self._last_done_terms["terrain_column_completed"][env_ids].float()).item()
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

        levels = self._terrain_runtime.terrain_levels[env_ids]
        max_target_level = max(int(self._terrain_runtime.max_terrain_level) - 1, 0)
        completed = self._last_done_terms["terrain_column_completed"][env_ids]
        max_level_without_valid_next_target = levels >= max_target_level
        reset_to_low = completed | max_level_without_valid_next_target
        row_progress = self._compute_active_goal_progress(env_ids)
        row_failed = (
            (
                self._last_done_terms["far_from_target"][env_ids]
                | self._last_done_terms["ball_joint_out_of_bounds"][env_ids]
                | self._last_done_terms["time_out"][env_ids]
            )
            & ~self._last_done_terms["waypoint_hit"][env_ids]
            & ~reset_to_low
        )
        move_down_threshold = float(getattr(self.cfg.curriculum, "terrain_column_move_down_progress_ratio", 0.30))
        move_down = row_failed & (row_progress < move_down_threshold) & (levels > 0)

        if torch.any(reset_to_low):
            reset_low_env_ids = env_ids[reset_to_low]
            self._terrain_runtime.terrain_levels[reset_low_env_ids] = mdp_curriculum.sample_initial_terrain_levels(
                self.cfg.curriculum,
                self._terrain_runtime,
                self._terrain_runtime.terrain_types[reset_low_env_ids],
            )
        if torch.any(move_down):
            move_down_env_ids = env_ids[move_down]
            self._terrain_runtime.terrain_levels[move_down_env_ids] = torch.clamp(
                self._terrain_runtime.terrain_levels[move_down_env_ids] - 1,
                min=0,
            )

        self._terrain_runtime.sync_env_origins(self.scene, env_ids)
        return self._sanitize_scalar_metrics(
            {
                "terrain/row_progress_at_reset": row_progress,
                "terrain/move_down_ratio": move_down.float(),
                "terrain/reset_to_low_ratio": reset_to_low.float(),
                "terrain/level_after_reset": self._terrain_runtime.terrain_levels[env_ids].float(),
            }
        )

    def _collect_step_metrics(self) -> dict[str, float]:
        relative_goal_commands = self._cached_step_relative_goal_commands
        raw_obs_terms = self._cached_step_raw_obs_terms
        if relative_goal_commands is None or raw_obs_terms is None:
            relative_goal_commands = self._compute_relative_goal_commands()
            if self._sensor_runtime is not None:
                wheel_contact_forces_w = self._sensor_runtime.get_wheel_contact_forces_w(WHEEL_BODY_NAMES)
            else:
                wheel_contact_forces_w = torch.zeros(
                    (self.num_envs, len(self._wheel_body_ids), 3),
                    device=self.device,
                    dtype=self.robot.data.root_link_pos_w.dtype,
                )
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
        if self._sensor_runtime is not None:
            wheel_contact_forces_w_for_metrics = self._sensor_runtime.get_wheel_contact_forces_w(WHEEL_BODY_NAMES)
        else:
            wheel_contact_forces_w_for_metrics = torch.zeros(
                (self.num_envs, len(self._wheel_body_ids), 3),
                device=self.device,
                dtype=self.robot.data.root_link_pos_w.dtype,
            )
        wheel_normal_force_n = torch.linalg.vector_norm(wheel_contact_forces_w_for_metrics, dim=-1)
        middle_rpy = quaternion_to_rpy(self.robot.data.root_link_quat_w)
        middle_roll_deg = torch.rad2deg(middle_rpy[:, 0])
        middle_pitch_deg = torch.rad2deg(middle_rpy[:, 1])
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
            "Reward/turn_speed_penalty": float(torch.mean(self._last_reward_components["turn_speed_penalty"]).item()),
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
            "Action/shaped_planar_command_abs_mean_raw": float(
                torch.mean(torch.abs(self._last_shaped_planar_command)).item()
            ),
            "Action/planar_command_shaping_delta_abs_mean_raw": float(
                torch.mean(torch.abs(planar_command_delta)).item()
            ),
            "Action/desired_planar_vx_raw": float(torch.mean(self._last_desired_planar_command[:, 0]).item()),
            "Action/desired_planar_wz_raw": float(torch.mean(self._last_desired_planar_command[:, 1]).item()),
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
            "Observation/ball_joint_target_error_abs_mean_raw": float(
                torch.mean(torch.abs(raw_obs_terms["ball_joint_target_error"])).item()
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
                )
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
            metrics[f"Observation/{joint_name}_limit_usage_mean_raw"] = float(
                torch.mean(ball_joint_limit_usage[:, joint_index]).item()
            )
            metrics[f"Observation/{joint_name}_limit_usage_max_raw"] = float(
                torch.max(ball_joint_limit_usage[:, joint_index]).item()
            )
        if self._terrain_runtime is not None and self._terrain_runtime.terrain_levels is not None:
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
        self._sample_waypoint_queue(
            env_ids,
            reset_pos_xy_w,
            reset_yaw_w,
        )
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
        self._last_ball_joint_rate_targets[env_ids] = 0.0
        self._last_wheel_speed_reference[env_ids] = 0.0
        self._last_wheel_torque_targets[env_ids] = 0.0
        self._last_desired_planar_command[env_ids] = 0.0
        self._last_shaped_planar_command[env_ids] = 0.0
        self._last_contact_weights[env_ids] = 0.0
        self._last_wheel_v_parallel[env_ids] = 0.0
        self._last_wheel_v_perp[env_ids] = 0.0
        self._last_wheel_delta_v[env_ids] = 0.0
        self._last_wheel_tau0[env_ids] = 0.0
        self._last_wheel_tau1[env_ids] = 0.0
        for key in self._last_done_terms:
            self._last_done_terms[key][env_ids] = False

        if self._obs_history is not None:
            self._obs_history[env_ids] = 0.0
        for name in REWARD_TERM_NAMES:
            self._episode_sums[name][env_ids] = 0.0
        self._episode_total_reward_sum[env_ids] = 0.0
        self._cached_step_relative_goal_commands = None
        self._cached_step_raw_obs_terms = None
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
        )


__all__ = ["CompleteCarDirectEnv"]
