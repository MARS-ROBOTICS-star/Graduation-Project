"""Complete-car direct env 的共享基础配置主干。"""

from __future__ import annotations

import math
from dataclasses import field

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnvCfg, ViewerCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass
from isaaclab.utils.noise import GaussianNoiseCfg, NoiseModelCfg, NoiseModelWithAdditiveBiasCfg

from ..assets.robot_cfg import BALL_JOINT_NAMES, WHEEL_JOINT_NAMES, WHEEL_RADIUS, build_complete_car_robot_cfg
from ..mdp.observations import PerComponentUniformNoiseCfg
from ..sensors.sensor_cfg import CompleteCarSensorSuiteCfg
from ..terrain.terrain_cfg import CompleteCarTerrainRuntimeCfg
from ..utils.io_descriptors import build_action_descriptor, build_observation_descriptor, build_state_descriptor, total_dim
from ..utils.math_utils import compute_policy_obs_noise_magnitudes


@configclass
class CommandCfg:
    """目标位姿命令采样器配置。"""

    num_commands: int = 4
    num_waypoints_per_episode: int = 1
    resampling_time: float = 5.0  # 目标重采样周期，单位：s。
    goal_distance: float = 20
    goal_direction_max_deg: float = 18.43
    min_segment_turn_deg: float = 0.0
    goal_heading_delta_max_deg: float = 9.215
    zero_command: bool = False  # 为 True 时，本次采样出的目标会退化为当前位置和当前朝向。
    rel_standing_envs: float = 0.0  # 每次重采样后，被随机指定为原地目标环境的比例。


@configclass
class ControlCfg:
    """动作语义和驱动参数。"""

    sim_dt: float = 1.0 / 120.0  # 仿真底层步长，单位：s。
    decimation: int = 2  # 每执行多少个 sim step 才更新一次 RL 控制。
    control_dt: float = 1.0 / 60.0  # 控制周期，单位：s。

    ball_joint_names: tuple[str, ...] = tuple(BALL_JOINT_NAMES)
    wheel_joint_names: tuple[str, ...] = tuple(WHEEL_JOINT_NAMES)
    ball_joint_planner_gains: tuple[float, ...] = (8.0, 8.0, 8.0, 8.0, 8.0, 8.0)
    ball_joint_planner_qdot_limits: tuple[float, ...] = (1.5, 1.5, 1.5, 1.5, 1.5, 1.5)
    ball_joint_planner_qddot_limits: tuple[float, ...] = (12.0, 12.0, 12.0, 12.0, 12.0, 12.0)
    ball_joint_planner_track_error_limit: float = 0.10
    base_forward_velocity_max: float = 1.2  # 中模块期望纵向速度上限，单位：m/s。
    base_yaw_rate_max: float = 0.6  # 中模块期望偏航角速度上限，单位：rad/s。
    base_allow_reverse: bool = False  # 为 False 时，高层只输出前进命令，不输出倒车命令。
    ball_joint_stiffness: float = 1000.0  # 球铰位置控制刚度，单位：N*m/rad。
    ball_joint_damping: float = 10.0  # 球铰位置控制阻尼，单位：N*m*s/rad。
    ball_joint_effort_limit_sim: float = 20.0  # 球铰驱动器力矩上限，单位：N*m。
    ball_joint_velocity_limit_sim: float = 2.0  # 球铰驱动器速度上限，单位：rad/s。

    wheel_joint_stiffness: float = 0.0  # 车轮位置刚度，单位：N*m/rad。
    wheel_joint_damping: float = 0.0  # 车轮速度驱动阻尼；速度目标模式下必须为非零才会产生 drive 力矩。
    wheel_joint_effort_limit_sim: float = 20.0  # 车轮驱动器力矩上限，单位：N*m。
    wheel_joint_velocity_limit_sim: float = 20.0  # 车轮驱动器速度上限，单位：rad/s。
    wheel_radius: float = WHEEL_RADIUS
    low_slip_lambda_tracking: float = 1.0
    low_slip_lambda_lateral: float = 5.0
    contact_force_off_threshold: float = 0.01
    contact_force_on_threshold: float = 0.08
    wheel_torque_tracking_gain: float = 2.0
    wheel_slip_feedback_gain: float = 4.0
    wheel_slip_velocity_epsilon: float = 0.1


