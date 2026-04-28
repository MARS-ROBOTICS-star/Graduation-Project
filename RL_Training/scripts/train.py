"""RSL-RL 训练入口。"""

from __future__ import annotations

import argparse
import os
import random
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
parser.add_argument("--experiment_name", type=str, default=None)
parser.add_argument("--run_name", type=str, default=None)
parser.add_argument("--resume", action="store_true", default=False)
parser.add_argument("--warmstart", action="store_true", default=False)
parser.add_argument("--load_run", type=str, default=None)
parser.add_argument("--checkpoint", type=str, default=None)
parser.add_argument("--logger", type=str, default=None, choices={"wandb", "tensorboard", "neptune"})
parser.add_argument("--log_project_name", type=str, default=None)
parser.add_argument(
    "--hide_goal_vis",
    action="store_true",
    default=False,
    help="Hide goal position and heading markers during training.",
)
parser.add_argument(
    "--hide_goal_heading",
    action="store_true",
    default=False,
    help="Hide only the goal heading arrow while keeping the goal position marker visible.",
)
parser.add_argument(
    "--hide_wheel_slip_vis",
    action="store_true",
    default=False,
    help="Hide wheel-slip debug arrows during training.",
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


def _select_terrain_chase_envs(raw_env, *, mode: str, seed: int) -> list[dict[str, int | str]]:
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

    rng = random.Random(seed)
    selected = []
    for group_key in sorted(groups):
        selected.append(rng.choice(groups[group_key]))
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
    ):
        super().__init__(env)
        self._raw_env = env.unwrapped
        self._selected_envs = _select_terrain_chase_envs(self._raw_env, mode=mode, seed=seed)
        self._target_frames = max(1, int(round(video_length_s / float(self._raw_env.step_dt))))
        self._frame = 0
        self._closed = False
        self._writers = []
        self._annotators = []

        if hasattr(self._raw_env, "_update_follow_views"):
            self._raw_env._update_follow_views()

        import imageio.v2 as imageio
        import omni.replicator.core as rep

        video_folder = os.path.join(log_dir, "videos", "terrain_chase")
        os.makedirs(video_folder, exist_ok=True)
        selection_path = os.path.join(video_folder, "selection.txt")
        fps = round(1.0 / float(self._raw_env.step_dt))

        with open(selection_path, "w", encoding="utf-8") as selection_file:
            selection_file.write(f"mode={mode}\n")
            selection_file.write(f"seed={seed}\n")
            selection_file.write(f"target_frames={self._target_frames}\n")
            selection_file.write(f"fps={fps}\n")
            for item in self._selected_envs:
                env_id = int(item["env_id"])
                label = _safe_filename_part(str(item["group_label"]))
                terrain_name = str(item["terrain_name"])
                output_name = f"{label}_env{env_id:02d}_chase_120s.mp4"
                output_path = os.path.join(video_folder, output_name)
                camera_prim_path = f"/view/env_{env_id}/chase_camera"
                render_product = rep.create.render_product(camera_prim_path, resolution=self._raw_env.cfg.viewer.resolution)
                if not isinstance(render_product, str):
                    render_product = render_product.path
                annotator = rep.AnnotatorRegistry.get_annotator("rgb", device="cpu")
                annotator.attach(render_product)
                writer = imageio.get_writer(
                    output_path,
                    fps=fps,
                    codec="libx264",
                    macro_block_size=None,
                )
                self._annotators.append(annotator)
                self._writers.append(writer)
                selection_file.write(
                    f"env={env_id}, column={item['terrain_column']}, level={item['terrain_level']}, "
                    f"terrain_index={item['terrain_index']}, terrain_name={terrain_name}, file={output_name}\n"
                )
                print(
                    "[INFO] Terrain chase video selected "
                    f"env={env_id}, column={item['terrain_column']}, terrain={terrain_name}, file={output_path}",
                    flush=True,
                )

    def step(self, action):
        result = self.env.step(action)
        self._record_frame()
        return result

    def _record_frame(self) -> None:
        if self._closed or self._frame >= self._target_frames:
            return

        self._raw_env.sim.render()
        for annotator, writer in zip(self._annotators, self._writers, strict=True):
            frame = annotator.get_data()
            if frame.size == 0:
                width, height = self._raw_env.cfg.viewer.resolution
                frame = np.zeros((height, width, 3), dtype=np.uint8)
            writer.append_data(frame[:, :, :3])

        self._frame += 1
        if self._frame % 600 == 0 or self._frame == self._target_frames:
            print(f"[INFO] Terrain chase videos streamed {self._frame}/{self._target_frames} frames", flush=True)
        if self._frame >= self._target_frames:
            self._close_writers()

    def _close_writers(self) -> None:
        if self._closed:
            return
        for writer in self._writers:
            writer.close()
        self._closed = True
        print("[INFO] Terrain chase video recording finished.", flush=True)

    def close(self):
        self._close_writers()
        return self.env.close()


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
    debug_draw_needed = (
        not args_cli.hide_goal_vis
        or args_cli.create_follow_views
        or args_cli.follow_all_envs
        or args_cli.record_terrain_chase_videos
    )
    env_cfg.debug.enable_debug_draw = debug_draw_needed
    env_cfg.debug.visualize_goal_heading = (not args_cli.hide_goal_vis) and (not args_cli.hide_goal_heading)
    if args_cli.hide_wheel_slip_vis:
        env_cfg.debug.visualize_wheel_slip = False
    if args_cli.create_follow_views or args_cli.follow_all_envs or args_cli.record_terrain_chase_videos:
        env_cfg.debug.create_follow_views = True
    if args_cli.follow_view_top_height is not None:
        env_cfg.debug.follow_view_top_height = args_cli.follow_view_top_height
    if args_cli.follow_view_chase_env is not None:
        env_cfg.debug.follow_view_chase_env_index = args_cli.follow_view_chase_env
    if args_cli.follow_all_envs or args_cli.record_terrain_chase_videos:
        env_cfg.debug.follow_view_chase_env_indices = tuple(range(env_cfg.scene.num_envs))

    log_root_path = os.path.abspath(os.path.join("logs", "rsl_rl", agent_cfg.experiment_name))
    log_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(f"Exact experiment name requested from command line: {log_dir}")
    if agent_cfg.run_name:
        log_dir += f"_{agent_cfg.run_name}"
    log_dir = os.path.join(log_root_path, log_dir)
    env_cfg.log_dir = log_dir

    env = gym.make(args_cli.task, cfg=env_cfg, render_mode="rgb_array" if args_cli.video else None)
    if agent_cfg.resume:
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
    if args_cli.record_terrain_chase_videos:
        terrain_chase_seed = args_cli.terrain_chase_video_seed
        if terrain_chase_seed is None:
            terrain_chase_seed = int(agent_cfg.seed if agent_cfg.seed is not None else time.time())
        env = TerrainChaseVideoRecorder(
            env,
            log_dir=log_dir,
            mode=args_cli.terrain_chase_video_mode,
            seed=terrain_chase_seed,
            video_length_s=args_cli.terrain_chase_video_length_s,
        )

    start_time = time.time()
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=log_dir, device=agent_cfg.device)
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

    dump_yaml(os.path.join(log_dir, "params", "env.yaml"), env_cfg)
    dump_yaml(os.path.join(log_dir, "params", "agent.yaml"), agent_cfg)
    runner.learn(num_learning_iterations=agent_cfg.max_iterations, init_at_random_ep_len=True)
    print(f"Training time: {round(time.time() - start_time, 2)} seconds")
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
