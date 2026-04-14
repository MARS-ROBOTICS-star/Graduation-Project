# RL阶段训练参数一览表

本文档按当前 `RL_Training/` 主线代码整理 `CompleteCar-Stage0` 的完整 RL 训练参数。  
目标是把 Stage0 在训练时真正生效的环境配置、维度、数学关系、PPO 超参数放到一份文档里，便于后续：

- 查参数
- 对照代码
- 做实验记录 
- 论文写作时回填任务定义

---

## 1. 总览

### 1.1 当前任务

- 任务名：`CompleteCar-Stage0`
- 环境类：`CompleteCarDirectEnv`
- 配置类：`CompleteCarStage0EnvCfg`
- PPO 配置类：`CompleteCarStage0PPORunnerCfg`
- 机器人形态：三节车体、两个球铰连接、六个车轮
- 当前阶段目标：平地 baseline，训练基础运动策略

### 1.2 Stage0 的核心特征

- 地形：平地
- 课程学习：关闭
- 显式高度 patch：关闭
- IMU：关闭
- 双目相机：关闭
- 激光雷达：关闭
- height scanner：关闭
- 动作随机化：关闭
- 观测噪声：关闭

### 1.3 当前关键维度

- 并行环境数：`512`
- 动作维度：`6`
- Actor 单帧观测维度：`45`
- Critic 单帧观测维度：`45`
- state space 维度：`0`
- 控制频率：`60 Hz`
- 单回合时长：`16 s`
- 单回合最大控制步数：`16 × 60 = 960`

---

## 2. 训练入口与层次关系

Stage0 训练时的配置继承关系是：

1. `CompleteCarStage0EnvCfg`
2. 继承 `CompleteCarEnvCfg`
3. `CompleteCarEnvCfg.__post_init__()` 统一装配：
   - action space
   - observation space
   - simulation cfg
   - robot cfg
4. `CompleteCarStage0PPORunnerCfg`
5. 继承 `CompleteCarBasePPORunnerCfg`

Stage0 最重要的覆写只有几条：

- `scene.num_envs = 512`
- `terrain.enabled = False`
- `terrain.mode = "plane"`
- `curriculum.enabled = False`
- `terrain.measure_heights = False`
- 所有传感器关闭

所以 Stage0 的思路非常明确：  
只保留最小可运行 RL 闭环，不引入 rough terrain、传感器、课程学习、显式高度图这些复杂因素。

---

## 3. 仿真层参数

### 3.1 时间参数

控制和仿真采用两层时间尺度。

- `sim_dt = 1 / 120 s`
- `decimation = 2`
- `control_dt = sim_dt × decimation = 1 / 60 s`

含义：

- 仿真底层物理步长是 `120 Hz`
- 每做 `2` 个仿真步，RL 控制更新一次
- 所以策略动作的实际更新频率是 `60 Hz`

### 3.2 仿真器参数

当前 PhysX 相关关键参数：

- `solver_type = 1`
- `max_position_iteration_count = 8`
- `max_velocity_iteration_count = 0`
- `bounce_threshold_velocity = 0.2`
- `friction_offset_threshold = 0.04`
- `friction_correlation_distance = 0.025`
- `enable_stabilization = True`

### 3.3 重力与接触材料

- 重力：`(0, 0, -9.81)`
- 静摩擦：`1.0`
- 动摩擦：`1.0`
- 恢复系数：`0.0`

Stage0 因为是平地，所以地面由 ground plane 直接生成。

---

## 4. 地形配置

### 4.1 Stage0 生效值

- `terrain.enabled = False`
- `terrain.mode = "plane"`
- `terrain.measure_heights = False`

这意味着：

- 不启用 generator terrain
- 不做 terrain class / terrain level 难度切换
- 不给 critic 拼显式高度图

### 4.2 Stage0 下实际地形行为

在 `_setup_scene()` 中：

- 如果 `generator_enabled = False`
- 就调用 `spawn_ground_plane(...)`

所以 Stage0 训练时的实际场景是标准平地。

---

## 5. 机器人配置

### 5.1 资产

