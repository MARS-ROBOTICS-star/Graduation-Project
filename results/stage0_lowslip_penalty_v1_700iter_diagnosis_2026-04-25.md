# Stage0 low-slip penalty v1 700 iteration 训练诊断报告

## 1. 训练基本信息

- 训练时间：2026-04-25
- run name：`stage0_lowslip_penalty_v1_700iter`
- run 目录：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_15-42-10_stage0_lowslip_penalty_v1_700iter`
- 启动命令：
  - `TERM=xterm MPLCONFIGDIR=/tmp OMNI_KIT_ACCEPT_EULA=YES /home/ubuntu/IsaacLab/isaaclab.sh -p scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --max_iterations 700 --run_name stage0_lowslip_penalty_v1_700iter`
- 实际执行：完整跑满 `700` iterations
- 总训练时间：`6035.71 s`
- TensorBoard 导出目录：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_15-42-10_stage0_lowslip_penalty_v1_700iter/tensorboard_export`
- 保存 checkpoint：
  - `model_0.pt`
  - `model_25.pt`
  - `model_50.pt`
  - ...
  - `model_675.pt`
  - `model_699.pt`

本轮相对上一轮主要变化：

- 新增 low-slip 评价指标。
- `slip_penalty_weight: -2.0 -> -4.0`
- `slip_angle_penalty_ratio: 4.0 -> 6.0`
- low-slip 阈值：
  - 纵向滑移均值 `< 1.0`
  - 侧滑角均值 `< 0.35 rad`
- checkpoint 保存间隔：
  - `save_interval: 100 -> 25`

## 2. 总体结论

本轮训练成功解决了“保存平台 checkpoint”的工程问题，也再次证明当前任务可以被策略学到：后段 `success_rate` 长时间维持在 `0.95` 左右，并多次达到 `1.0`。

但本轮没有解决低滑移控制问题。更强的 `slip_penalty` 主要降低了早期的纵向滑移，并没有让最终策略进入低侧滑、低纵滑状态。训练后段出现了明显的目标冲突：策略为了稳定完成 waypoint，持续提高轮速参考，成功率上升的同时侧滑角上升，low-slip 综合达标率下降。

因此，本轮不能作为“低侧滑 / 低纵滑协同转向已经实现”的证据。它只能支持以下结论：

- 当前 Stage0 在 `0.5 m` 成功半径和双 waypoint 转向约束下仍可学到高成功率策略。
- 单纯提高滑移惩罚权重不足以改变策略最终采用的高侧滑完成方式。
- low-slip 指标已经能暴露“成功完成”和“低滑移完成”之间的差异，评价体系本身是有用的。

## 3. 分阶段数据

| iteration 区间 | success | timeout | far | mean reward | 纵向滑移 | 侧滑角 | low-slip 综合达标 | 纵滑达标 | 侧滑达标 | 轮速参考 | active waypoint 误差 | episode 完成度 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0-99 | 0.004 | 0.744 | 0.255 | -19.12 | 3.543 | 0.524 | 0.043 | 0.110 | 0.164 | 2.489 | 7.790 | 4.19% |
| 100-199 | 0.030 | 0.970 | 0.000 | -9.15 | 2.750 | 0.506 | 0.066 | 0.135 | 0.205 | 2.750 | 5.454 | 5.76% |
| 200-349 | 0.149 | 0.830 | 0.021 | 0.04 | 2.695 | 0.524 | 0.066 | 0.140 | 0.191 | 3.278 | 4.986 | 16.24% |
| 350-474 | 0.712 | 0.288 | 0.000 | 17.89 | 2.775 | 0.607 | 0.043 | 0.127 | 0.112 | 5.191 | 5.017 | 19.17% |
| 475-599 | 0.916 | 0.084 | 0.000 | 22.88 | 2.847 | 0.650 | 0.031 | 0.113 | 0.077 | 6.293 | 5.146 | 21.57% |
| 600-699 | 0.953 | 0.047 | 0.000 | 25.88 | 2.892 | 0.680 | 0.020 | 0.101 | 0.050 | 6.811 | 5.504 | 26.59% |
| 650-699 | 0.960 | 0.040 | 0.000 | 26.11 | 2.888 | 0.681 | 0.019 | 0.100 | 0.048 | 6.787 | 5.498 | 26.83% |
| 675-699 | 0.976 | 0.024 | 0.000 | 26.58 | 2.899 | 0.685 | 0.018 | 0.099 | 0.045 | 6.889 | 5.522 | 26.08% |

