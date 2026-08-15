"""Draw the Stage1 local height-patch layout as a 2-D engineering diagram."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.patches import Patch

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
    }
)

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "results" / "stage1_patch_layout.png"


VEHICLE_TOTAL_LENGTH = 1.884419
VEHICLE_TOTAL_WIDTH = 0.560747
FRONT_BODY_LENGTH = 0.665721
MIDDLE_BODY_LENGTH = 0.35
REAR_BODY_LENGTH = 0.665721
FRONT_OVERHANG = 0.389232
REAR_OVERHANG = 0.389232
FRONT_TRACK_WIDTH = 0.539059
MIDDLE_TRACK_WIDTH = 0.53822
REAR_TRACK_WIDTH = 0.539059
FRONT_TO_MIDDLE_WHEELBASE = 0.552977
MIDDLE_TO_REAR_WHEELBASE = 0.552977

PATCH_FRONT_EXTENT = 0.942209
PATCH_REAR_EXTENT = 0.942209
PATCH_HALF_WIDTH = VEHICLE_TOTAL_WIDTH / 2.0
PATCH_PREVIEW_LENGTH = 1.0
PATCH_REAR_MARGIN = 0.40
PATCH_SIDE_MARGIN = 0.50
PATCH_RESOLUTION_X = 0.10
PATCH_RESOLUTION_Y = 0.10

WHEEL_RADIUS = 0.19
WHEEL_DIAMETER = 2.0 * WHEEL_RADIUS
FRONT_WHEEL_CENTER_Y = FRONT_TRACK_WIDTH / 2.0
MIDDLE_WHEEL_CENTER_Y = MIDDLE_TRACK_WIDTH / 2.0
REAR_WHEEL_CENTER_Y = REAR_TRACK_WIDTH / 2.0
# STL bbox width minus wheel-center track leaves a very thin top-view tire thickness.
# Keep a minimum drawn width so the wheel footprint remains readable.
FRONT_WHEEL_WIDTH = max(VEHICLE_TOTAL_WIDTH - FRONT_TRACK_WIDTH, 0.035)
MIDDLE_WHEEL_WIDTH = max(VEHICLE_TOTAL_WIDTH - MIDDLE_TRACK_WIDTH, 0.035)
REAR_WHEEL_WIDTH = max(VEHICLE_TOTAL_WIDTH - REAR_TRACK_WIDTH, 0.035)
FRONT_AXLE_X = FRONT_TO_MIDDLE_WHEELBASE
MIDDLE_AXLE_X = 0.0
REAR_AXLE_X = -MIDDLE_TO_REAR_WHEELBASE

SUPPORT_HALF_WIDTH = PATCH_HALF_WIDTH + 0.05
LEFT_TRACK_Y_MIN = 0.15
LEFT_TRACK_Y_MAX = 0.45
RIGHT_TRACK_Y_MIN = -0.45
RIGHT_TRACK_Y_MAX = -0.15
CENTER_TRACK_HALF_WIDTH = 0.20

COLORS = {
    "sampling": "#a3a3a3",
    "patch_edge": "#111111",
    "center_ref_face": "#ffb3b3",
    "center_ref_edge": "#e31a1c",
    "front_preview_face": "#d8b4fe",
    "front_preview_edge": "#5b21b6",
    "center_track_face": "#ffd43b",
    "center_track_edge": "#f08c00",
    "left_track_face": "#8ce99a",
    "left_track_edge": "#2b8a3e",
    "right_track_face": "#91c9ff",
    "right_track_edge": "#1c7ed6",
    "support_y_edge": "#003cff",
    "rear_support_face": "#5eead4",
    "rear_support_edge": "#0f766e",
    "middle_support_face": "#ffa94d",
    "middle_support_edge": "#d9480f",
    "front_support_face": "#69db7c",
    "front_support_edge": "#2f9e44",
    "body_face": "#f8fafc",
    "body_edge": "#111827",
    "wheel_face": "#e5e7eb",
    "wheel_edge": "#111827",
    "axis_x": "#111827",
    "axis_y": "#111827",
}


def _axis_points(min_value: float, max_value: float, target_resolution: float) -> list[float]:
    num_points = int(round((max_value - min_value) / target_resolution)) + 1
    if num_points < 2:
        return [round(min_value, 6)]
    step = (max_value - min_value) / (num_points - 1)
    return [round(min_value + i * step, 6) for i in range(num_points)]


def _to_plot(local_x: float, local_y: float) -> tuple[float, float]:
    """Map local car coordinates to plot coordinates.

    Plot vertical axis is local +X. Plot left direction is local +Y.
    """

    return -local_y, local_x


def _local_rect(
    ax,
    *,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    facecolor: str,
    edgecolor: str,
    alpha: float,
    linewidth: float = 1.4,
    linestyle: str = "-",
    zorder: int = 2,
    label: str | None = None,
    label_color: str = "#1f2937",
    label_size: int = 8,
) -> Rectangle:
    left = -y_max
    bottom = x_min
    width = y_max - y_min
    height = x_max - x_min
    rect = Rectangle(
        (left, bottom),
        width,
        height,
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        linestyle=linestyle,
        alpha=alpha,
        zorder=zorder,
    )
    ax.add_patch(rect)
    if label:
        ax.text(
            left + width / 2.0,
            bottom + height / 2.0,
            label,
            ha="center",
            va="center",
            fontsize=label_size,
            color=label_color,
            zorder=zorder + 1,
            bbox={
                "boxstyle": "round,pad=0.18",
                "facecolor": "white",
                "edgecolor": "none",
                "alpha": 0.78,
            },
        )
    return rect


def _text_local(
    ax,
    *,
    local_x: float,
    local_y: float,
    text: str,
    color: str = "#1f2937",
    size: int = 8,
    zorder: int = 20,
    ha: str = "center",
    va: str = "center",
) -> None:
    px, py = _to_plot(local_x, local_y)
    ax.text(
        px,
        py,
        text,
        ha=ha,
        va=va,
            fontsize=size,
            fontweight="bold",
            color=color,
            zorder=zorder,
        bbox={
            "boxstyle": "round,pad=0.18",
            "facecolor": "white",
            "edgecolor": "none",
            "alpha": 0.80,
        },
    )


def _draw_wheel(ax, *, center_x: float, center_y: float, width_y: float, label: str) -> None:
    _local_rect(
        ax,
        x_min=center_x - WHEEL_DIAMETER / 2.0,
        x_max=center_x + WHEEL_DIAMETER / 2.0,
        y_min=center_y - width_y / 2.0,
        y_max=center_y + width_y / 2.0,
        facecolor=COLORS["wheel_face"],
        edgecolor=COLORS["wheel_edge"],
        alpha=0.94,
        linewidth=1.4,
        zorder=8,
    )
    px, py = _to_plot(center_x, center_y)
    ax.plot(px, py, marker="o", markersize=2.8, color="#111827", zorder=10)
    ax.text(px, py + 0.075, label, ha="center", va="center", fontsize=8, color="#111827", zorder=10)


def _draw_body(ax) -> None:
    body_style = {
        "facecolor": COLORS["body_face"],
        "edgecolor": COLORS["body_edge"],
        "alpha": 0.54,
        "linewidth": 1.4,
        "zorder": 6,
    }
    half_width = VEHICLE_TOTAL_WIDTH / 2.0
    front_x_max = PATCH_FRONT_EXTENT
    front_x_min = front_x_max - FRONT_BODY_LENGTH
    middle_x_min = -MIDDLE_BODY_LENGTH / 2.0
    middle_x_max = MIDDLE_BODY_LENGTH / 2.0
    rear_x_min = -PATCH_REAR_EXTENT
    rear_x_max = rear_x_min + REAR_BODY_LENGTH
    _local_rect(
        ax,
        x_min=-PATCH_REAR_EXTENT,
        x_max=PATCH_FRONT_EXTENT,
        y_min=-half_width,
        y_max=half_width,
        facecolor="#ffffff",
        edgecolor="#111827",
        alpha=0.0,
        linewidth=1.2,
        linestyle=":",
        zorder=7,
    )
    _local_rect(ax, x_min=front_x_min, x_max=front_x_max, y_min=-half_width, y_max=half_width, **body_style, label="front body")
    _local_rect(ax, x_min=middle_x_min, x_max=middle_x_max, y_min=-half_width, y_max=half_width, **body_style, label="middle body")
    _local_rect(ax, x_min=rear_x_min, x_max=rear_x_max, y_min=-half_width, y_max=half_width, **body_style, label="rear body")
    ax.plot([0.0, 0.0], [middle_x_max, front_x_min], color=COLORS["body_edge"], linewidth=1.8, alpha=0.6, zorder=6)
    ax.plot([0.0, 0.0], [rear_x_max, middle_x_min], color=COLORS["body_edge"], linewidth=1.8, alpha=0.6, zorder=6)


def _draw_axes_arrows(ax) -> None:
    x0, y0 = _to_plot(1.48, 0.62)
    x1, y1 = _to_plot(1.78, 0.62)
    ax.annotate(
        "",
        xy=(x1, y1),
        xytext=(x0, y0),
        arrowprops={"arrowstyle": "-|>", "linewidth": 2.0, "color": COLORS["axis_x"]},
        zorder=12,
    )
    ax.text(x1, y1 + 0.04, "+X\nforward", ha="center", va="bottom", fontsize=9, weight="bold", zorder=12)

    x0, y0 = _to_plot(1.48, 0.38)
    x1, y1 = _to_plot(1.48, 0.70)
    ax.annotate(
        "",
        xy=(x1, y1),
        xytext=(x0, y0),
        arrowprops={"arrowstyle": "-|>", "linewidth": 2.0, "color": COLORS["axis_y"]},
        zorder=12,
    )
    ax.text(x1 - 0.02, y1, "+Y\nleft", ha="right", va="center", fontsize=9, weight="bold", color=COLORS["axis_y"], zorder=12)


def _draw_legend(legend_ax) -> None:
    legend_ax.axis("off")
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=COLORS["sampling"],
            markeredgecolor=COLORS["sampling"],
            markersize=5,
            label="sampling grid (0.10 m)",
        ),
        Patch(
            facecolor=COLORS["center_ref_face"],
            edgecolor=COLORS["center_ref_edge"],
            alpha=0.58,
            label="center reference / D_ref",
        ),
        Patch(
            facecolor=COLORS["front_preview_face"],
            edgecolor=COLORS["front_preview_edge"],
            alpha=0.52,
            label="front preview (x > 0.942209)",
        ),
        Patch(
            facecolor=COLORS["center_track_face"],
            edgecolor=COLORS["center_track_edge"],
            alpha=0.70,
            label="center track (|y| <= 0.20)",
        ),
        Patch(
            facecolor=COLORS["left_track_face"],
            edgecolor=COLORS["left_track_edge"],
            alpha=0.62,
            label="left track (+Y)",
        ),
        Patch(
            facecolor=COLORS["right_track_face"],
            edgecolor=COLORS["right_track_edge"],
            alpha=0.62,
            label="right track (-Y)",
        ),
        Patch(
            facecolor="none",
            edgecolor=COLORS["support_y_edge"],
            linestyle="--",
            linewidth=1.6,
            label="support_y (-0.330374 <= y <= 0.330374)",
        ),
        Patch(
            facecolor=COLORS["rear_support_face"],
            edgecolor=COLORS["rear_support_edge"],
            alpha=0.58,
            label="rear support (x in [-0.942209, -0.30])",
        ),
        Patch(
            facecolor=COLORS["middle_support_face"],
            edgecolor=COLORS["middle_support_edge"],
            alpha=0.58,
            label="middle support (x in [-0.30, 0.30])",
        ),
        Patch(
            facecolor=COLORS["front_support_face"],
            edgecolor=COLORS["front_support_edge"],
            alpha=0.58,
            label="front support (x in [0.30, 0.942209])",
        ),
        Patch(
            facecolor=COLORS["body_face"],
            edgecolor=COLORS["body_edge"],
            alpha=0.65,
            label="vehicle body / bbox width = 0.560747 m",
        ),
        Patch(
            facecolor=COLORS["wheel_face"],
            edgecolor=COLORS["wheel_edge"],
            alpha=0.94,
            label="wheel footprint, radius = 0.19 m",
        ),
        Line2D(
            [0],
            [0],
            color="#14532d",
            linestyle="-.",
            linewidth=1.1,
            label="wheel-center line, |y| ≈ 0.2695 m",
        ),
    ]
    legend = legend_ax.legend(
        handles=handles,
        loc="center",
        ncol=3,
        frameon=True,
        fancybox=False,
        edgecolor="#111827",
        framealpha=1.0,
        fontsize=10,
        handlelength=2.4,
        columnspacing=1.8,
        handletextpad=0.8,
        borderpad=0.85,
    )
    legend.get_frame().set_linewidth(0.8)


def main() -> None:
    x_min = -(PATCH_REAR_EXTENT + PATCH_REAR_MARGIN)
    x_max = PATCH_FRONT_EXTENT + PATCH_PREVIEW_LENGTH
    y_min = -(PATCH_HALF_WIDTH + PATCH_SIDE_MARGIN)
    y_max = PATCH_HALF_WIDTH + PATCH_SIDE_MARGIN

    x_points = _axis_points(x_min, x_max, PATCH_RESOLUTION_X)
    y_points = _axis_points(y_min, y_max, PATCH_RESOLUTION_Y)

    fig = plt.figure(figsize=(10.5, 15.0), dpi=220)
    grid = fig.add_gridspec(nrows=2, ncols=1, height_ratios=[12.6, 2.1], hspace=0.06)
    ax = fig.add_subplot(grid[0])
    legend_ax = fig.add_subplot(grid[1])
    ax.set_facecolor("#ffffff")

    # Draw the full sampled patch first.
    grid_plot_x = []
    grid_plot_y = []
    for lx in x_points:
        for ly in y_points:
            px, py = _to_plot(lx, ly)
            grid_plot_x.append(px)
            grid_plot_y.append(py)
    ax.scatter(
        grid_plot_x,
        grid_plot_y,
        s=10,
        color=COLORS["sampling"],
        edgecolors=COLORS["sampling"],
        linewidths=0.0,
        alpha=0.76,
        zorder=1,
    )
    _local_rect(
        ax,
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        facecolor="none",
        edgecolor=COLORS["patch_edge"],
        alpha=1.0,
        linewidth=1.6,
        zorder=3,
    )
    ax.text(
        0.0,
        x_max + 0.06,
        f"local height-map patch ({len(x_points)} x {len(y_points)} = {len(x_points) * len(y_points)} samples)",
        ha="center",
        va="bottom",
        fontsize=12,
        color="#1d4ed8",
        weight="bold",
        zorder=20,
    )

    # Feature masks. Y masks must be vertical strips in this view.
    _local_rect(
        ax,
        x_min=x_min,
        x_max=x_max,
        y_min=-CENTER_TRACK_HALF_WIDTH,
        y_max=CENTER_TRACK_HALF_WIDTH,
        facecolor=COLORS["center_track_face"],
        edgecolor=COLORS["center_track_edge"],
        alpha=0.56,
        linewidth=2.0,
        zorder=4,
    )
    _local_rect(
        ax,
        x_min=x_min,
        x_max=x_max,
        y_min=LEFT_TRACK_Y_MIN,
        y_max=LEFT_TRACK_Y_MAX,
        facecolor=COLORS["left_track_face"],
        edgecolor=COLORS["left_track_edge"],
        alpha=0.42,
        linewidth=1.4,
        zorder=3,
    )
    _local_rect(
        ax,
        x_min=x_min,
        x_max=x_max,
        y_min=RIGHT_TRACK_Y_MIN,
        y_max=RIGHT_TRACK_Y_MAX,
        facecolor=COLORS["right_track_face"],
        edgecolor=COLORS["right_track_edge"],
        alpha=0.42,
        linewidth=1.4,
        zorder=3,
    )
    for track_y in (-CENTER_TRACK_HALF_WIDTH, CENTER_TRACK_HALF_WIDTH):
        px, _ = _to_plot(0.0, track_y)
        ax.axvline(px, color=COLORS["center_track_edge"], linewidth=2.1, linestyle="-", alpha=0.95, zorder=9)
    _text_local(ax, local_x=1.10, local_y=0.30, text="left track (+Y)", color="#166534", size=10)
    _text_local(ax, local_x=1.10, local_y=0.00, text="center track\n|y| <= 0.20", color="#8a4b00", size=11)
    _text_local(ax, local_x=1.10, local_y=-0.30, text="right track (-Y)", color="#1e40af", size=10)

    # Support envelope and support regions.
    for support_y in (-SUPPORT_HALF_WIDTH, SUPPORT_HALF_WIDTH):
        px, _ = _to_plot(0.0, support_y)
        ax.axvline(px, color=COLORS["support_y_edge"], linewidth=1.8, linestyle="--", zorder=8)
    ax.text(
        0.0,
        x_min + 0.10,
        "support_y",
        ha="center",
        va="bottom",
        fontsize=10,
        color=COLORS["support_y_edge"],
        zorder=5,
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "none", "alpha": 0.78},
    )
    _local_rect(
        ax,
        x_min=-PATCH_REAR_EXTENT,
        x_max=-0.30,
        y_min=-SUPPORT_HALF_WIDTH,
        y_max=SUPPORT_HALF_WIDTH,
        facecolor=COLORS["rear_support_face"],
        edgecolor=COLORS["rear_support_edge"],
        alpha=0.42,
        linewidth=1.2,
        zorder=5,
    )
    _local_rect(
        ax,
        x_min=-0.30,
        x_max=0.30,
        y_min=-SUPPORT_HALF_WIDTH,
        y_max=SUPPORT_HALF_WIDTH,
        facecolor=COLORS["middle_support_face"],
        edgecolor=COLORS["middle_support_edge"],
        alpha=0.42,
        linewidth=1.2,
        zorder=5,
    )
    _local_rect(
        ax,
        x_min=0.30,
        x_max=PATCH_FRONT_EXTENT,
        y_min=-SUPPORT_HALF_WIDTH,
        y_max=SUPPORT_HALF_WIDTH,
        facecolor=COLORS["front_support_face"],
        edgecolor=COLORS["front_support_edge"],
        alpha=0.42,
        linewidth=1.2,
        zorder=5,
    )
    _text_local(ax, local_x=0.62, local_y=-0.64, text="front\nsupport", color="#166534", size=10)
    _text_local(ax, local_x=0.00, local_y=-0.64, text="middle\nsupport", color="#9a3412", size=10)
    _text_local(ax, local_x=-0.62, local_y=-0.64, text="rear\nsupport", color="#0f766e", size=10)
    _local_rect(
        ax,
        x_min=-0.30,
        x_max=0.30,
        y_min=-0.20,
        y_max=0.20,
        facecolor=COLORS["center_ref_face"],
        edgecolor=COLORS["center_ref_edge"],
        alpha=0.70,
        linewidth=1.8,
        zorder=7,
        label="center reference / D_ref",
        label_color="#b91c1c",
        label_size=11,
    )
    _local_rect(
        ax,
        x_min=PATCH_FRONT_EXTENT,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        facecolor=COLORS["front_preview_face"],
        edgecolor=COLORS["front_preview_edge"],
        alpha=0.30,
        linewidth=1.4,
        zorder=2,
        label="front_preview\nx > +0.942",
        label_color=COLORS["front_preview_edge"],
        label_size=10,
    )

    _draw_body(ax)
    wheels = [
        (FRONT_AXLE_X, FRONT_WHEEL_CENTER_Y, FRONT_WHEEL_WIDTH, "FL"),
        (FRONT_AXLE_X, -FRONT_WHEEL_CENTER_Y, FRONT_WHEEL_WIDTH, "FR"),
        (MIDDLE_AXLE_X, MIDDLE_WHEEL_CENTER_Y, MIDDLE_WHEEL_WIDTH, "ML"),
        (MIDDLE_AXLE_X, -MIDDLE_WHEEL_CENTER_Y, MIDDLE_WHEEL_WIDTH, "MR"),
        (REAR_AXLE_X, REAR_WHEEL_CENTER_Y, REAR_WHEEL_WIDTH, "RL"),
        (REAR_AXLE_X, -REAR_WHEEL_CENTER_Y, REAR_WHEEL_WIDTH, "RR"),
    ]
    for wx, wy, width_y, label in wheels:
        _draw_wheel(ax, center_x=wx, center_y=wy, width_y=width_y, label=label)

    for y_value, label, color in [
        (FRONT_WHEEL_CENTER_Y, "front/rear wheel center y = +0.2695", "#14532d"),
        (-FRONT_WHEEL_CENTER_Y, "front/rear wheel center y = -0.2695", "#1e3a8a"),
    ]:
        px, _ = _to_plot(0.0, y_value)
        ax.axvline(px, color=color, linewidth=0.95, linestyle="-.", alpha=0.85, zorder=8)

    _draw_axes_arrows(ax)

    # Mark key x boundaries as horizontal lines.
    for value, label in [
        (PATCH_FRONT_EXTENT, "x = +0.942 front extent"),
        (0.30, "x = +0.30"),
        (0.0, "x = 0 center"),
        (-0.30, "x = -0.30"),
        (-PATCH_REAR_EXTENT, "x = -0.942 rear extent"),
    ]:
        ax.axhline(value, color="#111827", linewidth=0.75, linestyle="--", alpha=0.55, zorder=5)
        ax.text(
            -y_min + 0.03,
            value,
            label,
            ha="left",
            va="center",
            fontsize=9,
            color="#111827",
            zorder=10,
            bbox={"boxstyle": "round,pad=0.12", "facecolor": "white", "edgecolor": "none", "alpha": 0.70},
        )

    y_ticks_local = [
        y_max,
        LEFT_TRACK_Y_MAX,
        SUPPORT_HALF_WIDTH,
        CENTER_TRACK_HALF_WIDTH,
        0.0,
        -CENTER_TRACK_HALF_WIDTH,
        -SUPPORT_HALF_WIDTH,
        RIGHT_TRACK_Y_MIN,
        y_min,
    ]
    ax.set_xticks([-value for value in y_ticks_local])
    ax.set_xticklabels([f"{value:+.3f}" for value in y_ticks_local], rotation=35, ha="right")
    ax.set_yticks([x_min, -PATCH_REAR_EXTENT, -0.30, 0.0, 0.30, PATCH_FRONT_EXTENT, x_max])
    ax.set_yticklabels([f"{value:+.3f}" for value in [x_min, -PATCH_REAR_EXTENT, -0.30, 0.0, 0.30, PATCH_FRONT_EXTENT, x_max]])

    ax.set_xlim(-y_max - 0.18, -y_min + 0.44)
    ax.set_ylim(x_min - 0.16, x_max + 0.16)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(False)
    ax.tick_params(axis="both", labelsize=11)
    ax.set_xlabel("local y (m), positive values are on the left side of the vehicle", fontsize=13, weight="bold")
    ax.set_ylabel("local x (m), positive values point forward", fontsize=13, weight="bold")
    ax.set_title(
        "Stage1 local patch sampling region and feature masks",
        fontsize=18,
        weight="bold",
        pad=14,
    )
    _draw_legend(legend_ax)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.94, bottom=0.04, hspace=0.08)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
