import carb
import omni.appwindow
import numpy as np

from omni.isaac.core import World
from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.types import ArticulationAction
from omni.isaac.core.utils.prims import get_prim_at_path

# ================= 用户配置 =================
ROBOT_PATH = "/World/complete_car_alternative/body_car_chassis"

WHEEL_JOINTS = [
    "body_car_wheel_left_joint",
    "body_car_wheel_right_joint",
    "head_car_wheel_left_joint",
    "head_car_wheel_right_joint",
    "tail_car_wheel_left_joint",
    "tail_car_wheel_right_joint",
]

# 假设 z=yaw, y=pitch, x=roll (请根据实际 USD 轴向确认)
FRONT_HINGE = [
    "spm1_platform_joint_z",
    "spm1_platform_joint_y",
    "spm1_platform_joint_x",
]

REAR_HINGE = [
    "spm2_platform_joint_z",
    "spm2_platform_joint_y",
    "spm2_platform_joint_x",
]

WHEEL_SPEED = 10.0
HINGE_SPEED = 0.05

# ========= 全局状态 (防重复执行重置) =========
if "command_state" not in globals():
    command_state = {
        "forward": 0.0, "turn": 0.0,
        "front_pitch": 0.0, "front_yaw": 0.0, "front_roll": 0.0,
        "rear_pitch": 0.0, "rear_yaw": 0.0, "rear_roll": 0.0,
    }
if "current_hinge_positions" not in globals():
    current_hinge_positions = np.zeros(6)
if "keyboard_sub" not in globals():
    keyboard_sub = None

# =========== 键盘事件处理 ===========
def keyboard_event_handler(event, *args, **kwargs):
    global command_state

    if event.type == carb.input.KeyboardEventType.KEY_PRESSED:
        active = 1
    elif event.type == carb.input.KeyboardEventType.KEY_RELEASED:
        active = 0
    else:
        return True

    # 前/后
    if event.input == carb.input.KeyboardInput.W: command_state["forward"] = WHEEL_SPEED * active
    elif event.input == carb.input.KeyboardInput.S: command_state["forward"] = -WHEEL_SPEED * active

    # 差速转向
    elif event.input == carb.input.KeyboardInput.A: command_state["turn"] = -(WHEEL_SPEED / 2.0) * active
    elif event.input == carb.input.KeyboardInput.D: command_state["turn"] = (WHEEL_SPEED / 2.0) * active

    # 前车姿态
    elif event.input == carb.input.KeyboardInput.I: command_state["front_pitch"] = HINGE_SPEED * active
    elif event.input == carb.input.KeyboardInput.K: command_state["front_pitch"] = -HINGE_SPEED * active
    elif event.input == carb.input.KeyboardInput.J: command_state["front_yaw"] = HINGE_SPEED * active
    elif event.input == carb.input.KeyboardInput.L: command_state["front_yaw"] = -HINGE_SPEED * active
    elif event.input == carb.input.KeyboardInput.U: command_state["front_roll"] = HINGE_SPEED * active
    elif event.input == carb.input.KeyboardInput.O: command_state["front_roll"] = -HINGE_SPEED * active

    # 后车姿态
    elif event.input == carb.input.KeyboardInput.T: command_state["rear_pitch"] = HINGE_SPEED * active
    elif event.input == carb.input.KeyboardInput.G: command_state["rear_pitch"] = -HINGE_SPEED * active
    elif event.input == carb.input.KeyboardInput.F: command_state["rear_yaw"] = HINGE_SPEED * active
    elif event.input == carb.input.KeyboardInput.H: command_state["rear_yaw"] = -HINGE_SPEED * active
    elif event.input == carb.input.KeyboardInput.R: command_state["rear_roll"] = HINGE_SPEED * active
    elif event.input == carb.input.KeyboardInput.Y: command_state["rear_roll"] = -HINGE_SPEED * active

    return True

# =========== 运行控制逻辑 ===========
# ========= 运行控制逻辑 ===========
def start_teleop():
    global keyboard_sub, current_hinge_positions

    # 1. 安全初始化 World
    world = World.instance()
    if world is None:
        print("❌ [错误] World 初始化失败！请检查是否正确启动了 Isaac Sim。")
        return
    
    # 启动物理引擎，确保仿真处于播放状态
    if not world.is_playing():
        world.stop()
        world.play()

    # 2. 检查模型并注册
    if not get_prim_at_path(ROBOT_PATH):
        print(f"❌ [错误] 找不到模型！请确保 Isaac Sim 场景中存在: {ROBOT_PATH}")
        return
        
    if not world.scene.object_exists("my_rover"):
        my_robot = Articulation(prim_path=ROBOT_PATH, name="my_rover")
        world.scene.add(my_robot)
    else:
        my_robot = world.scene.get_object("my_rover")
    
    all_joint_names = WHEEL_JOINTS + FRONT_HINGE + REAR_HINGE
    try:
        joint_indices = [my_robot.get_dof_index(name) for name in all_joint_names]
    except Exception as e:
        print(f"❌ [错误] 找不到关节!请检查 WHEEL_JOINTS 和 HINGE 列表名称是否正确。详细错误: {e}")
        return

    # 3. 物理回调
    def on_physics_step(step_size):
        if not world.is_playing():
            return
            
        left_speed = command_state["forward"] + command_state["turn"]
        right_speed = command_state["forward"] - command_state["turn"]
        
        # 修复：确保速度数组与 [左, 右, 左, 右, 左, 右] 的顺序一一对应
        wheel_vel_targets = [left_speed, right_speed, left_speed, right_speed, left_speed, right_speed]
        
        # 修复：按具体索引累加角度 (前车 0,1,2; 后车 3,4,5)
        current_hinge_positions[0] += command_state["front_yaw"]
        current_hinge_positions[1] += command_state["front_pitch"]
        current_hinge_positions[2] += command_state["front_roll"]
        current_hinge_positions[3] += command_state["rear_yaw"]
        current_hinge_positions[4] += command_state["rear_pitch"]
        current_hinge_positions[5] += command_state["rear_roll"]

        # 构造安全下发指令的列表 (使用 np.nan 忽略不控制的轴)
        vel_targets = np.full(12, np.nan)
        pos_targets = np.full(12, np.nan)

        for i in range(6): vel_targets[i] = wheel_vel_targets[i]
        for i in range(6): pos_targets[i + 6] = current_hinge_positions[i]

        action = ArticulationAction(
            joint_indices=joint_indices,
            velocity_targets=vel_targets.tolist(),
            position_targets=pos_targets.tolist()
        )
        my_robot.apply_action(action)

    # 4. 注册监听与回调
    appwindow = omni.appwindow.get_default_app_window()
    input_interface = carb.input.acquire_input_interface()
    keyboard = appwindow.get_keyboard()
    
    if keyboard_sub:
        input_interface.unsubscribe_to_keyboard_events(keyboard, keyboard_sub)
    if world.physics_callback_exists("rover_teleop"):
        world.remove_physics_callback("rover_teleop")
        
    keyboard_sub = input_interface.subscribe_to_keyboard_events(keyboard, keyboard_event_handler)
    world.add_physics_callback("rover_teleop", on_physics_step)
    
    print("✅ [成功] 交互式控制脚本已推送到 Isaac Sim！")
    print("👉 焦点激活提示：请在 Isaac Sim 中点击一下 3D 视口(Viewport)的空白处，然后按下 W 键测试。")

start_teleop()
