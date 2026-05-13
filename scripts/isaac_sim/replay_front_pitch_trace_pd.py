#!/usr/bin/env python3
"""Replay one trace joint target on complete_car.usd with online PD drive.

This script is intentionally independent from the RL environment. It opens the
robot USD directly, reads a recorded q_desired trace column, generates a smooth
q_cmd/qdot_cmd reference, sends both position and velocity targets to the Isaac
Sim articulation, and records tracking metrics.
"""

from __future__ import annotations

import argparse
import csv
import ctypes
import ctypes.util
import importlib.util
import json
import math
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np


THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = next(parent for parent in THIS_FILE.parents if (parent / "AGENTS.md").exists())
DEFAULT_USD_PATH = PROJECT_ROOT / "USD" / "complete_car.usd"
DEFAULT_TRACE_PATH = (
    PROJECT_ROOT
    / "results"
    / "stage1_model725_allcols_30hz_fine_pd_2026-05-12"
    / "raw_traces"
    / "model725_allcols_30hz_col05_stairs_down.csv"
)
ISAAC_SIM_ROOT = Path(os.environ.get("ISAAC_SIM_ROOT", "/home/ubuntu/isaacsim"))
ISAAC_SIM_PYTHON = ISAAC_SIM_ROOT / "python.sh"
REEXEC_ENV_FLAG = "FRONT_PITCH_TRACE_PD_ISAACSIM_REEXEC"

ROBOT_ARTICULATION_ROOT_PATH = "/World/complete_car_alternative/body_car_chassis"
GROUND_PRIM_PATH = "/World/defaultGroundPlane"
GROUND_SIZE_M = 30.0
GROUND_THICKNESS_M = 0.05

BALL_JOINT_NAMES = [
    "spm1_platform_joint_z",
    "spm1_platform_joint_y",
    "spm1_platform_joint_x",
    "spm2_platform_joint_z",
    "spm2_platform_joint_y",
    "spm2_platform_joint_x",
]
WHEEL_JOINT_NAMES = [
    "body_car_wheel_left_joint",
    "body_car_wheel_right_joint",
    "head_car_wheel_left_joint",
    "head_car_wheel_right_joint",
    "tail_car_wheel_left_joint",
    "tail_car_wheel_right_joint",
]


