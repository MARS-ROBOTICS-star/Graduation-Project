# Stage0 lowlevel diagnostics metrics v2 训练诊断报告

日期：2026-04-26  
对象：Stage0 新底层控制链路 + 新 TensorBoard 诊断指标验证训练  
结论等级：本轮不能作为成功训练结果；可以作为低层诊断指标和低滑移局部最优的有效证据。

## 1. Run 信息

| 项目 | 内容 |
|---|---|
| run | `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-26_18-17-37_stage0_lowlevel_diagnostics_metrics_v2_800iter` |
| 原计划 iteration | `800` |
| 实际停止 iteration | `209/800` |
| 停止方式 | 用户要求停止后手动中断，训练正常退出 |
| 最新 checkpoint | `model_200.pt` |
| TensorBoard 导出目录 | `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-26_18-17-37_stage0_lowlevel_diagnostics_metrics_v2_800iter/tensorboard_export` |
| Isaac Lab log | `/tmp/isaaclab/logs/isaaclab_2026-04-26_18-17-37.log` |
| 并行环境数 | `64` |
| 每回合长度 | `40 s` / `2400` 控制步 |
| PPO 保存间隔 | `25` iterations |

已保存 checkpoint：

| checkpoint |
|---|
| `model_0.pt` |
| `model_25.pt` |
| `model_50.pt` |
| `model_75.pt` |
| `model_100.pt` |
| `model_125.pt` |
| `model_150.pt` |
| `model_175.pt` |
| `model_200.pt` |

Isaac log 未发现 `Error`、`Warning`、`Traceback`。仿真端加载正常，车轮 effort limit 为 `15 N*m`，球铰 effort limit 为 `20 N*m`，球铰 stiffness/damping 为 `1000/10`。

## 2. 总结论

本轮训练把纵滑和侧滑显著压低了，但代价是车辆几乎不向 waypoint 前进。策略期望的前进命令仍然存在，但低层加权最小二乘整形和低滑移控制链把实际执行命令压到很小，导致车辆进入“低滑移、低速度、低任务完成度”的局部解。

| 结论项 | 结果 |
|---|---|
| 任务完成 | 失败 |
| 最后一轮 `success_rate` | `0.0000` |
| 后 25 轮 `success_rate` | `0.0000` |
| 最后一轮 `time_out_rate` | `1.0000` |
| 后 25 轮 `waypoints_completed_mean` | `0.0000` |
| 后 25 轮 `episode_completion_pct` | `0.0000%` |
| 后 25 轮 `active_waypoint_pos_error` | `9.834 m` |
| 后 25 轮纵滑均值 | `0.301` |
| 后 25 轮侧滑角均值 | `0.132 rad` / `7.59°` |
| 后 25 轮 low-slip 综合达标率 | `0.986` |
| 后 25 轮 progress gate multiplier | `1.251` |
| 后 25 轮 policy desired `vx` | `0.966 m/s` |
| 后 25 轮 shaped `vx` | `0.100 m/s` |
| 后 25 轮实际轮心纵向速度 `V_parallel` | `0.016 m/s` |

关键判断：

- 低滑移指标达标不是因为学会了低滑移完成任务，而是因为车辆近似静止。
- progress gate 不是当前主要瓶颈；后段 multiplier 已经升到约 `1.25`，没有压在 `0.10` 下限。
- 任务失败的直接原因是正向进度接近零：`positive_progress_raw` 后 25 轮约 `1.75e-5`。
- 当前 reward 后段升到约 `5.54`，但成功率和 waypoint 完成度为零，说明 reward 已经被生存、低滑移和持续项局部最优误导，不能用总 reward 判断任务成功。
- 中左轮后段 `contact_weight=0`、`normal_force=0`、最终 `wheel_torque_target=0`，说明该轮处于无有效接触状态，不是单纯“电机不转”。

## 2.1 当前生效奖励函数与参数

本节记录该 run 的实际生效 reward 口径，参数来自：