阶段变化可以概括为：

- 前 `100` 轮：策略未学会任务，失败主要来自 timeout 和 far_from_target。
- `100-349`：far_from_target 基本消失，说明策略学会避免明显跑飞，但大多数 episode 仍 timeout。
- `350-474`：成功率开始快速拉升，reward 同步转正。
- `475` 以后：进入高成功率平台，但低滑移指标持续恶化。

## 4. 关键里程碑

- 第一次 `success_rate >= 0.5`：iteration `243`
- 第一次 `success_rate >= 0.8`：iteration `373`
- 第一次 `success_rate >= 0.9`：iteration `397`
- 第一次 `success_rate >= 0.95`：iteration `397`
- 第一次 `success_rate = 1.0`：iteration `457`
- 第一次 25 轮滑动平均 `success_rate >= 0.8`：iteration `446`
- 第一次 25 轮滑动平均 `success_rate >= 0.9`：iteration `470`
- 第一次 25 轮滑动平均 `success_rate >= 0.95`：iteration `587`

这说明平台期大约从 `470` 附近开始形成，从 `587` 附近进入较稳定的高成功率阶段。由于保存间隔已改为 `25`，本轮已经保存了多个平台 checkpoint，包括：

- `model_475.pt`
- `model_500.pt`
- `model_525.pt`
- `model_550.pt`
- `model_575.pt`
- `model_600.pt`
- `model_625.pt`
- `model_650.pt`
- `model_675.pt`
- `model_699.pt`

## 5. 末尾状态

iteration `699` 的关键值：

| 指标 | 数值 |
|---|---:|
| `success_rate` | 0.9453 |
| `time_out_rate` | 0.0547 |
| `far_from_target_rate` | 0.0000 |
| `mean_reward` | 25.8630 |
| `wheel_longitudinal_slip_abs_mean_raw` | 2.8632 |
| `wheel_slip_angle_abs_mean_raw` | 0.6344 |
| `LowSlip/combined_pass_rate` | 0.0414 |
| `LowSlip/longitudinal_slip_pass_rate` | 0.1171 |
| `LowSlip/slip_angle_pass_rate` | 0.0995 |
| `LowSlip/longitudinal_slip_margin` | -1.8632 |
| `LowSlip/slip_angle_margin` | -0.2844 |
| `wheel_speed_reference_abs_mean_raw` | 5.8636 |
| `wheel_torque_target_abs_mean_raw` | 2.9055 |
| `active_waypoint_pos_error` | 5.1704 |
| `active_segment_completion_pct` | 48.3612 |
| `waypoints_completed_mean` | 0.4352 |
| `episode_completion_pct` | 21.7590 |
| `tilt_deg` | 0.1194 |
| `contact_force_sum_raw` | 1.0423 |

末尾状态说明：

- 成功率已经较高，但不是严格满成功。
- far_from_target 已经消失，说明失败不再主要来自跑飞。
- timeout 仍有少量存在，说明部分 episode 仍无法在时限内完成。
- 纵向滑移仍明显高于阈值 `1.0`。
- 侧滑角仍明显高于阈值 `0.35 rad`。
- low-slip 综合达标率只有 `4.14%`，不能视为低滑移策略。

## 6. 最优值与异常点

| 指标 | 最小值 | 最大值 |
|---|---:|---:|
| `success_rate` | iteration `0`: 0.0000 | iteration `457`: 1.0000 |
| `mean_reward` | iteration `10`: -36.8253 | iteration `686`: 27.5781 |
| `longitudinal_slip` | iteration `300`: 2.5762 | iteration `1`: 9.5062 |
| `slip_angle` | iteration `8`: 0.4823 | iteration `588`: 0.7069 |
| `low_slip_combined` | iteration `1`: 0.0035 | iteration `319`: 0.0812 |
| `low_slip_longitudinal` | iteration `1`: 0.0117 | iteration `334`: 0.1563 |
| `low_slip_angle` | iteration `588`: 0.0275 | iteration `130`: 0.2357 |
| `wheel_speed_reference` | iteration `3`: 1.8195 | iteration `587`: 7.7599 |
| `episode_completion_pct` | iteration `0`: 0.0000 | iteration `645`: 31.4743 |
| `active_waypoint_pos_error` | iteration `357`: 3.9357 | iteration `0`: 9.8646 |

