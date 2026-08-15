#!/usr/bin/env python3
"""Expanded Stage1 ball-joint PD sweep over plant uncertainty ranges.

This script complements the MATLAB/Simulink files in the same folder. It is
used for the large grid because running every candidate through interactive
Simulink scopes is unnecessarily slow.
"""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TRACE_DIR = PROJECT_ROOT / "results" / "stage1_ball_joint_pd_matlab" / "raw_traces"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "stage1_ball_joint_pd_matlab"
DEFAULT_TRACE_GLOB = "sec14_model699_flat_stairs_down_obstacles_col*.csv"

JOINT_NAMES = [
    "spm1_platform_joint_z",
    "spm1_platform_joint_y",
    "spm1_platform_joint_x",
    "spm2_platform_joint_z",
    "spm2_platform_joint_y",
    "spm2_platform_joint_x",
]

KPS = np.array([120.0, 160.0, 220.0, 320.0, 500.0, 800.0, 1000.0])
KDS = np.array([10.0, 16.0, 24.0, 32.0, 48.0, 64.0])
JS = np.array([0.03, 0.05, 0.08, 0.10, 0.15])
BS = np.array([0.0, 0.5, 1.0, 2.0, 5.0])
TAU_LOADS = np.array([-10.0, -5.0, 0.0, 5.0, 10.0])
TAU_VS = np.array([0.03, 0.04, 0.05])
QDOT_MAXS = np.array([2.0, 3.0, 4.0, 6.0, 8.0])

DT_SIM = 1.0 / 120.0
DT_CTRL = 1.0 / 30.0
DECIMATION = round(DT_CTRL / DT_SIM)
TAU_MAX = 60.0
QDOT_MAX = 2.0
Q_LOWER = np.array([-0.7, -1.6, -0.5, -0.7, -1.6, -0.5])
Q_UPPER = np.array([0.7, 0.5, 0.5, 0.7, 0.5, 0.5])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run expanded Stage1 ball-joint PD sweep.")
    parser.add_argument("--trace-dir", type=Path, default=DEFAULT_TRACE_DIR)
    parser.add_argument("--trace-glob", type=str, default=DEFAULT_TRACE_GLOB)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--kp-range",
        type=str,
        default=",".join(f"{value:g}" for value in KPS),
        help=(
            "Kp values as either comma-separated values or start:stop:step, inclusive. "
            "Example: 100:2000:10."
        ),
    )
    parser.add_argument(
        "--kd-range",
        type=str,
        default=",".join(f"{value:g}" for value in KDS),
        help=(
            "Kd values as either comma-separated values or start:stop:step, inclusive. "
            "Example: 10:1000:10."
        ),
    )
    parser.add_argument(
        "--plant-mode",
        type=str,
        choices=("uncertainty", "fixed"),
        default="uncertainty",
        help=(
            "Use the full J/B/tau_load plant uncertainty grid or a single fixed plant. "
            "The fixed mode is intended for fine Kp/Kd sweeps."
        ),
    )
    parser.add_argument("--fixed-j-axis", type=float, default=0.10)
    parser.add_argument("--fixed-b-axis", type=float, default=0.5)
    parser.add_argument("--fixed-tau-load", type=float, default=0.0)
    parser.add_argument(
        "--tau-v-values",
        type=str,
        default=",".join(f"{value:g}" for value in TAU_VS),
        help="Comma-separated qdot allocator filter time constants, in seconds.",
    )
    parser.add_argument(
        "--relative-error-floor-rad",
        type=float,
        default=0.05,
        help="Denominator floor for relative tracking error to avoid exploding near zero targets.",
    )
    parser.add_argument(
        "--qdot-max-values",
        type=str,
        default=",".join(f"{value:g}" for value in QDOT_MAXS),
        help="Comma-separated ball-joint velocity limits to sweep, in rad/s.",
    )
    parser.add_argument(
        "--sat-threshold",
        type=float,
        default=0.70,
        help="Torque saturation-rate threshold before adding risk penalty.",
    )
    parser.add_argument(
        "--qdot-limit-threshold",
        type=float,
        default=0.70,
        help="Velocity-limit-rate threshold before adding risk penalty.",
    )
    return parser.parse_args()


