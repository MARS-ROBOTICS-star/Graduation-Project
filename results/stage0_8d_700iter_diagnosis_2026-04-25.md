# Stage0 8 维动作 700 iteration 训练诊断报告

## 1. 运行识别

- 运行名称：`stage0_8d_baseline_repro_700iter`
- Isaac Lab 日志：`/tmp/isaaclab/logs/isaaclab_2026-04-25_10-29-24.log`
- Hydra 输出目录：`RL_Training/outputs/2026-04-25/10-29-24/`
- 训练 run 目录：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_10-29-24_stage0_8d_baseline_repro_700iter/`
- TensorBoard 导出目录：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_10-29-24_stage0_8d_baseline_repro_700iter/tensorboard_export/`
- 已保存 checkpoint：`model_0.pt`、`model_100.pt`、`model_200.pt`、`model_300.pt`、`model_400.pt`、`model_500.pt`、`model_600.pt`、`model_699.pt`

## 2. 启动与配置

- 设备：`cuda:0`
- 并行环境数：`64`
- 最大训练轮数：`700`
- 每个环境 rollout 步数：`512`
- 总训练步数：`22,937,600`
- actor / critic 观测维度：`54 / 54`
- policy 动作维度：`8`
- 任务口径：平地 Stage0 双 waypoint baseline，每个 episode `2` 个 waypoint，每段 `10 m`，episode 时长 `40 s`。
- 机器人 articulation 解析成功：
  - `17` 个刚体
  - `12` 个关节
  - `6` 个球铰执行器
  - `6` 个车轮执行器
- 终端中出现的主要 simulator warning：
  - CPU performance profile 为 `powersave`
  - PCIe 当前链路宽度为 `8`，最大链路宽度为 `16`
  - Isaac Sim / USD 关闭阶段存在非致命 warning
- allocator 运行时问题修复后，训练启动阶段未再出现异常。

## 3. 核心训练结果

| 指标 | 初始值 | 最终值 | 后 100 轮均值 | 解释 |
|---|---:|---:|---:|---|
| `Train/mean_reward` | `-1.471` | `33.176` | `33.211` | reward 收敛到稳定高平台。 |
| `Train/mean_episode_length` | `253.765` | `594.700` | `596.617` | 成功变快后 episode length 下降，不是生存失败。 |
| `termination_success_rate` | `0.000` | `1.000` | `1.000` | 后段成功终止率完全饱和。 |
| `time_out_rate` | `0.881` | `0.000` | `0.000` | 后段超时失败被消除。 |
| `far_from_target_rate` | `0.000` | `0.000` | `0.000` | 后段没有远离目标失败。 |
| `waypoints_completed` | `0.000` | `2.000` | `2.000` | 后段能完成配置中的两个 waypoint。 |
| `waypoint_completion_pct` | `0.000` | `100.000` | `100.000` | waypoint 层面的完成条件已满足。 |

学习过程中的关键节点：

- 第一次 `success_rate >= 0.9` 出现在 iteration `152`。
- 从 iteration `236` 开始，后续 `success_rate` 一直保持 `1.0`。
- 从 iteration `300` 到 `699`，success 和 waypoint completion 基本保持饱和。

核心结论：

- 从工程复现角度看，这是一轮成功 run：当前 Stage0 8 维动作 baseline 可以端到端跑满，并且 policy 可以稳定满足当前 waypoint 终止条件。
- 但它不能直接证明机器人已经学会了精确终点位姿捕获，也不能证明已经学会低滑移协同转向。

## 4. Reward 与跟踪诊断

| 指标 | 初始值 | 最终值 | 后 100 轮均值 | 解释 |
|---|---:|---:|---:|---|
| `reward_total` | `-0.0063` | `0.0550` | `0.0557` | per-step reward 稳定为正。 |
| `reached_target` reward | `0.0000` | `0.0320` | `0.0328` | 主要终止成功奖励来源。 |
| `progress_to_target` reward | `0.0003` | `0.0242` | `0.0240` | 主要 dense learning signal。 |
| `distance_to_target` reward | `0.0013` | `0.0017` | `0.0017` | 贡献较小。 |
| `angle_diff` reward | `0.0018` | `0.0022` | `0.0023` | 贡献较小。 |
| `slip_penalty` | `-0.0096` | `-0.0050` | `-0.0050` | 后段接近固定，约束作用偏弱。 |
| `turn_speed_penalty` | `-0.00007` | `-0.00016` | `-0.00013` | 量级太小，不主导行为。 |

