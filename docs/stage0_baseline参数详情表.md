# stage0_baseline参数详情表

本文档记录 `RL_Training/` 工作区内 `CompleteCar-Stage0` 的 baseline 配置、历史 `best_baseline_2` 训练 run、当前 `best_baseline5` 候选、底层运动学模型和运行边界。

当前 baseline 定义为：`best_baseline`。

当前详表对应的最新 Stage0 候选 run：`best_baseline5`。

`best_baseline_2` 不是一套新的环境设计。它是在当时 `best_baseline` 源码配置上，通过命令行覆盖 `run_name=best_baseline_2` 启动的一轮完整训练。因此：

- 环境配置以 run 内 `params/env.yaml` 和当前 active 源码为准。
- PPO 配置以 run 内 `params/agent.yaml` 为准。
- `best_baseline_2` 训练结果解释应以 run 内快照为准；当前 active Stage0 源码已在 2026-05-10 后加入 direct-target 球铰控制和 action-rate 平滑惩罚，不能再把当前源码回放视为该 run 的严格历史复现。

恢复基准来源：

- 训练结果版本：`2026-04-25_18-26-58_stage0_lowslip_gate_v1_700iter/model_699.pt`
- 结果说明文档：`results/stage0_lowslip_gate_v1_model699_detailed_result_config_motion_model_2026-04-28.md`
- 当前保留的关键口径差异之一：侧滑角仍使用 2026-04-28 后确认的当前口径，即 wheel local `Z` 作为水平侧向轴，低速分母使用 `max(abs(v_parallel), epsilon)`。
- 其余 Stage0 RL 配置、reward 结构和 PPO 语义恢复到上述 `model_699` 对应版本。
- 2026-05-10 新修改：Stage0 与 Stage1 的底层球铰和车轮控制参数统一，不再让底层运动学、机器人驱动配置随训练阶段变化；球铰控制链已取消旧的一阶位置规划器，policy 输出的 $q^d$ 直接作为球铰 position target，球铰 drive 统一为 `Kp=120, Kd=10, effort=60.0 N*m`。
- 2026-05-10 新修改：Stage0 启用 `action_rate_penalty`，用于约束 policy 连续控制步之间的动作跳变，重点压制球铰动作高频变化。
- 2026-05-10 新修改：Stage0 的 `progress_to_target` 新增中车 pitch gate，当前死区为 `1 deg`、尺度为 `π / 32 rad`，仅在 `|pitch| > 1 deg` 时降低正向 progress 奖励；Stage1 不启用该 gate，避免复杂地形训练时把中车强行约束为水平。

当前 `best_baseline5` 候选说明：

- run 目录：`RL_Training/logs/rsl_rl/complete_car_stage0/best_baseline5`
- 来源：原 `2026-05-10_21-31-37_stage0_pitch_gate_k32_from150_to700` 已按用户要求重命名为 `best_baseline5`
- Stage1 warm-start 来源 checkpoint：`model_75.pt`
- `model_75.pt` 窗口指标：`success = 1.0`、`episode length ≈ 630.1`、`LowSlip/combined_pass_rate ≈ 0.0799`、中车 pitch 约 `-1.41 deg`、球铰 tracking error 约 `0.0873 rad`
- 选择理由：相比同 run 后续 `model_150.pt`，`model_75.pt` 速度略慢，但 low-slip 更高、tracking error 更低，是当前本轮最平衡保存点；它已被转换为当前 Stage1 默认 warm-start：`RL_Training/logs/rsl_rl/complete_car_stage1/warmstart_best_baseline5_model75_terrain_features/model_0.pt`

当前 Stage0 主线特征：

- actor / critic 观测维度：`54 / 54`
- 动作维度：`8`
- 平地双 waypoint，每段 `10 m`
- reward 为历史 lowslip gate v1 的主结构，并新增 action rate 平滑惩罚
- 车轮执行链为 low-slip allocator 输出 torque target，不再使用 2026-04-28 中间版本的 direct wheel velocity target
- 纵滑率方向恢复为历史口径
- 侧滑角轴向保留当前修正口径
- timeout 恢复为 RSL-RL time-limit 语义：`is_finite_horizon = False`，PPO 允许 time-out bootstrap

## A. best_baseline_2 run 身份

| 项目 | 值 | 含义 |
|---|---|---|
| run name | `best_baseline_2` | 本轮训练名称 |
| run 目录 | `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-28_15-28-38_best_baseline_2` | 训练日志、参数、checkpoint 所在目录 |
| checkpoint | `model_699.pt` | 最终保存的模型 |
| 任务 | `CompleteCar-Stage0` | 平地 Stage0 双 waypoint 任务 |
| 设备 | `cuda:0` | 训练使用 GPU |
| 并行环境数 | `64` | 本轮训练实际并行环境数量 |
| 最大 iteration | `700` | 终端输出到 `699/700` 后正常结束 |
| 训练状态 | 正常完成 | 进程退出码为 `0` |

启动命令：

```bash
env TERM=xterm MPLCONFIGDIR=/tmp/matplotlib OMNI_KIT_ACCEPT_EULA=YES /home/ubuntu/IsaacLab/isaaclab.sh -p scripts/train.py --task CompleteCar-Stage0 --headless --device cuda:0 --num_envs 64 --max_iterations 700 --run_name best_baseline_2
```

运行结果边界：

