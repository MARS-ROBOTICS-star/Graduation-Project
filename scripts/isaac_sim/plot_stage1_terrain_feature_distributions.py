"""Plot Stage1 terrain-feature distributions from generated terrain tiles.

This script samples the Stage1 terrain generator directly, then applies the same
geometric feature logic used by the 28-D terrain actor features. It is intended
to validate threshold choices such as 0.02 m edge detection and -0.06 m gap
width counting.
"""

from __future__ import annotations

import csv
import importlib.util
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
    }
)


REPO_ROOT = Path(__file__).resolve().parents[2]
TERRAIN_BUILDER_PATH = (
    REPO_ROOT
    / "RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_builder.py"
)
OUTPUT_PNG = REPO_ROOT / "results/stage1_terrain_feature_distributions.png"
OUTPUT_CSV = REPO_ROOT / "results/stage1_terrain_feature_distribution_samples.csv"
OUTPUT_SUMMARY_CSV = REPO_ROOT / "results/stage1_terrain_feature_distribution_summary.csv"


PATCH_FRONT_EXTENT = 0.942209
PATCH_REAR_EXTENT = 0.942209
PATCH_HALF_WIDTH = 0.280374
PATCH_PREVIEW_LENGTH = 1.0
PATCH_REAR_MARGIN = 0.40
PATCH_SIDE_MARGIN = 0.50
PATCH_RESOLUTION_X = 0.10
PATCH_RESOLUTION_Y = 0.10

EDGE_DISTANCE_THRESHOLD_M = 0.02
GAP_DEPTH_THRESHOLD_M = 0.06
STEP_GATE_THRESHOLD_M = 0.08
GATE_SIGMA_M = 0.02
ROUGH_GATE_THRESHOLD_M = 0.03
ROUGH_SIGMA_M = 0.01

TERRAIN_GROUPS: dict[str, tuple[str, ...]] = {
    "flat": ("flat",),
    "rough": ("uneven rough",),
    "stairs": ("stairs up", "stairs down"),
    "obstacles": ("discrete obstacles",),
}


