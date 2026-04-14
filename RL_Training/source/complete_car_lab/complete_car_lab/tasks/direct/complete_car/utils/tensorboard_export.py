#!/usr/bin/env python3

"""Export TensorBoard scalar data from an RSL-RL run into local files."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from statistics import mean
from pathlib import Path

from tensorboard.backend.event_processing import event_accumulator


def _sanitize_tag(tag: str) -> str:
    return tag.replace("/", "__")


def _tag_group(tag: str) -> str:
    return tag.split("/", 1)[0] if "/" in tag else "ungrouped"


def _find_event_file(run_dir: Path) -> Path:
    event_files = sorted(run_dir.glob("events.out.tfevents.*"))
    if not event_files:
        raise FileNotFoundError(f"No TensorBoard event file found under: {run_dir}")
    return event_files[-1]


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
    args = parser.parse_args()

    export_dir = export_run_scalars(args.run_dir)
    print(f"Exported TensorBoard scalars to: {export_dir}")


if __name__ == "__main__":
    main()
