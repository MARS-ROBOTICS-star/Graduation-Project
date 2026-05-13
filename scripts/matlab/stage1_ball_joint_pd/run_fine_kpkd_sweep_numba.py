#!/usr/bin/env python3
"""Fine Kp/Kd sweep for Stage1 ball-joint traces using an Isaac-calibrated plant."""

from __future__ import annotations

import argparse
from pathlib import Path

import numba as nb
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
JOINT_NAMES = (
    "spm1_platform_joint_z",
    "spm1_platform_joint_y",
    "spm1_platform_joint_x",
    "spm2_platform_joint_z",
    "spm2_platform_joint_y",
    "spm2_platform_joint_x",
)
Q_LOWER = np.array([-0.7, -1.6, -0.5, -0.7, -1.6, -0.5], dtype=np.float64)
Q_UPPER = np.array([0.7, 0.5, 0.5, 0.7, 0.5, 0.5], dtype=np.float64)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run fine Kp/Kd sweep over exported ball-joint traces.")
    parser.add_argument("--trace-dir", type=Path, required=True)
    parser.add_argument("--trace-glob", type=str, default="*_col*.csv")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--kp-range", type=str, default="100:2000:10")
    parser.add_argument("--kd-range", type=str, default="10:1000:10")
    parser.add_argument("--dt-sim", type=float, default=1.0 / 120.0)
    parser.add_argument("--dt-ctrl", type=float, default=1.0 / 30.0)
    parser.add_argument("--j-axis", type=float, default=0.10)
    parser.add_argument("--b-axis", type=float, default=0.5)
    parser.add_argument("--tau-load", type=float, default=0.0)
    parser.add_argument("--calibrate-plant", action="store_true", default=True)
    parser.add_argument("--no-calibrate-plant", action="store_false", dest="calibrate_plant")
    parser.add_argument("--calibration-kp", type=float, default=120.0)
    parser.add_argument("--calibration-kd", type=float, default=10.0)
    parser.add_argument("--j-axis-range", type=str, default="0.02:0.12:0.01")
    parser.add_argument("--b-axis-range", type=str, default="0:6:0.5")
    parser.add_argument("--tau-load-range", type=str, default="-8:8:4")
    parser.add_argument("--tau-max", type=float, default=60.0)
    parser.add_argument("--qdot-max", type=float, default=2.0)
    parser.add_argument("--relative-error-floor-rad", type=float, default=0.05)
    parser.add_argument("--sat-threshold", type=float, default=0.70)
    parser.add_argument("--qdot-limit-threshold", type=float, default=0.70)
    parser.add_argument("--top-n", type=int, default=200)
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


def matrix_from_columns(table: pd.DataFrame, prefix: str) -> np.ndarray:
    return table[[prefix + name for name in JOINT_NAMES]].to_numpy(dtype=np.float64)


def load_cases(
    trace_dir: Path,
    trace_glob: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[dict[str, object]]]:
    q_desired_parts: list[np.ndarray] = []
    q_actual_parts: list[np.ndarray] = []
    qdot_actual_parts: list[np.ndarray] = []
    q_initial_parts: list[np.ndarray] = []
    qdot_initial_parts: list[np.ndarray] = []
    starts = [0]
    metadata: list[dict[str, object]] = []

    trace_files = sorted(path for path in trace_dir.glob(trace_glob) if "combined" not in path.name)
    if not trace_files:
        raise FileNotFoundError(f"No trace files found under {trace_dir} with glob {trace_glob!r}.")

    for csv_path in trace_files:
        table = pd.read_csv(csv_path)
        for env_id in pd.unique(table["env_id"]):
            env_table = table.loc[table["env_id"] == env_id].sort_values("step")
            q_desired = matrix_from_columns(env_table, "q_desired_")
            q_actual = matrix_from_columns(env_table, "q_actual_")
            qdot_actual = matrix_from_columns(env_table, "qdot_actual_")
            q_desired_parts.append(q_desired)
            q_actual_parts.append(q_actual)
            qdot_actual_parts.append(qdot_actual)
            q_initial_parts.append(q_actual[0].copy())
            qdot_initial_parts.append(qdot_actual[0].copy())
            starts.append(starts[-1] + q_desired.shape[0])
            metadata.append(
                {
                    "csv_name": csv_path.name,
                    "env_id": int(env_id),
                    "terrain_col": int(env_table["terrain_col"].iloc[0]),
                    "terrain_name": str(env_table["terrain_name"].iloc[0]),
                    "terrain_level": int(env_table["terrain_level"].iloc[0]),
                    "num_samples": int(q_desired.shape[0]),
                }
            )

    return (
        np.vstack(q_desired_parts),
        np.vstack(q_actual_parts),
        np.vstack(qdot_actual_parts),
        np.array(starts, dtype=np.int64),
        np.vstack(q_initial_parts),
        np.vstack(qdot_initial_parts),
        metadata,
    )


