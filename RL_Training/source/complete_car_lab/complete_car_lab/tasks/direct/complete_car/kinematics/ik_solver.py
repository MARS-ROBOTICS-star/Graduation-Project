"""完整车逆运动学接口。"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Literal, Sequence

import numpy as np


def _rot_x(angle: float) -> np.ndarray:
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, c, -s],
            [0.0, s, c],
        ],
        dtype=np.float64,
    )


def _rot_y(angle: float) -> np.ndarray:
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array(
        [
            [c, 0.0, s],
            [0.0, 1.0, 0.0],
            [-s, 0.0, c],
        ],
        dtype=np.float64,
    )


def _rot_z(angle: float) -> np.ndarray:
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array(
        [
            [c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )


def _wrap_to_pi(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def _as_rpy_array(values: Sequence[float] | None) -> np.ndarray:
    if values is None:
        return np.zeros(3, dtype=np.float64)
    array = np.asarray(values, dtype=np.float64)
    if array.shape != (3,):
        raise ValueError(f"RPY input must have shape (3,), got {array.shape}.")
    return array


@dataclass(frozen=True)
class Spherical3RRRIkParams:
    """单个 3RRR 球面并联模块的几何参数。"""

    alpha1: float = math.radians(90.0)
    alpha2: float = math.radians(90.0)
    beta: float = math.radians(54.75)
    gamma: float = math.radians(54.75)
    etas: tuple[float, float, float] = (
        math.radians(0.0),
        math.radians(120.0),
        math.radians(240.0),
    )


IKParams = Spherical3RRRIkParams


class Spherical3RRRInverseKinematics:
    """旧 `IK_model.py` 的核心求解器，现已迁入统一 `ik_solver.py`。"""

    def __init__(self, params: Spherical3RRRIkParams | None = None):
        self.params = params if params is not None else Spherical3RRRIkParams()

    def rotation_01(self, eta: float) -> np.ndarray:
        return _rot_z(eta + math.pi / 2.0) @ _rot_y(math.pi / 2.0 - self.params.gamma)

    def rotation_03(self, eta: float) -> np.ndarray:
        return _rot_z(eta + 5.0 * math.pi / 6.0) @ _rot_y(self.params.beta - math.pi / 2.0)

    def rotation_rpy(self, roll: float, pitch: float, yaw: float) -> np.ndarray:
        return _rot_z(yaw) @ _rot_y(pitch) @ _rot_x(roll)

    def w_i(self, eta: float, theta_i: float) -> np.ndarray:
        rotation_local = _rot_x(theta_i) @ _rot_z(self.params.alpha1)
        rotation_world = self.rotation_01(eta) @ rotation_local
        return rotation_world[:, 0]

    def v_i(self, eta: float, roll: float, pitch: float, yaw: float) -> np.ndarray:
        rotation_world = self.rotation_rpy(roll, pitch, yaw) @ self.rotation_03(eta)
        return rotation_world[:, 0]

    def abc_leg(self, eta: float, roll: float, pitch: float, yaw: float) -> tuple[float, float, float]:
        v_x, v_y, v_z = self.v_i(eta, roll, pitch, yaw).tolist()
        a_term = math.sin(self.params.alpha1) * (
            v_z * math.sin(self.params.gamma)
            + v_y * math.cos(eta) * math.cos(self.params.gamma)
            - v_x * math.cos(self.params.gamma) * math.sin(eta)
        )
        b_term = -math.sin(self.params.alpha1) * (v_x * math.cos(eta) + v_y * math.sin(eta))
        d_term = (
            v_y * math.cos(self.params.alpha1) * math.cos(eta) * math.sin(self.params.gamma)
            - v_z * math.cos(self.params.alpha1) * math.cos(self.params.gamma)
            - math.cos(self.params.alpha2)
            - v_x * math.cos(self.params.alpha1) * math.sin(eta) * math.sin(self.params.gamma)
        )
        return d_term - b_term, 2.0 * a_term, b_term + d_term

    def solve_leg_all_branches(
        self,
        eta: float,
        roll: float,
        pitch: float,
        yaw: float,
        eps: float = 1.0e-12,
    ) -> dict[str, object]:
        a_term, b_term, c_term = self.abc_leg(eta, roll, pitch, yaw)
        delta = b_term * b_term - 4.0 * a_term * c_term
        result: dict[str, object] = {
            "A": a_term,
            "B": b_term,
            "C": c_term,
            "Delta": delta,
            "roots_t": [],
            "roots_theta": [],
        }
        if delta < -eps:
            return result

        delta = max(delta, 0.0)
        if abs(a_term) > eps:
            sqrt_delta = math.sqrt(delta)
            roots_t = [
                (-b_term + sqrt_delta) / (2.0 * a_term),
                (-b_term - sqrt_delta) / (2.0 * a_term),
            ]
            roots_theta = [_wrap_to_pi(2.0 * math.atan(value)) for value in roots_t]
            result["roots_t"] = roots_t
            result["roots_theta"] = roots_theta
            return result

        if abs(b_term) > eps:
            root_t = -c_term / b_term
            result["roots_t"] = [root_t]
            result["roots_theta"] = [_wrap_to_pi(2.0 * math.atan(root_t))]
        return result

    @staticmethod
    def pick_branch(
        candidates: Sequence[float],
        prev_q: float | None = None,
        prefer: Literal["first", "second"] = "first",
    ) -> float:
        if not candidates:
            raise ValueError("No valid IK branch for this leg.")
        if prev_q is not None:
            return min(candidates, key=lambda value: abs(_wrap_to_pi(value - prev_q)))
        if prefer == "second" and len(candidates) >= 2:
            return candidates[1]
        return candidates[0]

    def solve(
        self,
        roll: float,
        pitch: float,
        yaw: float,
        prev_q: Sequence[float] | None = None,
        prefer: Literal["first", "second"] = "first",
    ) -> dict[str, object]:
        joint_angles: list[float] = []
        all_branches: list[dict[str, object]] = []
        for index, eta in enumerate(self.params.etas):
            branch_info = self.solve_leg_all_branches(eta, roll, pitch, yaw)
            all_branches.append(branch_info)
            previous_angle = None if prev_q is None else prev_q[index]
            joint_angles.append(self.pick_branch(branch_info["roots_theta"], prev_q=previous_angle, prefer=prefer))
        return {"q": joint_angles, "all_branches": all_branches}

    def compute_home_offsets(self, prefer: Literal["first", "second"] = "first") -> list[float]:
        return self.solve(0.0, 0.0, 0.0, prefer=prefer)["q"]

    @staticmethod
    def map_to_sim_joints(
        q_math: Sequence[float],
        q_home: Sequence[float],
        signs: Sequence[int] = (1, 1, 1),
        biases: Sequence[float] = (0.0, 0.0, 0.0),
    ) -> list[float]:
        return [signs[index] * (q_math[index] - q_home[index]) + biases[index] for index in range(3)]

    def residual(self, eta: float, theta_i: float, roll: float, pitch: float, yaw: float) -> float:
        return float(np.dot(self.w_i(eta, theta_i), self.v_i(eta, roll, pitch, yaw)) - math.cos(self.params.alpha2))

    def verify_solution(self, q: Sequence[float], roll: float, pitch: float, yaw: float) -> list[float]:
        return [self.residual(eta, q_i, roll, pitch, yaw) for eta, q_i in zip(self.params.etas, q, strict=True)]


IK_3RRR_Spherical = Spherical3RRRInverseKinematics


@dataclass
class CompleteCarInverseKinematics:
    """完整车逆运动学接口。

    当前前后两套模块共用相同的 3RRR 参数。输出顺序对齐 direct env 中的 6 个球铰自由度。
    """

    front_solver: Spherical3RRRInverseKinematics = field(default_factory=Spherical3RRRInverseKinematics)
    rear_solver: Spherical3RRRInverseKinematics = field(default_factory=Spherical3RRRInverseKinematics)
    signs_front: tuple[int, int, int] = (1, 1, 1)
    signs_rear: tuple[int, int, int] = (1, 1, 1)
    biases_front: tuple[float, float, float] = (0.0, 0.0, 0.0)
    biases_rear: tuple[float, float, float] = (0.0, 0.0, 0.0)
    prefer_branch: Literal["first", "second"] = "first"
    front_home_offsets: np.ndarray | None = None
    rear_home_offsets: np.ndarray | None = None
    default_output_dim: int = 6

    def __post_init__(self) -> None:
        if self.front_home_offsets is None:
            self.front_home_offsets = np.asarray(
                self.front_solver.compute_home_offsets(prefer=self.prefer_branch),
                dtype=np.float64,
            )
        else:
            self.front_home_offsets = np.asarray(self.front_home_offsets, dtype=np.float64)
        if self.rear_home_offsets is None:
            self.rear_home_offsets = np.asarray(
                self.rear_solver.compute_home_offsets(prefer=self.prefer_branch),
                dtype=np.float64,
            )
        else:
            self.rear_home_offsets = np.asarray(self.rear_home_offsets, dtype=np.float64)

    def solve_module(
        self,
        module_rpy: Sequence[float] | None,
        *,
        solver: Spherical3RRRInverseKinematics,
        home_offsets: Sequence[float],
        signs: Sequence[int],
        biases: Sequence[float],
        prev_q: Sequence[float] | None = None,
        prefer: Literal["first", "second"] | None = None,
    ) -> dict[str, object]:
        roll, pitch, yaw = _as_rpy_array(module_rpy).tolist()
        prefer = prefer or self.prefer_branch
        result = solver.solve(roll, pitch, yaw, prev_q=prev_q, prefer=prefer)
        q_math = np.asarray(result["q"], dtype=np.float64)
        q_sim = np.asarray(
            solver.map_to_sim_joints(q_math.tolist(), list(home_offsets), signs=signs, biases=biases),
            dtype=np.float64,
        )
        residuals = np.asarray(solver.verify_solution(q_math.tolist(), roll, pitch, yaw), dtype=np.float64)
        return {
            "rpy": np.array([roll, pitch, yaw], dtype=np.float64),
            "q_math": q_math,
            "q_sim": q_sim,
            "residuals": residuals,
            "all_branches": result["all_branches"],
        }

    def solve(
        self,
        front_rpy: Sequence[float] | None = None,
        rear_rpy: Sequence[float] | None = None,
        *,
        prev_front_q: Sequence[float] | None = None,
        prev_rear_q: Sequence[float] | None = None,
        prefer: Literal["first", "second"] | None = None,
    ) -> dict[str, object]:
        # 当前 direct env 仍以串联球铰动作为主，这里先把完整 IK 接口收口，便于后续接入策略或键盘验证。
        front_result = self.solve_module(
            front_rpy,
            solver=self.front_solver,
            home_offsets=self.front_home_offsets,
            signs=self.signs_front,
            biases=self.biases_front,
            prev_q=prev_front_q,
            prefer=prefer,
        )
        rear_result = self.solve_module(
            rear_rpy,
            solver=self.rear_solver,
            home_offsets=self.rear_home_offsets,
            signs=self.signs_rear,
            biases=self.biases_rear,
            prev_q=prev_rear_q,
            prefer=prefer,
        )
        ball_joint_targets = np.concatenate((front_result["q_sim"], rear_result["q_sim"]), axis=0)
        return {
            "front": front_result,
            "rear": rear_result,
            "ball_joint_targets": ball_joint_targets,
        }


__all__ = [
    "CompleteCarInverseKinematics",
    "IK_3RRR_Spherical",
    "IKParams",
    "Spherical3RRRIkParams",
    "Spherical3RRRInverseKinematics",
]