`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-26_18-17-37_stage0_lowlevel_diagnostics_metrics_v2_800iter/params/env.yaml`

### 2.1.1 任务与归一化参数

| 参数 | 当前值 | 作用 |
|---|---:|---|
| `num_waypoints_per_episode` | `2` | 每个 episode 两个连续 waypoint |
| `goal_distance` | `10.0 m` | 每段 waypoint 名义距离，也是 progress 归一化距离 |
| `goal_direction_max_deg` | `30.0°` | 每段目标方向最大偏角，也是转向强度归一化角度 |
| `resampling_time` | `40.0 s` | 与 episode 时长一致 |
| `control_dt` | `1 / 60 s` | RL 控制周期 |
| `max_episode_length` | `2400` steps | 每个 episode 最大控制步数 |
| `target_position_tolerance` | `0.5 m` | waypoint 命中距离 |
| `base_forward_velocity_max` | `2.0 m/s` | 转向速度惩罚中的速度归一化上限 |
| `only_positive_rewards` | `false` | 总 reward 不做非负裁剪 |

记 $T=2400$，$t$ 为当前 episode 控制步，$d_t$ 为当前 active waypoint 平面距离，$\theta_t$ 为当前目标点在车体系下的视线方向误差：

$$
d_t=\sqrt{x_g^2+y_g^2}
$$

$$
\theta_t=\mathrm{wrap}(commands[:,3])
$$

当前总奖励由 7 项相加：

$$
r=
r_{dist}
+r_{prog}
+r_{hit}
+r_{far}
+r_{angle}
+r_{turnspeed}
+r_{slip}
$$

### 2.1.2 奖励参数总表

| 参数 | 当前值 | 对应项 |
|---|---:|---|
| `distance_to_target_denominator_scale` | `0.01` | `distance_to_target` |
| `distance_to_target_weight` | `6.0` | `distance_to_target` |
| `progress_to_target_clip_m` | `0.25 m` | `progress_to_target` |
| `progress_to_target_relax_radius_m` | `4.0 m` | `progress_to_target` |
| `progress_to_target_weight` | `8.0` | `progress_to_target` |
| `reached_target_base_reward` | `2.0` | `reached_target` |
| `reached_target_weight` | `6.0` | `reached_target` |
| `far_from_target_margin` | `6.0 m` | `far_from_target` |
| `far_from_target_weight` | `-2.0` | `far_from_target` |
| `angle_diff_weight` | `6.0` | `angle_diff` |
| `turn_speed_penalty_weight` | `-2.0` | `turn_speed_penalty` |
| `slip_penalty_weight` | `-2.0` | `slip_penalty` |
| `slip_angle_penalty_ratio` | `6.0` | `slip_penalty` |
| `progress_gate_longitudinal_k` | `3.0` | low-slip progress gate |
| `progress_gate_slip_angle_scale_rad` | `1.5 rad` | low-slip progress gate |
| `progress_gate_min_multiplier` | `0.10` | low-slip progress gate |
| `progress_gate_max_multiplier` | `1.50` | low-slip progress gate |
| `low_slip_longitudinal_threshold` | `1.0` | low-slip 评价阈值 |
| `low_slip_angle_threshold_rad` | `0.35 rad` | low-slip 评价阈值 |

注意：`low_slip_longitudinal_threshold` 和 `low_slip_angle_threshold_rad` 当前用于评价指标，不是成功终止条件。

### 2.1.3 `distance_to_target`

$$
r_{dist}
=
6.0
\cdot
\frac{1}{1+0.01d_t^2}
\cdot
\frac{1}{T}
$$

作用：提供持续型接近目标奖励。由于除以 $T$，单步量级较小，不能单独保证 waypoint 完成。

### 2.1.4 `progress_to_target` 与 low-slip gate

距离进步量：

$$
\Delta d_t=d_{t-1}-d_t
$$

先裁剪：

$$
\Delta d_t^{clip}
=
\mathrm{clip}(\Delta d_t,-0.25,0.25)
$$

