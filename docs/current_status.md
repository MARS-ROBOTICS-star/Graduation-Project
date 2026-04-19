# 当前状态

## 当前总目标
- 将 `RL_Training/` 下的 Stage0 固化为一条可复现、可解释、训练链稳定的平地主线 baseline。
- 当前优先级不是继续盲目长训，而是先把 Stage0 的有效动作语义、奖励导向和日志判读口径收敛到一致。

## 当前阶段
- 当前处于：
  - Stage0 bounded policy 首轮 run 验证完成后的行为质量诊断阶段
- 当前工作重点是：
  - 区分“动作链问题已解决”与“任务行为质量仍然不好”这两层问题
  - 识别当前 Stage0 是否存在无效动作维度、滑移驱动和指标口径失真

## 当前默认设计
- Git 同步策略：
  - 默认只同步源码、文档与配置
  - `RL_Training/logs/` 与 `RL_Training/outputs/` 下的训练日志、checkpoint、导出结果不上传 GitHub
  - 只有当用户明确要求上传训练产物，或跑出较理想模型后，才提醒用户单独上传或归档
- 环境几何：
  - `episode_length_s = 16.0`
  - `commands.resampling_time = 16.0`
  - `commands.goal_distance = 8.0`
  - `commands.goal_direction_max_deg = 30.0`
  - `commands.goal_heading_delta_max_deg = 12.0`
- 动作与观测：
  - 动作维度 `12`
  - Actor / Critic 观测维度 `70 / 70`
  - 当前 Stage0 的接口口径仍是 `6` 个球铰目标 + `6` 个轮速直驱命令
  - 但在 `stage0_cfg` 中，`6` 个球铰动作上下限当前都被固定为 `0`
  - 因此当前 run 的实际有效控制主要只有 `6` 个轮速直驱维度，前 `6` 个动作维度等价于死维度
- PPO 当前默认口径：
  - actor 使用 `tanh squashed Gaussian`
  - `init_std = 0.20`
  - `log_std ∈ [-4.0, 0.0]`
  - actor / critic 都开启 `running normalization`
  - actor / critic hidden dims：
    - `[256, 256] / [256, 256]`
  - activation：
    - `relu`
  - PPO wrapper 的 `clip_actions = None`
  - env 预处理不再做前置动作 clip
  - 环境内部只保留末端 safeguard：
    - 球铰目标映射时的归一化范围保护
    - 轮速目标写入前的物理速度上限保护
  - rollout / update：
    - `num_steps_per_env = 512`
    - `max_iterations = 700`
    - `num_learning_epochs = 5`
    - `num_mini_batches = 16`
  - optimizer：
    - `Adam`
    - `learning_rate = 1e-4`
    - `adam_eps = 1e-5`
  - 其他关键 PPO 超参数：
    - `entropy_coef = 5e-4`
    - `value_loss_coef = 0.5`
    - `gamma = 0.99`
    - `lam = 0.95`
    - `desired_kl = 0.008`
    - `max_grad_norm = 0.5`
- 当前 reward 主形式：
  - `total_reward = distance_progress + goal_direction_reward + goal_heading_reward + stop_reward + success_bonus - time_penalty`
- 当前 termination：
  - `goal_reached`
  - `bad_orientation`
  - `head_tail_roll_out_of_bounds`
  - `ball_joint_out_of_bounds`
  - `time_out`

## 已完成里程碑
- 已完成 Stage0 PPO 审计：
  - 观测、动作、优化器、GAE / bootstrap、timeout 分流都已按源码核对
- 已完成 bounded policy 首轮代码落地：
  - 本地 actor 分布切换为 squashed Gaussian
  - `std` 改为 `log_std` 参数化并加 clamp
  - 移除 PPO wrapper 与 env preprocess 的双前置动作裁切
- 已完成 Stage0 PPO 超参数重设：
  - rollout 拉长到 `512`
  - 更新预算改到 `700`
  - 网络改成 `2 x 256 + relu`
  - `adam_eps` 显式设为 `1e-5`
- 已通过静态检查：
  - `python3 -m py_compile`
- 已完成 bounded policy 首轮真实 run 验证：
  - run：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-19_16-16-01`
  - 已确认：
    - `policy_abs_mean == processed_abs_mean`
    - `policy_std == processed_std`
  - 说明：
    - 这轮 run 中 PPO 采样动作与环境执行动作不再存在中途 clip / 改写不一致

## 当前阻塞
- 新动作链已经有 run 证据，但当前主要问题不再是“动作被谁改写”，而是“策略学出来的行为是否健康”。
- 当前 Stage0 暴露出三个新阻塞：
  - 有效动作语义与动作接口不一致：
    - 对外仍是 `12` 维动作
    - 其中前 `6` 维球铰动作在 Stage0 当前实际上不生效
  - 策略仍明显依赖高滑移轮速推进：
    - 末 `50` 轮 `|longitudinal slip| ≈ 2.38`
    - 末 `50` 轮 `|slip angle| ≈ 0.568 rad`
    - 末 `50` 轮 `wheel_velocity_target_abs_mean ≈ 8.03 rad/s`
  - 日志口径存在失真：
    - `Termination/success_rate` 明显非零
    - 但 `Tracking/goal_success_rate` 全程为 `0`
    - 当前不能再把 `Tracking/goal_success_rate` 当成可信主指标

## 下一步优先级
- 先围绕这次 run 做研究判断，而不是继续盲目长训：
  - 当前 Stage0 是否应保持 `12` 维接口，还是改成与真实可控自由度一致的动作语义
  - 当前 reward 是否过度鼓励“高轮速换距离进展”，而没有足够约束滑移与末端朝向质量
  - 当前 success 相关日志应以哪一个指标作为后续主判据
- 在用户确认判断后，再落地对应实现整改与下一轮验证。
