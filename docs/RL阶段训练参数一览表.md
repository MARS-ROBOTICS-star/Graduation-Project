# RL阶段训练参数一览表

本文档记录当前 `RL_Training/` 工作区内 `CompleteCar-Stage0` 的实际生效配置。
本文档以当前源码为准，覆盖 RL 环境配置、底层运动学轮速分配、球铰控制器、车轮力矩控制器、reward、termination 与 PPO 参数。

当前 Stage0 主线是平地双 waypoint active baseline；动作空间已重新加入 policy `yaw_rate_cmd`，底层执行链保留内部 `q_cmd/qdot_cmd` 球铰轨迹规划，但球铰 drive 只接收位置目标 `q_cmd`，并且车轮力矩控制器已恢复为旧版直接纵滑反馈 torque target 结构。因此本文档描述的是当前 active baseline，而不是已经撤回的衰减式力矩控制分支：

- `54 / 54` actor / critic 观测
- `8` 维动作
- 平地双 waypoint
- 每段 `10 m`
- reward 为 `8` 项，其中 `progress_to_target` 已接入 low-slip gate，新增 `action_rate_penalty` 与 `timeout_penalty`，直接 `slip_penalty` 与 `turn_speed_penalty` 已从 active reward 中移除，`load_equalization` 当前权重为 `0.0`，只保留六轮负载不均匀诊断
- 包含 `far_from_target`
- 不包含 `next_turn_delta`
- 不包含 `differential_turn_cost`
- 不启用基于 preview turn-demand 的 penalty scaling
- 球铰执行链：policy 给出最终姿态目标 `q^d`，环境内部轨迹生成器输出 `q_cmd/qdot_cmd`，PhysX 球铰 drive 只跟踪 `q_cmd`
- 车轮执行链：低层分配器输出 `Omega_ref` 与 `tau_cmd`，Isaac 车轮关节最终执行 torque target
- 当前车轮力矩公式：`contact_weight * (K_track * (Omega_ref - Omega) - K_slip * kappa)`，再做 `±20 N*m` 限幅

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

当 `base_allow_reverse = False` 时，第一维归一化动作 `a_v` 使用前进-only 映射：

$$
v_x^{cmd}=0.5(a_v+1)v_{max}
$$

当前 Stage0 使用 `base_allow_reverse = True`，因此 policy 第一维可以直接输出正向或反向底盘速度命令。

当前 policy 输出 `yaw_rate_cmd`。环境传给低层 allocator 的期望平面命令为：

$$
\mathbf u_v^{d}=[v_x^{cmd},\omega_z^{cmd}]^T
$$

## 4. 低层执行链、运动学模型与控制器

当前 Stage0 策略不直接输出 6 个车轮的轮速或扭矩。实际控制链为：

1. policy 输出 `8` 维动作。
2. 前 `2` 维映射为底盘平面命令 `u_v^d=[v_x^d, \omega_z^d]^T`。
3. 后 `6` 维映射为球铰最终目标姿态 `q^d`。
4. 低层 allocator 内部旧一阶球铰规划器根据 `q^d` 和当前实际球铰姿态 `q` 生成同一套 `q_cmd/qdot_cmd`。
5. Isaac/PhysX 球铰隐式 actuator 只接收位置目标 `q_cmd`，不再接收 `qdot_cmd` 作为球铰速度目标。
6. 低层 allocator 使用实际球铰姿态 `q_actual` 计算轮心几何，并复用同一个 `qdot_cmd` 计算构型速度项。
7. allocator 先用接触感知加权最小二乘整形底盘平面命令，得到 `u_v^*=[v_x^*, \omega_z^*]^T`。
8. allocator 根据 `q_actual`、`qdot_cmd` 和 `u_v^*` 计算每个车轮的滚动速度参考 `Omega_ref`。
9. allocator 根据 `Omega_ref`、实际车轮角速度、实际纵向速度、实际侧向速度和接触权重生成车轮力矩目标 `tau_cmd`。
10. 车轮关节最终执行 torque target；`Omega_ref` 只是力矩控制器内部参考，不是 Isaac 速度控制目标。

### 4.1 关节顺序与底层变量

球铰动作和状态顺序：

| 序号 | 球铰关节名 | 物理含义 |
|---:|---|---|
| 1 | `spm1_platform_joint_z` | 前球铰 z 轴转动 |
| 2 | `spm1_platform_joint_y` | 前球铰 y 轴转动 |
| 3 | `spm1_platform_joint_x` | 前球铰 x 轴转动 |
| 4 | `spm2_platform_joint_z` | 后球铰 z 轴转动 |
| 5 | `spm2_platform_joint_y` | 后球铰 y 轴转动 |
| 6 | `spm2_platform_joint_x` | 后球铰 x 轴转动 |

车轮输出顺序：

| 序号 | 车轮关节名 | 车轮刚体名 | 对应模块 |
|---:|---|---|---|
| 1 | `body_car_wheel_left_joint` | `body_car_wheel_left` | 中车左轮 |
| 2 | `body_car_wheel_right_joint` | `body_car_wheel_right` | 中车右轮 |
| 3 | `head_car_wheel_left_joint` | `head_car_wheel_left` | 前车左轮 |
| 4 | `head_car_wheel_right_joint` | `head_car_wheel_right` | 前车右轮 |
| 5 | `tail_car_wheel_left_joint` | `tail_car_wheel_left` | 后车左轮 |
| 6 | `tail_car_wheel_right_joint` | `tail_car_wheel_right` | 后车右轮 |

底层运动学统一记号：