近目标 `4.0 m` 内取消负 progress：

$$
d_t\le4.0
\Rightarrow
\Delta d_t^{clip}=\max(\Delta d_t^{clip},0)
$$

正负 progress 按 `goal_distance=10.0 m` 归一化：

$$
\Delta d_t^+
=
\frac{\max(\Delta d_t^{clip},0)}{10.0}
$$

$$
\Delta d_t^-
=
\frac{\min(\Delta d_t^{clip},0)}{10.0}
$$

六轮纵滑 gate：

$$
G_\kappa
=
\exp
\left[
-\frac{1}{2}
\sum_{i=1}^{6}
\left(
\frac{\kappa_i}{3.0}
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
\mathrm{clip}
\left(
\frac{\pi|\alpha_i|}{1.5},0,\pi
\right)
\right)
+0.5
\right]
$$

综合 gate：

$$
G=\min(G_\kappa,G_\alpha)
$$

progress multiplier：

$$
M
=
0.10+(1.50-0.10)G
=
0.10+1.40G
$$

最终 progress reward：

$$
r_{prog}
=
8.0
\left(
M\Delta d_t^+
+\Delta d_t^-
\right)
$$

作用：只门控正向 progress，负向 progress 不削弱。低滑移前进最多获得 `1.5` 倍正向 progress，高滑移前进至少保留 `0.1` 倍正向 progress。

### 2.1.5 `reached_target`

命中条件：

$$
d_t<0.5
$$

剩余时间系数：

$$
\eta_t=\frac{T-t}{T}
$$

命中奖励：

$$
r_{hit}
=
6.0
\cdot
2.0
\cdot
I_{hit}
\cdot
\eta_t
$$

作用：命中 waypoint 时给一次性奖励。命中最后一个 waypoint 才会形成 episode 成功。

### 2.1.6 `far_from_target`

远离阈值：

$$
d_{far}=10.0+6.0=16.0
$$

$$
r_{far}
=
-2.0
\cdot
I(d_t>16.0)
$$

作用：远离当前 active waypoint 时惩罚，并与远离终止条件配合。

### 2.1.7 `angle_diff`

$$
r_{angle}
=
6.0
\cdot
\frac{1}{1+|\theta_t|}
\cdot
\frac{1}{T}
$$

作用：弱引导车体朝向 active waypoint 方向。它不是硬约束，也不是最终姿态成功条件。

### 2.1.8 `turn_speed_penalty`

转向强度：

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

转向速度惩罚：

$$
r_{turnspeed}
=
-2.0
\cdot
\frac{\rho_t\nu_t}{T}
$$

作用：目标方向偏差较大且车速较高时扣分。本轮后段车辆近停滞，因此该项不会强烈影响行为。

### 2.1.9 `slip_penalty`

六轮平均纵滑与平均侧滑角：

$$
\bar{\kappa}
=
\frac{1}{6}
\sum_{i=1}^{6}
|\kappa_i|
$$

$$
\bar{\alpha}
=
\frac{1}{6}
\sum_{i=1}^{6}
|\alpha_i|
$$

滑移惩罚：

$$
r_{slip}
=
-2.0
\cdot
\frac{
\bar{\kappa}
+6.0\bar{\alpha}
}{T}
$$

作用：作为背景滑移约束。由于除以 $T$，单步惩罚量级较小；当前主要低滑移引导来自 `progress_to_target` 的 low-slip gate 和低层控制器。

### 2.1.10 对本轮结果的 reward 解释

| 现象 | 后 25 轮数据 | 解释 |
|---|---:|---|
| low-slip 综合达标率 | `0.986` | 策略确实进入低滑移状态 |
| progress multiplier | `1.251` | gate 已经奖励低滑移，不是压制 progress |
| `positive_progress_raw` | `1.75e-5` | 实际正向进度几乎为零 |
| policy desired `vx` | `0.966 m/s` | policy 仍想前进 |
| shaped `vx` | `0.100 m/s` | 低层整形大幅削弱前进命令 |
| `V_parallel` | `0.016 m/s` | 车轮实际纵向速度接近零 |
| `waypoints_completed_mean` | `0.000` | 低滑移没有转化为任务完成 |

