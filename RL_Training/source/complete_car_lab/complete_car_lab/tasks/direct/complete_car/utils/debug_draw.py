"""调试绘图辅助。"""

from __future__ import annotations

import torch

import isaaclab.sim as sim_utils
from isaaclab.markers import VisualizationMarkers, VisualizationMarkersCfg
from isaaclab.markers.config import GREEN_ARROW_X_MARKER_CFG
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
        self._goal_arrow_height_offset = 0.25
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

    def _ensure_goal_pose_visualizers(self) -> None:
        if self._goal_arrow_visualizer is None:
            arrow_cfg = GREEN_ARROW_X_MARKER_CFG.copy()
            arrow_cfg.prim_path = "/Visuals/Command/goal_heading"
            arrow_cfg.markers["arrow"].scale = (0.2, 0.2, 0.8)
            self._goal_arrow_visualizer = VisualizationMarkers(arrow_cfg)
        if self._goal_sphere_visualizer is None:
            sphere_cfg = GOAL_SPHERE_MARKER_CFG.copy()
            sphere_cfg.prim_path = "/Visuals/Command/goal_position"
            sphere_cfg.markers["sphere"].radius = 0.2
            self._goal_sphere_visualizer = VisualizationMarkers(sphere_cfg)
