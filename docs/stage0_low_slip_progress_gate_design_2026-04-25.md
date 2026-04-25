# Stage0 低滑移 Progress Gate 方案与数值分析

## 1. 设计背景

最新一轮 `stage0_lowslip_penalty_v1_700iter` 训练表明，单纯增强 `slip_penalty` 可以保留较高任务成功率，但没有把策略改造成低侧滑、低纵滑的完成方式。

当前策略仍倾向于用较高轮速完成 waypoint，导致成功率上升的同时侧滑角仍然偏高。因此，下一轮 reward 设计可以考虑不再把滑移只作为惩罚项，而是把低滑移质量引入 `progress_to_target` 本身。

核心思想：

- 高滑移前进仍然可以获得部分 progress，避免训练早期完全学不动。
- 低滑移前进可以获得完整甚至更高 progress。
- 高纵滑或高侧滑都会降低 progress 的有效收益。

本文件记录 reward 设计方案、数值分析和当前实现状态。该方案已在 `RL_Training/` 的 Stage0 reward 计算中接入。

## 2. 纵滑 Gate

设第 $i$ 个车轮的纵向滑移率为 $\kappa_i$，共 $6$ 个车轮。纵滑 gate 设计为：

$$
G_\kappa
=
\prod_{i=1}^{6}
\exp\left[
-\frac{1}{2}
\left(
\frac{\kappa_i}{k}
\right)^2
\right]
$$

等价于：

$$
G_\kappa
=
\exp\left[
-\frac{1}{2k^2}
\sum_{i=1}^{6}
\kappa_i^2
\right]
$$

其中 $k$ 控制纵滑 gate 的衰减速度：

- $k$ 越小，对纵滑越敏感。
- $k$ 越大，gate 越温和。

## 3. 侧滑 Gate

设第 $i$ 个车轮的侧滑角为 $\alpha_i$。侧滑 gate 设计为：

$$
G_\alpha
=
\prod_{i=1}^{6}
\left[
0.5\cos\left(x_i\right)+0.5
\right]
$$

其中：

$$
x_i
=
\operatorname{clip}
\left(
K|\alpha_i|,\ 0,\ \pi
\right)
$$

必须对 $K|\alpha_i|$ 截断到 $[0,\pi]$。否则当侧滑角继续增大时，cos 函数会周期性回升，导致大侧滑反而重新获得奖励。

## 4. 综合 Gate

用户提出的综合方式是将纵滑 gate 和侧滑 gate 相加取平均：

$$
G
=
\frac{1}{2}
\left(
G_\kappa + G_\alpha
\right)
$$

这个形式比直接让 $G_\kappa$ 和 $G_\alpha$ 相乘更温和。因为两个六轮乘积本身已经会快速衰减，如果再相乘，progress 很容易被完全压死。

## 5. 不建议直接使用 G 乘 Progress

如果直接写成：

$$
r_{\mathrm{prog,new}}
=
G r_{\mathrm{prog}}
$$

风险较大。原因是六个轮子相乘后，$G_\kappa$ 和 $G_\alpha$ 都可能非常小，尤其在训练早期或当前高滑移策略下，progress 会几乎被关死。

因此建议引入下限和上限：

$$
M
=
M_{\min}
+
\left(
M_{\max} - M_{\min}
\right)G
$$

推荐第一版取：

$$
M_{\min} = 0.25
$$

$$
M_{\max} = 1.5
$$

然后把 progress 拆成正进度和负进度。

设当前时刻到目标距离为 $d_t$，上一时刻到目标距离为 $d_{t-1}$，则：

$$
\Delta d_t = d_{t-1} - d_t
$$

其中：

- $\Delta d_t > 0$ 表示靠近目标。
- $\Delta d_t < 0$ 表示远离目标。

拆分为：

$$
\Delta d_t^+ = \max(\Delta d_t, 0)
$$

$$
\Delta d_t^- = \min(\Delta d_t, 0)
$$

最终 gated progress reward 写成：

$$
r_{\mathrm{prog,new}}
=
\frac{w_{\mathrm{prog}}}{D}
\left(
M\Delta d_t^+
+
\Delta d_t^-
\right)
$$

其中：

