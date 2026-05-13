# Stage1 球铰 PD 控制 MATLAB 真实轨迹仿真实验方案

## 1. 实验定位

本文档专门说明 MATLAB 预仿真实验怎么做。它不替代 `docs/Stage1球铰PD控制MATLAB预仿真方案.md` 中的控制链路总体设计，而是把 MATLAB 部分单独拆出来，明确：

- 使用哪些 IsaacLab 真实数据；
- 使用哪个策略模型和哪些轨迹；
- MATLAB 中采用什么简化动力学模型；
- 输入工况如何组织；
- 观察哪些信号；
- 用哪些指标筛选统一 PD 增益。

本实验的核心目标不是在 MATLAB 中完整复现三节车和地形接触，而是回答一个更窄的问题：

> 当 policy 给出的球铰目标姿态 $q^d(t)$ 直接作为 position target 下发时，统一球铰 PD 增益是否能让球铰在真实 policy 目标轨迹下稳定、平滑、足够快地响应，并且不会长期力矩饱和或速度限幅？

因此，MATLAB 仿真的输入应优先来自 IsaacLab 中真实 policy 的输出轨迹，而不是只使用人工阶跃。

## 2. 当前真实代码路径

当前 Stage1 active 链路相关文件：

| 内容 | 路径 |
|---|---|
| 环境主类和动作下发 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py` |
| 动作映射 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py` |
| 轮速分配和球铰 direct target | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py` |
| 共享控制配置 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py` |
| Stage0 配置 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py` |
| Stage1 配置 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage1_cfg.py` |
| actuator 构造 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/assets/actuators_cfg.py` |

说明：本文件前半部分记录 MATLAB 调参使用的旧 `model_699.pt` 轨迹来源；这些旧 CSV 中保留 `q_position_target_old` 和 `qdot_cmd_old` 字段，用于量化旧链路削弱 policy target 的幅度。2026-05-10 direct-target 代码落地后，`export_ball_joint_policy_trace.py` 新导出的 active 字段已改为 `q_position_target` 和 `qdot_alloc`。

旧轨迹导出时，`compute_low_slip_control_targets()` 仍会调用 `compute_ball_joint_planner_outputs()`，内部生成：

$$
\dot q_{\mathrm{cmd}}
=
\operatorname{clip}
\left(
K(q^d-q),
-\dot q_{\max},
\dot q_{\max}
\right)
$$

$$
q_{\mathrm{cmd}}
=
\operatorname{clip}
\left(
q+\Delta t_c\dot q_{\mathrm{cmd}},
q_{\mathrm{lower}},
q_{\mathrm{upper}}
\right)
$$

这就是当前 `desired_target -> position_target` 被削弱的直接位置。

## 3. 策略模型和数据路径

### 3.1 主策略模型

优先使用最近完整 Stage1 训练结果，因为它已经暴露出“policy 有球铰目标，但 position target 被削弱”的问题。

| 项目 | 路径 |
|---|---|
| Stage1 run | `RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-09_16-48-52_stage1_sec14_tune_v1_128env_700iter` |
| checkpoint | `RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-09_16-48-52_stage1_sec14_tune_v1_128env_700iter/model_699.pt` |
| TensorBoard 导出目录 | `RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-09_16-48-52_stage1_sec14_tune_v1_128env_700iter/tensorboard_export` |
| 聚合球铰 debug CSV | `RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-09_16-48-52_stage1_sec14_tune_v1_128env_700iter/tensorboard_export/scalars/Debug__Stage1__BallJoint__*.csv` |

已有 TensorBoard CSV 是按 PPO iteration 聚合后的标量均值，不是逐 control step 的真实时间序列。它能证明 `desired_target`、`position_target`、`actual_pos` 的平均差距，但不适合作为最终 MATLAB 时域响应输入。

因此 MATLAB 调参的真实输入数据分两级：

1. 第一优先级：新增 IsaacLab 回放导出的逐 control step 原始轨迹。
2. 第二优先级：已有 TensorBoard 聚合标量，仅用于复核平均差距和选择重点关节。

### 3.2 建议新增的原始轨迹导出路径

当前已实现导出脚本：

```text
RL_Training/scripts/export_ball_joint_policy_trace.py
```

当前输出目录：

```text
results/stage1_ball_joint_pd_matlab/raw_traces/
```

2026-05-10 已完成一次 `model_699.pt` 导出，输出文件：

```text
results/stage1_ball_joint_pd_matlab/raw_traces/sec14_model699_flat_stairs_down_obstacles_combined.csv
results/stage1_ball_joint_pd_matlab/raw_traces/sec14_model699_flat_stairs_down_obstacles_col00_flat.csv
results/stage1_ball_joint_pd_matlab/raw_traces/sec14_model699_flat_stairs_down_obstacles_col05_stairs_down.csv
results/stage1_ball_joint_pd_matlab/raw_traces/sec14_model699_flat_stairs_down_obstacles_col06_stairs_down.csv
results/stage1_ball_joint_pd_matlab/raw_traces/sec14_model699_flat_stairs_down_obstacles_col07_stairs_down.csv
results/stage1_ball_joint_pd_matlab/raw_traces/sec14_model699_flat_stairs_down_obstacles_col08_discrete_obstacles.csv
results/stage1_ball_joint_pd_matlab/raw_traces/sec14_model699_flat_stairs_down_obstacles_col09_discrete_obstacles.csv
results/stage1_ball_joint_pd_matlab/raw_traces/sec14_model699_flat_stairs_down_obstacles_summary.json
```

每个 CSV 应是逐 control step 数据，而不是 iteration 均值。

## 4. 真实轨迹 CSV 字段

每一行表示一个 env 在一个控制步的数据。建议至少包含以下字段。

### 4.1 时间和地形信息

| 字段 | 含义 |
|---|---|
| `step` | 控制步编号 |
| `time_s` | 仿真时间，单位 s |
| `env_id` | 环境编号 |
| `terrain_col` | terrain column |
| `terrain_name` | 地形名称 |
| `terrain_level` | 当前 row / level |
| `row_progress` | 当前目标段 row 推进比例 |
| `is_done` | 当前步是否 episode 结束 |
| `done_reason` | 终止原因，若可得 |

### 4.2 球铰信号

六个球铰顺序必须与当前 `BALL_JOINT_NAMES` 一致：

```text
spm1_platform_joint_z
spm1_platform_joint_y
spm1_platform_joint_x
spm2_platform_joint_z
spm2_platform_joint_y
spm2_platform_joint_x
```

每个关节建议导出：

| 字段模式 | 含义 |
|---|---|
| `q_desired_<joint>` | policy action 映射后的目标姿态 $q^d$ |
| `q_position_target_old_<joint>` | 旧 planner 下实际下发的 position target；新导出中对应 `q_position_target_<joint>` |
| `q_actual_<joint>` | Isaac 实际球铰位置 |
| `qdot_actual_<joint>` | Isaac 实际球铰角速度 |
| `qdot_cmd_old_<joint>` | 旧 planner 的 rate target；新导出中对应 `qdot_alloc_<joint>` |
| `target_error_old_<joint>` | 旧链路下 `position_target - actual_pos` |

如果能从 IsaacLab 取到关节驱动力矩或近似 drive effort，额外导出：

| 字段模式 | 含义 |
|---|---|
| `tau_applied_<joint>` | 实际驱动力矩或近似驱动力矩 |
| `tau_saturation_flag_<joint>` | 是否接近 effort limit |

### 4.3 轮速分配相关信号

| 字段 | 含义 |
|---|---|
| `vx_cmd_raw` | policy 原始前向速度命令 |
| `vx_cmd_limited` | 地形速度限幅后的前向速度命令 |
| `yaw_rate_cmd` | yaw rate 命令 |
| `wheel_speed_reference_<wheel>` | 轮速参考 |
| `wheel_torque_target_<wheel>` | 车轮 torque target |
| `contact_weight_<wheel>` | 接触权重 |
| `rolling_speed_actual_<wheel>` | 轮地纵向速度 |
| `lateral_speed_actual_<wheel>` | 轮地侧向速度 |

这些信号不直接进入第一版单关节 MATLAB plant，但用于判断 `qdot_alloc` 是否会污染 wheel speed reference。

## 5. MATLAB 模型路径和输出路径

MATLAB 文件建议放在：

```text
scripts/matlab/stage1_ball_joint_pd/
```

建议文件结构：

```text
scripts/matlab/stage1_ball_joint_pd/run_real_trace_pd_sweep.m
scripts/matlab/stage1_ball_joint_pd/load_isaac_ball_joint_trace.m
scripts/matlab/stage1_ball_joint_pd/simulate_uniform_ball_joint_pd.m
scripts/matlab/stage1_ball_joint_pd/compute_trace_metrics.m
scripts/matlab/stage1_ball_joint_pd/plot_trace_response.m
```

MATLAB 输出建议放在：

```text
results/stage1_ball_joint_pd_matlab/
```

输出文件：

```text
results/stage1_ball_joint_pd_matlab/metrics_uniform_gain_sweep.csv
results/stage1_ball_joint_pd_matlab/best_uniform_gain_candidates.csv
results/stage1_ball_joint_pd_matlab/figures/
results/stage1_ball_joint_pd_matlab/report_stage1_ball_joint_pd_matlab.md
```

### 5.1 当前已搭建的 Simulink 初版

2026-05-10 已在 MATLAB / Simulink 中搭建第一版统一增益仿真模型：

```text
scripts/matlab/stage1_ball_joint_pd/stage1_ball_joint_pd_uniform.slx
```

配套脚本：

```text
scripts/matlab/stage1_ball_joint_pd/build_stage1_ball_joint_pd_simulink.m
scripts/matlab/stage1_ball_joint_pd/init_stage1_ball_joint_pd_workspace.m
scripts/matlab/stage1_ball_joint_pd/load_isaac_ball_joint_trace.m
```

模型内容：

- `q_desired` 由真实轨迹 CSV 或 demo 输入提供；
- `q_target_new = clamp(q_desired, q_lower, q_upper)`；
- 六个球铰轴共用统一 `Kp/Kd`；
- 单轴 plant 使用 $J\ddot q = \tau - B\dot q - \tau_{\mathrm{load}}$；
- `tau` 限幅为 `60 N*m`；
- `qdot` 限幅为 `2 rad/s`；
- `qdot_alloc_new` 使用实际响应速度的一阶低通滤波；
- Scope 中同时显示旧链路的 `q_position_target_old`、`q_actual_old`、`qdot_actual_old`、`qdot_cmd_old` 和新链路预测信号。

打开并生成模型：

```matlab
run("/home/ubuntu/Graduation-Project/scripts/matlab/stage1_ball_joint_pd/build_stage1_ball_joint_pd_simulink.m")
```

使用真实轨迹打开模型示例：

```matlab
trace_csv_path = "/home/ubuntu/Graduation-Project/results/stage1_ball_joint_pd_matlab/raw_traces/sec14_model699_flat_stairs_down_obstacles_col08_discrete_obstacles.csv";
trace_env_id = 4;
run("/home/ubuntu/Graduation-Project/scripts/matlab/stage1_ball_joint_pd/build_stage1_ball_joint_pd_simulink.m")
```

当前已验证 `col08_discrete_obstacles`、`env_id=4` 的真实轨迹可以完整仿真，输出为 `6` 个球铰通道，仿真时长 `19.983333 s`。默认 `Kp=320`、`Kd=32` 下，验证结果为 `max_abs_q = 0.663702 rad`、`max_abs_qdot = 2.000000 rad/s`、`max_abs_tau = 60.000000 N*m`、`tau_saturation_ratio = 0.274211`。

### 5.2 IsaacLab 球铰动力学辨识数据

为减少 MATLAB 中 $J$、$B$、$\tau_{\mathrm{load}}$ 完全拍脑袋的问题，已新增 IsaacLab 辨识脚本：

```text
RL_Training/scripts/identify_ball_joint_dynamics.py
```

该脚本不训练 policy，而是像自动键盘控制一样给车辆施加脚本动作：

- 车轮给定小前进命令；
- 六个球铰轴按正弦目标逐个激励；
- 每个 control step 记录 `q_actual`、`qdot_actual`、`qddot_actual`、`computed_torque`、`applied_torque`；
- 对每个球铰轴拟合：

$$
\tau
\approx
J\ddot q + B\dot q + \tau_{\mathrm{load}}
$$

已完成一次正式导出：

```text
results/stage1_ball_joint_identification/flat_drive_lift_18env_1800_raw.csv
results/stage1_ball_joint_identification/flat_drive_lift_18env_1800_fit_results.csv
results/stage1_ball_joint_identification/flat_drive_lift_18env_1800_tau_v_metrics.csv
results/stage1_ball_joint_identification/flat_drive_lift_18env_1800_summary.json
```

已使用命令：

```text
env TERM=xterm MPLCONFIGDIR=/tmp/matplotlib OMNI_KIT_ACCEPT_EULA=YES \
/home/ubuntu/IsaacLab/isaaclab.sh -p scripts/identify_ball_joint_dynamics.py \
  --task CompleteCar-Stage1 \
  --num_envs 18 \
  --steps 1800 \
  --warmup_steps 180 \
  --drive_action 0.15 \
  --amplitude_rad 0.20 \
  --frequency_hz 0.25 \
  --terrain_replay_columns flat \
  --terrain_level 0 \
  --out_dir ../results/stage1_ball_joint_identification \
  --prefix flat_drive_lift_18env_1800
