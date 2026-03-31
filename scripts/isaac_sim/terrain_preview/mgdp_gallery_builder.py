from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from pxr import Gf, UsdGeom

try:
    from terrain_preview.mgdp_port import Terrain, initialize_curriculum, make_stage1_cfg, make_stage2_cfg
    from terrain_preview.terrain_builder import StaticBox, create_box, create_mesh, sanitize
except ModuleNotFoundError:
    from mgdp_port import Terrain, initialize_curriculum, make_stage1_cfg, make_stage2_cfg
    from terrain_builder import StaticBox, create_box, create_mesh, sanitize


GALLERY_NAMES = ("stage1", "stage2", "both")
_STAGE1_PRIMARY_OFFSET = (-4.0, -4.0, 0.0)
_STAGE2_PRIMARY_OFFSET = (-5.0, -2.0, 0.0)
_STAGE2_BOTH_OFFSET = (-5.0, 178.0, 0.0)


@dataclass
class SectionBounds:
    min_corner: np.ndarray
    max_corner: np.ndarray


@dataclass
class BuiltSection:
    name: str
    bounds: SectionBounds
    spawn_origin: np.ndarray


@dataclass
class GalleryBuildSummary:
    gallery: str
    min_corner: np.ndarray
    max_corner: np.ndarray
    spawn_origin: np.ndarray

    @property
    def center(self) -> np.ndarray:
        return (self.min_corner + self.max_corner) / 2.0

    @property
    def extent(self) -> np.ndarray:
        return self.max_corner - self.min_corner


def gallery_names() -> tuple[str, ...]:
    return GALLERY_NAMES


def _apply_offset(vertices: np.ndarray, offset: tuple[float, float, float]) -> np.ndarray:
    shifted = np.asarray(vertices, dtype=np.float32).copy()
    shifted[:, 0] += float(offset[0])
    shifted[:, 1] += float(offset[1])
    shifted[:, 2] += float(offset[2])
    return shifted


def _to_gf_points(vertices: np.ndarray) -> list[Gf.Vec3f]:
    return [Gf.Vec3f(float(x), float(y), float(z)) for x, y, z in vertices]


def _triangle_indices(triangles: np.ndarray) -> list[int]:
    return [int(v) for v in np.asarray(triangles).reshape(-1)]


def _marker_color(level: int, max_level: int) -> tuple[float, float, float]:
    ratio = 0.0 if max_level <= 1 else level / (max_level - 1)
    return (0.20 + 0.60 * ratio, 0.70 - 0.35 * ratio, 0.25 + 0.40 * (1.0 - ratio))


def _terrain_bounds(vertices: np.ndarray) -> SectionBounds:
    return SectionBounds(min_corner=np.min(vertices, axis=0), max_corner=np.max(vertices, axis=0))


def _add_base_box(stage, path: str, bounds: SectionBounds, z_margin: float = 0.25) -> None:
    size = bounds.max_corner - bounds.min_corner
    center = (bounds.min_corner + bounds.max_corner) / 2.0
    base = StaticBox(
        name="tile_base",
        center=(float(center[0]), float(center[1]), float(bounds.min_corner[2] - z_margin)),
        size=(float(size[0] + 0.20), float(size[1] + 0.20), z_margin),
        color=(0.18, 0.18, 0.18),
    )
    create_box(stage, f"{path}/{base.name}", base)


