# Stage0 lowslip gate v1 model_699 训练结果、RL 配置与底层运动模型说明

生成日期：2026-04-28
目标 checkpoint：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_18-26-58_stage0_lowslip_gate_v1_700iter/model_699.pt`

## 1. 结论先行

这次训练是目前历史记录中综合表现最好的可回放 Stage0 checkpoint 之一：最终 `model_699.pt` 的双 waypoint 任务成功率很高，后 25 个 iteration 的 `success_rate≈0.9863`、episode 级 waypoint 完成率约 `99.21%`，说明 policy 已经学会在平地上完成目标点到达任务。

但它不能被解释为“低滑移策略已经学成”。后 25 个 iteration 的纵向滑移均值约 `2.739`，明显高于 low-slip 阈值 `1.0`；旧口径侧滑角均值约 `0.691 rad`，也高于阈值 `0.35 rad`。更重要的是，2026-04-28 后已确认 2026-04-25 这批历史 run 的侧滑角使用 wheel local `Y` 作为侧向轴，而该轴接近竖直方向，不是真实水平侧向轴。因此本文中所有 `wheel_slip_angle`、`ProgressGate/slip_angle_gate`、`LowSlip/slip_angle_*` 都必须标为“历史旧口径”，不能作为真实水平侧滑证据。

本轮的底层运动模型是 2026-04-25 当时的低层力矩控制链路：policy 输出 8 维动作，先映射为底盘平面命令和六个等效球铰目标姿态，再经过低侧滑平面命令整形、轮速参考分配和纵滑反馈，最终对球铰下发位置目标、对六个车轮下发 effort target。它不是 2026-04-28 后当前 active 代码中的直接 wheel velocity target 链路。

## 2. 数据来源与版本边界

本报告使用以下本地数据重建该 run 的实际语义：

- run 目录：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_18-26-58_stage0_lowslip_gate_v1_700iter`
- checkpoint：`model_699.pt`
- 环境配置：`params/env.yaml`
- PPO 配置：`params/agent.yaml`
- TensorBoard 导出：`tensorboard_export/`
- run 内保存的源码状态：`git/Graduation-Project.diff`
- run 对应 git commit：`67e7d85173999cbf5916e6d52734b2d235170e1c`
- 已有诊断报告：`results/stage0_lowslip_gate_v1_700iter_diagnosis_2026-04-25.md`

需要注意：当前工作区代码已经经历 2026-04-27 到 2026-04-28 的多轮修改，不能直接用当前 `env.py` 解释这个历史 checkpoint。本报告按“git commit `67e7d851...` + run 内 diff + run 保存的 yaml 配置”解释 2026-04-25 当时实际运行的函数链路。

## 3. 运行配置

训练命令：

```bash
/home/ubuntu/IsaacLab/isaaclab.sh -p scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --max_iterations 700 --run_name stage0_lowslip_gate_v1_700iter
```

基础信息：

| 项目 | 数值 |
|---|---:|
| 任务 | `CompleteCar-Stage0` |
| run name | `stage0_lowslip_gate_v1_700iter` |
| 并行环境数 | `64` |
| 最大 iteration | `700` |
| 实际完成 | `699/700`，正常结束 |
| 保存间隔 | `25` iteration |
| 最终 checkpoint | `model_699.pt` |
| actor 观测维度 | `54` |
| critic 观测维度 | `54` |
| action 维度 | `8` |
| device | `cuda:0` |
| seed | `1` |

仿真与控制频率：

| 项目 | 数值 | 含义 |
|---|---:|---|
| `sim.dt` | `0.0083333333 s` | 物理步长，约 120 Hz |
| `decimation` | `2` | 每个 RL action 持续 2 个物理步 |
| `control_dt` | `0.0166666667 s` | RL 控制周期，约 60 Hz |
| `episode_length_s` | `40.0 s` | 单 episode 上限 |
| 最大控制步 | 约 `2400` step | 40 秒乘 60 Hz |

场景与目标：

