# Stage1 评价指标

本文档整理当前 `CompleteCar-Stage1` 训练中 TensorBoard 与终端日志会输出的内容、来源、含义和使用方式。

当前文档只解释“会记录什么、怎么看、用于判断什么”，不把这些指标直接解释为论文结论。是否能支撑“地形适应”“低滑移”“协同控制”等研究判断，仍需要结合具体训练曲线、视频、对比实验和人工复核。

## 1. 当前依据与边界

### 1.1 对应 Stage1 主线

当前 Stage1 主线是 `best_baseline_2` warm-start 地形训练阶段：

- task：`CompleteCar-Stage1`
- 训练工程：`RL_Training/`
- Stage1 配置：`complete_car_stage1_cfg.py`
- 环境主类：`env.py`
- 终端与 TensorBoard 写入逻辑：`rsl_rl/utils/logger.py`
- 训练入口：`scripts/train.py`

当前 Stage1 的关键配置背景：

- 并行环境数：`32`
- 控制频率：`60 Hz`
- episode 时长：`40 s`
- actor / critic 观测维度：`632`
- 动作维度：`8`
- 前两维动作映射为底盘平面命令：
  - `a0 -> vx_cmd`：`[-2.0, 2.0] m/s`
  - `a1 -> yaw_rate_cmd`：`[-2.0, 2.0] rad/s`
- 后六维动作映射为两组等效球铰目标姿态。
- Stage1 使用 terrain-column 目标点；目标点用于前进方向引导，目标命中本身不作为 Stage1 success termination。

### 1.2 当前本地日志可用性

项目记忆中记录的当前 Stage1 run 为：

- `RL_Training/logs/rsl_rl/complete_car_stage1/2026-04-29_07-37-58_stage1_warmstart_best_baseline_2_32env_best_per_terrain_chase_700iter`

项目记忆中记录的 runtime log 为：

- `RL_Training/logs/runtime/stage1_32env_best_per_terrain_chase_setsid.log`
- `RL_Training/logs/runtime/stage1_32env_best_per_terrain_chase_resume_record_only.log`

但当前本地工作区中，Stage1 run 目录只保留了已上传的 `slope_down_env02_chase_120s.mp4`，没有可读取的 `events.out.tfevents*`、`params/env.yaml`、`params/agent.yaml` 或 runtime `.log` 文件。因此本文档不填写某次 Stage1 训练的实际数值曲线，只整理当前源码会写入 TensorBoard 和终端的指标内容。

如果后续需要“某次训练的数值报告”，必须先恢复对应 run 的 TensorBoard event 文件和 runtime log，然后再导出曲线统计。

## 2. 输出通道

### 2.1 TensorBoard 输出

TensorBoard 输出由 `Logger.log()` 写入。每个 PPO iteration 结束后，logger 会写入：

- PPO 训练损失：`Loss/*`
- 学习率：`Loss/learning_rate`
- policy 分布标准差：`Policy/mean_std`
- 性能：`Perf/*`
- 已完成 episode 的滑动统计：`Train/*`
- 环境 step extra：reward、action、observation、low-slip、tracking、terrain、command、per-wheel 等
- episode extra：episode 累计 reward、每步 reward、终点误差、waypoint 完成等

当前 logger 只把 curated extra scalar 写入 TensorBoard；不在白名单中的环境 extra 不会进入 TensorBoard。`PerWheel/*` 是例外，只要 tag 以 `PerWheel/` 开头就会写入。

TensorBoard 中部分重要 tag 会被重命名到带序号的前缀分组，例如：

- `Termination/success_rate` 会显示为 `00_Behavior/00_termination_success_rate`
- `Reward/total` 会显示为 `00_Behavior/08_reward_total`
- `Terrain/current_level_mean` 会显示为 `Terrain/00_current_level_mean`
- `Train/mean_reward` 会显示为 `Train/01_mean_reward`

这样做的目的只是让关键曲线排在 TensorBoard 前面，不改变指标含义。

另一个细节是：logger 会延迟写入长期为零的 sparse scalar。某个 tag 在激活前如果数值绝对值小于等于 `1e-12`，会先暂存；等该 tag 第一次出现非零值后，再把之前暂存的零值补写进去。这会避免 TensorBoard 里出现大量没有信息量的空曲线。

### 2.2 终端日志输出

终端日志也是每个 PPO iteration 打印一次。一个训练 iteration 的终端块主要包含：

- `Learning iteration it/total_it`
- `Run name`
- `Total steps`
- `Steps per second`
- `Collection time`
- `Learning time`
- `Mean value loss`
- `Mean surrogate loss`
- `Mean entropy loss`
- `Mean reward`
- `Mean episode length`
- `Mean action std`
- curated 环境指标
- `Iteration time`
- `Time progress`
- `Time elapsed`
- `ETA`
- `Est. total time`

终端不会打印全部 TensorBoard extra，只打印 `CONSOLE_PRIORITY_TAGS` 中的高信号子集。终端打印的是便于训练时快速盯盘的指标；完整细分指标应看 TensorBoard。

### 2.3 Stage1 地形 chase 录制输出

