# Stage0 low-slip progress gate v1 训练诊断报告

## 1. Run Identification（运行识别）

- 训练 run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_18-26-58_stage0_lowslip_gate_v1_700iter`
- Hydra 目录：`RL_Training/outputs/2026-04-25/18-26-58`
- Isaac Lab 日志：`/tmp/isaaclab/logs/isaaclab_2026-04-25_18-26-58.log`
- TensorBoard 导出：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_18-26-58_stage0_lowslip_gate_v1_700iter/tensorboard_export`
- 训练命令：`/home/ubuntu/IsaacLab/isaaclab.sh -p scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --max_iterations 700 --run_name stage0_lowslip_gate_v1_700iter`
- checkpoint：已保存 `model_0.pt` 到 `model_699.pt`，并按 `25` iteration 间隔保存平台期 checkpoint，包括 `model_600.pt`、`model_625.pt`、`model_650.pt`、`model_675.pt` 和最终 `model_699.pt`。

## 2. Startup and Configuration（启动与配置）

- 设备：`cuda:0`
- 并行环境数：`64`
- 最大 iteration：`700`
- 实际结束：完整跑到 `699/700`，没有中途停止。
- PPO 保存间隔：`25`
- 观测 / 动作维度：actor `54`、critic `54`、action `8`
- Stage0 任务设置：
  - 双 waypoint：`num_waypoints_per_episode = 2`
  - 每段目标距离：`10 m`
  - 成功半径：`0.5 m`
  - 每回合时长：`40 s`
- low-slip gate 参数：
  - 纵滑 gate：六轮乘积，`k = 3.0`
  - 侧滑 gate：六轮余弦 gate，scale 为 `1.5 rad`
  - 综合 gate：纵滑 gate 与侧滑 gate 平均
  - progress multiplier：$M = 0.25 + 1.25G$
  - 只门控正向 `progress_to_target`，负向 progress 不削弱
- slip 相关配置：
  - `slip_penalty_weight = -2.0`
  - `slip_angle_penalty_ratio = 6.0`
  - low-slip 评价阈值：纵滑均值 `< 1.0`，侧滑角均值 `< 0.35 rad`
- 启动日志结论：
  - articulation 正常初始化：`17` 个 body、`12` 个 joint。
  - `ball_joints` 与 `wheel_joints` actuator collection 均正常解析。
  - 未看到导致训练失败的 Isaac Lab / articulation 启动错误。
  - 结束时有 USD stage reference count warning，属于关闭阶段警告，不影响本轮训练结果读取。

## 3. Core Training Outcome（核心训练结果）

本轮任务成功率达到了高成功平台，并且最终保存了平台期 checkpoint。

| 指标 | 开始 | 最终 iteration 699 | 后 115 轮均值 585-699 | 后 25 轮均值 675-699 |
|---|---:|---:|---:|---:|
| `Train/mean_reward` | `-1.919` | `21.778` | `20.785` | `21.590` |
| `Train/mean_episode_length` | `253.765` | `876.320` | `990.009` | `900.831` |
| `success_rate` | `0.000` | `0.9766` | `0.9592` | `0.9863` |
| `time_out_rate` | `0.8809` | `0.0234` | `0.0408` | `0.0137` |
| `episode/waypoints_completed` | `0.000` | `1.9766` | `1.9503` | `1.9841` |
| `episode/waypoint_completion_pct` | `0.000%` | `98.828%` | `97.512%` | `99.207%` |
| `episode/success_hit_pos_error` | `0.499 m` | `0.490 m` | `0.490 m` | `0.490 m` |

成功率阶段特征：

- 第一次单轮 `success_rate >= 0.5`：iteration `202`
- 第一次单轮 `success_rate >= 0.8`：iteration `404`
- 第一次单轮 `success_rate >= 0.9`：iteration `534`
- 第一次单轮 `success_rate = 1.0`：iteration `555`
- 第一次 25 轮滑动平均 `success_rate >= 0.95`：窗口结束于 iteration `602`
- 第一次 50 轮滑动平均 `success_rate >= 0.95`：窗口结束于 iteration `627`
- 最长连续满成功：iteration `688-698`，连续 `11` 轮 `success_rate = 1.0`

因此，本轮满足“成功率拉上来并进入平台期”的训练目标。它不是严格每一轮都满成功的平台，后段仍有少量波动，例如 `585-699` 区间最小 success 为 `0.8086`，但后 25 轮均值已达到 `0.9863`。

## 4. Reward and Error Diagnosis（奖励与误差诊断）

任务完成主要仍由 `reached_target` 和 `progress_to_target` 驱动。后 25 轮均值中：

- `progress_to_target` 单步贡献约 `0.00675`
- `reached_target` 单步贡献约 `0.01947`
- `distance_to_target` 单步贡献约 `0.00185`
- `angle_diff` 单步贡献约 `0.00196`
- `slip_penalty` 单步贡献约 `-0.00574`
- `turn_speed_penalty` 单步贡献约 `-0.00027`

low-slip gate 的实际状态：

| 指标 | 最终 iteration 699 | 后 115 轮均值 585-699 | 后 25 轮均值 675-699 |
|---|---:|---:|---:|
| `ProgressGate/combined_gate` | `0.1133` | `0.1146` | `0.1139` |
| `ProgressGate/multiplier` | `0.3917` | `0.3933` | `0.3924` |
| `ProgressGate/longitudinal_gate` | `0.1970` | `0.1936` | `0.1963` |
| `ProgressGate/slip_angle_gate` | `0.0297` | `0.0356` | `0.0314` |

这说明 gate 确实在工作：高滑移时正向 progress 只剩约 `39%` 的倍率。但侧滑 gate 长期接近 `0.03`，它是当前 gate 的主要瓶颈。

