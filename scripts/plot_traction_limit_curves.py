"""Plot Stage0 traction-aware wheel-limit curves."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import numpy as np


OUTPUT_DIR = Path("/home/ubuntu/Graduation-Project/results/traction_limit")
OUTPUT_PNG = OUTPUT_DIR / "traction_limit_curves_stage0.png"


def decreasing_scale(values: np.ndarray, start: float, full: float, min_scale: float) -> np.ndarray:
    ratio = (values - start) / max(full - start, 1.0e-6)
    ratio = np.clip(ratio, 0.0, 1.0)
    return 1.0 - ratio * (1.0 - min_scale)


def increasing_scale(values: np.ndarray, low: float, high: float, min_scale: float) -> np.ndarray:
    ratio = (values - low) / max(high - low, 1.0e-6)
    ratio = np.clip(ratio, 0.0, 1.0)
    return min_scale + ratio * (1.0 - min_scale)


def main() -> None:
    nominal_limit = 12.0
    min_scale = 0.35

    longitudinal_start = 0.6
    longitudinal_full = 1.5
    slip_angle_start_deg = 12.0
    slip_angle_full_deg = 28.0
    contact_force_low = 0.05
    contact_force_high = 0.12

    long_slip = np.linspace(0.0, 2.0, 400)
    slip_angle_deg = np.linspace(0.0, 45.0, 400)
    contact_force = np.linspace(0.0, 0.20, 400)

    long_scale = decreasing_scale(long_slip, longitudinal_start, longitudinal_full, min_scale)
    lat_scale = decreasing_scale(slip_angle_deg, slip_angle_start_deg, slip_angle_full_deg, min_scale)
    contact_scale = increasing_scale(contact_force, contact_force_low, contact_force_high, min_scale)

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("Stage0 Traction-Aware Wheel-Limit Curves", fontsize=16)

    ax = axes[0, 0]
    ax.plot(long_slip, long_scale, color="#d1495b", linewidth=2.5)
    ax.axvline(longitudinal_start, color="#888888", linestyle="--", linewidth=1.2)
    ax.axvline(longitudinal_full, color="#888888", linestyle="--", linewidth=1.2)
    ax.set_title("Longitudinal Slip -> Scale")
    ax.set_xlabel("|longitudinal slip|")
    ax.set_ylabel("scale")
    ax.set_ylim(0.3, 1.05)
    ax.grid(alpha=0.25)

    ax = axes[0, 1]
    ax.plot(slip_angle_deg, lat_scale, color="#00798c", linewidth=2.5)
    ax.axvline(slip_angle_start_deg, color="#888888", linestyle="--", linewidth=1.2)
    ax.axvline(slip_angle_full_deg, color="#888888", linestyle="--", linewidth=1.2)
    ax.set_title("Slip Angle -> Scale")
    ax.set_xlabel("|slip angle| [deg]")
    ax.set_ylabel("scale")
    ax.set_ylim(0.3, 1.05)
    ax.grid(alpha=0.25)

    ax = axes[1, 0]
    ax.plot(contact_force, contact_scale, color="#edae49", linewidth=2.5)
    ax.axvline(contact_force_low, color="#888888", linestyle="--", linewidth=1.2)
    ax.axvline(contact_force_high, color="#888888", linestyle="--", linewidth=1.2)
    ax.set_title("Normalized Contact Force -> Scale")
    ax.set_xlabel("normalized contact force")
    ax.set_ylabel("scale")
    ax.set_ylim(0.3, 1.05)
    ax.grid(alpha=0.25)

    combined_long = nominal_limit * long_scale
    combined_lat = nominal_limit * lat_scale
    combined_contact = nominal_limit * contact_scale

    ax = axes[1, 1]
    ax.plot(long_slip, combined_long, color="#d1495b", linewidth=2.0, label="from longitudinal slip")
    ax.plot(
        np.linspace(0.0, 45.0, 400),
        combined_lat,
        color="#00798c",
        linewidth=2.0,
        label="from slip angle",
    )
    ax.plot(
        np.linspace(0.0, 0.20, 400) * 225.0,
        combined_contact,
        color="#edae49",
        linewidth=2.0,
        label="from contact force",
    )
    ax.axhline(nominal_limit, color="#444444", linestyle="--", linewidth=1.2, label="nominal limit = 12 rad/s")
    ax.axhline(nominal_limit * min_scale, color="#444444", linestyle=":", linewidth=1.2, label="minimum limit = 4.2 rad/s")
    ax.set_title("Dynamic Wheel-Velocity Limit")
    ax.set_xlabel("channel input (rescaled per curve)")
    ax.set_ylabel("wheel velocity limit [rad/s]")
    ax.set_ylim(3.5, 12.5)
    ax.grid(alpha=0.25)
    ax.legend(loc="best", fontsize=9)

    note = (
        "Current Stage0 parameters:\n"
        f"min_scale={min_scale}, long_start/full={longitudinal_start}/{longitudinal_full}, "
        f"angle_start/full={slip_angle_start_deg}/{slip_angle_full_deg} deg, "
        f"contact_low/high={contact_force_low}/{contact_force_high}"
    )
    fig.text(0.5, 0.02, note, ha="center", va="bottom", fontsize=10)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=(0.03, 0.06, 0.98, 0.96))
    fig.savefig(OUTPUT_PNG, dpi=180)
    plt.close(fig)
    print(OUTPUT_PNG)


if __name__ == "__main__":
    main()
