from __future__ import annotations

import trimesh
import torch
from isaaclab.envs import ManagerBasedRLEnv

from .stage1_terrain import Stage1TerrainCfg, build_stage1_terrain_data


class CompleteCarStage1Env(ManagerBasedRLEnv):
    def __init__(self, cfg, **kwargs):
        super().__init__(cfg=cfg, **kwargs)

        self._terrain_cfg = Stage1TerrainCfg()
        terrain_data = build_stage1_terrain_data(self._terrain_cfg)
        terrain_mesh = trimesh.Trimesh(
            vertices=terrain_data.vertices,
            faces=terrain_data.faces,
        )

        self.scene.terrain.import_mesh("stage1", terrain_mesh)
        self.scene.terrain.configure_env_origins(terrain_data.env_origins)
        self._terrain_levels = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self._terrain_types = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self._terrain_curriculum_ready = False

    def _reset_idx(self, env_ids: torch.Tensor | None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)

        if self._terrain_curriculum_ready and len(env_ids) > 0:
            root_pos = self.scene["robot"].data.root_pos_w[env_ids]
            env_origins = self.scene.env_origins[env_ids]
            distance = torch.norm(root_pos[:, :2] - env_origins[:, :2], dim=1)
            commands = self.command_manager.get_command("base_velocity")[env_ids]
            required_distance = torch.norm(commands[:, :2], dim=1) * self.cfg.episode_length_s * 0.5

            move_up = distance > self._terrain_cfg.terrain_length / 2
            move_down = (distance < required_distance) & ~move_up

            self.scene.terrain.update_env_origins(env_ids, move_up, move_down)

        super()._reset_idx(env_ids)
        self._terrain_curriculum_ready = True