low-slip 结果没有达标：

| 指标 | 开始 | 最终 iteration 699 | 后 115 轮均值 585-699 | 后 25 轮均值 675-699 |
|---|---:|---:|---:|---:|
| 纵向滑移均值 | `9.048` | `2.719` | `2.808` | `2.739` |
| 侧滑角均值 | `0.518 rad` | `0.690 rad` | `0.680 rad` | `0.691 rad` |
| `LowSlip/longitudinal_slip_pass_rate` | `0.035` | `0.114` | `0.114` | `0.114` |
| `LowSlip/slip_angle_pass_rate` | `0.186` | `0.024` | `0.034` | `0.029` |
| `LowSlip/combined_pass_rate` | `0.006` | `0.012` | `0.014` | `0.013` |

相对阈值看，后 25 轮纵滑均值约 `2.739`，距离 `< 1.0` 的 low-slip 阈值仍差约 `1.739`；侧滑角均值约 `0.691 rad`，距离 `< 0.35 rad` 的阈值仍差约 `0.341 rad`。也就是说，本轮虽然把纵滑从早期高值压低了，但没有进入低纵滑区间；侧滑角反而随任务成功率上升而上升。

与上一轮 low-slip penalty v1 的后 25 轮相比：

| 指标 | penalty v1 后 25 轮 | gate v1 后 25 轮 | gate v1 变化 |
|---|---:|---:|---:|
| `success_rate` | `0.9757` | `0.9863` | `+0.0107` |
| `Train/mean_reward` | `26.575` | `21.590` | `-4.985` |
| 纵向滑移均值 | `2.899` | `2.739` | `-0.160` |
| 侧滑角均值 | `0.685 rad` | `0.691 rad` | `+0.006 rad` |
| `LowSlip/combined_pass_rate` | `0.0179` | `0.0131` | `-0.0048` |
| `LowSlip/longitudinal_slip_pass_rate` | `0.0993` | `0.1144` | `+0.0151` |
| `LowSlip/slip_angle_pass_rate` | `0.0449` | `0.0286` | `-0.0163` |
| 轮速参考均值 | `6.889` | `6.343` | `-0.546` |

这个对比很关键：gate v1 确实降低了轮速参考和纵向滑移，但没有降低侧滑角；综合 low-slip 达标率反而更低。当前 gate 对“低纵滑”有一点正向作用，对“低侧滑完成方式”没有形成有效约束。

## 5. Numerical Stability（数值稳定性）

- value loss：开始 `0.0096`，最终 `0.0286`，最大约 `0.2002`，未出现发散。
- surrogate loss：开始 `0.0218`，最终 `-0.0111`，波动正常。
- entropy：从 `-1.524` 到 `-4.107`，说明策略分布逐步收敛。
- policy mean std：从 `0.2000` 降到 `0.1456`，没有塌缩到接近零。
- FPS：平均约 `4005` steps/s，最终约 `3969` steps/s。
- 未看到 NaN、训练崩溃、articulation 初始化失败或终止异常。

控制质量方面：

- 后 25 轮轮速参考均值约 `6.343`，仍然偏高，但低于 penalty v1 的 `6.889`。
- 后 25 轮 torque target 均值约 `2.615`。
- 后 25 轮 tilt 约 `0.817 deg`，车体姿态没有明显失稳。
- 部分球铰 limit usage 后段较高，例如最终 `spm1_platform_joint_x_limit_usage_max ≈ 0.877`、`spm2_platform_joint_z_limit_usage_max ≈ 0.765`，说明策略在成功平台期使用了较激进的关节姿态范围，但没有触发 ball joint limit termination。

## 6. Diagnosis（诊断结论）

最大正向信号：本轮 low-slip gate v1 在不破坏任务学习的情况下，完整跑满 `700` iterations，并在后段形成高成功率平台；最终 `model_699.pt` 和多个平台 checkpoint 都可用于回放。

主要问题：本轮没有实现“低侧滑、低纵滑完成 waypoint”的目标。纵滑有所降低，但仍远高于 `< 1.0` 阈值；侧滑角维持在约 `0.68-0.69 rad`，明显高于 `< 0.35 rad` 阈值。策略仍然学会了在较高侧滑条件下完成目标。

当前最合理的解释是：

- `ProgressGate/multiplier` 后段约 `0.39`，对高滑移 progress 有削弱，但没有削弱到足以改变策略主路径。
- `reached_target` 仍提供强终点奖励，策略可以通过高侧滑快速命中目标来补偿 progress 折扣。
- 综合 gate 使用“纵滑 gate 与侧滑 gate 平均”，当纵滑 gate 仍有约 `0.19` 时，即使侧滑 gate 约 `0.03`，综合 gate 仍能维持约 `0.11`，再经过 `M_min = 0.25` 的保底后，最终仍保留约 `39%` 的正向 progress。
- 因此，当前 gate 是有效的 soft shaping，但不是低滑移约束；它不能单独保证低侧滑策略。

下一步建议只作为待用户判断的研究选择，不应直接自动实施：

- 如果目标是“保留高成功率，同时轻微改善纵滑”，当前 gate v1 有一定价值，可以优先回放 `model_650.pt`、`model_675.pt`、`model_699.pt` 核对实际运动。
- 如果目标是“低侧滑必须达标”，仅继续调大同类 penalty 或保留当前平均 gate 不够，应重新讨论是否把 low-slip 变成成功条件、课程门槛或更强的 progress 质量约束。
- 如果下一轮仍采用 gate 路线，优先讨论侧滑 gate 的组合方式和倍率下限，而不是继续只看总成功率。
