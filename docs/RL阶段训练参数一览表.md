# RL阶段训练参数一览表

本文档记录当前 `RL_Training/` 工作区内 `CompleteCar-Stage0` 的实际生效配置。
当前 Stage0 的任务、观测主项和 reward 已按用户要求回退到当前已知最佳真实 run 对应口径：

- `2026-04-21_21-51-09_stage0_waypoint_quality_goal10_v1_150iter`

在此基础上，动作空间已按用户最新要求重新加入 policy `yaw_rate_cmd`。因此本文档描述的是当前 active baseline，而不是后续待验证的新分支：

- `54 / 54` actor / critic 观测
- `8` 维动作
- 平地双 waypoint
- 每段 `10 m`
- reward 为 `7` 项，其中 `progress_to_target` 已接入 low-slip gate
- 包含 `far_from_target`
- 不包含 `next_turn_delta`
- 不包含 `differential_turn_cost`
- 不启用基于 preview turn-demand 的 penalty scaling

## 0. 对应源码

| 模块 | 源码 |
|---|---|
| Stage0 配置覆盖 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py` |
| 共享配置主干 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py` |
| 环境主类 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py` |
| 命令采样 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/commands.py` |
| 动作映射 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py` |
| 观测拼接 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py` |
| 奖励函数 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py` |
| 终止条件 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py` |
| IO 维度描述 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/io_descriptors.py` |
| PPO 配置 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py` |
| 低滑移分配器 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py` |

## 1. 当前 Stage0 总览

| 项目         |                  当前值 | 说明                                                  |
| ---------- | -------------------: | --------------------------------------------------- |
| 任务 ID      | `CompleteCar-Stage0` | 平地 baseline                                         |
| 阶段名        |             `stage0` | `CompleteCarStage0EnvCfg.stage_name`                |
| 并行环境数      |                 `64` | `scene.num_envs`                                    |
| 环境间距       |              `4.0 m` | `scene.env_spacing`                                 |
| 仿真步长       |          `1 / 120 s` | `control.sim_dt`                                    |
| decimation |                  `2` | 每 `2` 个 sim step 更新一次 RL 控制                         |
| 控制周期       |           `1 / 60 s` | `control.control_dt`                                |
| 回合时长       |               `40 s` | `episode_length_s`                                  |
| 最大控制步数     |               `2400` | `40 / (1 / 60)`                                     |
| 地形         |              `plane` | `terrain.enabled = False`，`terrain.mode = "plane"`  |
| 课程学习       |                   关闭 | `curriculum.enabled = False`                        |
| 传感器增强      |                   关闭 | IMU、相机、雷达、高度扫描均关闭                                   |
| 动作随机化      |                   关闭 | `randomization.enable_action_randomization = False` |
| 观测噪声       |                   关闭 | `observations.noise.enabled = False`                |

## 2. 任务命令与 waypoint

| 参数                           |      当前值 | 工程含义                      |
| ---------------------------- | -------: | ------------------------- |
| `num_commands`               |      `4` | 相对目标命令维度                  |
| `num_waypoints_per_episode`  |      `2` | 每个 episode 有两个连续 waypoint |
| `resampling_time`            | `40.0 s` | 与回合时长一致，当前不是短周期重采样任务      |
| `goal_distance`              | `10.0 m` | 每段 waypoint 名义距离          |
| 总名义路径长度                      | `20.0 m` | 两段 waypoint，共约 `20 m`     |
| `goal_direction_max_deg`     |  `30.0°` | 每段目标方向相对上一段方向的最大偏转        |
| `min_segment_turn_deg`       |   `0.0°` | 额外最小转角下限；当前第 2 段已直接约束为 `|phi_2| > |phi_1|` |
| `goal_heading_delta_max_deg` |   `0.0°` | 当前目标航向与目标点视线方向一致          |
| `zero_command`               |  `False` | 不退化为原地目标                  |
| `rel_standing_envs`          |    `0.0` | 不随机生成原地保持样本               |

当前双 waypoint 采样规则：

- 第 1 段偏角 `phi_1` 在 `[-30°，30°]` 内随机采样。
- 第 2 段偏角 `phi_2` 在 `[-30°，30°]` 内随机采样，但逐环境约束 `|phi_2| > |phi_1|`。
- 因此第 2 个 waypoint 相比第 1 个 waypoint 具有更大的转向偏角需求。

当前 `relative_goal_commands` 的 4 个分量为：

| 分量 | 维度 | 含义 |
|---|---:|---|
| `goal_rel_x` | `1` | 当前 active waypoint 在车体系下的 x 相对位置 |
| `goal_rel_y` | `1` | 当前 active waypoint 在车体系下的 y 相对位置 |
| `goal_rel_z` | `1` | 当前 active waypoint 相对车体高度 |
| `goal_rel_heading` | `1` | 当前目标点在车体系下的视线方向角，即 `atan2(goal_rel_y, goal_rel_x)` |

注意：当前 reward 中的 `angle_diff` 使用的是 `goal_rel_heading`，不是一个额外的“最终目标航向误差”。由于 Stage0 设置 `goal_heading_delta_max_deg = 0.0°`，目标航向采样本身与该段视线方向一致，但源码实际进入 reward 的量仍然是相对目标点视线角。

## 3. 动作空间

总动作维度为 `8`：

| 动作分量 | 维度 | 映射方式 | 当前范围或限制 |
|---|---:|---|---|
| `base_planar_command` | `2` | 归一化动作映射为 `[vx_cmd, yaw_rate_cmd]` | `vx_cmd ∈ [-2.0, 2.0] m/s`，`yaw_rate_cmd ∈ [-2.0, 2.0] rad/s` |
| `ball_joint_posture_reference` | `6` | 归一化动作映射为 6 个球铰期望姿态 `q^d` | 使用球铰 lower / upper limits 与默认零位线性映射 |

当前底盘命令参数：

| 参数 | 当前值 |
|---|---:|
| `base_forward_velocity_max` | `2.0 m/s` |
| `base_yaw_rate_max` | `2.0 rad/s` |
| `base_allow_reverse` | `True` |

当 `base_allow_reverse = True` 时，第一维归一化动作 `a_v` 直接映射为：

$$
v_x^{cmd}=a_v \cdot v_{max}
$$

当 `base_allow_reverse = False` 时才会使用前进-only 映射；当前 Stage0 不使用该模式。

当前 policy 输出 `yaw_rate_cmd`。环境传给低层 allocator 的期望平面命令为：

$$
\mathbf u_v^{d}=[v_x^{cmd},\omega_z^{cmd}]^T
$$

## 4. 低层执行链

当前 Stage0 策略不直接输出 6 个轮子的轮速或扭矩。实际控制链为：

1. policy 输出 `8` 维动作。
2. 前 `2` 维映射为底盘平面命令 `[vx_cmd, yaw_rate_cmd]`。
3. 后 `6` 维映射为球铰期望姿态 `q^d`。
4. 环境内部球铰姿态规划器根据当前球铰状态与 `q^d` 生成 `q_cmd`。
5. 低滑移 allocator 根据平面命令、球铰状态、轮地接触与滑移信息生成 `Omega_ref` 与 `tau_cmd`。
6. 球铰执行位置控制，车轮执行力矩控制。

关键低层参数：

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `ball_joint_planner_gains` | `(10, 10, 10, 10, 10, 10)` | 球铰姿态规划比例增益 |
| `ball_joint_planner_qdot_limits` | `(1, 1, 1, 1, 1, 1) rad/s` | 球铰规划速度限制 |
| `ball_joint_stiffness` | `8000.0` | 球铰位置驱动刚度 |
| `ball_joint_damping` | `1000.0` | 球铰位置驱动阻尼 |
| `ball_joint_effort_limit_sim` | `20.0 N*m` | 球铰仿真力矩限制 |
| `ball_joint_velocity_limit_sim` | `1.0 rad/s` | 球铰仿真速度限制 |
| `wheel_joint_stiffness` | `0.0` | 车轮不走位置刚度 |
| `wheel_joint_damping` | `0.0` | 车轮不靠阻尼驱动 |
| `wheel_joint_effort_limit_sim` | `15.0 N*m` | 车轮力矩限制 |
| `wheel_joint_velocity_limit_sim` | `20.0 rad/s` | 车轮速度限制 |
| `low_slip_lambda_tracking` | `1.0` | 低滑移分配器的跟踪权重 |
| `low_slip_lambda_lateral` | `10.0` | 低滑移分配器的横向滑移抑制权重 |
| `contact_force_off_threshold` | `0.01` | 接触权重关闭阈值 |
| `contact_force_on_threshold` | `0.08` | 接触权重开启阈值 |
| `wheel_torque_tracking_gain` | `1.5` | 轮速跟踪力矩增益 |
| `wheel_slip_feedback_gain` | `8.0` | 纵向滑移反馈抑制增益 |
| `wheel_slip_velocity_epsilon` | `0.1` | 纵向滑移计算中的速度小量 |

## 5. 观测空间

actor / critic 观测维度均为 `54 / 54`。当前 Critic 不额外追加 privileged state，也不追加高度 patch。

| 观测项 | 维度 | 缩放 | 来源或含义 |
|---|---:|---:|---|
| `ball_joint_pos` | `6` | `1.0` | 6 个球铰位置，经过角度 wrap |
| `ball_joint_vel` | `6` | `1.0` | 6 个球铰速度 |
| `base_lin_vel` | `3` | `1.0` | 车体质心线速度，body frame |
| `base_ang_vel` | `3` | `1.0` | 车体质心角速度，body frame |
| `wheel_joint_vel` | `6` | `1.0` | 6 个车轮关节速度 |
| `wheel_longitudinal_slip` | `6` | `1.0` | 6 个车轮纵向滑移率 |
| `wheel_slip_angle` | `6` | `1.0` | 6 个车轮侧偏角，裁剪到 `[-pi / 2, pi / 2]` |
| `wheel_normal_contact_force` | `6` | `1.0` | 6 个车轮法向接触力，按整车重量归一化 |
| `goal_relative_command` | `4` | `1.0` | 当前 active waypoint 相对命令 |
| `last_action` | `8` | `1.0` | 上一步 policy 动作 |

维度合计：

$$
6+6+3+3+6+6+6+6+4+8=54
$$

当前不在观测中的项：

- `next_turn_delta`
- `projected_gravity`
- `ball_joint_target_error`
- `module_roll_pitch`
- `terrain_height_patch`
- 外部 IMU / camera / lidar 观测

## 6. 当前奖励函数总式

当前 reward 在 `mdp/rewards.py` 的 `compute_reward_terms()` 中计算。
总奖励为 7 个加权分量直接求和：

$$
r =
r_{dist}
+ r_{prog}
+ r_{hit}
+ r_{far}
+ r_{angle}
+ r_{turnspeed}
+ r_{slip}
$$

其中 $r_{prog}$ 不是原始距离进度奖励，而是经过低滑移 gate 调制后的 progress 奖励。

当前 `only_positive_rewards = False`，所以总奖励不会被裁剪为非负数。

记号说明：

| 记号 | 含义 |
|---|---|
| $T$ | 最大控制步数，当前为 `2400` |
| $t$ | 当前 episode 控制步计数 |
| $d_t$ | 当前 active waypoint 的平面距离，$d_t=\sqrt{x_g^2+y_g^2}$ |
| $d_{t-1}$ | 上一步记录的 active waypoint 距离 |
| $\theta_t$ | 当前目标点在车体系下的视线方向误差，来自 `commands[:, 3]` |
| $v_{xy}$ | 车体平面速度模长，来自 `base_lin_vel_b[:, :2]` |
| $v_{max}$ | 当前 `base_forward_velocity_max = 2.0` |
| $s_i$ | 第 `i` 个车轮纵向滑移率 |
| $\alpha_i$ | 第 `i` 个车轮侧偏角 |
| $I_{hit}$ | 当前 active waypoint 是否命中 |
| $I_{far}$ | 当前 active waypoint 距离是否超过远离阈值 |
| $G_\kappa$ | 六轮纵滑 gate |
| $G_\alpha$ | 六轮侧滑 gate |
| $G$ | 纵滑 gate 和侧滑 gate 的较小值，即 $\min(G_\kappa,G_\alpha)$ |
| $M$ | progress 调制系数 |

## 7. Reward 分项明细

### 7.1 `distance_to_target`

源码形式：

$$
r_{dist}
=
6.0 \cdot
\frac{1}{1+0.01 d_t^2}
\cdot
\frac{1}{T}
$$

配置来源：

| 参数 | 当前值 |
|---|---:|
| `distance_to_target_denominator_scale` | `0.01` |
| `distance_to_target_weight` | `6.0` |

工程含义：

- 这是一个持续型接近目标奖励。
- 距离越小，单步奖励越大。
- 除以 $T$ 后，单步量级被压低，避免持续奖励压过 waypoint 命中奖励。

### 7.2 `progress_to_target`

先计算距离进步量：

$$
\Delta d_t = d_{t-1}-d_t
$$

再裁剪：

$$
\Delta d_t^{clip}
=
\mathrm{clip}(\Delta d_t,-0.25,0.25)
$$

若已经进入 `4.0 m` 近目标区域，则不再惩罚距离短时变大：

$$
d_t \le 4.0
\Rightarrow
\Delta d_t^{clip}=\max(\Delta d_t^{clip},0)
$$

拆分正进度和负进度：

$$
\Delta d_t^+
=
\max(\Delta d_t^{clip},0)
$$

$$
\Delta d_t^-
=
\min(\Delta d_t^{clip},0)
$$

六轮纵滑 gate：

$$
G_\kappa
=
\prod_{i=1}^{6}
\exp
\left[
-\frac{1}{2}
\left(
\frac{s_i}{3.0}
\right)^2
\right]
$$

六轮侧滑 gate：

$$
G_\alpha
=
\prod_{i=1}^{6}
\left[
0.5
\cos
\left(
\operatorname{clip}
\left(
\frac{\pi |\alpha_i|}{1.5},0,\pi
\right)
\right)
+0.5
\right]
$$

综合 gate：

$$
G
=
\min
\left(
G_\kappa,\ G_\alpha
\right)
$$

progress 调制系数：

$$
M
=
0.10 + 1.40G
$$

最终 gated progress 奖励：

$$
r_{prog}
=
8.0
\cdot
\frac{
M\Delta d_t^+
+
\Delta d_t^-
}{10.0}
$$

配置来源：

| 参数 | 当前值 |
|---|---:|
| `progress_to_target_clip_m` | `0.25 m` |
| `progress_to_target_relax_radius_m` | `4.0 m` |
| `progress_to_target_weight` | `8.0` |
| `goal_distance` | `10.0 m` |
| `progress_gate_longitudinal_k` | `3.0` |
| `progress_gate_slip_angle_scale_rad` | `1.5 rad` |
| `progress_gate_min_multiplier` | `0.10` |
| `progress_gate_max_multiplier` | `1.5` |

工程含义：

- 这是当前最直接的“每步向目标推进”奖励，也是 low-slip gate 的主作用位置。
- 向目标靠近为正，远离目标为负；只有正向进度会被 gate 调制。
- 高滑移前进仍保留至少 `10%` 的正向 progress，不会完全压死早期学习。
- 低滑移前进最多获得 `150%` 的正向 progress，鼓励低滑移完成。
- 当前使用 `min(G_kappa, G_alpha)`，因此纵滑和侧滑任一项较差都会明显降低正向 progress。
- 负向 progress 不受 gate 削弱，远离目标仍完整扣分。
- 近目标 `4.0 m` 内取消负进度，目的是减少末端调整时的抖动惩罚。

### 7.3 `reached_target`

命中条件：

$$
d_t < 0.5
$$

剩余时间缩放：

$$
\eta_t=\frac{T-t}{T}
$$

奖励：

$$
r_{hit}
=
6.0 \cdot 2.0 \cdot I_{hit} \cdot \eta_t
$$

配置来源：

| 参数 | 当前值 |
|---|---:|
| `target_position_tolerance` | `0.5 m` |
| `reached_target_base_reward` | `2.0` |
| `reached_target_weight` | `6.0` |

工程含义：

- 单次 waypoint 命中最高奖励为 `12.0`，随剩余时间线性衰减。
- 中间 waypoint 和最后 waypoint 都会触发该奖励。
- 命中中间 waypoint 后，环境会切换到下一个 active waypoint。
- 命中最后 waypoint 才算 episode 成功终止。

### 7.4 `far_from_target`

远离阈值：

$$
d_{far}=10.0+6.0=16.0
$$

奖励：

$$
r_{far}
=
-2.0 \cdot I(d_t>16.0)
$$

配置来源：

| 参数 | 当前值 |
|---|---:|
| `goal_distance` | `10.0 m` |
| `far_from_target_margin` | `6.0 m` |
| `far_from_target_weight` | `-2.0` |

工程含义：

- 这是远离目标惩罚，同时与终止条件共用同一个阈值。
- 一旦 `d_t > 16.0 m`，该项为 `-2.0`，并且 episode 会以 `far_from_target` 失败终止。

### 7.5 `angle_diff`

源码中的角度误差：

$$
\theta_t=\mathrm{wrap}(commands[:,3])
$$

奖励：

$$
r_{angle}
=
6.0 \cdot
\frac{1}{1+|\theta_t|}
\cdot
\frac{1}{T}
$$

配置来源：

| 参数 | 当前值 |
|---|---:|
| `angle_diff_weight` | `6.0` |

工程含义：

- 该项鼓励车体朝向当前目标点的方向。
- $\theta_t$ 越接近 `0`，奖励越高。
- 它不是强制终止项，只是持续型方向引导。

### 7.6 `turn_speed_penalty`

转向强度归一化：

$$
\rho_t
=
\mathrm{clip}
\left(
\frac{|\theta_t|}{30^\circ},
0,
1
\right)
$$

平面速度归一化：

$$
\nu_t
=
\frac{\|v_{xy}\|}{2.0}
$$

惩罚项：

$$
r_{turnspeed}
=
-2.0 \cdot
\frac{\rho_t \nu_t}{T}
$$

配置来源：

| 参数 | 当前值 |
|---|---:|
| `goal_direction_max_deg` | `30.0°` |
| `base_forward_velocity_max` | `2.0 m/s` |
| `turn_speed_penalty_weight` | `-2.0` |

工程含义：

- 当目标方向偏差大、车速又高时，该项惩罚更大。
- 它约束“大角度转向时高速冲过去”的行为。
- 当前没有使用 `next_turn_delta` 或 preview turn-demand 来缩放该项。

### 7.7 `slip_penalty`

先计算 6 个车轮的平均纵向滑移和平均侧偏角：

$$
\bar{s}
=
\frac{1}{6}
\sum_{i=1}^{6}|s_i|
$$

$$
\bar{\alpha}
=
\frac{1}{6}
\sum_{i=1}^{6}|\alpha_i|
$$

未加权 slip 量：

$$
c_{slip}
=
\frac{\bar{s}+6.0\bar{\alpha}}{T}
$$

奖励分量：

$$
r_{slip}
=
-2.0 \cdot c_{slip}
$$

配置来源：

| 参数 | 当前值 |
|---|---:|
| `slip_penalty_weight` | `-2.0` |
| `slip_angle_penalty_ratio` | `6.0` |
| `low_slip_longitudinal_threshold` | `1.0` |
| `low_slip_angle_threshold_rad` | `0.35` |
| `wheel_slip_epsilon` | `0.1` |
| `wheel_slip_angle_clip_rad` | `pi / 2` |

工程含义：

- 纵向滑移和侧偏都会被惩罚。
- 侧偏角权重为纵向滑移的 `6` 倍。
- 当前已将 `slip_penalty_weight` 从 `-4.0` 降到 `-2.0`，使其退回背景约束，主要低滑移约束转移到 gated progress。
- 当前新增 low-slip 评价阈值，但该阈值只用于日志评价，不直接作为成功终止条件。
- 当前最佳 run 虽然能学起来，但完成方式偏高侧滑，说明这个 slip 惩罚还没有把行为完全约束到低滑移协同转向。

## 8. 当前奖励函数回答

如果只用一句话概括，现在的奖励函数是：

$$
r =
6\frac{1}{1+0.01d_t^2}\frac{1}{T}
+
8\frac{M\Delta d_t^+ + \Delta d_t^-}{10}
+
12I_{hit}\frac{T-t}{T}
-
2I(d_t>16)
+
6\frac{1}{1+|\theta_t|}\frac{1}{T}
-
2\frac{\rho_t\nu_t}{T}
-
2\frac{\bar{s}+6\bar{\alpha}}{T}
$$

其中近目标区域有一个额外规则：

$$
d_t \le 4.0
\Rightarrow
\mathrm{clip}(d_{t-1}-d_t,-0.25,0.25)
\text{ 的负值会被置为 }0
$$

其中 low-slip progress gate 为：

$$
M
=
0.10
+
1.40
\cdot
\min
\left(
G_\kappa,\ G_\alpha
\right)
$$

这就是当前 Stage0 active baseline 的实际奖励函数。

## 9. 终止条件

| 终止项 | 条件 | 是否 counted as terminated | 说明 |
|---|---|---:|---|
| `is_success` | 当前 waypoint 命中，且 active waypoint 已是最后一个 | 是 | 最后一个 waypoint 距离 `< 0.5 m` |
| `far_from_target` | `d_t > 16.0 m` | 是 | 与 reward 中 `far_from_target` 共用阈值 |
| `ball_joint_out_of_bounds` | 任一球铰超出配置上下限 | 是 | 保护球铰动作不越界 |
| `time_out` | `episode_length_buf >= max_episode_length - 1` 且未成功 | 否，作为 timeout | 达到 `40 s` 控制步上限 |

当前球铰终止上下限：

| 关节组 | lower | upper |
|---|---|---|
| 6 个球铰 | `(-0.6, -1.0, -0.5, -0.6, -1.0, -0.5)` | `(0.6, 0.4, 0.5, 0.6, 0.4, 0.5)` |

## 10. Reset 与随机化

| 参数 | 当前值 |
|---|---:|
| `root_pos` | `(0.0, 0.0, 0.30)` |
| `root_lin_vel` | `(0.0, 0.0, 0.0)` |
| `root_ang_vel` | `(0.0, 0.0, 0.0)` |
| `root_x_range` | `(-1.0, 1.0)` |
| `root_y_range` | `(-1.0, 1.0)` |
| `root_yaw_range` | `(0.0, 0.0)` |
| `ball_joint_pos_range` | `(0.0, 0.0)` |
| `ball_joint_vel_range` | `(0.0, 0.0)` |
| `wheel_joint_pos_range` | `(0.0, 0.0)` |
| `wheel_joint_vel_range` | `(0.0, 0.0)` |
| `enable_action_randomization` | `False` |
| `joint_position_noise_scale` | `0.0` |
| `action_noise_std` | `0.0` |
| `action_bias_std` | `0.0` |

## 11. PPO 配置

| 参数 | 当前值 |
|---|---:|
| `runner.class_name` | `OnPolicyRunner` |
| `seed` | `1` |
| `device` | `cuda:0` |
| `num_steps_per_env` | `512` |
| `max_iterations` | `700` |
| `save_interval` | `25` |
| `experiment_name` | `complete_car_stage0` |
| `logger` | `tensorboard` |
| `obs_groups` | `{"actor": ["actor"], "critic": ["critic"]}` |
| `clip_actions` | `None` |
| `check_for_nan` | `True` |
| `resume` | `False` |
| `load_run` | `.*` |
| `load_checkpoint` | `model_.*.pt` |

Actor 网络：

| 参数 | 当前值 |
|---|---:|
| `hidden_dims` | `[256, 256]` |
| `activation` | `relu` |
| `obs_normalization` | `True` |
| `distribution` | `SquashedGaussianDistribution` |
| `init_std` | `0.20` |
| `log_std_min` | `-4.0` |
| `log_std_max` | `0.0` |

Critic 网络：

| 参数 | 当前值 |
|---|---:|
| `hidden_dims` | `[256, 256]` |
| `activation` | `relu` |
| `obs_normalization` | `True` |
| `distribution` | `None` |

PPO 算法：

| 参数 | 当前值 |
|---|---:|
| `num_learning_epochs` | `5` |
| `num_mini_batches` | `16` |
| `learning_rate` | `1.0e-4` |
| `adam_eps` | `1.0e-5` |
| `schedule` | `adaptive` |
| `gamma` | `0.99` |
| `lam` | `0.95` |
| `entropy_coef` | `5.0e-4` |
| `desired_kl` | `0.008` |
| `max_grad_norm` | `0.5` |
| `value_loss_coef` | `0.5` |
| `use_clipped_value_loss` | `True` |
| `clip_param` | `0.2` |

## 12. TensorBoard 重点观测量

当前环境会记录以下与 reward 和任务进度直接相关的指标：

| 类别 | 指标 |
|---|---|
| Reward | `Reward/total` |
| Reward | `Reward/distance_to_target` |
| Reward | `Reward/progress_to_target` |
| Reward | `Reward/reached_target` |
| Reward | `Reward/far_from_target` |
| Reward | `Reward/angle_diff` |
| Reward | `Reward/turn_speed_penalty` |
| Reward | `Reward/slip_penalty` |
| Tracking | `Tracking/active_waypoint_pos_error` |
| Tracking | `Tracking/active_waypoint_bearing_abs` |
| Tracking | `Tracking/active_segment_completion_pct` |
| Tracking | `Tracking/active_waypoint_index_mean` |
| Tracking | `Tracking/waypoints_completed_mean` |
| Tracking | `Tracking/episode_completion_pct` |
| LowSlip | `LowSlip/longitudinal_slip_pass_rate` |
| LowSlip | `LowSlip/slip_angle_pass_rate` |
| LowSlip | `LowSlip/combined_pass_rate` |
| LowSlip | `LowSlip/longitudinal_slip_margin` |
| LowSlip | `LowSlip/slip_angle_margin` |
| ProgressGate | `ProgressGate/combined_gate` |
| ProgressGate | `ProgressGate/multiplier` |
| ProgressGate | `ProgressGate/longitudinal_gate` |
| ProgressGate | `ProgressGate/slip_angle_gate` |
| ProgressGate | `ProgressGate/positive_progress_raw` |
| ProgressGate | `ProgressGate/negative_progress_raw` |
| ProgressGate | `ProgressGate/ungated_progress_raw` |
| Episode | `episode/waypoints_completed` |
| Episode | `episode/waypoint_completion_pct` |
| Episode | `episode/waypoint_hit_rate` |
| Episode | `episode/end_active_waypoint_pos_error` |
| Episode | `episode/end_active_waypoint_bearing_abs` |
| Episode | `episode/waypoint_hit_pos_error` |
| Episode | `episode/success_hit_pos_error` |
| Termination | `Termination/success_rate` |
| Termination | `Termination/time_out_rate` |
| Termination | `Termination/far_from_target_rate` |
| Termination | `Termination/ball_joint_limit_rate` |
| Action | `Action/policy_abs_mean` |
| Action | `Action/wheel_speed_reference_abs_mean_raw` |
| Action | `Action/wheel_torque_target_abs_mean_raw` |
| Action | `Action/shaped_planar_command_abs_mean_raw` |
| Action | `Action/contact_weight_mean_raw` |
| Observation | `Observation/roll_deg` |
| Observation | `Observation/pitch_deg` |
| Observation | `Observation/pitch_abs_deg` |
| Observation | `Observation/wheel_joint_vel_abs_mean_raw` |
| Observation | `Observation/wheel_longitudinal_slip_abs_mean_raw` |
| Observation | `Observation/wheel_slip_angle_abs_mean_raw` |
| Observation | `Observation/wheel_normal_contact_force_sum_raw` |

当前还会记录每个车轮的诊断指标。车轮名称按 `WHEEL_JOINT_NAMES` 顺序展开：

- `body_car_wheel_left`
- `body_car_wheel_right`
- `head_car_wheel_left`
- `head_car_wheel_right`
- `tail_car_wheel_left`
- `tail_car_wheel_right`

每个车轮都会记录以下 TensorBoard tag：

| 模板 | 含义 |
|---|---|
| `PerWheel/<wheel>/wheel_joint_vel` | 该车轮实际关节角速度 |
| `PerWheel/<wheel>/wheel_speed_reference` | 该车轮低层分配得到的轮速参考 |
| `PerWheel/<wheel>/wheel_torque_target` | 该车轮下发的力矩目标 |
| `PerWheel/<wheel>/contact_weight` | 由法向接触力映射得到的接触权重 |
| `PerWheel/<wheel>/normal_force` | 该车轮实际接触合力模长，单位为 N |
| `PerWheel/<wheel>/longitudinal_slip` | 该车轮纵向滑移率 |
| `PerWheel/<wheel>/slip_angle` | 该车轮侧偏角 |

## 13. 当前结论与使用边界

当前旧的 `2.0 m` 成功半径配置已经由真实训练 run 证明“能学起来”。当前表格记录的是后续收紧后的 active 配置：成功半径已改为 `0.5 m`，第 2 段 waypoint 偏角已要求大于第 1 段；该新配置已经完成多轮正式训练验证。

已知边界：

- `0.5 m` 成功半径已经可以训练到高成功率平台，但后段滑移质量仍不达标。
- 第 2 段更大偏角会增强转向需求，可能降低早期成功率。
- 当前 reward 中有 slip 惩罚，但还不足以证明“协同转向已经稳定学成”。
- 当前 low-slip progress gate 可以保住高成功率并略降纵滑，但没有把侧滑角压到 `0.5 rad` 或 `30°` 以下。
- 当前没有地形传感器、课程学习、高度 patch 或复杂地形输入。
- 当前没有 `next_turn_delta`，策略看不到下一段转向预告。
- 当前没有 `differential_turn_cost`，也没有 preview-based penalty scaling。
- 旧指标 `Tracking/goal_success_rate`、`Tracking/goal_pos_error`、`Tracking/goal_heading_error_abs`、`Tracking/goal_completion_pct` 已移除，避免把 active waypoint 指标误读为最终目标指标。
- 旧 `Observation/tilt_deg` 实际记录中车 roll 绝对值；当前已新增 `Observation/pitch_deg` 和 `Observation/pitch_abs_deg`，用于量化中车前俯/后仰。

后续推进原则：

- 若继续分析本轮 low-slip gate v1，应先用 per-wheel 日志确认左侧轮不转、接触权重、法向力和纵滑之间的关系。
- 若继续低滑移优化，应先决定 low-slip 是评价指标、奖励偏好，还是成功条件的一部分。
- 在确认 per-wheel 诊断后，再讨论是否修改 gate、低层 allocator、终止条件或训练课程。