@configclass
class ObservationScalesCfg:
    """各观测分量的缩放。"""

    base_lin_vel: float = 1.0
    base_ang_vel: float = 0.25
    projected_gravity: float = 1.0
    ball_joint_pos: float = 1.0
    ball_joint_vel: float = 0.05
    ball_joint_target_error: float =1.0
    module_roll_pitch: float =1.0
    wheel_joint_vel: float =0.05
    wheel_longitudinal_slip: float = 1.0
    wheel_slip_angle: float = 1.0
    wheel_normal_contact_force: float = 1.0
    commands: float = 1.0
    last_action: float = 1.0


@configclass
class ObservationNoiseCfg:
    """观测噪声幅值。"""

    enabled: bool = False
    level: float = 1.0
    base_lin_vel: float = 0.1
    base_ang_vel: float = 0.2
    projected_gravity: float = 0.02
    ball_joint_pos: float = 0.01
    ball_joint_vel: float = 0.05
    ball_joint_target_error: float =0.01
    module_roll_pitch: float =0.02
    wheel_joint_vel: float =0.05
    wheel_longitudinal_slip: float = 0.0
    wheel_slip_angle: float = 0.0
    wheel_normal_contact_force: float = 0.0
    commands: float = 0.0


@configclass
class ObservationCfg:
    """观测拼接与裁剪配置。"""

    use_history: bool = False
    history_length: int = 1
    clip_observations: float = 100.0
    wheel_slip_epsilon: float = 0.1
    wheel_slip_angle_clip_rad: float = math.pi / 2.0
    scales: ObservationScalesCfg = ObservationScalesCfg()
    noise: ObservationNoiseCfg = ObservationNoiseCfg()


@configclass
class RewardParamsCfg:
    """目标导向奖励参数。"""

    target_position_tolerance: float = 0.2
    target_yaw_tolerance_deg: float = math.degrees(0.1)
    distance_to_target_denominator_scale: float = 0.11
    distance_to_target_weight: float = 5.0
    progress_to_target_clip_m: float = 0.25
    progress_to_target_relax_radius_m: float = 0.0
    progress_to_target_weight: float = 0.0
    reached_target_base_reward: float = 2.0
    reached_target_weight: float = 5.0
    far_from_target_margin: float = 3.0
    far_from_target_weight: float = -2.0
    timeout_fixed_penalty: float = 12.0
    timeout_distance_penalty_scale: float = 0.5
    angle_diff_weight: float = 5.0
    action_rate_base_weight: float = 0.05
    action_rate_joint_weight: float = 0.02
    load_equalization_weight: float = 0.0
    load_equalization_k: float = 10.0
    load_equalization_target_shares: tuple[float, ...] = (1.0 / 6.0,) * 6
    progress_gate_longitudinal_k: float = 3.0
    progress_gate_slip_angle_scale_rad: float = 1.5
    progress_gate_min_multiplier: float = 0.10
    progress_gate_max_multiplier: float = 1.5
    low_slip_longitudinal_threshold: float = 1.0
    low_slip_angle_threshold_rad: float = 0.35


@configclass
class RewardCfg:
    """奖励核参数。"""

    params: RewardParamsCfg = RewardParamsCfg()
    only_positive_rewards: bool = False


