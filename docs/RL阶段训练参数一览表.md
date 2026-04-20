# RL阶段训练参数一览表

本文档记录当前 `RL_Training/` 工作区内 `CompleteCar-Stage0` 的实际生效配置。  
口径以当前源码为准，不再沿用历史 run、旧 reward 结构或旧 termination 设计。

当前主线对应源码：

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
- 训练脚本：`RL_Training/scripts/train.py`

### 1.2 当前任务定义

当前 Stage0 是一个平地上的目标跟踪 baseline：

- 地形：平面
- episode 时长：`20.0 s`
- 目标重采样周期：`20.0 s`
- 默认目标距离：`8.0 m`
- 目标方位相对当前车体偏航在 `[-30°, 30°]` 采样
- 目标朝向相对 LOS 再叠加 `[-12°, 12°]` 的 heading offset
- policy 输出是 `8` 维统一高层动作：
  - `2` 维中模块期望平面运动命令分支
  - `6` 维球铰期望构型分支

注意：

- 当前 `Stage0` 是“单回合单目标静态任务”。
- 因为 `episode_length_s = 20.0` 且 `commands.resampling_time = 20.0`，所以一个 episode 内不会中途重采样目标。

### 1.3 关键维度

- 并行环境数：`64`
- 动作维度：`8`
- Actor 观测维度：`18`
- Critic 观测维度：`18`
- 仿真频率：`120 Hz`
- 控制频率：`60 Hz`
- 回合时长：`20.0 s`
- 最大控制步数：`1200`
- PPO rollout：`512 steps / env`

---

## 2. 场景、机器人与仿真配置

### 2.1 场景与仿真

- `scene.num_envs = 64`
- `scene.env_spacing = 4.0`
- `scene.replicate_physics = True`
- `scene.clone_in_fabric = True`

时间设置：

- `sim_dt = 1 / 120 s`
- `decimation = 2`
- `control_dt = 1 / 60 s`
- `episode_length_s = 20.0`

物理与材质：

- `gravity = (0, 0, -9.81)`
- `static_friction = 1.0`
- `dynamic_friction = 1.0`
- `restitution = 0.0`
- `solver_type = 1`
- `max_position_iteration_count = 8`
- `max_velocity_iteration_count = 4`
- `enable_stabilization = True`
- `enable_external_forces_every_iteration = True`

### 2.2 执行器参数

球铰执行器：

- `stiffness = 8000.0`
- `damping = 1000.0`
- `effort_limit_sim = 20.0`
- `velocity_limit_sim = 0.8 rad/s`

车轮执行器：

- `stiffness = 0.0`
- `damping = 4000.0`
- `effort_limit_sim = 20.0`
- `velocity_limit_sim = 20.0 rad/s`

### 2.3 当前球铰控制策略

当前主线已恢复球铰期望构型输出：

- policy 后 `6` 维输出对应：
  - `q^d = [\psi_f^d, \theta_f^d, \phi_f^d, \psi_r^d, \theta_r^d, \phi_r^d]`
- 环境内部将归一化动作按球铰上下限映射为物理关节位置目标
- 写入执行器的是：
  - `q^{cmd} = q^d`
- 轮速分配器使用的是当前实际构型 `q`，不是 `q^d`

---

## 3. 命令采样与任务几何

### 3.1 当前命令参数

- `num_commands = 4`
- `resampling_time = 20.0`
- `goal_distance = 8.0`
- `goal_direction_max_deg = 30.0`
- `goal_heading_delta_max_deg = 12.0`
- `zero_command = False`
- `rel_standing_envs = 0.0`

### 3.2 命令语义

当前命令向量为：

```text
commands = [goal_rel_x, goal_rel_y, goal_rel_z, goal_rel_heading]
```

世界系目标存储为：

```text
command_targets_w = [goal_target_x_world, goal_target_y_world, goal_target_z_world, goal_target_heading_world]
```

目标点先在世界系采样 `xy`，然后：

- 平地模式下，`goal_target_z_world = 0`
- 若后续启用地形生成，则通过 `terrain_runtime.sample_heights_world_xy(...)` 查询目标点高度

### 3.3 相对目标命令

环境真正送入观测和 reward 的是车体系相对量：

```text
relative_xy_b = R_z(-yaw_base) * (target_xy_w - base_xy_w)
relative_z = target_z_w - base_z_w
relative_heading = wrap_to_pi(target_heading_w - base_yaw_w)
```

---

## 4. 动作空间与执行链路

### 4.1 动作空间

动作描述符为：

```text
[
  ("base_planar_command", 2),
  ("ball_joint_targets", 6),
]
```

### 4.2 平面运动命令分支

前 `2` 维动作先映射为中模块期望平面运动命令：

```text
u_v = [V_x^d, Ω_z^d]
```

