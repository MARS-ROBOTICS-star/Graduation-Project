"""完整车前向运动学接口。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


FRONT_BALL_JOINT_NAMES = (
    "spm1_platform_joint_z",
    "spm1_platform_joint_y",
    "spm1_platform_joint_x",
)

REAR_BALL_JOINT_NAMES = (
    "spm2_platform_joint_z",
    "spm2_platform_joint_y",
    "spm2_platform_joint_x",
)


def _as_joint_array(values: Sequence[float]) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.shape != (6,):
        raise ValueError(f"Expected 6 ball-joint positions, got shape {array.shape}.")
    return array


@dataclass(frozen=True)
class ModuleEulerAngles:
    """单个模块的欧拉角状态。"""

    roll: float
    pitch: float
    yaw: float

    def as_array(self) -> np.ndarray:
        return np.array([self.roll, self.pitch, self.yaw], dtype=np.float64)


@dataclass
class CompleteCarForwardKinematics:
    """完整车前向运动学接口。

    当前 direct workflow 使用串联球铰等效模型，因此这里直接按 z/y/x 关节恢复模块姿态。
    旧 MATLAB 推导文件仍保留在 `legacy_fk/` 里，作为后续核对和扩展参考。
    """

    front_joint_names: tuple[str, str, str] = FRONT_BALL_JOINT_NAMES
    rear_joint_names: tuple[str, str, str] = REAR_BALL_JOINT_NAMES

    def split_modules(self, joint_positions: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
        array = _as_joint_array(joint_positions)
        return array[:3], array[3:]

    @staticmethod
    def solve_module(joint_positions: Sequence[float]) -> dict[str, object]:
        module_joints = np.asarray(joint_positions, dtype=np.float64)
        if module_joints.shape != (3,):
            raise ValueError(f"Expected 3 module joint values, got shape {module_joints.shape}.")
        yaw, pitch, roll = module_joints.tolist()
        euler = ModuleEulerAngles(roll=roll, pitch=pitch, yaw=yaw)
        return {
            "joint_positions_zyx": module_joints,
            "euler": euler,
            "rpy": euler.as_array(),
        }

    def solve(self, joint_positions: Sequence[float]) -> dict[str, object]:
        front_joint_positions, rear_joint_positions = self.split_modules(joint_positions)
        front_state = self.solve_module(front_joint_positions)
        rear_state = self.solve_module(rear_joint_positions)
        return {
            "ball_joint_positions": _as_joint_array(joint_positions),
            "front": front_state,
            "rear": rear_state,
        }


__all__ = [
    "CompleteCarForwardKinematics",
    "ModuleEulerAngles",
]