@nb.njit(parallel=True, fastmath=True)
def calibrate_fixed_plant(
    js: np.ndarray,
    bs: np.ndarray,
    tau_loads: np.ndarray,
    q_desired_all: np.ndarray,
    q_actual_all: np.ndarray,
    starts: np.ndarray,
    q_initial: np.ndarray,
    qdot_initial: np.ndarray,
    dt_sim: float,
    dt_ctrl: float,
    calibration_kp: float,
    calibration_kd: float,
    tau_max: float,
    qdot_max: float,
    relative_error_floor: float,
) -> np.ndarray:
    combo_count = js.size * bs.size * tau_loads.size
    result = np.zeros((combo_count, 10), dtype=np.float64)
    decimation = max(1, int(round(dt_ctrl / dt_sim)))
    joint_count = q_desired_all.shape[1]

    for combo_index in nb.prange(combo_count):
        j_index = combo_index // (bs.size * tau_loads.size)
        rem = combo_index - j_index * bs.size * tau_loads.size
        b_index = rem // tau_loads.size
        load_index = rem - b_index * tau_loads.size
        j_axis = js[j_index]
        b_axis = bs[b_index]
        tau_load = tau_loads[load_index]

        error_sum = 0.0
        error_sq_sum = 0.0
        relative_error_sum = 0.0
        qdot_limit_count = 0.0
        sat_count = 0.0
        max_abs_qdot = 0.0
        max_abs_tau = 0.0
        total_points = 0.0

        for case_index in range(starts.size - 1):
            start = starts[case_index]
            stop = starts[case_index + 1]
            q = q_initial[case_index].copy()
            qdot = qdot_initial[case_index].copy()

            for row_index in range(start + 1, stop):
                tau = np.zeros(joint_count, dtype=np.float64)
                for _ in range(decimation):
                    for joint_index in range(joint_count):
                        q_target = q_desired_all[row_index, joint_index]
                        if q_target < Q_LOWER[joint_index]:
                            q_target = Q_LOWER[joint_index]
                        elif q_target > Q_UPPER[joint_index]:
                            q_target = Q_UPPER[joint_index]

                        tau_raw = calibration_kp * (q_target - q[joint_index]) - calibration_kd * qdot[joint_index]
                        if tau_raw < -tau_max:
                            tau[joint_index] = -tau_max
                        elif tau_raw > tau_max:
                            tau[joint_index] = tau_max
                        else:
                            tau[joint_index] = tau_raw

                        qddot = (tau[joint_index] - b_axis * qdot[joint_index] - tau_load) / j_axis
                        next_qdot = qdot[joint_index] + dt_sim * qddot
                        if next_qdot < -qdot_max:
                            next_qdot = -qdot_max
                        elif next_qdot > qdot_max:
                            next_qdot = qdot_max
                        qdot[joint_index] = next_qdot

                        next_q = q[joint_index] + dt_sim * qdot[joint_index]
                        if next_q < Q_LOWER[joint_index]:
                            next_q = Q_LOWER[joint_index]
                        elif next_q > Q_UPPER[joint_index]:
                            next_q = Q_UPPER[joint_index]
                        q[joint_index] = next_q

                for joint_index in range(joint_count):
                    actual = q_actual_all[row_index, joint_index]
                    error = abs(actual - q[joint_index])
                    denominator = max(abs(q_desired_all[row_index, joint_index]), relative_error_floor)
                    abs_qdot = abs(qdot[joint_index])
                    abs_tau = abs(tau[joint_index])
                    error_sum += error
                    error_sq_sum += error * error
                    relative_error_sum += error / denominator
                    if abs_qdot > 0.98 * qdot_max:
                        qdot_limit_count += 1.0
                    if abs_tau > 0.98 * tau_max:
                        sat_count += 1.0
                    if abs_qdot > max_abs_qdot:
                        max_abs_qdot = abs_qdot
                    if abs_tau > max_abs_tau:
                        max_abs_tau = abs_tau
                    total_points += 1.0

        error_mean = error_sum / total_points
        rmse = np.sqrt(error_sq_sum / total_points)
        rel_error_mean = relative_error_sum / total_points
        qdot_limit_rate = qdot_limit_count / total_points
        sat_ratio = sat_count / total_points
        score = rmse + 0.05 * qdot_limit_rate + 0.05 * sat_ratio

        result[combo_index, 0] = j_axis
        result[combo_index, 1] = b_axis
        result[combo_index, 2] = tau_load
        result[combo_index, 3] = score
        result[combo_index, 4] = error_mean
        result[combo_index, 5] = rmse
        result[combo_index, 6] = rel_error_mean
        result[combo_index, 7] = sat_ratio
        result[combo_index, 8] = qdot_limit_rate
        result[combo_index, 9] = max(max_abs_qdot / max(qdot_max, 1.0e-9), max_abs_tau / max(tau_max, 1.0e-9))

    return result