def parse_float_list(raw_value: str) -> np.ndarray:
    raw_value = raw_value.strip()
    if ":" in raw_value:
        parts = [float(item.strip()) for item in raw_value.split(":")]
        if len(parts) != 3:
            raise ValueError(f"Range expression must be start:stop:step, got {raw_value!r}.")
        start, stop, step = parts
        if step <= 0.0:
            raise ValueError(f"Range step must be positive, got {step}.")
        count = int(np.floor((stop - start) / step + 0.5)) + 1
        if count <= 0:
            raise ValueError(f"Range expression is empty: {raw_value!r}.")
        values = start + step * np.arange(count, dtype=np.float64)
        values = values[values <= stop + 1.0e-9]
        return values
    values = [float(item.strip()) for item in raw_value.split(",") if item.strip()]
    if not values:
        raise ValueError("Expected at least one numeric value.")
    return np.array(values, dtype=np.float64)


def build_param_grid(
    kps: np.ndarray,
    kds: np.ndarray,
    js: np.ndarray,
    bs: np.ndarray,
    tau_loads: np.ndarray,
    tau_vs: np.ndarray,
    qdot_maxs: np.ndarray,
) -> pd.DataFrame:
    rows = [
        (kp, kd, j, b, tau_load, tau_v, qdot_max)
        for kp, kd, j, b, tau_load, tau_v, qdot_max in itertools.product(
            kps,
            kds,
            js,
            bs,
            tau_loads,
            tau_vs,
            qdot_maxs,
        )
    ]
    return pd.DataFrame(rows, columns=["Kp", "Kd", "J_axis", "B_axis", "tau_load", "tau_v", "qdot_max"])


def load_trace_cases(trace_dir: Path, trace_glob: str) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    trace_files = sorted(trace_dir.glob(trace_glob))
    trace_files = [path for path in trace_files if "combined" not in path.name]
    for csv_path in trace_files:
        table = pd.read_csv(csv_path)
        for env_id in pd.unique(table["env_id"]):
            env_table = table.loc[table["env_id"] == env_id].sort_values("step")
            stem = csv_path.stem
            case_name = f"{stem}_env{int(env_id)}"
            q_desired = matrix_from_columns(env_table, "q_desired_")
            q_target_old = matrix_from_columns_any(
                env_table,
                ("q_position_target_", "q_position_target_old_"),
            )
            q_actual = matrix_from_columns(env_table, "q_actual_")
            qdot_actual = matrix_from_columns(env_table, "qdot_actual_")
            cases.append(
                {
                    "case_name": case_name,
                    "csv_name": csv_path.name,
                    "csv_path": str(csv_path),
                    "env_id": int(env_id),
                    "terrain_col": int(env_table["terrain_col"].iloc[0]),
                    "terrain_name": str(env_table["terrain_name"].iloc[0]),
                    "terrain_level": float(env_table["terrain_level"].iloc[0]),
                    "time_s": env_table["time_s"].to_numpy(dtype=np.float64),
                    "q_desired": q_desired,
                    "q_target_old": q_target_old,
                    "q_actual_old": q_actual,
                    "qdot_actual_old": qdot_actual,
                }
            )
    if not cases:
        raise FileNotFoundError(f"No trace cases found under {trace_dir} with glob {trace_glob!r}")
    return cases


def matrix_from_columns(table: pd.DataFrame, prefix: str) -> np.ndarray:
    columns = [prefix + name for name in JOINT_NAMES]
    return table[columns].to_numpy(dtype=np.float64)


def matrix_from_columns_any(table: pd.DataFrame, prefixes: tuple[str, ...]) -> np.ndarray:
    for prefix in prefixes:
        columns = [prefix + name for name in JOINT_NAMES]
        if all(column in table.columns for column in columns):
            return table[columns].to_numpy(dtype=np.float64)
    prefix_text = ", ".join(prefixes)
    raise KeyError(f"None of the requested column prefix groups exist: {prefix_text}")