def build_stage_section(
    stage,
    root_path: str,
    cfg,
    offset: tuple[float, float, float],
    num_envs: int,
    seed: int,
    include_markers: bool,
) -> BuiltSection:
    np.random.seed(seed)
    terrain = Terrain(cfg, num_envs)

    section_path = f"{root_path}/{sanitize(cfg.mesh_type)}"
    shifted_vertices = _apply_offset(terrain.vertices, offset)
    create_mesh(
        stage,
        f"{section_path}/terrain_surface",
        _to_gf_points(shifted_vertices),
        _triangle_indices(terrain.triangles),
        color=(0.48, 0.44, 0.38) if cfg.mesh_type == "mix" else (0.38, 0.44, 0.50),
    )

    bounds = _terrain_bounds(shifted_vertices)
    _add_base_box(stage, section_path, bounds)

    if getattr(terrain, "beam_vertices", None):
        for index, vertices in enumerate(terrain.beam_vertices):
            shifted = _apply_offset(vertices, offset)
            create_mesh(
                stage,
                f"{section_path}/air_beams/beam_{index:03d}",
                _to_gf_points(shifted),
                _triangle_indices(terrain.beam_triangles[index]),
                color=(0.82, 0.54, 0.20),
            )

    if getattr(terrain, "stone_vertices", None):
        for index, vertices in enumerate(terrain.stone_vertices):
            shifted = _apply_offset(vertices, offset)
            create_mesh(
                stage,
                f"{section_path}/air_stones/stone_{index:03d}",
                _to_gf_points(shifted),
                _triangle_indices(terrain.stone_triangles[index]),
                color=(0.62, 0.64, 0.68),
            )

    if include_markers:
        curriculum = initialize_curriculum(
            num_envs=num_envs,
            cfg=cfg,
            terrain=terrain,
            rng=np.random.default_rng(seed),
        )
        marker_root = f"{section_path}/curriculum_markers"
        max_level = int(cfg.num_rows)
        for env_index, origin in enumerate(curriculum.env_origins):
            level = int(curriculum.terrain_levels[env_index])
            marker = StaticBox(
                name=f"env_{env_index:03d}",
                center=(
                    float(offset[0] + origin[0]),
                    float(offset[1] + origin[1]),
                    float(offset[2] + origin[2] + 0.25),
                ),
                size=(0.28, 0.28, 0.28),
                color=_marker_color(level, max_level),
            )
            create_box(stage, f"{marker_root}/{marker.name}", marker)

        level_hist = np.bincount(curriculum.terrain_levels, minlength=int(cfg.num_rows))
        type_hist = np.bincount(curriculum.terrain_types, minlength=int(cfg.num_cols))
        print(f"[{cfg.mesh_type}] terrain grid: rows={cfg.num_rows}, cols={cfg.num_cols}, env_markers={num_envs}")
        print(f"[{cfg.mesh_type}] curriculum level histogram: {level_hist.tolist()}")
        print(f"[{cfg.mesh_type}] curriculum type histogram: {type_hist.tolist()}")

    spawn_origin = np.asarray(terrain.env_origins[0, 0], dtype=np.float32) + np.asarray(offset, dtype=np.float32)
    return BuiltSection(name=cfg.mesh_type, bounds=bounds, spawn_origin=spawn_origin)


def build_mgdp_gallery(
    stage,
    gallery: str,
    root_path: str = "/World/terrain_preview",
    seed: int = 7,
    curriculum_envs: int = 64,
    include_markers: bool = True,
) -> GalleryBuildSummary:
    if gallery not in GALLERY_NAMES:
        raise KeyError(f"Unknown MGDP gallery: {gallery}")

    UsdGeom.Xform.Define(stage, root_path)
    built_sections: list[BuiltSection] = []

    if gallery in ("stage1", "both"):
        stage1_offset = _STAGE1_PRIMARY_OFFSET
        built_sections.append(
            build_stage_section(
                stage=stage,
                root_path=root_path,
                cfg=make_stage1_cfg(),
                offset=stage1_offset,
                num_envs=curriculum_envs,
                seed=seed,
                include_markers=include_markers,
            )
        )

    if gallery in ("stage2", "both"):
        stage2_offset = _STAGE2_PRIMARY_OFFSET if gallery == "stage2" else _STAGE2_BOTH_OFFSET
        built_sections.append(
            build_stage_section(
                stage=stage,
                root_path=root_path,
                cfg=make_stage2_cfg(),
                offset=stage2_offset,
                num_envs=curriculum_envs,
                seed=seed + 1000,
                include_markers=include_markers,
            )
        )

    min_corner = np.min(np.stack([section.bounds.min_corner for section in built_sections]), axis=0)
    max_corner = np.max(np.stack([section.bounds.max_corner for section in built_sections]), axis=0)
    spawn_origin = built_sections[0].spawn_origin.copy()
    return GalleryBuildSummary(
        gallery=gallery,
        min_corner=min_corner,
        max_corner=max_corner,
        spawn_origin=spawn_origin,
    )
