"""Wheel-speed allocator aligned with the thesis Chapter03 direct derivation."""

from __future__ import annotations

from dataclasses import dataclass

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

PAPER_TO_OUTPUT_ROW_INDICES = (2, 3, 0, 1, 4, 5)


@dataclass(frozen=True)
class CompleteCarWheelAllocatorGeometry:
    """Scalar structure parameters used by the thesis final wheel-speed formulas."""

    a_x: float = 0.25633374
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


DEFAULT_COMPLETE_CAR_GEOMETRY = CompleteCarWheelAllocatorGeometry()


class NumpyWheelSpeedAllocator:
    """NumPy allocator for offline validation and formula checks."""

    def __init__(self, geometry: CompleteCarWheelAllocatorGeometry | None = None):
        self.geometry = geometry or DEFAULT_COMPLETE_CAR_GEOMETRY
        self._paper_to_output = np.asarray(PAPER_TO_OUTPUT_ROW_INDICES, dtype=np.int64)

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

    def compute_wheel_speed_jacobian(self, ball_joint_pos) -> np.ndarray:
        """Return J_w(q) with shape (6, 2) or (N, 6, 2) in env wheel-joint order."""

        ball_joint_pos, squeeze_output = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")

        psi_f, theta_f, phi_f = ball_joint_pos[:, 0], ball_joint_pos[:, 1], ball_joint_pos[:, 2]
        psi_r, theta_r, phi_r = ball_joint_pos[:, 3], ball_joint_pos[:, 4], ball_joint_pos[:, 5]

        c_psi_f = np.cos(psi_f)
        s_psi_f = np.sin(psi_f)
        c_theta_f = np.cos(theta_f)
        c_phi_f = np.cos(phi_f)
        s_phi_f = np.sin(phi_f)

        c_psi_r = np.cos(psi_r)
        s_psi_r = np.sin(psi_r)
        c_theta_r = np.cos(theta_r)
        c_phi_r = np.cos(phi_r)
        s_phi_r = np.sin(phi_r)

        r_inv = 1.0 / self.geometry.r_wheel

        front_vx = c_psi_f * c_theta_f * r_inv
        front_yaw_base = c_theta_f * (self.geometry.a_x * s_psi_f + self.geometry.h1 * s_phi_f) * r_inv
        front_yaw_offset = c_theta_f * (0.5 * self.geometry.d1 * c_phi_f) * r_inv

        middle_vx = np.full_like(front_vx, r_inv)
        middle_yaw_offset = np.full_like(front_vx, 0.5 * self.geometry.d2 * r_inv)

        rear_vx = c_psi_r * c_theta_r * r_inv
        rear_yaw_base = c_theta_r * (-self.geometry.a_x * s_psi_r + self.geometry.h3 * s_phi_r) * r_inv
        rear_yaw_offset = c_theta_r * (0.5 * self.geometry.d3 * c_phi_r) * r_inv

        jacobian_paper_order = np.stack(
            (
                np.stack((front_vx, front_yaw_base - front_yaw_offset), axis=-1),
                np.stack((front_vx, front_yaw_base + front_yaw_offset), axis=-1),
                np.stack((middle_vx, -middle_yaw_offset), axis=-1),
                np.stack((middle_vx, middle_yaw_offset), axis=-1),
                np.stack((rear_vx, rear_yaw_base - rear_yaw_offset), axis=-1),
                np.stack((rear_vx, rear_yaw_base + rear_yaw_offset), axis=-1),
            ),
            axis=1,
        )
        jacobian_output_order = jacobian_paper_order[:, self._paper_to_output, :]
        return self._squeeze_if_needed(jacobian_output_order, squeeze_output)

    def compute_wheel_speed_targets_from_planar_command(self, ball_joint_pos, planar_command) -> np.ndarray:
        """Map [Vx^d, wz^d] to six wheel angular-speed targets."""

        ball_joint_pos, squeeze_pos = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        planar_command, squeeze_cmd = self._ensure_2d(planar_command, 2, "planar_command")
        (ball_joint_pos, planar_command), _ = self._broadcast_batch(ball_joint_pos, planar_command)
        jacobian = self.compute_wheel_speed_jacobian(ball_joint_pos)
        wheel_targets = np.einsum("bij,bj->bi", jacobian, planar_command)
        return self._squeeze_if_needed(wheel_targets, squeeze_pos and squeeze_cmd)


