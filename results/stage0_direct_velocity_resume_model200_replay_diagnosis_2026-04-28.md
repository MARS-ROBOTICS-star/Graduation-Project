# Stage0 direct velocity resume model_200 回放诊断

日期：2026-04-28

## Run

- 训练 run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-28_08-24-09_stage0_direct_velocity_no_shaping_resume_from75_625iter`
- resume 来源：`2026-04-27_22-42-33_stage0_direct_velocity_no_shaping_watch_700iter/model_75.pt`
- 最新有效 checkpoint：`model_200.pt`
- TensorBoard step 范围：`75 -> 208`
- 回放探针：`RL_Training/scripts/replay_probe.py`

## 配置确认

- 底盘动作映射：policy 前两维直接映射为 `[vx_cmd, wz_cmd]`，最大值分别为 `2.0 m/s` 和 `2.0 rad/s`。
- 当前车轮执行方式：allocator 输出 `Omega_ref`，环境直接下发车轮 `velocity target`。
- 当前没有低滑移平面整形：`shaped_planar_command == desired_planar_command`。
- 当前没有轮级纵滑反馈力矩：`wheel_slip_feedback_gain=0.0`，`wheel_torque_tracking_gain=0.0`。
- 仍保留 low-slip progress gate；滑移仍会间接削弱正向 progress，但不直接作为 active reward penalty。

## TensorBoard 训练结论

后 25 个 step 均值：

- `desired_vx≈0.083 m/s`，`desired_wz≈0.133 rad/s`。
- `wheel_speed_reference_abs≈2.242 rad/s`。
- `wheel_joint_vel_abs≈2.097 rad/s`。
- `v_parallel_abs≈0.096 m/s`，`v_perp_abs≈0.099 m/s`。
- `delta_v_abs≈0.408 m/s`。
- 纵滑约 `3.328`，侧滑角约 `0.480 rad`。
- `progress_gate_multiplier≈0.250`，几乎卡在下限。
- `waypoints_completed=0`，`time_out_rate=1.0`，`mean_episode_length=2399`。

解释：

- policy 不是完全输出零动作，allocator 也不是输出零轮速。
- 车轮速度驱动能跟踪参考轮速，但轮周速度没有有效转化为车辆沿目标方向的位移。
- 训练后段策略更像是“低前进速度 + 小幅转向/姿态动作 + 活到 timeout”，没有学出 waypoint 完成。

## model_200 单环境回放探针

设置：`num_envs=1`，`steps=120`，`warmup_steps=20`。

回放均值：

- policy 全动作绝对值均值：`0.197`。
- policy 底盘动作绝对值均值：`0.063`。
- 映射后底盘命令：`vx_cmd≈-0.001 m/s`，`wz_cmd≈0.113 rad/s`。
- 轮速参考绝对值均值：`0.903 rad/s`。
- 车轮实际角速度绝对值均值：`0.821 rad/s`。
- 轮子实际滚动速度绝对值均值：`0.066 m/s`。
- 轮子侧向速度绝对值均值：`0.072 m/s`。
- 纵滑绝对值均值：`1.382`。
- 侧滑角绝对值均值：`0.443 rad`。
- 120 步总位移约 `0.134 m`。

回放中的平均动作向量：

`[-0.0006, 0.0566, 0.4632, 0.0876, -0.0834, -0.2422, -0.1020, -0.3024]`

对应底盘速度命令：

`[vx_cmd≈-0.0012 m/s, wz_cmd≈0.1133 rad/s]`

对应每轮平均参考速度：

- `body_car_wheel_left≈-0.139 rad/s`
- `body_car_wheel_right≈0.127 rad/s`
- `head_car_wheel_left≈-0.866 rad/s`
- `head_car_wheel_right≈0.973 rad/s`
- `tail_car_wheel_left≈1.101 rad/s`
- `tail_car_wheel_right≈-0.841 rad/s`

解释：

- 单环境回放时 policy 已基本不给前进速度，主要给小幅偏航和球铰姿态动作。
- 轮速参考呈正负混合，更多对应转向/构型运动，而不是一致向前滚动。
- 因此视觉上“小车基本不动”是合理结果，不是回放窗口没刷新，也不是车轮 velocity target 没下发。

## 当前判断

这次失败不主要在 actuator 没执行，也不主要在 allocator 把速度分配成零。问题分两层：

1. 训练统计层：policy 的前进命令从 step 75 的约 `0.390 m/s` 下降到后段约 `0.08 m/s`，任务没有形成完成 waypoint 的收益牵引。
2. 物理运动层：即使有约 `2 rad/s` 量级的训练轮速参考，实际滚动推进只有约 `0.1 m/s`，且纵滑和侧滑仍高，轮地接触没有把轮速高效转化为沿目标方向的位移。

下一步不应继续只延长同一配置训练。需要先决定是否把 Stage0 的成功标准明确改成“必须产生非零有效前进并完成 waypoint”，再同步修改 reward / termination / gate 的语义。
