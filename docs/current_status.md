# 当前状态

## 当前总目标
- 在 Isaac Lab 中构建可稳定训练、可控、可复现的三节完整车 RL 两阶段主线。
- 第一阶段先完成“平地 + 本体感知 + 固定球铰 + 目标导向移动” baseline。
- 第二阶段再完成“球铰纳入控制 + 底层 PID 与逆运动学映射 + 多样地形 + 外部感知与本体感知融合”的增强任务。

## 当前阶段
- 阶段 0 已完成：`reset -> step -> reward -> termination -> train` 闭环已实际跑通。
- 阶段 1 进行中：平地、本体感知、固定球铰、目标导向移动 baseline 的任务定义收敛与训练稳定性提升。

## 已完成
- 已确认导师要求：优先尽快跑通 RL 基线，而不是先追求完整机构机理、感知或复杂地形。
- 已将完整车训练工作区收敛到 `src/rl_lab/complete_car_rl_training/` 单一项目。
- 已完成 manager-based 环境首版替换，接入完整车 `ArticulationCfg`、动作、观测、reward、termination 与 PPO 配置。
- 已确认实际 Gym 任务 ID 为 `Complete-Car-Rl-Training-v0`。
- 已在当前 `env_isaacLab` 环境中通过 `python scripts/...` 直接启动训练项目。
- 已在 CPU 模式下实际跑通训练链路并生成首批日志与 checkpoint。
- 已新增训练后 TensorBoard 标量自动导出能力，每次 run 结束后会在对应 run 目录下生成 `tensorboard_export/`，便于离线查看和后续分析。
- 已补充 `docs/tensorboard_reading_guide.md`，统一说明 TensorBoard 读图方法、核心指标含义和标准诊断顺序。
- 已新增 `isaac-rl-run-diagnosis` skill 定义，并安装到 `~/.codex/skills/`，用于“给日志路径 -> 自动定位 run -> 导出并解读训练结果”。
- 已明确 scene cfg 与机器人 USD 的职责边界：地面和灯光归 scene cfg，机器人 USD 只保留 articulation 本体与必要挂载。
- 已在 `AGENTS.md` 中固化 RL 训练主线：先最小可训练系统，再逐步加入球铰、运动学、地形和感知。
- 已建立 `docs/literature/` 的 PDF + Markdown 并存工作流，并新增 MinerU 批量转换脚本与单篇文献 `reading_notes.md` 沉淀方式。
- 已将根目录 `literature_note_skill.md` 整理并安装为可发现的本地 Codex skill：`~/.codex/skills/literature-reading-notes/`，用于将论文 PDF / 章节 / 段落 / 截图转成结构化文献阅读笔记。
- 已完成 `Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning.pdf` 的单篇 MinerU 转换，并补充面向本课题的精读结论。
- 已在 `AGENTS.md` 中固化文献阅读交互协议：先确认阅读目标，再按文章写作顺序以“是什么 -> 为什么 -> 联想与反思”提问，并允许围绕同一问题做二次追问直到真正理解。
- 已在该文献对应目录下新增 `reading_notes.md`，整理本轮围绕 observation / action / reward / termination / curriculum 的问答式阅读笔记。
- 已完成 `Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain.pdf` 的单篇 MinerU 转换，并在对应目录下新增 `reading_notes.md`，整理其 RL 环境设计精读笔记。
- 已基于原始 PDF 完成 `Ha 等 - 2025 - Learning-based legged locomotion State of the art and future perspectives` 的首轮结构化阅读笔记，重点梳理全文逻辑、`MDP` 组成、常见学习框架、`sim-to-real` 路线以及对本课题两阶段主线的可迁移启发。
- 已按 `literature-reading-notes` skill 重写 `Ha 等 - 2025 - Learning-based legged locomotion State of the art and future perspectives` 的阅读笔记，补齐 `Paper Snapshot`、全文结构、mind map、分章节精读、术语表、重要参考文献与可复用 related-work 段落。
- 已将上述 `Ha 等 - 2025` 阅读笔记进一步改写为“摘录式整理”版本：重点围绕正文关键内容、概念定义、使用方式、作者引用的相关工作及其完整参考文献信息，不再夹带与当前课题绑定的迁移分析。
- 已按用户给出的示例格式再次重写 `Ha 等 - 2025` 阅读笔记：结构严格对齐 `Paper Snapshot -> 全文结构 -> Mind Map -> 章节精读笔记 -> 关键知识点 -> 术语表 -> 重要参考文献 -> 可复用综述段落`，其中 `Observation` 章节改为“核心观点 / 本节作用 / 分段摘录整理 / 完整参考文献”风格。
- 已优化根目录 `IK_iteration.mlx`：关键中间结果现可逐步打印到命令行窗口，并统一增加符号化简流程，便于核对逆运动学推导。
- 已按“RL 训练策略相关”主题，从 `docs/literature/` 中单独整理出一份 PDF 集合到 `docs/literature/rl_training_strategy_pdfs_2026-03-23/`，便于集中查阅。
- 当前工作区已整理完毕，并已同步到 GitHub `origin/main` 作为当前远端状态。
- 已新增 `docs/project_file_map.md`，按“RL 主线 / 资产与仿真 / 文献 / 论文 / 推导与配图 / 结果输出”归纳整个仓库文件职责，并重写根 `README.md` 使其与当前主线一致。
- 已将 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 改为当前版 Isaac Sim IK 静态一致性验证脚本：键盘直接摆动 6 个球铰关节，脚本每帧读取前后平台相对 base 的当前姿态，经 IK 反算得到预测关节角，再与 Isaac Sim 当前实际关节角直接对比。
- 上述 IK 验证脚本已增加 CSV 日志落盘，默认输出到 `results/ik_keyboard_logs/`，可同时记录当前平台姿态、手动关节命令、IK 预测关节角、Isaac Sim 实际关节角、残差以及 `ik_error`，便于后续直接读取和分析。
- 已按 `USD/complete_car_equivlent.usd` 的机器人本体层级，清理 `USD/complete_car.usd` 中 `/World/complete_car_final` 下多余的 12 个 SPM 腿部刚体及 `joints/` 下对应 12 个 fixed joint，并保留独立备份 `USD/complete_car.usd.spm_leg_cleanup.bak`。
- 已为 `complete_car.usd` 的 6 个轮子 collision 子树绑定共享 physics material：`staticFriction=1.0`、`dynamicFriction=1.0`、`frictionCombineMode=multiply`，并保留备份 `USD/complete_car.usd.wheel_friction.bak`。
- 已对 `results/ik_keyboard_logs/ik_keyboard_2026-03-27_09-58-33.csv` 完成首轮诊断：160 条采样中 `ik_error` 全程为空、6 个 residual 全为 0，说明 IK 方程本身始终可解；但 `q_ik` 与 `q_sim` 长期存在几十度级系统偏差，而 `joint_cmd` 与 `q_sim` 误差整体仍较小，说明当前问题不在关节执行跟踪，而在 IK 比较链路的零位/分支/映射定义。
- 已在 `USD/complete_car.usd` 中补入 `/World/complete_car_final/spm1_base/spm1_base_ref` 与 `/World/complete_car_final/spm2_base/spm2_base_ref`：二者固定挂在各自 `spm*_base` 下，局部姿态按当前零位 `spm*_spherical_virtual_z` 作者化；重新打开 stage 后验证 `base_ref -> platform` 的相对 `rpy` 已接近 `(0, 0, 0)`。
- 已将 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 的平台姿态读取基准切换为 `spm*_base_ref -> spm*_platform`，并按脚本同样的 ZYX 公式复核机械零位：前球铰 `rpy≈[5.493e-06, 6.94e-07, -2.571e-06] deg`，后球铰 `rpy≈[-1.4661e-05, -1.3655e-05, 4.951e-06] deg`，可视为零。
- 已在 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 中加入启动零偏标定：脚本启动后先以零轮速、零球铰目标静置并采样 `base_ref -> platform` 的原始 `rpy`，求均值作为前后平台 `rpy_bias`，后续统一用 `raw_rpy - rpy_bias` 作为送入 IK 和写入主日志的校正姿态；CSV 现同时记录 `raw / bias / corrected` 三组 `rpy`。
- 已将 `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` 重构为“姿态目标 -> IK -> joint target -> articulation controller 跟踪”验证脚本：键盘不再直接改球铰关节角，而是直接调整前后平台目标 `rpy`；脚本启动时同时标定平台 `rpy` 零偏和 Sim 关节零位，然后以校正后的姿态目标送入 IK，得到 joint target 后再经过一阶平滑发送给 articulation controller，并记录 joint 跟踪误差。
- 已分析 `results/ik_keyboard_logs/ik_keyboard_2026-03-27_18-53-34.csv`：新脚本下 `q_cmd -> q_sim` 跟踪已经较好，前球铰 3 轴平均绝对跟踪误差约 `[0.065, 0.049, 0.038] deg`，后球铰约 `[0.041, 0.021, 0.024] deg`，说明 articulation controller 可以平滑跟踪 joint target；但 `rpy_cmd -> rpy_meas` 明显不成立，前平台姿态平均绝对误差约 `[5.62, 4.69, 4.71] deg`，后平台约 `[2.42, 0.50, 2.20] deg`，且单轴命令会激发错误轴或相反方向，说明当前把 IK 电机角直接发给 USD 等效球铰关节这条链在语义上不成立。
- 已分析 `results/ik_keyboard_logs/ik_keyboard_2026-03-27_17-20-44.csv`：启动零偏标定后，前平台 `raw_rpy` 均值约 `[-0.0755, 0.0809, -0.0005] deg`、后平台约 `[0.0401, -0.0129, 0.0009] deg`；对应 `corrected_rpy` 均值已压到前 `[0.0137, -0.0108, -0.0063] deg`、后 `[-0.0019, 0.0004, 0.0032] deg`，说明零偏标定已基本生效，但 `q_ik` 与 `q_sim` 仍存在明显系统误差。
- 已按新稿整体替换 `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`：当前版本以“运动学模型”为题，内容覆盖位置/姿态/位姿、旋转矩阵、齐次变换矩阵以及 3-RRR 球面并联机构逆运动学解析求解；同时已在 `main.tex` 补入 `tikz` 与 `arrows.meta` 依赖，并通过两次 `xelatex` 编译验证。
- 已将 `scripts/isaac_sim/control_keyboard.py` 切换到 `USD/complete_car.usd` 与 `/World/complete_car_final`；当前脚本采用 `W/S/A/D/SPACE` 做车轮差速速度控制、数字小键盘 `1-9`、`/`、`*`、`-` 做 6 个球铰自由度正负调节，并对车轮速度与球铰位置命令都加入一阶平滑。
- 已将用户新增的地形预览脚本整理到 `scripts/isaac_sim/terrain_preview/`，当前包含 `mgdp_terrain_preview.py`、`run_terrain_preview.sh` 与说明文档 `README.md`；同时修正了其中仓库根路径解析与 README 中的旧启动路径。
- 已完成地形预览脚本的基础校验：`python3 -m py_compile scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py` 与 `bash -n scripts/isaac_sim/terrain_preview/run_terrain_preview.sh` 均通过。
- 已将地形生成逻辑抽到 `scripts/isaac_sim/terrain_preview/terrain_builder.py`，并让 `scripts/isaac_sim/control_keyboard.py` 支持启动时同步注入单块地形；当前默认地形为 `slope_ramp`，也可通过 `--terrain` 切换为 `stairs_up`、`gap`、`corridor` 等。
- 当前 `control_keyboard.py` 在注入地形时会优先尝试关闭常见默认地面 prim，避免原始 ground 把 `gap` 类地形“垫平”。
- 当前仓库已确认 GitHub 推送阻塞来自 `Drawing/完整小车等效串联.SAT` 超过 100 MB；后续默认将 `.SAT` 文件加入 `.gitignore`，不再直接纳入普通 Git 提交。

