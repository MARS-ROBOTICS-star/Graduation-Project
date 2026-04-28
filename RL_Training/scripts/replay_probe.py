"""Headless replay probe for policy action and wheel-speed diagnostics."""

from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path

from isaaclab.app import AppLauncher


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_SOURCE = PROJECT_ROOT / "source" / "complete_car_lab"
LOCAL_RSL_RL_SOURCE = EXTENSION_SOURCE / "complete_car_lab" / "tasks" / "direct" / "complete_car"

for path in (LOCAL_RSL_RL_SOURCE, EXTENSION_SOURCE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


parser = argparse.ArgumentParser(description="Probe complete-car checkpoint replay metrics.")
parser.add_argument("--task", type=str, default="CompleteCar-Stage0")
parser.add_argument("--agent", type=str, default="rsl_rl_cfg_entry_point")
parser.add_argument("--checkpoint", type=str, required=True)
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--steps", type=int, default=900)
parser.add_argument("--warmup_steps", type=int, default=120)
AppLauncher.add_app_launcher_args(parser)
args_cli, hydra_args = parser.parse_known_args()

if args_cli.device is None:
    args_cli.device = "cuda:0"
args_cli.headless = True
sys.argv = [sys.argv[0]] + hydra_args

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app


import gymnasium as gym
from packaging import version
from packaging.version import InvalidVersion
import torch
import rsl_rl
from rsl_rl.runners import OnPolicyRunner

from isaaclab.envs import DirectRLEnvCfg
from isaaclab.utils.assets import retrieve_file_path
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from isaaclab_tasks.utils.hydra import hydra_task_config

import isaaclab_tasks  # noqa: F401
import complete_car_lab  # noqa: F401
from complete_car_lab.tasks.direct.complete_car.assets.robot_cfg import WHEEL_JOINT_NAMES


def _resolve_checkpoint(checkpoint: str) -> str:
    local_path = Path(checkpoint).expanduser()
    if local_path.is_file():
        return str(local_path.resolve())
    resolved = Path(retrieve_file_path(checkpoint)).expanduser()
    if not resolved.is_file():
        raise FileNotFoundError(f"Checkpoint file does not exist: {resolved}")
    return str(resolved.resolve())


def _parse_rsl_rl_version(version_str: str):
    try:
        return version.parse(version_str)
    except InvalidVersion:
        return version.parse(version_str.replace("-local", "+local"))


def _record_tensor(metrics: dict[str, list[torch.Tensor]], name: str, value: torch.Tensor) -> None:
    metrics[name].append(value.detach().float().cpu().flatten())


def _summarize(values: list[torch.Tensor]) -> tuple[float, float, float, float]:
    if not values:
        return 0.0, 0.0, 0.0, 0.0
    x = torch.cat(values)
    return (
        float(x.mean().item()),
        float(x.abs().mean().item()),
        float(x.min().item()),
        float(x.max().item()),
    )


def _summarize_vector(values: list[torch.Tensor]) -> torch.Tensor:
    if not values:
        return torch.empty(0)
    return torch.stack(values, dim=0).mean(dim=0)


def _probe_print(message: str) -> None:
    print(f"[PROBE] {message}", flush=True)


@hydra_task_config(args_cli.task, args_cli.agent)
def main(env_cfg: DirectRLEnvCfg, agent_cfg):
    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.sim.device = args_cli.device
    agent_cfg.device = args_cli.device

    checkpoint = _resolve_checkpoint(args_cli.checkpoint)
    print(f"[INFO] Loading checkpoint: {checkpoint}")
    print(
        "[INFO] Config: "
        f"base_v_max={env_cfg.control.base_forward_velocity_max}, "
        f"base_wz_max={env_cfg.control.base_yaw_rate_max}, "
        f"wheel_radius={env_cfg.control.wheel_radius}, "
        f"wheel_damping={env_cfg.control.wheel_joint_damping}, "
        f"wheel_effort_limit={env_cfg.control.wheel_joint_effort_limit_sim}"
    )

    _probe_print("creating gym environment")
    env = gym.make(args_cli.task, cfg=env_cfg)
    _probe_print("wrapping environment")
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    _probe_print("creating runner")
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    _probe_print("loading checkpoint")
    runner.load(checkpoint)
    policy = runner.get_inference_policy(device=env.unwrapped.device)
    _probe_print("policy ready")

    installed_version = getattr(rsl_rl, "__version__", "0.0.0")
    parsed_rsl_rl_version = _parse_rsl_rl_version(installed_version)
    policy_nn = runner.alg.policy if parsed_rsl_rl_version < version.parse("4.0.0") else None

    obs = env.get_observations()
    raw_env = env.unwrapped
    initial_root_xy = raw_env.robot.data.root_link_pos_w[:, :2].detach().clone()
    initial_goal_distance = raw_env._last_active_waypoint_pos_error.detach().clone()

    scalar_metrics: dict[str, list[torch.Tensor]] = defaultdict(list)
    vector_metrics: dict[str, list[torch.Tensor]] = defaultdict(list)
    done_count = 0
    timeout_count = 0

    _probe_print("starting replay loop")
    with torch.inference_mode():
        for step in range(args_cli.steps):
            actions = policy(obs)
            obs, _, dones, _ = env.step(actions)
            if parsed_rsl_rl_version >= version.parse("4.0.0"):
                policy.reset(dones)
            elif policy_nn is not None:
                policy_nn.reset(dones)

            if step < args_cli.warmup_steps:
                continue

            done_count += int(torch.sum(dones).item())
            timeout_count += int(torch.sum(raw_env._last_done_terms["time_out"]).item())

            _record_tensor(scalar_metrics, "raw_action_all", actions)
            _record_tensor(scalar_metrics, "raw_action_base", actions[:, :2])
            _record_tensor(scalar_metrics, "raw_action_joint", actions[:, 2:])
            _record_tensor(scalar_metrics, "desired_planar_vx", raw_env._last_desired_planar_command[:, 0])
            _record_tensor(scalar_metrics, "desired_planar_wz", raw_env._last_desired_planar_command[:, 1])
            _record_tensor(scalar_metrics, "wheel_ref", raw_env._last_wheel_speed_reference)
            _record_tensor(scalar_metrics, "wheel_joint_vel", raw_env.robot.data.joint_vel[:, raw_env._wheel_joint_ids])
            _record_tensor(scalar_metrics, "wheel_rolling_speed", raw_env._last_wheel_v_parallel)
            _record_tensor(scalar_metrics, "wheel_lateral_speed", raw_env._last_wheel_v_perp)
            _record_tensor(scalar_metrics, "wheel_delta_v", raw_env._last_wheel_delta_v)
            _record_tensor(scalar_metrics, "wheel_longitudinal_slip", raw_env._cached_step_raw_obs_terms["wheel_longitudinal_slip"])
            _record_tensor(scalar_metrics, "wheel_slip_angle", raw_env._cached_step_raw_obs_terms["wheel_slip_angle"])
            _record_tensor(scalar_metrics, "active_goal_distance", raw_env._last_active_waypoint_pos_error)
            _record_tensor(scalar_metrics, "active_goal_bearing_abs", raw_env._last_active_waypoint_bearing_abs)
            _record_tensor(scalar_metrics, "progress_reward", raw_env._last_reward_components["progress_to_target"])
            _record_tensor(scalar_metrics, "progress_multiplier", raw_env._last_reward_diagnostics["progress_multiplier"])
            _record_tensor(scalar_metrics, "timeout_penalty", raw_env._last_reward_components["timeout_penalty"])

            vector_metrics["action_last"].append(actions[0].detach().float().cpu())
            vector_metrics["desired_planar_last"].append(raw_env._last_desired_planar_command[0].detach().float().cpu())
            vector_metrics["wheel_ref_last"].append(raw_env._last_wheel_speed_reference[0].detach().float().cpu())
            vector_metrics["wheel_vel_last"].append(raw_env.robot.data.joint_vel[0, raw_env._wheel_joint_ids].detach().float().cpu())
            vector_metrics["rolling_last"].append(raw_env._last_wheel_v_parallel[0].detach().float().cpu())
            vector_metrics["lateral_last"].append(raw_env._last_wheel_v_perp[0].detach().float().cpu())
    _probe_print("replay loop finished")

    _probe_print("printing summary")
    print("\n=== replay probe summary ===", flush=True)
    print(f"num_envs={args_cli.num_envs}, steps={args_cli.steps}, warmup_steps={args_cli.warmup_steps}", flush=True)
    print(f"done_count_after_warmup={done_count}, timeout_count_after_warmup={timeout_count}", flush=True)
    for name in (
        "raw_action_all",
        "raw_action_base",
        "raw_action_joint",
        "desired_planar_vx",
        "desired_planar_wz",
        "wheel_ref",
        "wheel_joint_vel",
        "wheel_rolling_speed",
        "wheel_lateral_speed",
        "wheel_delta_v",
        "wheel_longitudinal_slip",
        "wheel_slip_angle",
        "active_goal_distance",
        "active_goal_bearing_abs",
        "progress_reward",
        "progress_multiplier",
        "timeout_penalty",
    ):
        mean, abs_mean, min_value, max_value = _summarize(scalar_metrics[name])
        print(f"{name}: mean={mean:.6f}, abs_mean={abs_mean:.6f}, min={min_value:.6f}, max={max_value:.6f}", flush=True)

    wheel_labels = [name.removesuffix("_joint") for name in WHEEL_JOINT_NAMES]
    for name in ("wheel_ref_last", "wheel_vel_last", "rolling_last", "lateral_last"):
        mean_values = _summarize_vector(vector_metrics[name])
        values = ", ".join(f"{label}={float(value):.6f}" for label, value in zip(wheel_labels, mean_values))
        print(f"{name}_mean_by_wheel: {values}", flush=True)
    for name in ("action_last", "desired_planar_last"):
        mean_values = _summarize_vector(vector_metrics[name])
        values = ", ".join(f"{float(value):.6f}" for value in mean_values)
        print(f"{name}_mean_vector: [{values}]", flush=True)
    try:
        final_root_xy = raw_env.robot.data.root_link_pos_w[:, :2].detach().clone()
        final_goal_distance = raw_env._last_active_waypoint_pos_error.detach().clone()
        displacement = torch.linalg.vector_norm(final_root_xy - initial_root_xy, dim=1)
        goal_delta = initial_goal_distance - final_goal_distance
        print(f"root_xy_displacement_mean_m={float(displacement.mean().item()):.6f}", flush=True)
        print(f"goal_distance_delta_mean_m={float(goal_delta.mean().item()):.6f}", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Could not compute final displacement summary: {exc}", flush=True)

    env.close()
    simulation_app.close()


if __name__ == "__main__":
    main()