- $w_{\mathrm{prog}}$ 是 progress 奖励权重。
- $D$ 是单段目标距离，当前 Stage0 为 $10\ \mathrm{m}$。
- 正进度受低滑移 gate 调制。
- 负进度不受 gate 削弱，远离目标仍然完整扣分。

这样设计的含义是：

- 高滑移前进仍保留至少 $25\%$ 的 progress，避免训练被压死。
- 低滑移前进最多获得 $150\%$ 的 progress，鼓励低滑移完成。

## 6. 纵滑 Gate 数值计算

假设六个轮子的纵滑率相同。

| 每轮纵滑率 $\kappa$ | $k = 1.0$ | $k = 2.0$ | $k = 3.0$ |
|---:|---:|---:|---:|
| 0.3 | 0.763 | 0.935 | 0.970 |
| 0.6 | 0.340 | 0.763 | 0.887 |
| 1.0 | 0.050 | 0.472 | 0.717 |
| 2.0 | 0.000006 | 0.050 | 0.264 |
| 3.0 | 0.000000 | 0.001 | 0.050 |

结论：

- $k = 1.0$ 太激进，$\kappa = 1.0$ 时六轮相乘后只剩 $0.050$。
- $k = 2.0$ 中等，$\kappa = 1.0$ 时剩 $0.472$。
- $k = 3.0$ 更适合第一轮尝试，$\kappa = 1.0$ 时仍有 $0.717$。

## 7. 侧滑 Gate 数值计算

### 7.1 激进参数

如果希望 $\alpha = 0.75\ \mathrm{rad}$ 时 gate 归零，可取：

$$
K = \frac{\pi}{0.75}
$$

此时六轮侧滑角相同时：

| 每轮侧滑角 $\alpha$ | $G_\alpha$ |
|---:|---:|
| $0.10\ \mathrm{rad}$ | 0.767 |
| $0.20\ \mathrm{rad}$ | 0.338 |
| $0.35\ \mathrm{rad}$ | 0.028 |
| $0.50\ \mathrm{rad}$ | 0.00024 |
| $0.75\ \mathrm{rad}$ | 0.000 |

这个参数太激进。因为 $0.35\ \mathrm{rad}$ 本来是低侧滑阈值附近，但六轮相乘后只剩 $0.028$，会严重压制 progress。

### 7.2 温和参数

更推荐第一轮取：

$$
K = \frac{\pi}{2 \times 0.75}
=
\frac{\pi}{1.5}
$$

也就是让单轮 $\alpha = 0.75\ \mathrm{rad}$ 时，单轮 gate 为 $0.5$。

此时六轮相乘：

| 每轮侧滑角 $\alpha$ | $G_\alpha$ |
|---:|---:|
| $0.10\ \mathrm{rad}$ | 0.936 |
| $0.20\ \mathrm{rad}$ | 0.767 |
| $0.35\ \mathrm{rad}$ | 0.438 |
| $0.50\ \mathrm{rad}$ | 0.178 |
| $0.75\ \mathrm{rad}$ | 0.016 |

这个参数更合理：

- 低侧滑时保留较多 progress。
- 中等侧滑时明显降权。
- 高侧滑时几乎不给高质量 progress。

## 8. 综合 Gate 数值计算

推荐参数：

$$
k = 3.0
$$

$$
K = \frac{\pi}{2 \times 0.75}
=
\frac{\pi}{1.5}
$$

$$
G = \frac{1}{2}\left(G_\kappa + G_\alpha\right)
$$

| 情况 | $G_\kappa$ | $G_\alpha$ | 平均 $G$ | 对 progress 的影响 |
|---|---:|---:|---:|---|
| 全轮很低：$\kappa = 0.3,\ \alpha = 0.10$ | 0.970 | 0.936 | 0.953 | 几乎完整保留 |
| 全轮较低：$\kappa = 0.6,\ \alpha = 0.20$ | 0.887 | 0.767 | 0.827 | 保留 82.7% |
| 阈值附近：$\kappa = 1.0,\ \alpha = 0.35$ | 0.717 | 0.438 | 0.577 | 保留 57.7% |
| 中等偏高：$\kappa = 2.0,\ \alpha = 0.50$ | 0.264 | 0.178 | 0.221 | 只保留 22.1% |
| 高滑移：$\kappa = 3.0,\ \alpha = 0.75$ | 0.050 | 0.016 | 0.033 | 基本不给高质量 progress |
| 最新训练近似：$\kappa = 2.9,\ \alpha = 0.685$ | 0.061 | 0.034 | 0.047 | 只保留 4.7% |

