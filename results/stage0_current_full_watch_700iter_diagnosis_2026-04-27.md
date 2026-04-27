# Stage0 当前 active 配置完整训练诊断

日期：2026-04-27

## Run

- run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-27_18-17-40_stage0_current_full_watch_700iter`
- 任务：`CompleteCar-Stage0`
- 原计划：`700` iterations
- 实际结果：完整跑满，终端打印到 iteration `699/700`，进程退出码为 `0`
- 训练耗时：`8033.14 s`
- 最终 checkpoint：`model_699.pt`
- 事件文件：`events.out.tfevents.1777285066.ubuntu22.71551.0`
- TensorBoard 导出目录：`tensorboard_export/`

## 本轮生效关键参数

- `ball_joint_stiffness = 8000.0`
- `ball_joint_damping = 1000.0`
- `ball_joint_effort_limit_sim = 20.0`
- `ball_joint_velocity_limit_sim = 1.0`
- `low_slip_lambda_lateral = 5.0`
- `wheel_slip_feedback_gain = 4.0`
- `base_allow_reverse = true`
- `slip_penalty_weight = -2.0`
- `slip_longitudinal_penalty_ratio = 5.0`
- `slip_angle_penalty_ratio = 1.0`
- `load_equalization_weight = 0.0`
- `progress_gate_min_multiplier = 0.25`
- `progress_gate_max_multiplier = 1.5`
- `save_interval = 25`

说明：本轮未修改源码或配置，只按当前 active Stage0 配置启动完整训练。

## 任务完成情况

后 25 轮：

- `waypoints_completed_mean = 0.0`
- `episode_completion_pct = 0.0`
- `active_segment_completion_pct` 均值约 `3.29%`，最后一步约 `2.98%`
- `active_waypoint_pos_error` 均值约 `9.70 m`，最后一步约 `9.73 m`
- 终端最终 `success_rate = 0.0`
- 终端最终 `time_out_rate = 1.0`

全程统计：

- `active_segment_completion_pct` 最大约 `9.90%`
- `waypoints_completed_mean` 始终没有形成有效完成，最后仍为 `0.0`
- `episode_completion_pct` 最后为 `0.0`

判断：本轮没有恢复 waypoint 完成，完整训练后仍是 timeout 型失败。

## 滑移与低滑移指标

后 25 轮：

- 纵滑均值约 `0.765`，最后一步约 `0.563`
- 侧滑角均值约 `0.0945 rad`，最后一步约 `0.0749 rad`
- `LowSlip/combined_pass_rate` 均值约 `0.788`，最后一步约 `0.846`
- `LowSlip/longitudinal_slip_pass_rate` 均值约 `0.793`，最后一步约 `0.849`
- `LowSlip/slip_angle_pass_rate` 均值约 `0.957`，最后一步约 `0.975`
- `ProgressGate/multiplier` 均值约 `1.204`，最后一步约 `1.276`

全程首末变化：

- 纵滑从约 `6.906` 降到 `0.563`
- 侧滑角从约 `0.365 rad` 降到 `0.0749 rad`
- `ProgressGate/multiplier` 从约 `0.252` 升到 `1.276`

判断：滑移指标确实被压低，progress gate 也恢复到高 multiplier 区间。

## 速度与控制行为

后 25 轮：

- `v_parallel_abs_mean_raw` 均值约 `0.0135 m/s`，最后一步约 `0.0102 m/s`
- `v_perp_abs_mean_raw` 均值约 `0.0172 m/s`，最后一步约 `0.0111 m/s`
- `delta_v_abs_mean_raw` 均值约 `0.0809`，最后一步约 `0.0582`
- 轮速参考均值约 `0.567`，最后一步约 `0.480`
- 车轮力矩目标均值约 `1.892 N*m`，最后一步约 `1.549 N*m`

判断：低滑移主要来自速度和驱动幅值被压到很低，而不是形成了能推进到 waypoint 的低滑移运动策略。

## 结论

1. 本轮训练完整跑满 `700` iterations，最终 checkpoint `model_699.pt` 已保存。
2. 当前 active 配置没有学出 Stage0 waypoint 完成；最终仍为 `success_rate = 0.0`、`time_out_rate = 1.0`、`waypoints_completed_mean = 0.0`。
3. 当前纵滑主导的直接滑移惩罚配合 `min(Gκ,Gα)` progress gate 能显著降低纵滑和侧滑角，但策略收敛到近停滞低滑移局部解。
4. 本轮不能作为“低滑移协同控制成功”的证据；它只能说明当前奖励结构强烈鼓励低滑移，但缺少足够约束来保证非零推进和 waypoint 完成。
5. 下一步属于研究判断：需要先确认 Stage0 成功标准是否必须同时包含 waypoint 完成、非零有效推进和低滑移，再决定是否重构奖励主结构或成功条件。
