# 当前状态

## 当前 Stage1 地形训练状态

- 当前 Stage1 已进入 `best_baseline_2` warm-start 训练阶段。
- warm-start 来源：
  - Stage0 run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-28_15-28-38_best_baseline_2`
  - Stage0 checkpoint：`model_699.pt`
  - Stage1 warm-start checkpoint：`RL_Training/logs/rsl_rl/complete_car_stage1/warmstart_best_baseline_2/model_0.pt`
- warm-start 方式：
  - 不能直接 resume Stage0 checkpoint，因为 Stage0 actor/critic 观测维度为 `54`，Stage1 为 `972`。
  - 已将 actor/critic 第一层和 obs normalizer 扩展到 `972` 维，前 `54` 维继承 Stage0，新增高度图维度初始化为零权重。
  - 训练使用 `--warmstart` 只加载 actor/critic，不加载 optimizer 和 iteration。
- 当前 Stage1 观测策略：
  - actor / critic 均为 `54 + 34 * 27 = 972` 维。
  - 高度图保持原始 patch 尺寸和米制高度值，不 clip 到 `[-1, 1]`，不额外乘 scale，交由 PPO normalizer 归一化。
- 当前 Stage1 目标点逻辑：
  - 使用 terrain column / terrain type 生成目标点。
  - 目标方向沿地形列纵向 `+x`。
  - 目标列保持同列，目标行偏移 `1-2` 行，目标点 `y` 方向允许左右随机偏移 `3 m`。
  - reset 朝向固定为 `+x`。
- 当前可视化训练：
  - 默认并行环境数已改为 `32`，不影响 Stage0。
  - 当前 GUI run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-04-28_18-17-55_stage1_warmstart_best_baseline_2_32env_view_700iter`
  - 已按用户要求停止，终端最后完整输出到 PPO iteration `18/700`。
  - 该 run 当前只看到 `model_0.pt`，没有跑到默认保存间隔产生后续 checkpoint。
  - 目标点红色 marker 开启；`env_0` top/chase follow view 开启。
  - 目标方向箭头暂不画，因为 Stage1 目标方向固定为 `+x`，且此前 GUI 下该箭头曾触发 Fabric point-instancer warning。
- 当前 Git 上传规则：
  - Stage1 当前模型、checkpoint、TensorBoard event、run diff、输出目录默认不上传 GitHub。
  - `.gitignore` 已显式忽略 `RL_Training/logs/rsl_rl/complete_car_stage1/`。
  - 只有当用户明确要求上传某一次 Stage1 训练结果时，才使用 `git add -f` 纳入对应 run。

## 当前 active Stage0 基准

- 当前 Stage0 主线已按用户要求恢复为 `best_baseline`。
- `best_baseline` 对应历史版本：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_18-26-58_stage0_lowslip_gate_v1_700iter`
  - checkpoint：`model_699.pt`
  - 详细报告：`results/stage0_lowslip_gate_v1_model699_detailed_result_config_motion_model_2026-04-28.md`
- 恢复范围：
  - Stage0 reward 恢复为 lowslip gate v1 的 7 项结构。
  - PPO timeout 语义恢复为 `is_finite_horizon = False`，即 timeout 作为 time-limit，允许 PPO bootstrap。
  - 底层控制恢复为 low-slip allocator + 车轮 torque target，不再使用直接 wheel velocity target。
  - 纵滑率方向恢复为历史口径：`kappa = (v_parallel - r * omega) / max(abs(v_parallel), epsilon)`。
- 唯一保留的当前口径：
  - 侧滑角不恢复 2026-04-25 的 wheel local `Y` 旧轴向。
  - 当前继续使用 wheel local `Z` 作为水平侧向轴，并使用 `atan2(v_perp, max(abs(v_parallel), epsilon))`。

## 当前 Stage0 配置摘要

- 任务：平地双 waypoint。
- 并行环境：`64`。
- episode 时长：`40 s`。
- 控制频率：`60 Hz`。
- 每段 waypoint 距离：`10 m`。
- 命中半径：`0.5 m`。
- 动作维度：`8`，即 `[vx_cmd, yaw_rate_cmd, 6 个球铰姿态目标]`。
- 观测维度：actor / critic 均为 `54`。
- PPO 默认：
  - `experiment_name = complete_car_stage0`
  - `run_name = best_baseline`
  - `num_steps_per_env = 512`
  - `max_iterations = 700`
  - `seed = 1`
- 当前 Stage0 baseline 参数详情表：`docs/stage0_baseline参数详情表.md`。

## 当前 Stage0 回放视频

- 已按用户要求回放 `best_baseline_2/model_699.pt` 并录制 2 分钟 chase 跟踪视角视频。
- 视频文件：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-28_15-28-38_best_baseline_2/videos/play/best_baseline_2_chase_120s.mp4`。
- 视频规格：`1280x720`、`60 fps`、`120 s`、`7200` 帧。
- 回放设置：
  - 使用 `env_0` chase follow view：`/view/env_0/chase_camera`。
  - 开启目标点红色 marker。
  - 目标方向箭头关闭，避免此前 Fabric point-instancer warning。