当训练命令启用 `--record_terrain_chase_videos` 时，`scripts/train.py` 还会在终端打印 terrain chase recorder 的状态：

- 选择阶段开始：
  - `Terrain chase selection started`
  - 包含 `mode`、地形分组数、`selection_steps`
- 选择阶段进度：
  - 每 `120` 个 step 打印一次 `Terrain chase env scoring`
- 每组最优 env 选择结果：
  - `Terrain chase selected best env`
  - 包含 env id、terrain column、terrain name、正向 `+x` 累计分数
- 每个 chase 视频开始：
  - `Terrain chase recording started`
  - 包含第几个视频、env id、column、terrain、输出文件路径
- 每个视频录制进度：
  - 每 `600` 帧或最后一帧打印一次 streamed frames
- 全部视频录制完成：
  - `Terrain chase video recording finished`

当启用 `--record_only` 并传入 `--terrain_chase_selection_file` 时，终端还会打印：

- `Reusing existing terrain chase run directory`
- `Terrain chase resume loaded`
- `Loading checkpoint from`
- `Record-only runtime`

record-only 模式只做策略推理和视频补录，不执行 PPO rollout/update，因此不会打印 PPO 训练 iteration 指标，也不会写新的 TensorBoard 训练曲线。

### 2.4 异常与警告输出

当前源码中 `SquashedGaussianDistribution` 对非有限 action distribution 参数增加了保护。如果 policy 输出的 mean 或 log_std 出现 NaN/Inf，终端可能出现：

- `SquashedGaussianDistribution received non-finite action mean; sanitizing values.`
- `SquashedGaussianDistribution received non-finite log_std parameters; clamping values.`

项目记忆还记录过当前 Stage1 chase 训练在 PPO update 期间崩溃：

- `RuntimeError: normal expects all elements of std >= 0.0`

这类信息属于稳定性/数值健康诊断，不属于常规评价指标，但在分析训练失败时必须记录。

## 3. TensorBoard 指标分组

### 3.1 `Train/*`

| TensorBoard tag | 含义 | 主要用途 |
|---|---|---|
| `Train/mean_reward` | 最近完成 episode 的平均 return，来自 logger 的 `rewbuffer` | 判断整体训练回报是否提高 |
| `Train/mean_episode_length` | 最近完成 episode 的平均长度，单位为控制步 | 判断 episode 是经常提前终止还是接近 timeout |
| `Train/mean_reward/time` | 以累计训练时间为横轴的平均 return | 按真实训练耗时看学习速度 |
| `Train/mean_episode_length/time` | 以累计训练时间为横轴的平均 episode 长度 | 按真实训练耗时看终止趋势 |

Stage1 中如果 `mean_episode_length` 接近 `40 s * 60 Hz = 2400` 步，通常说明 episode 多数跑到 time limit；如果明显变短，需要结合 `Termination/*` 判断是失稳、远离目标还是球铰越界。

### 3.2 `Loss/*`

| TensorBoard tag | 终端字段 | 含义 | 主要用途 |
|---|---|---|---|
| `Loss/value` | `Mean value loss` | critic value function 的回归损失 | 判断 critic 是否能拟合 return |
| `Loss/surrogate` | `Mean surrogate loss` | PPO actor surrogate loss | 判断 policy update 的优化量 |
| `Loss/entropy` | `Mean entropy loss` | policy action distribution entropy | 判断探索程度 |
| `Loss/learning_rate` | 不单独打印 | 当前 PPO 学习率 | 检查 adaptive schedule 是否调整学习率 |

这些是优化过程指标，不直接说明机器人运动质量。它们主要用于判断 PPO 是否数值稳定、是否仍有探索、是否可能出现训练崩溃。

### 3.3 `Policy/*`

| TensorBoard tag | 终端字段 | 含义 | 主要用途 |
|---|---|---|---|
| `Policy/mean_std` | `Mean action std` | actor 输出分布的平均标准差 | 判断 policy 探索噪声是否过大或过早塌缩 |

如果 `mean_std` 快速贴近下限，policy 可能过早确定化；如果长期过高，则动作抖动和轮地冲击可能较大。

### 3.4 `Perf/*`

| TensorBoard tag | 终端字段 | 含义 | 主要用途 |
|---|---|---|---|
| `Perf/total_fps` | `Steps per second` | 并行环境总采样吞吐 | 评估训练效率 |
| `Perf/collection_time` | `Collection time` | rollout 采集耗时 | 判断仿真侧瓶颈 |
| `Perf/learning_time` | `Learning time` | PPO update 耗时 | 判断优化侧瓶颈 |

Stage1 开启地形、传感器或视频录制后，`collection_time` 可能显著增加。录制 chase 视频时，性能指标不能和纯 headless 训练直接横向比较。

## 4. 任务完成与终止指标

### 4.1 `Termination/*`

