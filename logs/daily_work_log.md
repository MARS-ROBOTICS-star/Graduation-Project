# 每日工作日志

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
