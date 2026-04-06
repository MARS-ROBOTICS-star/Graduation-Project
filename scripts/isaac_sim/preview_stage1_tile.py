"""Preview stage1 terrain tiles as separated meshes in Isaac Sim."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

from isaaclab.app import AppLauncher


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RL_PROJECT_ROOT = PROJECT_ROOT / "src" / "rl_lab" / "complete_car_rl_training"
if str(RL_PROJECT_ROOT) not in sys.path:
    sys.path.append(str(RL_PROJECT_ROOT))

STAGE1_TERRAIN_PATH = (
    RL_PROJECT_ROOT
    / "complete_car_rl_training"
    / "tasks"
    / "manager_based"
    / "complete_car_rl_training"
    / "stage1_terrain.py"
)


def load_stage1_terrain_module():
    """Load stage1_terrain.py directly to avoid importing the full task package tree."""
    spec = importlib.util.spec_from_file_location("stage1_terrain_local", STAGE1_TERRAIN_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load stage1 terrain module from {STAGE1_TERRAIN_PATH}")

    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


stage1_terrain_module = load_stage1_terrain_module()
Stage1TerrainCfg = stage1_terrain_module.Stage1TerrainCfg
convert_heightfield_to_trimesh = stage1_terrain_module.convert_heightfield_to_trimesh
get_origin_patch_center = stage1_terrain_module.get_origin_patch_center
get_origin_patch_radius = stage1_terrain_module.get_origin_patch_radius
get_terrain_name_from_idx = stage1_terrain_module.get_terrain_name_from_idx
make_tile_by_col = stage1_terrain_module.make_tile_by_col
make_tile_by_name = stage1_terrain_module.make_tile_by_name


parser = argparse.ArgumentParser(
    description="Preview local MGDP stage1 terrain tiles in Isaac Sim. Default mode loads all course tiles as separated meshes."
)
parser.add_argument(
    "--single-tile",
    action="store_true",
    default=False,
    help="Load only one tile. By default, the script loads all course-map tiles as separated meshes.",
)
parser.add_argument(
    "--row",
    type=int,
    default=0,
    help="Reference map row. In gallery mode, this selects the focus tile for summaries and optional car spawn.",
)
parser.add_argument(
    "--col",
    type=int,
    default=0,
    help="Reference map col. In gallery mode, this selects the focus tile for summaries and optional car spawn.",
)
parser.add_argument(
    "--terrain-name",
    type=str,
    default="",
    help="Optional explicit terrain name. If provided, the script automatically switches to single-tile mode.",
)
parser.add_argument(
    "--difficulty",
    type=float,
    default=None,
    help="Optional difficulty in [0, 1]. Used only in single-tile mode with --terrain-name.",
)
parser.add_argument(
    "--choice",
    type=float,
    default=None,
    help="Optional terrain-choice scalar. Used only in single-tile mode with --terrain-name.",
)
parser.add_argument(
    "--seed",
    type=int,
    default=None,
    help="Optional tile seed. Used only in single-tile mode with --terrain-name.",
)
parser.add_argument(
    "--tile-spacing",
    type=float,
    default=10.0,
    help="Center-to-center spacing used when laying out all course tiles as separated meshes.",
)
parser.add_argument(
    "--list-terrains",
    action="store_true",
    help="Print all supported stage1 terrain names and exit without launching Isaac Sim.",
)
parser.add_argument(
    "--show-origin",
    action=argparse.BooleanOptionalAction,
    default=True,
    help="Show or hide tile origin markers.",
)
parser.add_argument(
    "--center-at-origin",
    action=argparse.BooleanOptionalAction,
    default=True,
    help="Center each tile mesh at its own local origin before placing it in the scene.",
)
parser.add_argument("--frames", type=int, default=0, help="If > 0, stop after this many simulation steps.")
parser.add_argument("--spawn-car", action="store_true", default=False, help="Spawn the complete car on the focus tile.")
parser.add_argument("--save-usd", type=str, default="", help="Optional path to save the assembled preview stage as USD.")
parser.add_argument(
    "--car-height-offset",
    type=float,
    default=0.30,
    help="Extra height added above the focus tile origin when spawning the car.",
)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

if args_cli.list_terrains:
    cfg = Stage1TerrainCfg()
    print("[STAGE1_TILE_TERRAINS]")
    for terrain_name in cfg.terrain_names:
        print(f"  {terrain_name}")
    raise SystemExit(0)

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import numpy as np
import isaaclab.sim as sim_utils
import trimesh
from isaaclab.assets import AssetBaseCfg
from isaaclab.markers import VisualizationMarkers
from isaaclab.markers.config import FRAME_MARKER_CFG
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.sim import SimulationContext
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils import configclass

from complete_car_rl_training.tasks.manager_based.complete_car_env_cfg import (
    COMPLETE_CAR_CFG,
)


def is_single_tile_mode() -> bool:
    return args_cli.single_tile or bool(args_cli.terrain_name)


def sanitize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def validate_tile_indices(cfg: Stage1TerrainCfg, row: int, col: int) -> None:
    if not (0 <= row < cfg.num_rows):
        raise ValueError(f"--row must be in [0, {cfg.num_rows - 1}]")
    if not (0 <= col < cfg.num_cols):
        raise ValueError(f"--col must be in [0, {cfg.num_cols - 1}]")


def remove_default_plane(terrain_importer) -> None:
    """Remove the auto-created ground plane before importing custom tile meshes."""
    plane_path = f"{terrain_importer.cfg.prim_path}/terrain"
    if plane_path in terrain_importer.terrain_prim_paths:
        sim_utils.delete_prim(plane_path)
        terrain_importer.terrain_prim_paths = [path for path in terrain_importer.terrain_prim_paths if path != plane_path]


def derive_tile_seed(cfg: Stage1TerrainCfg, row: int, col: int, terrain_idx: int) -> int:
    """Mirror the current stage1 deterministic seed rule without importing a private helper."""
    return terrain_idx * cfg.num_rows * cfg.num_cols + row * cfg.num_cols + col


def resolve_tile_request(
    cfg: Stage1TerrainCfg,
    row: int,
    col: int,
    terrain_name: str = "",
) -> tuple[np.ndarray, int, str, float, float, int]:
    """Resolve a tile from map coordinates or an explicit terrain setting."""
    validate_tile_indices(cfg, row, col)

    if terrain_name:
        if terrain_name not in cfg.terrain_names:
            supported = ", ".join(cfg.terrain_names)
            raise ValueError(f"Unsupported --terrain-name '{terrain_name}'. Supported values: {supported}")

        terrain_idx = cfg.terrain_names.index(terrain_name)
        difficulty = args_cli.difficulty if args_cli.difficulty is not None else row / cfg.num_rows
        choice = args_cli.choice if args_cli.choice is not None else col / cfg.num_cols + 0.001
        seed = args_cli.seed if args_cli.seed is not None else derive_tile_seed(cfg, row, col, terrain_idx)
        if not (0.0 <= difficulty <= 1.0):
            raise ValueError("--difficulty must be in [0, 1]")

        tile = make_tile_by_name(cfg, terrain_name, difficulty, choice, seed)
        return tile, terrain_idx, terrain_name, difficulty, choice, seed

    tile, terrain_idx = make_tile_by_col(cfg, row, col)
    terrain_name = get_terrain_name_from_idx(cfg, terrain_idx)
    difficulty = row / cfg.num_rows
    choice = col / cfg.num_cols + 0.001
    seed = derive_tile_seed(cfg, row, col, terrain_idx)
    return tile, terrain_idx, terrain_name, difficulty, choice, seed


def compute_local_tile_origin(tile: np.ndarray, terrain_name: str, cfg: Stage1TerrainCfg) -> np.ndarray:
    """Compute the local tile origin using the same center-patch rule as stage1 map generation."""
    center_x, center_y = get_origin_patch_center(cfg, terrain_name)
    radius_x, radius_y = get_origin_patch_radius(cfg, terrain_name)

    x1 = max(0, center_x - radius_x)
    x2 = min(cfg.length_per_env_pixels, center_x + radius_x)
    y1 = max(0, center_y - radius_y)
    y2 = min(cfg.width_per_env_pixels, center_y + radius_y)

    if x2 <= x1:
        x2 = min(cfg.length_per_env_pixels, x1 + 1)
    if y2 <= y1:
        y2 = min(cfg.width_per_env_pixels, y1 + 1)

    tile_center_patch = tile[x1:x2, y1:y2]
    origin_z = max(0.0, float(tile_center_patch.max()) * cfg.vertical_scale)

    if args_cli.center_at_origin:
        return np.asarray([0.0, 0.0, origin_z], dtype=np.float32)

    return np.asarray([cfg.terrain_length / 2, cfg.terrain_width / 2, origin_z], dtype=np.float32)


def build_tile_mesh(tile: np.ndarray, cfg: Stage1TerrainCfg) -> trimesh.Trimesh:
    """Convert one tile heightfield into a trimesh."""
    vertices, faces, _ = convert_heightfield_to_trimesh(
        tile,
        cfg.horizontal_scale,
        cfg.vertical_scale,
        slope_threshold=cfg.slope_threshold,
    )
    terrain_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    if args_cli.center_at_origin:
        terrain_mesh = terrain_mesh.copy()
        terrain_mesh.vertices[:, 0] -= cfg.terrain_length / 2
        terrain_mesh.vertices[:, 1] -= cfg.terrain_width / 2

    return terrain_mesh


def offset_mesh(mesh: trimesh.Trimesh, translation: np.ndarray) -> trimesh.Trimesh:
    """Translate a tile mesh to its gallery position."""
    translated = mesh.copy()
    translated.vertices[:, 0] += float(translation[0])
    translated.vertices[:, 1] += float(translation[1])
    translated.vertices[:, 2] += float(translation[2])
    return translated


def compute_gallery_offset(cfg: Stage1TerrainCfg, row: int, col: int) -> np.ndarray:
    """Place all tiles in a centered gallery layout instead of stitching them into one big map."""
    gallery_x = (row - (cfg.num_rows - 1) / 2) * args_cli.tile_spacing
    gallery_y = (col - (cfg.num_cols - 1) / 2) * args_cli.tile_spacing
    return np.asarray([gallery_x, gallery_y, 0.0], dtype=np.float32)


def build_tile_entry(
    cfg: Stage1TerrainCfg,
    row: int,
    col: int,
    terrain_name: str = "",
    gallery_offset: np.ndarray | None = None,
) -> dict:
    """Build one standalone tile mesh entry for the scene."""
    tile, terrain_idx, resolved_name, difficulty, choice, seed = resolve_tile_request(cfg, row, col, terrain_name)
    mesh = build_tile_mesh(tile, cfg)
    local_origin = compute_local_tile_origin(tile, resolved_name, cfg)

    if gallery_offset is None:
        gallery_offset = np.zeros(3, dtype=np.float32)

    world_origin = gallery_offset + local_origin
    world_mesh = offset_mesh(mesh, gallery_offset)

    return {
        "row": row,
        "col": col,
        "terrain_idx": terrain_idx,
        "terrain_name": resolved_name,
        "difficulty": difficulty,
        "choice": choice,
        "seed": seed,
        "tile": tile,
        "origin": world_origin,
        "mesh": world_mesh,
        "prim_name": f"tile_r{row:02d}_c{col:02d}_{sanitize_name(resolved_name)}",
    }


def build_gallery_entries(cfg: Stage1TerrainCfg) -> list[dict]:
    """Build all course-map tiles as separated meshes."""
    entries: list[dict] = []
    for row in range(cfg.num_rows):
        for col in range(cfg.num_cols):
            entries.append(build_tile_entry(cfg, row, col, gallery_offset=compute_gallery_offset(cfg, row, col)))
    return entries


def find_focus_entry(entries: list[dict], cfg: Stage1TerrainCfg) -> dict:
    """Return the tile selected by --row/--col, or the only tile in single mode."""
    validate_tile_indices(cfg, args_cli.row, args_cli.col)
    for entry in entries:
        if entry["row"] == args_cli.row and entry["col"] == args_cli.col:
            return entry
    raise ValueError(f"Unable to find focus tile row={args_cli.row}, col={args_cli.col}.")


def build_origin_visualizer(origins: np.ndarray) -> VisualizationMarkers:
    """Create one frame marker at the origin of every standalone tile."""
    marker_cfg = FRAME_MARKER_CFG.replace(prim_path="/Visuals/TileOrigins")
    origin_visualizer = VisualizationMarkers(marker_cfg)
    origin_visualizer.visualize(translations=origins)
    return origin_visualizer


def set_single_tile_camera(sim: SimulationContext, focus_origin: np.ndarray) -> None:
    sim.set_camera_view(
        eye=[focus_origin[0] + 6.0, focus_origin[1] + 6.0, focus_origin[2] + 4.0],
        target=[focus_origin[0], focus_origin[1], focus_origin[2]],
    )


def set_gallery_camera(sim: SimulationContext, cfg: Stage1TerrainCfg) -> None:
    span_x = max(cfg.terrain_length, (cfg.num_rows - 1) * args_cli.tile_spacing + cfg.terrain_length)
    span_y = max(cfg.terrain_width, (cfg.num_cols - 1) * args_cli.tile_spacing + cfg.terrain_width)
    max_span = max(span_x, span_y)
    sim.set_camera_view(
        eye=[0.55 * max_span, 0.55 * max_span, 0.95 * max_span],
        target=[0.0, 0.0, 0.0],
    )


@configclass
class Stage1TilePreviewSceneCfg(InteractiveSceneCfg):
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

    if args_cli.spawn_car:
        robot = COMPLETE_CAR_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")


def main() -> None:
    terrain_cfg = Stage1TerrainCfg()
    validate_tile_indices(terrain_cfg, args_cli.row, args_cli.col)

    if is_single_tile_mode():
        entries = [build_tile_entry(terrain_cfg, args_cli.row, args_cli.col, terrain_name=args_cli.terrain_name)]
        mode_name = "single_tile"
    else:
        entries = build_gallery_entries(terrain_cfg)
        mode_name = "all_course_tiles"

    sim = SimulationContext(sim_utils.SimulationCfg(dt=1 / 120, device=args_cli.device))
    scene = InteractiveScene(Stage1TilePreviewSceneCfg(num_envs=1, env_spacing=1.0))

    remove_default_plane(scene.terrain)
    for entry in entries:
        scene.terrain.import_mesh(entry["prim_name"], entry["mesh"])

    origin_visualizer = None
    if args_cli.show_origin:
        origins = np.asarray([entry["origin"] for entry in entries], dtype=np.float32)
        origin_visualizer = build_origin_visualizer(origins)

    focus_entry = find_focus_entry(entries, terrain_cfg)

    sim.reset()
    if is_single_tile_mode():
        set_single_tile_camera(sim, focus_entry["origin"])
    else:
        set_gallery_camera(sim, terrain_cfg)

    if args_cli.spawn_car:
        robot = scene["robot"]
        root_state = robot.data.default_root_state.clone()
        root_state[:, 0] = focus_entry["origin"][0]
        root_state[:, 1] = focus_entry["origin"][1]
        root_state[:, 2] = focus_entry["origin"][2] + args_cli.car_height_offset
        robot.write_root_pose_to_sim(root_state[:, :7])
        robot.write_root_velocity_to_sim(root_state[:, 7:])
        robot.write_joint_state_to_sim(robot.data.default_joint_pos.clone(), robot.data.default_joint_vel.clone())

    max_height = max(float(entry["tile"].max()) * terrain_cfg.vertical_scale for entry in entries)
    min_height = min(float(entry["tile"].min()) * terrain_cfg.vertical_scale for entry in entries)

    print("[STAGE1_TILE_PREVIEW]")
    print(f"  mode: {mode_name}")
    print(f"  loaded_tiles: {len(entries)}")
    if not is_single_tile_mode():
        print(f"  rows x cols: {terrain_cfg.num_rows} x {terrain_cfg.num_cols}")
        print(f"  gallery_spacing_m: {args_cli.tile_spacing:.2f}")
        print("  stage_prim_pattern: /World/terrain/tile_rXX_cYY_<terrain_name>")
    print(
        f"  focus_tile: row={focus_entry['row']}, col={focus_entry['col']}, "
        f"terrain_idx={focus_entry['terrain_idx']}, terrain_name={focus_entry['terrain_name']}"
    )
    print(f"  focus_origin: {focus_entry['origin'].tolist()}")
    print(f"  tile_size_m: {terrain_cfg.terrain_length:.2f} x {terrain_cfg.terrain_width:.2f}")
    print(f"  tile_height_range_m: {min_height:.3f} ~ {max_height:.3f}")
    print(f"  show_origin: {args_cli.show_origin}")
    print(f"  center_at_origin: {args_cli.center_at_origin}")
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

    if origin_visualizer is not None:
        origin_visualizer.set_visibility(False)


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