## 正在进行
- 根据新的两阶段主线，收敛第 1 阶段 baseline 定义：平地、本体感知、固定球铰、目标导向移动，仅控制 6 个轮子速度。
- 按“整体掌握文章内容与逻辑为主，RL 环境设计提炼为辅”的目标继续精读 `Wiberg 等 - 2022`，为后续 env 设计吸收可迁移部分。
- 清理 `USD/complete_car.usd` 中剩余的外部引用与不适合多环境复制的内容。
- 调整 `root_too_low`、初始高度、reset 范围和奖励权重，提升 rollout 存活时间和训练有效性。

## 当前阻塞点
- 当前环境代码仍保留 12 维“轮子 + 球铰”联合控制原型，与最新确定的第 1 阶段默认路线不完全一致，后续需要按主线收敛。
- 当前训练中 `Episode_Termination/root_too_low` 长时间为 `1.0`，episode 长度过短，说明虽然能训练，但环境健康度不足。
- `complete_car.usd` 仍存在离线不可解析或不利于 replicated RL 的残留内容，例如外部引用和内嵌 `PhysicsScene` 风险。
- 虽然 `complete_car.usd` 的机器人本体树已收敛到 equivalent 主链，但轮子零速 drive、球铰高刚度 drive、损坏的 visual 引用和远端 `Example_Rotary` 引用仍可能导致 `Play` 后数值发散。
- 当前终端会话下 CUDA / NVIDIA driver 不可用，GPU 训练暂不能作为默认路径。
- 当前终端会话下 Isaac Sim 地形预览脚本无法实际拉起：`/home/lbz/isaac-sim/python.sh` 启动时出现 `Vulkan 1.1 is not supported`、`no CUDA-capable device is detected` 与段错误，属于本机图形/驱动环境阻塞，而不是当前地形脚本的 Python 语法或仓库路径问题。
- 当前 GitHub 上传需避免提交 `.SAT` 大文件；如需长期版本化 CAD 原件，应另行采用 Git LFS 或仓库外制品管理，而不是继续走普通 Git push。
- 当前已明确新的默认抽象：USD 中 3 个等效球铰关节的坐标本身就是移动平台姿态坐标，RL 后续应直接控制这 3 个等效关节角；IK 仅作为“平台姿态 -> 真实机构电机角”的并行映射层，用于后续可能的实物阶段，不再作为当前仿真闭环的直接控制输入。

