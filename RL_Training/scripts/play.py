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
parser.add_argument(
    "--stream_video",
    action="store_true",
    default=False,
    help="Write replay frames directly to mp4 instead of buffering them through Gymnasium RecordVideo.",
)
parser.add_argument("--video_output_name", type=str, default=None)
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
    "--hide_goal_heading",
    action="store_true",
    default=False,
    help="Hide only the goal heading arrow while keeping the goal position marker visible.",
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
parser.add_argument(
    "--record_chase_view",
    action="store_true",
    default=False,
    help="Record video from the chase follow camera instead of the default viewport camera.",
)
parser.add_argument("--follow_view_top_height", type=float, default=2.5)
parser.add_argument("--follow_view_chase_env", type=int, default=0)
parser.add_argument(
    "--terrain_replay_columns",
    type=str,
    default="all",
    help=(
        "Stage1 replay terrain columns: 'all', one or more column indices such as '0' or '7,8', "
        "or terrain names such as 'flat', 'slope_up', 'stairs_up'."
    ),
)
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


def _checkpoint_selector_is_explicit_path(checkpoint: str) -> bool:
    """Return True when checkpoint should be treated as a direct file path or URI."""
    local_path = Path(checkpoint).expanduser()
    return local_path.is_file() or local_path.is_absolute() or local_path.parent != Path(".") or "://" in checkpoint


def _parse_rsl_rl_version(version_str: str):
    """Parse vendored rsl_rl versions robustly."""
    try:
        return version.parse(version_str)
    except InvalidVersion:
        return version.parse(version_str.replace("-local", "+local"))


def _normalize_selector(value: str) -> str:
    return value.strip().lower().replace("-", " ").replace("_", " ")


def _terrain_column_name(terrain_runtime, column: int) -> str:
    terrain_cfg = terrain_runtime._terrain_cfg
    terrain_names = list(getattr(terrain_cfg, "terrain_names", []))
    if getattr(terrain_runtime, "_terrain_type_map", None) is not None:
        terrain_idx = int(terrain_runtime._terrain_type_map[0, column].item())
    else:
        terrain_idx = column
    if 0 <= terrain_idx < len(terrain_names):
        return terrain_names[terrain_idx]
    return f"terrain_{terrain_idx}"


def _parse_stage1_replay_columns(raw_selector: str, terrain_runtime) -> list[int] | None:
    selector = _normalize_selector(raw_selector)
    if selector in {"", "all", "*", "full", "full terrain", "all terrain"}:
        return None

    terrain_cfg = terrain_runtime._terrain_cfg
    num_cols = int(terrain_cfg.num_cols)
    columns_by_name: dict[str, list[int]] = {}
    for column in range(num_cols):
        terrain_name = _terrain_column_name(terrain_runtime, column)
        columns_by_name.setdefault(_normalize_selector(terrain_name), []).append(column)
    if "uneven rough" in columns_by_name:
        columns_by_name.setdefault("rough", list(columns_by_name["uneven rough"]))

    selected_columns: list[int] = []
    for token in selector.split(","):
        token = token.strip()
        if not token:
            continue
        if token.isdigit():
            column = int(token)
            if column < 0 or column >= num_cols:
                raise ValueError(f"Stage1 terrain replay column must be in [0, {num_cols - 1}], got {column}.")
            selected_columns.append(column)
            continue
        if token not in columns_by_name:
            available = ", ".join(
                f"{column}:{_terrain_column_name(terrain_runtime, column).replace(' ', '_')}"
                for column in range(num_cols)
            )
            raise ValueError(
                f"Unknown Stage1 terrain replay selector '{token}'. "
                f"Use 'all', a column index, or one of: {available}."
            )
        selected_columns.extend(columns_by_name[token])

    unique_columns = sorted(set(selected_columns))
    if not unique_columns:
        raise ValueError("No Stage1 terrain replay columns were selected.")
    return unique_columns


def _format_stage1_replay_columns(columns: list[int], terrain_runtime) -> str:
    return ", ".join(f"{column}:{_terrain_column_name(terrain_runtime, column)}" for column in columns)


def _configure_stage1_replay_terrain(raw_env, raw_selector: str) -> bool:
    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    if terrain_runtime is None or not getattr(terrain_runtime, "generator_enabled", False):
        if _normalize_selector(raw_selector) in {"", "all", "*", "full", "full terrain", "all terrain"}:
            return False
        raise RuntimeError("--terrain_replay_columns is only available for generated Stage1 terrain replay.")
    if terrain_runtime.terrain_types is None or terrain_runtime.terrain_levels is None:
        raise RuntimeError("Stage1 terrain runtime has not initialized terrain levels/types.")

    selected_columns = _parse_stage1_replay_columns(raw_selector, terrain_runtime)
    num_envs = int(raw_env.num_envs)
    num_cols = int(terrain_runtime._terrain_cfg.num_cols)
    env_ids = torch.arange(num_envs, device=raw_env.device, dtype=torch.long)

    if selected_columns is None:
        if num_envs < num_cols:
            raise ValueError(
                f"Full-terrain replay needs at least {num_cols} envs, but got {num_envs}. "
                "Increase --num_envs or choose a specific --terrain_replay_columns value."
            )
        columns_tensor = torch.remainder(env_ids, num_cols)
        terrain_runtime.terrain_types[:] = columns_tensor
        terrain_runtime.sync_env_origins(raw_env.scene)
        print(
            "[INFO] Stage1 replay terrain mode: all columns "
            f"({_format_stage1_replay_columns(list(range(num_cols)), terrain_runtime)}).",
            flush=True,
        )
        return True

    selected_tensor = torch.tensor(selected_columns, device=raw_env.device, dtype=torch.long)
    terrain_runtime.terrain_types[:] = selected_tensor[torch.remainder(env_ids, selected_tensor.numel())]
    terrain_runtime.sync_env_origins(raw_env.scene)
    print(
        "[INFO] Stage1 replay terrain columns: "
        f"{_format_stage1_replay_columns(selected_columns, terrain_runtime)}.",
        flush=True,
    )
    return True