def has_usable_x_display() -> bool:
    if not sys.platform.startswith("linux"):
        return True

    display_name = os.environ.get("DISPLAY")
    if not display_name:
        return False

    try:
        probe = subprocess.run(
            ["xset", "q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=2.0,
        )
        if probe.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    x11_library = ctypes.util.find_library("X11")
    if x11_library is None:
        return False

    x11 = ctypes.cdll.LoadLibrary(x11_library)
    x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x11.XOpenDisplay.restype = ctypes.c_void_p
    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    x11.XCloseDisplay.restype = ctypes.c_int

    handle = x11.XOpenDisplay(display_name.encode("utf-8"))
    if not handle:
        return False

    x11.XCloseDisplay(handle)
    return True


def maybe_reexec_via_isaacsim() -> None:
    if os.environ.get(REEXEC_ENV_FLAG) == "1":
        return
    if importlib.util.find_spec("isaacsim") is not None:
        return
    if not ISAAC_SIM_PYTHON.is_file():
        return

    env = os.environ.copy()
    env[REEXEC_ENV_FLAG] = "1"
    os.execvpe(str(ISAAC_SIM_PYTHON), [str(ISAAC_SIM_PYTHON), str(THIS_FILE), *sys.argv[1:]], env)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Open complete_car.usd directly and replay one q_desired trace column "
            "through a smooth q_cmd/qdot_cmd online PD target."
        )
    )
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE_PATH, help="Input trace CSV path.")
    parser.add_argument("--usd", type=Path, default=DEFAULT_USD_PATH, help="Robot USD path.")
    parser.add_argument("--env-id", type=int, default=5, help="Trace env_id to replay when the CSV has env_id.")
    parser.add_argument("--joint-name", type=str, default="spm1_platform_joint_y", choices=BALL_JOINT_NAMES)
    parser.add_argument(
        "--source-column",
        type=str,
        default="",
        help="Trace column to use. Default: q_desired_<joint-name>.",
    )
    parser.add_argument("--headless", action="store_true", help="Run without a visible Isaac Sim window.")
    parser.add_argument(
        "--require-gui",
        action="store_true",
        help="Fail instead of falling back to headless mode when no usable X display is available.",
    )
    parser.add_argument(
        "--no-gui-monitor",
        action="store_true",
        help="Disable the live omni.ui monitor window in GUI mode.",
    )
    parser.add_argument(
        "--realtime-factor",
        type=float,
        default=1.0,
        help="GUI playback speed. 1.0 means real-time, 0 or negative runs as fast as possible.",
    )
    parser.add_argument(
        "--hold-open",
        type=float,
        default=0.0,
        help="Keep the GUI window open for this many seconds after replay. 0 exits immediately.",
    )
    parser.add_argument(
        "--no-camera-setup",
        action="store_true",
        help="Do not move the viewport camera to the default replay inspection view.",
    )
    parser.add_argument(
        "--no-ground",
        action="store_true",
        help="Do not create the local ground collider.",
    )
    parser.add_argument("--frames", type=int, default=0, help="Maximum control rows to replay. 0 means all rows.")
    parser.add_argument("--skip-rows", type=int, default=0, help="Skip this many selected trace rows before replay.")
    parser.add_argument("--physics-dt", type=float, default=1.0 / 120.0)
    parser.add_argument("--control-dt", type=float, default=1.0 / 30.0)
    parser.add_argument("--render-dt", type=float, default=1.0 / 60.0)
    parser.add_argument("--settle-steps", type=int, default=120, help="Initial zero-command physics steps.")
    parser.add_argument("--kp", type=float, default=600.0)
    parser.add_argument("--kd", type=float, default=30.0)
    parser.add_argument("--effort-limit", type=float, default=60.0)
    parser.add_argument("--velocity-limit", type=float, default=2.0)
    parser.add_argument("--qddot-limit", type=float, default=8.0)
    parser.add_argument(
        "--tau-ref",
        type=float,
        default=0.05,
        help="First-order smoothing time constant for raw q_desired. <=0 disables smoothing.",
    )
    parser.add_argument("--wheel-kd", type=float, default=10.0)
    parser.add_argument("--wheel-effort-limit", type=float, default=80.0)
    parser.add_argument("--wheel-velocity-limit", type=float, default=20.0)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "results" / "front_pitch_trace_pd_usd")
    parser.add_argument("--save-plot", action="store_true", help="Also save a PNG plot if matplotlib is available.")
    parser.add_argument("--print-interval", type=int, default=100, help="Print progress every N control rows.")

    args = parser.parse_args()
    if args.physics_dt <= 0.0:
        parser.error("--physics-dt must be positive.")
    if args.control_dt <= 0.0:
        parser.error("--control-dt must be positive.")
    if args.render_dt <= 0.0:
        parser.error("--render-dt must be positive.")
    if args.kp < 0.0:
        parser.error("--kp must be non-negative.")
    if args.kd < 0.0:
        parser.error("--kd must be non-negative.")
    if args.effort_limit <= 0.0:
        parser.error("--effort-limit must be positive.")
    if args.velocity_limit <= 0.0:
        parser.error("--velocity-limit must be positive.")
    if args.qddot_limit <= 0.0:
        parser.error("--qddot-limit must be positive.")
    if args.settle_steps < 0:
        parser.error("--settle-steps must be non-negative.")
    if args.frames < 0:
        parser.error("--frames must be non-negative.")
    if args.skip_rows < 0:
        parser.error("--skip-rows must be non-negative.")
    if args.print_interval < 0:
        parser.error("--print-interval must be non-negative.")
    if args.hold_open < 0.0:
        parser.error("--hold-open must be non-negative.")
    if args.require_gui and args.headless:
        parser.error("--require-gui conflicts with --headless.")
    return args


@dataclass
class TraceSample:
    step: int
    time_s: float
    q_raw: float


@dataclass
class GovernorState:
    q_ref: float
    q_cmd: float
    qdot_cmd: float


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def finite_float(value: str, *, column: str, row_index: int) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid float in column {column!r}, row {row_index}: {value!r}") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"Non-finite float in column {column!r}, row {row_index}: {value!r}")
    return parsed