因此，本轮 reward 的核心问题不是公式没有计算 low-slip，而是 low-slip 奖励与“非零前进进度”没有绑定。策略可以通过近停滞拿到低滑移状态，但无法完成 waypoint。

## 3. 任务完成指标

| 指标 | first | last | min/max | 全程均值 | 后 25 轮均值 |
|---|---:|---:|---:|---:|---:|
| `Train/mean_reward` | `-0.214` | `5.556` | `-` | `0.325` | `5.536` |
| `Train/mean_episode_length` | `253.8` | `2399.0` | `-` | `2333.2` | `2399.0` |
| `Termination/success_rate` | `0.0000` | `0.0000` | max `0.0002` | `0.000003` | `0.0000` |
| `Termination/time_out_rate` | `0.8809` | `1.0000` | `-` | `0.9481` | `1.0000` |
| `Tracking/waypoints_completed_mean` | `0.0000` | `0.0000` | max `0.0224` | `0.0005` | `0.0000` |
| `Tracking/episode_completion_pct` | `0.0000` | `0.0000` | max `1.1185` | `0.0267` | `0.0000` |
| `Tracking/active_segment_completion_pct` | `14.33` | `1.62` | max `44.63` | `14.02` | `1.66` |
| `Tracking/active_waypoint_pos_error` | `8.57` | `9.84` | min `5.54` | `8.68` | `9.83` |

阶段变化：

| 窗口 | `active_segment_completion_pct` | `active_waypoint_pos_error` | 判断 |
|---|---:|---:|---|
| 前 10 轮 | `25.88%` | 较低 | 早期仍有一定前进 |
| 50-75 | `32.84%` | 较低 | 曾短暂接近更好任务进度 |
| 100-125 | `4.57%` | 升高 | 开始明显退化 |
| 150-175 | `1.77%` | 接近 `9.8 m` | 进入近停滞 |
| 后 25 轮 | `1.66%` | `9.83 m` | 基本不完成 waypoint |

因此，本轮不是训练到平台成功后停止，而是在低滑移指标改善但任务学习崩掉后停止。

## 4. 低滑移指标

| 指标 | first | last | min/max | 全程均值 | 后 25 轮均值 |
|---|---:|---:|---:|---:|---:|
| 纵滑均值 `abs` | `2.157` | `0.286` | min `0.282` | `0.958` | `0.301` |
| 侧滑角均值 `abs` | `0.684 rad` | `0.125 rad` | min `0.125 rad` | `0.350 rad` | `0.132 rad` |
| 侧滑角均值 `deg` | `39.2°` | `7.18°` | min `7.18°` | `20.1°` | `7.59°` |
| `LowSlip/combined_pass_rate` | `0.056` | `0.989` | `-` | `0.543` | `0.986` |
| `LowSlip/longitudinal_slip_pass_rate` | `0.215` | `0.995` | `-` | `-` | `0.994` |
| `LowSlip/slip_angle_pass_rate` | `0.146` | `0.991` | `-` | `-` | `0.989` |

低滑移曲线确实显著改善：

| 窗口 | 纵滑均值 | 侧滑角均值 | 综合达标率 |
|---|---:|---:|---:|
| 前 10 轮 | `2.182` | `0.684 rad` | `0.017` |
| 50-75 | `1.352` | `0.493 rad` | `0.103` |
| 100-125 | `0.558` | `0.251 rad` | `0.801` |
| 后 25 轮 | `0.301` | `0.132 rad` | `0.986` |

但这不能直接解释为“低滑移控制成功”，因为同一时期车辆速度和进度也一起降到了接近零。

## 5. Progress gate 与 reward 解释