- 末段任务完成质量较好：终端最后阶段基本保持 `success_rate=1.0`、`time_out_rate=0.0`。
- 末段运动不是近停滞：`v_parallel_abs` 约 `1.18-1.19 m/s`，`v_perp_abs` 约 `0.036-0.040 m/s`。
- 当前口径侧滑角末段约 `0.054-0.061 rad`，pitch 约 `-0.5 deg` 到 `-0.7 deg`。
- 主要缺陷是纵滑仍高：纵滑率约 `3.06-3.13`，`LowSlip/combined_pass_rate` 约 `0.087-0.092`。
- 因此该 run 可证明当前 baseline 能学出有效前向运动和稳定任务完成，但不能证明低纵滑控制已经成功。

## 0. 对应源码

| 模块 | 源码 |
|---|---|
| `best_baseline_2` 环境参数快照 | `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-28_15-28-38_best_baseline_2/params/env.yaml` |
| `best_baseline_2` PPO 参数快照 | `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-28_15-28-38_best_baseline_2/params/agent.yaml` |
| Stage0 配置覆盖 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py` |
| 共享配置主干 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py` |
| 环境主类 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py` |
| 动作映射 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/actions.py` |
| 观测拼接 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/observations.py` |
| 奖励函数 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py` |
| 终止条件 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/terminations.py` |
| 底层运动学和牵引分配 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/kinematics/wheel_speed_allocator.py` |
| PPO 配置 | `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/agents/rsl_rl_ppo_cfg.py` |

## 1. Stage0 总览

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `baseline_name` | `best_baseline` | 当前定义的 Stage0 基准配置名 |
| `run_name` | `best_baseline_2` | 本文档重点记录的最新完整训练 run 名 |
| task id | `CompleteCar-Stage0` | 平地 Stage0 任务 |
| `stage_name` | `stage0` | 环境内部阶段名 |
| `scene.num_envs` | `64` | 并行环境数量 |
| `scene.env_spacing` | `4.0 m` | 不同环境之间的间距 |
| `control.sim_dt` | `1 / 120 s` | PhysX 仿真步长 |
| `decimation` | `4` | 每 4 个 sim step 执行一次 RL action |
| `control.control_dt` | `1 / 30 s` | RL 控制周期 |
| `sim.physx.max_position_iteration_count` | `8` | 场景级 PhysX 位置约束求解迭代次数 |
| `sim.physx.max_velocity_iteration_count` | `4` | 场景级 PhysX 速度约束求解迭代次数，用于轮地摩擦、碰撞冲击等速度层约束 |
| `robot.articulation.solver_position_iteration_count` | `8` | 机器人 articulation root 位置约束求解迭代次数 |
| `robot.articulation.solver_velocity_iteration_count` | `4` | 机器人 articulation root 速度约束求解迭代次数；已与 Stage0 场景级 velocity iteration 对齐 |
| `episode_length_s` | `40.0 s` | 单个 episode 最大时长 |
| `max_episode_length` | `1200` | `40 / (1 / 30)` 个控制步 |
| `is_finite_horizon` | `False` | timeout 作为 time-limit 输出给 RSL-RL，PPO 会执行 bootstrap |
| `terrain.enabled` | `False` | 不启用 terrain generator |
| `terrain.mode` | `plane` | 平地 |
| `curriculum.enabled` | `False` | 不启用课程学习 |
| `observations.noise.enabled` | `False` | 不注入观测噪声 |
| `randomization.enable_action_randomization` | `False` | 不启用 action 随机化 |

## 2. 命令与 waypoint

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `commands.num_commands` | `4` | 相对目标命令维度 |
| `commands.num_waypoints_per_episode` | `2` | 每个 episode 有两个连续 waypoint |
| `commands.resampling_time` | `40.0 s` | 与 episode 时长一致，不做中途短周期重采样 |
| `commands.goal_distance` | `10.0 m` | 每段 waypoint 名义距离 |
| `commands.goal_direction_max_deg` | `30.0 deg` | 每段目标方向相对当前朝向的最大偏角 |
| `commands.min_segment_turn_deg` | `0.0 deg` | 最小转角下限 |
| `commands.goal_heading_delta_max_deg` | `0.0 deg` | 目标 heading 不额外偏离目标点视线方向 |
| `commands.zero_command` | `False` | 不生成原地目标 |
| `commands.rel_standing_envs` | `0.0` | 不随机生成 standing env |

`relative_goal_commands` 的 4 个分量：

| 分量 | 维度 | 含义 |
|---|---:|---|
| `goal_rel_x` | `1` | 当前 active waypoint 在车体系下的 x 相对位置 |
| `goal_rel_y` | `1` | 当前 active waypoint 在车体系下的 y 相对位置 |
| `goal_rel_z` | `1` | 当前 active waypoint 相对车体高度 |
| `goal_rel_heading` | `1` | 当前 waypoint 视线角，等价于 `atan2(goal_rel_y, goal_rel_x)` |

## 3. 动作空间

总动作维度为 `8`。

| 动作分量 | 维度 | 映射后物理含义 |
|---|---:|---|
| `actions[:, 0]` | `1` | 期望底盘前向速度命令 |
| `actions[:, 1]` | `1` | 期望底盘 yaw rate 命令 |
| `actions[:, 2:8]` | `6` | 两组等效球铰的目标姿态 |