当前参数：

- `base_forward_velocity_max = 2.0 m/s`
- `base_yaw_rate_max = 2.0 rad/s`
- `base_allow_reverse = True

因此：

- 第 `1` 维动作映射到 `[-2.0, 2.0] m/s` 的前向速度命令
- 第 `2` 维动作映射到 `[-2.0, 2.0] rad/s` 的偏航角速度命令

### 4.3 球铰目标映射

后 `6` 维动作映射为球铰期望构型：

```text
q^{cmd} = q^d
```

映射方式是：

- 以默认复位姿态为中心
- 正半轴动作沿上限方向张开
- 负半轴动作沿下限方向张开

### 4.4 轮速解析分配

环境内部不再让 policy 直接输出六轮轮速，而是调用：

```text
wheel_speed_allocator.py
```

按照论文第 3 章当前模型执行：

```text
(u_v, q, P) -> Ω^d
```

其中：

- `u_v = [V_x^d, Ω_z^d]^T`
- `q` 是当前实际球铰构型
- `P` 是固定结构参数集合

allocator 当前实现为论文一致的：

- `J_w(q) ∈ R^{6×2}`
- `Ω^d = J_w(q) u_v`

### 4.5 当前执行链路

```text
policy mean/std
-> Gaussian sample
-> tanh squash
-> split into [base_planar_command, ball_joint_targets]
-> base command mapping to [V_x^d, Ω_z^d]
-> ball-joint target mapping to q^d
-> wheel allocator computes Ω^d = J_w(q) u_v
-> final safeguard clip in env mapping
-> joint servo
```

球铰执行器跟踪的是 `q^{cmd}`，车轮执行器跟踪的是 `Ω^d`。

---

## 5. 当前观测空间

### 5.1 观测组成

当前 actor 观测按以下顺序拼接：

```text
wheel_joint_vel               6
goal_relative_command         4
last_action                   8
--------------------------------
total                        18
```

因为 `terrain.measure_heights = False`，当前 critic 不额外追加地形 patch，所以也是 `18` 维。

当前送入 actor / critic 的观测只保留三类：

- `wheel_joint_vel`
- `goal_relative_command`
- `last_action`

其余状态量例如：

- `base_lin_vel`
- `base_ang_vel`
- `projected_gravity`
- `ball_joint_pos / vel / target_error`
- `head_roll_pitch / tail_roll_pitch`
- `wheel_longitudinal_slip`
- `wheel_slip_angle`
- `wheel_normal_contact_force`

都不再送入网络，但仍然保留在 step metrics / TensorBoard 中用于行为诊断。

### 5.2 关键观测公式

纵滑率：

```text
v_x = wheel_body_lin_vel · wheel_forward_axis
v_surface = wheel_radius * wheel_joint_vel
safe_speed = max(|v_x|, slip_epsilon)
wheel_longitudinal_slip = clip((v_x - v_surface) / safe_speed, -3.0, 3.0)
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

### 5.3 观测 scale 与噪声

当前真正参与网络输入的 observation scale 为：

- `wheel_joint_vel = 1.0`
- `commands = 1.0`
- `last_action = 1.0`

噪声设置：

- `observations.noise.enabled = False`

虽然配置里仍保留了更完整的噪声字段，但当前主线训练既没有开启 observation noise，也不会把那些被移出 policy 输入的量送入网络。

---

## 6. 当前奖励函数

### 6.1 reward 总式

```text
total_reward =
    distance_to_target
  + reached_target
  + oscillation
  + angle_to_target
  + far_from_target
  + angle_diff
```

### 6.2 各奖励项

到达判定：

```text
reached_target_mask =
    (distance_to_goal < 0.2)
  and (|goal_heading_error| < 0.1 rad)
```

距离项：

```text
distance_to_target =
    distance_to_target_weight
    * [1 / (1 + 0.11 * distance^2)]
    / max_episode_length
```

到达奖励：

```text
reward_scale = (max_episode_length - episode_length_buf) / max_episode_length
reached_target =
    reached_target_weight
    * reached_target_base_reward
    * reward_scale
    * reached_target_mask
```

动作振荡惩罚：

```text
oscillation =
    oscillation_weight
    * mean(|action_t - action_t-1|^4)
    / max_episode_length
```

目标方向惩罚：

```text
angle_to_target = atan2(goal_rel_y, goal_rel_x)
angle_to_target_penalty =
    angle_to_target_weight
    * where(|angle_to_target| > 2.0, |angle_to_target| / max_episode_length, 0)
```

远离目标惩罚：

```text
far_from_target_threshold = cfg.commands.goal_distance + 3.0
far_from_target =
    far_from_target_weight
    * 1.0(distance > far_from_target_threshold)
```

距离-朝向耦合项：

