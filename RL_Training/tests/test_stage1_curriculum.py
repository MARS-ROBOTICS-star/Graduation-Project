"""Dry-run checks for Stage1 terrain curriculum row sampling."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from pathlib import Path

import torch


REPO_ROOT = Path(__file__).resolve().parents[2]
CURRICULUM_PATH = (
    REPO_ROOT
    / "RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/curriculum.py"
)


def _load_curriculum_module():
    spec = importlib.util.spec_from_file_location("curriculum", CURRICULUM_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@dataclass
class _FakeTerrainCfg:
    num_rows: int = 20
    num_cols: int = 10
    terrain_names: tuple[str, ...] = (
        "flat",
        "slope down",
        "slope up",
        "uneven rough",
        "stairs down",
        "stairs up",
        "discrete obstacles",
    )


@dataclass
class _FakeRuntime:
    device: torch.device = torch.device("cpu")
    _terrain_cfg: _FakeTerrainCfg = field(default_factory=_FakeTerrainCfg)

    def get_tile_type_indices(self, _levels: torch.Tensor, terrain_types: torch.Tensor) -> torch.Tensor:
        col_to_type = torch.tensor([0, 1, 2, 3, 3, 4, 4, 5, 5, 6], device=terrain_types.device)
        return col_to_type[terrain_types.to(torch.long)]


@dataclass
class _FakeCurriculumCfg:
    enabled: bool = True
    max_init_terrain_level: int = 5
    initial_min_terrain_level_by_name: dict[str, int] = field(
        default_factory=lambda: {
            "stairs down": 1,
            "stairs up": 1,
            "discrete obstacles": 1,
        }
    )
    initial_max_terrain_level_by_name: dict[str, int] = field(
        default_factory=lambda: {
            "stairs down": 1,
            "stairs up": 1,
            "discrete obstacles": 2,
        }
    )


def main() -> None:
    curriculum = _load_curriculum_module()
    cfg = _FakeCurriculumCfg()
    runtime = _FakeRuntime()

    terrain_types = torch.arange(10, dtype=torch.long).repeat(256)
    levels = curriculum.sample_initial_terrain_levels(cfg, runtime, terrain_types)

    non_step_mask = terrain_types <= 4
    assert int(levels[non_step_mask].min().item()) >= 0
    assert int(levels[non_step_mask].max().item()) <= 5

    stairs_down_mask = (terrain_types == 5) | (terrain_types == 6)
    stairs_up_mask = (terrain_types == 7) | (terrain_types == 8)
    obstacles_mask = terrain_types == 9

    assert torch.all(levels[stairs_down_mask] == 1)
    assert torch.all(levels[stairs_up_mask] == 1)
    assert int(levels[obstacles_mask].min().item()) >= 1
    assert int(levels[obstacles_mask].max().item()) <= 2

    min_levels = curriculum.get_min_initial_terrain_levels(cfg, runtime, torch.arange(10, dtype=torch.long))
    assert torch.equal(min_levels[:5], torch.zeros(5, dtype=torch.long))
    assert torch.equal(min_levels[5:], torch.ones(5, dtype=torch.long))


if __name__ == "__main__":
    main()
