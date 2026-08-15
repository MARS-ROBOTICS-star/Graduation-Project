from isaacsim import SimulationApp

# 建议先用带界面的方式验证
simulation_app = SimulationApp({"headless": False})

from pathlib import Path

import numpy as np
from PIL import Image

import omni.usd
import omni.replicator.core as rep

from isaacsim.core.api.world import World
from isaacsim.core.utils.stage import open_stage
from isaacsim.sensors.physics import _sensor


# =========================================================
# 1. 用户配置区
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
USD_PATH = str(PROJECT_ROOT / "complete_car_alternative.usd")

IMU_PATH = "/World/complete_car_alternative/body_car_chassis/IMU_body"
LEFT_CAMERA_PATH = "/World/complete_car_alternative/head_car_chassis/Stereo_rig/left_camera"
RIGHT_CAMERA_PATH = "/World/complete_car_alternative/head_car_chassis/Stereo_rig/right_camera"
LIDAR_PATH = "/World/complete_car_alternative/head_car_chassis/Example_Rotary"

OUTPUT_DIR = str(PROJECT_ROOT / "results" / "sensor_validation")

CAMERA_RESOLUTION = (640, 480)
LIDAR_RENDER_PRODUCT_RESOLUTION = (1024, 1024)

WARMUP_FRAMES = 30
TOTAL_FRAMES = 120
SAVE_EVERY_N_FRAMES = 20


# =========================================================
# 2. 工具函数
# =========================================================
def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def check_prim_exists(stage, prim_path: str):
    prim = stage.GetPrimAtPath(prim_path)
    return prim.IsValid(), prim


def save_rgb_image(arr: np.ndarray, save_path: str):
    """
    保存 RGB/RGBA 图像
    """
    if arr is None:
        return

    img = np.array(arr)
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)

    # 常见情况: HxWx4 或 HxWx3
    if img.ndim == 3 and img.shape[-1] == 4:
        img = img[..., :3]
    elif img.ndim == 2:
        img = np.stack([img] * 3, axis=-1)

    Image.fromarray(img).save(save_path)


def save_depth_visualization(depth: np.ndarray, save_path_png: str, save_path_npy: str):
    """
    保存深度图:
    - 原始 float32 到 .npy
    - 归一化可视化到 .png
    """
    if depth is None:
        return

    d = np.array(depth, dtype=np.float32)

    # 常见情况: HxWx1 -> HxW
    if d.ndim == 3 and d.shape[-1] == 1:
        d = d[..., 0]

    np.save(save_path_npy, d)

    valid = np.isfinite(d)
    if not np.any(valid):
        vis = np.zeros_like(d, dtype=np.uint8)
    else:
        d_valid = d[valid]
        d_min = np.percentile(d_valid, 5)
        d_max = np.percentile(d_valid, 95)
        if abs(d_max - d_min) < 1e-6:
            vis = np.zeros_like(d, dtype=np.uint8)
        else:
            d_clip = np.clip(d, d_min, d_max)
            vis = (255.0 * (d_clip - d_min) / (d_max - d_min)).astype(np.uint8)

    Image.fromarray(vis).save(save_path_png)


def parse_lidar_points(lidar_data):
    """
    尽量兼容不同 annotator 返回格式，提取 Nx3 点云
    """
    if lidar_data is None:
        return None

    # 直接就是 ndarray
    if isinstance(lidar_data, np.ndarray):
        arr = lidar_data
        if arr.ndim == 2 and arr.shape[1] >= 3:
            return arr[:, :3]
        return None

    # 如果是 dict，尝试常见 key
    if isinstance(lidar_data, dict):
        candidate_keys = [
            "data",
            "points",
            "pointCloud",
            "point_cloud",
            "xyz",
        ]
        for k in candidate_keys:
            if k in lidar_data:
                arr = np.array(lidar_data[k])
                if arr.ndim == 2 and arr.shape[1] >= 3:
                    return arr[:, :3]

        # 有些返回可能嵌套
        for _, v in lidar_data.items():
            try:
                arr = np.array(v)
                if arr.ndim == 2 and arr.shape[1] >= 3:
                    return arr[:, :3]
            except Exception:
                pass

    return None


