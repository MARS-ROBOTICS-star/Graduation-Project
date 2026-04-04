"""Remove the stale /World/terrain_preview subtree from complete_car.usd."""

from __future__ import annotations

from pathlib import Path
import shutil

from isaaclab.app import AppLauncher

simulation_app = AppLauncher(headless=True).app

from pxr import Usd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
USD_PATH = PROJECT_ROOT / "USD" / "complete_car.usd"
TARGET_PRIM_PATH = "/World/terrain_preview"
BACKUP_SUFFIX = ".terrain_preview_cleanup.bak"


def ensure_backup() -> Path:
    backup_path = USD_PATH.with_suffix(USD_PATH.suffix + BACKUP_SUFFIX)
    if not backup_path.exists():
        shutil.copy2(USD_PATH, backup_path)
        print(f"[BACKUP] Created {backup_path}")
    else:
        print(f"[BACKUP] Reusing existing {backup_path}")
    return backup_path


def main() -> None:
    ensure_backup()

    stage = Usd.Stage.Open(str(USD_PATH))
    if stage is None:
        raise RuntimeError(f"Failed to open USD: {USD_PATH}")

    target_prim = stage.GetPrimAtPath(TARGET_PRIM_PATH)
    if not target_prim.IsValid():
        raise RuntimeError(f"Prim not found: {TARGET_PRIM_PATH}")

    if not stage.RemovePrim(TARGET_PRIM_PATH):
        raise RuntimeError(f"Failed to remove prim: {TARGET_PRIM_PATH}")

    if not stage.GetRootLayer().Save():
        raise RuntimeError(f"Failed to save USD: {USD_PATH}")

    reopened_stage = Usd.Stage.Open(str(USD_PATH))
    if reopened_stage is None:
        raise RuntimeError(f"Failed to reopen USD after save: {USD_PATH}")
    if reopened_stage.GetPrimAtPath(TARGET_PRIM_PATH).IsValid():
        raise RuntimeError(f"Prim still exists after save: {TARGET_PRIM_PATH}")

    print(f"[REMOVED] {TARGET_PRIM_PATH}")
    print(f"[SAVED] {USD_PATH}")


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
