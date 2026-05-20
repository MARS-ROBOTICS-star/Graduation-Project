"""RSL-RL 回放入口。"""

from __future__ import annotations

import argparse
import csv
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
GLOBAL_DOLLY_VIEW_NAME = "global_dolly"
GLOBAL_DOLLY_CAMERA_PATH = "/view/global/obs_to_flat_dolly_camera"

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
    "--video_output_dir",
    type=str,
    default=None,
    help="Override mp4 output directory. Defaults to <checkpoint_run>/videos/play.",
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
parser.add_argument("--seed", type=int, default=None)
parser.add_argument("--task", type=str, default="CompleteCar-Stage0", choices=TASK_CHOICES)
parser.add_argument("--agent", type=str, default="rsl_rl_cfg_entry_point")
parser.add_argument("--checkpoint", type=str, default=None)
parser.add_argument("--load_run", type=str, default=None)
parser.add_argument("--real-time", action="store_true", default=False)
parser.add_argument(
    "--zero_actions",
    action="store_true",
    default=False,
    help="Force zero policy actions during playback. Useful for stationary debug visualization.",
)
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
parser.add_argument(
    "--record_global_dolly_view",
    action="store_true",
    default=False,
    help=(
        "Create a moving global camera for Stage1 replay. The default path starts near obs row 1 "
        "and moves toward flat row 19 with a low oblique view."
    ),
)
parser.add_argument("--global_dolly_camera_path", type=str, default=GLOBAL_DOLLY_CAMERA_PATH)
parser.add_argument("--global_dolly_duration_steps", type=int, default=2000)
parser.add_argument("--global_dolly_start_row", type=int, default=1)
parser.add_argument("--global_dolly_start_columns", type=str, default="obs")
parser.add_argument("--global_dolly_end_row", type=int, default=19)
parser.add_argument("--global_dolly_end_columns", type=str, default="flat")
parser.add_argument(
    "--global_dolly_start_eye_offset",
    type=str,
    default="-10,8,4.8",
    help="Comma-separated xyz offset from the start terrain focus.",
)
parser.add_argument(
    "--global_dolly_start_target_offset",
    type=str,
    default="3,-2,0.35",
    help="Comma-separated xyz offset from the start terrain focus.",
)
parser.add_argument(
    "--global_dolly_end_eye_offset",
    type=str,
    default="-10,8,3.8",
    help="Comma-separated xyz offset from the final terrain focus.",
)
parser.add_argument(
    "--global_dolly_end_target_offset",
    type=str,
    default="3,-1,0.35",
    help="Comma-separated xyz offset from the final terrain focus.",
)
parser.add_argument("--global_dolly_start_focal_length", type=float, default=24.0)
parser.add_argument("--global_dolly_end_focal_length", type=float, default=28.0)
parser.add_argument(
    "--capture_terrain_row_stills",
    action="store_true",
    default=False,
    help=(
        "Capture one still image for each unique terrain name present in the replay envs, "
        "using the current replay row/column assignment."
    ),
)
parser.add_argument(
    "--capture_terrain_only_stills",
    action="store_true",
    default=False,
    help=(
        "Capture one terrain-only still image for each unique terrain type at --still_terrain_row. "
        "The camera targets terrain tile origins directly instead of env/robot origins."
    ),
)
parser.add_argument("--still_terrain_row", type=int, default=19)
parser.add_argument(
    "--still_resolution",
    type=str,
    default="3840x2160",
    help="Still image resolution as WIDTHxHEIGHT, for example 3840x2160.",
)
parser.add_argument("--still_output_dir", type=str, default=None)
parser.add_argument("--still_camera_eye_offset", type=str, default="-7,-6,4.5")
parser.add_argument("--still_camera_target_offset", type=str, default="2,0,0.45")
parser.add_argument("--still_camera_focal_length", type=float, default=32.0)
parser.add_argument(
    "--terrain_only_camera_height",
    type=float,
    default=2.8,
    help="Top-down terrain-only still camera height above the row tile origin, in meters.",
)
parser.add_argument(
    "--terrain_only_camera_focal_length",
    type=float,
    default=8.0,
    help="Focal length for top-down terrain-only stills.",
)
parser.add_argument("--still_settle_steps", type=int, default=8)
parser.add_argument("--follow_view_top_height", type=float, default=3.5)
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
    "--terrain_replay_level",
    type=int,
    default=None,
    help=(
        "Start Stage1 replay from this terrain row and use it as the minimum reset floor. "
        "By default, row progression can continue after waypoint hits."
    ),
)
parser.add_argument(
    "--terrain_replay_level_range",
    type=str,
    default=None,
    help=(
        "Randomize initial Stage1 replay rows within an inclusive range, such as '0:4' or '0,4'. "
        "Rows are spread independently inside each selected terrain column to avoid all envs clustering "
        "on one row. Mutually exclusive with --terrain_replay_level."
    ),
)
parser.add_argument(
    "--terrain_replay_lock_level",
    action="store_true",
    default=False,
    help="Force every Stage1 replay reset back to --terrain_replay_level instead of allowing row progression.",
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
parser.add_argument(
    "--max_play_steps",
    type=int,
    default=0,
    help="Stop playback after this many control steps. Use 0 to run until the GUI closes or the process is interrupted.",
)
parser.add_argument(
    "--stop_after_continuous_terrain_completions",
    type=int,
    default=0,
    help=(
        "Stop Stage1 replay selection after this many envs continuously reach terrain_column_completed "
        "from the initial reset without timeout/stuck/low-quality/far/joint/roll failures."
    ),
)
parser.add_argument(
    "--selection_max_pre_completion_resets",
    type=int,
    default=0,
    help=(
        "When --stop_after_continuous_terrain_completions is used, keep an env eligible until it has "
        "more than this many pre-completion reset/failure events."
    ),
)
parser.add_argument(
    "--print_reset_causes",
    action="store_true",
    default=False,
    help="Print aggregated reset causes whenever any replay env resets.",
)
parser.add_argument(
    "--record_until_terrain_completion",
    action="store_true",
    default=False,
    help=(
        "For Stage1 recording, keep recording until the selected env reaches terrain_column_completed, "
        "then continue for --record_completion_padding_steps frames."
    ),
)
parser.add_argument(
    "--record_completion_env",
    type=int,
    default=-1,
    help="Env id whose terrain-column completion controls --record_until_terrain_completion. Defaults to follow env.",
)
parser.add_argument(
    "--record_completion_padding_steps",
    type=int,
    default=0,
    help="Extra control frames to record after the selected env reaches terrain_column_completed.",
)
parser.add_argument(
    "--record_completion_max_pre_completion_resets",
    type=int,
    default=-1,
    help=(
        "When --record_until_terrain_completion is used, fail recording if the selected env has more "
        "than this many pre-completion reset events. Use -1 to disable this guard."
    ),
)
parser.add_argument(
    "--record_reward_trace",
    action="store_true",
    default=False,
    help=(
        "Record per-control-step reward components and reward diagnostics to CSV during replay. "
        "The trace includes reward terms, terrain features, done terms, row/col context, commands, and actions."
    ),
)
parser.add_argument(
    "--reward_trace_output",
    type=str,
    default=None,
    help=(
        "CSV output path for --record_reward_trace. If omitted, a timestamped CSV is written under "
        "<run>/reward_traces/."
    ),
)
parser.add_argument(
    "--reward_trace_envs",
    type=str,
    default="all",
    help="Env ids to record for --record_reward_trace, such as '0', '0,3', or 'all'.",
)
parser.add_argument(
    "--reward_trace_flush_interval",
    type=int,
    default=120,
    help="Flush reward trace CSV after this many control steps.",
)
AppLauncher.add_app_launcher_args(parser)
args_cli, hydra_args = parser.parse_known_args()

if (
    args_cli.video
    or args_cli.record_global_dolly_view
    or args_cli.capture_terrain_row_stills
    or args_cli.capture_terrain_only_stills
):
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
import isaaclab.sim as sim_utils
from isaaclab.utils.assets import retrieve_file_path
from isaaclab.utils.dict import print_dict

from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper, export_policy_as_jit, export_policy_as_onnx

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import get_checkpoint_path
from isaaclab_tasks.utils.hydra import hydra_task_config

import complete_car_lab  # noqa: F401
from complete_car_lab.tasks.direct.complete_car.assets.robot_cfg import BALL_JOINT_NAMES
from complete_car_lab.tasks.direct.complete_car.mdp import curriculum as mdp_curriculum
from complete_car_lab.tasks.direct.complete_car.utils.math_utils import wrap_to_pi_tensor


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
        render_product_path = render_product if isinstance(render_product, str) else render_product.path
        annotator = rep.AnnotatorRegistry.get_annotator("rgb", device="cpu")
        annotator.attach([render_product_path])
        writer = _open_stream_writer(output_path, fps)
        recorders.append(
            {
                "view": view,
                "path": output_path,
                "render_product": render_product,
                "render_product_path": render_product_path,
                "annotator": annotator,
                "writer": writer,
            }
        )
        print(f"[INFO] Streaming {view} camera video to: {output_path}", flush=True)
    return recorders


def _open_global_dolly_stream_recorder(
    raw_env,
    stream_video_paths: dict[str, str],
    fps: int,
) -> list[dict[str, object]]:
    import omni.replicator.core as rep

    output_path = stream_video_paths[GLOBAL_DOLLY_VIEW_NAME]
    camera_prim_path = args_cli.global_dolly_camera_path
    render_product = rep.create.render_product(camera_prim_path, resolution=raw_env.cfg.viewer.resolution)
    render_product_path = render_product if isinstance(render_product, str) else render_product.path
    annotator = rep.AnnotatorRegistry.get_annotator("rgb", device="cpu")
    annotator.attach([render_product_path])
    writer = _open_stream_writer(output_path, fps)
    print(f"[INFO] Streaming global dolly camera video to: {output_path}", flush=True)
    return [
        {
            "view": GLOBAL_DOLLY_VIEW_NAME,
            "path": output_path,
            "render_product": render_product,
            "render_product_path": render_product_path,
            "annotator": annotator,
            "writer": writer,
        }
    ]


def _append_follow_view_frames(raw_env, recorders: list[dict[str, object]]) -> int:
    import numpy as np

    raw_env.sim.render()
    written_count = 0
    for recorder in recorders:
        annotator = recorder["annotator"]
        writer = recorder["writer"]
        rgb_data = annotator.get_data()
        rgb_data = np.frombuffer(rgb_data, dtype=np.uint8).reshape(*rgb_data.shape)
        if rgb_data.size == 0:
            continue
        writer.append_data(rgb_data[:, :, :3])
        written_count += 1
    return written_count


def _close_follow_view_stream_recorders(recorders: list[dict[str, object]]) -> None:
    for recorder in recorders:
        writer = recorder.get("writer")
        annotator = recorder.get("annotator")
        render_product = recorder.get("render_product_path")
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
    if "discrete obstacles" in columns_by_name:
        obstacle_columns = list(columns_by_name["discrete obstacles"])
        columns_by_name.setdefault("obstacle", obstacle_columns)
        columns_by_name.setdefault("obstacles", obstacle_columns)
        columns_by_name.setdefault("obs", obstacle_columns)

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


def _format_replay_level_mode(level: int | None, lock_level: bool) -> str:
    if level is None:
        return ""
    mode = "locked" if lock_level else "start"
    return f" {mode} row {level}"


def _parse_stage1_replay_level_range(raw_range: str | None) -> tuple[int, int] | None:
    if raw_range is None:
        return None
    normalized = raw_range.strip().replace("-", ":").replace(",", ":")
    parts = [part.strip() for part in normalized.split(":") if part.strip()]
    if len(parts) != 2:
        raise ValueError("--terrain_replay_level_range must use MIN:MAX format, for example 0:4.")
    try:
        low, high = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise ValueError("--terrain_replay_level_range must contain integer row indices.") from exc
    if low > high:
        low, high = high, low
    return low, high


def _format_replay_level_range_mode(level_range: tuple[int, int] | None) -> str:
    if level_range is None:
        return ""
    return f" random rows {level_range[0]}-{level_range[1]}"


def _clamp_stage1_replay_level(level: int, terrain_runtime) -> int:
    max_level = max(int(terrain_runtime.max_terrain_level) - 1, 0)
    return int(max(0, min(int(level), max_level)))


def _set_stage1_replay_level(raw_env, terrain_runtime, level: int | None, *, lock_level: bool = False) -> int | None:
    if level is None:
        if hasattr(raw_env, "_stage1_replay_fixed_terrain_level"):
            raw_env._stage1_replay_fixed_terrain_level = None
        return None

    replay_level = _clamp_stage1_replay_level(level, terrain_runtime)
    raw_env._stage1_replay_fixed_terrain_level = replay_level if lock_level else None
    terrain_runtime.terrain_levels[:] = replay_level
    level_floor = getattr(raw_env, "_stage1_terrain_level_floor", None)
    if level_floor is not None:
        level_floor.fill_(replay_level)
    return replay_level


def _set_stage1_replay_level_range(
    raw_env,
    terrain_runtime,
    level_range: tuple[int, int] | None,
) -> tuple[int, int] | None:
    if level_range is None:
        return None
    if terrain_runtime.terrain_levels is None or terrain_runtime.terrain_types is None:
        raise RuntimeError("Stage1 terrain runtime has not initialized terrain levels/types.")

    low = _clamp_stage1_replay_level(level_range[0], terrain_runtime)
    high = _clamp_stage1_replay_level(level_range[1], terrain_runtime)
    if low > high:
        low, high = high, low
    if hasattr(raw_env, "_stage1_replay_fixed_terrain_level"):
        raw_env._stage1_replay_fixed_terrain_level = None

    span = high - low + 1
    levels = torch.empty_like(terrain_runtime.terrain_levels)
    terrain_types = terrain_runtime.terrain_types
    for terrain_type in torch.unique(terrain_types):
        env_ids = torch.nonzero(terrain_types == terrain_type, as_tuple=False).flatten()
        if env_ids.numel() == 0:
            continue
        offset = int(torch.randint(0, span, (1,), device=terrain_runtime.device).item())
        permutation = torch.randperm(int(env_ids.numel()), device=terrain_runtime.device)
        assigned = low + torch.remainder(permutation + offset, span)
        levels[env_ids] = assigned.to(dtype=levels.dtype)
    terrain_runtime.terrain_levels[:] = levels

    level_floor = getattr(raw_env, "_stage1_terrain_level_floor", None)
    if level_floor is not None:
        level_floor.copy_(terrain_runtime.terrain_levels)
    return low, high


def _reset_stage1_replay_curriculum_state(
    raw_env,
    terrain_runtime,
    replay_level: int | None = None,
    *,
    lock_level: bool = False,
    replay_level_range: tuple[int, int] | None = None,
) -> int | None:
    """Keep Stage1 replay column selection from being overwritten by reset recycling."""
    num_cols = int(terrain_runtime._terrain_cfg.num_cols)
    if replay_level_range is not None:
        selected_level = None
        _set_stage1_replay_level_range(raw_env, terrain_runtime, replay_level_range)
    else:
        selected_level = _set_stage1_replay_level(raw_env, terrain_runtime, replay_level, lock_level=lock_level)
    if selected_level is None and replay_level_range is None:
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
    level_floor = getattr(raw_env, "_stage1_terrain_level_floor", None)
    if level_floor is not None:
        level_floor.copy_(terrain_runtime.terrain_levels)
    if hasattr(raw_env, "_stage1_recycle_cursor"):
        raw_env._stage1_recycle_cursor = 0
    return selected_level


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


def _scalar_log_value(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, torch.Tensor):
        if value.numel() == 0:
            return None
        return float(torch.nan_to_num(value.detach().float().mean(), nan=0.0, posinf=0.0, neginf=0.0).item())
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_replay_joint_limit_details(raw_env, dones: torch.Tensor) -> str | None:
    done_terms = getattr(raw_env, "_last_step_done_terms", None)
    if done_terms is None:
        done_terms = getattr(raw_env, "_last_done_terms", {})
    ball_joint_limit_mask = done_terms.get("ball_joint_out_of_bounds") if isinstance(done_terms, dict) else None
    if ball_joint_limit_mask is None or not torch.any(dones & ball_joint_limit_mask):
        return None

    env_ids = torch.nonzero(dones & ball_joint_limit_mask, as_tuple=False).flatten()
    if env_ids.numel() == 0:
        return None

    ball_joint_ids = getattr(raw_env, "_ball_joint_ids", None)
    if ball_joint_ids is None:
        return None
    saved_pos = getattr(raw_env, "_last_ball_joint_out_of_bounds_joint_pos", None)
    saved_mask = getattr(raw_env, "_last_ball_joint_out_of_bounds_joint_mask", None)
    if saved_pos is not None and saved_mask is not None:
        joint_pos = saved_pos[env_ids]
        violation = saved_mask[env_ids]
    else:
        joint_pos = wrap_to_pi_tensor(raw_env.robot.data.joint_pos[env_ids][:, ball_joint_ids])
        lower = joint_pos.new_tensor(raw_env.cfg.terminations.ball_joint_pos_lower_limits).unsqueeze(0)
        upper = joint_pos.new_tensor(raw_env.cfg.terminations.ball_joint_pos_upper_limits).unsqueeze(0)
        violation = (joint_pos < lower) | (joint_pos > upper)
    lower = joint_pos.new_tensor(raw_env.cfg.terminations.ball_joint_pos_lower_limits).unsqueeze(0)
    upper = joint_pos.new_tensor(raw_env.cfg.terminations.ball_joint_pos_upper_limits).unsqueeze(0)
    if not torch.any(violation):
        return None

    env_local, joint_index = torch.nonzero(violation, as_tuple=True)
    details: list[str] = []
    for env_offset, joint_offset in zip(env_local[:4], joint_index[:4], strict=False):
        env_id = int(env_ids[env_offset].item())
        joint_id = int(joint_offset.item())
        value = float(joint_pos[env_offset, joint_offset].item())
        low = float(lower[0, joint_offset].item())
        high = float(upper[0, joint_offset].item())
        side = "<" if value < low else ">"
        limit = low if value < low else high
        details.append(f"env{env_id}:{BALL_JOINT_NAMES[joint_id]}={value:.3f}{side}{limit:.3f}")
    if violation.numel() > 4:
        remaining = int(torch.count_nonzero(violation).item()) - len(details)
        if remaining > 0:
            details.append(f"+{remaining}_more")
    return "joint_oob=" + ",".join(details)


def _print_replay_reset_causes(timestep: int, dones: torch.Tensor, extras: dict, raw_env=None) -> None:
    if dones is None or not torch.any(dones):
        return
    done_count = int(torch.count_nonzero(dones).item())
    log = extras.get("log", {}) if isinstance(extras, dict) else {}

    fields = (
        ("terminated", "Termination/terminated_rate"),
        ("timeout", "Termination/time_out_rate"),
        ("stuck", "Termination/stuck_timeout_rate"),
        ("completed", "Termination/terrain_column_completed_rate"),
        ("low_quality", "Termination/low_quality_terrain_hit_rate"),
        ("far", "Termination/far_from_target_rate"),
        ("joint_limit", "Termination/ball_joint_limit_rate"),
        ("roll_limit", "Termination/orientation_out_of_bounds_rate"),
        ("waypoint_hit", "episode/waypoint_hit_rate"),
        ("row_progress", "terrain/row_progress_at_reset"),
        ("move_down", "terrain/move_down_ratio"),
        ("stuck_move_down", "terrain/stuck_move_down_ratio"),
        ("level_after", "terrain/level_after_reset"),
    )

    parts = [f"[RESET] step={timestep}", f"done_envs={done_count}"]
    for label, key in fields:
        value = _scalar_log_value(log.get(key))
        if value is None:
            continue
        parts.append(f"{label}={value:.3f}")
    if raw_env is not None:
        joint_limit_details = _format_replay_joint_limit_details(raw_env, dones)
        if joint_limit_details is not None:
            parts.append(joint_limit_details)
    print(" ".join(parts), flush=True)


def _print_stage1_replay_level_summary(raw_env, label: str) -> None:
    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    if (
        terrain_runtime is None
        or terrain_runtime.terrain_levels is None
        or terrain_runtime.terrain_types is None
        or terrain_runtime.terrain_levels.numel() == 0
    ):
        return
    levels = terrain_runtime.terrain_levels.detach().to(torch.long)
    types = terrain_runtime.terrain_types.detach().to(torch.long)
    parts = [
        f"[INFO] Stage1 replay levels {label}:",
        f"min={int(torch.min(levels).item())}",
        f"max={int(torch.max(levels).item())}",
        f"mean={float(torch.mean(levels.float()).item()):.2f}",
    ]
    for terrain_type in torch.unique(types):
        mask = types == terrain_type
        column = int(terrain_type.item())
        column_levels = levels[mask]
        parts.append(
            f"col{column:02d}:{_terrain_column_name(terrain_runtime, column).replace(' ', '_')}"
            f"={int(torch.min(column_levels).item())}-{int(torch.max(column_levels).item())}"
        )
    print(" ".join(parts), flush=True)


def _parse_float_triplet(raw_value: str, arg_name: str) -> tuple[float, float, float]:
    parts = [part.strip() for part in raw_value.split(",")]
    if len(parts) != 3:
        raise ValueError(f"{arg_name} must contain three comma-separated numbers, got '{raw_value}'.")
    try:
        return tuple(float(part) for part in parts)  # type: ignore[return-value]
    except ValueError as exc:
        raise ValueError(f"{arg_name} must contain valid numbers, got '{raw_value}'.") from exc


def _smoothstep(value: float) -> float:
    clamped = max(0.0, min(1.0, float(value)))
    return clamped * clamped * (3.0 - 2.0 * clamped)


def _lerp_triplet(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    ratio: float,
) -> tuple[float, float, float]:
    return tuple(start[index] + (end[index] - start[index]) * ratio for index in range(3))


def _add_triplet(
    lhs: tuple[float, float, float],
    rhs: tuple[float, float, float],
) -> tuple[float, float, float]:
    return tuple(lhs[index] + rhs[index] for index in range(3))


def _ensure_camera_prim(camera_prim_path: str, focal_length: float) -> None:
    if not camera_prim_path.startswith("/"):
        raise ValueError("--global_dolly_camera_path must be an absolute prim path.")
    stage = sim_utils.get_current_stage()
    path_parts = [part for part in camera_prim_path.strip("/").split("/") if part]
    if not path_parts:
        raise ValueError("--global_dolly_camera_path must be an absolute prim path.")
    parent_path = ""
    for part in path_parts[:-1]:
        parent_path = f"{parent_path}/{part}"
        if not stage.GetPrimAtPath(parent_path).IsValid():
            sim_utils.create_prim(parent_path, "Xform")
    if not stage.GetPrimAtPath(camera_prim_path).IsValid():
        sim_utils.create_prim(
            camera_prim_path,
            "Camera",
            attributes={
                "focalLength": float(focal_length),
                "horizontalAperture": 20.955,
                "clippingRange": (0.01, 1000.0),
            },
        )


def _set_camera_focal_length(camera_prim_path: str, focal_length: float) -> None:
    stage = sim_utils.get_current_stage()
    prim = stage.GetPrimAtPath(camera_prim_path)
    if not prim.IsValid():
        return
    focal_attr = prim.GetAttribute("focalLength")
    if focal_attr.IsValid():
        focal_attr.Set(float(focal_length))


def _dolly_focus_for_tiles(
    terrain_runtime,
    row: int,
    columns_selector: str,
) -> tuple[float, float, float]:
    selected_columns = _parse_stage1_replay_columns(columns_selector, terrain_runtime)
    num_cols = int(terrain_runtime._terrain_cfg.num_cols)
    if selected_columns is None:
        selected_columns = list(range(num_cols))
    if not selected_columns:
        raise ValueError(f"No terrain columns selected for global dolly selector '{columns_selector}'.")
    selected_row = _clamp_stage1_replay_level(row, terrain_runtime)
    levels = torch.full(
        (len(selected_columns),),
        int(selected_row),
        dtype=torch.long,
        device=terrain_runtime.device,
    )
    columns = torch.tensor(selected_columns, dtype=torch.long, device=terrain_runtime.device)
    origins = terrain_runtime.get_tile_origins(levels, columns)
    focus = torch.mean(origins, dim=0).detach().cpu()
    return (float(focus[0].item()), float(focus[1].item()), float(focus[2].item()))


def _update_global_dolly_camera(raw_env, timestep: int) -> None:
    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    if terrain_runtime is None or not getattr(terrain_runtime, "generator_enabled", False):
        raise RuntimeError("--record_global_dolly_view requires generated Stage1 terrain.")
    if terrain_runtime.terrain_levels is None or terrain_runtime.terrain_types is None:
        raise RuntimeError("Stage1 terrain runtime has not initialized terrain levels/types.")

    start_focus = _dolly_focus_for_tiles(
        terrain_runtime,
        args_cli.global_dolly_start_row,
        args_cli.global_dolly_start_columns,
    )
    end_focus = _dolly_focus_for_tiles(
        terrain_runtime,
        args_cli.global_dolly_end_row,
        args_cli.global_dolly_end_columns,
    )
    start_eye = _add_triplet(start_focus, _parse_float_triplet(args_cli.global_dolly_start_eye_offset, "--global_dolly_start_eye_offset"))
    start_target = _add_triplet(
        start_focus,
        _parse_float_triplet(args_cli.global_dolly_start_target_offset, "--global_dolly_start_target_offset"),
    )
    end_eye = _add_triplet(end_focus, _parse_float_triplet(args_cli.global_dolly_end_eye_offset, "--global_dolly_end_eye_offset"))
    end_target = _add_triplet(
        end_focus,
        _parse_float_triplet(args_cli.global_dolly_end_target_offset, "--global_dolly_end_target_offset"),
    )
    duration_steps = max(int(args_cli.global_dolly_duration_steps), 1)
    ratio = _smoothstep(float(timestep) / float(duration_steps))
    eye = _lerp_triplet(start_eye, end_eye, ratio)
    target = _lerp_triplet(start_target, end_target, ratio)
    focal_length = args_cli.global_dolly_start_focal_length + (
        args_cli.global_dolly_end_focal_length - args_cli.global_dolly_start_focal_length
    ) * ratio
    camera_prim_path = args_cli.global_dolly_camera_path
    _ensure_camera_prim(camera_prim_path, focal_length)
    _set_camera_focal_length(camera_prim_path, focal_length)
    raw_env.sim.set_camera_view(eye=eye, target=target, camera_prim_path=camera_prim_path)


def _slugify_filename(value: str) -> str:
    slug = _normalize_selector(value).replace(" ", "_")
    slug = re.sub(r"[^a-z0-9_]+", "_", slug)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "terrain"


def _collect_unique_terrain_still_envs(raw_env) -> list[int]:
    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    if terrain_runtime is None or terrain_runtime.terrain_types is None:
        return list(range(int(raw_env.num_envs)))
    selected_env_ids: list[int] = []
    seen_names: set[str] = set()
    for env_id in range(int(raw_env.num_envs)):
        column = int(terrain_runtime.terrain_types[env_id].item())
        terrain_name = _terrain_column_name(terrain_runtime, column)
        key = _normalize_selector(terrain_name)
        if key in seen_names:
            continue
        seen_names.add(key)
        selected_env_ids.append(env_id)
    return selected_env_ids


def _capture_terrain_row_stills(raw_env, output_dir: str, resolution: tuple[int, int]) -> list[str]:
    import imageio.v2 as imageio
    import numpy as np
    import omni.replicator.core as rep

    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    if terrain_runtime is None or terrain_runtime.terrain_levels is None or terrain_runtime.terrain_types is None:
        raise RuntimeError("--capture_terrain_row_stills requires initialized Stage1 terrain replay.")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    eye_offset = _parse_float_triplet(args_cli.still_camera_eye_offset, "--still_camera_eye_offset")
    target_offset = _parse_float_triplet(args_cli.still_camera_target_offset, "--still_camera_target_offset")
    focal_length = float(args_cli.still_camera_focal_length)
    if focal_length <= 0.0:
        raise ValueError("--still_camera_focal_length must be positive.")

    for _ in range(max(int(args_cli.still_settle_steps), 0)):
        raw_env.sim.render()

    saved_paths: list[str] = []
    for env_id in _collect_unique_terrain_still_envs(raw_env):
        column = int(terrain_runtime.terrain_types[env_id].item())
        row = int(terrain_runtime.terrain_levels[env_id].item())
        terrain_name = _terrain_column_name(terrain_runtime, column)
        origin = raw_env.scene.env_origins[env_id].detach().cpu()
        focus = (float(origin[0].item()), float(origin[1].item()), float(origin[2].item()))
        eye = _add_triplet(focus, eye_offset)
        target = _add_triplet(focus, target_offset)
        terrain_slug = _slugify_filename(terrain_name)
        camera_path = f"/view/stills/{terrain_slug}_row{row:02d}_env{env_id:02d}_camera"
        _ensure_camera_prim(camera_path, focal_length)
        _set_camera_focal_length(camera_path, focal_length)
        raw_env.sim.set_camera_view(eye=eye, target=target, camera_prim_path=camera_path)

        render_product = rep.create.render_product(camera_path, resolution=resolution)
        render_product_path = render_product if isinstance(render_product, str) else render_product.path
        annotator = rep.AnnotatorRegistry.get_annotator("rgb", device="cpu")
        annotator.attach([render_product_path])
        try:
            for _ in range(4):
                raw_env.sim.render()
            rgb_data = annotator.get_data()
            rgb_array = np.frombuffer(rgb_data, dtype=np.uint8).reshape(*rgb_data.shape)
            if rgb_array.size == 0:
                raise RuntimeError(f"Still camera did not return RGB data for env {env_id}.")
            file_path = output_path / f"row{row:02d}_col{column:02d}_{terrain_slug}_env{env_id:02d}_4k.png"
            imageio.imwrite(file_path, rgb_array[:, :, :3])
            saved_paths.append(str(file_path))
            print(f"[INFO] Saved terrain still: {file_path}", flush=True)
        finally:
            annotator.detach([render_product_path])
    return saved_paths


def _unique_terrain_columns(terrain_runtime) -> list[int]:
    num_cols = int(terrain_runtime._terrain_cfg.num_cols)
    selected_columns: list[int] = []
    seen_names: set[str] = set()
    for column in range(num_cols):
        terrain_name = _terrain_column_name(terrain_runtime, column)
        key = _normalize_selector(terrain_name)
        if key in seen_names:
            continue
        seen_names.add(key)
        selected_columns.append(column)
    return selected_columns


def _capture_terrain_only_stills(raw_env, output_dir: str, resolution: tuple[int, int]) -> list[str]:
    import imageio.v2 as imageio
    import numpy as np
    import omni.replicator.core as rep

    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    if terrain_runtime is None or not getattr(terrain_runtime, "generator_enabled", False):
        raise RuntimeError("--capture_terrain_only_stills requires generated Stage1 terrain.")
    if terrain_runtime.terrain_levels is None or terrain_runtime.terrain_types is None:
        raise RuntimeError("Stage1 terrain runtime has not initialized terrain levels/types.")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    terrain_row = _clamp_stage1_replay_level(args_cli.still_terrain_row, terrain_runtime)
    camera_height = float(args_cli.terrain_only_camera_height)
    focal_length = float(args_cli.terrain_only_camera_focal_length)
    if camera_height <= 0.0:
        raise ValueError("--terrain_only_camera_height must be positive.")
    if focal_length <= 0.0:
        raise ValueError("--terrain_only_camera_focal_length must be positive.")

    for _ in range(max(int(args_cli.still_settle_steps), 0)):
        raw_env.sim.render()

    saved_paths: list[str] = []
    selected_columns = _unique_terrain_columns(terrain_runtime)
    levels = torch.full((len(selected_columns),), terrain_row, dtype=torch.long, device=terrain_runtime.device)
    columns = torch.tensor(selected_columns, dtype=torch.long, device=terrain_runtime.device)
    origins = terrain_runtime.get_tile_origins(levels, columns).detach().cpu()

    for origin, column in zip(origins, selected_columns, strict=False):
        terrain_name = _terrain_column_name(terrain_runtime, column)
        focus = (float(origin[0].item()), float(origin[1].item()), float(origin[2].item()))
        eye = (focus[0], focus[1], focus[2] + camera_height)
        target = focus
        terrain_slug = _slugify_filename(terrain_name)
        camera_path = f"/view/terrain_stills/{terrain_slug}_row{terrain_row:02d}_camera"
        _ensure_camera_prim(camera_path, focal_length)
        _set_camera_focal_length(camera_path, focal_length)
        raw_env.sim.set_camera_view(eye=eye, target=target, camera_prim_path=camera_path)

        render_product = rep.create.render_product(camera_path, resolution=resolution)
        render_product_path = render_product if isinstance(render_product, str) else render_product.path
        annotator = rep.AnnotatorRegistry.get_annotator("rgb", device="cpu")
        annotator.attach([render_product_path])
        try:
            for _ in range(4):
                raw_env.sim.render()
            rgb_data = annotator.get_data()
            rgb_array = np.frombuffer(rgb_data, dtype=np.uint8).reshape(*rgb_data.shape)
            if rgb_array.size == 0:
                raise RuntimeError(f"Terrain still camera did not return RGB data for column {column}.")
            file_path = output_path / f"row{terrain_row:02d}_col{column:02d}_{terrain_slug}_terrain_only_4k.png"
            imageio.imwrite(file_path, rgb_array[:, :, :3])
            saved_paths.append(str(file_path))
            print(f"[INFO] Saved terrain-only still: {file_path}", flush=True)
        finally:
            annotator.detach([render_product_path])
    return saved_paths


def _csv_cell_from_scalar(value) -> float | int | str:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    return str(value)


def _tensor_item_to_csv(value: torch.Tensor) -> float | int:
    if value.dtype == torch.bool:
        return int(bool(value.item()))
    return float(torch.nan_to_num(value.detach().float(), nan=0.0, posinf=0.0, neginf=0.0).item())


def _add_trace_tensor_value(row: dict[str, object], name: str, value, env_id: int, num_envs: int) -> None:
    if value is None:
        return
    if isinstance(value, torch.Tensor):
        tensor = value.detach()
        if tensor.numel() == 0:
            return
        if tensor.ndim > 0 and tensor.shape[0] == num_envs:
            tensor = tensor[env_id]
        flat = tensor.reshape(-1)
        if flat.numel() == 1:
            row[name] = _tensor_item_to_csv(flat[0])
        else:
            for index, item in enumerate(flat):
                row[f"{name}_{index}"] = _tensor_item_to_csv(item)
        return
    try:
        row[name] = _csv_cell_from_scalar(value)
    except (TypeError, ValueError):
        row[name] = str(value)


def _add_trace_mapping(
    row: dict[str, object],
    prefix: str,
    mapping: dict | None,
    env_id: int,
    num_envs: int,
) -> None:
    if not isinstance(mapping, dict):
        return
    for key in sorted(mapping.keys()):
        _add_trace_tensor_value(row, f"{prefix}{key}", mapping[key], env_id, num_envs)


def _terrain_level_for_env(raw_env, env_id: int) -> int | None:
    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    if terrain_runtime is None or terrain_runtime.terrain_levels is None:
        return None
    return int(terrain_runtime.terrain_levels[env_id].item())


def _terrain_column_for_env(raw_env, env_id: int) -> int | None:
    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    if terrain_runtime is None or terrain_runtime.terrain_types is None:
        return None
    return int(terrain_runtime.terrain_types[env_id].item())


def _build_reward_trace_row(
    raw_env,
    timestep: int,
    env_id: int,
    rewards: torch.Tensor | None,
    dones: torch.Tensor | None,
    policy_actions: torch.Tensor | None,
) -> dict[str, object]:
    num_envs = int(raw_env.num_envs)
    row: dict[str, object] = {
        "step": int(timestep),
        "time_s": float(timestep) * float(raw_env.step_dt),
        "env_id": int(env_id),
    }
    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    terrain_column = _terrain_column_for_env(raw_env, env_id)
    terrain_level = _terrain_level_for_env(raw_env, env_id)
    if terrain_column is not None:
        row["terrain_col"] = terrain_column
        if terrain_runtime is not None:
            row["terrain_name"] = _terrain_column_name(terrain_runtime, terrain_column)
    if terrain_level is not None:
        row["terrain_level_after_step"] = terrain_level
    if rewards is not None:
        _add_trace_tensor_value(row, "returned_reward", rewards, env_id, num_envs)
    if dones is not None:
        _add_trace_tensor_value(row, "done", dones, env_id, num_envs)
    _add_trace_tensor_value(row, "episode_length_step", getattr(raw_env, "episode_length_buf", None), env_id, num_envs)
    _add_trace_tensor_value(row, "total_reward", getattr(raw_env, "_last_total_reward", None), env_id, num_envs)

    commands = getattr(raw_env, "commands", None)
    if isinstance(commands, torch.Tensor) and commands.ndim == 2 and commands.shape[0] == num_envs:
        row["command_x_m"] = _tensor_item_to_csv(commands[env_id, 0])
        row["command_y_m"] = _tensor_item_to_csv(commands[env_id, 1])
        row["command_goal_distance_m"] = float(
            torch.linalg.vector_norm(commands[env_id, :2].detach().float(), dim=0).item()
        )
        if commands.shape[1] > 3:
            row["command_heading_error_rad"] = _tensor_item_to_csv(commands[env_id, 3])

    if policy_actions is not None:
        _add_trace_tensor_value(row, "policy_action", policy_actions, env_id, num_envs)
    _add_trace_tensor_value(row, "env_action", getattr(raw_env, "actions", None), env_id, num_envs)

    _add_trace_mapping(row, "reward__", getattr(raw_env, "_last_reward_components", None), env_id, num_envs)
    _add_trace_mapping(row, "diag__", getattr(raw_env, "_last_reward_diagnostics", None), env_id, num_envs)
    _add_trace_mapping(row, "terrain__", getattr(raw_env, "_last_terrain_feature_diagnostics", None), env_id, num_envs)
    done_terms = getattr(raw_env, "_last_step_done_terms", None)
    if done_terms is None:
        done_terms = getattr(raw_env, "_last_done_terms", None)
    _add_trace_mapping(row, "done__", done_terms, env_id, num_envs)
    return row


class _RewardTraceRecorder:
    def __init__(self, output_path: str, env_ids: tuple[int, ...], flush_interval_steps: int):
        self.output_path = output_path
        self.env_ids = env_ids
        self.flush_interval_steps = max(int(flush_interval_steps), 1)
        self._file = None
        self._writer: csv.DictWriter | None = None
        self._fieldnames: list[str] | None = None
        self._last_flush_step = 0

    def append(
        self,
        raw_env,
        timestep: int,
        rewards: torch.Tensor | None,
        dones: torch.Tensor | None,
        policy_actions: torch.Tensor | None,
    ) -> None:
        rows = [
            _build_reward_trace_row(raw_env, timestep, env_id, rewards, dones, policy_actions)
            for env_id in self.env_ids
        ]
        if not rows:
            return
        if self._writer is None:
            output_path = Path(self.output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self._fieldnames = sorted({key for row in rows for key in row.keys()})
            self._file = output_path.open("w", newline="", encoding="utf-8")
            self._writer = csv.DictWriter(self._file, fieldnames=self._fieldnames, extrasaction="ignore")
            self._writer.writeheader()
            print(f"[INFO] Recording reward trace to: {output_path}", flush=True)
        self._writer.writerows(rows)
        if timestep - self._last_flush_step >= self.flush_interval_steps:
            self.flush()
            self._last_flush_step = timestep

    def flush(self) -> None:
        if self._file is not None:
            self._file.flush()

    def close(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None
        self._writer = None


def _default_reward_trace_path(log_dir: str, resume_path: str) -> str:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    checkpoint_stem = Path(resume_path).stem
    return str(Path(log_dir) / "reward_traces" / f"{checkpoint_stem}_reward_trace_{timestamp}.csv")


def _configure_stage1_replay_terrain(
    raw_env,
    raw_selector: str,
    replay_level: int | None = None,
    *,
    lock_level: bool = False,
    replay_level_range: tuple[int, int] | None = None,
) -> bool:
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
        selected_level = _reset_stage1_replay_curriculum_state(
            raw_env,
            terrain_runtime,
            replay_level,
            lock_level=lock_level,
            replay_level_range=replay_level_range,
        )
        terrain_runtime.sync_env_origins(raw_env.scene)
        level_msg = _format_replay_level_mode(selected_level, lock_level)
        if replay_level_range is not None:
            level_msg = _format_replay_level_range_mode(replay_level_range)
        print(
            "[INFO] Stage1 replay terrain mode: all columns "
            f"({_format_stage1_replay_columns(list(range(num_cols)), terrain_runtime)}){level_msg}.",
            flush=True,
        )
        return True

    selected_tensor = torch.tensor(selected_columns, device=raw_env.device, dtype=torch.long)
    terrain_runtime.terrain_types[:] = selected_tensor[torch.remainder(env_ids, selected_tensor.numel())]
    selected_level = _reset_stage1_replay_curriculum_state(
        raw_env,
        terrain_runtime,
        replay_level,
        lock_level=lock_level,
        replay_level_range=replay_level_range,
    )
    terrain_runtime.sync_env_origins(raw_env.scene)
    level_msg = _format_replay_level_mode(selected_level, lock_level)
    if replay_level_range is not None:
        level_msg = _format_replay_level_range_mode(replay_level_range)
    print(
        "[INFO] Stage1 replay terrain columns: "
        f"{_format_stage1_replay_columns(selected_columns, terrain_runtime)}{level_msg}.",
        flush=True,
    )
    return True


@hydra_task_config(args_cli.task, args_cli.agent)
def main(env_cfg: DirectRLEnvCfg, agent_cfg):
    agent_cfg = _update_agent_cfg(agent_cfg)
    if args_cli.seed is not None:
        agent_cfg.seed = args_cli.seed
    env_cfg.scene.num_envs = args_cli.num_envs if args_cli.num_envs is not None else env_cfg.scene.num_envs
    env_cfg.sim.device = args_cli.device if args_cli.device is not None else env_cfg.sim.device
    env_cfg.seed = agent_cfg.seed
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
    if args_cli.max_play_steps < 0:
        raise ValueError("--max_play_steps must be non-negative.")
    if args_cli.record_completion_max_pre_completion_resets < -1:
        raise ValueError("--record_completion_max_pre_completion_resets must be -1 or non-negative.")
    if args_cli.record_completion_padding_steps < 0:
        raise ValueError("--record_completion_padding_steps must be non-negative.")
    if args_cli.stop_after_continuous_terrain_completions < 0:
        raise ValueError("--stop_after_continuous_terrain_completions must be non-negative.")
    if args_cli.selection_max_pre_completion_resets < 0:
        raise ValueError("--selection_max_pre_completion_resets must be non-negative.")
    if args_cli.terrain_replay_lock_level and args_cli.terrain_replay_level is None:
        raise ValueError("--terrain_replay_lock_level requires --terrain_replay_level.")
    replay_level_range = _parse_stage1_replay_level_range(args_cli.terrain_replay_level_range)
    if replay_level_range is not None and args_cli.terrain_replay_level is not None:
        raise ValueError("--terrain_replay_level_range is mutually exclusive with --terrain_replay_level.")
    if replay_level_range is not None and args_cli.terrain_replay_lock_level:
        raise ValueError("--terrain_replay_level_range cannot be combined with --terrain_replay_lock_level.")
    if args_cli.reward_trace_flush_interval <= 0:
        raise ValueError("--reward_trace_flush_interval must be positive.")
    if args_cli.record_camera_views is not None and not args_cli.record_chase_view:
        raise ValueError("--record_camera_views requires --record_chase_view.")
    if args_cli.record_camera_views is not None and not args_cli.stream_video:
        raise ValueError("--record_camera_views requires --stream_video.")
    if args_cli.record_global_dolly_view and args_cli.record_chase_view:
        raise ValueError("--record_global_dolly_view and --record_chase_view are separate recording modes.")
    if args_cli.record_global_dolly_view and args_cli.video and not args_cli.stream_video:
        raise ValueError("--record_global_dolly_view video recording requires --stream_video.")
    if args_cli.record_global_dolly_view and args_cli.global_dolly_duration_steps <= 0:
        raise ValueError("--global_dolly_duration_steps must be positive.")
    if args_cli.record_global_dolly_view and args_cli.global_dolly_start_focal_length <= 0.0:
        raise ValueError("--global_dolly_start_focal_length must be positive.")
    if args_cli.record_global_dolly_view and args_cli.global_dolly_end_focal_length <= 0.0:
        raise ValueError("--global_dolly_end_focal_length must be positive.")
    if args_cli.capture_terrain_row_stills and args_cli.still_settle_steps < 0:
        raise ValueError("--still_settle_steps must be non-negative.")
    if args_cli.capture_terrain_only_stills and args_cli.still_settle_steps < 0:
        raise ValueError("--still_settle_steps must be non-negative.")
    record_camera_views = _parse_record_camera_views(args_cli.record_camera_views, args_cli.record_camera_view)
    if args_cli.video_resolution is not None:
        env_cfg.viewer.resolution = _parse_video_resolution(args_cli.video_resolution)
    still_resolution = _parse_video_resolution(args_cli.still_resolution)

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
    record_completion_env = (
        args_cli.follow_view_chase_env
        if args_cli.record_completion_env < 0
        else args_cli.record_completion_env
    )
    if args_cli.record_until_terrain_completion:
        if record_completion_env < 0 or record_completion_env >= env_cfg.scene.num_envs:
            raise ValueError(
                f"--record_completion_env must be in [0, {env_cfg.scene.num_envs - 1}], got {record_completion_env}."
            )
        env_cfg.debug.delay_terrain_completion_reset = True
        env_cfg.debug.delayed_terrain_completion_env_indices = (int(record_completion_env),)
    if args_cli.record_chase_view:
        env_cfg.debug.create_follow_views = True
        follow_camera_name = FOLLOW_CAMERA_NAMES[record_camera_views[0]]
        env_cfg.viewer.cam_prim_path = f"/view/env_{args_cli.follow_view_chase_env}/{follow_camera_name}"
    if args_cli.record_global_dolly_view:
        env_cfg.viewer.cam_prim_path = args_cli.global_dolly_camera_path
        env_cfg.viewer.origin_type = "world"
    if args_cli.capture_terrain_row_stills:
        env_cfg.viewer.origin_type = "world"
    if args_cli.capture_terrain_only_stills:
        env_cfg.viewer.origin_type = "world"
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
    if (not args_cli.capture_terrain_only_stills) and _configure_stage1_replay_terrain(
        env.unwrapped,
        args_cli.terrain_replay_columns,
        args_cli.terrain_replay_level,
        lock_level=args_cli.terrain_replay_lock_level,
        replay_level_range=replay_level_range,
    ):
        env.reset()
        _print_stage1_replay_level_summary(env.unwrapped, "after reset")
    if args_cli.record_global_dolly_view:
        _update_global_dolly_camera(env.unwrapped, 0)
    if args_cli.capture_terrain_row_stills:
        still_output_dir = args_cli.still_output_dir or str(Path(log_dir) / "stills" / "terrain_row19_4k")
        _capture_terrain_row_stills(env.unwrapped, still_output_dir, still_resolution)
        env.close()
        return
    if args_cli.capture_terrain_only_stills:
        still_output_dir = args_cli.still_output_dir or str(Path(log_dir) / "stills" / "terrain_only_row19_4k")
        _capture_terrain_only_stills(env.unwrapped, still_output_dir, still_resolution)
        env.close()
        return
    reward_trace_recorder = None
    if args_cli.record_reward_trace:
        selected_reward_trace_envs = _parse_env_indices(args_cli.reward_trace_envs, env.unwrapped.num_envs)
        if not selected_reward_trace_envs:
            selected_reward_trace_envs = tuple(range(int(env.unwrapped.num_envs)))
        reward_trace_output = args_cli.reward_trace_output or _default_reward_trace_path(log_dir, resume_path)
        reward_trace_recorder = _RewardTraceRecorder(
            reward_trace_output,
            selected_reward_trace_envs,
            args_cli.reward_trace_flush_interval,
        )
    if args_cli.record_chase_view and hasattr(env.unwrapped, "_update_follow_views"):
        env.unwrapped._update_follow_views()
    stream_video_paths: dict[str, str] = {}
    if args_cli.video and args_cli.stream_video:
        video_folder = args_cli.video_output_dir or os.path.join(log_dir, "videos", "play")
        os.makedirs(video_folder, exist_ok=True)
        if args_cli.record_global_dolly_view:
            stream_video_paths = _build_stream_video_paths(
                video_folder,
                resume_path,
                args_cli.video_output_name,
                (GLOBAL_DOLLY_VIEW_NAME,),
            )
        elif args_cli.record_chase_view:
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
        video_folder = args_cli.video_output_dir or os.path.join(log_dir, "videos", "play")
        video_kwargs = {
            "video_folder": video_folder,
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
    if stream_video_paths and args_cli.record_global_dolly_view:
        follow_view_recorders = _open_global_dolly_stream_recorder(
            env.unwrapped,
            stream_video_paths,
            fps=round(1.0 / dt),
        )
    elif stream_video_paths and args_cli.record_chase_view:
        follow_view_recorders = _open_follow_view_stream_recorders(
            env.unwrapped,
            stream_video_paths,
            fps=round(1.0 / dt),
        )
    elif stream_video_paths:
        video_writer = _open_stream_writer(stream_video_paths["viewport"], fps=round(1.0 / dt))
    obs = env.get_observations()
    timestep = 0
    empty_follow_frame_count = 0
    dynamic_video_stop_step: int | None = None
    terrain_completion_recorded = False
    record_pre_completion_reset_count = 0
    selection_pending = None
    selection_completed = None
    selection_reset_counts = None
    if args_cli.stop_after_continuous_terrain_completions > 0:
        num_selection_envs = int(env.unwrapped.num_envs)
        selection_pending = torch.ones(num_selection_envs, dtype=torch.bool, device=env.unwrapped.device)
        selection_completed = torch.zeros(num_selection_envs, dtype=torch.bool, device=env.unwrapped.device)
        selection_reset_counts = torch.zeros(num_selection_envs, dtype=torch.long, device=env.unwrapped.device)
    try:
        while simulation_app.is_running():
            start_time = time.time()
            with torch.inference_mode():
                actions = policy(obs)
                if args_cli.zero_actions:
                    actions = torch.zeros_like(actions)
                obs, rewards, dones, extras = env.step(actions)
                if reward_trace_recorder is not None:
                    reward_trace_recorder.append(env.unwrapped, timestep, rewards, dones, actions)
                if args_cli.print_reset_causes:
                    _print_replay_reset_causes(timestep, dones, extras, env.unwrapped)
                if args_cli.record_until_terrain_completion and not terrain_completion_recorded:
                    done_terms = getattr(env.unwrapped, "_last_step_done_terms", None)
                    delayed_completion = getattr(
                        env.unwrapped,
                        "_debug_delayed_terrain_completion_event",
                        None,
                    )
                    selected_completed = delayed_completion is not None and bool(
                        delayed_completion[record_completion_env].item()
                    )
                    selected_done = bool(dones[record_completion_env].item()) if dones is not None else False
                    if selected_done and not selected_completed:
                        record_pre_completion_reset_count += 1
                        reset_reasons: list[str] = []
                        if isinstance(done_terms, dict):
                            for reason_key, reason_value in done_terms.items():
                                if reason_value is None:
                                    continue
                                try:
                                    if bool(reason_value[record_completion_env].item()):
                                        reset_reasons.append(reason_key)
                                except (IndexError, RuntimeError, TypeError):
                                    continue
                        reason_text = ",".join(reset_reasons) if reset_reasons else "unknown"
                        print(
                            "[RECORD_RESET] "
                            f"env={record_completion_env} step={timestep} "
                            f"pre_completion_resets={record_pre_completion_reset_count} "
                            f"reasons={reason_text}",
                            flush=True,
                        )
                        reset_limit = int(args_cli.record_completion_max_pre_completion_resets)
                        if reset_limit >= 0 and record_pre_completion_reset_count > reset_limit:
                            raise RuntimeError(
                                "Selected env exceeded the recording reset budget before max-row completion: "
                                f"env={record_completion_env}, "
                                f"pre_completion_resets={record_pre_completion_reset_count}, "
                                f"limit={reset_limit}, step={timestep}, reasons={reason_text}."
                            )
                    if selected_completed:
                        terrain_completion_recorded = True
                        dynamic_video_stop_step = timestep + 1 + int(args_cli.record_completion_padding_steps)
                        print(
                            "[RECORD_COMPLETE] "
                            f"env={record_completion_env} step={timestep} "
                            f"stop_step={dynamic_video_stop_step} "
                            f"padding_steps={args_cli.record_completion_padding_steps} "
                            f"pre_completion_resets={record_pre_completion_reset_count}",
                            flush=True,
                        )
                if (
                    selection_pending is not None
                    and selection_completed is not None
                    and selection_reset_counts is not None
                ):
                    done_terms = getattr(env.unwrapped, "_last_step_done_terms", None)
                    if isinstance(done_terms, dict):
                        zeros = torch.zeros_like(selection_pending)
                        completed_mask = done_terms.get("terrain_column_completed", zeros).to(dtype=torch.bool)
                        failure_mask = torch.zeros_like(selection_pending)
                        for failure_key in (
                            "time_out",
                            "stuck_timeout",
                            "low_quality_terrain_hit",
                            "far_from_target",
                            "ball_joint_out_of_bounds",
                            "orientation_out_of_bounds",
                        ):
                            value = done_terms.get(failure_key)
                            if value is not None:
                                failure_mask |= value.to(dtype=torch.bool)
                        active_failure = selection_pending & failure_mask & ~completed_mask
                        selection_reset_counts[active_failure] += 1
                        exceeded_reset_budget = (
                            selection_reset_counts > int(args_cli.selection_max_pre_completion_resets)
                        )
                        newly_completed = selection_pending & completed_mask & ~failure_mask & ~exceeded_reset_budget
                        selection_completed |= newly_completed
                        selection_pending &= ~(newly_completed | exceeded_reset_budget)
                        completed_count = int(torch.count_nonzero(selection_completed).item())
                        pending_count = int(torch.count_nonzero(selection_pending).item())
                        if (
                            completed_count >= args_cli.stop_after_continuous_terrain_completions
                            or pending_count == 0
                        ):
                            print(
                                "[INFO] Continuous terrain-completion selection stop: "
                                f"completed={completed_count} pending={pending_count} step={timestep}",
                                flush=True,
                            )
                            break
                if parsed_rsl_rl_version >= version.parse("4.0.0"):
                    policy.reset(dones)
                elif policy_nn is not None:
                    policy_nn.reset(dones)
            if args_cli.record_global_dolly_view:
                _update_global_dolly_camera(env.unwrapped, timestep)
            if follow_view_recorders:
                written_count = _append_follow_view_frames(env.unwrapped, follow_view_recorders)
                if written_count != len(follow_view_recorders):
                    empty_follow_frame_count += 1
                    if empty_follow_frame_count >= 120:
                        raise RuntimeError(
                            "Follow-view stream recording did not receive RGB frames from all requested cameras. "
                            "No video frames were written; check Replicator render products and camera prim paths."
                        )
                    continue
                empty_follow_frame_count = 0
                timestep += 1
                if timestep % 600 == 0:
                    if args_cli.video_length > 0:
                        print(f"[INFO] Streamed {timestep}/{args_cli.video_length} video frames", flush=True)
                    else:
                        print(f"[INFO] Streamed {timestep} video frames", flush=True)
                if args_cli.video_length > 0 and timestep >= args_cli.video_length:
                    break
                if dynamic_video_stop_step is not None and timestep >= dynamic_video_stop_step:
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
                if dynamic_video_stop_step is not None and timestep >= dynamic_video_stop_step:
                    break
            elif args_cli.video:
                timestep += 1
                if args_cli.video_length > 0 and timestep == args_cli.video_length:
                    break
                if dynamic_video_stop_step is not None and timestep >= dynamic_video_stop_step:
                    break
            else:
                timestep += 1
                if dynamic_video_stop_step is not None and timestep >= dynamic_video_stop_step:
                    break
            if args_cli.max_play_steps > 0 and timestep >= args_cli.max_play_steps:
                break
            sleep_time = dt - (time.time() - start_time)
            if args_cli.real_time and sleep_time > 0:
                time.sleep(sleep_time)
    finally:
        if follow_view_recorders:
            _close_follow_view_stream_recorders(follow_view_recorders)
        if video_writer is not None:
            video_writer.close()
        if reward_trace_recorder is not None:
            reward_trace_recorder.close()
    env.close()
    if args_cli.record_until_terrain_completion and not terrain_completion_recorded:
        raise RuntimeError(
            "Selected env did not reach terrain_column_completed before playback stopped: "
            f"env={record_completion_env}, steps={timestep}, max_play_steps={args_cli.max_play_steps}, "
            f"video_length={args_cli.video_length}."
        )


if __name__ == "__main__":
    main()
    simulation_app.close()
