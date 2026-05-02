# 当前状态

## 当前文献 PDF 转 Markdown 工具状态

- 已新增 Codex Skill：`/home/lbz/.codex/skills/opendataloader-pdf/`。
- 后续文献 PDF 转 Markdown 默认使用该 Skill 和本地 OpenDataLoader PDF 项目；MinerU 不作为默认工具，`pdftotext` 仅用于诊断或修复 OpenDataLoader 已确认无法恢复的 PDF 字体/CMap 损坏片段，不作为整批替代转换器。
- 当前固定本地项目路径：`/home/lbz/opendataloader-pdf-fulltty`，其远端为 `https://github.com/opendataloader-project/opendataloader-pdf.git`；`/home/lbz/` 下重复的 `opendataloader-pdf*` 实验目录已清理，只保留该目录。
- Skill 内置批量转换脚本：`/home/lbz/.codex/skills/opendataloader-pdf/scripts/convert_pdfs.py`。
- 本终端环境运行 OpenDataLoader 时需设置 `JAVA_TOOL_OPTIONS=-Djava.awt.headless=true`。
- 已使用 OpenDataLoader 将 `docs/literature/铰接车发展历史` 中 `20` 个 PDF 覆盖转换到 `docs/literature/output/铰接车发展历史`，输出 `20` 个 Markdown 文件、`20` 个图片目录、`528` 张图片。
- 本次已修复该目录中 PDF 连字、私有区数学字形和参考文献空括号问题：`15` 个文件进行了通用乱码清理，其中 `2自由度铰接车体车辆越障偏移饱和控制_寇伟.md` 与 `张君 - 2019 - 双桥独立驱动铰接车辆牵引力控制策略研究.md` 因 CNKI PDF 字体/CMap 损坏严重，保留 OpenDataLoader 图片目录并用 PDF 文本层重建正文。
- 已基于上述 `20` 篇 Markdown 完成铰接车发展历史文献阶段 `3-8` 的结构化整理，输出位置仍为 `docs/literature/output/铰接车发展历史`。
- 阶段 `3-8` 产物包括：`literature_database.yaml`、`missing_references.md`、`classification_system.md`、`timeline.md`、`timeline.html`、`articulated_vehicle_review.md`、`quality_check.md`。
- 当前语料中没有直接以强化学习控制铰接式移动机器人为主题的论文；综述中应把 RL 作为当前课题的研究缺口和后续路线，不应写成该文献集已经验证过的成熟方向。
- 当前结构化抽取仍有不确定项：部分论文的铰接自由度、DOI、期刊/会议信息和复杂公式需要回查源 PDF 或补充数据库检索；相关位置已用 `[UNCERTAIN]` 或 `[MISSING]` 标记。

## 当前 Stage1 地形训练状态

