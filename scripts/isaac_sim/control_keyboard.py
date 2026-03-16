from isaacsim import SimulationApp

# 先启动 Isaac Sim，再导入其他 Isaac Sim 模块
simulation_app = SimulationApp({"headless": False})

from pathlib import Path

import numpy as np
import carb
import omni.appwindow
import omni.usd

from isaacsim.core.api.world import World
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.stage import open_stage
from isaacsim.core.utils.types import ArticulationAction


# =========================
# 1. 基本配置
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
USD_PATH = str(PROJECT_ROOT / "complete_car_alternative.usd")
ROBOT_PRIM_PATH = "/World/complete_car_alternative"

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
WHEEL_SPEED = 8.0
BALL_JOINT_DELTA = 0.01
BALL_JOINT_LIMIT = 0.8


# =========================
# 2. 键盘状态
# =========================
key_state = {}

def set_key(key_name, pressed):
    key_state[key_name] = pressed

def is_pressed(key_name):
    return key_state.get(key_name, False)


# =========================
# 3. 订阅键盘事件
# =========================
appwindow = omni.appwindow.get_default_app_window()
keyboard = appwindow.get_keyboard()
input_iface = carb.input.acquire_input_interface()

def on_keyboard_event(event, *args, **kwargs):
    key_name = event.input.name
    if event.type == carb.input.KeyboardEventType.KEY_PRESS:
        set_key(key_name, True)
    elif event.type == carb.input.KeyboardEventType.KEY_RELEASE:
        set_key(key_name, False)
    return True

keyboard_sub = input_iface.subscribe_to_keyboard_events(keyboard, on_keyboard_event)


# =========================
# 4. 创建世界并打开完整场景
# =========================
print(f"[INFO] Opening USD: {USD_PATH}")
ok = open_stage(USD_PATH)
print("[INFO] open_stage result:", ok)

if not ok:
    raise RuntimeError(f"Failed to open stage: {USD_PATH}")

if World.instance():
    World.instance().clear_instance()

world = World(stage_units_in_meters=1.0)
world.reset()

# 检查 prim 是否存在
stage = omni.usd.get_context().get_stage()
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


def clamp(x, low, high):
    return max(low, min(high, x))


def update_ball_joint_targets():
    global ball_targets

    # 第一个球绞
    if is_pressed("R"):
        ball_targets[0] += BALL_JOINT_DELTA
    if is_pressed("F"):
        ball_targets[0] -= BALL_JOINT_DELTA

    if is_pressed("T"):
        ball_targets[1] += BALL_JOINT_DELTA
    if is_pressed("G"):
        ball_targets[1] -= BALL_JOINT_DELTA

    if is_pressed("Y"):
        ball_targets[2] += BALL_JOINT_DELTA
    if is_pressed("H"):
        ball_targets[2] -= BALL_JOINT_DELTA

    # 第二个球绞
    if is_pressed("U"):
        ball_targets[3] += BALL_JOINT_DELTA
    if is_pressed("J"):
        ball_targets[3] -= BALL_JOINT_DELTA

    if is_pressed("I"):
        ball_targets[4] += BALL_JOINT_DELTA
    if is_pressed("K"):
        ball_targets[4] -= BALL_JOINT_DELTA

    if is_pressed("O"):
        ball_targets[5] += BALL_JOINT_DELTA
    if is_pressed("L"):
        ball_targets[5] -= BALL_JOINT_DELTA

    for i in range(len(ball_targets)):
        ball_targets[i] = clamp(ball_targets[i], -BALL_JOINT_LIMIT, BALL_JOINT_LIMIT)


def compute_wheel_velocities():
    v = 0.0
    if is_pressed("W"):
        v = WHEEL_SPEED
    elif is_pressed("S"):
        v = -WHEEL_SPEED

    if is_pressed("SPACE"):
        v = 0.0

    return np.array([v] * len(wheel_indices), dtype=np.float64)


print("\n==== Control Keys ====")
print("W/S        : forward/backward")
print("SPACE      : stop")
print("R/F T/G Y/H: SPM1 z/y/x +/-")
print("U/J I/K O/L: SPM2 z/y/x +/-")
print("ESC        : quit")
print("IMPORTANT  : click Isaac Sim window first to focus keyboard\n")


# =========================
# 6. 主循环
# =========================
try:
    while simulation_app.is_running():
        if is_pressed("ESCAPE"):
            break

        update_ball_joint_targets()
        wheel_vel_cmd = compute_wheel_velocities()

        # 轮子速度命令
        wheel_action = ArticulationAction(
            joint_velocities=wheel_vel_cmd,
            joint_indices=np.array(wheel_indices, dtype=np.int32),
        )
        robot.apply_action(wheel_action)

        # 球绞位置命令
        ball_action = ArticulationAction(
            joint_positions=np.array(ball_targets, dtype=np.float64),
            joint_indices=np.array(ball_indices, dtype=np.int32),
        )
        robot.apply_action(ball_action)

        world.step(render=True)

finally:
    input_iface.unsubscribe_from_keyboard_events(keyboard, keyboard_sub)
    simulation_app.close()  
