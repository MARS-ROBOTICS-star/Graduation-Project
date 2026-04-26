# Stage0 low-slip gate v2 训练诊断报告

报告对象：`stage0_lowslip_gate_v2_min_lowlevel_800iter`

报告状态：原计划 `800` iteration，用户在 iteration `522/800` 后要求停止。本报告基于 TensorBoard step `0-522`，核心判断使用后 `25` 轮均值。

---

## 1. 结论速览

| 结论项 | 关键数据 | 判断 |
|---|---:|---|
| 成功率 | 后 25 轮 `success_rate = 1.000` | 表面成功率已平台 |
| 超时 | 后 25 轮 `time_out_rate = 0.000` | 超时基本消失 |
| 完整 waypoint 完成度 | 后 25 轮 `waypoints_completed_mean = 0.481` | 与成功率严重冲突 |
| episode 完成度 | 后 25 轮 `episode_completion_pct = 24.07%` | 不支持完整双 waypoint 成功 |
| 纵向滑移 | 后 25 轮 `3.066` | 未达低滑移目标 |
| 侧滑角 | 后 25 轮 `0.709 rad / 40.6 deg` | 高于 `0.5 rad / 30 deg` 目标 |
| 低滑移综合达标率 | 后 25 轮 `0.0197` | 只有约 `2.0%` |
| progress gate multiplier | 后 25 轮 `0.139` | gate 已接近下限 |
| per-wheel 诊断 | 六轮纵滑均高 | 不是单个左侧轮问题 |

核心判断：

- v2 gate 没有压死学习，策略能进入 `success_rate` 平台。
- v2 gate 没有迫使策略形成低侧滑、低纵滑完成方式。
- 当前最优先的问题是指标语义冲突：`success_rate = 1.0` 不能再单独解释为完整双 waypoint 成功。
- 当前 reward 中 `reached_target` 仍然主导学习，progress gate 只压低 `progress_to_target`，不足以阻止高滑移命中策略。

---

## 2. Run 信息

| 项目 | 内容 |
|---|---|
| run | `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-26_10-32-46_stage0_lowslip_gate_v2_min_lowlevel_800iter` |
| run name | `stage0_lowslip_gate_v2_min_lowlevel_800iter` |
| 计划迭代 | `800` |
| 实际停止点 | iteration `522/800` 后停止 |
| TensorBoard 范围 | step `0-522`，共 `523` 个记录点 |
| 最后 checkpoint | `model_500.pt` |
| 导出目录 | `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-26_10-32-46_stage0_lowslip_gate_v2_min_lowlevel_800iter/tensorboard_export` |

---

## 3. 训练主指标

### 3.1 平台表现

| 指标 | 首值 | 最后值 | 后 25 轮均值 | 后 50 轮均值 | 判断 |
|---|---:|---:|---:|---:|---|
| `Termination/success_rate` | `0.000` | `1.000` | `1.000` | `0.9998` | 成功率平台 |
| `Termination/time_out_rate` | `0.881` | `0.000` | `0.000` | `0.0002` | 超时消失 |
| `Train/mean_reward` | `-0.574` | `19.479` | `19.463` | `19.441` | reward 平台 |
| `Train/mean_episode_length` | `253.8` | `685.0` | `687.5` | `691.2` | 后段稳定 |

平台出现时间：

| 事件 | iteration 区间 | 数值 |
|---|---:|---:|
| 第一次 25 轮平均 `success_rate >= 0.95` | `319-343` | `0.9548` |
| 第一次 25 轮平均 `success_rate >= 0.99` | `342-366` | `0.9929` |
| 最长连续 `success_rate = 1.0` | `408-464` | `57` 轮 |

### 3.2 waypoint 完成度冲突

| 指标 | 首值 | 最后值 | 后 25 轮均值 | 后 50 轮均值 | 判断 |
|---|---:|---:|---:|---:|---|
| `Tracking/waypoints_completed_mean` | `0.016` | `0.480` | `0.481` | `0.481` | 与成功率冲突 |
| `Tracking/episode_completion_pct` | `0.78%` | `23.99%` | `24.07%` | `24.06%` | 不支持完整完成 |
| `Tracking/active_waypoint_pos_error` | `6.684 m` | `5.751 m` | `5.687 m` | `5.684 m` | active 目标仍远 |
| `Tracking/active_segment_completion_pct` | `33.29%` | `42.54%` | `43.18%` | `43.21%` | 只完成部分段 |

