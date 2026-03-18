"""Inspect USD layer dependencies and prim composition for the articulated car asset."""

from pathlib import Path

from isaaclab.app import AppLauncher

simulation_app = AppLauncher(headless=True).app

from pxr import Sdf, Usd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
USD_ROOT = PROJECT_ROOT / "USD"
USD_PATH = USD_ROOT / "complete_car.usd"
REPORT_PATH = Path("/tmp/usd_dependency_report.txt")


REPORT_LINES: list[str] = []


def log(line: str = "") -> None:
    REPORT_LINES.append(line)


def print_layer_tree(layer: Sdf.Layer, indent: int = 0, visited: set[str] | None = None) -> None:
    if visited is None:
        visited = set()
    prefix = "  " * indent
    identifier = layer.identifier
    log(f"{prefix}- {identifier}")
    if identifier in visited:
        return
    visited.add(identifier)
    for sub_path in layer.subLayerPaths:
        sub_layer = Sdf.Layer.FindOrOpen(Sdf.ComputeAssetPathRelativeToLayer(layer, sub_path))
        log(f"{prefix}  subLayer: {sub_path}")
        if sub_layer is not None:
            print_layer_tree(sub_layer, indent + 2, visited)
        else:
            log(f"{prefix}    [missing] {sub_path}")


def inspect_prim(stage: Usd.Stage, prim_path: str) -> None:
    prim = stage.GetPrimAtPath(prim_path)
    log(f"[PRIM] {prim_path}")
    log(f"  valid: {prim.IsValid()}")
    if not prim.IsValid():
        return
    log(f"  type: {prim.GetTypeName()}")
    log(f"  has_payload: {prim.HasPayload()}")
    log(f"  has_references: {prim.HasAuthoredReferences()}")
    log(f"  variant_sets: {prim.GetVariantSets().GetNames()}")
    if prim.HasPayload():
        log(f"  payload_metadata: {prim.GetMetadata('payload')}")
    if prim.HasAuthoredReferences():
        log(f"  references_metadata: {prim.GetMetadata('references')}")
    log("  prim_stack:")
    for spec in prim.GetPrimStack():
        log(f"    - layer={spec.layer.identifier} path={spec.path}")


def main() -> None:
    log(f"[FILE] {USD_PATH}")
    stage = Usd.Stage.Open(str(USD_PATH))
    if stage is None:
        raise RuntimeError(f"Failed to open stage: {USD_PATH}")

    root_layer = stage.GetRootLayer()
    log("[ROOT_LAYER]")
    log(f"  identifier: {root_layer.identifier}")
    log(f"  real_path: {root_layer.realPath}")
    log(f"  sublayers: {root_layer.subLayerPaths}")

    log("[LAYER_TREE]")
    print_layer_tree(root_layer)

    default_prim = stage.GetDefaultPrim()
    log("[DEFAULT_PRIM]")
    log(f"  value: {default_prim.GetPath().pathString if default_prim else None}")

    log("[TOP_LEVEL_CHILDREN]")
    for prim in stage.GetPseudoRoot().GetChildren():
        log(f"  - {prim.GetPath().pathString} ({prim.GetTypeName()})")

    for prim_path in [
        "/World",
        "/World/complete_car_alternative",
        "/World/complete_car_alternative/spm1_spherical_virtual_y/visuals",
        "/World/complete_car_alternative/spm2_spherical_virtual_y/visuals",
    ]:
        inspect_prim(stage, prim_path)

    physics_layer_path = USD_ROOT / "configuration" / "default_scene_physics.usd"
    physics_stage = Usd.Stage.Open(str(physics_layer_path))
    if physics_stage is not None:
        log("[PHYSICS_LAYER_CHECK]")
        for prim_path in [
            "/visuals/spm1_spherical_virtual_y",
            "/visuals/spm2_spherical_virtual_y",
            "/visuals/spm1_spherical_virtual_z",
            "/visuals/spm2_spherical_virtual_z",
            "/complete_car_alternative/spm1_spherical_virtual_y",
            "/complete_car_alternative/spm1_spherical_virtual_y/visuals",
            "/complete_car_alternative/spm2_spherical_virtual_y",
            "/complete_car_alternative/spm2_spherical_virtual_y/visuals",
            "/complete_car_alternative/spm1_spherical_virtual_z",
            "/complete_car_alternative/spm1_spherical_virtual_z/visuals",
            "/complete_car_alternative/spm2_spherical_virtual_z",
            "/complete_car_alternative/spm2_spherical_virtual_z/visuals",
        ]:
            prim = physics_stage.GetPrimAtPath(prim_path)
            log(f"  {prim_path}: valid={prim.IsValid()} type={prim.GetTypeName() if prim.IsValid() else None}")

    REPORT_PATH.write_text("\n".join(REPORT_LINES), encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
