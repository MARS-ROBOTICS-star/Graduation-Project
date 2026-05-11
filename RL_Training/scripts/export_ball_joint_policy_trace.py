"""Export per-control-step ball-joint traces from a checkpoint replay."""

from __future__ import annotations

import argparse
import csv
import json
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

parser = argparse.ArgumentParser(description="Export ball-joint policy traces for MATLAB PD tuning.")
parser.add_argument("--task", type=str, default="CompleteCar-Stage1", choices=TASK_CHOICES)
parser.add_argument("--agent", type=str, default="rsl_rl_cfg_entry_point")
parser.add_argument("--checkpoint", type=str, required=True)
parser.add_argument("--num_envs", type=int, default=18)
parser.add_argument("--steps", type=int, default=1200)
parser.add_argument("--warmup_steps", type=int, default=120)
parser.add_argument(
    "--terrain_replay_columns",
    type=str,
    default="flat,stairs_down,discrete_obstacles",
    help=(
        "Stage1 terrain columns to replay: 'all', column indices such as '5,6,7', "
        "or terrain names such as 'flat,stairs_down,discrete_obstacles'."
    ),
)
parser.add_argument(
    "--terrain_level",
    type=int,
    default=None,
    help="Force all selected envs to this Stage1 terrain row/level before replay.",
)
parser.add_argument(
    "--terrain_level_by_name",
    type=str,
    default="flat=0,stairs_down=11,discrete_obstacles=11",
    help=(
        "Optional per-terrain level overrides, for example "
        "'flat=0,stairs_down=11,discrete_obstacles=11'. Use an empty string to disable."
    ),
)
parser.add_argument("--replay_episode_length_s", type=float, default=120.0)
parser.add_argument(
    "--out_dir",
    type=str,
    default=str(PROJECT_ROOT.parent / "results" / "stage1_ball_joint_pd_matlab" / "raw_traces"),
)
parser.add_argument("--prefix", type=str, default="sec14_model699")
parser.add_argument("--no_split_by_terrain", action="store_true", default=False)
parser.add_argument("--include_done_rows", action="store_true", default=False)
AppLauncher.add_app_launcher_args(parser)
args_cli, hydra_args = parser.parse_known_args()

if args_cli.device is None:
    args_cli.device = "cuda:0"
args_cli.headless = True
sys.argv = [sys.argv[0]] + hydra_args

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app


import gymnasium as gym
from packaging import version
from packaging.version import InvalidVersion
import torch
import rsl_rl
from rsl_rl.runners import OnPolicyRunner

from isaaclab.envs import DirectRLEnvCfg
from isaaclab.utils.assets import retrieve_file_path
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils.hydra import hydra_task_config

import complete_car_lab  # noqa: F401
from complete_car_lab.tasks.direct.complete_car.mdp import actions as mdp_actions


def _normalize_selector(value: str) -> str:
    return value.strip().lower().replace("-", " ").replace("_", " ")


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "unknown"


def _parse_rsl_rl_version(version_str: str):
    try:
        return version.parse(version_str)
    except InvalidVersion:
        return version.parse(version_str.replace("-local", "+local"))


def _validate_checkpoint_file(path: str) -> str:
    resolved_path = os.path.abspath(os.path.expanduser(path))
    if os.path.isdir(resolved_path):
        raise IsADirectoryError(f"Checkpoint must be a .pt file, got directory: {resolved_path}")
    if not os.path.isfile(resolved_path):
        raise FileNotFoundError(f"Checkpoint file does not exist: {resolved_path}")
    return resolved_path


def _resolve_explicit_checkpoint_path(checkpoint: str) -> str:
    local_path = Path(checkpoint).expanduser()
    if local_path.is_file():
        return str(local_path.resolve())
    return _validate_checkpoint_file(retrieve_file_path(checkpoint))


def _playback_load_cfg_for_checkpoint(checkpoint_path: str) -> dict[str, bool] | None:
    checkpoint = torch.load(checkpoint_path, weights_only=False, map_location="cpu")
    has_actor_critic = "actor_state_dict" in checkpoint and "critic_state_dict" in checkpoint
    if has_actor_critic and "optimizer_state_dict" not in checkpoint:
        return {"actor": True, "critic": True, "optimizer": False, "iteration": False, "rnd": False}
    return None


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


