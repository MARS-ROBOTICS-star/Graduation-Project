"""Minimal Isaac Lab asset loading check for the articulated car USD."""

import argparse
from pathlib import Path

from isaaclab.app import AppLauncher


parser = argparse.ArgumentParser(description="Check whether the articulated car USD can be loaded in Isaac Lab.")
parser.add_argument("--headless", action="store_true", default=False, help="Run Isaac Sim headless.")
args_cli = parser.parse_args()

app_launcher = AppLauncher(headless=args_cli.headless)
simulation_app = app_launcher.app

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.sim import SimulationContext
from isaaclab.utils import configclass
from pxr import Usd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
USD_PATH = PROJECT_ROOT / "USD" / "complete_car.usd"


def inspect_usd_file() -> None:
    """Print basic USD structure information."""
    stage = Usd.Stage.Open(str(USD_PATH))
    if stage is None:
        raise RuntimeError(f"Failed to open USD file: {USD_PATH}")

    default_prim = stage.GetDefaultPrim()
    top_level_children = [prim.GetPath().pathString for prim in stage.GetPseudoRoot().GetChildren()]

    print("[USD]")
    print(f"  path: {USD_PATH}")
    print(f"  default_prim: {default_prim.GetPath().pathString if default_prim else None}")
    print(f"  top_level_children: {top_level_children}")

    for prim_path in [
        "/World",
        "/World/complete_car",
        "/World/complete_car_alternative",
        "/World/complete_car_alternative/body_car_chassis",
    ]:
        prim = stage.GetPrimAtPath(prim_path)
        print(f"  prim {prim_path}: valid={prim.IsValid()} type={prim.GetTypeName() if prim.IsValid() else None}")


@configclass
class CarSceneCfg(InteractiveSceneCfg):
    """Minimal scene with ground, light, and the articulated car."""

    ground = AssetBaseCfg(
        prim_path="/World/defaultGroundPlane",
        spawn=sim_utils.GroundPlaneCfg(),
    )

    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DistantLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75)),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, 500.0)),
    )

    robot = ArticulationCfg(
        prim_path="{ENV_REGEX_NS}/Robot",
        articulation_root_prim_path="/body_car_chassis",
        spawn=sim_utils.UsdFileCfg(
            usd_path=str(USD_PATH),
            activate_contact_sensors=False,
        ),
        init_state=ArticulationCfg.InitialStateCfg(pos=(0.0, 0.0, 0.3)),
        actuators={},
    )


def main() -> None:
    inspect_usd_file()

    sim = SimulationContext(sim_utils.SimulationCfg(dt=0.005))
    scene = InteractiveScene(CarSceneCfg(num_envs=1, env_spacing=4.0))
    sim.reset()

    robot = scene["robot"]
    print("[ISAACLAB]")
    print(f"  num_instances: {robot.num_instances}")
    print(f"  num_joints: {robot.num_joints}")
    print(f"  joint_names: {robot.joint_names}")
    print(f"  default_root_state_shape: {tuple(robot.data.default_root_state.shape)}")
    print(f"  default_joint_pos_shape: {tuple(robot.data.default_joint_pos.shape)}")
    print(f"  default_joint_vel_shape: {tuple(robot.data.default_joint_vel.shape)}")

    key_joints = [
        "body_car_wheel_left_joint",
        "body_car_wheel_right_joint",
        "head_car_wheel_left_joint",
        "head_car_wheel_right_joint",
        "tail_car_wheel_left_joint",
        "tail_car_wheel_right_joint",
        "spm1_platform_joint_z",
        "spm1_platform_joint_y",
        "spm1_platform_joint_x",
        "spm2_platform_joint_z",
        "spm2_platform_joint_y",
        "spm2_platform_joint_x",
    ]

    print("[JOINT_CHECK]")
    missing_joints = [name for name in key_joints if name not in robot.joint_names]
    if missing_joints:
        print(f"  missing_joints: {missing_joints}")
    else:
        print("  missing_joints: []")

    print("[RESULT]")
    print("  Isaac Lab asset loading check completed.")


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