| 记号 | 源码变量 | 含义 |
|---|---|---|
| $q$ | `ball_joint_pos` | 实际球铰姿态，6 维 |
| $q^d$ | `desired_ball_joint_targets` | policy 映射得到的最终球铰目标姿态 |
| $q_{\mathrm{ref}}$ | `_ball_joint_reference_targets` | env 层轨迹参考字段；当前旧一阶 allocator 路径不使用 |
| $q_{\mathrm{cmd}}$ | `ball_joint_position_targets` | 本控制步下发给 Isaac 的球铰位置目标 |
| $\dot q_{\mathrm{cmd}}$ | `ball_joint_rate_targets` | 本控制步内部规划得到的球铰速度，用于轨迹积分和轮速分配；当前不下发给 Isaac/PhysX 球铰速度目标 |
| $u_v^d$ | `planar_command` / `desired_planar_command` | policy 映射得到的底盘平面命令 |
| $u_v^*$ | `shaped_planar_command` | 低侧滑整形后的底盘平面命令 |
| $p_j(q)$ | `wheel_positions` | 第 $j$ 个轮心在中车坐标系下的位置 |
| $t_j(q)$ | `rolling_directions` | 第 $j$ 个车轮滚动方向单位向量 |
| $n_j(q)$ | `lateral_directions` | 第 $j$ 个车轮侧向单位向量 |
| $J_{p,j}(q)$ | `position_jacobians` | 第 $j$ 个轮心位置对 $q$ 的雅可比 |
| $\Omega_j$ | `wheel_joint_vel` | 第 $j$ 个车轮实际关节角速度 |
| $\Omega_j^{\mathrm{ref}}$ | `wheel_speed_reference` | 第 $j$ 个车轮参考角速度 |
| $C_j$ | `contact_weights` | 第 $j$ 个车轮接触权重 |
| $\tau_j^{\mathrm{cmd}}$ | `wheel_torque_targets` | 第 $j$ 个车轮最终力矩目标 |

### 4.2 底层运动学几何参数

`wheel_speed_allocator.py` 中的当前几何参数如下。单位均为 `m`，车轮半径也在此表内。

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `a_x` | `0.25633374` | 前、后模块连接点相对中模块原点的 x 向偏置绝对值 |
| `b_f` | `0.30654739` | 前模块局部轮心 x 向安装偏置修正 |
| `b_r` | `0.30633826` | 后模块局部轮心 x 向安装偏置修正 |
| `l1` | `-0.00989449` | 前模块轮心局部 x 基准 |
| `l2` | `0.00000932` | 中模块轮心局部 x 基准 |
| `l3` | `0.00968251` | 后模块轮心局部 x 基准 |
| `d1` | `0.44737875` | 前模块左右轮距 |
| `d2` | `0.44737968` | 中模块左右轮距 |
| `d3` | `0.44737875` | 后模块左右轮距 |
| `h1` | `-0.043083285` | 前模块轮心局部 z 偏置 |
| `h2` | `-0.02578188` | 中模块轮心局部 z 偏置 |
| `h3` | `-0.043100655` | 后模块轮心局部 z 偏置 |
| `r_wheel` / `wheel_radius` | `0.19` | 车轮半径 |

中模块两个轮心位置固定为：

$$
p_{\mathrm{body},L}
=
\begin{bmatrix}
l_2\\
d_2/2\\
h_2
\end{bmatrix},
\qquad
p_{\mathrm{body},R}
=
\begin{bmatrix}
l_2\\
-d_2/2\\
h_2
\end{bmatrix}.
$$

前模块和后模块轮心先在各自模块局部坐标中定义，再通过球铰姿态旋转到中模块坐标系：

$$
p_{\mathrm{head},L}
=
\begin{bmatrix}
a_x\\
0\\
0
\end{bmatrix}
+
R_f(q_f)
\begin{bmatrix}
l_1-b_f\\
d_1/2\\
h_1
\end{bmatrix},
$$

$$
p_{\mathrm{head},R}
=
\begin{bmatrix}
a_x\\
0\\
0
\end{bmatrix}
+
R_f(q_f)
\begin{bmatrix}
l_1-b_f\\
-d_1/2\\
h_1
\end{bmatrix},
$$

$$
p_{\mathrm{tail},L}
=
\begin{bmatrix}
-a_x\\
0\\
0
\end{bmatrix}
+
R_r(q_r)
\begin{bmatrix}
l_3+b_r\\
d_3/2\\
h_3
\end{bmatrix},
$$

$$
p_{\mathrm{tail},R}
=
\begin{bmatrix}
-a_x\\
0\\
0
\end{bmatrix}
+
R_r(q_r)
\begin{bmatrix}
l_3+b_r\\
-d_3/2\\
h_3
\end{bmatrix}.
$$

滚动方向和侧向方向为：

$$
t_{\mathrm{body},L}
=
t_{\mathrm{body},R}
=
e_x,
\qquad
n_{\mathrm{body},L}
=
n_{\mathrm{body},R}
=
e_y,
$$

$$
t_{\mathrm{head},*}=R_f(q_f)e_x,
\qquad
n_{\mathrm{head},*}=R_f(q_f)e_y,
$$

$$
t_{\mathrm{tail},*}=R_r(q_r)e_x,
\qquad
n_{\mathrm{tail},*}=R_r(q_r)e_y.
$$

### 4.3 动作到物理命令的映射

policy 原始动作记为：

$$
a=
\begin{bmatrix}
a_v & a_\omega & a_{q,1} & \cdots & a_{q,6}
\end{bmatrix}^T,
\qquad
a_i\in[-1,1].
$$

当前 `base_allow_reverse = True`，因此底盘纵向速度命令为对称映射：

$$
v_x^d
=
a_v v_{\max},
\qquad
v_{\max}=2.0.
$$

偏航角速度命令为：

$$
\omega_z^d
=
a_\omega \omega_{\max},
\qquad
\omega_{\max}=2.0.
$$

因此：

$$
u_v^d
=
\begin{bmatrix}
v_x^d\\
\omega_z^d
\end{bmatrix}.
$$