| 项目 | 数值 | 含义 |
|---|---:|---|
| 地形 | `plane` | 平地训练，不是 Stage1 复杂地形 |
| `terrain.enabled` | `false` | 训练未启用地形生成器 |
| `terrain.measure_heights` | `false` | policy 不使用高度图 |
| `num_waypoints_per_episode` | `2` | 每个 episode 两段目标点 |
| `goal_distance` | `10.0 m` | 每段目标距离 |
| `goal_direction_max_deg` | `30 deg` | 目标方向相对当前朝向的最大偏角 |
| `goal_heading_delta_max_deg` | `0 deg` | 目标 heading 不额外变化 |
| `target_position_tolerance` | `0.5 m` | 命中 waypoint 的位置半径 |
| `resampling_time` | `40.0 s` | 与 episode 上限一致 |

终止语义：

| 条件 | 当时实际含义 |
|---|---|
| `is_success` | 命中最后一个 waypoint，且当前位置误差 `<0.5 m` |
| `far_from_target` | 当前目标距离大于 `goal_distance + far_from_target_margin`，即大于 `16 m` |
| `ball_joint_out_of_bounds` | 六个等效球铰任一超过配置上下限 |
| `time_out` | episode 达到最大步数且尚未 success |

`target_yaw_tolerance_deg`、`orientation_limit_deg`、`head_tail_roll_limit_deg`、`head_tail_pitch_limit_deg` 在该 run 的配置中存在，但从当时 `mdp/terminations.py` 的实际代码看，success 只检查位置半径和 waypoint 序号，不检查 yaw tolerance；姿态角限制也没有实际并入 `terminated`。因此不能把这轮结果解释成“位置 + 朝向 + 姿态”都严格达标的成功，只能解释成“位置型双 waypoint 到达成功”。

另外，该 run 的 `is_finite_horizon=false`。在当时 RSL-RL 语义下，`time_out` 会作为 `time_outs` 进入 PPO 的 time-limit bootstrap 流程，而不是作为失败终止直接截断 value target。这一点和 2026-04-28 后用户确认的当前语义不同；当前 active Stage0 已改成 timeout 失败终止、不再让 PPO bootstrap。

## 4. PPO / RL 配置

PPO runner：

| 项目 | 数值 |
|---|---:|
| runner | `OnPolicyRunner` |
| algorithm | `PPO` |
| `num_steps_per_env` | `512` |
| 每个 iteration 采样量 | `64 * 512 = 32768` step |
| `max_iterations` | `700` |
| `save_interval` | `25` |
| logger | `tensorboard` |
| resume | `false` |

网络结构：

| 部分 | 配置 |
|---|---|
| actor | MLP，`54 -> 256 -> 256 -> 8` |
| critic | MLP，`54 -> 256 -> 256 -> 1` |
| 激活函数 | `relu` |
| obs normalization | `true` |
| action distribution | `SquashedGaussianDistribution` |
| 初始 std | `0.2` |
| `log_std_min` | `-4.0` |
| `log_std_max` | `0.0` |

PPO 超参数：

| 参数 | 数值 | 含义 |
|---|---:|---|
| `num_learning_epochs` | `5` | 每批 rollout 重复优化次数 |
| `num_mini_batches` | `16` | 每轮优化切分的 mini-batch 数 |
| `learning_rate` | `1e-4` | 初始学习率 |
| `schedule` | `adaptive` | 学习率随 KL 自适应 |
| `desired_kl` | `0.008` | 自适应学习率的目标 KL |
| `gamma` | `0.99` | 折扣因子 |
| `lam` | `0.95` | GAE 参数 |
| `entropy_coef` | `0.0005` | 探索熵权重 |
| `value_loss_coef` | `0.5` | value loss 权重 |
| `clip_param` | `0.2` | PPO ratio clip |
| `max_grad_norm` | `0.5` | 梯度裁剪 |
| `use_clipped_value_loss` | `true` | 使用 clipped value loss |

观测向量共 `54` 维，按当时代码拼接为：

