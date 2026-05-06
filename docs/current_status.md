# 当前状态

## 当前文献 PDF 转 Markdown 工具状态

- 已新增 Codex Skill：`/home/lbz/.codex/skills/opendataloader-pdf/`。
- 后续文献 PDF 转 Markdown 默认使用该 Skill 和本地 OpenDataLoader PDF 项目；MinerU 不作为默认工具，`pdftotext` 仅用于诊断或修复 OpenDataLoader 已确认无法恢复的 PDF 字体/CMap 损坏片段，不作为整批替代转换器。
- 当前固定本地项目路径：`/home/lbz/opendataloader-pdf-fulltty`，其远端为 `https://github.com/opendataloader-project/opendataloader-pdf.git`；`/home/lbz/` 下重复的 `opendataloader-pdf*` 实验目录已清理，只保留该目录。
- Skill 内置批量转换脚本：`/home/lbz/.codex/skills/opendataloader-pdf/scripts/convert_pdfs.py`。
- 本终端环境运行 OpenDataLoader 时需设置 `JAVA_TOOL_OPTIONS=-Djava.awt.headless=true`。
- `docs/literature/lunwen` 已完成 PDF 清理与第一章写作用途分类：删除 `20` 个内容完全一致的 `-1.pdf` 副本，并按用户追加要求删除 `14` 个 `_zh-CN_dual.pdf` 双语版本；当前分类语料保留英文/原始版本 `41` 个 PDF，另有用户加入的本科毕业设计样本 `基于双目视觉的多自由度机械臂避障与运动规划 (2).pdf` 用于第一章写作风格调研；当前未发现 `_zh-CN_dual.pdf` 文件。
- `docs/literature/lunwen` 当前按 `01_development_and_applications`、`02_morphology_structure_mechanism`、`03_model_based_dynamics_control`、`04_terrain_perception_planning`、`05_rl_complex_terrain_control`、`06_learning_frameworks_transfer` 六类组织；第一章各小节参考文献选择和写作思路见 `docs/literature/lunwen/第一章文献分类与写作思路.md`。
- 已按用户逐节评价与修改建议继续润色第一章绪论 Markdown 初稿：`docs/literature/lunwen/第一章绪论初稿.md`；新版 `1.1` 从复杂地形失效机制切入，弱化工具平台表述，将“感知”收窄为当前阶段的局部地形观测。
- 新版第一章已重构为带二级小节的硕博论文式结构：`1.2` 按折腰转向/全地形运输、工程车辆机器人化、主动形态调节、模型控制到学习控制展开；`1.3` 改为三节主动铰接复杂地形控制难点；`1.4` 按模型方法的启示与局限组织；`1.5` 增加课程学习与 Stage0 到 Stage1 阶段训练逻辑；`1.7` 降调为“本文主要研究内容”。正文采用顺序编码引用，末尾列出 `42` 条参考文献，当前参考文献条目仍需后续按学校格式逐条核对。
- 正式 LaTeX 第一章 `毕业论文/毕业论文模板/LaTeX/chapters/chapter01.tex` 已补写 `1.4 论文主要研究内容`：按等效建模与仿真平台、底层运动控制链路、强化学习任务构建、Stage0 到 Stage1 阶段化训练与评价四项组织，并保持“不预设主动铰接结构必然优于其他结构”的表述边界。
- 正式 LaTeX 第二章和第四章正文初稿已更新：`chapter02.tex` 写成“系统结构与仿真建模”，突出从真实机构到可训练仿真模型的转换；`chapter04.tex` 写成基于强化学习的地形自适应控制方法，按分层控制、RL 问题定义、Stage0、Stage1、PPO warm-start 和结果边界展开。用户已明确要求第三章原来的运动学模型推导和底层动力学/轮级分配完整保留，当前 `chapter03.tex` 已恢复为“车辆运动学建模”主线，不再用 3-RRR 正逆运动学推导替换原正文。
- 已按用户澄清生成 `docs/literature/全部文献BibTeX.md`：扫描 `docs/literature/**/*.pdf` 共 `158` 个 PDF，按规范化题名合并跨目录副本、`-1` 副本和 `_zh-CN_dual` 双语副本后得到 `95` 个唯一 BibTeX 条目；缺少完整出版信息的条目用本地 PDF 文件名推断并保留草稿提示，正式进入论文参考文献库前仍需逐条核对。
- `docs/literature/全部文献LaTeX引用.md` 是此前误按 LaTeX 正文引用键生成的清单，不是本轮用户最终要求的 BibTeX 输出。
- 已使用 OpenDataLoader 将 `docs/literature/综述论文/Wang 等 - 2024 - A Survey on Path Planning for Autonomous Ground Vehicles in Unstructured Environments.pdf` 转换为 `docs/literature/output/Wang 等 - 2024 - A Survey on Path Planning for Autonomous Ground Vehicles in Unstructured Environments.md`；该 PDF 与 `docs/literature/lunwen/` 下同名文件 SHA-256 一致，输出 Markdown 为 `851` 行，并生成 `12` 张图片资源。
- 已使用 OpenDataLoader 将 `docs/literature/综述论文/无人驾驶铰接转向车辆路径跟踪控制研究综述_祝青园.pdf` 转换为 `docs/literature/output/无人驾驶铰接转向车辆路径跟踪控制研究综述_祝青园.md`；源 PDF 为 `21` 页，输出 Markdown 为 `966` 行，并生成 `16` 张图片资源。该 CNKI PDF 存在字体/CMap 映射警告，正文整体可读，但公式变量和部分参考编号可能需要回查源 PDF。
- 已使用 OpenDataLoader 将 `docs/literature/铰接车发展历史` 中 `20` 个 PDF 覆盖转换到 `docs/literature/output/铰接车发展历史`，输出 `20` 个 Markdown 文件、`20` 个图片目录、`528` 张图片。
- 本次已修复该目录中 PDF 连字、私有区数学字形和参考文献空括号问题：`15` 个文件进行了通用乱码清理，其中 `2自由度铰接车体车辆越障偏移饱和控制_寇伟.md` 与 `张君 - 2019 - 双桥独立驱动铰接车辆牵引力控制策略研究.md` 因 CNKI PDF 字体/CMap 损坏严重，保留 OpenDataLoader 图片目录并用 PDF 文本层重建正文。
- 已基于上述 `20` 篇 Markdown 完成铰接车发展历史文献阶段 `3-8` 的结构化整理，输出位置仍为 `docs/literature/output/铰接车发展历史`。
- 阶段 `3-8` 产物包括：`literature_database.yaml`、`missing_references.md`、`classification_system.md`、`timeline.md`、`timeline.html`、`articulated_vehicle_review.md`、`quality_check.md`。
- 已完成一轮铰接式越野车辆综述网络检索：国外最直接的发展脉络综述仍以 Holm 1970《Articulated, wheeled off-the-road vehicles》为核心；国内优先使用成龙 2018《铰接履带式全地形车技术发展对比解析》、李补莲和叶晓彤 2011《俄罗斯铰接式全地形车》、曲学春等 2014《国外履带式全地形车发展现状》等中文来源；近年补充可用 SAE 2023 主动铰接轮式架构和 Euro-SD 2025 军用铰接全地形车述评。
- SAE 2023《Actively Articulated Wheeled Architectures for Autonomous Ground Vehicles - Opportunities and Challenges》的 NSF PAGES accepted manuscript 公开全文已下载到 `docs/literature/综述论文/Mehta 等 - 2023 - Actively Articulated Wheeled Architectures for Autonomous Ground Vehicles - Opportunities and Challenges.pdf`。
- 已基于本地 `docs/literature/` 语料整理铰接式越野车辆与 AAWV 发展脉络，输出 `docs/literature/铰接式越野车辆与AAWV发展脉络整理.md`；文件包含 `21` 个车辆/图谱条目，每个条目均给出图片、文字说明、图片来源文献和本地引用位置/引用状态，并补充可用于第一章的综述表述草稿。
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
  - `last_action` 观测已修正为当前 step 刚执行过的 policy action；reward 中的 `action_rate_penalty` 仍使用 `actions - last_actions` 表示当前动作相对上一控制步动作的变化。
  - 高度图保持原始 patch 尺寸和米制高度值，不 clip 到 `[-1, 1]`，不额外乘 scale，交由 PPO normalizer 归一化。