球铰动作按默认零位、下限和上限分段线性映射。对第 $i$ 个球铰：

$$
q_i^d
=
q_{0,i}
+
\max(a_{q,i},0)(q_{i,\max}-q_{0,i})
+
\min(a_{q,i},0)(q_{0,i}-q_{i,\min}).
$$

当前默认零位 $q_0=0$。Stage0 当前球铰动作/终止共用上下限：

| 维度 | lower | upper |
|---:|---:|---:|
| `spm1_platform_joint_z` | `-0.6` | `0.6` |
| `spm1_platform_joint_y` | `-1.0` | `0.4` |
| `spm1_platform_joint_x` | `-0.5` | `0.5` |
| `spm2_platform_joint_z` | `-0.6` | `0.6` |
| `spm2_platform_joint_y` | `-1.0` | `0.4` |
| `spm2_platform_joint_x` | `-0.5` | `0.5` |

### 4.4 球铰轨迹生成器

当前生效路径不是 env 层 `q_ref/qddot` 轨迹整形器，而是 allocator 内部旧一阶球铰规划器。当前控制步先把 policy 给出的最终目标裁剪到关节上下限：

$$
q_{\mathrm{goal}}
=
\operatorname{clip}(q^d,q_{\min},q_{\max}).
$$

目标误差经比例增益转成原始速度命令：

$$
\dot q_{\mathrm{raw}}
=
K_q(q_{\mathrm{goal}}-q),
\qquad
K_q=
\operatorname{diag}(10,10,10,10,10,10).
$$

速度限幅：

$$
\dot q_{\mathrm{sat}}
=
\operatorname{clip}
\left(
\dot q_{\mathrm{raw}},
-\dot q_{\max},
\dot q_{\max}
\right),
\qquad
\dot q_{\max}=1.0\ \mathrm{rad/s}.
$$

当前旧一阶路径直接令：

$$
\dot q_{\mathrm{cmd}}=\dot q_{\mathrm{sat}}.
$$

位置目标积分并裁剪：

$$
q_{\mathrm{cmd}}
=
\operatorname{clip}
\left(
q+\Delta t\dot q_{\mathrm{cmd}},
q_{\min},
q_{\max}
\right).
$$

因此当前球铰每个控制步最大位置变化约为 `1.0 / 60 = 0.0167 rad`。`ball_joint_planner_qddot_limits` 和 `ball_joint_planner_track_error_limit` 字段仍存在于配置中，但当前这条旧一阶路径不使用它们。

### 4.5 Isaac/PhysX 球铰隐式 PD actuator

当前球铰 actuator 是 Isaac Lab `ImplicitActuatorCfg`。环境每个控制步只下发球铰位置目标：

$$
q_{\mathrm{des,sim}}=q_{\mathrm{cmd}}.
$$

`qdot_cmd` 仍由内部轨迹生成器计算，并继续给轮速分配器用于构型速度项；但它不再作为 PhysX 球铰速度目标。实际底层可近似理解为位置 drive 加默认零速度阻尼：

$$
\tau_q^{\mathrm{drive}}
\approx
K_p(q_{\mathrm{cmd}}-q)
+
K_d(0-\dot q).
$$

当前参数：

| 参数                              |              当前值 | 含义                  |
| ------------------------------- | ---------------: | ------------------- |
| `ball_joint_stiffness`          | `8000.0 N*m/rad` | 球铰 drive 位置刚度 $K_p$ |
| `ball_joint_damping`            |  `1000.0 N*m*s/rad` | 球铰 drive 速度阻尼 $K_d$ |
| `ball_joint_effort_limit_sim`   |       `20.0 N*m` | 球铰 drive 力矩上限       |
| `ball_joint_velocity_limit_sim` |      `1.0 rad/s` | 球铰 drive 速度上限       |

注意：`qdot_cmd` 当前只作为内部规划速度和轮速分配器的构型速度输入，不再送入 PhysX 球铰速度目标。该改动用于验证此前 `qdot_cmd` 主动速度跟踪是否导致中车被拱起和球铰左右高频摆动。

### 4.6 接触权重

传感器侧先对每个车轮求世界系接触合力模长，再按整车重量归一化：

$$
\bar F_j
=
\frac{\|F_j^{\mathrm{contact}}\|}{W_{\mathrm{vehicle}}}.
$$

接触权重为线性 ramp：

$$
C_j
=
\operatorname{clip}
\left(
\frac{\bar F_j-F_{\mathrm{off}}}{F_{\mathrm{on}}-F_{\mathrm{off}}},
0,
1
\right).
$$

当前参数：

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `contact_force_off_threshold` | `0.01` | 归一化法向力低于该值时认为接触权重为 `0` |
| `contact_force_on_threshold` | `0.08` | 归一化法向力高于该值时认为接触权重为 `1` |

这里的 `0.01` 和 `0.08` 是按整车重量归一化后的无量纲比例，不是牛顿值。

### 4.7 低侧滑平面命令整形

低层不直接使用 policy 的 `u_v^d` 生成轮速，而是先求整形后的平面命令：

$$
u_v^*
=
\begin{bmatrix}
v_x^*\\
\omega_z^*
\end{bmatrix}.
$$

轮心名义速度由三部分组成：

$$
v_j^{\mathrm{nom}}
=
v_x e_x
+
\omega_z(e_z \times p_j(q))
+
J_{p,j}(q)\dot q_{\mathrm{cmd}}.
$$

第 $j$ 个车轮的名义侧向速度可写成：

$$
v_{j,\perp}^{\mathrm{nom}}
=
n_j(q)^T v_j^{\mathrm{nom}}
=
a_j(q)^T u_v
+
b_j(q,\dot q_{\mathrm{cmd}}),
$$

其中：

