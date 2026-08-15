"""Plot Stage1 terrain gate transfer functions.

The curves match the deterministic formulas in
``complete_car_lab/tasks/direct/complete_car/mdp/terrain_features.py``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUT_PATH = Path("results/stage1_terrain_gate_functions.png")

PATCH_FRONT_EXTENT_M = 0.942209
PATCH_REAR_EXTENT_M = 0.942209
PATCH_PREVIEW_LENGTH_M = 1.0
PATCH_REAR_MARGIN_M = 0.40
PATCH_RESOLUTION_X_M = 0.10


def build_axis_points(min_value: float, max_value: float, target_resolution: float) -> np.ndarray:
    num_points = int(round((max_value - min_value) / target_resolution)) + 1
    if num_points < 2:
        return np.asarray([round(min_value, 6)], dtype=np.float64)
    step = (max_value - min_value) / (num_points - 1)
    return np.asarray([round(min_value + i * step, 6) for i in range(num_points)], dtype=np.float64)


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-x))


def main() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 9,
            "figure.dpi": 160,
            "savefig.dpi": 240,
        }
    )

    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.5), constrained_layout=True)

    # g_step_up is intentionally more sensitive than g_step_down.
    jump_m = np.linspace(0.0, 0.20, 600)
    g_step_up = sigmoid((jump_m - 0.05) / 0.02)
    g_step_down = sigmoid((jump_m - 0.08) / 0.02)
    ax = axes[0, 0]
    ax.plot(jump_m, g_step_up, color="#d1495b", lw=2.4, label="g_step_up")
    ax.plot(jump_m, g_step_down, color="#457b9d", lw=2.2, label="g_step_down")
    ax.axvline(0.05, color="#d1495b", lw=1.4, ls="--", label="step-up 0.05 m")
    ax.axvline(0.08, color="#457b9d", lw=1.4, ls="--", label="step-down 0.08 m")
    ax.axhline(0.5, color="#777777", lw=1.0, ls=":")
    ax.set_title("Step gates: height jump/drop -> gate")
    ax.set_xlabel("max height jump or drop (m)")
    ax.set_ylabel("gate value")
    ax.set_xlim(0, 0.20)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower right")

    # g_gap = g_step_down * sigmoid((gap_width_norm - 0.15) / 0.05).
    x_points = build_axis_points(
        -(PATCH_REAR_EXTENT_M + PATCH_REAR_MARGIN_M),
        PATCH_FRONT_EXTENT_M + PATCH_PREVIEW_LENGTH_M,
        PATCH_RESOLUTION_X_M,
    )
    front_x = x_points[x_points >= 0.0]
    front_x_span_m = float(front_x[-1] - front_x[0])
    gap_width_m = np.linspace(0.0, front_x_span_m, 600)
    gap_width_norm = gap_width_m / front_x_span_m
    width_gate = sigmoid((gap_width_norm - 0.15) / 0.05)
    width_threshold_m = 0.15 * front_x_span_m
    ax = axes[0, 1]
    for drop_m, color in [(0.04, "#8ecae6"), (0.08, "#219ebc"), (0.12, "#fb8500"), (0.16, "#d1495b")]:
        g_step_down = sigmoid((drop_m - 0.08) / 0.02)
        g_gap = g_step_down * width_gate
        ax.plot(gap_width_m, g_gap, lw=2.1, color=color, label=f"drop={drop_m:.2f} m")
    ax.axvline(
        width_threshold_m,
        color="#333333",
        lw=1.4,
        ls="--",
        label=f"width={width_threshold_m:.2f} m (norm=0.15)",
    )
    ax.axhline(0.5, color="#777777", lw=1.0, ls=":")
    ax.set_title("Gap gate: low-area width with different drops")
    ax.set_xlabel("equivalent low-area width (m)")
    ax.set_ylabel("g_gap")
    ax.set_xlim(0, front_x_span_m)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower right", ncols=2)

    # g_rough transfer function.
    rough_m = np.linspace(0.0, 0.10, 600)
    g_rough = sigmoid((rough_m - 0.03) / 0.01)
    ax = axes[1, 0]
    ax.plot(rough_m, g_rough, color="#2a9d8f", lw=2.4, label="g_rough")
    ax.axvline(0.03, color="#333333", lw=1.4, ls="--", label="0.03 m threshold")
    ax.axhline(0.5, color="#777777", lw=1.0, ls=":")
    ax.set_title("Rough gate: front roughness -> gate")
    ax.set_xlabel("front roughness std (m)")
    ax.set_ylabel("gate value")
    ax.set_xlim(0, 0.10)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower right")

    # g_flat is the remaining mass after complex terrain gates.
    gate_sum = np.linspace(0.0, 2.0, 600)
    g_flat = 1.0 - np.clip(gate_sum, 0.0, 1.0)
    ax = axes[1, 1]
    ax.plot(gate_sum, g_flat, color="#457b9d", lw=2.4, label="g_flat = 1 - clamp(sum, 0, 1)")
    ax.axvline(1.0, color="#333333", lw=1.4, ls="--", label="sum=1")
    ax.set_title("Flat gate: remaining flatness")
    ax.set_xlabel("g_step_up + g_step_down + g_gap + g_rough")
    ax.set_ylabel("g_flat")
    ax.set_xlim(0, 2)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper right")

    fig.suptitle("Stage1 Terrain Gate Functions", fontsize=16, fontweight="bold")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, bbox_inches="tight")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
