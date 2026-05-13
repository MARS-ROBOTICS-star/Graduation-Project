"""Complete-car actuator definitions."""

from __future__ import annotations

from isaaclab.actuators import ImplicitActuatorCfg


def build_complete_car_actuators_cfg(control_cfg) -> dict[str, ImplicitActuatorCfg]:
    """根据 ControlCfg 构造球铰与车轮的执行器配置。"""

    return {
        "ball_joints": ImplicitActuatorCfg(
            joint_names_expr=list(control_cfg.ball_joint_names),
            effort_limit_sim=control_cfg.ball_joint_effort_limit_sim,
            velocity_limit_sim=control_cfg.ball_joint_velocity_limit_sim,
            stiffness=control_cfg.ball_joint_stiffness,
            damping=control_cfg.ball_joint_damping,
        ),
        "wheel_joints": ImplicitActuatorCfg(
            joint_names_expr=list(control_cfg.wheel_joint_names),
            effort_limit_sim=control_cfg.wheel_joint_effort_limit_sim,
            velocity_limit_sim=control_cfg.wheel_joint_velocity_limit_sim,
            stiffness=control_cfg.wheel_joint_stiffness,
            damping=control_cfg.wheel_joint_damping,
        ),
    }