底盘动作映射参数：

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `control.base_forward_velocity_max` | `2.0 m/s` | policy 第一维动作的速度幅值上限 |
| `control.base_yaw_rate_max` | `2.0 rad/s` | policy 第二维动作的 yaw rate 幅值上限 |
| `control.base_allow_reverse` | `True` | 允许 policy 输出倒车速度命令 |

2026-05-09 已重新核对并同步当前 Stage0 源码：`complete_car_stage0_cfg.py` 中 `control.base_allow_reverse = True`，与历史 `best_baseline_2` 的 `params/env.yaml` 口径一致。

当前 Stage0 使用：

$$
v_x^d = a_0 \cdot 2.0
$$

$$
\omega_z^d = a_1 \cdot 2.0
$$

球铰动作顺序：

| 序号 | 关节名 | 含义 |
|---:|---|---|
| 1 | `spm1_platform_joint_z` | 前等效球铰 z 轴转动 |
| 2 | `spm1_platform_joint_y` | 前等效球铰 y 轴转动 |
| 3 | `spm1_platform_joint_x` | 前等效球铰 x 轴转动 |
| 4 | `spm2_platform_joint_z` | 后等效球铰 z 轴转动 |
| 5 | `spm2_platform_joint_y` | 后等效球铰 y 轴转动 |
| 6 | `spm2_platform_joint_x` | 后等效球铰 x 轴转动 |

球铰 action 按 lower / upper limit 与默认零位线性映射为目标姿态 $q^d$。

## 4. 底层运动学与控制链

当前 `best_baseline` 恢复为历史 lowslip gate v1 的低层力矩链路：

1. policy 输出 `8` 维 action。
2. 前两维映射为平面命令 $u_v^d = [v_x^d, \omega_z^d]^T$。
3. 后六维映射为球铰目标姿态 $q^d$。
4. 球铰位置目标直接使用 $q^d$ 的限幅结果 $q_{target}$。
5. 球铰驱动只下发 position target $q_{target}$。
6. low-slip 平面命令整形器根据接触权重和轮心侧向速度代价计算 $u_v^*$。
7. allocator 根据实际球铰姿态 $q$、命令姿态变化率 $\dot q^{cmd}$ 与 $u_v^*$ 计算各轮滚动速度参考 $\Omega_j^{ref}$。
8. 轮级 traction allocator 根据 $\Omega_j^{ref}$、实际轮速、纵滑率和接触权重计算车轮 torque target。
9. 车轮驱动最终下发 effort target，不下发 velocity target。

当前不再使用的中间版本逻辑：

| 逻辑 | 当前是否 active | 说明 |
|---|---|---|
| 直接 `set_joint_velocity_target()` 控制车轮 | 否 | 已恢复为 wheel effort target |
| no-progress reward | 否 | 不进入 `REWARD_TERM_NAMES` |
| timeout fixed penalty reward | 否 | 不进入 `REWARD_TERM_NAMES` |
| load equalization reward | 否 | 不进入 `REWARD_TERM_NAMES` |
| env 层 qddot 轨迹器传入 allocator | 否 | 当前使用 direct target 和实际球铰角速度低通 |

### 4.1 低层几何参数

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `a_x` | `0.25633374 m` | 前、后连接点相对中车体原点的 x 向偏置绝对值 |
| `b_f` | `0.30654739 m` | 前车体轮心局部 x 向安装偏置 |
| `b_r` | `0.30633826 m` | 后车体轮心局部 x 向安装偏置 |
| `l1` | `-0.00989449 m` | 前车体轮心局部 x 基准 |
| `l2` | `0.00000932 m` | 中车体轮心局部 x 基准 |
| `l3` | `0.00968251 m` | 后车体轮心局部 x 基准 |
| `d1` | `0.539 m` | 前车体左右轮距，按当前实测轮距统一修正 |
| `d2` | `0.539 m` | 中车体左右轮距，按当前实测轮距统一修正 |
| `d3` | `0.539 m` | 后车体左右轮距，按当前实测轮距统一修正 |
| `h1` | `-0.043083285 m` | 前车体轮心局部 z 偏置 |
| `h2` | `-0.02578188 m` | 中车体轮心局部 z 偏置 |
| `h3` | `-0.043100655 m` | 后车体轮心局部 z 偏置 |
| `r_wheel` / `control.wheel_radius` | `0.19 m` | 车轮半径 |

### 4.2 球铰 direct target 与 actuator

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `control.ball_joint_stiffness` | `120.0 N*m/rad` | PhysX 球铰 position drive 刚度；来自 MATLAB 真实轨迹扩展扫参推荐 |
| `control.ball_joint_damping` | `10.0 N*m*s/rad` | PhysX 球铰 position drive 阻尼；来自 MATLAB 真实轨迹扩展扫参推荐 |
| `control.ball_joint_effort_limit_sim` | `60.0 N*m` | 球铰驱动力矩上限；2026-05-10 起由 `20.0` 提高到 `60.0` |
| `control.ball_joint_velocity_limit_sim` | `2.0 rad/s` | 球铰速度限制 |
| `control.ball_joint_qdot_alloc_filter_tau_s` | `0.04 s` | 轮速分配使用的实际球铰角速度低通时间常数 |

球铰 active 执行链：

$$
q_{target} = \operatorname{clip}(q^d, q_{lower}, q_{upper})
$$

