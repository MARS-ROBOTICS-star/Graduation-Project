"""Align the complete_car robot subtree to the equivalent asset layout.

This script only edits the robot subtree under /World/complete_car_final and its
local joints scope. It removes the extra SPM leg rigid bodies and their matching
fixed joints so the articulation hierarchy matches the equivalent asset more
closely.
"""

from __future__ import annotations

from pathlib import Path
import shutil

from isaaclab.app import AppLauncher

simulation_app = AppLauncher(headless=True).app

from pxr import Usd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
USD_PATH = PROJECT_ROOT / "USD" / "complete_car.usd"
ROOT_PRIM_PATH = "/World/complete_car_final"
JOINTS_SCOPE_PATH = f"{ROOT_PRIM_PATH}/joints"
BACKUP_SUFFIX = ".spm_leg_cleanup.bak"

LEG_PRIM_NAMES = [
    "spm1_leg1_proximal",
    "spm1_leg1_distal",
    "spm1_leg2_proximal",
    "spm1_leg2_distal",
    "spm1_leg3_proximal",
    "spm1_leg3_distal",
    "spm2_leg1_proximal",
    "spm2_leg1_distal",
    "spm2_leg2_proximal",
    "spm2_leg2_distal",
    "spm2_leg3_proximal",
    "spm2_leg3_distal",
]

JOINT_PRIM_NAMES = [
    "spm1_leg1_base_proximal_joint",
    "spm1_leg1_intermediate_distal_joint",
    "spm1_leg2_base_proximal_joint",
    "spm1_leg2_intermediate_distal",
    "spm1_leg3_base_proximal",
    "spm1_leg3_intermediate_distal",
    "spm2_leg1_base_proximal_joint",
    "spm2_leg1_intermediate_distal_joint",
    "spm2_leg2_base_proximal",
    "spm2_leg2_intermediate_distal",
    "spm2_leg3_base_proximal_joint",
    "spm2_leg3_intermediate_distal",
]


def ensure_backup() -> Path:
    backup_path = USD_PATH.with_suffix(USD_PATH.suffix + BACKUP_SUFFIX)
    if not backup_path.exists():
        shutil.copy2(USD_PATH, backup_path)
        print(f"[BACKUP] Created {backup_path}")
    else:
        print(f"[BACKUP] Reusing existing {backup_path}")
    return backup_path


def remove_prim_or_fail(stage: Usd.Stage, prim_path: str) -> None:
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        raise RuntimeError(f"Prim not found: {prim_path}")
    if not stage.RemovePrim(prim_path):
        raise RuntimeError(f"Failed to remove prim: {prim_path}")
    print(f"[REMOVED] {prim_path}")


def remaining_robot_children(stage: Usd.Stage) -> list[str]:
    root = stage.GetPrimAtPath(ROOT_PRIM_PATH)
    if not root.IsValid():
        raise RuntimeError(f"Robot root not found: {ROOT_PRIM_PATH}")
    return [child.GetName() for child in root.GetChildren()]


def remaining_joint_children(stage: Usd.Stage) -> list[str]:
    joints_scope = stage.GetPrimAtPath(JOINTS_SCOPE_PATH)
    if not joints_scope.IsValid():
        raise RuntimeError(f"Joints scope not found: {JOINTS_SCOPE_PATH}")
    return [child.GetName() for child in joints_scope.GetChildren()]


def main() -> None:
    ensure_backup()

    stage = Usd.Stage.Open(str(USD_PATH))
    if stage is None:
        raise RuntimeError(f"Failed to open USD: {USD_PATH}")

    for prim_name in LEG_PRIM_NAMES:
        remove_prim_or_fail(stage, f"{ROOT_PRIM_PATH}/{prim_name}")

    for prim_name in JOINT_PRIM_NAMES:
        remove_prim_or_fail(stage, f"{JOINTS_SCOPE_PATH}/{prim_name}")

    if not stage.GetRootLayer().Save():
        raise RuntimeError(f"Failed to save USD: {USD_PATH}")

    print("[SAVED] complete_car.usd")
    print("[REMAINING ROBOT CHILDREN]")
    for name in remaining_robot_children(stage):
        print(name)
    print("[REMAINING JOINTS]")
    for name in remaining_joint_children(stage):
        print(name)


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