$$
a_j(q)
=
\begin{bmatrix}
n_j(q)^T e_x\\
n_j(q)^T(e_z \times p_j(q))
\end{bmatrix},
$$

$$
b_j(q,\dot q_{\mathrm{cmd}})
=
n_j(q)^T J_{p,j}(q)\dot q_{\mathrm{cmd}}.
$$

整形目标函数为：

$$
J(u_v)
=
\lambda_{\mathrm{track}}\|u_v-u_v^d\|^2
+
\lambda_{\mathrm{lat}}
\sum_{j=1}^{6}
C_j
\left(
a_j^T u_v+b_j
\right)^2.
$$

当前权重：

| 参数                         |   当前值 | 含义                  |
| -------------------------- | ----: | ------------------- |
| `low_slip_lambda_tracking` | `1.0` | 保持接近 policy 底盘命令的权重 |
| `low_slip_lambda_lateral`  | `5.0` | 抑制名义侧向速度的权重         |

当前低层仍启用横向低滑移整形，`u_v^*` 不一定等于 policy 输出的 $u_v^d$。

对应闭式线性方程为：

$$
H u_v^* = g,
$$

$$
H
=
\lambda_{\mathrm{track}} I
+
\lambda_{\mathrm{lat}}
\sum_{j=1}^{6}
C_j a_j a_j^T,
$$

$$
g
=
\lambda_{\mathrm{track}}u_v^d
-
\lambda_{\mathrm{lat}}
\sum_{j=1}^{6}
C_j a_j b_j.
$$

求解后再按平面命令限制裁剪：

$$
v_x^*
\in
[-2.0,2.0]\ \mathrm{m/s},
\qquad
\omega_z^*
\in
[-2.0,2.0]\ \mathrm{rad/s}.
$$

注意：policy 的 `v_x^d` 因 `base_allow_reverse=True` 可以为负；allocator 对 `u_v^*` 的最终裁剪也是对称区间。

### 4.8 轮速参考

用整形后的 `u_v^*` 重新计算轮心名义速度：

$$
v_j^{\mathrm{nom}}
=
v_x^* e_x
+
\omega_z^*(e_z \times p_j(q))
+
J_{p,j}(q)\dot q_{\mathrm{cmd}}.
$$

第 $j$ 个车轮滚动方向上的参考线速度：

$$
V_{j,\parallel}^{\mathrm{ref}}
=
t_j(q)^T v_j^{\mathrm{nom}}.
$$

车轮角速度参考：

$$
\Omega_j^{\mathrm{ref}}
=
\frac{V_{j,\parallel}^{\mathrm{ref}}}{r}.
$$

等价写成矩阵形式：

$$
\Omega^{\mathrm{ref}}
=
J_w(q)u_v^*
+
J_q(q)\dot q_{\mathrm{cmd}},
$$

其中第 $j$ 行为：

$$
J_{w,j}(q)
=
\frac{1}{r}
\begin{bmatrix}
t_j(q)^T e_x
&
t_j(q)^T(e_z \times p_j(q))
\end{bmatrix},
$$

$$
J_{q,j}(q)
=
\frac{1}{r}
t_j(q)^T J_{p,j}(q).
$$

### 4.9 实际轮速、纵滑与侧偏角

运行时由车轮刚体线速度和车轮姿态求实际滚动方向速度与侧向速度：

$$
V_{j,\parallel}
=
t_{j,w}^T v_{j,w},
\qquad
V_{j,\perp}
=
n_{j,w}^T v_{j,w}.
$$

车轮圆周速度与实际滚动速度差：

$$
\Delta V_j
=
r\Omega_j - V_{j,\parallel}.
$$

当前 signed 纵滑定义：

$$
\kappa_j
=
\frac{
r\Omega_j
-
V_{j,\parallel}
}{
\max(|V_{j,\parallel}|,\epsilon)
},
\qquad
\epsilon=0.1.
$$

因此车轮圆周速度大于实际纵向滚动速度时，$\kappa_j>0$，表示正向滑转倾向。

侧偏角定义：

$$
\alpha_j
=
\operatorname{atan2}
\left(
V_{j,\perp},
\max(|V_{j,\parallel}|,\epsilon)
\right).
$$

这里的 $\epsilon$ 只作为低速分母下限，不再对所有速度段执行加法偏置。

观测链会将侧偏角裁剪到：

$$
\alpha_j\in[-\pi/2,\pi/2].
$$

### 4.10 车轮力矩控制器

当前车轮控制器是旧版直接纵滑反馈 torque target，不是已经撤回的纵滑/侧滑衰减式控制器。

基础轮速跟踪力矩：

$$
\tau_{0,j}
=
K_{\Omega}
\left(
\Omega_j^{\mathrm{ref}}-\Omega_j
\right).
$$

加入 signed 纵滑反馈后的预接触权重力矩：

$$
\tau_{1,j}
=
\tau_{0,j}
-
K_{\kappa}\kappa_j.
$$

乘接触权重并限幅后的最终车轮力矩目标：

$$
\tau_j^{\mathrm{cmd}}
=
\operatorname{clip}
\left(
C_j\tau_{1,j},
-\tau_{\max},
\tau_{\max}
\right).
$$

代入当前参数：

$$
\tau_j^{\mathrm{cmd}}
=
\operatorname{clip}
\left(
C_j
\left[
2.0
\left(
\Omega_j^{\mathrm{ref}}-\Omega_j
\right)
-
4.0\kappa_j
\right],
-20.0,
20.0
\right).
$$