$$
qdot_{alloc,k} =
(1-\alpha_v)qdot_{alloc,k-1}+\alpha_v \dot q_{actual,k}
$$

$$
\alpha_v = 1 - \exp(-\Delta t / \tau_v)
$$

其中：

| 记号 | 含义 |
|---|---|
| $q^d$ | policy action 映射出的球铰目标姿态 |
| $q_{target}$ | 直接下发给 PhysX position drive 的球铰位置目标 |
| $\dot q_{actual}$ | IsaacLab 读取的球铰实际角速度 |
| $qdot_{alloc}$ | 轮速分配中姿态变化项使用的球铰角速度 |
| $\Delta t$ | `control.control_dt = 1 / 30 s` |
| $\tau_v$ | `control.ball_joint_qdot_alloc_filter_tau_s = 0.04 s` |

### 4.3 low-slip 平面命令整形

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `control.low_slip_lambda_tracking` | `1.0` | 保持接近 policy 平面命令的权重 |
| `control.low_slip_lambda_lateral` | `5.0` | 压低轮心名义侧向速度的权重；2026-05-10 起与 Stage1 统一 |
| `control.contact_force_off_threshold` | `0.01` | 接触权重为 0 的归一化法向力阈值 |
| `control.contact_force_on_threshold` | `0.08` | 接触权重为 1 的归一化法向力阈值 |

接触权重：

$$
C_j = \operatorname{clip}
\left(
\frac{F_{n,j} - F_{off}}{F_{on} - F_{off}},
0,
1
\right)
$$

其中：

| 记号 | 含义 |
|---|---|
| $F_{n,j}$ | 第 $j$ 个车轮归一化法向接触力 |
| $F_{off}$ | `contact_force_off_threshold` |
| $F_{on}$ | `contact_force_on_threshold` |
| $C_j$ | 第 $j$ 个车轮接触权重 |

底层运动学在中车体坐标系 `{B2}` 中计算。每个车轮都有三个核心几何量：

| 记号 | 源码变量 | 含义 |
|---|---|---|
| $p_j(q)$ | `wheel_positions[:, j]` | 第 $j$ 个轮心相对中车体原点的位置 |
| $t_j(q)$ | `rolling_directions[:, j]` | 第 $j$ 个车轮滚动方向 |
| $n_j(q)$ | `lateral_directions[:, j]` | 第 $j$ 个车轮侧向方向 |
| $J_{p,j}(q)$ | `position_jacobians[:, j]` | 轮心位置对六个球铰姿态的雅克比 |

中车两个轮的 $p_j$、$t_j$、$n_j$ 不随球铰变化；前车体和后车体的轮心位置、滚动方向、侧向方向由对应等效球铰欧拉角生成旋转矩阵后得到。

给定整车平面命令 $u=[v_x,\omega_z]^T$ 和球铰规划速度 $\dot q_{cmd}$，第 $j$ 个轮心名义速度为：

$$
v_j^{nom}
=
v_x e_x
+
\omega_z(e_z \times p_j)
+
J_{p,j}\dot q_{cmd}
$$

其中：

| 记号 | 含义 |
|---|---|
| $e_x$ | 中车体系前向单位向量 |
| $e_z$ | 中车体系竖直单位向量 |
| $e_z \times p_j$ | yaw rate 对轮心产生的平面旋转速度 |
| $J_{p,j}\dot q_{cmd}$ | 球铰姿态变化对轮心速度的贡献 |

low-slip 平面命令整形不是直接改 policy action，而是在低层求一个更利于低侧向速度的平面命令 $u^*$。源码对应 `shape_planar_command_for_low_slip()`。

其优化目标可写为：

$$
u^*
=
\arg\min_u
\lambda_{track}\|u-u^d\|^2
+
\lambda_{lat}
\sum_j
C_j
\left(
n_j^T v_j^{nom}(u,\dot q_{cmd})
\right)^2
$$

然后对 $u^*$ 按 `base_forward_velocity_max` 和 `base_yaw_rate_max` 做限幅。

含义：

- 第一项要求 $u^*$ 不要偏离 policy 想要的平面命令 $u^d$ 太多。
- 第二项惩罚接地车轮的名义侧向速度，接触权重 $C_j$ 越大，该轮越参与低侧滑整形。
- 当前 `lambda_tracking=1.0`、`lambda_lateral=5.0`，因此会明显优先压低接地轮侧向名义速度，但不会完全无视 policy 命令。

### 4.4 车轮参考速度与 torque target

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `control.wheel_joint_stiffness` | `0.0` | 车轮 position drive 刚度，当前不使用 |
| `control.wheel_joint_damping` | `0.0` | 车轮 velocity drive 阻尼，当前不使用 direct velocity drive |
| `control.wheel_joint_effort_limit_sim` | `20.0 N*m` | 车轮 torque target 限幅 |
| `control.wheel_joint_velocity_limit_sim` | `20.0 rad/s` | 车轮关节速度限制 |
| `control.wheel_torque_tracking_gain` | `2.0` | 轮速误差转力矩的比例增益 |
| `control.wheel_slip_feedback_gain` | `4.0` | 纵滑率反馈增益；2026-05-10 起与 Stage1 统一 |
| `control.wheel_slip_velocity_epsilon` | `0.1 m/s` | 纵滑率和侧滑角低速保护分母 |

车轮滚动速度参考：