| tag | 终端是否打印 | 含义 | Stage1 解读 |
|---|---:|---|---|
| `Termination/success_rate` | 是 | reset 环境中 `is_success` 的比例 | Stage1 terrain-column 目标下被强制为 `0`，不能用它判断成功 |
| `Termination/time_out_rate` | 是 | 因 episode 到达最大长度而 reset 的比例 | Stage1 中高 timeout 不一定是坏事，要结合前进距离和地形等级 |
| `Termination/far_from_target_rate` | 是 | 相对目标距离超过阈值导致终止的比例 | 过高说明目标引导或运动稳定性失败 |
| `Termination/ball_joint_limit_rate` | 是 | 球铰角度越过限制导致终止的比例 | 过高说明姿态动作或球铰约束不稳定 |
| `Termination/terminated_rate` | 是 | success、far、ball limit 三类非 timeout 终止的合计比例 | 只进终端，不进入当前 TensorBoard extra 白名单 |

Stage1 里最容易误读的是 `success_rate`。因为 `use_terrain_column_targets=True` 时，`is_success` 被置零，目标点只用于引导前进，不作为 episode 成功条件。因此 Stage1 的主要完成指标应看 `Terrain/*`、`Tracking/terrain_target_advances_mean`、`Tracking/active_segment_completion_pct` 和视频行为，而不是只看 `success_rate`。

### 4.2 `Tracking/*`

| tag | 终端是否打印 | 含义 | 主要用途 |
|---|---:|---|---|
| `Tracking/active_waypoint_pos_error` | 是 | 当前目标点在水平面上的平均距离误差，单位 m | 看车辆是否接近当前引导点 |
| `Tracking/active_waypoint_bearing_abs` | 是 | 当前目标方向相对车体 heading 的绝对角误差，单位 rad | 看车辆是否朝向目标方向 |
| `Tracking/active_segment_completion_pct` | 是 | 当前目标段完成百分比 | 看当前段推进程度 |
| `Tracking/active_waypoint_index_mean` | 否 | 当前 active waypoint index 均值 | Stage1 单 waypoint 下通常信息量较低 |
| `Tracking/waypoints_completed_mean` | 是 | 每个 episode 已命中 waypoint 的均值 | Stage1 目标命中不等于 success，但可作为局部命中记录 |
| `Tracking/terrain_target_advances_mean` | 是 | episode 内 terrain-column 目标推进次数均值 | Stage1 更重要，用于看是否持续向前换目标 |
| `Tracking/episode_completion_pct` | 是 | waypoint 完成百分比 | Stage1 中只能作为辅助，不是最终成功率 |

Stage1 的目标点逻辑是沿同一 terrain column 的 `+x` 方向推进。若 `active_segment_completion_pct` 增长但 `terrain_target_advances_mean` 长期低，说明车辆可能接近目标但没有稳定完成推进逻辑；若两者都低，则策略可能没有形成有效前进。

### 4.3 `Terrain/*`

| tag | 终端是否打印 | 含义 | 主要用途 |
|---|---:|---|---|
| `Terrain/current_level_mean` | TensorBoard debug | 当前 env 所处 terrain row / difficulty level 均值 | Stage1 主指标之一，越高说明能进入更难地形 row |
| `Terrain/tile_start_x_mean` | TensorBoard debug | 当前 tile 起点 x 坐标均值 | 检查 tile 几何定义 |
| `Terrain/tile_origin_x_mean` | TensorBoard debug | 当前 tile origin x 坐标均值 | 对照旧的 origin-based 口径 |
| `Terrain/tile_end_x_mean` | TensorBoard debug | 当前 tile 终点 x 坐标均值 | 检查 tile 范围 |
| `Terrain/root_x_mean` | TensorBoard debug | 车体 root x 坐标均值 | 与 tile start / origin / end 对照 |
| `Terrain/target_x_mean` | TensorBoard debug | 当前目标点 x 坐标均值 | 检查目标是否被错误夹紧 |
| `Terrain/forward_x_from_current_tile_start_mean` | TensorBoard debug | 相对当前 tile start 的世界系 `+x` 前进量均值，单位 m | tile 几何调试量，不再作为 row advance 判断口径 |
| `Terrain/forward_x_from_current_tile_origin_mean` | TensorBoard debug | 相对当前 tile origin 的世界系 `+x` 前进量均值，单位 m | tile 几何调试量，不再作为 row advance 判断口径 |
| `Terrain/active_goal_start_distance_mean` | TensorBoard debug | 当前目标段刚采样时车辆到目标点的水平距离均值 | 检查 row progress 的归一化分母 |
| `Terrain/active_goal_progress_mean` | TensorBoard debug | 当前目标段进度均值，范围约 `0-1` | reset 时 row 退级逻辑的核心参考量 |

当前 Stage1 的 terrain-column 课程逻辑不再使用 `root_x - tile_start_x > 5.6 m` 触发 row 推进。row 升级只由目标点命中触发；row 退级在 reset 时按当前目标段进度判断，失败/超时且 `active_goal_progress < 0.30` 时当前 row 退一级。

reset 日志会额外输出小写 `terrain/*` 指标：

- `terrain/row_progress_at_reset`：episode 结束时的当前目标段进度。
- `terrain/move_down_ratio`：本次 reset 中触发 row 退级的比例。
- `terrain/reset_to_low_ratio`：到达最高有效 row 或完成地形列后重新采样低 row 的比例。
- `terrain/level_after_reset`：reset curriculum 更新后的 terrain level 均值。