当前车轮 actuator 参数：

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `wheel_joint_stiffness` | `0.0` | 车轮不使用位置刚度驱动 |
| `wheel_joint_damping` | `0.0` | 车轮不靠 actuator damping 驱动 |
| `wheel_joint_effort_limit_sim` | `20.0 N*m` | 车轮 torque target 限幅 |
| `wheel_joint_velocity_limit_sim` | `20.0 rad/s` | 车轮关节速度限制 |
| `wheel_torque_tracking_gain` | `2.0` | $K_{\Omega}$，轮速跟踪增益 |
| `wheel_slip_feedback_gain` | `4.0` | $K_{\kappa}$，纵滑反馈增益 |
| `wheel_slip_velocity_epsilon` | `0.1 m/s` | 纵滑和侧偏角计算中的低速分母保护 |

当前兼容日志字段：

| 字段 | 当前含义 |
|---|---|
| `g_kappa` | 固定为 `1.0`，仅保留旧日志兼容性 |
| `g_alpha` | 固定为 `1.0`，仅保留旧日志兼容性 |
| `tau0` | $\tau_{0,j}$，基础轮速跟踪力矩 |
| `tau1` | $\tau_{1,j}$，加入纵滑反馈、乘接触权重前的力矩 |

### 4.11 低层参数总表

| 参数                                     |                                    当前值 | 生效位置                             |
| -------------------------------------- | -------------------------------------: | -------------------------------- |
| `control.sim_dt`                       |                            `1 / 120 s` | PhysX 仿真步长                       |
| `control.decimation`                   |                                    `2` | 每 2 个 sim step 更新一次 RL 控制        |
| `control.control_dt`                   |                             `1 / 60 s` | RL 控制周期与低层轨迹积分周期                 |
| `base_forward_velocity_max`            |                              `2.0 m/s` | policy 底盘前进速度映射上限                |
| `base_yaw_rate_max`                    |                            `2.0 rad/s` | policy 底盘偏航角速度映射上限               |
| `base_allow_reverse`                   |                                 `True` | policy 可输出正向或反向底盘速度                |
| `ball_joint_planner_gains`             |          `(10, 10, 10, 10, 10, 10)` | $K_q$                            |
| `ball_joint_planner_qdot_limits`       | `(1.0, 1.0, 1.0, 1.0, 1.0, 1.0) rad/s` | $\dot q_{\max}$                  |
| `ball_joint_planner_qddot_limits`      |       `(12.0, 12.0, 12.0, 12.0, 12.0, 12.0) rad/s^2` | 当前旧一阶路径不使用                 |
| `ball_joint_planner_track_error_limit` |                             `0.10 rad` | 当前旧一阶路径不使用 |
| `ball_joint_pos_lower_limits`          | `(-0.6, -1.0, -0.5, -0.6, -1.0, -0.5) rad` | Stage0 球铰动作映射与终止下限 |
| `ball_joint_pos_upper_limits`          | `(0.6, 0.4, 0.5, 0.6, 0.4, 0.5) rad` | Stage0 球铰动作映射与终止上限 |
| `ball_joint_stiffness`                 |                      `8000.0 N*m/rad` | Isaac 球铰 drive 刚度                |
| `ball_joint_damping`                   |                       `1000.0 N*m*s/rad` | Isaac 球铰 drive 阻尼                |
| `ball_joint_effort_limit_sim`          |                             `20.0 N*m` | Isaac 球铰 drive 力矩上限              |
| `ball_joint_velocity_limit_sim`        |                            `1.0 rad/s` | Isaac 球铰 drive 速度上限              |
| `wheel_radius`                         |                               `0.19 m` | 轮速参考和滑移率计算                       |
| `wheel_joint_stiffness`                |                                  `0.0` | 车轮 actuator 位置刚度                 |
| `wheel_joint_damping`                  |                                  `0.0` | 车轮 actuator 阻尼                   |
| `wheel_joint_effort_limit_sim`         |                             `20.0 N*m` | 车轮 torque target 限幅              |
| `wheel_joint_velocity_limit_sim`       |                           `20.0 rad/s` | 车轮关节速度限制                         |
| `low_slip_lambda_tracking`             |                                  `1.0` | 平面命令整形跟踪项权重                      |
| `low_slip_lambda_lateral`              |                                  `5.0` | 平面命令整形侧滑项权重                      |
| `contact_force_off_threshold`          |                                 `0.01` | 接触权重 ramp 下限                     |
| `contact_force_on_threshold`           |                                 `0.08` | 接触权重 ramp 上限                     |
| `wheel_torque_tracking_gain`           |                                  `2.0` | $K_{\Omega}$                     |
| `wheel_slip_feedback_gain`             |                                  `4.0` | $K_{\kappa}$                     |
| `wheel_slip_velocity_epsilon`          |                                  `0.1` | $\epsilon$                       |

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
总奖励为 8 个分量直接求和：

$$
r =
r_{dist}
+ r_{prog}
+ r_{hit}
+ r_{far}
+ r_{timeout}
+ r_{angle}
+ r_{actionrate}
+ r_{eq}
$$

其中 $r_{prog}$ 不是原始距离进度奖励，而是经过低滑移 gate 调制后的 progress 奖励。
其中 $r_{eq}$ 当前形式为负载不均匀惩罚项，但权重为 `0.0`，所以只保留诊断意义。

当前 `only_positive_rewards = False`，所以总奖励不会被裁剪为非负数。

记号说明：

| 记号 | 含义 |
|---|---|
| $T$ | 最大控制步数，当前为 `2400` |
| $t$ | 当前 episode 控制步计数 |
| $d_t$ | 当前 active waypoint 的平面距离，$d_t=\sqrt{x_g^2+y_g^2}$ |
| $d_{t-1}$ | 上一步记录的 active waypoint 距离 |
| $\theta_t$ | 当前目标点在车体系下的视线方向误差，来自 `commands[:, 3]` |
| $s_i$ | 第 `i` 个车轮纵向滑移率 |
| $\alpha_i$ | 第 `i` 个车轮侧偏角 |
| $\Delta a_{base}$ | 底盘 2 维动作相对上一步的变化量 |
| $\Delta a_{joint}$ | 球铰 6 维动作相对上一步的变化量 |
| $I_{hit}$ | 当前 active waypoint 是否命中 |
| $I_{far}$ | 当前 active waypoint 距离是否超过远离阈值 |
| $I_{timeout}$ | 当前 episode 是否因未成功达到时间上限而 timeout |
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