- USD 路径：`USD/complete_car.usd`
- articulation root prim path：`/body_car_chassis`

### 5.2 关节集合

机器人总关节分成两类。

球铰关节 6 个：

1. `spm1_platform_joint_z`
2. `spm1_platform_joint_y`
3. `spm1_platform_joint_x`
4. `spm2_platform_joint_z`
5. `spm2_platform_joint_y`
6. `spm2_platform_joint_x`

车轮关节 6 个：

1. `body_car_wheel_left_joint`
2. `body_car_wheel_right_joint`
3. `head_car_wheel_left_joint`
4. `head_car_wheel_right_joint`
5. `tail_car_wheel_left_joint`
6. `tail_car_wheel_right_joint`

### 5.3 控制关节

当前 RL policy 直接控制的只有 6 个球铰关节：

- `CONTROLLED_JOINT_NAMES = BALL_JOINT_NAMES`

所以：

- 动作维度 = `6`
- policy 不直接输出轮速

### 5.4 驱动器参数

球铰执行器：

- 刚度：`100.0`
- 阻尼：`10.0`
- 力矩上限：`120.0`
- 速度上限：`6.0 rad/s`

车轮执行器：

- 刚度：`0.0`
- 阻尼：`1000.0`
- 力矩上限：`80.0`
- 速度上限：`20.0 rad/s`

这说明：

- 球铰是典型位置控制
- 车轮更接近速度控制

### 5.5 初始姿态

root 初始位置：

- `(0.0, 0.0, 0.30)`

所有球铰和车轮默认关节位置：

- 全部 `0.0`

所有默认关节速度：

- 全部 `0.0`

---

## 6. Reset 配置

Reset 在每次 episode 结束后执行，负责把 root 和 joint 设回初值附近。

### 6.1 Root reset

默认值：

- `root_pos = (0.0, 0.0, 0.30)`
- `root_lin_vel = (0.0, 0.0, 0.0)`
- `root_ang_vel = (0.0, 0.0, 0.0)`

随机扰动范围：

- `root_x_range = (-0.25, 0.25)`
- `root_y_range = (-0.25, 0.25)`
- `root_yaw_range = (-0.25π, 0.25π)`

数学上，reset 后 root 状态可理解为：

$$
\mathbf{p}_{root}^{reset}
=
\mathbf{p}_{default}
+ \mathbf{o}_{env}
+ \Delta \mathbf{p}_{xy}
$$

其中：

- $\mathbf{p}_{default}$ 是默认 root 位置
- $\mathbf{o}_{env}$ 是 env origin
- $\Delta \mathbf{p}_{xy}$ 是 x/y 随机偏移

朝向只加随机 yaw：

$$
\mathbf{q}^{reset}
=
\mathbf{q}_{default} \otimes \mathbf{q}_{yaw}(\Delta \psi)
$$

### 6.2 Joint reset

当前 joint reset 扰动全是零：

- `ball_joint_pos_range = (0.0, 0.0)`
- `ball_joint_vel_range = (0.0, 0.0)`
- `wheel_joint_pos_range = (0.0, 0.0)`
- `wheel_joint_vel_range = (0.0, 0.0)`

因此当前 Stage0 的 joint reset 实际上就是：

- 球铰位置回到默认值 `0`
- 球铰速度回到默认值 `0`
- 车轮位置回到默认值 `0`
- 车轮速度回到默认值 `0`

### 6.3 与 terrain 的关系

Stage0 因为是平地，所以 reset 不会受到 terrain class 的 spawn offset 影响。

---

## 7. 命令配置

### 7.1 命令维度

命令维度是 `2`：

$$
\mathbf{c} = [v_x, \omega_z]
$$

分别对应：

- `lin_vel_x`
- `ang_vel_yaw`

### 7.2 当前采样范围

- `lin_vel_x ∈ [-1.0, 1.0]`
- `ang_vel_yaw ∈ [-1.0, 1.0]`

说明：

- 当前 Stage0 命令主线只保留前进速度和偏航角速度

### 7.3 命令重采样周期

- `resampling_time = 4.0 s`

也就是说每个环境每 `4` 秒重新采样一次命令。