def print_imu_reading(reading):
    """
    兼容 IMU 接口返回对象
    """
    try:
        is_valid = getattr(reading, "is_valid", None)
        t = getattr(reading, "time", None)
        lin_acc = (
            getattr(reading, "lin_acc_x", None),
            getattr(reading, "lin_acc_y", None),
            getattr(reading, "lin_acc_z", None),
        )
        ang_vel = (
            getattr(reading, "ang_vel_x", None),
            getattr(reading, "ang_vel_y", None),
            getattr(reading, "ang_vel_z", None),
        )
        ori = getattr(reading, "orientation", None)

        print("[IMU]")
        print(f"  valid = {is_valid}")
        print(f"  time  = {t}")
        print(f"  lin_acc = {lin_acc}")
        print(f"  ang_vel = {ang_vel}")
        print(f"  orientation = {ori}")
    except Exception as e:
        print(f"[IMU] Failed to print reading: {e}")
        print(f"[IMU] Raw reading repr: {reading}")


def summarize_camera_data(name: str, rgb_data, depth_data):
    rgb_shape = None if rgb_data is None else np.array(rgb_data).shape
    depth_shape = None if depth_data is None else np.array(depth_data).shape

    print(f"[{name}]")
    print(f"  rgb shape   = {rgb_shape}")
    print(f"  depth shape = {depth_shape}")

    if depth_data is not None:
        d = np.array(depth_data, dtype=np.float32)
        if d.ndim == 3 and d.shape[-1] == 1:
            d = d[..., 0]
        finite = np.isfinite(d)
        if np.any(finite):
            print(
                f"  depth stats = min {np.min(d[finite]):.4f}, "
                f"max {np.max(d[finite]):.4f}, mean {np.mean(d[finite]):.4f}"
            )
        else:
            print("  depth stats = no finite values")


def summarize_lidar_data(points: np.ndarray):
    print("[LIDAR]")
    if points is None:
        print("  point cloud = None")
        return

    norms = np.linalg.norm(points, axis=1)
    finite = np.isfinite(norms)
    if not np.any(finite):
        print(f"  points shape = {points.shape}, but no finite distances")
        return

    print(f"  points shape = {points.shape}")
    print(f"  nearest dist = {np.min(norms[finite]):.4f}")
    print(f"  mean dist    = {np.mean(norms[finite]):.4f}")
    print(f"  first 5 pts  =\n{points[:5]}")


# =========================================================
# 3. 打开场景
# =========================================================
ensure_dir(OUTPUT_DIR)

print(f"[INFO] Opening USD: {USD_PATH}")
ok = open_stage(USD_PATH)
print(f"[INFO] open_stage result: {ok}")
if not ok:
    raise RuntimeError(f"Failed to open stage: {USD_PATH}")

if World.instance():
    World.instance().clear_instance()

world = World(stage_units_in_meters=1.0)
world.reset()

stage = omni.usd.get_context().get_stage()

for path_name, path_value in [
    ("IMU_PATH", IMU_PATH),
    ("LEFT_CAMERA_PATH", LEFT_CAMERA_PATH),
    ("RIGHT_CAMERA_PATH", RIGHT_CAMERA_PATH),
    ("LIDAR_PATH", LIDAR_PATH),
]:
    exists, prim = check_prim_exists(stage, path_value)
    print(f"[CHECK] {path_name} = {path_value}")
    print(f"        exists = {exists}")
    print(f"        type   = {prim.GetTypeName() if exists else 'INVALID'}")
    if not exists:
        raise RuntimeError(f"Prim not found: {path_value}")


# =========================================================
# 4. 配置 IMU 读取接口
# =========================================================
imu_interface = _sensor.acquire_imu_sensor_interface()


# =========================================================
# 5. 配置相机 annotators
#    文档里推荐的相机数据类型包括 rgb / distance_to_image_plane(depth)
# =========================================================
left_rp = rep.create.render_product(LEFT_CAMERA_PATH, CAMERA_RESOLUTION)
right_rp = rep.create.render_product(RIGHT_CAMERA_PATH, CAMERA_RESOLUTION)

left_rgb_annot = rep.AnnotatorRegistry.get_annotator("rgb")
left_depth_annot = rep.AnnotatorRegistry.get_annotator("distance_to_image_plane")

right_rgb_annot = rep.AnnotatorRegistry.get_annotator("rgb")
right_depth_annot = rep.AnnotatorRegistry.get_annotator("distance_to_image_plane")

left_rgb_annot.attach([left_rp.path])
left_depth_annot.attach([left_rp.path])

right_rgb_annot.attach([right_rp.path])
right_depth_annot.attach([right_rp.path])


# =========================================================
# 6. 配置 RTX Lidar annotator
#    文档里 RTX lidar 常用 point cloud annotator:
#    IsaacExtractRTXSensorPointCloudNoAccumulator
# =========================================================
lidar_rp = rep.create.render_product(LIDAR_PATH, LIDAR_RENDER_PRODUCT_RESOLUTION)
lidar_pc_annot = rep.AnnotatorRegistry.get_annotator("IsaacExtractRTXSensorPointCloudNoAccumulator")
lidar_pc_annot.attach([lidar_rp.path])


