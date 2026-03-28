"""Add a shared physics material to the six wheels in complete_car.usd."""

from __future__ import annotations

from pathlib import Path
import shutil

from isaaclab.app import AppLauncher

simulation_app = AppLauncher(headless=True).app

from pxr import PhysxSchema, Usd, UsdPhysics, UsdShade


PROJECT_ROOT = Path(__file__).resolve().parents[2]
USD_PATH = PROJECT_ROOT / "USD" / "complete_car.usd"
BACKUP_PATH = USD_PATH.with_suffix(USD_PATH.suffix + ".wheel_friction.bak")
MATERIAL_PATH = "/World/complete_car_final/Looks/wheel_physics_material"
WHEEL_COLLISION_ROOTS = [
    "/World/complete_car_final/body_car_wheel_left/collisions",
    "/World/complete_car_final/body_car_wheel_right/collisions",
    "/World/complete_car_final/head_car_wheel_left/collisions",
    "/World/complete_car_final/head_car_wheel_right/collisions",
    "/World/complete_car_final/tail_car_wheel_left/collisions",
    "/World/complete_car_final/tail_car_wheel_right/collisions",
]


def ensure_backup() -> None:
    if not BACKUP_PATH.exists():
        shutil.copy2(USD_PATH, BACKUP_PATH)
        print(f"[BACKUP] Created {BACKUP_PATH}")
    else:
        print(f"[BACKUP] Reusing existing {BACKUP_PATH}")


def main() -> None:
    ensure_backup()

    stage = Usd.Stage.Open(str(USD_PATH))
    if stage is None:
        raise RuntimeError(f"Failed to open USD: {USD_PATH}")

    material = UsdShade.Material.Define(stage, MATERIAL_PATH)
    material_prim = material.GetPrim()

    material_api = UsdPhysics.MaterialAPI.Apply(material_prim)
    material_api.CreateStaticFrictionAttr(1.0)
    material_api.CreateDynamicFrictionAttr(1.0)

    physx_material_api = PhysxSchema.PhysxMaterialAPI.Apply(material_prim)
    physx_material_api.CreateFrictionCombineModeAttr("multiply")

    print(f"[MATERIAL] {MATERIAL_PATH}")
    print("  physics:staticFriction = 1.0")
    print("  physics:dynamicFriction = 1.0")
    print("  physxMaterial:frictionCombineMode = multiply")

    for collision_root_path in WHEEL_COLLISION_ROOTS:
        collision_root = stage.GetPrimAtPath(collision_root_path)
        if not collision_root.IsValid():
            raise RuntimeError(f"Collision root not found: {collision_root_path}")
        binding_api = UsdShade.MaterialBindingAPI.Apply(collision_root)
        binding_api.Bind(material, UsdShade.Tokens.weakerThanDescendants, "physics")
        print(f"[BOUND] {collision_root_path}")

    if not stage.GetRootLayer().Save():
        raise RuntimeError(f"Failed to save USD: {USD_PATH}")
    print(f"[SAVED] {USD_PATH}")


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