| 分量 | 维度 | 含义 |
|---|---:|---|
| `ball_joint_pos` | `6` | 六个等效球铰当前位置 |
| `ball_joint_vel` | `6` | 六个等效球铰角速度 |
| `base_lin_vel` | `3` | 车体根部线速度，body frame |
| `base_ang_vel` | `3` | 车体根部角速度，body frame |
| `wheel_joint_vel` | `6` | 六轮角速度 |
| `wheel_longitudinal_slip` | `6` | 六轮纵向滑移，历史符号口径 |
| `wheel_slip_angle` | `6` | 六轮侧滑角，2026-04-25 旧轴向口径 |
| `wheel_normal_contact_force` | `6` | 六轮归一化法向接触力 |
| `relative_goal_commands` | `4` | 目标在车体系下的相对位置与 heading |
| `last_actions` | `8` | 上一步 policy action |

动作向量共 `8` 维：

| action 分量 | 维度 | 映射后物理含义 |
|---|---:|---|
| `a0` | `1` | 期望前向速度命令 `v_x^d`，范围约 `[-2, 2] m/s` |
| `a1` | `1` | 期望 yaw rate 命令 `omega_z^d`，范围约 `[-2, 2] rad/s` |
| `a2:a7` | `6` | 六个等效球铰目标姿态 `q^d` |

球铰 action 的顺序是：

```text
spm1_platform_joint_z
spm1_platform_joint_y
spm1_platform_joint_x
spm2_platform_joint_z
spm2_platform_joint_y
spm2_platform_joint_x
```

## 5. 底层运动模型

### 5.1 机器人模型抽象

该 Stage0 环境使用三车体、六轮、两个等效球铰连接的 articulated ground vehicle：

- front body / middle body / rear body；
- 六个车轮；
- 两组 spherical-parallel-joint-inspired 连接机构；
- 在仿真中把每组复杂并联机构等效为串联旋转自由度；
- policy 控制的结构自由度是六个等效球铰关节；
- USD 文件为 `USD/complete_car.usd`。

当时 articulation 初始化日志显示机器人正常加载为 `17` 个 body、`12` 个 joint，其中 `6` 个球铰相关 joint 和 `6` 个 wheel joint 被 actuator collection 正常解析。

### 5.2 actuator 配置

球铰：

| 参数 | 数值 | 含义 |
|---|---:|---|
| actuator | `ImplicitActuator` | PhysX 隐式驱动 |
| `stiffness` | `8000.0` | 球铰位置驱动刚度 |
| `damping` | `1000.0` | 球铰位置驱动阻尼 |
| `effort_limit_sim` | `20.0` | 最大力矩限制 |
| `velocity_limit_sim` | `1.0` | 最大角速度限制 |

车轮：

| 参数 | 数值 | 含义 |
|---|---:|---|
| actuator | `ImplicitActuator` |
| `stiffness` | `0.0` |
| `damping` | `0.0` |
| `effort_limit_sim` | `20.0` |
| `velocity_limit_sim` | `20.0` |

这轮历史 run 中车轮不是靠 velocity drive 主动跟踪速度，而是由低层分配器计算 wheel torque target，最后通过 `set_joint_effort_target()` 下发 effort target。因为车轮 actuator 的 stiffness/damping 为 `0`，实际车轮运动主要由下发力矩和接触动力学决定。

### 5.3 policy action 到 PhysX 下发的实际链路

当时实际运行链路为：

```text
PPO actor action
  -> map_base_actions_to_planar_command()
  -> map_ball_joint_actions_to_desired_positions()
  -> compute_low_slip_control_targets()
       -> compute_ball_joint_planner_outputs()
       -> compute_wheel_kinematic_state()
       -> shape_planar_command_for_low_slip()
       -> compute_wheel_speed_references()
       -> compute_wheel_traction_targets()
  -> apply_ball_joint_position_targets()
  -> apply_wheel_effort_targets()
  -> robot.set_joint_position_target(ball joints)
  -> robot.set_joint_effort_target(wheels)
```

具体含义如下。

第一步，policy 的前两个 action 映射为平面运动命令：

$$
u^d = [v_x^d, \omega_z^d]
$$

其中 `base_forward_velocity_max=2.0`，`base_yaw_rate_max=2.0`，`base_allow_reverse=true`，所以 `a0=-1` 到 `1` 对应 `v_x^d=-2` 到 `2 m/s`，`a1=-1` 到 `1` 对应 `omega_z^d=-2` 到 `2 rad/s`。