def _terrain_name_for_env(terrain_runtime, env_id: int) -> str:
    if terrain_runtime.terrain_types is None:
        return "unknown"
    column = int(terrain_runtime.terrain_types[env_id].item())
    return _terrain_column_name(terrain_runtime, column)


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


def _format_stage1_replay_columns(columns: list[int], terrain_runtime) -> str:
    return ", ".join(f"{column}:{_terrain_column_name(terrain_runtime, column)}" for column in columns)


def _parse_level_by_name(raw_value: str) -> dict[str, int]:
    result: dict[str, int] = {}
    if not raw_value.strip():
        return result
    for item in raw_value.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"Invalid --terrain_level_by_name item '{item}'. Expected name=level.")
        name, level_raw = item.split("=", 1)
        result[_normalize_selector(name)] = int(level_raw)
    return result


def _configure_stage1_replay_terrain(raw_env, raw_selector: str, level: int | None, level_by_name: dict[str, int]) -> list[int]:
    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    if terrain_runtime is None or not getattr(terrain_runtime, "generator_enabled", False):
        raise RuntimeError("This exporter expects generated Stage1 terrain.")
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
    if level is not None:
        terrain_runtime.terrain_levels[:] = int(max(0, min(level, max_level)))
    elif level_by_name:
        for env_id in range(num_envs):
            terrain_name = _terrain_name_for_env(terrain_runtime, env_id)
            normalized = _normalize_selector(terrain_name)
            if normalized in level_by_name:
                terrain_runtime.terrain_levels[env_id] = int(max(0, min(level_by_name[normalized], max_level)))

    terrain_runtime.sync_env_origins(raw_env.scene)
    print(
        "[INFO] Stage1 trace terrain columns: "
        f"{_format_stage1_replay_columns(selected_columns, terrain_runtime)}.",
        flush=True,
    )
    level_info = ", ".join(
        f"env{env_id}:{_terrain_name_for_env(terrain_runtime, env_id).replace(' ', '_')}"
        f"/col{int(terrain_runtime.terrain_types[env_id].item())}"
        f"/row{int(terrain_runtime.terrain_levels[env_id].item())}"
        for env_id in range(num_envs)
    )
    print(f"[INFO] Initial env terrain assignment: {level_info}", flush=True)
    return selected_columns


def _configure_replay_terrain(raw_env, raw_selector: str, level: int | None, level_by_name: dict[str, int]) -> list[int]:
    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    if terrain_runtime is None or not getattr(terrain_runtime, "generator_enabled", False):
        print("[INFO] Generated terrain runtime is not active; exporting default environment replay.", flush=True)
        return []
    return _configure_stage1_replay_terrain(raw_env, raw_selector, level, level_by_name)


def _build_fieldnames() -> list[str]:
    fields = [
        "step",
        "time_s",
        "env_id",
        "episode_index",
        "is_done",
        "done_reason",
        "terrain_col",
        "terrain_name",
        "terrain_level",
        "row_progress",
        "root_x",
        "root_y",
        "root_z",
        "vx_cmd_raw",
        "yaw_rate_cmd_raw",
        "vx_cmd_limited",
        "yaw_rate_cmd_limited",
        "wheel_speed_reference_abs_mean",
        "wheel_torque_target_abs_mean",
        "contact_weight_mean",
        "rolling_speed_actual_mean",
        "lateral_speed_actual_abs_mean",
    ]
    for action_idx in range(8):
        fields.append(f"action_{action_idx}")
    for joint_name in BALL_JOINT_NAMES:
        fields.extend(
            [
                f"q_desired_{joint_name}",
                f"q_position_target_{joint_name}",
                f"q_actual_{joint_name}",
                f"qdot_actual_{joint_name}",
                f"qdot_alloc_{joint_name}",
                f"q_desired_minus_position_target_{joint_name}",
                f"q_desired_minus_actual_{joint_name}",
                f"q_position_target_minus_actual_{joint_name}",
            ]
        )
    return fields


