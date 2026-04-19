# RL阶段训练参数一览表

本文档记录当前 `RL_Training/` 工作区内 `CompleteCar-Stage0` 的**实际生效**训练环境配置。  
文档口径以当前源码为准；当前默认主线已经改为：

- `8m / 16s`
- `12` 维动作直驱
- `70 / 70` 观测
- PPO actor 使用 `tanh squashed Gaussian`
- 动作链路已取消 PPO wrapper / env 预处理中的前置 clip，只保留环境末端 safeguard
- 不使用速度分配模型

当前默认主线对应：

- 环境配置：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- 环境主类：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- 动作链路：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- 命令采样：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py`
- 观测构造：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- 奖励函数：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- 终止条件：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
- PPO 配置：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`

---

## 1. 环境总览

### 1.1 任务身份

- 任务名：`CompleteCar-Stage0`
- 环境类：`CompleteCarDirectEnv`
- 配置类：`CompleteCarStage0EnvCfg`
- PPO 配置类：`CompleteCarStage0PPORunnerCfg`
- 训练脚本：`scripts/train.py`

### 1.2 当前任务定义

当前 Stage0 是一个**平地、单目标、静态到点**任务：

- 地形：平面
- 每回合只采样一次目标
- 默认目标距离：`8.0 m`
- 目标方位相对当前车体偏航在 `[-30°, 30°]` 内采样
- 目标朝向相对 LOS 方向再叠加 `[-12°, 12°]` 的 heading offset
- policy 输出：
  - `6` 个球铰目标
  - `6` 个轮速直驱命令
- 当前执行层：
  - 直接把 wheel action 映射为轮速目标
  - 不再使用 measured-geometry allocator

### 1.3 关键维度

- 并行环境数：`64`
- 动作维度：`12`
- Actor 观测维度：`70`
- Critic 观测维度：`70`
- 仿真频率：`120 Hz`
- 控制频率：`60 Hz`
- 回合时长：`16 s`
- 最大控制步数：`960`
- PPO rollout：`240 steps / env`

---

## 2. 场景、机器人与仿真配置

### 2.1 机器人结构

- 三节车体：
  - `head_car`
  - `body_car`
  - `tail_car`
- 两个球铰模块：
  - `spm1_platform_joint_z / y / x`
  - `spm2_platform_joint_z / y / x`
- 六个轮子：
  - `body_car_wheel_left_joint`
  - `body_car_wheel_right_joint`
  - `head_car_wheel_left_joint`
  - `head_car_wheel_right_joint`
  - `tail_car_wheel_left_joint`
  - `tail_car_wheel_right_joint`

### 2.2 Scene / Simulation

- `scene.num_envs = 64`
- `scene.env_spacing = 4.0`
- `scene.replicate_physics = True`
- `scene.clone_in_fabric = True`

时间设置：

- `sim_dt = 1 / 120 s`
- `decimation = 2`
- `control_dt = 1 / 60 s`
- `episode_length_s = 16.0`

物理与材质：

- `gravity = (0, 0, -9.81)`
- `static_friction = 1.0`
- `dynamic_friction = 1.0`
- `restitution = 0.0`
- `solver_type = 1`
- `max_position_iteration_count = 8`
- `max_velocity_iteration_count = 4`

### 2.3 执行器参数

球铰执行器：

- `stiffness = 100.0`
- `damping = 20.0`
- `effort_limit_sim = 120.0`
- `velocity_limit_sim = 0.8 rad/s`

车轮执行器：

- `stiffness = 0.0`
- `damping = 1000.0`
- `effort_limit_sim = 80.0`
- `velocity_limit_sim = 12.0 rad/s`

---

## 3. 命令采样与任务几何

### 3.1 当前命令参数

- `num_commands = 3`
- `resampling_time = 16.0`
- `goal_distance = 8.0`
- `goal_direction_max_deg = 30.0`
- `goal_heading_delta_max_deg = 12.0`
- `zero_command = False`
- `rel_standing_envs = 0.0`

因为 `resampling_time = episode_length_s`，所以当前 Stage0 每回合只有一个静态目标。

### 3.2 目标采样公式

设当前底盘世界坐标为 `p_base = [x, y]`，当前偏航为 `yaw_base`：

```text
phi ~ U[-30°, 30°]
theta_los = yaw_base + phi
delta ~ U[-12°, 12°]
psi_target = theta_los + delta

x_target = x + 8.0 * cos(theta_los)
y_target = y + 8.0 * sin(theta_los)
```

### 3.3 相对目标命令

环境真正送入 observation 和 reward 的命令是车体系相对量：

```text
delta_xy_w = p_target - p_base
relative_xy_b = R_z(-yaw_base) * delta_xy_w
relative_yaw = wrap_to_pi(psi_target - yaw_base)

commands = [goal_rel_x, goal_rel_y, goal_rel_psi]
```

---

## 4. 动作空间与执行链路