def load_trace_samples(trace_path: Path, env_id: int, source_column: str, skip_rows: int, frames: int) -> list[TraceSample]:
    if not trace_path.is_file():
        raise FileNotFoundError(f"Trace CSV not found: {trace_path}")

    samples: list[TraceSample] = []
    with trace_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Trace CSV has no header: {trace_path}")
        fieldnames = set(reader.fieldnames)
        if source_column not in fieldnames:
            matching = sorted(name for name in fieldnames if "q_desired" in name or "front_pitch" in name)
            raise ValueError(
                f"Column {source_column!r} not found in {trace_path}. "
                f"Candidate target columns: {matching[:20]}"
            )

        has_env_id = "env_id" in fieldnames
        has_step = "step" in fieldnames
        has_time = "time_s" in fieldnames
        for row_index, row in enumerate(reader):
            if has_env_id and int(float(row["env_id"])) != env_id:
                continue
            step = int(float(row["step"])) if has_step else len(samples)
            time_s = finite_float(row["time_s"], column="time_s", row_index=row_index) if has_time else float(step)
            q_raw = finite_float(row[source_column], column=source_column, row_index=row_index)
            samples.append(TraceSample(step=step, time_s=time_s, q_raw=q_raw))

    samples.sort(key=lambda item: (item.step, item.time_s))
    if skip_rows:
        samples = samples[skip_rows:]
    if frames:
        samples = samples[:frames]
    if not samples:
        raise ValueError(f"No trace samples selected from {trace_path} for env_id={env_id}.")
    return samples


def governor_step(
    state: GovernorState,
    q_raw: float,
    *,
    control_dt: float,
    tau_ref: float,
    qdot_limit: float,
    qddot_limit: float,
    lower_limit: float,
    upper_limit: float,
) -> GovernorState:
    if tau_ref <= 0.0:
        q_ref = q_raw
    else:
        alpha = 1.0 - math.exp(-control_dt / tau_ref)
        q_ref = state.q_ref + alpha * (q_raw - state.q_ref)

    qdot_raw = (q_ref - state.q_cmd) / control_dt
    qdot_limited = clamp(qdot_raw, -qdot_limit, qdot_limit)
    qdot_delta = clamp(
        qdot_limited - state.qdot_cmd,
        -qddot_limit * control_dt,
        qddot_limit * control_dt,
    )
    qdot_cmd = state.qdot_cmd + qdot_delta
    q_cmd_unclamped = state.q_cmd + qdot_cmd * control_dt
    q_cmd = clamp(q_cmd_unclamped, lower_limit, upper_limit)
    if q_cmd != q_cmd_unclamped:
        qdot_cmd = (q_cmd - state.q_cmd) / control_dt
    return GovernorState(q_ref=q_ref, q_cmd=q_cmd, qdot_cmd=qdot_cmd)


def full_joint_value_array(joint_indices: list[int], value: float) -> np.ndarray:
    return np.full((1, len(joint_indices)), value, dtype=np.float32)


def ensure_default_ground(stage) -> None:
    if stage.GetPrimAtPath(GROUND_PRIM_PATH).IsValid():
        print(f"[INFO] Ground already exists at {GROUND_PRIM_PATH}.")
        return

    from pxr import Gf
    from pxr import UsdGeom
    from pxr import UsdPhysics

    ground = UsdGeom.Cube.Define(stage, GROUND_PRIM_PATH)
    ground.CreateSizeAttr(1.0)
    ground.CreateDisplayColorAttr([Gf.Vec3f(0.32, 0.34, 0.36)])
    ground.AddTranslateOp().Set(Gf.Vec3d(0.0, 0.0, -0.5 * GROUND_THICKNESS_M))
    ground.AddScaleOp().Set(Gf.Vec3f(GROUND_SIZE_M, GROUND_SIZE_M, GROUND_THICKNESS_M))
    UsdPhysics.CollisionAPI.Apply(ground.GetPrim())
    print(
        f"[INFO] Created local ground collider at {GROUND_PRIM_PATH} "
        f"({GROUND_SIZE_M:g} m x {GROUND_SIZE_M:g} m, top z=0)."
    )


