"""Basic numerical checks for the complete-car wheel-speed allocator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

ALLOCATOR_PATH = Path(__file__).resolve().parents[1] / "kinematics" / "wheel_speed_allocator.py"
ALLOCATOR_SPEC = importlib.util.spec_from_file_location("wheel_speed_allocator_module", ALLOCATOR_PATH)
if ALLOCATOR_SPEC is None or ALLOCATOR_SPEC.loader is None:
    raise RuntimeError(f"Failed to load allocator module from {ALLOCATOR_PATH}.")
ALLOCATOR_MODULE = importlib.util.module_from_spec(ALLOCATOR_SPEC)
sys.modules[ALLOCATOR_SPEC.name] = ALLOCATOR_MODULE
ALLOCATOR_SPEC.loader.exec_module(ALLOCATOR_MODULE)
NumpyWheelSpeedAllocator = ALLOCATOR_MODULE.NumpyWheelSpeedAllocator


def main() -> None:
    allocator = NumpyWheelSpeedAllocator()

    ball_joint_pos = np.zeros(6, dtype=np.float64)

    jacobian = allocator.compute_wheel_speed_jacobian(ball_joint_pos)
    print("Jacobian shape:", jacobian.shape)
    print("Output wheel-joint order:", allocator.geometry.wheel_joint_names)
    np.testing.assert_equal(jacobian.shape, (6, 2))

    zero_command = np.zeros(2, dtype=np.float64)
    zero_targets = allocator.compute_wheel_speed_targets_from_planar_command(
        ball_joint_pos,
        zero_command,
    )
    print("Zero-command wheel targets:", np.round(zero_targets, 8).tolist())
    np.testing.assert_allclose(zero_targets, np.zeros(6, dtype=np.float64), atol=1.0e-10)

    forward_command = np.array([1.0, 0.0], dtype=np.float64)
    forward_targets = allocator.compute_wheel_speed_targets_from_planar_command(
        ball_joint_pos,
        forward_command,
    )
    expected_forward = np.full(6, 1.0 / allocator.geometry.r_wheel, dtype=np.float64)
    print("Forward-command wheel targets:", np.round(forward_targets, 8).tolist())
    np.testing.assert_allclose(forward_targets, expected_forward, atol=1.0e-10)

    yaw_command = np.array([0.0, 0.5], dtype=np.float64)
    yaw_targets = allocator.compute_wheel_speed_targets_from_planar_command(
        ball_joint_pos,
        yaw_command,
    )
    print("Yaw-command wheel targets:", np.round(yaw_targets, 8).tolist())
    expected_yaw = (yaw_command[1] / allocator.geometry.r_wheel) * np.array(
        [
            -allocator.geometry.d2 / 2.0,
            allocator.geometry.d2 / 2.0,
            -allocator.geometry.d1 / 2.0,
            allocator.geometry.d1 / 2.0,
            -allocator.geometry.d3 / 2.0,
            allocator.geometry.d3 / 2.0,
        ],
        dtype=np.float64,
    )
    np.testing.assert_allclose(
        yaw_targets,
        expected_yaw,
        atol=1.0e-10,
    )

    nonzero_ball_joint_pos = np.array([0.2, -0.1, 0.05, -0.15, 0.08, -0.04], dtype=np.float64)
    nonzero_planar_command = np.array([0.7, 0.3], dtype=np.float64)
    nonzero_targets = allocator.compute_wheel_speed_targets_from_planar_command(
        nonzero_ball_joint_pos,
        nonzero_planar_command,
    )
    jacobian_nonzero = allocator.compute_wheel_speed_jacobian(nonzero_ball_joint_pos)
    np.testing.assert_allclose(
        nonzero_targets,
        jacobian_nonzero @ nonzero_planar_command,
        atol=1.0e-10,
    )
    print("Nonzero-command wheel targets:", np.round(nonzero_targets, 8).tolist())

    print("Validation checks passed.")


if __name__ == "__main__":
    main()