### 7.4 命令时钟逻辑

在每个控制步：

$$
t_{left} \leftarrow t_{left} - \Delta t
$$

如果：

$$
t_{left} \le 0
$$

则该环境重新采样命令。

### 7.5 命令变换矩阵

当前代码中，采样后的 $[v_x, \omega_z]$ 不会直接进入环境主线。  
它会先扩成虚拟三维向量 $[v_x, 0, \omega_z]$，再左乘固定矩阵：

$$
\begin{bmatrix}
v_x' \\
\omega_z'
\end{bmatrix}
=
\begin{bmatrix}
1 & 0 & 0 \\
0 & 0 & 1
\end{bmatrix}
\begin{bmatrix}
1 & 0 & -0.00614478162640497 \\
0 & 1 & -1.07379532542362 \times 10^{-5} \\
0 & 0 & 1
\end{bmatrix}
\begin{bmatrix}
v_x \\
0 \\
\omega_z
\end{bmatrix}
$$

所以 env 内真正用于：

- observation
- reward
- curriculum
- wheel allocator

的命令，是收口后的二维变换命令 $[v_x', \omega_z']$。

### 7.6 当前命令开关

- `zero_command = False`
- `rel_standing_envs = 0.0`

因此：

- 不强制全零命令
- 不随机抽一部分静止环境

---

## 8. 观测配置

### 8.1 Actor / Critic 观测组

当前 Stage0：

- Actor 观测组：`actor`
- Critic 观测组：`critic`

但因为 Stage0 不开显式 terrain patch，所以：

- `actor = critic`

### 8.2 单帧观测维度

当前单帧 Actor 观测维度：

$$
3 + 3 + 3 + 6 + 6 + 6 + 2 + 2 + 6 + 2 + 6 = 45
$$

即：

1. 中车 body-frame 线速度：`3`
2. 中车 body-frame 角速度：`3`
3. 中车重力投影：`3`
4. 6 个球铰角：`6`
5. 6 个球铰角速度：`6`
6. 6 个球铰目标跟踪误差：`6`
7. 前车绝对 roll/pitch：`2`
8. 后车绝对 roll/pitch：`2`
9. 6 个车轮轮速：`6`
10. command：`2`
11. 上一时刻动作：`6`

### 8.3 观测数学定义

记 Actor 观测为 $\mathbf{o}_t$，则：

$$
\mathbf{o}_t =
\mathrm{concat}
\left[
\mathbf{v}_b,\;
\boldsymbol{\omega}_b,\;
\mathbf{g}_b,\;
\mathbf{q}_{ball},\;
\dot{\mathbf{q}}_{ball},\;
\mathrm{wrap}(\mathbf{q}_{target}-\mathbf{q}_{ball}),\;
\mathbf{rpy}_{head}^{rp},\;
\mathbf{rpy}_{tail}^{rp},\;
\dot{\mathbf{q}}_{wheel},\;
\mathbf{c},\;
\mathbf{a}_{t-1}
\right]
$$

其中：

- $\mathbf{v}_b$：中车 body-frame 线速度
- $\boldsymbol{\omega}_b$：中车 body-frame 角速度
- $\mathbf{g}_b$：重力在 body frame 下的投影
- $\mathbf{q}_{ball}$：球铰角
- $\dot{\mathbf{q}}_{ball}$：球铰角速度
- $\mathbf{q}_{target}$：球铰目标角
- `wrap`：角度规整到 `[-π, π]`

### 8.4 观测缩放

观测先乘手工 scale，再进入 PPO 的经验归一化。

当前 scale：

- `base_lin_vel = 1.0`
- `base_ang_vel = 0.25`
- `projected_gravity = 1.0`
- `ball_joint_pos = 1.0`
- `ball_joint_vel = 0.05`
- `ball_joint_target_error = 1.0`
- `module_roll_pitch = 1.0`
- `wheel_joint_vel = 0.05`
- `commands = 1.0`
- `last_action = 1.0`

### 8.5 观测噪声

当前 Stage0：

- `observations.noise.enabled = False`

因此观测噪声模型不启用。

### 8.6 历史观测

