from isaacsim import SimulationApp

# Start Isaac Sim before importing other Isaac Sim modules.
simulation_app = SimulationApp({"headless": False})

from pathlib import Path
from datetime import datetime
import csv
import math

import numpy as np
import carb
import omni.appwindow
import omni.usd
from pxr import UsdGeom

from isaacsim.core.api.world import World
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.stage import open_stage
from isaacsim.core.utils.types import ArticulationAction

from IK_model import IK_3RRR_Spherical


# =========================
# 1. Basic configuration
# =========================
_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = next(parent for parent in _THIS_FILE.parents if (parent / "AGENTS.md").exists())
USD_PATH = str(PROJECT_ROOT / "USD" / "complete_car.usd")
ROBOT_PRIM_PATH = "/World/complete_car_final"
FRONT_BASE_REF_PRIM_PATH = f"{ROBOT_PRIM_PATH}/spm1_base/spm1_base_ref"
FRONT_PLATFORM_PRIM_PATH = f"{ROBOT_PRIM_PATH}/spm1_platform"
REAR_BASE_REF_PRIM_PATH = f"{ROBOT_PRIM_PATH}/spm2_base/spm2_base_ref"
REAR_PLATFORM_PRIM_PATH = f"{ROBOT_PRIM_PATH}/spm2_platform"
LOG_DIR = PROJECT_ROOT / "results" / "ik_keyboard_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / f"ik_keyboard_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

WHEEL_JOINT_NAMES = [
    "body_car_wheel_left_joint",
    "body_car_wheel_right_joint",
    "head_car_wheel_left_joint",
    "head_car_wheel_right_joint",
    "tail_car_wheel_left_joint",
    "tail_car_wheel_right_joint",
]

BALL_JOINT_NAMES = [
    "spm1_platform_joint_z",
    "spm1_platform_joint_y",
    "spm1_platform_joint_x",
    "spm2_platform_joint_z",
    "spm2_platform_joint_y",
    "spm2_platform_joint_x",
]

WHEEL_SPEED = 8.0
POSE_STEP = np.deg2rad(0.5)
POSE_LIMIT = np.deg2rad(12.0)
POSE_CMD_ALPHA = 0.20
JOINT_CMD_ALPHA = 0.35
PRINT_EVERY = 30
ZERO_CALIBRATION_SETTLE_STEPS = 240
ZERO_CALIBRATION_SAMPLE_STEPS = 120

# First-pass assumption for the IK-to-sim sign mapping.
# Zero offsets are calibrated at startup from the current sim joint steady state.
IK_SIGNS_FRONT = (1, 1, 1)
IK_SIGNS_REAR = (1, 1, 1)


# =========================
# 2. Keyboard state
# =========================
key_state = {}


def set_key(key_name, pressed):
    key_state[key_name] = pressed


def is_pressed(key_name):
    return key_state.get(key_name, False)


# =========================
# 3. Subscribe to keyboard
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
# 4. Create world and open stage
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

stage = omni.usd.get_context().get_stage()
target_prim = stage.GetPrimAtPath(ROBOT_PRIM_PATH)

print("\n===== CHECK ROBOT PRIM =====")
print("ROBOT_PRIM_PATH =", ROBOT_PRIM_PATH)
print("Exists:", target_prim.IsValid())
print("Type:", target_prim.GetTypeName() if target_prim.IsValid() else "INVALID")
print("===== END CHECK =====\n")

if not target_prim.IsValid():
    raise RuntimeError(f"Robot prim not found: {ROBOT_PRIM_PATH}")

front_base_ref_prim = stage.GetPrimAtPath(FRONT_BASE_REF_PRIM_PATH)
front_platform_prim = stage.GetPrimAtPath(FRONT_PLATFORM_PRIM_PATH)
rear_base_ref_prim = stage.GetPrimAtPath(REAR_BASE_REF_PRIM_PATH)
rear_platform_prim = stage.GetPrimAtPath(REAR_PLATFORM_PRIM_PATH)