def simulate_case(
    case: dict[str, object],
    grid: pd.DataFrame,
    relative_error_floor_rad: float,
    sat_threshold: float,
    qdot_limit_threshold: float,
) -> pd.DataFrame:
    q_desired = case["q_desired"]
    q_target_old = case["q_target_old"]
    q_actual_old = case["q_actual_old"]
    qdot_actual_old = case["qdot_actual_old"]
    time_s = case["time_s"]
    assert isinstance(q_desired, np.ndarray)
    assert isinstance(q_target_old, np.ndarray)
    assert isinstance(q_actual_old, np.ndarray)
    assert isinstance(qdot_actual_old, np.ndarray)
    assert isinstance(time_s, np.ndarray)

    candidate_count = len(grid)
    joint_count = q_desired.shape[1]
    sample_count = q_desired.shape[0]
    total_points = sample_count * joint_count
    duration_s = max(float(time_s[-1] - time_s[0]), DT_CTRL)

    kp = grid["Kp"].to_numpy(dtype=np.float64)[:, None]
    kd = grid["Kd"].to_numpy(dtype=np.float64)[:, None]
    j_axis = grid["J_axis"].to_numpy(dtype=np.float64)[:, None]
    b_axis = grid["B_axis"].to_numpy(dtype=np.float64)[:, None]
    tau_load = grid["tau_load"].to_numpy(dtype=np.float64)[:, None]
    alpha_v = (1.0 - np.exp(-DT_CTRL / grid["tau_v"].to_numpy(dtype=np.float64)))[:, None]
    qdot_max = grid["qdot_max"].to_numpy(dtype=np.float64)[:, None]

    q = np.zeros((candidate_count, joint_count), dtype=np.float64)
    qdot = np.zeros_like(q)
    qdot_alloc = np.zeros_like(q)
    prev_qdot = np.zeros_like(q)
    prev_qdot_alloc = np.zeros_like(q)
    prev_sign = np.zeros_like(q)

    new_error_sum = np.zeros(candidate_count, dtype=np.float64)
    new_error_sq_sum = np.zeros(candidate_count, dtype=np.float64)
    qdot_limit_count = np.zeros(candidate_count, dtype=np.float64)
    sat_count = np.zeros(candidate_count, dtype=np.float64)
    relative_error_sum = np.zeros(candidate_count, dtype=np.float64)
    relative_error_sq_sum = np.zeros(candidate_count, dtype=np.float64)
    max_abs_qdot = np.zeros(candidate_count, dtype=np.float64)
    max_abs_tau = np.zeros(candidate_count, dtype=np.float64)
    oscillation_count = np.zeros(candidate_count, dtype=np.float64)
    smoothness_sum = np.zeros(candidate_count, dtype=np.float64)
    qdot_alloc_rmse_sum = np.zeros(candidate_count, dtype=np.float64)
    qdot_alloc_smoothness_sum = np.zeros(candidate_count, dtype=np.float64)

    relative_error_floor = max(float(relative_error_floor_rad), 1.0e-9)
    q_target_all = np.clip(q_desired, Q_LOWER, Q_UPPER)
    relative_denominator_all = np.maximum(np.abs(q_target_all), relative_error_floor)

    for step_index in range(sample_count):
        q_target = q_target_all[step_index]
        relative_denominator = relative_denominator_all[step_index]
        tau = np.zeros_like(q)
        for _ in range(DECIMATION):
            tau_raw = kp * (q_target[None, :] - q) - kd * qdot
            tau = np.clip(tau_raw, -TAU_MAX, TAU_MAX)
            qddot = (tau - b_axis * qdot - tau_load) / j_axis
            qdot = np.clip(qdot + DT_SIM * qddot, -qdot_max, qdot_max)
            q = np.clip(q + DT_SIM * qdot, Q_LOWER, Q_UPPER)

        qdot_alloc = (1.0 - alpha_v) * qdot_alloc + alpha_v * qdot

        error = np.abs(q_target[None, :] - q)
        relative_error = error / relative_denominator[None, :]
        abs_qdot = np.abs(qdot)
        abs_tau = np.abs(tau)
        qdot_sign = np.sign(qdot)
        qdot_sign[abs_qdot < 1.0e-4] = 0.0

        new_error_sum += error.sum(axis=1)
        new_error_sq_sum += (error * error).sum(axis=1)
        relative_error_sum += relative_error.sum(axis=1)
        relative_error_sq_sum += (relative_error * relative_error).sum(axis=1)
        qdot_limit_count += (abs_qdot > 0.98 * qdot_max).sum(axis=1)
        sat_count += (abs_tau > 0.98 * TAU_MAX).sum(axis=1)
        max_abs_qdot = np.maximum(max_abs_qdot, abs_qdot.max(axis=1))
        max_abs_tau = np.maximum(max_abs_tau, abs_tau.max(axis=1))
        oscillation_count += (np.abs(qdot_sign - prev_sign) > 1.0).sum(axis=1)
        if step_index > 0:
            qdot_diff = qdot - prev_qdot
            alloc_diff = qdot_alloc - prev_qdot_alloc
            smoothness_sum += (qdot_diff * qdot_diff).sum(axis=1)
            qdot_alloc_smoothness_sum += (alloc_diff * alloc_diff).sum(axis=1)
        qdot_alloc_error = qdot_alloc - qdot
        qdot_alloc_rmse_sum += (qdot_alloc_error * qdot_alloc_error).sum(axis=1)

        prev_qdot = qdot.copy()
        prev_qdot_alloc = qdot_alloc.copy()
        prev_sign = qdot_sign

    old_gap = np.abs(q_target_all - q_target_old)
    old_error = np.abs(q_target_all - q_actual_old)
    old_relative_error = old_error / relative_denominator_all
    old_gap_mean = float(old_gap.mean())
    old_error_mean = float(old_error.mean())
    old_relative_error_mean = float(old_relative_error.mean())
    old_qdot_rms = float(np.sqrt(np.mean(qdot_actual_old * qdot_actual_old)))

    new_error_mean = new_error_sum / total_points
    rms_target_error_new = np.sqrt(new_error_sq_sum / total_points)
    new_relative_error_mean = relative_error_sum / total_points
    rms_relative_error_new = np.sqrt(relative_error_sq_sum / total_points)
    qdot_limit_rate = qdot_limit_count / total_points
    sat_ratio = sat_count / total_points
    oscillation_score = oscillation_count / duration_s / joint_count
    smoothness_cost = smoothness_sum / max((sample_count - 1) * joint_count, 1)
    qdot_alloc_rmse = np.sqrt(qdot_alloc_rmse_sum / total_points)
    qdot_alloc_smoothness = qdot_alloc_smoothness_sum / max((sample_count - 1) * joint_count, 1)
    new_qdot_rms = np.sqrt(np.mean(qdot * qdot, axis=1))
    error_reduction_ratio = (old_error_mean - new_error_mean) / max(abs(old_error_mean), 1.0e-9)
    relative_error_reduction_ratio = (old_relative_error_mean - new_relative_error_mean) / max(
        abs(old_relative_error_mean),
        1.0e-9,
    )
    new_vs_old_qdot_ratio = new_qdot_rms / max(abs(old_qdot_rms), 1.0e-9)
    risk_score = compute_risk(
        new_relative_error_mean,
        relative_error_reduction_ratio,
        sat_ratio,
        qdot_limit_rate,
        oscillation_score,
        smoothness_cost,
        sat_threshold,
        qdot_limit_threshold,
    )

    result = grid.copy()
    result.insert(0, "case_name", str(case["case_name"]))
    result.insert(1, "csv_name", str(case["csv_name"]))
    result.insert(2, "env_id", int(case["env_id"]))
    result.insert(3, "terrain_col", int(case["terrain_col"]))
    result.insert(4, "terrain_name", str(case["terrain_name"]))
    result.insert(5, "terrain_level", float(case["terrain_level"]))
    result["num_samples"] = sample_count
    result["duration_s"] = duration_s
    result["old_gap_mean"] = old_gap_mean
    result["old_error_mean"] = old_error_mean
    result["old_relative_error_mean"] = old_relative_error_mean
    result["new_error_mean"] = new_error_mean
    result["rms_target_error_new"] = rms_target_error_new
    result["new_relative_error_mean"] = new_relative_error_mean
    result["rms_relative_error_new"] = rms_relative_error_new
    result["error_reduction_ratio"] = error_reduction_ratio
    result["relative_error_reduction_ratio"] = relative_error_reduction_ratio
    result["max_abs_qdot_new"] = max_abs_qdot
    result["qdot_limit_rate"] = qdot_limit_rate
    result["sat_ratio"] = sat_ratio
    result["max_abs_tau_new"] = max_abs_tau
    result["oscillation_score"] = oscillation_score
    result["smoothness_cost"] = smoothness_cost
    result["qdot_alloc_rmse"] = qdot_alloc_rmse
    result["qdot_alloc_smoothness"] = qdot_alloc_smoothness
    result["old_qdot_rms"] = old_qdot_rms
    result["new_qdot_rms"] = new_qdot_rms
    result["new_vs_old_qdot_ratio"] = new_vs_old_qdot_ratio
    result["risk_score"] = risk_score
    return result


