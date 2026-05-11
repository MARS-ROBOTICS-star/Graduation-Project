"""CLI validation tool for direct ball-joint targets and the low-slip traction allocator."""

from __future__ import annotations

import argparse
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

DEFAULT_BALL_JOINT_RATE_TARGETS = (0.0,) * 6
DEFAULT_Q_LOWER_LIMITS = (-0.6, -1.0, -0.5, -0.6, -1.0, -0.5)
DEFAULT_Q_UPPER_LIMITS = (0.6, 0.4, 0.5, 0.6, 0.4, 0.5)
DEFAULT_PLANAR_LIMITS = (2.0, 2.0)
DEFAULT_CONTACT_FORCES = (1.0 / 6.0,) * 6
DEFAULT_WHEEL_JOINT_VEL = (0.0,) * 6
DEFAULT_ROLLING_SPEED_ACTUAL = (0.0,) * 6
DEFAULT_LATERAL_SPEED_ACTUAL = (0.0,) * 6


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the low-slip Chapter03 control chain with manual inputs. "
            "Provide q, q^d, qdot_alloc, planar command, wheel contact state, and actual wheel motion."
        )
    )
    joint_help = "Six values in joint order [spm1_z, spm1_y, spm1_x, spm2_z, spm2_y, spm2_x]."
    q_group = parser.add_mutually_exclusive_group()
    q_group.add_argument("--ball-joint-pos", nargs=6, type=float, help=f"{joint_help} Current q in rad.")
    q_group.add_argument("--ball-joint-pos-deg", nargs=6, type=float, help=f"{joint_help} Current q in deg.")

    qd_group = parser.add_mutually_exclusive_group()
    qd_group.add_argument("--ball-joint-desired", nargs=6, type=float, help=f"{joint_help} Desired q^d in rad.")
    qd_group.add_argument("--ball-joint-desired-deg", nargs=6, type=float, help=f"{joint_help} Desired q^d in deg.")

    parser.add_argument("--planar-command", nargs=2, type=float, metavar=("VX", "WZ"))
    parser.add_argument("--ball-joint-rate-targets", nargs=6, type=float, default=DEFAULT_BALL_JOINT_RATE_TARGETS)
    parser.add_argument("--ball-joint-lower-limits", nargs=6, type=float, default=DEFAULT_Q_LOWER_LIMITS)
    parser.add_argument("--ball-joint-upper-limits", nargs=6, type=float, default=DEFAULT_Q_UPPER_LIMITS)
    parser.add_argument("--wheel-normal-contact-force", nargs=6, type=float, default=DEFAULT_CONTACT_FORCES)
    parser.add_argument("--wheel-joint-vel", nargs=6, type=float, default=DEFAULT_WHEEL_JOINT_VEL)
    parser.add_argument("--rolling-speed-actual", nargs=6, type=float, default=DEFAULT_ROLLING_SPEED_ACTUAL)
    parser.add_argument("--lateral-speed-actual", nargs=6, type=float, default=DEFAULT_LATERAL_SPEED_ACTUAL)
    parser.add_argument("--lambda-tracking", type=float, default=1.0)
    parser.add_argument("--lambda-lateral", type=float, default=5.0)
    parser.add_argument("--planar-command-limits", nargs=2, type=float, default=DEFAULT_PLANAR_LIMITS)
    parser.add_argument("--contact-force-off-threshold", type=float, default=0.01)
    parser.add_argument("--contact-force-on-threshold", type=float, default=0.08)
    parser.add_argument("--torque-tracking-gain", type=float, default=1.5)
    parser.add_argument("--slip-feedback-gain", type=float, default=8.0)
    parser.add_argument("--wheel-torque-limit", type=float, default=15.0)
    parser.add_argument("--slip-velocity-epsilon", type=float, default=0.1)
    parser.add_argument("--show-jacobian", action="store_true")
    parser.add_argument("--run-smoke-cases", action="store_true")
    return parser


