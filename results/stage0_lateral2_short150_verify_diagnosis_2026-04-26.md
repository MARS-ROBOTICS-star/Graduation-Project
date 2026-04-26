# Stage0 加权最小二乘侧滑惩罚降至 2.0 短训练诊断

## 1. 本轮目的

本轮只验证一个工程问题：

- 将加权最小二乘低侧滑整形参数 `low_slip_lambda_lateral` 从 `10.0` 改为 `2.0` 后，是否能缓解上一轮出现的低速近停滞问题。

本轮不是最终正式收敛训练，不用于证明 Stage0 已达到低滑移完成能力。

## 2. 运行信息

| 项目 | 内容 |
|---|---|
| run | `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-26_19-38-39_stage0_lateral2_short150_verify` |
| 训练指令 | `isaaclab.sh -p scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --max_iterations 150 --run_name stage0_lateral2_short150_verify` |
| 实际迭代 | `150` iterations，日志显示到 `149/150` |
| 最终 checkpoint | `model_149.pt` |
| TensorBoard 导出 | `tensorboard_export/` |
| 对比基准 | `2026-04-26_18-17-37_stage0_lowlevel_diagnostics_metrics_v2_800iter`，即 `low_slip_lambda_lateral = 10.0` 的上一轮 |

## 3. 参数修改

| 参数 | 上一轮 | 本轮 | 含义 |
|---|---:|---:|---|
| `low_slip_lambda_lateral` | `10.0` | `2.0` | 加权最小二乘平面速度整形中的侧向速度抑制权重 |

其余低层链路保持当前主线设置：

- 车轮仍为 torque target 控制。
- `Omega_ref` 仍只是力矩控制器内部的参考轮速。
- 球铰仍使用同一套 `q_cmd/qdot_cmd` 同时给 Isaac/PhysX PD 和轮速分配器。
- progress gate 仍为 `G = min(G_kappa, G_alpha)`，`M = 0.10 + 1.40G`。

## 4. 分段统计

### 4.1 任务完成与轨迹推进

| 指标 | iter 0-24 | iter 50-74 | iter 100-124 | iter 125-149 | 最后一轮 |
|---|---:|---:|---:|---:|---:|
| `Train/mean_reward` | `-11.085` | `-10.528` | `-4.920` | `-1.959` | `-0.965` |
| `time_out_rate` | `0.487` | `0.975` | `1.000` | `1.000` | `1.000` |
| `far_from_target_rate` | `0.508` | `0.025` | `0.000` | `0.000` | `0.000` |
| `active_segment_completion_pct` | `23.956` | `31.191` | `38.223` | `39.975` | `37.901` |
| `waypoints_completed_mean` | `0.002` | `0.000` | `0.000` | `0.000` | `0.000` |
| `episode_completion_pct` | `0.089` | `0.000` | `0.000` | `0.000` | `0.000` |
| `active_waypoint_pos_error` | `8.254` | `7.141` | `6.178` | `6.003` | `6.210` |

观察：

- 本轮没有完成 waypoint，后段全部以 timeout 结束。
- 但车辆不再像上一轮那样几乎停在起点附近，后段 `active_segment_completion_pct` 约为 `40%`。
- 这说明 `lambda=2` 确实解除了一部分低层整形对前进速度的强压制。

### 4.2 滑移质量

| 指标 | iter 0-24 | iter 50-74 | iter 100-124 | iter 125-149 | 最后一轮 |
|---|---:|---:|---:|---:|---:|
| `wheel_longitudinal_slip_abs_mean_raw` | `2.200` | `2.023` | `1.702` | `1.496` | `1.368` |
| `wheel_slip_angle_abs_mean_raw` | `0.689` | `0.660` | `0.585` | `0.530` | `0.496` |
| `LowSlip/combined_pass_rate` | `0.014` | `0.022` | `0.038` | `0.085` | `0.131` |
| `LowSlip/longitudinal_slip_pass_rate` | `0.078` | `0.114` | `0.160` | `0.248` | `0.316` |
| `LowSlip/slip_angle_pass_rate` | `0.045` | `0.057` | `0.090` | `0.156` | `0.210` |

