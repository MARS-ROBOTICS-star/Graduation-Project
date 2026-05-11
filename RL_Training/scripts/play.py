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
FOLLOW_CAMERA_NAMES = {
    "chase": "chase_camera",
    "left_chase": "left_chase_camera",
    "forward": "forward_camera",
    "right_side": "right_side_camera",
    "top_down": "top_down_camera",
}

parser = argparse.ArgumentParser(description="Play complete-car checkpoint with RSL-RL.")
parser.add_argument("--video", action="store_true", default=False)
parser.add_argument(
    "--video_length",
    type=int,
    default=0,
    help="Optional recording frame limit. Use 0 to record until the GUI is closed or the process is interrupted.",
)
parser.add_argument(
    "--video_resolution",
    type=str,
    default=None,
    help="Override recorded render resolution as WIDTHxHEIGHT, for example 3840x2160.",
)
parser.add_argument(
    "--stream_video",
    action="store_true",
    default=False,
    help="Write replay frames directly to mp4 instead of buffering them through Gymnasium RecordVideo.",
)
parser.add_argument("--video_output_name", type=str, default=None)
parser.add_argument(
    "--video_crf",
    type=int,
    default=18,
    help="x264 CRF for --stream_video. Lower is higher quality; 0 is lossless, 18 is visually high quality.",
)
parser.add_argument(
    "--video_preset",
    type=str,
    default="slow",
    choices=("ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"),
    help="x264 encoding preset for --stream_video. Slower presets improve compression at the same CRF.",
)
parser.add_argument("--num_envs", type=int, default=None)
parser.add_argument("--task", type=str, default="CompleteCar-Stage0", choices=TASK_CHOICES)
parser.add_argument("--agent", type=str, default="rsl_rl_cfg_entry_point")
parser.add_argument("--checkpoint", type=str, default=None)
parser.add_argument("--load_run", type=str, default=None)
parser.add_argument("--real-time", action="store_true", default=False)
parser.add_argument(
    "--show_goal_vis",
    action="store_true",
    default=False,
    help="Show goal position marker during playback.",
)
parser.add_argument(
    "--show_goal_heading",
    action="store_true",
    default=False,
    help="Show goal heading arrow during playback. Requires --show_goal_vis.",
)
parser.add_argument(
    "--show_wheel_slip_vis",
    action="store_true",
    default=False,
    help="Draw wheel rolling directions in green and actual planar velocity directions in red.",
)
parser.add_argument(
    "--show_height_patch_vis",
    action="store_true",
    default=False,
    help="Draw Stage1 local height-map patch sample points in the Isaac Sim viewport.",
)
parser.add_argument(
    "--height_patch_vis_envs",
    type=str,
    default="0",
    help="Env ids for height-patch visualization, such as '0', '0,7', or 'all'.",
)
parser.add_argument("--height_patch_vis_radius", type=float, default=0.035)
parser.add_argument("--height_patch_vis_height_offset", type=float, default=0.035)
parser.add_argument("--height_patch_vis_color_range_m", type=float, default=0.30)
parser.add_argument(
    "--show_height_patch_axis",
    action="store_true",
    default=False,
    help="Show the red +Y direction axis with Stage1 height-patch visualization.",
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
    help="Record video from a follow camera instead of the default viewport camera.",
)
parser.add_argument(
    "--record_camera_view",
    type=str,
    default="chase",
    choices=tuple(FOLLOW_CAMERA_NAMES.keys()),
    help="Follow camera to record when --record_chase_view is enabled.",
)
parser.add_argument(
    "--record_camera_views",
    type=str,
    default=None,
    help=(
        "Comma-separated follow cameras to record simultaneously when --record_chase_view and "
        "--stream_video are enabled, such as 'chase,right_side'."
    ),
)
parser.add_argument("--follow_view_top_height", type=float, default=2.5)
parser.add_argument("--follow_view_chase_env", type=int, default=0)
parser.add_argument(
    "--terrain_replay_columns",
    type=str,
    default="all",
    help=(
        "Stage1 replay terrain columns: 'all', one or more column indices such as '0' or '7,8', "
        "or terrain names such as 'flat', 'slope_up', 'stairs_down', 'discrete_obstacles'."
    ),
)
parser.add_argument(
    "--replay_episode_length_s",
    type=float,
    default=None,
    help=(
        "Override episode length only for playback. This is useful for inspecting whether a policy "
        "can eventually reach terrain-column targets after the training timeout."
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
from complete_car_lab.tasks.direct.complete_car.mdp import curriculum as mdp_curriculum


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


def _playback_load_cfg_for_checkpoint(checkpoint_path: str) -> dict[str, bool] | None:
    """Use actor/critic-only loading for warm-start checkpoints without optimizer state."""
    checkpoint = torch.load(checkpoint_path, weights_only=False, map_location="cpu")
    has_actor_critic = "actor_state_dict" in checkpoint and "critic_state_dict" in checkpoint
    if has_actor_critic and "optimizer_state_dict" not in checkpoint:
        return {"actor": True, "critic": True, "optimizer": False, "iteration": False, "rnd": False}
    return None


def _parse_video_resolution(raw_resolution: str) -> tuple[int, int]:
    normalized = raw_resolution.lower().replace(" ", "")
    parts = normalized.split("x")
    if len(parts) != 2:
        raise ValueError("--video_resolution must use WIDTHxHEIGHT format, for example 3840x2160.")
    width, height = int(parts[0]), int(parts[1])
    if width <= 0 or height <= 0:
        raise ValueError("--video_resolution width and height must be positive.")
    return width, height


def _parse_record_camera_views(raw_views: str | None, fallback_view: str) -> tuple[str, ...]:
    if raw_views is None:
        return (fallback_view,)
    views: list[str] = []
    for raw_view in raw_views.split(","):
        view = raw_view.strip()
        if not view:
            continue
        if view not in FOLLOW_CAMERA_NAMES:
            valid_views = ", ".join(FOLLOW_CAMERA_NAMES.keys())
            raise ValueError(f"Unknown record camera view '{view}'. Valid views: {valid_views}.")
        if view not in views:
            views.append(view)
    if not views:
        raise ValueError("--record_camera_views must contain at least one valid camera view.")
    return tuple(views)


def _build_stream_video_paths(
    video_folder: str,
    resume_path: str,
    output_name: str | None,
    camera_views: tuple[str, ...],
) -> dict[str, str]:
    video_name = output_name or f"{Path(resume_path).stem}_replay.mp4"
    if not video_name.endswith(".mp4"):
        video_name += ".mp4"

    stem, suffix = os.path.splitext(video_name)
    if len(camera_views) == 1:
        return {camera_views[0]: os.path.join(video_folder, video_name)}
    return {view: os.path.join(video_folder, f"{stem}_{view}{suffix}") for view in camera_views}


def _open_stream_writer(output_path: str, fps: int):
    import imageio.v2 as imageio

    return imageio.get_writer(
        output_path,
        fps=fps,
        codec="libx264",
        macro_block_size=None,
        output_params=[
            "-crf",
            str(args_cli.video_crf),
            "-preset",
            args_cli.video_preset,
            "-pix_fmt",
            "yuv420p",
        ],
    )


def _open_follow_view_stream_recorders(
    raw_env,
    stream_video_paths: dict[str, str],
    fps: int,
) -> list[dict[str, object]]:
    import omni.replicator.core as rep

    recorders: list[dict[str, object]] = []
    for view, output_path in stream_video_paths.items():
        camera_prim_path = f"/view/env_{args_cli.follow_view_chase_env}/{FOLLOW_CAMERA_NAMES[view]}"
        render_product = rep.create.render_product(camera_prim_path, resolution=raw_env.cfg.viewer.resolution)
        if not isinstance(render_product, str):
            render_product = render_product.path
        annotator = rep.AnnotatorRegistry.get_annotator("rgb", device="cpu")
        annotator.attach(render_product)
        writer = _open_stream_writer(output_path, fps)
        recorders.append(
            {
                "view": view,
                "path": output_path,
                "render_product": render_product,
                "annotator": annotator,
                "writer": writer,
            }
        )
        print(f"[INFO] Streaming {view} camera video to: {output_path}", flush=True)
    return recorders


def _append_follow_view_frames(recorders: list[dict[str, object]]) -> None:
    import numpy as np

    for recorder in recorders:
        annotator = recorder["annotator"]
        writer = recorder["writer"]
        rgb_data = annotator.get_data()
        rgb_data = np.frombuffer(rgb_data, dtype=np.uint8).reshape(*rgb_data.shape)
        if rgb_data.size == 0:
            continue
        writer.append_data(rgb_data[:, :, :3])


def _close_follow_view_stream_recorders(recorders: list[dict[str, object]]) -> None:
    for recorder in recorders:
        writer = recorder.get("writer")
        annotator = recorder.get("annotator")
        render_product = recorder.get("render_product")
        if writer is not None:
            writer.close()
            recorder["writer"] = None
        if annotator is not None and render_product is not None:
            annotator.detach([render_product])
        recorder["annotator"] = None
        recorder["render_product"] = None


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


def _reset_stage1_replay_curriculum_state(raw_env, terrain_runtime) -> None:
    """Keep Stage1 replay column selection from being overwritten by reset recycling."""
    num_cols = int(terrain_runtime._terrain_cfg.num_cols)
    terrain_runtime.terrain_levels[:] = mdp_curriculum.sample_initial_terrain_levels(
        raw_env.cfg.curriculum,
        terrain_runtime,
        terrain_runtime.terrain_types,
    )
    targets = mdp_curriculum.compute_terrain_column_counts(terrain_runtime.terrain_types, num_cols)

    completion_targets = getattr(raw_env, "_stage1_column_completion_targets", None)
    completion_counts = getattr(raw_env, "_stage1_column_completion_counts", None)
    completed_columns = getattr(raw_env, "_stage1_completed_terrain_columns", None)
    if completion_targets is not None and completion_counts is not None and completed_columns is not None:
        completion_targets.copy_(targets)
        completion_counts.zero_()
        completed_columns.copy_(targets <= 0)

    training_active = getattr(raw_env, "_stage1_training_active", None)
    transition_train_mask = getattr(raw_env, "_stage1_transition_train_mask", None)
    recycled_ever = getattr(raw_env, "_stage1_recycled_envs_ever", None)
    last_recycled = getattr(raw_env, "_stage1_last_recycled_env_mask", None)
    if training_active is not None:
        training_active.fill_(True)
    if transition_train_mask is not None:
        transition_train_mask.fill_(True)
    if recycled_ever is not None:
        recycled_ever.zero_()
    if last_recycled is not None:
        last_recycled.zero_()
    if hasattr(raw_env, "_stage1_recycle_cursor"):
        raw_env._stage1_recycle_cursor = 0


def _parse_env_indices(raw_selector: str, num_envs: int) -> tuple[int, ...]:
    selector = _normalize_selector(raw_selector)
    if selector in {"", "all", "*"}:
        return ()

    selected_env_ids: list[int] = []
    for token in selector.split(","):
        token = token.strip()
        if not token:
            continue
        if not token.isdigit():
            raise ValueError(f"Env id selector must be an integer, comma list, or 'all', got '{token}'.")
        env_id = int(token)
        if env_id < 0 or env_id >= num_envs:
            raise ValueError(f"Env id for visualization must be in [0, {num_envs - 1}], got {env_id}.")
        selected_env_ids.append(env_id)
    if not selected_env_ids:
        raise ValueError("No env ids were selected for visualization.")
    return tuple(sorted(set(selected_env_ids)))


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
        _reset_stage1_replay_curriculum_state(raw_env, terrain_runtime)
        terrain_runtime.sync_env_origins(raw_env.scene)
        print(
            "[INFO] Stage1 replay terrain mode: all columns "
            f"({_format_stage1_replay_columns(list(range(num_cols)), terrain_runtime)}).",
            flush=True,
        )
        return True

    selected_tensor = torch.tensor(selected_columns, device=raw_env.device, dtype=torch.long)
    terrain_runtime.terrain_types[:] = selected_tensor[torch.remainder(env_ids, selected_tensor.numel())]
    _reset_stage1_replay_curriculum_state(raw_env, terrain_runtime)
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
    if args_cli.replay_episode_length_s is not None:
        if args_cli.replay_episode_length_s <= 0.0:
            raise ValueError("--replay_episode_length_s must be positive.")
        env_cfg.episode_length_s = args_cli.replay_episode_length_s
        print(f"[INFO] Replay episode length override: {env_cfg.episode_length_s:.2f}s", flush=True)
    if args_cli.height_patch_vis_radius <= 0.0:
        raise ValueError("--height_patch_vis_radius must be positive.")
    if args_cli.height_patch_vis_height_offset < 0.0:
        raise ValueError("--height_patch_vis_height_offset must be non-negative.")
    if args_cli.height_patch_vis_color_range_m <= 0.0:
        raise ValueError("--height_patch_vis_color_range_m must be positive.")
    if args_cli.video_crf < 0 or args_cli.video_crf > 51:
        raise ValueError("--video_crf must be between 0 and 51.")
    if args_cli.video and not args_cli.stream_video and args_cli.video_length <= 0:
        raise ValueError("--video_length must be positive when using Gym RecordVideo. Use --stream_video for manual-stop recording.")
    if args_cli.record_camera_views is not None and not args_cli.record_chase_view:
        raise ValueError("--record_camera_views requires --record_chase_view.")
    if args_cli.record_camera_views is not None and not args_cli.stream_video:
        raise ValueError("--record_camera_views requires --stream_video.")
    record_camera_views = _parse_record_camera_views(args_cli.record_camera_views, args_cli.record_camera_view)
    if args_cli.video_resolution is not None:
        env_cfg.viewer.resolution = _parse_video_resolution(args_cli.video_resolution)

    env_cfg.debug.enable_debug_draw = (
        args_cli.show_goal_vis
        or args_cli.show_wheel_slip_vis
        or args_cli.show_height_patch_vis
        or args_cli.create_follow_views
        or args_cli.record_chase_view
    )
    env_cfg.debug.visualize_goal_position = args_cli.show_goal_vis
    env_cfg.debug.visualize_goal_heading = args_cli.show_goal_vis and args_cli.show_goal_heading
    env_cfg.debug.visualize_wheel_slip = args_cli.show_wheel_slip_vis
    env_cfg.debug.visualize_height_patch = args_cli.show_height_patch_vis
    env_cfg.debug.height_patch_visualization_env_indices = _parse_env_indices(
        args_cli.height_patch_vis_envs,
        env_cfg.scene.num_envs,
    )
    env_cfg.debug.height_patch_marker_radius = args_cli.height_patch_vis_radius
    env_cfg.debug.height_patch_marker_height_offset = args_cli.height_patch_vis_height_offset
    env_cfg.debug.height_patch_color_range_m = args_cli.height_patch_vis_color_range_m
    env_cfg.debug.visualize_height_patch_positive_y_axis = args_cli.show_height_patch_axis
    env_cfg.debug.create_follow_views = args_cli.create_follow_views
    env_cfg.debug.follow_view_top_height = args_cli.follow_view_top_height
    env_cfg.debug.follow_view_chase_env_index = args_cli.follow_view_chase_env
    if args_cli.record_chase_view:
        env_cfg.debug.create_follow_views = True
        follow_camera_name = FOLLOW_CAMERA_NAMES[record_camera_views[0]]
        env_cfg.viewer.cam_prim_path = f"/view/env_{args_cli.follow_view_chase_env}/{follow_camera_name}"
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
    if args_cli.record_chase_view and hasattr(env.unwrapped, "_update_follow_views"):
        env.unwrapped._update_follow_views()
    stream_video_paths: dict[str, str] = {}
    if args_cli.video and args_cli.stream_video:
        video_folder = os.path.join(log_dir, "videos", "play")
        os.makedirs(video_folder, exist_ok=True)
        if args_cli.record_chase_view:
            stream_video_paths = _build_stream_video_paths(
                video_folder,
                resume_path,
                args_cli.video_output_name,
                record_camera_views,
            )
        else:
            stream_video_paths = {
                "viewport": _build_stream_video_paths(video_folder, resume_path, args_cli.video_output_name, ("viewport",))[
                    "viewport"
                ]
            }
            print(f"[INFO] Streaming video to: {stream_video_paths['viewport']}")
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
    playback_load_cfg = _playback_load_cfg_for_checkpoint(resume_path)
    if playback_load_cfg is not None:
        print("[INFO] Detected warm-start checkpoint; loading actor/critic only.", flush=True)
        runner.load(resume_path, load_cfg=playback_load_cfg)
    else:
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
    follow_view_recorders: list[dict[str, object]] = []
    if stream_video_paths and args_cli.record_chase_view:
        follow_view_recorders = _open_follow_view_stream_recorders(
            env.unwrapped,
            stream_video_paths,
            fps=round(1.0 / dt),
        )
    elif stream_video_paths:
        video_writer = _open_stream_writer(stream_video_paths["viewport"], fps=round(1.0 / dt))
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
            if follow_view_recorders:
                _append_follow_view_frames(follow_view_recorders)
                timestep += 1
                if timestep % 600 == 0:
                    if args_cli.video_length > 0:
                        print(f"[INFO] Streamed {timestep}/{args_cli.video_length} video frames", flush=True)
                    else:
                        print(f"[INFO] Streamed {timestep} video frames", flush=True)
                if args_cli.video_length > 0 and timestep >= args_cli.video_length:
                    break
            elif video_writer is not None:
                frame = env.unwrapped.render(recompute=False)
                if frame is not None:
                    video_writer.append_data(frame)
                timestep += 1
                if timestep % 600 == 0:
                    if args_cli.video_length > 0:
                        print(f"[INFO] Streamed {timestep}/{args_cli.video_length} video frames", flush=True)
                    else:
                        print(f"[INFO] Streamed {timestep} video frames", flush=True)
                if args_cli.video_length > 0 and timestep >= args_cli.video_length:
                    break
            elif args_cli.video:
                timestep += 1
                if args_cli.video_length > 0 and timestep == args_cli.video_length:
                    break
            sleep_time = dt - (time.time() - start_time)
            if args_cli.real_time and sleep_time > 0:
                time.sleep(sleep_time)
    finally:
        if follow_view_recorders:
            _close_follow_view_stream_recorders(follow_view_recorders)
        if video_writer is not None:
            video_writer.close()
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
