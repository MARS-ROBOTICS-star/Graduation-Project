# 每日工作日志

## 2026-03-29

已完成：
- 核对本地 `main` 与 GitHub `origin/main` 的提交关系，确认远端在同步前没有额外新提交。
- 按当前工作区原样整理并提交 Git 变更，包含现有删除项与未跟踪新增内容。
- 将当前仓库快照推送到 GitHub `origin/main`，使远端与本地工作区保持一致。
- 同步更新 `docs/current_status.md`，移除“待同步”状态。

修改文件：
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- GitHub `origin/main` 已更新为当前本地工作区快照。
- 本轮同步后，仓库当前状态与远端主分支已一致。

下一步：
- 回到 RL baseline 收敛、USD 清理与论文写作主线。

## 2026-03-29

已完成：
- 根据 3-RRR 球面并联机构文献与现有符号化推导结果，重写毕业论文 `chapter03` 的球铰逆运动学部分。
- 在章节中补入三维旋转矩阵、齐次变换矩阵、方向向量约束、半角代换以及闭式逆解公式。
- 统一论文符号口径，将动平台姿态写为 `(\phi,\vartheta,\psi)`，将主动关节角保留为 `\theta_i`，避免姿态角与关节角冲突。
- 向论文参考文献库新增 `Sadeqi 等 2017` 的 BibTeX 条目。
- 实际执行 `xelatex -> bibtex -> xelatex -> xelatex` 编译验证，确认新增章节可被模板接受。

修改文件：
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- `毕业论文/毕业论文模板/LaTeX/reference/ref.bib`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `chapter03.tex` 已从占位模板改写为可直接用于论文正文的中文逆运动学章节。
- 当前章节推导链路已经固定为 方向向量建模 -> 几何约束 -> 半角代换 -> 二次方程闭式求解。
- 编译过程中与本次改动直接相关的引用和交叉引用均已收敛；主文档仍保留 `chapter01` 历史未补的两个旧引用告警，与本次修改无关。

下一步：
- 若需要，可继续在 `chapter04` 或 `chapter05` 中承接本章公式，补写控制映射、仿真验证或实验结果分析内容。

## 2026-03-28

已完成：
- 基于原始 PDF 重新整理 `Learning-based legged locomotion: State of the art and future perspectives` 的阅读笔记。
- 按已安装的 `literature-reading-notes` skill 模板重写了文献笔记结构，补齐论文快照、章节逻辑、mind map、分章节精读、术语表、重要参考文献和可复用 related-work 段落。
- 将该文献的总结重点进一步对齐到当前课题两阶段主线，明确其对 observation / reward / action / training framework / sim-to-real 的可迁移启发。
- 同步更新 `docs/current_status.md`，记录该阅读笔记已完成规范化重写。
- 根据用户新要求，将该笔记再次改写为“重要内容摘录与整理”版本，重点围绕正文中的概念定义、使用方式、该段引用的相关工作，以及对应完整参考文献信息。
- 去除了与当前课题直接绑定的分析内容，回到面向原文内容本身的综述笔记写法。
- 继续按用户给出的示例格式重写整份笔记，结构明确对齐为：论文快照、全文结构、mind map、章节精读笔记、关键知识点、术语表、重要参考文献、可复用综述段落。
- 将 `Section 3.2 Observation` 及其子节改为“核心观点 / 本节作用 / 段落主旨 / 重点概念提炼 / 学术含义 / 完整参考文献”风格，并同步重排 `Reward`、`Action Space`、`Learning Frameworks`、`Sim-to-real`、`Combining control and learning` 等关键章节。

修改文件：
- `docs/literature/mineru_output/Ha 等 - 2025 - Learning-based legged locomotion State of the art and future perspectives/auto/reading_notes.md`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前该文献对应目录下的 `reading_notes.md` 已不再只是首轮高层梳理，而是可直接复用的结构化综述笔记。
- 该综述继续支持当前仓库已固化的阶段化路线：先最小 baseline，再逐步加入复杂 observation、球铰控制、复杂地形和 sim-to-real 设计。
- 当前版本更符合“文献摘录式阅读笔记”用途：可以直接按节查看某个概念在综述中的定义、作用与引用来源。
- 当前版本已更接近“综述型文献精读卡片”，便于后续继续逐段扩写。

下一步：
- 若需要，可继续把 `3.3 Reward`、`3.4 Action space`、`4 Learning frameworks` 进一步扩展成逐段摘录版，并补得更全。

## 2026-03-16

已完成：
- 将仓库重组为更清晰的 `scripts/`、`results/`、`refs/` 和 `src/` 结构。
- 在 `AGENTS.md` 中加入仓库级启动上下文规则。
- 新增持久化会话记录文件 `docs/conversation_history.md`。
- 新增按日期记录的进度日志 `logs/daily_work_log.md`。
- 更新 Isaac Sim 辅助脚本，使其使用仓库相对路径。
- 确认 `.codex/config.toml` 存在且已启用 Web 搜索。
- 新增 `scripts/isaac_sim/check_isaaclab_asset.py` 用于 Isaac Lab 资产验证。
- 对 `USD/complete_car_alternative.usd` 进行了 Isaac Lab headless 验证。
- 识别出当前 USD 包尚不能直接作为 Isaac Lab articulation 生成，原因包括缺失 `configuration/*.usd` 依赖文件以及缺少 default prim。
- 将 Isaac Lab 资产检查入口切换为 `USD/complete_car.usd`。
- 对 `USD/complete_car.usd` 再次进行了 Isaac Lab headless 验证。
- 确认 stage 中实际根节点仍为 `/World/complete_car_alternative`，同时 `USD/complete_car.usd` 仍缺少 default prim，且 `USD/configuration/` 下存在 unresolved references。
- 修复 `USD/complete_car.usd`，将 default prim 设置为 `/World`。
- 清理 `USD/configuration/default_scene_base.usd` 中四个损坏的纯可视化引用。
- 通过 USD 检查确认损坏引用已被移除。
- 通过 Isaac Lab headless 加载确认当前机器人已被识别为 12 关节 articulation。