| 指标 | first | last | 全程均值 | 后 25 轮均值 |
|---|---:|---:|---:|---:|
| `ProgressGate/combined_gate` | `0.078` | `0.838` | `-` | `0.822` |
| `ProgressGate/multiplier` | `0.210` | `1.273` | `0.718` | `1.251` |
| `ProgressGate/longitudinal_gate` | `0.264` | `0.948` | `-` | `0.943` |
| `ProgressGate/slip_angle_gate` | `0.108` | `0.843` | `-` | `0.827` |
| `ProgressGate/positive_progress_raw` | `0.000653` | `0.0000158` | `-` | `0.0000175` |
| `ProgressGate/ungated_progress_raw` | `0.000651` | `0.00000826` | `-` | `0.0000103` |
| `Reward/progress_to_target` | `0.00109` | `0.000086` | `-0.000268` | `0.000099` |

判断：

- gate 后段已经从抑制变成奖励放大，`M≈1.25`。
- 问题不是 gate 把 progress 压死，而是实际正向 progress 接近零。
- 当前总 reward 上升主要不代表任务完成，而是策略进入了“少动、少滑、少出界、撑满回合”的局部模式。

## 6. 动作整形与低层速度

| 指标 | first | last | 全程均值 | 后 25 轮均值 |
|---|---:|---:|---:|---:|
| `Action/desired_planar_command_abs_mean_raw` | `0.686` | `0.760` | `0.766` | `0.760` |
| `Action/shaped_planar_command_abs_mean_raw` | `0.649` | `0.274` | `0.385` | `0.273` |
| `Action/planar_command_shaping_delta_abs_mean_raw` | `0.106` | `0.517` | `0.434` | `0.523` |
| `Action/desired_planar_vx_raw` | `1.028` | `0.961` | `1.000` | `0.966` |
| `Action/shaped_planar_vx_raw` | `0.967` | `0.104` | `0.323` | `0.100` |
| `Action/planar_command_delta_vx_raw` | `-0.060` | `-0.857` | `-0.678` | `-0.866` |
| `Action/desired_planar_wz_raw` | `0.151` | `0.533` | `0.464` | `0.521` |
| `Action/shaped_planar_wz_raw` | `0.122` | `0.357` | `0.305` | `0.343` |
| `Action/wheel_speed_reference_abs_mean_raw` | `5.069` | `0.884` | `2.028` | `0.893` |
| `Action/wheel_torque_target_abs_mean_raw` | `0.497` | `0.658` | `0.558` | `0.652` |
| `LowLevel/v_parallel_abs_mean_raw` | `0.292` | `0.015` | `0.098` | `0.016` |
| `LowLevel/v_perp_abs_mean_raw` | `0.323` | `0.018` | `0.104` | `0.019` |
| `LowLevel/delta_v_abs_mean_raw` | `0.496` | `0.029` | `0.163` | `0.030` |
| `LowLevel/tau0_abs_mean_raw` | `3.932` | `1.310` | `2.156` | `1.319` |
| `LowLevel/g_kappa_mean_raw` | `0.365` | `0.574` | `0.443` | `0.558` |
| `LowLevel/tau1_abs_mean_raw` | `1.583` | `1.033` | `1.264` | `1.030` |
| `LowLevel/g_alpha_mean_raw` | `0.457` | `0.908` | `0.692` | `0.899` |

最关键比例：

| 项目 | 后 25 轮 |
|---|---:|
| shaped `vx` / desired `vx` | 约 `10.4%` |
| 实际 `V_parallel` / desired `vx` | 约 `1.7%` |
| shaped planar command abs / desired planar command abs | 约 `35.9%` |

这说明 policy 并不是完全不想前进；真正被压低的是低层整形后的可执行平面速度和实际轮心纵向速度。

## 7. 车体姿态与 PPO 数值状态

