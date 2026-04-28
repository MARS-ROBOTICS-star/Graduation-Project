# Stage0 0.5 m 双 waypoint 训练结果、RL 配置与底层运动模型说明

## 1. Run Identification

- 目标 run：`2026-04-25_13-37-33_stage0_tol05_turn2_gt_turn1_700iter`
- 运行名称：`stage0_tol05_turn2_gt_turn1_700iter`
- 训练任务：`CompleteCar-Stage0`
- 训练目录：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_13-37-33_stage0_tol05_turn2_gt_turn1_700iter/`
- Hydra 输出目录：`RL_Training/outputs/2026-04-25/13-37-33/`
- TensorBoard 导出目录：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-25_13-37-33_stage0_tol05_turn2_gt_turn1_700iter/tensorboard_export/`
- 已保存 checkpoint：`model_0.pt`、`model_100.pt`、`model_200.pt`
- 原计划训练轮数：`700`
- 实际停止位置：iteration `294`
- 当前文件系统未找到原始 Isaac Lab 日志 `/tmp/isaaclab/logs/isaaclab_2026-04-25_13-37-33.log`；本报告基于 run 内保存的 `params/env.yaml`、`params/agent.yaml`、Hydra 配置、TensorBoard 导出和该 run 保存的 git diff。

## 2. 一句话结论

这次训练证明：在平地 Stage0、双 waypoint、成功半径收紧到 `0.5 m`、第二段转向更强的设置下，8 维动作的 PPO policy 能够学到稳定完成两个 waypoint 的策略；但是该 run 没有保存最终满成功平台 checkpoint，并且当时的侧滑角日志使用旧轴向口径，因此它不能作为“低滑移协同控制已经学成”的证据。

## 3. 训练结果

### 3.1 训练是否成功

从 episode 结束口径看，这次训练是成功的。

| 指标 | step 0 | step 100 | step 200 | step 294 | 后 20 step 均值 |
|---|---:|---:|---:|---:|---:|
| `success_rate` | `0.000` | `0.000` | `0.928` | `1.000` | `1.000` |
| `time_out_rate` | `0.881` | `1.000` | `0.072` | `0.000` | `0.000` |
| `Train/mean_reward` | `-1.409` | `9.042` | `29.140` | `33.102` | `33.254` |
| `Train/mean_episode_length` | `253.765` | `2359.500` | `1264.800` | `750.390` | `736.619` |
| `episode/waypoints_completed` | `0.000` | `0.053` | `1.916` | `2.000` | `2.000` |
| `episode/waypoint_completion_pct` | `0.000%` | `2.637%` | `95.801%` | `100.000%` | `100.000%` |
| `episode/success_hit_pos_error` | - | - | `0.490 m` | `0.486 m` | `0.488 m` |

关键过程：

- 第一次 `success_rate = 1.0` 出现在 iteration `210`。
- iteration `250-257` 出现过连续 `8` 轮满成功。
- iteration `269-294` 连续 `26` 轮 `success_rate = 1.0` 且 `time_out_rate = 0.0`。
- 后 `40` step 的 `success_rate` 均值约为 `0.995`，说明最后阶段不是单点偶然成功。

### 3.2 为什么 mean episode length 后期下降不是坏事

这次训练早期的 episode length 会接近 `2399`，因为大量环境跑到 `40 s` timeout。后期 `mean_episode_length` 降到约 `750`，不是因为更早失败，而是因为 policy 更快完成两个 waypoint 后提前成功终止。

因此这轮应按如下逻辑解释：

- `time_out_rate` 从 `0.881` 降到 `0.0`，说明 timeout 失败消失。
- `success_rate` 从 `0.0` 升到 `1.0`，说明终止主要来自成功。
- `episode/waypoints_completed = 2`，说明不是只碰到第一个 waypoint，而是完成了双 waypoint。

### 3.3 step 级指标和 episode 级指标不要混淆

这次 run 同时记录了 step 级即时指标和 episode 结束指标。二者含义不同。