def configure_drive_parameters(robot, ball_indices: list[int], wheel_indices: list[int], args: argparse.Namespace) -> None:
    articulation_view = robot._articulation_view
    ball_np = np.asarray(ball_indices, dtype=np.int32)
    wheel_np = np.asarray(wheel_indices, dtype=np.int32)

    articulation_view.set_gains(
        kps=full_joint_value_array(ball_indices, args.kp),
        kds=full_joint_value_array(ball_indices, args.kd),
        joint_indices=ball_np,
    )
    articulation_view.set_gains(
        kps=full_joint_value_array(wheel_indices, 0.0),
        kds=full_joint_value_array(wheel_indices, args.wheel_kd),
        joint_indices=wheel_np,
    )
    articulation_view.set_max_efforts(
        values=full_joint_value_array(ball_indices, args.effort_limit),
        joint_indices=ball_np,
    )
    articulation_view.set_max_efforts(
        values=full_joint_value_array(wheel_indices, args.wheel_effort_limit),
        joint_indices=wheel_np,
    )
    articulation_view.set_max_joint_velocities(
        values=full_joint_value_array(ball_indices, args.velocity_limit),
        joint_indices=ball_np,
    )
    articulation_view.set_max_joint_velocities(
        values=full_joint_value_array(wheel_indices, args.wheel_velocity_limit),
        joint_indices=wheel_np,
    )


def compute_summary(records: list[dict[str, float]], args: argparse.Namespace) -> dict[str, object]:
    q_cmd_error = np.asarray([row["q_cmd_minus_actual"] for row in records], dtype=np.float64)
    q_desired_error = np.asarray([row["q_raw_minus_actual"] for row in records], dtype=np.float64)
    qdot_error = np.asarray([row["qdot_cmd_minus_actual"] for row in records], dtype=np.float64)
    qdot_cmd = np.asarray([row["qdot_cmd"] for row in records], dtype=np.float64)
    tau_est = np.asarray([row["tau_est_clamped"] for row in records], dtype=np.float64)

    def stats(values: np.ndarray) -> dict[str, float]:
        abs_values = np.abs(values)
        return {
            "mean_abs": float(np.mean(abs_values)),
            "rmse": float(math.sqrt(np.mean(np.square(values)))),
            "p50_abs": float(np.percentile(abs_values, 50)),
            "p95_abs": float(np.percentile(abs_values, 95)),
            "p99_abs": float(np.percentile(abs_values, 99)),
            "max_abs": float(np.max(abs_values)),
        }

    qdot_delta = np.diff(qdot_cmd) if qdot_cmd.size > 1 else np.asarray([0.0], dtype=np.float64)
    return {
        "rows": len(records),
        "joint_name": args.joint_name,
        "kp": args.kp,
        "kd": args.kd,
        "effort_limit": args.effort_limit,
        "velocity_limit": args.velocity_limit,
        "qddot_limit": args.qddot_limit,
        "tau_ref": args.tau_ref,
        "control_dt": args.control_dt,
        "physics_dt": args.physics_dt,
        "q_cmd_minus_actual": stats(q_cmd_error),
        "q_raw_minus_actual": stats(q_desired_error),
        "qdot_cmd_minus_actual": stats(qdot_error),
        "qdot_cmd_abs": stats(qdot_cmd),
        "qdot_cmd_delta_abs_mean": float(np.mean(np.abs(qdot_delta))),
        "qdot_cmd_delta_abs_p95": float(np.percentile(np.abs(qdot_delta), 95)),
        "estimated_tau_abs": stats(tau_est),
        "estimated_tau_saturation_rate_ge_0p98": float(
            np.mean(np.abs(tau_est) >= 0.98 * abs(args.effort_limit))
        ),
    }


