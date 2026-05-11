"""调试绘图辅助。"""

from __future__ import annotations

import torch

import isaaclab.sim as sim_utils
from isaaclab.markers import VisualizationMarkers, VisualizationMarkersCfg
from isaaclab.utils.math import quat_from_euler_xyz


GOAL_SPHERE_MARKER_CFG = VisualizationMarkersCfg(
    markers={
        "sphere": sim_utils.SphereCfg(
            radius=0.2,
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(1.0, 0.0, 0.0)),
        ),
    }
)


def _make_local_x_axis_marker_cfg(
    prim_path: str,
    color: tuple[float, float, float],
    length: float,
    radius: float,
) -> VisualizationMarkersCfg:
    return VisualizationMarkersCfg(
        prim_path=prim_path,
        markers={
            "axis": sim_utils.CylinderCfg(
                radius=radius,
                height=length,
                axis="X",
                visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=color),
            ),
        },
    )


HEIGHT_PATCH_COLORS = (
    (0.05, 0.18, 1.0),
    (0.0, 0.75, 1.0),
    (0.0, 0.9, 0.25),
    (1.0, 0.86, 0.0),
    (1.0, 0.12, 0.02),
)


def _make_height_patch_marker_cfg(radius: float) -> VisualizationMarkersCfg:
    return VisualizationMarkersCfg(
        prim_path="/Visuals/HeightPatch/sample_points",
        markers={
            f"bin_{index}": sim_utils.SphereCfg(
                radius=radius,
                visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=color),
            )
            for index, color in enumerate(HEIGHT_PATCH_COLORS)
        },
    )