- `use_history = False`
- `history_length = 1`

所以当前没有 observation stacking。

### 8.7 观测裁剪

- `clip_observations = 100.0`

环境在 `step()` 返回前，会对 actor/critic 观测做 clip。

### 8.8 PPO 归一化

虽然环境侧 hand-scale 已经做了，但 actor 和 critic 仍会再经过经验归一化：

$$
\hat{\mathbf{o}} = \frac{\mathbf{o} - \mu}{\sigma + \varepsilon}
$$

其中：

- $\mu$：running mean
- $\sigma$：running std
- $\varepsilon = 10^{-2}$

这一步在 PPO 模型内部执行，不在 env 里执行。

---

## 9. 动作配置

### 9.1 动作维度

动作维度为 `6`，对应 6 个球铰关节。

$$
\mathbf{a}_t \in \mathbb{R}^6
$$

### 9.2 动作裁剪

当前动作先裁剪到：

$$
\mathbf{a}_t^{clip} = \mathrm{clip}(\mathbf{a}_t, -1, 1)
$$

其中：

- `clip_actions = 1.0`

### 9.3 动作随机化

当前：

- `enable_action_randomization = False`

所以：

- 不加 action noise
- 不加 action bias
- `motor_strength = 1`

因此：

$$
\mathbf{a}_t^{proc} = \mathbf{a}_t^{clip}
$$

### 9.4 球铰目标映射

当前不是统一 `action_scale`，而是按每个关节上下界做非对称映射。

记默认关节角为 $\mathbf{q}_0$，动作处理后为 $\mathbf{a}\in[-1,1]^6$，  
下界为 $\mathbf{q}_{low}$，上界为 $\mathbf{q}_{up}$。

则逐维映射逻辑为：

- 若 $a_i \ge 0$：

$$
q_{target,i} = q_{0,i} + a_i (q_{up,i} - q_{0,i})
$$

- 若 $a_i < 0$：

$$
q_{target,i} = q_{0,i} + a_i (q_{0,i} - q_{low,i})
$$

这样保证：

- `action = 0` -> 默认关节角
- `action = 1` -> 上界
- `action = -1` -> 下界

### 9.5 当前球铰动作范围

按关节顺序 `z, y, x, z, y, x`：

- yaw：`[-0.7, 0.7]`
- pitch：`[-1.6, 0.5]`
- roll：`[-0.5, 0.5]`

### 9.6 轮速目标生成

当前 policy 不直接输出轮速。  
轮速目标由 wheel allocator 根据：

- 当前球铰角
- 当前球铰角速度
- 当前命令

自动生成。

也就是说，控制结构是：

- 高层 RL：控制球铰姿态
- 低层解析器：自动分配 6 个轮速

---

## 10. 奖励配置

### 10.1 当前奖励项集合

当前 Stage0 reward 共有 `5` 项：

1. `tracking_lin_vel`
2. `tracking_ang_vel`
3. `orientation`
4. `action_rate`
5. `termination`

### 10.2 跟踪类奖励

#### 线速度跟踪

令命令前进速度为 $c_x$，实际 body-frame 前向速度为 $v_x$，则：

$$
e_{lin} = (c_x - v_x)^2
$$

$$
r_{lin} = \exp\left(-\frac{e_{lin}}{\sigma_{lin}^2}\right)
$$

当前：

- `tracking_lin_vel_std = sqrt(0.25)`
- scale：`2.0`

因此实际加权项为：

$$
R_{lin} = 2.0 \cdot r_{lin}
$$

#### 角速度跟踪

设命令 yaw rate 为 $c_{\omega}$，实际 yaw rate 为 $\omega_z$，则：

$$
e_{ang} = (c_{\omega} - \omega_z)^2
$$

$$
r_{ang} = \exp\left(-\frac{e_{ang}}{\sigma_{ang}^2}\right)
$$

当前：

- `tracking_ang_vel_std = sqrt(0.25)`
- scale：`2.0`

### 10.3 姿态惩罚

令重力在 body frame 下投影为 $\mathbf{g}_b = [g_x, g_y, g_z]$，则：