def _format_vector(values: np.ndarray) -> str:
    return "[" + ", ".join(f"{float(value): .8f}" for value in values.tolist()) + "]"


def _format_matrix(values: np.ndarray) -> str:
    return "\n".join(_format_vector(row) for row in values)


def _resolve_joint_vector(rad_values, deg_values, name: str) -> np.ndarray | None:
    if rad_values is not None:
        return np.asarray(rad_values, dtype=np.float64)
    if deg_values is not None:
        return np.deg2rad(np.asarray(deg_values, dtype=np.float64))
    if name == "desired":
        return None
    raise ValueError("One of --ball-joint-pos or --ball-joint-pos-deg must be provided.")


def _run_smoke_cases(allocator: "NumpyWheelSpeedAllocator") -> None:
    q = np.zeros(6, dtype=np.float64)
    q_desired = np.zeros(6, dtype=np.float64)
    qdot_alloc = np.zeros(6, dtype=np.float64)
    planar_command = np.zeros(2, dtype=np.float64)
    full_contact = np.full(6, 1.0 / 6.0, dtype=np.float64)
    wheel_joint_vel = np.zeros(6, dtype=np.float64)
    rolling_speed_actual = np.zeros(6, dtype=np.float64)
    lateral_speed_actual = np.zeros(6, dtype=np.float64)

    zero_outputs = allocator.compute_low_slip_control_targets(
        ball_joint_pos=q,
        desired_ball_joint_pos=q_desired,
        ball_joint_rate_targets=qdot_alloc,
        desired_planar_command=planar_command,
        wheel_normal_contact_force=full_contact,
        wheel_joint_vel=wheel_joint_vel,
        rolling_speed_actual=rolling_speed_actual,
        lateral_speed_actual=lateral_speed_actual,
        q_lower_limits=DEFAULT_Q_LOWER_LIMITS,
        q_upper_limits=DEFAULT_Q_UPPER_LIMITS,
        lambda_tracking=1.0,
        lambda_lateral=5.0,
        planar_command_limits=DEFAULT_PLANAR_LIMITS,
        contact_force_off_threshold=0.01,
        contact_force_on_threshold=0.08,
        torque_tracking_gain=1.5,
        slip_feedback_gain=8.0,
        wheel_torque_limit=15.0,
        slip_velocity_epsilon=0.1,
    )
    np.testing.assert_allclose(zero_outputs.ball_joint_rate_targets, np.zeros(6), atol=1.0e-10)
    np.testing.assert_allclose(zero_outputs.ball_joint_position_targets, np.zeros(6), atol=1.0e-10)
    np.testing.assert_allclose(zero_outputs.shaped_planar_command, np.zeros(2), atol=1.0e-10)
    np.testing.assert_allclose(zero_outputs.wheel_speed_reference, np.zeros(6), atol=1.0e-10)

    forward_outputs = allocator.compute_low_slip_control_targets(
        ball_joint_pos=q,
        desired_ball_joint_pos=q_desired,
        ball_joint_rate_targets=qdot_alloc,
        desired_planar_command=np.array([1.0, 0.0], dtype=np.float64),
        wheel_normal_contact_force=full_contact,
        wheel_joint_vel=wheel_joint_vel,
        rolling_speed_actual=rolling_speed_actual,
        lateral_speed_actual=lateral_speed_actual,
        q_lower_limits=DEFAULT_Q_LOWER_LIMITS,
        q_upper_limits=DEFAULT_Q_UPPER_LIMITS,
        lambda_tracking=1.0,
        lambda_lateral=5.0,
        planar_command_limits=DEFAULT_PLANAR_LIMITS,
        contact_force_off_threshold=0.01,
        contact_force_on_threshold=0.08,
        torque_tracking_gain=1.5,
        slip_feedback_gain=8.0,
        wheel_torque_limit=15.0,
        slip_velocity_epsilon=0.1,
    )
    np.testing.assert_allclose(forward_outputs.shaped_planar_command, np.array([1.0, 0.0]), atol=1.0e-10)
    expected_forward_ref = np.full(6, 1.0 / allocator.geometry.r_wheel, dtype=np.float64)
    np.testing.assert_allclose(forward_outputs.wheel_speed_reference, expected_forward_ref, atol=1.0e-10)

    no_contact_outputs = allocator.compute_low_slip_control_targets(
        ball_joint_pos=q,
        desired_ball_joint_pos=q_desired,
        ball_joint_rate_targets=qdot_alloc,
        desired_planar_command=np.array([1.0, 0.0], dtype=np.float64),
        wheel_normal_contact_force=np.zeros(6, dtype=np.float64),
        wheel_joint_vel=wheel_joint_vel,
        rolling_speed_actual=rolling_speed_actual,
        lateral_speed_actual=lateral_speed_actual,
        q_lower_limits=DEFAULT_Q_LOWER_LIMITS,
        q_upper_limits=DEFAULT_Q_UPPER_LIMITS,
        lambda_tracking=1.0,
        lambda_lateral=5.0,
        planar_command_limits=DEFAULT_PLANAR_LIMITS,
        contact_force_off_threshold=0.01,
        contact_force_on_threshold=0.08,
        torque_tracking_gain=1.5,
        slip_feedback_gain=8.0,
        wheel_torque_limit=15.0,
        slip_velocity_epsilon=0.1,
    )
    np.testing.assert_allclose(no_contact_outputs.contact_weights, np.zeros(6), atol=1.0e-10)
    np.testing.assert_allclose(no_contact_outputs.wheel_torque_targets, np.zeros(6), atol=1.0e-10)

    traction_outputs = allocator.compute_wheel_traction_targets(
        wheel_speed_reference=np.full(6, 2.0, dtype=np.float64),
        wheel_joint_vel=np.full(6, 1.0, dtype=np.float64),
        rolling_speed_actual=np.full(6, 0.1, dtype=np.float64),
        lateral_speed_actual=np.zeros(6, dtype=np.float64),
        contact_weights=np.ones(6, dtype=np.float64),
        torque_tracking_gain=1.0,
        slip_feedback_gain=1.0,
        wheel_torque_limit=20.0,
        slip_velocity_epsilon=0.1,
    )
    np.testing.assert_allclose(traction_outputs.longitudinal_slip, np.full(6, -0.9), atol=1.0e-10)
    np.testing.assert_allclose(traction_outputs.wheel_torque_targets, np.full(6, 1.9), atol=1.0e-10)

    braking_outputs = allocator.compute_wheel_traction_targets(
        wheel_speed_reference=np.zeros(6, dtype=np.float64),
        wheel_joint_vel=np.full(6, 1.0, dtype=np.float64),
        rolling_speed_actual=np.full(6, 0.1, dtype=np.float64),
        lateral_speed_actual=np.zeros(6, dtype=np.float64),
        contact_weights=np.ones(6, dtype=np.float64),
        torque_tracking_gain=1.0,
        slip_feedback_gain=1.0,
        wheel_torque_limit=20.0,
        slip_velocity_epsilon=0.1,
    )
    np.testing.assert_allclose(braking_outputs.wheel_torque_targets, np.full(6, -0.1), atol=1.0e-10)

    target_test_qd = np.array([0.6, -1.0, 0.3, -0.6, 0.4, -0.3], dtype=np.float64)
    command_outputs = allocator.compute_ball_joint_command_outputs(
        target_test_qd,
        qdot_alloc,
        DEFAULT_Q_LOWER_LIMITS,
        DEFAULT_Q_UPPER_LIMITS,
    )
    np.testing.assert_allclose(
        command_outputs.ball_joint_position_targets,
        np.clip(target_test_qd, DEFAULT_Q_LOWER_LIMITS, DEFAULT_Q_UPPER_LIMITS),
        atol=1.0e-10,
    )

    print("Validation checks passed.")