| 指标 | step 294 | 后 20 step 均值 | 正确解释 |
|---|---:|---:|---|
| `Tracking/active_segment_completion_pct` | `44.452%` | `44.228%` | 所有并行环境当前 active waypoint 段的即时平均进度。 |
| `Tracking/waypoints_completed_mean` | `0.512` | `0.491` | 当前训练 step 中所有环境平均已经完成几个 waypoint。 |
| `Tracking/episode_completion_pct` | `25.623%` | `24.532%` | 当前 step 中所有环境的即时 episode 完成比例。 |
| `episode/waypoints_completed` | `2.000` | `2.000` | episode 结束时，结束环境平均完成的 waypoint 数。 |
| `episode/waypoint_completion_pct` | `100.000%` | `100.000%` | episode 结束时的任务完成比例。 |

判断训练是否完成任务，应以 `episode/waypoints_completed`、`episode/waypoint_completion_pct`、`success_rate` 和 `time_out_rate` 为主。`Tracking/*` 受并行环境 reset、目标切换和新 episode 中间状态影响，不能直接当作 episode 完成率。

### 3.4 控制质量指标

| 指标 | step 0 | step 200 | step 294 | 后 20 step 均值 | 解释 |
|---|---:|---:|---:|---:|---|
| `wheel_longitudinal_slip_abs_mean_raw` | `9.073` | `3.241` | `2.966` | `3.002` | 纵向滑移从初期明显下降，但仍不低。 |
| `wheel_slip_angle_abs_mean_raw` | `0.518 rad` | `0.662 rad` | `0.709 rad` | `0.711 rad` | 该 run 使用旧轴向口径，不能当作真实水平侧滑角。 |
| `wheel_speed_reference_abs_mean_raw` | `1.840 rad/s` | `5.670 rad/s` | `7.516 rad/s` | `7.644 rad/s` | 后期依赖较高轮速完成任务。 |
| `wheel_joint_vel_abs_mean_raw` | `6.798 rad/s` | `7.638 rad/s` | `8.946 rad/s` | `8.960 rad/s` | 车轮实际角速度较高。 |
| `wheel_torque_target_abs_mean_raw` | `4.636` | `2.968` | `2.744` | `2.738` | 后期平均力矩目标较初期下降。 |
| `shaped_planar_command_abs_mean_raw` | `0.346` | `0.712` | `0.896` | `0.911` | 低层整形后的平面命令幅值明显增大。 |
| `tilt_deg` | `0.143°` | `0.122°` | `0.142°` | `0.148°` | 平地车体姿态稳定。 |

需要特别注意：2026-04-28 之后通过 USD 几何检查确认，车轮 local `Y` 近似竖直方向，local `Z` 才是水平侧向/轮轴方向。该 run 是 2026-04-25 的旧日志，`wheel_slip_angle_abs_mean_raw` 使用旧的 local `Y` 口径，所以不能作为真实水平侧滑角的严格证据。它只能说明当时训练代码内部使用的滑移观测/奖励信号较大。

### 3.5 数值稳定性

| 指标 | step 0 | step 294 | 后 20 step 均值 | 判断 |
|---|---:|---:|---:|---|
| `Loss/value` | `0.0096` | `0.1628` | `0.1276` | 有波动，但没有爆炸。 |
| `Loss/surrogate` | `0.0212` | `-0.0168` | `-0.0123` | PPO 更新稳定。 |
| `Loss/entropy` | `-1.524` | `-2.968` | `-2.936` | 探索逐渐收窄。 |
| `Policy/mean_std` | `0.200` | `0.167` | `0.168` | policy std 下降但未塌缩。 |
| `Perf/total_fps` | `3957` | `4029` | `4034` | 64 环境吞吐稳定。 |

## 4. RL 任务配置

### 4.1 环境和仿真

- 仿真设备：`cuda:0`
- 并行环境数：`64`
- 仿真步长：`sim_dt = 1/120 s`
- 控制 decimation：`2`
- RL 控制周期：`control_dt = 1/60 s`
- episode 时长：`40 s`
- 每个 episode 最大控制步数：`2400`
- 地形：平地 plane
- 地形摩擦：静摩擦 `1.0`，动摩擦 `1.0`
- 高度图、IMU、相机、LiDAR：均未接入 policy
- 域随机化：关闭
- 观测噪声：关闭
- curriculum：关闭

### 4.2 waypoint 任务

- 每个 episode 包含 `2` 个 waypoint。
- 每段目标距离：`10 m`。
- 目标方向最大偏角：`±30°`。
- 目标航向偏差：`0°`，即目标航向等于该段目标方向。
- 成功半径：`0.5 m`。
- reset yaw：固定为 `0`。
- reset 位置：`x, y` 各在 `[-1, 1] m` 范围内随机。

