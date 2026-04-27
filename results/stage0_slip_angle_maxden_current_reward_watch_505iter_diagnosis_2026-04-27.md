# Stage0 当前奖励与侧滑角新口径训练诊断

日期：2026-04-27

## Run

- run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-27_15-30-59_stage0_slip_angle_maxden_current_reward_watch_700iter`
- 任务：`CompleteCar-Stage0`
- 原计划：`700` iterations
- 实际停止：终端打印到 iteration `505/700` 后按稳定成功率平台停止
- 最新 checkpoint：`model_500.pt`
- 事件文件：`events.out.tfevents.1777275064.ubuntu22.53386.0`

## 本轮生效关键参数

- `ball_joint_stiffness = 1000.0`
- `ball_joint_damping = 10.0`
- `low_slip_lambda_lateral = 0.0`
- `slip_penalty_weight = -2.0`
- `slip_angle_penalty_ratio = 2`
- `load_equalization_weight = 0.0`
- `load_equalization_k = 10.0`
- `save_interval = 25`

说明：本轮负载均衡相关标量只记录，不参与奖励。

## 成功率平台

按 TensorBoard step `495-505` 作为平台窗口：

- `success_rate` 均值约 `0.9606`
- `success_rate` 最低约 `0.9082`
- `success_rate` 最高 `1.0`
- 最后一步 `success_rate = 1.0`
- `time_out_rate` 均值约 `0.0394`
- 最新 checkpoint 为 `model_500.pt`，平台末端没有单独保存 `model_505.pt`

判断：从成功率看，已经出现稳定成功率平台；因此按用户要求停止训练。

## 运动质量

平台窗口 step `495-505`：

- 纵向滑移均值约 `2.497`
- 侧滑角均值约 `0.767 rad`
- `LowSlip/combined_pass_rate` 均值约 `0.0938`
- `ProgressGate/combined_gate` 均值约 `0.0649`
- `v_parallel_abs_mean_raw` 均值约 `0.646 m/s`
- `v_perp_abs_mean_raw` 均值约 `0.701 m/s`
- `delta_v_abs_mean_raw` 均值约 `1.097`
- 轮速参考均值约 `8.278`
- pitch 均值约 `4.71 deg`，最高约 `5.19 deg`
- roll 均值约 `0.31 deg`

判断：成功率平台不是低滑移平台。车辆主要仍是高纵滑、高侧滑完成，且横向速度均值大于纵向速度均值。

## 六轮与中车接地

平台窗口 step `495-505` 六轮法向力均值：

- 前左：`71.89 N`
- 前右：`77.05 N`
- 中左：`32.05 N`
- 中右：`25.85 N`
- 后左：`77.13 N`
- 后右：`77.99 N`
- 六轮总法向力均值：`361.98 N`
- 中车两轮合计均值：`57.91 N`
- 中车载荷占比均值：`15.997%`
- 中车左右不均衡均值约 `10.65%`

最新 step `505`：

- 中左：`28.89 N`
- 中右：`25.69 N`
- 中车合计：`54.59 N`
- 六轮总法向力：`361.28 N`
- 中车载荷占比：`15.11%`

判断：中车不是悬空，但仍明显弱承载。若六轮近似均载，中车两轮应占六轮总载荷约 `33.33%`；本轮平台窗口只有约 `16.0%`。

## 结论

1. 本轮已恢复并稳定了 Stage0 成功率，step `495-505` 连续 `11` 轮 `success_rate >= 0.90`。
2. 本轮没有形成低滑移完成方式，低滑移综合达标率均值只有约 `9.4%`。
3. 中车接地比近悬空状态好，但仍是弱承载，中车载荷占比约 `16.0%`。
4. 当前 `load_equalization_weight = 0.0`，所以负载均衡只作为诊断指标；本轮不能证明负载均衡奖励有效。
5. 下一步若目标是论文可解释的协同稳定控制，应先明确：Stage0 是否只要求成功率，还是要把低滑移和中车有效承载纳入成功条件或奖励主结构。