def compute_risk(
    new_relative_error_mean: np.ndarray,
    relative_error_reduction_ratio: np.ndarray,
    sat_ratio: np.ndarray,
    qdot_limit_rate: np.ndarray,
    oscillation_score: np.ndarray,
    smoothness_cost: np.ndarray,
    sat_threshold: float,
    qdot_limit_threshold: float,
) -> np.ndarray:
    return (
        new_relative_error_mean
        + 2.0 * np.maximum(0.0, sat_ratio - sat_threshold)
        + 2.0 * np.maximum(0.0, qdot_limit_rate - qdot_limit_threshold)
        + 2.0 * np.maximum(0.0, -relative_error_reduction_ratio)
        + 0.01 * oscillation_score
        + 0.20 * smoothness_cost
    )


def write_report(
    report_path: Path,
    summary: pd.DataFrame,
    robust: pd.DataFrame,
    full_best: pd.Series,
    case_best: pd.DataFrame,
    *,
    grid: pd.DataFrame,
    case_count: int,
    trace_dir: Path,
    trace_glob: str,
    relative_error_floor_rad: float,
    plant_mode: str,
    sat_threshold: float,
    qdot_limit_threshold: float,
) -> None:
    top = robust.iloc[0]
    top10 = robust.head(10)

    def _format_values(values: np.ndarray) -> str:
        unique_values = np.unique(values.astype(np.float64))
        if unique_values.size > 12:
            return f"{unique_values[0]:g}:{unique_values[-1]:g} ({unique_values.size} values)"
        return ", ".join(f"{value:g}" for value in unique_values)

    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Stage1 球铰 PD 扩展 plant 不确定性扫参报告\n\n")
        f.write("本轮按相对跟踪误差排序：`|q_target - q_actual| / max(|q_target|, q_floor)`。\n")
        f.write(f"- trace 目录：`{trace_dir}`\n")
        f.write(f"- trace glob：`{trace_glob}`\n")
        f.write(f"- `q_floor = {relative_error_floor_rad:.3f} rad`\n\n")
        f.write(f"- `sat_threshold = {sat_threshold:.2f}`\n")
        f.write(f"- `qdot_limit_threshold = {qdot_limit_threshold:.2f}`\n\n")
        f.write("## 1. 扫参范围\n\n")
        f.write(f"- `plant_mode = {plant_mode}`\n")
        f.write(f"- `Kp = {_format_values(grid['Kp'].to_numpy())}`\n")
        f.write(f"- `Kd = {_format_values(grid['Kd'].to_numpy())}`\n")
        f.write(f"- `J = {_format_values(grid['J_axis'].to_numpy())} kg*m^2`\n")
        f.write(f"- `B = {_format_values(grid['B_axis'].to_numpy())}`\n")
        f.write(f"- `tau_load = {_format_values(grid['tau_load'].to_numpy())} N*m`\n")
        f.write(f"- `tau_v = {_format_values(grid['tau_v'].to_numpy())} s`\n")
        f.write(f"- `qdot_max = {_format_values(grid['qdot_max'].to_numpy())} rad/s`\n\n")
        f.write("这里 `J/B/tau_load` 作为 plant 不确定性，不是后续要写入 Isaac 的控制参数；")
        f.write("真正可落地的控制候选是 `Kp/Kd/qdot_max/tau_v`。\n\n")
        f.write("## 2. 数据规模\n\n")
        f.write(f"- 真实轨迹 case：`{case_count}`\n")
        f.write(f"- 完整参数组合：`{len(grid)}`\n")
        f.write(f"- 全量仿真评估：`{case_count * len(grid)}` 条 case-combination 结果\n\n")
        f.write("## 3. 鲁棒控制推荐\n\n")
        f.write("跨全部 `J/B/tau_load` 和全部真实轨迹聚合后，当前鲁棒跟踪候选第一组为：\n\n")
        f.write("| Kp | Kd | qdot_max | tau_v | risk_mean | risk_max | rel_error_mean | abs_error_mean | rel_reduction | sat_ratio | qdot_limit_rate | qdot_alloc_rmse | qdot_alloc_smoothness |\n")
        f.write("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        f.write(
            f"| {top.Kp:.0f} | {top.Kd:.0f} | {top.qdot_max:.1f} | {top.tau_v:.2f} | "
            f"{top.risk_score_mean:.6f} | "
            f"{top.risk_score_max:.6f} | {top.new_relative_error_mean_mean:.6f} | "
            f"{top.new_error_mean_mean:.6f} | {top.relative_error_reduction_ratio_mean:.6f} | "
            f"{top.sat_ratio_mean:.6f} | "
            f"{top.qdot_limit_rate_mean:.6f} | {top.qdot_alloc_rmse_mean:.6f} | "
            f"{top.qdot_alloc_smoothness_mean:.6f} |\n\n"
        )
        f.write("说明：`tau_v` 不改变 PD plant 的 `q/qdot/tau` 跟踪响应，只改变 `qdot_alloc` 低通后的 allocator 输入；因此同一 `Kp/Kd/qdot_max` 下三档 `tau_v` 的 tracking risk 会相同。`tau_v=0.03` 速度滞后最小，`tau_v=0.05` 最平滑，`tau_v=0.04` 是两者之间的折中。\n\n")
        f.write("前 `10` 个鲁棒候选：\n\n")
        f.write("| rank | Kp | Kd | qdot_max | tau_v | risk_mean | risk_max | rel_error_mean | abs_error_mean | sat_ratio | qdot_limit_rate | qdot_alloc_rmse | qdot_alloc_smoothness |\n")
        f.write("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for rank, (_, row) in enumerate(top10.iterrows(), start=1):
            f.write(
                f"| {rank} | {row.Kp:.0f} | {row.Kd:.0f} | {row.qdot_max:.1f} | {row.tau_v:.2f} | "
                f"{row.risk_score_mean:.6f} | {row.risk_score_max:.6f} | "
                f"{row.new_relative_error_mean_mean:.6f} | {row.new_error_mean_mean:.6f} | "
                f"{row.sat_ratio_mean:.6f} | "
                f"{row.qdot_limit_rate_mean:.6f} | {row.qdot_alloc_rmse_mean:.6f} | "
                f"{row.qdot_alloc_smoothness_mean:.6f} |\n"
            )
        f.write("\n## 4. 完整六维最小风险点\n\n")
        f.write("完整六维组合的最小平均风险点为：\n\n")
        f.write("| Kp | Kd | J | B | tau_load | tau_v | qdot_max | risk_score | rel_error_mean | abs_error_mean | sat_ratio | qdot_limit_rate |\n")
        f.write("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        f.write(
            f"| {full_best.Kp:.0f} | {full_best.Kd:.0f} | {full_best.J_axis:.2f} | "
            f"{full_best.B_axis:.1f} | {full_best.tau_load:.0f} | {full_best.tau_v:.2f} | "
            f"{full_best.qdot_max:.1f} | "
            f"{full_best.risk_score:.6f} | {full_best.new_relative_error_mean:.6f} | "
            f"{full_best.new_error_mean:.6f} | "
            f"{full_best.sat_ratio:.6f} | {full_best.qdot_limit_rate:.6f} |\n\n"
        )
        f.write("注意：这个六维最小点包含 plant 假设，因此不能直接理解成 Isaac 控制参数。\n\n")
        f.write("## 5. 结论\n\n")
        f.write("本轮扩展扫参用于确认上一轮推荐在 plant 不确定性下是否仍稳健。")
        f.write("最终是否进入代码，仍需要 Isaac direct-target 短回放验证 flat、stairs down 和 discrete obstacles。\n\n")
        f.write("## 6. 输出文件\n\n")
        f.write("- `metrics_expanded_param_sweep_summary.csv`\n")
        f.write("- `robust_expanded_control_candidates.csv`\n")
        f.write("- `best_expanded_param_by_case.csv`\n")
        f.write("- `report_stage1_ball_joint_pd_expanded_sweep.md`\n")
        f.write(f"\n逐 case 最优记录数：`{len(case_best)}`。\n")


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.expanduser().resolve()
    trace_dir = args.trace_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    kps = parse_float_list(args.kp_range)
    kds = parse_float_list(args.kd_range)
    tau_vs = parse_float_list(args.tau_v_values)
    qdot_maxs = parse_float_list(args.qdot_max_values)
    if args.plant_mode == "fixed":
        js = np.array([float(args.fixed_j_axis)], dtype=np.float64)
        bs = np.array([float(args.fixed_b_axis)], dtype=np.float64)
        tau_loads = np.array([float(args.fixed_tau_load)], dtype=np.float64)
    else:
        js = JS
        bs = BS
        tau_loads = TAU_LOADS
    grid = build_param_grid(kps, kds, js, bs, tau_loads, tau_vs, qdot_maxs)
    cases = load_trace_cases(trace_dir, args.trace_glob)
    print(f"Loaded {len(cases)} trace cases and {len(grid)} parameter combinations.")

    metric_sums: pd.DataFrame | None = None
    metric_max: pd.DataFrame | None = None
    case_best_rows: list[pd.Series] = []

    metric_columns = [
        "old_gap_mean",
        "old_error_mean",
        "old_relative_error_mean",
        "new_error_mean",
        "rms_target_error_new",
        "new_relative_error_mean",
        "rms_relative_error_new",
        "error_reduction_ratio",
        "relative_error_reduction_ratio",
        "max_abs_qdot_new",
        "qdot_limit_rate",
        "sat_ratio",
        "max_abs_tau_new",
        "oscillation_score",
        "smoothness_cost",
        "qdot_alloc_rmse",
        "qdot_alloc_smoothness",
        "old_qdot_rms",
        "new_qdot_rms",
        "new_vs_old_qdot_ratio",
        "risk_score",
    ]
    max_columns = ["max_abs_qdot_new", "max_abs_tau_new", "risk_score"]

    for case_index, case in enumerate(cases, start=1):
        print(f"[{case_index:02d}/{len(cases)}] {case['case_name']}", flush=True)
        case_metrics = simulate_case(
            case,
            grid,
            args.relative_error_floor_rad,
            args.sat_threshold,
            args.qdot_limit_threshold,
        )
        best_index = int(case_metrics["risk_score"].idxmin())
        case_best_rows.append(case_metrics.loc[best_index].copy())
        current = case_metrics[metric_columns]
        if metric_sums is None:
            metric_sums = current.copy()
            metric_max = current[max_columns].copy()
        else:
            metric_sums += current
            assert metric_max is not None
            metric_max = pd.DataFrame(
                np.maximum(metric_max.to_numpy(), current[max_columns].to_numpy()),
                columns=max_columns,
            )

    assert metric_sums is not None
    assert metric_max is not None
    summary = grid.copy()
    summary[metric_columns] = metric_sums / len(cases)
    for column in max_columns:
        summary[column + "_case_max"] = metric_max[column]
    summary["compatibility_pass"] = (
        (summary["new_relative_error_mean"] < summary["old_relative_error_mean"])
        & (summary["sat_ratio"] < args.sat_threshold)
        & (summary["qdot_limit_rate"] < args.qdot_limit_threshold)
    )
    summary = summary.sort_values("risk_score", kind="stable").reset_index(drop=True)

    robust = (
        summary.groupby(["Kp", "Kd", "qdot_max", "tau_v"], as_index=False)
        .agg(
            risk_score_mean=("risk_score", "mean"),
            risk_score_max=("risk_score", "max"),
            risk_score_p95=("risk_score", lambda values: float(np.percentile(values, 95))),
            old_relative_error_mean_mean=("old_relative_error_mean", "mean"),
            new_relative_error_mean_mean=("new_relative_error_mean", "mean"),
            rms_relative_error_new_mean=("rms_relative_error_new", "mean"),
            new_error_mean_mean=("new_error_mean", "mean"),
            relative_error_reduction_ratio_mean=("relative_error_reduction_ratio", "mean"),
            error_reduction_ratio_mean=("error_reduction_ratio", "mean"),
            sat_ratio_mean=("sat_ratio", "mean"),
            qdot_limit_rate_mean=("qdot_limit_rate", "mean"),
            qdot_alloc_rmse_mean=("qdot_alloc_rmse", "mean"),
            qdot_alloc_smoothness_mean=("qdot_alloc_smoothness", "mean"),
            compatibility_pass_rate=("compatibility_pass", "mean"),
        )
        .sort_values(["risk_score_mean", "risk_score_max"], kind="stable")
        .reset_index(drop=True)
    )

    case_best = pd.DataFrame(case_best_rows).reset_index(drop=True)
    summary_path = output_dir / "metrics_expanded_param_sweep_summary.csv"
    robust_path = output_dir / "robust_expanded_control_candidates.csv"
    case_best_path = output_dir / "best_expanded_param_by_case.csv"
    report_path = output_dir / "report_stage1_ball_joint_pd_expanded_sweep.md"

    summary.to_csv(summary_path, index=False)
    robust.to_csv(robust_path, index=False)
    case_best.to_csv(case_best_path, index=False)
    write_report(
        report_path,
        summary,
        robust,
        summary.iloc[0],
        case_best,
        grid=grid,
        case_count=len(cases),
        trace_dir=trace_dir,
        trace_glob=args.trace_glob,
        relative_error_floor_rad=args.relative_error_floor_rad,
        plant_mode=args.plant_mode,
        sat_threshold=args.sat_threshold,
        qdot_limit_threshold=args.qdot_limit_threshold,
    )

    print("Expanded sweep complete.")
    print(f"Summary: {summary_path}")
    print(f"Robust candidates: {robust_path}")
    print(f"Case best: {case_best_path}")
    print(f"Report: {report_path}")
    top = robust.iloc[0]
    print(
        "Robust best: "
        f"Kp={top.Kp:.0f}, Kd={top.Kd:.0f}, qdot_max={top.qdot_max:.1f}, tau_v={top.tau_v:.2f}, "
        f"relative_error={top.new_relative_error_mean_mean:.6f}, "
        f"risk_mean={top.risk_score_mean:.6f}, risk_max={top.risk_score_max:.6f}"
    )


if __name__ == "__main__":
    main()
