# 当前状态

## 当前总目标
- 将 `RL_Training/` 下的 Stage0 固化为一条可复现、可解释的平地双 waypoint 纯 RL 连续转向 baseline。
- 当前重点是让策略在路线级转向需求下学会预瞄、协同球铰，并减少高侧滑的“纯差速硬拧”完成方式。

## 当前阶段
- 当前处于：
  - Stage0 代码主线已完成新一轮结构改造：
    - observation 新增 `next_turn_delta`
    - waypoint 采样新增 `min_segment_turn_deg = 20.0°`
    - reward 新增 `differential_turn_cost`
    - `slip_penalty / turn_speed_penalty` 已改为按转向需求加权
- 当前工作重点是：
  - 先恢复 Isaac Lab 运行环境并完成 smoke run
  - 再跑新的真实训练，判断纯 RL 是否开始利用球铰降低差速转向代价
  - 并行完成研究背景/综述首轮文献筛选，先围绕“复杂地形能力需求 → 铰接式车辆 → 球面并联关节启发 → 控制挑战 → 传统方法不足 → RL 价值与不足”建立主干文献池

## 本轮已完成
- 已完成研究背景/综述主干文献的 Markdown 转换：
  - 已放弃本轮继续使用 `MinerU`
  - 改用 `opendataloader-pdf`
  - 第一批与第二批共 `22` 篇核心文献已转换为 `md`
  - 产物目录：
    - `docs/literature/opendataloader_output/`
- 已完成 next-turn preview 观测接线：
  - 利用 `env.py` 中现有 `_waypoint_targets_w` 与 `_active_waypoint_index`
  - 新增 `turn_delta = next_segment_heading - current_segment_heading`
  - actor / critic observation 现已从 `54 / 54` 增至 `55 / 55`
- 已完成 waypoint 采样约束修改：
  - Stage0 当前 `goal_direction_max_deg = 30.0°`
  - Stage0 当前 `min_segment_turn_deg = 20.0°`
  - 因此第二段 waypoint 不再允许退化为近似直线
- 已完成 reward 结构修改：
  - 当前 active reward 为：
    - `distance_to_target`
    - `progress_to_target`
    - `reached_target`
    - `angle_diff`
    - `turn_speed_penalty`
    - `slip_penalty`
    - `differential_turn_cost`
  - `far_from_target` 已从 reward 中删除，只保留为 termination 护栏
  - `differential_turn_cost` 当前基于左右轮扭矩差
  - `slip_penalty` 与 `differential_turn_cost` 当前使用按转向需求缩放的惩罚系数
  - `turn_speed_penalty` 当前使用“当前 bearing 与 preview turn_delta 取大”的转向需求
- 已完成代码链同步：
  - `io_descriptors.py`、observation dim 统计、noise dim 统计、logger tag 已同步更新
- 已完成静态检查：
  - `python3 -m py_compile ...` 通过

## 当前主要问题
- 新主线还没有完成 runtime 验证：
  - 当前终端环境缺少 `isaaclab`
  - 直接执行 `python3 scripts/train.py ...` 会报：
    - `ModuleNotFoundError: No module named 'isaaclab'`
- 因此目前最新的真实训练结论仍来自上一版 `54 / 54` 观测、未含 `differential_turn_cost` 的 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-21_21-51-09_stage0_waypoint_quality_goal10_v1_150iter`
  - 那一版已经证明双 waypoint 主线“能学”，但成功仍不稳定，且完成方式偏高侧滑

## 当前默认设计
- 平地 Stage0 当前默认口径：
  - 双 waypoint
  - 每段 `10 m`
  - 总名义路程约 `20 m`
  - 第二段相对第一段最小转角 `20°`
  - 命中半径 `< 2.0 m`
  - 回合时长 `40 s`
- 当前观测主链：
  - `ball_joint_pos`
  - `ball_joint_vel`
  - `base_lin_vel`
  - `base_ang_vel`
  - `wheel_joint_vel`
  - `wheel_longitudinal_slip`
  - `wheel_slip_angle`
  - `wheel_normal_contact_force`
  - `goal_relative_command`
  - `next_turn_delta`
  - `last_action`
- 当前 reward 设计口径：
  - 不直接奖励球铰角度
  - 通过 preview 转向需求、滑移、转向速度、左右轮差速代价共同塑造协同转向
  - 车轮最终执行链仍为 torque target
  - allocator 仍是固定低层，不是学习器

## 下一步优先级
1. 先恢复 Isaac Lab 运行环境并补跑 smoke run，确认 `55 / 55` 观测链与新 reward/log 指标运行无误。
2. 再跑一轮新的真实训练，重点检查：
   - `Reward/differential_turn_cost`
   - `Reward/slip_penalty`
   - `Reward/turn_speed_penalty`
   - `Observation/wheel_slip_angle_abs_mean_raw`
   - `Action/wheel_torque_target_abs_mean_raw`
3. 在回放中核对球铰是否开始提前参与第二段转向，而不是继续主要依赖高侧滑差速机动。
4. 按已完成的文献筛选结果，优先把综述主干文献转为 `md`，再进入结构化阅读与综述写作。