## 下一步优先事项
- 先按第 1 阶段主线收敛 baseline：平地、目标导向移动、本体感知、固定球铰，仅保留 6 维轮速动作。
- 将 reward、termination、reset 与目标采样方式统一改写为“目标导向移动”任务，而不是继续沿用速度跟踪思路。
- 清理 `USD/complete_car.usd` 的远端依赖和 replicated 不兼容项。
- 在已对齐的机器人本体树基础上，继续清理轮子 drive、损坏的 visual 引用、远端 `Example_Rotary` 引用与内嵌 `PhysicsScene`。
- 基于现有训练日志调节终止阈值、初始姿态和奖励权重，把 episode 从“几乎必然早终止”修到可持续 rollout。
- 下一步优先回到 RL 主线：将策略输出和控制接口明确收敛为前后 3 个等效球铰姿态角与 6 个轮子动作，不再继续围绕“用 IK 电机角直接驱动等效球铰”这条路线投入。
- 若需要继续使用地形预览脚本，应在具备可用 Vulkan / CUDA / 显示环境的 Isaac Sim 主机上执行 `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh` 做实际窗口或 headless 验证。
- 若要继续做车体与地形联调，当前默认入口应直接使用 `python3 scripts/isaac_sim/control_keyboard.py --terrain <terrain_name>`，而不是分别手工开两个 Isaac Sim 进程。
- 待第 1 阶段稳定后，再进入第 2 阶段，接入球铰高层控制、底层 PID + 逆运动学、多样地形与外部感知。

