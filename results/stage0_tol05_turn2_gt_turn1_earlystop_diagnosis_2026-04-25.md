# Stage0 0.5 m 成功半径双 waypoint 早停训练诊断报告

## 1. Run Identification

- 运行名称：`stage0_tol05_turn2_gt_turn1_700iter`
- Isaac Lab 日志：`/tmp/isaaclab/logs/isaaclab_2026-04-25_13-37-33.log`
- Hydra 输出目录：`RL_Training/outputs/2026-04-25/13-37-33/`
- 训练 run 目录：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_13-37-33_stage0_tol05_turn2_gt_turn1_700iter/`
- TensorBoard 导出目录：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_13-37-33_stage0_tol05_turn2_gt_turn1_700iter/tensorboard_export/`
- 原计划最大训练轮数：`700`
- 实际停止位置：iteration `294`
- 早停原因：iteration `269-294` 连续 `26` 轮 `success_rate = 1.0` 且 `time_out_rate = 0.0`，reward 与 episode length 进入平台期。
- 已保存 checkpoint：`model_0.pt`、`model_100.pt`、`model_200.pt`
- 工程限制：本轮在保存间隔中途提前中断，未保存 plateau 末端的 `model_294.pt`；因此训练日志可用于诊断，但后续 replay / eval 不能直接用 `model_200.pt` 代表最终平台策略。

## 2. Startup and Configuration

- 设备：`cuda:0`
- 并行环境数：`64`
- 每个环境 rollout 步数：`512`
- actor / critic 观测维度：`54 / 54`
- policy 动作维度：`8`
- 动作含义：`[vx_cmd, yaw_rate_cmd] + q^d`
- Stage0 任务口径：
  - 双 waypoint：`num_waypoints_per_episode = 2`
  - 每段名义距离：`10 m`
  - 偏角上限：`±30°`
  - 成功半径：`0.5 m`
  - waypoint 采样要求：第 2 段偏角绝对值大于第 1 段偏角绝对值，即 `|phi_2| > |phi_1|`
  - episode 时长：`40 s`
- 机器人 articulation 与执行器解析成功：
  - 6 个球铰执行器：`spm1/spm2_platform_joint_{x,y,z}`
  - 6 个车轮执行器：`body/head/tail_car_wheel_{left,right}_joint`
- simulator 日志未发现导致训练失败的 error / traceback；启动阶段 actuator 解析正常。

## 3. Core Training Outcome

| 指标 | 初始值 | 最终值 | 后 20 轮均值 | 解释 |
|---|---:|---:|---:|---|
| `Train/mean_reward` | `-1.409` | `33.102` | `33.254` | reward 已进入高平台。 |
| `Train/mean_episode_length` | `253.765` | `750.390` | `736.620` | 后段 episode 变短主要来自更快成功终止，不是失败。 |
| `termination_success_rate` | `0.000` | `1.000` | `1.000` | 后 20 轮全部成功。 |
| `time_out_rate` | `0.881` | `0.000` | `0.000` | 后 20 轮无超时失败。 |
| `episode/waypoints_completed` | `0.000` | `2.000` | `2.000` | episode 级统计显示两个 waypoint 都完成。 |
| `episode/waypoint_completion_pct` | `0.000%` | `100.000%` | `100.000%` | episode 完成度已饱和。 |
| `episode/waypoint_hit_rate` | `0.000` | `1.000` | `1.000` | 终止 episode 均为 waypoint 命中。 |
| `success_hit_pos_error` | - | `0.486 m` | `0.488 m` | 命中成功瞬间误差稳定低于 `0.5 m`。 |

学习过程关键节点：

- 第一次满成功出现在 iteration `210`。
- iteration `253-257` 曾连续满成功，但 iteration `258` 短暂回落到 `0.9922`。
- iteration `269-294` 连续 `26` 轮满成功，满足本次早停条件。
- 最后 `40` 轮均值：`success_rate = 0.9953`、`time_out_rate = 0.0047`，说明平台期开始前仍有少量波动，但末尾已稳定。

核心结论：

- 在 `0.5 m` 成功半径和更强第二段转向采样条件下，当前 Stage0 8 维动作 baseline 仍能学到稳定完成双 waypoint 的策略。
- 这轮结果比上一轮 `2.0 m` 成功半径更有说服力，因为 `success_hit_pos_error` 最终约 `0.486 m`，与新的成功半径一致。
- 但因为未保存 plateau 末端 checkpoint，本轮当前产物更适合作为训练趋势证据，不适合作为最终可回放策略证据。

## 4. Reward and Error Diagnosis

| 指标 | 初始值 | 最终值 | 后 20 轮均值 | 解释 |
|---|---:|---:|---:|---|
| `Reward/total` | `-0.0057` | `0.0465` | `0.0449` | per-step reward 后段稳定为正。 |
| `Reward/reached_target` | `0.0000` | `0.0265` | `0.0249` | 成功命中奖励成为主要正信号之一。 |
| `Reward/progress_to_target` | `0.0005` | `0.0211` | `0.0210` | dense progress 是主要学习驱动力。 |
| `Reward/distance_to_target` | `0.0013` | `0.0019` | `0.0019` | 量级较小，辅助作用。 |
| `Reward/angle_diff` | `0.0019` | `0.0021` | `0.0021` | 量级较小，辅助作用。 |
| `Reward/slip_penalty` | `-0.0093` | `-0.0048` | `-0.0049` | 后段惩罚较稳定，但仍不是主导项。 |