class TorchWheelSpeedAllocator:
    """Torch allocator for Isaac Lab integration."""

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
        self._paper_to_output = torch.tensor(PAPER_TO_OUTPUT_ROW_INDICES, device=self.device, dtype=torch.long)

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

    def compute_wheel_speed_jacobian(self, ball_joint_pos):
        """Return J_w(q) with shape (6, 2) or (N, 6, 2) in env wheel-joint order."""

        torch = self.torch
        ball_joint_pos, squeeze_output = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")

        psi_f, theta_f, phi_f = ball_joint_pos[:, 0], ball_joint_pos[:, 1], ball_joint_pos[:, 2]
        psi_r, theta_r, phi_r = ball_joint_pos[:, 3], ball_joint_pos[:, 4], ball_joint_pos[:, 5]

        c_psi_f = torch.cos(psi_f)
        s_psi_f = torch.sin(psi_f)
        c_theta_f = torch.cos(theta_f)
        c_phi_f = torch.cos(phi_f)
        s_phi_f = torch.sin(phi_f)

        c_psi_r = torch.cos(psi_r)
        s_psi_r = torch.sin(psi_r)
        c_theta_r = torch.cos(theta_r)
        c_phi_r = torch.cos(phi_r)
        s_phi_r = torch.sin(phi_r)

        r_inv_value = 1.0 / self.geometry.r_wheel
        r_inv = torch.tensor(r_inv_value, device=self.device, dtype=self.dtype)

        front_vx = c_psi_f * c_theta_f * r_inv
        front_yaw_base = c_theta_f * (self.geometry.a_x * s_psi_f + self.geometry.h1 * s_phi_f) * r_inv
        front_yaw_offset = c_theta_f * (0.5 * self.geometry.d1 * c_phi_f) * r_inv

        middle_vx = torch.full_like(front_vx, r_inv_value)
        middle_yaw_offset = torch.full_like(front_vx, 0.5 * self.geometry.d2 * r_inv_value)

        rear_vx = c_psi_r * c_theta_r * r_inv
        rear_yaw_base = c_theta_r * (-self.geometry.a_x * s_psi_r + self.geometry.h3 * s_phi_r) * r_inv
        rear_yaw_offset = c_theta_r * (0.5 * self.geometry.d3 * c_phi_r) * r_inv

        jacobian_paper_order = torch.stack(
            (
                torch.stack((front_vx, front_yaw_base - front_yaw_offset), dim=-1),
                torch.stack((front_vx, front_yaw_base + front_yaw_offset), dim=-1),
                torch.stack((middle_vx, -middle_yaw_offset), dim=-1),
                torch.stack((middle_vx, middle_yaw_offset), dim=-1),
                torch.stack((rear_vx, rear_yaw_base - rear_yaw_offset), dim=-1),
                torch.stack((rear_vx, rear_yaw_base + rear_yaw_offset), dim=-1),
            ),
            dim=1,
        )
        jacobian_output_order = jacobian_paper_order[:, self._paper_to_output, :]
        return self._squeeze_if_needed(jacobian_output_order, squeeze_output)

    def compute_wheel_speed_targets_from_planar_command(self, ball_joint_pos, planar_command):
        """Map [Vx^d, wz^d] to six wheel angular-speed targets."""

        ball_joint_pos, squeeze_pos = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        planar_command, squeeze_cmd = self._ensure_2d(planar_command, 2, "planar_command")
        (ball_joint_pos, planar_command), _ = self._broadcast_batch(ball_joint_pos, planar_command)
        jacobian = self.compute_wheel_speed_jacobian(ball_joint_pos)
        wheel_targets = self.torch.einsum("bij,bj->bi", jacobian, planar_command)
        return self._squeeze_if_needed(wheel_targets, squeeze_pos and squeeze_cmd)

    def compute_traction_scales(
        self,
        wheel_longitudinal_slip,
        wheel_normal_contact_force,
        *,
        min_scale: float,
        longitudinal_slip_start: float,
        longitudinal_slip_full: float,
        contact_force_low: float,
        contact_force_high: float,
    ):
        wheel_longitudinal_slip, squeeze_slip = self._ensure_2d(
            wheel_longitudinal_slip, len(OUTPUT_WHEEL_JOINT_NAMES), "wheel_longitudinal_slip"
        )
        wheel_normal_contact_force, squeeze_force = self._ensure_2d(
            wheel_normal_contact_force, len(OUTPUT_WHEEL_JOINT_NAMES), "wheel_normal_contact_force"
        )
        (wheel_longitudinal_slip, wheel_normal_contact_force), _ = self._broadcast_batch(
            wheel_longitudinal_slip, wheel_normal_contact_force
        )

        abs_longitudinal_slip = self.torch.abs(wheel_longitudinal_slip)
        slip_span = max(longitudinal_slip_full - longitudinal_slip_start, 1.0e-6)
        slip_ratio = self.torch.clamp((abs_longitudinal_slip - longitudinal_slip_start) / slip_span, min=0.0, max=1.0)
        longitudinal_scale = 1.0 - slip_ratio * (1.0 - min_scale)

        contact_span = max(contact_force_high - contact_force_low, 1.0e-6)
        contact_ratio = self.torch.clamp(
            (wheel_normal_contact_force - contact_force_low) / contact_span,
            min=0.0,
            max=1.0,
        )
        contact_scale = min_scale + contact_ratio * (1.0 - min_scale)

        traction_scale = self.torch.minimum(longitudinal_scale, contact_scale)
        if squeeze_slip and squeeze_force:
            return traction_scale[0], longitudinal_scale[0], contact_scale[0]
        return traction_scale, longitudinal_scale, contact_scale

    def apply_traction_scaling(
        self,
        wheel_targets,
        wheel_longitudinal_slip,
        wheel_normal_contact_force,
        *,
        min_scale: float,
        longitudinal_slip_start: float,
        longitudinal_slip_full: float,
        contact_force_low: float,
        contact_force_high: float,
    ):
        wheel_targets, squeeze_targets = self._ensure_2d(wheel_targets, len(OUTPUT_WHEEL_JOINT_NAMES), "wheel_targets")
        traction_scale, longitudinal_scale, contact_scale = self.compute_traction_scales(
            wheel_longitudinal_slip,
            wheel_normal_contact_force,
            min_scale=min_scale,
            longitudinal_slip_start=longitudinal_slip_start,
            longitudinal_slip_full=longitudinal_slip_full,
            contact_force_low=contact_force_low,
            contact_force_high=contact_force_high,
        )
        traction_scale, squeeze_scale = self._ensure_2d(traction_scale, len(OUTPUT_WHEEL_JOINT_NAMES), "traction_scale")
        (wheel_targets, traction_scale), _ = self._broadcast_batch(wheel_targets, traction_scale)
        scaled_targets = wheel_targets * traction_scale
        if squeeze_targets and squeeze_scale:
            return scaled_targets[0], traction_scale[0], longitudinal_scale[0], contact_scale[0]
        return scaled_targets, traction_scale, longitudinal_scale, contact_scale


__all__ = [
    "BALL_JOINT_NAMES",
    "DEFAULT_COMPLETE_CAR_GEOMETRY",
    "OUTPUT_WHEEL_JOINT_NAMES",
    "CompleteCarWheelAllocatorGeometry",
    "NumpyWheelSpeedAllocator",
    "TorchWheelSpeedAllocator",
]
