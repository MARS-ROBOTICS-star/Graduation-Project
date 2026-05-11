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
        "discrete obstacles",
    )


@dataclass
class _FakeRuntime:
    device: torch.device = torch.device("cpu")
    _terrain_cfg: _FakeTerrainCfg = field(default_factory=_FakeTerrainCfg)

    def get_tile_type_indices(self, _levels: torch.Tensor, terrain_types: torch.Tensor) -> torch.Tensor:
        col_to_type = torch.tensor([0, 1, 2, 3, 3, 4, 4, 4, 5, 5], device=terrain_types.device)
        return col_to_type[terrain_types.to(torch.long)]


@dataclass
class _FakeCurriculumCfg:
    enabled: bool = True
    max_init_terrain_level: int = 5
    initial_min_terrain_level_by_name: dict[str, int] = field(
        default_factory=lambda: {
            "stairs down": 1,
            "discrete obstacles": 1,
        }
    )
    initial_max_terrain_level_by_name: dict[str, int] = field(
        default_factory=lambda: {
            "stairs down": 1,
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

    stairs_down_mask = (terrain_types == 5) | (terrain_types == 6) | (terrain_types == 7)
    obstacles_mask = (terrain_types == 8) | (terrain_types == 9)

    assert torch.all(levels[stairs_down_mask] == 1)
    assert int(levels[obstacles_mask].min().item()) >= 1
    assert int(levels[obstacles_mask].max().item()) <= 2

    min_levels = curriculum.get_min_initial_terrain_levels(cfg, runtime, torch.arange(10, dtype=torch.long))
    assert torch.equal(min_levels[:5], torch.zeros(5, dtype=torch.long))
    assert torch.equal(min_levels[5:], torch.ones(5, dtype=torch.long))

    active_counts = torch.zeros(10, dtype=torch.long)
    unfinished_columns = torch.zeros(10, dtype=torch.bool)
    unfinished_columns[5:10] = True
    assignments = curriculum.assign_recycled_terrain_columns(active_counts, unfinished_columns, 50)
    assigned_counts = curriculum.compute_terrain_column_counts(assignments, 10)
    assert torch.equal(assigned_counts[:5], torch.zeros(5, dtype=torch.long))
    assert int(assigned_counts[5:10].min().item()) == 10
    assert int(assigned_counts[5:10].max().item()) == 10
    assert int(assigned_counts[5:8].sum().item()) == 30
    assert int(assigned_counts[8:10].sum().item()) == 20

    active_counts = torch.tensor([0, 0, 0, 0, 0, 16, 16, 16, 16, 15], dtype=torch.long)
    assignments = curriculum.assign_recycled_terrain_columns(active_counts, unfinished_columns, 5)
    assigned_counts = curriculum.compute_terrain_column_counts(assignments, 10)
    final_counts = active_counts + assigned_counts
    assert int(final_counts[5:10].min().item()) == 16
    assert int(final_counts[5:10].max().item()) == 17

    active_counts = torch.tensor([8, 8, 8, 8, 8, 18, 18, 18, 17, 17], dtype=torch.long)
    completed_columns = torch.zeros(10, dtype=torch.bool)
    completed_columns[:5] = True
    retention_count = curriculum.compute_completed_column_retention_count(
        active_counts,
        completed_columns,
        num_envs=128,
        retention_ratio=0.40,
        candidate_count=16,
    )
    assert retention_count == 12

    active_counts[:5] = torch.tensor([11, 11, 10, 10, 10], dtype=torch.long)
    retention_count = curriculum.compute_completed_column_retention_count(
        active_counts,
        completed_columns,
        num_envs=128,
        retention_ratio=0.40,
        candidate_count=16,
    )
    assert retention_count == 0

    retention_count = curriculum.compute_completed_column_retention_count(
        active_counts,
        torch.zeros(10, dtype=torch.bool),
        num_envs=128,
        retention_ratio=0.40,
        candidate_count=16,
    )
    assert retention_count == 0


if __name__ == "__main__":
    main()
