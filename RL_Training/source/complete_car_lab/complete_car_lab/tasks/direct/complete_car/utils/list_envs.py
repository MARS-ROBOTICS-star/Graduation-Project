"""
列出当前 complete-car direct workflow 已注册的 Gym task。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher


PROJECT_ROOT = Path(__file__).resolve().parents[7]
EXTENSION_SOURCE = PROJECT_ROOT / "source" / "complete_car_lab"
if str(EXTENSION_SOURCE) not in sys.path:
    sys.path.insert(0, str(EXTENSION_SOURCE))


TASK_PREFIX = "CompleteCar-"

parser = argparse.ArgumentParser(description="List Isaac Lab environments.")
parser.add_argument("--keyword", type=str, default=None, help="Keyword to filter environments.")
args_cli = parser.parse_args()

app_launcher = AppLauncher(headless=True)
simulation_app = app_launcher.app

import gymnasium as gym
from prettytable import PrettyTable

import complete_car_lab  # noqa: F401


def main() -> None:
    """打印当前 complete-car 包注册出来的环境。"""

    table = PrettyTable(["S. No.", "Task Name", "Entry Point", "Config"])
    table.title = "Available CompleteCar Environments"
    table.align["Task Name"] = "l"
    table.align["Entry Point"] = "l"
    table.align["Config"] = "l"

    index = 0
    for task_spec in gym.registry.values():
        if task_spec.id.startswith(TASK_PREFIX) and (args_cli.keyword is None or args_cli.keyword in task_spec.id):
            table.add_row([index + 1, task_spec.id, task_spec.entry_point, task_spec.kwargs["env_cfg_entry_point"]])
            index += 1

    print(table)


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