- 当前 Stage1 参数详情表：`docs/Stage1参数详情表.md`。
- `docs/Stage1参数详情表.md` 已按当前 Stage1 源码配置重新同步，区分了源码默认值、训练命令覆盖值和历史 run 参数快照。
- 当前 Stage1 奖励函数后续设计草案：`docs/Stage1奖励函数设计草案.md`；该文档已补充当前源码实际 reward 公式对照和拟采用 reward 公式设计。当前已将动作变化惩罚、接触权重 mask slip、模块支撑惩罚和地形突变前速度惩罚写入源码，其余拟采用项尚未写入源码；设计边界仍是保留局部高程图输入，不加入双目/LiDAR 原始感知、球铰极限惩罚和非轮体碰撞惩罚。
- 当前 Stage1 TensorBoard / 终端日志指标说明文档：`docs/stage1评价指标.md`；该文档基于当前 logger、env 和 train 源码整理指标含义，并明确当前本地缺少 Stage1 event/runtime log，未伪造具体曲线数值。
- 当前 Stage1 日志系统已重构为 stage-specific：Stage0 仍使用原 TensorBoard 白名单和终端 `CONSOLE_PRIORITY_TAGS`；Stage1 终端只打印 `Stage1Eval/*` 高信号评价指标，不再把固定为 `0` 的 `Termination/success_rate` 作为主指标。
- Stage1 新增 `Stage1Eval/global`、`Stage1Eval/flat` 和 `Stage1Eval/col00-col09` 指标，用于观察 flat retention、terrain column 通过能力、max-row reached、valid-target masked、滑移、接触、姿态、动作饱和与最难地形列。
- Stage1 PerWheel TensorBoard 调试默认关闭：`logging.enable_stage1_per_wheel_debug = False`；打开后只写法向力、纵滑、侧滑角、轮地纵/侧向速度、轮端力矩目标和轮速参考。
- 当前 CompleteCar 训练链路已补充 NaN/Inf 数值安全保护：policy action mean / std / log_std 在进入 `Normal` 前清理并保证 `std > 0`，obs / reward / extras metrics 写入前执行 `nan_to_num`，Stage1Eval 的 retention / difficulty 空 mask 返回 `0`。
- 已修复 Stage1 iteration `31` 暴露出的分布参数原地修改问题：`SquashedGaussianDistribution` 现在先在 `no_grad` 下清理 `log_std_param`，再让清理后的参数参与当前 autograd graph，避免 backward 报 `modified by an inplace operation`。
- PPO update 主流程已加入有限值保护：batch / loss / gradient / 参数更新前后都会检查 finite 状态；异常 mini-batch 会跳过，异常 optimizer step 会恢复更新前参数并清空 optimizer state，避免一次 `inf` surrogate loss 污染整条训练链。
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
  - 初始 row 已按地形限制：`stairs down` 和 `stairs up` 为 `0-1`，`discrete obstacles` 为 `0-2`，`flat` / `slope` / `rough` 保持 `0-5`。
  - episode 内 terrain-column 目标推进只增加 row，不改变 column，因此全地形训练依赖初始化时覆盖所有 column。
