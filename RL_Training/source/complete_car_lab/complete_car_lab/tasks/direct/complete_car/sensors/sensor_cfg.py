"""传感器配置与运行时装配。"""

from __future__ import annotations

from dataclasses import field

import torch
from isaacsim.core.simulation_manager import SimulationManager
from isaaclab.sensors import RayCaster, RayCasterCfg
import isaaclab.sim as sim_utils
from isaaclab.utils import configclass

from ..assets.robot_cfg import WHEEL_BODY_NAMES
from .imu import ImuSensorAdapter, ImuSensorCfg
from .lidar import LidarSensorAdapter, LidarSensorCfg
from .stereo_camera import StereoCameraAdapter, StereoCameraSensorCfg


def _resolve_env_regex_ns(prim_path: str, scene) -> str:
    """Resolve Isaac Lab's environment namespace placeholder for manually-built sensors."""

    return prim_path.format(ENV_REGEX_NS=scene.env_regex_ns)


def _resolve_ground_contact_filter_pattern(ground_prim_path: str) -> str:
    """Resolve the exact collider prim used as the wheel-ground contact filter."""

    ground_collision_prim = sim_utils.get_first_matching_child_prim(
        ground_prim_path,
        predicate=lambda prim: prim.GetTypeName() in {"Plane", "Mesh"},
    )
    if ground_collision_prim is None:
        if sim_utils.is_prim_path_valid(ground_prim_path):
            return ground_prim_path
        raise RuntimeError(f"Failed to resolve a ground collision prim under '{ground_prim_path}'.")
    return ground_collision_prim.GetPath().pathString


@configclass
class CompleteCarSensorSuiteCfg:
    """集中描述 Stage0/1/2 需要绑定的传感器集合。"""

    imu: ImuSensorCfg = ImuSensorCfg()
    stereo_camera: StereoCameraSensorCfg = StereoCameraSensorCfg()
    lidar: LidarSensorCfg = LidarSensorCfg()
    enable_height_scanner: bool = False
    height_scanner_debug_vis: bool = False

    # 计算策略网络（Actor）传感器特征的总维度
    def get_policy_feature_dim(self) -> int:
        return (
            self.imu.get_policy_feature_dim()
            + self.stereo_camera.get_policy_feature_dim()
            + self.lidar.get_policy_feature_dim()
        )
    #返回传感器维度的详细描述列表
    def policy_descriptor(self) -> list[tuple[str, int]]:
        descriptor: list[tuple[str, int]] = []
        imu_dim = self.imu.get_policy_feature_dim()
        stereo_dim = self.stereo_camera.get_policy_feature_dim()
        lidar_dim = self.lidar.get_policy_feature_dim()
        if imu_dim:
            descriptor.append(("imu", imu_dim))
        if stereo_dim:
            descriptor.append(("stereo_camera", stereo_dim))
        if lidar_dim:
            descriptor.append(("lidar", lidar_dim))
        return descriptor