for prim_path, prim in (
    (FRONT_BASE_REF_PRIM_PATH, front_base_ref_prim),
    (FRONT_PLATFORM_PRIM_PATH, front_platform_prim),
    (REAR_BASE_REF_PRIM_PATH, rear_base_ref_prim),
    (REAR_PLATFORM_PRIM_PATH, rear_platform_prim),
):
    if not prim.IsValid():
        raise RuntimeError(f"Prim not found: {prim_path}")

robot = SingleArticulation(prim_path=ROBOT_PRIM_PATH, name="my_car")
robot.initialize()

xform_cache = UsdGeom.XformCache()

dof_names = robot.dof_names
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
print("Front pose reference:", FRONT_BASE_REF_PRIM_PATH, "->", FRONT_PLATFORM_PRIM_PATH)
print("Rear pose reference :", REAR_BASE_REF_PRIM_PATH, "->", REAR_PLATFORM_PRIM_PATH)
print(f"[INFO] Logging IK snapshots to: {LOG_PATH}")


# =========================
# 5. IK state and command state
# =========================
ik_solver = IK_3RRR_Spherical()
q_home = np.array(ik_solver.compute_home_offsets(), dtype=np.float64)

front_rpy_raw = np.zeros(3, dtype=np.float64)
rear_rpy_raw = np.zeros(3, dtype=np.float64)
front_rpy_bias = np.zeros(3, dtype=np.float64)
rear_rpy_bias = np.zeros(3, dtype=np.float64)
front_rpy_meas = np.zeros(3, dtype=np.float64)
rear_rpy_meas = np.zeros(3, dtype=np.float64)
front_rpy_des = np.zeros(3, dtype=np.float64)
rear_rpy_des = np.zeros(3, dtype=np.float64)
front_rpy_cmd = np.zeros(3, dtype=np.float64)
rear_rpy_cmd = np.zeros(3, dtype=np.float64)

front_joint_zero = np.zeros(3, dtype=np.float64)
rear_joint_zero = np.zeros(3, dtype=np.float64)
front_joint_target_ik = np.zeros(3, dtype=np.float64)
rear_joint_target_ik = np.zeros(3, dtype=np.float64)
front_joint_target_cmd = np.zeros(3, dtype=np.float64)
rear_joint_target_cmd = np.zeros(3, dtype=np.float64)

front_prev_q_math = q_home.copy()
rear_prev_q_math = q_home.copy()
front_q_math = q_home.copy()
rear_q_math = q_home.copy()
front_residuals = np.zeros(3, dtype=np.float64)
rear_residuals = np.zeros(3, dtype=np.float64)
ik_error_message = None
print_counter = 0

log_file = open(LOG_PATH, "w", newline="", encoding="utf-8")
log_writer = csv.writer(log_file)
log_writer.writerow([
    "step",
    "front_roll_raw_deg",
    "front_pitch_raw_deg",
    "front_yaw_raw_deg",
    "rear_roll_raw_deg",
    "rear_pitch_raw_deg",
    "rear_yaw_raw_deg",
    "front_roll_bias_deg",
    "front_pitch_bias_deg",
    "front_yaw_bias_deg",
    "rear_roll_bias_deg",
    "rear_pitch_bias_deg",
    "rear_yaw_bias_deg",
    "front_roll_meas_deg",
    "front_pitch_meas_deg",
    "front_yaw_meas_deg",
    "rear_roll_meas_deg",
    "rear_pitch_meas_deg",
    "rear_yaw_meas_deg",
    "front_roll_des_deg",
    "front_pitch_des_deg",
    "front_yaw_des_deg",
    "rear_roll_des_deg",
    "rear_pitch_des_deg",
    "rear_yaw_des_deg",
    "front_roll_cmd_deg",
    "front_pitch_cmd_deg",
    "front_yaw_cmd_deg",
    "rear_roll_cmd_deg",
    "rear_pitch_cmd_deg",
    "rear_yaw_cmd_deg",
    "front_q_ik_0_deg",
    "front_q_ik_1_deg",
    "front_q_ik_2_deg",
    "rear_q_ik_0_deg",
    "rear_q_ik_1_deg",
    "rear_q_ik_2_deg",
    "front_q_cmd_0_deg",
    "front_q_cmd_1_deg",
    "front_q_cmd_2_deg",
    "rear_q_cmd_0_deg",
    "rear_q_cmd_1_deg",
    "rear_q_cmd_2_deg",
    "front_q_sim_0_deg",
    "front_q_sim_1_deg",
    "front_q_sim_2_deg",
    "rear_q_sim_0_deg",
    "rear_q_sim_1_deg",
    "rear_q_sim_2_deg",
    "front_track_err_0_deg",
    "front_track_err_1_deg",
    "front_track_err_2_deg",
    "rear_track_err_0_deg",
    "rear_track_err_1_deg",
    "rear_track_err_2_deg",
    "front_residual_0",
    "front_residual_1",
    "front_residual_2",
    "rear_residual_0",
    "rear_residual_1",
    "rear_residual_2",
    "ik_error",
])
log_file.flush()


