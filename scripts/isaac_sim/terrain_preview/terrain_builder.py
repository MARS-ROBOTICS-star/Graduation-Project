from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from pxr import Gf, PhysxSchema, Sdf, UsdGeom, UsdLux, UsdPhysics


@dataclass
class StaticBox:
    name: str
    center: tuple[float, float, float]
    size: tuple[float, float, float]
    color: tuple[float, float, float]


@dataclass
class TileSpec:
    name: str
    group: str
    length: float
    width: float
    horizontal_scale: float
    vertical_quantum: float
    builder: Callable[[int], tuple["HeightField", list[StaticBox]]]
    color: tuple[float, float, float] = (0.55, 0.48, 0.38)


class HeightField:
    def __init__(
        self,
        length: float,
        width: float,
        horizontal_scale: float,
        vertical_quantum: float,
        default_height: float = 0.0,
    ) -> None:
        self.length = float(length)
        self.width = float(width)
        self.horizontal_scale = float(horizontal_scale)
        self.vertical_quantum = float(vertical_quantum)
        self.xs = np.linspace(0.0, self.length, int(round(self.length / self.horizontal_scale)) + 1)
        self.ys = np.linspace(-self.width / 2.0, self.width / 2.0, int(round(self.width / self.horizontal_scale)) + 1)
        self.heights = np.full((len(self.xs), len(self.ys)), default_height, dtype=np.float32)
        self.quantize()

    def quantize(self) -> None:
        self.heights = (
            np.round(self.heights / self.vertical_quantum) * self.vertical_quantum
        ).astype(np.float32)

    def rect_mask(self, x_min: float, x_max: float, y_min: float, y_max: float) -> np.ndarray:
        x_mask = (self.xs >= x_min) & (self.xs <= x_max)
        y_mask = (self.ys >= y_min) & (self.ys <= y_max)
        return x_mask[:, None] & y_mask[None, :]

    def set_rect(self, x_min: float, x_max: float, y_min: float, y_max: float, height: float) -> None:
        self.heights[self.rect_mask(x_min, x_max, y_min, y_max)] = height
        self.quantize()

    def add_noise(
        self,
        seed: int,
        min_height: float,
        max_height: float,
        corridor_width: float | None = None,
    ) -> None:
        rng = np.random.default_rng(seed)
        noise = rng.uniform(min_height, max_height, size=self.heights.shape).astype(np.float32)
        mask = np.ones_like(self.heights, dtype=bool)
        if corridor_width is not None:
            mask &= np.abs(self.ys)[None, :] > corridor_width / 2.0
        self.heights = np.where(mask, self.heights + noise, self.heights)
        self.quantize()

    def apply_ramp(self, x_start: float, x_end: float, z_start: float, z_end: float) -> None:
        ramp_mask = (self.xs >= x_start) & (self.xs <= x_end)
        if not np.any(ramp_mask):
            return
        ratio = (self.xs[ramp_mask] - x_start) / max(x_end - x_start, 1e-6)
        ramp = z_start + ratio * (z_end - z_start)
        self.heights[ramp_mask, :] = ramp[:, None]
        self.quantize()

    def apply_stairs(
        self,
        x_start: float,
        x_end: float,
        step_depth: float,
        step_height: float,
        y_min: float,
        y_max: float,
    ) -> None:
        current_x = x_start
        current_height = 0.0
        while current_x < x_end:
            next_x = min(current_x + step_depth, x_end)
            self.set_rect(current_x, next_x, y_min, y_max, current_height)
            current_x = next_x
            current_height += step_height

    def to_mesh_data(self, origin: tuple[float, float, float]) -> tuple[list[Gf.Vec3f], list[int]]:
        points: list[Gf.Vec3f] = []
        indices: list[int] = []
        cols = len(self.ys)
        for i, x in enumerate(self.xs):
            for j, y in enumerate(self.ys):
                points.append(
                    Gf.Vec3f(
                        float(origin[0] + x),
                        float(origin[1] + y),
                        float(origin[2] + self.heights[i, j]),
                    )
                )
        for i in range(len(self.xs) - 1):
            for j in range(len(self.ys) - 1):
                idx0 = i * cols + j
                idx1 = idx0 + 1
                idx2 = idx0 + cols
                idx3 = idx2 + 1
                indices.extend([idx0, idx2, idx3, idx0, idx3, idx1])
        return points, indices

    def min_height(self) -> float:
        return float(np.min(self.heights))