class CompleteCarSensorSuiteRuntime:
    """统一封装传感器 runtime，env 只与这一层交互。"""

    def __init__(self, cfg: CompleteCarSensorSuiteCfg, terrain_cfg, ground_prim_path: str):
        self.cfg = cfg
        self.terrain_cfg = terrain_cfg
        self.ground_prim_path = ground_prim_path

        self.imu = ImuSensorAdapter(cfg.imu)
        self.stereo_camera = StereoCameraAdapter(cfg.stereo_camera)
        self.lidar = LidarSensorAdapter(cfg.lidar, ground_prim_path)
        self.height_scanner: RayCaster | None = None
        self._wheel_contact_views: dict[str, object] = {}
        self._wheel_contact_sim_dt: float | None = None
        self._wheel_contact_env_glob_ns: str | None = None
        self._wheel_contact_num_envs: int | None = None
        self._wheel_contact_filter_patterns: list[str] = []
        self._raw_output: dict[str, torch.Tensor | dict[str, torch.Tensor]] = {}

    def build_scene_entities(self, scene) -> None:
        self.cfg.imu.prim_path = _resolve_env_regex_ns(self.cfg.imu.prim_path, scene)
        self.cfg.stereo_camera.prim_path = _resolve_env_regex_ns(self.cfg.stereo_camera.prim_path, scene)
        self.cfg.lidar.prim_path = _resolve_env_regex_ns(self.cfg.lidar.prim_path, scene)
        self.terrain_cfg.height_scanner_prim_path = _resolve_env_regex_ns(self.terrain_cfg.height_scanner_prim_path, scene)
        self._wheel_contact_env_glob_ns = scene.env_regex_ns.replace(".*", "*")
        self._wheel_contact_num_envs = scene.cfg.num_envs
        self._wheel_contact_filter_patterns = [_resolve_ground_contact_filter_pattern(self.ground_prim_path)]

        self.imu.build(scene)
        self.stereo_camera.build(scene)
        self.lidar.build(scene)

        if self.cfg.enable_height_scanner:
            height_cfg: RayCasterCfg = self.terrain_cfg.build_height_scanner_cfg(self.ground_prim_path)
            height_cfg.debug_vis = self.cfg.height_scanner_debug_vis
            self.height_scanner = RayCaster(height_cfg)
            scene.sensors["height_scanner"] = self.height_scanner

    def reset(self, env_ids: torch.Tensor | None = None) -> None:
        self.imu.reset(env_ids)
        self.stereo_camera.reset(env_ids)
        self.lidar.reset(env_ids)
        if self.height_scanner is not None:
            self.height_scanner.reset(env_ids)
    # 监听车轮与地面的碰撞事件
    def _initialize_wheel_contact_views(self) -> None:
        if self._wheel_contact_views:
            return
        if self._wheel_contact_env_glob_ns is None:
            raise RuntimeError("Wheel contact env namespace has not been prepared.")
        if self._wheel_contact_num_envs is None:
            raise RuntimeError("Wheel contact env count has not been prepared.")

        sim = sim_utils.SimulationContext.instance()
        if sim is None:
            raise RuntimeError("Simulation context is not initialized.")
        physics_sim_view = SimulationManager.get_physics_sim_view()
        self._wheel_contact_sim_dt = sim.get_physics_dt()
        num_envs = self._wheel_contact_num_envs

        for wheel_body_name in WHEEL_BODY_NAMES:
            wheel_prim_glob = (
                f"{self._wheel_contact_env_glob_ns}/Robot/complete_car_alternative/{wheel_body_name}"
            )
            body_view = physics_sim_view.create_rigid_body_view(wheel_prim_glob)
            if body_view.count != num_envs:
                raise RuntimeError(
                    "Failed to initialize wheel rigid body view."
                    f"\n\tWheel body : {wheel_body_name}"
                    f"\n\tPrim glob  : {wheel_prim_glob}"
                    f"\n\tBody count : {body_view.count}"
                    f"\n\tNum envs   : {num_envs}"
                )
            self._wheel_contact_views[wheel_body_name] = physics_sim_view.create_rigid_contact_view(
                wheel_prim_glob,
                filter_patterns=self._wheel_contact_filter_patterns,
                max_contact_data_count=16 * num_envs,
            )
    #接触力张量聚合
    def _aggregate_contact_force_vectors(
        self,
        contact_forces: torch.Tensor,
        contact_normals: torch.Tensor,
        pair_counts: torch.Tensor,
        pair_start_indices: torch.Tensor,
    ) -> torch.Tensor:
        """Aggregate detailed contact-point data into one normal-force vector per (env, filter) pair."""

        num_envs = self._wheel_contact_num_envs
        if num_envs is None:
            raise RuntimeError("Wheel contact env count has not been prepared.")

        force_vectors = contact_forces * contact_normals
        counts = pair_counts.view(-1).to(dtype=torch.long)
        starts = pair_start_indices.view(-1).to(dtype=torch.long)
        num_pairs = counts.numel()
        aggregated = torch.zeros((num_pairs, 3), device=force_vectors.device, dtype=force_vectors.dtype)
        total_contacts = int(counts.sum().item())
        if total_contacts > 0:
            row_ids = torch.repeat_interleave(torch.arange(num_pairs, device=force_vectors.device), counts)
            block_starts = counts.cumsum(0) - counts
            deltas = torch.arange(total_contacts, device=force_vectors.device) - block_starts.repeat_interleave(counts)
            flat_indices = starts[row_ids] + deltas
            aggregated.index_add_(0, row_ids, force_vectors.index_select(0, flat_indices))
        return aggregated.view(num_envs, -1, 3)
    
    def get_policy_features(self) -> list[torch.Tensor]:
        features: list[torch.Tensor] = []

        imu_feature = self.imu.policy_features()
        if imu_feature is not None:
            self._raw_output["imu"] = imu_feature
            features.append(imu_feature)

        camera_feature, camera_raw = self.stereo_camera.policy_features()
        if camera_feature is not None:
            self._raw_output["stereo_camera"] = camera_raw
            features.append(camera_feature)

        lidar_feature, lidar_raw = self.lidar.policy_features()
        if lidar_feature is not None:
            self._raw_output["lidar"] = lidar_raw
            features.append(lidar_feature)

        return features
    # 对外输出所有车轮的最终接触力
    def get_wheel_contact_forces_w(self, wheel_body_names: list[str]) -> torch.Tensor:
        self._initialize_wheel_contact_views()
        if self._wheel_contact_sim_dt is None:
            raise RuntimeError("Wheel contact sim dt has not been initialized.")

        wheel_force_vectors = []
        for wheel_body_name in wheel_body_names:
            contact_view = self._wheel_contact_views[wheel_body_name]
            normal_forces, _, contact_normals, _, pair_counts, pair_start_indices = contact_view.get_contact_data(
                dt=self._wheel_contact_sim_dt
            )
            aggregated_force_vectors = self._aggregate_contact_force_vectors(
                normal_forces,
                contact_normals,
                pair_counts,
                pair_start_indices,
            )
            wheel_force_vectors.append(torch.sum(aggregated_force_vectors, dim=1, keepdim=True))

        net_forces_w = torch.cat(wheel_force_vectors, dim=1)
        self._raw_output["wheel_contact_forces_w"] = net_forces_w
        return net_forces_w

    def get_raw_output(self) -> dict[str, torch.Tensor | dict[str, torch.Tensor]]:
        return dict(self._raw_output)