def clamp(x, low, high):
    return max(low, min(high, x))


def clamp_pose_targets(rpy):
    for i in range(3):
        rpy[i] = clamp(rpy[i], -POSE_LIMIT, POSE_LIMIT)


def update_pose_targets_from_keyboard():
    # Front pose target in [roll, pitch, yaw].
    if is_pressed("Y"):
        front_rpy_des[0] += POSE_STEP
    if is_pressed("H"):
        front_rpy_des[0] -= POSE_STEP

    if is_pressed("T"):
        front_rpy_des[1] += POSE_STEP
    if is_pressed("G"):
        front_rpy_des[1] -= POSE_STEP

    if is_pressed("R"):
        front_rpy_des[2] += POSE_STEP
    if is_pressed("F"):
        front_rpy_des[2] -= POSE_STEP

    # Rear pose target in [roll, pitch, yaw].
    if is_pressed("O"):
        rear_rpy_des[0] += POSE_STEP
    if is_pressed("L"):
        rear_rpy_des[0] -= POSE_STEP

    if is_pressed("I"):
        rear_rpy_des[1] += POSE_STEP
    if is_pressed("K"):
        rear_rpy_des[1] -= POSE_STEP

    if is_pressed("U"):
        rear_rpy_des[2] += POSE_STEP
    if is_pressed("J"):
        rear_rpy_des[2] -= POSE_STEP

    if is_pressed("X"):
        front_rpy_des[:] = 0.0
        rear_rpy_des[:] = 0.0

    clamp_pose_targets(front_rpy_des)
    clamp_pose_targets(rear_rpy_des)


def read_actual_ball_positions():
    joint_positions = robot.get_joint_positions()
    return np.array([joint_positions[i] for i in ball_indices], dtype=np.float64)


def apply_actions(wheel_velocities, ball_positions):
    wheel_action = ArticulationAction(
        joint_velocities=np.array(wheel_velocities, dtype=np.float64),
        joint_indices=np.array(wheel_indices, dtype=np.int32),
    )
    robot.apply_action(wheel_action)

    ball_action = ArticulationAction(
        joint_positions=np.array(ball_positions, dtype=np.float64),
        joint_indices=np.array(ball_indices, dtype=np.int32),
    )
    robot.apply_action(ball_action)


def rotation_matrix_to_rpy_zyx(rot):
    pitch = math.asin(np.clip(-rot[2, 0], -1.0, 1.0))
    cos_pitch = math.cos(pitch)

    if abs(cos_pitch) > 1e-8:
        roll = math.atan2(rot[2, 1], rot[2, 2])
        yaw = math.atan2(rot[1, 0], rot[0, 0])
    else:
        roll = 0.0
        yaw = math.atan2(-rot[0, 1], rot[1, 1])

    return np.array([roll, pitch, yaw], dtype=np.float64)


