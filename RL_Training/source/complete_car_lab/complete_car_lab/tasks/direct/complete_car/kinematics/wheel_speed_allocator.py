"""Wheel-speed allocation using the thesis Jacobian and measured geometry."""

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

PLANAR_COMMAND_TRANSFORM = np.array(
    (
        (1.0, 0.0, -0.00614478162640497),
        (0.0, 1.0, -1.07379532542362e-5),
        (0.0, 0.0, 1.0),
    ),
    dtype=np.float64,
)


@dataclass(frozen=True)
class CompleteCarWheelAllocatorGeometry:
    """Measured complete-car geometry used by the wheel-speed allocator."""

    a: tuple[float, float, float] = (0.25633374, -0.00614478, 0.01121736)
    b1: tuple[float, float, float] = (-0.30654739 , -0.00428771, -0.00608413)
    b3: tuple[float, float, float] = (0.30633826, -0.00426448, -0.00610151)
    r1L: tuple[float, float, float] = (-0.00989449, 0.21932649, -0.04353780)
    r1R: tuple[float, float, float] = (-0.00989449, -0.22805226, -0.04262877)
    r2L: tuple[float, float, float] = (0.00000932, 0.21754506, -0.02578188)
    r2R: tuple[float, float, float] = (0.00000932, -0.22983462, -0.02578188)
    r3L: tuple[float, float, float] = (0.00968251, 0.21950007, -0.04264614)
    r3R: tuple[float, float, float] = (0.00968251, -0.22787868, -0.04355517)
    r_wheel: float = 0.19
    ball_joint_names: tuple[str, ...] = BALL_JOINT_NAMES
    wheel_joint_names: tuple[str, ...] = OUTPUT_WHEEL_JOINT_NAMES
    paper_wheel_joint_names: tuple[str, ...] = PAPER_WHEEL_JOINT_NAMES


DEFAULT_COMPLETE_CAR_GEOMETRY = CompleteCarWheelAllocatorGeometry()


def transform_planar_command_numpy(planar_command) -> np.ndarray:
    """Apply the measured left-multiplication transform to [vx, wz]."""

    planar_command = np.asarray(planar_command, dtype=np.float64)
    if planar_command.ndim == 1:
        if planar_command.shape[0] != 2:
            raise ValueError("planar_command must have shape (2,).")
        planar_command_2d = planar_command.reshape(1, -1)
        squeeze_output = True
    elif planar_command.ndim == 2 and planar_command.shape[1] == 2:
        planar_command_2d = planar_command
        squeeze_output = False
    else:
        raise ValueError("planar_command must have shape (N, 2).")

    planar_command_xyz = np.zeros((planar_command_2d.shape[0], 3), dtype=np.float64)
    planar_command_xyz[:, 0] = planar_command_2d[:, 0]
    planar_command_xyz[:, 2] = planar_command_2d[:, 1]
    transformed_xyz = planar_command_xyz @ PLANAR_COMMAND_TRANSFORM.T
    transformed = np.stack((transformed_xyz[:, 0], transformed_xyz[:, 2]), axis=1)
    return transformed.reshape(-1) if squeeze_output else transformed
def _numpy_skew_single(vector: np.ndarray) -> np.ndarray:
    x, y, z = vector.tolist()
    return np.array(
        [
            [0.0, -z, y],
            [z, 0.0, -x],
            [-y, x, 0.0],
        ],
        dtype=np.float64,
    )


def _numpy_module_wheel_map(left_center: np.ndarray, right_center: np.ndarray, wheel_radius: float) -> np.ndarray:
    e_x = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    left_row = np.concatenate((e_x, -(e_x @ _numpy_skew_single(left_center)))) / wheel_radius
    right_row = np.concatenate((e_x, -(e_x @ _numpy_skew_single(right_center)))) / wheel_radius
    return np.stack((left_row, right_row), axis=0)