如果直接用 $G$ 乘 progress，最新训练那种高滑移策略只能获得约 $4.7\%$ 的 progress，可能过于激进。

## 9. 加入下限和上限后的实际影响

使用：

$$
M = 0.25 + 1.25G
$$

则：

| 情况 | 平均 $G$ | $M$ | 实际效果 |
|---|---:|---:|---|
| 全轮很低：$\kappa = 0.3,\ \alpha = 0.10$ | 0.953 | 1.44 | progress 提高 44% |
| 全轮较低：$\kappa = 0.6,\ \alpha = 0.20$ | 0.827 | 1.28 | progress 提高 28% |
| 阈值附近：$\kappa = 1.0,\ \alpha = 0.35$ | 0.577 | 0.97 | 基本等于原 progress |
| 中等偏高：$\kappa = 2.0,\ \alpha = 0.50$ | 0.221 | 0.53 | progress 减半 |
| 高滑移：$\kappa = 3.0,\ \alpha = 0.75$ | 0.033 | 0.29 | 只保留约 29% |
| 最新训练近似：$\kappa = 2.9,\ \alpha = 0.685$ | 0.047 | 0.31 | 只保留约 31% |

这样比直接使用 $G$ 更稳健。

## 10. 当前已实现的 v1 公式

当前 `RL_Training/` 的 Stage0 已接入第一版 low-slip progress gate。当前实现使用平均组合：

$$
G_\kappa
=
\prod_{i=1}^{6}
\exp\left[
-\frac{1}{2}
\left(
\frac{\kappa_i}{3.0}
\right)^2
\right]
$$

$$
G_\alpha
=
\prod_{i=1}^{6}
\left[
0.5
\cos\left(
\operatorname{clip}
\left(
\frac{\pi|\alpha_i|}{1.5},\ 0,\ \pi
\right)
\right)
+
0.5
\right]
$$

综合 gate：

$$
G_{\mathrm{avg}}
=
\frac{1}{2}
\left(
G_\kappa + G_\alpha
\right)
$$

progress 调制系数：

$$
M
=
0.25 + 1.25G_{\mathrm{avg}}
$$

最终奖励：

$$
r_{\mathrm{prog,new}}
=
\frac{w_{\mathrm{prog}}}{D}
\left(
M\Delta d_t^+
+
\Delta d_t^-
\right)
$$

当前实现状态：

- $G_{\mathrm{avg}}$ 使用纵滑 gate 和侧滑 gate 的平均。
- $M_{\min}=0.25$。
- $M_{\max}=1.5$。
- 只门控正向 progress。
- 负向 progress 不受 gate 削弱。

## 11. v1 正式训练后的实测结果

v1 已完成一轮正式训练：

