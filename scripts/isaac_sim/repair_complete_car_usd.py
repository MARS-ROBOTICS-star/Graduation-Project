"""Repair the articulated car USD package for Isaac Lab loading."""

from pathlib import Path
import shutil

from isaaclab.app import AppLauncher

simulation_app = AppLauncher(headless=True).app

from pxr import Sdf, Usd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
USD_ROOT = PROJECT_ROOT / "USD"
MAIN_USD = USD_ROOT / "complete_car.usd"
BASE_USD = USD_ROOT / "configuration" / "default_scene_base.usd"


def backup_file(path: Path) -> Path:
    backup_path = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup_path)
    return backup_path


def repair_base_layer() -> None:
    stage = Usd.Stage.Open(str(BASE_USD))
    if stage is None:
        raise RuntimeError(f"Failed to open base layer: {BASE_USD}")

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
        refs.AddInternalReference(target_path)

    if not stage.GetRootLayer().Save():
        raise RuntimeError(f"Failed to save repaired base layer: {BASE_USD}")


def repair_main_layer() -> None:
    stage = Usd.Stage.Open(str(MAIN_USD))
    if stage is None:
        raise RuntimeError(f"Failed to open main USD: {MAIN_USD}")

    world_prim = stage.GetPrimAtPath("/World")
    if not world_prim.IsValid():
        raise RuntimeError("Prim '/World' not found in main USD.")

    stage.SetDefaultPrim(world_prim)

    if not stage.GetRootLayer().Save():
        raise RuntimeError(f"Failed to save repaired main USD: {MAIN_USD}")


def main() -> None:
    base_backup = backup_file(BASE_USD)
    main_backup = backup_file(MAIN_USD)
    print(f"[BACKUP] {base_backup}")
    print(f"[BACKUP] {main_backup}")

    repair_base_layer()
    print(f"[FIXED] {BASE_USD}")

    repair_main_layer()
    print(f"[FIXED] {MAIN_USD}")


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
