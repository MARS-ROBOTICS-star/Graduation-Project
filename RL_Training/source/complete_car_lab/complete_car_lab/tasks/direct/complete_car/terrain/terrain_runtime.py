"""训练期 terrain runtime、curriculum 和 reset 绑定逻辑。"""

from __future__ import annotations

import torch
import trimesh

import isaaclab.sim as sim_utils
from isaaclab.terrains.utils import create_prim_from_mesh

from .terrain_builder import build_stage1_terrain_data
from .terrain_cfg import (
    CompleteCarTerrainRuntimeCfg,
    STAGE1_TERRAIN_CLASS_GAP,
    STAGE1_TERRAIN_CLASS_OTHER,
    STAGE1_TERRAIN_CLASS_STEP,
)
from ..utils.math_utils import yaw_quaternion


def _offset_mesh_to_world_frame(terrain_cfg, terrain_mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    terrain_mesh = terrain_mesh.copy()
    terrain_mesh.vertices[:, 0] -= terrain_cfg.border_size
    terrain_mesh.vertices[:, 1] -= terrain_cfg.border_size
    return terrain_mesh


def _sample_uniform(value_range: tuple[float, float], shape: tuple[int, ...], device: torch.device) -> torch.Tensor:
    low, high = value_range
    return torch.empty(shape, device=device).uniform_(low, high)


class CompleteCarTerrainRuntime:
    """运行时只负责场景构建、curriculum 和 reset spawn 偏移。"""

    def __init__(self, terrain_cfg: CompleteCarTerrainRuntimeCfg, curriculum_cfg, device: torch.device | str, num_envs: int):
        self.cfg = terrain_cfg
        self.curriculum_cfg = curriculum_cfg
        self.device = torch.device(device)
        self.num_envs = num_envs
        self.curriculum_ready = False

        self._terrain_cfg = terrain_cfg.generator
        self._terrain_origins: torch.Tensor | None = None
        self._terrain_type_map: torch.Tensor | None = None
        self._terrain_class_map: torch.Tensor | None = None
        self.terrain_levels: torch.Tensor | None = None
        self.terrain_types: torch.Tensor | None = None
        self.terrain_classes: torch.Tensor | None = None
        self.default_terrain_type = 0
        self.max_terrain_level = 0
        self.ground_prim_path = "/World/ground"

        self._height_field_raw: torch.Tensor | None = None
        self._horizontal_scale: float = float(self._terrain_cfg.horizontal_scale)
        self._vertical_scale: float = float(self._terrain_cfg.vertical_scale)
        self._border_size: float = float(self._terrain_cfg.border_size)

    @property
    def generator_enabled(self) -> bool:
        return bool(self.cfg.enabled and self.cfg.mode == "generator")

    def setup_scene(self) -> str:
        if not self.generator_enabled:
            return self.ground_prim_path

        default_terrain_name = self.curriculum_cfg.default_terrain_name
        if default_terrain_name not in self._terrain_cfg.terrain_names:
            raise ValueError(
                f"Unknown default terrain name '{default_terrain_name}'. Expected one of {self._terrain_cfg.terrain_names}."
            )

        self.default_terrain_type = self._terrain_cfg.terrain_names.index(default_terrain_name)
        terrain_data = build_stage1_terrain_data(self._terrain_cfg) #生成完整训练地形的数据结构
        self._height_field_raw = torch.from_numpy(terrain_data.height_field_raw).to(self.device, dtype=torch.float32) #转为tensor,放到device
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

    def initialize_plane_after_scene_clone(self, scene) -> None:
        if self.generator_enabled:
            return
        self._height_field_raw = None
        self.terrain_levels = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self.terrain_types = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self.terrain_classes = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self._terrain_origins = scene.env_origins.clone()

    def sync_env_origins(self, scene, env_ids: torch.Tensor | None = None) -> None:
        if not self.generator_enabled:
            return
        if env_ids is None:
            self.terrain_classes[:] = self._terrain_class_map[self.terrain_levels, self.terrain_types]
            scene.env_origins[:] = self._terrain_origins[self.terrain_levels, self.terrain_types]
            return
        self.terrain_classes[env_ids] = self._terrain_class_map[self.terrain_levels[env_ids], self.terrain_types[env_ids]]
        scene.env_origins[env_ids] = self._terrain_origins[self.terrain_levels[env_ids], self.terrain_types[env_ids]]

    def get_tile_origins(self, terrain_levels: torch.Tensor, terrain_types: torch.Tensor) -> torch.Tensor:
        if self._terrain_origins is None:
            raise RuntimeError("Terrain origins are not initialized.")
        return self._terrain_origins[terrain_levels, terrain_types]

    def get_tile_type_indices(self, terrain_levels: torch.Tensor, terrain_types: torch.Tensor) -> torch.Tensor:
        if self._terrain_type_map is None:
            raise RuntimeError("Terrain type map is not initialized.")
        return self._terrain_type_map[terrain_levels, terrain_types]

    def get_tile_x_bounds(self, terrain_levels: torch.Tensor, terrain_types: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        origins = self.get_tile_origins(terrain_levels, terrain_types)
        half_length = 0.5 * float(self._terrain_cfg.terrain_length)
        tile_origin_x = origins[:, 0]
        return tile_origin_x - half_length, tile_origin_x, tile_origin_x + half_length

    def apply_spawn_offsets(self, root_state: torch.Tensor, env_ids: torch.Tensor) -> torch.Tensor:
        if not self.generator_enabled or env_ids.numel() == 0:
            return root_state

        env_classes = self.terrain_classes[env_ids]
        step_mask = env_classes == STAGE1_TERRAIN_CLASS_STEP
        gap_mask = env_classes == STAGE1_TERRAIN_CLASS_GAP
        other_mask = env_classes == STAGE1_TERRAIN_CLASS_OTHER

        if torch.any(step_mask):
            step_env_ids = env_ids[step_mask]
            num_step = int(step_env_ids.numel())
            tile_origins = self.get_tile_origins(
                self.terrain_levels[step_env_ids],
                self.terrain_types[step_env_ids],
            ).to(device=self.device, dtype=root_state.dtype)
            tile_start_x = tile_origins[:, 0] - 0.5 * float(self._terrain_cfg.terrain_length)
            spawn_back = _sample_uniform(self.cfg.step_approach_spawn_back_range, (num_step,), self.device).to(root_state.dtype)
            spawn_lateral = _sample_uniform(self.cfg.step_approach_spawn_lateral_range, (num_step,), self.device).to(
                root_state.dtype
            )
            spawn_xy = torch.stack(
                (
                    tile_start_x - spawn_back,
                    tile_origins[:, 1] + spawn_lateral,
                ),
                dim=-1,
            )
            root_state[step_mask, 0:2] = spawn_xy
            root_state[step_mask, 2] = (
                self.sample_heights_world_xy(spawn_xy).to(dtype=root_state.dtype)
                + float(self.cfg.base_spawn_clearance)
            )
            root_state[step_mask, 3:7] = yaw_quaternion(torch.zeros(num_step, device=self.device, dtype=root_state.dtype))
        if torch.any(gap_mask):
            root_state[gap_mask, 0:1] -= _sample_uniform(
                self.cfg.gap_spawn_back_range, (int(gap_mask.sum().item()), 1), self.device
            )
        if torch.any(other_mask):
            root_state[other_mask, :2] += _sample_uniform(
                self.cfg.other_spawn_xy_range, (int(other_mask.sum().item()), 2), self.device
            )
        return root_state
    
    # 输入世界坐标系下的一批二维点，在height_field_raw做双线性插值，输出点对应的地形高度
    def sample_heights_world_xy(self, points_xy_w: torch.Tensor) -> torch.Tensor:
        if self._height_field_raw is None:
            return torch.zeros(points_xy_w.shape[:-1], device=self.device, dtype=torch.float32)
        hf = self._height_field_raw
        max_x_index = hf.shape[0] - 1
        max_y_index = hf.shape[1] - 1

        x_index = (points_xy_w[..., 0] + self._border_size) / self._horizontal_scale
        y_index = (points_xy_w[..., 1] + self._border_size) / self._horizontal_scale

        x0 = torch.floor(x_index).long().clamp(0, max_x_index - 1)
        y0 = torch.floor(y_index).long().clamp(0, max_y_index - 1)
        x1 = (x0 + 1).clamp(max=max_x_index)
        y1 = (y0 + 1).clamp(max=max_y_index)

        wx = (x_index - x0.float()).clamp(0.0, 1.0)
        wy = (y_index - y0.float()).clamp(0.0, 1.0)

        h00 = hf[x0, y0]
        h01 = hf[x0, y1]
        h10 = hf[x1, y0]
        h11 = hf[x1, y1]

        height_raw = (
            (1.0 - wx) * (1.0 - wy) * h00
            + (1.0 - wx) * wy * h01
            + wx * (1.0 - wy) * h10
            + wx * wy * h11
        )
        return height_raw * self._vertical_scale

__all__ = ["CompleteCarTerrainRuntime"]