def save_records_csv(path: Path, records: list[dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)


def save_plot(path: Path, records: list[dict[str, float]]) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"[WARN] matplotlib unavailable, skipping plot: {exc}")
        return

    t = np.asarray([row["trace_time_s"] for row in records], dtype=np.float64)
    q_raw = np.asarray([row["q_raw"] for row in records], dtype=np.float64)
    q_cmd = np.asarray([row["q_cmd"] for row in records], dtype=np.float64)
    q_actual = np.asarray([row["q_actual"] for row in records], dtype=np.float64)
    qdot_cmd = np.asarray([row["qdot_cmd"] for row in records], dtype=np.float64)
    qdot_actual = np.asarray([row["qdot_actual"] for row in records], dtype=np.float64)

    fig, axes = plt.subplots(2, 1, figsize=(11.0, 7.0), sharex=True, constrained_layout=True)
    axes[0].plot(t, q_raw, label="q_desired raw", lw=1.2)
    axes[0].plot(t, q_cmd, label="q_cmd", lw=1.6)
    axes[0].plot(t, q_actual, label="q_actual", lw=1.2)
    axes[0].set_ylabel("position [rad]")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc="best")

    axes[1].plot(t, qdot_cmd, label="qdot_cmd", lw=1.4)
    axes[1].plot(t, qdot_actual, label="qdot_actual", lw=1.2)
    axes[1].set_xlabel("trace time [s]")
    axes[1].set_ylabel("velocity [rad/s]")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(loc="best")

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


class LiveGuiMonitor:
    def __init__(self, *, enabled: bool, args: argparse.Namespace, source_column: str, sample_count: int) -> None:
        self.enabled = False
        self._labels: dict[str, object] = {}
        if not enabled:
            return
        try:
            import omni.ui as ui

            self._ui = ui
            self._window = ui.Window("Front Pitch Trace PD Monitor", width=430, height=390)
            with self._window.frame:
                with ui.VStack(spacing=4):
                    ui.Label("Front Pitch Trace PD", height=24)
                    ui.Label(
                        f"{args.joint_name} | {source_column} | Kp={args.kp:g}, Kd={args.kd:g}",
                        height=20,
                    )
                    ui.Spacer(height=4)
                    for key, title in (
                        ("status", "status"),
                        ("progress", "progress"),
                        ("q", "q desired / cmd / actual"),
                        ("q_error", "position error"),
                        ("qdot", "qdot cmd / actual"),
                        ("qdot_error", "velocity error"),
                        ("tau", "tau estimated"),
                        ("running", "running mean"),
                        ("limits", "limits"),
                    ):
                        with ui.HStack(height=24):
                            ui.Label(title, width=155)
                            self._labels[key] = ui.Label("-", width=260)
                    ui.Spacer(height=6)
                    ui.Label(f"samples: {sample_count}", height=20)
            self.enabled = True
        except Exception as exc:
            print(f"[WARN] Failed to create GUI monitor, continuing without it: {exc}")

    def update(self, record: dict[str, float], running: dict[str, float], *, status: str) -> None:
        if not self.enabled:
            return

        def set_text(key: str, value: str) -> None:
            label = self._labels.get(key)
            if label is not None:
                label.text = value

        set_text("status", status)
        set_text(
            "progress",
            f"{int(running['row'])}/{int(running['total'])}  t={record['trace_time_s']:.3f}s",
        )
        set_text(
            "q",
            f"{record['q_raw']:+.4f} / {record['q_cmd']:+.4f} / {record['q_actual']:+.4f} rad",
        )
        set_text(
            "q_error",
            f"cmd-act {record['q_cmd_minus_actual']:+.4f}, raw-act {record['q_raw_minus_actual']:+.4f} rad",
        )
        set_text(
            "qdot",
            f"{record['qdot_cmd']:+.4f} / {record['qdot_actual']:+.4f} rad/s",
        )
        set_text("qdot_error", f"{record['qdot_cmd_minus_actual']:+.4f} rad/s")
        set_text(
            "tau",
            f"{record['tau_est_clamped']:+.2f} N*m ({running['tau_saturation_rate'] * 100.0:.2f}% sat)",
        )
        set_text(
            "running",
            f"|e_cmd| {running['cmd_mean_abs']:.4f}, |e_raw| {running['raw_mean_abs']:.4f} rad",
        )
        set_text(
            "limits",
            f"|qdot_cmd| {abs(record['qdot_cmd']):.3f}/{running['velocity_limit']:.3f}, "
            f"|tau| {abs(record['tau_est_clamped']):.1f}/{running['effort_limit']:.1f}",
        )

    def set_status(self, status: str) -> None:
        if not self.enabled:
            return
        label = self._labels.get("status")
        if label is not None:
            label.text = status