- 抽帧检查：`results/best_baseline_2_chase_120s_frame10.jpg`，确认 chase 视角和目标点 marker 可见。

## 当前 reward 结构

active reward 项：

1. `distance_to_target`
2. `progress_to_target`
3. `reached_target`
4. `far_from_target`
5. `angle_diff`
6. `turn_speed_penalty`
7. `slip_penalty`

当前不再 active 的中间实验项：

- `timeout_penalty`
- `no_progress_penalty`
- `action_rate_penalty`
- `load_equalization`

说明：

- 上述中间实验项已从 active reward 代码和配置字段中删除，不再作为“保留但不生效”的配置存在。
- `progress_gate` 使用平均 gate：`0.5 * (G_kappa + G_alpha)`，不是 `min` gate。
- 正向 progress 受 gate 调制，负 progress 不被 gate 削弱。

## 当前底层运动模型

active 控制链：

1. policy 输出 action。
2. action 前两维映射为 `vx_cmd` 和 `yaw_rate_cmd`。
3. action 后六维映射为两组等效球铰目标姿态。
4. allocator 内部一阶球铰规划器生成 `q_cmd` 和 `qdot_cmd`。
5. low-slip 平面命令整形器生成 `shaped_planar_command`。
6. 轮速分配器生成 `wheel_speed_reference`。
7. 轮级 traction allocator 根据纵滑反馈和接触权重生成 `wheel_torque_targets`。
8. 环境对球铰下发 position target，对车轮下发 effort target。

当前不 active：

- 车轮 direct velocity target。
- env 层 qddot 轨迹器传入 allocator 的中间版本。
- 去掉低滑移整形后的直接轮速参考链路。
- `g_kappa/g_alpha` 纵滑/侧滑衰减诊断字段；当前轮级力矩公式不使用这两个衰减因子。

## 当前结论边界

- `best_baseline` 可作为 Stage0 平地双 waypoint 可学习、工程链路可闭环的基准版本。
- 不能把该 baseline 直接解释为低滑移协同控制已经成功。
- 原始历史 TensorBoard 的侧滑角来自旧 local `Y` 口径，不能作为真实水平侧滑证据。
- 当前代码已修正侧滑角口径，因此后续新训练的侧滑角曲线不能与历史旧侧滑角曲线直接数值比较。

## 最新训练监控结果

- 已完成新训练 run：`2026-04-28_15-28-38_best_baseline_2`。
- 训练跑满 `700` iterations，终端输出到 `699/700`，进程正常退出，最终 checkpoint 为 `model_699.pt`。
- 末段任务完成质量较好：最后可见阶段基本保持 `success_rate=1.0`、`time_out_rate=0.0`，无远离目标或球铰限位终止。
- 末段运动行为不是近停滞：`v_parallel_abs` 约 `1.18-1.19 m/s`，`v_perp_abs` 约 `0.036-0.040 m/s`，当前口径侧滑角约 `0.054-0.061 rad`，pitch 约 `-0.5 deg` 到 `-0.7 deg`。
- 主要问题仍是纵滑：纵滑率约 `3.06-3.13`，`LowSlip/combined_pass_rate` 约 `0.087-0.092`，车轮参考角速度约 `8.7-8.8 rad/s`。
- 因此该训练可说明当前 `best_baseline` 配置能学出有效前向运动和高任务完成率，但不能解释为低纵滑控制成功。

## 下一步优先事项

1. 如需训练新基准，直接使用默认 `run_name=best_baseline` 或显式指定新 run 名。
2. 若继续研究低滑移控制，不应只看 `success_rate`，需要同步观察纵滑率、当前口径侧滑角、有效推进速度、中车载荷和 waypoint 完成质量。
3. 若要声称低滑移/协同控制贡献，需要设计新的成功条件、对比实验或 ablation，而不是仅依赖该 baseline。
