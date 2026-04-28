# Stage0 progress/no-progress v1 训练诊断

日期：2026-04-28

## 1. Run Identification

- Run 目录：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-28_10-37-44_stage0_progress_main_no_progress_v1_watch_700iter`
- 训练任务：`CompleteCar-Stage0`
- 计划训练：`700` iterations
- 实际停止：终端打印到 iteration `342/700`，TensorBoard 标量 step `0-342`
- 最新 checkpoint：`model_325.pt`
- 回放视频：`videos/play/rl-video-step-0.mp4`
- TensorBoard 导出：`tensorboard_export/`

## 2. Startup and Configuration

- 设备：`cuda:0`
- 并行环境数：`64`
- 每次 rollout：`512` steps/env
- episode 长度：`40 s`，`2400` 个控制步
- `is_finite_horizon=True`：timeout 按失败终止，不再让 PPO bootstrap
- PPO：`gamma=0.99`，`lam=0.95`，`learning_rate=1e-4`，`entropy_coef=0.0005`
- 当前 Stage0 reward 关键参数：
  - `distance_to_target_weight=2.0`
  - `angle_diff_weight=2.0`
  - `progress_to_target_weight=8.0`
  - `progress_negative_scale=2.0`
  - `no_progress_threshold_m=0.005`
  - `no_progress_weight=8.0`
  - `timeout_fixed_penalty=8.0`
  - `timeout_distance_penalty_scale=0.3`
  - `progress_gate_longitudinal_k=0.5`
  - `progress_gate_min_multiplier=0.25`
  - `progress_gate_max_multiplier=1.5`
- 启动日志未发现训练中断级错误。主要是 Isaac/Kit 常见 warning，例如 MaterialX、dynamic_control deprecated、CPU powersave、PCIe link width warning。

## 3. Core Training Outcome

本轮不再是“策略完全不动”，但也没有学成稳定到达目标。

| 指标 | 首步 | 末步 | 后 25 step 均值 | 关键峰值 |
|---|---:|---:|---:|---:|
| `Train/mean_reward` | `-11.485` | `-2.301` | `-2.336` | `0.439 @ step 318` |
| `success_rate` | `0.000` | `0.000` | `0.0337` | `0.316 @ step 288` |
| `time_out_rate` | `0.881` | `1.000` | `0.966` | 最低 `0.684 @ step 288` |
| `active_waypoint_pos_error` | `9.868 m` | `4.813 m` | `4.379 m` | 最低 `3.321 m @ step 297` |
| `active_segment_completion_pct` | `1.42%` | `51.88%` | `56.24%` | 最高 `66.82% @ step 297` |
| `waypoints_completed_mean` | `0.000` | `0.389` | `0.301` | 最高 `0.401 @ step 334` |
| `episode_completion_pct` | `0.00%` | `19.44%` | `15.08%` | 最高 `20.07% @ step 334` |

成功只在 step `276-340` 零散出现，共 `33` 个 step 有非零成功率；最长连续非零成功只有 `7` 个 step。`success_rate > 0.2` 只出现 `5` 次，`success_rate > 0.3` 只出现 `1` 次。

命中误差也说明成功很边界化：`episode/success_hit_pos_error` 只在 step `276-340` 记录到，范围约 `0.482-0.500 m`，平均 `0.494 m`，基本贴着 `0.5 m` 的成功半径。

## 4. Motion and Progress Diagnosis

速度确实上来了：

- `v_parallel_abs`：首步 `0.059 m/s`，末步 `0.519 m/s`，后 25 step 均值 `0.550 m/s`
- `wheel_speed_reference_abs`：首步 `1.843 rad/s`，末步 `6.356 rad/s`，后 25 step 均值 `6.477 rad/s`
- `wheel_joint_vel_abs`：末步 `6.176 rad/s`，后 25 step 均值 `6.298 rad/s`
- `desired_planar_command_abs`：首步 `0.341`，末步 `0.950`，后 25 step 均值 `0.961`

但朝目标的有效推进仍不足：

- `raw_delta_m` 末步 `0.00383 m/step`，后 25 step 均值 `0.00466 m/step`
- 当前阈值是 $\delta=0.005 m/step$，等价于约 `0.30 m/s` 的径向接近速度
- 后 25 step 实际径向接近速度约 `0.279 m/s`，仍低于阈值
- `no_progress_gap_m` 后 25 step 均值 `0.00361 m`，说明 no-progress 惩罚仍长期激活
- 末步 `raw_delta_m/control_dt` 约 `0.230 m/s`，只占 `v_parallel_abs=0.519 m/s` 的约 `44%`

这说明小车已经在动，但相当一部分轮地速度没有转化为朝目标方向的距离缩短。

## 5. Slip and Gate Diagnosis

本轮主要失败模式是高命令、高轮速、高纵滑。

| 指标 | 首步 | 末步 | 后 25 step 均值 |
|---|---:|---:|---:|
| `wheel_longitudinal_slip_abs` | `2.985` | `4.375` | `4.228` |
| `wheel_slip_angle_abs` | `0.121 rad` | `0.288 rad` | `0.268 rad` |
| `LowSlip/combined_pass_rate` | `0.0869` | `0.0349` | `0.0389` |
| `LowSlip/longitudinal_pass_rate` | `0.0886` | `0.0390` | `0.0424` |
| `LowSlip/slip_angle_pass_rate` | `0.992` | `0.737` | `0.765` |
| `ProgressGate/combined_gate` | `0.428` | `0.237` | `0.251` |
| `ProgressGate/longitudinal_gate` | `0.00101` | `0.000239` | `0.000278` |
| `ProgressGate/slip_angle_gate` | `0.854` | `0.474` | `0.502` |
| `ProgressGate/multiplier` | `0.785` | `0.547` | `0.564` |

由于 `combined_gate = 0.5*(Gκ+Gα)`，纵滑 gate 近似为零时，combined gate 主要由侧滑 gate 的一半支撑。也就是说：当前正向 progress 没有被完全压到底线，但纵滑质量几乎没有改善。

相关性也支持这一点：

- 全程 `mean_reward` 与 `v_parallel_abs` 相关系数约 `0.782`
- 全程 `mean_reward` 与纵滑相关系数约 `0.744`
- 全程 `raw_delta_m` 与 `desired_planar_command_abs` 相关系数约 `0.796`
- 全程 `raw_delta_m` 与 `desired_wz` 相关系数约 `0.747`
- 全程 `raw_delta_m` 与 signed `desired_vx` 相关系数约 `-0.219`

这说明当前奖励改善主要伴随“整体命令幅值和轮速升高”，而不是学出清晰、低滑移、朝目标方向的纵向推进策略。

## 6. Reward Diagnosis

末步主要 reward 项：

- `Reward/total = -0.000544`
- `progress_to_target = 0.002305`
- `no_progress_penalty = -0.002972`
- `timeout_penalty = -0.002570`
- `distance_to_target = 0.000665`
- `angle_diff = 0.000337`
- `reached_target = 0.001693`

后 25 step 均值：

- `progress_to_target = 0.002907`
- `no_progress_penalty = -0.002891`
- `timeout_penalty = -0.003760`
- `reward_total = -0.001066`

当前奖励结构已经把“完全低速不动”的局部解打破，但 `progress_to_target` 仍没有强到稳定主导行为。更准确地说，它现在推动 policy 增大命令和轮速，但没有足够强地把行为收束到“朝目标方向稳定接近”。

## 7. Contact and Pose Diagnosis

- 后 25 step 六轮法向力合计约 `365.5 N`
- 中部 `body_car` 两轮载荷份额约 `21.1%`
- 前部 `head_car` 两轮载荷份额约 `39.1%`
- 后部 `tail_car` 两轮载荷份额约 `39.8%`
- `load_equalization_error` 首步 `0.076`，末步 `0.284`，后 25 step 均值 `0.287`
- `pitch_deg` 末步约 `-4.38 deg`，后 25 step 均值约 `-4.05 deg`

中部车轮仍偏弱承载，但本轮的主问题不是完全离地，而是高纵滑下的低效推进。

## 8. Numerical Stability

- `Loss/value` 首步 `0.529`，末步 `0.251`，无爆炸
- `Loss/surrogate` 末步约 `-0.00531`
- `Policy/mean_std` 从 `0.200` 增至 `0.215`
- `Action/policy_std` 从 `0.208` 增至 `0.464`
- 总 FPS 平均约 `3556`

没有看到 PPO 数值崩溃；训练失败主要是任务奖励/行为语义问题，不是优化器爆炸。

## 9. Diagnosis

最大正向信号：progress/no-progress 修改有效打破了前一轮低速近停滞局部解，实际轮地速度从约 `0.06 m/s` 提升到后段约 `0.55 m/s`，并开始出现零散 waypoint 命中。

主问题：policy 当前学到的是高命令、高轮速、高纵滑的“碰运气式接近/命中”，不是稳定朝目标方向推进；末端仍基本 timeout，成功率不稳定，低滑移达标率只有约 `4%`。

本轮不适合作为成功训练结果。它证明修改方向能让车动起来，但也暴露出下一层结构问题：推进奖励已经能驱动运动，却还没有强到把“有效朝目标推进”变成主导策略，同时成功条件仍允许边界化、高滑移命中。

## 10. Next-Step Priority

如果当前 Stage0 目标仍是“稳定完成 waypoint，同时保持较低滑移”，下一轮不应只是继续放大命令或奖励 raw `vx`。

建议优先讨论并确认三点：

1. 是否把低滑移或低纵滑作为成功条件的一部分，而不仅是 soft gate。
2. 是否把 progress 从“每步距离变化的弱 shaped 项”提升为 episode 中最主要的即时学习信号，同时进一步压低与任务完成无关的 dense 项。
3. 是否对高纵滑高命中策略设置失败或强惩罚，否则 PPO 会继续利用高轮速、高滑移换取偶发命中。
