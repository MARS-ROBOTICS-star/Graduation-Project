# Stage0 `lambda_lat=4.0` 训练中断诊断

## 1. Run Identification

- 训练 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-27_09-14-07_stage0_lambda4_current_700iter`
- Isaac Lab 日志：
  - `/tmp/isaaclab/logs/isaaclab_2026-04-27_09-14-07.log`
- 原计划：
  - `700` iterations
- 实际完成：
  - TensorBoard 写入到 step `81`
  - 用户要求停止后训练进程已终止
- Checkpoint：
  - 已保存 `model_0.pt`
  - 已保存 `model_25.pt`
  - 已保存 `model_50.pt`
  - 已保存 `model_75.pt`
- TensorBoard 导出：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-27_09-14-07_stage0_lambda4_current_700iter/tensorboard_export/`

## 2. Startup and Configuration

- 设备：
  - `cuda:0`
- 并行环境数：
  - `64`
- PPO：
  - `num_steps_per_env=512`
  - `max_iterations=700`
  - `save_interval=25`
- 动作/观测：
  - policy 动作 `8` 维
  - actor / critic 观测 `54 / 54`
- 本轮训练实际生效低层参数以 run 内 `params/env.yaml` 和 Isaac log 为准：
  - `low_slip_lambda_lateral=4.0`
  - `wheel_torque_tracking_gain=2.0`
  - `wheel_slip_feedback_gain=1.5`
  - `wheel_joint_effort_limit_sim=15.0`
  - `ball_joint_stiffness=1000.0`
  - `ball_joint_damping=10.0`
  - `ball_joint_effort_limit_sim=20.0`
  - `ball_joint_velocity_limit_sim=2.0`
- Isaac log 确认 articulation 初始化正常：
  - `17` bodies
  - `12` joints
  - `ball_joints` actuator 匹配 6 个球铰关节
  - `wheel_joints` actuator 匹配 6 个车轮关节
- 备注：
  - 训练结束后当前工作区检测到 `complete_car_stage0_cfg.py` 有未提交改动，将球铰 drive 从 `1000/10` 改为 `1500/30`。
  - 该改动没有参与本轮 run；本轮实际运行配置仍按 `params/env.yaml` 和 Isaac log 的 `1000/10` 判断。

## 3. Core Training Outcome

本轮不应作为成功训练结果。

- `Train/mean_reward`：
  - first `-0.371`
  - last `0.526`
  - 后 10 轮均值约 `-0.046`
  - 后 25 轮均值约 `-1.192`
- `Train/mean_episode_length`：
  - first `253.8`
  - last `2399`
  - 后 25 轮均值 `2399`
- termination：
  - `time_out_rate` 后 25 轮均值 `1.0`
  - `far_from_target_rate` 后 25 轮均值 `0.0`
  - `success_rate` 终端日志中始终为 `0.0`，因全零未保留为有效 TensorBoard scalar

解释：

- 正向信号：
  - 训练没有启动失败，仿真和 PPO 均正常运行。
  - 策略从早期大量 `far_from_target` 终止转为几乎全部撑满 episode。
  - reward 和 low-slip 指标均有改善。
- 主要问题：
  - 目标完成没有形成有效学习。
  - 最后仍未达到 waypoint 成功。
  - 策略更像是学到“低速、低滑移、前后轮承载、中车弱接触”的行为，而不是学到稳定到达目标。

## 4. Target Completion Diagnosis

关键指标：

| 指标 | first | last | 后 10 轮均值 | 后 25 轮均值 | 解释 |
|---|---:|---:|---:|---:|---|
| active waypoint position error | `8.263 m` | `7.558 m` | `6.781 m` | `6.302 m` | 有改善，但远大于 `0.5 m` 成功半径 |
| active waypoint bearing abs | `0.495 rad` | `0.608 rad` | `0.615 rad` | `0.810 rad` | 后段方向误差未稳定下降 |
| active segment completion | `17.37%` | `24.42%` | `32.19%` | `36.99%` | 后段能推进约三到四成路段 |
| waypoints completed mean | `0.0` | `0.0` | `0.0009` | `0.0173` | waypoint 命中几乎没有形成 |
| episode completion pct | `0.0%` | `0.0%` | `0.046%` | `0.864%` | 完整双 waypoint 任务基本未完成 |

