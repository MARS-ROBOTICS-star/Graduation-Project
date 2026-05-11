# Stage0 `model_200.pt` 球铰 PD 统一增益真实轨迹扫参报告

## 1. 实验口径

- 输入数据：`results/stage0_model200_ball_joint_pd_matlab/raw_traces/` 下的 Stage0 flat 逐 control step 真实 CSV。
- checkpoint：`2026-05-10_18-21-11_stage0_slip2_actionrate_m50_qmon_700iter/model_200.pt`。
- 参与 case 数：`8`，每个 case 对应一个 `env_id`。
- 固定 plant 参数：`J = 0.100 kg*m^2`、`B = 0.500`、`tau_load = 0.000 N*m`、`tau_v = 0.040 s`。
- 固定限制：`tau_max = 60.0 N*m`、`qdot_max = 2.0 rad/s`、`dt_sim = 1/120 s`、`dt_ctrl = 1/60 s`。
- 仿真初值：使用真实 trace 的第一帧 `q_actual`、`qdot_actual` 和 `qdot_alloc`。
- 关节顺序：`spm1_platform_joint_z`, `spm1_platform_joint_y`, `spm1_platform_joint_x`, `spm2_platform_joint_z`, `spm2_platform_joint_y`, `spm2_platform_joint_x`。

## 2. 当前真实回放指标

| 指标 | 数值 |
|---|---:|
| `q_desired_abs_mean` | 0.089725 |
| `q_desired_abs_p95` | 0.197211 |
| `tracking_error_abs_mean` | 0.047755 |
| `tracking_error_abs_p95` | 0.119797 |
| `tracking_error_mean / q_desired_abs_mean` | 0.532232 |
| `position_target_gap_mean` | 0.000000 |
| `position_target_gap_max` | 0.000000 |
| `qdot_abs_mean` | 0.456345 |
| `qdot_abs_p95` | 1.255009 |
| `qdot_limit_rate_0.95` | 0.006591 |
| `qdot_limit_rate_0.98` | 0.004834 |
| `q_desired_delta_abs_mean` | 0.036201 |
| `q_desired_delta_abs_p95` | 0.099542 |

## 3. 最优候选与当前参数

| item | Kp | Kd | new_error_mean | old_error_mean | error_reduction_ratio | sat_ratio | qdot_limit_rate | risk_score | rank |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| best risk | 320 | 24 | 0.031266 | 0.047755 | 0.345262 | 0.000157 | 0.327716 | 0.166175 | 1 |
| current | 120 | 10 | 0.029699 | 0.047755 | 0.378080 | 0.000000 | 0.007739 | 0.317272 | 18 |
| conservative alt | 120 | 16 | 0.031889 | 0.047755 | 0.332243 | 0.000000 | 0.000817 | 0.238376 | 5 |
| moderate alt | 160 | 16 | 0.030005 | 0.047755 | 0.371695 | 0.000000 | 0.003826 | 0.253101 | 6 |
| stronger alt | 220 | 16 | 0.027730 | 0.047755 | 0.419330 | 0.000000 | 0.011808 | 0.276161 | 10 |

## 4. 结论

- 当前 `Kp=120, Kd=10` 的优点是保守稳定：真实回放中 `qdot` 贴近 `2 rad/s` 的比例很低，且 `position_target_gap = 0`，说明 `q_desired` 已完整进入底层 position target。
- 当前 `Kp=120, Kd=10` 的问题是实际跟踪误差仍偏大：真实 `tracking_error_abs_mean / q_desired_abs_mean = 0.532`，说明球铰实际姿态只是在稳定跟踪，不能认为已经高精度跟上 policy 目标。
- MATLAB 简化 plant 中，`Kp=120, Kd=10` 的预测 tracking error 不差，甚至比 best-risk 候选略低；它排名靠后主要是因为简化模型中的平滑 / 振荡风险项偏高。
- 综合 risk 第一的 `Kp=320, Kd=24` 平滑性更好，但 `qdot_limit_rate = 0.328`，已经明显高于当前参数，不能直接替换为训练默认值。
- 因此当前参数不是明显错误，更准确的判断是：`120/10` 适合作为保守稳定基线；若要降低 tracking error，应先用 Isaac GUI 短回放对照 `120/16`、`160/16`，再把 `320/24` 作为激进候选单独观察。
- `old_error_mean` 是当前 Isaac 真实回放中的 `|q_desired - q_actual|`，不是 MATLAB 模型预测值；`new_error_mean` 是简化单轴 plant 对候选 `Kp/Kd` 的预测，只能用于预筛，不能替代 Isaac 回放。

## 5. 结果文件

- 全量扫参指标：`/home/ubuntu/Graduation-Project/results/stage0_model200_ball_joint_pd_matlab/metrics_stage0_model200_uniform_gain_sweep.csv`
- 候选表：`/home/ubuntu/Graduation-Project/results/stage0_model200_ball_joint_pd_matlab/best_stage0_model200_uniform_gain_candidates.csv`
- 每个 case 的最优参数：`/home/ubuntu/Graduation-Project/results/stage0_model200_ball_joint_pd_matlab/best_stage0_model200_uniform_gain_by_case.csv`
- 代表性曲线目录：`/home/ubuntu/Graduation-Project/results/stage0_model200_ball_joint_pd_matlab/figures`
