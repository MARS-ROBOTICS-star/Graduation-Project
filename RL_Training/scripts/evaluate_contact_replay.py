"""Headless checkpoint replay for middle-wheel contact diagnostics."""

from __future__ import annotations

import argparse
import os
import re
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


TASK_CHOICES = ["CompleteCar-Stage0", "CompleteCar-Stage1", "CompleteCar-Stage2"]

parser = argparse.ArgumentParser(description="Evaluate middle-wheel contact during checkpoint replay.")
parser.add_argument("--num_envs", type=int, default=8)
parser.add_argument("--task", type=str, default="CompleteCar-Stage0", choices=TASK_CHOICES)
parser.add_argument("--agent", type=str, default="rsl_rl_cfg_entry_point")
parser.add_argument("--checkpoint", type=str, required=True)
parser.add_argument("--steps", type=int, default=1200)
parser.add_argument("--warmup_steps", type=int, default=120)
parser.add_argument("--ball_joint_stiffness", type=float, default=None)
parser.add_argument("--ball_joint_damping", type=float, default=None)
parser.add_argument("--ball_joint_effort_limit", type=float, default=None)
parser.add_argument("--qdot_alloc_filter_tau", type=float, default=None)
parser.add_argument("--ball_joint_yaw_limit", type=float, default=None)
parser.add_argument("--ball_joint_pitch_limit", type=float, default=None)
parser.add_argument("--ball_joint_roll_limit", type=float, default=None)
parser.add_argument("--low_slip_lambda_lateral", type=float, default=None)
parser.add_argument("--label", type=str, default="")
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

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils.hydra import hydra_task_config

import complete_car_lab  # noqa: F401


def _validate_checkpoint_file(path: str) -> str:
    resolved_path = os.path.abspath(os.path.expanduser(path))
    if os.path.isdir(resolved_path):
        raise IsADirectoryError(f"Checkpoint must be a .pt file, got directory: {resolved_path}")
    if not os.path.isfile(resolved_path):
        raise FileNotFoundError(f"Checkpoint file does not exist: {resolved_path}")
    return resolved_path


def _resolve_explicit_checkpoint_path(checkpoint: str) -> str:
    local_path = Path(checkpoint).expanduser()
    if local_path.is_file():
        return str(local_path.resolve())
    return _validate_checkpoint_file(retrieve_file_path(checkpoint))


def _parse_rsl_rl_version(version_str: str):
    try:
        return version.parse(version_str)
    except InvalidVersion:
        return version.parse(version_str.replace("-local", "+local"))


def _set_ball_joint_symmetric_limits(yaw: float, pitch: float, roll: float) -> tuple[tuple[float, ...], tuple[float, ...]]:
    lower = (-yaw, -pitch, -roll, -yaw, -pitch, -roll)
    upper = (yaw, pitch, roll, yaw, pitch, roll)
    return lower, upper


def _mean(values: list[float]) -> float:
    return sum(values) / max(len(values), 1)


def _tail_mean(values: list[float], count: int = 120) -> float:
    if not values:
        return 0.0
    return _mean(values[-min(count, len(values)):])


