# Stage0 负载不均匀惩罚短训练诊断

日期：2026-04-27

## 训练信息

- run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-27_14-42-42_stage0_load_imbalance_penalty_m05_watch_700iter`
- 原计划：`700` iterations
- 实际停止：终端打印到 iteration `100/700`
- 已保存 checkpoint：`model_0.pt`、`model_25.pt`、`model_50.pt`、`model_75.pt`、`model_100.pt`
- 奖励项状态：`load_equalization_weight=-0.5`，`load_equalization` 为负载不均匀惩罚

## 任务完成

- `success_rate` 最后一步为 `0.0`
- `success_rate` 最大瞬时值约 `0.123`
- `success_rate` 全程均值约 `0.0021`
- `active_segment_completion_pct` 最后约 `41.94%`，最大约 `44.06%`
- `episode_completion_pct` 最后约 `5.28%`，最大约 `7.20%`
- `waypoints_completed_mean` 最后约 `0.106`

判断：策略能把当前 active segment 推进到约 40%，但没有形成稳定 waypoint 命中，更没有恢复完整双 waypoint 完成。

## 运动质量

- 纵滑均值从约 `2.44` 降到最后约 `2.22`，仍远高于低纵滑目标
- 侧滑角从约 `0.73 rad` 降到最后约 `0.66 rad`，仍高于 `0.5 rad` 目标
- `v_parallel_abs` 从约 `0.349 m/s` 降到最后约 `0.268 m/s`
- `v_perp_abs` 从约 `0.399 m/s` 降到最后约 `0.292 m/s`
- `ball_joint_vel_abs_mean_raw` 从约 `0.160` 升到最后约 `0.236`
- `pitch_deg` 从约 `0.10 deg` 升到最后约 `1.06 deg`

判断：滑移指标下降主要伴随速度降低，不是更高质量的滚动推进；球铰和车体姿态活动没有变得更平静。

## 六轮接地与中车载荷

最终法向力：

- 中车左轮：约 `31.72 N`
- 中车右轮：约 `21.07 N`
- 前车左轮：约 `96.31 N`
- 前车右轮：约 `55.48 N`
- 后车左轮：约 `60.44 N`
- 后车右轮：约 `101.69 N`

最终中车载荷占比约 `14.4%`，明显低于理想三段均分时的 `33.3%`。

全程均值估算：

- 中车两轮合计均值约 `64.8 N`
- 六轮总法向力均值约 `366.9 N`
- 中车平均载荷占比约 `17.7%`

判断：中车不是完全悬空，但仍是弱载荷接地；负载不均匀惩罚没有把载荷有效拉回中车。

## 负载惩罚效果

- `Reward/load_equalization` 为负值，确认惩罚项已经生效
- `Reward/23_load_equalization_error` 从首步约 `0.1659` 升到最后约 `0.1856`
- 全程最大约 `0.1892`，均值约 `0.1786`

判断：该弱惩罚没有降低负载误差，反而随训练略微变差。

## 结论

`load_equalization_weight=-0.5` 的负载不均匀惩罚没有恢复任务完成，也没有改善中车载荷。它没有像正奖励版本那样立即把训练完全压死，但在前 100 个 iteration 内表现为：偶发成功、整体低完成度、速度下降、中车弱载荷和负载误差上升。

当前不应继续单独依赖这个弱惩罚项解决中车接地。下一步应先明确六轮接地在 Stage0 中的角色：是评价指标、奖励偏好，还是成功条件；如果作为必须满足的条件，需要把有效接地、非零前进和 waypoint 完成绑定，而不是只加一个独立小权重 reward term。
