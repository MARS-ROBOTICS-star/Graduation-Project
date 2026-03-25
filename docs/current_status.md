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
- 已建立 `docs/literature/` 的 PDF + Markdown 并存工作流，并新增 MinerU 批量转换脚本与文献目录索引。
- 已新增 `docs/literature/rl_env_reading_notes.md`，整理 RL 环境配置相关文献的推荐阅读顺序与理由，作为后续持续维护的文献阅读笔记。
- 已完成 `Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning.pdf` 的单篇 MinerU 转换，并补充面向本课题的精读结论。
- 已在 `AGENTS.md` 中固化文献阅读交互协议：先确认阅读目标，再按文章写作顺序以“是什么 -> 为什么 -> 联想与反思”提问，并允许围绕同一问题做二次追问直到真正理解。
- 已在该文献对应目录下新增 `reading_notes.md`，整理本轮围绕 observation / action / reward / termination / curriculum 的问答式阅读笔记。
- 已完成 `Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain.pdf` 的单篇 MinerU 转换，并在对应目录下新增 `reading_notes.md`，整理其 RL 环境设计精读笔记。
- 已优化根目录 `IK_iteration.mlx`：关键中间结果现可逐步打印到命令行窗口，并统一增加符号化简流程，便于核对逆运动学推导。
- 已按“RL 训练策略相关”主题，从 `docs/literature/` 中单独整理出一份 PDF 集合到 `docs/literature/rl_training_strategy_pdfs_2026-03-23/`，便于集中查阅。
- 当前工作区已整理完毕，待同步到 GitHub `origin/main` 作为最新远端状态。

## 正在进行
- 根据新的两阶段主线，收敛第 1 阶段 baseline 定义：平地、本体感知、固定球铰、目标导向移动，仅控制 6 个轮子速度。
- 按“整体掌握文章内容与逻辑为主，RL 环境设计提炼为辅”的目标继续精读 `Wiberg 等 - 2022`，为后续 env 设计吸收可迁移部分。
- 清理 `USD/complete_car.usd` 中剩余的外部引用与不适合多环境复制的内容。
- 调整 `root_too_low`、初始高度、reset 范围和奖励权重，提升 rollout 存活时间和训练有效性。

## 当前阻塞点
- 当前环境代码仍保留 12 维“轮子 + 球铰”联合控制原型，与最新确定的第 1 阶段默认路线不完全一致，后续需要按主线收敛。
- 当前训练中 `Episode_Termination/root_too_low` 长时间为 `1.0`，episode 长度过短，说明虽然能训练，但环境健康度不足。
- `complete_car.usd` 仍存在离线不可解析或不利于 replicated RL 的残留内容，例如外部引用和内嵌 `PhysicsScene` 风险。
- 当前终端会话下 CUDA / NVIDIA driver 不可用，GPU 训练暂不能作为默认路径。

## 下一步优先事项
- 先按第 1 阶段主线收敛 baseline：平地、目标导向移动、本体感知、固定球铰，仅保留 6 维轮速动作。
- 将 reward、termination、reset 与目标采样方式统一改写为“目标导向移动”任务，而不是继续沿用速度跟踪思路。
- 清理 `USD/complete_car.usd` 的远端依赖和 replicated 不兼容项。
- 基于现有训练日志调节终止阈值、初始姿态和奖励权重，把 episode 从“几乎必然早终止”修到可持续 rollout。
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
  - `cd /home/ubuntu/Graduation-Project/src/rl_lab/complete_car_rl_training`
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
- `docs/literature/catalog.md`
- `docs/literature/rl_env_reading_notes.md`
- `docs/literature/mineru_output/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning/auto/reading_notes.md`
- `docs/literature/mineru_output/Xu 等 - 2024 - Reinforcement learning for wheeled mobility on vertically challenging terrain/auto/reading_notes.md`
- `scripts/literature/mineru_batch_convert.sh`
- `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `src/rl_lab/complete_car_rl_training/scripts/tensorboard_export.py`
- `src/rl_lab/complete_car_rl_training/skills/isaac-rl-run-diagnosis/SKILL.md`