Stage1Eval 额外提供：

- `Stage1Eval/global/max_row_reached_rate`
- `Stage1Eval/global/valid_target_masked`
- `Stage1Eval/colXX/max_row_reached_rate`
- `Stage1Eval/colXX/valid_target_masked`

这些指标用于区分“真实不能前进”和“已经到达最高 row 语义边界，目标不应继续夹紧”的情况。

## 5. Reward 与 progress gate 指标

### 5.1 `Reward/*`

| tag | 终端是否打印 | 含义 | 期望方向 |
|---|---:|---|---|
| `Reward/total` | 是 | 当前 step reward 总和的 env 均值 | 趋势上升，但不能单独判断运动质量 |
| `Reward/distance_to_target` | 是 | 距离目标越近越高的 dense reward | 越高越好 |
| `Reward/progress_to_target` | 是 | 当前步相对上一帧向目标接近的 progress reward | 越高越好 |
| `Reward/reached_target` | 是 | 命中目标点时的奖励项 | Stage1 当前权重为 `6.0`，目标命中会直接贡献稀疏奖励 |
| `Reward/far_from_target` | 是 | 远离目标阈值后的惩罚项 | 越接近 `0` 越好 |
| `Reward/angle_diff` | 是 | heading error 越小越高的奖励项 | 越高越好 |
| `Reward/turn_speed_penalty` | 是 | 大角度误差下高速运动惩罚 | 越接近 `0` 越好 |
| `Reward/slip_penalty` | 是 | 接触权重 mask 后的纵滑和侧滑角惩罚 | 越接近 `0` 越好 |
| `Reward/action_rate_penalty` | 否 | 动作变化惩罚；Stage1 当前按 `N=2400` 归一化，并通过 `Debug/Stage1/Reward/action_rate_penalty` 写入 TensorBoard | 越接近 `0` 越好 |
| `Reward/contact_support_penalty` | 否 | 前、中、后三段模块支撑丢失惩罚，并通过 `Debug/Stage1/Reward/contact_support_penalty` 写入 TensorBoard | 越接近 `0` 越好 |
| `Reward/edge_speed_penalty` | 否 | 地形突变前正向超速惩罚，并通过 `Debug/Stage1/Reward/edge_speed_penalty` 写入 TensorBoard | 越接近 `0` 越好 |

注意：当前 Stage1 终端主输出已切换为 `Stage1Eval/*`，`Reward/*` 诊断在 Stage1 TensorBoard 中会以 `Debug/Stage1/Reward/*` 写入；终端盯盘仍以第 10 节的 Stage1Eval 建议为准。

Stage1 的 `reached_target_weight=6.0`，参数与 Stage0 相同；目标点命中既用于推进下一个 terrain-column 目标，也会通过 `Reward/reached_target` 提供稀疏奖励。
Stage1 的 `action_rate_penalty_weight=-10.0`，动作权重为 `[0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]`，前两个底盘动作变化惩罚较轻，后六个球铰姿态动作变化惩罚较重。
Stage1 的 `contact_support_penalty_weight=-4.0`，最低模块支撑要求为 `0.3`；中车、前车、后车各自只取左右轮中较大的接触权重，不强制六轮同时接地。
Stage1 的 slip reward 现在使用接触权重 masked mean；TensorBoard 额外记录 `Debug/Stage1/Slip/masked_longitudinal_abs_mean_raw`、`Debug/Stage1/Slip/masked_angle_abs_mean_raw` 和 `Debug/Stage1/Slip/contact_weight_sum_raw`，用于确认实际参与 slip 评价的有效接触规模。
Stage1 的 `edge_speed_penalty_weight=-6.0`，edge strength 使用前方 `1.0 m`、侧向额外 `0.5 m` 的 height patch 预览区域；高度跳变阈值为 `0.04-0.10 m`，强突变安全速度为 `0.5 m/s`，平地不额外限速。

### 5.2 `ProgressGate/*`

| tag | 终端是否打印 | 含义 | 主要用途 |
|---|---:|---|---|
| `ProgressGate/ungated_progress_raw` | 否 | 未经过 low-slip gate 调制的原始 progress | 观察任务推进本身 |
| `ProgressGate/positive_progress_raw` | 否 | 正向接近目标的原始 progress | 判断是否有有效前进 |
| `ProgressGate/negative_progress_raw` | 否 | 远离目标的负 progress | 判断是否倒退或偏离 |
| `ProgressGate/longitudinal_gate` | 是 | 纵滑率 gate | 越高说明纵滑越低 |
| `ProgressGate/slip_angle_gate` | 是 | 侧滑角 gate | 越高说明侧向滑移越低 |
| `ProgressGate/combined_gate` | 是 | 当前使用平均 gate：`0.5 * (G_kappa + G_alpha)` | 观察 progress reward 是否被滑移压低 |
| `ProgressGate/multiplier` | 是 | progress reward multiplier | 当前范围由 `0.25` 到 `1.5` |