第二步，policy 的后六个 action 映射为六个球铰期望姿态 `q^d`。当时球铰位置上下限为：

```text
lower = [-0.6, -1.0, -0.5, -0.6, -1.0, -0.5]
upper = [ 0.6,  0.4,  0.5,  0.6,  0.4,  0.5]
```

第三步，球铰一阶规划器把 `q^d` 转为下一控制周期的位置目标：

$$
\dot q^{cmd} = \operatorname{clip}(K(q^d - q), -\dot q_{\max}, \dot q_{\max})
$$

$$
q^{cmd} = q + \Delta t \dot q^{cmd}
$$

本轮中 `K=10.0`，`\dot q_max=1.0 rad/s`，`\Delta t=1/60 s`。

第四步，低侧滑平面命令整形器并不是直接执行 policy 给出的 `u^d`，而是在保持接近期望命令的同时，降低六轮名义侧向速度。其核心可以理解为求解一个 2 维二次优化问题：

$$
\min_u
\lambda_{track}\|u-u^d\|^2
+
\lambda_{lat}\sum_i w_i (n_i^T(v_i(u,\dot q^{cmd})))^2
$$

其中：

- `u=[v_x, omega_z]` 是整形后的平面命令；
- `w_i` 是第 `i` 个车轮的接触权重；
- `n_i` 是第 `i` 个车轮的侧向方向；
- `v_i` 是由底盘平动、yaw 转动和球铰姿态变化共同决定的车轮中心名义速度；
- `lambda_tracking=1.0`；
- `lambda_lateral=5.0`。

这一步的作用是：不让底层无条件执行 policy 的平面速度，而是试图在轮-地接触约束下选一个侧向速度成本更小的 `v_x / omega_z` 组合。

第五步，轮速参考由车轮滚动方向上的名义速度给出：

$$
\Omega_i^{ref} = \frac{t_i^T v_i}{r}
$$

其中 `r=0.19 m` 是车轮半径，`t_i` 是第 `i` 个车轮滚动方向。

第六步，计算历史口径纵向滑移：

$$
\kappa_i = \frac{v_{\parallel,i} - r\Omega_i}{\max(|v_{\parallel,i}|,\epsilon)}
$$

其中 `epsilon=0.1`。注意这是 2026-04-25 当时的纵滑符号口径；后续项目中曾调整过纵滑方向定义。由于这轮报告多数使用的是 `abs_mean` 或平方 gate，符号方向不影响纵滑大小和 low-slip gate 量级，但会影响“驱动/制动滑移”的物理方向解释。

第七步，轮级 traction allocator 生成车轮力矩：

$$
\tau_i =
\operatorname{clip}
\left(
w_i
\left[
K_{\omega}(\Omega_i^{ref}-\Omega_i)
-
K_{\kappa}\kappa_i
\right],
-20,20
\right)
$$

其中：

- `K_omega=wheel_torque_tracking_gain=2.0`；
- `K_kappa=wheel_slip_feedback_gain=4.0`；
- `w_i` 来自法向接触力阈值 `0.01 -> 0.08` 的线性接触权重；
- `20` 是车轮 effort limit。

因此，这轮 run 的车轮动作实际是“轮速参考 + 纵滑反馈 + 接触权重”共同产生的力矩目标，不是 policy 直接控制车轮角速度。

### 5.4 旧侧滑角定义

该 run 中观测和 reward 使用的侧滑角来自：

$$
\alpha_i = \operatorname{atan2}(v_{\perp,i}^{old}, |v_{\parallel,i}|+\epsilon)
$$

其中 `v_parallel` 使用 wheel local `X` 投影，`v_perp_old` 使用 wheel local `Y` 投影。2026-04-28 对 USD 车轮几何复查后确认，wheel local `Y` 接近竖直方向，wheel local `Z` 才是更合理的水平轮轴/侧向方向。因此该 run 的 `alpha_i` 更接近“混入竖直运动的旧侧滑指标”，不能直接代表真实水平侧滑。