判断：后 25 轮 `success_rate = 1.0`，但 `waypoints_completed_mean ≈ 0.481`、`episode_completion_pct ≈ 24.07%`、`active_waypoint_pos_error ≈ 5.69 m`。因此当前 `Termination/success_rate` 的统计语义必须重新核对，不能直接当作完整双 waypoint 成功率。

---

## 4. 低滑移结果

| 指标 | 后 25 轮均值 | 阈值 / 目标 | 结论 |
|---|---:|---:|---|
| 纵向滑移绝对均值 | `3.066` | 评价阈值 `< 1.0` | 未达标 |
| 纵向滑移达标率 | `0.138` | 越高越好 | 只有约 `13.8%` |
| 侧滑角绝对均值 | `0.709 rad / 40.6 deg` | 用户目标约 `0.5 rad / 30 deg` | 未达标 |
| 侧滑角达标率 | `0.034` | 越高越好 | 只有约 `3.4%` |
| 低滑移综合达标率 | `0.0197` | 越高越好 | 只有约 `2.0%` |

对比上一轮 gate v1：

| 指标 | gate v1 后段 | 本轮 v2 后 25 轮 | 变化 |
|---|---:|---:|---|
| 纵向滑移 | 约 `2.739` | `3.066` | 变差 |
| 侧滑角 | 约 `0.691 rad` | `0.709 rad` | 略变差 |
| 低滑移综合达标率 | 约 `0.013` | `0.0197` | 仍很低 |

判断：这轮没有把侧滑角压到 `0.5 rad` 附近，也没有让纵滑继续下降。

---

## 5. Gate 与 reward

### 5.1 Progress gate

| 指标 | 后 25 轮均值 | 含义 |
|---|---:|---|
| `ProgressGate/longitudinal_gate` | `0.187` | 纵滑 gate 已较低 |
| `ProgressGate/slip_angle_gate` | `0.0327` | 侧滑 gate 是主要瓶颈 |
| `ProgressGate/combined_gate` | `0.0279` | 当前为 `min(Gκ,Gα)` |
| `ProgressGate/multiplier` | `0.139` | 正向 progress 基本接近下限 |

判断：v2 gate 确实识别了高侧滑行为，并把正向 progress multiplier 压到约 `0.14`。

### 5.2 Reward 构成

| reward 项 | 后 25 轮均值 | 相对作用 |
|---|---:|---|
| `Reward/reached_target` | `0.0273` | 主要正奖励 |
| `Reward/progress_to_target` | `0.00315` | 被 gate 明显压低 |
| `Reward/slip_penalty` | `-0.00611` | 不足以压制高滑移 |
| `Reward/total` | `0.0283` | 仍为正 |

判断：gate 只压低了 progress 奖励，没有压住 `reached_target` 奖励。策略仍然可以用高滑移方式拿到主要正反馈。

---

## 6. 车辆整体状态

| 指标 | 后 25 轮均值 | 判断 |
|---|---:|---|
| `wheel_speed_reference_abs_mean_raw` | `6.75` | 后段轮速参考偏高 |
| `wheel_torque_target_abs_mean_raw` | `3.07` | 扭矩稳定，无发散 |
| `pitch_deg` | `-2.95 deg` | 中车持续前俯 |
| `roll_deg` | `-0.017 deg` | 横滚不是主要问题 |

判断：策略后段没有通过降低轮速参考来换取低滑移；中车仍有持续前俯，但量级需要结合回放视觉继续确认。

---

## 7. Per-wheel 诊断

### 7.1 读表说明

当前 `PerWheel/<wheel>/slip_angle` 是 signed mean，不是每个轮子的绝对侧滑均值。它会被不同环境中的正负侧滑抵消。因此 per-wheel `slip_angle` 小，不能否定全局 `wheel_slip_angle_abs_mean_raw ≈ 0.709 rad` 的高侧滑结论。