该 run 保存的 git diff 修改了 waypoint 采样逻辑：第二段 waypoint 的绝对转向角按每个环境以前一段绝对转向角为下界采样，因此任务语义是第二段转向更强，即大体满足 $|\phi_2| > |\phi_1|$，并受 `30°` 上限约束。

### 4.3 终止条件

当时 `compute_done_terms()` 实际使用的终止条件为：

- `waypoint_hit`：当前 active waypoint 距离小于 `0.5 m`。
- `is_success`：命中 waypoint 且当前 waypoint 已经是最后一个 waypoint。
- `time_out`：达到 `2400` 控制步且还未成功。
- `far_from_target`：当前 active waypoint 距离大于 `10 + 6 = 16 m`。
- `ball_joint_out_of_bounds`：任一球铰角超出配置上下限。

配置里存在 `target_yaw_tolerance_deg`、`orientation_limit_deg`、`head_tail_roll_limit_deg`、`head_tail_pitch_limit_deg`，但该 run 对应的 `terminations.py` 没有把目标航向误差、整车姿态角或头尾姿态角接入成功/失败终止逻辑。因此本轮“成功”本质上是位置命中双 waypoint，不包含目标 yaw 精度或姿态质量硬约束。

### 4.4 PPO 配置

| 项目 | 配置 |
|---|---|
| runner | `OnPolicyRunner` |
| algorithm | PPO |
| seed | `1` |
| device | `cuda:0` |
| num_steps_per_env | `512` |
| max_iterations | `700` |
| save_interval | `100` |
| actor hidden dims | `[256, 256]` |
| critic hidden dims | `[256, 256]` |
| activation | ReLU |
| observation normalization | 开启 |
| action distribution | `SquashedGaussianDistribution` |
| initial std | `0.2` |
| log std range | `[-4.0, 0.0]` |
| learning rate | `1e-4` |
| schedule | adaptive |
| desired KL | `0.008` |
| gamma | `0.99` |
| lambda | `0.95` |
| entropy coef | `0.0005` |
| clip param | `0.2` |
| value loss coef | `0.5` |
| max grad norm | `0.5` |
| epochs per update | `5` |
| mini batches | `16` |

该 run 的 `is_finite_horizon = false`。这意味着 timeout 在 RSL-RL 侧更接近时间截断语义，而不是严格失败终止语义。由于本轮后段 `time_out_rate = 0`，这个问题不影响“后段已成功完成任务”的判断，但它会影响对早期 timeout episode 的 return 解释。

## 5. 观测与动作配置

### 5.1 动作空间

动作维度为 `8`：

| 动作分支 | 维度 | 物理含义 |
|---|---:|---|
| base planar action | `2` | 期望中车体平面纵向速度 `v_x_cmd` 与偏航角速度 `yaw_rate_cmd` |
| ball joint action | `6` | 两个等效球铰的 6 个串联转动关节期望姿态 |

动作映射关系：

- `base_allow_reverse = true`
- 第 1 维动作 $a_0 \in [-1, 1]$ 映射为 $v_x^{cmd} = 2.0 a_0$，单位 `m/s`。
- 第 2 维动作 $a_1 \in [-1, 1]$ 映射为 $\omega_z^{cmd} = 2.0 a_1$，单位 `rad/s`。
- 后 6 维动作分别映射到球铰角目标区间：
  - lower：`(-0.6, -1.0, -0.5, -0.6, -1.0, -0.5)`
  - upper：`(0.6, 0.4, 0.5, 0.6, 0.4, 0.5)`

policy 不直接输出车轮速度，也不直接输出车轮力矩。车轮命令由底层运动模型根据平面速度命令、球铰姿态命令、接触权重和当前轮速计算。

### 5.2 观测空间

actor 和 critic 观测维度均为 `54`，critic 没有额外 privileged state 或高度图。

观测拼接为：

| 分量 | 维度 | 含义 |
|---|---:|---|
| `ball_joint_pos` | `6` | 两个等效球铰的 6 个关节角 |
| `ball_joint_vel` | `6` | 6 个球铰关节速度 |
| `base_lin_vel` | `3` | 中车体坐标系下线速度 |
| `base_ang_vel` | `3` | 中车体坐标系下角速度 |
| `wheel_joint_vel` | `6` | 6 个车轮关节角速度 |
| `wheel_longitudinal_slip` | `6` | 当时口径的纵向滑移 |
| `wheel_slip_angle` | `6` | 当时旧轴向口径的滑移角 |
| `wheel_normal_contact_force` | `6` | 每个车轮接触法向力占整车重量的比例 |
| `relative_goal_commands` | `4` | 当前 active waypoint 在车体坐标系下的相对 `x, y, z, heading` |
| `last_action` | `8` | 上一步 policy 动作 |

