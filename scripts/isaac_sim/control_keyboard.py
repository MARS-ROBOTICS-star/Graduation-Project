import argparse
from pathlib import Path

from isaacsim import SimulationApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Keyboard teleop for the complete car with optional terrain preview."
    )
    parser.add_argument(
        "--terrain",
        choices=["none", "slope_ramp", "stairs_up", "discrete_obstacles", "gap", "single_gap", "stepping_stones", "single_bridge", "air_beams", "corridor"],
        default="slope_ramp",
        help="Optional terrain tile to build under the robot before teleop starts.",
    )
    parser.add_argument(
        "--terrain-seed",
        type=int,
        default=7,
        help="Random seed for obstacle-like terrain tiles.",
    )
    return parser.parse_args()


ARGS = parse_args()

# 先启动 Isaac Sim，再导入其他 Isaac Sim 模块
simulation_app = SimulationApp({"headless": False})

import numpy as np
import carb
import omni.appwindow
import omni.usd

from isaacsim.core.api.world import World
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.stage import open_stage
from isaacsim.core.utils.types import ArticulationAction
from terrain_preview.terrain_builder import build_single_tile


# =========================
# 1. 基本配置
# =========================
_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = next(parent for parent in _THIS_FILE.parents if (parent / "AGENTS.md").exists())
USD_PATH = str(PROJECT_ROOT / "USD" / "complete_car.usd")
ROBOT_PRIM_PATH = "/World/complete_car_final"
TERRAIN_ROOT_PATH = "/World/terrain_preview"
TERRAIN_ORIGIN = (-1.0, 0.0, 0.0)
GROUND_PRIM_CANDIDATES = [
    "/World/defaultGroundPlane",
    "/World/GroundPlane",
    "/World/ground",
    "/World/groundPlane",
    "/World/Environment/defaultGroundPlane",
]

# 轮子关节名
WHEEL_JOINT_NAMES = [
    "body_car_wheel_left_joint",
    "body_car_wheel_right_joint",
    "head_car_wheel_left_joint",
    "head_car_wheel_right_joint",
    "tail_car_wheel_left_joint",
    "tail_car_wheel_right_joint",
]

# 两个球绞各 3 自由度
BALL_JOINT_NAMES = [
    "spm1_platform_joint_z",
    "spm1_platform_joint_y",
    "spm1_platform_joint_x",
    "spm2_platform_joint_z",
    "spm2_platform_joint_y",
    "spm2_platform_joint_x",
]

# 控制参数
WHEEL_LINEAR_SPEED = 8.0
WHEEL_TURN_SPEED = 4.0
BALL_JOINT_DELTA = 0.01
BALL_JOINT_LIMIT = 0.8
WHEEL_VELOCITY_SMOOTHING = 0.20
BALL_POSITION_SMOOTHING = 0.20

# 数字小键盘键位映射
BALL_JOINT_KEY_BINDINGS = [
    (carb.input.KeyboardInput.NUMPAD_7, carb.input.KeyboardInput.NUMPAD_4),
    (carb.input.KeyboardInput.NUMPAD_8, carb.input.KeyboardInput.NUMPAD_5),
    (carb.input.KeyboardInput.NUMPAD_9, carb.input.KeyboardInput.NUMPAD_6),
    (carb.input.KeyboardInput.NUMPAD_1, carb.input.KeyboardInput.NUMPAD_DIVIDE),
    (carb.input.KeyboardInput.NUMPAD_2, carb.input.KeyboardInput.NUMPAD_MULTIPLY),
    (carb.input.KeyboardInput.NUMPAD_3, carb.input.KeyboardInput.NUMPAD_SUBTRACT),
]


# =========================
# 2. 键盘状态
# =========================
key_state = {}


def set_key(key_code, pressed):
    key_state[key_code] = pressed


def is_pressed(key_code):
    return key_state.get(key_code, False)


# =========================
# 3. 订阅键盘事件
# =========================
appwindow = omni.appwindow.get_default_app_window()
keyboard = appwindow.get_keyboard()
input_iface = carb.input.acquire_input_interface()