### 4.1 动作空间

policy 输出 `12` 维动作：

- 前 `6` 维：球铰目标
- 后 `6` 维：轮速直驱命令

动作描述符：

```text
[
  ("ball_joint_targets", 6),
  ("wheel_velocity_targets", 6),
]
```

### 4.2 球铰动作映射

球铰动作采用“以默认位姿为中心的分段余量映射”：

```text
joint_target =
    default_target
  + clamp(a, 0, 1)  * (upper - default_target)
  + clamp(a, -1, 0) * (default_target - lower)
```

当前动作边界：

```text
lower = (-0.56, -1.30, -0.35, -0.56, -1.30, -0.35)
upper = ( 0.56,  0.40,  0.35,  0.56,  0.40,  0.35)
```

### 4.3 轮速直驱映射

设 policy 后六维动作是 `a_wheel ∈ [-1, 1]^6`。  
当前直接映射为：

```text
wheel_speed_target = a_wheel * wheel_action_scale * wheel_joint_velocity_limit_sim
```

当前参数：

- `wheel_action_scale = 1.0`
- `wheel_joint_velocity_limit_sim = 12.0 rad/s`

因此每个轮子的目标角速度范围是：

```text
[-12.0, 12.0] rad/s
```

### 4.4 当前执行链路

当前环境内部执行顺序：

```text
policy mean/std
-> Gaussian sample
-> tanh squash
-> ball joint target mapping
-> wheel velocity target mapping
-> final safeguard clip in env mapping
-> joint servo
```

当前 PPO / env 已经**不再经过**：

- wrapper action clip
- env preprocess action clip

当前**不再经过**：

- `base_planar_command`
- `transform_planar_command`
- `wheel allocator`

---

## 5. 当前速度分配模型状态

当前默认主线**不使用速度分配模型**。

也就是说：

- `TorchWheelSpeedAllocator`
- measured-geometry Jacobian
- traction-aware scaling

都不参与当前执行链路。

这些实现仍保留在代码库里作为历史分支能力，但当前 Stage0 默认训练时不会调用。

---

## 6. 当前观测空间

### 6.1 观测组成

当前 actor 观测按以下顺序拼接：

```text
base_lin_vel_b                3
base_ang_vel_b                3
projected_gravity_b           3
ball_joint_pos                6
ball_joint_vel                6
ball_joint_target_error       6
head_roll_pitch               2
tail_roll_pitch               2
wheel_joint_vel               6
wheel_longitudinal_slip       6
wheel_slip_angle              6
wheel_normal_contact_force    6
goal_relative_command         3
last_action                  12
--------------------------------
total                        70
```

因为 `terrain.measure_heights = False`，当前 critic 也没有额外高度 patch，所以仍为 `70` 维。

### 6.2 关键观测公式

纵滑率：

```text
v_x = wheel_body_lin_vel · wheel_forward_axis
v_surface = r_wheel * wheel_joint_vel
safe_speed = max(|v_x|, slip_epsilon)

wheel_longitudinal_slip = (v_x - v_surface) / safe_speed
wheel_longitudinal_slip = clip(wheel_longitudinal_slip, -3.0, 3.0)
```

侧滑角：

```text
v_y = wheel_body_lin_vel · wheel_lateral_axis
wheel_slip_angle = atan2(v_y, |v_x| + slip_epsilon)
```

轮法向接触力：

```text
wheel_normal_contact_force = ||wheel_contact_forces_w|| / total_vehicle_weight
```

球铰目标误差：

```text
ball_joint_target_error = wrap_to_pi(ball_joint_target - ball_joint_pos)
```

### 6.3 观测 scale / noise

当前 Stage0 统一采用 `1.0` 量级 scale：

- `base_lin_vel = 1.0`
- `base_ang_vel = 1.0`
- `projected_gravity = 1.0`
- `ball_joint_pos = 1.0`
- `ball_joint_vel = 1.0`
- `ball_joint_target_error = 1.0`
- `module_roll_pitch = 1.0`
- `wheel_joint_vel = 1.0`
- `wheel_longitudinal_slip = 1.0`
- `wheel_slip_angle = 1.0`
- `wheel_normal_contact_force = 1.0`
- `commands = 1.0`
- `last_action = 1.0`

噪声：

- `observations.noise.enabled = False`

---

## 7. 当前奖励函数

### 7.1 当前 reward 总式

当前 reward 形式为：

```text
total_reward =
    distance_progress
  + goal_direction_reward
  + goal_heading_reward
  + stop_reward
  + success_bonus
  - time_penalty
```

### 7.2 各奖励项公式

目标到达判定：

```text
goal_reached =
    (goal_distance_now < 0.5)
  & (|goal_yaw_error| < 15°)
```

distance progress：

```text
distance_progress = (previous_goal_distance - current_goal_distance) / control_dt
```

near-goal gate：