跟踪指标：

| 指标 | 初始值 | 最终值 | 后 100 轮均值 | 解释 |
|---|---:|---:|---:|---|
| `goal_pos_error` | `9.891 m` | `6.733 m` | `6.770 m` | 即使 success 饱和，目标位置误差仍然很高。 |
| `goal_heading_error_abs` | `0.431 rad` | `0.125 rad` | `0.102 rad` | 航向误差明显改善。 |
| `goal_completion_pct` | `2.158%` | `33.655%` | `33.288%` | 与 waypoint success 不一致，仍偏低。 |

关键解释：

- `goal_success_rate = 1.0`、`waypoints_completed = 2`、`waypoint_completion_pct = 100%` 与 `goal_pos_error ≈ 6.77 m`、`goal_completion_pct ≈ 33%` 同时出现，说明这些指标不是在同一个语义时刻描述同一件事。
- 最可能的解释是日志语义错位：success / waypoint completion 记录的是刚命中 waypoint 的成功条件，而 `goal_pos_error` 与 `goal_completion_pct` 很可能记录的是 waypoint 切换后当前激活目标或重采样目标的状态。
- 在把这轮训练作为论文证据之前，必须区分并单独记录：
  - 命中成功瞬间的距离误差
  - waypoint 切换后的当前激活目标距离误差
  - episode 结束时的最终误差

## 5. 控制质量诊断

| 指标 | 初始值 | 最终值 | 后 100 轮均值 | 解释 |
|---|---:|---:|---:|---|
| 纵向滑移绝对均值 | `9.439` | `3.083` | `3.090` | 前期明显下降，但最终仍不低。 |
| 侧滑角绝对均值 | `0.516 rad` | `0.728 rad` | `0.728 rad` | 不但没有下降，反而升高并稳定在较高水平。 |
| 车体倾斜角 | `0.145 deg` | `0.146 deg` | `0.145 deg` | 平地上车体姿态非常稳定。 |
| 球铰速度绝对均值 | `0.200` | `0.224` | `0.223` | 没有明显球铰速度发散。 |
| 轮速参考绝对均值 | `1.845` | `9.041` | `8.908` | policy 学到了更激进的轮速需求。 |
| 车轮力矩目标绝对均值 | `4.697` | `2.834` | `2.828` | 收敛后力矩需求下降。 |

控制质量结论：

- policy 学会了完成当前 waypoint 任务，但并不是通过降低侧滑完成的。
- 纵向滑移相比初期显著改善，但最终数值仍不足以支撑“低纵滑控制”结论。
- 侧滑是当前控制质量中最明确的问题。

## 6. 数值稳定性与吞吐

| 指标 | 初始值 | 最终值 | 后 100 轮均值 | 解释 |
|---|---:|---:|---:|---|
| Value loss | `0.0101` | `0.0945` | `0.0874` | 有界，没有 loss 爆炸。 |
| Surrogate loss | `0.0229` | `-0.0140` | `-0.0135` | PPO 更新稳定。 |
| Entropy loss | `-1.524` | `-4.179` | `-4.091` | policy 逐渐收敛，探索减弱。 |
| Policy mean std | `0.200` | `0.144` | `0.146` | 动作分布正常收窄。 |
| FPS | `3956` | `4022` | `4010` | 当前 GPU 上 64 env 吞吐稳定。 |

数值稳定性结论：

- TensorBoard 标量没有显示 PPO 数值不稳定。
- 在当前环境和 GPU 条件下，训练吞吐稳定，后续可以继续复现实验。

## 7. 综合诊断

最大正向信号：

- 当前 Stage0 8 维动作 baseline 可以在 GPU 上完整跑满 700 iteration，并且能稳定满足当前双 waypoint 的成功终止条件。

当前主要问题：

- 成功指标已经饱和，但目标误差和滑移质量指标仍然差或存在语义歧义，因此这轮结果还不能支撑“精确到达”或“低滑移协同转向”的论文结论。

下一步优先级：

1. 先增加或核对日志：必须分清成功瞬间命中误差、当前激活目标误差、episode 最终误差。
2. 使用 `model_699.pt` 做 deterministic replay / eval，直观看策略如何完成两个 waypoint。
3. 如果研究目标继续指向低滑移协同转向，应在指标语义清楚之后，再讨论 reward 或评价指标重构。
