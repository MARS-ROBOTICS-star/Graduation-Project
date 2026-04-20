#!/usr/bin/env python3

"""Export TensorBoard scalar data from an RSL-RL run into local files."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import defaultdict
from math import isfinite
from statistics import mean
from pathlib import Path

from tensorboard.compat.proto.event_pb2 import Event
from tensorboard.compat.proto.summary_pb2 import Summary
from tensorboard.backend.event_processing import event_accumulator
from tensorboard.summary.writer.event_file_writer import EventFileWriter


def _sanitize_tag(tag: str) -> str:
    return tag.replace("/", "__")


def _tag_group(tag: str) -> str:
    return tag.split("/", 1)[0] if "/" in tag else "ungrouped"


def _find_event_file(run_dir: Path) -> Path:
    event_files = sorted(run_dir.glob("events.out.tfevents.*"))
    if not event_files:
        raise FileNotFoundError(f"No TensorBoard event file found under: {run_dir}")
    return event_files[-1]


def _series_is_all_zero(events: list) -> bool:
    if not events:
        return False
    values = [float(event.value) for event in events]
    return all(isfinite(value) and abs(value) <= 1.0e-12 for value in values)


def find_sparse_zero_scalar_tags(run_dir: str | Path) -> list[str]:
    """Return TensorBoard scalar tags that stayed zero for the whole run and should be hidden."""
    run_dir = Path(run_dir).resolve()
    accumulator = event_accumulator.EventAccumulator(str(_find_event_file(run_dir)))
    accumulator.Reload()

    pruned_tags: list[str] = []
    for tag in accumulator.Tags().get("scalars", []):
        events = accumulator.Scalars(tag)
        if _series_is_all_zero(events):
            pruned_tags.append(tag)
    return sorted(pruned_tags)


def prune_sparse_zero_scalar_tags(run_dir: str | Path) -> tuple[Path, list[str]]:
    """Rewrite the run event file after removing selected all-zero scalar series."""
    run_dir = Path(run_dir).resolve()
    event_file = _find_event_file(run_dir)
    accumulator = event_accumulator.EventAccumulator(str(event_file))
    accumulator.Reload()

    pruned_tags = find_sparse_zero_scalar_tags(run_dir)
    if not pruned_tags:
        return event_file, []

    backup_dir = run_dir / "tensorboard_export" / "original_events"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / event_file.name
    if backup_path.exists():
        backup_path.unlink()
    shutil.move(str(event_file), str(backup_path))

    writer = EventFileWriter(str(run_dir))
    try:
        for tag in accumulator.Tags().get("scalars", []):
            if tag in pruned_tags:
                continue
            for scalar_event in accumulator.Scalars(tag):
                writer.add_event(
                    Event(
                        wall_time=scalar_event.wall_time,
                        step=scalar_event.step,
                        summary=Summary(
                            value=[Summary.Value(tag=tag, simple_value=float(scalar_event.value))]
                        ),
                    )
                )
        writer.flush()
    finally:
        writer.close()

    return _find_event_file(run_dir), pruned_tags


def export_run_scalars(run_dir: str | Path) -> Path:
    """Export all scalar tags for one run directory.

    Returns the export directory path.
    """
    run_dir = Path(run_dir).resolve()
    event_file = _find_event_file(run_dir)

    accumulator = event_accumulator.EventAccumulator(str(event_file))
    accumulator.Reload()

    export_dir = run_dir / "tensorboard_export"
    scalars_dir = export_dir / "scalars"
    export_dir.mkdir(parents=True, exist_ok=True)
    scalars_dir.mkdir(parents=True, exist_ok=True)

    scalar_tags = accumulator.Tags().get("scalars", [])
    summary: dict[str, object] = {
        "run_dir": str(run_dir),
        "event_file": str(event_file),
        "scalar_tags": scalar_tags,
        "scalars": {},
        "groups": {},
    }

    latest_rows: list[dict[str, object]] = []
    grouped_rows: dict[str, list[dict[str, object]]] = defaultdict(list)

    for tag in scalar_tags:
        events = accumulator.Scalars(tag)
        safe_name = _sanitize_tag(tag)
        csv_path = scalars_dir / f"{safe_name}.csv"

        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["wall_time", "step", "value"])
            for event in events:
                writer.writerow([event.wall_time, event.step, event.value])

        first_value = events[0].value if events else None
        last_value = events[-1].value if events else None
        mean_value = mean(event.value for event in events) if events else None
        min_value = min((event.value for event in events), default=None)
        max_value = max((event.value for event in events), default=None)
        last_step = events[-1].step if events else None
        group = _tag_group(tag)
        delta = (last_value - first_value) if events else None

        summary["scalars"][tag] = {
            "group": group,
            "count": len(events),
            "first_step": events[0].step if events else None,
            "last_step": last_step,
            "first_value": first_value,
            "last_value": last_value,
            "delta": delta,
            "min_value": min_value,
            "max_value": max_value,
            "mean_value": mean_value,
            "csv_path": str(csv_path),
        }
        row = {
            "group": group,
            "tag": tag,
            "count": len(events),
            "first_step": events[0].step if events else None,
            "last_step": last_step,
            "first_value": first_value,
            "last_value": last_value,
            "delta": delta,
            "min_value": min_value,
            "max_value": max_value,
            "mean_value": mean_value,
            "csv_path": str(csv_path),
        }
        latest_rows.append(row)
        grouped_rows[group].append(row)

    with (export_dir / "latest_values.csv").open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "group",
                "tag",
                "count",
                "first_step",
                "last_step",
                "first_value",
                "last_value",
                "delta",
                "min_value",
                "max_value",
                "mean_value",
                "csv_path",
            ],
        )
        writer.writeheader()
        writer.writerows(latest_rows)

    group_summary_rows: list[dict[str, object]] = []
    for group, rows in sorted(grouped_rows.items()):
        latest_values = [row["last_value"] for row in rows if row["last_value"] is not None]
        summary["groups"][group] = {
            "tag_count": len(rows),
            "tags": [row["tag"] for row in rows],
            "latest_mean": mean(latest_values) if latest_values else None,
        }
        group_summary_rows.append(
            {
                "group": group,
                "tag_count": len(rows),
                "latest_mean": mean(latest_values) if latest_values else None,
            }
        )

    with (export_dir / "group_summary.csv").open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["group", "tag_count", "latest_mean"])
        writer.writeheader()
        writer.writerows(group_summary_rows)

    with (export_dir / "summary.json").open("w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, indent=2, ensure_ascii=False)

    return export_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Export TensorBoard scalar data to CSV and JSON.")
    parser.add_argument("--run_dir", required=True, help="One RSL-RL run directory.")
    parser.add_argument(
        "--prune-sparse-zero-tags",
        action="store_true",
        help="Rewrite the run event file after removing selected all-zero scalar series.",
    )
    args = parser.parse_args()

    if args.prune_sparse_zero_tags:
        _, pruned_tags = prune_sparse_zero_scalar_tags(args.run_dir)
        if pruned_tags:
            print("Pruned sparse-zero TensorBoard tags:")
            for tag in pruned_tags:
                print(f"  - {tag}")
        else:
            print("No sparse-zero TensorBoard tags found.")

    export_dir = export_run_scalars(args.run_dir)
    print(f"Exported TensorBoard scalars to: {export_dir}")


if __name__ == "__main__":
    main()