- 当前 Stage1 已进入 `best_baseline_2` warm-start 地形训练阶段。
- warm-start 来源：
  - Stage0 run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-28_15-28-38_best_baseline_2`
  - Stage0 checkpoint：`model_699.pt`
  - Stage1 warm-start checkpoint：`RL_Training/logs/rsl_rl/complete_car_stage1/warmstart_best_baseline_2/model_0.pt`
- warm-start 方式：
  - 不能直接 resume Stage0 checkpoint，因为 Stage0 actor/critic 观测维度为 `54`，当前 Stage1 为 `632`。
  - 已将 actor/critic 第一层和 obs normalizer 扩展到 `632` 维，前 `54` 维继承 Stage0，新增高度图维度初始化为零权重。
  - 训练使用 `--warmstart` 只加载 actor/critic，不加载 optimizer 和 iteration。
  - `convert_stage0_to_stage1_warmstart.py` 默认 `target_obs_dim` 已改为当前 Stage1 的 `632`，重新生成 warm-start 时不再默认生成旧 `972` 维 checkpoint。
- 当前 Stage1 观测策略：
  - actor / critic 均为 `54 + 34 * 17 = 632` 维。
  - 前 `54` 维继承自 Stage0 的本体 / command / last action 观测，当前 active scale 与 Stage0 对齐，全部为 `1.0`。
  - 高度图保持原始 patch 尺寸和米制高度值，不 clip 到 `[-1, 1]`，不额外乘 scale，交由 PPO normalizer 归一化。
- 当前 Stage1 参数详情表：`docs/Stage1参数详情表.md`。
- `docs/Stage1参数详情表.md` 已按当前 Stage1 源码配置重新同步，区分了源码默认值、训练命令覆盖值和历史 run 参数快照。
- 当前 Stage1 TensorBoard / 终端日志指标说明文档：`docs/stage1评价指标.md`；该文档基于当前 logger、env 和 train 源码整理指标含义，并明确当前本地缺少 Stage1 event/runtime log，未伪造具体曲线数值。
- 当前 Stage1 日志系统已重构为 stage-specific：Stage0 仍使用原 TensorBoard 白名单和终端 `CONSOLE_PRIORITY_TAGS`；Stage1 终端只打印 `Stage1Eval/*` 高信号评价指标，不再把固定为 `0` 的 `Termination/success_rate` 作为主指标。
- Stage1 新增 `Stage1Eval/global`、`Stage1Eval/flat` 和 `Stage1Eval/col00-col09` 指标，用于观察 flat retention、terrain column 通过能力、滑移、接触、姿态、动作饱和与最难地形列。
- Stage1 PerWheel TensorBoard 调试默认关闭：`logging.enable_stage1_per_wheel_debug = False`；打开后只写法向力、纵滑、侧滑角、轮地纵/侧向速度、轮端力矩目标和轮速参考。
- 当前 CompleteCar 训练链路已补充 NaN/Inf 数值安全保护：policy action mean / std / log_std 在进入 `Normal` 前清理并保证 `std > 0`，obs / reward / extras metrics 写入前执行 `nan_to_num`，Stage1Eval 的 retention / difficulty 空 mask 返回 `0`。
- 当前 `complete_car_stage1_cfg.py` 已改为 Stage1 相关参数显式配置风格，后续 Stage1 参数优先在该文件中统一修改。
- 当前新启动的 Stage1 run 使用与 Stage0 相同的底盘动作物理速度输出范围：
  - `a0 -> vx_cmd` 映射为 `[-2.0, 2.0] m/s`，允许倒车。
  - `a1 -> yaw_rate_cmd` 映射为 `[-2.0, 2.0] rad/s`。
- 当前 Stage1 训练地形列映射：
  - `0: flat`
  - `1: slope down`
  - `2: slope up`
  - `3-4: uneven rough`
  - `5-6: stairs down`
  - `7-8: stairs up`
  - `9: discrete obstacles`
  - 即第一列已恢复为平地，后续地形顺推，最后只保留一列 `discrete obstacles`。
- 当前 Stage1 初始出生 / 训练列分配：
  - 初始化时 env 按 id 均匀分配到 `0-9` 全部地形列。
  - episode 内 terrain-column 目标推进只增加 row，不改变 column，因此全地形训练依赖初始化时覆盖所有 column。
- 为避免 terrain-column target 与自由 waypoint 采样语义混淆，Stage1 cfg 不再显式写入 `commands.goal_distance` / `commands.goal_direction_max_deg`；其 reward 名义尺度改由 `rewards.params.nominal_goal_distance_m` 和 `turn_speed_angle_scale_deg` 表达。
- 当前 Stage1 目标点逻辑：
  - 使用 terrain column / terrain type 生成目标点。
  - 目标方向沿地形列纵向 `+x`。
  - 目标列保持同列，目标行固定偏移 `1` 行；除 `stairs down`、`stairs up`、`discrete obstacles` 外，目标点 `y` 方向允许左右随机偏移 `3 m`。
  - `stairs down`、`stairs up`、`discrete obstacles` 的目标 x / y 直接使用下一行同列 tile origin，不做横向偏移。
  - `discrete obstacles` 已归入 `step` terrain class，reset 时使用 step 类向后 spawn offset。
  - terrain-column 目标不使用 `commands.resampling_time` 的计时重采样；目标命中或相对当前 tile origin 前进超过 `5.6 m` 时，terrain level 加 `1` 并重采样下一目标。
  - 目标命中不会触发 Stage1 success termination，目标点只提供前进引导。
  - reset 朝向固定为 `+x`。
  - 训练地形颜色已改为黑色 `(0.0, 0.0, 0.0)`。
  - 当前 episode 时长为 `40.0 s`，PhysX `max_velocity_iteration_count = 4`。
- 当前后台训练：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-04-29_07-37-58_stage1_warmstart_best_baseline_2_32env_best_per_terrain_chase_700iter`
  - runtime log：`RL_Training/logs/runtime/stage1_32env_best_per_terrain_chase_setsid.log`
  - 启动方式：`32` env、headless、`700` iterations、`--warmstart`、`--record_terrain_chase_videos`。
  - 视频策略：按 terrain name 分组，先用 `600` step 选择每个地形中正向 `+x` 表现最好的 env，再按顺序逐个录制 `120 s` chase 视频。
  - 当前录制为非并发策略，同一时刻只创建一个 chase render product 和一个 mp4 writer。
  - 目标点红色 marker 开启；所有 env 创建 follow view；本次启动关闭目标方向箭头和 wheel-slip 可视箭头，保留目标点 marker。
  - 若该 run 是 2026-05-02 前启动，其 `params/env.yaml` 仍保留启动时的旧动作映射；源码修改只影响之后新启动的 Stage1 run。
  - 该训练 run 已在第 `2/6` 个视频期间于 PPO 更新阶段报错退出：`RuntimeError: normal expects all elements of std >= 0.0`。
  - 当前已切换为纯推理续录：
    - runtime log：`RL_Training/logs/runtime/stage1_32env_best_per_terrain_chase_resume_record_only.log`
    - 续录方式：`scripts/train.py --record_only --record_terrain_chase_videos --terrain_chase_selection_file .../selection.txt --terrain_chase_start_from 2`
    - 续录逻辑：复用原 `selection.txt`，从第 `2/6` 个视频开始覆盖重录 `slope up`，随后顺序录制剩余地形，不再进行 PPO 参数更新。
  - 当前源码已加入完整数值保护：若 policy distribution 的 action mean / std / log_std 出现非有限值，会先做有限值清理和 clamp，并保证传入 `Normal` 的 `std > 0`；obs、reward 和 extras metrics 在写出前也会清理 NaN/Inf。
- 历史可视化训练：
  - GUI run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-04-28_18-17-55_stage1_warmstart_best_baseline_2_32env_view_700iter`
  - 已按用户要求停止，终端最后完整输出到 PPO iteration `18/700`。
  - 该 run 当前只看到 `model_0.pt`，没有跑到默认保存间隔产生后续 checkpoint。
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