## 6. 奖励函数结构

这轮 run 的 reward 项共 7 个：

```text
distance_to_target
progress_to_target
reached_target
far_from_target
angle_diff
turn_speed_penalty
slip_penalty
```

权重如下：

| 参数 | 数值 |
|---|---:|
| `distance_to_target_weight` | `6.0` |
| `progress_to_target_weight` | `8.0` |
| `progress_to_target_clip_m` | `0.25` |
| `progress_to_target_relax_radius_m` | `4.0` |
| `reached_target_base_reward` | `2.0` |
| `reached_target_weight` | `6.0` |
| `far_from_target_margin` | `6.0` |
| `far_from_target_weight` | `-2.0` |
| `angle_diff_weight` | `6.0` |
| `turn_speed_penalty_weight` | `-2.0` |
| `slip_penalty_weight` | `-2.0` |
| `slip_angle_penalty_ratio` | `6.0` |

### 6.1 progress gate

原始 progress 是当前帧目标距离减少量：

$$
\Delta d = d_{prev} - d_{now}
$$

先裁剪到 `[-0.25, 0.25] m`。当距离目标小于 `4.0 m` 时，负 progress 会被截到 `0`，避免近目标区域反复转向导致过强负信号。

正向 progress 和负向 progress 分开处理：

$$
p^+ = \frac{\max(\Delta d,0)}{d_{goal}}
$$

$$
p^- = \frac{\min(\Delta d,0)}{d_{goal}}
$$

纵滑 gate：

$$
G_{\kappa} =
\exp\left(
-0.5 \sum_i
\left(
\frac{\kappa_i}{3.0}
\right)^2
\right)
$$

旧口径侧滑角 gate：

$$
G_{\alpha} =
\prod_i
\left[
0.5\cos
\left(
\operatorname{clip}
\left(
\frac{\pi|\alpha_i|}{1.5},
0,
\pi
\right)
\right)
+ 0.5
\right]
$$

综合 gate 使用平均值：

$$
G = 0.5(G_{\kappa}+G_{\alpha})
$$

progress multiplier：

$$
M = 0.25 + (1.5 - 0.25)G
$$

最终 progress reward 的内部量为：

$$
p = M p^+ + p^-
$$

也就是说，该 gate 只削弱正向 progress；如果车远离目标，负 progress 不会被 gate 减弱。这个设计比“直接奖励 raw vx”更合理，因为它奖励的是目标距离减少，而不是车体速度本身。但它仍是 soft shaping，不是硬约束；当 `M` 保留 `0.25` 下限时，高滑移策略仍能保留一部分正向 progress 奖励。

### 6.2 reached target

命中 waypoint 时：

$$
r_{hit} = 1_{hit} \cdot 2.0 \cdot \frac{T-t}{T}
$$

再乘 `reached_target_weight=6.0`。所以越早命中，终点奖励越大。这个项是本轮高成功率的重要驱动力，但它没有绑定低滑移、姿态稳定或真实水平侧滑约束。

### 6.3 slip penalty

滑移惩罚为：

$$
r_{slip}
=
-2.0
\cdot
\frac{
\operatorname{mean}(|\kappa|)
+
6.0\operatorname{mean}(|\alpha|)
}{T}
$$

其中 `alpha` 是历史旧侧滑角口径。该项确实对高滑移有惩罚，但它按 `T` 归一化到每步，后段实际量级仍小于完成任务带来的收益，因此没有阻止 policy 用较高滑移完成目标。

## 7. 训练结果

核心训练指标：

| 指标 | 开始 | iteration 699 | 后 115 轮均值 | 后 25 轮均值 |
|---|---:|---:|---:|---:|
| `Train/mean_reward` | `-1.919` | `21.778` | `20.785` | `21.590` |
| `Train/mean_episode_length` | `253.765` | `876.320` | `990.009` | `900.831` |
| `success_rate` | `0.000` | `0.9766` | `0.9592` | `0.9863` |
| `time_out_rate` | `0.8809` | `0.0234` | `0.0408` | `0.0137` |
| `episode/waypoints_completed` | `0.000` | `1.9766` | `1.9503` | `1.9841` |
| `episode/waypoint_completion_pct` | `0.000%` | `98.828%` | `97.512%` | `99.207%` |
| `episode/success_hit_pos_error` | `0.499 m` | `0.490 m` | `0.490 m` | `0.490 m` |

