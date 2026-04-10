"""Preview the local stage1 terrain generation result in Isaac Sim."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RL_PROJECT_ROOT = PROJECT_ROOT / "RL_Training"
if str(RL_PROJECT_ROOT) not in sys.path:
    sys.path.append(str(RL_PROJECT_ROOT))


parser = argparse.ArgumentParser(description="Preview the locally generated MGDP stage1 terrain in Isaac Sim.")
parser.add_argument("--frames", type=int, default=0, help="If > 0, stop after this many simulation steps.")
parser.add_argument("--row", type=int, default=0, help="Focused tile row for camera and optional car spawn.")
parser.add_argument("--col", type=int, default=0, help="Focused tile col for camera and optional car spawn.")
parser.add_argument("--show-origins", action="store_true", default=True, help="Show terrain origin markers.")
parser.add_argument("--spawn-car", action="store_true", default=False, help="Spawn the complete car on the selected tile.")
parser.add_argument("--save-usd", type=str, default="", help="Optional path to save the assembled preview stage as USD.")
parser.add_argument(
    "--car-height-offset",
    type=float,
    default=0.30,
    help="Extra height added above the focused terrain origin when spawning the car.",
)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import isaaclab.sim as sim_utils
import torch
import trimesh
from isaaclab.assets import AssetBaseCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.sim import SimulationContext
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils import configclass

from complete_car_rl_training.tasks.direct.complete_car.assets import COMPLETE_CAR_CFG
from complete_car_rl_training.tasks.direct.complete_car.terrain import (
    Stage1TerrainCfg,
    build_stage1_terrain_data,
    get_terrain_name_from_idx,
)


def remove_default_plane(terrain_importer) -> None:
    """Remove the auto-created ground plane before importing the custom stage1 mesh."""
    plane_path = f"{terrain_importer.cfg.prim_path}/terrain"
    if plane_path in terrain_importer.terrain_prim_paths:
        sim_utils.delete_prim(plane_path)
        terrain_importer.terrain_prim_paths = [path for path in terrain_importer.terrain_prim_paths if path != plane_path]


def offset_mesh_to_mgdp_frame(terrain_cfg: Stage1TerrainCfg, terrain_mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Match MGDP's triangle-mesh placement, which shifts the full map by -border_size in x/y."""
    terrain_mesh = terrain_mesh.copy()
    terrain_mesh.vertices[:, 0] -= terrain_cfg.border_size
    terrain_mesh.vertices[:, 1] -= terrain_cfg.border_size
    return terrain_mesh


@configclass
class Stage1PreviewSceneCfg(InteractiveSceneCfg):
    terrain = TerrainImporterCfg(
        prim_path="/World/terrain",
        terrain_type="plane",
        collision_group=-1,
        visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.42, 0.38, 0.30)),
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
        debug_vis=False,
    )

    dome_light = AssetBaseCfg(
        prim_path="/World/skyLight",
        spawn=sim_utils.DomeLightCfg(intensity=2500.0, color=(0.75, 0.75, 0.75)),
    )

    robot = COMPLETE_CAR_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")


def main() -> None:
    terrain_cfg = Stage1TerrainCfg()
    terrain_data = build_stage1_terrain_data(terrain_cfg)

    if not (0 <= args_cli.row < terrain_cfg.num_rows):
        raise ValueError(f"--row must be in [0, {terrain_cfg.num_rows - 1}]")
    if not (0 <= args_cli.col < terrain_cfg.num_cols):
        raise ValueError(f"--col must be in [0, {terrain_cfg.num_cols - 1}]")

    terrain_mesh = trimesh.Trimesh(vertices=terrain_data.vertices, faces=terrain_data.faces)
    terrain_mesh = offset_mesh_to_mgdp_frame(terrain_cfg, terrain_mesh)

    sim = SimulationContext(sim_utils.SimulationCfg(dt=1 / 120))
    scene = InteractiveScene(Stage1PreviewSceneCfg(num_envs=1, env_spacing=1.0))

    remove_default_plane(scene.terrain)
    scene.terrain.import_mesh("stage1", terrain_mesh)
    scene.terrain.configure_env_origins(terrain_data.env_origins)
    if args_cli.show_origins:
        scene.terrain.set_debug_vis(True)

    focus_origin = terrain_data.env_origins[args_cli.row, args_cli.col]
    focus_idx = int(terrain_data.terrain_type[args_cli.row, args_cli.col])
    focus_name = get_terrain_name_from_idx(terrain_cfg, focus_idx)

    sim.reset()
    sim.set_camera_view(
        eye=[focus_origin[0] + 6.0, focus_origin[1] + 6.0, focus_origin[2] + 4.0],
        target=[focus_origin[0], focus_origin[1], focus_origin[2]],
    )

    if args_cli.spawn_car:
        robot = scene["robot"]
        root_state = robot.data.default_root_state.clone()
        root_state[:, 0] = focus_origin[0]
        root_state[:, 1] = focus_origin[1]
        root_state[:, 2] = focus_origin[2] + args_cli.car_height_offset
        robot.write_root_pose_to_sim(root_state[:, :7])
        robot.write_root_velocity_to_sim(root_state[:, 7:])
        robot.write_joint_state_to_sim(robot.data.default_joint_pos.clone(), robot.data.default_joint_vel.clone())

    print("[STAGE1_PREVIEW]")
    print(f"  rows x cols: {terrain_cfg.num_rows} x {terrain_cfg.num_cols}")
    print(f"  map_size_m: {terrain_cfg.total_rows * terrain_cfg.horizontal_scale:.2f} x {terrain_cfg.total_cols * terrain_cfg.horizontal_scale:.2f}")
    print(f"  height_range_m: {terrain_data.height_field_raw.min() * terrain_cfg.vertical_scale:.3f} ~ {terrain_data.height_field_raw.max() * terrain_cfg.vertical_scale:.3f}")
    print(f"  focus_tile: row={args_cli.row}, col={args_cli.col}, terrain_idx={focus_idx}, terrain_name={focus_name}")
    print(f"  focus_origin: {focus_origin.tolist()}")
    print(f"  spawn_car: {args_cli.spawn_car}")

    if args_cli.save_usd:
        save_path = str(Path(args_cli.save_usd).expanduser().resolve())
        ok = sim_utils.save_stage(save_path, save_and_reload_in_place=False)
        print(f"  save_usd: {save_path}")
        print(f"  save_ok: {ok}")

    frame_count = 0
    while simulation_app.is_running():
        scene.write_data_to_sim()
        sim.step()
        scene.update(sim.get_physics_dt())
        frame_count += 1
        if args_cli.frames > 0 and frame_count >= args_cli.frames:
            break


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