维度合计：`6 + 6 + 3 + 3 + 6 + 6 + 6 + 6 + 4 + 8 = 54`。

## 6. 奖励函数配置

该 run 的奖励项为：

| 奖励项 | 权重 | 作用 |
|---|---:|---|
| `distance_to_target` | `6.0` | 距离越近奖励越大。 |
| `progress_to_target` | `8.0` | 当前步相对上一控制步更接近目标时给正奖励。 |
| `reached_target` | `6.0` | 命中 waypoint 时给一次性奖励。 |
| `far_from_target` | `-2.0` | 距离超过 `16 m` 时惩罚。 |
| `angle_diff` | `6.0` | 当前目标方位误差越小奖励越大。 |
| `turn_speed_penalty` | `-2.0` | 转向误差大时惩罚较高平面速度。 |
| `slip_penalty` | `-2.0` | 惩罚纵向滑移和旧口径滑移角。 |

用 $T = 2400$ 表示最大控制步数，用 $d_t$ 表示当前 active waypoint 距离，则主要形式为：

$$
r_{dist} = \frac{1}{1 + 0.01 d_t^2} \cdot \frac{1}{T}
$$

$$
\Delta d = clip(d_{t-1} - d_t, -0.25, 0.25)
$$

当 $d_t \le 4.0 m$ 时，负 progress 被裁成 `0`，即靠近目标后不再因小幅远离目标被 progress 项惩罚：

$$
r_{prog} = \frac{\Delta d}{10}
$$

命中 waypoint 时：

$$
r_{hit} = 2.0 \cdot \frac{T - t}{T}
$$

滑移惩罚为：

$$
r_{slip} = \frac{mean(|\kappa|) + 4.0 \cdot mean(|\alpha|)}{T}
$$

总奖励为：

$$
R = 6 r_{dist} + 8 r_{prog} + 6 r_{hit} - 2 r_{far} + 6 r_{angle} - 2 r_{turn} - 2 r_{slip}
$$

这次训练后期主要正信号来自 `progress_to_target` 和 `reached_target`：

| 奖励/惩罚项 | step 0 | step 294 | 后 20 step 均值 |
|---|---:|---:|---:|
| `Reward/total` | `-0.00570` | `0.04652` | `0.04501` |
| `Reward/progress_to_target` | `0.00052` | `0.02106` | `0.02110` |
| `Reward/reached_target` | `0.00000` | `0.02651` | `0.02497` |
| `Reward/distance_to_target` | `0.00127` | `0.00189` | `0.00189` |
| `Reward/angle_diff` | `0.00186` | `0.00212` | `0.00214` |
| `Reward/slip_penalty` | `-0.00929` | `-0.00484` | `-0.00488` |
| `Reward/turn_speed_penalty` | `-0.00007` | `-0.00022` | `-0.00021` |

因此本轮的学习主线是“朝 waypoint 推进并命中”，不是“以低滑移为硬约束完成”。

## 7. 底层运动模型

### 7.1 机器人抽象

仿真对象是三车体铰接车辆：

- 中车体作为主基体。
- 前车体和后车体分别通过一个等效球铰连接到中车体。
- 每个等效球铰用 3 个串联转动关节表示，因此两个连接机构共 6 个球铰关节。
- 全车 6 个车轮：
  - 中车体左右轮
  - 前车体左右轮
  - 后车体左右轮

该 run 使用的 USD 为 `USD/complete_car.usd`，不是闭链并联机构的精确物理建模，而是“串联 3-DOF 等效球铰 + 六轮接触”的可训练简化模型。

### 7.2 底层控制链路

本轮 2026-04-25 的实际执行链路是：