def set_display_color(prim, color: tuple[float, float, float]) -> None:
    gprim = UsdGeom.Gprim(prim)
    gprim.CreateDisplayColorPrimvar(UsdGeom.Tokens.constant).Set([Gf.Vec3f(*color)])


def apply_static_mesh_collision(prim) -> None:
    UsdPhysics.CollisionAPI.Apply(prim)
    mesh_collision = UsdPhysics.MeshCollisionAPI.Apply(prim)
    mesh_collision.CreateApproximationAttr().Set("none")


def apply_box_collision(prim) -> None:
    UsdPhysics.CollisionAPI.Apply(prim)


def create_mesh(
    stage,
    path: str,
    points: list[Gf.Vec3f],
    face_vertex_indices: list[int],
    color: tuple[float, float, float],
):
    mesh = UsdGeom.Mesh.Define(stage, path)
    mesh.CreatePointsAttr(points)
    mesh.CreateFaceVertexCountsAttr([3] * (len(face_vertex_indices) // 3))
    mesh.CreateFaceVertexIndicesAttr(face_vertex_indices)
    mesh.CreateSubdivisionSchemeAttr("none")
    mesh.CreateExtentAttr().Set(mesh.ComputeExtent(points))
    set_display_color(mesh.GetPrim(), color)
    apply_static_mesh_collision(mesh.GetPrim())
    return mesh


def create_box(stage, path: str, box: StaticBox):
    cube = UsdGeom.Cube.Define(stage, path)
    cube.CreateSizeAttr(1.0)
    xformable = UsdGeom.Xformable(cube)

    translate_op = None
    scale_op = None
    for op in xformable.GetOrderedXformOps():
        if op.GetOpType() == UsdGeom.XformOp.TypeTranslate and translate_op is None:
            translate_op = op
        elif op.GetOpType() == UsdGeom.XformOp.TypeScale and scale_op is None:
            scale_op = op

    if translate_op is None:
        translate_op = xformable.AddTranslateOp(precision=UsdGeom.XformOp.PrecisionDouble)
    if scale_op is None:
        scale_op = xformable.AddScaleOp(precision=UsdGeom.XformOp.PrecisionFloat)

    translate_op.Set(Gf.Vec3d(*box.center))
    scale_op.Set(Gf.Vec3f(*box.size))
    set_display_color(cube.GetPrim(), box.color)
    apply_box_collision(cube.GetPrim())
    return cube


def sanitize(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


def stage1_ramp(seed: int) -> tuple[HeightField, list[StaticBox]]:
    hf = HeightField(length=8.0, width=8.0, horizontal_scale=0.10, vertical_quantum=0.005)
    hf.apply_ramp(1.0, 4.5, 0.0, 0.42)
    hf.apply_ramp(4.5, 7.0, 0.42, 0.0)
    hf.add_noise(seed, 0.0, 0.02, corridor_width=2.0)
    return hf, []


def stage1_stairs(seed: int) -> tuple[HeightField, list[StaticBox]]:
    hf = HeightField(length=8.0, width=8.0, horizontal_scale=0.10, vertical_quantum=0.005)
    hf.apply_stairs(1.0, 6.8, step_depth=0.45, step_height=0.05, y_min=-1.3, y_max=1.3)
    hf.add_noise(seed, 0.0, 0.015, corridor_width=2.8)
    return hf, []


def stage1_discrete_obstacles(seed: int) -> tuple[HeightField, list[StaticBox]]:
    hf = HeightField(length=8.0, width=8.0, horizontal_scale=0.10, vertical_quantum=0.005)
    rng = np.random.default_rng(seed)
    for _ in range(16):
        obs_length = rng.uniform(0.45, 1.20)
        obs_width = rng.uniform(0.35, 1.10)
        x = rng.uniform(1.0, 6.8)
        y = rng.uniform(-2.6, 2.6)
        height = rng.uniform(0.06, 0.24)
        hf.set_rect(x, min(7.6, x + obs_length), y, np.clip(y + obs_width, -4.0, 4.0), height)
    hf.set_rect(0.0, 1.2, -1.2, 1.2, 0.0)
    hf.set_rect(6.8, 8.0, -1.2, 1.2, 0.0)
    return hf, []


def stage1_gap(seed: int) -> tuple[HeightField, list[StaticBox]]:
    hf = HeightField(length=8.0, width=8.0, horizontal_scale=0.10, vertical_quantum=0.005)
    hf.add_noise(seed, 0.0, 0.015, corridor_width=2.2)
    hf.set_rect(3.1, 4.7, -1.0, 1.0, -0.80)
    return hf, []


def stage2_single_gap(seed: int) -> tuple[HeightField, list[StaticBox]]:
    hf = HeightField(length=10.0, width=4.0, horizontal_scale=0.05, vertical_quantum=0.005)
    hf.add_noise(seed, 0.0, 0.01, corridor_width=1.4)
    hf.set_rect(4.4, 5.4, -0.70, 0.70, -0.90)
    return hf, []


def stage2_stepping_stones(seed: int) -> tuple[HeightField, list[StaticBox]]:
    hf = HeightField(length=10.0, width=4.0, horizontal_scale=0.05, vertical_quantum=0.005, default_height=-0.85)
    hf.set_rect(0.0, 1.3, -1.0, 1.0, 0.0)
    hf.set_rect(8.7, 10.0, -1.0, 1.0, 0.0)
    rng = np.random.default_rng(seed)
    x = 1.6
    while x < 8.2:
        stone_len = float(rng.uniform(0.45, 0.75))
        stone_w = float(rng.uniform(0.55, 0.95))
        y = float(rng.uniform(-0.6, 0.6))
        height = float(rng.uniform(0.02, 0.20))
        hf.set_rect(x, min(8.4, x + stone_len), y - stone_w / 2.0, y + stone_w / 2.0, height)
        x += float(rng.uniform(0.65, 1.05))
    return hf, []


def stage2_bridge(seed: int) -> tuple[HeightField, list[StaticBox]]:
    hf = HeightField(length=10.0, width=4.0, horizontal_scale=0.05, vertical_quantum=0.005, default_height=-0.90)
    hf.set_rect(0.0, 1.2, -1.0, 1.0, 0.0)
    hf.set_rect(8.8, 10.0, -1.0, 1.0, 0.0)
    hf.set_rect(1.0, 9.0, -0.20, 0.20, 0.0)
    return hf, []


def stage2_air_beams(seed: int) -> tuple[HeightField, list[StaticBox]]:
    hf = HeightField(length=10.0, width=4.0, horizontal_scale=0.05, vertical_quantum=0.005, default_height=-1.00)
    hf.set_rect(0.0, 1.2, -1.0, 1.0, 0.0)
    hf.set_rect(8.8, 10.0, -1.0, 1.0, 0.0)
    rng = np.random.default_rng(seed)
    extras: list[StaticBox] = []
    x = 1.7
    index = 0
    while x < 8.0:
        beam_len = 0.48
        beam_width = 0.22
        beam_height = float(rng.uniform(0.08, 0.30))
        y = float(rng.uniform(-0.35, 0.35))
        extras.append(
            StaticBox(
                name=f"beam_{index}",
                center=(x, y, beam_height / 2.0),
                size=(beam_len, beam_width, beam_height),
                color=(0.85, 0.55, 0.18),
            )
        )
        x += float(rng.uniform(0.70, 1.00))
        index += 1
    return hf, extras


def stage2_corridor(seed: int) -> tuple[HeightField, list[StaticBox]]:
    hf = HeightField(length=10.0, width=4.0, horizontal_scale=0.05, vertical_quantum=0.005)
    hf.add_noise(seed, 0.0, 0.01, corridor_width=1.0)
    extras: list[StaticBox] = []
    segments = [
        (2.0, 0.95),
        (4.2, 0.75),
        (6.4, 0.60),
        (8.0, 0.90),
    ]
    for idx, (x_center, half_gap) in enumerate(segments):
        wall_len = 1.4
        wall_w = 0.18
        wall_h = 0.55
        extras.append(
            StaticBox(
                name=f"corridor_left_{idx}",
                center=(x_center, -(half_gap + wall_w / 2.0), wall_h / 2.0),
                size=(wall_len, wall_w, wall_h),
                color=(0.32, 0.37, 0.45),
            )
        )
        extras.append(
            StaticBox(
                name=f"corridor_right_{idx}",
                center=(x_center, half_gap + wall_w / 2.0, wall_h / 2.0),
                size=(wall_len, wall_w, wall_h),
                color=(0.32, 0.37, 0.45),
            )
        )
    return hf, extras


def build_gallery_specs(gallery: str) -> list[TileSpec]:
    specs: list[TileSpec] = []
    if gallery in ("stage1", "both"):
        specs.extend(
            [
                TileSpec("slope_ramp", "stage1_mix", 8.0, 8.0, 0.10, 0.005, stage1_ramp, (0.58, 0.49, 0.37)),
                TileSpec("stairs_up", "stage1_mix", 8.0, 8.0, 0.10, 0.005, stage1_stairs, (0.63, 0.53, 0.40)),
                TileSpec(
                    "discrete_obstacles",
                    "stage1_mix",
                    8.0,
                    8.0,
                    0.10,
                    0.005,
                    stage1_discrete_obstacles,
                    (0.56, 0.47, 0.35),
                ),
                TileSpec("gap", "stage1_mix", 8.0, 8.0, 0.10, 0.005, stage1_gap, (0.52, 0.45, 0.34)),
            ]
        )
    if gallery in ("stage2", "both"):
        specs.extend(
            [
                TileSpec("single_gap", "stage2_gap_parkour", 10.0, 4.0, 0.05, 0.005, stage2_single_gap, (0.40, 0.45, 0.47)),
                TileSpec(
                    "stepping_stones",
                    "stage2_gap_parkour",
                    10.0,
                    4.0,
                    0.05,
                    0.005,
                    stage2_stepping_stones,
                    (0.40, 0.47, 0.50),
                ),
                TileSpec("single_bridge", "stage2_gap_parkour", 10.0, 4.0, 0.05, 0.005, stage2_bridge, (0.38, 0.44, 0.48)),
                TileSpec("air_beams", "stage2_gap_parkour", 10.0, 4.0, 0.05, 0.005, stage2_air_beams, (0.37, 0.42, 0.47)),
                TileSpec("corridor", "stage2_gap_parkour", 10.0, 4.0, 0.05, 0.005, stage2_corridor, (0.35, 0.40, 0.44)),
            ]
        )
    return specs


def terrain_names() -> list[str]:
    return [spec.name for spec in build_gallery_specs("both")]


def build_single_spec(name: str) -> TileSpec:
    specs_by_name = {spec.name: spec for spec in build_gallery_specs("both")}
    if name not in specs_by_name:
        raise KeyError(f"Unknown terrain spec: {name}")
    return specs_by_name[name]


def create_tile(stage, parent_path: str, spec: TileSpec, origin: tuple[float, float, float], seed: int) -> None:
    tile_root = UsdGeom.Xform.Define(stage, f"{parent_path}/{sanitize(spec.name)}")
    hf, extras = spec.builder(seed)
    points, indices = hf.to_mesh_data(origin)
    create_mesh(stage, f"{tile_root.GetPath()}/terrain_surface", points, indices, spec.color)

    min_height = hf.min_height()
    base = StaticBox(
        name="tile_base",
        center=(origin[0] + spec.length / 2.0, origin[1], min_height - 0.20),
        size=(spec.length + 0.20, spec.width + 0.20, 0.20),
        color=(0.18, 0.18, 0.18),
    )
    create_box(stage, f"{tile_root.GetPath()}/{base.name}", base)

    for box in extras:
        shifted = StaticBox(
            name=box.name,
            center=(origin[0] + box.center[0], origin[1] + box.center[1], origin[2] + box.center[2]),
            size=box.size,
            color=box.color,
        )
        create_box(stage, f"{tile_root.GetPath()}/{sanitize(box.name)}", shifted)


def build_gallery_layout(
    stage,
    specs: list[TileSpec],
    root_path: str = "/World",
    seed_base: int = 7,
) -> tuple[np.ndarray, np.ndarray]:
    groups: dict[str, list[TileSpec]] = {}
    for spec in specs:
        groups.setdefault(spec.group, []).append(spec)

    all_centers: list[np.ndarray] = []
    all_extents: list[np.ndarray] = []
    group_root = UsdGeom.Xform.Define(stage, root_path)

    group_names = list(groups.keys())
    for group_index, group_name in enumerate(group_names):
        specs_in_group = groups[group_name]
        if group_name == "stage1_mix":
            x_gap = 10.0
            row_y = 7.0 if len(group_names) > 1 else 0.0
        else:
            x_gap = 12.0
            row_y = -7.0 if len(group_names) > 1 else 0.0
        group_path = f"{group_root.GetPath()}/{sanitize(group_name)}"
        UsdGeom.Xform.Define(stage, group_path)
        cursor_x = 0.0
        for tile_index, spec in enumerate(specs_in_group):
            origin = (cursor_x, row_y, 0.0)
            create_tile(stage, group_path, spec, origin, seed_base + group_index * 100 + tile_index)
            center = np.array([origin[0] + spec.length / 2.0, row_y, 0.0], dtype=np.float32)
            extent = np.array([spec.length / 2.0, spec.width / 2.0, 1.0], dtype=np.float32)
            all_centers.append(center)
            all_extents.append(extent)
            cursor_x += spec.length + x_gap

    center = np.mean(np.stack(all_centers), axis=0)
    extent = np.max(np.stack(all_extents), axis=0)
    return center, extent


def build_single_tile(
    stage,
    terrain_name: str,
    origin: tuple[float, float, float],
    seed: int = 7,
    root_path: str = "/World/terrain_preview",
) -> TileSpec:
    UsdGeom.Xform.Define(stage, root_path)
    spec = build_single_spec(terrain_name)
    create_tile(stage, root_path, spec, origin, seed)
    return spec


def setup_base_scene(stage) -> None:
    world = UsdGeom.Xform.Define(stage, "/World")
    stage.SetDefaultPrim(world.GetPrim())

    scene = UsdPhysics.Scene.Define(stage, Sdf.Path("/World/physicsScene"))
    scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(0.0, 0.0, -1.0))
    scene.CreateGravityMagnitudeAttr().Set(9.81)
    physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/World/physicsScene"))
    physx_scene.CreateEnableCCDAttr(True)
    physx_scene.CreateEnableStabilizationAttr(True)
    physx_scene.CreateEnableGPUDynamicsAttr(False)
    physx_scene.CreateBroadphaseTypeAttr("MBP")
    physx_scene.CreateSolverTypeAttr("TGS")

    distant = UsdLux.DistantLight.Define(stage, Sdf.Path("/World/DistantLight"))
    distant.CreateIntensityAttr(1400.0)
    distant.CreateAngleAttr(0.53)

    dome = UsdLux.DomeLight.Define(stage, Sdf.Path("/World/DomeLight"))
    dome.CreateIntensityAttr(250.0)