@configclass
class TerminationCfg:
    """终止条件阈值。"""

    orientation_limit_deg: float = 45.0 #整车最大侧倾角
    head_tail_roll_limit_deg: float = 35.0
    head_tail_pitch_limit_deg: float = 20.0
    ball_joint_pos_lower_limits: tuple[float, ...] = (-0.7, -1.6, -0.5, -0.7, -1.6, -0.5)#球铰yaw,pitch,roll的限制
    ball_joint_pos_upper_limits: tuple[float, ...] = (0.7, 0.5, 0.5, 0.7, 0.5, 0.5)


@configclass
class ResetCfg:
    """reset 初值与扰动范围。"""

    root_pos: tuple[float, float, float] = (0.0, 0.0, 0.30)
    root_lin_vel: tuple[float, float, float] = (0.0, 0.0, 0.0)
    root_ang_vel: tuple[float, float, float] = (0.0, 0.0, 0.0)
    root_x_range: tuple[float, float] = (-1.0, 1.0)
    root_y_range: tuple[float, float] = (-1.0, 1.0)
    root_yaw_range: tuple[float, float] = (0.0 * math.pi, 0.0 * math.pi)

    default_ball_joint_angles: dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in BALL_JOINT_NAMES})
    default_wheel_joint_pos: dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in WHEEL_JOINT_NAMES})
    default_ball_joint_vel: dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in BALL_JOINT_NAMES})
    default_wheel_joint_vel: dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in WHEEL_JOINT_NAMES})

    ball_joint_pos_range: tuple[float, float] = (0.0, 0.0)
    ball_joint_vel_range: tuple[float, float] = (0.0, 0.0)
    wheel_joint_pos_range: tuple[float, float] = (0.0, 0.0)
    wheel_joint_vel_range: tuple[float, float] = (0.0, 0.0)


@configclass
class RandomizationCfg:
    """域随机化配置。"""

    enable_action_randomization: bool = False
    joint_position_noise_scale: float = 0.0
    action_noise_std: float = 0.0
    action_bias_std: float = 0.0


@configclass
class CurriculumCfg:
    """地形课程学习参数。"""

    enabled: bool = False
    max_init_terrain_level: int = 0
    default_terrain_name: str = "slope down"
    move_up_distance_ratio: float = 0.5
    move_down_command_ratio: float = 0.5


@configclass
class TerrainBindingCfg(CompleteCarTerrainRuntimeCfg):
    """terrain runtime 绑定配置。"""


@configclass
class SensorBindingCfg(CompleteCarSensorSuiteCfg):
    """sensor suite 绑定配置。"""


@configclass
class DebugCfg:
    """调试辅助配置。"""

    enable_debug_draw: bool = False
    visualize_wheel_slip: bool = False
    create_follow_views: bool = False
    follow_view_top_height: float = 2.5
    follow_view_chase_env_index: int = 0
    follow_view_chase_offset_b: tuple[float, float, float] = (-4.0, -3.0, 2.4)
    follow_view_chase_target_offset_b: tuple[float, float, float] = (1.0, 0.0, 0.4)
    log_sensor_outputs: bool = True


@configclass
class SceneCfg(InteractiveSceneCfg):
    """场景克隆配置。"""

    num_envs: int = 64
    env_spacing: float = 4.0 #不同环境之间的间距 m
    replicate_physics: bool = True
    clone_in_fabric: bool = True