def read_relative_rpy(base_prim, platform_prim):
    xform_cache.Clear()
    base_world = xform_cache.GetLocalToWorldTransform(base_prim)
    platform_world = xform_cache.GetLocalToWorldTransform(platform_prim)
    relative = base_world.GetInverse() * platform_world
    rot_mat = relative.ExtractRotationMatrix()
    rot_np = np.array([[rot_mat[i][j] for j in range(3)] for i in range(3)], dtype=np.float64)
    return rotation_matrix_to_rpy_zyx(rot_np)


def rad_to_deg(values):
    values = np.asarray(values, dtype=np.float64)
    return np.rad2deg(values)


def update_measured_pose():
    global front_rpy_raw, rear_rpy_raw, front_rpy_meas, rear_rpy_meas
    front_rpy_raw = read_relative_rpy(front_base_ref_prim, front_platform_prim)
    rear_rpy_raw = read_relative_rpy(rear_base_ref_prim, rear_platform_prim)
    front_rpy_meas = front_rpy_raw - front_rpy_bias
    rear_rpy_meas = rear_rpy_raw - rear_rpy_bias


def calibrate_zero_offsets():
    global front_rpy_bias, rear_rpy_bias, front_joint_zero, rear_joint_zero

    zero_wheel = np.zeros(len(wheel_indices), dtype=np.float64)
    zero_ball = np.zeros(len(ball_indices), dtype=np.float64)
    front_rpy_samples = []
    rear_rpy_samples = []
    joint_samples = []

    print(
        f"[INFO] Calibrating offsets with {ZERO_CALIBRATION_SETTLE_STEPS} settle steps and "
        f"{ZERO_CALIBRATION_SAMPLE_STEPS} sample steps..."
    )

    for _ in range(ZERO_CALIBRATION_SETTLE_STEPS):
        apply_actions(zero_wheel, zero_ball)
        world.step(render=True)

    for _ in range(ZERO_CALIBRATION_SAMPLE_STEPS):
        apply_actions(zero_wheel, zero_ball)
        world.step(render=True)
        front_rpy_samples.append(read_relative_rpy(front_base_ref_prim, front_platform_prim))
        rear_rpy_samples.append(read_relative_rpy(rear_base_ref_prim, rear_platform_prim))
        joint_samples.append(read_actual_ball_positions())

    front_rpy_bias = np.mean(np.asarray(front_rpy_samples, dtype=np.float64), axis=0)
    rear_rpy_bias = np.mean(np.asarray(rear_rpy_samples, dtype=np.float64), axis=0)
    joint_mean = np.mean(np.asarray(joint_samples, dtype=np.float64), axis=0)
    front_joint_zero = joint_mean[:3]
    rear_joint_zero = joint_mean[3:]

    print("[INFO] Front zero RPY bias deg:", np.round(rad_to_deg(front_rpy_bias), 6).tolist())
    print("[INFO] Rear zero RPY bias deg :", np.round(rad_to_deg(rear_rpy_bias), 6).tolist())
    print("[INFO] Front joint zero deg   :", np.round(rad_to_deg(front_joint_zero), 6).tolist())
    print("[INFO] Rear joint zero deg    :", np.round(rad_to_deg(rear_joint_zero), 6).tolist())


def smooth_pose_commands():
    front_rpy_cmd[:] = front_rpy_cmd + POSE_CMD_ALPHA * (front_rpy_des - front_rpy_cmd)
    rear_rpy_cmd[:] = rear_rpy_cmd + POSE_CMD_ALPHA * (rear_rpy_des - rear_rpy_cmd)


def solve_single_spm(target_rpy, prev_q_math, signs, joint_zero):
    out = ik_solver.ik(
        roll=float(target_rpy[0]),
        pitch=float(target_rpy[1]),
        yaw=float(target_rpy[2]),
        prev_q=prev_q_math.tolist(),
    )
    q_math = np.array(out["q"], dtype=np.float64)
    q_target = np.array(
        ik_solver.map_to_sim_joints(
            q_math=q_math.tolist(),
            q_home=q_home.tolist(),
            signs=signs,
            biases=tuple(float(v) for v in joint_zero),
        ),
        dtype=np.float64,
    )
    residuals = np.array(
        ik_solver.verify_solution(
            q=q_math.tolist(),
            roll=float(target_rpy[0]),
            pitch=float(target_rpy[1]),
            yaw=float(target_rpy[2]),
        ),
        dtype=np.float64,
    )
    return q_math, q_target, residuals