最重要的异常不是单点尖峰，而是趋势：

- `slip_angle` 最大值出现在 `588`，接近高成功率平台形成后的阶段。
- `low_slip_angle_pass_rate` 最低值也出现在 `588`。
- `wheel_speed_reference` 最大值出现在 `587`。

这三个点相邻，说明高轮速参考、侧滑角升高、低侧滑达标率下降是同一类行为的不同表现。

## 7. 相关性分析

全训练过程相关性：

| 指标对 | 相关系数 |
|---|---:|
| success vs slip_angle | 0.925 |
| success vs long_slip | -0.098 |
| success vs low_slip_combined | -0.734 |
| success vs wheel_ref | 0.945 |
| wheel_ref vs slip_angle | 0.977 |
| wheel_ref vs low_slip_combined | -0.780 |
| mean_reward vs success | 0.934 |

后段 `475-699` 相关性：

| 指标对 | 相关系数 |
|---|---:|
| success vs slip_angle | 0.464 |
| success vs long_slip | 0.377 |
| success vs low_slip_combined | -0.443 |
| success vs wheel_ref | 0.441 |
| wheel_ref vs slip_angle | 0.978 |
| wheel_ref vs low_slip_combined | -0.930 |
| mean_reward vs success | 0.485 |

解释：

- 全程看，success 与 wheel_ref、slip_angle 都强正相关。这说明训练主要通过更强的运动执行能力把任务完成率拉上来。
- wheel_ref 与 slip_angle 的相关性接近 `0.98`，说明轮速参考增大和侧滑角增大几乎同步。
- success 与 low_slip_combined 为负相关，说明当前优化方向仍优先满足到点成功，而不是低滑移完成。
- 后段相关性减弱但方向不变，说明平台期内低滑移问题仍未自然消失。

## 8. 与上一轮早停训练的关系

上一轮 `stage0_tol05_turn2_gt_turn1_700iter` 在 iteration `269-294` 已经出现连续满成功平台，但由于 `save_interval=100`，没有保存平台末端 checkpoint。

本轮解决了保存问题：

- `save_interval=25` 后，平台期内保存了多个 checkpoint。
- 即使未来按平台期早停，也更容易留下可回放模型。

但本轮没有解决控制质量问题：

- 上一轮后 20 轮侧滑角约 `0.711 rad`，纵向滑移约 `3.002`。
- 本轮后 25 轮侧滑角约 `0.685 rad`，纵向滑移约 `2.899`。
- 数值略低，但仍远高于当前 low-slip 阈值，不能认为已经低滑移化。

## 9. 结论与下一步判断

本轮训练后的核心判断：

1. 如果只看 Stage0 到点成功，本轮是有效训练。
2. 如果目标是低侧滑、低纵滑，本轮没有达标。
3. `slip_penalty` 加权增强后没有改变策略的主要完成方式，说明低滑移目标还没有在优化问题中占据足够强的位置。
4. 当前 reward 仍允许策略用“高轮速、高侧滑、快速到点”的方式取得高回报。
5. 下一轮不应只继续线性加大同一个 `slip_penalty`，否则可能只是降低 reward 或成功率，而不一定产生期望的低滑移行为。

下一步需要用户先判断研究取向：

- 若当前阶段目标仍是“先保任务完成”，可以选取 `model_600.pt`、`model_650.pt`、`model_675.pt` 或 `model_699.pt` 做 deterministic replay，观察哪一个 checkpoint 的成功率和运动形态更稳。
- 若下一阶段目标切换为“低滑移完成”，需要把 low-slip 从评价指标进一步提升为更强的训练约束，例如把侧滑角惩罚从均值型软惩罚改成阈值超限惩罚、分阶段 curriculum、或把高侧滑行为作为 episode 质量约束。但这属于任务目标层面的选择，需要用户确认后再实现。