### 7.2 滑移与转速表

#### 7.2.1 诊断总览

| 轮子 | 纵滑状态 | 转速跟踪状态 | 直接判断 |
|---|---|---|---|
| 前左 | 高纵滑，abs `2.869` | 偏差 `2.821`，六轮最大 | 纵滑高，速度偏差最大 |
| 前右 | 高纵滑，abs `2.942` | 偏差 `2.432` | 纵滑高 |
| 中左 | 高纵滑，abs `2.657` | joint vel `8.721`，六轮最低 | 不是不转，但转速最低 |
| 中右 | 高纵滑，abs `2.954` | 偏差 `2.426` | 纵滑高 |
| 后左 | 高纵滑，abs `2.856` | 偏差 `2.801` | 纵滑高，速度偏差大 |
| 后右 | 最高纵滑，abs `3.062` | 偏差 `2.789` | 纵滑最高 |

#### 7.2.2 数值明细

<table>
  <thead>
    <tr>
      <th rowspan="2">轮子</th>
      <th colspan="3">滑移指标</th>
      <th colspan="3">转速跟踪</th>
    </tr>
    <tr>
      <th>纵滑 signed mean</th>
      <th>纵滑 abs 参考</th>
      <th>slip_angle signed mean rad</th>
      <th>wheel_joint_vel</th>
      <th>wheel_speed_reference</th>
      <th>|vel-ref|</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>前左</td>
      <td><code>-2.869</code></td>
      <td><code>2.869</code></td>
      <td><code>-0.033</code></td>
      <td><code>9.311</code></td>
      <td><code>6.490</code></td>
      <td><code>2.821</code></td>
    </tr>
    <tr>
      <td>前右</td>
      <td><code>-2.942</code></td>
      <td><code>2.942</code></td>
      <td><code>-0.035</code></td>
      <td><code>9.443</code></td>
      <td><code>7.011</code></td>
      <td><code>2.432</code></td>
    </tr>
    <tr>
      <td>中左</td>
      <td><code>-2.657</code></td>
      <td><code>2.657</code></td>
      <td><code>-0.079</code></td>
      <td><code>8.721</code></td>
      <td><code>6.524</code></td>
      <td><code>2.196</code></td>
    </tr>
    <tr>
      <td>中右</td>
      <td><code>-2.954</code></td>
      <td><code>2.954</code></td>
      <td><code>-0.056</code></td>
      <td><code>9.441</code></td>
      <td><code>7.015</code></td>
      <td><code>2.426</code></td>
    </tr>
    <tr>
      <td>后左</td>
      <td><code>-2.856</code></td>
      <td><code>2.856</code></td>
      <td><code>-0.033</code></td>
      <td><code>9.297</code></td>
      <td><code>6.497</code></td>
      <td><code>2.801</code></td>
    </tr>
    <tr>
      <td>后右</td>
      <td><code>-3.062</code></td>
      <td><code>3.062</code></td>
      <td><code>-0.015</code></td>
      <td><code>9.755</code></td>
      <td><code>6.966</code></td>
      <td><code>2.789</code></td>
    </tr>
  </tbody>
</table>

滑移与转速结论：

- 六轮纵滑均高，绝对量约 `2.66-3.06`，不是单个左侧轮问题。
- 中左轮 `wheel_joint_vel ≈ 8.72`，不是完全不转，只是六轮中最低。
- 所有轮子的 `wheel_joint_vel` 都明显高于 `wheel_speed_reference`，差值约 `2.20-2.82`，这与持续高纵滑一致。

### 7.3 力矩与接触矩阵

| 轮子 | torque target | contact weight | normal force N | 直接观察 |
|---|---:|---:|---:|---|
| 前左 | `2.294` | `0.351` | `66.6` | 接触正常 |
| 前右 | `2.290` | `0.307` | `58.9` | 接触正常 |
| 中左 | `2.128` | `0.311` | `49.6` | 中段轮载低 |
| 中右 | `2.394` | `0.301` | `50.4` | 中段轮载低 |
| 后左 | `2.637` | `0.370` | `73.1` | 后段负载高 |
| 后右 | `3.335` | `0.411` | `82.4` | 负载和力矩最高 |

