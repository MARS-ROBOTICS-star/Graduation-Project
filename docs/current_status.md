# 当前状态

## 当前总目标
- 将 `RL_Training/` 下的 Stage0 固化为一条可复现、可解释的平地多 waypoint 高质量运动 baseline。
- 当前优先级不再是“严格终点捕获”，而是“连续通过 waypoint、低滑移转向、训练链稳定”。

## 当前阶段
- 当前处于：
  - Stage0 任务语义已切换为“单回合双 waypoint 连续跟踪”，且首轮 `150` 轮真实训练已完整跑通
- 当前工作重点是：
  - 判断新 Stage0 的 reward 平衡是否合理
  - 判断当前成功是否已经稳定，还是仍靠激进机动换取 waypoint 完成

## 本轮已完成
- 已完成 Stage0 任务语义重构：
  - `episode_length_s = 40.0`
  - `commands.num_waypoints_per_episode = 2`
  - `commands.goal_distance = 10.0`
  - waypoint 命中阈值改为 `< 2.0 m`
  - 命中当前 waypoint 后自动切换到下一个
  - 只有最后一个 waypoint 命中时 episode 才记为 `success`
- 已将 `wheel_slip_angle` 正式加入 actor / critic observation：
  - 当前观测维度为 `54 / 54`
  - 观测主链现在包含：
    - `ball_joint_pos`
    - `ball_joint_vel`
    - `base_lin_vel`
    - `base_ang_vel`
    - `wheel_joint_vel`
    - `wheel_longitudinal_slip`
    - `wheel_slip_angle`
    - `wheel_normal_contact_force`
    - `goal_relative_command`
    - `last_action`
- 已完成 Stage0 reward 重构：
  - 主目标改为“连续 waypoint 跟踪 + 行为质量”
  - 当前 active reward 为：
    - `distance_to_target`
    - `progress_to_target`
    - `reached_target`
    - `far_from_target`
    - `angle_diff`
    - `turn_speed_penalty`
    - `slip_penalty`
  - 当前 `commands[:, 3]` 的含义已改为：
    - 车体系下指向当前 active waypoint 的 bearing
    - 不再是终点最终朝向误差
- 已完成代码级一致性修正：
  - `termination` 中 `far_from_target` 已改为使用 `goal_distance + far_from_target_margin`
  - 当前 Stage0 口径为 `20.0 + 6.0`
- 已完成静态检查与 smoke run：
  - `python3 -m py_compile ...` 通过
  - smoke run：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-21_21-32-41_smoke_stage0_waypoint_quality_v2_far_margin_fix`
  - smoke run 显示 actor / critic 输入已变为 `54`
  - 新 reward 项、waypoint 统计链、修正后的 `far_from_target` 判定都已正常输出
- 已完成首轮真实训练：
  - run：
    - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-21_21-51-09_stage0_waypoint_quality_goal10_v1_150iter`
  - Isaac 日志：
    - `/tmp/isaaclab/logs/isaaclab_2026-04-21_21-51-09.log`
  - 训练结果表明新 Stage0 不是“起不来”，而是“能学，但成功稳定性和行为质量都还不够”
  - 当前关键量：
    - `Train/mean_reward: -1.46 -> 19.15`
    - `Train/mean_episode_length: 253.8 -> 1622.5`
    - `goal_success_rate: 0.0 -> 0.5625`
    - `time_out_rate: 0.8809 -> 0.4375`
    - `episode/waypoints_completed: 0.0 -> 1.3047`
    - `episode/waypoint_completion_pct: 0.0 -> 65.23`
    - `wheel_longitudinal_slip_abs_mean_raw: 9.22 -> 3.49`
    - `wheel_slip_angle_abs_mean_raw: 0.514 -> 0.630`
    - `Loss/value: 0.0099 -> 0.3265`

## 当前主要问题
- 训练存在明显两阶段形态：
  - `iteration 0-117` 长时间平台期，大多数 episode 仍以 `time_out` 结束
  - `iteration 118+` 才出现明显 success 跃迁
- 成功还不稳定：
  - 虽然在 `iteration 131` 一度到 `goal_success_rate = 1.0`
  - 但末轮只剩 `0.5625`，最后 `10` 轮平均约 `0.5722`
- 行为质量仍不够好：
  - 纵滑率明显下降
  - 但侧滑角在后段反而升到约 `0.60~0.63 rad`
  - 当前更像“靠激进机动完成 waypoint”，不是低侧滑高质量转向
- reward 平衡仍偏向推进：
  - 后段 `progress_to_target` 与 `reached_target` 是主要正奖励来源
  - `slip_penalty` 虽然不再压死训练，但全程仍保持约 `-0.005`
- critic 稳定性偏弱：
  - `Loss/value` 后段升到 `0.3~0.4`
  - 说明成功跃迁后价值拟合开始变得吃力

## 当前默认设计
- 平地 Stage0 任务定义：
  - 双 waypoint
  - 每段 `10 m`
  - 总名义路程约 `20 m`
  - 命中半径 `< 2.0 m`
  - 回合时长 `40 s`
  - 目标是高质量连续运动，不要求每个 waypoint 停稳
- 成功口径：
  - 中间 waypoint 命中只切换目标，不终止
  - 最后一个 waypoint 命中才算 episode success
- 行为质量口径：
  - 关注低纵滑、低侧滑、转向时主动降速
  - 不强制要求球铰在回放里显著参与转向
- 训练链默认口径：
  - 动作维度 `8`
  - 观测维度 `54 / 54`
  - 车轮最终执行链仍为 torque target
  - allocator 仍是固定低层，不是学习器

## 下一步优先级
1. 先基于本轮真实 run 判断 reward 平衡，而不是继续盲目加长训练。
2. 重点围绕以下矛盾做下一轮研究判断：
   - `progress_to_target / reached_target` 是否仍过强
   - `slip_penalty` 是否对侧滑抑制不够但对早期学习又偏硬
   - `turn_speed_penalty` 是否不足以让策略在转向段主动降速
3. 在回放中核对 late-phase success 的真实运动形态，确认 waypoint 完成是否主要依赖高侧滑机动。