```

本次辨识结果显示：

- 六轴拟合得到的 $J$ 大致在 `0.03 ~ 0.08 kg*m^2`；
- 但 $R^2$ 只有约 `0.02 ~ 0.05`；
- 部分 $B$ 为负，说明单轴线性模型无法充分解释“行驶 + 抬升 + 地面接触 + 多体耦合”下的力矩变化。

因此，这批结果不能直接当成真实唯一参数，只能作为 MATLAB 扫描范围的约束依据。当前更合理的 MATLAB 范围是：

```text
J = 0.03, 0.05, 0.08, 0.10, 0.15 kg*m^2
B = 0.0, 0.5, 1.0, 2.0, 5.0 N*m*s/rad
tau_load = -10, -5, 0, 5, 10 N*m
```

`tau_v` 不是被控对象物理参数，不能通过动力学方程直接拟合；它是轮速分配中 `qdot_alloc = LPF(qdot_actual)` 的滤波设计参数。本次 `tau_v` 评估显示：

| `tau_v` | 速度粗糙度降低比例 | `qdot_alloc - qdot_actual` RMSE |
|---:|---:|---:|
| `0.03 s` | `0.641` | `0.134 rad/s` |
| `0.05 s` | `0.765` | `0.165 rad/s` |
| `0.08 s` | `0.845` | `0.187 rad/s` |

所以第一版可以继续把 `tau_v = 0.03 ~ 0.05 s` 作为主候选；`0.08 s` 更平滑但滞后更大。

## 6. MATLAB 动力学模型

第一版采用六个独立单轴模型。六个轴使用同一组统一增益 $K_p,K_d$，不做分关节 gain。

单轴动力学：

$$
J\ddot q
=
\tau
-
B\dot q
-
\tau_{\mathrm{load}}
$$

控制目标：

$$
q_{\mathrm{target}}
=
\operatorname{clip}
\left(
q^d,
q_{\mathrm{lower}},
q_{\mathrm{upper}}
\right)
$$

PD drive：

$$
\tau_{\mathrm{raw}}
=
K_p(q_{\mathrm{target}}-q)
-
K_d\dot q
$$

力矩限幅：

$$
\tau
=
\operatorname{clip}
\left(
\tau_{\mathrm{raw}},
-\tau_{\max},
\tau_{\max}
\right)
$$

速度限幅：

$$
\dot q
\leftarrow
\operatorname{clip}
\left(
\dot q,
-\dot q_{\max},
\dot q_{\max}
\right)
$$

轮速分配用速度：

$$
\dot q_{\mathrm{alloc},k}
=
(1-\alpha_v)\dot q_{\mathrm{alloc},k-1}
+
\alpha_v \dot q_k
$$

$$
\alpha_v
=
1-\exp
\left(
-\frac{\Delta t_c}{\tau_v}
\right)
$$

注意：这里的 $\dot q_{\mathrm{alloc}}$ 是 MATLAB 模型中模拟的新链路 allocator 输入。旧链路中的 $\dot q_{\mathrm{cmd}}=K(q^d-q)$ 只作为对照信号，不再作为主方案输入。

## 7. 时间步和固定限制

当前源码配置：

| 参数 | 当前值 | 说明 |
|---|---:|---|
| `control.sim_dt` | `1/120 s` | Isaac physics step |
| `control.decimation` | `4` | 每四个 physics step 更新一次 RL 控制 |
| `control.control_dt` | `1/30 s` | 控制周期 |
| `ball_joint_effort_limit_sim` | `60 N*m` | 球铰 effort limit |
| `ball_joint_velocity_limit_sim` | `2 rad/s` | 球铰 velocity limit |

MATLAB 第一版应使用：

```text
dt_sim = 1/120 s
dt_ctrl = 1/30 s
tau_max = 60 N*m
qdot_max = 2 rad/s
```

如果后续 Isaac 配置改变，MATLAB 参数必须同步改，不允许继续沿用旧的 `1/240 s` 或 `20 N*m`。

## 8. 输入工况

### 8.1 主工况：真实 policy 轨迹

主工况来自 `model_699.pt` 在 Stage1 地形上的回放导出。至少包含：

| 工况 | 目的 |
|---|---|
| `flat` | 检查新 PD 参数是否破坏平地动作平滑性 |
| `stairs_down_col05_highrow` | 检查下台阶时 pitch 和回中响应 |
| `stairs_down_col07_highrow` | 检查高 row 下台阶的更强目标变化 |
| `obstacles_col08_highrow` | 检查最高难度障碍下 policy 目标是否被执行 |
| `obstacles_col09_midrow` | 检查中等难度障碍处卡滞 / recovery 相关目标 |

每个工况至少导出 `10 ~ 20 s`，优先选择包含明显球铰目标变化和通过失败 / 卡滞的片段。

选择片段时优先满足：

```text
abs(q_desired - q_position_target_old) > 0.10 rad
```

或：

```text
abs(q_desired - q_actual) > 0.15 rad
```

### 8.2 辅助工况：人工目标

人工阶跃只作为 sanity check，不作为主结论依据。

| 工况 | 数值 | 目的 |
|---|---|---|
| 小阶跃 | `0 -> 0.05 rad` | 看小动作是否过慢 |
| 中阶跃 | `0 -> 0.20 rad` | 对应当前主要误差量级 |
| 大阶跃 | `0 -> 0.50 rad` | 看限位附近饱和和稳定性 |
| 释放 | `0 -> 0.25 rad -> 0` | 看回中是否平滑 |
| 正弦 | `0.2*sin(2*pi*f*t)`，`f=0.5,1,2,3 Hz` | 看频率响应 |

如果人工工况和真实 policy 工况结论冲突，以真实 policy 工况为准。

## 9. 统一增益扫描

第一版采用统一增益：

$$
K_{p,z}=K_{p,y}=K_{p,x}=K_p
$$

$$
K_{d,z}=K_{d,y}=K_{d,x}=K_d
$$

也就是说六个球铰轴共享同一个 $K_p,K_d$。这样可以保持底层配置简单，避免在 MATLAB 结果还不充分时引入分轴调参。

建议扫描：

| 参数 | 候选 |
|---|---|
| $K_p$ | `120, 160, 220, 320, 500, 800, 1000` |
| $K_d$ | `10, 16, 24, 32, 48, 64` |
| $J$ | `0.03, 0.05, 0.10, 0.20, 0.40 kg*m^2` |
| $B$ | `0.0, 0.5, 1.0` |
| $\tau_{\mathrm{load}}$ | `-15, -10, -5, 0, 5, 10, 15 N*m` |
| $\tau_v$ | `0.03, 0.05, 0.08 s` |

固定：

```text
tau_max = 60 N*m
qdot_max = 2 rad/s
dt_sim = 1/120 s
dt_ctrl = 1/30 s
```

当前 `Kp=1000, Kd=10` 必须保留为压力测试基线。它不是推荐值，而是用于量化“当前 gain 直接 target 后会不会长期饱和和抖动”。

初始优先关注两类候选：

| 类型 | 参数 |
|---|---|
| 保守候选 | `Kp=160, Kd=16` |
| 中等候选 | `Kp=320, Kd=32` |

最终选择以真实 policy 轨迹指标为准。

## 10. 观察信号

每个候选参数必须画出以下曲线。

### 10.1 每个关节的核心曲线

| 信号 | 含义 |
|---|---|
| `q_desired` | 真实 policy 目标 |
| `q_position_target_old` | 旧 planner 下发目标 |
| `q_actual_old` | Isaac 旧链路实际位置 |
| `q_target_new` | 新链路下发目标，等于 clamp 后的 `q_desired` |
| `q_sim_new` | MATLAB 预测的新链路实际位置 |
| `qdot_actual_old` | Isaac 旧链路实际速度 |
| `qdot_sim_new` | MATLAB 预测的新链路实际速度 |
| `qdot_cmd_old` | 旧 planner 速度 |
| `qdot_alloc_new` | 新链路 allocator 使用的速度 |
| `tau_sim_new` | MATLAB 预测力矩 |
| `sat_flag` | 力矩是否接近饱和 |

### 10.2 汇总曲线

| 信号 | 含义 |
|---|---|
| `mean_abs_target_gap_old` | 旧链路 `abs(q_desired - q_position_target_old)` 的六轴均值 |
| `mean_abs_tracking_error_old` | 旧链路 `abs(q_desired - q_actual_old)` 的六轴均值 |
| `mean_abs_tracking_error_new` | 新链路 `abs(q_target_new - q_sim_new)` 的六轴均值 |
| `max_abs_qdot_new` | 新链路六轴最大速度 |
| `sat_ratio_new` | 新链路六轴力矩饱和比例 |
| `qdot_alloc_smoothness` | allocator 速度平滑性 |

## 11. 评价指标

### 11.1 单关节指标

| 指标 | 说明 | 建议 |
|---|---|---|
| `rms_target_error_new` | `q_target_new - q_sim_new` 的 RMS | 越小越好 |
| `p95_target_error_new` | 95 分位误差 | 应明显低于旧链路 `q_desired - q_actual_old` |
| `max_abs_qdot_new` | 最大角速度 | 不应长期贴近 `2 rad/s` |
| `qdot_limit_rate` | `abs(qdot) > 0.98*qdot_max` 比例 | 越低越好 |
| `sat_ratio` | `abs(tau) > 0.98*tau_max` 比例 | 中等目标下不应长期高于 `0.3` |
| `oscillation_score` | 速度换向次数或高频能量 | 不能出现持续振荡 |
| `smoothness_cost` | `mean(diff(qdot)^2)` | 越低越平滑 |
| `qdot_alloc_rmse` | `qdot_alloc_new - qdot_sim_new` 的 RMS | 越小越好 |

### 11.2 真实轨迹对比指标

| 指标 | 说明 |
|---|---|
| `old_gap_mean` | 旧链路 `abs(q_desired - q_position_target_old)` 均值 |
| `old_error_mean` | 旧链路 `abs(q_desired - q_actual_old)` 均值 |
| `new_error_mean` | MATLAB 新链路 `abs(q_target_new - q_sim_new)` 均值 |
| `error_reduction_ratio` | `(old_error_mean - new_error_mean) / old_error_mean` |
| `new_vs_old_qdot_ratio` | 新旧速度幅值比例 |
| `new_saturation_risk` | 新链路饱和风险等级 |

期望：

```text
new_error_mean < old_error_mean
sat_ratio 不长期接近 1
qdot_limit_rate 不长期接近 1
oscillation_score 无明显高频振荡
```

如果 `new_error_mean` 降低，但 `sat_ratio` 和 `qdot_limit_rate` 很高，说明是靠饱和硬拉，不应直接采用。

## 12. MATLAB 实验流程

### 12.1 第一步：导出 IsaacLab 真实轨迹

用最新 Stage1 policy 回放，导出逐 control step CSV。

已使用的导出命令：

```text
env TERM=xterm MPLCONFIGDIR=/tmp/matplotlib OMNI_KIT_ACCEPT_EULA=YES \
/home/ubuntu/IsaacLab/isaaclab.sh -p scripts/export_ball_joint_policy_trace.py \
  --task CompleteCar-Stage1 \
  --checkpoint logs/rsl_rl/complete_car_stage1/2026-05-09_16-48-52_stage1_sec14_tune_v1_128env_700iter/model_699.pt \
  --num_envs 18 \
  --steps 1200 \
  --warmup_steps 120 \
  --terrain_replay_columns flat,stairs_down,discrete_obstacles \
  --terrain_level_by_name flat=0,stairs_down=11,discrete_obstacles=11 \
  --out_dir ../results/stage1_ball_joint_pd_matlab/raw_traces \
  --prefix sec14_model699_flat_stairs_down_obstacles
