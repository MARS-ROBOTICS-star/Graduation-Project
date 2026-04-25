"""调试绘图辅助。"""

from __future__ import annotations

import torch

import isaaclab.sim as sim_utils
from isaaclab.markers import VisualizationMarkers, VisualizationMarkersCfg
from isaaclab.markers.config import GREEN_ARROW_X_MARKER_CFG, RED_ARROW_X_MARKER_CFG
from isaaclab.utils.math import quat_from_euler_xyz


GOAL_SPHERE_MARKER_CFG = VisualizationMarkersCfg(
    markers={
        "sphere": sim_utils.SphereCfg(
            radius=0.2,
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(1.0, 0.0, 0.0)),
        ),
    }
)


class CompleteCarDebugDraw:
    """集中放置可选调试可视化入口，避免 env.py 直接依赖绘图细节。"""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self._goal_arrow_visualizer: VisualizationMarkers | None = None
        self._goal_sphere_visualizer: VisualizationMarkers | None = None
        self._wheel_forward_visualizer: VisualizationMarkers | None = None
        self._wheel_velocity_visualizer: VisualizationMarkers | None = None
        self._goal_arrow_height_offset = 0.25
        self._wheel_arrow_height_offset = 0.0
        self._view_root_path = "/view"
        self._follow_view_count = 0
        self._follow_view_chase_env_index = 0
        if self.enabled:
            self._ensure_goal_pose_visualizers()
            self.set_visibility(True)

    def clear(self) -> None:
        if not self.enabled:
            return
        self.set_visibility(False)

    def draw_reset_points(self, *_args, **_kwargs) -> None:
        if not self.enabled:
            return

    def draw_command_vectors(self, *_args, **_kwargs) -> None:
        if not self.enabled:
            return

    def set_visibility(self, visible: bool) -> None:
        if visible and self.enabled:
            self._ensure_goal_pose_visualizers()
        if self._goal_arrow_visualizer is not None:
            self._goal_arrow_visualizer.set_visibility(visible)
        if self._goal_sphere_visualizer is not None:
            self._goal_sphere_visualizer.set_visibility(visible)
        if self._wheel_forward_visualizer is not None:
            self._wheel_forward_visualizer.set_visibility(visible)
        if self._wheel_velocity_visualizer is not None:
            self._wheel_velocity_visualizer.set_visibility(visible)

    def draw_goal_pose(self, goal_positions_w: torch.Tensor, goal_headings_w: torch.Tensor) -> None:
        if not self.enabled:
            return

        self._ensure_goal_pose_visualizers()
        self._goal_sphere_visualizer.visualize(translations=goal_positions_w)

        zero = torch.zeros_like(goal_headings_w)
        arrow_orientations = quat_from_euler_xyz(zero, zero, goal_headings_w)
        arrow_positions_w = goal_positions_w.clone()
        arrow_positions_w[:, 2] += self._goal_arrow_height_offset
        self._goal_arrow_visualizer.visualize(
            translations=arrow_positions_w,
            orientations=arrow_orientations,
        )

    def draw_wheel_motion(
        self,
        wheel_positions_w: torch.Tensor,
        wheel_forward_axis_w: torch.Tensor,
        wheel_velocity_w: torch.Tensor,
    ) -> None:
        """Draw wheel rolling direction and actual planar velocity direction.

        Green arrows point along each wheel's rolling direction. Red arrows point along the
        wheel body's actual planar velocity. Their yaw difference is the visible slip angle.
        """
        if not self.enabled:
            return

        self._ensure_wheel_motion_visualizers()
        wheel_centers = wheel_positions_w.reshape(-1, 3).clone()
        wheel_centers[:, 2] += self._wheel_arrow_height_offset
        forward = wheel_forward_axis_w.reshape(-1, 3)
        velocity = wheel_velocity_w.reshape(-1, 3)

        forward_yaw = torch.atan2(forward[:, 1], forward[:, 0])
        planar_speed = torch.linalg.vector_norm(velocity[:, :2], dim=-1)
        velocity_yaw = torch.atan2(velocity[:, 1], velocity[:, 0])
        velocity_yaw = torch.where(planar_speed > 1.0e-4, velocity_yaw, forward_yaw)

        zero = torch.zeros_like(forward_yaw)
        forward_orientations = quat_from_euler_xyz(zero, zero, forward_yaw)
        velocity_orientations = quat_from_euler_xyz(zero, zero, velocity_yaw)

        forward_scales = torch.zeros((wheel_centers.shape[0], 3), device=wheel_centers.device, dtype=wheel_centers.dtype)
        forward_scales[:, 0] = 2.4
        forward_scales[:, 1:] = 0.12

        velocity_scales = torch.zeros_like(forward_scales)
        velocity_scales[:, 0] = torch.clamp(planar_speed * 0.35, min=1.2, max=3.0)
        velocity_scales[:, 1:] = 0.12

        velocity_positions = wheel_centers.clone()
        velocity_positions[:, 2] += 0.08

        self._wheel_forward_visualizer.visualize(
            translations=wheel_centers,
            orientations=forward_orientations,
            scales=forward_scales,
        )
        self._wheel_velocity_visualizer.visualize(
            translations=velocity_positions,
            orientations=velocity_orientations,
            scales=velocity_scales,
        )

    def update_follow_views(
        self,
        sim,
        root_positions_w: torch.Tensor,
        root_yaws_w: torch.Tensor,
        *,
        top_height: float,
        chase_env_index: int,
        chase_offset_b: tuple[float, float, float],
        chase_target_offset_b: tuple[float, float, float],
    ) -> None:
        """Create/update selectable USD cameras under /view for playback inspection."""
        if not self.enabled:
            return

        root_positions = root_positions_w.detach().cpu()
        root_yaws = root_yaws_w.detach().cpu()
        num_envs = int(root_positions.shape[0])
        self._ensure_follow_view_paths(num_envs, chase_env_index)

        for env_id in range(num_envs):
            root_pos = root_positions[env_id]
            eye = (float(root_pos[0]), float(root_pos[1]), float(root_pos[2] + top_height))
            target = (float(root_pos[0]), float(root_pos[1]), float(root_pos[2]))
            sim.set_camera_view(eye=eye, target=target, camera_prim_path=f"{self._view_root_path}/env_{env_id}/top_down_camera")

        if 0 <= chase_env_index < num_envs:
            root_pos = root_positions[chase_env_index]
            yaw = float(root_yaws[chase_env_index])
            eye_offset = self._rotate_planar_offset(chase_offset_b, yaw)
            target_offset = self._rotate_planar_offset(chase_target_offset_b, yaw)
            eye = (
                float(root_pos[0] + eye_offset[0]),
                float(root_pos[1] + eye_offset[1]),
                float(root_pos[2] + eye_offset[2]),
            )
            target = (
                float(root_pos[0] + target_offset[0]),
                float(root_pos[1] + target_offset[1]),
                float(root_pos[2] + target_offset[2]),
            )
            sim.set_camera_view(
                eye=eye,
                target=target,
                camera_prim_path=f"{self._view_root_path}/env_{chase_env_index}/chase_camera",
            )

    def _ensure_goal_pose_visualizers(self) -> None:
        if self._goal_arrow_visualizer is None:
            arrow_cfg = GREEN_ARROW_X_MARKER_CFG.copy()
            arrow_cfg.prim_path = "/Visuals/Command/goal_heading"
            arrow_cfg.markers["arrow"].scale = (0.8, 0.12, 0.12)
            self._goal_arrow_visualizer = VisualizationMarkers(arrow_cfg)
        if self._goal_sphere_visualizer is None:
            sphere_cfg = GOAL_SPHERE_MARKER_CFG.copy()
            sphere_cfg.prim_path = "/Visuals/Command/goal_position"
            sphere_cfg.markers["sphere"].radius = 0.2
            self._goal_sphere_visualizer = VisualizationMarkers(sphere_cfg)

    def _ensure_wheel_motion_visualizers(self) -> None:
        if self._wheel_forward_visualizer is None:
            forward_cfg = GREEN_ARROW_X_MARKER_CFG.copy()
            forward_cfg.prim_path = "/Visuals/WheelMotion/rolling_direction"
            forward_cfg.markers["arrow"].scale = (1.0, 0.12, 0.12)
            self._wheel_forward_visualizer = VisualizationMarkers(forward_cfg)
        if self._wheel_velocity_visualizer is None:
            velocity_cfg = RED_ARROW_X_MARKER_CFG.copy()
            velocity_cfg.prim_path = "/Visuals/WheelMotion/actual_velocity"
            velocity_cfg.markers["arrow"].scale = (1.0, 0.12, 0.12)
            self._wheel_velocity_visualizer = VisualizationMarkers(velocity_cfg)

    def _ensure_follow_view_paths(self, num_envs: int, chase_env_index: int) -> None:
        if self._follow_view_count == num_envs and self._follow_view_chase_env_index == chase_env_index:
            return
        self._create_xform_if_missing(self._view_root_path)
        for env_id in range(num_envs):
            self._create_xform_if_missing(f"{self._view_root_path}/env_{env_id}")
            self._create_camera_if_missing(f"{self._view_root_path}/env_{env_id}/top_down_camera")
        if 0 <= chase_env_index < num_envs:
            self._create_xform_if_missing(f"{self._view_root_path}/env_{chase_env_index}")
            self._create_camera_if_missing(f"{self._view_root_path}/env_{chase_env_index}/chase_camera")
        self._follow_view_count = num_envs
        self._follow_view_chase_env_index = chase_env_index

    @staticmethod
    def _create_xform_if_missing(prim_path: str) -> None:
        stage = sim_utils.get_current_stage()
        if not stage.GetPrimAtPath(prim_path).IsValid():
            sim_utils.create_prim(prim_path, "Xform", stage=stage)

    @staticmethod
    def _create_camera_if_missing(prim_path: str) -> None:
        stage = sim_utils.get_current_stage()
        if not stage.GetPrimAtPath(prim_path).IsValid():
            sim_utils.create_prim(
                prim_path,
                "Camera",
                stage=stage,
                attributes={
                    "focalLength": 18.0,
                    "horizontalAperture": 20.955,
                    "clippingRange": (0.01, 1000.0),
                },
            )

    @staticmethod
    def _rotate_planar_offset(offset_b: tuple[float, float, float], yaw: float) -> tuple[float, float, float]:
        cos_yaw = torch.cos(torch.tensor(yaw)).item()
        sin_yaw = torch.sin(torch.tensor(yaw)).item()
        x_b, y_b, z_b = offset_b
        return (
            cos_yaw * x_b - sin_yaw * y_b,
            sin_yaw * x_b + cos_yaw * y_b,
            z_b,
        )
