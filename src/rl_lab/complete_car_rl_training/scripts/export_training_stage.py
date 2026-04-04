"""Export the assembled training stage for the current RL task."""

from __future__ import annotations

import argparse
from pathlib import Path

from isaaclab.app import AppLauncher


parser = argparse.ArgumentParser(description="Export the assembled Isaac Lab training stage to USD.")
parser.add_argument("--task", type=str, required=True, help="Task name to instantiate.")
parser.add_argument("--num_envs", type=int, default=1, help="Number of environments to simulate.")
parser.add_argument("--steps", type=int, default=1, help="Number of zero-action steps before saving the stage.")
parser.add_argument("--save-usd", type=str, required=True, help="Output USD path.")
parser.add_argument(
    "--tree-out",
    type=str,
    default="",
    help="Optional output path for the full prim tree. Defaults next to the exported USD.",
)
parser.add_argument(
    "--terrain-tree-out",
    type=str,
    default="",
    help="Optional output path for the /World/terrain prim tree. Defaults next to the exported USD.",
)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch
from pxr import Usd

import isaaclab.sim as sim_utils
import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg

import complete_car_rl_training.tasks  # noqa: F401


def _log(message: str) -> None:
    print(message, flush=True)


def _format_tree(stage: Usd.Stage, root_path: str | None = None) -> str:
    root_prim = stage.GetPrimAtPath(root_path) if root_path else stage.GetPseudoRoot()
    if not root_prim.IsValid():
        raise ValueError(f"Invalid prim path: {root_path}")

    lines: list[str] = []

    def walk(prim: Usd.Prim, depth: int) -> None:
        if prim == stage.GetPseudoRoot():
            label = "/"
        else:
            label = prim.GetPath().pathString
        lines.append(f"{'  ' * depth}{label} :: {prim.GetTypeName() or 'PseudoRoot'}")
        for child in prim.GetChildren():
            walk(child, depth + 1)

    walk(root_prim, 0)
    return "\n".join(lines) + "\n"


def _resolve_output_path(primary_path: Path, override: str, suffix: str) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    return primary_path.with_suffix(primary_path.suffix + suffix)


def main() -> None:
    save_path = Path(args_cli.save_usd).expanduser().resolve()
    if save_path.exists() and save_path.is_dir():
        raise ValueError(
            "--save-usd must be a USD file path, not a directory. "
            f"Received existing directory: {save_path}"
        )
    if save_path.suffix.lower() not in {".usd", ".usda"}:
        raise ValueError(
            "--save-usd must end with .usd or .usda so the output target is unambiguous. "
            f"Received: {save_path}"
        )
    save_path.parent.mkdir(parents=True, exist_ok=True)

    _log("[EXPORT_STAGE] parsing env config")
    env_cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs, use_fabric=False)
    _log("[EXPORT_STAGE] creating gym env")
    env = gym.make(args_cli.task, cfg=env_cfg)

    try:
        _log("[EXPORT_STAGE] resetting env")
        env.reset()
        _log("[EXPORT_STAGE] reset complete")

        for _ in range(max(0, args_cli.steps)):
            with torch.inference_mode():
                actions = torch.zeros(env.action_space.shape, device=env.unwrapped.device)
                env.step(actions)
        _log("[EXPORT_STAGE] stepping complete")

        scene = env.unwrapped.scene
        terrain = scene.terrain

        _log("[EXPORT_STAGE] scene summary")
        _log(f"  task: {args_cli.task}")
        _log(f"  device: {env.unwrapped.device}")
        _log(f"  num_envs: {scene.num_envs}")
        _log(f"  env_origins_shape: {tuple(scene.env_origins.shape)}")
        _log(f"  terrain_prim_paths: {terrain.terrain_prim_paths}")

        _log("[EXPORT_STAGE] saving stage")
        ok = sim_utils.save_stage(str(save_path), save_and_reload_in_place=False)
        _log(f"  save_usd: {save_path}")
        _log(f"  save_ok: {ok}")
        if not ok:
            raise RuntimeError(f"Failed to save stage to: {save_path}")

        stage = Usd.Stage.Open(str(save_path))
        if stage is None:
            raise RuntimeError(f"Failed to reopen saved stage: {save_path}")

        tree_out = _resolve_output_path(save_path, args_cli.tree_out, ".tree.txt")
        tree_out.write_text(_format_tree(stage), encoding="utf-8")

        terrain_tree_out = _resolve_output_path(save_path, args_cli.terrain_tree_out, ".terrain_tree.txt")
        terrain_tree_out.write_text(_format_tree(stage, "/World/terrain"), encoding="utf-8")

        _log(f"  tree_out: {tree_out}")
        _log(f"  terrain_tree_out: {terrain_tree_out}")
    finally:
        env.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