1. PPO 输出 8 维动作。
2. 前 2 维映射为期望平面命令 $u^{des} = [v_x^{des}, \omega_z^{des}]$。
3. 后 6 维映射为球铰期望姿态 $q^d$。
4. 球铰一阶规划器根据当前球铰角 $q$ 和目标 $q^d$ 生成 $q_{cmd}$ 与 $\dot q_{cmd}$。
5. 低侧滑平面命令整形器把 $u^{des}$ 改写为 $u^* = [v_x^*, \omega_z^*]$。
6. 轮速分配器根据车辆几何、球铰速度和整形后的平面命令计算每个车轮的 $\Omega_{ref}$。
7. 轮级牵引控制器根据 $\Omega_{ref}$、实际轮速、纵向滑移和接触权重计算车轮力矩 $\tau_{cmd}$。
8. Isaac/PhysX 中球铰下发 position target，车轮下发 effort target。

这一点很重要：该 run 不是 2026-04-28 后的“车轮直接速度 target”配置，而是低层力矩控制配置。

### 7.3 球铰姿态规划器

球铰规划器使用一阶限速跟踪：

$$
\dot q_{raw} = K(q^d - q)
$$

$$
\dot q_{cmd} = clip(\dot q_{raw}, -\dot q_{max}, \dot q_{max})
$$

$$
q_{cmd} = clip(q + \Delta t \dot q_{cmd}, q_{min}, q_{max})
$$

本 run 的参数：

- $K = 10.0$，6 个球铰相同。
- $\dot q_{max} = 1.0 rad/s$。
- $\Delta t = 1/60 s$。
- 球铰 position drive：
  - stiffness：`8000`
  - damping：`1000`
  - effort limit：`20`
  - velocity limit：`1.0`

### 7.4 轮系几何和速度分配

底层 allocator 使用中车体坐标系下的轮心几何参数：

| 参数 | 值 |
|---|---:|
| `a_x` | `0.25633374` |
| `b_f` | `0.30654739` |
| `b_r` | `0.30633826` |
| `l1` | `-0.00989449` |
| `l2` | `0.00000932` |
| `l3` | `0.00968251` |
| `d1` | `0.44737875` |
| `d2` | `0.44737968` |
| `d3` | `0.44737875` |
| `h1` | `-0.043083285` |
| `h2` | `-0.02578188` |
| `h3` | `-0.043100655` |
| `wheel_radius` | `0.19 m` |

对于每个车轮，allocator 计算：

- 轮心位置 $p_i(q)$
- 轮滚动方向 $t_i(q)$
- 轮侧向方向 $n_i(q)$
- 球铰姿态变化引起的轮心位置雅可比 $G_i(q)$

名义轮心速度为：

$$
v_i^* = v_x^* e_x + \omega_z^* (e_z \times p_i) + G_i(q)\dot q_{cmd}
$$

滚动速度参考为：

$$
V_{roll,i}^{ref} = t_i(q) \cdot v_i^*
$$

车轮角速度参考为：

$$
\Omega_i^{ref} = \frac{V_{roll,i}^{ref}}{r}
$$

### 7.5 低侧滑平面命令整形

policy 给出的平面命令不是直接用于轮速分配，而是先经过低侧滑整形。

整形器求解一个二维二次优化问题，变量是 $u = [v_x, \omega_z]$。目标是既不要偏离 policy 的原始命令，又尽量降低接触车轮的名义侧向速度：

$$
\min_u \lambda_{track}\|u-u^{des}\|^2 + \lambda_{lat}\sum_i c_i (n_i \cdot v_i(u, \dot q_{cmd}))^2
$$

本 run 参数：

- $\lambda_{track} = 1.0$
- $\lambda_{lat} = 5.0$
- $v_x$ 裁剪范围：`[-2.0, 2.0] m/s`
- $\omega_z$ 裁剪范围：`[-2.0, 2.0] rad/s`
- 接触权重 $c_i$ 来自每个车轮法向接触力占整车重量的比例：
  - off threshold：`0.01`
  - on threshold：`0.08`

训练末期 `shaped_planar_command_abs_mean_raw` 后 20 step 约为 `0.911`，说明低层整形后的平面命令并不小，policy 已经学到较强运动命令。

### 7.6 车轮牵引力矩控制

该 run 的车轮不是速度驱动，而是 effort target。

车轮牵引控制器使用：

$$
\kappa_i = \frac{V_{roll,i} - r\Omega_i}{\max(|V_{roll,i}|, \epsilon)}
$$

其中 $\epsilon = 0.1$。

力矩目标为：

