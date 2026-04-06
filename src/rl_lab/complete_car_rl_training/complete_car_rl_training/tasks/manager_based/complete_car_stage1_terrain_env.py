from __future__ import annotations

import trimesh
import torch
import isaaclab.sim as sim_utils
from isaaclab.envs import ManagerBasedRLEnv
from isaaclab.terrains.utils import create_prim_from_mesh

from . import mdp
from .stage1_terrain import (
    Stage1TerrainCfg,
    build_stage1_terrain_data,
)


STAGE1_TERRAIN_PRIM_PATH = "/World/terrain/stage1"
STAGE1_TERRAIN_DIFFUSE_COLOR = (0.0, 0.0, 0.0)


def _offset_mesh_to_stage1_frame(terrain_cfg: Stage1TerrainCfg, terrain_mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Match MGDP's mesh placement, which shifts the full map by -border_size in x/y."""
    terrain_mesh = terrain_mesh.copy()
    terrain_mesh.vertices[:, 0] -= terrain_cfg.border_size
    terrain_mesh.vertices[:, 1] -= terrain_cfg.border_size
    return terrain_mesh


class CompleteCarStage1TerrainEnv(ManagerBasedRLEnv):
    def __init__(self, cfg, **kwargs):
        super().__init__(cfg=cfg, **kwargs)

        self._terrain_cfg = Stage1TerrainCfg()
        self._flat_terrain_type = self._terrain_cfg.terrain_names.index("flat")
        terrain_data = build_stage1_terrain_data(self._terrain_cfg)
        terrain_mesh = trimesh.Trimesh(
            vertices=terrain_data.vertices,
            faces=terrain_data.faces,
        )
        terrain_mesh = _offset_mesh_to_stage1_frame(self._terrain_cfg, terrain_mesh)

        if sim_utils.is_prim_path_valid(STAGE1_TERRAIN_PRIM_PATH):
            sim_utils.delete_prim(STAGE1_TERRAIN_PRIM_PATH)

        create_prim_from_mesh(
            STAGE1_TERRAIN_PRIM_PATH,
            terrain_mesh,
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=STAGE1_TERRAIN_DIFFUSE_COLOR),
            physics_material=sim_utils.RigidBodyMaterialCfg(
                friction_combine_mode="multiply",
                restitution_combine_mode="multiply",
                static_friction=1.0,
                dynamic_friction=1.0,
                restitution=0.0,
            ),
        )

        self._terrain_origins = torch.from_numpy(terrain_data.env_origins).to(self.device, dtype=torch.float)
        self._terrain_type_map = torch.from_numpy(terrain_data.terrain_type).to(self.device, dtype=torch.long)
        self._terrain_class_map = torch.from_numpy(terrain_data.terrain_class).to(self.device, dtype=torch.long)
        self._max_terrain_level = self._terrain_cfg.num_rows

        self._terrain_levels = self._build_initial_terrain_levels()
        self._terrain_types = self._build_initial_terrain_types()
        self._terrain_classes = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self.sync_env_origins_from_terrain_state()

        self.terrain_origins = self._terrain_origins
        self.terrain_types = self._terrain_types
        self.terrain_levels = self._terrain_levels
        self.terrain_class = self._terrain_class_map
        self.env_class = self._terrain_classes

        self._terrain_curriculum_ready = False

    def _build_initial_terrain_levels(self) -> torch.Tensor:
        max_init_level = min(self.cfg.stage1.max_init_terrain_level, self._terrain_cfg.num_rows - 1)
        if not self.cfg.stage1.curriculum:
            max_init_level = self._terrain_cfg.num_rows - 1
        return torch.randint(0, max_init_level + 1, (self.num_envs,), device=self.device, dtype=torch.long)

    def _build_initial_terrain_types(self) -> torch.Tensor:
        if self.cfg.stage1.flat_only_reset:
            return torch.full((self.num_envs,), self._flat_terrain_type, device=self.device, dtype=torch.long)
        env_ids = torch.arange(self.num_envs, device=self.device, dtype=torch.long)
        terrain_types = env_ids * self._terrain_cfg.num_cols // self.num_envs
        return terrain_types.clamp_(max=self._terrain_cfg.num_cols - 1)

    def sync_env_origins_from_terrain_state(self, env_ids: torch.Tensor | None = None) -> None:
        if env_ids is None:
            self._terrain_classes[:] = self._terrain_class_map[self._terrain_levels, self._terrain_types]
            self.scene.env_origins[:] = self._terrain_origins[self._terrain_levels, self._terrain_types]
        else:
            self._terrain_classes[env_ids] = self._terrain_class_map[
                self._terrain_levels[env_ids], self._terrain_types[env_ids]
            ]
            self.scene.env_origins[env_ids] = self._terrain_origins[
                self._terrain_levels[env_ids], self._terrain_types[env_ids]
            ]

    def _reset_idx(self, env_ids: torch.Tensor | None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)

        mdp.curriculums.update_stage1_terrain_curriculum(
            self,
            env_ids,
            command_name="base_velocity",
            move_up_distance_ratio=self.cfg.stage1.move_up_distance_ratio,
            move_down_command_ratio=self.cfg.stage1.move_down_command_ratio,
        )
        super()._reset_idx(env_ids)
        mdp.events.apply_stage1_spawn_offsets(
            self,
            env_ids,
            step_spawn_back_range=self.cfg.stage1.step_spawn_back_range,
            gap_spawn_back_range=self.cfg.stage1.gap_spawn_back_range,
            other_spawn_xy_range=self.cfg.stage1.other_spawn_xy_range,
        )
        self._terrain_curriculum_ready = True
