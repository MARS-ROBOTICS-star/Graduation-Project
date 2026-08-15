"""Add fixed SPM base reference frames aligned with the platform zero pose.

This script authors one helper frame under each SPM base rigid body:
- /World/complete_car_final/spm1_base/spm1_base_ref
- /World/complete_car_final/spm2_base/spm2_base_ref

Each base_ref is given the same local transform as the corresponding
spm*_spherical_virtual_z frame relative to spm*_base in the current static USD.
Under the current equivalent-chain asset, this makes:
    base_ref -> platform ~= identity
at the mechanical zero pose.
"""

from __future__ import annotations

from pathlib import Path
import math
import shutil

from isaaclab.app import AppLauncher

simulation_app = AppLauncher(headless=True).app

from pxr import Gf, UsdGeom
import omni.usd
from isaacsim.core.utils.stage import open_stage


PROJECT_ROOT = Path(__file__).resolve().parents[2]
USD_PATH = PROJECT_ROOT / "USD" / "complete_car.usd"
BACKUP_PATH = USD_PATH.with_suffix(USD_PATH.suffix + ".base_ref.bak")

REF_SPECS = [
    {
        "base_path": "/World/complete_car_final/spm1_base",
        "target_path": "/World/complete_car_final/spm1_spherical_virtual_z",
        "platform_path": "/World/complete_car_final/spm1_platform",
        "ref_name": "spm1_base_ref",
    },
    {
        "base_path": "/World/complete_car_final/spm2_base",
        "target_path": "/World/complete_car_final/spm2_spherical_virtual_z",
        "platform_path": "/World/complete_car_final/spm2_platform",
        "ref_name": "spm2_base_ref",
    },
]


def ensure_backup() -> None:
    if not BACKUP_PATH.exists():
        shutil.copy2(USD_PATH, BACKUP_PATH)
        print(f"[BACKUP] Created {BACKUP_PATH}")
    else:
        print(f"[BACKUP] Reusing existing {BACKUP_PATH}")


def rotation_matrix_to_rpy_zyx_deg(rot: Gf.Matrix3d) -> tuple[float, float, float]:
    r20 = float(rot[2][0])
    pitch = math.asin(max(-1.0, min(1.0, -r20)))
    cos_pitch = math.cos(pitch)

    if abs(cos_pitch) > 1e-8:
        roll = math.atan2(float(rot[2][1]), float(rot[2][2]))
        yaw = math.atan2(float(rot[1][0]), float(rot[0][0]))
    else:
        roll = 0.0
        yaw = math.atan2(-float(rot[0][1]), float(rot[1][1]))

    return tuple(round(math.degrees(v), 6) for v in (roll, pitch, yaw))


def matrix_to_trs(matrix: Gf.Matrix4d) -> tuple[Gf.Vec3d, Gf.Quatf, Gf.Vec3f]:
    transform = Gf.Transform()
    transform.SetMatrix(matrix)
    translation = transform.GetTranslation()
    rotation_d = transform.GetRotation().GetQuat()
    rotation = Gf.Quatf(
        float(rotation_d.GetReal()),
        Gf.Vec3f(*[float(v) for v in rotation_d.GetImaginary()]),
    )
    scale = Gf.Vec3f(*[float(v) for v in transform.GetScale()])
    return translation, rotation, scale


def remove_if_exists(stage, prim_path: str) -> None:
    prim = stage.GetPrimAtPath(prim_path)
    if prim.IsValid():
        if not stage.RemovePrim(prim_path):
            raise RuntimeError(f"Failed to remove existing prim: {prim_path}")
        print(f"[REMOVED] Existing {prim_path}")


def author_ref_frame(stage, cache: UsdGeom.XformCache, spec: dict[str, str]) -> None:
    base_path = spec["base_path"]
    target_path = spec["target_path"]
    platform_path = spec["platform_path"]
    ref_path = f"{base_path}/{spec['ref_name']}"

    base_prim = stage.GetPrimAtPath(base_path)
    target_prim = stage.GetPrimAtPath(target_path)
    platform_prim = stage.GetPrimAtPath(platform_path)
    if not base_prim.IsValid():
        raise RuntimeError(f"Base prim not found: {base_path}")
    if not target_prim.IsValid():
        raise RuntimeError(f"Target prim not found: {target_path}")
    if not platform_prim.IsValid():
        raise RuntimeError(f"Platform prim not found: {platform_path}")

    base_world = cache.GetLocalToWorldTransform(base_prim)
    target_world = cache.GetLocalToWorldTransform(target_prim)
    relative = base_world.GetInverse() * target_world

    remove_if_exists(stage, ref_path)
    ref_xform = UsdGeom.Xform.Define(stage, ref_path)
    translation, rotation, scale = matrix_to_trs(relative)
    ref_xform.AddTranslateOp(UsdGeom.XformOp.PrecisionDouble).Set(translation)
    ref_xform.AddOrientOp(UsdGeom.XformOp.PrecisionFloat).Set(rotation)
    ref_xform.AddScaleOp(UsdGeom.XformOp.PrecisionFloat).Set(scale)

    cache.Clear()
    ref_prim = stage.GetPrimAtPath(ref_path)
    ref_world = cache.GetLocalToWorldTransform(ref_prim)
    rel_ref_platform = ref_world.GetInverse() * cache.GetLocalToWorldTransform(platform_prim)
    rel_rot = rel_ref_platform.ExtractRotationMatrix()

    print(f"[ADDED] {ref_path}")
    print(f"  base -> target zero-pose rpy_zyx_deg = {rotation_matrix_to_rpy_zyx_deg(relative.ExtractRotationMatrix())}")
    print(f"  base_ref -> platform zero-pose rpy_zyx_deg = {rotation_matrix_to_rpy_zyx_deg(rel_rot)}")



def main() -> None:
    ensure_backup()

    if not open_stage(str(USD_PATH)):
        raise RuntimeError(f"Failed to open stage: {USD_PATH}")
    stage = omni.usd.get_context().get_stage()
    if stage is None:
        raise RuntimeError(f"Failed to get stage for: {USD_PATH}")

    cache = UsdGeom.XformCache()
    for spec in REF_SPECS:
        author_ref_frame(stage, cache, spec)

    root_layer = stage.GetRootLayer()
    root_layer.Save()
    print(f"[SAVED] {root_layer.realPath}")


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