| 指标 | first | last | max | 全程均值 | 后 25 轮均值 |
|---|---:|---:|---:|---:|---:|
| `Observation/pitch_deg` | `0.048` | `0.624` | `3.296` | `1.945` | `0.946` |
| `Observation/roll_deg` | `0.059` | `4.574` | `-` | `2.408` | `4.583` |
| `Train/policy_std` | `0.200` | `0.148` | `-` | `-` | `0.150` |
| `Loss/value_function` | `0.00516` | `0.0000119` | `-` | `-` | `0.0000139` |
| `Loss/surrogate` | `0.0480` | `-0.0078` | `-` | `-` | `-0.0086` |
| `Perf/fps` | `3196` | `3351` | `-` | `3315` | `3348` |

pitch 在中段曾升到约 `3.30°`，后段回落到 `1°` 以下；roll 后段约 `4.58°`。当前训练失败主要不是 PPO 数值不稳定或仿真崩溃，而是控制目标进入近停滞局部解。

## 8. 六轮状态分析

轮子名称映射：

| 中文 | TensorBoard wheel tag |
|---|---|
| 前左 | `head_car_wheel_left` |
| 前右 | `head_car_wheel_right` |
| 中左 | `body_car_wheel_left` |
| 中右 | `body_car_wheel_right` |
| 后左 | `tail_car_wheel_left` |
| 后右 | `tail_car_wheel_right` |

### 8.1 最后一轮逐轮状态

| 轮子 | joint vel | speed ref | `|vel-ref|` | torque target | contact weight | normal force N | long slip signed | slip angle rad | `V_parallel` | `V_perp` | `Delta V` | `tau0` | `g_kappa` | `tau1` | `g_alpha` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 前左 | `0.032` | `0.236` | `0.204` | `0.169` | `0.955` | `68.06` | `0.031` | `-0.009` | `0.0029` | `0.0023` | `0.0032` | `0.306` | `0.619` | `0.223` | `0.931` |
| 前右 | `0.049` | `1.012` | `0.963` | `0.996` | `0.995` | `104.87` | `0.075` | `-0.029` | `0.0019` | `-0.0003` | `0.0073` | `1.445` | `0.630` | `1.106` | `0.923` |
| 中左 | `-0.177` | `0.126` | `0.302` | `0.000` | `0.000` | `0.00` | `-0.356` | `0.011` | `0.0028` | `0.0025` | `-0.0363` | `0.454` | `0.451` | `0.532` | `0.836` |
| 中右 | `0.061` | `0.967` | `0.906` | `0.201` | `0.253` | `8.88` | `0.111` | `-0.008` | `0.0005` | `0.0019` | `0.0112` | `1.359` | `0.545` | `0.974` | `0.892` |
| 后左 | `0.048` | `-0.088` | `0.136` | `-0.241` | `0.996` | `114.36` | `0.053` | `-0.025` | `0.0035` | `-0.0001` | `0.0057` | `-0.205` | `0.621` | `-0.248` | `0.937` |
| 后右 | `0.060` | `1.046` | `0.986` | `1.021` | `0.971` | `67.93` | `0.092` | `-0.016` | `0.0022` | `0.0010` | `0.0092` | `1.479` | `0.575` | `1.125` | `0.931` |

### 8.2 后 25 轮逐轮均值