```text
angle_diff =
    angle_diff_weight
    * [1 / (1 + distance)]
    * [1 / (1 + |goal_heading_error|)]
    / max_episode_length
```

### 6.3 当前 reward 参数

- `target_position_tolerance = 0.2`
- `target_yaw_tolerance_deg = degrees(0.1) ≈ 5.73`
- `distance_to_target_denominator_scale = 0.11`
- `distance_to_target_weight = 5.0`
- `reached_target_base_reward = 2.0`
- `reached_target_weight = 5.0`
- `oscillation_weight = -0.05`
- `angle_to_target_threshold_rad = 2.0`
- `angle_to_target_weight = -1.5`
- `far_from_target_margin = 3.0`
- `far_from_target_weight = -2.0`
- `angle_diff_weight = 5.0`
- `only_positive_rewards = False`

当前主线不包含：

- `distance_progress`
- `goal_direction_reward`
- `goal_heading_reward`
- `stop_reward`
- `success_bonus`
- `time_penalty`
- allocator 相关 reward

---

## 7. 当前终止条件

当前 done term 为：

- `is_success`
- `far_from_target`
- `ball_joint_out_of_bounds`
- `time_out`

对应逻辑：

```text
time_out =
    episode_length_buf >= max_episode_length - 1

is_success =
    (distance_to_goal < 0.2 m)
    and (|goal_heading_error| < 0.1 rad)

far_from_target =
    distance_to_goal > (cfg.commands.goal_distance + 3.0)

ball_joint_out_of_bounds =
    any(ball_joint_pos < lower_limit or ball_joint_pos > upper_limit)
```

当前球铰终止边界：

```text
lower = (-0.6, -1.0, -0.5, -0.6, -1.0, -0.5)
upper = ( 0.6,  0.4,  0.5,  0.6,  0.4,  0.5)
```

注意：

- 旧的姿态类硬终止已不在当前主线的 active done path 中：
  - `bad_orientation`
  - `head_tail_roll_out_of_bounds`

---

## 8. Reset、地形与传感器

### 8.1 Reset

- `root_pos = (0.0, 0.0, 0.30)`
- `root_lin_vel = (0.0, 0.0, 0.0)`
- `root_ang_vel = (0.0, 0.0, 0.0)`
- `root_x_range = (-1.0, 1.0)`
- `root_y_range = (-1.0, 1.0)`
- `root_yaw_range = (0, 0)`
- `ball_joint_pos_range = (0.0, 0.0)`
- `ball_joint_vel_range = (0.0, 0.0)`
- `wheel_joint_pos_range = (0.0, 0.0)`
- `wheel_joint_vel_range = (0.0, 0.0)`

### 8.2 Terrain

- `terrain.enabled = False`
- `terrain.mode = "plane"`
- `terrain.measure_heights = False`

### 8.3 Sensors

- `imu.enabled = False`
- `stereo_camera.enabled = False`
- `lidar.enabled = False`
- `enable_height_scanner = False`

当前虽然显式传感器关闭，但轮地接触重建路径仍用于：

- `wheel_normal_contact_force`
- 日志中的 slip / contact diagnostics

---

## 9. PPO 配置

### 9.1 Runner

- `seed = 1`
- `num_steps_per_env = 512`
- `max_iterations = 700`
- `save_interval = 100`
- `clip_actions = None`
- `experiment_name = "complete_car_stage0"`

### 9.2 Actor / Critic

- hidden dims：`[256, 256]`
- activation：`relu`
- `obs_normalization = True`
- actor distribution：`SquashedGaussianDistribution`
- actor `init_std = 0.20`
- `log_std_min = -4.0`
- `log_std_max = 0.0`
- critic 不使用分布头

### 9.3 PPO 算法参数

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

## 10. 当前主线解释

当前默认 Stage0 的关键特点不是“球铰-车轮全 12 维都在有效控制”，而是：

- 动作接口仍保留 `12` 维
- 但球铰动作当前被冻结，实际有效控制主要是 `6` 维轮速直驱
- command 口径已经扩展成 `4` 维：
  - `goal_rel_x`
  - `goal_rel_y`
  - `goal_rel_z`
  - `goal_rel_heading`
- 观测维度因此变为 `71 / 71`
- PPO 使用 `tanh squashed Gaussian`
- PPO wrapper 与 env preprocess 前置 clip 都已移除
- 当前终止口径已收敛成：
  - `is_success`
  - `far_from_target`
  - `ball_joint_out_of_bounds`
  - `time_out`

因此，后续所有训练分析都应以这套 Stage0 当前源码口径解释，而不是用旧的：

- `8动作 allocator`
- `70 / 70` 观测
- `16s` 回合
- 姿态类硬终止
- 旧 progress 型 reward