def setup_viewport_camera(enabled: bool) -> None:
    if not enabled:
        return
    try:
        from isaacsim.core.utils.viewports import set_camera_view

        set_camera_view(eye=[3.4, -4.2, 2.2], target=[0.0, 0.0, 0.35])
    except Exception as exc:
        print(f"[WARN] Failed to set viewport camera: {exc}")


def pace_gui_replay(simulation_app, replay_wall_start: float, sample_count: int, args: argparse.Namespace) -> None:
    if args.realtime_factor <= 0.0:
        return
    target_elapsed = sample_count * args.control_dt / args.realtime_factor
    while True:
        sleep_s = replay_wall_start + target_elapsed - time.perf_counter()
        if sleep_s <= 0.0:
            return
        if hasattr(simulation_app, "is_running") and not simulation_app.is_running():
            return
        simulation_app.update()
        time.sleep(min(0.01, sleep_s))


def hold_gui_open(simulation_app, monitor: LiveGuiMonitor, seconds: float) -> None:
    if seconds <= 0.0:
        return
    monitor.set_status(f"Finished. Holding GUI for {seconds:g}s")
    end_time = time.perf_counter() + seconds
    while time.perf_counter() < end_time:
        if hasattr(simulation_app, "is_running") and not simulation_app.is_running():
            return
        simulation_app.update()
        time.sleep(0.02)