成功率里程碑：

| 事件 | iteration |
|---|---:|
| 第一次 `success_rate >= 0.5` | `202` |
| 第一次 `success_rate >= 0.8` | `404` |
| 第一次 `success_rate >= 0.9` | `534` |
| 第一次 `success_rate = 1.0` | `555` |
| 第一次 25 轮滑动平均 `success_rate >= 0.95` | 窗口结束于 `602` |
| 第一次 50 轮滑动平均 `success_rate >= 0.95` | 窗口结束于 `627` |
| 最长连续满成功 | `688-698`，连续 `11` 轮 |

这说明 `model_699.pt` 处于高成功平台末端。它不是完全无波动的平台，后 115 轮内仍出现过低于平台均值的波动，但后 25 轮成功率已经接近满成功。

## 8. 奖励分解与 gate 实际状态

后 25 轮中，各主要 reward 项的每步贡献约为：

| 项 | 后 25 轮均值 |
|---|---:|
| `progress_to_target` | `0.00675` |
| `reached_target` | `0.01947` |
| `distance_to_target` | `0.00185` |
| `angle_diff` | `0.00196` |
| `slip_penalty` | `-0.00574` |
| `turn_speed_penalty` | `-0.00027` |

progress gate 的实际数值：

| 指标 | iteration 699 | 后 115 轮均值 | 后 25 轮均值 |
|---|---:|---:|---:|
| `ProgressGate/combined_gate` | `0.1133` | `0.1146` | `0.1139` |
| `ProgressGate/multiplier` | `0.3917` | `0.3933` | `0.3924` |
| `ProgressGate/longitudinal_gate` | `0.1970` | `0.1936` | `0.1963` |
| `ProgressGate/slip_angle_gate` | `0.0297` | `0.0356` | `0.0314` |

解释：

- gate 确实在起作用，高滑移时正向 progress 只保留约 `39%` 的倍率。
- 但 `M_min=0.25` 提供了保底，综合 gate 又使用平均值，所以即使旧侧滑 gate 很低，策略仍有可学习的正向 progress 信号。
- `reached_target` 的后段贡献约为 `0.01947`，大于 `slip_penalty` 的绝对值约 `0.00574`，因此高滑移命中目标在总回报上仍然划算。

## 9. 滑移与运动质量

low-slip 指标：

| 指标 | 开始 | iteration 699 | 后 115 轮均值 | 后 25 轮均值 |
|---|---:|---:|---:|---:|
| 纵向滑移均值 | `9.048` | `2.719` | `2.808` | `2.739` |
| 旧口径侧滑角均值 | `0.518 rad` | `0.690 rad` | `0.680 rad` | `0.691 rad` |
| `LowSlip/longitudinal_slip_pass_rate` | `0.035` | `0.114` | `0.114` | `0.114` |
| `LowSlip/slip_angle_pass_rate` | `0.186` | `0.024` | `0.034` | `0.029` |
| `LowSlip/combined_pass_rate` | `0.006` | `0.012` | `0.014` | `0.013` |

运动执行相关指标：

| 指标 | 后 25 轮结论 |
|---|---:|
| 轮速参考均值 | 约 `6.343 rad/s` |
| wheel torque target 均值 | 约 `2.615` |
| tilt | 约 `0.817 deg` |
| `spm1_platform_joint_x_limit_usage_max` | 最终约 `0.877` |
| `spm2_platform_joint_z_limit_usage_max` | 最终约 `0.765` |

从这些指标看，车体姿态没有明显失稳，球铰也未触发越界终止，但 policy 在成功平台期使用了比较激进的关节姿态和较高轮速/滑移。它完成了 waypoint，但完成方式不是低滑移完成方式。

## 10. 数值稳定性

PPO 数值状态：