- 当前 Stage1 回放列选择：
  - `scripts/play.py` 新增 `--terrain_replay_columns`，默认 `all`。
  - `all` 表示按 env id 轮转分配到 `0-9` 全部地形列，要求 `--num_envs >= 10`。
  - 可指定单列编号，如 `--terrain_replay_columns 7`，使所有 env 出生在该地形列。
  - 可指定列编号列表，如 `--terrain_replay_columns 5,6`，也可指定地形名，如 `flat`、`slope_up`、`stairs_up`；重复地形名会映射到对应多列。
  - `scripts/play.py` 已修正 checkpoint 解析：`--checkpoint model_699.pt` 这类裸文件名会结合 `--load_run` 在 run 目录下查找；绝对路径、带目录的相对路径或 URI 仍按显式路径读取。
- 为避免 terrain-column target 与自由 waypoint 采样语义混淆，Stage1 cfg 不再显式写入 `commands.goal_distance` / `commands.goal_direction_max_deg`；其 reward 名义尺度改由 `rewards.params.nominal_goal_distance_m = 8.0` 和 `turn_speed_angle_scale_deg` 表达。
- 当前 Stage1 `reached_target` 奖励已启用，参数与 Stage0 相同：`reached_target_base_reward = 2.0`、`reached_target_weight = 6.0`。
- 当前 Stage1 `slip_penalty` 使用纵滑率系数 `5.0` 和侧滑角系数 `1.0`，总权重仍为 `slip_penalty_weight = -2.0`；该项已复用底层接触权重做 masked mean，只主要惩罚有效接地轮滑移，并用 `max(sum(c_i), 1.0)` 作为保护分母。
- 当前 Stage1 `action_rate_penalty` 已启用，用最大 episode 步数 `N = 2400` 归一化；`action_rate_penalty_weight = -10.0`，底盘动作权重 `0.5`，六个球铰姿态动作权重 `1.0`。Stage0 对应默认权重为 `0.0`。
- 当前 Stage1 `contact_support_penalty` 已启用，用同一底层接触权重评价前、中、后三段模块支撑；`contact_support_penalty_weight = -4.0`，`contact_support_min_weight = 0.3`。该项不强制六轮同时接地，只惩罚某一模块左右轮都长期支撑不足。
- 当前 Stage1 `edge_speed_penalty` 已启用，使用局部高程图车头前方 `1.0 m`、侧向额外 `0.5 m` 预览区域计算高度突变强度；高度跳变阈值为 `0.04-0.10 m`，强突变安全前进速度为 `0.5 m/s`，`edge_speed_penalty_weight = -6.0`。该项平地不额外限速，只惩罚地形突变前正向超速。
- 当前 Stage1 目标点逻辑：
  - 使用 terrain column / terrain type 生成目标点。
  - 目标方向沿地形列纵向 `+x`。
  - 目标列保持同列，目标行固定偏移 `1` 行；除 `stairs down`、`stairs up`、`discrete obstacles` 外，目标点 `y` 方向允许左右随机偏移 `3 m`。
  - `stairs down`、`stairs up`、`discrete obstacles` 的目标 x / y 直接使用下一行同列 tile origin，不做横向偏移。
  - 目标采样不再允许超过最大 row 后夹紧到同一最后 row；若推进会进入没有合法下一目标的最高 row 区域，则本段记为完成并 reset 到新的低 row。
  - `discrete obstacles` 已归入 `step` terrain class；`stairs down`、`stairs up`、`discrete obstacles` reset 时 xy 直接使用当前 tile origin，spawn z 由该 origin 点 heightfield 高度加 `0.30 m` 得到，不再使用 tile start 前 `0.3-0.8 m` 的 approach spawn。
  - terrain-column 目标不使用 `commands.resampling_time` 的计时重采样；row 升级只由目标点命中触发，不再使用相对当前 `tile_start_x` 前进超过 `5.6 m` 的距离捷径。
  - terrain-column reset 时按当前目标段进度判断 row 退级：若 episode 失败/超时、未命中目标且当前段进度 `< 0.30`，则当前 row 退一级；若已推进至少 `30%`，则保持当前 row 继续练习。
  - 目标命中不会触发 Stage1 success termination，但会贡献 `reached_target` 稀疏奖励并触发 row / target 推进。
  - reset 朝向固定为 `+x`。
  - 训练地形颜色已改为黑色 `(0.0, 0.0, 0.0)`。
  - 当前 episode 时长为 `40.0 s`，PhysX `max_velocity_iteration_count = 4`。
