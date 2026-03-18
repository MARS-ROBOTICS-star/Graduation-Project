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