$$
v_{\parallel,j}^{ref}
=
t_j^T v_j^{nom}(u^*,\dot q_{cmd})
$$

$$
\Omega_j^{ref}
=
\frac{v_{\parallel,j}^{ref}}{r}
$$

实际轮地速度误差：

$$
\Delta v_j
=
r\Omega_j - v_{\parallel,j}
$$

车轮 torque target：

$$
\tau_{0,j} = k_{\Omega}(\Omega_j^{ref} - \Omega_j)
$$

$$
\tau_{cmd,j} =
\operatorname{clip}
\left(
C_j(\tau_{0,j} - k_{\kappa}\kappa_j),
-\tau_{max},
\tau_{max}
\right)
$$

其中：

| 记号 | 含义 |
|---|---|
| $\Omega_j^{ref}$ | 第 $j$ 个车轮参考角速度 |
| $\Omega_j$ | 第 $j$ 个车轮实际角速度 |
| $k_{\Omega}$ | `wheel_torque_tracking_gain` |
| $\kappa_j$ | 第 $j$ 个车轮纵滑率 |
| $k_{\kappa}$ | `wheel_slip_feedback_gain` |
| $C_j$ | 第 $j$ 个车轮接触权重 |
| $\tau_{max}$ | `wheel_joint_effort_limit_sim` |

## 5. 纵滑率与侧滑角定义

### 5.1 纵滑率

当前已恢复历史 `model_699` 方向：

$$
\kappa_j =
\frac{
v_{\parallel,j} - r\Omega_j
}{
\max(|v_{\parallel,j}|,\epsilon)
}
$$

其中：

| 记号 / 参数 | 源码变量 | 含义 |
|---|---|---|
| $\kappa_j$ | `wheel_longitudinal_slip[:, j]` | 第 $j$ 个车轮纵向滑移率 |
| $v_{\parallel,j}$ | `rolling_speed_actual[:, j]` / `v_x` | 第 $j$ 个轮心速度在车轮滚动方向上的投影 |
| $r$ | `wheel_radius` | 车轮半径，当前 `0.19 m` |
| $\Omega_j$ | `wheel_joint_vel[:, j]` | 第 $j$ 个车轮实际角速度 |
| $\epsilon$ | `wheel_slip_velocity_epsilon` / `wheel_slip_epsilon` | 低速分母保护，当前 `0.1 m/s` |

方向解释：

- 若 $v_{\parallel,j} > r\Omega_j$，则 $\kappa_j > 0$。
- 若 $v_{\parallel,j} < r\Omega_j$，则 $\kappa_j < 0$。
- reward 和日志中的 pass rate 多数使用 $|\kappa_j|$，但轮级 torque feedback 使用带符号的 $\kappa_j$。

### 5.2 侧滑角

侧滑角保留当前修正口径，不恢复 2026-04-25 历史旧轴向口径。

当前口径：

$$
\alpha_j =
\operatorname{atan2}
\left(
v_{\perp,j},
\max(|v_{\parallel,j}|,\epsilon)
\right)
$$

其中：

| 记号 / 参数 | 源码变量 | 含义 |
|---|---|---|
| $\alpha_j$ | `wheel_slip_angle[:, j]` | 第 $j$ 个车轮侧滑角 |
| $v_{\parallel,j}$ | `v_x` | 轮心速度在 wheel local `X` 滚动方向上的投影 |
| $v_{\perp,j}$ | `v_y` / `lateral_speed_actual` | 轮心速度在 wheel local `Z` 水平侧向轴上的投影 |
| $\epsilon$ | `wheel_slip_epsilon` | 低速保护分母，当前 `0.1 m/s` |
| `wheel_slip_angle_clip_rad` | `pi / 2` | 观测侧滑角裁剪范围 |

口径说明：

- wheel local `X`：车轮滚动前进方向。
- wheel local `Z`：当前确认后的水平侧向/轮轴方向。
- 旧 `model_699` 原始 TensorBoard 使用 wheel local `Y`，该轴接近竖直方向，因此当前代码不再使用旧侧滑角轴向。

## 6. 观测空间

actor 与 critic 当前都使用同一组 `54` 维观测。

| 分量 | 维度 | 含义 |
|---|---:|---|
| `ball_joint_pos` | `6` | 六个等效球铰当前位置 |
| `ball_joint_vel` | `6` | 六个等效球铰角速度 |
| `base_lin_vel` | `3` | 根部线速度，body frame |
| `base_ang_vel` | `3` | 根部角速度，body frame |
| `wheel_joint_vel` | `6` | 六个车轮角速度 |
| `wheel_longitudinal_slip` | `6` | 六轮纵滑率，使用当前恢复后的历史方向 |
| `wheel_slip_angle` | `6` | 六轮侧滑角，使用当前 local `Z` 口径 |
| `wheel_normal_contact_force` | `6` | 六轮归一化法向接触力 |
| `relative_goal_commands` | `4` | 当前 waypoint 相对位置与视线角 |
| `last_actions` | `8` | 上一步 policy action |