- 当前最新 Stage1 完整训练：
  - run：`RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-03_02-17-59_stage1_resume_from125_ppo_guard_to700`
  - 启动方式：从 `2026-05-03_01-17-07_stage1_resume_from25_fixed_distribution_to700/model_125.pt` resume，`32` env、headless、目标补足到 `700` iterations。
  - 训练结果：终端输出到 `699/700`，进程退出码 `0`，训练耗时约 `15492.84 s`，最终 checkpoint 为 `model_699.pt`。
  - 输出文件：同一 run 目录下已保存 TensorBoard event 文件、`model_125.pt` 到 `model_699.pt` 的间隔 checkpoint、`params/` 和 `git/` 快照；已导出 `308` 个非空 TensorBoard scalar tag 到 `tensorboard_export/`。
  - 数值稳定结论：未复现 iteration `31` 的 in-place autograd crash，也未出现会终止训练的 NaN/Inf distribution 错误。
  - 策略效果边界：训练链路已跑通，但末段仍未学出可靠全地形前进；最后可见 `Stage1Eval/flat/row_advance_rate = 0.0000`、`Stage1Eval/global/rows_advanced_mean = 0.0087`、`Stage1Eval/global/longitudinal_slip_abs_mean = 5.8542`、`Stage1Eval/global/contact_loss_rate = 0.5531`、`Stage1Eval/global/pitch_abs_mean = 10.5290`。
  - Flat 全过程复核：`Stage1Eval/flat` 不能只看最后 50 iteration。三段有效 Stage1 训练链路中，flat 在每次从低 row 重新开始后约 `9` 个 PPO iteration 内达到 `current_level_mean = 19`；到达最后 row 前，`row_advance_rate` 均值约 `0.75-0.85`，`v_forward_mean` 约 `1.9-2.1 m/s`，`retention_score` 约 `0.85-0.89`，说明 Stage0 平地前进技能基本保留。最后 row 后的 `row_advance_rate = 0` 主要受 terrain level 饱和和目标推进语义影响，不能单独解释为平地技能丢失。
  - TensorBoard 全量数据包：`results/stage1_tensorboard_all_iterations_2026-05-03.tar.gz` / `.zip`，包含当前 `complete_car_stage1` 下 `11` 个 run 的原始 event 文件、全部 scalar CSV/JSON 导出，以及有效训练链路 `0-699` 的 long/wide 合并表。
  - ChatGPT 高效分析精简包：`results/stage1_tensorboard_chatgpt_essential_0_699_2026-05-03.zip`，只保留 `0-699` 全 iteration 结果分析必要的核心 CSV、地形列长表、摘要表和分析提示；压缩包约 `1.5M`，内部 `10` 个实际文件。
  - 工程判断：当前优先问题已从“训练会崩溃”转为“Stage1 reward / curriculum / 目标推进语义下 policy 未形成稳定全地形通过能力”。
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
8. `action_rate_penalty`（Stage1 启用，Stage0 默认权重为 `0.0`）
9. `contact_support_penalty`（Stage1 启用，Stage0 默认权重为 `0.0`）
10. `edge_speed_penalty`（Stage1 启用，Stage0 默认权重为 `0.0`）

