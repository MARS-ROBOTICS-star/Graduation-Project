#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from isaaclab.app import AppLauncher


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview the original MGDP terrain generation and curriculum layout inside Isaac Sim via env_isaacLab."
    )
    parser.add_argument(
        "--gallery",
        choices=["stage1", "stage2", "both"],
        default="both",
        help="Which MGDP terrain family to build.",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=0,
        help="If > 0, close after this many updates. Use 0 to keep the window open until closed.",
    )
    parser.add_argument(
        "--save-usd",
        type=str,
        default="",
        help="Optional output USD path.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=7,
        help="Random seed for terrain generation and curriculum sampling.",
    )
    parser.add_argument(
        "--curriculum-envs",
        type=int,
        default=64,
        help="How many curriculum assignment markers to place on the terrain grid.",
    )
    AppLauncher.add_app_launcher_args(parser)
    return parser.parse_args()


ARGS = parse_args()
APP_LAUNCHER = AppLauncher(ARGS)
SIMULATION_APP = APP_LAUNCHER.app

import omni.timeline
import omni.usd
from isaacsim.core.utils.stage import save_stage
from isaacsim.core.utils.viewports import set_camera_view

from mgdp_gallery_builder import build_mgdp_gallery
from terrain_builder import setup_base_scene


_THIS_FILE = Path(__file__).resolve()
REPO_ROOT = next(parent for parent in _THIS_FILE.parents if (parent / "AGENTS.md").exists())
DEFAULT_SAVE_PATH = REPO_ROOT / "outputs" / "isaacsim" / f"mgdp_ported_terrain_{ARGS.gallery}.usd"

def maybe_save_stage(output_path: str) -> Path | None:
    if not output_path:
        return None
    save_path = Path(output_path).expanduser()
    if not save_path.is_absolute():
        save_path = REPO_ROOT / save_path
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_stage(str(save_path), save_and_reload_in_place=False)
    print(f"Saved USD stage to: {save_path}")
    return save_path

def main() -> None:
    omni.usd.get_context().new_stage()
    stage = omni.usd.get_context().get_stage()
    setup_base_scene(stage)
    summary = build_mgdp_gallery(
        stage=stage,
        gallery=ARGS.gallery,
        root_path="/World/mgdp_ported",
        seed=ARGS.seed,
        curriculum_envs=ARGS.curriculum_envs,
        include_markers=True,
    )

    if not ARGS.headless:
        distance = max(float(summary.extent[0]), float(summary.extent[1])) * 1.2
        eye = [
            float(summary.center[0] - 0.15 * distance),
            float(summary.center[1] - 0.95 * distance),
            float(max(12.0, summary.extent[2] + 0.35 * distance)),
        ]
        target = [float(summary.center[0]), float(summary.center[1]), float(summary.center[2])]
        set_camera_view(eye=eye, target=target, camera_prim_path="/OmniverseKit_Persp")

    for _ in range(8):
        SIMULATION_APP.update()

    save_target = maybe_save_stage(ARGS.save_usd or (str(DEFAULT_SAVE_PATH) if ARGS.headless else ""))
    if save_target is not None:
        print("Open this USD later in Isaac Sim if you want a static scene review.")

    timeline = omni.timeline.get_timeline_interface()
    timeline.play()

    if ARGS.frames > 0:
        for _ in range(ARGS.frames):
            SIMULATION_APP.update()
    elif ARGS.headless:
        for _ in range(24):
            SIMULATION_APP.update()
    else:
        while SIMULATION_APP.is_running():
            SIMULATION_APP.update()

    timeline.stop()
    SIMULATION_APP.close()


if __name__ == "__main__":
    main()
