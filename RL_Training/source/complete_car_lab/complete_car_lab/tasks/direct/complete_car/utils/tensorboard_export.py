#!/usr/bin/env python3

"""Export TensorBoard scalar data from an RSL-RL run into local files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from tensorboard.backend.event_processing import event_accumulator


def _sanitize_tag(tag: str) -> str:
    return tag.replace("/", "__")


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
    }

    latest_rows: list[dict[str, object]] = []

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
        last_step = events[-1].step if events else None

        summary["scalars"][tag] = {
            "count": len(events),
            "first_step": events[0].step if events else None,
            "last_step": last_step,
            "first_value": first_value,
            "last_value": last_value,
            "csv_path": str(csv_path),
        }
        latest_rows.append(
            {
                "tag": tag,
                "count": len(events),
                "last_step": last_step,
                "last_value": last_value,
            }
        )

    with (export_dir / "summary.json").open("w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, indent=2, ensure_ascii=False)

    with (export_dir / "latest_values.csv").open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["tag", "count", "last_step", "last_value"])
        writer.writeheader()
        writer.writerows(latest_rows)

    return export_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Export TensorBoard scalar data to CSV and JSON.")
    parser.add_argument("--run_dir", required=True, help="One RSL-RL run directory.")
    args = parser.parse_args()

    export_dir = export_run_scalars(args.run_dir)
    print(f"Exported TensorBoard scalars to: {export_dir}")


if __name__ == "__main__":
    main()
