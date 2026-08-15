#!/usr/bin/env python3
"""Offline sweep for the front-pitch trace PD reference-governor controller.

The sweep uses the same command generator as replay_front_pitch_trace_pd.py:

    q_desired trace -> smoothed/limited q_cmd, qdot_cmd -> PD plant

It does not launch Isaac Sim. The result is a shortlist of candidate
parameters for later USD direct validation in Isaac Sim.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path

import numba as nb
import numpy as np
import pandas as pd


THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = next(parent for parent in THIS_FILE.parents if (parent / "AGENTS.md").exists())
DEFAULT_TRACE_PATH = (
    PROJECT_ROOT
    / "results"
    / "stage1_model725_allcols_30hz_fine_pd_2026-05-12"
    / "raw_traces"
    / "model725_allcols_30hz_col05_stairs_down.csv"
)
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "results" / "front_pitch_trace_pd_usd_sweep"
DEFAULT_JOINT_NAME = "spm1_platform_joint_y"
DEFAULT_SOURCE_COLUMN = f"q_desired_{DEFAULT_JOINT_NAME}"
DEFAULT_ACTUAL_COLUMN = f"q_actual_{DEFAULT_JOINT_NAME}"
DEFAULT_QDOT_ACTUAL_COLUMN = f"qdot_actual_{DEFAULT_JOINT_NAME}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sweep q_desired -> q_cmd/qdot_cmd -> PD plant parameters before Isaac Sim validation."
    )
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE_PATH)
    parser.add_argument(
        "--env-id",
        type=str,
        default="5",
        help="Trace env_id to use, or 'all' to use every env in the trace.",
    )
    parser.add_argument("--source-column", type=str, default=DEFAULT_SOURCE_COLUMN)
    parser.add_argument("--actual-column", type=str, default=DEFAULT_ACTUAL_COLUMN)
    parser.add_argument("--qdot-actual-column", type=str, default=DEFAULT_QDOT_ACTUAL_COLUMN)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--skip-rows", type=int, default=0)
    parser.add_argument("--max-rows-per-case", type=int, default=0, help="0 means all selected rows.")
    parser.add_argument("--dt-sim", type=float, default=1.0 / 120.0)
    parser.add_argument("--dt-ctrl", type=float, default=1.0 / 30.0)
    parser.add_argument("--kp-range", type=str, default="100:1200:50")
    parser.add_argument("--kd-range", type=str, default="5:80:5")
    parser.add_argument("--tau-ref-values", type=str, default="0.02,0.04,0.06,0.08,0.10")
    parser.add_argument("--qddot-limit-values", type=str, default="4,6,8,10,12,16")
    parser.add_argument("--velocity-limit-values", type=str, default="1.5,2.0,2.5,3.0")
    parser.add_argument("--effort-limit-values", type=str, default="60")
    parser.add_argument("--j-axis", type=float, default=0.115)
    parser.add_argument("--b-axis", type=float, default=18.0)
    parser.add_argument("--tau-load", type=float, default=0.0)
    parser.add_argument("--q-lower", type=float, default=-1.6)
    parser.add_argument("--q-upper", type=float, default=0.5)
    parser.add_argument("--q0", type=float, default=0.0, help="Initial USD direct-test joint position.")
    parser.add_argument("--qdot0", type=float, default=0.0, help="Initial USD direct-test joint velocity.")
    parser.add_argument("--relative-error-floor-rad", type=float, default=0.05)
    parser.add_argument("--top-n", type=int, default=80)
    parser.add_argument("--plot-top", type=int, default=5)
    return parser.parse_args()


def parse_float_range(raw_value: str) -> np.ndarray:
    raw_value = raw_value.strip()
    if ":" in raw_value:
        parts = [float(item.strip()) for item in raw_value.split(":")]
        if len(parts) != 3:
            raise ValueError(f"Expected start:stop:step, got {raw_value!r}.")
        start, stop, step = parts
        if step <= 0.0:
            raise ValueError("Range step must be positive.")
        count = int(np.floor((stop - start) / step + 0.5)) + 1
        values = start + step * np.arange(count, dtype=np.float64)
        return values[values <= stop + 1.0e-9]
    return np.array([float(item.strip()) for item in raw_value.split(",") if item.strip()], dtype=np.float64)


def format_float(value: float, precision: int = 3) -> str:
    if math.isclose(value, round(value), rel_tol=0.0, abs_tol=1.0e-9):
        return str(int(round(value)))
    return f"{value:.{precision}f}".rstrip("0").rstrip(".")


def filename_float(value: float, precision: int = 3) -> str:
    return format_float(value, precision).replace("-", "m").replace(".", "p")


def validate_args(args: argparse.Namespace) -> None:
    if args.skip_rows < 0:
        raise ValueError("--skip-rows must be non-negative.")
    if args.max_rows_per_case < 0:
        raise ValueError("--max-rows-per-case must be non-negative.")
    if args.dt_sim <= 0.0 or args.dt_ctrl <= 0.0:
        raise ValueError("--dt-sim and --dt-ctrl must be positive.")
    if args.j_axis <= 0.0:
        raise ValueError("--j-axis must be positive.")
    if args.q_lower >= args.q_upper:
        raise ValueError("--q-lower must be smaller than --q-upper.")
    if args.top_n <= 0:
        raise ValueError("--top-n must be positive.")
    if args.plot_top < 0:
        raise ValueError("--plot-top must be non-negative.")


def load_trace_cases(args: argparse.Namespace) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[dict[str, object]]]:
    trace_path = args.trace.expanduser().resolve()
    if not trace_path.is_file():
        raise FileNotFoundError(f"Trace CSV not found: {trace_path}")

    table = pd.read_csv(trace_path)
    required = {"step", "time_s", args.source_column}
    missing = sorted(column for column in required if column not in table.columns)
    if missing:
        raise ValueError(f"Missing required columns in {trace_path}: {missing}")

    if args.actual_column not in table.columns:
        table[args.actual_column] = np.nan
    if args.qdot_actual_column not in table.columns:
        table[args.qdot_actual_column] = np.nan

    if args.env_id.lower() == "all":
        if "env_id" in table.columns:
            env_ids = sorted(int(env_id) for env_id in pd.unique(table["env_id"]))
        else:
            env_ids = [-1]
    else:
        env_ids = [int(args.env_id)]

    q_raw_parts: list[np.ndarray] = []
    q_actual_parts: list[np.ndarray] = []
    qdot_actual_parts: list[np.ndarray] = []
    starts = [0]
    metadata: list[dict[str, object]] = []

    for env_id in env_ids:
        if "env_id" in table.columns and env_id >= 0:
            env_table = table.loc[table["env_id"].astype(int) == env_id].copy()
        else:
            env_table = table.copy()
        if env_table.empty:
            continue
        env_table = env_table.sort_values(["step", "time_s"], kind="stable")
        if args.skip_rows:
            env_table = env_table.iloc[args.skip_rows:]
        if args.max_rows_per_case:
            env_table = env_table.iloc[: args.max_rows_per_case]
        if env_table.empty:
            continue

        q_raw = env_table[args.source_column].to_numpy(dtype=np.float64)
        q_actual = env_table[args.actual_column].to_numpy(dtype=np.float64)
        qdot_actual = env_table[args.qdot_actual_column].to_numpy(dtype=np.float64)
        q_raw_parts.append(q_raw)
        q_actual_parts.append(q_actual)
        qdot_actual_parts.append(qdot_actual)
        starts.append(starts[-1] + q_raw.size)

        metadata.append(
            {
                "trace": str(trace_path),
                "env_id": int(env_id),
                "rows": int(q_raw.size),
                "terrain_col": int(env_table["terrain_col"].iloc[0]) if "terrain_col" in env_table.columns else None,
                "terrain_name": str(env_table["terrain_name"].iloc[0]) if "terrain_name" in env_table.columns else "",
                "terrain_level": int(env_table["terrain_level"].iloc[0]) if "terrain_level" in env_table.columns else None,
                "step_start": int(env_table["step"].iloc[0]) if "step" in env_table.columns else 0,
                "step_end": int(env_table["step"].iloc[-1]) if "step" in env_table.columns else int(q_raw.size - 1),
            }
        )

    if not q_raw_parts:
        raise ValueError(f"No rows selected from {trace_path} with env_id={args.env_id!r}.")

    return (
        np.concatenate(q_raw_parts).astype(np.float64),
        np.concatenate(q_actual_parts).astype(np.float64),
        np.concatenate(qdot_actual_parts).astype(np.float64),
        np.array(starts, dtype=np.int64),
        metadata,
    )


@nb.njit(fastmath=True)
def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


@nb.njit(parallel=True, fastmath=True)
def sweep_controller(
    kps: np.ndarray,
    kds: np.ndarray,
    tau_refs: np.ndarray,
    qddot_limits: np.ndarray,
    velocity_limits: np.ndarray,
    effort_limits: np.ndarray,
    q_raw_all: np.ndarray,
    starts: np.ndarray,
    dt_sim: float,
    dt_ctrl: float,
    j_axis: float,
    b_axis: float,
    tau_load: float,
    q_lower: float,
    q_upper: float,
    q0: float,
    qdot0: float,
    relative_error_floor: float,
) -> np.ndarray:
    combo_count = (
        kps.size
        * kds.size
        * tau_refs.size
        * qddot_limits.size
        * velocity_limits.size
        * effort_limits.size
    )
    result = np.zeros((combo_count, 29), dtype=np.float64)
    decimation = max(1, int(round(dt_ctrl / dt_sim)))

    for combo_index in nb.prange(combo_count):
        rem0 = combo_index
        effort_index = rem0 % effort_limits.size
        rem1 = rem0 // effort_limits.size
        velocity_index = rem1 % velocity_limits.size
        rem2 = rem1 // velocity_limits.size
        qddot_index = rem2 % qddot_limits.size
        rem3 = rem2 // qddot_limits.size
        tau_ref_index = rem3 % tau_refs.size
        rem4 = rem3 // tau_refs.size
        kd_index = rem4 % kds.size
        kp_index = rem4 // kds.size

        kp = kps[kp_index]
        kd = kds[kd_index]
        tau_ref = tau_refs[tau_ref_index]
        qddot_limit = qddot_limits[qddot_index]
        velocity_limit = velocity_limits[velocity_index]
        effort_limit = effort_limits[effort_index]

        cmd_error_sum = 0.0
        cmd_error_sq_sum = 0.0
        raw_error_sum = 0.0
        raw_error_sq_sum = 0.0
        lag_sum = 0.0
        lag_sq_sum = 0.0
        qdot_error_sum = 0.0
        qdot_error_sq_sum = 0.0
        rel_raw_error_sum = 0.0
        tau_abs_sum = 0.0
        qdot_abs_sum = 0.0
        qdot_cmd_abs_sum = 0.0
        qdot_cmd_delta_abs_sum = 0.0
        qdot_cmd_delta_sq_sum = 0.0
        qcmd_delta_abs_sum = 0.0
        sat_count = 0.0
        qdot_limit_count = 0.0
        qdot_cmd_limit_count = 0.0
        sign_flip_count = 0.0
        max_cmd_error = 0.0
        max_raw_error = 0.0
        max_qdot_error = 0.0
        max_abs_tau = 0.0
        max_abs_qdot = 0.0
        max_abs_qdot_cmd_delta = 0.0
        total = 0.0
        delta_points = 0.0

        for case_index in range(starts.size - 1):
            start = starts[case_index]
            stop = starts[case_index + 1]
            q = q0
            qdot = qdot0
            q_ref = q0
            q_cmd = q0
            qdot_cmd = 0.0
            prev_q_cmd = q0
            prev_qdot_cmd = 0.0
            prev_qdot_sign = 0.0

            for row_index in range(start, stop):
                q_raw = q_raw_all[row_index]
                if tau_ref <= 0.0:
                    q_ref = q_raw
                else:
                    alpha = 1.0 - math.exp(-dt_ctrl / tau_ref)
                    q_ref = q_ref + alpha * (q_raw - q_ref)

                qdot_raw = (q_ref - q_cmd) / dt_ctrl
                qdot_limited = _clamp(qdot_raw, -velocity_limit, velocity_limit)
                qdot_delta = _clamp(
                    qdot_limited - qdot_cmd,
                    -qddot_limit * dt_ctrl,
                    qddot_limit * dt_ctrl,
                )
                qdot_cmd = qdot_cmd + qdot_delta
                q_cmd_unclamped = q_cmd + qdot_cmd * dt_ctrl
                q_cmd = _clamp(q_cmd_unclamped, q_lower, q_upper)
                if q_cmd != q_cmd_unclamped:
                    qdot_cmd = (q_cmd - prev_q_cmd) / dt_ctrl

                tau = 0.0
                for _ in range(decimation):
                    tau_raw = kp * (q_cmd - q) + kd * (qdot_cmd - qdot)
                    tau = _clamp(tau_raw, -effort_limit, effort_limit)
                    qddot = (tau - b_axis * qdot - tau_load) / j_axis
                    qdot = qdot + dt_sim * qddot
                    qdot = _clamp(qdot, -velocity_limit, velocity_limit)
                    q = q + dt_sim * qdot
                    q = _clamp(q, q_lower, q_upper)

                cmd_error = abs(q_cmd - q)
                raw_error = abs(q_raw - q)
                lag = abs(q_raw - q_cmd)
                qdot_error = abs(qdot_cmd - qdot)
                abs_tau = abs(tau)
                abs_qdot = abs(qdot)
                abs_qdot_cmd = abs(qdot_cmd)
                qdot_cmd_delta_abs = abs(qdot_cmd - prev_qdot_cmd)
                qcmd_delta_abs = abs(q_cmd - prev_q_cmd)
                rel_raw_error = raw_error / max(abs(q_raw), relative_error_floor)

                cmd_error_sum += cmd_error
                cmd_error_sq_sum += cmd_error * cmd_error
                raw_error_sum += raw_error
                raw_error_sq_sum += raw_error * raw_error
                lag_sum += lag
                lag_sq_sum += lag * lag
                qdot_error_sum += qdot_error
                qdot_error_sq_sum += qdot_error * qdot_error
                rel_raw_error_sum += rel_raw_error
                tau_abs_sum += abs_tau
                qdot_abs_sum += abs_qdot
                qdot_cmd_abs_sum += abs_qdot_cmd
                qdot_cmd_delta_abs_sum += qdot_cmd_delta_abs
                qdot_cmd_delta_sq_sum += qdot_cmd_delta_abs * qdot_cmd_delta_abs
                qcmd_delta_abs_sum += qcmd_delta_abs

                if abs_tau >= 0.98 * effort_limit:
                    sat_count += 1.0
                if abs_qdot >= 0.98 * velocity_limit:
                    qdot_limit_count += 1.0
                if abs_qdot_cmd >= 0.98 * velocity_limit:
                    qdot_cmd_limit_count += 1.0

                qdot_sign = 0.0
                if abs_qdot >= 1.0e-4:
                    qdot_sign = 1.0 if qdot > 0.0 else -1.0
                if row_index > start and abs(qdot_sign - prev_qdot_sign) > 1.0:
                    sign_flip_count += 1.0

                if cmd_error > max_cmd_error:
                    max_cmd_error = cmd_error
                if raw_error > max_raw_error:
                    max_raw_error = raw_error
                if qdot_error > max_qdot_error:
                    max_qdot_error = qdot_error
                if abs_tau > max_abs_tau:
                    max_abs_tau = abs_tau
                if abs_qdot > max_abs_qdot:
                    max_abs_qdot = abs_qdot
                if qdot_cmd_delta_abs > max_abs_qdot_cmd_delta:
                    max_abs_qdot_cmd_delta = qdot_cmd_delta_abs

                total += 1.0
                if row_index > start:
                    delta_points += 1.0

                prev_q_cmd = q_cmd
                prev_qdot_cmd = qdot_cmd
                prev_qdot_sign = qdot_sign

        cmd_error_mean = cmd_error_sum / total
        cmd_error_rmse = math.sqrt(cmd_error_sq_sum / total)
        raw_error_mean = raw_error_sum / total
        raw_error_rmse = math.sqrt(raw_error_sq_sum / total)
        lag_mean = lag_sum / total
        lag_rmse = math.sqrt(lag_sq_sum / total)
        qdot_error_mean = qdot_error_sum / total
        qdot_error_rmse = math.sqrt(qdot_error_sq_sum / total)
        rel_raw_error_mean = rel_raw_error_sum / total
        tau_abs_mean = tau_abs_sum / total
        qdot_abs_mean = qdot_abs_sum / total
        qdot_cmd_abs_mean = qdot_cmd_abs_sum / total
        qdot_cmd_delta_abs_mean = qdot_cmd_delta_abs_sum / max(delta_points, 1.0)
        qdot_cmd_delta_rmse = math.sqrt(qdot_cmd_delta_sq_sum / max(delta_points, 1.0))
        qcmd_delta_abs_mean = qcmd_delta_abs_sum / max(delta_points, 1.0)
        sat_rate = sat_count / total
        qdot_limit_rate = qdot_limit_count / total
        qdot_cmd_limit_rate = qdot_cmd_limit_count / total
        sign_flip_rate = sign_flip_count / max(delta_points, 1.0)

        # Balanced ranking:
        # - q_cmd tracking is the low-level PD objective.
        # - q_raw tracking/lag guards against over-smoothing the policy target.
        # - qdot_cmd_delta and sign flips guard against frequent motion jitter.
        # - saturation and qdot-limit use are hard-risk terms.
        risk = (
            cmd_error_mean / 0.02
            + cmd_error_rmse / 0.03
            + 0.60 * raw_error_mean / 0.10
            + 0.40 * lag_mean / 0.10
            + 0.20 * qdot_error_mean / 0.50
            + 3.0 * sat_rate
            + 2.0 * qdot_limit_rate
            + 1.0 * qdot_cmd_limit_rate
            + 0.25 * qdot_cmd_delta_abs_mean / 0.25
            + 0.50 * sign_flip_rate
        )

        result[combo_index, 0] = kp
        result[combo_index, 1] = kd
        result[combo_index, 2] = tau_ref
        result[combo_index, 3] = qddot_limit
        result[combo_index, 4] = velocity_limit
        result[combo_index, 5] = effort_limit
        result[combo_index, 6] = risk
        result[combo_index, 7] = cmd_error_mean
        result[combo_index, 8] = cmd_error_rmse
        result[combo_index, 9] = max_cmd_error
        result[combo_index, 10] = raw_error_mean
        result[combo_index, 11] = raw_error_rmse
        result[combo_index, 12] = max_raw_error
        result[combo_index, 13] = rel_raw_error_mean
        result[combo_index, 14] = lag_mean
        result[combo_index, 15] = lag_rmse
        result[combo_index, 16] = qdot_error_mean
        result[combo_index, 17] = qdot_error_rmse
        result[combo_index, 18] = max_qdot_error
        result[combo_index, 19] = sat_rate
        result[combo_index, 20] = qdot_limit_rate
        result[combo_index, 21] = qdot_cmd_limit_rate
        result[combo_index, 22] = tau_abs_mean
        result[combo_index, 23] = max_abs_tau
        result[combo_index, 24] = qdot_abs_mean
        result[combo_index, 25] = max_abs_qdot
        result[combo_index, 26] = qdot_cmd_abs_mean
        result[combo_index, 27] = qdot_cmd_delta_abs_mean
        result[combo_index, 28] = sign_flip_rate

    return result


def simulate_one(
    q_raw: np.ndarray,
    *,
    kp: float,
    kd: float,
    tau_ref: float,
    qddot_limit: float,
    velocity_limit: float,
    effort_limit: float,
    dt_sim: float,
    dt_ctrl: float,
    j_axis: float,
    b_axis: float,
    tau_load: float,
    q_lower: float,
    q_upper: float,
    q0: float,
    qdot0: float,
) -> pd.DataFrame:
    decimation = max(1, int(round(dt_ctrl / dt_sim)))
    q = float(q0)
    qdot = float(qdot0)
    q_ref = float(q0)
    q_cmd = float(q0)
    qdot_cmd = 0.0
    rows: list[dict[str, float]] = []
    for sample_index, raw in enumerate(q_raw):
        if tau_ref <= 0.0:
            q_ref = float(raw)
        else:
            alpha = 1.0 - math.exp(-dt_ctrl / tau_ref)
            q_ref = q_ref + alpha * (float(raw) - q_ref)
        qdot_raw = (q_ref - q_cmd) / dt_ctrl
        qdot_limited = max(-velocity_limit, min(velocity_limit, qdot_raw))
        qdot_delta = max(-qddot_limit * dt_ctrl, min(qddot_limit * dt_ctrl, qdot_limited - qdot_cmd))
        qdot_cmd += qdot_delta
        q_cmd_prev = q_cmd
        q_cmd_unclamped = q_cmd + qdot_cmd * dt_ctrl
        q_cmd = max(q_lower, min(q_upper, q_cmd_unclamped))
        if q_cmd != q_cmd_unclamped:
            qdot_cmd = (q_cmd - q_cmd_prev) / dt_ctrl
        tau = 0.0
        for _ in range(decimation):
            tau_raw = kp * (q_cmd - q) + kd * (qdot_cmd - qdot)
            tau = max(-effort_limit, min(effort_limit, tau_raw))
            qddot = (tau - b_axis * qdot - tau_load) / j_axis
            qdot = max(-velocity_limit, min(velocity_limit, qdot + dt_sim * qddot))
            q = max(q_lower, min(q_upper, q + dt_sim * qdot))
        rows.append(
            {
                "sample_index": sample_index,
                "time_s": sample_index * dt_ctrl,
                "q_raw": float(raw),
                "q_ref": q_ref,
                "q_cmd": q_cmd,
                "qdot_cmd": qdot_cmd,
                "q_model": q,
                "qdot_model": qdot,
                "q_cmd_minus_model": q_cmd - q,
                "q_raw_minus_model": float(raw) - q,
                "qdot_cmd_minus_model": qdot_cmd - qdot,
                "tau_model": tau,
            }
        )
    return pd.DataFrame(rows)


def save_plot(output_path: Path, traces: list[tuple[str, pd.DataFrame]]) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"[WARN] matplotlib unavailable, skip plot: {exc}", flush=True)
        return

    fig, axes = plt.subplots(2, 1, figsize=(11.5, 7.5), sharex=True, constrained_layout=True)
    for label, frame in traces:
        axes[0].plot(frame["time_s"], frame["q_model"], lw=1.2, label=f"{label} q_model")
        axes[0].plot(frame["time_s"], frame["q_cmd"], lw=1.0, ls="--", label=f"{label} q_cmd")
        axes[1].plot(frame["time_s"], frame["qdot_cmd"], lw=1.2, label=f"{label} qdot_cmd")
    if traces:
        axes[0].plot(traces[0][1]["time_s"], traces[0][1]["q_raw"], color="#222222", lw=1.0, alpha=0.7, label="q_desired raw")
    axes[0].set_ylabel("position [rad]")
    axes[1].set_ylabel("velocity [rad/s]")
    axes[1].set_xlabel("time [s]")
    for ax in axes:
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize=8)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    validate_args(args)

    trace_path = args.trace.expanduser().resolve()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = args.output_dir
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_ROOT / f"{trace_path.stem}_env{args.env_id}_sweep_{timestamp}"
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    kps = parse_float_range(args.kp_range)
    kds = parse_float_range(args.kd_range)
    tau_refs = parse_float_range(args.tau_ref_values)
    qddot_limits = parse_float_range(args.qddot_limit_values)
    velocity_limits = parse_float_range(args.velocity_limit_values)
    effort_limits = parse_float_range(args.effort_limit_values)

    q_raw, q_actual, qdot_actual, starts, metadata = load_trace_cases(args)
    combo_count = (
        kps.size
        * kds.size
        * tau_refs.size
        * qddot_limits.size
        * velocity_limits.size
        * effort_limits.size
    )
    print(
        f"Loaded {len(metadata)} case(s), {q_raw.size} samples, {combo_count} candidates.",
        flush=True,
    )
    print(
        f"Kp={args.kp_range}, Kd={args.kd_range}, tau_ref={args.tau_ref_values}, "
        f"qddot={args.qddot_limit_values}, velocity={args.velocity_limit_values}, effort={args.effort_limit_values}",
        flush=True,
    )

    result = sweep_controller(
        kps.astype(np.float64),
        kds.astype(np.float64),
        tau_refs.astype(np.float64),
        qddot_limits.astype(np.float64),
        velocity_limits.astype(np.float64),
        effort_limits.astype(np.float64),
        q_raw.astype(np.float64),
        starts,
        float(args.dt_sim),
        float(args.dt_ctrl),
        float(args.j_axis),
        float(args.b_axis),
        float(args.tau_load),
        float(args.q_lower),
        float(args.q_upper),
        float(args.q0),
        float(args.qdot0),
        max(float(args.relative_error_floor_rad), 1.0e-9),
    )

    columns = [
        "Kp",
        "Kd",
        "tau_ref_s",
        "qddot_limit_radps2",
        "velocity_limit_radps",
        "effort_limit_nm",
        "risk_score",
        "cmd_error_mean_rad",
        "cmd_error_rmse_rad",
        "cmd_error_max_rad",
        "raw_error_mean_rad",
        "raw_error_rmse_rad",
        "raw_error_max_rad",
        "raw_relative_error_mean",
        "raw_to_cmd_lag_mean_rad",
        "raw_to_cmd_lag_rmse_rad",
        "qdot_error_mean_radps",
        "qdot_error_rmse_radps",
        "qdot_error_max_radps",
        "tau_saturation_rate",
        "qdot_limit_rate",
        "qdot_cmd_limit_rate",
        "tau_abs_mean_nm",
        "tau_abs_max_nm",
        "qdot_abs_mean_radps",
        "qdot_abs_max_radps",
        "qdot_cmd_abs_mean_radps",
        "qdot_cmd_delta_abs_mean_radps",
        "qdot_sign_flip_rate",
    ]
    table = pd.DataFrame(result, columns=columns).sort_values(
        ["risk_score", "cmd_error_mean_rad", "raw_error_mean_rad"],
        kind="stable",
    )
    stable = table[
        (table["tau_saturation_rate"] <= 0.05)
        & (table["qdot_limit_rate"] <= 0.20)
        & (table["qdot_cmd_limit_rate"] <= 0.20)
        & (table["qdot_sign_flip_rate"] <= 0.20)
    ].sort_values(["risk_score", "cmd_error_mean_rad", "raw_error_mean_rad"], kind="stable")
    smooth = table[
        (table["tau_saturation_rate"] <= 0.05)
        & (table["qdot_limit_rate"] <= 0.20)
        & (table["qdot_cmd_limit_rate"] <= 0.20)
        & (table["qdot_sign_flip_rate"] <= 0.20)
        & (table["qdot_cmd_delta_abs_mean_radps"] <= 0.15)
    ].sort_values(["risk_score", "cmd_error_mean_rad", "raw_error_mean_rad"], kind="stable")
    tracking = table[
        (table["tau_saturation_rate"] <= 0.20)
        & (table["qdot_limit_rate"] <= 0.50)
    ].sort_values(["cmd_error_mean_rad", "risk_score"], kind="stable")

    table.to_csv(output_dir / "front_pitch_trace_pd_sweep_sorted.csv", index=False)
    table.head(args.top_n).to_csv(output_dir / "front_pitch_trace_pd_sweep_top.csv", index=False)
    stable.head(args.top_n).to_csv(output_dir / "front_pitch_trace_pd_sweep_stable_top.csv", index=False)
    smooth.head(args.top_n).to_csv(output_dir / "front_pitch_trace_pd_sweep_smooth_top.csv", index=False)
    tracking.head(args.top_n).to_csv(output_dir / "front_pitch_trace_pd_sweep_best_tracking.csv", index=False)
    pd.DataFrame(metadata).to_csv(output_dir / "front_pitch_trace_pd_sweep_cases.csv", index=False)

    best = table.iloc[0]
    best_stable = stable.iloc[0] if not stable.empty else None
    best_smooth = smooth.iloc[0] if not smooth.empty else None
    best_tracking = tracking.iloc[0] if not tracking.empty else None
    report = {
        "trace": str(trace_path),
        "env_id": args.env_id,
        "source_column": args.source_column,
        "samples": int(q_raw.size),
        "cases": metadata,
        "candidate_count": int(combo_count),
        "ranges": {
            "kp": args.kp_range,
            "kd": args.kd_range,
            "tau_ref": args.tau_ref_values,
            "qddot_limit": args.qddot_limit_values,
            "velocity_limit": args.velocity_limit_values,
            "effort_limit": args.effort_limit_values,
        },
        "plant": {
            "J_axis": args.j_axis,
            "B_axis": args.b_axis,
            "tau_load": args.tau_load,
            "q0": args.q0,
            "qdot0": args.qdot0,
            "q_lower": args.q_lower,
            "q_upper": args.q_upper,
        },
        "best_risk": best.to_dict(),
        "best_stable": None if best_stable is None else best_stable.to_dict(),
        "best_smooth": None if best_smooth is None else best_smooth.to_dict(),
        "best_tracking": None if best_tracking is None else best_tracking.to_dict(),
        "outputs": {
            "sorted": str(output_dir / "front_pitch_trace_pd_sweep_sorted.csv"),
            "top": str(output_dir / "front_pitch_trace_pd_sweep_top.csv"),
            "stable_top": str(output_dir / "front_pitch_trace_pd_sweep_stable_top.csv"),
            "smooth_top": str(output_dir / "front_pitch_trace_pd_sweep_smooth_top.csv"),
            "best_tracking": str(output_dir / "front_pitch_trace_pd_sweep_best_tracking.csv"),
        },
    }
    with (output_dir / "front_pitch_trace_pd_sweep_summary.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")

    with (output_dir / "front_pitch_trace_pd_sweep_report.md").open("w", encoding="utf-8") as f:
        f.write("# Front Pitch Trace PD Controller Sweep\n\n")
        f.write(f"- trace: `{trace_path}`\n")
        f.write(f"- env_id: `{args.env_id}`\n")
        f.write(f"- source_column: `{args.source_column}`\n")
        f.write(f"- samples: `{q_raw.size}`\n")
        f.write(f"- candidates: `{combo_count}`\n")
        f.write(f"- plant: `J={args.j_axis}`, `B={args.b_axis}`, `tau_load={args.tau_load}`\n\n")
        f.write("## Best Risk\n\n")
        f.write(
            f"- `Kp={format_float(best.Kp)}`, `Kd={format_float(best.Kd)}`, "
            f"`tau_ref={format_float(best.tau_ref_s)}`, `qddot={format_float(best.qddot_limit_radps2)}`, "
            f"`velocity={format_float(best.velocity_limit_radps)}`, `effort={format_float(best.effort_limit_nm)}`\n"
        )
        f.write(
            f"- risk `{best.risk_score:.6f}`, cmd error mean `{best.cmd_error_mean_rad:.6f} rad`, "
            f"raw error mean `{best.raw_error_mean_rad:.6f} rad`, tau sat `{best.tau_saturation_rate:.6f}`, "
            f"qdot limit `{best.qdot_limit_rate:.6f}`, qdot cmd delta mean `{best.qdot_cmd_delta_abs_mean_radps:.6f} rad/s`\n\n"
        )
        if best_stable is not None:
            f.write("## Best Stable\n\n")
            f.write(
                f"- `Kp={format_float(best_stable.Kp)}`, `Kd={format_float(best_stable.Kd)}`, "
                f"`tau_ref={format_float(best_stable.tau_ref_s)}`, "
                f"`qddot={format_float(best_stable.qddot_limit_radps2)}`, "
                f"`velocity={format_float(best_stable.velocity_limit_radps)}`, "
                f"`effort={format_float(best_stable.effort_limit_nm)}`\n"
            )
            f.write(
                f"- risk `{best_stable.risk_score:.6f}`, cmd error mean `{best_stable.cmd_error_mean_rad:.6f} rad`, "
                f"raw error mean `{best_stable.raw_error_mean_rad:.6f} rad`, tau sat `{best_stable.tau_saturation_rate:.6f}`, "
                f"qdot limit `{best_stable.qdot_limit_rate:.6f}`\n\n"
            )
        if best_smooth is not None:
            f.write("## Best Smooth\n\n")
            f.write(
                f"- `Kp={format_float(best_smooth.Kp)}`, `Kd={format_float(best_smooth.Kd)}`, "
                f"`tau_ref={format_float(best_smooth.tau_ref_s)}`, "
                f"`qddot={format_float(best_smooth.qddot_limit_radps2)}`, "
                f"`velocity={format_float(best_smooth.velocity_limit_radps)}`, "
                f"`effort={format_float(best_smooth.effort_limit_nm)}`\n"
            )
            f.write(
                f"- risk `{best_smooth.risk_score:.6f}`, cmd error mean `{best_smooth.cmd_error_mean_rad:.6f} rad`, "
                f"raw error mean `{best_smooth.raw_error_mean_rad:.6f} rad`, tau sat `{best_smooth.tau_saturation_rate:.6f}`, "
                f"qdot limit `{best_smooth.qdot_limit_rate:.6f}`, "
                f"qdot cmd delta mean `{best_smooth.qdot_cmd_delta_abs_mean_radps:.6f} rad/s`\n\n"
            )
        if best_tracking is not None:
            f.write("## Best Tracking Under Loose Limits\n\n")
            f.write(
                f"- `Kp={format_float(best_tracking.Kp)}`, `Kd={format_float(best_tracking.Kd)}`, "
                f"`tau_ref={format_float(best_tracking.tau_ref_s)}`, "
                f"`qddot={format_float(best_tracking.qddot_limit_radps2)}`, "
                f"`velocity={format_float(best_tracking.velocity_limit_radps)}`, "
                f"`effort={format_float(best_tracking.effort_limit_nm)}`\n"
            )
            f.write(
                f"- risk `{best_tracking.risk_score:.6f}`, cmd error mean `{best_tracking.cmd_error_mean_rad:.6f} rad`, "
                f"raw error mean `{best_tracking.raw_error_mean_rad:.6f} rad`, tau sat `{best_tracking.tau_saturation_rate:.6f}`, "
                f"qdot limit `{best_tracking.qdot_limit_rate:.6f}`\n"
            )

    if args.plot_top > 0:
        plot_traces: list[tuple[str, pd.DataFrame]] = []
        unique_candidates = table.head(args.plot_top)
        for _, row in unique_candidates.iterrows():
            frame = simulate_one(
                q_raw[: starts[1] - starts[0]],
                kp=float(row.Kp),
                kd=float(row.Kd),
                tau_ref=float(row.tau_ref_s),
                qddot_limit=float(row.qddot_limit_radps2),
                velocity_limit=float(row.velocity_limit_radps),
                effort_limit=float(row.effort_limit_nm),
                dt_sim=float(args.dt_sim),
                dt_ctrl=float(args.dt_ctrl),
                j_axis=float(args.j_axis),
                b_axis=float(args.b_axis),
                tau_load=float(args.tau_load),
                q_lower=float(args.q_lower),
                q_upper=float(args.q_upper),
                q0=float(args.q0),
                qdot0=float(args.qdot0),
            )
            label = (
                f"Kp{filename_float(row.Kp)}_Kd{filename_float(row.Kd)}_"
                f"t{filename_float(row.tau_ref_s)}_a{filename_float(row.qddot_limit_radps2)}_"
                f"v{filename_float(row.velocity_limit_radps)}"
            )
            frame.to_csv(output_dir / f"trace_{label}.csv", index=False)
            plot_traces.append((label, frame))
        save_plot(output_dir / "front_pitch_trace_pd_sweep_top_traces.png", plot_traces)

    print("[RESULT]", flush=True)
    print(f"  output_dir: {output_dir}", flush=True)
    print(
        "  best_risk: "
        f"Kp={format_float(best.Kp)}, Kd={format_float(best.Kd)}, tau_ref={format_float(best.tau_ref_s)}, "
        f"qddot={format_float(best.qddot_limit_radps2)}, velocity={format_float(best.velocity_limit_radps)}, "
        f"risk={best.risk_score:.6f}, cmd_err={best.cmd_error_mean_rad:.6f}, "
        f"raw_err={best.raw_error_mean_rad:.6f}",
        flush=True,
    )
    if best_stable is not None:
        print(
            "  best_stable: "
            f"Kp={format_float(best_stable.Kp)}, Kd={format_float(best_stable.Kd)}, "
            f"tau_ref={format_float(best_stable.tau_ref_s)}, "
            f"qddot={format_float(best_stable.qddot_limit_radps2)}, "
            f"velocity={format_float(best_stable.velocity_limit_radps)}, "
            f"risk={best_stable.risk_score:.6f}, cmd_err={best_stable.cmd_error_mean_rad:.6f}, "
            f"raw_err={best_stable.raw_error_mean_rad:.6f}",
            flush=True,
        )
    if best_smooth is not None:
        print(
            "  best_smooth: "
            f"Kp={format_float(best_smooth.Kp)}, Kd={format_float(best_smooth.Kd)}, "
            f"tau_ref={format_float(best_smooth.tau_ref_s)}, "
            f"qddot={format_float(best_smooth.qddot_limit_radps2)}, "
            f"velocity={format_float(best_smooth.velocity_limit_radps)}, "
            f"risk={best_smooth.risk_score:.6f}, cmd_err={best_smooth.cmd_error_mean_rad:.6f}, "
            f"raw_err={best_smooth.raw_error_mean_rad:.6f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