结论：

- `lambda_lat=4.0` 比 `lambda_lat=10.0` 的近停滞失败 run 更能推进，后 25 轮平均 active segment completion 达到约 `37%`。
- 但它仍没有学会命中 waypoint。
- 后段误差仍在米级，不能支持“平地双 waypoint baseline 成功”结论。

## 5. Motion Quality Diagnosis

### 5.1 Slip and Low-Slip Metrics

| 指标 | first | last | 后 10 轮均值 | 后 25 轮均值 | 目标口径 |
|---|---:|---:|---:|---:|---|
| longitudinal slip abs | `2.435` | `1.309` | `1.442` | `1.586` | `< 1.0` |
| slip angle abs | `0.733 rad` | `0.411 rad` | `0.453 rad` | `0.503 rad` | `< 0.35 rad` |
| low-slip combined pass | `1.81%` | `20.23%` | `13.13%` | `8.59%` | 越高越好 |
| longitudinal pass | `14.13%` | `34.05%` | `26.75%` | `21.15%` | 越高越好 |
| slip-angle pass | `7.92%` | `40.58%` | `30.55%` | `21.90%` | 越高越好 |
| progress gate multiplier | `0.156` | `0.427` | `0.353` | `0.292` | 低滑移越好越高 |

结论：

- 滑移质量确实比训练初期改善。
- 最后一轮侧滑角已经接近用户提出的约 `0.5 rad / 30°` 观察上限，但后 25 轮均值仍约 `0.503 rad`，并且评价阈值 `0.35 rad` 尚未达到。
- 纵滑后 25 轮约 `1.586`，仍明显高于 `< 1.0` 的评价阈值。
- low-slip combined pass 后 25 轮只有约 `8.6%`，不能认为已形成低滑移完成方式。

### 5.2 Speed and Command Shaping

| 指标 | first | last | 后 10 轮均值 | 后 25 轮均值 |
|---|---:|---:|---:|---:|
| desired planar command abs | `0.687` | `0.490` | `0.514` | `0.527` |
| shaped planar command abs | `0.667` | `0.349` | `0.374` | `0.404` |
| shaped vx | `0.999 m/s` | `0.330 m/s` | `0.374 m/s` | `0.448 m/s` |
| shaping delta abs | `0.046` | `0.172` | `0.172` | `0.154` |
| wheel speed reference abs | `5.233` | `1.814` | `2.044` | `2.407` |
| low-level `v_parallel_abs` | `0.338 m/s` | `0.091 m/s` | `0.107 m/s` | `0.133 m/s` |
| low-level `v_perp_abs` | `0.391 m/s` | `0.095 m/s` | `0.112 m/s` | `0.140 m/s` |

结论：

- 本轮改善滑移的主要方式之一是降低速度和轮速参考。
- 后段 `v_parallel_abs` 已降到约 `0.1 m/s` 量级。
- `v_perp_abs` 与 `v_parallel_abs` 同量级，说明侧向运动仍未被有效压到低于纵向推进。
- 当前不属于完全近停滞，但已经向“慢速低滑移局部解”靠近。

### 5.3 Wheel-Ground Contact and Middle Body State

后 10 轮 per-wheel 均值：

| 车轮 | 法向力 | contact weight | torque target | longitudinal slip | wheel joint vel |
|---|---:|---:|---:|---:|---:|
| head left | `101.7 N` | `0.960` | `-0.145 Nm` | `1.120` | `0.824` |
| head right | `74.3 N` | `0.881` | `0.481 Nm` | `1.307` | `0.934` |
| body left | `4.06 N` | `0.082` | `0.009 Nm` | `0.111` | `0.101` |
| body right | `1.47 N` | `0.023` | `0.003 Nm` | `0.637` | `0.495` |
| tail left | `83.7 N` | `0.958` | `0.055 Nm` | `1.153` | `0.818` |
| tail right | `100.4 N` | `0.962` | `0.911 Nm` | `1.245` | `0.897` |

