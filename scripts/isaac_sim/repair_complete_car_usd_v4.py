"""Pragmatic repair for Isaac Lab: clear broken visual-only references and set default prim."""

from pathlib import Path
import shutil

from isaaclab.app import AppLauncher

simulation_app = AppLauncher(headless=True).app

from pxr import Usd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
USD_ROOT = PROJECT_ROOT / "USD"
MAIN_USD = USD_ROOT / "complete_car.usd"
BASE_USD = USD_ROOT / "configuration" / "default_scene_base.usd"
PHYSICS_USD = USD_ROOT / "configuration" / "default_scene_physics.usd"


def restore_backup_if_present(target: Path) -> None:
    backup = target.with_suffix(target.suffix + ".bak")
    if backup.exists():
        shutil.copy2(backup, target)


def clear_broken_visual_refs() -> None:
    stage = Usd.Stage.Open(str(BASE_USD))
    if stage is None:
        raise RuntimeError(f"Failed to open base USD: {BASE_USD}")

    broken_visual_prims = [
        "/complete_car_alternative/spm1_spherical_virtual_y/visuals",
        "/complete_car_alternative/spm1_spherical_virtual_z/visuals",
        "/complete_car_alternative/spm2_spherical_virtual_y/visuals",
        "/complete_car_alternative/spm2_spherical_virtual_z/visuals",
    ]

    for prim_path in broken_visual_prims:
        prim = stage.GetPrimAtPath(prim_path)
        if not prim.IsValid():
            raise RuntimeError(f"Prim not found in base USD: {prim_path}")
        prim.GetReferences().ClearReferences()

    if not stage.GetRootLayer().Save():
        raise RuntimeError(f"Failed to save base USD: {BASE_USD}")


def restore_physics_if_present() -> None:
    backup = PHYSICS_USD.with_suffix(PHYSICS_USD.suffix + ".bak")
    if backup.exists():
        shutil.copy2(backup, PHYSICS_USD)


def set_default_prim() -> None:
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
    restore_backup_if_present(BASE_USD)
    restore_backup_if_present(MAIN_USD)
    restore_physics_if_present()
    print(f"[RESTORED] {BASE_USD}")
    print(f"[RESTORED] {MAIN_USD}")
    print(f"[RESTORED] {PHYSICS_USD}")

    clear_broken_visual_refs()
    print(f"[FIXED] Cleared broken visual references in {BASE_USD}")

    set_default_prim()
    print(f"[FIXED] Set default prim in {MAIN_USD}")


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
