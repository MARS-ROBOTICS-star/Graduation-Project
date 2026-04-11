"""调试绘图占位接口。"""

from __future__ import annotations


class CompleteCarDebugDraw:
    """集中放置可选调试可视化入口，避免 env.py 直接依赖绘图细节。"""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def clear(self) -> None:
        if not self.enabled:
            return

    def draw_reset_points(self, *_args, **_kwargs) -> None:
        if not self.enabled:
            return

    def draw_command_vectors(self, *_args, **_kwargs) -> None:
        if not self.enabled:
            return