`ProgressGate/combined_gate` 不是成功率。它只说明正向 progress 在 reward 中被放大或削弱的程度。若 `positive_progress_raw` 有明显正值，但 `combined_gate` 很低，说明车辆在“能动”的同时伴随明显滑移，reward 对这种 progress 会打折。

### 5.3 `EdgeSpeed/*`

| tag | 终端是否打印 | 含义 | 主要用途 |
|---|---:|---|---|
| `EdgeSpeed/strength_raw` | 否 | 前方预览区域高度突变强度，范围约为 `0-1` | 判断 height patch 是否识别到台阶/障碍边缘 |
| `EdgeSpeed/height_jump_m_raw` | 否 | 前方预览区域相邻采样点最大高度跳变，单位 m | 对照地形生成高度，检查阈值是否合适 |
| `EdgeSpeed/safe_speed_mps_raw` | 否 | 当前 edge strength 对应的安全前进速度，单位 m/s | 看突变前是否把安全速度压到 `0.5 m/s` 附近 |
| `EdgeSpeed/forward_speed_mps_raw` | 否 | 车体系正向速度，倒车时记为 `0` | 看车辆实际是否仍在向前冲 |
| `EdgeSpeed/excess_speed_mps_raw` | 否 | 超过安全速度的正向速度部分，单位 m/s | 越接近 `0` 越好 |

这些指标在 Stage1 TensorBoard 中会以 `Debug/Stage1/EdgeSpeed/*` 写入。若 `height_jump_m_raw` 明显大于 `0.10` 但 `excess_speed_mps_raw` 长期较高，说明策略仍在地形突变前高速冲击；若 `height_jump_m_raw` 接近 `0`，`Reward/edge_speed_penalty` 应接近 `0`。

## 6. 动作与底层控制指标

### 6.1 `Action/*`

| tag | 终端是否打印 | 含义 | 主要用途 |
|---|---:|---|---|
| `Action/policy_abs_mean` | 是 | policy 8 维归一化动作绝对值均值 | 判断动作是否过于激进或塌缩 |
| `Action/policy_std` | 是 | 当前 batch 中动作标准差 | 判断动作变化幅度 |
| `Action/wheel_speed_reference_abs_mean_raw` | 是 | 轮速参考绝对值均值，单位 rad/s | 看底层轮速分配是否过高 |
| `Action/wheel_torque_target_abs_mean_raw` | 是 | 车轮力矩目标绝对值均值，单位 N*m | 看牵引力矩使用强度 |
| `Action/desired_planar_command_abs_mean_raw` | 是 | policy 映射后的期望平面命令绝对值均值 | 看高层想让车怎么动 |
| `Action/shaped_planar_command_abs_mean_raw` | 是 | low-slip 整形后的平面命令绝对值均值 | 看底层整形后实际给分配器的命令 |
| `Action/planar_command_shaping_delta_abs_mean_raw` | 是 | shaped command 与 desired command 的差值绝对值均值 | 看 low-slip 整形干预强度 |
| `Action/desired_planar_vx_raw` | 否 | 期望纵向速度均值，单位 m/s | 判断 policy 是否输出前进/倒车 |
| `Action/desired_planar_wz_raw` | 否 | 期望偏航角速度均值，单位 rad/s | 判断 policy 是否持续转向 |
| `Action/shaped_planar_vx_raw` | 否 | 整形后的纵向速度均值，单位 m/s | 判断低层是否削弱/调整前进命令 |
| `Action/shaped_planar_wz_raw` | 否 | 整形后的偏航角速度均值，单位 rad/s | 判断低层是否削弱/调整转向命令 |
| `Action/planar_command_delta_vx_raw` | 否 | `shaped_vx - desired_vx` | 看纵向命令被改了多少 |
| `Action/planar_command_delta_wz_raw` | 否 | `shaped_wz - desired_wz` | 看转向命令被改了多少 |
| `Action/contact_weight_mean_raw` | 否 | 轮级接触权重均值 | 看车轮接触状态对力矩分配的影响 |

判断 Stage1 是否真的学到地形推进，不能只看 `desired_planar_vx_raw`。更合理的链条是同时看 `desired_planar_vx_raw`、`shaped_planar_vx_raw`、`wheel_speed_reference_abs_mean_raw`、`wheel_torque_target_abs_mean_raw`、`Stage1Eval/global/forward_x_mean` 和滑移指标。

### 6.2 `LowLevel/*`

| tag | 终端是否打印 | 含义 | 主要用途 |
|---|---:|---|---|
| `LowLevel/v_parallel_abs_mean_raw` | 是 | 轮体沿轮前向的速度绝对值均值，单位 m/s | 判断有效轮地前向运动 |
| `LowLevel/v_perp_abs_mean_raw` | 是 | 轮体沿水平侧向轴的速度绝对值均值，单位 m/s | 判断侧向漂移 |
| `LowLevel/delta_v_abs_mean_raw` | 是 | 轮地速度误差绝对值均值 | 判断轮速参考与实际轮地运动不匹配程度 |
| `LowLevel/tau0_abs_mean_raw` | 是 | 牵引分配中的基础力矩项绝对值均值 | 看前馈/跟踪部分用力 |
| `LowLevel/tau1_abs_mean_raw` | 是 | 滑移反馈力矩项绝对值均值 | 看反馈修正强度 |

