"""Inspect wheel joint axes and collision geometry in complete_car.usd."""

from __future__ import annotations

import argparse
import contextlib
import math
from pathlib import Path

from isaaclab.app import AppLauncher


parser = argparse.ArgumentParser(description="Inspect complete-car wheel USD geometry.")
parser.add_argument("--usd", type=Path, default=Path("USD/complete_car.usd"))
parser.add_argument("--report", type=Path, default=None)
AppLauncher.add_app_launcher_args(parser)
parser.set_defaults(headless=True)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

from pxr import Gf, Usd, UsdGeom, UsdPhysics  # noqa: E402


WHEEL_NAMES = (
    "body_car_wheel_left",
    "body_car_wheel_right",
    "head_car_wheel_left",
    "head_car_wheel_right",
    "tail_car_wheel_left",
    "tail_car_wheel_right",
)


def _as_vec3d(value) -> Gf.Vec3d:
    return Gf.Vec3d(float(value[0]), float(value[1]), float(value[2]))


def _normalize(value: Gf.Vec3d) -> Gf.Vec3d:
    length = value.GetLength()
    if length <= 1.0e-12:
        return Gf.Vec3d(0.0, 0.0, 0.0)
    return value / length


def _format_vec(value: Gf.Vec3d) -> str:
    return f"({value[0]: .6f}, {value[1]: .6f}, {value[2]: .6f})"


def _axis_token_to_vec(axis_token) -> Gf.Vec3d:
    axis = str(axis_token or "X").upper()
    if axis == "X":
        return Gf.Vec3d(1.0, 0.0, 0.0)
    if axis == "Y":
        return Gf.Vec3d(0.0, 1.0, 0.0)
    if axis == "Z":
        return Gf.Vec3d(0.0, 0.0, 1.0)
    raise ValueError(f"Unsupported revolute joint axis token: {axis_token}")


def _rotate_quat(quat, vector: Gf.Vec3d) -> Gf.Vec3d:
    if quat is None:
        return vector
    return Gf.Rotation(quat).TransformDir(vector)


def _get_rel_target(prim: Usd.Prim, rel_name: str) -> str | None:
    rel = prim.GetRelationship(rel_name)
    if not rel:
        return None
    targets = rel.GetTargets()
    if not targets:
        return None
    return targets[0].pathString


def _get_attr_value(prim: Usd.Prim, attr_name: str):
    attr = prim.GetAttribute(attr_name)
    if not attr:
        return None
    return attr.Get()


def _world_axis(transform: Gf.Matrix4d, local_axis: Gf.Vec3d) -> Gf.Vec3d:
    return _normalize(transform.TransformDir(local_axis))


def _collect_meshes(root: Usd.Prim) -> list[Usd.Prim]:
    meshes: list[Usd.Prim] = []
    for prim in Usd.PrimRange(root):
        if prim.GetTypeName() == "Mesh":
            meshes.append(prim)
    return meshes


def _mesh_points_in_wheel_frame(
    mesh_prim: Usd.Prim,
    wheel_world_inv: Gf.Matrix4d,
    xform_cache: UsdGeom.XformCache,
) -> list[Gf.Vec3d]:
    mesh = UsdGeom.Mesh(mesh_prim)
    points = mesh.GetPointsAttr().Get()
    if not points:
        return []
    mesh_world = xform_cache.GetLocalToWorldTransform(mesh_prim)
    output = []
    for point in points:
        point_w = mesh_world.Transform(_as_vec3d(point))
        output.append(wheel_world_inv.Transform(point_w))
    return output


def _bbox(points: list[Gf.Vec3d]) -> tuple[Gf.Vec3d, Gf.Vec3d, Gf.Vec3d] | None:
    if not points:
        return None
    mins = Gf.Vec3d(
        min(point[0] for point in points),
        min(point[1] for point in points),
        min(point[2] for point in points),
    )
    maxs = Gf.Vec3d(
        max(point[0] for point in points),
        max(point[1] for point in points),
        max(point[2] for point in points),
    )
    return mins, maxs, maxs - mins


def _dominant_axis(vector: Gf.Vec3d) -> str:
    values = (abs(vector[0]), abs(vector[1]), abs(vector[2]))
    idx = max(range(3), key=lambda i: values[i])
    sign = "+" if vector[idx] >= 0.0 else "-"
    return sign + "XYZ"[idx]


def _estimate_radius_from_extents(axis_in_wheel: Gf.Vec3d, extents: Gf.Vec3d) -> tuple[float, float, float]:
    dominant = _dominant_axis(axis_in_wheel)[-1]
    if dominant == "X":
        radial = (extents[1], extents[2])
        width = extents[0]
    elif dominant == "Y":
        radial = (extents[0], extents[2])
        width = extents[1]
    else:
        radial = (extents[0], extents[1])
        width = extents[2]
    return 0.5 * min(radial), 0.5 * max(radial), width