```text
near_goal_gate = sigmoid(4.0 * (2.1 - current_goal_distance))
stop_gate = sigmoid(4.0 * (0.8 - current_goal_distance))
```

goal direction reward：

```text
goal_direction_reward =
    0.012 * exp(-abs(goal_direction_error) / 1.2)
```

goal heading reward：

```text
goal_heading_reward =
    0.06 * near_goal_gate * exp(-abs(goal_yaw_error) / 0.8)
```

stop reward：

```text
planar_speed_sq = vx^2 + vy^2
stop_reward =
    0.004 * stop_gate * exp(-planar_speed_sq / (1.2^2))
```

success bonus：

```text
success_bonus = goal_reached * 45.0
```

time penalty：

```text
time_penalty = 0.02
```

### 7.3 当前 reward 参数

- `target_position_tolerance = 0.5`
- `target_yaw_tolerance_deg = 15.0`
- `goal_direction_reward_weight = 0.012`
- `goal_direction_error_scale = 1.2`
- `goal_heading_reward_weight = 0.06`
- `goal_heading_error_scale = 0.8`
- `near_goal_gate_distance = 2.1`
- `near_goal_gate_sharpness = 4.0`
- `stop_gate_distance = 0.8`
- `stop_reward_weight = 0.004`
- `stop_speed_squared_scale = 1.2`
- `success_bonus = 45.0`
- `time_penalty = 0.02`
- `only_positive_rewards = False`

### 7.4 当前 reward 不包含的项

当前主线不包含：

- `gated_progress`
- `composite_gate`
- `roll_gate`
- `longitudinal_slip_cost_penalty`
- `pose_reward / capture_reward / arrival_* gate`

---

## 8. 当前终止条件

当前 done term 为：

- `bad_orientation`
- `head_tail_roll_out_of_bounds`
- `ball_joint_out_of_bounds`
- `time_out`

对应公式：

```text
bad_orientation = |middle_roll| > 30°
head_tail_roll_out_of_bounds =
    (|head_roll| > 35°) or (|tail_roll| > 35°)
ball_joint_out_of_bounds =
    any(ball_joint_pos < lower_limit or ball_joint_pos > upper_limit)
time_out = episode_length_buf >= max_episode_length - 1
```

当前球铰终止边界：

```text
lower = (-0.6, -1.0, -0.5, -0.6, -1.0, -0.5)
upper = ( 0.6,  0.4,  0.5,  0.6,  0.4,  0.5)
```

---

## 9. Reset、地形与传感器

### 9.1 Reset

- `root_pos = (0.0, 0.0, 0.30)`
- `root_lin_vel = (0.0, 0.0, 0.0)`
- `root_ang_vel = (0.0, 0.0, 0.0)`
- `root_x_range = (-1.0, 1.0)`
- `root_y_range = (-1.0, 1.0)`
- `root_yaw_range = (0, 0)`
- 球铰和轮速初值扰动范围均为 `0`

### 9.2 Terrain

- `terrain.enabled = False`
- `terrain.mode = "plane"`
- `measure_heights = False`

### 9.3 Sensors

- `imu.enabled = False`
- `stereo_camera.enabled = False`
- `lidar.enabled = False`
- `enable_height_scanner = False`

轮接触力仍会通过 runtime 接触重建路径进入 observation 和诊断。

---

## 10. PPO 配置

Runner：

- `seed = 1`
- `num_steps_per_env = 512`
- `max_iterations = 700`
- `save_interval = 100`
- `clip_actions = None`
- `experiment_name = "complete_car_stage0"`

Actor / Critic：

- MLP hidden dims：`[256, 256]`
- activation：`relu`
- `obs_normalization = True`
- actor distribution：`SquashedGaussianDistribution`
- actor 初始 std：`0.20`
- `log_std_min = -4.0`
- `log_std_max = 0.0`

PPO：

- `value_loss_coef = 0.5`
- `use_clipped_value_loss = True`
- `clip_param = 0.2`
- `entropy_coef = 5e-4`
- `num_learning_epochs = 5`
- `num_mini_batches = 16`
- `learning_rate = 1e-4`
- `adam_eps = 1e-5`
- `schedule = "adaptive"`
- `gamma = 0.99`
- `lam = 0.95`
- `desired_kl = 0.008`
- `max_grad_norm = 0.5`

---

## 11. 当前主线解释

当前默认 Stage0 的核心变化不是调了几个数值，而是：

- 动作语义从高层底盘命令改成了直接轮速命令
- 执行层不再经过 allocator
- 策略分布从无界 Gaussian 改成了 `tanh squashed Gaussian`
- PPO wrapper 与 env 预处理中的前置动作 clip 已移除
- 因为 `last_action` 维度变了，观测也同步从 `66 / 66` 变成了 `70 / 70`

因此这版环境和之前的 `8动作 allocator` 主线已经不是同口径实验。  
后续所有训练结论都应按这条新主线解释。