def on_keyboard_event(event, *args, **kwargs):
    key_code = event.input
    if event.type == carb.input.KeyboardEventType.KEY_PRESS:
        set_key(key_code, True)
    elif event.type == carb.input.KeyboardEventType.KEY_RELEASE:
        set_key(key_code, False)
    return True


keyboard_sub = input_iface.subscribe_to_keyboard_events(keyboard, on_keyboard_event)


def deactivate_default_ground(stage):
    disabled_paths = []
    for prim_path in GROUND_PRIM_CANDIDATES:
        prim = stage.GetPrimAtPath(prim_path)
        if prim.IsValid() and prim.IsActive():
            prim.SetActive(False)
            disabled_paths.append(prim_path)
    if disabled_paths:
        print("[INFO] Disabled existing ground prims:")
        for prim_path in disabled_paths:
            print("  ", prim_path)


def maybe_build_terrain(stage):
    if ARGS.terrain == "none":
        print("[INFO] Terrain preview disabled for control_keyboard.py")
        return

    deactivate_default_ground(stage)
    spec = build_single_tile(
        stage,
        terrain_name=ARGS.terrain,
        origin=TERRAIN_ORIGIN,
        seed=ARGS.terrain_seed,
        root_path=TERRAIN_ROOT_PATH,
    )
    print(
        "[INFO] Built terrain tile:",
        spec.name,
        f"(origin={TERRAIN_ORIGIN}, size=({spec.length:.2f}, {spec.width:.2f}))",
    )


# =========================
# 4. 创建世界并打开完整场景
# =========================
print(f"[INFO] Opening USD: {USD_PATH}")
ok = open_stage(USD_PATH)
print("[INFO] open_stage result:", ok)

if not ok:
    raise RuntimeError(f"Failed to open stage: {USD_PATH}")

stage = omni.usd.get_context().get_stage()
maybe_build_terrain(stage)

if World.instance():
    World.instance().clear_instance()

world = World(stage_units_in_meters=1.0)
world.reset()

# 检查 prim 是否存在
target_prim = stage.GetPrimAtPath(ROBOT_PRIM_PATH)

print("\n===== CHECK ROBOT PRIM =====")
print("ROBOT_PRIM_PATH =", ROBOT_PRIM_PATH)
print("Exists:", target_prim.IsValid())
print("Type:", target_prim.GetTypeName() if target_prim.IsValid() else "INVALID")
print("===== END CHECK =====\n")

if not target_prim.IsValid():
    raise RuntimeError(f"Robot prim not found: {ROBOT_PRIM_PATH}")

# 包装 articulation
robot = SingleArticulation(prim_path=ROBOT_PRIM_PATH, name="my_car")
robot.initialize()

# 输出 DOF 信息
dof_names = robot.dof_names
print("==== Robot DOF Names ====")
for i, name in enumerate(dof_names):
    print(i, name)

# 构建 joint name -> index 映射
joint_name_to_index = {name: i for i, name in enumerate(dof_names)}

# 检查 joint 是否都存在
for name in WHEEL_JOINT_NAMES + BALL_JOINT_NAMES:
    if name not in joint_name_to_index:
        raise RuntimeError(f"Joint name not found in DOF list: {name}")

wheel_indices = [joint_name_to_index[name] for name in WHEEL_JOINT_NAMES]
ball_indices = [joint_name_to_index[name] for name in BALL_JOINT_NAMES]

print("Wheel joint indices:", wheel_indices)
print("Ball joint indices:", ball_indices)


# =========================
# 5. 初始目标
# =========================
current_positions = robot.get_joint_positions()
ball_targets = np.array([current_positions[i] for i in ball_indices], dtype=np.float64)
ball_position_cmd = ball_targets.copy()
wheel_velocity_cmd = np.zeros(len(wheel_indices), dtype=np.float64)


def clamp(x, low, high):
    return max(low, min(high, x))


def blend_command(current, target, alpha):
    return current + alpha * (target - current)