$$
r_{ori} = g_x^2 + g_y^2
$$

对应权重：

- `orientation = -2.0`

所以实际项为：

$$
R_{ori} = -2.0 \cdot (g_x^2 + g_y^2)
$$

这项本质上在罚 roll/pitch 倾斜。

### 10.4 动作变化惩罚

设当前动作为 $\mathbf{a}_t$，上一时刻动作为 $\mathbf{a}_{t-1}$，则：

$$
r_{act} = \|\mathbf{a}_t - \mathbf{a}_{t-1}\|^2
$$

权重：

- `action_rate = -0.01`

### 10.5 终止惩罚

若当前帧因为失败终止，则：

$$
r_{term} = 1
$$

否则：

$$
r_{term} = 0
$$

权重：

- `termination = -2.0`

### 10.6 总奖励

当前总奖励为：

$$
R =
R_{lin}
+ R_{ang}
+ R_{ori}
+ R_{act}
+ R_{term}
$$

当前：

- `only_positive_rewards = False`

所以不会对总奖励做非负截断。

---

## 11. 终止条件配置

终止函数返回两类信号：

- `terminated`
- `time_out`

### 11.1 时间终止

若：

$$
step \ge max\_episode\_length - 1
$$

则：

- `time_out = True`

这不是失败终止，只是回合走满。

### 11.2 姿态终止

令 body-frame 重力投影为 $\mathbf{g}_b$，则倾角计算为：

$$
\theta = \arccos(\mathrm{clip}(-g_z,-1,1))
$$

若：

$$
\theta > 45^\circ
$$

则失败终止。

### 11.3 球铰越界终止

当前球铰上下界与动作上下界一致：

- yaw：`[-0.7, 0.7]`
- pitch：`[-1.6, 0.5]`
- roll：`[-0.5, 0.5]`

对任意关节 $q_i$，若：

$$
q_i < q_{low,i}
\quad \text{or} \quad
q_i > q_{up,i}
$$

则失败终止。

### 11.4 最低高度终止

当前：

- `minimum_root_height = None`

所以 Stage0 不启用该项。

---

## 12. 随机化配置

当前随机化总开关与子项如下：

- `enable_action_randomization = False`
- `randomize_motor_strength = False`
- `motor_strength_range = (0.9, 1.1)`
- `joint_position_noise_scale = 0.0`
- `action_noise_std = 0.0`
- `action_bias_std = 0.0`

实际效果：

- 不做动作侧随机化
- 不做 motor strength 随机化
- joint reset 不叠加额外噪声

---

## 13. 课程学习配置

Stage0 当前课程学习关闭：

- `curriculum.enabled = False`

虽然配置类里仍然有：

- `max_init_terrain_level = 0`
- `default_terrain_name = "flat"`
- `move_up_distance_ratio = 0.5`
- `move_down_command_ratio = 0.5`

但在 Stage0 下它们都不会真正起作用，因为：

- terrain 不是 generator
- curriculum 总开关关闭

所以 Stage0 可以理解为：

- 无课程学习

---

## 14. 传感器配置

Stage0 所有额外传感器关闭：

- `imu.enabled = False`
- `stereo_camera.enabled = False`
- `lidar.enabled = False`
- `enable_height_scanner = False`

因此：

- policy 不吃任何外部传感器特征
- 观测完全来自机器人自身状态和命令

---

## 15. PPO 超参数

### 15.1 Rollout 参数

- `num_steps_per_env = 48`
- `num_envs = 512`

所以每轮 rollout 总样本数：

$$
48 \times 512 = 24576
$$

### 15.2 训练总轮数

- `max_iterations = 600`

### 15.3 Mini-batch

- `num_learning_epochs = 5`
- `num_mini_batches = 4`

每个 mini-batch 大小：

$$
\frac{24576}{4} = 6144
$$

### 15.4 折扣与 GAE

- `gamma = 0.99`
- `lam = 0.95`

GAE 的递推形式为：

$$
\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)
$$

$$
A_t = \delta_t + \gamma \lambda A_{t+1}
$$

$$
R_t = A_t + V(s_t)
$$

### 15.5 PPO clip