def _done_reason(raw_env, env_id: int) -> str:
    reasons = []
    for name, values in getattr(raw_env, "_last_done_terms", {}).items():
        try:
            if bool(values[env_id].item()):
                reasons.append(name)
        except Exception:
            continue
    return "|".join(reasons)


def _tensor_to_cpu(tensor: torch.Tensor) -> torch.Tensor:
    return tensor.detach().to(device="cpu")


def _collect_rows(raw_env, actions: torch.Tensor, step: int, episode_indices: torch.Tensor, dones: torch.Tensor) -> list[dict[str, object]]:
    terrain_runtime = getattr(raw_env, "_terrain_runtime", None)
    num_envs = int(raw_env.num_envs)
    time_s = float(step) * float(getattr(raw_env, "step_dt", raw_env.cfg.control.control_dt))

    actions_cpu = _tensor_to_cpu(actions)
    root_pos_cpu = _tensor_to_cpu(raw_env.robot.data.root_link_pos_w[:, :3])
    desired_cpu = _tensor_to_cpu(raw_env._last_ball_joint_desired_targets)
    position_target_cpu = _tensor_to_cpu(raw_env._joint_pos_targets[:, raw_env._ball_joint_ids])
    actual_pos_cpu = _tensor_to_cpu(raw_env.robot.data.joint_pos[:, raw_env._ball_joint_ids])
    actual_vel_cpu = _tensor_to_cpu(raw_env.robot.data.joint_vel[:, raw_env._ball_joint_ids])
    qdot_alloc_cpu = _tensor_to_cpu(raw_env._last_ball_joint_rate_targets)
    planar_cmd_cpu = _tensor_to_cpu(raw_env._last_desired_planar_command)
    wheel_ref_abs_cpu = _tensor_to_cpu(torch.mean(torch.abs(raw_env._last_wheel_speed_reference), dim=1))
    wheel_tau_abs_cpu = _tensor_to_cpu(torch.mean(torch.abs(raw_env._last_wheel_torque_targets), dim=1))
    contact_mean_cpu = _tensor_to_cpu(torch.mean(raw_env._last_contact_weights, dim=1))
    rolling_mean_cpu = _tensor_to_cpu(torch.mean(raw_env._last_wheel_v_parallel, dim=1))
    lateral_abs_cpu = _tensor_to_cpu(torch.mean(torch.abs(raw_env._last_wheel_v_perp), dim=1))
    dones_cpu = _tensor_to_cpu(dones).to(dtype=torch.bool)
    episode_cpu = _tensor_to_cpu(episode_indices)

    if terrain_runtime is not None and terrain_runtime.terrain_types is not None:
        terrain_cols_cpu = _tensor_to_cpu(terrain_runtime.terrain_types)
    else:
        terrain_cols_cpu = torch.zeros(num_envs, dtype=torch.long)
    if terrain_runtime is not None and terrain_runtime.terrain_levels is not None:
        terrain_levels_cpu = _tensor_to_cpu(terrain_runtime.terrain_levels)
    else:
        terrain_levels_cpu = torch.zeros(num_envs, dtype=torch.long)

    try:
        row_progress_cpu = _tensor_to_cpu(raw_env._compute_active_goal_progress())
    except Exception:
        row_progress_cpu = torch.zeros(num_envs)

    base_raw = mdp_actions.map_base_actions_to_planar_command(
        actions[:, :2],
        raw_env.cfg.control.base_forward_velocity_max,
        raw_env.cfg.control.base_yaw_rate_max,
        allow_reverse=raw_env.cfg.control.base_allow_reverse,
    )
    base_raw_cpu = _tensor_to_cpu(base_raw)

    rows: list[dict[str, object]] = []
    for env_id in range(num_envs):
        terrain_name = _terrain_name_for_env(terrain_runtime, env_id) if terrain_runtime is not None else "unknown"
        row: dict[str, object] = {
            "step": step,
            "time_s": time_s,
            "env_id": env_id,
            "episode_index": int(episode_cpu[env_id].item()),
            "is_done": int(dones_cpu[env_id].item()),
            "done_reason": _done_reason(raw_env, env_id) if bool(dones_cpu[env_id].item()) else "",
            "terrain_col": int(terrain_cols_cpu[env_id].item()),
            "terrain_name": terrain_name,
            "terrain_level": int(terrain_levels_cpu[env_id].item()),
            "row_progress": float(row_progress_cpu[env_id].item()),
            "root_x": float(root_pos_cpu[env_id, 0].item()),
            "root_y": float(root_pos_cpu[env_id, 1].item()),
            "root_z": float(root_pos_cpu[env_id, 2].item()),
            "vx_cmd_raw": float(base_raw_cpu[env_id, 0].item()),
            "yaw_rate_cmd_raw": float(base_raw_cpu[env_id, 1].item()),
            "vx_cmd_limited": float(planar_cmd_cpu[env_id, 0].item()),
            "yaw_rate_cmd_limited": float(planar_cmd_cpu[env_id, 1].item()),
            "wheel_speed_reference_abs_mean": float(wheel_ref_abs_cpu[env_id].item()),
            "wheel_torque_target_abs_mean": float(wheel_tau_abs_cpu[env_id].item()),
            "contact_weight_mean": float(contact_mean_cpu[env_id].item()),
            "rolling_speed_actual_mean": float(rolling_mean_cpu[env_id].item()),
            "lateral_speed_actual_abs_mean": float(lateral_abs_cpu[env_id].item()),
        }
        for action_idx in range(actions_cpu.shape[1]):
            row[f"action_{action_idx}"] = float(actions_cpu[env_id, action_idx].item())
        for joint_index, joint_name in enumerate(BALL_JOINT_NAMES):
            q_desired = float(desired_cpu[env_id, joint_index].item())
            q_position_target = float(position_target_cpu[env_id, joint_index].item())
            q_actual = float(actual_pos_cpu[env_id, joint_index].item())
            row[f"q_desired_{joint_name}"] = q_desired
            row[f"q_position_target_{joint_name}"] = q_position_target
            row[f"q_actual_{joint_name}"] = q_actual
            row[f"qdot_actual_{joint_name}"] = float(actual_vel_cpu[env_id, joint_index].item())
            row[f"qdot_alloc_{joint_name}"] = float(qdot_alloc_cpu[env_id, joint_index].item())
            row[f"q_desired_minus_position_target_{joint_name}"] = q_desired - q_position_target
            row[f"q_desired_minus_actual_{joint_name}"] = q_desired - q_actual
            row[f"q_position_target_minus_actual_{joint_name}"] = q_position_target - q_actual
        rows.append(row)
    return rows


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _summarize_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    by_terrain: dict[str, int] = defaultdict(int)
    by_col: dict[str, int] = defaultdict(int)
    done_count = 0
    for row in rows:
        by_terrain[str(row["terrain_name"])] += 1
        by_col[f"col{row['terrain_col']}_{_slug(str(row['terrain_name']))}"] += 1
        done_count += int(row["is_done"])
    return {
        "rows": len(rows),
        "done_rows": done_count,
        "terrain_counts": dict(sorted(by_terrain.items())),
        "column_counts": dict(sorted(by_col.items())),
    }


