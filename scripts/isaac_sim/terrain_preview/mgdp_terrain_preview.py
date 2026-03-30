#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import omni.timeline
import omni.usd
from isaacsim import SimulationApp
from isaacsim.core.utils.stage import save_stage
from isaacsim.core.utils.viewports import set_camera_view

from terrain_builder import build_gallery_layout, build_gallery_specs, setup_base_scene


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview representative MGDP terrains inside Isaac Sim."
    )
    parser.add_argument(
        "--gallery",
        choices=["stage1", "stage2", "both"],
        default="both",
        help="Which terrain gallery to build.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Isaac Sim without opening a window.",
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
        help="Random seed for obstacle placement.",
    )
    return parser.parse_args()


ARGS = parse_args()

SIMULATION_APP = SimulationApp(
    {
        "headless": ARGS.headless,
        "renderer": "RaytracedLighting",
    }
)

_THIS_FILE = Path(__file__).resolve()
REPO_ROOT = next(parent for parent in _THIS_FILE.parents if (parent / "AGENTS.md").exists())
DEFAULT_SAVE_PATH = REPO_ROOT / "outputs" / "isaacsim" / f"mgdp_terrain_{ARGS.gallery}.usd"


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

    specs = build_gallery_specs(ARGS.gallery)
    if not specs:
        raise RuntimeError("No terrain specs selected.")

    center, extent = build_gallery_layout(stage, specs, root_path="/World", seed_base=ARGS.seed)

    if not ARGS.headless:
        distance = max(extent[0] * 1.6, 18.0)
        eye = [
            float(center[0] - distance * 0.30),
            float(center[1] - distance * 0.95),
            float(max(8.0, extent[0] * 0.55)),
        ]
        target = [float(center[0]), float(center[1]), 0.0]
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