若已经进入 `3.0 m` 近目标区域，则不再惩罚距离短时变大：

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
\frac{s_i}{0.5}
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
0.25 + 1.25G
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
| `progress_to_target_relax_radius_m` | `3.0 m` |
| `progress_to_target_weight` | `8.0` |
| `goal_distance` | `10.0 m` |
| `progress_gate_longitudinal_k` | `0.5` |
| `progress_gate_slip_angle_scale_rad` | `1.5 rad` |
| `progress_gate_min_multiplier` | `0.25` |
| `progress_gate_max_multiplier` | `1.5` |

工程含义：

- 这是当前最直接的“每步向目标推进”奖励，也是 low-slip gate 的主作用位置。
- 向目标靠近为正，远离目标为负；只有正向进度会被 gate 调制。
- 高滑移前进仍保留至少 `25%` 的正向 progress，不会完全压死早期学习。
- 低滑移前进最多获得 `150%` 的正向 progress，鼓励低滑移完成。
- 当前使用 `min(G_kappa, G_alpha)`，因此纵滑和侧滑任一项较差都会明显降低正向 progress。
- 负向 progress 不受 gate 削弱，远离目标仍完整扣分。
- 近目标 `3.0 m` 内取消负进度，目的是减少末端调整时的抖动惩罚。

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

### 7.5 `timeout_penalty`

timeout 条件来自 `mdp/terminations.py`：

$$
I_{timeout}=1
\Leftrightarrow
t\ge T-1
\ \mathrm{and}\ I_{success}=0
$$

超时惩罚由固定项和剩余距离项组成：

$$
r_{timeout}
=
-I_{timeout}
\left(
12.0 + 0.5d_t
\right)
$$

配置来源：

| 参数 | 当前值 |
|---|---:|
| `timeout_fixed_penalty` | `12.0` |
| `timeout_distance_penalty_scale` | `0.5` |

工程含义：

- 该项只在 episode 因未成功达到时间上限而 timeout 的最后一步触发一次。
- 固定项用于让“未完成但活到超时”明确变差。
- 距离项使用当前 active waypoint 的剩余距离；如果已完成第一个 waypoint，则自动针对第二个 active waypoint 的剩余距离。
- 当前初始 `10 m` 距离下，未推进 timeout 会额外得到约 `-17.0` 惩罚，可压过原地存活从 `distance_to_target` 和 `angle_diff` 累积到的正回报。

### 7.6 `angle_diff`

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

### 7.7 `action_rate_penalty`

当前动作拆成底盘动作和球铰动作：

$$
a_t=[a_{base,t},a_{joint,t}]
$$

其中：

$$
a_{base,t}=[a_{v,t},a_{\omega,t}]
$$

$$
a_{joint,t}\in\mathbb{R}^{6}
$$

动作变化量：

$$
\Delta a_{base}=a_{base,t}-a_{base,t-1}
$$

$$
\Delta a_{joint}=a_{joint,t}-a_{joint,t-1}
$$

奖励分量：

$$
r_{actionrate}
=
-\frac{1}{T}
\left(
0.05\cdot\mathrm{mean}(\Delta a_{base}^{2})
+
0.02\cdot\mathrm{mean}(\Delta a_{joint}^{2})
\right)
$$

配置来源：

| 参数 | 当前值 |
|---|---:|
| `action_rate_base_weight` | `0.05` |
| `action_rate_joint_weight` | `0.02` |

工程含义：

- 该项惩罚 policy 动作在相邻控制步之间突变，而不是惩罚动作本身的非零大小。
- 底盘二维命令变化权重为 `0.05`，球铰六维目标变化权重为 `0.02`。
- 该项用于鼓励速度、偏航和球铰目标逐步变化；它不会像动作幅值惩罚那样直接鼓励原地不动。
- 直接 `turn_speed_penalty` 和直接 `slip_penalty` 当前已从 active reward 中移除；滑移仍通过 low-slip progress gate 影响正向 progress，并继续作为观测和日志指标。

### 7.8 `load_equalization`

先取 6 个车轮的归一化法向接触力：

$$
F_i=\frac{\|F_{contact,i}\|}{mg}
$$

再换算为当前六轮总接触力内的负载占比：

$$
f_i=
\frac{F_i}
{\max\left(\sum_{j=1}^{6}F_j,\epsilon\right)}
$$

当前目标负载占比为六轮均分：

$$
w_i=\frac{1}{6}
$$

负载均衡误差：

$$
E_{eq}
=
\sum_{i=1}^{6}
\left(
f_i-w_i
\right)^2
$$

归一化惩罚项：

$$
r_{eq}
=
0.0
\cdot
\frac{
1-\exp\left(-10.0E_{eq}\right)
}{T}
$$

配置来源：

| 参数 | 当前值 |
|---|---:|
| `load_equalization_weight` | `0.0` |
| `load_equalization_k` | `10.0` |
| `load_equalization_target_shares` | `(1/6, 1/6, 1/6, 1/6, 1/6, 1/6)` |

工程含义：