def update_ik_joint_targets_from_pose_targets():
    global front_prev_q_math, rear_prev_q_math
    global front_q_math, rear_q_math
    global front_joint_target_ik, rear_joint_target_ik
    global front_residuals, rear_residuals, ik_error_message

    try:
        front_q_math, front_joint_target_ik, front_residuals = solve_single_spm(
            target_rpy=front_rpy_cmd,
            prev_q_math=front_prev_q_math,
            signs=IK_SIGNS_FRONT,
            joint_zero=front_joint_zero,
        )
        rear_q_math, rear_joint_target_ik, rear_residuals = solve_single_spm(
            target_rpy=rear_rpy_cmd,
            prev_q_math=rear_prev_q_math,
            signs=IK_SIGNS_REAR,
            joint_zero=rear_joint_zero,
        )
        front_prev_q_math = front_q_math.copy()
        rear_prev_q_math = rear_q_math.copy()
        ik_error_message = None
    except ValueError as exc:
        ik_error_message = str(exc)


def smooth_joint_targets():
    front_joint_target_cmd[:] = front_joint_target_cmd + JOINT_CMD_ALPHA * (
        front_joint_target_ik - front_joint_target_cmd
    )
    rear_joint_target_cmd[:] = rear_joint_target_cmd + JOINT_CMD_ALPHA * (
        rear_joint_target_ik - rear_joint_target_cmd
    )


def compute_wheel_velocities():
    v = 0.0
    if is_pressed("W"):
        v = WHEEL_SPEED
    elif is_pressed("S"):
        v = -WHEEL_SPEED

    if is_pressed("SPACE"):
        v = 0.0

    return np.array([v] * len(wheel_indices), dtype=np.float64)


def write_log_snapshot(step, actual_ball):
    front_track_err = front_joint_target_cmd - actual_ball[:3]
    rear_track_err = rear_joint_target_cmd - actual_ball[3:]
    log_writer.writerow([
        step,
        *np.round(rad_to_deg(front_rpy_raw), 6).tolist(),
        *np.round(rad_to_deg(rear_rpy_raw), 6).tolist(),
        *np.round(rad_to_deg(front_rpy_bias), 6).tolist(),
        *np.round(rad_to_deg(rear_rpy_bias), 6).tolist(),
        *np.round(rad_to_deg(front_rpy_meas), 6).tolist(),
        *np.round(rad_to_deg(rear_rpy_meas), 6).tolist(),
        *np.round(rad_to_deg(front_rpy_des), 6).tolist(),
        *np.round(rad_to_deg(rear_rpy_des), 6).tolist(),
        *np.round(rad_to_deg(front_rpy_cmd), 6).tolist(),
        *np.round(rad_to_deg(rear_rpy_cmd), 6).tolist(),
        *np.round(rad_to_deg(front_joint_target_ik), 6).tolist(),
        *np.round(rad_to_deg(rear_joint_target_ik), 6).tolist(),
        *np.round(rad_to_deg(front_joint_target_cmd), 6).tolist(),
        *np.round(rad_to_deg(rear_joint_target_cmd), 6).tolist(),
        *np.round(rad_to_deg(actual_ball[:3]), 6).tolist(),
        *np.round(rad_to_deg(actual_ball[3:]), 6).tolist(),
        *np.round(rad_to_deg(front_track_err), 6).tolist(),
        *np.round(rad_to_deg(rear_track_err), 6).tolist(),
        *np.round(front_residuals, 10).tolist(),
        *np.round(rear_residuals, 10).tolist(),
        "" if ik_error_message is None else ik_error_message,
    ])
    log_file.flush()