| 指标 | 结果 |
|---|---:|
| value loss | 开始 `0.0096`，最终 `0.0286`，最大约 `0.2002` |
| surrogate loss | 开始 `0.0218`，最终 `-0.0111` |
| entropy | 从 `-1.524` 降到 `-4.107` |
| policy mean std | 从 `0.2000` 降到 `0.1456` |
| 平均 FPS | 约 `4005 steps/s` |
| 最终 FPS | 约 `3969 steps/s` |

没有看到 NaN、训练崩溃、articulation 初始化失败或 PPO 明显发散。策略分布逐步变窄，但没有塌缩到接近零动作。

## 11. 与 lowslip penalty v1 的对比

和 `2026-04-25_15-42-10_stage0_lowslip_penalty_v1_700iter/model_699.pt` 的后 25 轮相比：

| 指标 | penalty v1 后 25 轮 | gate v1 后 25 轮 | gate v1 变化 |
|---|---:|---:|---:|
| `success_rate` | `0.9757` | `0.9863` | `+0.0107` |
| `Train/mean_reward` | `26.575` | `21.590` | `-4.985` |
| 纵向滑移均值 | `2.899` | `2.739` | `-0.160` |
| 旧口径侧滑角均值 | `0.685 rad` | `0.691 rad` | `+0.006 rad` |
| `LowSlip/combined_pass_rate` | `0.0179` | `0.0131` | `-0.0048` |
| `LowSlip/longitudinal_slip_pass_rate` | `0.0993` | `0.1144` | `+0.0151` |
| `LowSlip/slip_angle_pass_rate` | `0.0449` | `0.0286` | `-0.0163` |
| 轮速参考均值 | `6.889` | `6.343` | `-0.546` |

gate v1 的确略微降低轮速参考和纵向滑移，同时保持了更高的任务成功率。但它没有改善旧口径侧滑角，综合 low-slip pass rate 反而更低。因此 gate v1 的有效贡献应表述为“在不破坏任务成功率的情况下略微压低纵滑和轮速”，不能表述为“学成低滑移控制”。

## 12. 对 thesis / 实验结论的可用性

这轮结果可以支撑的结论：

- Stage0 平地双 waypoint 到达任务是可学习的；
- 8 维动作空间，即 `v_x / omega_z` 加六个等效球铰姿态，能够训练出可回放的高成功策略；
- 低层力矩分配链路在工程上能闭环运行，没有阻断 policy 学习；
- progress gate 不会像过强硬约束那样直接摧毁任务学习。

这轮结果不能支撑的结论：

- 不能证明车辆已经学会低纵滑控制；
- 不能证明车辆已经学会低水平侧滑控制；
- 不能证明球铰协同本身带来了稳定性或通过性优势；
- 不能作为 Stage1 地形适应性的证据，因为本轮训练地形是平地；
- 不能用旧侧滑角曲线直接比较 2026-04-28 之后修正轴向口径的新 run。

最准确的定位是：`model_699.pt` 是一个高成功率、可回放、工程链路有效的 Stage0 历史 checkpoint；它适合作为“任务能跑通”的参考，不适合作为“低滑移协同控制已经成功”的最终证据。

## 13. 回放与引用建议

如果需要回放该 checkpoint，应明确记录：

```text
run:
RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_18-26-58_stage0_lowslip_gate_v1_700iter

checkpoint:
model_699.pt
```

回放时可以重点观察：

- 是否稳定命中两个 waypoint；
- 运动是否存在明显侧漂、绕圈或轮胎空转；
- 球铰是否长期贴近限位；
- 车轮是否出现较高转速而车体有效推进不足；
- 如果使用 2026-04-28 之后的修正侧滑口径重新探针评估，应单独标注为“新口径 replay probe”，不要和该 run 原始 TensorBoard 的旧侧滑角混合。

论文或答辩中引用时建议使用保守表述：

> 在 Stage0 平地双 waypoint 任务中，历史 lowslip gate v1 策略能够达到接近满成功率，说明 RL 控制链路和动作空间具备完成基础目标跟踪任务的能力。但该策略仍伴随较高纵向滑移，且历史侧滑角指标存在轴向口径问题，因此不能作为低滑移协同控制成功的直接证据。