- 该项是独立惩罚项，不是 progress gate；六轮越接近目标负载分布，惩罚越接近 `0`。
- 它惩罚六轮负载占比偏离目标分布，当前目标是六轮均分。
- 当前 `load_equalization_weight=0.0`，所以该项只保留诊断计算和日志，不改变总奖励。
- 当前没有把它设为硬约束；如果中车轮长期卸载，该项会体现在 `LoadEqualization/error`，但不会直接扣分或终止 episode。

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
-I_{timeout}(12.0+0.5d_t)
+
6\frac{1}{1+|\theta_t|}\frac{1}{T}
-
\frac{
0.05\cdot\mathrm{mean}(\Delta a_{base}^{2})
+
0.02\cdot\mathrm{mean}(\Delta a_{joint}^{2})
}{T}
+
0.0
\frac{
1-\exp\left(-10.0E_{eq}\right)
}{T}
$$

其中近目标区域有一个额外规则：

$$
d_t \le 3.0
\Rightarrow
\mathrm{clip}(d_{t-1}-d_t,-0.25,0.25)
\text{ 的负值会被置为 }0
$$

其中 low-slip progress gate 为：

$$
M
=
0.25
+
1.25
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
| Reward | `Reward/timeout_penalty` |
| Reward | `Reward/angle_diff` |
| Reward | `Reward/action_rate_penalty` |
| Reward | `Reward/load_equalization` |
| Timeout | `Timeout/remaining_distance_on_timeout` |
| Action | `Action/base_action_delta_abs_mean_raw` |
| Action | `Action/joint_action_delta_abs_mean_raw` |
| Action | `Action/action_rate_base_cost_raw` |
| Action | `Action/action_rate_joint_cost_raw` |
| LoadEqualization | `LoadEqualization/error` |
| LoadEqualization | `LoadEqualization/raw` |
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
| Action | `Action/desired_planar_command_abs_mean_raw` |
| Action | `Action/shaped_planar_command_abs_mean_raw` |
| Action | `Action/planar_command_shaping_delta_abs_mean_raw` |
| Action | `Action/desired_planar_vx_raw` |
| Action | `Action/desired_planar_wz_raw` |
| Action | `Action/shaped_planar_vx_raw` |
| Action | `Action/shaped_planar_wz_raw` |
| Action | `Action/planar_command_delta_vx_raw` |
| Action | `Action/planar_command_delta_wz_raw` |
| Action | `Action/contact_weight_mean_raw` |
| LowLevel | `LowLevel/v_parallel_abs_mean_raw` |
| LowLevel | `LowLevel/v_perp_abs_mean_raw` |
| LowLevel | `LowLevel/delta_v_abs_mean_raw` |
| LowLevel | `LowLevel/tau0_abs_mean_raw` |
| LowLevel | `LowLevel/g_kappa_mean_raw` |
| LowLevel | `LowLevel/tau1_abs_mean_raw` |
| LowLevel | `LowLevel/g_alpha_mean_raw` |
| Observation | `Observation/roll_deg` |
| Observation | `Observation/pitch_deg` |
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
| `PerWheel/<wheel>/v_parallel` | 该车轮轮心实际纵向速度 |
| `PerWheel/<wheel>/v_perp` | 该车轮轮心实际侧向速度 |
| `PerWheel/<wheel>/delta_v` | 车轮圆周速度与实际纵向速度的差值 |
| `PerWheel/<wheel>/tau0` | 基础轮速跟踪力矩 |
| `PerWheel/<wheel>/g_kappa` | 兼容旧日志字段；当前恢复旧力矩控制器后固定为 `1.0` |
| `PerWheel/<wheel>/tau1` | 当前为 `tau0 - K_slip * kappa` 后、乘接触权重前的力矩 |
| `PerWheel/<wheel>/g_alpha` | 兼容旧日志字段；当前恢复旧力矩控制器后固定为 `1.0` |

## 13. 当前结论与使用边界

当前旧的 `2.0 m` 成功半径配置已经由真实训练 run 证明“能学起来”。当前表格记录的是后续收紧后的 active 配置：成功半径已改为 `0.5 m`，第 2 段 waypoint 偏角已要求大于第 1 段；该配置已经完成多轮正式训练验证。

已知边界：