跟踪与完成度指标：

| 指标 | 最终值 | 后 20 轮均值 | 解释 |
|---|---:|---:|---|
| `Tracking/active_waypoint_pos_error` | `5.561 m` | `5.583 m` | step 级当前激活 waypoint 距离；在大量环境刚重置或已切换目标时，不等价于成功瞬间误差。 |
| `Tracking/active_waypoint_bearing_abs` | `0.209 rad` | `0.209 rad` | 当前激活 waypoint 方位误差后段较小。 |
| `Tracking/active_segment_completion_pct` | `44.452%` | `44.228%` | step 级当前段平均进度，不等价于 episode 完成度。 |
| `Tracking/waypoints_completed_mean` | `0.512` | `0.491` | step 级跨全部环境的即时完成数量，受 reset 后新 episode 影响。 |
| `Tracking/episode_completion_pct` | `25.623%` | `24.532%` | step 级即时完成比例，不能当作 episode 结束完成率。 |
| `episode/waypoints_completed` | `2.000` | `2.000` | episode 结束口径，才是判断该 episode 是否完成两个 waypoint 的主指标。 |
| `episode/waypoint_completion_pct` | `100.000%` | `100.000%` | episode 结束口径，后段稳定完成。 |

指标口径解释：

- `episode/*` 指标只在 episode 结束时对结束环境统计，因此适合判断“这一批结束的 episode 是否完成任务”。
- `Tracking/*` 指标是每个训练 step 对所有并行环境取均值，其中很多环境处于新 episode 或刚切换 waypoint 的中间状态，因此不能直接等价为 episode 结束结果。
- 本轮新日志已经解决上一轮“旧 `goal_pos_error` 看起来与 success 冲突”的主要歧义：成功瞬间误差应看 `episode/success_hit_pos_error`，后段约 `0.488 m`。

## 5. Numerical Stability and Control Quality

| 指标 | 初始值 | 最终值 | 后 20 轮均值 | 解释 |
|---|---:|---:|---:|---|
| Value loss | `0.0096` | `0.1628` | `0.1276` | 有波动但未爆炸。 |
| Surrogate loss | `0.0212` | `-0.0168` | `-0.0123` | PPO 更新稳定。 |
| Entropy loss | `-1.524` | `-2.968` | `-2.936` | policy 探索逐渐收窄。 |
| Policy mean std | `0.200` | `0.167` | `0.168` | 动作分布收敛但未塌缩。 |
| FPS | `3957` | `4029` | `4034` | 64 env 训练吞吐稳定。 |
| 纵向滑移绝对均值 | `9.073` | `2.966` | `3.002` | 相比初期显著下降，但仍不能称为低纵滑。 |
| 侧滑角绝对均值 | `0.518 rad` | `0.709 rad` | `0.711 rad` | 后段仍高，不能支撑低侧滑结论。 |
| 车体倾斜角 | `0.143°` | `0.142°` | `0.148°` | 平地姿态稳定。 |
| 轮速参考绝对均值 | `1.840` | `7.516` | 约 `7.7` | policy 倾向使用较高轮速完成任务。 |
| 车轮力矩目标绝对均值 | `4.636` | `2.744` | 约 `2.7` | 后段力矩需求低于初期。 |

控制质量结论：

- 当前策略能稳定完成更严格的 waypoint 成功条件。
- 完成方式仍偏向较高速度和较高侧滑，不应把本轮结果解释为“低滑移协同转向已经学成”。
- 平地车体姿态非常稳定，未看到姿态失稳或球铰越界失败。

## 6. Diagnosis

最大正向信号：

- 在 `0.5 m` 命中半径与 `|phi_2| > |phi_1|` 的更难双 waypoint 分布下，Stage0 仍在约 `294` iterations 内进入连续满成功平台，后 20 轮 episode 级 `waypoints_completed = 2`、`waypoint_completion_pct = 100%`。

主要问题：

- 本轮早停位置没有保存最终 plateau checkpoint，导致训练曲线已经证明策略学成，但当前可用于 replay 的最新 checkpoint 只有 `model_200.pt`，不能代表 iteration `294` 的最终策略。
- 控制质量上，侧滑角后段约 `0.71 rad`，纵向滑移约 `3.0`，仍不足以支撑低滑移或高质量协同转向结论。

下一步优先级：

1. 若要做 deterministic replay / eval，应重新跑到下一个保存点，或把 `save_interval` 改小后复现一轮短训练，确保保存 plateau 策略。
2. 论文或报告中，本轮可作为“严格成功半径下双 waypoint 可学成”的证据，但不能作为“低滑移协同转向”的证据。
3. 如果下一阶段研究目标转向低滑移质量，应先由用户确定滑移评价标准，再调整 reward 或比较实验。