这些指标更接近底层控制健康状态。若 `v_parallel_abs` 很低但轮速和力矩很高，通常说明轮地作用效率差；若 `v_perp_abs` 很高，说明车辆在地形上有明显侧向滑动。

## 7. 滑移、姿态和观测指标

### 7.1 `LowSlip/*`

| tag | 终端是否打印 | 含义 | 主要用途 |
|---|---:|---|---|
| `LowSlip/longitudinal_slip_pass_rate` | 是 | 单个 env 的平均纵滑率低于阈值的比例 | 看低纵滑条件是否满足 |
| `LowSlip/slip_angle_pass_rate` | 是 | 单个 env 的平均侧滑角低于阈值的比例 | 看低侧滑条件是否满足 |
| `LowSlip/combined_pass_rate` | 是 | 纵滑和侧滑角同时达标的比例 | 低滑移综合通过率 |
| `LowSlip/longitudinal_slip_margin` | 是 | 纵滑阈值减去实际平均纵滑 | 大于 `0` 表示平均意义下达标 |
| `LowSlip/slip_angle_margin` | 是 | 侧滑角阈值减去实际平均侧滑角 | 大于 `0` 表示平均意义下达标 |

当前阈值：

- 纵滑阈值：`1.0`
- 侧滑角阈值：`0.35 rad`

`combined_pass_rate` 是运动质量指标，不是任务完成指标。它必须和 `Terrain/*`、`Tracking/*` 一起看：只有既能前进又能低滑移，才有资格进一步讨论地形适应控制质量。

### 7.2 `Observation/*`

| tag | 终端是否打印 | 含义 |
|---|---:|---|
| `Observation/wheel_longitudinal_slip_abs_mean_raw` | 是 | 六个车轮纵滑率绝对值均值 |
| `Observation/wheel_slip_angle_abs_mean_raw` | 是 | 六个车轮侧滑角绝对值均值，单位 rad |
| `Observation/wheel_normal_contact_force_sum_raw` | 是 | 每个 env 六轮法向接触力归一化和 |
| `Observation/pitch_deg` | 是 | 中车体 pitch 均值，单位 deg |
| `Observation/roll_deg` | 否 | 中车体 roll 均值，单位 deg |
| `Observation/ball_joint_vel_abs_mean_raw` | 是 | 六个球铰速度绝对值均值 |
| `Observation/ball_joint_pos_abs_mean_raw` | 否 | 六个球铰角度绝对值均值 |
| `Observation/ball_joint_target_error_abs_mean_raw` | 否 | 球铰目标与当前角度误差绝对值均值 |
| `Observation/base_lin_vel_y_raw` | 否 | 车体系横向速度均值 |
| `Observation/projected_gravity_xy_norm_raw` | 否 | 车体姿态倾斜在重力投影中的水平分量 |
| `Observation/wheel_joint_vel_abs_mean_raw` | 否 | 六个车轮角速度绝对值均值 |

球铰限位使用率也会写入 TensorBoard：

- `Observation/spm1_platform_joint_x_pos_raw`
- `Observation/spm1_platform_joint_y_pos_raw`
- `Observation/spm1_platform_joint_z_pos_raw`
- `Observation/spm2_platform_joint_x_pos_raw`
- `Observation/spm2_platform_joint_y_pos_raw`
- `Observation/spm2_platform_joint_z_pos_raw`
- 对每个球铰还会记录 `limit_usage_mean_raw` 和 `limit_usage_max_raw`

这些指标用于判断球铰是否长期贴近限位。若 limit usage 接近或超过 `1.0`，说明策略正在频繁使用危险姿态范围，容易触发 `ball_joint_limit_rate`。

## 8. 命令与目标点指标

### 8.1 `Command/*`

| tag | 终端是否打印 | 含义 |
|---|---:|---|
| `Command/goal_rel_x` | 否 | env_0 目标点在车体系前向的相对坐标，单位 m |
| `Command/goal_rel_y` | 否 | env_0 目标点在车体系横向的相对坐标，单位 m |
| `Command/goal_rel_z` | 否 | env_0 目标点相对高度，单位 m |
| `Command/goal_rel_heading` | 否 | env_0 目标 heading 相对车体 heading，单位 rad |
| `Command/goal_direction_offset_deg` | 否 | env_0 目标方向采样偏移，单位 deg |
| `Command/goal_heading_offset_deg` | 否 | env_0 目标 heading 偏移，单位 deg |

注意：command 曲线刻意使用 `env_0`，不是跨 env 均值。这样可以看到一个具体目标轨迹，而不是多个 env 的目标平均后变成难以解释的曲线。

### 8.2 `episode/*`

episode 指标只在有环境 reset 后聚合，因此训练前期或 episode 很长时，某些曲线可能更新较慢。

