"""Select best Stage1 replays and record clean single-env follow-view videos."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHECKPOINT = (
    PROJECT_ROOT
    / "logs"
    / "rsl_rl"
    / "complete_car_stage1"
    / "2026-05-15_21-54-23_stage1_m100_model100_obs016_dr_all_96env_200iter_20260515"
    / "model_150.pt"
)
LARGE_MOUNT = Path("/media/ubuntu/4AF2C275F2C26533")
DEFAULT_EXTERNAL_ROOT = LARGE_MOUNT / "complete_car_stage1_best_env_videos"
HARD_BATCH_GROUPS = frozenset({"stairs_cols05_07", "obstacles_cols08_09"})


@dataclass(frozen=True)
class RecordSpec:
    suffix: str
    views: tuple[str, ...]
    show_height_patch: bool = False


@dataclass(frozen=True)
class TerrainGroup:
    name: str
    columns: tuple[int, ...]
    label: str
    records: tuple[RecordSpec, ...]
    seeds_per_group: int


def build_groups(hard_seeds_per_col: int, other_seeds_per_group: int) -> tuple[TerrainGroup, ...]:
    hard_records = (
        RecordSpec("no_patch", ("chase", "right_side"), show_height_patch=False),
        RecordSpec("height_patch_chase", ("chase",), show_height_patch=True),
    )
    other_records = (RecordSpec("no_patch_chase", ("chase",), show_height_patch=False),)
    return (
        TerrainGroup("stairs_cols05_07", (5, 6, 7), "stairs down cols 5-7", hard_records, 3 * hard_seeds_per_col),
        TerrainGroup("obstacles_cols08_09", (8, 9), "discrete obstacles cols 8-9", hard_records, 2 * hard_seeds_per_col),
        TerrainGroup("flat_col00", (0,), "flat col 0", other_records, other_seeds_per_group),
        TerrainGroup("slope_down_col01", (1,), "slope down col 1", other_records, other_seeds_per_group),
        TerrainGroup("slope_up_col02", (2,), "slope up col 2", other_records, other_seeds_per_group),
        TerrainGroup("rough_cols03_04", (3, 4), "uneven rough cols 3-4", other_records, other_seeds_per_group),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Single-env multi-seed best replay selection and recording.")
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--task", type=str, default="CompleteCar-Stage1")
    parser.add_argument("--device", type=str, default="cuda:0")
    parser.add_argument("--seed-start", type=int, default=42)
    parser.add_argument("--hard-seeds-per-col", type=int, default=20)
    parser.add_argument("--other-seeds-per-group", type=int, default=5)
    parser.add_argument("--selection-steps", type=int, default=72000)
    parser.add_argument("--max-pre-completion-resets", type=int, default=5)
    parser.add_argument("--completion-padding-steps", type=int, default=0)
    parser.add_argument("--video-resolution", type=str, default="2560x1440")
    parser.add_argument("--video-crf", type=int, default=18)
    parser.add_argument("--video-preset", type=str, default="slow")
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--video-output-root", type=Path, default=None)
    parser.add_argument("--record-from-summary", type=Path, default=None)
    parser.add_argument(
        "--rerank-summary-best",
        action="store_true",
        help="Before recording, reselect each group best candidate from summary candidates using the current ranking rule.",
    )
    parser.add_argument(
        "--groups",
        type=str,
        default="",
        help="Comma-separated group names to select. Empty means all groups.",
    )
    parser.add_argument("--select-only", action="store_true")
    parser.add_argument(
        "--reuse-existing-traces",
        action="store_true",
        help="Reuse completed selection trace/log pairs in output-root instead of rerunning them.",
    )
    parser.add_argument("--run", action="store_true", help="Execute commands. Without this, print the plan only.")
    return parser.parse_args()


def quote_cmd(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def default_output_root(checkpoint: Path) -> Path:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    if LARGE_MOUNT.exists():
        return DEFAULT_EXTERNAL_ROOT / checkpoint.parent.name / timestamp
    return checkpoint.parent / "best_terrain_video_records" / timestamp


def candidate_plan(group: TerrainGroup, seed_start: int) -> list[dict[str, int]]:
    candidates: list[dict[str, int]] = []
    for index in range(group.seeds_per_group):
        col = group.columns[index % len(group.columns)]
        candidates.append({"col": int(col), "seed": int(seed_start + index)})
    return candidates


def should_batch_group(group: TerrainGroup) -> bool:
    return group.name in HARD_BATCH_GROUPS and len(group.columns) > 1


def columns_arg(columns: tuple[int, ...]) -> str:
    return ",".join(str(col) for col in columns)


def columns_label(columns: tuple[int, ...]) -> str:
    return "cols" + "_".join(f"{col:02d}" for col in columns)


def base_play_cmd(
    args: argparse.Namespace,
    col: int,
    seed: int,
    *,
    num_envs: int = 1,
    replay_columns: str | None = None,
) -> list[str]:
    checkpoint = args.checkpoint.expanduser().resolve()
    return [
        sys.executable,
        "scripts/play.py",
        "--task",
        args.task,
        "--device",
        args.device,
        "--num_envs",
        str(num_envs),
        "--seed",
        str(seed),
        "--checkpoint",
        str(checkpoint),
        "--terrain_replay_columns",
        replay_columns if replay_columns is not None else str(col),
        "--headless",
    ]


def selection_cmd(
    args: argparse.Namespace,
    col: int,
    seed: int,
    trace_path: Path,
    *,
    num_envs: int = 1,
    replay_columns: str | None = None,
    completion_target: int = 1,
) -> list[str]:
    cmd = base_play_cmd(args, col, seed, num_envs=num_envs, replay_columns=replay_columns)
    cmd.extend(
        [
            "--record_reward_trace",
            "--reward_trace_output",
            str(trace_path),
            "--reward_trace_envs",
            "all",
            "--max_play_steps",
            str(args.selection_steps),
            "--stop_after_continuous_terrain_completions",
            str(completion_target),
            "--selection_max_pre_completion_resets",
            str(args.max_pre_completion_resets),
        ]
    )
    return cmd


def record_cmd(
    args: argparse.Namespace,
    spec: RecordSpec,
    col: int,
    seed: int,
    duration_steps: int,
    video_output_dir: Path,
    video_name: str,
) -> list[str]:
    cmd = base_play_cmd(args, col, seed)
    cmd.extend(
        [
            "--video",
            "--stream_video",
            "--record_chase_view",
            "--follow_view_chase_env",
            "0",
            "--video_resolution",
            args.video_resolution,
            "--video_length",
            str(duration_steps),
            "--video_output_dir",
            str(video_output_dir),
            "--video_output_name",
            video_name,
            "--video_crf",
            str(args.video_crf),
            "--video_preset",
            args.video_preset,
            "--show_goal_vis",
        ]
    )
    if len(spec.views) > 1:
        cmd.extend(["--record_camera_views", ",".join(spec.views)])
    else:
        cmd.extend(["--record_camera_view", spec.views[0]])
    if spec.show_height_patch:
        cmd.extend(["--show_height_patch_vis", "--height_patch_vis_envs", "0"])
    return cmd


def run_command(cmd: list[str], log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("TERM", "xterm")
    env.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
    env.setdefault("OMNI_KIT_ACCEPT_EULA", "YES")
    with log_path.open("w", encoding="utf-8") as log_file:
        print("$ " + quote_cmd(cmd), file=log_file, flush=True)
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            check=False,
        )
    return int(result.returncode)


def selection_log_finished(log_path: Path) -> bool:
    if not log_path.exists():
        return False
    try:
        text = log_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return "Continuous terrain-completion selection stop:" in text


def parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_candidate_trace(
    trace_path: Path,
    *,
    group_name: str,
    col: int,
    seed: int,
    env_id: int = 0,
    max_pre_completion_resets: int,
) -> dict[str, Any]:
    stats: dict[str, Any] = {
        "group": group_name,
        "col": int(col),
        "seed": int(seed),
        "env_id": int(env_id),
        "qualified_completion": False,
        "completion_step": None,
        "completion_time_s": None,
        "pre_completion_reset_count": 0,
        "steps": 0,
        "reward_sum": 0.0,
        "reward_count": 0,
        "avg_reward": 0.0,
        "max_level": -1.0,
        "max_row_progress": 0.0,
        "timeout_count": 0,
        "stuck_count": 0,
        "low_quality_count": 0,
        "far_count": 0,
        "joint_limit_count": 0,
        "roll_limit_count": 0,
        "score": None,
    }
    if not trace_path.exists():
        stats["error"] = "trace_missing"
        return stats

    with trace_path.open("r", newline="", encoding="utf-8") as trace_file:
        reader = csv.DictReader(trace_file)
        for row in reader:
            row_env_id = parse_float(row.get("env_id"))
            if row_env_id is not None and int(row_env_id) != int(env_id):
                continue
            if stats["completion_step"] is not None:
                continue
            stats["steps"] += 1
            reward = parse_float(row.get("returned_reward"))
            if reward is None:
                reward = parse_float(row.get("total_reward"))
            if reward is not None:
                stats["reward_sum"] += reward
                stats["reward_count"] += 1
            level = parse_float(row.get("terrain_level_after_step"))
            if level is not None:
                stats["max_level"] = max(stats["max_level"], level)

            row_failed = False
            row_completed = False
            for key, value in row.items():
                key_lower = key.lower()
                parsed = parse_float(value)
                if parsed is not None and "row_progress" in key_lower:
                    stats["max_row_progress"] = max(stats["max_row_progress"], parsed)
                if not key.startswith("done__") or parsed is None or parsed <= 0.5:
                    continue
                if "terrain_column_completed" in key_lower:
                    row_completed = True
                elif "timeout" in key_lower or "time_out" in key_lower:
                    row_failed = True
                    stats["timeout_count"] += 1
                elif "stuck" in key_lower:
                    row_failed = True
                    stats["stuck_count"] += 1
                elif "low_quality" in key_lower:
                    row_failed = True
                    stats["low_quality_count"] += 1
                elif "far" in key_lower:
                    row_failed = True
                    stats["far_count"] += 1
                elif "joint_limit" in key_lower or "ball_joint" in key_lower:
                    row_failed = True
                    stats["joint_limit_count"] += 1
                elif "orientation" in key_lower or "roll_limit" in key_lower:
                    row_failed = True
                    stats["roll_limit_count"] += 1

            if row_completed and not row_failed:
                stats["completion_step"] = int(float(row.get("step") or 0))
                time_s = parse_float(row.get("time_s"))
                stats["completion_time_s"] = time_s if time_s is not None else float(stats["completion_step"]) / 30.0
                break
            if row_failed:
                stats["pre_completion_reset_count"] += 1

    reward_count = max(int(stats["reward_count"]), 1)
    stats["avg_reward"] = float(stats["reward_sum"]) / reward_count
    stats["qualified_completion"] = (
        stats["completion_step"] is not None
        and stats["pre_completion_reset_count"] <= int(max_pre_completion_resets)
    )
    failure_penalty = (
        2000.0 * stats["joint_limit_count"]
        + 2000.0 * stats["roll_limit_count"]
        + 1000.0 * stats["stuck_count"]
        + 700.0 * stats["low_quality_count"]
        + 500.0 * stats["far_count"]
        + 100.0 * stats["timeout_count"]
        + 5000.0 * stats["pre_completion_reset_count"]
    )
    if stats["qualified_completion"]:
        stats["score"] = (
            10000.0 * stats["avg_reward"]
            + 1000.0 * stats["max_row_progress"]
            - 2.0 * float(stats["completion_step"])
            - failure_penalty
        )
    return stats


def load_summary(path: Path) -> dict[str, Any]:
    with path.expanduser().resolve().open("r", encoding="utf-8") as summary_file:
        return json.load(summary_file)


def save_summary(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as summary_file:
        json.dump(payload, summary_file, indent=2, ensure_ascii=False)
        summary_file.write("\n")


def selected_group_names(groups: tuple[TerrainGroup, ...], value: str) -> set[str]:
    if not value:
        return {group.name for group in groups}
    available = {group.name for group in groups}
    selected = {item.strip() for item in value.split(",") if item.strip()}
    unknown = selected - available
    if unknown:
        raise ValueError(f"Unknown group name(s): {', '.join(sorted(unknown))}")
    if not selected:
        raise ValueError("--groups was provided but no valid group names were found.")
    return selected


def best_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    qualified = [candidate for candidate in candidates if candidate.get("qualified_completion")]
    if not qualified:
        raise RuntimeError("No candidate completed the highest row within the reset budget.")
    qualified.sort(
        key=lambda item: (
            -float(item.get("pre_completion_reset_count") or 0),
            float(item.get("score") or -1.0e30),
            -float(item.get("completion_step") or 1.0e30),
        ),
        reverse=True,
    )
    return qualified[0]


def rerank_summary_best(summary: dict[str, Any]) -> None:
    groups_payload = summary.get("groups", {})
    if not isinstance(groups_payload, dict):
        raise ValueError("Summary has no valid groups mapping.")
    for group_name, group_payload in groups_payload.items():
        if not isinstance(group_payload, dict):
            continue
        candidates = group_payload.get("candidates", [])
        if not candidates:
            continue
        group_payload["best"] = best_candidate(candidates)
        group_payload["best_selection_rule"] = (
            "qualified completion, then fewest pre-completion resets, then score, then faster completion"
        )


def main() -> None:
    args = parse_args()
    checkpoint = args.checkpoint.expanduser().resolve()
    if not checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint}")
    if args.selection_steps <= 0:
        raise ValueError("--selection-steps must be positive.")
    if args.hard_seeds_per_col <= 0 or args.other_seeds_per_group <= 0:
        raise ValueError("Seed counts must be positive.")
    if args.max_pre_completion_resets < 0 or args.completion_padding_steps < 0:
        raise ValueError("Reset budget and completion padding must be non-negative.")

    output_root = args.output_root.expanduser().resolve() if args.output_root else default_output_root(checkpoint)
    video_output_root = (
        args.video_output_root.expanduser().resolve()
        if args.video_output_root
        else output_root / "videos"
    )
    trace_dir = output_root / "reward_traces"
    command_log_dir = output_root / "command_logs"
    groups = build_groups(args.hard_seeds_per_col, args.other_seeds_per_group)
    group_names_to_select = selected_group_names(groups, args.groups)
    summary_path = output_root / "selected_envs.json"

    if args.record_from_summary is not None:
        summary = load_summary(args.record_from_summary)
        if args.rerank_summary_best:
            rerank_summary_best(summary)
            if args.run:
                save_summary(args.record_from_summary.expanduser().resolve(), summary)
    else:
        if args.run and summary_path.exists():
            summary = load_summary(summary_path)
            summary.setdefault("groups", {})
        else:
            summary = {
                "created_at": time.strftime("%Y%m%d_%H%M%S"),
                "checkpoint": str(checkpoint),
                "task": args.task,
                "selection_mode": "hard_grouped_envs_by_seed_then_single_env_record",
                "selection_steps": args.selection_steps,
                "max_pre_completion_resets": args.max_pre_completion_resets,
                "completion_padding_steps": args.completion_padding_steps,
                "hard_seeds_per_col": args.hard_seeds_per_col,
                "other_seeds_per_group": args.other_seeds_per_group,
                "output_root": str(output_root),
                "video_output_root": str(video_output_root),
                "groups": {},
                "selection_runs": [],
            }
        summary.setdefault("selection_runs", [])
        for group in groups:
            if group.name not in group_names_to_select:
                continue
            print(f"\n[SELECT_GROUP] {group.label}")
            candidates: list[dict[str, Any]] = []
            if should_batch_group(group):
                replay_columns = columns_arg(group.columns)
                batch_label = columns_label(group.columns)
                num_envs = len(group.columns)
                for index in range(args.hard_seeds_per_col):
                    seed = args.seed_start + index
                    trace_path = trace_dir / group.name / f"{batch_label}_seed{seed}_trace.csv"
                    log_path = command_log_dir / group.name / f"{batch_label}_seed{seed}_select.log"
                    cmd = selection_cmd(
                        args,
                        group.columns[0],
                        seed,
                        trace_path,
                        num_envs=num_envs,
                        replay_columns=replay_columns,
                        completion_target=num_envs,
                    )
                    print(f"[SELECT_BATCH] {group.name} columns={replay_columns} seed={seed} num_envs={num_envs}")
                    print(f"cd {PROJECT_ROOT}")
                    print(quote_cmd(cmd))
                    if not args.run:
                        continue
                    if args.reuse_existing_traces and trace_path.exists() and selection_log_finished(log_path):
                        print(f"[REUSE] {group.name} columns={replay_columns} seed={seed}")
                        return_code = 0
                    else:
                        return_code = run_command(cmd, log_path)
                    for env_id, col in enumerate(group.columns):
                        stats = parse_candidate_trace(
                            trace_path,
                            group_name=group.name,
                            col=col,
                            seed=seed,
                            env_id=env_id,
                            max_pre_completion_resets=args.max_pre_completion_resets,
                        )
                        stats["return_code"] = return_code
                        stats["batch_columns"] = list(group.columns)
                        stats["batch_num_envs"] = num_envs
                        stats["trace_path"] = str(trace_path)
                        candidates.append(stats)
                        if stats.get("qualified_completion"):
                            print(
                                "[CANDIDATE] "
                                f"{group.name} env={env_id} col={col} seed={seed} "
                                f"step={stats['completion_step']} time={stats['completion_time_s']:.2f}s "
                                f"resets={stats['pre_completion_reset_count']} score={stats['score']:.2f}"
                            )
                        else:
                            print(
                                "[MISS] "
                                f"{group.name} env={env_id} col={col} seed={seed} "
                                f"resets={stats['pre_completion_reset_count']} max_level={stats['max_level']}"
                            )
            else:
                for candidate in candidate_plan(group, args.seed_start):
                    col = candidate["col"]
                    seed = candidate["seed"]
                    trace_path = trace_dir / group.name / f"col{col:02d}_seed{seed}_trace.csv"
                    log_path = command_log_dir / group.name / f"col{col:02d}_seed{seed}_select.log"
                    cmd = selection_cmd(args, col, seed, trace_path)
                    print(f"[SELECT] {group.name} col={col} seed={seed}")
                    print(f"cd {PROJECT_ROOT}")
                    print(quote_cmd(cmd))
                    if args.run:
                        if args.reuse_existing_traces and trace_path.exists() and selection_log_finished(log_path):
                            print(f"[REUSE] {group.name} col={col} seed={seed}")
                            return_code = 0
                        else:
                            return_code = run_command(cmd, log_path)
                        stats = parse_candidate_trace(
                            trace_path,
                            group_name=group.name,
                            col=col,
                            seed=seed,
                            max_pre_completion_resets=args.max_pre_completion_resets,
                        )
                        stats["return_code"] = return_code
                        stats["trace_path"] = str(trace_path)
                        candidates.append(stats)
                        if stats.get("qualified_completion"):
                            print(
                                "[CANDIDATE] "
                                f"{group.name} col={col} seed={seed} "
                                f"step={stats['completion_step']} time={stats['completion_time_s']:.2f}s "
                                f"resets={stats['pre_completion_reset_count']} score={stats['score']:.2f}"
                            )
                        else:
                            print(
                                "[MISS] "
                                f"{group.name} col={col} seed={seed} "
                                f"resets={stats['pre_completion_reset_count']} max_level={stats['max_level']}"
                            )
            if args.run:
                best = best_candidate(candidates)
                previous_candidates = summary.get("groups", {}).get(group.name, {}).get("candidates", [])
                merged_candidates = [*previous_candidates, *candidates]
                summary["groups"][group.name] = {
                    "label": group.label,
                    "columns": list(group.columns),
                    "records": [
                        {
                            "suffix": record.suffix,
                            "views": list(record.views),
                            "show_height_patch": record.show_height_patch,
                        }
                        for record in group.records
                    ],
                    "best": best,
                    "candidates": merged_candidates,
                }
                summary["selection_runs"].append(
                    {
                        "created_at": time.strftime("%Y%m%d_%H%M%S"),
                        "groups": [group.name],
                        "seed_start": args.seed_start,
                        "hard_seeds_per_col": args.hard_seeds_per_col,
                        "other_seeds_per_group": args.other_seeds_per_group,
                        "selection_steps": args.selection_steps,
                        "max_pre_completion_resets": args.max_pre_completion_resets,
                        "hard_batch_by_seed": should_batch_group(group),
                        "batched_env_columns": list(group.columns) if should_batch_group(group) else [],
                    }
                )
                print(
                    "[BEST] "
                    f"{group.name}: col={best['col']} seed={best['seed']} "
                    f"step={best['completion_step']} time={best['completion_time_s']:.2f}s "
                    f"resets={best['pre_completion_reset_count']} score={best['score']:.2f}"
                )
            else:
                summary["groups"][group.name] = {
                    "label": group.label,
                    "columns": list(group.columns),
                    "note": "Run with --run to execute candidate selection.",
                }
        if args.run:
            save_summary(summary_path, summary)
            print(f"\n[INFO] Selection summary: {summary_path}")
        else:
            return

    if args.select_only:
        return

    for group in groups:
        group_summary = summary.get("groups", {}).get(group.name)
        if not group_summary or "best" not in group_summary:
            raise RuntimeError(f"Missing selected best candidate for group: {group.name}")
        best = group_summary["best"]
        duration_steps = int(best["completion_step"]) + int(args.completion_padding_steps)
        duration_steps = max(duration_steps, 1)
        col = int(best["col"])
        seed = int(best["seed"])
        records = group.records
        video_group_dir = video_output_root / group.name
        for spec in records:
            view_part = "_".join(spec.views)
            video_name = (
                f"{group.name}_col{col:02d}_seed{seed}_"
                f"{duration_steps}step_{spec.suffix}_{view_part}.mp4"
            )
            cmd = record_cmd(args, spec, col, seed, duration_steps, video_group_dir, video_name)
            log_path = command_log_dir / group.name / f"{spec.suffix}_{view_part}_record.log"
            print(
                f"\n[RECORD] {group.label}: col={col} seed={seed} "
                f"duration_steps={duration_steps} views={','.join(spec.views)}"
            )
            print(f"cd {PROJECT_ROOT}")
            print(quote_cmd(cmd))
            if args.run:
                return_code = run_command(cmd, log_path)
                if return_code != 0:
                    raise RuntimeError(f"Recording failed for {group.name} {spec.suffix}. See {log_path}")

    if args.run:
        print(f"\n[INFO] Finished. Outputs are under: {output_root}")
        print(f"[INFO] Videos are under: {video_output_root}")


if __name__ == "__main__":
    main()
