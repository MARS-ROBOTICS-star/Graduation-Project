"""RSL-RL 训练入口。"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from isaaclab.app import AppLauncher
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_SOURCE = PROJECT_ROOT / "source" / "complete_car_lab"
LOCAL_RSL_RL_SOURCE = EXTENSION_SOURCE / "complete_car_lab" / "tasks" / "direct" / "complete_car"

for path in (LOCAL_RSL_RL_SOURCE, EXTENSION_SOURCE):
    if str(path) not in sys.path:
        # 优先使用项目内 vendored 的 PPO 本体，而不是环境里的外部 rsl_rl。
        sys.path.insert(0, str(path))


TASK_CHOICES = ["CompleteCar-Stage0", "CompleteCar-Stage1", "CompleteCar-Stage2"]

parser = argparse.ArgumentParser(description="Train complete-car with RSL-RL.")
parser.add_argument("--video", action="store_true", default=False)
parser.add_argument("--video_length", type=int, default=200)
parser.add_argument("--video_interval", type=int, default=2000)
parser.add_argument("--num_envs", type=int, default=None)
parser.add_argument("--task", type=str, default="CompleteCar-Stage0", choices=TASK_CHOICES)
parser.add_argument("--agent", type=str, default="rsl_rl_cfg_entry_point")
parser.add_argument("--seed", type=int, default=None)
parser.add_argument("--max_iterations", type=int, default=None)
parser.add_argument("--learning_rate", type=float, default=None)
parser.add_argument("--experiment_name", type=str, default=None)
parser.add_argument("--run_name", type=str, default=None)
parser.add_argument("--resume", action="store_true", default=False)
parser.add_argument("--warmstart", action="store_true", default=False)
parser.add_argument("--load_run", type=str, default=None)
parser.add_argument("--checkpoint", type=str, default=None)
parser.add_argument("--logger", type=str, default=None, choices={"wandb", "tensorboard", "neptune"})
parser.add_argument("--log_project_name", type=str, default=None)
parser.add_argument(
    "--record_only",
    action="store_true",
    default=False,
    help="Load a checkpoint and run policy inference only, without PPO updates.",
)
parser.add_argument(
    "--show_goal_vis",
    action="store_true",
    default=False,
    help="Show goal position and optional heading markers during training.",
)
parser.add_argument(
    "--hide_goal_vis",
    action="store_true",
    default=False,
    help="Disable goal position and heading markers even when --show_goal_vis is set.",
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
    help="Show wheel-slip debug arrows during training.",
)
parser.add_argument(
    "--hide_wheel_slip_vis",
    action="store_true",
    default=False,
    help="Disable wheel-slip debug arrows even when --show_wheel_slip_vis is set.",
)
parser.add_argument(
    "--create_follow_views",
    action="store_true",
    default=False,
    help="Create selectable follow cameras under /view during training.",
)
parser.add_argument(
    "--follow_all_envs",
    action="store_true",
    default=False,
    help="Create top-down and chase follow cameras for every parallel environment.",
)
parser.add_argument("--follow_view_top_height", type=float, default=None)
parser.add_argument("--follow_view_chase_env", type=int, default=None)
parser.add_argument(
    "--record_terrain_chase_videos",
    action="store_true",
    default=False,
    help="Record one chassis-follow chase video for each selected Stage1 terrain group.",
)
parser.add_argument("--terrain_chase_video_length_s", type=float, default=120.0)
parser.add_argument("--terrain_chase_video_seed", type=int, default=None)
parser.add_argument(
    "--terrain_chase_selection_file",
    type=str,
    default=None,
    help="Reuse an existing terrain_chase/selection.txt instead of rescoring envs.",
)
parser.add_argument(
    "--terrain_chase_start_from",
    type=int,
    default=1,
    help="1-based selected-video index to start from when using an existing selection file.",
)
parser.add_argument(
    "--terrain_chase_selection_steps",
    type=int,
    default=600,
    help="Number of training steps used to score envs before choosing the best env in each terrain group.",
)
parser.add_argument(
    "--terrain_chase_video_mode",
    type=str,
    choices={"per_column", "per_name"},
    default="per_column",
    help="Select one env per terrain column or per unique terrain name.",
)
AppLauncher.add_app_launcher_args(parser)
args_cli, hydra_args = parser.parse_known_args()

if args_cli.device is None:
    args_cli.device = "cuda:0"
if args_cli.video or args_cli.record_terrain_chase_videos:
    args_cli.enable_cameras = True

sys.argv = [sys.argv[0]] + hydra_args

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app


import gymnasium as gym
import torch
from rsl_rl.runners import OnPolicyRunner

from isaaclab.envs import DirectRLEnvCfg
from isaaclab.utils.dict import print_dict
from isaaclab.utils.io import dump_yaml

from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import get_checkpoint_path
from isaaclab_tasks.utils.hydra import hydra_task_config

import complete_car_lab  # noqa: F401


def _safe_filename_part(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "terrain"


def _terrain_name_from_index(terrain_cfg, terrain_idx: int) -> str:
    names = list(getattr(terrain_cfg, "terrain_names", []))
    if 0 <= terrain_idx < len(names):
        return names[terrain_idx]
    return f"terrain_{terrain_idx}"


def _build_terrain_chase_candidates(raw_env, *, mode: str) -> dict[tuple[int | str, ...], list[dict[str, int | str]]]:
    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    if terrain_runtime is None or terrain_runtime.terrain_types is None or terrain_runtime.terrain_levels is None:
        raise RuntimeError("Terrain chase video recording requires an initialized terrain runtime.")

    terrain_types = terrain_runtime.terrain_types.detach()
    terrain_levels = terrain_runtime.terrain_levels.detach()
    terrain_type_indices = terrain_runtime.get_tile_type_indices(terrain_levels, terrain_types).detach().cpu().tolist()
    terrain_columns = terrain_types.cpu().tolist()
    terrain_levels_cpu = terrain_levels.cpu().tolist()
    terrain_cfg = terrain_runtime._terrain_cfg

    groups: dict[tuple[int | str, ...], list[dict[str, int | str]]] = {}
    for env_id in range(raw_env.num_envs):
        terrain_idx = int(terrain_type_indices[env_id])
        terrain_col = int(terrain_columns[env_id])
        terrain_name = _terrain_name_from_index(terrain_cfg, terrain_idx)
        if mode == "per_name":
            group_key = ("name", terrain_idx)
            group_label = terrain_name
        else:
            group_key = ("column", terrain_col)
            group_label = f"col{terrain_col:02d}_{terrain_name}"
        groups.setdefault(group_key, []).append(
            {
                "env_id": env_id,
                "terrain_level": int(terrain_levels_cpu[env_id]),
                "terrain_column": terrain_col,
                "terrain_index": terrain_idx,
                "terrain_name": terrain_name,
                "group_label": group_label,
            }
        )

    return groups


def _parse_terrain_chase_selection_file(selection_file: str) -> list[dict[str, int | float | str]]:
    selected: list[dict[str, int | float | str]] = []
    selection_path = Path(selection_file).expanduser().resolve()
    with selection_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line.startswith("env="):
                continue
            values: dict[str, str] = {}
            for field in line.split(","):
                if "=" not in field:
                    continue
                key, value = field.split("=", 1)
                values[key.strip()] = value.strip()
            output_name = values["file"]
            output_stem = Path(output_name).stem
            group_label = output_stem.rsplit("_env", 1)[0] if "_env" in output_stem else output_stem
            selected.append(
                {
                    "env_id": int(values["env"]),
                    "terrain_level": int(values["level"]),
                    "terrain_column": int(values["column"]),
                    "terrain_index": int(values["terrain_index"]),
                    "terrain_name": values["terrain_name"],
                    "group_label": group_label,
                    "output_name": output_name,
                    "selection_score_forward_x_m": float(values.get("score_forward_x_m", "0.0")),
                }
            )
    if not selected:
        raise RuntimeError(f"No selected terrain chase envs were found in: {selection_path}")
    return selected


class TerrainChaseVideoRecorder(gym.Wrapper):
    """Stream Stage1 chassis-follow videos from selected follow-view cameras during training."""

    def __init__(
        self,
        env,
        *,
        log_dir: str,
        mode: str,
        seed: int,
        video_length_s: float,
        selection_steps: int,
        selection_file: str | None = None,
        start_from: int = 1,
    ):
        super().__init__(env)
        self._raw_env = env.unwrapped
        del seed
        selection_path = Path(selection_file).expanduser().resolve() if selection_file else None
        self._candidate_groups = (
            {}
            if selection_path is not None
            else _build_terrain_chase_candidates(self._raw_env, mode=mode)
        )
        self._selected_envs: list[dict[str, int | float | str]] = (
            _parse_terrain_chase_selection_file(str(selection_path)) if selection_path is not None else []
        )
        self._selection_steps = max(1, int(selection_steps))
        self._selection_frame = 0
        self._selection_start_root_x = self._raw_env.robot.data.root_link_pos_w[:, 0].detach().clone()
        self._selection_prev_root_x = self._selection_start_root_x.clone()
        self._selection_positive_forward_x = torch.zeros(self._raw_env.num_envs, device=self._raw_env.device)
        self._target_frames = max(1, int(round(video_length_s / float(self._raw_env.step_dt))))
        self._video_length_label = f"{int(round(video_length_s))}s"
        self._closed = False
        self._video_folder = (
            str(selection_path.parent)
            if selection_path is not None
            else os.path.join(log_dir, "videos", "terrain_chase")
        )
        self._fps = round(1.0 / float(self._raw_env.step_dt))
        self._active_index = max(0, int(start_from) - 1)
        self._active_frame = 0
        self._active_writer = None
        self._active_annotator = None
        self._active_render_product = None
        self._selection_written = selection_path is not None

        if hasattr(self._raw_env, "_update_follow_views"):
            self._raw_env._update_follow_views()

        os.makedirs(self._video_folder, exist_ok=True)
        if self._selected_envs:
            total = len(self._selected_envs)
            if self._active_index >= total:
                self._closed = True
                print(
                    f"[INFO] Terrain chase resume start {self._active_index + 1}/{total} exceeds selection count; nothing to record.",
                    flush=True,
                )
            else:
                print(
                    "[INFO] Terrain chase resume loaded: "
                    f"selection_file={selection_path}, start={self._active_index + 1}/{total}",
                    flush=True,
                )
        else:
            print(
                "[INFO] Terrain chase selection started: "
                f"mode={mode}, groups={len(self._candidate_groups)}, selection_steps={self._selection_steps}",
                flush=True,
            )

    def step(self, action):
        result = self.env.step(action)
        if self._selected_envs:
            self._record_frame()
        else:
            self._update_selection_scores()
        return result

    def _update_selection_scores(self) -> None:
        if self._closed:
            return
        current_root_x = self._raw_env.robot.data.root_link_pos_w[:, 0].detach()
        forward_delta = torch.clamp(current_root_x - self._selection_prev_root_x, min=0.0)
        self._selection_positive_forward_x += forward_delta
        self._selection_prev_root_x = current_root_x.clone()
        self._selection_frame += 1
        if self._selection_frame % 120 == 0:
            print(
                f"[INFO] Terrain chase env scoring {self._selection_frame}/{self._selection_steps} steps",
                flush=True,
            )
        if self._selection_frame >= self._selection_steps:
            self._select_best_envs()

    def _select_best_envs(self) -> None:
        if self._selected_envs:
            return
        selected = []
        scores = self._selection_positive_forward_x.detach().cpu()
        for group_key in sorted(self._candidate_groups):
            candidates = self._candidate_groups[group_key]
            best_item = max(candidates, key=lambda item: float(scores[int(item["env_id"])].item()))
            best_item = dict(best_item)
            best_item["selection_score_forward_x_m"] = float(scores[int(best_item["env_id"])].item())
            selected.append(best_item)
        self._selected_envs = selected
        self._write_selection_file()
        for item in self._selected_envs:
            print(
                "[INFO] Terrain chase selected best env "
                f"env={item['env_id']}, column={item['terrain_column']}, terrain={item['terrain_name']}, "
                f"score_forward_x_m={item['selection_score_forward_x_m']:.3f}",
                flush=True,
            )

    def _write_selection_file(self) -> None:
        if self._selection_written:
            return
        selection_path = os.path.join(self._video_folder, "selection.txt")
        with open(selection_path, "w", encoding="utf-8") as selection_file:
            selection_file.write("selection=best_positive_forward_x\n")
            selection_file.write(f"selection_steps={self._selection_steps}\n")
            selection_file.write("schedule=sequential\n")
            selection_file.write(f"target_frames={self._target_frames}\n")
            selection_file.write(f"fps={self._fps}\n")
            for item in self._selected_envs:
                env_id = int(item["env_id"])
                label = _safe_filename_part(str(item["group_label"]))
                output_name = f"{label}_env{env_id:02d}_chase_{self._video_length_label}.mp4"
                selection_file.write(
                    f"env={env_id}, column={item['terrain_column']}, level={item['terrain_level']}, "
                    f"terrain_index={item['terrain_index']}, terrain_name={item['terrain_name']}, "
                    f"score_forward_x_m={item['selection_score_forward_x_m']:.6f}, file={output_name}\n"
                )
        self._selection_written = True

    def _record_frame(self) -> None:
        if self._closed:
            return
        self._ensure_active_video()
        if self._closed:
            return

        self._raw_env.sim.render()
        frame = self._active_annotator.get_data()
        if frame.size == 0:
            width, height = self._raw_env.cfg.viewer.resolution
            frame = np.zeros((height, width, 3), dtype=np.uint8)
        self._active_writer.append_data(frame[:, :, :3])

        self._active_frame += 1
        if self._active_frame % 600 == 0 or self._active_frame == self._target_frames:
            current = self._active_index + 1
            total = len(self._selected_envs)
            print(
                f"[INFO] Terrain chase video {current}/{total} streamed "
                f"{self._active_frame}/{self._target_frames} frames",
                flush=True,
            )
        if self._active_frame >= self._target_frames:
            self._close_active_video()
            self._active_index += 1
            self._active_frame = 0
            if self._active_index >= len(self._selected_envs):
                self._closed = True
                print("[INFO] Terrain chase video recording finished.", flush=True)

    def _ensure_active_video(self) -> None:
        if self._active_writer is not None:
            return
        if self._active_index >= len(self._selected_envs):
            self._closed = True
            return

        import imageio.v2 as imageio
        import omni.replicator.core as rep

        item = self._selected_envs[self._active_index]
        env_id = int(item["env_id"])
        label = _safe_filename_part(str(item["group_label"]))
        output_name = str(item.get("output_name") or f"{label}_env{env_id:02d}_chase_{self._video_length_label}.mp4")
        output_path = os.path.join(self._video_folder, output_name)
        camera_prim_path = f"/view/env_{env_id}/chase_camera"
        render_product = rep.create.render_product(camera_prim_path, resolution=self._raw_env.cfg.viewer.resolution)
        if not isinstance(render_product, str):
            render_product = render_product.path
        annotator = rep.AnnotatorRegistry.get_annotator("rgb", device="cpu")
        annotator.attach(render_product)
        writer = imageio.get_writer(
            output_path,
            fps=self._fps,
            codec="libx264",
            macro_block_size=None,
        )
        self._active_writer = writer
        self._active_annotator = annotator
        self._active_render_product = render_product
        print(
            "[INFO] Terrain chase recording started "
            f"{self._active_index + 1}/{len(self._selected_envs)}: env={env_id}, "
            f"column={item['terrain_column']}, terrain={item['terrain_name']}, file={output_path}",
            flush=True,
        )

    def _close_active_video(self) -> None:
        if self._active_writer is not None:
            self._active_writer.close()
            self._active_writer = None
        if self._active_annotator is not None and self._active_render_product is not None:
            self._active_annotator.detach([self._active_render_product])
        self._active_annotator = None
        self._active_render_product = None

    def _close_recorder(self) -> None:
        if self._closed:
            return
        self._close_active_video()
        self._closed = True

    def close(self):
        self._close_recorder()
        return self.env.close()

    @property
    def is_finished(self) -> bool:
        return self._closed


def _update_agent_cfg(agent_cfg):
    if args_cli.seed is not None:
        agent_cfg.seed = args_cli.seed
    if args_cli.resume is not None:
        agent_cfg.resume = args_cli.resume
    if args_cli.load_run is not None:
        agent_cfg.load_run = args_cli.load_run
    if args_cli.checkpoint is not None:
        agent_cfg.load_checkpoint = args_cli.checkpoint
    if args_cli.experiment_name is not None:
        agent_cfg.experiment_name = args_cli.experiment_name
    if args_cli.run_name is not None:
        agent_cfg.run_name = args_cli.run_name
    if args_cli.logger is not None:
        agent_cfg.logger = args_cli.logger
    if args_cli.log_project_name:
        agent_cfg.wandb_project = args_cli.log_project_name
        agent_cfg.neptune_project = args_cli.log_project_name
    if args_cli.max_iterations is not None:
        agent_cfg.max_iterations = args_cli.max_iterations
    if args_cli.learning_rate is not None:
        agent_cfg.algorithm.learning_rate = args_cli.learning_rate
    return agent_cfg


def _resolve_checkpoint_lookup_args(agent_cfg) -> tuple[str, str]:
    """Normalize run/checkpoint selectors for Isaac Lab checkpoint lookup."""
    run_pattern = agent_cfg.load_run if isinstance(agent_cfg.load_run, str) else ".*"
    checkpoint_pattern = agent_cfg.load_checkpoint if isinstance(agent_cfg.load_checkpoint, str) else "model_.*.pt"
    return run_pattern, checkpoint_pattern


@hydra_task_config(args_cli.task, args_cli.agent)
def main(env_cfg: DirectRLEnvCfg, agent_cfg):
    agent_cfg = _update_agent_cfg(agent_cfg)
    env_cfg.scene.num_envs = args_cli.num_envs if args_cli.num_envs is not None else env_cfg.scene.num_envs
    env_cfg.seed = agent_cfg.seed
    env_cfg.sim.device = args_cli.device
    agent_cfg.device = args_cli.device
    goal_vis_enabled = args_cli.show_goal_vis and not args_cli.hide_goal_vis
    wheel_slip_vis_enabled = args_cli.show_wheel_slip_vis and not args_cli.hide_wheel_slip_vis
    debug_draw_needed = (
        goal_vis_enabled
        or wheel_slip_vis_enabled
        or args_cli.create_follow_views
        or args_cli.follow_all_envs
        or args_cli.record_terrain_chase_videos
    )
    env_cfg.debug.enable_debug_draw = debug_draw_needed
    env_cfg.debug.visualize_goal_position = goal_vis_enabled
    env_cfg.debug.visualize_goal_heading = goal_vis_enabled and (not args_cli.hide_goal_heading)
    env_cfg.debug.visualize_wheel_slip = wheel_slip_vis_enabled
    if args_cli.create_follow_views or args_cli.follow_all_envs or args_cli.record_terrain_chase_videos:
        env_cfg.debug.create_follow_views = True
    if args_cli.follow_view_top_height is not None:
        env_cfg.debug.follow_view_top_height = args_cli.follow_view_top_height
    if args_cli.follow_view_chase_env is not None:
        env_cfg.debug.follow_view_chase_env_index = args_cli.follow_view_chase_env
    if args_cli.follow_all_envs or args_cli.record_terrain_chase_videos:
        env_cfg.debug.follow_view_chase_env_indices = tuple(range(env_cfg.scene.num_envs))

    log_root_path = os.path.abspath(os.path.join("logs", "rsl_rl", agent_cfg.experiment_name))
    selection_path = Path(args_cli.terrain_chase_selection_file).expanduser().resolve() if args_cli.terrain_chase_selection_file else None
    if args_cli.record_only and selection_path is not None:
        log_dir = str(selection_path.parents[2])
        print(f"[INFO] Reusing existing terrain chase run directory: {log_dir}")
    else:
        log_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print(f"Exact experiment name requested from command line: {log_dir}")
        if agent_cfg.run_name:
            log_dir += f"_{agent_cfg.run_name}"
        log_dir = os.path.join(log_root_path, log_dir)
    env_cfg.log_dir = log_dir

    env = gym.make(args_cli.task, cfg=env_cfg, render_mode="rgb_array" if args_cli.video else None)
    needs_checkpoint = agent_cfg.resume or args_cli.record_only
    if needs_checkpoint:
        run_pattern, checkpoint_pattern = _resolve_checkpoint_lookup_args(agent_cfg)
        resume_path = get_checkpoint_path(log_root_path, run_pattern, checkpoint_pattern)
    else:
        resume_path = None

    if args_cli.video:
        video_kwargs = {
            "video_folder": os.path.join(log_dir, "videos", "train"),
            "step_trigger": lambda step: step % args_cli.video_interval == 0,
            "video_length": args_cli.video_length,
            "disable_logger": True,
        }
        print_dict(video_kwargs, nesting=4)
        env = gym.wrappers.RecordVideo(env, **video_kwargs)
    terrain_chase_recorder = None
    if args_cli.record_terrain_chase_videos:
        terrain_chase_seed = args_cli.terrain_chase_video_seed
        if terrain_chase_seed is None:
            terrain_chase_seed = int(agent_cfg.seed if agent_cfg.seed is not None else time.time())
        terrain_chase_recorder = TerrainChaseVideoRecorder(
            env,
            log_dir=log_dir,
            mode=args_cli.terrain_chase_video_mode,
            seed=terrain_chase_seed,
            video_length_s=args_cli.terrain_chase_video_length_s,
            selection_steps=args_cli.terrain_chase_selection_steps,
            selection_file=args_cli.terrain_chase_selection_file,
            start_from=args_cli.terrain_chase_start_from,
        )
        env = terrain_chase_recorder

    start_time = time.time()
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    try:
        runner_log_dir = None if args_cli.record_only else log_dir
        runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=runner_log_dir, device=agent_cfg.device)
        if not args_cli.record_only:
            runner.add_git_repo_to_log(__file__)

        if resume_path is not None:
            print(f"[INFO] Loading checkpoint from: {resume_path}")
            if args_cli.warmstart:
                runner.load(
                    resume_path,
                    load_cfg={"actor": True, "critic": True, "optimizer": False, "iteration": False, "rnd": False},
                )
            else:
                runner.load(resume_path)

        if args_cli.record_only:
            policy = runner.get_inference_policy(device=env.unwrapped.device)
            obs = env.get_observations()
            while simulation_app.is_running():
                with torch.inference_mode():
                    actions = policy(obs, stochastic_output=True)
                    obs, _, dones, _ = env.step(actions)
                    policy.reset(dones)
                if terrain_chase_recorder is not None and terrain_chase_recorder.is_finished:
                    break
            print(f"Record-only runtime: {round(time.time() - start_time, 2)} seconds")
        else:
            dump_yaml(os.path.join(log_dir, "params", "env.yaml"), env_cfg)
            dump_yaml(os.path.join(log_dir, "params", "agent.yaml"), agent_cfg)
            runner.learn(num_learning_iterations=agent_cfg.max_iterations, init_at_random_ep_len=True)
            print(f"Training time: {round(time.time() - start_time, 2)} seconds")
    finally:
        env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
