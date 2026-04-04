import argparse
import ctypes
import ctypes.util
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = next(parent for parent in _THIS_FILE.parents if (parent / "AGENTS.md").exists())
RL_PROJECT_ROOT = PROJECT_ROOT / "src" / "rl_lab" / "complete_car_rl_training"
ISAACLAB_SOURCE_ROOT = Path("/home/ubuntu/IsaacLab/source/isaaclab")
STAGE1_TERRAIN_PATH = (
    RL_PROJECT_ROOT
    / "complete_car_rl_training"
    / "tasks"
    / "manager_based"
    / "complete_car_rl_training"
    / "stage1_terrain.py"
)
DEFAULT_HEADLESS_FRAMES = 120
ISAAC_SIM_ROOT = Path(os.environ.get("ISAAC_SIM_ROOT", "/home/ubuntu/isaacsim"))
ISAAC_SIM_PYTHON = ISAAC_SIM_ROOT / "python.sh"
REEXEC_ENV_FLAG = "CONTROL_KEYBOARD_ISAACSIM_REEXEC"
FULL_GALLERY_ARG_CHOICES = {"stage1", "stage2", "both"}


def requested_full_gallery(argv: list[str]) -> bool:
    for index, arg in enumerate(argv):
        if arg == "--terrain" and index + 1 < len(argv):
            return argv[index + 1] in FULL_GALLERY_ARG_CHOICES
    return False


def maybe_reexec_via_standalone_isaacsim() -> None:
    if os.environ.get(REEXEC_ENV_FLAG) == "1":
        return
    if not ISAAC_SIM_PYTHON.is_file():
        return
    if os.environ.get("CONDA_PREFIX") is None:
        return
    if requested_full_gallery(sys.argv[1:]):
        return

    env = os.environ.copy()
    for key in (
        "CONDA_PREFIX",
        "CONDA_DEFAULT_ENV",
        "CONDA_EXE",
        "CONDA_PYTHON_EXE",
        "CONDA_SHLVL",
        "_CE_M",
        "_CE_CONDA",
    ):
        env.pop(key, None)
    env[REEXEC_ENV_FLAG] = "1"
    os.execvpe(str(ISAAC_SIM_PYTHON), [str(ISAAC_SIM_PYTHON), str(_THIS_FILE), *sys.argv[1:]], env)


maybe_reexec_via_standalone_isaacsim()

from isaacsim import SimulationApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Keyboard teleop for the complete car with optional terrain preview."
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without opening a window. Useful for smoke validation on remote or no-display shells.",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=0,
        help="If > 0, stop after this many simulation steps. In auto-headless mode, 0 uses a default smoke-run length.",
    )
    parser.add_argument(
        "--terrain",
        choices=[
            "none",
            "slope_ramp",
            "stairs_up",
            "discrete_obstacles",
            "gap",
            "single_gap",
            "stepping_stones",
            "single_bridge",
            "air_beams",
            "corridor",
            "stage1",
            "stage2",
            "both",
        ],
        default="slope_ramp",
        help="Optional terrain to build under the robot before teleop starts. 'stage1' loads the same full training terrain mesh used by RL; 'stage2' and 'both' keep using MGDP gallery previews.",
    )
    parser.add_argument(
        "--terrain-seed",
        type=int,
        default=7,
        help="Random seed for obstacle-like terrain tiles.",
    )
    return parser.parse_args()


ARGS = parse_args()