| tag | 含义 |
|---|---|
| `episode/return` | 单个 episode 累计总 reward 的均值 |
| `episode/return_per_step` | episode 平均每步 reward |
| `episode/distance_to_target` | episode 内该 reward 分量累计值 |
| `episode/progress_to_target` | episode 内 progress reward 累计值 |
| `episode/reached_target` | episode 内 reached target reward 累计值 |
| `episode/far_from_target` | episode 内 far penalty 累计值 |
| `episode/angle_diff` | episode 内 angle reward 累计值 |
| `episode/turn_speed_penalty` | episode 内 turn-speed penalty 累计值 |
| `episode/slip_penalty` | episode 内 slip penalty 累计值 |
| `episode/action_rate_penalty` | episode 内 action rate penalty 累计值 |
| `episode/contact_support_penalty` | episode 内 contact support penalty 累计值 |
| `episode/edge_speed_penalty` | episode 内 edge speed penalty 累计值 |
| `episode/goal_target_x_world` | episode 结束时目标点世界系 x 均值 |
| `episode/goal_target_y_world` | episode 结束时目标点世界系 y 均值 |
| `episode/goal_target_z_world` | episode 结束时目标点世界系 z 均值 |
| `episode/goal_target_heading_world` | episode 结束时目标 heading 世界系均值 |
| `episode/goal_direction_offset_deg` | episode 目标方向偏移均值 |
| `episode/goal_heading_offset_deg` | episode 目标 heading 偏移均值 |
| `episode/waypoints_completed` | episode 内命中的 waypoint 数 |
| `episode/waypoint_completion_pct` | waypoint 完成百分比 |
| `episode/waypoint_hit_rate` | reset 时 waypoint_hit 的比例 |
| `episode/end_active_waypoint_pos_error` | episode 结束时 active waypoint 距离误差 |
| `episode/end_active_waypoint_bearing_abs` | episode 结束时 active waypoint 方向误差 |
| `episode/waypoint_hit_pos_error` | 命中 waypoint 时的位置误差 |
| `episode/success_hit_pos_error` | success reset 的位置误差；Stage1 terrain-column 下通常不适合作为主指标 |

对应还有 `episode_per_step/*` 指标，即把 episode 累计分量除以 episode 长度，便于比较不同长度 episode。

## 9. Per-wheel 指标

所有 `PerWheel/*` tag 都会写入 TensorBoard，不打印到终端。格式为：

`PerWheel/<wheel_name>/<metric_name>`

当前每个车轮会记录：

- `wheel_joint_vel`
- `wheel_speed_reference`
- `wheel_torque_target`
- `contact_weight`
- `normal_force`
- `v_parallel`
- `v_perp`
- `delta_v`
- `tau0`
- `tau1`
- `longitudinal_slip`
- `slip_angle`

这些指标用于定位“是哪一个轮子造成问题”。例如：

- 某个轮子的 `normal_force` 长期接近 `0`，说明它经常离地或接触弱。
- 某个轮子的 `longitudinal_slip` 长期显著高于其他轮，说明该轮可能在空转、打滑或被地形卡住。
- `wheel_speed_reference` 高但 `v_parallel` 低，说明轮速命令没有转化成有效前进。
- `tau1` 高说明滑移反馈正在强烈修正该轮。

## 10. 终端高频盯盘指标

终端每个 PPO iteration 会按固定顺序打印以下环境指标：

1. `Action/policy_abs_mean`
2. `Action/policy_std`
3. `Action/wheel_speed_reference_abs_mean_raw`
4. `Action/wheel_torque_target_abs_mean_raw`
5. `Action/desired_planar_command_abs_mean_raw`
6. `Action/shaped_planar_command_abs_mean_raw`
7. `Action/planar_command_shaping_delta_abs_mean_raw`
8. `Reward/total`
9. `Reward/reached_target`
10. `Reward/distance_to_target`
11. `Reward/progress_to_target`
12. `Reward/angle_diff`
13. `Reward/turn_speed_penalty`
14. `Reward/slip_penalty`
15. `Reward/far_from_target`
16. `Observation/wheel_longitudinal_slip_abs_mean_raw`
17. `Observation/wheel_slip_angle_abs_mean_raw`
18. `LowSlip/combined_pass_rate`
19. `LowSlip/longitudinal_slip_pass_rate`
20. `LowSlip/slip_angle_pass_rate`
21. `LowSlip/longitudinal_slip_margin`
22. `LowSlip/slip_angle_margin`
23. `ProgressGate/combined_gate`
24. `ProgressGate/multiplier`
25. `ProgressGate/longitudinal_gate`
26. `ProgressGate/slip_angle_gate`
27. `Observation/wheel_normal_contact_force_sum_raw`
28. `Observation/pitch_deg`
29. `Observation/ball_joint_vel_abs_mean_raw`
30. `LowLevel/v_parallel_abs_mean_raw`
31. `LowLevel/v_perp_abs_mean_raw`
32. `LowLevel/delta_v_abs_mean_raw`
33. `LowLevel/tau0_abs_mean_raw`
34. `LowLevel/tau1_abs_mean_raw`
35. `Termination/success_rate`
36. `Termination/time_out_rate`
37. `Termination/far_from_target_rate`
38. `Termination/ball_joint_limit_rate`
39. `Termination/terminated_rate`
40. `Tracking/active_waypoint_pos_error`
41. `Tracking/active_waypoint_bearing_abs`
42. `Tracking/active_segment_completion_pct`
43. `Tracking/terrain_target_advances_mean`
44. `Terrain/current_level_mean`
45. `Terrain/forward_x_from_current_tile_start_mean`
46. `Tracking/waypoints_completed_mean`
47. `Tracking/episode_completion_pct`