# =========================================================
# 7. 启动 timeline
#    文档强调 RTX 传感器 annotator 依赖 timeline.play()
# =========================================================
timeline = omni.timeline.get_timeline_interface()
app = omni.kit.app.get_app()

print("[INFO] Starting timeline...")
timeline.play()

# 先 warmup 一段，等渲染和传感器缓冲稳定
for i in range(WARMUP_FRAMES):
    app.update()
print(f"[INFO] Warmup finished: {WARMUP_FRAMES} frames")


# =========================================================
# 8. 主循环：读取并保存传感器数据
# =========================================================
print("[INFO] Start sensor validation loop")
start_time = time.time()

try:
    for frame in range(TOTAL_FRAMES):
        app.update()

        # ---------------- IMU ----------------
        imu_reading = imu_interface.get_sensor_reading(
            IMU_PATH,
            use_latest_data=True,
            read_gravity=True,
        )

        # ---------------- Cameras ----------------
        left_rgb = left_rgb_annot.get_data()
        left_depth = left_depth_annot.get_data()

        right_rgb = right_rgb_annot.get_data()
        right_depth = right_depth_annot.get_data()

        # ---------------- Lidar ----------------
        lidar_raw = lidar_pc_annot.get_data()
        lidar_points = parse_lidar_points(lidar_raw)

        # 每隔若干帧打印一次摘要
        if frame % SAVE_EVERY_N_FRAMES == 0:
            print(f"\n================ Frame {frame} ================")
            print_imu_reading(imu_reading)
            summarize_camera_data("LEFT_CAMERA", left_rgb, left_depth)
            summarize_camera_data("RIGHT_CAMERA", right_rgb, right_depth)
            summarize_lidar_data(lidar_points)

            # 保存图像与点云
            frame_dir = os.path.join(OUTPUT_DIR, f"frame_{frame:04d}")
            ensure_dir(frame_dir)

            save_rgb_image(left_rgb, os.path.join(frame_dir, "left_rgb.png"))
            save_depth_visualization(
                left_depth,
                os.path.join(frame_dir, "left_depth_vis.png"),
                os.path.join(frame_dir, "left_depth.npy"),
            )

            save_rgb_image(right_rgb, os.path.join(frame_dir, "right_rgb.png"))
            save_depth_visualization(
                right_depth,
                os.path.join(frame_dir, "right_depth_vis.png"),
                os.path.join(frame_dir, "right_depth.npy"),
            )

            if lidar_points is not None:
                np.save(os.path.join(frame_dir, "lidar_points.npy"), lidar_points)

            # 同时保存一份 IMU 文本
            with open(os.path.join(frame_dir, "imu.txt"), "w", encoding="utf-8") as f:
                try:
                    f.write(f"is_valid: {getattr(imu_reading, 'is_valid', None)}\n")
                    f.write(f"time: {getattr(imu_reading, 'time', None)}\n")
                    f.write(
                        "lin_acc: "
                        f"({getattr(imu_reading, 'lin_acc_x', None)}, "
                        f"{getattr(imu_reading, 'lin_acc_y', None)}, "
                        f"{getattr(imu_reading, 'lin_acc_z', None)})\n"
                    )
                    f.write(
                        "ang_vel: "
                        f"({getattr(imu_reading, 'ang_vel_x', None)}, "
                        f"{getattr(imu_reading, 'ang_vel_y', None)}, "
                        f"{getattr(imu_reading, 'ang_vel_z', None)})\n"
                    )
                    f.write(f"orientation: {getattr(imu_reading, 'orientation', None)}\n")
                except Exception as e:
                    f.write(f"Failed to serialize IMU reading: {e}\n")
                    f.write(repr(imu_reading))

    elapsed = time.time() - start_time
    print(f"\n[INFO] Validation finished in {elapsed:.2f}s")
    print(f"[INFO] Output saved to: {OUTPUT_DIR}")

finally:
    print("[INFO] Stopping timeline...")
    timeline.stop()

    # detach annotators
    try:
        left_rgb_annot.detach([left_rp.path])
        left_depth_annot.detach([left_rp.path])
        right_rgb_annot.detach([right_rp.path])
        right_depth_annot.detach([right_rp.path])
        lidar_pc_annot.detach([lidar_rp.path])
    except Exception as e:
        print(f"[WARN] Annotator detach failed: {e}")

    simulation_app.close()