@hydra_task_config(args_cli.task, args_cli.agent)
def main(env_cfg: DirectRLEnvCfg, agent_cfg):
    agent_cfg = _update_agent_cfg(agent_cfg)
    env_cfg.scene.num_envs = args_cli.num_envs if args_cli.num_envs is not None else env_cfg.scene.num_envs
    env_cfg.sim.device = args_cli.device if args_cli.device is not None else env_cfg.sim.device
    env_cfg.debug.enable_debug_draw = (not args_cli.hide_goal_vis) or args_cli.show_wheel_slip_vis or args_cli.create_follow_views
    env_cfg.debug.visualize_goal_heading = not args_cli.hide_goal_heading
    env_cfg.debug.visualize_wheel_slip = args_cli.show_wheel_slip_vis
    env_cfg.debug.create_follow_views = args_cli.create_follow_views
    env_cfg.debug.follow_view_top_height = args_cli.follow_view_top_height
    env_cfg.debug.follow_view_chase_env_index = args_cli.follow_view_chase_env
    if args_cli.record_chase_view:
        env_cfg.debug.create_follow_views = True
        env_cfg.viewer.cam_prim_path = f"/view/env_{args_cli.follow_view_chase_env}/chase_camera"
    if args_cli.slip_vis_close_view:
        env_cfg.viewer.eye = (6.0, -8.0, 5.0)
        env_cfg.viewer.lookat = (6.0, 0.0, 0.4)
        env_cfg.viewer.origin_type = "world"
    agent_cfg.device = env_cfg.sim.device

    log_root_path = os.path.abspath(os.path.join("logs", "rsl_rl", agent_cfg.experiment_name))
    if args_cli.checkpoint and _checkpoint_selector_is_explicit_path(args_cli.checkpoint):
        resume_path = _resolve_explicit_checkpoint_path(args_cli.checkpoint)
    else:
        run_pattern, checkpoint_pattern = _resolve_checkpoint_lookup_args(agent_cfg)
        resume_path = _validate_checkpoint_file(_resolve_checkpoint_path(log_root_path, run_pattern, checkpoint_pattern))
    print(f"[INFO] Loading checkpoint: {resume_path}")
    log_dir = os.path.dirname(resume_path)
    env_cfg.log_dir = log_dir

    env = gym.make(args_cli.task, cfg=env_cfg, render_mode="rgb_array" if args_cli.video else None)
    if _configure_stage1_replay_terrain(env.unwrapped, args_cli.terrain_replay_columns):
        env.reset()
    stream_video_path = None
    if args_cli.video and args_cli.stream_video:
        video_folder = os.path.join(log_dir, "videos", "play")
        os.makedirs(video_folder, exist_ok=True)
        video_name = args_cli.video_output_name or f"{Path(resume_path).stem}_replay.mp4"
        if not video_name.endswith(".mp4"):
            video_name += ".mp4"
        stream_video_path = os.path.join(video_folder, video_name)
        print(f"[INFO] Streaming video to: {stream_video_path}")
    elif args_cli.video:
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
    video_writer = None
    if stream_video_path is not None:
        import imageio.v2 as imageio

        video_writer = imageio.get_writer(
            stream_video_path,
            fps=round(1.0 / dt),
            codec="libx264",
            macro_block_size=None,
        )
    obs = env.get_observations()
    timestep = 0
    try:
        while simulation_app.is_running():
            start_time = time.time()
            with torch.inference_mode():
                actions = policy(obs)
                obs, _, dones, _ = env.step(actions)
                if parsed_rsl_rl_version >= version.parse("4.0.0"):
                    policy.reset(dones)
                elif policy_nn is not None:
                    policy_nn.reset(dones)
            if video_writer is not None:
                frame = env.unwrapped.render(recompute=False)
                if frame is not None:
                    video_writer.append_data(frame)
                timestep += 1
                if timestep % 600 == 0:
                    print(f"[INFO] Streamed {timestep}/{args_cli.video_length} video frames", flush=True)
                if timestep >= args_cli.video_length:
                    break
            elif args_cli.video:
                timestep += 1
                if timestep == args_cli.video_length:
                    break
            sleep_time = dt - (time.time() - start_time)
            if args_cli.real_time and sleep_time > 0:
                time.sleep(sleep_time)
    finally:
        if video_writer is not None:
            video_writer.close()
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
