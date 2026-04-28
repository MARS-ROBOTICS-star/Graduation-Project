# Stage0 policy 输出低前进速度根因诊断

日期：2026-04-28

## 诊断对象

- 前置 run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-27_22-42-33_stage0_direct_velocity_no_shaping_watch_700iter`
- resume run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-28_08-24-09_stage0_direct_velocity_no_shaping_resume_from75_625iter`
- checkpoint：`model_200.pt`

本诊断关注一个问题：为什么 policy 的 `vx_cmd` 会从能给出一定前进速度，逐渐收缩到接近不前进。

## 关键事实

`resume200` 这轮中，policy 速度降低时，训练回报反而变好：

| 指标 | 前 10 step 均值 | 后 25 step 均值 |
|---|---:|---:|
| `desired_planar_vx_raw` | `0.358 m/s` | `0.083 m/s` |
| `v_parallel_abs_mean_raw` | `0.224 m/s` | `0.096 m/s` |
| `active_segment_completion_pct` | `30.2%` | `21.5%` |
| `Train/mean_reward` | `-6.64` | `-3.10` |
| `episode/return` | `-5.53` | `-3.10` |

同一 run 内，`vx` 与回报呈明显负相关：

- `corr(vx, Train/mean_reward) ≈ -0.78`
- `corr(vx, episode/return) ≈ -0.75`
- `corr(vx, progress_to_target) ≈ -0.68`

这说明低速不是偶然现象，而是当前训练信号实际在奖励“降低前进速度”。

## 直接原因 1：正向 progress 被 low-slip gate 压到几乎没有学习信号

`resume200` 后 25 step：

| 指标 | 后 25 step 均值 |
|---|---:|
| `progress_gate_longitudinal` | `0.000368` |
| `progress_gate_slip_angle` | `0.264` |
| `progress_gate_combined` | `0.000195` |
| `progress_gate_multiplier` | `0.25024` |
| `progress_positive_raw` | `0.000123` |
| `Reward/progress_to_target` | `0.000096` |

这轮训练使用的日志口径显示 combined gate 基本被纵滑 gate 卡死，`progress_multiplier` 长期贴在 `0.25` 下限附近。也就是说，即使车辆有正向进度，policy 得到的正向进度奖励也很弱。

关键参数差异：

- 当前 direct velocity run：`progress_gate_longitudinal_k = 0.5`
- 历史能跑通的 `2026-04-25_18-26-58`：`progress_gate_longitudinal_k = 3.0`

同样是几倍量级的纵滑，`k=0.5` 会把 `G_kappa` 压到接近零；`k=3.0` 还能保留一部分 progress 信号。历史 `18-26-58` 后 25 step 的 `Reward/progress_to_target≈0.00675`，而 `resume200` 后 25 step 只有约 `0.000096`，相差约 `70` 倍。

## 直接原因 2：运动探索经常产生负 progress，PPO 学到“慢一点更不亏”

在 `direct75` 前置训练中，`vx` 和 active segment completion 曾一起升高：

- 后 25 step `desired_planar_vx≈0.227 m/s`
- 最后一步 `desired_planar_vx≈0.436 m/s`
- 最后一步 `active_segment_completion_pct≈30.3%`

但这时 `progress_to_target` 反而变差：

- `corr(vx, progress_to_target) ≈ -0.78`
- `corr(v_parallel, progress_to_target) ≈ -0.81`

这表示探索出来的“动起来”很多时候不是稳定朝目标推进，而是滑、转、偏航或构型运动导致目标距离变化噪声很大，甚至变差。对 PPO 来说，降低 `vx` 可以减少负 progress 和运动噪声，于是回报上升。

## 直接原因 3：timeout / reached target 都太远，不能给早期速度动作有效信用分配

当前控制周期是 `1 / 60 s`，PPO 使用 `gamma=0.99`。按控制步折扣：

| 时间 / 步数 | 折扣因子 |
|---|---:|
| `60` 步，约 `1 s` | `0.547` |
| `300` 步，约 `5 s` | `0.049` |
| `512` 步，约 `8.5 s` | `0.0058` |
| `2400` 步，约 `40 s` | `3.3e-11` |

因此，40 s 末尾的 timeout penalty 对 episode 前段动作几乎没有信用分配能力。`reached_target` 也是稀疏事件；在没有形成命中样本之前，它同样不能稳定推动早期 `vx` 增大。

这解释了为什么“加了 timeout 惩罚”仍不足以让 policy 主动提速：它主要改变 episode 末端的 return，不等价于每一步都告诉 policy “现在不前进会变差”。

## 直接原因 4：每步正奖励仍允许低速 timeout 局部解

`resume200` 后 25 step 每步量级：

| 项 | 后 25 step 均值 |
|---|---:|
| `Reward/distance_to_target` | `0.00156` |
| `Reward/angle_diff` | `0.00132` |
| `Reward/progress_to_target` | `0.000096` |
| `Reward/timeout_penalty` | `-0.00431` |

`distance_to_target` 和 `angle_diff` 是每步正向项，低速或近似原地也能拿到。正向 progress 很小，timeout 又是远期/稀疏信号，所以“低速活到 timeout”仍然是一个可被 PPO 找到的局部解。

## 物理层放大因素

当前不是 actuator 完全没执行，也不是 allocator 输出零：

- 后 25 step `wheel_speed_reference_abs≈2.24 rad/s`
- 后 25 step `wheel_joint_vel_abs≈2.10 rad/s`
- 后 25 step `v_parallel_abs≈0.096 m/s`

按 `r=0.19 m` 粗略估算，轮周速度量级约 `0.43 m/s`，但有效滚动速度只有约 `0.096 m/s`。轮速到有效推进的转化效率偏低，会让 progress 奖励更弱、更噪声化，从而进一步鼓励 policy 降低速度。

## 本质结论

policy 输出速度低的本质原因不是单个语义错误，也不是车轮速度目标没下发。

本质是当前训练目标的信用分配结构不成立：有效前进的正反馈被纵滑 gate 和运动噪声压得太弱，而失败 timeout / 成功命中又太远、太稀疏；在这种信号下，PPO 发现降低 `vx` 会提高 return，于是收敛到“低速、低风险、活到 timeout”的局部解。

更短地说：

> 当前 reward 没有让“不前进”在每个控制阶段都明确变差；相反，在这批训练数据中，降低前进速度能减少负 progress 和运动噪声，从而提高回报。

## 后续验证重点

下一轮不应只看 `success_rate`，必须同时看：

- `desired_planar_vx_raw`
- `LowLevel/v_parallel_abs_mean_raw`
- `ProgressGate/positive_progress_raw`
- `ProgressGate/negative_progress_raw`
- `ProgressGate/longitudinal_gate`
- `ProgressGate/slip_angle_gate`
- `Reward/progress_to_target`
- `episode/return`
- `waypoints_completed`

只要出现“`vx` 降低而 return 升高”，就说明奖励仍在鼓励低速局部解。