class NumpyWheelSpeedAllocator:
    """NumPy allocator for independent kinematics validation."""

    def __init__(self, geometry: CompleteCarWheelAllocatorGeometry | None = None):
        self.geometry = geometry or DEFAULT_COMPLETE_CAR_GEOMETRY
        self._paper_to_output = np.asarray(PAPER_TO_OUTPUT_ROW_INDICES, dtype=np.int64)

        self._a = np.asarray(self.geometry.a, dtype=np.float64)
        self._b1 = np.asarray(self.geometry.b1, dtype=np.float64)
        self._b3 = np.asarray(self.geometry.b3, dtype=np.float64)

        self._s_a = _numpy_skew_single(self._a)
        self._s_b1 = _numpy_skew_single(self._b1)
        self._s_b3 = _numpy_skew_single(self._b3)

        self._h1 = _numpy_module_wheel_map(
            np.asarray(self.geometry.r1L, dtype=np.float64),
            np.asarray(self.geometry.r1R, dtype=np.float64),
            self.geometry.r_wheel,
        )
        self._h2 = _numpy_module_wheel_map(
            np.asarray(self.geometry.r2L, dtype=np.float64),
            np.asarray(self.geometry.r2R, dtype=np.float64),
            self.geometry.r_wheel,
        )
        self._h3 = _numpy_module_wheel_map(
            np.asarray(self.geometry.r3L, dtype=np.float64),
            np.asarray(self.geometry.r3R, dtype=np.float64),
            self.geometry.r_wheel,
        )
        self._k2 = np.block(
            [
                [np.eye(3), np.zeros((3, 3)), np.zeros((3, 3)), np.zeros((3, 3))],
                [np.zeros((3, 3)), np.eye(3), np.zeros((3, 3)), np.zeros((3, 3))],
            ]
        )

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

    @staticmethod
    def _rot_x(roll: np.ndarray) -> np.ndarray:
        cos_r = np.cos(roll)
        sin_r = np.sin(roll)
        ones = np.ones_like(roll)
        zeros = np.zeros_like(roll)
        return np.stack(
            (
                np.stack((ones, zeros, zeros), axis=-1),
                np.stack((zeros, cos_r, -sin_r), axis=-1),
                np.stack((zeros, sin_r, cos_r), axis=-1),
            ),
            axis=-2,
        )

    @staticmethod
    def _rot_y(pitch: np.ndarray) -> np.ndarray:
        cos_p = np.cos(pitch)
        sin_p = np.sin(pitch)
        ones = np.ones_like(pitch)
        zeros = np.zeros_like(pitch)
        return np.stack(
            (
                np.stack((cos_p, zeros, sin_p), axis=-1),
                np.stack((zeros, ones, zeros), axis=-1),
                np.stack((-sin_p, zeros, cos_p), axis=-1),
            ),
            axis=-2,
        )

    @staticmethod
    def _rot_z(yaw: np.ndarray) -> np.ndarray:
        cos_y = np.cos(yaw)
        sin_y = np.sin(yaw)
        ones = np.ones_like(yaw)
        zeros = np.zeros_like(yaw)
        return np.stack(
            (
                np.stack((cos_y, -sin_y, zeros), axis=-1),
                np.stack((sin_y, cos_y, zeros), axis=-1),
                np.stack((zeros, zeros, ones), axis=-1),
            ),
            axis=-2,
        )

    @staticmethod
    def _euler_rate_matrix(roll: np.ndarray, pitch: np.ndarray) -> np.ndarray:
        sin_roll = np.sin(roll)
        cos_roll = np.cos(roll)
        sin_pitch = np.sin(pitch)
        cos_pitch = np.cos(pitch)
        zeros = np.zeros_like(roll)
        ones = np.ones_like(roll)
        return np.stack(
            (
                np.stack((-sin_pitch, zeros, ones), axis=-1),
                np.stack((sin_roll * cos_pitch, cos_roll, zeros), axis=-1),
                np.stack((cos_roll * cos_pitch, -sin_roll, zeros), axis=-1),
            ),
            axis=-2,
        )

    def build_generalized_velocity_from_planar_command(
        self,
        ball_joint_vel,
        planar_command,
    ) -> np.ndarray:
        """Build xi from qdot and planar command [vx, yaw_rate]."""

        ball_joint_vel, squeeze_vel = self._ensure_2d(ball_joint_vel, 6, "ball_joint_vel")
        planar_command = np.asarray(planar_command, dtype=np.float64)
        if planar_command.ndim == 1:
            if planar_command.shape[0] != 2:
                raise ValueError("planar_command must have shape (2,).")
            planar_command = planar_command.reshape(1, -1)
            squeeze_cmd = True
        elif planar_command.ndim == 2 and planar_command.shape[1] == 2:
            squeeze_cmd = False
        else:
            raise ValueError("planar_command must have shape (N, 2).")

        (ball_joint_vel, planar_command), _ = self._broadcast_batch(ball_joint_vel, planar_command)

        batch_size = planar_command.shape[0]
        spatial_twist = np.zeros((batch_size, 6), dtype=np.float64)
        spatial_twist[:, 0] = planar_command[:, 0]
        spatial_twist[:, 5] = planar_command[:, 1]
        generalized_velocity = np.concatenate(
            (
                spatial_twist[:, :3],
                spatial_twist[:, 3:],
                ball_joint_vel[:, :3],
                ball_joint_vel[:, 3:],
            ),
            axis=1,
        )
        return self._squeeze_if_needed(generalized_velocity, squeeze_vel and squeeze_cmd)

    def build_generalized_velocity_from_spatial_twist(
        self,
        ball_joint_vel,
        spatial_twist_command,
    ) -> np.ndarray:
        """Build xi from qdot and spatial twist [vx, vy, vz, wx, wy, wz]."""

        ball_joint_vel, squeeze_vel = self._ensure_2d(ball_joint_vel, 6, "ball_joint_vel")
        spatial_twist_command, squeeze_twist = self._ensure_2d(
            spatial_twist_command,
            6,
            "spatial_twist_command",
        )
        (ball_joint_vel, spatial_twist_command), _ = self._broadcast_batch(ball_joint_vel, spatial_twist_command)
        generalized_velocity = np.concatenate(
            (
                spatial_twist_command[:, :3],
                spatial_twist_command[:, 3:],
                ball_joint_vel[:, :3],
                ball_joint_vel[:, 3:],
            ),
            axis=1,
        )
        return self._squeeze_if_needed(generalized_velocity, squeeze_vel and squeeze_twist)

    def compute_wheel_speed_jacobian(self, ball_joint_pos) -> np.ndarray:
        """Return the 6x12 wheel-speed Jacobian in actual wheel-joint order."""

        ball_joint_pos, squeeze_output = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")

        q_front = ball_joint_pos[:, :3]
        q_rear = ball_joint_pos[:, 3:]
        psi_f, theta_f, phi_f = q_front[:, 0], q_front[:, 1], q_front[:, 2]
        psi_r, theta_r, phi_r = q_rear[:, 0], q_rear[:, 1], q_rear[:, 2]

        r2_1 = np.transpose(self._rot_z(psi_f) @ self._rot_y(theta_f) @ self._rot_x(phi_f), (0, 2, 1))
        r2_3 = np.transpose(self._rot_z(psi_r) @ self._rot_y(theta_r) @ self._rot_x(phi_r), (0, 2, 1))
        t_front = self._euler_rate_matrix(phi_f, theta_f)
        t_rear = self._euler_rate_matrix(phi_r, theta_r)

        batch_size = ball_joint_pos.shape[0]
        zeros = np.zeros((batch_size, 3, 3), dtype=np.float64)
        s_a = np.broadcast_to(self._s_a, (batch_size, 3, 3))
        s_b1 = np.broadcast_to(self._s_b1, (batch_size, 3, 3))
        s_b3 = np.broadcast_to(self._s_b3, (batch_size, 3, 3))
        h1 = np.broadcast_to(self._h1, (batch_size, 2, 6))
        h2 = np.broadcast_to(self._h2, (batch_size, 2, 6))
        h3 = np.broadcast_to(self._h3, (batch_size, 2, 6))
        k2 = np.broadcast_to(self._k2, (batch_size, 6, 12))

        k1 = np.concatenate(
            (
                np.concatenate((r2_1, -(r2_1 @ s_a + s_b1 @ r2_1), -(s_b1 @ t_front), zeros), axis=2),
                np.concatenate((zeros, r2_1, t_front, zeros), axis=2),
            ),
            axis=1,
        )
        k3 = np.concatenate(
            (
                np.concatenate((r2_3, r2_3 @ s_a - s_b3 @ r2_3, zeros, -(s_b3 @ t_rear)), axis=2),
                np.concatenate((zeros, r2_3, zeros, t_rear), axis=2),
            ),
            axis=1,
        )

        jacobian_paper_order = np.concatenate((h1 @ k1, h2 @ k2, h3 @ k3), axis=1)
        jacobian_output_order = jacobian_paper_order[:, self._paper_to_output, :]
        return self._squeeze_if_needed(jacobian_output_order, squeeze_output)

    def compute_wheel_speed_targets_from_generalized_velocity(
        self,
        ball_joint_pos,
        generalized_velocity,
    ) -> np.ndarray:
        """Map xi to 6 wheel angular-speed targets in actual wheel-joint order."""

        ball_joint_pos, squeeze_pos = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        generalized_velocity, squeeze_xi = self._ensure_2d(generalized_velocity, 12, "generalized_velocity")
        (ball_joint_pos, generalized_velocity), _ = self._broadcast_batch(ball_joint_pos, generalized_velocity)
        jacobian = self.compute_wheel_speed_jacobian(ball_joint_pos)
        wheel_targets = np.einsum("bij,bj->bi", jacobian, generalized_velocity)
        return self._squeeze_if_needed(wheel_targets, squeeze_pos and squeeze_xi)

    def compute_wheel_speed_targets_from_planar_command(
        self,
        ball_joint_pos,
        ball_joint_vel,
        planar_command,
    ) -> np.ndarray:
        generalized_velocity = self.build_generalized_velocity_from_planar_command(ball_joint_vel, planar_command)
        return self.compute_wheel_speed_targets_from_generalized_velocity(ball_joint_pos, generalized_velocity)

    def compute_wheel_speed_targets_from_spatial_twist(
        self,
        ball_joint_pos,
        ball_joint_vel,
        spatial_twist_command,
    ) -> np.ndarray:
        generalized_velocity = self.build_generalized_velocity_from_spatial_twist(ball_joint_vel, spatial_twist_command)
        return self.compute_wheel_speed_targets_from_generalized_velocity(ball_joint_pos, generalized_velocity)


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

        self._a = torch.tensor(self.geometry.a, device=self.device, dtype=self.dtype)
        self._b1 = torch.tensor(self.geometry.b1, device=self.device, dtype=self.dtype)
        self._b3 = torch.tensor(self.geometry.b3, device=self.device, dtype=self.dtype)

        self._s_a = self._skew_single(self._a)
        self._s_b1 = self._skew_single(self._b1)
        self._s_b3 = self._skew_single(self._b3)

        self._h1 = self._module_wheel_map(
            torch.tensor(self.geometry.r1L, device=self.device, dtype=self.dtype),
            torch.tensor(self.geometry.r1R, device=self.device, dtype=self.dtype),
            self.geometry.r_wheel,
        )
        self._h2 = self._module_wheel_map(
            torch.tensor(self.geometry.r2L, device=self.device, dtype=self.dtype),
            torch.tensor(self.geometry.r2R, device=self.device, dtype=self.dtype),
            self.geometry.r_wheel,
        )
        self._h3 = self._module_wheel_map(
            torch.tensor(self.geometry.r3L, device=self.device, dtype=self.dtype),
            torch.tensor(self.geometry.r3R, device=self.device, dtype=self.dtype),
            self.geometry.r_wheel,
        )
        self._k2 = torch.tensor(
            np.block(
                [
                    [np.eye(3), np.zeros((3, 3)), np.zeros((3, 3)), np.zeros((3, 3))],
                    [np.zeros((3, 3)), np.eye(3), np.zeros((3, 3)), np.zeros((3, 3))],
                ]
            ),
            device=self.device,
            dtype=self.dtype,
        )

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

    def _expand_const(self, tensor, batch_size: int):
        return tensor.unsqueeze(0).expand(batch_size, *tensor.shape)

    def _skew_single(self, vector):
        torch = self.torch
        x, y, z = vector.unbind(dim=-1)
        return torch.stack(
            (
                torch.stack((torch.zeros_like(x), -z, y), dim=-1),
                torch.stack((z, torch.zeros_like(x), -x), dim=-1),
                torch.stack((-y, x, torch.zeros_like(x)), dim=-1),
            ),
            dim=-2,
        )

    def _module_wheel_map(self, left_center, right_center, wheel_radius: float):
        torch = self.torch
        e_x = torch.tensor((1.0, 0.0, 0.0), device=self.device, dtype=self.dtype)
        left_row = torch.cat((e_x, -(e_x @ self._skew_single(left_center)))) / wheel_radius
        right_row = torch.cat((e_x, -(e_x @ self._skew_single(right_center)))) / wheel_radius
        return torch.stack((left_row, right_row), dim=0)

    def _rot_x(self, roll):
        torch = self.torch
        cos_r = torch.cos(roll)
        sin_r = torch.sin(roll)
        ones = torch.ones_like(roll)
        zeros = torch.zeros_like(roll)
        return torch.stack(
            (
                torch.stack((ones, zeros, zeros), dim=-1),
                torch.stack((zeros, cos_r, -sin_r), dim=-1),
                torch.stack((zeros, sin_r, cos_r), dim=-1),
            ),
            dim=-2,
        )

    def _rot_y(self, pitch):
        torch = self.torch
        cos_p = torch.cos(pitch)
        sin_p = torch.sin(pitch)
        ones = torch.ones_like(pitch)
        zeros = torch.zeros_like(pitch)
        return torch.stack(
            (
                torch.stack((cos_p, zeros, sin_p), dim=-1),
                torch.stack((zeros, ones, zeros), dim=-1),
                torch.stack((-sin_p, zeros, cos_p), dim=-1),
            ),
            dim=-2,
        )

    def _rot_z(self, yaw):
        torch = self.torch
        cos_y = torch.cos(yaw)
        sin_y = torch.sin(yaw)
        ones = torch.ones_like(yaw)
        zeros = torch.zeros_like(yaw)
        return torch.stack(
            (
                torch.stack((cos_y, -sin_y, zeros), dim=-1),
                torch.stack((sin_y, cos_y, zeros), dim=-1),
                torch.stack((zeros, zeros, ones), dim=-1),
            ),
            dim=-2,
        )

    def _euler_rate_matrix(self, roll, pitch):
        torch = self.torch
        sin_roll = torch.sin(roll)
        cos_roll = torch.cos(roll)
        sin_pitch = torch.sin(pitch)
        cos_pitch = torch.cos(pitch)
        zeros = torch.zeros_like(roll)
        ones = torch.ones_like(roll)
        return torch.stack(
            (
                torch.stack((-sin_pitch, zeros, ones), dim=-1),
                torch.stack((sin_roll * cos_pitch, cos_roll, zeros), dim=-1),
                torch.stack((cos_roll * cos_pitch, -sin_roll, zeros), dim=-1),
            ),
            dim=-2,
        )

    def build_generalized_velocity_from_planar_command(self, ball_joint_vel, planar_command):
        torch = self.torch
        ball_joint_vel, squeeze_vel = self._ensure_2d(ball_joint_vel, 6, "ball_joint_vel")
        planar_command = (
            planar_command
            if torch.is_tensor(planar_command)
            else torch.as_tensor(planar_command, device=self.device, dtype=self.dtype)
        )
        planar_command = planar_command.to(device=self.device, dtype=self.dtype)
        if planar_command.ndim == 1:
            if planar_command.shape[0] != 2:
                raise ValueError("planar_command must have shape (2,).")
            planar_command = planar_command.reshape(1, -1)
            squeeze_cmd = True
        elif planar_command.ndim == 2 and planar_command.shape[1] == 2:
            squeeze_cmd = False
        else:
            raise ValueError("planar_command must have shape (N, 2).")

        (ball_joint_vel, planar_command), _ = self._broadcast_batch(ball_joint_vel, planar_command)

        batch_size = planar_command.shape[0]
        spatial_twist = torch.zeros((batch_size, 6), device=self.device, dtype=self.dtype)
        spatial_twist[:, 0] = planar_command[:, 0]
        spatial_twist[:, 5] = planar_command[:, 1]
        generalized_velocity = torch.cat(
            (
                spatial_twist[:, :3],
                spatial_twist[:, 3:],
                ball_joint_vel[:, :3],
                ball_joint_vel[:, 3:],
            ),
            dim=1,
        )
        return self._squeeze_if_needed(generalized_velocity, squeeze_vel and squeeze_cmd)

    def build_generalized_velocity_from_spatial_twist(self, ball_joint_vel, spatial_twist_command):
        ball_joint_vel, squeeze_vel = self._ensure_2d(ball_joint_vel, 6, "ball_joint_vel")
        spatial_twist_command, squeeze_twist = self._ensure_2d(
            spatial_twist_command,
            6,
            "spatial_twist_command",
        )
        (ball_joint_vel, spatial_twist_command), _ = self._broadcast_batch(ball_joint_vel, spatial_twist_command)
        generalized_velocity = self.torch.cat(
            (
                spatial_twist_command[:, :3],
                spatial_twist_command[:, 3:],
                ball_joint_vel[:, :3],
                ball_joint_vel[:, 3:],
            ),
            dim=1,
        )
        return self._squeeze_if_needed(generalized_velocity, squeeze_vel and squeeze_twist)

    def compute_wheel_speed_jacobian(self, ball_joint_pos):
        ball_joint_pos, squeeze_output = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")

        q_front = ball_joint_pos[:, :3]
        q_rear = ball_joint_pos[:, 3:]
        psi_f, theta_f, phi_f = q_front[:, 0], q_front[:, 1], q_front[:, 2]
        psi_r, theta_r, phi_r = q_rear[:, 0], q_rear[:, 1], q_rear[:, 2]

        r2_1 = (self._rot_z(psi_f) @ self._rot_y(theta_f) @ self._rot_x(phi_f)).transpose(1, 2)
        r2_3 = (self._rot_z(psi_r) @ self._rot_y(theta_r) @ self._rot_x(phi_r)).transpose(1, 2)
        t_front = self._euler_rate_matrix(phi_f, theta_f)
        t_rear = self._euler_rate_matrix(phi_r, theta_r)

        batch_size = ball_joint_pos.shape[0]
        zeros = self.torch.zeros((batch_size, 3, 3), device=self.device, dtype=self.dtype)
        s_a = self._expand_const(self._s_a, batch_size)
        s_b1 = self._expand_const(self._s_b1, batch_size)
        s_b3 = self._expand_const(self._s_b3, batch_size)
        h1 = self._expand_const(self._h1, batch_size)
        h2 = self._expand_const(self._h2, batch_size)
        h3 = self._expand_const(self._h3, batch_size)
        k2 = self._expand_const(self._k2, batch_size)

        k1 = self.torch.cat(
            (
                self.torch.cat((r2_1, -(r2_1 @ s_a + s_b1 @ r2_1), -(s_b1 @ t_front), zeros), dim=2),
                self.torch.cat((zeros, r2_1, t_front, zeros), dim=2),
            ),
            dim=1,
        )
        k3 = self.torch.cat(
            (
                self.torch.cat((r2_3, r2_3 @ s_a - s_b3 @ r2_3, zeros, -(s_b3 @ t_rear)), dim=2),
                self.torch.cat((zeros, r2_3, zeros, t_rear), dim=2),
            ),
            dim=1,
        )

        jacobian_paper_order = self.torch.cat((h1 @ k1, h2 @ k2, h3 @ k3), dim=1)
        jacobian_output_order = jacobian_paper_order[:, self._paper_to_output, :]
        return self._squeeze_if_needed(jacobian_output_order, squeeze_output)

    def compute_wheel_speed_targets_from_generalized_velocity(self, ball_joint_pos, generalized_velocity):
        ball_joint_pos, squeeze_pos = self._ensure_2d(ball_joint_pos, 6, "ball_joint_pos")
        generalized_velocity, squeeze_xi = self._ensure_2d(generalized_velocity, 12, "generalized_velocity")
        (ball_joint_pos, generalized_velocity), _ = self._broadcast_batch(ball_joint_pos, generalized_velocity)
        jacobian = self.compute_wheel_speed_jacobian(ball_joint_pos)
        wheel_targets = self.torch.einsum("bij,bj->bi", jacobian, generalized_velocity)
        return self._squeeze_if_needed(wheel_targets, squeeze_pos and squeeze_xi)

    def compute_wheel_speed_targets_from_planar_command(self, ball_joint_pos, ball_joint_vel, planar_command):
        generalized_velocity = self.build_generalized_velocity_from_planar_command(ball_joint_vel, planar_command)
        return self.compute_wheel_speed_targets_from_generalized_velocity(ball_joint_pos, generalized_velocity)

    def compute_wheel_speed_targets_from_spatial_twist(self, ball_joint_pos, ball_joint_vel, spatial_twist_command):
        generalized_velocity = self.build_generalized_velocity_from_spatial_twist(ball_joint_vel, spatial_twist_command)
        return self.compute_wheel_speed_targets_from_generalized_velocity(ball_joint_pos, generalized_velocity)

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
            return (
                traction_scale[0],
                longitudinal_scale[0],
                contact_scale[0],
            )
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
        (wheel_targets, traction_scale, longitudinal_scale, contact_scale), _ = self._broadcast_batch(
            wheel_targets,
            traction_scale,
            self._ensure_2d(longitudinal_scale, len(OUTPUT_WHEEL_JOINT_NAMES), "longitudinal_scale")[0],
            self._ensure_2d(contact_scale, len(OUTPUT_WHEEL_JOINT_NAMES), "contact_scale")[0],
        )
        scaled_targets = wheel_targets * traction_scale
        if squeeze_targets and squeeze_scale:
            return scaled_targets[0], traction_scale[0], longitudinal_scale[0], contact_scale[0]
        return scaled_targets, traction_scale, longitudinal_scale, contact_scale


__all__ = [
    "BALL_JOINT_NAMES",
    "DEFAULT_COMPLETE_CAR_GEOMETRY",
    "OUTPUT_WHEEL_JOINT_NAMES",
    "PLANAR_COMMAND_TRANSFORM",
    "CompleteCarWheelAllocatorGeometry",
    "NumpyWheelSpeedAllocator",
    "TorchWheelSpeedAllocator",
    "transform_planar_command_numpy",
]
