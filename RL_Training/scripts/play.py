"""RSL-RL 回放入口。"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

from isaaclab.app import AppLauncher


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_SOURCE = PROJECT_ROOT / "source" / "complete_car_lab"
LOCAL_RSL_RL_SOURCE = EXTENSION_SOURCE / "complete_car_lab" / "tasks" / "direct" / "complete_car"

for path in (LOCAL_RSL_RL_SOURCE, EXTENSION_SOURCE):
    if str(path) not in sys.path:
        # 回放链路和训练链路保持一致，统一走项目内的本地 rsl_rl 实现。
        sys.path.insert(0, str(path))


TASK_CHOICES = ["CompleteCar-Stage0", "CompleteCar-Stage1", "CompleteCar-Stage2"]

parser = argparse.ArgumentParser(description="Play complete-car checkpoint with RSL-RL.")
parser.add_argument("--video", action="store_true", default=False)
parser.add_argument("--video_length", type=int, default=200)
parser.add_argument("--num_envs", type=int, default=None)
parser.add_argument("--task", type=str, default="CompleteCar-Stage0", choices=TASK_CHOICES)
parser.add_argument("--agent", type=str, default="rsl_rl_cfg_entry_point")
parser.add_argument("--checkpoint", type=str, default=None)
parser.add_argument("--load_run", type=str, default=None)
parser.add_argument("--real-time", action="store_true", default=False)
parser.add_argument(
    "--hide_goal_vis",
    action="store_true",
    default=False,
    help="Hide goal position and heading markers during playback.",
)
parser.add_argument(
    "--show_wheel_slip_vis",
    action="store_true",
    default=False,
    help="Draw wheel rolling directions in green and actual planar velocity directions in red.",
)
parser.add_argument(
    "--slip_vis_close_view",
    action="store_true",
    default=False,
    help="Use a closer fixed camera view for inspecting wheel-slip visualization.",
)
parser.add_argument(
    "--create_follow_views",
    action="store_true",
    default=False,
    help="Create selectable follow cameras under /view: one top-down camera per env and one chase camera.",
)
parser.add_argument("--follow_view_top_height", type=float, default=2.5)
parser.add_argument("--follow_view_chase_env", type=int, default=0)
AppLauncher.add_app_launcher_args(parser)
args_cli, hydra_args = parser.parse_known_args()

if args_cli.video:
    args_cli.enable_cameras = True

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
from isaaclab.utils.dict import print_dict

from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper, export_policy_as_jit, export_policy_as_onnx

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import get_checkpoint_path
from isaaclab_tasks.utils.hydra import hydra_task_config

import complete_car_lab  # noqa: F401


def _update_agent_cfg(agent_cfg):
    if args_cli.load_run is not None:
        agent_cfg.load_run = args_cli.load_run
    if args_cli.checkpoint is not None:
        agent_cfg.load_checkpoint = args_cli.checkpoint
    return agent_cfg


def _resolve_checkpoint_lookup_args(agent_cfg) -> tuple[str, str]:
    """Normalize run/checkpoint selectors for Isaac Lab checkpoint lookup."""
    run_pattern = agent_cfg.load_run if isinstance(agent_cfg.load_run, str) else ".*"
    checkpoint_pattern = agent_cfg.load_checkpoint if isinstance(agent_cfg.load_checkpoint, str) else "model_.*.pt"
    return run_pattern, checkpoint_pattern


def _resolve_checkpoint_path(log_root_path: str, run_pattern: str, checkpoint_pattern: str) -> str:
    """Resolve checkpoints from either a run name or a direct run-directory-like path."""

    def _try_existing_run_dir(candidate: Path) -> str | None:
        if not candidate.is_dir():
            return None
        return get_checkpoint_path(str(candidate.parent), candidate.name, checkpoint_pattern)

    if run_pattern in {"", ".*"}:
        return get_checkpoint_path(log_root_path, run_pattern, checkpoint_pattern)

    run_selector = Path(run_pattern)
    direct_candidates = []
    if run_selector.is_absolute():
        direct_candidates.append(run_selector)
    else:
        direct_candidates.append(Path(run_pattern))
        direct_candidates.append(Path(log_root_path) / run_selector)
        direct_candidates.append(Path(log_root_path).parent / run_selector)

    for candidate in direct_candidates:
        resolved = _try_existing_run_dir(candidate)
        if resolved is not None:
            return resolved

    if not run_selector.is_absolute():
        normalized_pattern = str(run_selector).strip()
        normalized_pattern = re.sub(r"^[./]+", "", normalized_pattern)
        log_root_name = Path(log_root_path).name
        duplicated_prefix = f"{log_root_name}/"
        if normalized_pattern.startswith(duplicated_prefix):
            normalized_pattern = normalized_pattern[len(duplicated_prefix) :]
        return get_checkpoint_path(log_root_path, normalized_pattern, checkpoint_pattern)

    return get_checkpoint_path(log_root_path, run_pattern, checkpoint_pattern)


def _validate_checkpoint_file(path: str) -> str:
    """Ensure the resolved checkpoint is a real file before passing it to torch.load."""
    resolved_path = os.path.abspath(os.path.expanduser(path))
    if os.path.isdir(resolved_path):
        raise IsADirectoryError(
            f"Checkpoint must be a .pt file, but got directory: {resolved_path}. "
            "Check the value passed after --checkpoint."
        )
    if not os.path.isfile(resolved_path):
        raise FileNotFoundError(f"Checkpoint file does not exist: {resolved_path}")
    return resolved_path


def _resolve_explicit_checkpoint_path(checkpoint: str) -> str:
    """Resolve a user-provided checkpoint path without turning local files into temp dirs."""
    local_path = Path(checkpoint).expanduser()
    if local_path.is_file():
        return str(local_path.resolve())
    return _validate_checkpoint_file(retrieve_file_path(checkpoint))


def _parse_rsl_rl_version(version_str: str):
    """Parse vendored rsl_rl versions robustly."""
    try:
        return version.parse(version_str)
    except InvalidVersion:
        return version.parse(version_str.replace("-local", "+local"))


@hydra_task_config(args_cli.task, args_cli.agent)
def main(env_cfg: DirectRLEnvCfg, agent_cfg):
    agent_cfg = _update_agent_cfg(agent_cfg)
    env_cfg.scene.num_envs = args_cli.num_envs if args_cli.num_envs is not None else env_cfg.scene.num_envs
    env_cfg.sim.device = args_cli.device if args_cli.device is not None else env_cfg.sim.device
    env_cfg.debug.enable_debug_draw = (not args_cli.hide_goal_vis) or args_cli.show_wheel_slip_vis or args_cli.create_follow_views
    env_cfg.debug.visualize_wheel_slip = args_cli.show_wheel_slip_vis
    env_cfg.debug.create_follow_views = args_cli.create_follow_views
    env_cfg.debug.follow_view_top_height = args_cli.follow_view_top_height
    env_cfg.debug.follow_view_chase_env_index = args_cli.follow_view_chase_env
    if args_cli.slip_vis_close_view:
        env_cfg.viewer.eye = (6.0, -8.0, 5.0)
        env_cfg.viewer.lookat = (6.0, 0.0, 0.4)
        env_cfg.viewer.origin_type = "world"
    agent_cfg.device = env_cfg.sim.device

    log_root_path = os.path.abspath(os.path.join("logs", "rsl_rl", agent_cfg.experiment_name))
    if args_cli.checkpoint:
        resume_path = _resolve_explicit_checkpoint_path(args_cli.checkpoint)
    else:
        run_pattern, checkpoint_pattern = _resolve_checkpoint_lookup_args(agent_cfg)
        resume_path = _validate_checkpoint_file(_resolve_checkpoint_path(log_root_path, run_pattern, checkpoint_pattern))
    print(f"[INFO] Loading checkpoint: {resume_path}")
    log_dir = os.path.dirname(resume_path)
    env_cfg.log_dir = log_dir

    env = gym.make(args_cli.task, cfg=env_cfg, render_mode="rgb_array" if args_cli.video else None)
    if args_cli.video:
        video_kwargs = {
            "video_folder": os.path.join(log_dir, "videos", "play"),
            "step_trigger": lambda step: step == 0,
            "video_length": args_cli.video_length,
            "disable_logger": True,
        }
        print_dict(video_kwargs, nesting=4)
        env = gym.wrappers.RecordVideo(env, **video_kwargs)

    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    runner.load(resume_path)
    policy = runner.get_inference_policy(device=env.unwrapped.device)

    export_model_dir = os.path.join(os.path.dirname(resume_path), "exported")
    installed_version = getattr(rsl_rl, "__version__", "0.0.0")
    parsed_rsl_rl_version = _parse_rsl_rl_version(installed_version)
    if parsed_rsl_rl_version >= version.parse("4.0.0"):
        runner.export_policy_to_jit(path=export_model_dir, filename="policy.pt")
        runner.export_policy_to_onnx(path=export_model_dir, filename="policy.onnx")
        policy_nn = None
    else:
        policy_nn = runner.alg.policy
        normalizer = getattr(policy_nn, "actor_obs_normalizer", None)
        export_policy_as_jit(policy_nn, normalizer=normalizer, path=export_model_dir, filename="policy.pt")
        export_policy_as_onnx(policy_nn, normalizer=normalizer, path=export_model_dir, filename="policy.onnx")

    dt = env.unwrapped.step_dt
    obs = env.get_observations()
    timestep = 0
    while simulation_app.is_running():
        start_time = time.time()
        with torch.inference_mode():
            actions = policy(obs)
            obs, _, dones, _ = env.step(actions)
            if parsed_rsl_rl_version >= version.parse("4.0.0"):
                policy.reset(dones)
            elif policy_nn is not None:
                policy_nn.reset(dones)
        if args_cli.video:
            timestep += 1
            if timestep == args_cli.video_length:
                break
        sleep_time = dt - (time.time() - start_time)
        if args_cli.real_time and sleep_time > 0:
            time.sleep(sleep_time)
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