def _print_summary(label: str, metrics: dict[str, list[float]]) -> None:
    middle_left = _mean(metrics["PerWheel/body_car_wheel_left/normal_force"])
    middle_right = _mean(metrics["PerWheel/body_car_wheel_right/normal_force"])
    wheel_names = (
        "body_car_wheel_left",
        "body_car_wheel_right",
        "head_car_wheel_left",
        "head_car_wheel_right",
        "tail_car_wheel_left",
        "tail_car_wheel_right",
    )
    wheel_force_means = {
        name: _mean(metrics[f"PerWheel/{name}/normal_force"])
        for name in wheel_names
    }
    total_force_n = sum(wheel_force_means.values())
    middle_sum = middle_left + middle_right
    middle_ratio = middle_sum / max(total_force_n, 1.0e-6)

    print("\n=== contact replay summary ===")
    if label:
        print(f"label: {label}")
    print(f"samples: {len(metrics['Observation/pitch_deg'])}")
    print(f"middle_normal_force_n_mean: left={middle_left:.4f}, right={middle_right:.4f}, sum={middle_sum:.4f}")
    print(f"middle_normal_force_n_tail: left={_tail_mean(metrics['PerWheel/body_car_wheel_left/normal_force']):.4f}, right={_tail_mean(metrics['PerWheel/body_car_wheel_right/normal_force']):.4f}")
    print(f"wheel_normal_force_n_mean: total={total_force_n:.4f}, middle_ratio={middle_ratio:.4f}")
    print(
        "wheel_normal_force_n_by_wheel: "
        + ", ".join(f"{name}={wheel_force_means[name]:.4f}" for name in wheel_names)
    )
    print(f"wheel_normal_contact_force_sum_raw_mean: {_mean(metrics['Observation/wheel_normal_contact_force_sum_raw']):.4f}")
    print(f"middle_contact_weight_mean: left={_mean(metrics['PerWheel/body_car_wheel_left/contact_weight']):.4f}, right={_mean(metrics['PerWheel/body_car_wheel_right/contact_weight']):.4f}")
    print(f"pitch_deg_mean: {_mean(metrics['Observation/pitch_deg']):.4f}")
    print(f"roll_deg_mean: {_mean(metrics['Observation/roll_deg']):.4f}")
    print(f"ball_joint_vel_abs_mean: {_mean(metrics['Observation/ball_joint_vel_abs_mean_raw']):.4f}")
    print(f"ball_joint_target_error_abs_mean: {_mean(metrics['Observation/ball_joint_target_error_abs_mean_raw']):.4f}")
    print(f"v_parallel_abs_mean: {_mean(metrics['LowLevel/v_parallel_abs_mean_raw']):.4f}")
    print(f"v_perp_abs_mean: {_mean(metrics['LowLevel/v_perp_abs_mean_raw']):.4f}")
    print(f"longitudinal_slip_abs_mean: {_mean(metrics['Observation/wheel_longitudinal_slip_abs_mean_raw']):.4f}")
    print(f"slip_angle_abs_mean: {_mean(metrics['Observation/wheel_slip_angle_abs_mean_raw']):.4f}")
    print(f"active_segment_completion_pct_tail: {_tail_mean(metrics['Tracking/active_segment_completion_pct']):.4f}")
    reward_keys = [
        "Reward/total",
        "Reward/distance_to_target",
        "Reward/progress_to_target",
        "Reward/reached_target",
        "Reward/far_from_target",
        "Reward/angle_diff",
        "Reward/slip_penalty",
        "Reward/action_rate_penalty",
        "Reward/contact_support_penalty",
        "Reward/edge_speed_penalty",
        "Reward/terrain_aware_edge_speed_penalty",
        "Reward/stuck_penalty",
        "Reward/no_progress_penalty",
        "Reward/airborne_spin_penalty",
        "Reward/hard_terrain_spin_penalty",
        "Reward/action_soft_limit_penalty",
        "Reward/step_up_front_posture_penalty",
        "Reward/step_up_module_progress_reward",
        "Reward/quality_row_advance_reward",
        "Reward/recovery_reward",
        "Reward/drop_anti_dive_penalty",
    ]
    print("reward_mean_per_step:")
    for key in reward_keys:
        values = metrics.get(key, [])
        if values:
            print(f"  {key}: mean={_mean(values):.8f}, tail={_tail_mean(values):.8f}")