当前不再 active 的中间实验项：

- `timeout_penalty`
- `no_progress_penalty`
- `load_equalization`

说明：

- 上述中间实验项已从 active reward 代码和配置字段中删除，不再作为“保留但不生效”的配置存在；`action_rate_penalty` 已作为 Stage1 归一化动作变化惩罚重新接入，不属于该废弃项列表。
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

## MGDP 深度感知迁移调研状态

- 已检查本地 `/home/lbz/MGDP` 与官方远端 `origin/master`：当前本地 `master` 相对 `origin/master` 为“领先 1、落后 1”，远端新增提交 `dc0e4ef Uupdate author info`，仅修改 `index.html` 作者信息；`personal` 远端需要 GitHub 凭据，未完成 fetch。
- 已对照 MGDP 论文与代码实现：其深度感知主线是 Warp 深度图采集、深度图噪声注入、CNN encoder/decoder 重建干净深度图、可选高度图 encoder/decoder、深度 token 与高度 token 对比约束，再把低维视觉 token 与本体历史估计一起输入 actor。
- 当前 CompleteCar Stage1 已有局部高度 patch 直接进入 actor/critic，且相机、LiDAR 配置目前默认不参与策略输入；因此“直接复制 MGDP 完整感知模型”不是当前最短主线。
- 初步工程判断：把 MGDP 思路迁移到小车是可行的，但更适合作为 Stage2/Stage1 后续增强；在用户确认研究目标前，不应把它默认替换当前 Stage1 主线。
- 已完成围绕 height map / depth map / LiDAR / stereo / traversability / rough terrain RL / Isaac Lab height scanner 的补充检索：未找到成熟综述专门以“双目相机与 LiDAR 融合作为强化学习外感知模型”为中心；可用文献应按三条线组织，即地形可通行性与高程图融合综述、感知式强化学习 locomotion、开源感知与仿真训练框架。
- 对 CompleteCar 后续 Stage2 的当前边界判断：更合理的感知增强路线是先将双目/深度相机与 LiDAR 统一为局部 elevation / traversability map 或低维感知 token，再接入 RL 策略；不宜直接把原始双目图像和点云拼接到当前 Stage1 actor 中作为默认方案。
- 进一步按 Google Scholar / CNKI 线索复核后，英文侧最贴合“双目相机 + LiDAR 融合感知”的综述是 Marsh 等 2022《A Critical Review of Deep Learning-Based Multi-Sensor Fusion Techniques》；CNKI 侧最贴合的是王荣儿、伍济钢 2026《面向AGV环境感知的图像点云融合研究综述》和马建红等 2022《自动驾驶中图像与点云融合方法研究综述》。CNKI 中“图像点云融合”通常对应相机与 LiDAR 融合，不一定专门限定双目相机。

## 下一步优先事项

1. 如需训练新基准，直接使用默认 `run_name=best_baseline` 或显式指定新 run 名。
2. 若继续研究低滑移控制，不应只看 `success_rate`，需要同步观察纵滑率、当前口径侧滑角、有效推进速度、中车载荷和 waypoint 完成质量。
3. 若要声称低滑移/协同控制贡献，需要设计新的成功条件、对比实验或 ablation，而不是仅依赖该 baseline。