中车姿态：

- `pitch_deg`
  - first `0.074°`
  - last `3.614°`
  - 后 10 轮均值 `3.218°`
  - 后 25 轮均值 `2.799°`
- `roll_deg`
  - last `-0.668°`
  - 后 10 轮均值 `-0.914°`

结论：

- 中车轮组再次出现明显低载荷：
  - body left 后 10 轮仅约 `4.06 N`
  - body right 后 10 轮仅约 `1.47 N`
- 中车轮 torque target 几乎为零：
  - body left 后 10 轮约 `0.009 Nm`
  - body right 后 10 轮约 `0.003 Nm`
- 前后轮承担主要支撑和推进。
- 这与中车 pitch 上升趋势一致，说明当前局部策略仍在把中段轮组推向弱接触状态。
- 这不是车轮力矩限幅导致：
  - 全局 wheel torque abs 后 25 轮约 `1.554 Nm`
  - 距离 `15 Nm` 上限很远。

## 6. Numerical Stability

| 指标 | first | last | 后 10 轮均值 | 结论 |
|---|---:|---:|---:|---|
| value loss | `0.0047` | `0.00030` | `0.00032` | 未爆炸 |
| surrogate loss | `0.0357` | `-0.0117` | `-0.0156` | 正常范围 |
| entropy loss | `-1.525` | `-2.191` | `-2.153` | 探索分布逐渐变化 |
| policy mean std | `0.200` | `0.184` | `0.185` | 没有塌缩到零 |
| total fps | `3277` | `3311` | `3406` | 训练吞吐正常 |

结论：

- 本轮不是数值不稳定或训练崩溃。
- 主要问题是任务目标与运动质量之间形成了不理想的行为折中。

## 7. Overall Diagnosis

最大正向信号：

- `lambda_lat=4.0` 相比 `lambda_lat=10.0` 没有把训练一开始就压成完全近停滞，能在后段推进到约 `37%` 路段，并显著降低纵滑和侧滑角。

主要问题：

- 策略仍未学会命中 waypoint；后段主要表现为慢速推进、前后轮承载、中车轮弱接触、滑移下降但任务完成失败。

当前判断：

- `lambda_lat=4.0` 是介于 `10.0` 和 `2.0` 之间的中间配置，但它仍没有解决“低滑移与目标完成同时成立”的核心矛盾。
- 本轮结果比 `lambda_lat=10.0` 的近停滞局部解更有推进能力，但仍没有达到 Stage0 可用 baseline。
- 继续长训可能会让低滑移指标继续改善，但从前 81 轮看，改善路径伴随速度下降和中轮卸载；如果目标是可解释的稳定完成，不能只看 low-slip pass rate 上升。

## 8. Next Step Options

这些是需要用户做研究判断的方向，不应由工程实现直接替代：

1. 若坚持当前双 waypoint 任务定义，应优先处理“目标完成驱动不足”：
   - 检查 `reached_target`、`progress_to_target`、`distance_to_target` 的相对权重是否仍能在 low-slip gate 下推动到达。
   - 明确 success 是否必须绑定完整双 waypoint，而不只看单步 hit 或局部指标。
2. 若优先保证运动行为质量，应把“中车轮有效接地/载荷分配”纳入评价或约束：
   - 当前中车两轮后 10 轮法向力只有约 `4.06 N / 1.47 N`。
   - 如果中轮长期弱接触，所谓低滑移可能只是少数负载轮慢速拖动。
3. 若继续参数扫描，`lambda_lat=4.0` 不应直接当作成功点：
   - 它比 `10.0` 不那么停滞，比 `2.0` 更能降低滑移。
   - 但后段 `success_rate=0`、后 25 轮 `episode_completion_pct≈0.86%`，说明当前参数还不能支撑目标完成结论。
