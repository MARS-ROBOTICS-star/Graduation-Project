"""Dry-run checks for deterministic Stage1 terrain features."""

from __future__ import annotations

import importlib.util
import math
from dataclasses import dataclass
from pathlib import Path

import torch


REPO_ROOT = Path(__file__).resolve().parents[2]
TERRAIN_FEATURES_PATH = (
    REPO_ROOT
    / "RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terrain_features.py"
)


def _load_terrain_features_module():
    spec = importlib.util.spec_from_file_location("terrain_features", TERRAIN_FEATURES_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _build_axis_points(min_value: float, max_value: float, target_resolution: float) -> list[float]:
    num_points = int(round((max_value - min_value) / target_resolution)) + 1
    step = (max_value - min_value) / (num_points - 1)
    return [round(min_value + i * step, 6) for i in range(num_points)]


@dataclass
class _FakeTerrainCfg:
    patch_front_extent: float = 0.942209
    patch_rear_extent: float = 0.942209
    patch_half_width: float = 0.280374
    patch_preview_length: float = 1.0
    patch_rear_margin: float = 0.40
    patch_side_margin: float = 0.5
    patch_resolution_x: float = 0.10
    patch_resolution_y: float = 0.10
    patch_origin_offset_xy: tuple[float, float] = (0.0, 0.0)

    def _get_measured_points_x(self) -> list[float]:
        return _build_axis_points(
            -(self.patch_rear_extent + self.patch_rear_margin),
            self.patch_front_extent + self.patch_preview_length,
            self.patch_resolution_x,
        )

    def _get_measured_points_y(self) -> list[float]:
        return _build_axis_points(
            -(self.patch_half_width + self.patch_side_margin),
            self.patch_half_width + self.patch_side_margin,
            self.patch_resolution_y,
        )


@dataclass
class _FakeObservationCfg:
    terrain_feature_height_scale_m: float = 0.25


@dataclass
class _FakeCfg:
    terrain: _FakeTerrainCfg
    observations: _FakeObservationCfg


def _make_cfg() -> _FakeCfg:
    return _FakeCfg(terrain=_FakeTerrainCfg(), observations=_FakeObservationCfg())


def _grid(cfg: _FakeCfg) -> tuple[torch.Tensor, torch.Tensor]:
    x = torch.tensor(cfg.terrain._get_measured_points_x(), dtype=torch.float32)
    y = torch.tensor(cfg.terrain._get_measured_points_y(), dtype=torch.float32)
    return torch.meshgrid(x, y, indexing="ij")


def _height_patch_from_terrain_z(terrain_z: torch.Tensor) -> torch.Tensor:
    root_z = 1.0
    d_patch = root_z - terrain_z
    return d_patch.reshape(1, -1)


def _feature_index(module, name: str) -> int:
    return tuple(module.TERRAIN_FEATURE_NAMES).index(name)


def main() -> None:
    terrain_features = _load_terrain_features_module()
    cfg = _make_cfg()
    grid_x, grid_y = _grid(cfg)

    flat_patch = _height_patch_from_terrain_z(torch.zeros_like(grid_x))
    flat_features, flat_diag = terrain_features.compute_terrain_features(cfg, flat_patch)
    assert flat_features is not None
    assert flat_features.shape == (1, terrain_features.TERRAIN_FEATURE_DIM)
    assert terrain_features.TERRAIN_FEATURE_DIM == 28
    assert torch.isfinite(flat_features).all()
    assert abs(float(flat_diag["step_up_height_m"][0])) < 1.0e-6
    assert abs(float(flat_diag["drop_depth_m"][0])) < 1.0e-6
    assert float(flat_diag["g_flat"][0]) > 0.85
    assert float(flat_diag["g_flat"][0]) > float(flat_diag["g_step_up"][0])
    assert float(flat_diag["g_flat"][0]) > float(flat_diag["g_step_down"][0])

    step_up_z = torch.zeros_like(grid_x)
    step_up_z[grid_x > 0.50] = 0.12
    step_up_features, step_up_diag = terrain_features.compute_terrain_features(
        cfg,
        _height_patch_from_terrain_z(step_up_z),
    )
    assert step_up_features is not None
    assert torch.isfinite(step_up_features).all()
    assert float(step_up_diag["step_up_height_m"][0]) > 0.09
    assert float(step_up_diag["g_step_up"][0]) > 0.75
    assert step_up_features[0, _feature_index(terrain_features, "step_up_height_m")] > 0.35

    step_down_z = torch.zeros_like(grid_x)
    step_down_z[grid_x > 0.50] = -0.12
    step_down_features, step_down_diag = terrain_features.compute_terrain_features(
        cfg,
        _height_patch_from_terrain_z(step_down_z),
    )
    assert step_down_features is not None
    assert torch.isfinite(step_down_features).all()
    assert float(step_down_diag["drop_depth_m"][0]) > 0.09
    assert float(step_down_diag["g_step_down"][0]) > 0.75
    assert step_down_features[0, _feature_index(terrain_features, "drop_depth_m")] > 0.35

    left_high_z = torch.zeros_like(grid_x)
    left_track = (grid_y >= 0.15) & (grid_y <= 0.45) & (grid_x > cfg.terrain.patch_front_extent)
    left_high_z[left_track] = 0.10
    _, left_high_diag = terrain_features.compute_terrain_features(
        cfg,
        _height_patch_from_terrain_z(left_high_z),
    )
    assert float(left_high_diag["left_right_height_diff_m"][0]) > 0.05

    rough_z = torch.zeros_like(grid_x)
    front = grid_x > cfg.terrain.patch_front_extent
    rough_pattern = torch.where((torch.arange(grid_y.shape[1]) % 2).view(1, -1) == 0, 0.08, -0.08)
    rough_z[front] = rough_pattern.expand_as(rough_z)[front]
    rough_features, rough_diag = terrain_features.compute_terrain_features(
        cfg,
        _height_patch_from_terrain_z(rough_z),
    )
    assert rough_features is not None
    assert torch.isfinite(rough_features).all()
    assert float(rough_diag["front_roughness_m"][0]) > 0.05
    assert float(rough_diag["g_rough"][0]) > 0.85

    for diagnostics in (flat_diag, step_up_diag, step_down_diag, left_high_diag, rough_diag):
        assert not any(not math.isfinite(float(value.mean().item())) for value in diagnostics.values())


if __name__ == "__main__":
    main()
