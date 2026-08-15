"""Repair the articulated car USD package without creating self-reference cycles."""

from pathlib import Path
import shutil

from isaaclab.app import AppLauncher

simulation_app = AppLauncher(headless=True).app

from pxr import Usd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
USD_ROOT = PROJECT_ROOT / "USD"
MAIN_USD = USD_ROOT / "complete_car.usd"
BASE_USD = USD_ROOT / "configuration" / "default_scene_base.usd"
MAIN_BACKUP = USD_ROOT / "complete_car.usd.bak"
BASE_BACKUP = USD_ROOT / "configuration" / "default_scene_base.usd.bak"


def restore_backup_if_present(target: Path, backup: Path) -> None:
    if backup.exists():
        shutil.copy2(backup, target)


def repair_base_layer() -> None:
    stage = Usd.Stage.Open(str(BASE_USD))
    if stage is None:
        raise RuntimeError(f"Failed to open base layer: {BASE_USD}")

    ref_asset_path = "./default_scene_physics.usd"
    fixes = {
        "/complete_car_alternative/spm1_spherical_virtual_y/visuals": "/complete_car_alternative/spm1_spherical_virtual_y/visuals",
        "/complete_car_alternative/spm1_spherical_virtual_z/visuals": "/complete_car_alternative/spm1_spherical_virtual_z/visuals",
        "/complete_car_alternative/spm2_spherical_virtual_y/visuals": "/complete_car_alternative/spm2_spherical_virtual_y/visuals",
        "/complete_car_alternative/spm2_spherical_virtual_z/visuals": "/complete_car_alternative/spm2_spherical_virtual_z/visuals",
    }

    for prim_path, target_path in fixes.items():
        prim = stage.GetPrimAtPath(prim_path)
        if not prim.IsValid():
            raise RuntimeError(f"Prim not found in base layer: {prim_path}")
        refs = prim.GetReferences()
        refs.ClearReferences()
        refs.AddReference(assetPath=ref_asset_path, primPath=target_path)

    if not stage.GetRootLayer().Save():
        raise RuntimeError(f"Failed to save repaired base layer: {BASE_USD}")


def ensure_default_prim() -> None:
    stage = Usd.Stage.Open(str(MAIN_USD))
    if stage is None:
        raise RuntimeError(f"Failed to open main USD: {MAIN_USD}")

    world_prim = stage.GetPrimAtPath("/World")
    if not world_prim.IsValid():
        raise RuntimeError("Prim '/World' not found in main USD.")

    stage.SetDefaultPrim(world_prim)
    if not stage.GetRootLayer().Save():
        raise RuntimeError(f"Failed to save main USD: {MAIN_USD}")


def main() -> None:
    restore_backup_if_present(BASE_USD, BASE_BACKUP)
    restore_backup_if_present(MAIN_USD, MAIN_BACKUP)
    print(f"[RESTORED] {BASE_USD}")
    print(f"[RESTORED] {MAIN_USD}")

    repair_base_layer()
    print(f"[FIXED] {BASE_USD}")

    ensure_default_prim()
    print(f"[FIXED] {MAIN_USD}")


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
