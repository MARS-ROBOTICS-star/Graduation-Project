"""Scripted ball-joint dynamics identification in IsaacLab.

This script drives the complete car with scripted wheel and ball-joint commands,
records joint response and approximate implicit-drive torques, then fits

    tau ~= J * qddot + B * qdot + tau_load

for each ball-joint axis.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

from isaaclab.app import AppLauncher


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_SOURCE = PROJECT_ROOT / "source" / "complete_car_lab"
LOCAL_RSL_RL_SOURCE = EXTENSION_SOURCE / "complete_car_lab" / "tasks" / "direct" / "complete_car"

for path in (LOCAL_RSL_RL_SOURCE, EXTENSION_SOURCE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


TASK_CHOICES = ["CompleteCar-Stage0", "CompleteCar-Stage1", "CompleteCar-Stage2"]
BALL_JOINT_NAMES = (
    "spm1_platform_joint_z",
    "spm1_platform_joint_y",
    "spm1_platform_joint_x",
    "spm2_platform_joint_z",
    "spm2_platform_joint_y",
    "spm2_platform_joint_x",
)

parser = argparse.ArgumentParser(description="Identify approximate ball-joint J/B/load from scripted IsaacLab motion.")
parser.add_argument("--task", type=str, default="CompleteCar-Stage1", choices=TASK_CHOICES)
parser.add_argument("--agent", type=str, default="rsl_rl_cfg_entry_point")
parser.add_argument("--num_envs", type=int, default=18)
parser.add_argument("--steps", type=int, default=1800)
parser.add_argument("--warmup_steps", type=int, default=180)
parser.add_argument("--drive_action", type=float, default=0.20, help="Normalized forward action during excitation.")
parser.add_argument("--yaw_action", type=float, default=0.0, help="Normalized yaw action during excitation.")
parser.add_argument("--amplitude_rad", type=float, default=0.25, help="Target amplitude in rad for the excited joint.")
parser.add_argument("--frequency_hz", type=float, default=0.35)
parser.add_argument("--waveform", type=str, default="sine", choices=["sine", "square"])
parser.add_argument(
    "--excite_joints",
    type=str,
    default="all",
    help="Comma list of ball-joint names/indices to excite, or 'all'.",
)
parser.add_argument(
    "--terrain_replay_columns",
    type=str,
    default="flat",
    help="Stage1 generated terrain columns to use, e.g. flat or flat,stairs_down.",
)
parser.add_argument("--terrain_level", type=int, default=0)
parser.add_argument("--episode_length_s", type=float, default=120.0)
parser.add_argument("--ball_joint_stiffness", type=float, default=None)
parser.add_argument("--ball_joint_damping", type=float, default=None)
parser.add_argument("--ball_joint_effort_limit", type=float, default=None)
parser.add_argument("--ball_joint_velocity_limit", type=float, default=None)
parser.add_argument("--qdot_alloc_filter_tau", type=float, default=None)
parser.add_argument("--exclude_saturated", action="store_true", default=True)
parser.add_argument("--include_saturated", action="store_false", dest="exclude_saturated")
parser.add_argument("--saturation_ratio", type=float, default=0.98)
parser.add_argument("--min_abs_qddot", type=float, default=0.05)
parser.add_argument("--min_abs_qdot", type=float, default=0.01)
parser.add_argument(
    "--tau_v_candidates",
    type=str,
    default="0.02,0.03,0.05,0.08,0.12",
    help="Comma list of qdot_alloc LPF time constants to evaluate.",
)
parser.add_argument(
    "--out_dir",
    type=str,
    default=str(PROJECT_ROOT.parent / "results" / "stage1_ball_joint_identification"),
)
parser.add_argument("--prefix", type=str, default="scripted_drive_lift")
AppLauncher.add_app_launcher_args(parser)
args_cli, hydra_args = parser.parse_known_args()

if args_cli.device is None:
    args_cli.device = "cuda:0"
args_cli.headless = True
sys.argv = [sys.argv[0]] + hydra_args

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app


import gymnasium as gym
import numpy as np
import torch

from isaaclab.envs import DirectRLEnvCfg
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from isaaclab_tasks.utils.hydra import hydra_task_config

import isaaclab_tasks  # noqa: F401
import complete_car_lab  # noqa: F401
from complete_car_lab.tasks.direct.complete_car.mdp import actions as mdp_actions


def _normalize_selector(value: str) -> str:
    return value.strip().lower().replace("-", " ").replace("_", " ")


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "unknown"


def _parse_float_list(raw_value: str) -> list[float]:
    return [float(item.strip()) for item in raw_value.split(",") if item.strip()]


def _terrain_column_name(terrain_runtime, column: int) -> str:
    terrain_cfg = terrain_runtime._terrain_cfg
    terrain_names = list(getattr(terrain_cfg, "terrain_names", []))
    if getattr(terrain_runtime, "_terrain_type_map", None) is not None:
        terrain_idx = int(terrain_runtime._terrain_type_map[0, column].item())
    else:
        terrain_idx = column
    if 0 <= terrain_idx < len(terrain_names):
        return terrain_names[terrain_idx]
    return f"terrain_{terrain_idx}"


def _parse_stage1_replay_columns(raw_selector: str, terrain_runtime) -> list[int] | None:
    selector = _normalize_selector(raw_selector)
    if selector in {"", "all", "*", "full", "full terrain", "all terrain"}:
        return None

    terrain_cfg = terrain_runtime._terrain_cfg
    num_cols = int(terrain_cfg.num_cols)
    columns_by_name: dict[str, list[int]] = {}
    for column in range(num_cols):
        terrain_name = _terrain_column_name(terrain_runtime, column)
        columns_by_name.setdefault(_normalize_selector(terrain_name), []).append(column)
    if "uneven rough" in columns_by_name:
        columns_by_name.setdefault("rough", list(columns_by_name["uneven rough"]))

    selected_columns: list[int] = []
    for token in selector.split(","):
        token = token.strip()
        if not token:
            continue
        if token.isdigit():
            column = int(token)
            if column < 0 or column >= num_cols:
                raise ValueError(f"Stage1 terrain replay column must be in [0, {num_cols - 1}], got {column}.")
            selected_columns.append(column)
            continue
        if token not in columns_by_name:
            available = ", ".join(
                f"{column}:{_terrain_column_name(terrain_runtime, column).replace(' ', '_')}"
                for column in range(num_cols)
            )
            raise ValueError(
                f"Unknown Stage1 terrain replay selector '{token}'. "
                f"Use 'all', a column index, or one of: {available}."
            )
        selected_columns.extend(columns_by_name[token])

    unique_columns = sorted(set(selected_columns))
    if not unique_columns:
        raise ValueError("No Stage1 terrain replay columns were selected.")
    return unique_columns


def _configure_stage1_replay_terrain(raw_env, raw_selector: str, terrain_level: int) -> list[int]:
    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    if terrain_runtime is None or not getattr(terrain_runtime, "generator_enabled", False):
        return []
    if terrain_runtime.terrain_types is None or terrain_runtime.terrain_levels is None:
        raise RuntimeError("Stage1 terrain runtime has not initialized terrain levels/types.")

    selected_columns = _parse_stage1_replay_columns(raw_selector, terrain_runtime)
    num_envs = int(raw_env.num_envs)
    num_cols = int(terrain_runtime._terrain_cfg.num_cols)
    env_ids = torch.arange(num_envs, device=raw_env.device, dtype=torch.long)

    if selected_columns is None:
        if num_envs < num_cols:
            raise ValueError(
                f"Full-terrain replay needs at least {num_cols} envs, but got {num_envs}. "
                "Increase --num_envs or choose specific --terrain_replay_columns."
            )
        selected_columns = list(range(num_cols))

    selected_tensor = torch.tensor(selected_columns, device=raw_env.device, dtype=torch.long)
    terrain_runtime.terrain_types[:] = selected_tensor[torch.remainder(env_ids, selected_tensor.numel())]
    max_level = max(int(terrain_runtime.max_terrain_level) - 1, 0)
    terrain_runtime.terrain_levels[:] = int(max(0, min(terrain_level, max_level)))
    terrain_runtime.sync_env_origins(raw_env.scene)
    print(
        "[INFO] Identification terrain columns: "
        + ", ".join(f"{column}:{_terrain_column_name(terrain_runtime, column)}" for column in selected_columns),
        flush=True,
    )
    return selected_columns


def _parse_joint_selection(raw_value: str) -> list[int]:
    selector = _normalize_selector(raw_value)
    if selector in {"", "all", "*"}:
        return list(range(len(BALL_JOINT_NAMES)))

    name_to_index = {_normalize_selector(name): i for i, name in enumerate(BALL_JOINT_NAMES)}
    aliases = {
        "front yaw": 0,
        "front pitch": 1,
        "front roll": 2,
        "rear yaw": 3,
        "rear pitch": 4,
        "rear roll": 5,
        "spm1 z": 0,
        "spm1 y": 1,
        "spm1 x": 2,
        "spm2 z": 3,
        "spm2 y": 4,
        "spm2 x": 5,
    }
    selected: list[int] = []
    for token in selector.split(","):
        token = token.strip()
        if not token:
            continue
        if token.isdigit():
            index = int(token)
        elif token in aliases:
            index = aliases[token]
        elif token in name_to_index:
            index = name_to_index[token]
        else:
            raise ValueError(f"Unknown ball-joint selector '{token}'.")
        if index < 0 or index >= len(BALL_JOINT_NAMES):
            raise ValueError(f"Ball-joint index must be in [0, {len(BALL_JOINT_NAMES) - 1}], got {index}.")
        selected.append(index)
    if not selected:
        raise ValueError("No ball joints were selected for excitation.")
    return sorted(set(selected))


def _target_to_normalized_action(q_target: torch.Tensor, default: torch.Tensor, lower_limits, upper_limits) -> torch.Tensor:
    lower = q_target.new_tensor(lower_limits).unsqueeze(0)
    upper = q_target.new_tensor(upper_limits).unsqueeze(0)
    positive_span = torch.clamp(upper - default, min=1.0e-6)
    negative_span = torch.clamp(default - lower, min=1.0e-6)
    positive = (q_target - default) / positive_span
    negative = (q_target - default) / negative_span
    return torch.where(q_target >= default, positive, negative).clamp(min=-1.0, max=1.0)


def _make_scripted_actions(raw_env, selected_joint_indices: list[int], step: int, collect_step: int) -> tuple[torch.Tensor, torch.Tensor]:
    device = raw_env.device
    num_envs = raw_env.num_envs
    actions = torch.zeros((num_envs, 8), device=device)
    actions[:, 0] = float(args_cli.drive_action)
    actions[:, 1] = float(args_cli.yaw_action)

    q_default = raw_env.robot.data.default_joint_pos[:, raw_env._ball_joint_ids]
    q_target = q_default.clone()
    if collect_step >= 0:
        t = float(collect_step) * float(raw_env.step_dt)
        if args_cli.waveform == "sine":
            command_value = math.sin(2.0 * math.pi * float(args_cli.frequency_hz) * t)
        else:
            command_value = 1.0 if math.sin(2.0 * math.pi * float(args_cli.frequency_hz) * t) >= 0.0 else -1.0
        for env_id in range(num_envs):
            joint_index = selected_joint_indices[env_id % len(selected_joint_indices)]
            q_target[env_id, joint_index] = q_default[env_id, joint_index] + float(args_cli.amplitude_rad) * command_value

    q_action = _target_to_normalized_action(
        q_target,
        q_default,
        raw_env.cfg.terminations.ball_joint_pos_lower_limits,
        raw_env.cfg.terminations.ball_joint_pos_upper_limits,
    )
    actions[:, 2:] = q_action
    return actions, q_target


def _done_reason(raw_env, env_id: int) -> str:
    reasons = []
    for name, values in getattr(raw_env, "_last_done_terms", {}).items():
        try:
            if bool(values[env_id].item()):
                reasons.append(name)
        except Exception:
            continue
    return "|".join(reasons)


def _tensor_cpu(tensor: torch.Tensor) -> torch.Tensor:
    return tensor.detach().to(device="cpu")


def _build_fieldnames() -> list[str]:
    fields = [
        "step",
        "time_s",
        "env_id",
        "excited_joint_index",
        "excited_joint_name",
        "is_done",
        "done_reason",
        "terrain_col",
        "terrain_name",
        "terrain_level",
        "root_x",
        "root_y",
        "root_z",
        "vx_action",
        "yaw_action",
    ]
    for joint_name in BALL_JOINT_NAMES:
        fields.extend(
            [
                f"q_target_scripted_{joint_name}",
                f"q_position_target_old_{joint_name}",
                f"q_actual_{joint_name}",
                f"qdot_actual_{joint_name}",
                f"qddot_actual_{joint_name}",
                f"computed_torque_{joint_name}",
                f"applied_torque_{joint_name}",
                f"saturated_{joint_name}",
            ]
        )
    return fields


def _terrain_info(raw_env, env_id: int) -> tuple[int, str, int]:
    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    if terrain_runtime is None or terrain_runtime.terrain_types is None:
        return 0, "unknown", 0
    terrain_col = int(terrain_runtime.terrain_types[env_id].item())
    terrain_level = int(terrain_runtime.terrain_levels[env_id].item()) if terrain_runtime.terrain_levels is not None else 0
    terrain_name = _terrain_column_name(terrain_runtime, terrain_col)
    return terrain_col, terrain_name, terrain_level


def _collect_rows(raw_env, q_target_scripted: torch.Tensor, selected_joint_indices: list[int], collect_step: int, dones: torch.Tensor) -> list[dict[str, object]]:
    num_envs = int(raw_env.num_envs)
    time_s = float(collect_step) * float(raw_env.step_dt)
    q_target_cpu = _tensor_cpu(q_target_scripted)
    q_position_target_cpu = _tensor_cpu(raw_env._joint_pos_targets[:, raw_env._ball_joint_ids])
    q_cpu = _tensor_cpu(raw_env.robot.data.joint_pos[:, raw_env._ball_joint_ids])
    qdot_cpu = _tensor_cpu(raw_env.robot.data.joint_vel[:, raw_env._ball_joint_ids])
    qddot_cpu = _tensor_cpu(raw_env.robot.data.joint_acc[:, raw_env._ball_joint_ids])
    computed_tau_cpu = _tensor_cpu(raw_env.robot.data.computed_torque[:, raw_env._ball_joint_ids])
    applied_tau_cpu = _tensor_cpu(raw_env.robot.data.applied_torque[:, raw_env._ball_joint_ids])
    root_pos_cpu = _tensor_cpu(raw_env.robot.data.root_link_pos_w[:, :3])
    dones_cpu = _tensor_cpu(dones).to(dtype=torch.bool)
    effort_limit = float(raw_env.cfg.control.ball_joint_effort_limit_sim)

    rows: list[dict[str, object]] = []
    for env_id in range(num_envs):
        excited_joint_index = selected_joint_indices[env_id % len(selected_joint_indices)]
        terrain_col, terrain_name, terrain_level = _terrain_info(raw_env, env_id)
        row: dict[str, object] = {
            "step": collect_step,
            "time_s": time_s,
            "env_id": env_id,
            "excited_joint_index": excited_joint_index,
            "excited_joint_name": BALL_JOINT_NAMES[excited_joint_index],
            "is_done": int(dones_cpu[env_id].item()),
            "done_reason": _done_reason(raw_env, env_id) if bool(dones_cpu[env_id].item()) else "",
            "terrain_col": terrain_col,
            "terrain_name": terrain_name,
            "terrain_level": terrain_level,
            "root_x": float(root_pos_cpu[env_id, 0].item()),
            "root_y": float(root_pos_cpu[env_id, 1].item()),
            "root_z": float(root_pos_cpu[env_id, 2].item()),
            "vx_action": float(args_cli.drive_action),
            "yaw_action": float(args_cli.yaw_action),
        }
        for joint_index, joint_name in enumerate(BALL_JOINT_NAMES):
            applied_tau = float(applied_tau_cpu[env_id, joint_index].item())
            row[f"q_target_scripted_{joint_name}"] = float(q_target_cpu[env_id, joint_index].item())
            row[f"q_position_target_old_{joint_name}"] = float(q_position_target_cpu[env_id, joint_index].item())
            row[f"q_actual_{joint_name}"] = float(q_cpu[env_id, joint_index].item())
            row[f"qdot_actual_{joint_name}"] = float(qdot_cpu[env_id, joint_index].item())
            row[f"qddot_actual_{joint_name}"] = float(qddot_cpu[env_id, joint_index].item())
            row[f"computed_torque_{joint_name}"] = float(computed_tau_cpu[env_id, joint_index].item())
            row[f"applied_torque_{joint_name}"] = applied_tau
            row[f"saturated_{joint_name}"] = int(abs(applied_tau) >= float(args_cli.saturation_ratio) * effort_limit)
        rows.append(row)
    return rows


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _fit_joint(rows: list[dict[str, object]], joint_index: int) -> dict[str, float | int | str]:
    joint_name = BALL_JOINT_NAMES[joint_index]
    qdot_key = f"qdot_actual_{joint_name}"
    qddot_key = f"qddot_actual_{joint_name}"
    tau_key = f"applied_torque_{joint_name}"
    sat_key = f"saturated_{joint_name}"

    qdot = []
    qddot = []
    tau = []
    for row in rows:
        if int(row["excited_joint_index"]) != joint_index:
            continue
        if args_cli.exclude_saturated and int(row[sat_key]) != 0:
            continue
        qdot_i = float(row[qdot_key])
        qddot_i = float(row[qddot_key])
        tau_i = float(row[tau_key])
        if abs(qddot_i) < float(args_cli.min_abs_qddot) and abs(qdot_i) < float(args_cli.min_abs_qdot):
            continue
        qdot.append(qdot_i)
        qddot.append(qddot_i)
        tau.append(tau_i)

    if len(tau) < 20:
        return {
            "joint_index": joint_index,
            "joint_name": joint_name,
            "sample_count": len(tau),
            "status": "insufficient_samples",
        }

    qdot_np = np.asarray(qdot, dtype=np.float64)
    qddot_np = np.asarray(qddot, dtype=np.float64)
    tau_np = np.asarray(tau, dtype=np.float64)
    x = np.stack((qddot_np, qdot_np, np.ones_like(qdot_np)), axis=1)
    beta, residuals, rank, _singular = np.linalg.lstsq(x, tau_np, rcond=None)
    pred = x @ beta
    err = tau_np - pred
    rmse = float(np.sqrt(np.mean(err**2)))
    tau_var = float(np.var(tau_np))
    r2 = float(1.0 - np.var(err) / max(tau_var, 1.0e-12))
    return {
        "joint_index": joint_index,
        "joint_name": joint_name,
        "sample_count": int(len(tau)),
        "status": "ok",
        "J": float(beta[0]),
        "B": float(beta[1]),
        "tau_load": float(beta[2]),
        "rmse": rmse,
        "r2": r2,
        "rank": int(rank),
        "tau_abs_mean": float(np.mean(np.abs(tau_np))),
        "qdot_abs_mean": float(np.mean(np.abs(qdot_np))),
        "qddot_abs_mean": float(np.mean(np.abs(qddot_np))),
    }


def _evaluate_tau_v(rows: list[dict[str, object]], tau_v_candidates: list[float], dt: float) -> list[dict[str, float | int | str]]:
    results: list[dict[str, float | int | str]] = []
    grouped: dict[tuple[int, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["env_id"]), int(row["excited_joint_index"]))].append(row)

    for tau_v in tau_v_candidates:
        if tau_v <= 0.0:
            continue
        alpha = 1.0 - math.exp(-dt / tau_v)
        all_raw = []
        all_filtered = []
        all_error = []
        all_raw_diff = []
        all_filtered_diff = []
        for (_env_id, joint_index), group_rows in grouped.items():
            joint_name = BALL_JOINT_NAMES[joint_index]
            group_rows = sorted(group_rows, key=lambda row: int(row["step"]))
            raw = np.asarray([float(row[f"qdot_actual_{joint_name}"]) for row in group_rows], dtype=np.float64)
            if raw.size < 3:
                continue
            filtered = np.zeros_like(raw)
            filtered[0] = raw[0]
            for i in range(1, raw.size):
                filtered[i] = (1.0 - alpha) * filtered[i - 1] + alpha * raw[i]
            all_raw.append(raw)
            all_filtered.append(filtered)
            all_error.append(filtered - raw)
            all_raw_diff.append(np.diff(raw) / dt)
            all_filtered_diff.append(np.diff(filtered) / dt)

        if not all_raw:
            continue
        raw_concat = np.concatenate(all_raw)
        filtered_concat = np.concatenate(all_filtered)
        err_concat = np.concatenate(all_error)
        raw_diff_concat = np.concatenate(all_raw_diff)
        filtered_diff_concat = np.concatenate(all_filtered_diff)
        results.append(
            {
                "tau_v": float(tau_v),
                "alpha": float(alpha),
                "sample_count": int(raw_concat.size),
                "raw_qdot_abs_mean": float(np.mean(np.abs(raw_concat))),
                "filtered_qdot_abs_mean": float(np.mean(np.abs(filtered_concat))),
                "filter_error_rmse": float(np.sqrt(np.mean(err_concat**2))),
                "raw_qdot_diff_rms": float(np.sqrt(np.mean(raw_diff_concat**2))),
                "filtered_qdot_diff_rms": float(np.sqrt(np.mean(filtered_diff_concat**2))),
                "roughness_reduction_ratio": float(
                    1.0 - np.sqrt(np.mean(filtered_diff_concat**2)) / max(np.sqrt(np.mean(raw_diff_concat**2)), 1.0e-12)
                ),
            }
        )
    return results


def _write_fit_outputs(out_dir: Path, prefix: str, rows: list[dict[str, object]], selected_joint_indices: list[int], dt: float) -> None:
    fit_results = [_fit_joint(rows, joint_index) for joint_index in selected_joint_indices]
    fit_path = out_dir / f"{prefix}_fit_results.csv"
    fit_fields = [
        "joint_index",
        "joint_name",
        "sample_count",
        "status",
        "J",
        "B",
        "tau_load",
        "rmse",
        "r2",
        "rank",
        "tau_abs_mean",
        "qdot_abs_mean",
        "qddot_abs_mean",
    ]
    with fit_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fit_fields)
        writer.writeheader()
        for result in fit_results:
            writer.writerow(result)

    tau_v_results = _evaluate_tau_v(rows, _parse_float_list(args_cli.tau_v_candidates), dt)
    tau_v_path = out_dir / f"{prefix}_tau_v_metrics.csv"
    tau_v_fields = [
        "tau_v",
        "alpha",
        "sample_count",
        "raw_qdot_abs_mean",
        "filtered_qdot_abs_mean",
        "filter_error_rmse",
        "raw_qdot_diff_rms",
        "filtered_qdot_diff_rms",
        "roughness_reduction_ratio",
    ]
    with tau_v_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=tau_v_fields)
        writer.writeheader()
        for result in tau_v_results:
            writer.writerow(result)

    ok_results = [result for result in fit_results if result.get("status") == "ok"]
    summary = {
        "fit_csv": str(fit_path),
        "tau_v_csv": str(tau_v_path),
        "selected_joint_indices": selected_joint_indices,
        "selected_joint_names": [BALL_JOINT_NAMES[index] for index in selected_joint_indices],
        "equation": "applied_torque ~= J*qddot + B*qdot + tau_load",
        "note": (
            "For implicit actuators, applied_torque is IsaacLab's approximate clipped drive torque. "
            "tau_v is not fitted as a physical parameter; it is evaluated as a qdot_alloc LPF design choice."
        ),
        "fit_mean": {
            "J": float(np.mean([float(result["J"]) for result in ok_results])) if ok_results else None,
            "B": float(np.mean([float(result["B"]) for result in ok_results])) if ok_results else None,
            "tau_load": float(np.mean([float(result["tau_load"]) for result in ok_results])) if ok_results else None,
            "r2": float(np.mean([float(result["r2"]) for result in ok_results])) if ok_results else None,
        },
    }
    summary_path = out_dir / f"{prefix}_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Wrote fit results: {fit_path}", flush=True)
    print(f"[INFO] Wrote tau_v metrics: {tau_v_path}", flush=True)
    print(f"[INFO] Wrote summary: {summary_path}", flush=True)


@hydra_task_config(args_cli.task, args_cli.agent)
def main(env_cfg: DirectRLEnvCfg, agent_cfg):
    if args_cli.num_envs <= 0:
        raise ValueError("--num_envs must be positive.")
    if args_cli.steps <= 0:
        raise ValueError("--steps must be positive.")
    if args_cli.warmup_steps < 0:
        raise ValueError("--warmup_steps must be non-negative.")
    if args_cli.frequency_hz <= 0.0:
        raise ValueError("--frequency_hz must be positive.")
    if args_cli.amplitude_rad <= 0.0:
        raise ValueError("--amplitude_rad must be positive.")

    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.sim.device = args_cli.device
    env_cfg.episode_length_s = args_cli.episode_length_s
    env_cfg.rewards.params.far_from_target_margin = 1.0e6
    env_cfg.rewards.params.stuck_timeout_s = 0.0
    env_cfg.debug.enable_debug_draw = False
    env_cfg.debug.visualize_goal_position = False
    env_cfg.debug.visualize_goal_heading = False
    env_cfg.debug.visualize_wheel_slip = False
    env_cfg.debug.visualize_height_patch = False
    env_cfg.debug.create_follow_views = False
    if args_cli.ball_joint_stiffness is not None:
        env_cfg.control.ball_joint_stiffness = float(args_cli.ball_joint_stiffness)
    if args_cli.ball_joint_damping is not None:
        env_cfg.control.ball_joint_damping = float(args_cli.ball_joint_damping)
    if args_cli.ball_joint_effort_limit is not None:
        env_cfg.control.ball_joint_effort_limit_sim = float(args_cli.ball_joint_effort_limit)
    if args_cli.ball_joint_velocity_limit is not None:
        env_cfg.control.ball_joint_velocity_limit_sim = float(args_cli.ball_joint_velocity_limit)
    if args_cli.qdot_alloc_filter_tau is not None:
        env_cfg.control.ball_joint_qdot_alloc_filter_tau_s = float(args_cli.qdot_alloc_filter_tau)
    agent_cfg.device = args_cli.device

    selected_joint_indices = _parse_joint_selection(args_cli.excite_joints)
    out_dir = Path(args_cli.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_csv_path = out_dir / f"{args_cli.prefix}_raw.csv"
    fieldnames = _build_fieldnames()

    env = gym.make(args_cli.task, cfg=env_cfg)
    _configure_stage1_replay_terrain(env.unwrapped, args_cli.terrain_replay_columns, args_cli.terrain_level)
    env.reset()
    env = RslRlVecEnvWrapper(env, clip_actions=1.0)
    raw_env = env.unwrapped
    obs = env.get_observations()
    del obs

    print(
        "[INFO] Identification setup: "
        f"task={args_cli.task}, num_envs={args_cli.num_envs}, joints={selected_joint_indices}, "
        f"drive_action={args_cli.drive_action}, amplitude_rad={args_cli.amplitude_rad}, "
        f"frequency_hz={args_cli.frequency_hz}, waveform={args_cli.waveform}",
        flush=True,
    )
    print(
        "[INFO] Control params: "
        f"Kp={raw_env.cfg.control.ball_joint_stiffness}, "
        f"Kd={raw_env.cfg.control.ball_joint_damping}, "
        f"effort={raw_env.cfg.control.ball_joint_effort_limit_sim}, "
        f"vel_limit={raw_env.cfg.control.ball_joint_velocity_limit_sim}, "
        f"tau_v={raw_env.cfg.control.ball_joint_qdot_alloc_filter_tau_s}",
        flush=True,
    )

    rows: list[dict[str, object]] = []
    total_steps = int(args_cli.warmup_steps + args_cli.steps)
    with torch.inference_mode():
        for step in range(total_steps):
            collect_step = step - int(args_cli.warmup_steps)
            actions, q_target_scripted = _make_scripted_actions(raw_env, selected_joint_indices, step, collect_step)
            _obs, _reward, dones, _extras = env.step(actions)
            if collect_step >= 0:
                rows.extend(_collect_rows(raw_env, q_target_scripted, selected_joint_indices, collect_step, dones))
            if (step + 1) % 300 == 0:
                print(f"[INFO] Progress: {step + 1}/{total_steps} steps, rows={len(rows)}", flush=True)

    _write_csv(raw_csv_path, fieldnames, rows)
    print(f"[INFO] Wrote raw identification trace: {raw_csv_path}", flush=True)
    _write_fit_outputs(out_dir, args_cli.prefix, rows, selected_joint_indices, float(raw_env.step_dt))
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