观测缩放：

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `observations.clip_observations` | `100.0` | actor / critic 输出观测裁剪范围 |
| `observations.wheel_slip_epsilon` | `0.1` | 观测侧纵滑低速保护 |
| `scales.base_lin_vel` | `1.0` | 根部线速度缩放 |
| `scales.base_ang_vel` | `1.0` | 根部角速度缩放 |
| `scales.ball_joint_pos` | `1.0` | 球铰位置缩放 |
| `scales.ball_joint_vel` | `1.0` | 球铰速度缩放 |
| `scales.ball_joint_target_error` | `1.0` | 球铰目标误差缩放 |
| `scales.wheel_joint_vel` | `1.0` | 车轮角速度缩放 |
| `scales.wheel_longitudinal_slip` | `1.0` | 纵滑率缩放 |
| `scales.wheel_slip_angle` | `1.0` | 侧滑角缩放 |
| `scales.wheel_normal_contact_force` | `1.0` | 归一化接触力缩放 |
| `scales.commands` | `1.0` | 目标命令缩放 |
| `scales.last_action` | `1.0` | 上一步 action 缩放 |

## 7. Reward 结构

当前 Stage0 非零 active reward 项为 7 项：

```text
distance_to_target
progress_to_target
reached_target
far_from_target
angle_diff
slip_penalty
action_rate_penalty
```

reward 参数：

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `target_position_tolerance` | `0.5 m` | waypoint 命中半径 |
| `target_yaw_tolerance_deg` | `5.7296 deg` | 配置保留项，当前 success 代码不使用 yaw tolerance |
| `distance_to_target_denominator_scale` | `0.01` | 距离型 shaping 分母系数 |
| `distance_to_target_weight` | `6.0` | 距离型 shaping 权重 |
| `progress_to_target_clip_m` | `0.25 m` | 单步 progress 裁剪幅值 |
| `progress_to_target_relax_radius_m` | `4.0 m` | 近目标区域负 progress 截断半径 |
| `progress_to_target_weight` | `8.0` | progress reward 权重 |
| `reached_target_base_reward` | `2.0` | 命中 waypoint 的基础奖励 |
| `reached_target_weight` | `6.0` | waypoint 命中奖励权重 |
| `far_from_target_margin` | `6.0 m` | 远离失败距离裕度 |
| `far_from_target_weight` | `-2.0` | 远离目标惩罚权重 |
| `angle_diff_weight` | `6.0` | 目标视线角 shaping 权重 |
| `slip_penalty_weight` | `-2.0` | 滑移惩罚权重 |
| `slip_longitudinal_penalty_ratio` | `2.0` | 【2026-05-10 修改】纵滑率在滑移惩罚中的相对系数 |
| `slip_angle_penalty_ratio` | `1.0` | 【2026-05-10 修改】侧滑角在滑移惩罚中的相对系数 |
| `action_rate_penalty_weight` | `-50.0` | 【2026-05-10 新增】动作变化率惩罚权重；用于压制连续控制步之间的 policy action 跳变 |
| `action_rate_base_ratio` | `0.2` | 【2026-05-10 新增】底盘两维动作变化的相对权重 |
| `action_rate_joint_ratio` | `1.0` | 【2026-05-10 新增】六个球铰动作变化的相对权重 |
| `progress_gate_longitudinal_k` | `3.0` | progress gate 的纵滑尺度 |
| `progress_gate_slip_angle_scale_rad` | `1.5 rad` | progress gate 的侧滑角尺度 |
| `progress_gate_min_multiplier` | `0.25` | 正 progress 乘子的下限 |
| `progress_gate_max_multiplier` | `1.5` | 正 progress 乘子的上限 |
| `progress_pitch_gate_deadband_deg` | `1.0 deg` | 【2026-05-10 修改】中车 pitch gate 死区；死区内不影响正 progress |
| `progress_pitch_gate_k_rad` | `π / 32 rad` | 【2026-05-10 修改】中车 pitch gate 尺度；`|pitch| > 1 deg` 时正 progress 额外乘以 `exp(-0.5 * (|pitch| / k)^2)` |
| `low_slip_longitudinal_threshold` | `1.0` | low-slip 纵滑 pass rate 统计阈值 |
| `low_slip_angle_threshold_rad` | `0.35 rad` | low-slip 侧滑 pass rate 统计阈值 |

Stage0 pitch gate 的参数先依据 `2026-05-10_19-52-05_stage0_slip2_actionrate_m50_qmon_resume200_to_quality` 续训到 `model_300.pt` 附近的实际 reward 尺度确定。iteration `301` 的末 `25` 轮窗口中，`Reward/progress_to_target` 约 `+0.0238/step`，`Reward/slip_penalty` 约 `-0.00457/step`，中车 pitch 均值约 `-6.0 deg`。原第一版 `deadband = 2 deg`、`k = π / 16 rad = 11.25 deg` 在后续 `2026-05-10_20-39-29_stage0_pitch_gate_gauss_from150_to700` 中过于温和：训练到 `model_150.pt` 附近时 pitch 已接近 `-2.8 deg`，但 `ProgressGate/pitch_gate` 仍约 `0.96`，不足以压制“快速推进但中车前俯”的策略倾向。因此当前改为 `deadband = 1 deg`、`k = π / 32 rad = 5.625 deg`；在 `|pitch| = 3 deg` 时 gate 约 `0.867`，在 `6 deg` 时 gate 约 `0.567`，会更明确地降低前俯推进的正 progress 收益。

已删除的非 active reward 配置字段：