def main() -> None:
    args = parse_args()
    maybe_reexec_via_isaacsim()

    source_column = args.source_column or f"q_desired_{args.joint_name}"
    samples = load_trace_samples(args.trace.resolve(), args.env_id, source_column, args.skip_rows, args.frames)

    display_available = has_usable_x_display()
    if args.require_gui and not display_available:
        raise RuntimeError(
            "GUI was requested but no usable X display was detected. "
            "Start this from the Isaac Sim desktop session or fix DISPLAY/X11 forwarding."
        )
    run_headless = args.headless or not display_available
    sim_config = {"headless": run_headless}
    if run_headless:
        sim_config["hide_ui"] = True
        sim_config["extra_args"] = ["--no-window", "--/app/window/hideUi=1"]

    from isaacsim import SimulationApp

    simulation_app = SimulationApp(sim_config)

    import omni.usd
    from isaacsim.core.api.world import World
    from isaacsim.core.prims import SingleArticulation
    from isaacsim.core.utils.stage import open_stage
    from isaacsim.core.utils.types import ArticulationAction

    try:
        usd_path = args.usd.resolve()
        ok = open_stage(str(usd_path))
        print("[INFO] open_stage:", ok, usd_path)
        if not ok:
            raise RuntimeError(f"Failed to open USD stage: {usd_path}")

        stage = omni.usd.get_context().get_stage()
        if World.instance():
            World.instance().clear_instance()
        world = World(
            physics_dt=args.physics_dt,
            rendering_dt=args.render_dt,
            stage_units_in_meters=1.0,
        )
        if not args.no_ground:
            ensure_default_ground(stage)
        world.reset()
        setup_viewport_camera((not run_headless) and (not args.no_camera_setup))

        robot_prim = stage.GetPrimAtPath(ROBOT_ARTICULATION_ROOT_PATH)
        if not robot_prim.IsValid():
            raise RuntimeError(f"Robot articulation root not found: {ROBOT_ARTICULATION_ROOT_PATH}")

        robot = SingleArticulation(prim_path=ROBOT_ARTICULATION_ROOT_PATH, name="trace_pd_car")
        robot.initialize()
        dof_names = list(robot.dof_names)
        joint_name_to_index = {name: i for i, name in enumerate(dof_names)}
        missing = [name for name in WHEEL_JOINT_NAMES + BALL_JOINT_NAMES if name not in joint_name_to_index]
        if missing:
            raise RuntimeError(f"Missing expected joints in USD articulation: {missing}")

        ball_indices = [joint_name_to_index[name] for name in BALL_JOINT_NAMES]
        wheel_indices = [joint_name_to_index[name] for name in WHEEL_JOINT_NAMES]
        target_local_index = BALL_JOINT_NAMES.index(args.joint_name)
        target_dof_index = ball_indices[target_local_index]
        configure_drive_parameters(robot, ball_indices, wheel_indices, args)

        default_state = robot.get_joints_default_state()
        ball_default_pos = np.asarray([default_state.positions[i] for i in ball_indices], dtype=np.float64)
        ball_zero_vel = np.zeros(len(ball_indices), dtype=np.float64)
        wheel_zero_vel = np.zeros(len(wheel_indices), dtype=np.float64)

        ball_action = ArticulationAction(
            joint_positions=ball_default_pos.copy(),
            joint_velocities=ball_zero_vel.copy(),
            joint_indices=np.asarray(ball_indices, dtype=np.int32),
        )
        wheel_action = ArticulationAction(
            joint_velocities=wheel_zero_vel.copy(),
            joint_indices=np.asarray(wheel_indices, dtype=np.int32),
        )
        for _ in range(args.settle_steps):
            robot.apply_action(wheel_action)
            robot.apply_action(ball_action)
            world.step(render=not run_headless)

        current_positions = np.asarray(robot.get_joint_positions(), dtype=np.float64).reshape(-1)
        initial_q = float(current_positions[target_dof_index])
        state = GovernorState(q_ref=initial_q, q_cmd=initial_q, qdot_cmd=0.0)
        q_lower = -math.inf
        q_upper = math.inf
        # The selected raw trace target is already inside training limits. Keep
        # this clamp broad so the USD direct test reflects the input trajectory.
        control_decimation = max(1, int(round(args.control_dt / args.physics_dt)))
        records: list[dict[str, float]] = []
        monitor = LiveGuiMonitor(
            enabled=(not run_headless) and (not args.no_gui_monitor),
            args=args,
            source_column=source_column,
            sample_count=len(samples),
        )
        cmd_error_abs_sum = 0.0
        raw_error_abs_sum = 0.0
        qdot_error_abs_sum = 0.0
        tau_saturation_count = 0.0

        print("[INFO] Starting trace replay.")
        print(f"  trace: {args.trace.resolve()}")
        print(f"  samples: {len(samples)}  env_id: {args.env_id}  source: {source_column}")
        print(f"  joint: {args.joint_name}  dof_index: {target_dof_index}")
        print(f"  Kp={args.kp:g} Kd={args.kd:g} effort={args.effort_limit:g} velocity={args.velocity_limit:g}")
        print(f"  tau_ref={args.tau_ref:g} qddot_limit={args.qddot_limit:g} decimation={control_decimation}")

        replay_wall_start = time.perf_counter()
        for sample_index, sample in enumerate(samples):
            state = governor_step(
                state,
                sample.q_raw,
                control_dt=args.control_dt,
                tau_ref=args.tau_ref,
                qdot_limit=args.velocity_limit,
                qddot_limit=args.qddot_limit,
                lower_limit=q_lower,
                upper_limit=q_upper,
            )

            ball_pos_cmd = ball_default_pos.copy()
            ball_vel_cmd = ball_zero_vel.copy()
            ball_pos_cmd[target_local_index] = state.q_cmd
            ball_vel_cmd[target_local_index] = state.qdot_cmd
            ball_action = ArticulationAction(
                joint_positions=ball_pos_cmd,
                joint_velocities=ball_vel_cmd,
                joint_indices=np.asarray(ball_indices, dtype=np.int32),
            )

            for _ in range(control_decimation):
                robot.apply_action(wheel_action)
                robot.apply_action(ball_action)
                world.step(render=not run_headless)

            positions = np.asarray(robot.get_joint_positions(), dtype=np.float64).reshape(-1)
            velocities = np.asarray(robot.get_joint_velocities(), dtype=np.float64).reshape(-1)
            q_actual = float(positions[target_dof_index])
            qdot_actual = float(velocities[target_dof_index])
            tau_raw = args.kp * (state.q_cmd - q_actual) + args.kd * (state.qdot_cmd - qdot_actual)
            tau_clamped = clamp(tau_raw, -args.effort_limit, args.effort_limit)
            record = {
                "sample_index": sample_index,
                "trace_step": sample.step,
                "trace_time_s": sample.time_s,
                "q_raw": sample.q_raw,
                "q_ref": state.q_ref,
                "q_cmd": state.q_cmd,
                "qdot_cmd": state.qdot_cmd,
                "q_actual": q_actual,
                "qdot_actual": qdot_actual,
                "q_cmd_minus_actual": state.q_cmd - q_actual,
                "q_raw_minus_actual": sample.q_raw - q_actual,
                "qdot_cmd_minus_actual": state.qdot_cmd - qdot_actual,
                "tau_est_raw": tau_raw,
                "tau_est_clamped": tau_clamped,
            }
            records.append(record)
            cmd_error_abs_sum += abs(record["q_cmd_minus_actual"])
            raw_error_abs_sum += abs(record["q_raw_minus_actual"])
            qdot_error_abs_sum += abs(record["qdot_cmd_minus_actual"])
            tau_saturation_count += float(abs(tau_clamped) >= 0.98 * args.effort_limit)
            running = {
                "row": float(sample_index + 1),
                "total": float(len(samples)),
                "cmd_mean_abs": cmd_error_abs_sum / float(sample_index + 1),
                "raw_mean_abs": raw_error_abs_sum / float(sample_index + 1),
                "qdot_mean_abs": qdot_error_abs_sum / float(sample_index + 1),
                "tau_saturation_rate": tau_saturation_count / float(sample_index + 1),
                "velocity_limit": args.velocity_limit,
                "effort_limit": args.effort_limit,
            }
            monitor.update(record, running, status="Running")

            if args.print_interval and (sample_index + 1) % args.print_interval == 0:
                error = records[-1]["q_cmd_minus_actual"]
                print(
                    f"[INFO] row {sample_index + 1:5d}/{len(samples)} "
                    f"q_raw={sample.q_raw:+.4f} q_cmd={state.q_cmd:+.4f} "
                    f"q={q_actual:+.4f} err={error:+.4f}"
                )
            if not run_headless:
                pace_gui_replay(simulation_app, replay_wall_start, sample_index + 1, args)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = args.output_dir.resolve() / (
            f"{args.joint_name}_env{args.env_id}_kp{args.kp:g}_kd{args.kd:g}_{timestamp}"
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        records_csv = out_dir / "front_pitch_trace_pd_records.csv"
        summary_json = out_dir / "front_pitch_trace_pd_summary.json"
        save_records_csv(records_csv, records)
        summary = compute_summary(records, args)
        summary.update(
            {
                "trace": str(args.trace.resolve()),
                "usd": str(usd_path),
                "env_id": args.env_id,
                "source_column": source_column,
                "records_csv": str(records_csv),
            }
        )
        with summary_json.open("w") as f:
            json.dump(summary, f, indent=2)
            f.write("\n")

        if args.save_plot:
            save_plot(out_dir / "front_pitch_trace_pd_plot.png", records)

        print("[RESULT]")
        print(f"  output_dir: {out_dir}")
        print(f"  records_csv: {records_csv}")
        print(f"  summary_json: {summary_json}")
        print(
            "  q_cmd_minus_actual mean_abs/p95_abs: "
            f"{summary['q_cmd_minus_actual']['mean_abs']:.6f} / "
            f"{summary['q_cmd_minus_actual']['p95_abs']:.6f} rad"
        )
        print(
            "  qdot_cmd_minus_actual mean_abs/p95_abs: "
            f"{summary['qdot_cmd_minus_actual']['mean_abs']:.6f} / "
            f"{summary['qdot_cmd_minus_actual']['p95_abs']:.6f} rad/s"
        )
        print(
            "  tau saturation rate: "
            f"{100.0 * summary['estimated_tau_saturation_rate_ge_0p98']:.3f}%"
        )
        hold_gui_open(simulation_app, monitor, args.hold_open if not run_headless else 0.0)
    finally:
        simulation_app.close()


if __name__ == "__main__":
    main()