def inspect_wheel(stage: Usd.Stage, wheel_name: str, xform_cache: UsdGeom.XformCache) -> None:
    root = "/World/complete_car_alternative"
    wheel_path = f"{root}/{wheel_name}"
    joint_path = f"{root}/joints/{wheel_name}_joint"
    collision_root_path = f"{wheel_path}/collisions"

    wheel_prim = stage.GetPrimAtPath(wheel_path)
    joint_prim = stage.GetPrimAtPath(joint_path)
    collision_root = stage.GetPrimAtPath(collision_root_path)

    print(f"\n[WHEEL] {wheel_name}")
    print(f"  wheel_prim_valid: {wheel_prim.IsValid()} path={wheel_path}")
    print(f"  joint_prim_valid: {joint_prim.IsValid()} path={joint_path} type={joint_prim.GetTypeName() if joint_prim.IsValid() else None}")
    if not wheel_prim.IsValid() or not joint_prim.IsValid():
        return

    wheel_world = xform_cache.GetLocalToWorldTransform(wheel_prim)
    wheel_world_inv = wheel_world.GetInverse()
    wheel_translation = wheel_world.ExtractTranslation()
    wheel_x_w = _world_axis(wheel_world, Gf.Vec3d(1.0, 0.0, 0.0))
    wheel_y_w = _world_axis(wheel_world, Gf.Vec3d(0.0, 1.0, 0.0))
    wheel_z_w = _world_axis(wheel_world, Gf.Vec3d(0.0, 0.0, 1.0))
    print(f"  wheel_world_pos: {_format_vec(wheel_translation)}")
    print(f"  wheel_local_X_world: {_format_vec(wheel_x_w)}")
    print(f"  wheel_local_Y_world: {_format_vec(wheel_y_w)}")
    print(f"  wheel_local_Z_world: {_format_vec(wheel_z_w)}")

    revolute = UsdPhysics.RevoluteJoint(joint_prim)
    axis_token = revolute.GetAxisAttr().Get()
    axis_joint = _axis_token_to_vec(axis_token)
    body0_path = _get_rel_target(joint_prim, "physics:body0")
    body1_path = _get_rel_target(joint_prim, "physics:body1")
    local_pos0 = _get_attr_value(joint_prim, "physics:localPos0")
    local_pos1 = _get_attr_value(joint_prim, "physics:localPos1")
    local_rot0 = _get_attr_value(joint_prim, "physics:localRot0")
    local_rot1 = _get_attr_value(joint_prim, "physics:localRot1")
    print(f"  joint_axis_token: {axis_token}")
    print(f"  body0: {body0_path}")
    print(f"  body1: {body1_path}")
    print(f"  localPos0: {local_pos0}")
    print(f"  localPos1: {local_pos1}")
    print(f"  localRot0: {local_rot0}")
    print(f"  localRot1: {local_rot1}")

    axis_in_body1 = _normalize(_rotate_quat(local_rot1, axis_joint))
    axis_world_from_body1 = _world_axis(wheel_world, axis_in_body1)
    print(f"  joint_axis_in_wheel_body: {_format_vec(axis_in_body1)} dominant={_dominant_axis(axis_in_body1)}")
    print(f"  joint_axis_world_from_wheel: {_format_vec(axis_world_from_body1)}")
    print(
        "  dot(axis, wheel_local_axes): "
        f"X={Gf.Dot(axis_world_from_body1, wheel_x_w): .6f}, "
        f"Y={Gf.Dot(axis_world_from_body1, wheel_y_w): .6f}, "
        f"Z={Gf.Dot(axis_world_from_body1, wheel_z_w): .6f}"
    )

    meshes = _collect_meshes(collision_root) if collision_root.IsValid() else []
    print(f"  collision_mesh_count: {len(meshes)}")
    for mesh_prim in meshes:
        points = _mesh_points_in_wheel_frame(mesh_prim, wheel_world_inv, xform_cache)
        bbox = _bbox(points)
        has_collision_api = mesh_prim.HasAPI(UsdPhysics.CollisionAPI)
        if bbox is None:
            print(f"    mesh: {mesh_prim.GetPath()} points=0 collision_api={has_collision_api}")
            continue
        mins, maxs, extents = bbox
        radius_min, radius_max, width = _estimate_radius_from_extents(axis_in_body1, extents)
        print(f"    mesh: {mesh_prim.GetPath()}")
        print(f"      collision_api: {has_collision_api}")
        print(f"      bbox_min_wheel: {_format_vec(mins)}")
        print(f"      bbox_max_wheel: {_format_vec(maxs)}")
        print(f"      bbox_extent_wheel: {_format_vec(extents)}")
        print(
            "      radius_estimate_from_joint_axis: "
            f"min={radius_min:.6f}, max={radius_max:.6f}, width_along_axis={width:.6f}"
        )


def main() -> None:
    usd_path = args_cli.usd.resolve()
    stage = Usd.Stage.Open(str(usd_path))
    if stage is None:
        raise RuntimeError(f"Failed to open USD: {usd_path}")

    print(f"[USD] {usd_path}")
    print(f"  default_prim: {stage.GetDefaultPrim().GetPath() if stage.GetDefaultPrim() else None}")
    print(f"  meters_per_unit: {UsdGeom.GetStageMetersPerUnit(stage)}")
    print(f"  up_axis: {UsdGeom.GetStageUpAxis(stage)}")

    xform_cache = UsdGeom.XformCache(Usd.TimeCode.Default())
    for wheel_name in WHEEL_NAMES:
        inspect_wheel(stage, wheel_name, xform_cache)


if __name__ == "__main__":
    try:
        if args_cli.report is None:
            main()
        else:
            args_cli.report.parent.mkdir(parents=True, exist_ok=True)
            with args_cli.report.open("w", encoding="utf-8") as report_file:
                with contextlib.redirect_stdout(report_file):
                    main()
    finally:
        simulation_app.close()