- run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_18-26-58_stage0_lowslip_gate_v1_700iter`
- 训练轮数：完整 `700` iterations
- 最终 checkpoint：`model_699.pt`

后 25 轮关键结果：

| 指标 | 后 25 轮均值 |
|---|---:|
| `Termination/success_rate` | 0.986 |
| `episode/waypoints_completed` | 1.984 |
| `episode/success_hit_pos_error` | 0.490 m |
| `Observation/wheel_longitudinal_slip_abs_mean_raw` | 2.739 |
| `Observation/wheel_slip_angle_abs_mean_raw` | 0.691 rad |
| `LowSlip/combined_pass_rate` | 0.013 |
| `ProgressGate/longitudinal_gate` | 0.196 |
| `ProgressGate/slip_angle_gate` | 0.031 |
| `ProgressGate/combined_gate` | 0.114 |
| `ProgressGate/multiplier` | 0.392 |

这个结果说明：

- 当前 v1 gate 可以保住高成功率。
- 纵向滑移相比 penalty v1 略有下降。
- 侧滑角没有下降，仍约为 $0.69\ \mathrm{rad}$。
- 当前平均 gate 仍允许 high-slip 策略获得约 $39\%$ 的正向 progress。
- high-slip 到点仍然可以拿到较高任务收益，因此 v1 不能证明低滑移完成方式已经形成。

## 12. 新组合方式的实测复算

用户提出下一步考虑把综合 gate 从平均方式改为更严格的方式：

$$
G_{\mathrm{prod}}
=
G_\kappa G_\alpha
$$

或：

$$
G_{\min}
=
\min
\left(
G_\kappa,\ G_\alpha
\right)
$$

同时将 progress multiplier 下限从 $0.25$ 降到 $0.10$，上限仍保持 $1.5$。因此新的 multiplier 写为：

$$
M
=
0.10 + 1.40G
$$

基于 v1 正式训练后 25 轮实测 gate：

$$
G_\kappa \approx 0.196
$$

$$
G_\alpha \approx 0.031
$$

可得到：

$$
G_{\mathrm{avg}}
=
\frac{0.196+0.031}{2}
\approx
0.114
$$

$$
G_{\mathrm{prod}}
=
0.196 \times 0.031
\approx
0.006
$$

$$
G_{\min}
=
\min(0.196,0.031)
\approx
0.031
$$

对应 multiplier：

| 组合方式 | $G$ | multiplier 公式 | $M$ | 相对当前 v1 的正向 progress |
|---|---:|---|---:|---:|
| 当前 v1：平均 gate，$M_{\min}=0.25$ | 0.114 | $0.25+1.25G$ | 0.392 | 100% |
| 平均 gate，$M_{\min}=0.10$ | 0.114 | $0.10+1.40G$ | 0.259 | 66.1% |
| 乘积 gate，$M_{\min}=0.10$ | 0.006 | $0.10+1.40G$ | 0.109 | 27.7% |
| min gate，$M_{\min}=0.10$ | 0.031 | $0.10+1.40G$ | 0.144 | 36.7% |

这里的“相对当前 v1 的正向 progress”表示：

$$
\frac{M_{\mathrm{candidate}}}{M_{\mathrm{v1}}}
$$

因此：

- 只降低 $M_{\min}$，但继续使用平均 gate，会把当前 high-slip progress 从约 $39.2\%$ 压到约 $25.9\%$。
- 使用乘积 gate 会把当前 high-slip progress 压到约 $10.9\%$。
- 使用 min gate 会把当前 high-slip progress 压到约 $14.4\%$。

## 13. 不同统计窗口下的稳定性核对

为了避免只看后 25 轮造成误判，继续对后 50 轮和后 100 轮做同样复算。

| 统计窗口 | $G_\kappa$ | $G_\alpha$ | $G_{\mathrm{avg}}$ | $G_{\mathrm{prod}}$ | $G_{\min}$ | 当前 $M$ | 平均 gate + 0.10 | 乘积 gate + 0.10 | min gate + 0.10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 后 25 轮 | 0.196 | 0.031 | 0.114 | 0.006 | 0.031 | 0.392 | 0.259 | 0.109 | 0.144 |
| 后 50 轮 | 0.195 | 0.033 | 0.114 | 0.007 | 0.033 | 0.393 | 0.260 | 0.109 | 0.147 |
| 后 100 轮 | 0.194 | 0.035 | 0.115 | 0.007 | 0.035 | 0.393 | 0.260 | 0.110 | 0.149 |

结论：

- 三个统计窗口结果非常接近。
- 当前 high-slip 行为下，侧滑 gate $G_\alpha$ 明显小于纵滑 gate $G_\kappa$。
- 因此 min gate 基本由侧滑 gate 决定。
- 乘积 gate 在当前数据上几乎贴近 $M_{\min}=0.10$，区分度很小。

## 14. 会不会压死 progress

如果保留 multiplier 下限：

$$
M_{\min}=0.10
$$

则 progress 不会被数学意义上压死。即使 $G=0$，正向 progress 仍有：

$$
M = 0.10
$$

也就是仍保留 $10\%$ 的正向 progress。

但需要区分“不会归零”和“是否过强”：

- 乘积 gate 后 25 轮 $M \approx 0.109$，只比下限高 $0.009$。
- 这说明乘积 gate 对当前 high-slip 行为几乎是 floor-locked。
- floor-locked 的问题是策略只能感受到“都很差”，难以区分“稍微降低侧滑”和“完全不降低侧滑”的收益差异。
- min gate 后 25 轮 $M \approx 0.144$，仍然严格，但比乘积 gate 多保留了一些可学习的梯度差异。

因此：

- $G_\kappa G_\alpha$：不会压死，但非常接近压死，训练风险较高。
- $\min(G_\kappa,G_\alpha)$：不会压死，严格程度较高，优先级高于乘积 gate。
- 平均 gate + $M_{\min}=0.10$：最稳，但对 high-slip 行为的压制可能仍不够强。

## 15. 当前推荐判断

如果下一轮只改一个 gate 组合方式，推荐顺序是：

1. 优先尝试 $\min(G_\kappa,G_\alpha)$，并将 $M_{\min}$ 降到 $0.10$。
2. 暂不直接使用 $G_\kappa G_\alpha$。
3. 若 min gate 仍不能压低侧滑，再考虑把 `reached_target` 也乘以低滑移质量 gate，或把高滑移命中从成功奖励中剥离。

推荐理由：

- 当前失败主要来自侧滑 gate 过低，但平均组合允许纵滑 gate 补偿侧滑 gate。
- min gate 可以保证纵滑和侧滑任一项差，progress 都明显下降。
- min gate 比乘积 gate 更不容易 floor-locked。
- $M_{\min}=0.10$ 可以保证训练早期仍有基础 progress，不会完全学不动。

需要避免的设计：

- 不建议直接使用硬阈值 gate。
- 不建议直接让六轮相乘后的 $G$ 乘 progress。
- 不建议把 $K$ 设为 $\pi / 0.75$ 这种过激形式。
- 不建议让 cosine 不截断，否则大侧滑时 gate 会周期性回升。
- 不建议在没有新训练验证前，把乘积 gate、低 multiplier、命中奖励 gate 和成功条件 gate 一次性全部叠加。

## 16. 当前状态

本文件最初是方案讨论与数值分析记录。当前方案已接入 `RL_Training/` 源码，位置为：

- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
- `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/utils/logger.py`

当前 `RL_Training/` 源码仍保留原有 reward 分项结构：

- `distance_to_target`
- `progress_to_target`
- `reached_target`
- `far_from_target`
- `angle_diff`
- `turn_speed_penalty`
- `slip_penalty`

但其中 `progress_to_target` 已改为 low-slip gated progress：

- 只门控正向 progress。
- 负向 progress 不受 gate 削弱。
- 当前参数为 `k = 3.0`、`K = pi / 1.5`、`M = 0.10 + 1.40G`。
- 当前源码中的 $G$ 已从 $G_{\mathrm{avg}}$ 改为 $G_{\min}=\min(G_\kappa,G_\alpha)$。
- `slip_penalty_weight` 已从 `-4.0` 降到 `-2.0`，作为背景约束保留。

新增训练日志指标：

- `ProgressGate/combined_gate`
- `ProgressGate/multiplier`
- `ProgressGate/longitudinal_gate`
- `ProgressGate/slip_angle_gate`
- `ProgressGate/positive_progress_raw`
- `ProgressGate/negative_progress_raw`
- `ProgressGate/ungated_progress_raw`

v1 已经完成正式训练验证：

- 高成功率可以保持。
- 纵滑略有下降。
- 侧滑角没有下降到目标范围。
- 当前平均 gate 不是低滑移约束，只是 soft shaping。

v2 已按用户确认接入源码：

- 已将 $G_{\mathrm{avg}}$ 改为 $G_{\min}=\min(G_\kappa,G_\alpha)$。
- 已将 $M_{\min}$ 从 $0.25$ 降到 $0.10$。
- 暂不推荐直接使用 $G_\kappa G_\alpha$。

按照上一轮 v1 后 25 轮实测 gate 估算，v2 会把 high-slip 行为的正向 progress multiplier 从约 $0.392$ 压到约 $0.144$。这不会数学归零，但会明显降低高侧滑完成方式的收益。