## 当前默认方案
- 训练路线默认遵循：
  - 阶段 0：先跑通可训练环境
  - 阶段 1：平地 + 本体感知 + 固定球铰 + 目标导向移动
  - 阶段 2：球铰纳入控制 + 底层 PID 与逆运动学映射 + 多样地形 + 外部感知与本体感知融合
- 第 1 阶段默认采用：
  - 平地
  - 本体状态输入
  - 目标导向移动任务
  - 固定球铰姿态
  - 仅训练 6 个轮子速度控制
- 第 2 阶段默认采用：
  - RL 输出高层轮式推进与球铰目标
  - 底层控制器负责 PID 跟踪与逆运动学映射
  - 先从简单非平地开始，再逐步提高地形复杂度
  - 外部感知先做降维编码，再与本体状态融合后送入策略
- 当前默认启动路径：
  - 激活 `env_isaacLab`
  - `cd /home/lbz/Graduation-Project/src/rl_lab/complete_car_rl_training`
  - 必要时设置 `OMNI_KIT_ACCEPT_EULA=YES`
  - `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --headless --device cpu`
  - 训练完成后优先查看对应 run 目录下的 `tensorboard_export/summary.json`、`latest_values.csv` 和 `scalars/*.csv`

## 关键文件
- `AGENTS.md`
- `docs/current_status.md`
- `docs/conversation_history.md`
- `src/rl_lab/complete_car_rl_training/README.md`
- `src/rl_lab/complete_car_rl_training/docs/tensorboard_reading_guide.md`
- `docs/literature/README.md`
- `docs/project_file_map.md`
- `/home/lbz/.codex/skills/literature-reading-notes/SKILL.md`
- `docs/literature/mineru_output/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning/auto/reading_notes.md`
- `docs/literature/mineru_output/Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain/auto/reading_notes.md`
- `docs/literature/mineru_output/Ha 等 - 2025 - Learning-based legged locomotion State of the art and future perspectives/auto/reading_notes.md`
- `scripts/literature/mineru_batch_convert.sh`
- `scripts/isaac_sim/control_keyboard.py`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/scripts/tensorboard_export.py`
- `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`
- `src/rl_lab/complete_car_rl_training/skills/isaac-rl-run-diagnosis/SKILL.md`
- `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
