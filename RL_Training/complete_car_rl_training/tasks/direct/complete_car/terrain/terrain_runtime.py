"""Runtime terrain helper for direct complete-car tasks."""

from __future__ import annotations

from dataclasses import field

import torch
import trimesh

import isaaclab.sim as sim_utils
from isaaclab.sensors import RayCasterCfg, patterns
from isaaclab.terrains.utils import create_prim_from_mesh
from isaaclab.utils import configclass

from .terrain_generator import (
    STAGE1_TERRAIN_CLASS_GAP,
    STAGE1_TERRAIN_CLASS_OTHER,
    STAGE1_TERRAIN_CLASS_STEP,
    Stage1TerrainCfg,
    build_stage1_terrain_data,
)


@configclass
class CompleteCarTerrainRuntimeCfg:
    """Terrain parameters for direct complete-car tasks."""

    enabled: bool = False
    mode: str = "plane"
    prim_path: str = "/World/terrain/stage1"
    diffuse_color: tuple[float, float, float] = (0.42, 0.38, 0.30)
    static_friction: float = 1.0
    dynamic_friction: float = 1.0
    restitution: float = 0.0
    measure_heights: bool = False
    measured_points_x: list[float] = field(
        default_factory=lambda: [
            -0.8,
            -0.7,
            -0.6,
            -0.5,
            -0.4,
            -0.3,
            -0.2,
            -0.1,
            0.0,
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
        ]
    )
    measured_points_y: list[float] = field(
        default_factory=lambda: [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    )
    height_scanner_prim_path: str = "{ENV_REGEX_NS}/Robot/body"
    height_scanner_update_period: float = 0.02
    height_scanner_offset: tuple[float, float, float] = (0.0, 0.0, 20.0)
    flat_only_reset: bool = False
    curriculum: bool = False
    max_init_terrain_level: int = 0
    default_terrain_name: str = "flat"
    move_up_distance_ratio: float = 0.5
    move_down_command_ratio: float = 0.5
    step_spawn_back_range: tuple[float, float] = (2.0, 3.0)
    gap_spawn_back_range: tuple[float, float] = (0.0, 0.4)
    other_spawn_xy_range: tuple[float, float] = (-0.5, 0.5)
    generator: Stage1TerrainCfg = Stage1TerrainCfg()

    def build_height_scanner_cfg(self, ground_prim_path: str) -> RayCasterCfg:
        size_x = max(self.measured_points_x) - min(self.measured_points_x)
        size_y = max(self.measured_points_y) - min(self.measured_points_y)
        resolution_x = size_x / max(len(self.measured_points_x) - 1, 1)
        resolution_y = size_y / max(len(self.measured_points_y) - 1, 1)
        resolution = min(resolution_x, resolution_y)
        return RayCasterCfg(
            prim_path=self.height_scanner_prim_path,
            update_period=self.height_scanner_update_period,
            offset=RayCasterCfg.OffsetCfg(pos=self.height_scanner_offset),
            ray_alignment="yaw",
            pattern_cfg=patterns.GridPatternCfg(resolution=resolution, size=[size_x, size_y]),
            debug_vis=False,
            mesh_prim_paths=[ground_prim_path],
        )


def _offset_mesh_to_world_frame(terrain_cfg: Stage1TerrainCfg, terrain_mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    terrain_mesh = terrain_mesh.copy()
    terrain_mesh.vertices[:, 0] -= terrain_cfg.border_size
    terrain_mesh.vertices[:, 1] -= terrain_cfg.border_size
    return terrain_mesh


def _sample_uniform(value_range: tuple[float, float], shape: tuple[int, ...], device: torch.device) -> torch.Tensor:
    low, high = value_range
    return torch.empty(shape, device=device).uniform_(low, high)


class CompleteCarTerrainRuntime:
    """Runtime state for generated terrain, curriculum, and spawn offsets."""

    def __init__(self, cfg: CompleteCarTerrainRuntimeCfg, device: torch.device | str, num_envs: int):
        self.cfg = cfg
        self.device = torch.device(device)
        self.num_envs = num_envs
        self.curriculum_ready = False

        self._terrain_cfg = cfg.generator
        self._terrain_origins: torch.Tensor | None = None
        self._terrain_type_map: torch.Tensor | None = None
        self._terrain_class_map: torch.Tensor | None = None
        self.terrain_levels: torch.Tensor | None = None
        self.terrain_types: torch.Tensor | None = None
        self.terrain_classes: torch.Tensor | None = None
        self.default_terrain_type = 0
        self.max_terrain_level = 0
        self.ground_prim_path = "/World/ground"

    @property
    def generator_enabled(self) -> bool:
        return bool(self.cfg.enabled and self.cfg.mode == "generator")

    def setup_scene(self) -> str:
        if not self.generator_enabled:
            return self.ground_prim_path

        default_terrain_name = self.cfg.default_terrain_name
        if default_terrain_name not in self._terrain_cfg.terrain_names:
            raise ValueError(
                f"Unknown default terrain name '{default_terrain_name}'. Expected one of {self._terrain_cfg.terrain_names}."
            )

        self.default_terrain_type = self._terrain_cfg.terrain_names.index(default_terrain_name)
        terrain_data = build_stage1_terrain_data(self._terrain_cfg)
        terrain_mesh = trimesh.Trimesh(vertices=terrain_data.vertices, faces=terrain_data.faces)
        terrain_mesh = _offset_mesh_to_world_frame(self._terrain_cfg, terrain_mesh)

        if sim_utils.is_prim_path_valid(self.cfg.prim_path):
            sim_utils.delete_prim(self.cfg.prim_path)

        create_prim_from_mesh(
            self.cfg.prim_path,
            terrain_mesh,
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=self.cfg.diffuse_color),
            physics_material=sim_utils.RigidBodyMaterialCfg(
                friction_combine_mode="multiply",
                restitution_combine_mode="multiply",
                static_friction=self.cfg.static_friction,
                dynamic_friction=self.cfg.dynamic_friction,
                restitution=self.cfg.restitution,
            ),
        )

        self._terrain_origins = torch.from_numpy(terrain_data.env_origins).to(self.device, dtype=torch.float)
        self._terrain_type_map = torch.from_numpy(terrain_data.terrain_type).to(self.device, dtype=torch.long)
        self._terrain_class_map = torch.from_numpy(terrain_data.terrain_class).to(self.device, dtype=torch.long)
        self.max_terrain_level = self._terrain_cfg.num_rows
        self.ground_prim_path = self.cfg.prim_path
        return self.ground_prim_path

    def initialize_after_scene_clone(self, scene) -> None:
        if not self.generator_enabled:
            return
        self.terrain_levels = self._build_initial_terrain_levels()
        self.terrain_types = self._build_initial_terrain_types()
        self.terrain_classes = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self.sync_env_origins(scene)

    def initialize_plane_after_scene_clone(self, scene) -> None:
        if self.generator_enabled:
            return
        self.terrain_levels = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self.terrain_types = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self.terrain_classes = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self._terrain_origins = scene.env_origins.clone()

    def _build_initial_terrain_levels(self) -> torch.Tensor:
        max_init_level = min(self.cfg.max_init_terrain_level, self._terrain_cfg.num_rows - 1)
        if not self.cfg.curriculum:
            max_init_level = self._terrain_cfg.num_rows - 1
        return torch.randint(0, max_init_level + 1, (self.num_envs,), device=self.device, dtype=torch.long)

    def _build_initial_terrain_types(self) -> torch.Tensor:
        if self.cfg.flat_only_reset:
            return torch.full((self.num_envs,), self.default_terrain_type, device=self.device, dtype=torch.long)
        env_ids = torch.arange(self.num_envs, device=self.device, dtype=torch.long)
        terrain_types = env_ids * self._terrain_cfg.num_cols // self.num_envs
        return terrain_types.clamp_(max=self._terrain_cfg.num_cols - 1)

    def sync_env_origins(self, scene, env_ids: torch.Tensor | None = None) -> None:
        if not self.generator_enabled:
            return
        if env_ids is None:
            self.terrain_classes[:] = self._terrain_class_map[self.terrain_levels, self.terrain_types]
            scene.env_origins[:] = self._terrain_origins[self.terrain_levels, self.terrain_types]
            return
        self.terrain_classes[env_ids] = self._terrain_class_map[self.terrain_levels[env_ids], self.terrain_types[env_ids]]
        scene.env_origins[env_ids] = self._terrain_origins[self.terrain_levels[env_ids], self.terrain_types[env_ids]]

    def update_curriculum(self, scene, robot, env_ids: torch.Tensor, commands: torch.Tensor, episode_length_s: float) -> dict[str, float] | None:
        if not self.generator_enabled or not self.cfg.curriculum or not self.curriculum_ready or env_ids.numel() == 0:
            return None

        root_pos = robot.data.root_link_pos_w[env_ids]
        env_origins = scene.env_origins[env_ids]
        distance = torch.norm(root_pos[:, :2] - env_origins[:, :2], dim=1)
        required_distance = torch.norm(commands[env_ids, :2], dim=1) * episode_length_s * self.cfg.move_down_command_ratio

        move_up = distance > self._terrain_cfg.terrain_length * self.cfg.move_up_distance_ratio
        move_down = (distance < required_distance) & ~move_up

        self.terrain_levels[env_ids] += move_up.to(torch.long) - move_down.to(torch.long)
        self.terrain_levels[env_ids] = torch.where(
            self.terrain_levels[env_ids] >= self.max_terrain_level,
            torch.randint_like(self.terrain_levels[env_ids], self.max_terrain_level),
            self.terrain_levels[env_ids].clamp_(min=0),
        )
        self.sync_env_origins(scene, env_ids)

        return {
            "terrain_level": float(torch.mean(self.terrain_levels.float()).item()),
            "move_up_ratio": float(torch.mean(move_up.float()).item()),
            "move_down_ratio": float(torch.mean(move_down.float()).item()),
        }

    def apply_spawn_offsets(self, root_state: torch.Tensor, env_ids: torch.Tensor) -> torch.Tensor:
        if not self.generator_enabled or env_ids.numel() == 0:
            return root_state

        env_classes = self.terrain_classes[env_ids]
        step_mask = env_classes == STAGE1_TERRAIN_CLASS_STEP
        gap_mask = env_classes == STAGE1_TERRAIN_CLASS_GAP
        other_mask = env_classes == STAGE1_TERRAIN_CLASS_OTHER

        if torch.any(step_mask):
            root_state[step_mask, 0:1] -= _sample_uniform(
                self.cfg.step_spawn_back_range, (int(step_mask.sum().item()), 1), self.device
            )
        if torch.any(gap_mask):
            root_state[gap_mask, 0:1] -= _sample_uniform(
                self.cfg.gap_spawn_back_range, (int(gap_mask.sum().item()), 1), self.device
            )
        if torch.any(other_mask):
            root_state[other_mask, :2] += _sample_uniform(
                self.cfg.other_spawn_xy_range, (int(other_mask.sum().item()), 2), self.device
            )
        return root_state


__all__ = ["CompleteCarTerrainRuntime", "CompleteCarTerrainRuntimeCfg"]