修改文件：
- `AGENTS.md`
- `README.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `docs/current_status.md`
- `scripts/isaac_sim/check_isaaclab_asset.py`
- `scripts/isaac_sim/inspect_usd_dependencies.py`
- `scripts/isaac_sim/repair_complete_car_usd.py`
- `scripts/isaac_sim/repair_complete_car_usd_v2.py`
- `scripts/isaac_sim/repair_complete_car_usd_v3.py`
- `scripts/isaac_sim/repair_complete_car_usd_v4.py`
- `scripts/isaac_sim/control_keyboard.py`
- `scripts/isaac_sim/validate_sensors.py`
- `refs/isaac_kb/README.md`
- `src/rl_lab/README.md`

下一步：
- 构建最小 Isaac Lab 任务骨架，并为完整车补齐 actuator 配置。

## 2026-03-16

已完成：
- 删除了仓库内手写的 direct-workflow 任务骨架 `src/rl_lab/tasks/`。
- 保留 `src/rl_lab/complete_car_rl_training/` 作为唯一的 Isaac Lab 模板 project。
- 更新仓库状态说明，明确后续 RL 环境开发应继续在模板 project 内进行。

修改文件：
- `src/rl_lab/__init__.py`
- `src/rl_lab/tasks/__init__.py`
- `src/rl_lab/tasks/complete_car_attitude_direct/__init__.py`
- `src/rl_lab/tasks/complete_car_attitude_direct/complete_car_env.py`
- `src/rl_lab/tasks/complete_car_attitude_direct/agents/__init__.py`
- `src/rl_lab/tasks/complete_car_attitude_direct/agents/rsl_rl_ppo_cfg.py`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

下一步：
- 将 `src/rl_lab/complete_car_rl_training/` 中的 cartpole 模板内容替换为完整车的 manager-based 最小任务。

## 2026-03-16

已完成：
- 新增 `docs/isaaclab模板使用指南.md`，整理了当前模板 project 的用途、推荐工作流、具体使用命令以及模板改造位置。
- 将 `docs/current_status.md` 改写为中文。
- 将 `logs/daily_work_log.md` 改写为中文，并明确后续新增日志统一使用中文。
- 在 `AGENTS.md` 中补充规则：`docs/current_status.md` 与 `logs/daily_work_log.md` 统一使用中文维护。

修改文件：
- `AGENTS.md`
- `docs/isaaclab模板使用指南.md`
- `docs/current_status.md`
- `logs/daily_work_log.md`

下一步：
- 按照 `docs/isaaclab模板使用指南.md` 中的顺序，在模板 project 内替换任务名、资产配置、动作配置、观测配置、奖励配置和 PPO 配置。

## 2026-03-17

已完成：
- 修复了 `complete_car_rl_training_env_cfg.py` 中已有的语法和 Isaac Lab API 拼写错误。
- 将模板环境中的 cartpole 资产配置整体替换为完整车 `ArticulationCfg`，入口指向 `USD/complete_car.usd`。
- 为完整车补齐了两组 actuator：
  - 6 个球铰等效关节 `ball_joints`
  - 6 个车轮关节 `wheel_joints`
- 将动作空间改为 12 维：
  - 6 维球铰位置动作
  - 6 维车轮速度动作
- 加入 `UniformVelocityCommandCfg`，使策略可以基于速度指令学习前进/后退。
- 将观测改为完整车版本，包含底盘速度、重力投影、速度指令、球铰状态、车轮速度和上一时刻动作。
- 将 reset、reward、termination 从 cartpole 版本替换为完整车版本。
- 用 `python3 -m py_compile` 对新的环境配置文件做了语法检查，结果通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/source/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前模板环境已经不再依赖 cartpole 关节名。
- 当前基线任务设计已经从“仅球铰姿态控制”升级为“球铰姿态 + 车轮前进/后退”的联合控制版本。
- 目前只完成了静态改写和语法检查，尚未完成 Isaac Lab 运行时验证。

下一步：
- 用 `list_envs.py`、`zero_agent.py` 或 `random_agent.py` 验证完整车环境能否正常创建与 step。
- 根据运行结果继续调节 wheel actuator 参数、奖励权重和终止阈值。

## 2026-03-18

已完成：
- 删除了 `complete_car_rl_training_env_cfg.py` 中 scene 级重复定义的 `ground` 与 `dome_light`。
- 将完整车 RL 环境的默认场景来源明确为 `USD/complete_car.usd` 内部已有场景元素。
- 将 PPO 配置中的 `experiment_name` 从 `cartpole_direct` 改为 `complete_car_rl_training`。
- 在 `AGENTS.md` 中新增“第一性原理”和“方案规范”两组仓库级协作约束。
- 同步更新了项目当前状态和长期会话结论。

修改文件：
- `src/rl_lab/complete_car_rl_training/source/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/source/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/agents/rsl_rl_ppo_cfg.py`
- `AGENTS.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 RL scene 只保留机器人资产定义，不再在配置层重复生成地面和灯光。
- 后续训练日志目录将使用完整车任务名，不再落到 cartpole 模板名下。
- 后续运行时验证需要优先确认 `complete_car.usd` 内置场景在 Isaac Lab 多环境复制下的行为是否稳定。

下一步：
- 运行 `list_envs.py`、`zero_agent.py` 或 `random_agent.py` 做环境创建与 step 验证。

## 2026-03-18

已完成：
- 对 `src/rl_lab/complete_car_rl_training/` 进行了目录整理，移除了重复的模板壳层。
- 将 Python 包从 `source/complete_car_rl_training/complete_car_rl_training/` 收平到项目根下的 `complete_car_rl_training/`。
- 将 `setup.py` 与 `config/extension.toml` 移到训练项目根目录，并将安装方式统一为 `pip install -e .`。
- 将 `setup.py` 改为优先使用标准库 `tomllib`，避免在 Python 3.11 下额外依赖第三方 `toml` 包。
- 删除了训练项目中的嵌套 `.git`、`.vscode`、UI 示例文件和旧 `src/rl_lab/tasks/` 残留。
- 更新了训练项目 README、仓库 README 和 `docs/isaaclab模板使用指南.md`，同步新的目录结构与命令。
- 新增 `src/rl_lab/README.md`，明确 `complete_car_rl_training/` 是唯一保留的训练工作区。

修改文件：
- `src/rl_lab/README.md`
- `src/rl_lab/complete_car_rl_training/setup.py`
- `src/rl_lab/complete_car_rl_training/pyproject.toml`
- `src/rl_lab/complete_car_rl_training/.gitignore`
- `src/rl_lab/complete_car_rl_training/config/extension.toml`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/__init__.py`
- `src/rl_lab/complete_car_rl_training/README.md`
- `src/rl_lab/complete_car_rl_training/scripts/list_envs.py`
- `README.md`
- `docs/isaaclab模板使用指南.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 训练项目后续统一按“项目根 + 单个 Python 包 + scripts”结构维护。
- 后续所有安装、运行、训练、回放命令都应从 `src/rl_lab/complete_car_rl_training/` 项目根执行。
- `python3 setup.py --name` 已能在本机默认 Python 下通过，不再因为缺少 `toml` 包失败。

下一步：
- 在新结构下重新执行 `pip install -e .`，然后做 `list_envs.py`、`zero_agent.py`、`random_agent.py` 验证。