观察：

- 纵滑从初期约 `2.20` 降到末尾 `1.37`，有下降趋势，但仍高于当前评价阈值 `1.0`。
- 侧滑角从初期约 `0.69 rad` 降到末尾 `0.50 rad` 左右，最后一轮刚接近用户提出的 `30 deg` 上限，但后 25 轮平均仍为 `0.530 rad`，仍偏高。
- 综合低滑移通过率后 25 轮只有 `0.085`，不满足低滑移目标。

### 4.3 整形前后速度命令

| 指标 | iter 0-24 | iter 50-74 | iter 100-124 | iter 125-149 | 最后一轮 |
|---|---:|---:|---:|---:|---:|
| `desired_planar_command_abs_mean_raw` | `0.673` | `0.598` | `0.521` | `0.495` | `0.477` |
| `shaped_planar_command_abs_mean_raw` | `0.662` | `0.586` | `0.488` | `0.450` | `0.430` |
| `planar_command_shaping_delta_abs_mean_raw` | `0.023` | `0.028` | `0.064` | `0.084` | `0.083` |
| `desired_planar_vx_raw` | `1.013` | `0.851` | `0.693` | `0.622` | `0.572` |
| `shaped_planar_vx_raw` | `1.000` | `0.834` | `0.640` | `0.542` | `0.488` |
| `planar_command_delta_vx_raw` | `-0.014` | `-0.017` | `-0.053` | `-0.080` | `-0.085` |

观察：

- 本轮整形后的速度命令仍接近策略原始命令。
- 后 25 轮 `vx` 只从 `0.622` 降到 `0.542`，没有出现上一轮 `desired vx≈0.966` 被压到 `shaped vx≈0.100` 的情况。
- 从“是否过度压死速度”的角度看，`lambda=2` 是有效的。

### 4.4 实际轮心水平速度与低层力矩链

| 指标 | iter 0-24 | iter 50-74 | iter 100-124 | iter 125-149 | 最后一轮 |
|---|---:|---:|---:|---:|---:|
| `V_parallel_abs_mean` | `0.335` | `0.272` | `0.195` | `0.158` | `0.140` |
| `V_perp_abs_mean` | `0.349` | `0.281` | `0.202` | `0.164` | `0.145` |
| `DeltaV_abs_mean` | `0.553` | `0.441` | `0.312` | `0.251` | `0.221` |
| `tau0_abs_mean` | `3.646` | `3.246` | `2.905` | `2.738` | `2.586` |
| `g_kappa_mean` | `0.369` | `0.373` | `0.368` | `0.370` | `0.375` |
| `tau1_abs_mean` | `1.401` | `1.270` | `1.297` | `1.340` | `1.311` |
| `g_alpha_mean` | `0.453` | `0.462` | `0.497` | `0.529` | `0.549` |

观察：

- `V_parallel` 后段约 `0.158 m/s`，比上一轮近停滞状态明显更高，但仍远低于 shaped `vx≈0.542 m/s`。
- `V_perp` 与 `V_parallel` 数值接近，说明车辆仍存在明显横向速度成分。
- `g_alpha` 后段约 `0.529`，说明侧滑衰减仍在持续削弱力矩，但削弱强度不足以把侧滑角快速压进低滑移评价阈值。

### 4.5 progress gate

| 指标 | iter 0-24 | iter 50-74 | iter 100-124 | iter 125-149 | 最后一轮 |
|---|---:|---:|---:|---:|---:|
| `ProgressGate/multiplier` | `0.153` | `0.165` | `0.206` | `0.264` | `0.312` |
| `ProgressGate/combined_gate` | `0.038` | `0.046` | `0.076` | `0.117` | `0.151` |
| `ProgressGate/longitudinal_gate` | `0.176` | `0.220` | `0.309` | `0.389` | `0.444` |
| `ProgressGate/slip_angle_gate` | `0.044` | `0.053` | `0.082` | `0.124` | `0.157` |