@hydra_task_config(args_cli.task, args_cli.agent)
def main(env_cfg: DirectRLEnvCfg, agent_cfg):
    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.sim.device = args_cli.device
    agent_cfg.device = args_cli.device

    if args_cli.ball_joint_stiffness is not None:
        env_cfg.control.ball_joint_stiffness = args_cli.ball_joint_stiffness
    if args_cli.ball_joint_damping is not None:
        env_cfg.control.ball_joint_damping = args_cli.ball_joint_damping
    if args_cli.ball_joint_effort_limit is not None:
        env_cfg.control.ball_joint_effort_limit_sim = args_cli.ball_joint_effort_limit
    if args_cli.qdot_alloc_filter_tau is not None:
        env_cfg.control.ball_joint_qdot_alloc_filter_tau_s = args_cli.qdot_alloc_filter_tau
    if (
        args_cli.ball_joint_yaw_limit is not None
        or args_cli.ball_joint_pitch_limit is not None
        or args_cli.ball_joint_roll_limit is not None
    ):
        current_lower = env_cfg.terminations.ball_joint_pos_lower_limits
        current_upper = env_cfg.terminations.ball_joint_pos_upper_limits
        yaw_limit = (
            args_cli.ball_joint_yaw_limit
            if args_cli.ball_joint_yaw_limit is not None
            else max(abs(current_lower[0]), abs(current_upper[0]))
        )
        pitch_limit = (
            args_cli.ball_joint_pitch_limit
            if args_cli.ball_joint_pitch_limit is not None
            else max(abs(current_lower[1]), abs(current_upper[1]))
        )
        roll_limit = (
            args_cli.ball_joint_roll_limit
            if args_cli.ball_joint_roll_limit is not None
            else max(abs(current_lower[2]), abs(current_upper[2]))
        )
        lower, upper = _set_ball_joint_symmetric_limits(yaw_limit, pitch_limit, roll_limit)
        env_cfg.terminations.ball_joint_pos_lower_limits = lower
        env_cfg.terminations.ball_joint_pos_upper_limits = upper
    if args_cli.low_slip_lambda_lateral is not None:
        env_cfg.control.low_slip_lambda_lateral = args_cli.low_slip_lambda_lateral

    resume_path = _resolve_explicit_checkpoint_path(args_cli.checkpoint)
    print(f"[INFO] Loading checkpoint: {resume_path}")
    print(
        "[INFO] Eval params: "
        f"Kp={env_cfg.control.ball_joint_stiffness}, "
        f"Kd={env_cfg.control.ball_joint_damping}, "
        f"effort={env_cfg.control.ball_joint_effort_limit_sim}, "
        f"vel_limit={env_cfg.control.ball_joint_velocity_limit_sim}, "
        f"tau_v={env_cfg.control.ball_joint_qdot_alloc_filter_tau_s}, "
        f"joint_lower={env_cfg.terminations.ball_joint_pos_lower_limits}, "
        f"joint_upper={env_cfg.terminations.ball_joint_pos_upper_limits}, "
        f"lambda_lat={env_cfg.control.low_slip_lambda_lateral}"
    )

    env = gym.make(args_cli.task, cfg=env_cfg)
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    runner.load(resume_path)
    policy = runner.get_inference_policy(device=env.unwrapped.device)

    installed_version = getattr(rsl_rl, "__version__", "0.0.0")
    parsed_rsl_rl_version = _parse_rsl_rl_version(installed_version)
    policy_nn = runner.alg.policy if parsed_rsl_rl_version < version.parse("4.0.0") else None

    obs = env.get_observations()
    collected: dict[str, list[float]] = defaultdict(list)
    keys = [
        "Observation/pitch_deg",
        "Observation/roll_deg",
        "Observation/ball_joint_vel_abs_mean_raw",
        "Observation/ball_joint_target_error_abs_mean_raw",
        "Observation/wheel_normal_contact_force_sum_raw",
        "Observation/wheel_longitudinal_slip_abs_mean_raw",
        "Observation/wheel_slip_angle_abs_mean_raw",
        "LowLevel/v_parallel_abs_mean_raw",
        "LowLevel/v_perp_abs_mean_raw",
        "Tracking/active_segment_completion_pct",
        "PerWheel/body_car_wheel_left/normal_force",
        "PerWheel/body_car_wheel_right/normal_force",
        "PerWheel/head_car_wheel_left/normal_force",
        "PerWheel/head_car_wheel_right/normal_force",
        "PerWheel/tail_car_wheel_left/normal_force",
        "PerWheel/tail_car_wheel_right/normal_force",
        "PerWheel/body_car_wheel_left/contact_weight",
        "PerWheel/body_car_wheel_right/contact_weight",
        "Reward/total",
        "Reward/distance_to_target",
        "Reward/progress_to_target",
        "Reward/reached_target",
        "Reward/far_from_target",
        "Reward/angle_diff",
        "Reward/slip_penalty",
        "Reward/action_rate_penalty",
        "Reward/contact_support_penalty",
        "Reward/edge_speed_penalty",
        "Reward/terrain_aware_edge_speed_penalty",
        "Reward/stuck_penalty",
        "Reward/no_progress_penalty",
        "Reward/airborne_spin_penalty",
        "Reward/hard_terrain_spin_penalty",
        "Reward/action_soft_limit_penalty",
        "Reward/step_up_front_posture_penalty",
        "Reward/step_up_module_progress_reward",
        "Reward/quality_row_advance_reward",
        "Reward/recovery_reward",
        "Reward/drop_anti_dive_penalty",
    ]

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
            metrics = env.unwrapped.extras.get("metrics", {})
            for key in keys:
                value = metrics.get(key)
                if value is not None:
                    collected[key].append(float(value))

    _print_summary(args_cli.label, collected)
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