## 2026-03-18

已完成：
- 实际执行了完整车 RSL-RL 训练启动流程，并确认正确任务 ID 为 `Complete-Car-Rl-Training-v0`。
- 确认当前终端会话下默认 GPU 路径不可用，CUDA / NVIDIA driver 未加载，直接按默认配置会在 runner 初始化时失败。
- 修复了 `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`，使 `--device` 同时覆盖环境和 RSL-RL runner 的 device。
- 使用 `PYTHONPATH` 注入训练项目根目录，绕过当前沙箱下 `pip install -e .` 的 build isolation 联网与用户站点只读问题。
- 以 `--headless --device cpu --num_envs 100` 实际跑通了 `reset -> step -> train` 链路。
- 训练已进入稳定学习迭代，并在日志目录中生成了 `model_0.pt` 与 `model_50.pt`。
- 识别出 `USD/complete_car.usd` 仍有离线不可解析的远端引用，以及多环境复制时的 `PhysicsScene` replication 报错。
- 从训练指标确认当前主要行为问题是 `root_too_low` 终止长期为 `1.0`，说明环境虽可训练，但 rollout 质量很差。

修改文件：
- `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 第一条完整训练链路已经在本机 CPU 模式下验证通过，说明任务注册、环境创建、manager 配置、RSL-RL runner 与日志落盘均已打通。
- 最新训练输出目录为 `src/rl_lab/complete_car_rl_training/logs/rsl_rl/complete_car_rl_training/2026-03-18_17-14-07/`。
- 当前真正阻塞点已经从“能否启动训练”切换为“USD 资产离线清理 + replicated physics scene 清理 + root height 相关任务调参”。

下一步：
- 清理 `USD/complete_car.usd` 中的远端引用和内嵌 `PhysicsScene`。
- 结合当前训练日志调整初始高度、`root_too_low` 阈值、reset 范围和奖励权重。
- 如果继续在当前终端会话运行训练，默认使用 `--device cpu`。

## 2026-03-18

已完成：
- 重新在当前 `env_isaacLab` conda 环境中核实了启动方式，确认 `python` 直接可导入 `isaaclab` 与 `isaacsim`。
- 确认旧文档中的 `env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV /home/ubuntu/IsaacLab/isaaclab.sh -p ...` 属于历史工作绕过方式，不再应作为默认启动命令。
- 识别出直接 `python scripts/...` 初始失败的真实原因不是 conda，而是：
  - 首次无交互启动会卡在 Omniverse EULA 确认
  - 当前 conda 环境内尚未安装项目包 `complete_car_rl_training`
- 使用 `python -m pip install -e . --no-build-isolation` 将训练项目安装到 `env_isaacLab`。
- 在安装后重新验证，直接运行 `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --num_envs 4 --headless --device cpu --max_iterations 1` 已可进入完整训练循环并完成 1 次 learning iteration。
- 更新了训练项目 README、模板使用指南、当前状态和长期会话结论，使仓库文档与当前真实启动方式一致。

修改文件：
- `src/rl_lab/complete_car_rl_training/README.md`
- `docs/isaaclab模板使用指南.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前默认启动路径应为：激活 `env_isaacLab` -> `python -m pip install -e . --no-build-isolation` -> 必要时设置 `OMNI_KIT_ACCEPT_EULA=YES` -> 直接运行 `python scripts/...`。
- 直接训练链路已在当前 conda 环境下重新验证通过。

下一步：
- 继续清理 `USD/complete_car.usd` 的远端引用与内嵌 `PhysicsScene`。
- 在直接 `python` 启动路径下继续迭代训练配置与奖励设计。

## 2026-03-18

已完成：
- 根据 Isaac Lab 的资产组织方式，重新明确了 `complete_car.usd` 与 `scene cfg` 的职责分离：
  - `complete_car.usd` 仅保留小车 articulation 本体与车体挂载传感器
  - `scene cfg` 负责地面和灯光
- 修改 `src/rl_lab/complete_car_rl_training/.../complete_car_rl_training_env_cfg.py`，在 `CompleteCarRlTrainingSceneCfg` 中补回 `ground` 与 `dome_light`。
- 识别出当前两个主要远端依赖分别是：
  - scene 层的 `default_environment.usd`
  - 机器人 USD 内的 `Example_Rotary.usda`
- 按当前需求，保留 scene 层 `default_environment.usd`，不再使用临时本地 `CuboidCfg` 地面方案。

修改文件：
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `scene` 层的 ground/light 配置已经重新回到 Isaac Lab 标准职责边界。
- 当前远端依赖分为两类：
  - scene 层继续使用 `default_environment.usd`
  - 机器人 USD 中仍有 `Example_Rotary.usda`

下一步：
- 清理 `USD/complete_car.usd` 中残留的 `Example_Rotary.usda` 远端引用。
- 继续评估 camera / lidar / IMU 是否都需要保留在当前 RL 基线资产里。

## 2026-03-19

已完成：
- 重新整理了仓库级 `AGENTS.md` 结构，将启动上下文、项目背景、优先级、协作规则、记忆规则和规范文件职责重新归类。
- 将 RL 训练路径正式固化到 `AGENTS.md`：
  - 阶段 0 先跑通训练闭环

## 2026-03-28

已完成：
- 读取并整理了根目录草稿 `literature_note_skill.md`。
- 将其安装为可被 Codex 发现的本地 skill：`/home/lbz/.codex/skills/literature-reading-notes/`。
- 新增该 skill 的 `SKILL.md` 与 `agents/openai.yaml`，统一技能名为 `literature-reading-notes`。
- 将本次变更同步写入 `docs/current_status.md` 与 `docs/conversation_history.md`，保证后续会话可继承。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `/home/lbz/.codex/skills/literature-reading-notes/SKILL.md`
- `/home/lbz/.codex/skills/literature-reading-notes/agents/openai.yaml`

产出/结论：
- 当前已可直接使用 `$literature-reading-notes` 触发结构化文献阅读笔记工作流。
- 根目录 `literature_note_skill.md` 现可视为技能草稿源，而不是最终可发现的 skill 入口。

下一步：
- 如需继续完善，可再按实际使用频率补充该 skill 的示例、引用规则细化或与 `docs/literature/` 的仓库内工作流衔接说明。
  - 阶段 1 做平地基础速度跟踪 baseline
  - 阶段 2 再加入球铰控制
  - 更后续阶段再加入运动学先验、地形适应和感知融合
- 明确了第 1 阶段默认 baseline 应优先采用“固定球铰姿态 + 轮式运动控制 + 低维本体观测”的最短路径方案。
- 同步更新了 `docs/current_status.md` 与 `docs/conversation_history.md`，把新的训练主线和当前代码现状之间的差异记录为长期记忆。

