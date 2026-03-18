# 当前状态

## 已完成
- 已安装 Isaac Sim 5.1。
- 已确认将 Isaac Lab 作为 RL 主开发框架。
- 已将两个球面并联机构等效简化为两个 3-DOF 串联球铰。
- 已完成部分基础关节与驱动配置。
- 已确认导师要求优先尽快跑通 RL 基线。
- 已删除仓库内手写的 direct task 骨架，仅保留 `src/rl_lab/complete_car_rl_training/` 模板 project。
- 已新增 `docs/isaaclab模板使用指南.md`，整理模板使用方法、命令和改造位置。
- 已在 `complete_car_rl_training_env_cfg.py` 中完成完整车 manager-based 环境首版替换。
- 已接入完整车 `ArticulationCfg`、12 关节 actuator 分组、12 维动作空间和完整车 reset/reward/termination 首版配置。
- 已加入 `UniformVelocityCommandCfg`，支持基于速度指令的前进/后退训练设计。
- 已删除 RL scene 中重复定义的 `ground` 与 `dome_light`，当前默认使用 `complete_car.usd` 内已包含的场景元素。
- 已将 PPO `experiment_name` 从模板默认值改为 `complete_car_rl_training`。
- 已在 `AGENTS.md` 中补充“第一性原理”和“方案规范”协作约束。
- 已将 `src/rl_lab/complete_car_rl_training/` 从模板壳结构整理为单层训练项目结构。
- 已删除嵌套 `.git`、`.vscode`、UI 示例和旧 `src/rl_lab/tasks/` 残留。
- 已将训练项目安装路径统一为项目根 `pip install -e .`。
- 已确认实际 Gym 任务 ID 为 `Complete-Car-Rl-Training-v0`，不是带下划线的旧写法。
- 已在 CPU 模式下实际跑通 `reset -> step -> train` 链路，`100` 个环境可创建并进入 RSL-RL 学习循环。
- 已修正 `scripts/rsl_rl/train.py`，传入 `--device` 时会同时覆盖环境与 runner 的 device，避免环境走 CPU 而策略网络仍错误落到 CUDA。
- 已产出第一次训练日志与 checkpoint：`src/rl_lab/complete_car_rl_training/logs/rsl_rl/complete_car_rl_training/2026-03-18_17-14-07/`，其中已生成 `model_0.pt` 与 `model_50.pt`。

## 当前目标
- 基于保留的 Isaac Lab 模板 project 构建最小可训练完整车 RL 环境。
- 先得到第一个可运行、可训练、可展示的姿态与前进/后退联合控制策略。

## 当前阻塞项
- 当前终端会话下 CUDA/NVIDIA driver 不可用，默认 GPU 训练无法直接启动，只能先用 `--device cpu` 验证训练链路。
- `complete_car.usd` 仍包含离线环境无法解析的外部引用：
  - `defaultGroundPlane -> default_environment.usd`
  - `Example_Rotary -> Example_Rotary.usda`
- `complete_car.usd` 内仍带有 `PhysicsScene`，在多环境复制时触发 `Replication of this type is not supported`，说明资产内嵌物理场景不适合作为 replicated robot asset。
- 当前训练中 `Episode_Termination/root_too_low` 长时间为 `1.0`，平均 episode length 约 `12.3`，说明虽然能训练，但任务几乎始终以车体过低终止。
- 当前环境配置尚未结合真实训练表现调参，轮子 actuator 参数、奖励权重、root height 阈值和 reset 范围仍需迭代。

## 立即下一步
- 从 `USD/complete_car.usd` 中移除或重定向外部联网引用，确保离线环境下不再访问远端资产。
- 清理资产内嵌 `PhysicsScene`，使机器人 USD 可被 Isaac Lab 多环境复制而不报 replication error。
- 基于当前日志调节 `root_too_low` 阈值、初始高度、reset 范围与奖励权重，先把 episode 从“几乎必然落地终止”修到可持续 rollout。
- 若需要继续在当前终端会话运行，默认使用：
  - `env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV /home/ubuntu/IsaacLab/isaaclab.sh -p scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --num_envs 100 --headless --device cpu`