力矩与接触结论：

- 后右轮负载和驱动最强：纵滑绝对量约 `3.06`、力矩约 `3.33`、接触权重约 `0.411`、法向力约 `82.4 N`。
- 中车两轮法向力最低，约 `50 N`；后车两轮法向力最高，约 `77.8 N`。
- 当前不是“左侧轮整体失去接触”，而是中段轮载偏低、后段轮载偏高。

### 7.4 分组对比

| 分组 | 纵滑 abs 参考 | slip_angle signed abs 参考 | 力矩均值 | 接触权重均值 | 法向力均值 N | 判断 |
|---|---:|---:|---:|---:|---:|---|
| 左侧三轮 | `2.794` | `0.048` | `2.353` | `0.344` | `63.1` | 左侧不是主要异常源 |
| 右侧三轮 | `2.986` | `0.035` | `2.673` | `0.340` | `63.9` | 右侧纵滑和力矩略高 |
| 前车两轮 | `2.905` | `0.034` | `2.292` | `0.329` | `62.7` | 中等负载 |
| 中车两轮 | `2.805` | `0.067` | `2.261` | `0.306` | `50.0` | 轮载最低 |
| 后车两轮 | `2.959` | `0.024` | `2.986` | `0.390` | `77.8` | 负载和力矩最高 |

### 7.5 后 25 轮波动范围

| 轮子 | 纵滑范围 | slip_angle signed 范围 rad | 力矩范围 | 接触权重范围 | 法向力范围 N |
|---|---:|---:|---:|---:|---:|
| 前左 | `-2.935 ~ -2.802` | `-0.039 ~ -0.026` | `2.246 ~ 2.338` | `0.343 ~ 0.357` | `64.5 ~ 68.1` |
| 前右 | `-3.013 ~ -2.889` | `-0.043 ~ -0.026` | `2.202 ~ 2.349` | `0.302 ~ 0.312` | `57.7 ~ 60.2` |
| 中左 | `-2.728 ~ -2.614` | `-0.087 ~ -0.071` | `2.072 ~ 2.218` | `0.305 ~ 0.318` | `48.4 ~ 52.0` |
| 中右 | `-3.000 ~ -2.900` | `-0.070 ~ -0.046` | `2.340 ~ 2.452` | `0.296 ~ 0.304` | `49.3 ~ 51.5` |
| 后左 | `-2.909 ~ -2.810` | `-0.037 ~ -0.027` | `2.570 ~ 2.697` | `0.361 ~ 0.377` | `71.3 ~ 74.5` |
| 后右 | `-3.116 ~ -3.010` | `-0.021 ~ -0.010` | `3.266 ~ 3.407` | `0.404 ~ 0.419` | `81.6 ~ 83.5` |

---

## 8. 数值稳定性

| 指标 | 后 25 轮均值 | 判断 |
|---|---:|---|
| `Loss/value` | `0.0266` | 无爆炸 |
| `Loss/surrogate` | `-0.0155` | 稳定 |
| `Policy/mean_std` | `0.1556` | 策略探索收敛 |
| `Perf/total_fps` | `3556` | 训练吞吐稳定 |

判断：数值层面没有明显异常；问题主要是任务指标定义、reward 优先级和低层滑移行为，而不是 PPO 崩溃。

---

## 9. 下一步优先级

1. 优先核对 `success_rate`、`waypoints_completed_mean`、`episode_completion_pct` 的统计语义，修正成功指标冲突。
2. 若继续做 per-wheel 诊断，新增 `PerWheel/<wheel>/slip_angle_abs` 和 `PerWheel/<wheel>/longitudinal_slip_abs`，避免 signed mean 抵消。
3. 重新审查 `reached_target` 奖励是否应被低滑移 gate 约束，否则策略仍可用高滑移方式拿主要正奖励。
4. 结合回放检查中车前俯、后轮高负载和中段轮载偏低是否一致出现。