def has_usable_x_display() -> bool:
    if not sys.platform.startswith("linux"):
        return True

    display_name = os.environ.get("DISPLAY")
    if not display_name:
        return False

    try:
        probe = subprocess.run(
            ["xset", "q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=2.0,
        )
        if probe.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    x11_library = ctypes.util.find_library("X11")
    if x11_library is None:
        return False

    x11 = ctypes.cdll.LoadLibrary(x11_library)
    x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x11.XOpenDisplay.restype = ctypes.c_void_p
    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    x11.XCloseDisplay.restype = ctypes.c_int

    handle = x11.XOpenDisplay(display_name.encode("utf-8"))
    if not handle:
        return False

    x11.XCloseDisplay(handle)
    return True


RUN_HEADLESS = ARGS.headless or not has_usable_x_display()

# 先启动 Isaac Sim，再导入其他 Isaac Sim 模块
SIMULATION_LAUNCH_CONFIG = {"headless": RUN_HEADLESS}
if RUN_HEADLESS:
    SIMULATION_LAUNCH_CONFIG["hide_ui"] = True
    SIMULATION_LAUNCH_CONFIG["extra_args"] = ["--no-window", "--/app/window/hideUi=1"]
simulation_app = SimulationApp(SIMULATION_LAUNCH_CONFIG)

import numpy as np
import carb
import omni.appwindow
import omni.usd

from pxr import Gf, PhysxSchema, PhysicsSchemaTools, UsdPhysics, UsdShade
from isaacsim.core.api.world import World
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.stage import open_stage
from isaacsim.core.utils.types import ArticulationAction


# =========================
# 1. 基本配置
# =========================
USD_PATH = str(PROJECT_ROOT / "USD" / "complete_car.usd")
ROBOT_PRIM_PATH = "/World/complete_car_alternative"
TERRAIN_ROOT_PATH = "/World/terrain_preview"
TRAINING_TERRAIN_ROOT_PATH = "/World/terrain"
TERRAIN_ORIGIN = (-1.0, 0.0, 0.0)
GROUND_PRIM_PATH = "/World/defaultGroundPlane"
GROUND_COLLISION_PRIM_CANDIDATES = [
    "/World/defaultGroundPlane/GroundPlane/CollisionPlane",
    "/World/defaultGroundPlane/CollisionPlane",
    "/World/defaultGroundPlane",
]
CONTROL_PHYSICS_MATERIAL_PATH = "/World/PhysicsMaterials/control_keyboard_material"
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
WHEEL_COLLISION_ROOTS = [
    f"{ROBOT_PRIM_PATH}/body_car_wheel_left/collisions",
    f"{ROBOT_PRIM_PATH}/body_car_wheel_right/collisions",
    f"{ROBOT_PRIM_PATH}/head_car_wheel_left/collisions",
    f"{ROBOT_PRIM_PATH}/head_car_wheel_right/collisions",
    f"{ROBOT_PRIM_PATH}/tail_car_wheel_left/collisions",
    f"{ROBOT_PRIM_PATH}/tail_car_wheel_right/collisions",
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

# 训练同构控制参数
TRAINING_PHYSICS_DT = 1.0 / 120.0  # 物理仿真步长，对齐训练环境的 sim.dt
TRAINING_RENDER_DT = 1.0 / 60.0  # 渲染刷新步长，交互窗口下约 60 Hz
TRAINING_ACTION_DECIMATION = 2  # 每 2 个物理步更新 1 次控制目标，对齐训练 decimation
TRAINING_POLICY_DT = TRAINING_PHYSICS_DT * TRAINING_ACTION_DECIMATION  # 等效策略控制周期

TRAINING_BALL_ACTION_SCALE = 0.25  # 球铰 raw action 到位置目标的缩放系数，单位 rad
TRAINING_WHEEL_ACTION_SCALE = 8.0  # 轮子 raw action 到速度目标的缩放系数，单位 rad/s

TRAINING_BALL_STIFFNESS = 80.0  # 球铰位置控制刚度，对齐训练中的 implicit actuator stiffness
TRAINING_BALL_DAMPING = 8.0  # 球铰位置控制阻尼，对齐训练中的 implicit actuator damping
TRAINING_BALL_EFFORT_LIMIT = 120.0  # 球铰关节最大驱动力/力矩限制
TRAINING_BALL_VELOCITY_LIMIT = 6.0  # 球铰关节物理速度上限，单位 rad/s

TRAINING_WHEEL_STIFFNESS = 0.0  # 轮子速度控制刚度；速度驱动模式下保持为 0
TRAINING_WHEEL_DAMPING = 10.0  # 轮子速度控制阻尼，对齐训练中的 implicit actuator damping
TRAINING_WHEEL_EFFORT_LIMIT = 80.0  # 轮子关节最大驱动力/力矩限制
TRAINING_WHEEL_VELOCITY_LIMIT = 20.0  # 轮子关节物理速度上限，单位 rad/s

BALL_JOINT_ACTION_DELTA = 0.08  # 每次按键对球铰 raw action 的增量步长
WHEEL_ACTION_LIMIT = 1.0  # 轮子 raw action 的限幅范围，最终会映射到 [-8, 8] rad/s
STATIC_FRICTION = 0.5  # 共享物理材质的静摩擦系数
DYNAMIC_FRICTION = 0.5  # 共享物理材质的动摩擦系数
GROUND_SIZE = 50.0  # 无地形模式下默认 ground plane 的尺寸，单位 m

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
appwindow = None
keyboard = None
input_iface = None
keyboard_sub = None
terrain_spawn_position = None

if not RUN_HEADLESS:
    appwindow = omni.appwindow.get_default_app_window()
    if appwindow is None:
        print("[WARN] Isaac Sim did not expose a default window. Switching to headless smoke mode.")
        RUN_HEADLESS = True
    else:
        keyboard = appwindow.get_keyboard()
        if keyboard is None:
            print("[WARN] Isaac Sim window exists but keyboard interface is unavailable. Switching to headless smoke mode.")
            RUN_HEADLESS = True
        else:
            input_iface = carb.input.acquire_input_interface()


def on_keyboard_event(event, *args, **kwargs):
    key_code = event.input
    if event.type == carb.input.KeyboardEventType.KEY_PRESS:
        set_key(key_code, True)
    elif event.type == carb.input.KeyboardEventType.KEY_RELEASE:
        set_key(key_code, False)
    return True


if input_iface is not None and keyboard is not None:
    keyboard_sub = input_iface.subscribe_to_keyboard_events(keyboard, on_keyboard_event)


def load_stage1_terrain_module():
    """Load stage1_terrain.py directly to avoid importing the full task package tree."""
    spec = importlib.util.spec_from_file_location("stage1_terrain_local", STAGE1_TERRAIN_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load stage1 terrain module from {STAGE1_TERRAIN_PATH}")

    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


def ensure_isaaclab_source_on_path() -> None:
    if str(ISAACLAB_SOURCE_ROOT) not in sys.path:
        sys.path.append(str(ISAACLAB_SOURCE_ROOT))


def build_training_stage1_mesh():
    ensure_isaaclab_source_on_path()
    stage1_terrain_module = load_stage1_terrain_module()
    import trimesh

    terrain_cfg = stage1_terrain_module.Stage1TerrainCfg()
    terrain_data = stage1_terrain_module.build_stage1_terrain_data(terrain_cfg)
    terrain_mesh = trimesh.Trimesh(vertices=terrain_data.vertices, faces=terrain_data.faces)
    terrain_mesh = terrain_mesh.copy()
    terrain_mesh.vertices[:, 0] -= terrain_cfg.border_size
    terrain_mesh.vertices[:, 1] -= terrain_cfg.border_size

    spawn_position = terrain_data.env_origins[0, 0].astype(np.float64).copy()
    spawn_position[2] += 0.30
    return terrain_cfg, terrain_mesh, spawn_position


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
    global terrain_spawn_position

    if ARGS.terrain == "none":
        print("[INFO] Terrain preview disabled for control_keyboard.py")
        terrain_spawn_position = None
        return None

    deactivate_default_ground(stage)
    terrain_spawn_position = None

    if ARGS.terrain == "stage1":
        ensure_isaaclab_source_on_path()
        import isaaclab.sim as sim_utils
        from isaaclab.terrains.utils import create_prim_from_mesh

        terrain_cfg, terrain_mesh, terrain_spawn_position = build_training_stage1_mesh()
        if stage.GetPrimAtPath(TRAINING_TERRAIN_ROOT_PATH).IsValid():
            stage.RemovePrim(TRAINING_TERRAIN_ROOT_PATH)

        create_prim_from_mesh(
            f"{TRAINING_TERRAIN_ROOT_PATH}/stage1",
            terrain_mesh,
            physics_material=sim_utils.RigidBodyMaterialCfg(
                friction_combine_mode="multiply",
                restitution_combine_mode="multiply",
                static_friction=1.0,
                dynamic_friction=1.0,
                restitution=0.0,
            ),
        )
        print(
            "[INFO] Built training stage1 terrain mesh:",
            f"root={TRAINING_TERRAIN_ROOT_PATH}",
            f"spawn_position={terrain_spawn_position.tolist()}",
            f"terrain_size=({terrain_cfg.total_rows}, {terrain_cfg.total_cols})",
        )
        return f"{TRAINING_TERRAIN_ROOT_PATH}/stage1/mesh"

    if ARGS.terrain in FULL_GALLERY_ARG_CHOICES:
        from terrain_preview.mgdp_gallery_builder import build_mgdp_gallery

        summary = build_mgdp_gallery(
            stage=stage,
            gallery=ARGS.terrain,
            root_path=TERRAIN_ROOT_PATH,
            seed=ARGS.terrain_seed,
            curriculum_envs=64,
            include_markers=False,
        )
        print(
            "[INFO] Built MGDP terrain gallery:",
            summary.gallery,
            f"(bounds_min={summary.min_corner.tolist()}, bounds_max={summary.max_corner.tolist()})",
        )
        print(
            "[INFO] Robot origin aligned near gallery spawn hint:",
            summary.spawn_origin.tolist(),
        )
        terrain_spawn_position = np.asarray(summary.spawn_origin, dtype=np.float64)
        terrain_spawn_position[2] += 0.30
        return TERRAIN_ROOT_PATH

    from terrain_preview.terrain_builder import build_single_tile

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
    return TERRAIN_ROOT_PATH


def ensure_shared_physics_material(stage):
    material = UsdShade.Material.Define(stage, CONTROL_PHYSICS_MATERIAL_PATH)
    material_prim = material.GetPrim()

    material_api = UsdPhysics.MaterialAPI.Apply(material_prim)
    material_api.CreateStaticFrictionAttr(STATIC_FRICTION)
    material_api.CreateDynamicFrictionAttr(DYNAMIC_FRICTION)

    physx_material_api = PhysxSchema.PhysxMaterialAPI.Apply(material_prim)
    physx_material_api.CreateFrictionCombineModeAttr("multiply")

    return material


def bind_physics_material(stage, prim_path, material):
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        return False

    binding_api = UsdShade.MaterialBindingAPI.Apply(prim)
    binding_api.Bind(material, UsdShade.Tokens.weakerThanDescendants, "physics")
    return True


def ensure_ground_and_friction(stage, terrain_bind_path: str | None):
    material = ensure_shared_physics_material(stage)

    if ARGS.terrain == "none":
        ground_prim = stage.GetPrimAtPath(GROUND_PRIM_PATH)
        if not ground_prim.IsValid():
            PhysicsSchemaTools.addGroundPlane(
                stage,
                GROUND_PRIM_PATH,
                "Z",
                GROUND_SIZE,
                Gf.Vec3f(0.0, 0.0, 0.0),
                Gf.Vec3f(0.45, 0.45, 0.45),
            )
            print(
                "[INFO] Added ground plane:",
                GROUND_PRIM_PATH,
                f"(size={GROUND_SIZE:.1f}, static_friction={STATIC_FRICTION}, dynamic_friction={DYNAMIC_FRICTION})",
            )

        ground_bound = False
        for prim_path in GROUND_COLLISION_PRIM_CANDIDATES:
            ground_bound = bind_physics_material(stage, prim_path, material) or ground_bound
        if not ground_bound:
            print("[WARN] Ground plane was created but no collision prim was found for physics material binding.")
    else:
        if terrain_bind_path is not None and bind_physics_material(stage, terrain_bind_path, material):
            print("[INFO] Applied shared terrain friction material:", terrain_bind_path)
        else:
            print("[WARN] Terrain root was not found for physics material binding:", terrain_bind_path)

    bound_wheels = []
    for prim_path in WHEEL_COLLISION_ROOTS:
        if bind_physics_material(stage, prim_path, material):
            bound_wheels.append(prim_path)

    if bound_wheels:
        print("[INFO] Applied shared wheel/ground friction material:")
        for prim_path in bound_wheels:
            print("  ", prim_path)
    else:
        print("[WARN] No wheel collision roots were found for friction material binding.")


# =========================
# 4. 创建世界并打开完整场景
# =========================
print(f"[INFO] Opening USD: {USD_PATH}")
ok = open_stage(USD_PATH)
print("[INFO] open_stage result:", ok)

if not ok:
    raise RuntimeError(f"Failed to open stage: {USD_PATH}")

stage = omni.usd.get_context().get_stage()
terrain_bind_path = maybe_build_terrain(stage)
ensure_ground_and_friction(stage, terrain_bind_path)

if World.instance():
    World.instance().clear_instance()

world = World(
    physics_dt=TRAINING_PHYSICS_DT,
    rendering_dt=TRAINING_RENDER_DT,
    stage_units_in_meters=1.0,
)
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

robot = SingleArticulation(prim_path=ROBOT_PRIM_PATH, name="my_car")
dof_names = []
joint_name_to_index = {}
wheel_indices = []
ball_indices = []


# =========================
# 5. 初始目标
# =========================
ball_default_positions = np.zeros(len(BALL_JOINT_NAMES), dtype=np.float64)
wheel_default_velocities = np.zeros(len(WHEEL_JOINT_NAMES), dtype=np.float64)
ball_action_raw = np.zeros(len(BALL_JOINT_NAMES), dtype=np.float64)
ball_position_cmd = np.zeros(len(BALL_JOINT_NAMES), dtype=np.float64)
wheel_action_raw = np.zeros(len(WHEEL_JOINT_NAMES), dtype=np.float64)
wheel_velocity_cmd = np.zeros(len(WHEEL_JOINT_NAMES), dtype=np.float64)


def clear_all_keys():
    key_state.clear()


def full_joint_value_array(joint_indices, value):
    return np.full((1, len(joint_indices)), value, dtype=np.float32)


def configure_training_drive_parameters() -> None:
    articulation_view = robot._articulation_view

    articulation_view.set_gains(
        kps=full_joint_value_array(ball_indices, TRAINING_BALL_STIFFNESS),
        kds=full_joint_value_array(ball_indices, TRAINING_BALL_DAMPING),
        joint_indices=np.array(ball_indices, dtype=np.int32),
    )
    articulation_view.set_gains(
        kps=full_joint_value_array(wheel_indices, TRAINING_WHEEL_STIFFNESS),
        kds=full_joint_value_array(wheel_indices, TRAINING_WHEEL_DAMPING),
        joint_indices=np.array(wheel_indices, dtype=np.int32),
    )
    articulation_view.set_max_efforts(
        values=full_joint_value_array(ball_indices, TRAINING_BALL_EFFORT_LIMIT),
        joint_indices=np.array(ball_indices, dtype=np.int32),
    )
    articulation_view.set_max_efforts(
        values=full_joint_value_array(wheel_indices, TRAINING_WHEEL_EFFORT_LIMIT),
        joint_indices=np.array(wheel_indices, dtype=np.int32),
    )
    articulation_view.set_max_joint_velocities(
        values=full_joint_value_array(ball_indices, TRAINING_BALL_VELOCITY_LIMIT),
        joint_indices=np.array(ball_indices, dtype=np.int32),
    )
    articulation_view.set_max_joint_velocities(
        values=full_joint_value_array(wheel_indices, TRAINING_WHEEL_VELOCITY_LIMIT),
        joint_indices=np.array(wheel_indices, dtype=np.int32),
    )


def initialize_robot_handles(*, reset_targets: bool, reason: str) -> None:
    global dof_names, joint_name_to_index, wheel_indices, ball_indices
    global ball_default_positions, wheel_default_velocities
    global ball_action_raw, ball_position_cmd, wheel_action_raw, wheel_velocity_cmd

    robot.initialize()
    dof_names = list(robot.dof_names)

    print(f"[INFO] Robot articulation initialized ({reason}).")
    print("==== Robot DOF Names ====")
    for i, name in enumerate(dof_names):
        print(i, name)

    joint_name_to_index = {name: i for i, name in enumerate(dof_names)}
    for name in WHEEL_JOINT_NAMES + BALL_JOINT_NAMES:
        if name not in joint_name_to_index:
            raise RuntimeError(f"Joint name not found in DOF list: {name}")

    wheel_indices = [joint_name_to_index[name] for name in WHEEL_JOINT_NAMES]
    ball_indices = [joint_name_to_index[name] for name in BALL_JOINT_NAMES]
    print("Wheel joint indices:", wheel_indices)
    print("Ball joint indices:", ball_indices)

    configure_training_drive_parameters()

    if terrain_spawn_position is not None:
        robot.set_world_pose(position=np.asarray(terrain_spawn_position, dtype=np.float64))
        print("[INFO] Moved robot to terrain spawn position:", terrain_spawn_position.tolist())

    if reset_targets:
        default_joint_state = robot.get_joints_default_state()
        ball_default_positions = np.array(
            [default_joint_state.positions[i] for i in ball_indices],
            dtype=np.float64,
        )
        wheel_default_velocities = np.array(
            [default_joint_state.velocities[i] for i in wheel_indices],
            dtype=np.float64,
        )
        ball_action_raw = np.zeros(len(ball_indices), dtype=np.float64)
        wheel_action_raw = np.zeros(len(wheel_indices), dtype=np.float64)
        ball_position_cmd = ball_default_positions.copy()
        wheel_velocity_cmd = wheel_default_velocities.copy()
        clear_all_keys()
        print("[INFO] Control actions and key state were reset to the training default offsets.")
        print(
            "[INFO] Training-equivalent control profile applied:",
            f"ball(pos): scale={TRAINING_BALL_ACTION_SCALE}, stiffness={TRAINING_BALL_STIFFNESS}, damping={TRAINING_BALL_DAMPING}, effort_limit={TRAINING_BALL_EFFORT_LIMIT}, velocity_limit={TRAINING_BALL_VELOCITY_LIMIT}",
        )
        print(
            "[INFO] Training-equivalent control profile applied:",
            f"wheel(vel): scale={TRAINING_WHEEL_ACTION_SCALE}, stiffness={TRAINING_WHEEL_STIFFNESS}, damping={TRAINING_WHEEL_DAMPING}, effort_limit={TRAINING_WHEEL_EFFORT_LIMIT}, velocity_limit={TRAINING_WHEEL_VELOCITY_LIMIT}",
        )


initialize_robot_handles(reset_targets=True, reason="initial startup")


def clamp(x, low, high):
    return max(low, min(high, x))


def signed_axis(positive_key, negative_key):
    positive = is_pressed(positive_key)
    negative = is_pressed(negative_key)
    if positive and not negative:
        return 1.0
    if negative and not positive:
        return -1.0
    return 0.0


def update_ball_joint_actions():
    global ball_action_raw

    for i, (increase_key, decrease_key) in enumerate(BALL_JOINT_KEY_BINDINGS):
        if is_pressed(increase_key):
            ball_action_raw[i] += BALL_JOINT_ACTION_DELTA
        if is_pressed(decrease_key):
            ball_action_raw[i] -= BALL_JOINT_ACTION_DELTA


def compute_ball_position_targets():
    return ball_default_positions + ball_action_raw * TRAINING_BALL_ACTION_SCALE


def compute_wheel_velocity_targets():
    if is_pressed(carb.input.KeyboardInput.SPACE):
        wheel_action_raw[:] = 0.0
        return wheel_default_velocities.copy()

    linear_axis = signed_axis(carb.input.KeyboardInput.W, carb.input.KeyboardInput.S)
    turn_axis = signed_axis(carb.input.KeyboardInput.A, carb.input.KeyboardInput.D)

    left_action = clamp(linear_axis - turn_axis, -WHEEL_ACTION_LIMIT, WHEEL_ACTION_LIMIT)
    right_action = clamp(linear_axis + turn_axis, -WHEEL_ACTION_LIMIT, WHEEL_ACTION_LIMIT)

    wheel_action_raw[:] = np.array(
        [
            left_action,
            right_action,
            left_action,
            right_action,
            left_action,
            right_action,
        ],
        dtype=np.float64,
    )

    return wheel_default_velocities + wheel_action_raw * TRAINING_WHEEL_ACTION_SCALE


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
print(f"Window mode                 : {'headless smoke run' if RUN_HEADLESS else 'interactive teleop'}")
print(f"Physics dt                  : {TRAINING_PHYSICS_DT:.6f} s")
print(f"Render dt                   : {TRAINING_RENDER_DT:.6f} s")
print(f"Action decimation           : {TRAINING_ACTION_DECIMATION}")
print(f"Action update dt            : {TRAINING_POLICY_DT:.6f} s")
print(f"Ball raw action range       : unbounded -> target offset = raw_action * {TRAINING_BALL_ACTION_SCALE:.2f} rad")
print(f"Wheel raw action range      : [-{WHEEL_ACTION_LIMIT:.1f}, {WHEEL_ACTION_LIMIT:.1f}] -> target velocity [-{TRAINING_WHEEL_ACTION_SCALE:.1f}, {TRAINING_WHEEL_ACTION_SCALE:.1f}] rad/s")
print(f"Wheel physx velocity limit  : {TRAINING_WHEEL_VELOCITY_LIMIT:.1f} rad/s")
if RUN_HEADLESS:
    effective_frames = ARGS.frames if ARGS.frames > 0 else DEFAULT_HEADLESS_FRAMES
    print(f"Smoke frames                : {effective_frames}")
print("ESC        : quit")
print("IMPORTANT  : click Isaac Sim window first; wheels use WASD, ball joints use the numeric keypad\n")


# =========================
# 6. 主循环
# =========================
def apply_current_command() -> None:
    wheel_action = ArticulationAction(
        joint_velocities=np.array(wheel_velocity_cmd, dtype=np.float64),
        joint_indices=np.array(wheel_indices, dtype=np.int32),
    )
    robot.apply_action(wheel_action)

    ball_action = ArticulationAction(
        joint_positions=np.array(ball_position_cmd, dtype=np.float64),
        joint_indices=np.array(ball_indices, dtype=np.int32),
    )
    robot.apply_action(ball_action)


try:
    if RUN_HEADLESS:
        smoke_frames = ARGS.frames if ARGS.frames > 0 else DEFAULT_HEADLESS_FRAMES
        print(f"[INFO] Running headless smoke validation for {smoke_frames} frames.")
        physics_step_counter = 0
        for _ in range(smoke_frames):
            if physics_step_counter % TRAINING_ACTION_DECIMATION == 0:
                update_ball_joint_actions()
                ball_position_cmd = compute_ball_position_targets()
                wheel_velocity_cmd = compute_wheel_velocity_targets()
            apply_current_command()
            world.step(render=False)
            physics_step_counter += 1
        print("[INFO] Headless smoke validation finished successfully.")
    else:
        needs_reinitialize_after_stop = False
        last_playing_state = world.is_playing()
        physics_step_counter = 0
        while simulation_app.is_running():
            if is_pressed(carb.input.KeyboardInput.ESCAPE):
                break

            is_playing = world.is_playing()
            if not is_playing:
                if last_playing_state:
                    clear_all_keys()
                    if world.current_time_step_index == 0:
                        needs_reinitialize_after_stop = True
                        print("[INFO] Timeline stopped. Waiting for Play to reinitialize teleop control.")
                    else:
                        print("[INFO] Timeline paused. Teleop commands will resume when Play continues physics.")
                last_playing_state = False
                world.step(render=True)
                continue

            if needs_reinitialize_after_stop or (not last_playing_state) or world.current_time_step_index == 0:
                print("[INFO] Timeline entered Play. Resetting world and reinitializing articulation handles.")
                world.reset()
                initialize_robot_handles(reset_targets=True, reason="timeline play/resume")
                needs_reinitialize_after_stop = False
                physics_step_counter = 0

            last_playing_state = True

            if physics_step_counter % TRAINING_ACTION_DECIMATION == 0:
                update_ball_joint_actions()
                ball_position_cmd = compute_ball_position_targets()
                wheel_velocity_cmd = compute_wheel_velocity_targets()

            apply_current_command()
            world.step(render=True)
            physics_step_counter += 1

finally:
    if input_iface is not None and keyboard is not None and keyboard_sub is not None:
        input_iface.unsubscribe_from_keyboard_events(keyboard, keyboard_sub)
    simulation_app.close()
