# Stage0 `lambda_lat=4.0, ball=1500/30` 训练诊断

## 基本信息

- run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-27_09-35-03_stage0_lambda4_ball1500_damp30_watch_700iter`
- 任务：`CompleteCar-Stage0`
- 原计划：`700` iterations
- 实际停止：终端打印到 iteration `98/700`，TensorBoard step `98`
- 最后 checkpoint：`model_75.pt`
- 停止原因：用户要求停止训练并分析

本轮 run 内 `params/env.yaml` 确认实际参数：

- `ball_joint_stiffness = 1500.0`
- `ball_joint_damping = 30.0`
- `low_slip_lambda_lateral = 4.0`
- `wheel_torque_tracking_gain = 2.0`
- `wheel_slip_feedback_gain = 1.5`
- `wheel_joint_effort_limit_sim = 15.0`

## 任务完成情况

后 25 个 TensorBoard 点：

- `time_out_rate = 1.0`
- `far_from_target_rate = 0.0`
- `success_rate = 0.0`，该序列全程为零，导出时被空零序列裁剪
- `waypoints_completed_mean = 0.0`
- `episode/waypoints_completed = 0.0`
- `active_segment_completion_pct ≈ 9.71%`
- `active_waypoint_pos_error ≈ 9.03 m`

最后一个点 step `98`：

- `active_segment_completion_pct ≈ 3.71%`
- `active_waypoint_pos_error ≈ 9.63 m`
- `waypoints_completed_mean = 0.0`

结论：本轮不是成功训练。车辆可以撑满 episode，但几乎没有有效推进到 waypoint。

## 低滑移指标

后 25 个 TensorBoard 点：

- 纵滑均值约 `0.746`
- 侧滑角均值约 `0.282 rad`
- `LowSlip/combined_pass_rate ≈ 0.645`
- `ProgressGate/multiplier ≈ 0.761`

最后一个点 step `98`：

- 纵滑约 `0.530`
- 侧滑角约 `0.218 rad`
- `LowSlip/combined_pass_rate ≈ 0.865`
- `ProgressGate/multiplier ≈ 0.965`

低滑移指标已经明显达标，但该达标不是通过有效运动完成任务获得，而是伴随近停滞出现。

## 速度与运动质量

后 25 个 TensorBoard 点：

- `v_parallel_abs ≈ 0.041 m/s`
- `v_perp_abs ≈ 0.047 m/s`
- `wheel_speed_reference_abs_mean ≈ 1.106`
- `wheel_torque_target_abs_mean ≈ 1.223 Nm`

最后一个点 step `98`：

- `v_parallel_abs ≈ 0.0235 m/s`
- `v_perp_abs ≈ 0.0316 m/s`
- `wheel_speed_reference_abs_mean ≈ 0.922`
- `wheel_torque_target_abs_mean ≈ 1.212 Nm`

结论：车辆后段基本进入低速蠕动状态；侧向速度仍不小于纵向速度，不是健康的前向通过运动。

## 中车姿态与接地

后 25 个 TensorBoard 点：

- 中车 `pitch_deg ≈ 1.32°`
- 中车 `roll_deg ≈ -4.69°`

最后一个点 step `98`：

- 中车 `pitch_deg ≈ 1.21°`
- 中车 `roll_deg ≈ -5.59°`

中车 pitch 本身不大，但 roll 逐步增大。更关键的是 per-wheel 接触数据：

后 25 个 TensorBoard 点：

| 车轮 | 法向力均值 | 接触权重均值 | 力矩目标均值 |
| --- | ---: | ---: | ---: |
| 中左轮 | `0.019 N` | `0.00028` | `0.00028 Nm` |
| 中右轮 | `0.019 N` | `0.00021` | `0.00019 Nm` |
| 前左轮 | `83.82 N` | `0.967` | `0.305 Nm` |
| 前右轮 | `95.42 N` | `0.973` | `1.066 Nm` |
| 后左轮 | `101.24 N` | `0.985` | `0.436 Nm` |
| 后右轮 | `83.88 N` | `0.969` | `1.107 Nm` |

最后一个点 step `98`：

| 车轮 | 法向力 | 接触权重 | 力矩目标 |
| --- | ---: | ---: | ---: |
| 中左轮 | `0.00089 N` | `0.000030` | `0.00018 Nm` |
| 中右轮 | `0.00000 N` | `0.000000` | `0.00000 Nm` |
| 前左轮 | `79.73 N` | `0.972` | `0.774 Nm` |
| 前右轮 | `98.22 N` | `0.987` | `1.466 Nm` |
| 后左轮 | `98.15 N` | `0.990` | `0.888 Nm` |
| 后右轮 | `88.82 N` | `0.988` | `1.533 Nm` |

结论：中车轮组已经基本无有效接地。整车接触总量正常，但载荷几乎全部由前车和后车承担，中车两轮既不提供有效支撑，也不提供有效驱动力。

## 与上一轮 `1000/10` 的对比

上一轮 `2026-04-27_09-14-07_stage0_lambda4_current_700iter` 使用球铰 drive `1000/10`，后段表现为：

- 后 25 轮 `active_segment_completion_pct ≈ 36.99%`
- 后 25 轮纵滑约 `1.586`，侧滑角约 `0.503 rad`
- 后 25 轮 `v_parallel_abs ≈ 0.133 m/s`
- 后 10 轮中车两轮法向力约 `4.06 N / 1.47 N`

本轮 `1500/30` 后段表现为：

- 后 25 轮 `active_segment_completion_pct ≈ 9.71%`
- 后 25 轮纵滑约 `0.746`，侧滑角约 `0.282 rad`
- 后 25 轮 `v_parallel_abs ≈ 0.041 m/s`
- 后 25 轮中车两轮法向力约 `0.019 N / 0.019 N`

直接判断：

- `1500/30` 确实让滑移指标明显变好；
- 但它同时把任务推进压到更低，并进一步加重中车轮组失载；
- 因此它不能作为当前 Stage0 的成功方向。

## 结论

本轮训练验证了一个明确失败模式：

- 低滑移指标可以被训练到达标；
- 但达标方式是近停滞、前后轮承载、中车轮组失载；
- `success_rate` 始终为 `0`，没有完成 waypoint；
- 中车姿态角本身不大，但接触数据证明中轮几乎不接地；
- 继续按当前 `lambda_lat=4.0 + ball=1500/30` 长训，大概率只会强化低速低滑移局部解，而不是恢复有效完成任务。

下一步不应继续把本轮当作可延长的成功苗头；需要先决定是否把中车有效接地/载荷分配作为下一轮的显式约束或评价重点。