观察：

- 后段 multiplier 从约 `0.153` 升到 `0.264`，说明滑移下降后 gate 有恢复。
- 但 `slip_angle_gate` 仍明显低于 `longitudinal_gate`，当前 progress gate 的主要短板仍是侧滑角。
- gate 没有完全压死 progress，但由于任务本身仍未完成，不能把这一轮视为成功训练。

## 5. 与 `lambda=10` 上一轮对比

| 指标 | 本轮 `lambda=2` 后 25 轮 | 上一轮 `lambda=10` iter 100-124 | 上一轮 `lambda=10` 后 25 轮 |
|---|---:|---:|---:|
| `time_out_rate` | `1.000` | `1.000` | `1.000` |
| `far_from_target_rate` | `0.000` | `0.000` | `0.000` |
| `active_segment_completion_pct` | `39.975` | `4.648` | `1.663` |
| `waypoints_completed_mean` | `0.000` | `0.000` | `0.000` |
| `wheel_longitudinal_slip_abs_mean_raw` | `1.496` | `0.563` | `0.301` |
| `wheel_slip_angle_abs_mean_raw` | `0.530` | `0.253` | `0.132` |
| `LowSlip/combined_pass_rate` | `0.085` | `0.796` | `0.986` |
| `desired_planar_command_abs_mean_raw` | `0.495` | `0.826` | `0.760` |
| `shaped_planar_command_abs_mean_raw` | `0.450` | `0.333` | `0.273` |
| `planar_command_shaping_delta_abs_mean_raw` | `0.084` | `0.525` | `0.523` |
| `desired_planar_vx_raw` | `0.622` | `1.018` | `0.966` |
| `shaped_planar_vx_raw` | `0.542` | `0.161` | `0.100` |
| `V_parallel_abs_mean` | `0.158` | `0.032` | `0.016` |
| `V_perp_abs_mean` | `0.164` | `0.040` | `0.019` |
| `ProgressGate/multiplier` | `0.264` | `0.862` | `1.251` |

关键对比：

- `lambda=10`：低滑移指标很好，但主要靠低速近停滞实现，任务推进几乎消失。
- `lambda=2`：任务推进恢复到约 `40%` segment，但低滑移质量明显恶化，纵滑和侧滑仍不达标。

## 6. 有效性结论

`low_slip_lambda_lateral = 2.0` 是“部分有效”，但不是当前目标的合格解。

有效的部分：

- 明显缓解上一轮低层整形过强导致的近停滞。
- `shaped vx` 后 25 轮约 `0.542 m/s`，不再被压到 `0.100 m/s`。
- 实际 `V_parallel` 后 25 轮约 `0.158 m/s`，比上一轮 `0.016 m/s` 高一个数量级。
- `active_segment_completion_pct` 后 25 轮约 `40%`，比上一轮后 25 轮约 `1.7%` 明显更好。

无效或不足的部分：

- 后 25 轮没有完成任何 waypoint。
- 后段全部 timeout，任务没有完成。
- 纵滑后 25 轮约 `1.496`，仍高于评价阈值 `1.0`。
- 侧滑角后 25 轮约 `0.530 rad`，仍高于评价阈值 `0.35 rad`，也略高于用户提出的 `0.5 rad / 30 deg` 上限。
- 综合 low-slip 通过率后 25 轮只有 `0.085`。

## 7. 工程判断

这次验证说明问题不在于“低滑移整形一定会压死车辆”，而在于 `lambda=10` 和 `lambda=2` 位于两个极端：

- `10.0` 太强，低滑移好但通过近停滞实现。
- `2.0` 太弱，车辆能动起来但滑移控制不足。

如果下一步继续沿加权最小二乘整形参数线搜索，工程上应在中间区间验证，例如 `4.0` 或 `5.0`。但是否继续用参数搜索，还是把低滑移纳入成功条件或 reward 主项，需要作为下一轮研究判断单独确认。