修改文件：
- `AGENTS.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 后续会话不应再把“轮子 + 球铰联合控制 + 复杂扩展”默认视为第一阶段主线。
- 当前应先把平地速度跟踪 baseline 做稳定，再逐步恢复机构复杂度。
- `AGENTS.md` 现在已经包含完整且可继承的 RL 训练路线说明，不再依赖单次对话上下文。

下一步：
- 按新的第 1 阶段主线收敛环境配置，优先确认是否需要把当前 12 维联合动作基线简化为固定球铰版本。
- 继续处理 `USD/complete_car.usd` 的远端依赖、复制兼容性和 `root_too_low` 相关训练稳定性问题。

## 2026-03-19

已完成：
- 读取并解释了 `2026-03-19_13-13-03` 训练 run 的 Isaac Lab 日志、Hydra 配置和 TensorBoard 标量项。
- 确认该 run 已生成 `model_0.pt`、`model_50.pt`、`model_100.pt`、`model_149.pt`，属于完整训练完成而非中途终止。
- 新增 `scripts/tensorboard_export.py`，可将单次 run 的 TensorBoard scalar 自动导出为本地 `csv/json`。
- 修改 `scripts/rsl_rl/train.py`，使训练结束后自动生成 `tensorboard_export/summary.json`、`latest_values.csv` 和各 tag 的 `scalars/*.csv`。
- 对 `2026-03-19_13-13-03` 的已有 run 执行了一次导出验证，确认离线分析文件已正常生成。
- 更新训练项目 `README.md`，补充 TensorBoard 离线导出说明。
- 新增 `docs/tensorboard_reading_guide.md`，总结 TensorBoard 读图方法、指标含义和诊断顺序。
- 新增 `skills/isaac-rl-run-diagnosis/` skill，并复制安装到 `~/.codex/skills/isaac-rl-run-diagnosis/`。

修改文件：
- `src/rl_lab/complete_car_rl_training/scripts/tensorboard_export.py`
- `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`
- `src/rl_lab/complete_car_rl_training/README.md`
- `src/rl_lab/complete_car_rl_training/docs/tensorboard_reading_guide.md`
- `src/rl_lab/complete_car_rl_training/skills/isaac-rl-run-diagnosis/SKILL.md`
- `src/rl_lab/complete_car_rl_training/skills/isaac-rl-run-diagnosis/agents/openai.yaml`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 后续每次训练结束后，都可以直接读取 run 目录下的 `tensorboard_export/`，不必依赖 TensorBoard 网页界面。
- 当前 `2026-03-19_13-13-03` run 的关键信号是：
  - `Train/mean_reward` 已明显上升
  - `Train/mean_episode_length` 已到 `480.0`
  - `Episode_Termination/time_out = 1.0`
  - `Episode_Termination/root_too_low = 0.0`
- 这说明当前 run 的 rollout 存活性明显好于此前 `root_too_low` 主导的异常情况。

下一步：
- 基于导出的 `latest_values.csv` 与各 tag CSV，继续逐项分析奖励构成和速度跟踪误差。
- 再按第 1 阶段主线评估是否应将球铰动作从默认 baseline 中收紧或固定。

## 2026-03-20

已完成：
- 为 `docs/literature/` 建立了“原始 PDF 保留 + MinerU 转 Markdown”并存的文献工作流。
- 新增 `scripts/literature/mineru_batch_convert.sh`，用于批量或单篇执行 MinerU PDF 转 Markdown。
- 新增 `scripts/literature/build_literature_manifest.py`，用于自动生成文献 PDF 与 Markdown 对照索引。
- 新增 `docs/literature/README.md`，明确文献目录规范、转换命令和 Codex 的读取顺序。
- 生成了首版 `docs/literature/catalog.md`，当前已列出全部本地 PDF，待 MinerU 转换后自动补齐 Markdown 路径。
- 更新 `AGENTS.md`、`README.md` 和 `docs/current_status.md`，把本地文献优先读 Markdown、PDF 负责核验的规则固化为长期约定。
- 创建仓库级 `.gitignore`，忽略本地 `.venv-mineru/` 文献工具虚拟环境。
- 在当前 `env_isaacLab` 环境中安装完成 `MinerU`。
- 首次单篇转换验证中，确认当前会话继承的本地代理变量会阻塞 MinerU 模型下载；已切换为“清空代理 + `MINERU_MODEL_SOURCE=modelscope`”的首跑方式。

修改文件：
- `.gitignore`
- `AGENTS.md`
- `README.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `docs/literature/README.md`
- `docs/literature/catalog.md`
- `scripts/literature/mineru_batch_convert.sh`
- `scripts/literature/build_literature_manifest.py`

产出/结论：
- 本仓库后续文献读取默认采用：
  - 先读 `md`
  - 再用 `pdf` 核对图、公式、页码和可疑段落
- 文献目录已经从“仅 PDF 堆放”升级为“可转换、可索引、可被 Codex 稳定读取”的结构。
- 当前机器上 MinerU 的首次模型下载不应直接沿用现有代理环境，而应优先使用 `modelscope`。

下一步：
- 完成至少一篇文献的 MinerU 转换 smoke test，并确认真实输出目录结构。
- 确认 MinerU 的实际输出目录结构后，再按真实产物补齐 catalog 中的 Markdown 链接。


补充完成：
- 阅读并筛选了 `docs/literature/` 下与 RL 环境配置和训练设计相关的文献。
- 按“与本课题形态相似度 + 对 observation/reward/action/termination 的直接借鉴价值 + 与当前阶段主线的贴合度”完成了推荐排序。
- 新增 `docs/literature/rl_env_reading_notes.md`，作为后续持续维护的文献阅读笔记。
- 将当前优先阅读顺序收敛为：
  - `Wiberg 2022`
  - `Wiberg 2024`
  - `Bauer 2025`
  - `Xu 2024`
  - `Salvi 2022`

补充修改文件：
- `docs/literature/rl_env_reading_notes.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

补充产出/结论：
- 已形成一份面向 RL env 设计的本地文献阅读入口，不再需要每次从全部文献重新筛选。
- 当前不应优先把感知综述和 3-RRR 机构学论文作为第 1 阶段 baseline 的主参考。

补充下一步：
- 基于阅读笔记中的前 3 篇文献，进一步提炼可直接映射到 Isaac Lab 的 `observation / action / reward / termination` 草案。

## 2026-03-20

已完成：
- 对 `Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning.pdf` 执行了单篇 MinerU 转换。
- 成功生成对应 Markdown、图片与中间产物目录：
  - `docs/literature/mineru_output/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning/auto/`
- 自动更新 `docs/literature/catalog.md`，将该文献条目标记为 `ready`。
- 基于生成的 Markdown 与原始 PDF，补充了 `docs/literature/rl_env_reading_notes.md` 中该文的精读结论。
- 提炼了该文对本课题的可迁移要点：
  - reward 的主目标项 + 约束项组织方式
  - termination 的危险姿态 / 危险接触 / timeout 框架
  - curriculum 的逐层加难组织方式
  - 不应在第 1 阶段直接照搬高维地形 observation 与联合结构控制

修改文件：
- `docs/literature/catalog.md`
- `docs/literature/mineru_output/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning/auto/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning.md`
- `docs/literature/rl_env_reading_notes.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前仓库已经有这篇论文的本地 Markdown，可直接作为后续阅读入口。
- 这篇论文对本课题最重要的价值不是“平台完全相同”，而是它把 rough-terrain vehicle 的 RL 任务定义拆得很完整。
- 对当前主线最合适的吸收方式是：先借鉴 reward / termination 逻辑，再在后续阶段逐步吸收地形 observation 和结构联合控制。

下一步：
- 继续辅助用户精读该文，并把其 `observation / action / reward / termination / curriculum` 映射到本课题的 Isaac Lab 环境设计上。

## 2026-03-21

已完成：
- 根据用户提出的要求，补充并固化了文献阅读类任务的交互协议。
- 在 `AGENTS.md` 的研究交互部分新增文献阅读辅助规则，明确：
  - 先确认单篇阅读目标
  - 默认按文章写作顺序推进提问
  - 提问逻辑优先遵循“是什么 -> 为什么 -> 联想与反思”
  - 每轮回答后需要进行纠正、补充与整理
  - 若理解不充分，允许围绕同一问题继续二次追问
- 确认当前 `Wiberg 等 - 2022` 的阅读目标为：
  - 主目标：整体掌握文章内容与逻辑
  - 次目标：提炼并学习 RL 环境设计
- 同步更新项目当前状态与长期会话结论，避免后续会话丢失这条协作规则。

修改文件：
- `AGENTS.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 本仓库后续的文献辅助阅读默认采用“教师式带读”而不是直接给结论。
- 对高相关文献，后续应先帮助用户掌握文章整体逻辑，再进入 env 设计细节和与本课题的迁移讨论。

下一步：
- 按新的交互协议，从 `Wiberg 等 - 2022` 的引言开始，依照文章顺序继续带读。
## 2026-03-22

已完成：
- 围绕 `Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning` 开展了一轮问答式精读，重点聚焦 RL 环境设计而非全文泛读。
- 将本轮对话中关于任务定义、observation、action、reward、termination、curriculum、evaluation 的梳理整理为结构化阅读笔记。
- 在该文献的 MinerU 输出目录下新增 `reading_notes.md`，便于后续直接在文献旁复习，不再只依赖聊天记录。
- 同步更新 `docs/current_status.md`，记录该文献目录下已形成可复用阅读笔记这一状态。

修改文件：
- `docs/literature/mineru_output/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning/auto/reading_notes.md`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已将该文献的第一轮精读结论沉淀为本地笔记，核心包括：
  - 任务定义应区分“目标”和“结果表现”
  - observation 可整理为地形感知、本体状态、任务相关信息三组
  - reward 设计应按“主任务 + 行为质量约束 + 终止条件 + 评估指标”来理解
  - curriculum、自然化 reset、训练/评估地形分离是该文献的重要训练组织方法

下一步：
- 继续对比后续 rough-terrain RL 文献，形成跨文献的可迁移设计共识，再回到本课题任务定义收敛。

## 2026-03-22

已完成：
- 安装并配置了独立的 `MinerU` 工作环境 `.venv-mineru`，避免污染现有 Isaac Lab 环境。
- 首次运行中补齐了 MinerU 所需的本地模型缓存，包括主模型、版面分析、阅读顺序、OCR、表格识别等依赖。
- 将 `Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain.pdf` 按仓库既定脚本流程转换为 Markdown。
- 围绕该文献完成了一轮问答式精读，重点提炼其 `observation / action / reward / termination / curriculum` 设计。
- 在该文献对应目录下新增 `reading_notes.md`，沉淀可复用阅读笔记，服务后续跨文献横向对比。

修改文件：
- `docs/literature/mineru_output/Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain/auto/Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain.md`
- `docs/literature/mineru_output/Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain/auto/reading_notes.md`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 该文献提供了一种更轻量的 rough-terrain RL 任务定义：高层 action、简洁 observation、极简 reward、单一维度 curriculum。
- 相比 `Wiberg 2022`，它更适合作为“任务简化、课程推进、goal-directed mobility 设计”的参考，而不是多执行器联合控制模板。
- 当前已具备至少两篇高相关文献的本地 Markdown 与结构化阅读笔记，后续可继续积累 2-3 篇后开展横向对比与本课题方案规划。

下一步：
- 继续精读 2-3 篇高相关文献并整理阅读笔记。
- 在文献样本足够后，系统输出面向本课题的横向对比与方案规划。

## 2026-03-22

已完成：
- 将 `Bouton和Gao - 2023 - MARCEL mobile active rover chassis for enhanced locomotion.pdf` 转换为 Markdown。
- 基于文献内容判断其更适合作为“结构动机与机理解释”参考，而不是当前阶段的 RL 环境配置主文献。
- 按用户要求，将该文献标记为后续撰写论文动机部分时应回看的参考文献。

修改文件：
- `docs/literature/mineru_output/Bouton和Gao - 2023 - MARCEL mobile active rover chassis for enhanced locomotion/auto/Bouton和Gao - 2023 - MARCEL mobile active rover chassis for enhanced locomotion.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `MARCEL` 与当前课题在“主动内部关节提升轮式平台通过能力”的动机层面较高相关。
- 但其不作为当前 RL 环境配置主线文献，后续写动机与结构价值时再重点回看。

下一步：
- 继续把阅读重点收敛到 RL 环境配置相关文献上。


## 2026-03-23

已完成：
- 读取仓库启动上下文，确认当前文献工作应优先围绕 RL 环境与训练设计主线展开。
- 检查 `docs/literature/` 目录、文献目录索引和 `rl_env_reading_notes.md`。
- 按“直接涉及 RL 训练/策略设计”的标准，从现有文献中筛出 17 篇相关 PDF。
- 新建 `docs/literature/rl_training_strategy_pdfs_2026-03-23/`，并将筛选出的 PDF 复制到该目录中，便于后续集中阅读。

修改文件：
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前独立整理出的 RL 训练策略相关 PDF 目录为 `docs/literature/rl_training_strategy_pdfs_2026-03-23/`。
- 该目录当前包含 17 篇文献，覆盖 rough terrain vehicle、articulated robot、curriculum、sim-to-real、state estimator joint training 等主题。

下一步：
- 若需要进一步收敛，可在这 17 篇中再细分出“最贴近本课题完整车 RL baseline”的高优先级子集。

已完成：
- 将本轮讨论确定的两阶段 RL 训练主线写入项目记忆文件。
- 更新 `docs/current_status.md`，把旧的“速度跟踪/平地加入球铰”表述替换为新的两阶段目标。
- 更新 `docs/conversation_history.md`，固化阶段 1 与阶段 2 的职责边界、任务定义和研究含义。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 阶段 1 正式定义为“平地 + 本体感知 + 固定球铰 + 目标导向移动”。
- 阶段 2 正式定义为“球铰纳入控制 + 底层 PID 与逆运动学映射 + 多样地形 + 外部感知与本体感知融合”。

下一步：
- 按新的阶段 1 目标，重写 env 的 observation、reward、termination、reset 与目标采样逻辑。

已完成：
- 将当前项目工作区整理后准备同步到 GitHub 远端 `origin/main`。

修改文件：
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前本地仓库状态已与待推送内容对齐，准备作为最新项目快照上传到 GitHub。

## 2026-03-24

已完成：
- 优化了根目录 `IK_iteration.mlx` 的符号推导脚本。
- 为 `R01`、`u_i`、`R_local`、`R_w`、`w_i`、`R03`、`R_rpy`、`R_v`、`v_i`、约束方程、半角代换结果、分子分母、多项式以及 `A/B/C` 系数补充了命令行输出。
- 为关键表达式统一增加 `expand + simplify` 化简流程，便于将移相三角表达式尽量压缩为更标准的 `sin/cos` 形式后再核对文献公式。
- 重新打包生成更新后的 `IK_iteration.mlx`。

修改文件：
- `IK_iteration.mlx`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 live script 在每一步关键推导后都会显示结果，更适合逐步检查逆运动学推导链路。
- 当前脚本会先做展开再做符号化简，表达式可读性比原版更高。

下一步：
- 在 MATLAB 中实际运行 `IK_iteration.mlx`，确认本机符号工具箱对 `simplify(..., ''Steps'', 100, ''IgnoreAnalyticConstraints'', true)` 的输出形式满足预期。

## 2026-03-26

已完成：
- 对比 `USD/complete_car.usd` 与 `USD/complete_car_equivlent.usd` 的机器人本体层级和关节树。
- 新增 `scripts/isaac_sim/align_complete_car_structure_to_equivalent.py`，用于按 equivalent 主链清理 `complete_car.usd` 机器人子树。
- 按用户要求，仅在 `/World/complete_car_final` 及其 `joints/` 范围内执行结构树收敛。
- 删除了 12 个多余的 SPM 腿部刚体：
  - `spm1_leg1_proximal`、`spm1_leg1_distal`、`spm1_leg2_proximal`、`spm1_leg2_distal`、`spm1_leg3_proximal`、`spm1_leg3_distal`
  - `spm2_leg1_proximal`、`spm2_leg1_distal`、`spm2_leg2_proximal`、`spm2_leg2_distal`、`spm2_leg3_proximal`、`spm2_leg3_distal`
- 删除了 `joints/` 下对应的 12 个 fixed joint，使保留链路收敛为 `base -> virtual_z -> virtual_y -> platform`。
- 生成编辑前备份 `USD/complete_car.usd.spm_leg_cleanup.bak`。
- 复查修改结果，确认 `/World/complete_car_final` 下已不再包含上述腿部刚体，`joints/` 下也只保留 equivalent 主链所需关节。

修改文件：
- `USD/complete_car.usd`
- `USD/complete_car.usd.spm_leg_cleanup.bak`
- `scripts/isaac_sim/align_complete_car_structure_to_equivalent.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `complete_car.usd` 的机器人本体结构树已按 equivalent 主链收敛，不再保留多余的 SPM 腿部层级。
- 这一步只处理机器人本体层级，不涉及场景层 `/Environment`、`/Render`、`/physicsScene` 以及根级 `/visuals`、`/colliders`、`/meshes`。
- 当前资产仍存在未解决问题，包括轮子零速 drive、损坏的 visual 引用、远端 `Example_Rotary` 引用和内嵌 `PhysicsScene` 风险。

下一步：
- 在新的结构树基础上继续清理 `complete_car.usd` 的 drive、损坏引用与 replicated 不兼容项，再重新验证 `Play` 时是否仍出现 transform 爆炸。

已完成：
- 新增 `scripts/isaac_sim/add_wheel_friction_material.py`，用于给 `complete_car.usd` 的 6 个轮子 collision 子树统一绑定 physics material。
- 在 `USD/complete_car.usd` 中新增共享材质 `/World/complete_car_final/Looks/wheel_physics_material`。
- 将该材质参数设置为：`staticFriction=1.0`、`dynamicFriction=1.0`、`frictionCombineMode=multiply`。
- 将该材质绑定到 6 个轮子的 `collisions` 子树。
- 生成编辑前备份 `USD/complete_car.usd.wheel_friction.bak`。
- 复查确认材质属性和 6 个 wheel collision 绑定均已写入 USD。

修改文件：
- `USD/complete_car.usd`
- `USD/complete_car.usd.wheel_friction.bak`
- `scripts/isaac_sim/add_wheel_friction_material.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `complete_car.usd` 的 6 个轮子已不再依赖默认地面摩擦，而是显式使用统一的轮胎 physics material。
- 这一步只增加轮子接触摩擦参数，不处理轮子 drive、visual 引用错误、远端 `Example_Rotary` 引用和 `PhysicsScene` 风险。

已完成：
- 将 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 从原始关节直控脚本改为第一版 Isaac Sim IK 键控验证脚本。
- 将键盘控制对象从“6 个球铰关节角”改为“前后两个平台目标姿态”。
- 接入 `IK_3RRR_Spherical`，实现每帧根据目标姿态解算前后两组 3 电机角，并映射到 6 个球铰关节目标。
- 保留轮子速度控制，并增加周期性调试输出：`rpy_des / q_ik / q_sim / residual`。
- 将资产路径切换到 `USD/complete_car.usd`，机器人根路径切换到 `/World/complete_car_final`。
- 对更新后的脚本执行了 `python3 -m py_compile` 语法检查，结果通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已有一个可用于“姿态目标 -> IK -> 球铰目标 -> Isaac Sim 读回对比”的第一版键控验证脚本。
- 当前脚本仍使用第一轮假设的 `IK -> sim joint` 顺序、`signs` 和 `biases`，后续需要结合实际运动方向做标定。

已完成：
- 为 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 增加 CSV 日志功能。
- 新增日志目录 `results/ik_keyboard_logs/`，脚本启动时会自动创建时间戳日志文件。
- 日志内容包含 `rpy_des`、`q_ik`、`q_sim`、前后球铰残差以及 `ik_error` 字段，并在每次快照打印时同步落盘。
- 在终端调试输出中增加 `log_path` 字段，便于定位本次运行对应的日志文件。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 IK 键控验证脚本除终端快照外，还能把关键结果稳定保存到 CSV，便于后续直接读取和复盘。

## 2026-03-26

已完成：
- 重新梳理了 `test_ik_keyboard.py` 的验证目标，确认用户当前需要的是“静态几何一致性验证”，而不是“姿态命令下发后由 drive 跟踪”的控制执行验证。
- 将 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 改为新的静态一致性验证逻辑：
  - 键盘直接摆动 6 个球铰等效关节角
  - 每帧读取前后 platform 相对各自 base 的当前姿态
  - 将当前姿态送入 `IK_3RRR_Spherical`
  - 将 IK 预测关节角与 Isaac Sim 当前实际关节角直接对比
- 在脚本中新增前后 `base/platform` prim 路径读取、相对旋转矩阵提取，以及 `Rz(yaw) @ Ry(pitch) @ Rx(roll)` 对应的 ZYX 欧拉角反解。
- 保留并适配了 CSV 日志落盘，日志现记录当前平台姿态、手动关节命令、IK 预测关节角、Isaac Sim 实际关节角、残差和 `ik_error`。
- 对修改后的脚本执行了 `python3 -m py_compile` 语法检查，结果通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- `test_ik_keyboard.py` 不再把 IK 输出回写给 Isaac Sim 关节执行，而是作为“当前姿态 -> IK 预测关节角”的几何一致性验证脚本使用。
- 之后读取日志时，应把 `q_ik` 与 `q_sim` 的差异理解为静态映射误差、坐标定义误差、零位/符号/偏置标定误差，而不再理解为 drive 跟踪误差。

下一步：
- 运行新的 `test_ik_keyboard.py`，分别做前球铰和后球铰的单轴扫描，进一步标定 `IK_SIGNS_*`、关节顺序和偏置。
## 2026-03-27

已完成：
- 读取并分析了 `results/ik_keyboard_logs/ik_keyboard_2026-03-27_09-58-33.csv`。
- 统计确认该日志共 160 条采样，`ik_error` 全程为空，6 个 residual 全为 `0.0`。
- 统计确认 `joint_cmd` 与 `q_sim` 的误差整体较小，说明 Isaac Sim 关节执行跟踪基本正常。
- 统计确认 `q_ik` 与 `q_sim` 长期存在几十度级系统偏差，前后球铰都存在，且并非只出现在瞬态阶段。
- 结合 `test_ik_keyboard.py` 与 `IK_model.py` 的当前实现，确认本轮主要问题是 IK 比较链路中的零位/分支/映射定义未与仿真关节约定对齐，而不是 IK 方程求解失败。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 IK 键盘验证脚本的 residual 为 0，只能说明“给定姿态存在一组数学合法解”，不能说明“该解已映射回 Isaac Sim 当前实际关节分支”。
- 后续应优先标定零命令姿态下的球铰零位、分支选择和 `signs/biases`，再继续用该脚本做一致性验证。

下一步：
- 在 `test_ik_keyboard.py` 中把当前零命令姿态作为映射基准重新标定，并验证 `read_relative_rpy -> IK -> map_to_sim_joints -> q_sim` 是否能闭合。
已完成：
- 直接检查 `USD/complete_car.usd` 的 SPM 主链层级，确认零位姿态偏置固定存在于 `spm*_base -> spm*_spherical_virtual_z` 之间。
- 在 `USD/complete_car.usd` 中新增 `/World/complete_car_final/spm1_base/spm1_base_ref` 与 `/World/complete_car_final/spm2_base/spm2_base_ref`。
- 新增脚本 `scripts/isaac_sim/add_spm_base_reference_frames.py`，用于为当前 complete car 资产补写上述两个参考系，并自动生成 `USD/complete_car.usd.base_ref.bak` 备份。
- 重新打开 stage 验证新增 prim 后，确认 `spm1_base_ref -> spm1_platform` 与 `spm2_base_ref -> spm2_platform` 的相对 ZYX `rpy` 均已接近零。

修改文件：
- `USD/complete_car.usd`
- `scripts/isaac_sim/add_spm_base_reference_frames.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 USD 已具备两个固定在 base 上、且在机械零位与 platform 轴方向对齐的姿态参考系，可作为后续平台 `rpy` 读取的正确起点。
- 后续 `test_ik_keyboard.py` 应切换到 `spm*_base_ref -> spm*_platform` 读取零位姿态，而不应继续直接使用 `spm*_base -> spm*_platform`。

下一步：
- 在 `test_ik_keyboard.py` 中改用 `spm*_base_ref` 作为姿态参考 frame，并重新验证零位 `rpy` 与 IK 输入链路。
已完成：
- 将 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 的平台姿态读取基准从 `spm*_base -> spm*_platform` 改为 `spm*_base_ref -> spm*_platform`。
- 保留原有 `Rz(yaw) -> Ry(pitch) -> Rx(roll)` 的 ZYX 欧拉角分解与 IK 求解逻辑，仅替换姿态参考 frame。
- 对修改后的脚本执行 `python3 -m py_compile`，语法检查通过。
- 使用与脚本一致的读取公式重新检查机械零位，确认前球铰 `rpy≈[5.493e-06, 6.94e-07, -2.571e-06] deg`、后球铰 `rpy≈[-1.4661e-05, -1.3655e-05, 4.951e-06] deg`，可视为零。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 IK 静态验证脚本的 `rpy` 输入参考系已与 USD 中补入的零位参考 frame 对齐。
- 后续若 `q_ik` 与 `q_sim` 仍不一致，应优先继续检查 `IK_model.py` 输出到仿真关节的零位、分支与符号/偏置映射，而不是继续怀疑平台姿态读取坐标系。

下一步：
- 在已对齐的姿态输入前提下，继续标定 `IK_SIGNS_FRONT/REAR`、`IK_BIASES_FRONT/REAR` 与分支初值。
已完成：
- 在 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 中加入启动零偏标定逻辑。
- 脚本启动后会先对 6 个球铰保持零目标、对 6 个轮子保持零轮速，先静置 `240` 步，再连续采样 `120` 步，对前后 `spm*_base_ref -> spm*_platform` 的原始 `rpy` 求均值作为 `rpy_bias`。
- 后续 IK 输入改为 `raw_rpy - rpy_bias`，不再直接使用原始相对姿态。
- CSV 日志新增 `raw / bias / corrected` 三组平台 `rpy` 字段，便于区分物理稳态偏置与送入 IK 的校正姿态。
- 对修改后的脚本执行 `python3 -m py_compile`，语法检查通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 IK 键控验证脚本已具备启动零偏标定能力，可直接用新日志判断“原始平台姿态偏置”和“校正后送入 IK 的姿态”是否分离成功。

下一步：
- 重新运行脚本生成新日志，先检查 `front/rear_*_cur_deg` 是否在零命令稳态下接近 0，再继续分析 `q_ik` 与 `q_sim` 的剩余差异。
已完成：
- 读取并分析 `results/ik_keyboard_logs/ik_keyboard_2026-03-27_17-20-44.csv`，验证加入启动零偏标定后的新日志格式。
- 统计确认零命令稳态下，平台原始姿态 `raw_rpy` 仍存在小幅物理偏置，但校正后 `corrected_rpy` 已明显逼近零。
- 前平台 `corrected_rpy` 均值约为 `[0.013734, -0.010834, -0.00631] deg`，后平台约为 `[-0.001878, 0.000419, 0.003239] deg`。
- 同时确认 `q_ik` 与 `q_sim` 在零命令稳态下仍有系统差异，说明当前主问题已从姿态读取收敛到关节映射标定。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 启动零偏标定已基本解决“平台 `rpy` 输入不为零”的问题，后续应优先继续标定 `IK_SIGNS_*`、`IK_BIASES_*` 与分支初值。

下一步：
- 在零偏校正保持不变的前提下，针对前后球铰分别做单轴扫描，继续拟合 `q_ik -> q_sim` 的零位、符号和偏置。
已完成：
- 重写 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`，将其从“关节直控 + 反算对照”脚本改为“姿态目标 -> IK -> joint target -> articulation controller 跟踪”验证脚本。
- 键盘输入现直接修改前后平台的 `roll/pitch/yaw` 目标，不再直接修改 6 个球铰关节角。
- 启动阶段新增联合零位标定：同时估计平台 `rpy` 零偏和 Sim 当前球铰关节零位，并将后者作为 `map_to_sim_joints()` 的零位偏置。
- 控制链中新增两级一阶平滑：先对姿态目标做平滑，再对 IK 生成的 joint target 做平滑，最后再把 `q_cmd` 发送给 articulation controller。
- 日志字段改为完整记录 `raw/meas/des/cmd` 姿态、`q_ik/q_cmd/q_sim`、joint 跟踪误差以及 IK residual。
- 对重写后的脚本执行 `python3 -m py_compile`，语法检查通过。

修改文件：
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 `test_ik_keyboard.py` 已能直接验证三个关键问题：姿态目标是否稳定送进 IK、IK 生成的 joint target 是否和零位标定一致、articulation controller 是否能平滑跟踪 joint target。

下一步：
- 实际运行新脚本并读取新日志，检查 `rpy_des -> rpy_meas`、`q_cmd -> q_sim` 和 `track_err` 三条误差曲线，再决定是否需要继续调 `IK_SIGNS_*`、姿态/关节平滑系数或底层 drive 参数。
已完成：
- 读取并分析 `results/ik_keyboard_logs/ik_keyboard_2026-03-27_18-53-34.csv`，评估重构后 `test_ik_keyboard.py` 的整条控制链。
- 确认 `q_cmd -> q_sim` 跟踪效果较好，前后球铰关节平均绝对跟踪误差均在约 `0.02~0.07 deg` 量级，说明 articulation controller 可以平滑跟踪 joint target。
- 确认 IK 全程可解，`residual` 为 0，`ik_error` 为空。
- 同时确认 `rpy_cmd -> rpy_meas` 误差很大，前平台平均绝对误差约 `[5.62, 4.69, 4.71] deg`，后平台约 `[2.42, 0.50, 2.20] deg`，且单轴姿态命令会激发错误轴或相反方向。
- 据此得出当前关键结论：问题不在关节跟踪，而在“IK 电机角”和“USD 等效球铰关节坐标”不是同一组坐标，无法直接把 IK 输出当作现有等效模型的关节目标。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 现阶段已验证：IK 可稳定求解，joint target 可被底层平滑跟踪；但姿态目标通过 IK 直接驱动当前等效球铰模型这条路线在语义上不成立。

下一步：
- 回到研究层重新决定架构：是保留等效球铰姿态控制并让 IK 仅作为真实电机角映射层，还是重建一个真实电机坐标可控的下层模型。
已完成：
- 明确了当前仿真建模的语义：USD 中 3 个等效球铰关节角本身就是移动平台姿态坐标，而不是 3-RRR 真实电机角代理。
- 因此重新界定 RL 与 IK 的角色分工：RL 在仿真中应直接控制等效球铰姿态角；IK 只负责把平台姿态并行映射为真实机构电机角，供后续可能的实物阶段使用。
- 据此停止继续沿“IK 电机角直接驱动当前等效球铰模型”这条路线投入。

修改文件：
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前 RL 主线重新收敛为：直接控制 3 个等效球铰姿态角和轮子动作；IK 暂不进入仿真闭环控制。

下一步：
- 回到 RL 环境设计与实现，明确动作空间、观测和奖励如何围绕等效球铰姿态控制来组织。

## 2026-03-28

已完成：
- 按 `literature-reading-notes` 的结构化方式整理 `Ha 等 - 2025 - Learning-based legged locomotion: State of the art and future perspectives`。
- 基于原始 PDF 提炼出该综述的整体逻辑、`MDP` 组成、训练框架、`sim-to-real` 路线以及 `control + learning` 组合方式。
- 将阅读笔记落盘到对应文献目录下，保持与现有 `Wiberg 2022`、`Xu 2024` 笔记一致的仓库组织方式。
- 同步更新项目状态与长期会话记忆，避免后续重复整理该综述。

修改文件：
- `docs/literature/mineru_output/Ha 等 - 2025 - Learning-based legged locomotion State of the art and future perspectives/auto/reading_notes.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`

产出/结论：
- 当前已形成一份可直接复用的综述型阅读笔记，重点不是复述全文，而是为本课题提炼任务设计与训练组织方法。
- 该综述支持当前已确定的两阶段主线：先做最小可训练 baseline，再逐步加入外感知、分层控制和更强的 sim-to-real 机制。

下一步：
- 若继续沿文献主线推进，可把 `Ha 2025` 与 `Wiberg 2022`、`Xu 2024` 做一次横向对比，专门整理“baseline 如何定义、复杂度如何分阶段引入”的共性结论。