def print_debug_snapshot(step):
    actual_ball = read_actual_ball_positions()
    front_track_err = front_joint_target_cmd - actual_ball[:3]
    rear_track_err = rear_joint_target_cmd - actual_ball[3:]

    print("\n==== IK Tracking Snapshot ====")
    print("step               :", step)
    print("front_rpy_meas_deg :", np.round(rad_to_deg(front_rpy_meas), 3).tolist())
    print("rear_rpy_meas_deg  :", np.round(rad_to_deg(rear_rpy_meas), 3).tolist())
    print("front_rpy_des_deg  :", np.round(rad_to_deg(front_rpy_des), 3).tolist())
    print("rear_rpy_des_deg   :", np.round(rad_to_deg(rear_rpy_des), 3).tolist())
    print("front_rpy_cmd_deg  :", np.round(rad_to_deg(front_rpy_cmd), 3).tolist())
    print("rear_rpy_cmd_deg   :", np.round(rad_to_deg(rear_rpy_cmd), 3).tolist())
    print("front_q_ik_deg     :", np.round(rad_to_deg(front_joint_target_ik), 3).tolist())
    print("rear_q_ik_deg      :", np.round(rad_to_deg(rear_joint_target_ik), 3).tolist())
    print("front_q_cmd_deg    :", np.round(rad_to_deg(front_joint_target_cmd), 3).tolist())
    print("rear_q_cmd_deg     :", np.round(rad_to_deg(rear_joint_target_cmd), 3).tolist())
    print("front_q_sim_deg    :", np.round(rad_to_deg(actual_ball[:3]), 3).tolist())
    print("rear_q_sim_deg     :", np.round(rad_to_deg(actual_ball[3:]), 3).tolist())
    print("front_track_err_deg:", np.round(rad_to_deg(front_track_err), 3).tolist())
    print("rear_track_err_deg :", np.round(rad_to_deg(rear_track_err), 3).tolist())
    print("front_residuals    :", np.round(front_residuals, 8).tolist())
    print("rear_residuals     :", np.round(rear_residuals, 8).tolist())
    if ik_error_message is not None:
        print("ik_error           :", ik_error_message)
    print("log_path           :", LOG_PATH)
    print("==============================\n")

    write_log_snapshot(step, actual_ball)


print("\n==== Control Keys ====")
print("W/S                : forward/backward")
print("SPACE              : stop wheels")
print("Y/H                : front roll +/-")
print("T/G                : front pitch +/-")
print("R/F                : front yaw +/-")
print("O/L                : rear roll +/-")
print("I/K                : rear pitch +/-")
print("U/J                : rear yaw +/-")
print("X                  : reset front/rear pose targets to zero")
print("ESC                : quit")
print("IMPORTANT          : click Isaac Sim window first to focus keyboard\n")


# =========================
# 6. Main loop
# =========================
print(
    f"[INFO] Startup calibration enabled: settle={ZERO_CALIBRATION_SETTLE_STEPS}, "
    f"sample={ZERO_CALIBRATION_SAMPLE_STEPS}"
)
calibrate_zero_offsets()
update_measured_pose()
front_rpy_des[:] = 0.0
rear_rpy_des[:] = 0.0
front_rpy_cmd[:] = 0.0
rear_rpy_cmd[:] = 0.0
front_joint_target_cmd[:] = front_joint_zero
rear_joint_target_cmd[:] = rear_joint_zero
update_ik_joint_targets_from_pose_targets()

try:
    while simulation_app.is_running():
        if is_pressed("ESCAPE"):
            break

        update_pose_targets_from_keyboard()
        smooth_pose_commands()
        update_ik_joint_targets_from_pose_targets()
        smooth_joint_targets()
        wheel_vel_cmd = compute_wheel_velocities()

        apply_actions(
            wheel_velocities=wheel_vel_cmd,
            ball_positions=np.concatenate([front_joint_target_cmd, rear_joint_target_cmd]),
        )

        world.step(render=True)
        update_measured_pose()
        print_counter += 1

        if print_counter % PRINT_EVERY == 0:
            print_debug_snapshot(print_counter)

finally:
    input_iface.unsubscribe_from_keyboard_events(keyboard, keyboard_sub)
    log_file.close()
    simulation_app.close()
