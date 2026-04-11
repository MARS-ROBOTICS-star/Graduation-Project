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
from ..mdp import randomization as mdp_randomization
from ..mdp import resets as mdp_resets
from ..mdp.observations import compute_policy_observation
from ..mdp.rewards import REWARD_TERM_NAMES, compute_reward_terms
from ..mdp.terminations import compute_dones
from ..sensors.sensor_cfg import CompleteCarSensorSuiteRuntime
from ..terrain.terrain_runtime import CompleteCarTerrainRuntime
from ..utils.debug_draw import CompleteCarDebugDraw
from ..utils.math_utils import update_history
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
        self._root_height_sum = torch.zeros(self.num_envs, device=self.device)
        self._root_height_min = torch.full((self.num_envs,), float("inf"), device=self.device)

        self._obs_history = None
        if self.cfg.observations.use_history and self.cfg.observations.history_length > 1:
            history_dim = int(self.cfg.observation_space / self.cfg.observations.history_length)
            self._obs_history = torch.zeros(
                (self.num_envs, self.cfg.observations.history_length, history_dim),
                device=self.device,
            )

        if not hasattr(self, "extras"):
            self.extras = {}
        self.extras.setdefault("log", {})

    def step(self, action: torch.Tensor):
        observations, rewards, terminated, time_outs, extras = super().step(action)
        observations["policy"] = observations["policy"].clamp(
            -self.cfg.observations.clip_observations,
            self.cfg.observations.clip_observations,
        )
        return observations, rewards, terminated, time_outs, extras

    def _setup_scene(self) -> None:
        self.robot = Articulation(self.cfg.robot)
        self.scene.articulations["robot"] = self.robot

        self._terrain_runtime = CompleteCarTerrainRuntime(self.cfg.terrain, self.device, self.cfg.scene.num_envs)
        ground_prim_path = self._terrain_runtime.setup_scene()
        if not self._terrain_runtime.generator_enabled:
            spawn_ground_plane(prim_path=ground_prim_path, cfg=GroundPlaneCfg())

        self._sensor_runtime = CompleteCarSensorSuiteRuntime(self.cfg.sensors, self.cfg.terrain, ground_prim_path)
        self._sensor_runtime.build_scene_entities(self.scene)

        self.scene.clone_environments(copy_from_source=False)
        if str(self.device) == "cpu":
            self.scene.filter_collisions(global_prim_paths=[])

        if self._terrain_runtime.generator_enabled:
            self._terrain_runtime.initialize_after_scene_clone(self.scene)
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
            self.cfg.control.ball_joint_action_scale,
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
        sensor_features = self._sensor_runtime.get_policy_features() if self._sensor_runtime is not None else []

        current_obs = compute_policy_observation(
            self.cfg,
            self.robot,
            self._ball_joint_ids,
            self.commands,
            self.last_actions,
            sensor_features,
        )
        policy_obs = update_history(self._obs_history, current_obs)
        if self._sensor_runtime is not None and self.cfg.debug.log_sensor_outputs:
            self.extras["sensors"] = self._sensor_runtime.get_raw_output()
        return {"policy": policy_obs}

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

        root_height = self.robot.data.root_link_pos_w[:, 2]
        self._root_height_sum += root_height
        self._root_height_min = torch.minimum(self._root_height_min, root_height)
        return total_reward

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        return compute_dones(self.cfg, self.robot, self._ball_joint_ids, self.episode_length_buf, self.max_episode_length)

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

        for name, buffer in self._episode_sums.items():
            extras[f"episode/{name}"] = float(torch.mean(buffer[env_ids]).item())
        extras["episode/root_height_mean"] = float(torch.mean(root_height_mean).item())
        extras["episode/root_height_min"] = float(torch.mean(root_height_min).item())
        extras["episode/command_lin_x"] = float(torch.mean(self.commands[env_ids, 0]).item())
        extras["episode/command_ang_vel_yaw"] = float(torch.mean(self.commands[env_ids, 2]).item())
        extras["episode/command_heading"] = float(torch.mean(self.commands[env_ids, 3]).item())
        if terrain_metrics is not None:
            extras.update({f"terrain/{key}": value for key, value in terrain_metrics.items()})
        return extras

    def _reset_idx(self, env_ids: Sequence[int] | None):
        if env_ids is None:
            env_ids = self.robot._ALL_INDICES
        env_ids = torch.as_tensor(env_ids, device=self.device, dtype=torch.long)
        if env_ids.numel() == 0:
            return

        terrain_metrics = None
        if self._terrain_runtime is not None:
            terrain_metrics = self._terrain_runtime.update_curriculum(
                self.scene, self.robot, env_ids, self.commands, self.cfg.episode_length_s
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
