import omni.kit.commands
import omni.usd
from pxr import Usd

ROOT_PATH = "/World/complete_car_final"

usd_context = omni.usd.get_context()
stage = usd_context.get_stage()

if stage is None:
    raise RuntimeError("No USD stage is currently open.")

root_prim = stage.GetPrimAtPath(ROOT_PATH)
if not root_prim.IsValid():
    raise RuntimeError(f"Root prim not found: {ROOT_PATH}")


def is_visual_or_collision_path(path_str: str) -> bool:
    s = path_str.lower()
    return ("visual" in s) or ("collision" in s)


def collect_instanceable_prims_under_visual_collision(root: Usd.Prim) -> list[str]:
    prim_paths = []

    for prim in Usd.PrimRange(root):
        if not prim.IsValid():
            continue

        path_str = str(prim.GetPath()).lower()

        # Only handle visual / collision related paths.
        if not is_visual_or_collision_path(path_str):
            continue

        # Skip prototype / instance proxy prims.
        if prim.IsInPrototype() or prim.IsInstanceProxy():
            continue

        # Only collect prims that are currently instanceable.
        if prim.IsInstanceable():
            prim_paths.append(str(prim.GetPath()))

    return prim_paths


prim_paths_to_disable = collect_instanceable_prims_under_visual_collision(root_prim)

print(f"Found {len(prim_paths_to_disable)} instanceable prim(s) under visual/collision.")

if prim_paths_to_disable:
    omni.kit.commands.execute(
        "ToggleInstanceableCommand",
        prim_path=prim_paths_to_disable,
    )

    disabled_count = 0
    still_instanceable = []

    for path in prim_paths_to_disable:
        prim = stage.GetPrimAtPath(path)
        if prim.IsValid():
            if not prim.IsInstanceable():
                disabled_count += 1
            else:
                still_instanceable.append(path)

    print(f"Successfully disabled instanceable on {disabled_count} prim(s).")

    if still_instanceable:
        print("These prims are still instanceable:")
        for path in still_instanceable:
            print("  ", path)
    else:
        print("All target prims are now non-instanceable.")
else:
    print("No instanceable prims found under visual/collision.")
