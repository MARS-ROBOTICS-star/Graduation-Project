# RL阶段训练参数一览表

本文档记录当前 `RL_Training/` 工作区内 `CompleteCar-Stage0` 的**实际生效配置**，用于对 RL 环境做逐环节审查。  
口径以当前源码为准，不再沿用旧的纯轮速解析分配主线，也不沿用历史 run 中已经失效的 observation、reward 或 termination 说明。

## 0. 口径与源码来源

当前文档对应的主线源码：

- 任务环境配置：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- 共享环境主干：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- 环境主类：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- 动作映射：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py`
- 低层 allocator：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py`
- 命令采样：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py`
- 观测构造：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py`
- 奖励函数：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- 终止条件：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py`
- reset 与随机化：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/resets.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/randomization.py`
- 地形与传感器：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/terrain/terrain_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/sensors/sensor_cfg.py`
- 机器人与执行器：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/assets/robot_cfg.py`
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/assets/actuators_cfg.py`
- PPO 配置：`RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py`
- 训练入口：`RL_Training/scripts/train.py`

## 1. 当前 Stage0 主线到底是什么

当前 `CompleteCar-Stage0` 不是“policy 直接输出 6 个轮子的轮速”或“policy 直接输出 6 个轮子的扭矩”。  
它的实际执行链是：

$$
a_t
\rightarrow [u_v^d, q^d]
\rightarrow [\dot q_{cmd}, q_{cmd}]
\rightarrow u_v^\ast
\rightarrow \Omega_{ref}
\rightarrow \tau_{cmd}
$$

其中：

- policy 输出高层动作 $a_t \in \mathbb{R}^8$
- 前 $2$ 维动作映射为中模块平面命令 $u_v^d = [V_x^d, \Omega_z^d]^\top$
- 后 $6$ 维动作映射为两组球铰期望构型 $q^d$
- 环境内部的球铰姿态规划器生成 $\dot q_{cmd}$ 和 $q_{cmd}$
- 环境内部的低滑移 allocator 再生成：
  - 整形后的平面命令 $u_v^\ast$
  - 轮速参考 $\Omega_{ref}$
  - 最终轮级扭矩 $\tau_{cmd}$
- 球铰执行器最终接收的是位置目标 $q_{cmd}$
- 车轮执行器最终接收的是力矩目标 $\tau_{cmd}$

一句话概括当前主线：

- **策略学高层运动意图**
- **环境内部固定低层模型负责低滑移、接触感知、轮级牵引分配**

## 2. 审查时建议先固定的符号表

为避免审查时把论文层、代码层和日志层混在一起，本文档统一使用下列符号：

- $q \in \mathbb{R}^6$：当前球铰实际构型
- $q^d \in \mathbb{R}^6$：policy 给出的球铰期望构型
- $\dot q_{cmd} \in \mathbb{R}^6$：球铰姿态规划器输出的变化率命令
- $q_{cmd} \in \mathbb{R}^6$：球铰执行器最终跟踪的位置目标
- $u_v^d = [V_x^d, \Omega_z^d]^\top \in \mathbb{R}^2$：policy 给出的原始平面命令
- $u_v^\ast \in \mathbb{R}^2$：低滑移整形后的平面命令
- $F_n \in \mathbb{R}^6$：6 个轮子的归一化法向接触力
- $\Omega \in \mathbb{R}^6$：6 个轮子的实际角速度
- $v_{\parallel}^{act} \in \mathbb{R}^6$：6 个轮子的实际滚动方向速度
- $\Omega_{ref} \in \mathbb{R}^6$：低层模型内部的轮速参考
- $\tau_{cmd} \in \mathbb{R}^6$：最终下发给车轮执行器的驱动扭矩命令

## 3. 环境总览与时序参数

### 3.1 任务身份

- 任务名：`CompleteCar-Stage0`
- 环境类：`CompleteCarDirectEnv`
- 环境配置类：`CompleteCarStage0EnvCfg`
- PPO 配置类：`CompleteCarStage0PPORunnerCfg`
- 训练入口脚本：`RL_Training/scripts/train.py`

### 3.2 并行规模、时间步与回合长度

- 并行环境数：`64`
- `scene.env_spacing = 4.0`
- `scene.replicate_physics = True`
- `scene.clone_in_fabric = True`

时间相关参数：

- 仿真步长：`sim_dt = 1 / 120 s`
- 控制降采样：`decimation = 2`
- 控制周期：`control_dt = sim_dt × decimation = 1 / 60 s`
- 回合时长：`episode_length_s = 40.0 s`
- 每回合最大控制步数：`40 × 60 = 2400`
- 每回合最大仿真步数：`40 × 120 = 4800`

### 3.3 当前 Stage0 的任务几何

当前 Stage0 是**平地、双 waypoint、命中后切换 active waypoint** 的 baseline：

- `commands.num_waypoints_per_episode = 2`
- `commands.goal_distance = 10.0 m`
- `commands.resampling_time = 40.0 s`
- `episode_length_s = 40.0 s`
- waypoint 队列只在 reset 时一次性采样
- active waypoint 满足 `distance < 2.0 m` 后立即切到下一个
- 只有最后一个 waypoint 被命中时，episode 才记为 `success`
- 当前默认几何含义是：
  - 每段 waypoint 长度 `10.0 m`
  - 因为有 `2` 段，所以总名义路径长度约 `20.0 m`

## 4. 机器人、关节、轮子与执行器

### 4.1 受控关节与轮子顺序

球铰关节顺序：

```text
[
  spm1_platform_joint_z,
  spm1_platform_joint_y,
  spm1_platform_joint_x,
  spm2_platform_joint_z,
  spm2_platform_joint_y,
  spm2_platform_joint_x,
]
```

车轮关节顺序：

```text
[
  body_car_wheel_left_joint,
  body_car_wheel_right_joint,
  head_car_wheel_left_joint,
  head_car_wheel_right_joint,
  tail_car_wheel_left_joint,
  tail_car_wheel_right_joint,
]
```

车轮刚体顺序：

```text
[
  body_car_wheel_left,
  body_car_wheel_right,
  head_car_wheel_left,
  head_car_wheel_right,
  tail_car_wheel_left,
  tail_car_wheel_right,
]
```

注意：allocator 与环境内部使用的 6 轮顺序是**中轮、前轮、后轮**，不是论文里常见的前-中-后展示顺序。

### 4.2 机器人资产与初始状态

- USD 文件：`USD/complete_car.usd`
- articulation root prim：`/complete_car_alternative/body_car_chassis`
- 生成机器人时启用接触传感：`activate_contact_sensors = True`
- 默认 root 初始位置：`(0.0, 0.0, 0.30)`
- 默认所有球铰角、轮角、球铰角速度、轮角速度都为 `0`

### 4.3 执行器参数

球铰执行器：

- `stiffness = 8000.0`
- `damping = 1000.0`
- `effort_limit_sim = 20.0`
- `velocity_limit_sim = 1.0 rad/s`

车轮执行器：

- `stiffness = 0.0`
- `damping = 0.0`
- `effort_limit_sim = 20.0`
- `velocity_limit_sim = 20.0 rad/s`
- 轮半径：`r_wheel = 0.19 m`

当前最终 actuator 写入方式：

- 球铰：`set_joint_position_target(...)`
- 车轮：`set_joint_effort_target(...)`

因此当前车轮已经不是最终速度控制链，而是最终**力矩控制链**。

## 5. 动作空间与动作映射

### 5.1 动作描述符

当前动作描述符为：

```text
[
  ("base_planar_command", 2),
  ("ball_joint_posture_reference", 6),
]
```

因此动作总维度为：

- `2 + 6 = 8`

### 5.2 policy 输出后的内部动作张量

当前环境已经不再保留独立的 `preprocess_policy_actions(...)` 阶段。  
policy 输出的 `[-1, 1]` 动作会直接写入环境内部动作张量：

- `self.actions`
- `self.last_actions`

当前 reward 已不再包含基于相邻两步原始动作差分的振荡惩罚项。`last_action` 目前保留在观测中，仅作为策略可见的上一时刻动作信息。
同时，环境内也不再保留旧的 wheel velocity target 写入路径，车轮执行链只保留 effort / torque 目标写入。

### 5.3 平面命令分支

前 2 维动作映射为：

$$
u_v^d = [V_x^d, \Omega_z^d]^\top
$$

当前参数：

- `base_forward_velocity_max = 2.0 m/s`
- `base_yaw_rate_max = 2.0 rad/s`
- `base_allow_reverse = True`

映射结果：

- 第 1 维动作映射到 $[-2.0, 2.0]$ m/s
- 第 2 维动作映射到 $[-2.0, 2.0]$ rad/s

因为 `base_allow_reverse = True`，当前 Stage0 允许倒车。

### 5.4 球铰期望构型分支

后 6 维动作映射为：

$$
q^d = [\psi_f^d, \theta_f^d, \phi_f^d, \psi_r^d, \theta_r^d, \phi_r^d]^\top
$$

当前动作上下限：

- 下限：`(-0.6, -1.0, -0.5, -0.6, -1.0, -0.5)`
- 上限：`(0.6, 0.4, 0.5, 0.6, 0.4, 0.5)`

映射逻辑：

- 以默认复位姿态为中心
- 正动作沿上限方向张开
- 负动作沿下限方向张开
- 当前动作映射边界直接与 `ball_joint_out_of_bounds` 使用的终止边界保持一致，不再单独维护一套 `control` 侧 action limit

### 5.5 球铰姿态规划器

环境内部先执行：

$$
\dot q_{cmd} = \mathrm{sat}(K_q (q^d - q))
$$

$$
q_{cmd} = \mathrm{sat}(q + \Delta t\, \dot q_{cmd})
$$

当前参数：

- `ball_joint_planner_gains = (10, 10, 10, 10, 10, 10)`
- `ball_joint_planner_qdot_limits = (1, 1, 1, 1, 1, 1) rad/s`
- `control_dt = 1 / 60 s`
- `q^d` 到 `q_cmd` 的位置饱和边界与 termination 完全一致：
  - `(-0.6, -1.0, -0.5, -0.6, -1.0, -0.5)` 到 `(0.6, 0.4, 0.5, 0.6, 0.4, 0.5)`

这意味着：

- policy 给出的 `q^d` 本身就被限制在与 termination 一致的球铰边界内
- 同时姿态规划器输出的 `q_{cmd}` 也会再次按同一组边界做饱和
- 如果实际球铰角仍然越过这组边界，episode 会被终止

## 6. 低滑移接触感知 allocator

### 6.1 allocator 在整个 RL 链中的位置

当前 allocator 不是网络，而是环境内部的固定低层模型。  
其输入输出为：

$$
(q, q^d, u_v^d, F_n, \Omega, v_{\parallel}^{act})
\rightarrow
(\dot q_{cmd}, q_{cmd}, u_v^\ast, \Omega_{ref}, \tau_{cmd})
$$

### 6.2 当前几何参数

allocator 使用的几何常数为：

- $a_x = 0.25633374$
- $b_f = 0.30654739$
- $b_r = 0.30633826$
- $l_1 = -0.00989449$
- $l_2 = 0.00000932$
- $l_3 = 0.00968251$
- $d_1 = 0.44737875$
- $d_2 = 0.44737968$
- $d_3 = 0.44737875$
- $h_1 = -0.043083285$
- $h_2 = -0.02578188$
- $h_3 = -0.043100655$
- $r_{wheel} = 0.19$

这些参数决定：

- 轮心位置
- 轮滚动方向
- 轮侧向方向
- 位置雅可比
- 名义轮速参考与侧向速度代价

### 6.3 轮心运动学状态

allocator 运行时先构造：

- 每个轮子的轮心位置 $p_w$
- 滚动方向 $t_w$
- 侧向方向 $n_w$
- 位置雅可比 $G_w(q)$

同时代码里仍显式保留：

- 轮速雅可比 $J_w(q) \in \mathbb{R}^{6 \times 2}$
- 姿态变化率修正雅可比 $J_q(q) \in \mathbb{R}^{6 \times 6}$

它们并没有失效，只是在低滑移整形步骤里采用了逐轮展开的等价写法。

### 6.4 接触权重

当前接触权重计算为：

$$
c = \mathrm{sat}\left(\frac{F_n - F_{off}}{F_{on} - F_{off}}, 0, 1\right)
$$

当前参数：

- `contact_force_off_threshold = 0.01`
- `contact_force_on_threshold = 0.08`

说明：

- 当轮子接触力很小，权重接近 `0`
- 当轮子稳定接地，权重接近 `1`

### 6.5 低滑移平面命令整形

allocator 不是直接执行 $u_v^d$，而是求解：

$$
\min_{u_v}
\; \lambda_{tracking} \|u_v - u_v^d\|^2
+ \lambda_{lateral} \sum_w c_w (a_w^\top u_v + b_w)^2
$$

当前参数：

- `low_slip_lambda_tracking = 1.0`
- `low_slip_lambda_lateral = 5.0`

平面命令幅值限制：

- 前向速度上限：`2.0 m/s`
- 偏航角速度上限：`2.0 rad/s`

因此当前整形的倾向是：

- 保持接近期望命令
- 但更重地压低有接触轮的侧向速度

### 6.6 名义轮速参考

整形完成后再生成：

$$
\Omega_{ref} = \frac{1}{r_{wheel}} \operatorname{proj}_{roll}(v_w^{nom})
$$

其中轮心名义速度可以理解为由三部分叠加得到：

- 车体平移项
- 车体偏航项
- 球铰姿态变化项

这一步的角色是：

- 给后续扭矩控制器一个“理想纯滚动下轮子应当怎么转”的参考量

### 6.7 滑移与扭矩分配

纵向滑移按下式计算：

$$
s = \frac{v_{\parallel}^{act} - r_{wheel}\,\Omega}{\max(|v_{\parallel}^{act}|, \varepsilon)}
$$

当前参数：

- `wheel_slip_velocity_epsilon = 0.1`

最终扭矩律为：

$$
\tau_{cmd} = \mathrm{sat}\Big(c \odot [K_\Omega (\Omega_{ref} - \Omega) - K_s s]\Big)
$$

当前参数：

- `wheel_torque_tracking_gain = 2.0`
- `wheel_slip_feedback_gain = 4.0`
- `wheel_joint_effort_limit_sim = 20.0 N·m`

这说明当前低层控制器不是单纯速度跟踪，而是：

- 轮速参考跟踪项
- 纵向滑移抑制项
- 接触权重抑制项

三者共同决定最终扭矩。

### 6.8 审查 allocator 时要特别注意的事实

- policy 当前**能看到**：
  - 轮系纵滑率
  - 轮系侧滑角
  - 归一化法向接触力
- policy 仍然**看不到**：
  - 接触权重 $c$
  - 整形后的平面命令 $u_v^\ast$
  - 轮速参考 $\Omega_{ref}$
  - 最终轮级扭矩 $\tau_{cmd}$
- 当前 reward 已经开始**显式约束**：
  - 转向时过高的平面速度
  - 纵滑率
  - 侧滑角
- 因此当前 low-slip 链对训练的影响有两条：
  - 通过 observation / reward 直接影响策略
  - 通过真实动力学执行结果间接影响策略

## 7. 命令采样与任务目标

### 7.1 命令维度与语义

当前命令维度：`4`

$$
commands = [goal\_rel\_x,\; goal\_rel\_y,\; goal\_rel\_z,\; goal\_bearing]
$$

世界系目标存储为：

$$
command\_targets\_w = [x_t, y_t, z_t, \psi_{seg}]
$$

这里要区分两个量：

- `command_targets_w[:, :3]` 是当前 active waypoint 的世界系位置
- `command_targets_w[:, 3]` 当前主要用于 marker 可视化，表示该段路径的世界系方位角 `\psi_{seg}`
- 真正送入 observation / reward / termination 的第 4 维不是最终目标朝向误差，而是**车体系下指向当前 active waypoint 的 bearing**

### 7.2 目标采样参数

- `num_waypoints_per_episode = 2`
- `goal_distance = 10.0 m`
- `goal_direction_max_deg = 30.0°`
- `goal_heading_delta_max_deg = 0.0°`
- `resampling_time = 40.0 s`
- `zero_command = False`
- `rel_standing_envs = 0.0`

### 7.3 当前 waypoint 队列采样逻辑

当前 Stage0 在 reset 时一次性采样一段长度为 `2` 的 waypoint 队列。  
第 `k` 个 waypoint 总是相对“上一段的 heading”采样，因此整回合形成的是一条短折线，而不是彼此独立的随机点。

第 `k` 段先采样相对上一段 heading 的偏角：

$$
\phi = s \cdot \phi_{max} \cdot \sqrt{u}
$$

其中：

- $u \sim U[0,1)$
- $s \in \{-1, +1\}$
- 采用 $\sqrt{u}$ 是为了做边缘强化采样

再得到：

$$
\theta_{los} = \psi_{base} + \phi
$$

因为当前 `goal_heading_delta_max_deg = 0.0°`，所以：

$$
\psi_{seg} = \theta_{los}
$$

最后在世界系写入目标：

$$
\begin{aligned}
x_t &= x_{anchor} + d \cos \theta_{los} \\
y_t &= y_{anchor} + d \sin \theta_{los} \\
z_t &= 0 \quad \text{(平地模式)}
\end{aligned}
$$

然后把本段的终点位置和方位作为下一段的 `anchor`。

### 7.4 相对目标命令

环境真正送入 observation、reward、termination 的是相对目标量：

$$
relative\_xy_b = R_z(-\psi_{base})(target\_xy_w - base\_xy_w)
$$

$$
relative\_z = z_t - z_{base}
$$

$$
goal\_bearing = \operatorname{atan2}(goal\_rel\_y,\; goal\_rel\_x)
$$

因此当前 `commands[:, 3]` 的物理含义是：

- 当前车体在本体坐标系下看向 active waypoint 的视线角
- 它用于衡量“当前 waypoint 在车头左前方还是右前方偏了多少”
- 它**不是**“到达 waypoint 时车头最终应该朝向哪里”的终点姿态误差

## 8. 观测空间

### 8.1 实际送入 policy 的观测

当前 actor 观测顺序：

```text
ball_joint_pos            6
ball_joint_vel            6
base_lin_vel              3
base_ang_vel              3
wheel_joint_vel           6
wheel_longitudinal_slip   6
wheel_slip_angle          6
wheel_normal_contact_force 6
goal_relative_command     4
last_action               8
----------------------------
total                    54
```

当前 critic 观测：

- 因为 `terrain.measure_heights = False`
- 所以 critic 不追加 terrain height patch
- 当前 critic 维度也为 `54`

### 8.2 可以被构造但当前没有送入 policy 的原始观测项

但当前真正送入网络的是：

- `ball_joint_pos`
- `ball_joint_vel`
- `base_lin_vel`
- `base_ang_vel`
- `wheel_joint_vel`
- `wheel_longitudinal_slip`
- `wheel_normal_contact_force`
- `relative_goal_commands`
- `last_actions`

这意味着当前 policy：

- 已经能看到球铰当前构型与速度
- 已经能看到轮系纵滑率
- 已经能看到轮系侧滑角
- 已经能看到归一化法向接触力
- 仍然看不到球铰目标误差
- 看不到机体姿态

### 8.3 当前观测 scale

虽然当前 actor 只选择了 9 类量送入网络，但配置中仍保留了完整 scale 参数：

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

### 8.4 观测历史、裁剪与噪声

- `use_history = False`
- `history_length = 1`
- `clip_observations = 100.0`
- `noise.enabled = False`
- `noise.level = 1.0`

当前 observation noise **整体关闭**，即使各分量噪声幅值仍保留在配置中，也不会生效。

### 8.5 轮系诊断量公式

纵滑率：

$$
v_x = v_{wheel} \cdot e_{forward}
$$

$$
v_{surface} = r_{wheel} \Omega
$$

$$
wheel\_longitudinal\_slip = \frac{v_x - v_{surface}}{\max(|v_x|, \varepsilon)}
$$

说明：

- 当前诊断量里的纵滑率已经直接复用 allocator 的共享实现
- allocator 与诊断量的原始定义完全一致：
  - $\dfrac{v_x - r\Omega}{\max(|v_x|,\varepsilon)}$
- 当前诊断量与 allocator 控制内部使用的纵滑率都不再做额外裁剪

侧滑角：

$$
wheel\_slip\_angle = \arctan2(v_y, |v_x| + \varepsilon)
$$

接触力：

$$
wheel\_normal\_contact\_force = \frac{\|f_{contact}\|}{W_{vehicle}}
$$

这些量里，当前只有 `ball_joint_target_error` 和 `projected_gravity` 不进入 policy；  
`wheel_slip_angle` 已经进入 actor / critic observation，同时也保留在日志里。

## 9. 奖励函数

### 9.1 当前 reward 总式

$$  
reward =
reward_{distance}
+ reward_{progress}
+ reward_{reached}
+ reward_{far}
+ reward_{angle\_diff}
+ reward_{turn\_speed}
+ reward_{slip}
$$  

当前 reward term 名称：

- `distance_to_target`
- `progress_to_target`
- `reached_target`
- `far_from_target`
- `angle_diff`
- `turn_speed_penalty`
- `slip_penalty`

### 9.2 当前 reward 参数

- `target_position_tolerance = 2.0`
- `target_yaw_tolerance_deg = degrees(0.1) ≈ 5.73°`
- `distance_to_target_denominator_scale = 0.01`
- `distance_to_target_weight = 6.0`
- `progress_to_target_clip_m = 0.25`
- `progress_to_target_relax_radius_m = 4.0`
- `progress_to_target_weight = 8.0`
- `reached_target_base_reward = 2.0`
- `reached_target_weight = 6.0`
- `far_from_target_margin = 6.0`
- `far_from_target_weight = -2.0`
- `angle_diff_weight = 6.0`
- `turn_speed_penalty_weight = -2.0`
- `slip_penalty_weight = -2.0`
- `slip_angle_penalty_ratio = 4.0`
- `only_positive_rewards = False`

说明：

- `target_yaw_tolerance_deg` 仍保留在共享配置里
- 但当前 Stage0 的 waypoint 命中与 episode success 已经**不再使用**该 yaw 阈值

### 9.3 各项 reward 的真实公式

waypoint 命中判定：

$$
waypoint\_hit = (\|commands_{xy}\| < 2.0)
$$

距离项：

$$
reward_{distance} = 6.0 \cdot \frac{1}{1 + 0.01\, d^2} \cdot \frac{1}{T}
$$

进度项：

$$
reward_{progress} =
8.0 \cdot
\frac{\Delta d_{relaxed}}{goal\_distance}
$$

其中：

$$
\Delta d = \operatorname{clip}(d_{prev} - d,\,-0.25,\,0.25)
$$

$$
\Delta d_{relaxed} =
\begin{cases}
\max(\Delta d, 0), & d \le 4.0 \\
\Delta d, & d > 4.0
\end{cases}
$$

waypoint 命中奖励：

$$
reward_{reached} = 6.0 \cdot 2.0 \cdot \frac{T - t}{T} \cdot waypoint\_hit
$$

远离目标惩罚：

$$  
reward_{far} = -2.0 \cdot \mathbb{1}(d > goal\_distance + 6.0)
$$  

当前 waypoint 方向对齐项：

$$
reward_{angle\_diff} = 6.0 \cdot \frac{1}{1+|goal\_bearing|} \cdot \frac{1}{T}
$$

转向时高速惩罚：

$$
reward_{turn\_speed} =
-2.0 \cdot
\frac{
\operatorname{clip}(|goal\_bearing| / 30^\circ,\; 0,\; 1)
\cdot
\left\|v_{base,xy}\right\| / 2.0
}{T}
$$

滑移惩罚：

$$
reward_{slip} =
-2.0 \cdot
\frac{
\operatorname{mean}(|s_{long}|)
+
4.0 \cdot \operatorname{mean}(|\alpha_{slip}|)
}{T}
$$

### 9.4 审查 reward 时必须知道的事实

- 当前 reward 已不再直接惩罚高层 8 维动作变化
- 当前 reward 已经开始直接约束：
  - 当前 active waypoint 的方向对齐
  - 转向时的过高前进速度
  - 纵滑率
  - 侧滑角
- 当前 reward 仍然**没有直接约束**：
  - 接触权重
  - 扭矩大小
  - 球铰极限使用率
  - 轮速参考误差
- 因此当前 low-slip allocator 的好坏既会通过显式滑移项影响 reward，也会通过是否更容易完成 waypoint 跟踪来间接体现

## 10. 终止条件

### 10.1 当前 active done terms

当前 active done term 共有 5 个：

- `waypoint_hit`
- `is_success`
- `far_from_target`
- `ball_joint_out_of_bounds`
- `time_out`

对应公式：

$$
waypoint\_hit = d < 2.0
$$

$$
is\_success = waypoint\_hit \land (active\_waypoint\_index \ge num\_waypoints\_per\_episode - 1)
$$

$$
time\_out = (episode\_length\_buf \ge max\_episode\_length - 1) \land \neg is\_success
$$

$$
far\_from\_target = d > (goal\_distance + 6.0)
$$

$$
ball\_joint\_out\_of\_bounds = \exists i,\; q_i < q_i^{low} \;\text{or}\; q_i > q_i^{up}
$$

注意：

- 中间 waypoint 被命中时，只会触发 `waypoint_hit`
- 环境随后会把 active waypoint 切到下一个
- 只有最后一个 waypoint 被命中时，`is_success` 才会为真并结束 episode

### 10.2 当前球铰终止边界

- 下限：`(-0.6, -1.0, -0.5, -0.6, -1.0, -0.5)`
- 上限：`(0.6, 0.4, 0.5, 0.6, 0.4, 0.5)`

### 10.3 配置存在但当前没有接入 done path 的字段

以下字段还在配置类里，但当前 `compute_done_terms(...)` 并没有使用：

- `orientation_limit_deg = 30.0`
- `head_tail_roll_limit_deg = 35.0`
- `head_tail_pitch_limit_deg = 20.0`

因此当前 Stage0 不会因为整车侧倾、前后车体滚转或俯仰超限而终止。

## 11. Reset 与随机化

### 11.1 root 初值与扰动

- `root_pos = (0.0, 0.0, 0.30)`
- `root_lin_vel = (0.0, 0.0, 0.0)`
- `root_ang_vel = (0.0, 0.0, 0.0)`
- `root_x_range = (-1.0, 1.0)`
- `root_y_range = (-1.0, 1.0)`
- `root_yaw_range = (0.0, 0.0)`

说明：

- 初始位置在各自环境原点附近做平面随机平移
- 初始偏航当前不随机

### 11.2 关节 reset 扰动

- `ball_joint_pos_range = (0.0, 0.0)`
- `ball_joint_vel_range = (0.0, 0.0)`
- `wheel_joint_pos_range = (0.0, 0.0)`
- `wheel_joint_vel_range = (0.0, 0.0)`

说明：

- 当前 reset 时球铰与车轮都不做额外状态扰动

### 11.3 随机化配置

- `enable_action_randomization = False`
- `joint_position_noise_scale = 0.0`
- `action_noise_std = 0.0`
- `action_bias_std = 0.0`

因此当前 Stage0：

- 不加动作噪声
- 不加动作 bias
- 不加 joint position noise

## 12. 地形、课程学习与传感器

### 12.1 当前地形设置

- `terrain.enabled = False`
- `terrain.mode = "plane"`
- `static_friction = 1.0`
- `dynamic_friction = 1.0`
- `restitution = 0.0`
- `measure_heights = False`

这意味着当前 Stage0 使用的是平地，不启用地形生成器，也不向 critic 追加高度 patch。

### 12.2 当前保留但未激活的 terrain patch 参数

以下参数已经配置好，但在当前平地主线中不参与 policy 输入：

- `patch_front_extent = 0.942209`
- `patch_rear_extent = 0.942209`
- `patch_half_width = 0.280374`
- `patch_preview_length = 1.0`
- `patch_rear_margin = 0.40`
- `patch_side_margin = 1.0`
- `patch_origin_offset_xy = (0.0, 0.0)`
- `patch_resolution_x = 0.10`
- `patch_resolution_y = 0.10`
- `height_scanner_update_period = 0.02`
- `height_scanner_offset = (0.0, 0.0, 20.0)`

这些参数是为后续非平地 critic height patch 预留的，不是当前 Stage0 actor/critic 的 active 输入。

### 12.3 课程学习

- `curriculum.enabled = False`
- `max_init_terrain_level = 0`
- `default_terrain_name = "flat"`
- `move_up_distance_ratio = 0.5`
- `move_down_command_ratio = 0.5`

因为当前地形生成器未启用且 curriculum 关闭，所以 terrain curriculum 逻辑当前不生效。

### 12.4 当前显式传感器开关

- `sensors.imu.enabled = False`
- `sensors.stereo_camera.enabled = False`
- `sensors.lidar.enabled = False`
- `sensors.enable_height_scanner = False`
- `sensors.height_scanner_debug_vis = False`

### 12.5 虽然高层传感器全关，但接触感知仍在工作

这一点非常关键。当前虽然 IMU、双目、激光雷达、height scanner 都关闭了，但：

- 机器人 spawn 时启用了 `activate_contact_sensors = True`
- `CompleteCarSensorSuiteRuntime` 仍会在运行时为 6 个轮子建立 rigid contact view
- 环境和 allocator 仍能实时得到每个轮子的接触力合力向量

因此当前 Stage0 仍然具备：

- 轮地接触感知
- 归一化法向接触力计算
- 接触权重 $c$
- 接触感知牵引分配

换句话说，当前“传感器全关”只意味着**没有高层感知传感器**，并不意味着 allocator 失去了轮地接触信息。

## 13. PPO 与训练器参数

### 13.1 Runner 级参数

- `seed = 1`
- `device = "cuda:0"`
- `num_steps_per_env = 512`
- `max_iterations = 700`
- `save_interval = 100`
- `experiment_name = "complete_car_stage0"`
- `run_name = ""`
- `obs_groups = {"actor": ["actor"], "critic": ["critic"]}`
- `clip_actions = None`
- `check_for_nan = True`
- `logger = "tensorboard"`
- `resume = False`
- `load_run = ".*"`
- `load_checkpoint = "model_.*.pt"`

### 13.2 Actor 网络

- MLP hidden dims：`[256, 256]`
- activation：`relu`
- `obs_normalization = True`
- 分布：`SquashedGaussianDistribution`
- `init_std = 0.20`
- `log_std_min = -4.0`
- `log_std_max = 0.0`

### 13.3 Critic 网络

- MLP hidden dims：`[256, 256]`
- activation：`relu`
- `obs_normalization = True`
- 无动作分布头

### 13.4 PPO 算法参数

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

### 13.5 训练入口可被 CLI 覆盖的参数

`RL_Training/scripts/train.py` 允许通过命令行覆盖这些关键项：

- `--task`
- `--num_envs`
- `--seed`
- `--max_iterations`
- `--experiment_name`
- `--run_name`
- `--resume`
- `--load_run`
- `--checkpoint`
- `--logger`
- `--log_project_name`
- `--video`

因此在审查训练结果时，不能只看默认配置文件，也要检查本次 run 是否通过 CLI 覆写了关键参数。

## 14. 当前哪些量进入训练，哪些量只留在日志里

### 14.1 当前真正进入策略学习闭环的量

进入 policy 的量：

- `ball_joint_pos`
- `ball_joint_vel`
- `base_lin_vel`
- `base_ang_vel`
- `wheel_joint_vel`
- `wheel_longitudinal_slip`
- `wheel_slip_angle`
- `wheel_normal_contact_force`
- `goal_relative_command`
- `last_action`

直接决定执行器的量：

- 球铰：`q_cmd`
- 车轮：`τ_cmd`

直接进入 reward / termination 的量：

- `relative_goal_commands`
- `base_lin_vel_b`
- `wheel_longitudinal_slip`
- `wheel_slip_angle`
- 当前球铰角 `q`
- `episode_length_buf`

### 14.2 当前只用于内部执行或诊断的量

当前这些量很重要，但不直接进入 policy：

- `wheel_contact_forces_w`
- `desired_ball_joint_targets`
- `wheel_normal_contact_force`
- `contact_weights`
- `shaped_planar_command`
- `wheel_speed_reference`
- `wheel_torque_targets`
- `wheel_slip_angle`
- `ball_joint_target_error`
- `projected_gravity`

### 14.3 当前日志输出面板的有效口径

当前终端主链会优先打印以下高信号 tag：

- `Action/policy_abs_mean`
- `Action/policy_std`
- `Action/wheel_speed_reference_abs_mean_raw`
- `Action/wheel_torque_target_abs_mean_raw`
- `Reward/total`
- `Reward/reached_target`
- `Reward/distance_to_target`
- `Reward/progress_to_target`
- `Reward/angle_diff`
- `Reward/turn_speed_penalty`
- `Reward/slip_penalty`
- `Reward/far_from_target`
- `Observation/wheel_longitudinal_slip_abs_mean_raw`
- `Observation/wheel_slip_angle_abs_mean_raw`
- `Observation/wheel_normal_contact_force_sum_raw`
- `Observation/tilt_deg`
- `Observation/ball_joint_vel_abs_mean_raw`
- `Termination/success_rate`
- `Termination/time_out_rate`
- `Termination/far_from_target_rate`
- `Termination/ball_joint_limit_rate`
- `Termination/terminated_rate`
- `Tracking/goal_success_rate`
- `Tracking/goal_pos_error`
- `Tracking/goal_heading_error_abs`
- `Tracking/goal_completion_pct`

当前 TensorBoard 还会额外记录：

- `episode/waypoints_completed`
- `episode/waypoint_completion_pct`

其中：

- `Tracking/goal_success_rate` 当前来自 reset 批次 episode log，与 `Termination/success_rate` 使用同一批 env、同一时刻 done 判定
- `Tracking/goal_heading_error_abs` 在当前 Stage0 里的实际物理含义是：
  - **车体系下对当前 active waypoint 的 bearing 误差**
  - 不是旧版单目标终点捕获任务里的“最终目标朝向误差”

已经从 active logging path 删除的 step metrics 包括：

- `Observation/turn_radius_raw`
- step 级 `Command/goal_target_x_world`
- step 级 `Command/goal_target_y_world`
- step 级 `Command/goal_target_z_world`
- step 级 `Command/goal_target_heading_world`
- `Observation/head_roll_pitch_abs_mean_raw`
- `Observation/tail_roll_pitch_abs_mean_raw`
- `Observation/goal_rel_x_raw`
- `Observation/goal_rel_y_raw`
- `Observation/goal_rel_z_raw`
- `Observation/goal_rel_heading_raw`
- `Observation/last_action_abs_mean_raw`
- `Critic/height_patch_mean`
- `Critic/height_patch_max`

### 14.4 当前最容易在审查中混淆的点

- policy 输出不是 $\Omega_{ref}$，也不是 $\tau_{cmd}$
- allocator 输出虽然包含 $\Omega_{ref}$，但车轮最终执行的是 $\tau_{cmd}$
- reward 已不再惩罚高层动作变化
- 当前 Stage0 的 low-slip 机制已经同时通过：
  - 滑移相关 observation
  - 显式 `slip_penalty`
  - 转向减速项
  - 动力学执行结果
 共同影响 learning signal
- `Termination/terminated_rate` 当前只保留终端打印，不再写 TensorBoard
- 配置类里还保留了一些未接入 active path 的字段，审查时必须区分“配置存在”和“运行时实际使用”

## 15. 建议的逐环节审查顺序

如果要对当前 RL 环境做系统审查，建议按下面顺序看：

1. 先确认双 waypoint 平地几何是否合理
2. 再确认 `54` 维观测是否已经覆盖你想约束的行为质量
3. 再看 8 维动作如何通过 planner 和 allocator 变成 $q_{cmd}$ 与 $\tau_{cmd}$
4. 再核对 reward 是否真的在鼓励你希望的“连续通过 + 低滑移转向”，而不是仅仅鼓励“接近当前点即可”
5. 再核对 termination 是否过宽或过窄
6. 最后再看 PPO 超参数，因为当前很多训练现象可能首先来自任务闭环本身，而不是来自 PPO 数值设置

按这个顺序，你能更快区分：

- 是 policy 输入不够
- 还是 reward 在引导错误行为
- 还是 low-slip allocator 没被显式利用
- 还是 PPO 只是把一个本来就弱监督的任务学到了局部坏平衡