$$
\tau_i = c_i \left(K_{track}(\Omega_i^{ref} - \Omega_i) - K_{slip}\kappa_i\right)
$$

再裁剪到 `[-20, 20]`。

本 run 参数：

- `K_track = 2.0`
- `K_slip = 4.0`
- `wheel_effort_limit = 20.0`
- `wheel_stiffness = 0.0`
- `wheel_damping = 0.0`
- 车轮实际下发：`set_joint_effort_target()`

该结构的含义是：

- policy 不直接控制轮子。
- allocator 先根据期望车体运动和球铰姿态速度算出轮速参考。
- 牵引控制器再根据轮速误差和纵向滑移生成力矩。
- 接触力越小的轮子，力矩权重越低。

### 7.7 该底层模型对结果解释的影响

本轮训练学到的不是单纯的差速小车控制，而是“球铰姿态 + 车体平面速度 + 六轮力矩分配”的耦合策略。

后段指标显示：

- `wheel_speed_reference_abs_mean_raw` 后 20 step 约 `7.64 rad/s`。
- `wheel_joint_vel_abs_mean_raw` 后 20 step 约 `8.96 rad/s`。
- `wheel_torque_target_abs_mean_raw` 后 20 step 约 `2.74`。
- `ball_joint_pos_abs_mean_raw` 后 20 step 约 `0.085 rad`。
- `ball_joint_target_error_abs_mean_raw` 后 20 step 约 `0.011 rad`。

这说明球铰 position tracking 本身比较稳，训练后期主要通过较高车轮速度和有限幅度的构型调整完成 waypoint。它能证明 Stage0 目标到达策略可学，但不能单独证明构型控制已经产生了低滑移、高通过性的物理优势。

## 8. 可用结论和不可用结论

### 8.1 可以使用的结论

这次训练可以支持以下结论：

- 在平地、双 waypoint、`0.5 m` 成功半径下，当前 Isaac Lab Stage0 环境可以稳定训练出完成任务的 policy。
- 8 维动作空间，即 `2` 维平面命令加 `6` 维球铰姿态命令，是可训练的。
- 低层运动模型链路在工程上跑通：policy 动作能经过球铰规划、低侧滑整形、轮速分配和力矩控制形成有效运动。
- 训练曲线没有显示 PPO 数值发散。

### 8.2 不能使用的结论

这次训练不能支持以下结论：

- 不能说已经学到低滑移控制。纵向滑移绝对均值后 20 step 约 `3.0`，且侧滑角是旧轴向口径。
- 不能说目标 yaw 精度已经满足要求。该 run 的成功终止没有检查 `target_yaw_tolerance_deg`。
- 不能说姿态约束下稳定完成。该 run 的成功/失败终止没有接入整车姿态角或头尾姿态角限制。
- 不能把 `model_200.pt` 当作最终满成功平台策略。`model_200.pt` 对应 step `200`，当时 `success_rate≈0.928`，还不是 iteration `269-294` 的连续满成功平台。

## 9. Checkpoint 限制

这次 run 最关键的工程限制是保存间隔：

- `save_interval = 100`
- 已保存：`model_0.pt`、`model_100.pt`、`model_200.pt`
- 训练在 iteration `294` 早停
- 因此没有 `model_294.pt` 或 `model_299.pt`

也就是说，训练曲线证明了后期策略已经进入连续满成功平台，但没有保存该平台的 policy checkpoint。若要做回放、视频、定量 eval 或论文展示，应重新训练到下一个保存点，或把 `save_interval` 调小后复现该配置。

## 10. 面向论文/项目记忆的最终判断

这轮训练在项目中的定位应是：

> Stage0 平地双 waypoint 到达任务的严格成功半径验证 run。它证明当前 RL 环境、动作空间和底层控制链路能够训练出稳定到达策略，但它不是低滑移协同控制的最终证据，也不是可直接回放的最佳 checkpoint。

如果写入论文或阶段总结，建议表述为：

- “在平地双 waypoint 任务中，将 waypoint 命中半径收紧至 `0.5 m` 后，PPO policy 仍能在约 `294` iterations 内达到连续满成功，episode 级双 waypoint 完成率达到 `100%`。”
- “该结果验证了 Stage0 到达任务的可学习性和仿真控制链路的可运行性。”
- “但本轮未保存最终平台 checkpoint，且低滑移指标口径尚未修正，因此不能据此宣称低滑移协同运动已经实现。”