@nb.njit(parallel=True, fastmath=True)
def sweep_fixed_plant(
    kps: np.ndarray,
    kds: np.ndarray,
    q_desired_all: np.ndarray,
    starts: np.ndarray,
    q_initial: np.ndarray,
    qdot_initial: np.ndarray,
    dt_sim: float,
    dt_ctrl: float,
    j_axis: float,
    b_axis: float,
    tau_load: float,
    tau_max: float,
    qdot_max: float,
    relative_error_floor: float,
    old_relative_error_mean: float,
    sat_threshold: float,
    qdot_limit_threshold: float,
) -> np.ndarray:
    combo_count = kps.size * kds.size
    result = np.zeros((combo_count, 13), dtype=np.float64)
    decimation = max(1, int(round(dt_ctrl / dt_sim)))
    joint_count = q_desired_all.shape[1]

    for combo_index in nb.prange(combo_count):
        kp_index = combo_index // kds.size
        kd_index = combo_index - kp_index * kds.size
        kp = kps[kp_index]
        kd = kds[kd_index]

        new_error_sum = 0.0
        new_error_sq_sum = 0.0
        relative_error_sum = 0.0
        relative_error_sq_sum = 0.0
        qdot_limit_count = 0.0
        sat_count = 0.0
        max_abs_qdot = 0.0
        max_abs_tau = 0.0
        oscillation_count = 0.0
        smoothness_sum = 0.0
        total_points = 0.0
        smoothness_points = 0.0

        for case_index in range(starts.size - 1):
            start = starts[case_index]
            stop = starts[case_index + 1]
            q = q_initial[case_index].copy()
            qdot = qdot_initial[case_index].copy()
            prev_qdot = np.zeros(joint_count, dtype=np.float64)
            prev_sign = np.zeros(joint_count, dtype=np.float64)

            for row_index in range(start + 1, stop):
                tau = np.zeros(joint_count, dtype=np.float64)
                for _ in range(decimation):
                    for joint_index in range(joint_count):
                        q_target = q_desired_all[row_index, joint_index]
                        if q_target < Q_LOWER[joint_index]:
                            q_target = Q_LOWER[joint_index]
                        elif q_target > Q_UPPER[joint_index]:
                            q_target = Q_UPPER[joint_index]

                        tau_raw = kp * (q_target - q[joint_index]) - kd * qdot[joint_index]
                        if tau_raw < -tau_max:
                            tau[joint_index] = -tau_max
                        elif tau_raw > tau_max:
                            tau[joint_index] = tau_max
                        else:
                            tau[joint_index] = tau_raw

                        qddot = (tau[joint_index] - b_axis * qdot[joint_index] - tau_load) / j_axis
                        next_qdot = qdot[joint_index] + dt_sim * qddot
                        if next_qdot < -qdot_max:
                            next_qdot = -qdot_max
                        elif next_qdot > qdot_max:
                            next_qdot = qdot_max
                        qdot[joint_index] = next_qdot

                        next_q = q[joint_index] + dt_sim * qdot[joint_index]
                        if next_q < Q_LOWER[joint_index]:
                            next_q = Q_LOWER[joint_index]
                        elif next_q > Q_UPPER[joint_index]:
                            next_q = Q_UPPER[joint_index]
                        q[joint_index] = next_q

                for joint_index in range(joint_count):
                    target = q_desired_all[row_index, joint_index]
                    if target < Q_LOWER[joint_index]:
                        target = Q_LOWER[joint_index]
                    elif target > Q_UPPER[joint_index]:
                        target = Q_UPPER[joint_index]

                    error = abs(target - q[joint_index])
                    denominator = max(abs(target), relative_error_floor)
                    relative_error = error / denominator
                    abs_qdot = abs(qdot[joint_index])
                    abs_tau = abs(tau[joint_index])
                    qdot_sign = 0.0
                    if abs_qdot >= 1.0e-4:
                        qdot_sign = 1.0 if qdot[joint_index] > 0.0 else -1.0

                    new_error_sum += error
                    new_error_sq_sum += error * error
                    relative_error_sum += relative_error
                    relative_error_sq_sum += relative_error * relative_error
                    if abs_qdot > 0.98 * qdot_max:
                        qdot_limit_count += 1.0
                    if abs_tau > 0.98 * tau_max:
                        sat_count += 1.0
                    if abs_qdot > max_abs_qdot:
                        max_abs_qdot = abs_qdot
                    if abs_tau > max_abs_tau:
                        max_abs_tau = abs_tau
                    if abs(qdot_sign - prev_sign[joint_index]) > 1.0:
                        oscillation_count += 1.0
                    if row_index > start:
                        qdot_diff = qdot[joint_index] - prev_qdot[joint_index]
                        smoothness_sum += qdot_diff * qdot_diff
                        smoothness_points += 1.0
                    prev_qdot[joint_index] = qdot[joint_index]
                    prev_sign[joint_index] = qdot_sign
                    total_points += 1.0

        new_error_mean = new_error_sum / total_points
        rms_error = np.sqrt(new_error_sq_sum / total_points)
        rel_error_mean = relative_error_sum / total_points
        rms_rel_error = np.sqrt(relative_error_sq_sum / total_points)
        qdot_limit_rate = qdot_limit_count / total_points
        sat_ratio = sat_count / total_points
        smoothness_cost = smoothness_sum / max(smoothness_points, 1.0)
        rel_reduction = (old_relative_error_mean - rel_error_mean) / max(abs(old_relative_error_mean), 1.0e-9)
        oscillation_score = oscillation_count / max(total_points / joint_count * dt_ctrl, 1.0e-9)
        risk = (
            rel_error_mean
            + 2.0 * max(0.0, sat_ratio - sat_threshold)
            + 2.0 * max(0.0, qdot_limit_rate - qdot_limit_threshold)
            + 2.0 * max(0.0, -rel_reduction)
            + 0.01 * oscillation_score
            + 0.20 * smoothness_cost
        )

        result[combo_index, 0] = kp
        result[combo_index, 1] = kd
        result[combo_index, 2] = risk
        result[combo_index, 3] = rel_error_mean
        result[combo_index, 4] = rms_rel_error
        result[combo_index, 5] = new_error_mean
        result[combo_index, 6] = rms_error
        result[combo_index, 7] = rel_reduction
        result[combo_index, 8] = sat_ratio
        result[combo_index, 9] = qdot_limit_rate
        result[combo_index, 10] = max_abs_qdot
        result[combo_index, 11] = max_abs_tau
        result[combo_index, 12] = smoothness_cost

    return result