@hydra_task_config(args_cli.task, args_cli.agent)
def main(env_cfg: DirectRLEnvCfg, agent_cfg):
    if args_cli.num_envs <= 0:
        raise ValueError("--num_envs must be positive.")
    if args_cli.steps <= 0:
        raise ValueError("--steps must be positive.")
    if args_cli.warmup_steps < 0:
        raise ValueError("--warmup_steps must be non-negative.")
    if args_cli.replay_episode_length_s <= 0.0:
        raise ValueError("--replay_episode_length_s must be positive.")

    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.sim.device = args_cli.device
    env_cfg.episode_length_s = args_cli.replay_episode_length_s
    env_cfg.debug.enable_debug_draw = False
    env_cfg.debug.visualize_goal_position = False
    env_cfg.debug.visualize_goal_heading = False
    env_cfg.debug.visualize_wheel_slip = False
    env_cfg.debug.visualize_height_patch = False
    env_cfg.debug.create_follow_views = False
    agent_cfg.device = args_cli.device

    resume_path = _resolve_explicit_checkpoint_path(args_cli.checkpoint)
    print(f"[INFO] Loading checkpoint: {resume_path}", flush=True)

    env = gym.make(args_cli.task, cfg=env_cfg)
    selected_columns = _configure_replay_terrain(
        env.unwrapped,
        args_cli.terrain_replay_columns,
        args_cli.terrain_level,
        _parse_level_by_name(args_cli.terrain_level_by_name),
    )
    env.reset()

    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    playback_load_cfg = _playback_load_cfg_for_checkpoint(resume_path)
    if playback_load_cfg is not None:
        runner.load(resume_path, load_cfg=playback_load_cfg)
    else:
        runner.load(resume_path)
    policy = runner.get_inference_policy(device=env.unwrapped.device)

    installed_version = getattr(rsl_rl, "__version__", "0.0.0")
    parsed_rsl_rl_version = _parse_rsl_rl_version(installed_version)
    policy_nn = runner.alg.policy if parsed_rsl_rl_version < version.parse("4.0.0") else None

    obs = env.get_observations()
    rows: list[dict[str, object]] = []
    episode_indices = torch.zeros(env.unwrapped.num_envs, dtype=torch.long, device=env.unwrapped.device)
    fieldnames = _build_fieldnames()
    total_steps = args_cli.warmup_steps + args_cli.steps
    with torch.inference_mode():
        for step in range(total_steps):
            actions = policy(obs)
            obs, _, dones, _ = env.step(actions)
            if parsed_rsl_rl_version >= version.parse("4.0.0"):
                policy.reset(dones)
            elif policy_nn is not None:
                policy_nn.reset(dones)

            if step >= args_cli.warmup_steps:
                collected_step = step - args_cli.warmup_steps
                step_rows = _collect_rows(env.unwrapped, actions, collected_step, episode_indices, dones)
                if not args_cli.include_done_rows:
                    step_rows = [row for row in step_rows if int(row["is_done"]) == 0]
                rows.extend(step_rows)

            episode_indices += dones.to(dtype=torch.long)
            if (step + 1) % 300 == 0:
                print(f"[INFO] Replay progress: {step + 1}/{total_steps} steps, exported rows={len(rows)}", flush=True)

    out_dir = Path(args_cli.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    combined_path = out_dir / f"{args_cli.prefix}_combined.csv"
    _write_csv(combined_path, fieldnames, rows)
    print(f"[INFO] Wrote combined trace: {combined_path}", flush=True)

    split_paths: dict[str, str] = {}
    if not args_cli.no_split_by_terrain:
        grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in rows:
            key = f"col{int(row['terrain_col']):02d}_{_slug(str(row['terrain_name']))}"
            grouped[key].append(row)
        for key, group_rows in sorted(grouped.items()):
            path = out_dir / f"{args_cli.prefix}_{key}.csv"
            _write_csv(path, fieldnames, group_rows)
            split_paths[key] = str(path)
            print(f"[INFO] Wrote split trace: {path} ({len(group_rows)} rows)", flush=True)

    summary = {
        "checkpoint": resume_path,
        "task": args_cli.task,
        "num_envs": args_cli.num_envs,
        "warmup_steps": args_cli.warmup_steps,
        "export_steps": args_cli.steps,
        "terrain_replay_columns": args_cli.terrain_replay_columns,
        "selected_columns": selected_columns,
        "terrain_level": args_cli.terrain_level,
        "terrain_level_by_name": args_cli.terrain_level_by_name,
        "combined_csv": str(combined_path),
        "split_csv": split_paths,
        "summary": _summarize_rows(rows),
        "ball_joint_names": list(BALL_JOINT_NAMES),
    }
    summary_path = out_dir / f"{args_cli.prefix}_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Wrote summary: {summary_path}", flush=True)
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
