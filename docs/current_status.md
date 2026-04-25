# 当前状态

## 当前总目标
- 将 `RL_Training/` 下的 Stage0 固化为一条可复现、可解释的平地双 waypoint 纯 RL baseline。
- 先稳住一条已经被真实训练证明“能学起来”的环境主线，再在此基础上继续讨论更高质量的协同转向改造。

## 当前阶段
- 当前处于：
  - Stage0 主体配置曾按用户要求回退到当前已知最佳真实 run 对应口径：
    - `2026-04-21_21-51-09_stage0_waypoint_quality_goal10_v1_150iter`
  - 当前源码已按用户最新要求把 `yaw_rate_cmd` 加回 policy 动作空间：
    - policy 动作为 `8` 维：`[vx_cmd, yaw_rate_cmd] + q^d`
    - actor / critic 观测为 `54 / 54`
    - 环境内部直接将二维底盘平面命令 `[vx_cmd, yaw_rate_cmd]` 交给低层 allocator
  - 当前源码主线不再使用：
    - `next_turn_delta`
    - `min_segment_turn_deg = 20.0°`
    - `differential_turn_cost`
    - 按 turn-demand 缩放的 `slip_penalty / turn_speed_penalty`

## 当前默认设计
- 平地 Stage0 当前默认口径：
  - 双 waypoint
  - 每段 `10 m`
  - 总名义路程约 `20 m`
  - 命中半径 `< 2.0 m`
  - 回合时长 `40 s`
  - `64` 个并行环境
- 当前动作空间：
  - `8` 维
  - `2` 维底盘平面命令
  - `6` 维球铰期望姿态
- 当前观测主链：
  - `54 / 54`
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
- 当前 reward 口径：
  - `distance_to_target`
  - `progress_to_target`
  - `reached_target`
  - `far_from_target`
  - `angle_diff`
  - `turn_speed_penalty`
  - `slip_penalty`
- `RL_Training/` 源码当前低层执行链保持不变：
  - 高层策略输出 `u_v^d=[vx_cmd, yaw_rate_cmd]` 与 `q^d`
  - 环境内部将二维底盘平面命令直接交给 allocator
  - 环境内部 allocator 生成 `q_cmd`、`Omega_ref`、`tau_cmd`
  - 车轮仍走 torque target 链

## 已完成里程碑
- 已有最佳真实 run：
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-21_21-51-09_stage0_waypoint_quality_goal10_v1_150iter`
  - 该 run 已证明双 waypoint 主线“能学”，但成功仍不稳定，且完成方式偏高侧滑。
- 已完成当前源码同步：
  - Stage0 环境已回到与上述最佳 run 一致的任务、观测主项和 reward 口径。
  - 动作空间已按用户最新要求恢复为 `8` 维，重新加入 policy 输出的 `yaw_rate_cmd`。
  - 已通过 `py_compile` 静态检查。
- 论文侧当前仍保持：
  - `chapter01` 七部分首轮落稿已完成
  - `chapter03` 已恢复为“球铰姿态规划器 + 名义轮速解析分配 + 低滑移执行层”结构
  - `chapter03` 已完成一轮语言润色：公式、接口和技术口径未改，行文改为更接近本科毕业论文的“建模对象—变量定义—几何关系—速度关系—轮速分配—执行整形”递进叙述
  - `chapter03` 已按“高层动作不给 `yaw_rate_cmd`”重新推导运动学模型：
    - 高层动作改为 `7` 维：`V_x^d` 与 `q^d`
    - 名义轮心速度不再含独立偏航角速度项，写为 `V_x^d e_x + G_w(q) qdot_cmd`
    - 名义轮速分配改为 `Omega^d = J_w(q) V_x^d + J_q(q) qdot_cmd`，其中 `J_w(q)` 为 `6 x 1`
    - 低滑移整形变量改为标量 `tilde V_x`，输出整形后的纵向速度 `V_x^*`
  - `chapter03` 已完成符号一致性修订：
    - 第 3 章当前不再把中模块偏航角速度作为高层输入；若叙述偏航角速度，只用于说明旧动作口径不再采用
    - 车轮角速度继续使用 `\Omega`
    - 低滑移优化变量改为 `\tilde V_x`
    - 侧向速度仿射系数改为 `\boldsymbol\alpha_w,\beta_w`
    - 低滑移层接口不再把 `\mathbf q^{cmd}` 写成自身输出
    - 纵向滑移 `\kappa_w` 在论文中按“车轮圆周速度大于实际纵向滚动速度时为正滑转”的口径定义

## 当前主要问题
- 当前终端环境仍缺少 `isaaclab`：
  - 直接执行 `python3 scripts/train.py ...` 会报 `ModuleNotFoundError: No module named 'isaaclab'`
  - 因此本轮只能完成代码回退与静态校验，不能在本机会话内直接补跑 smoke。
- 当前 reward 评价结论：
  - 关键学习信号主要来自 `progress_to_target` 与 `reached_target`，辅以 `distance_to_target` 和 `angle_diff`。
  - `slip_penalty` 有约束作用，但不足以稳定实现低侧滑、低纵滑和球铰协同转向。
  - `far_from_target` 主要是失败护栏，`turn_speed_penalty` 量级偏弱且只基于当前目标视线角。
- 最佳 run 虽然能学，但仍有两个未解决问题：
  - 成功率后段有脉冲，但末轮不稳定
  - 完成方式偏高侧滑，不适合直接作为“协同转向已经学成”的证据
- 论文 `chapter04` 与答辩材料仍未完全同步 `chapter03` 当前接口口径。
- `RL_Training/` 源码已重新加入 policy `yaw_rate_cmd`，恢复为 `8` 维动作模型；该口径尚未完成本轮 Isaac Lab smoke。
- 论文 `chapter03` 目前仍记录“不含 `yaw_rate_cmd`”的 `7` 维动作推导，已与当前 `RL_Training/` 源码重新加入 `yaw_rate_cmd` 的 `8` 维动作口径不一致；若后续论文要同步，需要单独修改第 3 章。

## 下一步优先级
1. 先恢复 Isaac Lab 运行环境。
2. 用当前 `54 / 54`、`8` 维动作的 Stage0 主线补跑 smoke run。
3. 再复跑一轮当前 `8` 维动作主线的真实训练，确认当前代码与历史最好结果对齐。
4. 只有在这条 baseline 重新复现后，才继续推进 `next_turn preview / differential_turn_cost` 这类新设计。
