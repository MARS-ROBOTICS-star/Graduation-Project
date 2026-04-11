"""Basic numerical checks for the complete-car wheel-speed allocator."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[7]
EXTENSION_SOURCE = PROJECT_ROOT / "source" / "complete_car_lab"
if str(EXTENSION_SOURCE) not in sys.path:
    sys.path.insert(0, str(EXTENSION_SOURCE))

from complete_car_lab.tasks.direct.complete_car.kinematics.wheel_speed_allocator import NumpyWheelSpeedAllocator


def main() -> None:
    allocator = NumpyWheelSpeedAllocator()

    ball_joint_pos = np.zeros(6, dtype=np.float64)
    ball_joint_vel = np.zeros(6, dtype=np.float64)

    jacobian = allocator.compute_wheel_speed_jacobian(ball_joint_pos)
    print("Jacobian shape:", jacobian.shape)
    print("Output wheel-joint order:", allocator.geometry.wheel_joint_names)

    zero_command = np.zeros(4, dtype=np.float64)
    zero_targets = allocator.compute_wheel_speed_targets_from_planar_command(ball_joint_pos, ball_joint_vel, zero_command)
    print("Zero-command wheel targets:", np.round(zero_targets, 8).tolist())
    np.testing.assert_allclose(zero_targets, np.zeros(6, dtype=np.float64), atol=1.0e-10)

    forward_command = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
    forward_targets = allocator.compute_wheel_speed_targets_from_planar_command(
        ball_joint_pos,
        ball_joint_vel,
        forward_command,
    )
    expected_forward = np.full(6, 1.0 / allocator.geometry.r_wheel, dtype=np.float64)
    print("Forward-command wheel targets:", np.round(forward_targets, 8).tolist())
    np.testing.assert_allclose(forward_targets, expected_forward, atol=1.0e-10)

    yaw_command = np.array([0.0, 0.0, 0.5, 0.0], dtype=np.float64)
    yaw_targets = allocator.compute_wheel_speed_targets_from_planar_command(ball_joint_pos, ball_joint_vel, yaw_command)
    print("Yaw-command wheel targets:", np.round(yaw_targets, 8).tolist())

    print("Validation checks passed.")


if __name__ == "__main__":
    main()