- `clip_param = 0.2`

PPO surrogate 目标可写成：

$$
L^{CLIP}(\theta)
=
\mathbb{E}
\left[
\min
\left(
r_t(\theta)A_t,\;
\mathrm{clip}(r_t(\theta),1-\epsilon,1+\epsilon)A_t
\right)
\right]
$$

其中：

- $\epsilon = 0.2$
- $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}$

### 15.6 学习率与 KL 调度

- `learning_rate = 3e-4`
- `schedule = "adaptive"`
- `desired_kl = 0.01`

这表示学习率会参考 KL 偏离程度自适应调整。

### 15.7 其他 PPO 超参数

- `entropy_coef = 0.005`
- `value_loss_coef = 1.0`
- `use_clipped_value_loss = True`
- `max_grad_norm = 1.0`

### 15.8 Actor / Critic 网络结构

Actor：

- 隐层：`[256, 128, 64]`
- 激活函数：`ELU`
- 观测归一化：开启
- 输出分布：Gaussian
- 初始标准差：`0.7`
- `std_type = "scalar"`

Critic：

- 隐层：`[256, 128, 64]`
- 激活函数：`ELU`
- 观测归一化：开启
- 输出分布：无

### 15.9 动作分布

Actor 使用对角高斯分布：

$$
\mathbf{a} \sim \mathcal{N}(\boldsymbol{\mu}_\theta(\mathbf{o}), \mathrm{diag}(\boldsymbol{\sigma}^2))
$$

其中：

- 均值 $\boldsymbol{\mu}_\theta$ 由 MLP 输出
- 标准差 $\boldsymbol{\sigma}$ 是可学习的状态无关参数

### 15.10 优势归一化

当前 PPO 会对整批 advantage 做标准化：

$$
\hat{A}_t = \frac{A_t - \mu_A}{\sigma_A + 10^{-8}}
$$

---

## 16. Stage0 训练流程总串联

从训练流程角度，Stage0 每个控制周期的闭环如下：

1. 如果命令计时器到期，重采样命令
2. 采样到的命令先经过固定变换矩阵
3. policy 读取 45 维 actor 观测
4. actor 输出 6 维标准化动作
5. 动作先裁剪到 `[-1, 1]`
6. 动作按逐轴关节上下界映射成 6 个球铰目标角
7. wheel allocator 根据球铰状态和命令计算 6 个轮速目标
8. Isaac Sim 执行球铰位置控制和轮速控制
9. 环境读取新状态，生成下一时刻观测
10. 按 5 项 reward 计算当前奖励
11. 判断是否终止或超时
12. PPO 存 rollout，周期性更新 actor/critic

---

## 17. Stage0 当前默认参数摘要

如果只看最关键的 Stage0 默认值，可以简化成下面这张短表。

### 17.1 环境与仿真

- `num_envs = 512`
- `episode_length_s = 16`
- `sim_dt = 1/120`
- `control_dt = 1/60`
- 平地

### 17.2 动作与观测

- 动作维度：`6`
- Actor 观测维度：`45`
- Critic 观测维度：`45`
- 动作范围：逐轴 `[-1, 1]` 标准化，映射到球铰物理上下界

### 17.3 命令

- 命令维度：`2`
- 每 `4 s` 重采样一次
- `vx ∈ [-1,1]`
- `wz ∈ [-1,1]`

### 17.4 奖励

- 跟踪线速度
- 跟踪角速度
- 姿态惩罚
- 动作变化惩罚
- 终止惩罚

### 17.5 终止

- 姿态倾角 > `45°`
- 球铰越界
- 或超时

### 17.6 PPO

- `num_steps_per_env = 48`
- `num_learning_epochs = 5`
- `num_mini_batches = 4`
- `learning_rate = 3e-4`
- `gamma = 0.99`
- `lam = 0.95`
- `clip_param = 0.2`

---

## 18. 当前文档适用范围

本文档只对应当前代码版本下的 `Stage0`。  
如果后续你继续修改：

- reward 集合
- observation 维度
- action 上下界
- command 语义
- PPO 超参数

那么这份表也要同步更新。