| 字段 | 删除原因 |
|---|---|
| `timeout_fixed_penalty` | 当前 timeout 只作为 PPO time-limit 处理，不再存在 timeout reward 项 |
| `timeout_distance_penalty_scale` | 当前 reward 不再按 timeout 距离扣分 |
| `progress_negative_scale` | 当前负 progress 不额外放大 |
| `no_progress_threshold_m` | 当前没有 no-progress penalty |
| `no_progress_weight` | 当前没有 no-progress penalty |
| `load_equalization_weight` | 当前没有 load equalization reward |
| `load_equalization_k` | 当前没有 load equalization reward |
| `load_equalization_target_shares` | 当前没有 load equalization reward |

已删除的非 active 底层控制字段和诊断字段：

| 字段 / 代码路径 | 删除原因 |
|---|---|
| `ball_joint_planner_qddot_limits` | env 层 qddot 轨迹器已不再运行 |
| `ball_joint_planner_track_error_limit` | env 层 qddot 轨迹器已不再运行 |
| `planned_ball_joint_pos/planned_ball_joint_rate` allocator 兼容入口 | 当前已改为 direct target 与 `qdot_alloc` 显式输入 |
| `g_kappa/g_alpha` 诊断输出 | 当前轮级力矩公式不再使用纵滑/侧滑衰减因子，保留固定 `1.0` 日志会误导判断 |

### 7.1 progress gate

目标距离变化：

$$
\Delta d = d_{prev} - d_{now}
$$

裁剪后：

$$
\Delta d_c = \operatorname{clip}(\Delta d, -0.25, 0.25)
$$

若 $d_{now} \le 4.0$，则负 progress 被截断为 0：

$$
\Delta d_c = \max(\Delta d_c, 0)
$$

正负 progress：

$$
p^+ = \frac{\max(\Delta d_c, 0)}{d_{goal}}
$$

$$
p^- = \frac{\min(\Delta d_c, 0)}{d_{goal}}
$$

纵滑 gate：

$$
G_{\kappa}
=
\exp
\left(
-0.5
\sum_j
\left(
\frac{\kappa_j}{3.0}
\right)^2
\right)
$$

侧滑角 gate：

$$
G_{\alpha}
=
\prod_j
\left[
0.5\cos
\left(
\operatorname{clip}
\left(
\frac{\pi|\alpha_j|}{1.5},
0,
\pi
\right)
\right)
+0.5
\right]
$$

综合 gate 使用平均值：

$$
G = 0.5(G_{\kappa} + G_{\alpha})
$$

progress multiplier：

$$
M = 0.25 + (1.5 - 0.25)G
$$

最终 progress 内部量：

$$
p = Mp^+ + p^-
$$

进入总 reward：

$$
r_{progress} = 8.0p
$$

### 7.2 其他 reward 项

距离 shaping：

$$
r_{dist}
=
6.0
\frac{
1
}{
1 + 0.01d_{now}^2
}
\frac{1}{T}
$$

命中 waypoint：

$$
r_{hit}
=
6.0
\cdot
1_{hit}
\cdot
2.0
\cdot
\frac{T-t}{T}
$$

远离目标：

$$
r_{far}
=
-2.0
\cdot
1_{d_{now} > 10.0 + 6.0}
$$

目标视线角 shaping：

$$
r_{angle}
=
6.0
\cdot
\frac{1}{1 + |\theta_{goal}|}
\cdot
\frac{1}{T}
$$

滑移惩罚：

$$
r_{slip}
=
-2.0
\cdot
\frac{
2.0\operatorname{mean}_j(|\kappa_j|)
+ 1.0\operatorname{mean}_j(|\alpha_j|)
}{T}
$$

动作变化率惩罚：

$$
\Delta a = a_t - a_{t-1}
$$

$$
w_a =
\begin{cases}
0.2, & \text{底盘前进 / 偏航动作} \\
1.0, & \text{六个球铰姿态动作}
\end{cases}
$$

$$
r_{action\_rate}
=
-50.0
\cdot
\frac{
\operatorname{mean}_i(w_{a,i}\Delta a_i^2)
}{T}
$$

其中：

| 记号 | 含义 |
|---|---|
| $d_{now}$ | 当前 active waypoint 的平面距离 |
| $d_{goal}$ | `goal_distance = 10.0 m` |
| $T$ | `max_episode_length = 1200` |
| $t$ | 当前 episode 控制步数 |
| $\theta_{goal}$ | `goal_rel_heading` |
| $\theta_{max}$ | `goal_direction_max_deg = 30 deg` |
| $a_t$ | 当前 policy action |
| $a_{t-1}$ | 上一个 control step 的 policy action |
| $v_{xy}$ | 车体根部 body frame 平面速度 |
| $v_{max}$ | `base_forward_velocity_max = 2.0 m/s` |

## 8. Termination 与 timeout

| 条件 | 当前语义 | 是否进入 `terminated` |
|---|---|---|
| `is_success` | 命中最后一个 waypoint，位置误差小于 `0.5 m` | 是 |
| `far_from_target` | 当前目标距离大于 `goal_distance + far_from_target_margin = 16.0 m` | 是 |
| `ball_joint_out_of_bounds` | 任一球铰超过 lower / upper limits | 是 |
| `time_out` | episode 达到 `1200` 步 | 否，作为 time-limit 输出 |

实际运行函数为 `compute_done_terms()` 和环境 `_get_dones()`：

