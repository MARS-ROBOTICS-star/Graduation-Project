"""Low-slip low-level ball-joint planner and traction allocator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


BALL_JOINT_NAMES = (
    "spm1_platform_joint_z",
    "spm1_platform_joint_y",
    "spm1_platform_joint_x",
    "spm2_platform_joint_z",
    "spm2_platform_joint_y",
    "spm2_platform_joint_x",
)

PAPER_WHEEL_JOINT_NAMES = (
    "head_car_wheel_left_joint",
    "head_car_wheel_right_joint",
    "body_car_wheel_left_joint",
    "body_car_wheel_right_joint",
    "tail_car_wheel_left_joint",
    "tail_car_wheel_right_joint",
)

OUTPUT_WHEEL_JOINT_NAMES = (
    "body_car_wheel_left_joint",
    "body_car_wheel_right_joint",
    "head_car_wheel_left_joint",
    "head_car_wheel_right_joint",
    "tail_car_wheel_left_joint",
    "tail_car_wheel_right_joint",
)


@dataclass(frozen=True)
class CompleteCarWheelAllocatorGeometry:
    """Geometry parameters used by the Chapter03 low-slip model."""

    a_x: float = 0.25633374
    b_f: float = 0.30654739
    b_r: float = 0.30633826
    l1: float = -0.00989449
    l2: float = 0.00000932
    l3: float = 0.00968251
    d1: float = 0.44737875
    d2: float = 0.44737968
    d3: float = 0.44737875
    h1: float = -0.043083285
    h2: float = -0.02578188
    h3: float = -0.043100655
    r_wheel: float = 0.19
    ball_joint_names: tuple[str, ...] = BALL_JOINT_NAMES
    wheel_joint_names: tuple[str, ...] = OUTPUT_WHEEL_JOINT_NAMES
    paper_wheel_joint_names: tuple[str, ...] = PAPER_WHEEL_JOINT_NAMES


@dataclass
class BallJointPlannerOutputs:
    """Planner outputs from Chapter03 equations (3.26) and (3.27)."""

    ball_joint_position_targets: Any
    ball_joint_rate_targets: Any


@dataclass
class WheelKinematicState:
    """Wheel-center kinematics in the middle-body frame {B2}."""

    wheel_positions: Any
    rolling_directions: Any
    lateral_directions: Any
    position_jacobians: Any


@dataclass
class ShapedPlanarCommandOutputs:
    """Outputs of the low-slip planar-command shaper."""

    desired_planar_command: Any
    shaped_planar_command: Any
    contact_weights: Any
    lateral_velocity_nominal: Any
    lateral_cost: Any


@dataclass
class WheelReferenceOutputs:
    """Nominal wheel-center and rolling references after command shaping."""

    wheel_center_velocity_nominal: Any
    rolling_speed_reference: Any
    wheel_speed_reference: Any
    wheel_speed_jacobian: Any
    posture_rate_jacobian: Any


@dataclass
class WheelTractionOutputs:
    """Wheel-level longitudinal slip and torque targets."""

    longitudinal_slip: Any
    wheel_torque_targets: Any


@dataclass
class LowSlipControlOutputs(BallJointPlannerOutputs):
    """Complete outputs for posture planner + low-slip traction allocator."""

    desired_planar_command: Any
    shaped_planar_command: Any
    contact_weights: Any
    wheel_center_velocity_nominal: Any
    rolling_speed_reference: Any
    wheel_speed_reference: Any
    wheel_torque_targets: Any
    lateral_velocity_nominal: Any
    lateral_cost: Any
    longitudinal_slip: Any
    wheel_speed_jacobian: Any
    posture_rate_jacobian: Any


DEFAULT_COMPLETE_CAR_GEOMETRY = CompleteCarWheelAllocatorGeometry()


def _build_local_wheel_vectors(geometry: CompleteCarWheelAllocatorGeometry) -> dict[str, np.ndarray]:
    return {
        "front_left": np.asarray((geometry.l1 - geometry.b_f, geometry.d1 / 2.0, geometry.h1), dtype=np.float64),
        "front_right": np.asarray((geometry.l1 - geometry.b_f, -geometry.d1 / 2.0, geometry.h1), dtype=np.float64),
        "middle_left": np.asarray((geometry.l2, geometry.d2 / 2.0, geometry.h2), dtype=np.float64),
        "middle_right": np.asarray((geometry.l2, -geometry.d2 / 2.0, geometry.h2), dtype=np.float64),
        "rear_left": np.asarray((geometry.l3 + geometry.b_r, geometry.d3 / 2.0, geometry.h3), dtype=np.float64),
        "rear_right": np.asarray((geometry.l3 + geometry.b_r, -geometry.d3 / 2.0, geometry.h3), dtype=np.float64),
    }


def compute_longitudinal_slip_torch(
    rolling_speed_actual,
    wheel_joint_vel,
    wheel_radius: float,
    slip_velocity_epsilon: float,
    *,
    clip: float | None = None,
):
    """Shared torch implementation of longitudinal slip.

    This is the single source of truth for the runtime slip definition used by both
    the low-level allocator and the observation/diagnostic path.
    """

    import torch

    wheel_radius_tensor = torch.as_tensor(
        wheel_radius,
        device=rolling_speed_actual.device,
        dtype=rolling_speed_actual.dtype,
    )
    safe_speed = torch.maximum(
        torch.abs(rolling_speed_actual),
        torch.full_like(rolling_speed_actual, slip_velocity_epsilon),
    )
    longitudinal_slip = (rolling_speed_actual - wheel_radius_tensor * wheel_joint_vel) / safe_speed
    if clip is not None:
        longitudinal_slip = torch.clamp(longitudinal_slip, min=-clip, max=clip)
    return longitudinal_slip


class NumpyWheelSpeedAllocator:
    """NumPy implementation for offline validation and formula checks."""

    def __init__(self, geometry: CompleteCarWheelAllocatorGeometry | None = None):
        self.geometry = geometry or DEFAULT_COMPLETE_CAR_GEOMETRY
        self._local_vectors = _build_local_wheel_vectors(self.geometry)
        self._a_front = np.asarray((self.geometry.a_x, 0.0, 0.0), dtype=np.float64)
        self._a_rear = np.asarray((-self.geometry.a_x, 0.0, 0.0), dtype=np.float64)
        self._e_x = np.asarray((1.0, 0.0, 0.0), dtype=np.float64)
        self._e_y = np.asarray((0.0, 1.0, 0.0), dtype=np.float64)

    @staticmethod
    def _ensure_2d(values, expected_last_dim: int, name: str) -> tuple[np.ndarray, bool]:
        array = np.asarray(values, dtype=np.float64)
        if array.ndim == 1:
            if array.shape[0] != expected_last_dim:
                raise ValueError(f"{name} must have shape ({expected_last_dim},), got {array.shape}.")
            return array.reshape(1, expected_last_dim), True
        if array.ndim != 2 or array.shape[1] != expected_last_dim:
            raise ValueError(f"{name} must have shape (N, {expected_last_dim}), got {array.shape}.")
        return array, False

    @staticmethod
    def _ensure_vector(values, expected_dim: int, name: str) -> np.ndarray:
        array = np.asarray(values, dtype=np.float64)
        if array.ndim == 0:
            return np.full(expected_dim, float(array), dtype=np.float64)
        if array.ndim == 1 and array.shape[0] == expected_dim:
            return array.astype(np.float64, copy=False)
        raise ValueError(f"{name} must be a scalar or a vector with shape ({expected_dim},), got {array.shape}.")

    @staticmethod
    def _broadcast_batch(*arrays: np.ndarray) -> tuple[list[np.ndarray], int]:
        batch_size = max(array.shape[0] for array in arrays)
        broadcasted = []
        for array in arrays:
            if array.shape[0] == batch_size:
                broadcasted.append(array)
            elif array.shape[0] == 1:
                broadcasted.append(np.repeat(array, batch_size, axis=0))
            else:
                raise ValueError("Inputs have incompatible batch dimensions.")
        return broadcasted, batch_size

    @staticmethod
    def _squeeze_if_needed(values: np.ndarray, squeeze_output: bool) -> np.ndarray:
        return values[0] if squeeze_output else values

    @staticmethod
    def _apply_rotation(rotation: np.ndarray, vector: np.ndarray) -> np.ndarray:
        return np.einsum("bij,j->bi", rotation, vector)

    @staticmethod
    def _dot_rows(lhs: np.ndarray, rhs: np.ndarray) -> np.ndarray:
        return np.einsum("bi,bi->b", lhs, rhs)

    @staticmethod
    def _cross_ez(position: np.ndarray) -> np.ndarray:
        zeros = np.zeros_like(position[:, 0])
        return np.stack((-position[:, 1], position[:, 0], zeros), axis=-1)

    @staticmethod
    def _sat(values: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
        return np.minimum(np.maximum(values, lower), upper)

    @staticmethod
    def _build_rotation_and_derivatives(module_angles: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        psi = module_angles[:, 0]
        theta = module_angles[:, 1]
        phi = module_angles[:, 2]

        c_psi = np.cos(psi)
        s_psi = np.sin(psi)
        c_theta = np.cos(theta)
        s_theta = np.sin(theta)
        c_phi = np.cos(phi)
        s_phi = np.sin(phi)

        rotation = np.stack(
            (
                np.stack(
                    (
                        c_psi * c_theta,
                        c_psi * s_theta * s_phi - s_psi * c_phi,
                        c_psi * s_theta * c_phi + s_psi * s_phi,
                    ),
                    axis=-1,
                ),
                np.stack(
                    (
                        s_psi * c_theta,
                        s_psi * s_theta * s_phi + c_psi * c_phi,
                        s_psi * s_theta * c_phi - c_psi * s_phi,
                    ),
                    axis=-1,
                ),
                np.stack((-s_theta, c_theta * s_phi, c_theta * c_phi), axis=-1),
            ),
            axis=1,
        )
        d_rotation_d_psi = np.stack(
            (
                np.stack(
                    (
                        -s_psi * c_theta,
                        -s_psi * s_theta * s_phi - c_psi * c_phi,
                        -s_psi * s_theta * c_phi + c_psi * s_phi,
                    ),
                    axis=-1,
                ),
                np.stack(
                    (
                        c_psi * c_theta,
                        c_psi * s_theta * s_phi - s_psi * c_phi,
                        c_psi * s_theta * c_phi + s_psi * s_phi,
                    ),
                    axis=-1,
                ),
                np.stack((np.zeros_like(psi), np.zeros_like(psi), np.zeros_like(psi)), axis=-1),
            ),
            axis=1,
        )
        d_rotation_d_theta = np.stack(
            (
                np.stack((-c_psi * s_theta, c_psi * c_theta * s_phi, c_psi * c_theta * c_phi), axis=-1),
                np.stack((-s_psi * s_theta, s_psi * c_theta * s_phi, s_psi * c_theta * c_phi), axis=-1),
                np.stack((-c_theta, -s_theta * s_phi, -s_theta * c_phi), axis=-1),
            ),
            axis=1,
        )
        d_rotation_d_phi = np.stack(
            (
                np.stack(
                    (
                        np.zeros_like(phi),
                        c_psi * s_theta * c_phi + s_psi * s_phi,
                        -c_psi * s_theta * s_phi + s_psi * c_phi,
                    ),
                    axis=-1,
                ),
                np.stack(
                    (
                        np.zeros_like(phi),
                        s_psi * s_theta * c_phi - c_psi * s_phi,
                        -s_psi * s_theta * s_phi - c_psi * c_phi,
                    ),
                    axis=-1,
                ),
                np.stack((np.zeros_like(phi), c_theta * c_phi, -c_theta * s_phi), axis=-1),
            ),
            axis=1,
        )
        return rotation, d_rotation_d_psi, d_rotation_d_theta, d_rotation_d_phi

    def compute_ball_joint_planner_outputs(
        self,
        ball_joint_pos,
        desired_ball_joint_pos,
        control_dt: float,
        planner_gains,
        planner_qdot_limits,
        q_lower_limits,
        q_upper_limits,
    ) -> BallJointPlannerOutputs:
        ball_joint_pos, squeeze_pos = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        desired_ball_joint_pos, squeeze_desired = self._ensure_2d(desired_ball_joint_pos, 6, "desired_ball_joint_pos")
        (ball_joint_pos, desired_ball_joint_pos), _ = self._broadcast_batch(ball_joint_pos, desired_ball_joint_pos)

        gains = self._ensure_vector(planner_gains, 6, "planner_gains").reshape(1, 6)
        qdot_limits = self._ensure_vector(planner_qdot_limits, 6, "planner_qdot_limits").reshape(1, 6)
        q_lower = self._ensure_vector(q_lower_limits, 6, "q_lower_limits").reshape(1, 6)
        q_upper = self._ensure_vector(q_upper_limits, 6, "q_upper_limits").reshape(1, 6)

        qdot_cmd_raw = gains * (desired_ball_joint_pos - ball_joint_pos)
        qdot_cmd = self._sat(qdot_cmd_raw, -qdot_limits, qdot_limits)
        q_cmd = self._sat(ball_joint_pos + float(control_dt) * qdot_cmd, q_lower, q_upper)

        squeeze_output = squeeze_pos and squeeze_desired
        return BallJointPlannerOutputs(
            ball_joint_position_targets=self._squeeze_if_needed(q_cmd, squeeze_output),
            ball_joint_rate_targets=self._squeeze_if_needed(qdot_cmd, squeeze_output),
        )

    def _compute_front_rear_wheel_kinematics(self, ball_joint_pos: np.ndarray) -> dict[str, np.ndarray]:
        front_angles = ball_joint_pos[:, :3]
        rear_angles = ball_joint_pos[:, 3:]

        r_front, dr_front_d_psi, dr_front_d_theta, dr_front_d_phi = self._build_rotation_and_derivatives(front_angles)
        r_rear, dr_rear_d_psi, dr_rear_d_theta, dr_rear_d_phi = self._build_rotation_and_derivatives(rear_angles)

        t_front = self._apply_rotation(r_front, self._e_x)
        t_rear = self._apply_rotation(r_rear, self._e_x)
        n_front = self._apply_rotation(r_front, self._e_y)
        n_rear = self._apply_rotation(r_rear, self._e_y)

        front_left_pos = self._a_front + self._apply_rotation(r_front, self._local_vectors["front_left"])
        front_right_pos = self._a_front + self._apply_rotation(r_front, self._local_vectors["front_right"])
        rear_left_pos = self._a_rear + self._apply_rotation(r_rear, self._local_vectors["rear_left"])
        rear_right_pos = self._a_rear + self._apply_rotation(r_rear, self._local_vectors["rear_right"])

        zeros = np.zeros_like(front_left_pos)

        def front_position_jacobian(local_vector: np.ndarray) -> np.ndarray:
            return np.stack(
                (
                    self._apply_rotation(dr_front_d_psi, local_vector),
                    self._apply_rotation(dr_front_d_theta, local_vector),
                    self._apply_rotation(dr_front_d_phi, local_vector),
                    zeros,
                    zeros,
                    zeros,
                ),
                axis=-1,
            )

        def rear_position_jacobian(local_vector: np.ndarray) -> np.ndarray:
            return np.stack(
                (
                    zeros,
                    zeros,
                    zeros,
                    self._apply_rotation(dr_rear_d_psi, local_vector),
                    self._apply_rotation(dr_rear_d_theta, local_vector),
                    self._apply_rotation(dr_rear_d_phi, local_vector),
                ),
                axis=-1,
            )

        return {
            "front_left_pos": front_left_pos,
            "front_right_pos": front_right_pos,
            "rear_left_pos": rear_left_pos,
            "rear_right_pos": rear_right_pos,
            "front_t": t_front,
            "rear_t": t_rear,
            "front_n": n_front,
            "rear_n": n_rear,
            "front_left_g": front_position_jacobian(self._local_vectors["front_left"]),
            "front_right_g": front_position_jacobian(self._local_vectors["front_right"]),
            "rear_left_g": rear_position_jacobian(self._local_vectors["rear_left"]),
            "rear_right_g": rear_position_jacobian(self._local_vectors["rear_right"]),
        }

    def compute_wheel_kinematic_state(self, ball_joint_pos) -> WheelKinematicState:
        ball_joint_pos, squeeze_output = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        kinematics = self._compute_front_rear_wheel_kinematics(ball_joint_pos)

        batch_size = ball_joint_pos.shape[0]
        middle_left_pos = np.repeat(self._local_vectors["middle_left"][None, :], batch_size, axis=0)
        middle_right_pos = np.repeat(self._local_vectors["middle_right"][None, :], batch_size, axis=0)
        middle_t = np.repeat(self._e_x[None, :], batch_size, axis=0)
        middle_n = np.repeat(self._e_y[None, :], batch_size, axis=0)
        middle_g = np.zeros((batch_size, 3, 6), dtype=np.float64)

        wheel_positions = np.stack(
            (
                middle_left_pos,
                middle_right_pos,
                kinematics["front_left_pos"],
                kinematics["front_right_pos"],
                kinematics["rear_left_pos"],
                kinematics["rear_right_pos"],
            ),
            axis=1,
        )
        rolling_directions = np.stack(
            (
                middle_t,
                middle_t.copy(),
                kinematics["front_t"],
                kinematics["front_t"],
                kinematics["rear_t"],
                kinematics["rear_t"],
            ),
            axis=1,
        )
        lateral_directions = np.stack(
            (
                middle_n,
                middle_n.copy(),
                kinematics["front_n"],
                kinematics["front_n"],
                kinematics["rear_n"],
                kinematics["rear_n"],
            ),
            axis=1,
        )
        position_jacobians = np.stack(
            (
                middle_g,
                middle_g.copy(),
                kinematics["front_left_g"],
                kinematics["front_right_g"],
                kinematics["rear_left_g"],
                kinematics["rear_right_g"],
            ),
            axis=1,
        )
        return WheelKinematicState(
            wheel_positions=self._squeeze_if_needed(wheel_positions, squeeze_output),
            rolling_directions=self._squeeze_if_needed(rolling_directions, squeeze_output),
            lateral_directions=self._squeeze_if_needed(lateral_directions, squeeze_output),
            position_jacobians=self._squeeze_if_needed(position_jacobians, squeeze_output),
        )

    def compute_wheel_speed_jacobian(self, ball_joint_pos) -> np.ndarray:
        ball_joint_pos, squeeze_output = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        wheel_state = self.compute_wheel_kinematic_state(ball_joint_pos)
        if np.asarray(wheel_state.wheel_positions).ndim == 2:
            wheel_state = WheelKinematicState(
                wheel_positions=wheel_state.wheel_positions.reshape(1, 6, 3),
                rolling_directions=wheel_state.rolling_directions.reshape(1, 6, 3),
                lateral_directions=wheel_state.lateral_directions.reshape(1, 6, 3),
                position_jacobians=wheel_state.position_jacobians.reshape(1, 6, 3, 6),
            )
        e_x = np.repeat(self._e_x[None, None, :], ball_joint_pos.shape[0], axis=0)
        e_x = np.repeat(e_x, 6, axis=1)
        cross_terms = self._cross_ez(wheel_state.wheel_positions.reshape(-1, 3)).reshape(ball_joint_pos.shape[0], 6, 3)
        jacobian = (1.0 / self.geometry.r_wheel) * np.stack(
            (
                np.einsum("bwi,bwi->bw", wheel_state.rolling_directions, e_x),
                np.einsum("bwi,bwi->bw", wheel_state.rolling_directions, cross_terms),
            ),
            axis=-1,
        )
        return self._squeeze_if_needed(jacobian, squeeze_output)

    def compute_posture_rate_jacobian(self, ball_joint_pos) -> np.ndarray:
        ball_joint_pos, squeeze_output = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        wheel_state = self.compute_wheel_kinematic_state(ball_joint_pos)
        if np.asarray(wheel_state.position_jacobians).ndim == 3:
            wheel_state = WheelKinematicState(
                wheel_positions=wheel_state.wheel_positions.reshape(1, 6, 3),
                rolling_directions=wheel_state.rolling_directions.reshape(1, 6, 3),
                lateral_directions=wheel_state.lateral_directions.reshape(1, 6, 3),
                position_jacobians=wheel_state.position_jacobians.reshape(1, 6, 3, 6),
            )
        jacobian = (1.0 / self.geometry.r_wheel) * np.einsum(
            "bwi,bwij->bwj",
            wheel_state.rolling_directions,
            wheel_state.position_jacobians,
        )
        return self._squeeze_if_needed(jacobian, squeeze_output)

    def compute_contact_weights(
        self,
        wheel_normal_contact_force,
        contact_force_off_threshold: float,
        contact_force_on_threshold: float,
    ) -> np.ndarray:
        wheel_normal_contact_force, squeeze_output = self._ensure_2d(
            wheel_normal_contact_force,
            6,
            "wheel_normal_contact_force",
        )
        if contact_force_on_threshold <= contact_force_off_threshold:
            raise ValueError("contact_force_on_threshold must be greater than contact_force_off_threshold.")
        weights = (wheel_normal_contact_force - contact_force_off_threshold) / (
            contact_force_on_threshold - contact_force_off_threshold
        )
        weights = self._sat(weights, 0.0, 1.0)
        return self._squeeze_if_needed(weights, squeeze_output)

    def _compute_nominal_wheel_center_velocity(
        self,
        wheel_state: WheelKinematicState,
        planar_command: np.ndarray,
        ball_joint_rate_targets: np.ndarray,
    ) -> np.ndarray:
        batch_size = planar_command.shape[0]
        cross_terms = self._cross_ez(wheel_state.wheel_positions.reshape(-1, 3)).reshape(batch_size, 6, 3)
        translational = planar_command[:, 0][:, None, None] * self._e_x.reshape(1, 1, 3)
        rotational = planar_command[:, 1][:, None, None] * cross_terms
        posture = np.einsum("bwij,bj->bwi", wheel_state.position_jacobians, ball_joint_rate_targets)
        return translational + rotational + posture

    def shape_planar_command_for_low_slip(
        self,
        wheel_state: WheelKinematicState,
        desired_planar_command,
        ball_joint_rate_targets,
        wheel_normal_contact_force,
        lambda_tracking: float,
        lambda_lateral: float,
        planar_command_limits,
        contact_force_off_threshold: float,
        contact_force_on_threshold: float,
    ) -> ShapedPlanarCommandOutputs:
        desired_planar_command, squeeze_cmd = self._ensure_2d(desired_planar_command, 2, "desired_planar_command")
        ball_joint_rate_targets, squeeze_qdot = self._ensure_2d(ball_joint_rate_targets, 6, "ball_joint_rate_targets")
        wheel_normal_contact_force, squeeze_force = self._ensure_2d(
            wheel_normal_contact_force,
            6,
            "wheel_normal_contact_force",
        )
        (desired_planar_command, ball_joint_rate_targets, wheel_normal_contact_force), _ = self._broadcast_batch(
            desired_planar_command,
            ball_joint_rate_targets,
            wheel_normal_contact_force,
        )
        limits = self._ensure_vector(planar_command_limits, 2, "planar_command_limits").reshape(1, 2)
        if np.any(limits <= 0.0):
            raise ValueError("planar_command_limits must be strictly positive.")
        if np.asarray(wheel_state.wheel_positions).ndim == 2:
            wheel_state = WheelKinematicState(
                wheel_positions=wheel_state.wheel_positions.reshape(1, 6, 3),
                rolling_directions=wheel_state.rolling_directions.reshape(1, 6, 3),
                lateral_directions=wheel_state.lateral_directions.reshape(1, 6, 3),
                position_jacobians=wheel_state.position_jacobians.reshape(1, 6, 3, 6),
            )

        contact_weights = self.compute_contact_weights(
            wheel_normal_contact_force,
            contact_force_off_threshold,
            contact_force_on_threshold,
        )
        if np.asarray(contact_weights).ndim == 1:
            contact_weights = contact_weights.reshape(1, 6)

        cross_terms = self._cross_ez(wheel_state.wheel_positions.reshape(-1, 3)).reshape(desired_planar_command.shape[0], 6, 3)
        lateral_directions = wheel_state.lateral_directions
        a_vectors = np.stack(
            (
                np.einsum("bwi,i->bw", lateral_directions, self._e_x),
                np.einsum("bwi,bwi->bw", lateral_directions, cross_terms),
            ),
            axis=-1,
        )
        posture_velocity = np.einsum("bwij,bj->bwi", wheel_state.position_jacobians, ball_joint_rate_targets)
        b_scalars = np.einsum("bwi,bwi->bw", lateral_directions, posture_velocity)

        identity = np.repeat(np.eye(2, dtype=np.float64)[None, :, :], desired_planar_command.shape[0], axis=0)
        outer_terms = np.einsum("bwi,bwj->bwij", a_vectors, a_vectors)
        hessian = lambda_tracking * identity + lambda_lateral * np.sum(
            contact_weights[:, :, None, None] * outer_terms,
            axis=1,
        )
        rhs = lambda_tracking * desired_planar_command - lambda_lateral * np.sum(
            contact_weights[:, :, None] * a_vectors * b_scalars[:, :, None],
            axis=1,
        )
        shaped_planar_command = np.linalg.solve(hessian, rhs[..., None]).squeeze(-1)
        shaped_planar_command = self._sat(shaped_planar_command, -limits, limits)
        lateral_velocity_nominal = np.einsum("bwi,bi->bw", a_vectors, shaped_planar_command) + b_scalars
        lateral_cost = np.sum(contact_weights * np.square(lateral_velocity_nominal), axis=1)

        squeeze_output = squeeze_cmd and squeeze_qdot and squeeze_force
        return ShapedPlanarCommandOutputs(
            desired_planar_command=self._squeeze_if_needed(desired_planar_command, squeeze_output),
            shaped_planar_command=self._squeeze_if_needed(shaped_planar_command, squeeze_output),
            contact_weights=self._squeeze_if_needed(contact_weights, squeeze_output),
            lateral_velocity_nominal=self._squeeze_if_needed(lateral_velocity_nominal, squeeze_output),
            lateral_cost=self._squeeze_if_needed(lateral_cost, squeeze_output),
        )

    def compute_wheel_speed_references(
        self,
        wheel_state: WheelKinematicState,
        shaped_planar_command,
        ball_joint_rate_targets,
    ) -> WheelReferenceOutputs:
        shaped_planar_command, squeeze_cmd = self._ensure_2d(shaped_planar_command, 2, "shaped_planar_command")
        ball_joint_rate_targets, squeeze_qdot = self._ensure_2d(ball_joint_rate_targets, 6, "ball_joint_rate_targets")
        (shaped_planar_command, ball_joint_rate_targets), _ = self._broadcast_batch(
            shaped_planar_command,
            ball_joint_rate_targets,
        )
        if np.asarray(wheel_state.wheel_positions).ndim == 2:
            wheel_state = WheelKinematicState(
                wheel_positions=wheel_state.wheel_positions.reshape(1, 6, 3),
                rolling_directions=wheel_state.rolling_directions.reshape(1, 6, 3),
                lateral_directions=wheel_state.lateral_directions.reshape(1, 6, 3),
                position_jacobians=wheel_state.position_jacobians.reshape(1, 6, 3, 6),
            )
        wheel_center_velocity_nominal = self._compute_nominal_wheel_center_velocity(
            wheel_state,
            shaped_planar_command,
            ball_joint_rate_targets,
        )
        rolling_speed_reference = np.einsum("bwi,bwi->bw", wheel_state.rolling_directions, wheel_center_velocity_nominal)
        wheel_speed_reference = rolling_speed_reference / self.geometry.r_wheel
        wheel_speed_jacobian = self.compute_wheel_speed_jacobian(np.zeros((shaped_planar_command.shape[0], 6)))
        posture_rate_jacobian = self.compute_posture_rate_jacobian(np.zeros((shaped_planar_command.shape[0], 6)))
        squeeze_output = squeeze_cmd and squeeze_qdot
        return WheelReferenceOutputs(
            wheel_center_velocity_nominal=self._squeeze_if_needed(wheel_center_velocity_nominal, squeeze_output),
            rolling_speed_reference=self._squeeze_if_needed(rolling_speed_reference, squeeze_output),
            wheel_speed_reference=self._squeeze_if_needed(wheel_speed_reference, squeeze_output),
            wheel_speed_jacobian=None,
            posture_rate_jacobian=None,
        )

    def compute_longitudinal_slip(
        self,
        rolling_speed_actual,
        wheel_joint_vel,
        slip_velocity_epsilon: float,
    ) -> np.ndarray:
        rolling_speed_actual, squeeze_speed = self._ensure_2d(rolling_speed_actual, 6, "rolling_speed_actual")
        wheel_joint_vel, squeeze_joint_vel = self._ensure_2d(wheel_joint_vel, 6, "wheel_joint_vel")
        (rolling_speed_actual, wheel_joint_vel), _ = self._broadcast_batch(rolling_speed_actual, wheel_joint_vel)
        safe_speed = np.maximum(np.abs(rolling_speed_actual), slip_velocity_epsilon)
        longitudinal_slip = (rolling_speed_actual - self.geometry.r_wheel * wheel_joint_vel) / safe_speed
        return self._squeeze_if_needed(longitudinal_slip, squeeze_speed and squeeze_joint_vel)

    def compute_wheel_traction_targets(
        self,
        wheel_speed_reference,
        wheel_joint_vel,
        rolling_speed_actual,
        contact_weights,
        torque_tracking_gain: float,
        slip_feedback_gain: float,
        wheel_torque_limit: float,
        slip_velocity_epsilon: float,
    ) -> WheelTractionOutputs:
        wheel_speed_reference, squeeze_ref = self._ensure_2d(wheel_speed_reference, 6, "wheel_speed_reference")
        wheel_joint_vel, squeeze_joint_vel = self._ensure_2d(wheel_joint_vel, 6, "wheel_joint_vel")
        rolling_speed_actual, squeeze_speed = self._ensure_2d(rolling_speed_actual, 6, "rolling_speed_actual")
        contact_weights, squeeze_weights = self._ensure_2d(contact_weights, 6, "contact_weights")
        (wheel_speed_reference, wheel_joint_vel, rolling_speed_actual, contact_weights), _ = self._broadcast_batch(
            wheel_speed_reference,
            wheel_joint_vel,
            rolling_speed_actual,
            contact_weights,
        )
        longitudinal_slip = self.compute_longitudinal_slip(
            rolling_speed_actual,
            wheel_joint_vel,
            slip_velocity_epsilon,
        )
        if np.asarray(longitudinal_slip).ndim == 1:
            longitudinal_slip = longitudinal_slip.reshape(1, 6)
        wheel_torque_targets = contact_weights * (
            torque_tracking_gain * (wheel_speed_reference - wheel_joint_vel)
            - slip_feedback_gain * longitudinal_slip
        )
        wheel_torque_targets = self._sat(wheel_torque_targets, -wheel_torque_limit, wheel_torque_limit)
        squeeze_output = squeeze_ref and squeeze_joint_vel and squeeze_speed and squeeze_weights
        return WheelTractionOutputs(
            longitudinal_slip=self._squeeze_if_needed(longitudinal_slip, squeeze_output),
            wheel_torque_targets=self._squeeze_if_needed(wheel_torque_targets, squeeze_output),
        )

    def compute_low_slip_control_targets(
        self,
        ball_joint_pos,
        desired_ball_joint_pos,
        desired_planar_command,
        wheel_normal_contact_force,
        wheel_joint_vel,
        rolling_speed_actual,
        control_dt: float,
        planner_gains,
        planner_qdot_limits,
        q_lower_limits,
        q_upper_limits,
        lambda_tracking: float,
        lambda_lateral: float,
        planar_command_limits,
        contact_force_off_threshold: float,
        contact_force_on_threshold: float,
        torque_tracking_gain: float,
        slip_feedback_gain: float,
        wheel_torque_limit: float,
        slip_velocity_epsilon: float,
    ) -> LowSlipControlOutputs:
        ball_joint_pos, squeeze_pos = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        desired_ball_joint_pos, squeeze_desired = self._ensure_2d(desired_ball_joint_pos, 6, "desired_ball_joint_pos")
        desired_planar_command, squeeze_cmd = self._ensure_2d(desired_planar_command, 2, "desired_planar_command")
        wheel_normal_contact_force, squeeze_force = self._ensure_2d(
            wheel_normal_contact_force,
            6,
            "wheel_normal_contact_force",
        )
        wheel_joint_vel, squeeze_joint_vel = self._ensure_2d(wheel_joint_vel, 6, "wheel_joint_vel")
        rolling_speed_actual, squeeze_speed = self._ensure_2d(rolling_speed_actual, 6, "rolling_speed_actual")
        (
            ball_joint_pos,
            desired_ball_joint_pos,
            desired_planar_command,
            wheel_normal_contact_force,
            wheel_joint_vel,
            rolling_speed_actual,
        ), _ = self._broadcast_batch(
            ball_joint_pos,
            desired_ball_joint_pos,
            desired_planar_command,
            wheel_normal_contact_force,
            wheel_joint_vel,
            rolling_speed_actual,
        )

        planner_outputs = self.compute_ball_joint_planner_outputs(
            ball_joint_pos,
            desired_ball_joint_pos,
            control_dt,
            planner_gains,
            planner_qdot_limits,
            q_lower_limits,
            q_upper_limits,
        )
        q_cmd = planner_outputs.ball_joint_position_targets
        qdot_cmd = planner_outputs.ball_joint_rate_targets
        if np.asarray(q_cmd).ndim == 1:
            q_cmd = q_cmd.reshape(1, 6)
            qdot_cmd = qdot_cmd.reshape(1, 6)

        wheel_state = self.compute_wheel_kinematic_state(ball_joint_pos)
        if np.asarray(wheel_state.wheel_positions).ndim == 2:
            wheel_state = WheelKinematicState(
                wheel_positions=wheel_state.wheel_positions.reshape(1, 6, 3),
                rolling_directions=wheel_state.rolling_directions.reshape(1, 6, 3),
                lateral_directions=wheel_state.lateral_directions.reshape(1, 6, 3),
                position_jacobians=wheel_state.position_jacobians.reshape(1, 6, 3, 6),
            )

        shaped_outputs = self.shape_planar_command_for_low_slip(
            wheel_state=wheel_state,
            desired_planar_command=desired_planar_command,
            ball_joint_rate_targets=qdot_cmd,
            wheel_normal_contact_force=wheel_normal_contact_force,
            lambda_tracking=lambda_tracking,
            lambda_lateral=lambda_lateral,
            planar_command_limits=planar_command_limits,
            contact_force_off_threshold=contact_force_off_threshold,
            contact_force_on_threshold=contact_force_on_threshold,
        )
        shaped_planar_command = shaped_outputs.shaped_planar_command
        contact_weights = shaped_outputs.contact_weights
        if np.asarray(shaped_planar_command).ndim == 1:
            shaped_planar_command = shaped_planar_command.reshape(1, 2)
            contact_weights = contact_weights.reshape(1, 6)

        reference_outputs = self.compute_wheel_speed_references(
            wheel_state=wheel_state,
            shaped_planar_command=shaped_planar_command,
            ball_joint_rate_targets=qdot_cmd,
        )
        wheel_speed_reference = reference_outputs.wheel_speed_reference
        if np.asarray(wheel_speed_reference).ndim == 1:
            wheel_speed_reference = wheel_speed_reference.reshape(1, 6)

        traction_outputs = self.compute_wheel_traction_targets(
            wheel_speed_reference=wheel_speed_reference,
            wheel_joint_vel=wheel_joint_vel,
            rolling_speed_actual=rolling_speed_actual,
            contact_weights=contact_weights,
            torque_tracking_gain=torque_tracking_gain,
            slip_feedback_gain=slip_feedback_gain,
            wheel_torque_limit=wheel_torque_limit,
            slip_velocity_epsilon=slip_velocity_epsilon,
        )

        squeeze_output = (
            squeeze_pos
            and squeeze_desired
            and squeeze_cmd
            and squeeze_force
            and squeeze_joint_vel
            and squeeze_speed
        )
        wheel_speed_jacobian = self.compute_wheel_speed_jacobian(ball_joint_pos)
        posture_rate_jacobian = self.compute_posture_rate_jacobian(ball_joint_pos)
        return LowSlipControlOutputs(
            ball_joint_position_targets=self._squeeze_if_needed(q_cmd, squeeze_output),
            ball_joint_rate_targets=self._squeeze_if_needed(qdot_cmd, squeeze_output),
            desired_planar_command=self._squeeze_if_needed(desired_planar_command, squeeze_output),
            shaped_planar_command=self._squeeze_if_needed(shaped_planar_command, squeeze_output),
            contact_weights=self._squeeze_if_needed(contact_weights, squeeze_output),
            wheel_center_velocity_nominal=self._squeeze_if_needed(reference_outputs.wheel_center_velocity_nominal, squeeze_output),
            rolling_speed_reference=self._squeeze_if_needed(reference_outputs.rolling_speed_reference, squeeze_output),
            wheel_speed_reference=self._squeeze_if_needed(wheel_speed_reference, squeeze_output),
            wheel_torque_targets=self._squeeze_if_needed(traction_outputs.wheel_torque_targets, squeeze_output),
            lateral_velocity_nominal=self._squeeze_if_needed(shaped_outputs.lateral_velocity_nominal, squeeze_output),
            lateral_cost=self._squeeze_if_needed(shaped_outputs.lateral_cost, squeeze_output),
            longitudinal_slip=self._squeeze_if_needed(traction_outputs.longitudinal_slip, squeeze_output),
            wheel_speed_jacobian=self._squeeze_if_needed(wheel_speed_jacobian, squeeze_output),
            posture_rate_jacobian=self._squeeze_if_needed(posture_rate_jacobian, squeeze_output),
        )


class TorchWheelSpeedAllocator:
    """Torch implementation for Isaac Lab integration."""

    def __init__(
        self,
        geometry: CompleteCarWheelAllocatorGeometry | None = None,
        *,
        device: "torch.device | str | None" = None,
        dtype: "torch.dtype | None" = None,
    ):
        try:
            import torch
        except ModuleNotFoundError as exc:
            raise ImportError("TorchWheelSpeedAllocator requires torch to be installed.") from exc

        self.torch = torch
        self.geometry = geometry or DEFAULT_COMPLETE_CAR_GEOMETRY
        self.device = torch.device(device) if device is not None else torch.device("cpu")
        self.dtype = dtype if dtype is not None else torch.float32

        self._local_vectors = {
            name: torch.tensor(vector, device=self.device, dtype=self.dtype)
            for name, vector in _build_local_wheel_vectors(self.geometry).items()
        }
        self._a_front = torch.tensor((self.geometry.a_x, 0.0, 0.0), device=self.device, dtype=self.dtype)
        self._a_rear = torch.tensor((-self.geometry.a_x, 0.0, 0.0), device=self.device, dtype=self.dtype)
        self._e_x = torch.tensor((1.0, 0.0, 0.0), device=self.device, dtype=self.dtype)
        self._e_y = torch.tensor((0.0, 1.0, 0.0), device=self.device, dtype=self.dtype)

    def _ensure_2d(self, values, expected_last_dim: int, name: str):
        torch = self.torch
        tensor = values if torch.is_tensor(values) else torch.as_tensor(values, device=self.device, dtype=self.dtype)
        tensor = tensor.to(device=self.device, dtype=self.dtype)
        if tensor.ndim == 1:
            if tensor.shape[0] != expected_last_dim:
                raise ValueError(f"{name} must have shape ({expected_last_dim},), got {tuple(tensor.shape)}.")
            return tensor.reshape(1, expected_last_dim), True
        if tensor.ndim != 2 or tensor.shape[1] != expected_last_dim:
            raise ValueError(f"{name} must have shape (N, {expected_last_dim}), got {tuple(tensor.shape)}.")
        return tensor, False

    def _ensure_vector(self, values, expected_dim: int, name: str):
        torch = self.torch
        tensor = values if torch.is_tensor(values) else torch.as_tensor(values, device=self.device, dtype=self.dtype)
        tensor = tensor.to(device=self.device, dtype=self.dtype)
        if tensor.ndim == 0:
            return tensor.expand(expected_dim)
        if tensor.ndim == 1 and tensor.shape[0] == expected_dim:
            return tensor
        raise ValueError(f"{name} must be a scalar or a vector with shape ({expected_dim},), got {tuple(tensor.shape)}.")

    @staticmethod
    def _squeeze_if_needed(values, squeeze_output: bool):
        return values[0] if squeeze_output else values

    def _broadcast_batch(self, *tensors):
        batch_size = max(tensor.shape[0] for tensor in tensors)
        broadcasted = []
        for tensor in tensors:
            if tensor.shape[0] == batch_size:
                broadcasted.append(tensor)
            elif tensor.shape[0] == 1:
                broadcasted.append(tensor.expand(batch_size, tensor.shape[1]))
            else:
                raise ValueError("Inputs have incompatible batch dimensions.")
        return broadcasted, batch_size

    def _apply_rotation(self, rotation, vector):
        return self.torch.einsum("bij,j->bi", rotation, vector)

    def _cross_ez(self, position):
        torch = self.torch
        zeros = torch.zeros_like(position[:, 0])
        return torch.stack((-position[:, 1], position[:, 0], zeros), dim=-1)

    def _sat(self, values, lower, upper):
        torch = self.torch
        lower = torch.as_tensor(lower, device=values.device, dtype=values.dtype)
        upper = torch.as_tensor(upper, device=values.device, dtype=values.dtype)
        return torch.minimum(torch.maximum(values, lower), upper)

    def _build_rotation_and_derivatives(self, module_angles):
        torch = self.torch
        psi = module_angles[:, 0]
        theta = module_angles[:, 1]
        phi = module_angles[:, 2]

        c_psi = torch.cos(psi)
        s_psi = torch.sin(psi)
        c_theta = torch.cos(theta)
        s_theta = torch.sin(theta)
        c_phi = torch.cos(phi)
        s_phi = torch.sin(phi)

        rotation = torch.stack(
            (
                torch.stack(
                    (
                        c_psi * c_theta,
                        c_psi * s_theta * s_phi - s_psi * c_phi,
                        c_psi * s_theta * c_phi + s_psi * s_phi,
                    ),
                    dim=-1,
                ),
                torch.stack(
                    (
                        s_psi * c_theta,
                        s_psi * s_theta * s_phi + c_psi * c_phi,
                        s_psi * s_theta * c_phi - c_psi * s_phi,
                    ),
                    dim=-1,
                ),
                torch.stack((-s_theta, c_theta * s_phi, c_theta * c_phi), dim=-1),
            ),
            dim=1,
        )
        d_rotation_d_psi = torch.stack(
            (
                torch.stack(
                    (
                        -s_psi * c_theta,
                        -s_psi * s_theta * s_phi - c_psi * c_phi,
                        -s_psi * s_theta * c_phi + c_psi * s_phi,
                    ),
                    dim=-1,
                ),
                torch.stack(
                    (
                        c_psi * c_theta,
                        c_psi * s_theta * s_phi - s_psi * c_phi,
                        c_psi * s_theta * c_phi + s_psi * s_phi,
                    ),
                    dim=-1,
                ),
                torch.stack((torch.zeros_like(psi), torch.zeros_like(psi), torch.zeros_like(psi)), dim=-1),
            ),
            dim=1,
        )
        d_rotation_d_theta = torch.stack(
            (
                torch.stack((-c_psi * s_theta, c_psi * c_theta * s_phi, c_psi * c_theta * c_phi), dim=-1),
                torch.stack((-s_psi * s_theta, s_psi * c_theta * s_phi, s_psi * c_theta * c_phi), dim=-1),
                torch.stack((-c_theta, -s_theta * s_phi, -s_theta * c_phi), dim=-1),
            ),
            dim=1,
        )
        d_rotation_d_phi = torch.stack(
            (
                torch.stack(
                    (
                        torch.zeros_like(phi),
                        c_psi * s_theta * c_phi + s_psi * s_phi,
                        -c_psi * s_theta * s_phi + s_psi * c_phi,
                    ),
                    dim=-1,
                ),
                torch.stack(
                    (
                        torch.zeros_like(phi),
                        s_psi * s_theta * c_phi - c_psi * s_phi,
                        -s_psi * s_theta * s_phi - c_psi * c_phi,
                    ),
                    dim=-1,
                ),
                torch.stack((torch.zeros_like(phi), c_theta * c_phi, -c_theta * s_phi), dim=-1),
            ),
            dim=1,
        )
        return rotation, d_rotation_d_psi, d_rotation_d_theta, d_rotation_d_phi

    # 球铰姿态规划器
    def compute_ball_joint_planner_outputs(
        self,
        ball_joint_pos,
        desired_ball_joint_pos,
        control_dt: float,
        planner_gains,
        planner_qdot_limits,
        q_lower_limits,
        q_upper_limits,
    ) -> BallJointPlannerOutputs:
        ball_joint_pos, squeeze_pos = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        desired_ball_joint_pos, squeeze_desired = self._ensure_2d(desired_ball_joint_pos, 6, "desired_ball_joint_pos")
        (ball_joint_pos, desired_ball_joint_pos), _ = self._broadcast_batch(ball_joint_pos, desired_ball_joint_pos)

        gains = self._ensure_vector(planner_gains, 6, "planner_gains").reshape(1, 6)
        qdot_limits = self._ensure_vector(planner_qdot_limits, 6, "planner_qdot_limits").reshape(1, 6)
        q_lower = self._ensure_vector(q_lower_limits, 6, "q_lower_limits").reshape(1, 6)
        q_upper = self._ensure_vector(q_upper_limits, 6, "q_upper_limits").reshape(1, 6)

        qdot_cmd_raw = gains * (desired_ball_joint_pos - ball_joint_pos)
        qdot_cmd = self._sat(qdot_cmd_raw, -qdot_limits, qdot_limits)
        q_cmd = self._sat(ball_joint_pos + float(control_dt) * qdot_cmd, q_lower, q_upper)

        squeeze_output = squeeze_pos and squeeze_desired
        return BallJointPlannerOutputs(
            ball_joint_position_targets=self._squeeze_if_needed(q_cmd, squeeze_output),
            ball_joint_rate_targets=self._squeeze_if_needed(qdot_cmd, squeeze_output),
        )

    def _compute_front_rear_wheel_kinematics(self, ball_joint_pos):
        torch = self.torch
        front_angles = ball_joint_pos[:, :3]
        rear_angles = ball_joint_pos[:, 3:]

        r_front, dr_front_d_psi, dr_front_d_theta, dr_front_d_phi = self._build_rotation_and_derivatives(front_angles)
        r_rear, dr_rear_d_psi, dr_rear_d_theta, dr_rear_d_phi = self._build_rotation_and_derivatives(rear_angles)

        t_front = self._apply_rotation(r_front, self._e_x)
        t_rear = self._apply_rotation(r_rear, self._e_x)
        n_front = self._apply_rotation(r_front, self._e_y)
        n_rear = self._apply_rotation(r_rear, self._e_y)

        front_left_pos = self._a_front + self._apply_rotation(r_front, self._local_vectors["front_left"])
        front_right_pos = self._a_front + self._apply_rotation(r_front, self._local_vectors["front_right"])
        rear_left_pos = self._a_rear + self._apply_rotation(r_rear, self._local_vectors["rear_left"])
        rear_right_pos = self._a_rear + self._apply_rotation(r_rear, self._local_vectors["rear_right"])

        zeros = torch.zeros_like(front_left_pos)

        def front_position_jacobian(local_vector):
            return torch.stack(
                (
                    self._apply_rotation(dr_front_d_psi, local_vector),
                    self._apply_rotation(dr_front_d_theta, local_vector),
                    self._apply_rotation(dr_front_d_phi, local_vector),
                    zeros,
                    zeros,
                    zeros,
                ),
                dim=-1,
            )

        def rear_position_jacobian(local_vector):
            return torch.stack(
                (
                    zeros,
                    zeros,
                    zeros,
                    self._apply_rotation(dr_rear_d_psi, local_vector),
                    self._apply_rotation(dr_rear_d_theta, local_vector),
                    self._apply_rotation(dr_rear_d_phi, local_vector),
                ),
                dim=-1,
            )

        return {
            "front_left_pos": front_left_pos,
            "front_right_pos": front_right_pos,
            "rear_left_pos": rear_left_pos,
            "rear_right_pos": rear_right_pos,
            "front_t": t_front,
            "rear_t": t_rear,
            "front_n": n_front,
            "rear_n": n_rear,
            "front_left_g": front_position_jacobian(self._local_vectors["front_left"]),
            "front_right_g": front_position_jacobian(self._local_vectors["front_right"]),
            "rear_left_g": rear_position_jacobian(self._local_vectors["rear_left"]),
            "rear_right_g": rear_position_jacobian(self._local_vectors["rear_right"]),
        }

    # 轮心位置，滚动方向，侧向方向，位置雅克比
    def compute_wheel_kinematic_state(self, ball_joint_pos) -> WheelKinematicState:
        torch = self.torch
        ball_joint_pos, squeeze_output = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        kinematics = self._compute_front_rear_wheel_kinematics(ball_joint_pos)

        batch_size = ball_joint_pos.shape[0]
        middle_left_pos = self._local_vectors["middle_left"].reshape(1, 3).expand(batch_size, 3)
        middle_right_pos = self._local_vectors["middle_right"].reshape(1, 3).expand(batch_size, 3)
        middle_t = self._e_x.reshape(1, 3).expand(batch_size, 3)
        middle_n = self._e_y.reshape(1, 3).expand(batch_size, 3)
        middle_g = torch.zeros((batch_size, 3, 6), device=self.device, dtype=self.dtype)

        wheel_positions = torch.stack(
            (
                middle_left_pos,
                middle_right_pos,
                kinematics["front_left_pos"],
                kinematics["front_right_pos"],
                kinematics["rear_left_pos"],
                kinematics["rear_right_pos"],
            ),
            dim=1,
        )
        rolling_directions = torch.stack(
            (
                middle_t,
                middle_t,
                kinematics["front_t"],
                kinematics["front_t"],
                kinematics["rear_t"],
                kinematics["rear_t"],
            ),
            dim=1,
        )
        lateral_directions = torch.stack(
            (
                middle_n,
                middle_n,
                kinematics["front_n"],
                kinematics["front_n"],
                kinematics["rear_n"],
                kinematics["rear_n"],
            ),
            dim=1,
        )
        position_jacobians = torch.stack(
            (
                middle_g,
                middle_g,
                kinematics["front_left_g"],
                kinematics["front_right_g"],
                kinematics["rear_left_g"],
                kinematics["rear_right_g"],
            ),
            dim=1,
        )
        return WheelKinematicState(
            wheel_positions=self._squeeze_if_needed(wheel_positions, squeeze_output),
            rolling_directions=self._squeeze_if_needed(rolling_directions, squeeze_output),
            lateral_directions=self._squeeze_if_needed(lateral_directions, squeeze_output),
            position_jacobians=self._squeeze_if_needed(position_jacobians, squeeze_output),
        )

    # 速度雅克比矩阵
    def compute_wheel_speed_jacobian(self, ball_joint_pos):
        ball_joint_pos, squeeze_output = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        wheel_state = self.compute_wheel_kinematic_state(ball_joint_pos)
        if wheel_state.wheel_positions.ndim == 2:
            wheel_state = WheelKinematicState(
                wheel_positions=wheel_state.wheel_positions.reshape(1, 6, 3),
                rolling_directions=wheel_state.rolling_directions.reshape(1, 6, 3),
                lateral_directions=wheel_state.lateral_directions.reshape(1, 6, 3),
                position_jacobians=wheel_state.position_jacobians.reshape(1, 6, 3, 6),
            )
        batch_size = ball_joint_pos.shape[0]
        e_x = self._e_x.reshape(1, 1, 3).expand(batch_size, 6, 3)
        cross_terms = self._cross_ez(wheel_state.wheel_positions.reshape(-1, 3)).reshape(batch_size, 6, 3)
        jacobian = (1.0 / self.geometry.r_wheel) * self.torch.stack(
            (
                self.torch.einsum("bwi,bwi->bw", wheel_state.rolling_directions, e_x),
                self.torch.einsum("bwi,bwi->bw", wheel_state.rolling_directions, cross_terms),
            ),
            dim=-1,
        )
        return self._squeeze_if_needed(jacobian, squeeze_output)
    #位置姿态雅克比矩阵
    def compute_posture_rate_jacobian(self, ball_joint_pos):
        ball_joint_pos, squeeze_output = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        wheel_state = self.compute_wheel_kinematic_state(ball_joint_pos)
        if wheel_state.position_jacobians.ndim == 3:
            wheel_state = WheelKinematicState(
                wheel_positions=wheel_state.wheel_positions.reshape(1, 6, 3),
                rolling_directions=wheel_state.rolling_directions.reshape(1, 6, 3),
                lateral_directions=wheel_state.lateral_directions.reshape(1, 6, 3),
                position_jacobians=wheel_state.position_jacobians.reshape(1, 6, 3, 6),
            )
        jacobian = (1.0 / self.geometry.r_wheel) * self.torch.einsum(
            "bwi,bwij->bwj",
            wheel_state.rolling_directions,
            wheel_state.position_jacobians,
        )
        return self._squeeze_if_needed(jacobian, squeeze_output)
    # 接触权重
    def compute_contact_weights(
        self,
        wheel_normal_contact_force,
        contact_force_off_threshold: float,
        contact_force_on_threshold: float,
    ):
        wheel_normal_contact_force, squeeze_output = self._ensure_2d(
            wheel_normal_contact_force,
            6,
            "wheel_normal_contact_force",
        )
        if contact_force_on_threshold <= contact_force_off_threshold:
            raise ValueError("contact_force_on_threshold must be greater than contact_force_off_threshold.")
        weights = (wheel_normal_contact_force - contact_force_off_threshold) / (
            contact_force_on_threshold - contact_force_off_threshold
        )
        weights = self._sat(weights, 0.0, 1.0)
        return self._squeeze_if_needed(weights, squeeze_output)

    def _compute_nominal_wheel_center_velocity(
        self,
        wheel_state: WheelKinematicState,
        planar_command,
        ball_joint_rate_targets,
    ):
        batch_size = planar_command.shape[0]
        cross_terms = self._cross_ez(wheel_state.wheel_positions.reshape(-1, 3)).reshape(batch_size, 6, 3)
        translational = planar_command[:, 0].reshape(batch_size, 1, 1) * self._e_x.reshape(1, 1, 3)
        rotational = planar_command[:, 1].reshape(batch_size, 1, 1) * cross_terms
        posture = self.torch.einsum("bwij,bj->bwi", wheel_state.position_jacobians, ball_joint_rate_targets)
        return translational + rotational + posture
    # 低滑移整形
    def shape_planar_command_for_low_slip(
        self,
        wheel_state: WheelKinematicState,
        desired_planar_command,
        ball_joint_rate_targets,
        wheel_normal_contact_force,
        lambda_tracking: float,
        lambda_lateral: float,
        planar_command_limits,
        contact_force_off_threshold: float,
        contact_force_on_threshold: float,
    ) -> ShapedPlanarCommandOutputs:
        torch = self.torch
        desired_planar_command, squeeze_cmd = self._ensure_2d(desired_planar_command, 2, "desired_planar_command")
        ball_joint_rate_targets, squeeze_qdot = self._ensure_2d(ball_joint_rate_targets, 6, "ball_joint_rate_targets")
        wheel_normal_contact_force, squeeze_force = self._ensure_2d(
            wheel_normal_contact_force,
            6,
            "wheel_normal_contact_force",
        )
        (desired_planar_command, ball_joint_rate_targets, wheel_normal_contact_force), _ = self._broadcast_batch(
            desired_planar_command,
            ball_joint_rate_targets,
            wheel_normal_contact_force,
        )
        limits = self._ensure_vector(planar_command_limits, 2, "planar_command_limits").reshape(1, 2)
        if torch.any(limits <= 0.0):
            raise ValueError("planar_command_limits must be strictly positive.")
        if wheel_state.wheel_positions.ndim == 2:
            wheel_state = WheelKinematicState(
                wheel_positions=wheel_state.wheel_positions.reshape(1, 6, 3),
                rolling_directions=wheel_state.rolling_directions.reshape(1, 6, 3),
                lateral_directions=wheel_state.lateral_directions.reshape(1, 6, 3),
                position_jacobians=wheel_state.position_jacobians.reshape(1, 6, 3, 6),
            )

        contact_weights = self.compute_contact_weights(
            wheel_normal_contact_force,
            contact_force_off_threshold,
            contact_force_on_threshold,
        )
        if contact_weights.ndim == 1:
            contact_weights = contact_weights.reshape(1, 6)

        batch_size = desired_planar_command.shape[0]
        cross_terms = self._cross_ez(wheel_state.wheel_positions.reshape(-1, 3)).reshape(batch_size, 6, 3)
        lateral_directions = wheel_state.lateral_directions
        a_vectors = torch.stack(
            (
                torch.einsum("bwi,i->bw", lateral_directions, self._e_x),
                torch.einsum("bwi,bwi->bw", lateral_directions, cross_terms),
            ),
            dim=-1,
        )
        posture_velocity = torch.einsum("bwij,bj->bwi", wheel_state.position_jacobians, ball_joint_rate_targets)
        b_scalars = torch.einsum("bwi,bwi->bw", lateral_directions, posture_velocity)

        identity = torch.eye(2, device=self.device, dtype=self.dtype).unsqueeze(0).expand(batch_size, 2, 2)
        outer_terms = torch.einsum("bwi,bwj->bwij", a_vectors, a_vectors)
        hessian = lambda_tracking * identity + lambda_lateral * torch.sum(
            contact_weights[:, :, None, None] * outer_terms,
            dim=1,
        )
        rhs = lambda_tracking * desired_planar_command - lambda_lateral * torch.sum(
            contact_weights[:, :, None] * a_vectors * b_scalars[:, :, None],
            dim=1,
        )
        shaped_planar_command = torch.linalg.solve(hessian, rhs.unsqueeze(-1)).squeeze(-1)
        shaped_planar_command = self._sat(shaped_planar_command, -limits, limits)
        lateral_velocity_nominal = torch.einsum("bwi,bi->bw", a_vectors, shaped_planar_command) + b_scalars
        lateral_cost = torch.sum(contact_weights * torch.square(lateral_velocity_nominal), dim=1)

        squeeze_output = squeeze_cmd and squeeze_qdot and squeeze_force
        return ShapedPlanarCommandOutputs(
            desired_planar_command=self._squeeze_if_needed(desired_planar_command, squeeze_output),
            shaped_planar_command=self._squeeze_if_needed(shaped_planar_command, squeeze_output),
            contact_weights=self._squeeze_if_needed(contact_weights, squeeze_output),
            lateral_velocity_nominal=self._squeeze_if_needed(lateral_velocity_nominal, squeeze_output),
            lateral_cost=self._squeeze_if_needed(lateral_cost, squeeze_output),
        )
    # 名义速度参考
    def compute_wheel_speed_references(
        self,
        wheel_state: WheelKinematicState,
        shaped_planar_command,
        ball_joint_rate_targets,
    ) -> WheelReferenceOutputs:
        shaped_planar_command, squeeze_cmd = self._ensure_2d(shaped_planar_command, 2, "shaped_planar_command")
        ball_joint_rate_targets, squeeze_qdot = self._ensure_2d(ball_joint_rate_targets, 6, "ball_joint_rate_targets")
        (shaped_planar_command, ball_joint_rate_targets), _ = self._broadcast_batch(
            shaped_planar_command,
            ball_joint_rate_targets,
        )
        if wheel_state.wheel_positions.ndim == 2:
            wheel_state = WheelKinematicState(
                wheel_positions=wheel_state.wheel_positions.reshape(1, 6, 3),
                rolling_directions=wheel_state.rolling_directions.reshape(1, 6, 3),
                lateral_directions=wheel_state.lateral_directions.reshape(1, 6, 3),
                position_jacobians=wheel_state.position_jacobians.reshape(1, 6, 3, 6),
            )
        wheel_center_velocity_nominal = self._compute_nominal_wheel_center_velocity(
            wheel_state,
            shaped_planar_command,
            ball_joint_rate_targets,
        )
        rolling_speed_reference = self.torch.einsum(
            "bwi,bwi->bw",
            wheel_state.rolling_directions,
            wheel_center_velocity_nominal,
        )
        wheel_speed_reference = rolling_speed_reference / self.geometry.r_wheel
        squeeze_output = squeeze_cmd and squeeze_qdot
        return WheelReferenceOutputs(
            wheel_center_velocity_nominal=self._squeeze_if_needed(wheel_center_velocity_nominal, squeeze_output),
            rolling_speed_reference=self._squeeze_if_needed(rolling_speed_reference, squeeze_output),
            wheel_speed_reference=self._squeeze_if_needed(wheel_speed_reference, squeeze_output),
            wheel_speed_jacobian=None,
            posture_rate_jacobian=None,
        )

    def compute_longitudinal_slip(
        self,
        rolling_speed_actual,
        wheel_joint_vel,
        slip_velocity_epsilon: float,
    ):
        rolling_speed_actual, squeeze_speed = self._ensure_2d(rolling_speed_actual, 6, "rolling_speed_actual")
        wheel_joint_vel, squeeze_joint_vel = self._ensure_2d(wheel_joint_vel, 6, "wheel_joint_vel")
        (rolling_speed_actual, wheel_joint_vel), _ = self._broadcast_batch(rolling_speed_actual, wheel_joint_vel)
        longitudinal_slip = compute_longitudinal_slip_torch(
            rolling_speed_actual,
            wheel_joint_vel,
            self.geometry.r_wheel,
            slip_velocity_epsilon,
        )
        return self._squeeze_if_needed(longitudinal_slip, squeeze_speed and squeeze_joint_vel)

    def compute_wheel_traction_targets(
        self,
        wheel_speed_reference,
        wheel_joint_vel,
        rolling_speed_actual,
        contact_weights,
        torque_tracking_gain: float,
        slip_feedback_gain: float,
        wheel_torque_limit: float,
        slip_velocity_epsilon: float,
    ) -> WheelTractionOutputs:
        wheel_speed_reference, squeeze_ref = self._ensure_2d(wheel_speed_reference, 6, "wheel_speed_reference")
        wheel_joint_vel, squeeze_joint_vel = self._ensure_2d(wheel_joint_vel, 6, "wheel_joint_vel")
        rolling_speed_actual, squeeze_speed = self._ensure_2d(rolling_speed_actual, 6, "rolling_speed_actual")
        contact_weights, squeeze_weights = self._ensure_2d(contact_weights, 6, "contact_weights")
        (wheel_speed_reference, wheel_joint_vel, rolling_speed_actual, contact_weights), _ = self._broadcast_batch(
            wheel_speed_reference,
            wheel_joint_vel,
            rolling_speed_actual,
            contact_weights,
        )
        longitudinal_slip = self.compute_longitudinal_slip(
            rolling_speed_actual,
            wheel_joint_vel,
            slip_velocity_epsilon,
        )
        if longitudinal_slip.ndim == 1:
            longitudinal_slip = longitudinal_slip.reshape(1, 6)
        wheel_torque_targets = contact_weights * (
            torque_tracking_gain * (wheel_speed_reference - wheel_joint_vel)
            - slip_feedback_gain * longitudinal_slip
        )
        wheel_torque_targets = self._sat(wheel_torque_targets, -wheel_torque_limit, wheel_torque_limit)
        squeeze_output = squeeze_ref and squeeze_joint_vel and squeeze_speed and squeeze_weights
        return WheelTractionOutputs(
            longitudinal_slip=self._squeeze_if_needed(longitudinal_slip, squeeze_output),
            wheel_torque_targets=self._squeeze_if_needed(wheel_torque_targets, squeeze_output),
        )

    def compute_low_slip_control_targets(
        self,
        ball_joint_pos,
        desired_ball_joint_pos,
        desired_planar_command,
        wheel_normal_contact_force,
        wheel_joint_vel,
        rolling_speed_actual,
        control_dt: float,
        planner_gains,
        planner_qdot_limits,
        q_lower_limits,
        q_upper_limits,
        lambda_tracking: float,
        lambda_lateral: float,
        planar_command_limits,
        contact_force_off_threshold: float,
        contact_force_on_threshold: float,
        torque_tracking_gain: float,
        slip_feedback_gain: float,
        wheel_torque_limit: float,
        slip_velocity_epsilon: float,
    ) -> LowSlipControlOutputs:
        ball_joint_pos, squeeze_pos = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        desired_ball_joint_pos, squeeze_desired = self._ensure_2d(desired_ball_joint_pos, 6, "desired_ball_joint_pos")
        desired_planar_command, squeeze_cmd = self._ensure_2d(desired_planar_command, 2, "desired_planar_command")
        wheel_normal_contact_force, squeeze_force = self._ensure_2d(
            wheel_normal_contact_force,
            6,
            "wheel_normal_contact_force",
        )
        wheel_joint_vel, squeeze_joint_vel = self._ensure_2d(wheel_joint_vel, 6, "wheel_joint_vel")
        rolling_speed_actual, squeeze_speed = self._ensure_2d(rolling_speed_actual, 6, "rolling_speed_actual")
        (
            ball_joint_pos,
            desired_ball_joint_pos,
            desired_planar_command,
            wheel_normal_contact_force,
            wheel_joint_vel,
            rolling_speed_actual,
        ), _ = self._broadcast_batch(
            ball_joint_pos,
            desired_ball_joint_pos,
            desired_planar_command,
            wheel_normal_contact_force,
            wheel_joint_vel,
            rolling_speed_actual,
        )

        planner_outputs = self.compute_ball_joint_planner_outputs(
            ball_joint_pos,
            desired_ball_joint_pos,
            control_dt,
            planner_gains,
            planner_qdot_limits,
            q_lower_limits,
            q_upper_limits,
        )
        q_cmd = planner_outputs.ball_joint_position_targets
        qdot_cmd = planner_outputs.ball_joint_rate_targets
        if q_cmd.ndim == 1:
            q_cmd = q_cmd.reshape(1, 6)
            qdot_cmd = qdot_cmd.reshape(1, 6)

        wheel_state = self.compute_wheel_kinematic_state(ball_joint_pos)
        if wheel_state.wheel_positions.ndim == 2:
            wheel_state = WheelKinematicState(
                wheel_positions=wheel_state.wheel_positions.reshape(1, 6, 3),
                rolling_directions=wheel_state.rolling_directions.reshape(1, 6, 3),
                lateral_directions=wheel_state.lateral_directions.reshape(1, 6, 3),
                position_jacobians=wheel_state.position_jacobians.reshape(1, 6, 3, 6),
            )

        shaped_outputs = self.shape_planar_command_for_low_slip(
            wheel_state=wheel_state,
            desired_planar_command=desired_planar_command,
            ball_joint_rate_targets=qdot_cmd,
            wheel_normal_contact_force=wheel_normal_contact_force,
            lambda_tracking=lambda_tracking,
            lambda_lateral=lambda_lateral,
            planar_command_limits=planar_command_limits,
            contact_force_off_threshold=contact_force_off_threshold,
            contact_force_on_threshold=contact_force_on_threshold,
        )
        shaped_planar_command = shaped_outputs.shaped_planar_command
        contact_weights = shaped_outputs.contact_weights
        if shaped_planar_command.ndim == 1:
            shaped_planar_command = shaped_planar_command.reshape(1, 2)
            contact_weights = contact_weights.reshape(1, 6)

        reference_outputs = self.compute_wheel_speed_references(
            wheel_state=wheel_state,
            shaped_planar_command=shaped_planar_command,
            ball_joint_rate_targets=qdot_cmd,
        )
        wheel_speed_reference = reference_outputs.wheel_speed_reference
        if wheel_speed_reference.ndim == 1:
            wheel_speed_reference = wheel_speed_reference.reshape(1, 6)

        traction_outputs = self.compute_wheel_traction_targets(
            wheel_speed_reference=wheel_speed_reference,
            wheel_joint_vel=wheel_joint_vel,
            rolling_speed_actual=rolling_speed_actual,
            contact_weights=contact_weights,
            torque_tracking_gain=torque_tracking_gain,
            slip_feedback_gain=slip_feedback_gain,
            wheel_torque_limit=wheel_torque_limit,
            slip_velocity_epsilon=slip_velocity_epsilon,
        )

        squeeze_output = (
            squeeze_pos
            and squeeze_desired
            and squeeze_cmd
            and squeeze_force
            and squeeze_joint_vel
            and squeeze_speed
        )
        wheel_speed_jacobian = self.compute_wheel_speed_jacobian(ball_joint_pos)
        posture_rate_jacobian = self.compute_posture_rate_jacobian(ball_joint_pos)
        return LowSlipControlOutputs(
            ball_joint_position_targets=self._squeeze_if_needed(q_cmd, squeeze_output),
            ball_joint_rate_targets=self._squeeze_if_needed(qdot_cmd, squeeze_output),
            desired_planar_command=self._squeeze_if_needed(desired_planar_command, squeeze_output),
            shaped_planar_command=self._squeeze_if_needed(shaped_planar_command, squeeze_output),
            contact_weights=self._squeeze_if_needed(contact_weights, squeeze_output),
            wheel_center_velocity_nominal=self._squeeze_if_needed(reference_outputs.wheel_center_velocity_nominal, squeeze_output),
            rolling_speed_reference=self._squeeze_if_needed(reference_outputs.rolling_speed_reference, squeeze_output),
            wheel_speed_reference=self._squeeze_if_needed(wheel_speed_reference, squeeze_output),
            wheel_torque_targets=self._squeeze_if_needed(traction_outputs.wheel_torque_targets, squeeze_output),
            lateral_velocity_nominal=self._squeeze_if_needed(shaped_outputs.lateral_velocity_nominal, squeeze_output),
            lateral_cost=self._squeeze_if_needed(shaped_outputs.lateral_cost, squeeze_output),
            longitudinal_slip=self._squeeze_if_needed(traction_outputs.longitudinal_slip, squeeze_output),
            wheel_speed_jacobian=self._squeeze_if_needed(wheel_speed_jacobian, squeeze_output),
            posture_rate_jacobian=self._squeeze_if_needed(posture_rate_jacobian, squeeze_output),
        )


__all__ = [
    "BALL_JOINT_NAMES",
    "BallJointPlannerOutputs",
    "CompleteCarWheelAllocatorGeometry",
    "DEFAULT_COMPLETE_CAR_GEOMETRY",
    "LowSlipControlOutputs",
    "NumpyWheelSpeedAllocator",
    "OUTPUT_WHEEL_JOINT_NAMES",
    "PAPER_WHEEL_JOINT_NAMES",
    "ShapedPlanarCommandOutputs",
    "TorchWheelSpeedAllocator",
    "WheelKinematicState",
    "WheelReferenceOutputs",
    "WheelTractionOutputs",
]
