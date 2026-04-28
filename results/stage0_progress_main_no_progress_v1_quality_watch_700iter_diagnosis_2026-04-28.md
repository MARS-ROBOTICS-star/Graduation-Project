# Stage0 progress/no-progress v1 quality-watch 700iter 训练诊断

## Run 信息

- Run: `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-28_12-09-46_stage0_progress_main_no_progress_v1_quality_watch_700iter`
- 命令任务: `CompleteCar-Stage0`
- 计划迭代: `700`
- 实际终端: `699/700`
- 退出码: `0`
- 训练耗时: `7295.66 s`
- 最终 checkpoint: `model_699.pt`
- TensorBoard 导出: `tensorboard_export/`

说明：RSL-RL 的终端计数从 `0` 开始，因此 `699/700` 表示本轮 `700` 次迭代已跑满。

## 总体结论

这轮训练不是“完全不动”的局部解，但也不是成功策略。

policy 后期能产生明显动作和车体前向速度，最后 `v_parallel_abs_mean_raw≈0.583 m/s`，后 100 step 平均约 `0.586 m/s`。但是这些运动主要表现为高轮速、高纵滑和姿态变差，并没有稳定转化为 waypoint 完成。

核心判断：

- 任务完成失败：全程平均 `success_rate≈0.0296`，后 100 step 平均 `success_rate≈0.0772`，最终 `success_rate≈0.0684`。
- timeout 仍主导：全程平均 `time_out_rate≈0.9696`，后 100 step 平均 `time_out_rate≈0.9228`。
- 路径完成不足：后 100 step 平均 `episode_completion_pct≈13.79%`，最终约 `10.31%`。
- 滑移严重：后 100 step 平均纵滑约 `4.65`，最终约 `4.88`；后 100 step `LowSlip/combined_pass_rate≈3.84%`，最终约 `3.24%`。
- 姿态逐步变差：后 100 step 平均 `pitch≈6.63 deg`，最终约 `8.32 deg`。

因此，本轮证明当前 reward 可以驱动车动起来，但学到的是高滑移低稳定命中行为，不能作为 Stage0 成功训练结果。

## 关键窗口均值

| step 窗口 | success | timeout | episode completion | waypoint mean | v_parallel | long slip | slip angle | low-slip pass | pitch | mean reward |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0-99 | 0.0000 | 0.9940 | 0.6059 | 0.0121 | 0.1804 | 3.0016 | 0.1053 | 0.0722 | -0.7594 | -9.2187 |
| 100-199 | 0.0041 | 0.9959 | 3.4643 | 0.0693 | 0.3097 | 2.9980 | 0.1493 | 0.0655 | -3.5672 | -4.9517 |
| 200-299 | 0.0062 | 0.9938 | 5.7879 | 0.1158 | 0.4507 | 3.5534 | 0.2277 | 0.0526 | -7.2102 | -4.4383 |
| 300-399 | 0.0334 | 0.9666 | 15.1467 | 0.3029 | 0.5356 | 4.5989 | 0.2472 | 0.0402 | -5.1098 | 0.4138 |
| 400-499 | 0.0513 | 0.9487 | 14.2115 | 0.2842 | 0.5344 | 4.7969 | 0.2164 | 0.0441 | -1.6761 | 2.3995 |
| 500-599 | 0.0349 | 0.9651 | 9.4396 | 0.1888 | 0.5537 | 4.5184 | 0.1981 | 0.0471 | 1.8984 | -0.7154 |
| 600-699 | 0.0772 | 0.9228 | 13.7874 | 0.2757 | 0.5857 | 4.6528 | 0.2436 | 0.0384 | 6.6254 | 1.8960 |

## 任务完成情况

- 单点最高 `success_rate≈0.5234` 出现在 step `611`，但这是批次波动。
- 最好的 30-step rolling success 窗口为 step `601-630`，均值约 `0.1250`。
- 最好的 30-step rolling episode completion 窗口为 step `367-396`，均值约 `19.67%`。
- 全程最大 `episode_completion_pct≈25.50%` 出现在 step `382`。
- 全程最大 `waypoints_completed_mean≈0.510`，仍远低于 Stage0 双 waypoint 完成目标。

结论：训练中出现过偶发命中，但没有进入稳定完成平台。

## 运动行为质量

速度不是主要问题：

- 后 100 step `v_parallel_abs_mean_raw≈0.586 m/s`。
- 最终 `v_parallel_abs_mean_raw≈0.583 m/s`。
- 后 100 step `wheel_speed_reference_abs_mean_raw≈7.19 rad/s`。
- 最终 `wheel_speed_reference_abs_mean_raw≈7.42 rad/s`。

真正的问题是速度质量差：

- 后 100 step 纵滑约 `4.65`，最终约 `4.88`。
- 后 100 step 侧滑角约 `0.244 rad`，最终约 `0.277 rad`。
- 后 100 step low-slip combined pass rate 只有约 `3.84%`。
- 后 100 step `ProgressGate/longitudinal_gate≈0.0158`，说明正向 progress 的纵滑质量门控几乎被高纵滑压低。
- 后 100 step `pitch≈6.63 deg`，最终约 `8.32 deg`，姿态质量随训练后期动作增强而变差。

因此，“车动了”不能等价于“朝目标有效推进”。当前 policy 更像是在用大轮速和高滑移换取偶发接近。

## Reward 语义观察

后 100 step 关键 reward / gate 均值：

- `Reward/progress_to_target≈0.002824`
- `Reward/no_progress_penalty≈-0.002816`
- `Reward/timeout_penalty≈-0.003670`
- `Reward/total≈0.000885`
- `ProgressGate/combined_gate≈0.3218`
- `ProgressGate/longitudinal_gate≈0.0158`
- `ProgressGate/slip_angle_gate≈0.6278`
- `ProgressGate/raw_delta_m≈0.004752`

解释：

- 平均原始距离进步量约 `0.004752 m/step`，低于当前 `no_progress_threshold_m=0.005`，所以 no-progress penalty 仍持续生效。
- progress 正奖励与 no-progress 惩罚在后段几乎互相抵消。
- 纵滑 gate 极低，说明当前有效前进质量仍被纵滑破坏。
- timeout penalty 虽然存在，但后段仍没有把策略推入稳定成功平台。

## 与上一轮中断训练的关系

相对 `2026-04-28_10-37-44_stage0_progress_main_no_progress_v1_watch_700iter` 中断在 step `342` 的结果，本轮跑满后确认：

- progress/no-progress 方向确实能避免近停滞。
- 继续训练没有自然修复高滑移。
- 后期动作幅度、轮速参考、pitch 和滑移继续升高。
- 成功率仍处于低且波动的状态。

这说明当前失败不只是训练步数不够，而是 reward / 成功语义仍允许高滑移低稳定命中策略存在。

## 后续判断边界

本报告只确认工程事实：

- 当前 checkpoint `model_699.pt` 可回放，但不应作为成功策略。
- 当前 reward 能驱动车动起来，但没有把“稳定完成 waypoint”和“低滑移有效推进”同时绑定起来。
- 是否把低滑移、姿态、有效推进量或 waypoint 完成质量纳入成功条件/强约束，属于下一步研究判断，需要由用户确认。