def _load_terrain_builder():
    spec = importlib.util.spec_from_file_location("stage1_terrain_builder", TERRAIN_BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load terrain builder from {TERRAIN_BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _axis_points(min_value: float, max_value: float, target_resolution: float) -> np.ndarray:
    num_points = int(round((max_value - min_value) / target_resolution)) + 1
    if num_points < 2:
        return np.asarray([round(min_value, 6)], dtype=np.float64)
    step = (max_value - min_value) / (num_points - 1)
    return np.asarray([round(min_value + i * step, 6) for i in range(num_points)], dtype=np.float64)


def _bilinear_sample(tile_m: np.ndarray, cfg, sample_x_m: np.ndarray, sample_y_m: np.ndarray) -> np.ndarray:
    x_idx = np.clip(sample_x_m / cfg.horizontal_scale, 0.0, tile_m.shape[0] - 1.0)
    y_idx = np.clip(sample_y_m / cfg.horizontal_scale, 0.0, tile_m.shape[1] - 1.0)

    x0 = np.floor(x_idx).astype(np.int64)
    y0 = np.floor(y_idx).astype(np.int64)
    x1 = np.clip(x0 + 1, 0, tile_m.shape[0] - 1)
    y1 = np.clip(y0 + 1, 0, tile_m.shape[1] - 1)

    wx = x_idx - x0
    wy = y_idx - y0
    v00 = tile_m[x0, y0]
    v10 = tile_m[x1, y0]
    v01 = tile_m[x0, y1]
    v11 = tile_m[x1, y1]
    return (1.0 - wx) * (1.0 - wy) * v00 + wx * (1.0 - wy) * v10 + (1.0 - wx) * wy * v01 + wx * wy * v11


def _sigmoid(value: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-value))


def _nearest_distance_norm(jumps_m: np.ndarray, transition_x: np.ndarray, threshold_m: float) -> float:
    if jumps_m.size == 0:
        return 0.0
    max_distance = max(float(np.max(transition_x)), 1.0e-6)
    detected = jumps_m > threshold_m
    if not np.any(detected):
        return 1.0
    return float(np.clip(np.min(transition_x[detected]) / max_distance, 0.0, 1.0))


def _compute_patch_features(h_patch_m: np.ndarray, x_points: np.ndarray, y_points: np.ndarray) -> dict[str, float]:
    center_x = (x_points >= -0.30) & (x_points <= 0.30)
    center_y = np.abs(y_points) <= 0.20
    d_ref_m = float(np.median(h_patch_m[np.ix_(center_x, center_y)]))
    h_rel_m = h_patch_m - d_ref_m

    front_preview = x_points > PATCH_FRONT_EXTENT
    x_nonnegative = x_points >= 0.0
    center_track = np.abs(y_points) <= 0.20

    front_m = h_rel_m[front_preview, :]
    h_front_mean_m = float(np.mean(front_m))
    h_front_max_m = float(np.max(front_m))
    h_front_min_m = float(np.min(front_m))
    front_roughness_m = float(np.std(front_m))

    profile_m = np.median(h_rel_m[:, center_track], axis=1)
    d_profile_m = profile_m[1:] - profile_m[:-1]
    transition_x = 0.5 * (x_points[1:] + x_points[:-1])
    future_transition = transition_x >= 0.0
    future_d_profile_m = d_profile_m[future_transition]
    future_transition_x = np.clip(transition_x[future_transition], 0.0, None)

    step_up_jumps_m = np.maximum(future_d_profile_m, 0.0)
    drop_jumps_m = np.maximum(-future_d_profile_m, 0.0)
    step_up_height_m = float(np.max(step_up_jumps_m)) if step_up_jumps_m.size else 0.0
    drop_depth_m = float(np.max(drop_jumps_m)) if drop_jumps_m.size else 0.0
    step_up_distance_norm = _nearest_distance_norm(
        step_up_jumps_m,
        future_transition_x,
        EDGE_DISTANCE_THRESHOLD_M,
    )
    drop_distance_norm = _nearest_distance_norm(
        drop_jumps_m,
        future_transition_x,
        EDGE_DISTANCE_THRESHOLD_M,
    )

    front_profile_m = profile_m[x_nonnegative]
    front_profile_x = x_points[x_nonnegative]
    front_x_span = max(float(front_profile_x[-1] - front_profile_x[0]), 1.0e-6)
    gap_width_norm = float(np.mean(front_profile_m < -GAP_DEPTH_THRESHOLD_M))
    front_slope = float(np.clip((front_profile_m[-1] - front_profile_m[0]) / front_x_span, -1.0, 1.0))

    g_step_up = float(_sigmoid((step_up_height_m - STEP_GATE_THRESHOLD_M) / GATE_SIGMA_M))
    g_step_down = float(_sigmoid((drop_depth_m - STEP_GATE_THRESHOLD_M) / GATE_SIGMA_M))
    g_gap = float(g_step_down * _sigmoid((gap_width_norm - 0.15) / 0.05))
    g_rough = float(_sigmoid((front_roughness_m - ROUGH_GATE_THRESHOLD_M) / ROUGH_SIGMA_M))

    return {
        "step_up_height_m": step_up_height_m,
        "drop_depth_m": drop_depth_m,
        "step_up_distance_norm": step_up_distance_norm,
        "drop_distance_norm": drop_distance_norm,
        "gap_width_norm": gap_width_norm,
        "front_slope": front_slope,
        "front_roughness_m": front_roughness_m,
        "h_front_min_m": h_front_min_m,
        "h_front_mean_m": h_front_mean_m,
        "h_front_max_m": h_front_max_m,
        "edge_up_detected": float(step_up_height_m > EDGE_DISTANCE_THRESHOLD_M),
        "edge_down_detected": float(drop_depth_m > EDGE_DISTANCE_THRESHOLD_M),
        "gap_any_detected": float(gap_width_norm > 0.0),
        "g_step_up": g_step_up,
        "g_step_down": g_step_down,
        "g_gap": g_gap,
        "g_rough": g_rough,
    }


def _sample_group_features() -> list[dict[str, float | str | int]]:
    terrain_builder = _load_terrain_builder()
    cfg = terrain_builder.Stage1TerrainCfg()
    x_points = _axis_points(
        -(PATCH_REAR_EXTENT + PATCH_REAR_MARGIN),
        PATCH_FRONT_EXTENT + PATCH_PREVIEW_LENGTH,
        PATCH_RESOLUTION_X,
    )
    y_points = _axis_points(
        -(PATCH_HALF_WIDTH + PATCH_SIDE_MARGIN),
        PATCH_HALF_WIDTH + PATCH_SIDE_MARGIN,
        PATCH_RESOLUTION_Y,
    )
    grid_x, grid_y = np.meshgrid(x_points, y_points, indexing="ij")

    x_center_min = -float(np.min(x_points)) + 0.05
    x_center_max = cfg.terrain_length - float(np.max(x_points)) - 0.05
    x_centers = np.linspace(x_center_min, x_center_max, 28)
    y_center = cfg.terrain_width / 2.0

    records: list[dict[str, float | str | int]] = []
    for group_name, terrain_names in TERRAIN_GROUPS.items():
        for terrain_name in terrain_names:
            seed_count = 1 if terrain_name in {"flat", "stairs up", "stairs down"} else 16
            for row in range(cfg.num_rows):
                difficulty = row / cfg.num_rows
                for seed_idx in range(seed_count):
                    seed = 10_000 * (row + 1) + 97 * seed_idx + len(terrain_name)
                    tile_raw = terrain_builder.make_tile_by_name(cfg, terrain_name, difficulty, 0.0, seed)
                    tile_m = tile_raw.astype(np.float64) * cfg.vertical_scale
                    for x_center in x_centers:
                        sample_x_m = x_center + grid_x
                        sample_y_m = y_center + grid_y
                        patch_m = _bilinear_sample(tile_m, cfg, sample_x_m, sample_y_m)
                        features = _compute_patch_features(patch_m, x_points, y_points)
                        records.append(
                            {
                                "terrain_group": group_name,
                                "terrain_name": terrain_name,
                                "row": row,
                                "difficulty": difficulty,
                                "seed_idx": seed_idx,
                                "patch_center_x_m": float(x_center),
                                **features,
                            }
                        )
    return records


def _write_records(records: list[dict[str, float | str | int]]) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys())
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    summary_fields = [
        "step_up_height_m",
        "drop_depth_m",
        "front_roughness_m",
        "gap_width_norm",
        "front_slope",
        "edge_up_detected",
        "edge_down_detected",
        "gap_any_detected",
        "g_step_up",
        "g_step_down",
        "g_gap",
        "g_rough",
    ]
    with OUTPUT_SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["terrain_group", "feature", "count", "mean", "p50", "p75", "p90", "p95", "max"])
        for group_name in TERRAIN_GROUPS:
            group_records = [record for record in records if record["terrain_group"] == group_name]
            for feature in summary_fields:
                values = np.asarray([float(record[feature]) for record in group_records], dtype=np.float64)
                writer.writerow(
                    [
                        group_name,
                        feature,
                        values.size,
                        np.mean(values),
                        np.percentile(values, 50),
                        np.percentile(values, 75),
                        np.percentile(values, 90),
                        np.percentile(values, 95),
                        np.max(values),
                    ]
                )