class CompleteCarDebugDraw:
    """集中放置可选调试可视化入口，避免 env.py 直接依赖绘图细节。"""

    def __init__(
        self,
        enabled: bool = False,
        visualize_goal_position: bool = True,
        visualize_goal_heading: bool = True,
        height_patch_marker_radius: float = 0.035,
    ):
        self.enabled = enabled
        self.visualize_goal_position = visualize_goal_position
        self.visualize_goal_heading = visualize_goal_heading
        self._goal_arrow_visualizer: VisualizationMarkers | None = None
        self._goal_sphere_visualizer: VisualizationMarkers | None = None
        self._wheel_forward_visualizer: VisualizationMarkers | None = None
        self._wheel_velocity_visualizer: VisualizationMarkers | None = None
        self._height_patch_visualizer: VisualizationMarkers | None = None
        self._height_patch_positive_y_visualizer: VisualizationMarkers | None = None
        self._height_patch_marker_radius = height_patch_marker_radius
        self._goal_arrow_height_offset = 0.25
        self._wheel_arrow_height_offset = 0.0
        self._view_root_path = "/view"
        self._follow_view_count = 0
        self._follow_view_chase_env_index = 0
        self._follow_view_env_ids: tuple[int, ...] = ()
        if self.enabled and (self.visualize_goal_position or self.visualize_goal_heading):
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
        if visible and self.enabled and (self.visualize_goal_position or self.visualize_goal_heading):
            self._ensure_goal_pose_visualizers()
        if self._goal_arrow_visualizer is not None:
            self._goal_arrow_visualizer.set_visibility(visible)
        if self._goal_sphere_visualizer is not None:
            self._goal_sphere_visualizer.set_visibility(visible)
        if self._wheel_forward_visualizer is not None:
            self._wheel_forward_visualizer.set_visibility(visible)
        if self._wheel_velocity_visualizer is not None:
            self._wheel_velocity_visualizer.set_visibility(visible)
        if self._height_patch_visualizer is not None:
            self._height_patch_visualizer.set_visibility(visible)
        if self._height_patch_positive_y_visualizer is not None:
            self._height_patch_positive_y_visualizer.set_visibility(visible)

    def draw_goal_pose(self, goal_positions_w: torch.Tensor, goal_headings_w: torch.Tensor) -> None:
        if not self.enabled or not (self.visualize_goal_position or self.visualize_goal_heading):
            return

        self._ensure_goal_pose_visualizers()
        if self.visualize_goal_position:
            self._goal_sphere_visualizer.visualize(translations=goal_positions_w)

        if self.visualize_goal_heading:
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

    def draw_height_patch(
        self,
        patch_points_w: torch.Tensor,
        *,
        height_offset: float,
        color_range_m: float,
        positive_y_axis_w: torch.Tensor | None = None,
    ) -> None:
        """Draw sampled local height-patch points at their world-space terrain height."""
        if not self.enabled:
            return
        if patch_points_w.numel() == 0:
            return

        self._ensure_height_patch_visualizer()

        marker_positions = patch_points_w.reshape(-1, 3).clone()
        marker_positions[:, 2] += float(height_offset)

        terrain_z = patch_points_w[..., 2]
        centered_height = terrain_z - torch.mean(terrain_z, dim=1, keepdim=True)
        normalized = torch.clamp(
            (centered_height + float(color_range_m)) / max(2.0 * float(color_range_m), 1.0e-6),
            min=0.0,
            max=1.0,
        )
        marker_indices = torch.clamp(
            torch.floor(normalized.reshape(-1) * len(HEIGHT_PATCH_COLORS)).long(),
            min=0,
            max=len(HEIGHT_PATCH_COLORS) - 1,
        )
        self._height_patch_visualizer.visualize(
            translations=marker_positions,
            marker_indices=marker_indices,
        )

        if positive_y_axis_w is None:
            return

        self._ensure_height_patch_positive_y_visualizer()
        axis = torch.nan_to_num(positive_y_axis_w, nan=0.0, posinf=0.0, neginf=0.0)
        axis_xy_norm = torch.linalg.vector_norm(axis[:, :2], dim=1, keepdim=True).clamp(min=1.0e-6)
        axis = axis / axis_xy_norm
        patch_center_w = torch.mean(patch_points_w, dim=1)
        arrow_positions = patch_center_w + 0.45 * axis
        arrow_positions[:, 2] = torch.mean(patch_points_w[..., 2], dim=1) + float(height_offset) + 0.25
        arrow_yaw = torch.atan2(axis[:, 1], axis[:, 0])
        zero = torch.zeros_like(arrow_yaw)
        arrow_orientations = quat_from_euler_xyz(zero, zero, arrow_yaw)
        arrow_scales = torch.zeros((arrow_positions.shape[0], 3), device=arrow_positions.device, dtype=arrow_positions.dtype)
        arrow_scales[:, 0] = 0.9
        arrow_scales[:, 1:] = 0.16
        self._height_patch_positive_y_visualizer.visualize(
            translations=arrow_positions,
            orientations=arrow_orientations,
            scales=arrow_scales,
        )

    def update_follow_views(
        self,
        sim,
        root_positions_w: torch.Tensor,
        root_yaws_w: torch.Tensor,
        *,
        top_height: float,
        chase_env_index: int,
        chase_env_indices: tuple[int, ...] = (),
        chase_offset_b: tuple[float, float, float],
        chase_target_offset_b: tuple[float, float, float],
        forward_height_m: float,
        forward_distance_m: float,
        right_side_distance_m: float,
    ) -> None:
        """Create/update selectable USD cameras under /view for playback inspection."""
        if not self.enabled:
            return

        root_positions = root_positions_w.detach().cpu()
        root_yaws = root_yaws_w.detach().cpu()
        num_envs = int(root_positions.shape[0])
        if chase_env_indices:
            view_env_ids = tuple(sorted({int(env_id) for env_id in chase_env_indices if 0 <= int(env_id) < num_envs}))
        else:
            view_env_ids = (chase_env_index,) if 0 <= chase_env_index < num_envs else (0,)
        if not view_env_ids:
            view_env_ids = (0,)
        self._ensure_follow_view_paths(view_env_ids, chase_env_index)

        for env_id in view_env_ids:
            root_pos = root_positions[env_id]
            eye = (float(root_pos[0]), float(root_pos[1]), float(root_pos[2] + top_height))
            target = (float(root_pos[0]), float(root_pos[1]), float(root_pos[2]))
            sim.set_camera_view(eye=eye, target=target, camera_prim_path=f"{self._view_root_path}/env_{env_id}/top_down_camera")

        for env_id in view_env_ids:
            root_pos = root_positions[env_id]
            yaw = float(root_yaws[env_id])
            eye_offset = self._rotate_planar_offset(chase_offset_b, yaw)
            left_chase_offset_b = (chase_offset_b[0], -chase_offset_b[1], chase_offset_b[2])
            left_eye_offset = self._rotate_planar_offset(left_chase_offset_b, yaw)
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
                camera_prim_path=f"{self._view_root_path}/env_{env_id}/chase_camera",
            )
            left_eye = (
                float(root_pos[0] + left_eye_offset[0]),
                float(root_pos[1] + left_eye_offset[1]),
                float(root_pos[2] + left_eye_offset[2]),
            )
            sim.set_camera_view(
                eye=left_eye,
                target=target,
                camera_prim_path=f"{self._view_root_path}/env_{env_id}/left_chase_camera",
            )

            forward_height = float(forward_height_m)
            forward_distance = max(float(forward_distance_m), 0.1)
            forward_target_offset = self._rotate_planar_offset((forward_distance, 0.0, forward_height), yaw)
            forward_eye = (
                float(root_pos[0]),
                float(root_pos[1]),
                float(root_pos[2] + forward_height),
            )
            forward_target = (
                float(root_pos[0] + forward_target_offset[0]),
                float(root_pos[1] + forward_target_offset[1]),
                float(root_pos[2] + forward_target_offset[2]),
            )
            sim.set_camera_view(
                eye=forward_eye,
                target=forward_target,
                camera_prim_path=f"{self._view_root_path}/env_{env_id}/forward_camera",
            )

            right_side_distance = max(float(right_side_distance_m), 0.1)
            right_side_eye_offset = self._rotate_planar_offset((0.0, -right_side_distance, 0.0), yaw)
            right_side_eye = (
                float(root_pos[0] + right_side_eye_offset[0]),
                float(root_pos[1] + right_side_eye_offset[1]),
                float(root_pos[2] + right_side_eye_offset[2]),
            )
            right_side_target = (
                float(root_pos[0]),
                float(root_pos[1]),
                float(root_pos[2]),
            )
            sim.set_camera_view(
                eye=right_side_eye,
                target=right_side_target,
                camera_prim_path=f"{self._view_root_path}/env_{env_id}/right_side_camera",
            )

    def _ensure_goal_pose_visualizers(self) -> None:
        if self.visualize_goal_heading and self._goal_arrow_visualizer is None:
            self._goal_arrow_visualizer = VisualizationMarkers(
                _make_local_x_axis_marker_cfg(
                    prim_path="/Visuals/Command/goal_heading",
                    color=(0.0, 1.0, 0.0),
                    length=0.8,
                    radius=0.04,
                )
            )
        if self.visualize_goal_position and self._goal_sphere_visualizer is None:
            sphere_cfg = GOAL_SPHERE_MARKER_CFG.copy()
            sphere_cfg.prim_path = "/Visuals/Command/goal_position"
            sphere_cfg.markers["sphere"].radius = 0.2
            self._goal_sphere_visualizer = VisualizationMarkers(sphere_cfg)

    def _ensure_wheel_motion_visualizers(self) -> None:
        if self._wheel_forward_visualizer is None:
            self._wheel_forward_visualizer = VisualizationMarkers(
                _make_local_x_axis_marker_cfg(
                    prim_path="/Visuals/WheelMotion/rolling_direction",
                    color=(0.0, 1.0, 0.0),
                    length=1.0,
                    radius=0.045,
                )
            )
        if self._wheel_velocity_visualizer is None:
            self._wheel_velocity_visualizer = VisualizationMarkers(
                _make_local_x_axis_marker_cfg(
                    prim_path="/Visuals/WheelMotion/actual_velocity",
                    color=(1.0, 0.0, 0.0),
                    length=1.0,
                    radius=0.045,
                )
            )

    def _ensure_height_patch_visualizer(self) -> None:
        if self._height_patch_visualizer is None:
            radius = max(float(self._height_patch_marker_radius), 1.0e-4)
            self._height_patch_visualizer = VisualizationMarkers(_make_height_patch_marker_cfg(radius))

    def _ensure_height_patch_positive_y_visualizer(self) -> None:
        if self._height_patch_positive_y_visualizer is None:
            self._height_patch_positive_y_visualizer = VisualizationMarkers(
                _make_local_x_axis_marker_cfg(
                    prim_path="/Visuals/HeightPatch/positive_y_axis",
                    color=(1.0, 0.0, 0.0),
                    length=0.9,
                    radius=0.06,
                )
            )

    def _ensure_follow_view_paths(self, view_env_ids: tuple[int, ...], chase_env_index: int) -> None:
        if self._follow_view_env_ids == view_env_ids and self._follow_view_chase_env_index == chase_env_index:
            return
        self._create_xform_if_missing(self._view_root_path)
        for env_id in view_env_ids:
            self._create_xform_if_missing(f"{self._view_root_path}/env_{env_id}")
            self._create_camera_if_missing(f"{self._view_root_path}/env_{env_id}/top_down_camera")
            self._create_camera_if_missing(f"{self._view_root_path}/env_{env_id}/chase_camera")
            self._create_camera_if_missing(f"{self._view_root_path}/env_{env_id}/left_chase_camera")
            self._create_camera_if_missing(f"{self._view_root_path}/env_{env_id}/forward_camera")
            self._create_camera_if_missing(f"{self._view_root_path}/env_{env_id}/right_side_camera")
        self._follow_view_count = len(view_env_ids)
        self._follow_view_chase_env_index = chase_env_index
        self._follow_view_env_ids = view_env_ids

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