终端快速判断建议：

- 先看 `Stage1Eval/global/forward_x_mean`、`Stage1Eval/global/current_level_mean`、`Stage1Eval/global/max_row_reached_rate` 和 `Stage1Eval/global/valid_target_masked`：是否真的沿地形列向前推进，还是已经进入最高 row 语义边界。
- 再看 `Termination/far_from_target_rate` 和 `ball_joint_limit_rate`：是否因偏离或姿态越界提前失败。
- 再看 `Observation/wheel_longitudinal_slip_abs_mean_raw`、`Observation/wheel_slip_angle_abs_mean_raw`、`LowSlip/combined_pass_rate`：是否形成低滑移运动。
- 最后看 `Action/*` 和 `LowLevel/*`：判断是 policy 命令问题、low-slip 整形问题、轮速分配问题，还是轮地接触问题。

## 11. 不能直接作为结论的指标

以下指标容易被误读：

- `Termination/success_rate`：Stage1 terrain-column 目标下不是主成功率，当前会被置零。
- `Reward/total`：回报升高不等于真实地形适应能力增强，可能来自 reward shaping。
- `Train/mean_reward`：只能说明 PPO 目标函数改善，不能单独说明低滑移或稳定性。
- `Action/desired_planar_vx_raw`：高前进命令不等于有效前进，需要同时看 `forward_x`、`v_parallel` 和滑移。
- `LowSlip/combined_pass_rate`：低滑移通过率高但车不前进，也不能说明任务成功。
- 单个 terrain chase 视频：视频是行为证据，但不能替代完整曲线和多地形统计。

## 12. 推荐的 Stage1 判断组合

### 12.1 是否在地形列上有效前进

优先看：

- `Stage1Eval/global/forward_x_mean`
- `Terrain/current_level_mean`
- `Stage1Eval/global/max_row_reached_rate`
- `Stage1Eval/global/valid_target_masked`
- `Tracking/terrain_target_advances_mean`
- `Tracking/active_segment_completion_pct`
- terrain chase 视频中的实际车体位移

基本逻辑：车辆应沿当前 terrain column 的 `+x` 方向持续推进，并能推动 terrain level 上升。

### 12.2 是否稳定

优先看：

- `Termination/far_from_target_rate`
- `Termination/ball_joint_limit_rate`
- `Termination/time_out_rate`
- `Observation/pitch_deg`
- `Observation/roll_deg`
- 球铰 `limit_usage_*`

基本逻辑：如果 `far_from_target_rate` 或 `ball_joint_limit_rate` 高，说明策略没有稳定穿越当前地形。

### 12.3 是否低滑移

优先看：

- `Observation/wheel_longitudinal_slip_abs_mean_raw`
- `Observation/wheel_slip_angle_abs_mean_raw`
- `LowSlip/combined_pass_rate`
- `LowSlip/longitudinal_slip_margin`
- `LowSlip/slip_angle_margin`
- `PerWheel/*/longitudinal_slip`
- `PerWheel/*/slip_angle`

基本逻辑：低滑移必须和有效前进一起成立，不能只看 pass rate。

### 12.4 是否底层控制链健康

优先看：

- `Action/desired_planar_command_abs_mean_raw`
- `Action/shaped_planar_command_abs_mean_raw`
- `Action/planar_command_shaping_delta_abs_mean_raw`
- `Action/wheel_speed_reference_abs_mean_raw`
- `Action/wheel_torque_target_abs_mean_raw`
- `LowLevel/v_parallel_abs_mean_raw`
- `LowLevel/v_perp_abs_mean_raw`
- `LowLevel/delta_v_abs_mean_raw`
- `PerWheel/*`

基本逻辑：如果 action、轮速、力矩都很大，但 `forward_x` 和 `v_parallel` 不高，则问题更可能在轮地接触/滑移/地形阻碍，而不是 policy 没有输出动作。

## 13. 后续导出数值报告的方法

如果恢复了 Stage1 的 TensorBoard event 文件，可以用当前项目已有的导出工具生成 CSV / JSON：

```bash
python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/tensorboard_export.py \
  RL_Training/logs/rsl_rl/complete_car_stage1/<run_dir>
```

如果恢复了 runtime log，应同时保留：

- PPO iteration blocks
- terrain chase selection / recording messages
- warning / error traceback
- `Training time` 或 `Record-only runtime`

数值报告应至少包含：

- 最后一个有效 iteration
- 是否正常跑满 `max_iterations`
- 最终 checkpoint
- 后 `25/50/100` 个 TensorBoard step 的均值
- peak 与稳定窗口，而不是只看单点最高值
- 对每类地形分别的 chase 视频行为观察