| 轮子 | joint vel | speed ref | `|vel-ref|` | torque target | contact weight | normal force N | long slip signed | slip angle rad | `V_parallel` | `V_perp` | `Delta V` | `tau0` | `g_kappa` | `tau1` | `g_alpha` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 前左 | `0.042` | `0.229` | `0.187` | `0.129` | `0.947` | `67.29` | `0.051` | `-0.009` | `0.0028` | `0.0021` | `0.0052` | `0.280` | `0.590` | `0.183` | `0.924` |
| 前右 | `0.061` | `0.989` | `0.928` | `0.920` | `0.995` | `104.46` | `0.099` | `-0.034` | `0.0017` | `-0.0010` | `0.0098` | `1.393` | `0.606` | `1.032` | `0.913` |
| 中左 | `-0.140` | `0.123` | `0.263` | `0.000` | `0.000` | `0.00` | `-0.284` | `0.010` | `0.0024` | `0.0024` | `-0.0290` | `0.394` | `0.461` | `0.464` | `0.824` |
| 中右 | `0.066` | `0.930` | `0.864` | `0.222` | `0.305` | `10.37` | `0.118` | `-0.003` | `0.0007` | `0.0024` | `0.0118` | `1.296` | `0.525` | `0.915` | `0.891` |
| 后左 | `0.061` | `-0.105` | `0.166` | `-0.282` | `0.996` | `115.98` | `0.074` | `-0.032` | `0.0038` | `-0.0012` | `0.0077` | `-0.249` | `0.601` | `-0.301` | `0.923` |
| 后右 | `0.070` | `1.017` | `0.947` | `0.946` | `0.960` | `66.15` | `0.109` | `-0.020` | `0.0023` | `0.0006` | `0.0110` | `1.421` | `0.565` | `1.062` | `0.917` |

逐轮解释：

- 中左轮后 25 轮 `contact_weight=0`、`normal_force=0 N`、`torque target=0`，说明它没有有效接触，因此最终力矩被接触权重切掉。
- 中右轮后 25 轮 `contact_weight≈0.305`、`normal_force≈10.37 N`，比前后轮低很多，说明中车轮组负载不足。
- 前右和后右轮 `|vel-ref|` 最大，约 `0.93-0.95 rad/s`，但绝对速度参考本身已经很低。
- 后段 signed 侧滑角不大，但 signed mean 可能发生正负抵消。全局 `wheel_slip_angle_abs_mean_raw` 同样已经降到约 `0.132 rad`，所以本轮低侧滑是真实出现的，但它伴随近停滞。
- 总接触力归一化仍约 `1.0`，说明整车整体没有完全离地，问题主要是轮间载荷分布不均。

## 9. 新 TensorBoard 指标验证

本轮已验证新增诊断指标进入 TensorBoard：

| 类别 | 指标 |
|---|---|
| Action | `desired_planar_command_abs_mean_raw` |
| Action | `shaped_planar_command_abs_mean_raw` |
| Action | `planar_command_shaping_delta_abs_mean_raw` |
| Action | `desired_planar_vx_raw` / `desired_planar_wz_raw` |
| Action | `shaped_planar_vx_raw` / `shaped_planar_wz_raw` |
| Action | `planar_command_delta_vx_raw` / `planar_command_delta_wz_raw` |
| LowLevel | `v_parallel_abs_mean_raw` |
| LowLevel | `v_perp_abs_mean_raw` |
| LowLevel | `delta_v_abs_mean_raw` |
| LowLevel | `tau0_abs_mean_raw` |
| LowLevel | `g_kappa_mean_raw` |
| LowLevel | `tau1_abs_mean_raw` |
| LowLevel | `g_alpha_mean_raw` |
| PerWheel | 每个轮子的 `v_parallel`、`v_perp`、`delta_v`、`tau0`、`g_kappa`、`tau1`、`g_alpha` |

同时，旧的 `Observation/tilt_deg` 和 `Observation/pitch_abs_deg` 没有出现在本轮导出的 tag 列表中；当前保留 `Observation/roll_deg` 和 `Observation/pitch_deg`。

## 10. 主要问题定位

### 10.1 不是仿真崩溃

仿真日志干净，FPS 稳定，PPO loss 没有爆炸。训练失败不是环境启动问题。

### 10.2 不是 progress gate 下限太低导致 progress 被压死

后段 `ProgressGate/multiplier≈1.25`，已经高于 `1.0`。真正的问题是车辆没有产生有效前进，导致 raw progress 接近零。

### 10.3 是低滑移整形形成了近静止局部最优

policy 后段仍输出约 `0.966 m/s` 的期望 `vx`，但 shaped `vx` 只有约 `0.100 m/s`，实际轮心纵向速度只有约 `0.016 m/s`。因此当前低层整形对任务速度的削弱过强。