def main() -> None:
    args = parse_args()
    trace_dir = args.trace_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    kps = parse_float_range(args.kp_range)
    kds = parse_float_range(args.kd_range)
    (
        q_desired,
        q_actual,
        qdot_actual,
        starts,
        q_initial,
        qdot_initial,
        metadata,
    ) = load_cases(trace_dir, args.trace_glob)
    q_target = np.clip(q_desired, Q_LOWER, Q_UPPER)
    denominator = np.maximum(np.abs(q_target), max(args.relative_error_floor_rad, 1.0e-9))
    old_error = np.abs(q_target - q_actual)
    old_relative_error = old_error / denominator
    old_relative_error_mean = float(np.mean(old_relative_error))

    print(
        f"Loaded {len(metadata)} cases, {q_desired.shape[0]} samples, "
        f"{kps.size * kds.size} Kp/Kd candidates.",
        flush=True,
    )

    j_axis = float(args.j_axis)
    b_axis = float(args.b_axis)
    tau_load = float(args.tau_load)
    calibration_best: dict[str, float] | None = None
    calibration_columns = [
        "J_axis",
        "B_axis",
        "tau_load",
        "calibration_score",
        "calibration_error_mean",
        "calibration_rmse",
        "calibration_relative_error_mean",
        "calibration_sat_ratio",
        "calibration_qdot_limit_rate",
        "calibration_max_norm",
    ]
    if args.calibrate_plant:
        js = parse_float_range(args.j_axis_range)
        bs = parse_float_range(args.b_axis_range)
        tau_loads = parse_float_range(args.tau_load_range)
        print(
            f"Calibrating plant over {js.size * bs.size * tau_loads.size} candidates "
            f"with Kp={args.calibration_kp:g}, Kd={args.calibration_kd:g}.",
            flush=True,
        )
        calibration_result = calibrate_fixed_plant(
            js.astype(np.float64),
            bs.astype(np.float64),
            tau_loads.astype(np.float64),
            q_desired.astype(np.float64),
            q_actual.astype(np.float64),
            starts,
            q_initial.astype(np.float64),
            qdot_initial.astype(np.float64),
            float(args.dt_sim),
            float(args.dt_ctrl),
            float(args.calibration_kp),
            float(args.calibration_kd),
            float(args.tau_max),
            float(args.qdot_max),
            max(float(args.relative_error_floor_rad), 1.0e-9),
        )
        calibration_table = pd.DataFrame(calibration_result, columns=calibration_columns).sort_values(
            ["calibration_rmse", "calibration_error_mean", "calibration_score"],
            kind="stable",
        )
        calibration_table.to_csv(output_dir / "plant_calibration_grid.csv", index=False)
        best_calibration = calibration_table.iloc[0]
        j_axis = float(best_calibration.J_axis)
        b_axis = float(best_calibration.B_axis)
        tau_load = float(best_calibration.tau_load)
        calibration_best = {column: float(best_calibration[column]) for column in calibration_columns}
        pd.Series(calibration_best).to_json(output_dir / "plant_calibration_best.json", indent=2)
        print(
            f"Calibrated plant: J={j_axis:g}, B={b_axis:g}, tau_load={tau_load:g}, "
            f"rmse={best_calibration.calibration_rmse:.6f}.",
            flush=True,
        )

    result = sweep_fixed_plant(
        kps.astype(np.float64),
        kds.astype(np.float64),
        q_desired.astype(np.float64),
        starts,
        q_initial.astype(np.float64),
        qdot_initial.astype(np.float64),
        float(args.dt_sim),
        float(args.dt_ctrl),
        j_axis,
        b_axis,
        tau_load,
        float(args.tau_max),
        float(args.qdot_max),
        max(float(args.relative_error_floor_rad), 1.0e-9),
        old_relative_error_mean,
        float(args.sat_threshold),
        float(args.qdot_limit_threshold),
    )
    columns = [
        "Kp",
        "Kd",
        "risk_score",
        "new_relative_error_mean",
        "rms_relative_error_new",
        "new_error_mean",
        "rms_target_error_new",
        "relative_error_reduction_ratio",
        "sat_ratio",
        "qdot_limit_rate",
        "max_abs_qdot_new",
        "max_abs_tau_new",
        "smoothness_cost",
    ]
    table = pd.DataFrame(result, columns=columns).sort_values(["risk_score", "new_relative_error_mean"], kind="stable")
    table.to_csv(output_dir / "fine_kpkd_sweep_sorted.csv", index=False)
    table.head(max(int(args.top_n), 1)).to_csv(output_dir / "fine_kpkd_sweep_top.csv", index=False)
    under_limits = table[
        (table["sat_ratio"] <= float(args.sat_threshold))
        & (table["qdot_limit_rate"] <= float(args.qdot_limit_threshold))
    ].sort_values(["new_relative_error_mean", "risk_score"], kind="stable")
    under_limits.head(max(int(args.top_n), 1)).to_csv(
        output_dir / "fine_kpkd_sweep_best_tracking_under_limits.csv",
        index=False,
    )
    conservative_limits = table[
        (table["sat_ratio"] <= 0.30)
        & (table["qdot_limit_rate"] <= 0.60)
    ].sort_values(["new_relative_error_mean", "risk_score"], kind="stable")
    conservative_limits.head(max(int(args.top_n), 1)).to_csv(
        output_dir / "fine_kpkd_sweep_best_tracking_under_60qdot_30tau.csv",
        index=False,
    )
    pd.DataFrame(metadata).to_csv(output_dir / "fine_kpkd_trace_cases.csv", index=False)
    with (output_dir / "fine_kpkd_sweep_report.md").open("w", encoding="utf-8") as f:
        best = table.iloc[0]
        f.write("# Stage1 model_725 30 Hz fine Kp/Kd sweep\n\n")
        f.write(f"- trace_dir: `{trace_dir}`\n")
        f.write(f"- trace_glob: `{args.trace_glob}`\n")
        f.write(f"- cases: `{len(metadata)}`\n")
        f.write(f"- samples: `{q_desired.shape[0]}`\n")
        f.write(f"- Kp: `{args.kp_range}`\n")
        f.write(f"- Kd: `{args.kd_range}`\n")
        f.write(f"- plant calibration enabled: `{bool(args.calibrate_plant)}`\n")
        if calibration_best is not None:
            f.write(
                f"- plant calibration grid: `J={args.j_axis_range}`, `B={args.b_axis_range}`, "
                f"`tau_load={args.tau_load_range}`\n"
            )
            f.write(
                f"- plant calibration base gains: `Kp={args.calibration_kp}`, `Kd={args.calibration_kd}`\n"
            )
        f.write(f"- fixed plant used by sweep: `J={j_axis}`, `B={b_axis}`, `tau_load={tau_load}`\n")
        f.write(f"- fixed limits: `tau_max={args.tau_max}`, `qdot_max={args.qdot_max}`\n")
        f.write(f"- risk thresholds: `sat_threshold={args.sat_threshold}`, `qdot_limit_threshold={args.qdot_limit_threshold}`\n")
        f.write(f"- old_relative_error_mean: `{old_relative_error_mean:.6f}`\n\n")
        if calibration_best is not None:
            f.write("## Plant Calibration Best\n\n")
            f.write(
                f"`J={calibration_best['J_axis']:.6f}, B={calibration_best['B_axis']:.6f}, "
                f"tau_load={calibration_best['tau_load']:.6f}`, "
                f"`score={calibration_best['calibration_score']:.6f}`, "
                f"`rmse={calibration_best['calibration_rmse']:.6f}`, "
                f"`relative_error={calibration_best['calibration_relative_error_mean']:.6f}`.\n\n"
            )
        f.write("## Best Risk\n\n")
        f.write(
            f"`Kp={best.Kp:.0f}, Kd={best.Kd:.0f}`, "
            f"`risk={best.risk_score:.6f}`, "
            f"`relative_error={best.new_relative_error_mean:.6f}`, "
            f"`abs_error={best.new_error_mean:.6f}`, "
            f"`sat_ratio={best.sat_ratio:.6f}`, "
            f"`qdot_limit_rate={best.qdot_limit_rate:.6f}`.\n"
        )
        if not under_limits.empty:
            best_tracking = under_limits.iloc[0]
            f.write("\n## Best Tracking Under Configured Limits\n\n")
            f.write(
                f"`Kp={best_tracking.Kp:.0f}, Kd={best_tracking.Kd:.0f}`, "
                f"`risk={best_tracking.risk_score:.6f}`, "
                f"`relative_error={best_tracking.new_relative_error_mean:.6f}`, "
                f"`abs_error={best_tracking.new_error_mean:.6f}`, "
                f"`sat_ratio={best_tracking.sat_ratio:.6f}`, "
                f"`qdot_limit_rate={best_tracking.qdot_limit_rate:.6f}`.\n"
            )
        if not conservative_limits.empty:
            best_conservative_tracking = conservative_limits.iloc[0]
            f.write("\n## Best Tracking Under 60% Qdot / 30% Torque Limits\n\n")
            f.write(
                f"`Kp={best_conservative_tracking.Kp:.0f}, Kd={best_conservative_tracking.Kd:.0f}`, "
                f"`risk={best_conservative_tracking.risk_score:.6f}`, "
                f"`relative_error={best_conservative_tracking.new_relative_error_mean:.6f}`, "
                f"`abs_error={best_conservative_tracking.new_error_mean:.6f}`, "
                f"`sat_ratio={best_conservative_tracking.sat_ratio:.6f}`, "
                f"`qdot_limit_rate={best_conservative_tracking.qdot_limit_rate:.6f}`.\n"
            )
    print(f"Fine sweep complete: {output_dir / 'fine_kpkd_sweep_sorted.csv'}", flush=True)


if __name__ == "__main__":
    main()