@configclass
class CompleteCarEnvCfg(DirectRLEnvCfg):
    """总装配配置类，所有阶段都从这里派生。"""

    stage_name: str = "stage0"
    episode_length_s: float = 16.0 #control_dt = 1/60 s 理论最大控制步数：16 × 60 = 960 步
    action_space: int = 2 + len(BALL_JOINT_NAMES)
    observation_space: dict[str, int] | int = 0
    state_space: int = 0 #critic state 或 privileged state 的维度
    decimation: int = 2

    sim: sim_utils.SimulationCfg = sim_utils.SimulationCfg()
    viewer: ViewerCfg = ViewerCfg(eye=(-53.885, 43.696, 64.903), lookat=(-53.054, 43.698, 64.346))
    scene: SceneCfg = SceneCfg()
    robot: ArticulationCfg = build_complete_car_robot_cfg()

    commands: CommandCfg = CommandCfg()
    control: ControlCfg = ControlCfg()
    observations: ObservationCfg = ObservationCfg()
    rewards: RewardCfg = RewardCfg()
    terminations: TerminationCfg = TerminationCfg()
    resets: ResetCfg = ResetCfg()
    randomization: RandomizationCfg = RandomizationCfg()
    curriculum: CurriculumCfg = CurriculumCfg()
    terrain: TerrainBindingCfg = TerrainBindingCfg()
    sensors: SensorBindingCfg = SensorBindingCfg()
    debug: DebugCfg = DebugCfg()

    def _build_action_noise_model_cfg(self) -> NoiseModelWithAdditiveBiasCfg | None:
        if not self.randomization.enable_action_randomization:
            return None
        if self.randomization.action_noise_std <= 0.0 and self.randomization.action_bias_std <= 0.0:
            return None
        return NoiseModelWithAdditiveBiasCfg(
            noise_cfg=GaussianNoiseCfg(mean=0.0, std=self.randomization.action_noise_std, operation="add"),
            bias_noise_cfg=GaussianNoiseCfg(mean=0.0, std=self.randomization.action_bias_std, operation="abs"),
        )

    def _build_observation_noise_model_cfg(self) -> NoiseModelCfg | None:
        if not self.observations.noise.enabled or self.observations.noise.level <= 0.0:
            return None

        magnitudes = compute_policy_obs_noise_magnitudes(self)
        if self.observations.use_history and self.observations.history_length > 1:
            magnitudes = magnitudes * self.observations.history_length
        if not any(magnitude > 0.0 for magnitude in magnitudes):
            return None

        return NoiseModelCfg(
            noise_cfg=PerComponentUniformNoiseCfg(
                n_min=tuple(-magnitude for magnitude in magnitudes),
                n_max=tuple(magnitude for magnitude in magnitudes),
                operation="add",
            )
        )

    def __post_init__(self) -> None:
        super().__post_init__()

        self.control.control_dt = self.control.sim_dt * self.control.decimation
        self.decimation = self.control.decimation

        self.action_space = total_dim(build_action_descriptor(self))
        base_obs_dim = total_dim(build_observation_descriptor(self))
        actor_obs_dim = (
            base_obs_dim * self.observations.history_length
            if self.observations.use_history and self.observations.history_length > 1
            else base_obs_dim
        )
        critic_obs_dim = actor_obs_dim + (self.terrain.get_num_height_points() if self.terrain.measure_heights else 0)
        self.observation_space = {
            "actor": actor_obs_dim,
            "critic": critic_obs_dim,
        }
        self.state_space = total_dim(build_state_descriptor(self))

        self.action_noise_model = self._build_action_noise_model_cfg()
        self.observation_noise_model = self._build_observation_noise_model_cfg()

        self.sim.dt = self.control.sim_dt
        self.sim.render_interval = self.decimation
        self.sim.gravity = (0.0, 0.0, -9.81)
        self.sim.use_fabric = True
        self.sim.physics_material.static_friction = self.terrain.static_friction
        self.sim.physics_material.dynamic_friction = self.terrain.dynamic_friction
        self.sim.physics_material.restitution = self.terrain.restitution
        self.sim.physx.solver_type = 1
        self.sim.physx.max_position_iteration_count = 8
        self.sim.physx.max_velocity_iteration_count = 0
        self.sim.physx.bounce_threshold_velocity = 0.2
        self.sim.physx.friction_offset_threshold = 0.04
        self.sim.physx.friction_correlation_distance = 0.025
        self.sim.physx.enable_stabilization = True

        # 机器人配置在 __post_init__ 统一重建，避免 stage 覆写后出现旧 actuator 残留。
        self.robot = build_complete_car_robot_cfg(self.control, self.resets)
