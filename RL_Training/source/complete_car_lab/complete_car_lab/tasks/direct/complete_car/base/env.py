"""Complete-car direct workflow 环境主类。"""

from __future__ import annotations

from collections.abc import Sequence

import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation
from isaaclab.envs import DirectRLEnv
from isaaclab.sim.spawners.from_files import GroundPlaneCfg, spawn_ground_plane

from ..assets.robot_cfg import BALL_JOINT_NAMES, WHEEL_JOINT_NAMES
from ..kinematics.wheel_speed_allocator import TorchWheelSpeedAllocator
from ..mdp import actions as mdp_actions
from ..mdp import commands as mdp_commands
from ..mdp import curriculum as mdp_curriculum
from ..mdp import randomization as mdp_randomization
from ..mdp import resets as mdp_resets
from ..mdp.observations import compute_actor_observation, compute_critic_observation
from ..mdp.rewards import REWARD_TERM_NAMES, compute_reward_terms
from ..mdp.terminations import compute_done_terms
from ..sensors.sensor_cfg import CompleteCarSensorSuiteRuntime
from ..terrain.terrain_runtime import CompleteCarTerrainRuntime
from ..utils.debug_draw import CompleteCarDebugDraw
from ..utils.math_utils import quaternion_to_rpy, update_history, wrap_to_pi_tensor
from .complete_car_cfg import CompleteCarEnvCfg