- `terminated = is_success or far_from_target or ball_joint_out_of_bounds`
- `time_out = episode_length_buf >= max_episode_length - 1 and not is_success`
- 当前 `orientation_limit_deg`、`head_tail_roll_limit_deg`、`head_tail_pitch_limit_deg` 只存在于配置快照中，当前 `compute_done_terms()` 不读取它们，因此它们不是 `best_baseline_2` 的 active 终止条件。

PPO 语义：

- `is_finite_horizon = False`
- timeout 会进入 RSL-RL 的 time-limit bootstrap 处理
- 当前没有单独的 timeout reward penalty

球铰限位：

| 关节顺序 | lower | upper |
|---|---:|---:|
| `spm1_platform_joint_z` | `-0.6` | `0.6` |
| `spm1_platform_joint_y` | `-1.0` | `0.4` |
| `spm1_platform_joint_x` | `-0.5` | `0.5` |
| `spm2_platform_joint_z` | `-0.6` | `0.6` |
| `spm2_platform_joint_y` | `-1.0` | `0.4` |
| `spm2_platform_joint_x` | `-0.5` | `0.5` |

## 9. Reset 与初始状态

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `resets.root_pos` | `(0.0, 0.0, 0.30)` | 根部初始位置 |
| `resets.root_lin_vel` | `(0.0, 0.0, 0.0)` | 根部初始线速度 |
| `resets.root_ang_vel` | `(0.0, 0.0, 0.0)` | 根部初始角速度 |
| `resets.root_x_range` | `(-1.0, 1.0)` | reset x 位置随机范围 |
| `resets.root_y_range` | `(-1.0, 1.0)` | reset y 位置随机范围 |
| `resets.root_yaw_range` | `(0.0, 0.0)` | reset yaw 范围 |
| `resets.ball_joint_pos_range` | `(0.0, 0.0)` | 球铰位置随机扰动范围 |
| `resets.ball_joint_vel_range` | `(0.0, 0.0)` | 球铰速度随机扰动范围 |
| `resets.wheel_joint_pos_range` | `(0.0, 0.0)` | 车轮位置随机扰动范围 |
| `resets.wheel_joint_vel_range` | `(0.0, 0.0)` | 车轮速度随机扰动范围 |

## 10. PPO 配置

`best_baseline_2` run 内 `params/agent.yaml`：

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `experiment_name` | `complete_car_stage0` | 日志主目录 |
| `run_name` | `best_baseline_2` | 本轮训练实际 run 名，由命令行覆盖默认值 |
| 源码默认 `run_name` | `best_baseline` | 当前 Stage0 baseline 配置默认 run 名 |
| `seed` | `1` | 随机种子 |
| `num_steps_per_env` | `512` | 每个环境每轮 rollout 步数 |
| `rollout_steps_per_iteration` | `64 * 512 = 32768` | 每个 iteration 总采样量 |
| `max_iterations` | `700` | 默认最大训练轮数 |
| `save_interval` | `25` | checkpoint 保存间隔 |
| `logger` | `tensorboard` | 日志后端 |
| `resume` | `False` | 默认不续训 |
| `clip_actions` | `None` | runner 不额外裁剪 action |

网络：

| 部分 | 当前值 | 含义 |
|---|---|---|
| actor | `[256, 256]`, `relu` | policy MLP |
| critic | `[256, 256]`, `relu` | value MLP |
| obs normalization | `True` | actor / critic 均启用观测归一化 |
| distribution | `SquashedGaussianDistribution` | actor 动作分布 |
| `init_std` | `0.20` | 初始标准差 |
| `log_std_min` | `-4.0` | log std 下限 |
| `log_std_max` | `0.0` | log std 上限 |

PPO 超参数：

| 参数 | 当前值 | 含义 |
|---|---:|---|
| `num_learning_epochs` | `5` | 每批 rollout 重复优化次数 |
| `num_mini_batches` | `16` | 每轮优化切分的 mini-batch 数 |
| `learning_rate` | `1.0e-4` | 初始学习率 |
| `adam_eps` | `1.0e-5` | Adam epsilon |
| `schedule` | `adaptive` | 根据 KL 自适应学习率 |
| `desired_kl` | `0.008` | 目标 KL |
| `gamma` | `0.99` | 折扣因子 |
| `lam` | `0.95` | GAE lambda |
| `entropy_coef` | `5.0e-4` | 熵奖励权重 |
| `value_loss_coef` | `0.5` | value loss 权重 |
| `clip_param` | `0.2` | PPO ratio clip |
| `max_grad_norm` | `0.5` | 梯度裁剪阈值 |
| `use_clipped_value_loss` | `True` | 使用 clipped value loss |

## 11. 当前 baseline 的边界

`best_baseline` 的定义是工程基准，不等价于“低滑移控制已经成功”。

可作为证据的内容：

- Stage0 平地双 waypoint 任务可以被当前动作空间和低层力矩链路学会。
- 历史 `model_699` 训练达到接近满 waypoint 完成率。
- 当前代码保留了更合理的侧滑角轴向口径，避免继续使用旧 local `Y` 侧滑指标。

不能直接声称的内容：

- 不能把历史 TensorBoard 里的旧 `wheel_slip_angle` 当作真实水平侧滑角证据。
- 不能仅凭该 baseline 证明低滑移策略已经学成。
- 不能把 timeout 当作失败惩罚，因为当前恢复为 time-limit bootstrap 语义。