- `0.5 m` 成功半径已经可以训练到高成功率平台，但后段滑移质量仍不达标。
- 第 2 段更大偏角会增强转向需求，可能降低早期成功率。
- 当前直接 `slip_penalty` 与直接 `turn_speed_penalty` 已从 active reward 中移除；新增 `action_rate_penalty`，公式为 `-(0.05*mean(Delta a_base^2)+0.02*mean(Delta a_joint^2))/T`。新增 `timeout_penalty`，公式为 `-I_timeout*(12.0+0.5*d_t)`。low-slip progress gate 仍会让滑移间接影响正向 progress。
- 当前 low-slip progress gate 可以保住高成功率并略降纵滑，但没有把侧滑角压到 `0.5 rad` 或 `30°` 以下。
- 2026-04-26 的新球铰 `q_cmd/qdot_cmd` 联合跟踪链路和低侧滑命令整形训练验证表明，强低侧滑整形可以把后段纵滑降到约 `0.301`、侧滑角降到约 `0.132 rad`，但会把 shaped `vx` 压到 desired `vx` 的约 `10%`，导致 `success_rate=0`、`waypoints_completed_mean=0`。
- 2026-04-26 的 `low_slip_lambda_lateral=2.0` 短训练表明，降低侧滑整形权重可以解除近停滞：后 25 轮 shaped `vx≈0.542 m/s`、`V_parallel≈0.158 m/s`；但低滑移约束明显不足，后 25 轮纵滑约 `1.496`、侧滑角约 `0.530 rad`、综合达标率约 `0.085`，仍没有完成 waypoint。
- 2026-04-26 用户回放 `stage0_lateral2_short150_verify/model_149.pt` 后观察到六个轮子基本不转、车辆在地面上蠕动；随后用户要求将底层车轮力矩控制器恢复到 `stage0_lowslip_gate_v2_min_lowlevel_522iter` 版本，当前已恢复为旧版 `contact_weight * (K_track * (Omega_ref - Omega) - K_slip * kappa)` 公式结构，并将 signed 纵滑方向修正为 `kappa=(r*Omega-V_parallel)/max(|V_parallel|, epsilon)`。
- 2026-04-27 的 `low_slip_lambda_lateral=4.0, ball=1500/30` 短训练表明，该组合能把后 25 轮纵滑降到约 `0.746`、侧滑角降到约 `0.282 rad`，但同时把 `v_parallel_abs` 压到约 `0.041 m/s`，`active_segment_completion_pct` 降到约 `9.71%`，且中车两轮法向力仅约 `0.019 N / 0.019 N`，因此不能作为成功训练方向。
- 当前源码 Stage0 已按用户要求恢复到 `2026-04-25_18-26-58_stage0_lowslip_gate_v1_700iter` 的旧球铰规划器和主要数值参数，但不恢复旧纵滑符号。当前 active reward 进一步改为移除直接 `slip_penalty` 与直接 `turn_speed_penalty`，并加入 `action_rate_base_weight=0.05`、`action_rate_joint_weight=0.02`、`timeout_fixed_penalty=12.0`、`timeout_distance_penalty_scale=0.5`。其他关键生效参数为 `low_slip_lambda_lateral=5.0`、`load_equalization_weight=0.0`、`K_track=2.0`、`K_slip=4.0`、`wheel_joint_effort_limit_sim=20.0`、`ball_joint_stiffness=8000.0`、`ball_joint_damping=1000.0`、`ball_joint_effort_limit_sim=20.0`。球铰规划器回到 allocator 内部旧一阶链路：`qdot_cmd=clip(K*(q_des-q), ±1.0)`，`q_cmd=clip(q+dt*qdot_cmd, q_min, q_max)`；不再使用 env 层 `q_ref/qddot` 轨迹整形。PhysX 球铰 drive 仍只接收 `q_cmd` 位置目标；`qdot_cmd` 只供轮速分配使用。Stage0 球铰姿态边界为 yaw `±0.6 rad`、pitch 下限/上限 `-1.0/0.4 rad`、roll `±0.5 rad`。
- 2026-04-27 严格核对发现：当前 `progress_gate` 组合公式仍是后续 v2 的 $\min(G_\kappa,G_\alpha)$，而 `2026-04-25_18-26-58` 旧 run 使用的是 $0.5(G_\kappa+G_\alpha)$。因此当前源码不是对 `2026-04-25_18-26-58` 的奖励结构严格复现。
- 2026-04-27 针对 `model_375.pt` 的 headless 回放参数扫描表明：只降低 `Kp/Kd/qdot/qddot` 最多只能把中车载荷占比提升到约 `5.0%`；将 pitch/roll 近似锁定后，中车载荷占比可恢复到约 `27.5%-33.3%`，双中轮法向力约 `63-94 N`，但旧 checkpoint 的 waypoint 进度基本坍缩。该接地修正已按用户后续要求从 active 源码撤回，作为历史诊断结论保留。
- 2026-04-27 的 `low_slip_lambda_lateral=0.0, slip_penalty_weight=0.0, ball=1500/30` 对照训练在 iteration `393/700` 按成功率平台期早停，确认目标完成能力恢复：后 25 轮 `success_rate≈0.965`、episode 级 `waypoint_completion_pct≈97.41%`；但后 25 轮纵滑约 `2.308`、侧滑角约 `0.714 rad`、`LowSlip/combined_pass_rate≈0.0064`，且中车载荷占六轮总法向力仅约 `2.08%`。因此该配置是“恢复跑起来”的对照结果，不是低滑移完成方案。
- 最近一轮已完成诊断的 `lambda_lat=10.0, K_track=2.0, K_slip=1.5` 短训练仍表现为低滑移近停滞：后段低滑移指标改善，但 `waypoints_completed_mean=0.0`，中车轮组接近卸载；因此该参数组合尚不能作为成功训练结果。
- 历史对照中的 `lambda_lat=0.0` 已验证可以在去掉直接 `slip_penalty` 后恢复 waypoint 完成能力；当前 active 源码已经回到 `lambda_lat=5.0`，不是关闭低层横向滑移整形的对照配置。
- 因此当前不能只追求更低滑移；下一轮必须把低滑移与实际 waypoint progress 或非零前进速度绑定，避免“原地低滑移”成为局部最优。
- 当前没有地形传感器、课程学习、高度 patch 或复杂地形输入。
- 当前没有 `next_turn_delta`，策略看不到下一段转向预告。
- 当前没有 `differential_turn_cost`，也没有 preview-based penalty scaling。
- 旧指标 `Tracking/goal_success_rate`、`Tracking/goal_pos_error`、`Tracking/goal_heading_error_abs`、`Tracking/goal_completion_pct` 已移除，避免把 active waypoint 指标误读为最终目标指标。
- 旧 `Observation/tilt_deg` 实际记录中车 roll 绝对值；当前重点保留 `Observation/roll_deg` 和 `Observation/pitch_deg`，不再使用 `Observation/tilt_deg` 或 `Observation/pitch_abs_deg` 作为 TensorBoard 重点指标。

后续推进原则：

- 若继续分析当前低层链路，应优先回放最近的短训练 checkpoint，确认中车轮组低载荷、车辆近停滞与低层整形之间的关系。
- 若继续沿 `low_slip_lambda_lateral` 调参，`10.0`、`5.0`、`2.0` 和 `0.0` 应作为已有边界点；当前源码 `5.0` 是恢复旧参数后的 active 配置。
- 若继续低滑移优化，应先决定 low-slip 是评价指标、奖励偏好，还是成功条件的一部分。
- 在确认 per-wheel 诊断后，再讨论是否修改 gate、低层 allocator、终止条件或训练课程。