class CompleteCarDirectEnv(DirectRLEnv):
    """三个 Stage 共享的 direct 环境主类。"""

    cfg: CompleteCarEnvCfg

    def __init__(self, cfg: CompleteCarEnvCfg, render_mode: str | None = None, **kwargs):
        self._terrain_runtime: CompleteCarTerrainRuntime | None = None
        self._sensor_runtime: CompleteCarSensorSuiteRuntime | None = None
        self._debug_draw = CompleteCarDebugDraw(cfg.debug.enable_debug_draw)
        super().__init__(cfg, render_mode, **kwargs)

        self._wheel_speed_allocator = TorchWheelSpeedAllocator(device=self.device, dtype=self.robot.data.joint_pos.dtype)
        self._ball_joint_ids, _ = self.robot.find_joints(BALL_JOINT_NAMES)
        self._wheel_joint_ids, _ = self.robot.find_joints(WHEEL_JOINT_NAMES)
        self._head_car_body_id, _ = self.robot.find_bodies("head_car_chassis")
        self._tail_car_body_id, _ = self.robot.find_bodies("tail_car_chassis")
        self._head_car_body_id = self._head_car_body_id[0]
        self._tail_car_body_id = self._tail_car_body_id[0]

        self.actions = torch.zeros((self.num_envs, self.cfg.action_space), device=self.device)
        self.last_actions = torch.zeros_like(self.actions)
        self._policy_actions = torch.zeros_like(self.actions)
        self._processed_actions = torch.zeros_like(self.actions)
        self._motor_strength = torch.ones_like(self.actions)
        self.commands = torch.zeros((self.num_envs, self.cfg.commands.num_commands), device=self.device)
        self._command_time_left = torch.zeros(self.num_envs, device=self.device)

        self._joint_pos_targets = self.robot.data.default_joint_pos.clone()
        self._joint_vel_targets = self.robot.data.default_joint_vel.clone()
        self._episode_sums = {name: torch.zeros(self.num_envs, device=self.device) for name in REWARD_TERM_NAMES}
        self._last_reward_components = {name: torch.zeros(self.num_envs, device=self.device) for name in REWARD_TERM_NAMES}
        self._last_total_reward = torch.zeros(self.num_envs, device=self.device)
        self._last_done_terms = {
            "bad_orientation": torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
            "ball_joint_out_of_bounds": torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
            "root_too_low": torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
            "time_out": torch.zeros(self.num_envs, dtype=torch.bool, device=self.device),
        }
        self._root_height_sum = torch.zeros(self.num_envs, device=self.device)
        self._root_height_min = torch.full((self.num_envs,), float("inf"), device=self.device)
        self._last_critic_height_patch: torch.Tensor | None = None

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

    def step(self, action: torch.Tensor):
        observations, rewards, terminated, time_outs, extras = super().step(action)
        for group_name in ("actor", "critic"):
            observations[group_name] = observations[group_name].clamp(
                -self.cfg.observations.clip_observations,
                self.cfg.observations.clip_observations,
            )
        extras["metrics"] = self._collect_step_metrics()
        return observations, rewards, terminated, time_outs, extras

    def _setup_scene(self) -> None:
        self.robot = Articulation(self.cfg.robot)
        self.scene.articulations["robot"] = self.robot

        self._terrain_runtime = CompleteCarTerrainRuntime(self.cfg.terrain, self.cfg.curriculum, self.device, self.cfg.scene.num_envs)
        ground_prim_path = self._terrain_runtime.setup_scene()
        if not self._terrain_runtime.generator_enabled:
            spawn_ground_plane(prim_path=ground_prim_path, cfg=GroundPlaneCfg())

        self._sensor_runtime = CompleteCarSensorSuiteRuntime(self.cfg.sensors, self.cfg.terrain, ground_prim_path)
        self._sensor_runtime.build_scene_entities(self.scene)

        self.scene.clone_environments(copy_from_source=False)
        if str(self.device) == "cpu":
            self.scene.filter_collisions(global_prim_paths=[])

        if self._terrain_runtime.generator_enabled:
            mdp_curriculum.initialize_terrain_curriculum(self.cfg.curriculum, self._terrain_runtime, self.scene)
        else:
            self._terrain_runtime.initialize_plane_after_scene_clone(self.scene)

        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)

    def _pre_physics_step(self, actions: torch.Tensor) -> None:
        self.last_actions.copy_(self.actions)
        policy_actions, processed_actions = mdp_actions.preprocess_policy_actions(
            actions, self.cfg.observations.clip_actions, self._motor_strength
        )
        self._policy_actions.copy_(policy_actions)
        self.actions.copy_(policy_actions)
        self._processed_actions.copy_(processed_actions)

        resample_env_ids = mdp_commands.step_command_timer(self._command_time_left, self.step_dt)
        if resample_env_ids.numel() > 0:
            mdp_commands.resample_velocity_commands(self.commands, self._command_time_left, resample_env_ids, self.cfg.commands)

        self._joint_pos_targets = mdp_actions.apply_ball_joint_targets(
            self.robot,
            self._joint_pos_targets,
            self._ball_joint_ids,
            self._processed_actions,
            self.cfg.control.ball_joint_action_lower_limits,
            self.cfg.control.ball_joint_action_upper_limits,
        )
        self._joint_vel_targets = mdp_actions.apply_wheel_velocity_targets(
            self._wheel_speed_allocator,
            self.robot,
            self._joint_vel_targets,
            self._ball_joint_ids,
            self._wheel_joint_ids,
            self.commands,
        )

    def _apply_action(self) -> None:
        self.robot.set_joint_position_target(self._joint_pos_targets[:, self._ball_joint_ids], joint_ids=self._ball_joint_ids)
        self.robot.set_joint_velocity_target(self._joint_vel_targets[:, self._wheel_joint_ids], joint_ids=self._wheel_joint_ids)

    def _get_observations(self) -> dict:
        if self._sensor_runtime is not None:
            self._sensor_runtime.get_height_features()

        current_actor_obs = compute_actor_observation(
            self.cfg,
            self.robot,
            self._ball_joint_ids,
            self._wheel_joint_ids,
            self._head_car_body_id,
            self._tail_car_body_id,
            self._joint_pos_targets[:, self._ball_joint_ids],
            self.commands,
            self.last_actions,
        )
        actor_obs = update_history(self._obs_history, current_actor_obs)
        critic_height_patch = self._compute_critic_height_patch()
        self._last_critic_height_patch = critic_height_patch
        critic_obs = compute_critic_observation(actor_obs, critic_height_patch)
        if self._sensor_runtime is not None and self.cfg.debug.log_sensor_outputs:
            self.extras["sensors"] = self._sensor_runtime.get_raw_output()
        return {"actor": actor_obs, "critic": critic_obs}

    def _get_rewards(self) -> torch.Tensor:
        total_reward, components = compute_reward_terms(
            self.cfg,
            self.robot,
            self._ball_joint_ids,
            self.commands,
            self.actions,
            self.last_actions,
            self.reset_terminated,
        )
        for name, value in components.items():
            self._episode_sums[name] += value
            self._last_reward_components[name].copy_(value)

        root_height = self.robot.data.root_link_pos_w[:, 2]
        self._root_height_sum += root_height
        self._root_height_min = torch.minimum(self._root_height_min, root_height)
        self._last_total_reward.copy_(total_reward)
        return total_reward

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        done_terms = compute_done_terms(
            self.cfg,
            self.robot,
            self._ball_joint_ids,
            self.episode_length_buf,
            self.max_episode_length,
        )
        for key, value in done_terms.items():
            self._last_done_terms[key].copy_(value)
        terminated = (
            done_terms["bad_orientation"]
            | done_terms["ball_joint_out_of_bounds"]
            | done_terms["root_too_low"]
        )
        return terminated, done_terms["time_out"]

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

    def _collect_episode_logs(self, env_ids: torch.Tensor, terrain_metrics: dict[str, float] | None):
        extras = {}
        if env_ids.numel() == 0:
            return extras

        episode_lengths = self.episode_length_buf[env_ids].float().clamp(min=1.0)
        root_height_mean = self._root_height_sum[env_ids] / episode_lengths
        current_root_height = self.robot.data.root_link_pos_w[env_ids, 2]
        root_height_min = torch.where(
            torch.isfinite(self._root_height_min[env_ids]),
            self._root_height_min[env_ids],
            current_root_height,
        )
        total_episode_reward = torch.zeros_like(episode_lengths)

        for name, buffer in self._episode_sums.items():
            extras[f"episode/{name}"] = float(torch.mean(buffer[env_ids]).item())
            extras[f"episode_per_step/{name}"] = float(torch.mean(buffer[env_ids] / episode_lengths).item())
            total_episode_reward += buffer[env_ids]
        extras["episode/return"] = float(torch.mean(total_episode_reward).item())
        extras["episode/return_per_step"] = float(torch.mean(total_episode_reward / episode_lengths).item())
        extras["episode/root_height_mean"] = float(torch.mean(root_height_mean).item())
        extras["episode/root_height_min"] = float(torch.mean(root_height_min).item())
        extras["episode/command_lin_x"] = float(torch.mean(self.commands[env_ids, 0]).item())
        extras["episode/command_ang_vel_yaw"] = float(torch.mean(self.commands[env_ids, 1]).item())
        terminated = (
            self._last_done_terms["bad_orientation"][env_ids]
            | self._last_done_terms["ball_joint_out_of_bounds"][env_ids]
            | self._last_done_terms["root_too_low"][env_ids]
        )
        extras["episode_reset/terminated_rate"] = float(torch.mean(terminated.float()).item())
        extras["episode_reset/time_out_rate"] = float(torch.mean(self._last_done_terms["time_out"][env_ids].float()).item())
        extras["episode_reset/bad_orientation_rate"] = float(
            torch.mean(self._last_done_terms["bad_orientation"][env_ids].float()).item()
        )
        extras["episode_reset/ball_joint_limit_rate"] = float(
            torch.mean(self._last_done_terms["ball_joint_out_of_bounds"][env_ids].float()).item()
        )
        extras["episode_reset/root_too_low_rate"] = float(
            torch.mean(self._last_done_terms["root_too_low"][env_ids].float()).item()
        )
        if terrain_metrics is not None:
            extras.update({f"terrain/{key}": value for key, value in terrain_metrics.items()})
        return extras

    def _collect_step_metrics(self) -> dict[str, float]:
        base_lin_vel = self.robot.data.root_com_lin_vel_b
        base_ang_vel = self.robot.data.root_com_ang_vel_b
        projected_gravity = self.robot.data.projected_gravity_b
        ball_joint_pos = wrap_to_pi_tensor(self.robot.data.joint_pos[:, self._ball_joint_ids])
        ball_joint_vel = self.robot.data.joint_vel[:, self._ball_joint_ids]
        ball_joint_target_error = wrap_to_pi_tensor(self._joint_pos_targets[:, self._ball_joint_ids] - ball_joint_pos)
        wheel_joint_vel = self.robot.data.joint_vel[:, self._wheel_joint_ids]
        head_roll_pitch = quaternion_to_rpy(self.robot.data.body_quat_w[:, self._head_car_body_id])[:, :2]
        tail_roll_pitch = quaternion_to_rpy(self.robot.data.body_quat_w[:, self._tail_car_body_id])[:, :2]
        tilt_deg = torch.rad2deg(torch.acos(torch.clamp(-projected_gravity[:, 2], -1.0, 1.0)))
        lin_vel_error_abs = torch.abs(self.commands[:, 0] - base_lin_vel[:, 0])
        yaw_rate_error_abs = torch.abs(self.commands[:, 1] - base_ang_vel[:, 2])

        metrics = {
            "Reward/total": float(torch.mean(self._last_total_reward).item()),
            "Reward/tracking_lin_vel": float(torch.mean(self._last_reward_components["tracking_lin_vel"]).item()),
            "Reward/tracking_ang_vel": float(torch.mean(self._last_reward_components["tracking_ang_vel"]).item()),
            "Reward/orientation": float(torch.mean(self._last_reward_components["orientation"]).item()),
            "Reward/action_rate": float(torch.mean(self._last_reward_components["action_rate"]).item()),
            "Reward/termination": float(torch.mean(self._last_reward_components["termination"]).item()),
            "Tracking/lin_vel_x_abs_error": float(torch.mean(lin_vel_error_abs).item()),
            "Tracking/ang_vel_yaw_abs_error": float(torch.mean(yaw_rate_error_abs).item()),
            "Action/policy_abs_mean": float(torch.mean(torch.abs(self.actions)).item()),
            "Action/processed_abs_mean": float(torch.mean(torch.abs(self._processed_actions)).item()),
            "Action/policy_std": float(self.actions.std(unbiased=False).item()),
            "Action/processed_std": float(self._processed_actions.std(unbiased=False).item()),
            "Action/motor_strength_mean": float(torch.mean(self._motor_strength).item()),
            "Command/lin_vel_x": float(torch.mean(self.commands[:, 0]).item()),
            "Command/ang_vel_yaw": float(torch.mean(self.commands[:, 1]).item()),
            "Observation/base_lin_vel_x": float(torch.mean(base_lin_vel[:, 0]).item()),
            "Observation/base_ang_vel_yaw": float(torch.mean(base_ang_vel[:, 2]).item()),
            "Observation/tilt_deg": float(torch.mean(tilt_deg).item()),
            "Observation/projected_gravity_xy_norm": float(
                torch.mean(torch.linalg.vector_norm(projected_gravity[:, :2], dim=1)).item()
            ),
            "Observation/ball_joint_pos_abs_mean": float(torch.mean(torch.abs(ball_joint_pos)).item()),
            "Observation/ball_joint_vel_abs_mean": float(torch.mean(torch.abs(ball_joint_vel)).item()),
            "Observation/ball_joint_target_error_abs_mean": float(torch.mean(torch.abs(ball_joint_target_error)).item()),
            "Observation/wheel_joint_vel_abs_mean": float(torch.mean(torch.abs(wheel_joint_vel)).item()),
            "Observation/head_roll_pitch_abs_mean": float(torch.mean(torch.abs(head_roll_pitch)).item()),
            "Observation/tail_roll_pitch_abs_mean": float(torch.mean(torch.abs(tail_roll_pitch)).item()),
            "Observation/root_height": float(torch.mean(self.robot.data.root_link_pos_w[:, 2]).item()),
            "Termination/terminated_rate": float(
                torch.mean(
                    (
                        self._last_done_terms["bad_orientation"]
                        | self._last_done_terms["ball_joint_out_of_bounds"]
                        | self._last_done_terms["root_too_low"]
                    ).float()
                ).item()
            ),
            "Termination/time_out_rate": float(torch.mean(self._last_done_terms["time_out"].float()).item()),
            "Termination/bad_orientation_rate": float(
                torch.mean(self._last_done_terms["bad_orientation"].float()).item()
            ),
            "Termination/ball_joint_limit_rate": float(
                torch.mean(self._last_done_terms["ball_joint_out_of_bounds"].float()).item()
            ),
            "Termination/root_too_low_rate": float(torch.mean(self._last_done_terms["root_too_low"].float()).item()),
        }
        if self._last_critic_height_patch is not None:
            metrics["Critic/height_patch_mean"] = float(torch.mean(self._last_critic_height_patch).item())
            metrics["Critic/height_patch_max"] = float(
                torch.mean(torch.max(self._last_critic_height_patch, dim=1).values).item()
            )
        return metrics

    def _reset_idx(self, env_ids: Sequence[int] | None):
        if env_ids is None:
            env_ids = self.robot._ALL_INDICES
        env_ids = torch.as_tensor(env_ids, device=self.device, dtype=torch.long)
        if env_ids.numel() == 0:
            return

        terrain_metrics = None
        if self._terrain_runtime is not None:
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

        if self._sensor_runtime is not None:
            self._sensor_runtime.reset(env_ids)

        self._root_height_sum[env_ids] = 0.0
        self._root_height_min[env_ids] = float("inf")

        root_state = mdp_resets.build_root_state(
            self.cfg, self.robot, self.scene, self._terrain_runtime, env_ids, self.device
        )
        joint_pos, joint_vel = mdp_resets.build_joint_state(
            self.cfg, self.robot, self._ball_joint_ids, self._wheel_joint_ids, env_ids, self.device
        )

        self.robot.write_root_pose_to_sim(root_state[:, :7], env_ids)
        self.robot.write_root_velocity_to_sim(root_state[:, 7:], env_ids)
        self.robot.write_joint_state_to_sim(joint_pos, joint_vel, None, env_ids)

        mdp_commands.resample_velocity_commands(self.commands, self._command_time_left, env_ids, self.cfg.commands)

        self.actions[env_ids] = 0.0
        self.last_actions[env_ids] = 0.0
        self._policy_actions[env_ids] = 0.0
        self._processed_actions[env_ids] = 0.0
        self._joint_pos_targets[env_ids] = self.robot.data.default_joint_pos[env_ids]
        self._joint_vel_targets[env_ids] = self.robot.data.default_joint_vel[env_ids]

        self._motor_strength[env_ids] = mdp_randomization.sample_motor_strength(
            self.cfg, env_ids, self.cfg.action_space, self.device
        )

        if self._obs_history is not None:
            self._obs_history[env_ids] = 0.0
        for name in REWARD_TERM_NAMES:
            self._episode_sums[name][env_ids] = 0.0
        if self._terrain_runtime is not None:
            self._terrain_runtime.curriculum_ready = True

        self._debug_draw.draw_reset_points(env_ids=env_ids, env_origins=self.scene.env_origins[env_ids])


__all__ = ["CompleteCarDirectEnv"]