```

本次导出使用 `18` 个 env：`col00 flat` 为 row `0`，`col05/06/07 stairs_down` 为 row `11`，`col08/09 discrete_obstacles` 为 row `11`，每列约 `3` 个 env。输出不是 TensorBoard iteration 均值，而是逐 control step 的真实数据。

### 12.2 第二步：MATLAB 加载真实轨迹

MATLAB 加载：

```matlab
trace = load_isaac_ball_joint_trace("results/stage1_ball_joint_pd_matlab/raw_traces/sec14_model699_obstacles_col08_highrow.csv");
```

每条 trace 内部应整理为：

```text
trace.t
trace.q_desired     % N x 6
trace.q_target_old  % N x 6
trace.q_actual_old  % N x 6
trace.qdot_old      % N x 6
trace.qdot_cmd_old  % N x 6
```

### 12.3 第三步：统一增益扫参

对每组统一 $K_p,K_d$，对六个轴同时仿真：

```matlab
params.Kp = 320;
params.Kd = 32;
params.tau_max = 60;
params.qdot_max = 2;
params.dt_sim = 1/120;
params.dt_ctrl = 1/30;
params.tau_v = 0.05;
```

输出：

```text
q_sim_new      % N x 6
qdot_sim_new   % N x 6
qdot_alloc_new % N x 6
tau_sim_new    % N x 6
```

### 12.4 第四步：跨工况评分

每个候选参数必须同时通过：

- flat 不抖；
- stairs down 不长期饱和；
- obstacles 的真实 policy 大目标能明显跟踪；
- `qdot_alloc_new` 平滑，不比旧 `qdot_cmd_old` 更尖锐；
- 六个轴统一 gain 下没有某一类轴明显失控。

如果只有某一地形好，其他地形明显恶化，不作为第一版参数。

## 13. 选择规则

最终候选必须满足：

1. 真实 policy 轨迹上 `new_error_mean` 明显小于 `old_error_mean`。
2. `sat_ratio` 不长期接近 `1.0`。
3. `qdot_limit_rate` 不长期接近 `1.0`。
4. 不出现持续振荡。
5. flat 工况下响应平滑。
6. obstacles / stairs down 工况下能明显跟随大目标。
7. 使用统一 $K_p,K_d$，不做分关节特殊调参。

推荐第一轮候选优先从以下组合中选：

```text
Kp=160, Kd=16
Kp=220, Kd=24
Kp=320, Kd=32
Kp=500, Kd=48
```

`Kp=1000, Kd=10` 只作为压力测试。如果它在真实轨迹下高饱和或高振荡，就证明当前 gain 不适合 direct target。

## 14. MATLAB 后的 Isaac 验证

MATLAB 只负责预筛。确定 1 到 2 组统一 gain 后，下一步必须做 Isaac 短验证。

Isaac 验证内容：

1. 修改代码，让 `q_target = q_desired`。
2. `qdot_alloc = LPF(qdot_actual)`。
3. 使用 MATLAB 推荐的统一 `ball_joint_stiffness` 和 `ball_joint_damping`。
4. 保持 `ball_joint_effort_limit_sim = 60`。
5. 做 flat、stairs down、obstacles 短回放。

Isaac 验证通过后，才进入 Stage1 短训。

## 15. 与旧文档的关系

`docs/Stage1球铰PD控制MATLAB预仿真方案.md` 说明完整控制链路怎么改。

本文档是 MATLAB 实验执行标准。若两者冲突，MATLAB 实验部分以本文档为准，特别是以下三条：

1. MATLAB 输入优先使用 IsaacLab 真实 policy 逐步轨迹。
2. 第一版球铰 PD 增益采用统一 $K_p,K_d$，不做分关节增益。
3. 人工阶跃只作为 sanity check，不能替代真实策略轨迹。