def _run_manual_case(args: argparse.Namespace, allocator: "NumpyWheelSpeedAllocator") -> None:
    if args.planar_command is None:
        raise ValueError("--planar-command must be provided for a manual validation case.")

    q = _resolve_joint_vector(args.ball_joint_pos, args.ball_joint_pos_deg, name="current")
    q_desired = _resolve_joint_vector(args.ball_joint_desired, args.ball_joint_desired_deg, name="desired")
    if q_desired is None:
        q_desired = q.copy()
    qdot_alloc = np.asarray(args.ball_joint_rate_targets, dtype=np.float64)

    outputs = allocator.compute_low_slip_control_targets(
        ball_joint_pos=q,
        desired_ball_joint_pos=q_desired,
        ball_joint_rate_targets=qdot_alloc,
        desired_planar_command=np.asarray(args.planar_command, dtype=np.float64),
        wheel_normal_contact_force=np.asarray(args.wheel_normal_contact_force, dtype=np.float64),
        wheel_joint_vel=np.asarray(args.wheel_joint_vel, dtype=np.float64),
        rolling_speed_actual=np.asarray(args.rolling_speed_actual, dtype=np.float64),
        lateral_speed_actual=np.asarray(args.lateral_speed_actual, dtype=np.float64),
        q_lower_limits=np.asarray(args.ball_joint_lower_limits, dtype=np.float64),
        q_upper_limits=np.asarray(args.ball_joint_upper_limits, dtype=np.float64),
        lambda_tracking=float(args.lambda_tracking),
        lambda_lateral=float(args.lambda_lateral),
        planar_command_limits=np.asarray(args.planar_command_limits, dtype=np.float64),
        contact_force_off_threshold=float(args.contact_force_off_threshold),
        contact_force_on_threshold=float(args.contact_force_on_threshold),
        torque_tracking_gain=float(args.torque_tracking_gain),
        slip_feedback_gain=float(args.slip_feedback_gain),
        wheel_torque_limit=float(args.wheel_torque_limit),
        slip_velocity_epsilon=float(args.slip_velocity_epsilon),
    )

    print("Input ball-joint order:", allocator.geometry.ball_joint_names)
    print("Output wheel-joint order:", allocator.geometry.wheel_joint_names)
    print("q [rad]:", _format_vector(q))
    print("q [deg]:", _format_vector(np.rad2deg(q)))
    print("q^d [rad]:", _format_vector(q_desired))
    print("q^d [deg]:", _format_vector(np.rad2deg(q_desired)))
    print("u_v^d = [Vx, Wz]:", _format_vector(outputs.desired_planar_command))
    print("u_v*  = [Vx, Wz]:", _format_vector(outputs.shaped_planar_command))
    print("qdot_alloc [rad/s]:", _format_vector(outputs.ball_joint_rate_targets))
    print("q_target [rad]:", _format_vector(outputs.ball_joint_position_targets))
    print("q_target [deg]:", _format_vector(np.rad2deg(outputs.ball_joint_position_targets)))
    print("contact weights:", _format_vector(outputs.contact_weights))
    print("rolling-speed reference [m/s]:", _format_vector(outputs.rolling_speed_reference))
    print("wheel angular-speed reference [rad/s]:", _format_vector(outputs.wheel_speed_reference))
    print("lateral nominal velocity [m/s]:", _format_vector(outputs.lateral_velocity_nominal))
    print("longitudinal slip:", _format_vector(outputs.longitudinal_slip))
    print("wheel torque targets [N*m]:", _format_vector(outputs.wheel_torque_targets))
    print("lateral cost:", f"{float(outputs.lateral_cost):.8f}")
    if args.show_jacobian:
        print("J_w(q) [6x2]:")
        print(_format_matrix(outputs.wheel_speed_jacobian))
        print("J_q(q) [6x6]:")
        print(_format_matrix(outputs.posture_rate_jacobian))


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    allocator = NumpyWheelSpeedAllocator()
    if args.run_smoke_cases:
        _run_smoke_cases(allocator)
        return
    _run_manual_case(args, allocator)


if __name__ == "__main__":
    main()