def _boxplot(ax, records: list[dict[str, float | str | int]], feature: str, title: str, ylabel: str) -> None:
    labels = list(TERRAIN_GROUPS.keys())
    data = [
        np.asarray([float(record[feature]) for record in records if record["terrain_group"] == label], dtype=np.float64)
        for label in labels
    ]
    box = ax.boxplot(data, tick_labels=labels, patch_artist=True, showfliers=False)
    colors = ["#f8fafc", "#8ce99a", "#ffd43b", "#91c9ff"]
    for patch, color in zip(box["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.72)
        patch.set_edgecolor("#111827")
        patch.set_linewidth(1.1)
    for median in box["medians"]:
        median.set_color("#b91c1c")
        median.set_linewidth(1.4)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=11)
    ax.tick_params(axis="x", labelrotation=12, labelsize=10)
    ax.tick_params(axis="y", labelsize=10)
    ax.grid(axis="y", color="#d4d4d4", linewidth=0.6, alpha=0.75)


def _plot_records(records: list[dict[str, float | str | int]]) -> None:
    fig, axes = plt.subplots(3, 3, figsize=(15.5, 12.0), dpi=180)
    axes = axes.reshape(-1)

    plot_specs = [
        ("step_up_height_m", "max upward jump", "m"),
        ("drop_depth_m", "max downward jump", "m"),
        ("front_roughness_m", "front roughness", "m"),
        ("gap_width_norm", "gap-width ratio", "ratio"),
        ("front_slope", "front slope", "height / distance"),
        ("h_front_min_m", "front minimum relative height", "m"),
        ("g_step_up", "soft gate: step up", "[0, 1]"),
        ("g_step_down", "soft gate: step down", "[0, 1]"),
        ("g_gap", "soft gate: gap", "[0, 1]"),
    ]
    for ax, (feature, title, ylabel) in zip(axes, plot_specs):
        _boxplot(ax, records, feature, title, ylabel)
        if feature in {"step_up_height_m", "drop_depth_m"}:
            ax.axhline(EDGE_DISTANCE_THRESHOLD_M, color="#f97316", linestyle="--", linewidth=1.2, label="edge dist threshold 0.02 m")
            ax.axhline(STEP_GATE_THRESHOLD_M, color="#dc2626", linestyle="--", linewidth=1.2, label="gate threshold 0.08 m")
            ax.legend(loc="upper left", fontsize=8, frameon=False)
        if feature == "h_front_min_m":
            ax.axhline(-GAP_DEPTH_THRESHOLD_M, color="#2563eb", linestyle="--", linewidth=1.2, label="gap depth threshold -0.06 m")
            ax.legend(loc="lower left", fontsize=8, frameon=False)
        if feature == "front_roughness_m":
            ax.axhline(ROUGH_GATE_THRESHOLD_M, color="#16a34a", linestyle="--", linewidth=1.2, label="rough gate threshold 0.03 m")
            ax.legend(loc="upper left", fontsize=8, frameon=False)

    fig.suptitle(
        "Stage1 generated-terrain feature distributions\n"
        "groups: flat / uneven rough / stairs up+down / discrete obstacles",
        fontsize=18,
        fontweight="bold",
        y=0.985,
    )
    fig.text(
        0.5,
        0.012,
        "Each sample is a local 34 x 17 patch swept along x within generated 8 m terrain tiles across all 20 rows.",
        ha="center",
        fontsize=10,
    )
    fig.tight_layout(rect=(0.02, 0.035, 1.0, 0.955))
    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PNG, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    records = _sample_group_features()
    _write_records(records)
    _plot_records(records)
    print(OUTPUT_PNG)
    print(OUTPUT_CSV)
    print(OUTPUT_SUMMARY_CSV)


if __name__ == "__main__":
    main()
