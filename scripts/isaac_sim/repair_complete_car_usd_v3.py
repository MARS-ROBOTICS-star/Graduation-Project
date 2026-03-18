"""Repair complete_car.usd by restoring base references and adding missing /visuals aliases."""

from pathlib import Path
import shutil

from isaaclab.app import AppLauncher

simulation_app = AppLauncher(headless=True).app

from pxr import Sdf, Usd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
USD_ROOT = PROJECT_ROOT / "USD"
MAIN_USD = USD_ROOT / "complete_car.usd"
BASE_USD = USD_ROOT / "configuration" / "default_scene_base.usd"
PHYSICS_USD = USD_ROOT / "configuration" / "default_scene_physics.usd"


def restore_backup_if_present(target: Path) -> None:
    backup = target.with_suffix(target.suffix + ".bak")
    if backup.exists():
        shutil.copy2(backup, target)


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


def add_visual_aliases() -> None:
    stage = Usd.Stage.Open(str(PHYSICS_USD))
    if stage is None:
        raise RuntimeError(f"Failed to open physics USD: {PHYSICS_USD}")

    # Ensure the /visuals container exists.
    stage.DefinePrim("/visuals", "Xform")

    alias_map = {
        "/visuals/spm1_spherical_virtual_y": "/complete_car_alternative/spm1_spherical_virtual_y/visuals",
        "/visuals/spm1_spherical_virtual_z": "/complete_car_alternative/spm1_spherical_virtual_z/visuals",
        "/visuals/spm2_spherical_virtual_y": "/complete_car_alternative/spm2_spherical_virtual_y/visuals",
        "/visuals/spm2_spherical_virtual_z": "/complete_car_alternative/spm2_spherical_virtual_z/visuals",
    }

    for alias_path, target_path in alias_map.items():
        prim = stage.DefinePrim(alias_path, "Xform")
        refs = prim.GetReferences()
        refs.ClearReferences()
        refs.AddInternalReference(target_path)

    if not stage.GetRootLayer().Save():
        raise RuntimeError(f"Failed to save physics USD: {PHYSICS_USD}")


def main() -> None:
    restore_backup_if_present(BASE_USD)
    restore_backup_if_present(MAIN_USD)
    print(f"[RESTORED] {BASE_USD}")
    print(f"[RESTORED] {MAIN_USD}")

    add_visual_aliases()
    print(f"[FIXED] {PHYSICS_USD}")

    set_default_prim()
    print(f"[FIXED] {MAIN_USD}")


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