def signed_axis(positive_key, negative_key):
    positive = is_pressed(positive_key)
    negative = is_pressed(negative_key)
    if positive and not negative:
        return 1.0
    if negative and not positive:
        return -1.0
    return 0.0


def update_ball_joint_targets():
    global ball_targets

    for i, (increase_key, decrease_key) in enumerate(BALL_JOINT_KEY_BINDINGS):
        if is_pressed(increase_key):
            ball_targets[i] += BALL_JOINT_DELTA
        if is_pressed(decrease_key):
            ball_targets[i] -= BALL_JOINT_DELTA

    for i in range(len(ball_targets)):
        ball_targets[i] = clamp(ball_targets[i], -BALL_JOINT_LIMIT, BALL_JOINT_LIMIT)


def compute_wheel_velocity_targets():
    if is_pressed(carb.input.KeyboardInput.SPACE):
        return np.zeros(len(wheel_indices), dtype=np.float64)

    linear_axis = signed_axis(carb.input.KeyboardInput.W, carb.input.KeyboardInput.S)
    turn_axis = signed_axis(carb.input.KeyboardInput.A, carb.input.KeyboardInput.D)

    linear_velocity = WHEEL_LINEAR_SPEED * linear_axis
    turn_velocity = WHEEL_TURN_SPEED * turn_axis

    left_velocity = linear_velocity - turn_velocity
    right_velocity = linear_velocity + turn_velocity

    return np.array(
        [
            left_velocity,
            right_velocity,
            left_velocity,
            right_velocity,
            left_velocity,
            right_velocity,
        ],
        dtype=np.float64,
    )


print("\n==== Control Keys ====")
print("W / S                       : forward / backward")
print("A / D                       : differential left / right turn")
print("SPACE                       : zero wheel target")
print("NUMPAD_7 / NUMPAD_4        : SPM1 z +/-")
print("NUMPAD_8 / NUMPAD_5        : SPM1 y +/-")
print("NUMPAD_9 / NUMPAD_6        : SPM1 x +/-")
print("NUMPAD_1 / NUMPAD_DIVIDE   : SPM2 z +/-")
print("NUMPAD_2 / NUMPAD_MULTIPLY : SPM2 y +/-")
print("NUMPAD_3 / NUMPAD_SUBTRACT : SPM2 x +/-")
print(f"Active terrain              : {ARGS.terrain}")
print(f"Terrain seed                : {ARGS.terrain_seed}")
print(f"Wheel smoothing alpha       : {WHEEL_VELOCITY_SMOOTHING:.2f}")
print(f"Ball smoothing alpha        : {BALL_POSITION_SMOOTHING:.2f}")
print("ESC        : quit")
print("IMPORTANT  : click Isaac Sim window first; wheels use WASD, ball joints use the numeric keypad\n")


# =========================
# 6. 主循环
# =========================
try:
    while simulation_app.is_running():
        if is_pressed(carb.input.KeyboardInput.ESCAPE):
            break

        update_ball_joint_targets()
        ball_position_cmd = blend_command(ball_position_cmd, ball_targets, BALL_POSITION_SMOOTHING)
        wheel_velocity_targets = compute_wheel_velocity_targets()
        wheel_velocity_cmd = blend_command(wheel_velocity_cmd, wheel_velocity_targets, WHEEL_VELOCITY_SMOOTHING)

        # 轮子速度命令
        wheel_action = ArticulationAction(
            joint_velocities=np.array(wheel_velocity_cmd, dtype=np.float64),
            joint_indices=np.array(wheel_indices, dtype=np.int32),
        )
        robot.apply_action(wheel_action)

        # 球绞位置命令
        ball_action = ArticulationAction(
            joint_positions=np.array(ball_position_cmd, dtype=np.float64),
            joint_indices=np.array(ball_indices, dtype=np.int32),
        )
        robot.apply_action(ball_action)

        world.step(render=True)

finally:
    input_iface.unsubscribe_from_keyboard_events(keyboard, keyboard_sub)
    simulation_app.close()
