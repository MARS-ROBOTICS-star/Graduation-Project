# Stage0 `model_699.pt` 回放近停滞问题排查

日期：2026-04-27

## 排查对象

- run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-27_18-17-40_stage0_current_full_watch_700iter`
- checkpoint：`model_699.pt`
- 现象：可视化回放时小车几乎完全不动。

## 回放确认

使用 `scripts/evaluate_contact_replay.py` 对 `model_699.pt` 做 `num_envs=1`、`steps=1200`、`warmup_steps=120` 的 headless 回放。

结果摘要：

- `v_parallel_abs_mean = 0.0051 m/s`
- `v_perp_abs_mean = 0.0063 m/s`
- `active_segment_completion_pct_tail = 4.1077%`
- `longitudinal_slip_abs_mean = 0.3453`
- `slip_angle_abs_mean = 0.0399 rad`
- `ball_joint_vel_abs_mean = 0.0091`
- `ball_joint_target_error_abs_mean = 0.0046`
- 中车两轮平均法向力：`21.58 N / 62.84 N`
- 中车载荷占六轮总法向力约 `23.05%`

判断：回放中的“几乎不动”是真实策略行为，不是单纯可视化错觉。机器人没有明显接触丢失或球铰失控，主要是策略和低层控制共同把运动幅度压得很小。

## 训练末端动作数据

TensorBoard 后 25 轮：

- `desired_planar_vx_raw ≈ 0.00176 m/s`
- 最后一步 `desired_planar_vx_raw ≈ -0.00953 m/s`
- `desired_planar_wz_raw ≈ -0.0762 rad/s`
- `shaped_planar_vx_raw ≈ 0.00128 m/s`
- 最后一步 `shaped_planar_vx_raw ≈ -0.01037 m/s`
- `shaped_planar_wz_raw ≈ -0.0608 rad/s`
- `wheel_speed_reference_abs_mean_raw ≈ 0.567 rad/s`
- 最后一步 `wheel_speed_reference_abs_mean_raw ≈ 0.480 rad/s`
- `wheel_torque_target_abs_mean_raw ≈ 1.892 N*m`
- `v_parallel_abs_mean_raw ≈ 0.0135 m/s`

与历史可移动 run `2026-04-25_18-26-58_stage0_lowslip_gate_v1_700iter` 后 25 轮对比：

- `policy_abs_mean`：当前约 `0.120`，旧 run 约 `0.485`
- `shaped_planar_command_abs_mean`：当前约 `0.134`，旧 run 约 `0.854`
- `wheel_speed_reference_abs_mean`：当前约 `0.567 rad/s`，旧 run 约 `6.343 rad/s`
- `wheel_torque_target_abs_mean`：当前约 `1.892 N*m`，旧 run 约 `2.615 N*m`
- `waypoints_completed_mean`：当前 `0.0`，旧 run 约 `0.551`
- 纵滑：当前约 `0.765`，旧 run 约 `2.739`
- 侧滑角：当前约 `0.0945 rad`，旧 run 约 `0.691 rad`

判断：当前 policy 不是“想动但底层不让动”，而是高层已经学成了近零前进命令。底层控制随后进一步把这个小命令压成几乎不可见的运动。

## 配置链路检查

当前 Stage0 生效参数：

- `base_forward_velocity_max = 2.0`
- `base_yaw_rate_max = 2.0`
- `base_allow_reverse = true`
- `low_slip_lambda_lateral = 5.0`
- `wheel_torque_tracking_gain = 2.0`
- `wheel_slip_feedback_gain = 4.0`
- `wheel_slip_velocity_epsilon = 0.1`
- `slip_penalty_weight = -2.0`
- `slip_longitudinal_penalty_ratio = 5.0`
- `slip_angle_penalty_ratio = 1.0`
- `progress_gate_min_multiplier = 0.25`
- `progress_gate_max_multiplier = 1.5`
- `load_equalization_weight = 0.0`

动作下发链路：

1. `actions[:, :2]` 映射成 `[vx_cmd, yaw_rate_cmd]`。
2. `actions[:, 2:]` 映射成球铰期望位置 `q^d`。
3. allocator 内部生成 `q_cmd/qdot_cmd`。
4. low-slip shaper 把 `[vx_cmd, yaw_rate_cmd]` 整形成 `shaped_planar_command`。
5. 运动学模型根据 `shaped_planar_command` 和 `qdot_cmd` 计算 `wheel_speed_reference`。
6. 轮级牵引控制计算 `wheel_torque_targets`。
7. `_apply_action()` 下发球铰位置目标和车轮力矩目标。

检查结果：

- `_apply_action()` 没有断链，车轮力矩目标确实下发到 wheel joints。
- 球铰没有失控，headless 回放中 `ball_joint_target_error_abs_mean` 只有约 `0.0046`。
- 接触没有完全丢失，六轮总法向力约 `366 N`，中车载荷占比约 `23%`。
- 主要问题不在 Isaac 下发接口，而在 policy 输出和低层纵滑反馈的组合。

## 底层运动学与牵引控制问题

当前轮级牵引公式为：

$$
\tau_i = w_i \left[K_t(\Omega_i^{ref}-\Omega_i)-K_s \kappa_i\right]
$$

其中当前纵滑定义为：

$$
\kappa_i = \frac{r\Omega_i - V_{\parallel,i}}{\max(|V_{\parallel,i}|,\epsilon)}
$$

在低速回放中 $V_{\parallel,i} \approx 0$，因此分母基本由 $\epsilon=0.1$ 决定。此时如果忽略接触权重，轮速平衡近似满足：

$$
K_t(\Omega^{ref}-\Omega)-K_s \frac{r\Omega}{\epsilon}=0
$$

代入当前参数 $K_t=2.0$、$K_s=4.0$、$r=0.19$、$\epsilon=0.1$：

$$
\Omega \approx \frac{2.0}{2.0+4.0 \times 0.19 / 0.1}\Omega^{ref}
\approx 0.208\Omega^{ref}
$$

也就是说，在低速近零车体速度下，纵滑反馈会把实际轮速压到参考轮速的大约 `21%`。当前最后一步平均 `wheel_speed_reference_abs_mean_raw ≈ 0.480 rad/s`，对应的平衡轮速只有约 `0.10 rad/s`，轮周速度约 `0.019 m/s`。视觉上就接近不动。

判断：这不是单纯符号错误。低层公式在大命令下仍可驱动车辆，但当 policy 已经输出小命令时，当前低速纵滑反馈会主动形成强制动效果。

## 奖励结构问题

当前奖励中存在一个低速局部最优：

- `distance_to_target` 和 `angle_diff` 是持续正奖励，即使车辆不前进也能拿到。
- `progress_to_target` 只奖励实际距离缩短，不会主动产生前进命令。
- `progress_gate` 只放大/缩小正向 progress；如果 policy 不动，progress 本身就是 `0`。
- `slip_penalty` 使用 `5.0 * mean_abs_longitudinal_slip + 1.0 * mean_abs_slip_angle`，且外部权重为 `-2.0`，对产生滑移的运动有强惩罚。
- timeout 没有对应的强负反馈。

因此，policy 可以通过“少动、低滑移、低风险”获得相对更稳定的回报，而不是承担高滑移代价去完成 waypoint。

## 结论

1. 小车回放完全不动的直接原因是 `model_699.pt` 的 policy 已经学成近零前进命令。
2. 底层运动学/牵引模型没有断链，但当前低速纵滑反馈会在小轮速参考下进一步把车轮转速压低。
3. 当前配置的主要问题是奖励和低层控制目标不一致：奖励强烈鼓励低滑移，却没有同等强度要求非零推进和 waypoint 完成。
4. 当前 `low_slip_lambda_lateral=5.0` 不是唯一原因；它只会进一步保守化平面命令。更关键的是纵滑惩罚和低速纵滑反馈共同把策略吸进近停滞局部解。
5. 当前结果不能解释为“底层运动学模型坏了”，更准确地说是：底层模型在低速区的滑移反馈过强，而训练目标允许 policy 利用这一点停住。

## 下一步需要用户确认的研究判断

如果 Stage0 的成功标准仍然是“完成双 waypoint”，那么后续不应继续训练当前配置。需要先确认 Stage0 是否必须同时满足：

- waypoint 完成；
- 非零有效推进；
- 低纵滑和低侧滑；
- 中车有效承载。

确认后再改奖励主结构或成功条件；否则继续调单个小权重会继续在“能动但高滑移”和“不动但低滑移”之间摆动。
