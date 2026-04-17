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
- wheel contact sensor：开启
- 动作随机化：关闭
- 观测噪声：关闭

### 1.3 当前关键维度

- 并行环境数：`64`
- 动作维度：`12`
- Actor 单帧观测维度：`48`
- Critic 单帧观测维度：`48`
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

当前 Stage0 不再只保留少量覆写。  
为便于后续直接在 `baseline/complete_car_stage0_cfg.py` 中维护参数，当前已经把 Stage0 活跃参数显式集中在该文件内。

当前最重要的 Stage0 生效值包括：

- `scene.num_envs = 64`
- `terrain.enabled = False`
- `terrain.mode = "plane"`
- `curriculum.enabled = False`
- `terrain.measure_heights = False`
- `episode_length_s = 16.0`
- `commands.resampling_time = 5.3`
- `commands.goal_distance = 12.0`
- `commands.goal_direction_max_deg = 30.0`
- `commands.goal_heading_delta_max_deg = 12.0`
- 除 wheel contact sensor 以外，其余显式传感器关闭
- 训练优先级改为稳定性优先：
  - 低滑移
  - 低侧滑
  - 低跳动
  - 球铰速度更平滑
  - 然后再处理 critic 稳定性
- Stage0 额外覆写：
  - 收紧球铰动作上下界
  - 球铰阻尼 `20.0`
  - 球铰速度上限 `0.8 rad/s`
  - 车轮速度上限 `12.0 rad/s`
  - `PhysX max_velocity_iteration_count = 1`
  - `enable_external_forces_every_iteration = True`

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
- `max_velocity_iteration_count = 1`
- `bounce_threshold_velocity = 0.2`
- `friction_offset_threshold = 0.04`
- `friction_correlation_distance = 0.025`
- `enable_stabilization = True`
- `enable_external_forces_every_iteration = True`

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

当前 RL policy 直接控制全部 `12` 个执行量：

- 6 个球铰姿态目标
- 6 个车轮速度目标

所以：

- 动作维度 = `12`
- policy 直接输出轮速目标

### 5.4 驱动器参数

球铰执行器：

- 刚度：`100.0`
- 阻尼：`20.0`
- 力矩上限：`120.0`
- 速度上限：`0.8 rad/s`

车轮执行器：

- 刚度：`0.0`
- 阻尼：`1000.0`
- 力矩上限：`80.0`
- 速度上限：`12.0 rad/s`
- 车轮半径：`0.19 m`

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

- `root_x_range = (-1, 1)`
- `root_y_range = (-1, 1)`
- `root_yaw_range = (0, 0)`

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

命令维度是 `3`，但 env 内部存的是全局目标位姿：

$$
\mathbf{c}_t^{world} = [x_t, y_t, \psi_{target}]
$$

policy 在观测里实际接收到的不是全局量，而是当前车体系下的相对目标：

$$
\mathbf{c}_t^{rel} = [x_{rel}, y_{rel}, \psi_{rel}]
$$

### 7.2 当前目标采样规则

- 目标距离固定：`12.0 m`
- 目标方向相对当前车头的偏角范围：`[-30°, +30°]`
- 目标朝向相对目标连线方向的偏置范围：`[-12°, +12°]`

工程实现：

1. 先采样 $u \sim U(0,1)$
2. 再采样符号 $s \in \{-1,+1\}$
3. 目标方向偏角：

$$
\phi = s \cdot 30^\circ \cdot \sqrt{u}
$$

这里采用的是“偏向扇区边缘的二次分布”实现，使接近边缘角的目标比接近正前方的目标更常出现。

再定义：

$$
\theta_{los} = \psi_0 + \phi
$$

$$
\delta \sim U(-12^\circ, 12^\circ)
$$

$$
\psi_{target} = \mathrm{wrapToPi}(\theta_{los} + \delta)
$$

目标点坐标为：

$$
x_t = x_0 + 12.0 \cos(\theta_{los})
$$

$$
y_t = y_0 + 12.0 \sin(\theta_{los})
$$

### 7.3 命令重采样周期

- `episode_length_s = 16.0 s`
- `resampling_time = 5.3 s`

也就是说当前每个环境会在 reset 时采样一次目标，并在回合中途继续重采样，单个 episode 通常会经历 `2 ~ 3` 个目标段。

### 7.4 命令时钟逻辑

当前主线已重新启用“回合内定时重采样”。

- reset 时会调用一次目标采样。
- 预物理步内当 `resampling_time < episode_length_s` 时，会启用定时器倒计时与中途重采样。
- 当前实际行为是：
  - 一个 episode 内通常包含 `2 ~ 3` 个目标。

### 7.5 观测中的相对命令表达

设当前车体世界坐标为 $(x, y)$，当前航向为 $\psi$，则：

$$
\Delta x = x_t - x,\quad \Delta y = y_t - y
$$

世界系到车体系的二维变换使用：

$$
x_{rel} = \cos\psi \cdot \Delta x + \sin\psi \cdot \Delta y
$$

$$
y_{rel} = -\sin\psi \cdot \Delta x + \cos\psi \cdot \Delta y
$$

$$
\psi_{rel} = \mathrm{wrapToPi}(\psi_{target} - \psi)
$$

最终 observation 中的命令项就是：

$$
[x_{rel}, y_{rel}, \psi_{rel}]
$$

### 7.6 当前命令开关

- `zero_command = False`
- `rel_standing_envs = 0.0`

因此默认情况下：

- 不强制原地目标
- 不随机抽一部分原地目标环境

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
3 + 3 + 3 + 6 + 6 + 6 + 6 + 3 + 12 = 48
$$

即：

1. 中车 body-frame 线速度：`3`
2. 中车 body-frame 角速度：`3`
3. 中车重力投影：`3`
4. 6 个球铰角：`6`
5. 6 个车轮纵向滑移率：`6`
6. 6 个车轮侧滑角：`6`
7. 6 个按整车重量归一化的车轮法向接触力：`6`
8. 相对目标命令：`3`
9. 上一时刻动作：`12`

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
\boldsymbol{\lambda}_{wheel},\;
\boldsymbol{\alpha}_{wheel},\;
\bar{\mathbf{F}}_{n,wheel},\;
\mathbf{c},\;
\mathbf{a}_{t-1}
\right]
$$

其中：

- $\mathbf{v}_b$：中车 body-frame 线速度
- $\boldsymbol{\omega}_b$：中车 body-frame 角速度
- $\mathbf{g}_b$：重力在 body frame 下的投影
- $\mathbf{q}_{ball}$：球铰角
- $\boldsymbol{\lambda}_{wheel}$：6 个车轮纵向滑移率
- $\boldsymbol{\alpha}_{wheel}$：6 个车轮侧滑角
- $\bar{\mathbf{F}}_{n,wheel}$：6 个按整车重量归一化的车轮法向接触力

当前暂时不送入 policy observation 的量包括：

- 6 个球铰角速度
- 6 个球铰目标跟踪误差
- 前车绝对 roll/pitch
- 后车绝对 roll/pitch
- 6 个车轮轮速

其中新增 3 组车轮接触观测的定义为：

- 纵向滑移率：

$$
\lambda_i = \mathrm{clip}\left(
\frac{v_{x,i} - r \omega_i}{\max(|v_{x,i}|, \varepsilon)},
[-1, 1]
\right)
$$

这里：
- $v_{x,i}$ 是第 $i$ 个车轮轮心线速度在车轮局部前向轴上的投影
- $r = 0.19 \text{ m}$
- $\varepsilon = 0.1$

- 侧滑角：

$$
\alpha_i = \mathrm{clip}\left(
\mathrm{atan2}(v_{y,i}, |v_{x,i}| + \varepsilon),
\left[-\frac{\pi}{2}, \frac{\pi}{2}\right]
\right)
$$

这里：
- $v_{y,i}$ 是第 $i$ 个车轮轮心线速度在车轮局部侧向轴上的投影
- 单位保持为弧度

- 法向接触力：

$$
\bar{F}_{n,i} = \frac{\left\lVert \mathbf{F}_{n,i}^{w} \right\rVert_2}{m_{total} g}
$$

这里：

- $\mathbf{F}_{n,i}^{w}$ 是第 `i` 个车轮对地面所有接触点法向力的世界系合力向量
- 当前运行时实现不再依赖 Isaac Lab `ContactSensor`
- 当前直接对 PhysX `rigid_contact_view.get_contact_data(dt)` 返回的逐接触点数据做聚合：

$$
\mathbf{F}_{n,i}^{w} = \sum_k f_{n,i,k} \mathbf{n}_{i,k}
$$

这里：
- $f_{n,i,k}$ 是第 `i` 个车轮第 `k` 个接触点的法向接触力标量
- $\mathbf{n}_{i,k}$ 是对应接触点的世界系接触法向单位向量

因此当前实现直接取这个法向力向量的模长，而不再使用世界坐标系竖直方向近似。

### 8.4 观测缩放

观测先乘手工 scale，再进入 PPO 的经验归一化。

当前 scale：

- `base_lin_vel = 1.0`
- `base_ang_vel = 0.35`
- `projected_gravity = 1.5`
- `ball_joint_pos = 1.0`
- `wheel_longitudinal_slip = 2.0`
- `wheel_slip_angle = 1.5`
- `wheel_normal_contact_force = 1.25`
- `commands = 1.0`
- `last_action = 1.5`

当前 slip 相关观测参数：

- `wheel_slip_epsilon = 0.1`
- `wheel_longitudinal_slip_clip = 1.0`
- `wheel_slip_angle_clip_rad = π / 2`

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

动作维度为 `12`：

- 前 6 维：6 个球铰姿态目标
- 后 6 维：6 个车轮速度目标

$$
\mathbf{a}_t \in \mathbb{R}^{12}
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

- yaw：`[-0.56, 0.56]`
- pitch：`[-1.30, 0.40]`
- roll：`[-0.35, 0.35]`

### 9.6 车轮速度目标映射

当前 policy 直接输出 6 个车轮速度目标的标准化动作。
每个车轮动作仍先裁剪到 `[-1, 1]`，然后只按单一对称速度上限映射：

- 速度上限参数：`wheel_joint_velocity_limit_sim = 12 rad/s`

映射公式为：

$$
\omega_{target,i} = a_i \cdot \omega_{max}
$$

其中：

- `a_i` 是第 `i` 个标准化车轮动作
- `\omega_{max}` 是统一车轮速度上限

因此：

- `action = 1` -> `+12 rad/s`
- `action = -1` -> `-12 rad/s`
- `action = 0` -> `0`

因此现在的控制结构是：

- 高层 RL：同时输出球铰目标角和车轮速度目标
- wheel allocator：保留在仓库里，但当前执行链路不再参与 env 控制

---

## 10. 奖励配置

### 10.1 当前奖励主干

当前 active reward 已经不再围绕速度命令跟踪展开，而是改成目标导向结构：

$$
R = r_{tar} + r_{prog} \cdot r_{roll} \cdot r_{speed} \cdot r_{forces} \cdot r_{vertical} \cdot r_{ball\_speed} \cdot \left(\frac{r_{head} + r_{slip\parallel} + r_{slip\perp}}{3}\right)
$$

其中：

- `r_tar` 是目标达成 bonus
- `r_prog` 是朝目标推进的 dense progress 主奖励
- `r_roll / r_speed / r_forces / r_vertical / r_ball_speed` 是乘性抑制项
- `r_head / r_slip_parallel / r_slip_perp` 先取平均，再作为复合乘子

### 10.2 目标达成奖励

设当前相对目标位置误差为：

$$
d_t = \sqrt{x_{rel}^2 + y_{rel}^2}
$$

设当前相对目标朝向误差为：

$$
\Psi = \psi_{rel}
$$

当同时满足：

- `d_t < 0.3 m`
- `|\Psi| < 9°`

则给 target bonus：

$$
r_{tar} = k_{tar} \cdot \mathbf{1}(d_t < 0.3,\ |\Psi| < 9^\circ)
$$

当前代码里 `k_tar` 不是手填常数，而是按“最大无折扣回报的 5%”反解：

$$
k_{tar} = \frac{\rho \cdot (r_0 \cdot f_{control})}{1 - \rho}, \qquad \rho = 0.03
$$

其中：

- `r_0 = 12 m`
- `f_control = 60 Hz`

### 10.3 朝目标推进奖励

设上一时刻和当前时刻到目标的水平距离分别为 $d_{t-1}$ 与 $d_t$，则：

$$
r_{prog} = (d_{t-1} - d_t) \cdot f_{control}
$$

当前：

- `f_control = 60 Hz`

因此：

- 朝目标前进时，`r_prog > 0`
- 远离目标时，`r_prog < 0`

### 10.4 航向对齐项

航向门控项定义为：

$$
r_{head} = \exp\left[-\frac{1}{2}\left(\frac{\Psi}{d_t / k_d}\right)^2\right]
$$

当前：

- `k_d = 5 m`

这个设计的含义是：

- 离目标远时，允许先把车开到目标附近
- 离目标近时，目标朝向误差会被更严格地放大

### 10.5 中车 roll 约束项

设中车绝对 roll 为 $\phi$，则：

$$
r_{roll} =
\begin{cases}
1, & |\phi| \le 5^\circ \\
\exp\left[-\frac{1}{2}\left(\frac{\phi}{k_\phi}\right)^2\right], & |\phi| > 5^\circ
\end{cases}
$$

当前：

- `roll_free_deg = 3°`
- `k_phi = \pi/24`

这项用于抑制过大侧倾。

### 10.6 速度约束项

设中车平面速度模长为 $|v|$，则：

$$
r_{speed} = \min\left(1,\ \exp[k_{speed}(v_{lim} - |v|)]\right)
$$

当前：

- `v_lim = 1.6 m/s`
- `k_speed = 3`

这项不会额外奖励低速，只在速度过高时明显压低回报。

### 10.7 轮载均匀性项

对 6 个车轮，先计算按整车重量归一化后的法向接触力标准差：

$$
\sigma_{forces} = \operatorname{std}(\bar F_{n,1}, \dots, \bar F_{n,6})
$$

然后定义：

$$
r_{forces} = \exp\left[-\frac{1}{2}\left(\frac{\sigma_{forces}}{k_{forces}}\right)^2\right]
$$

当前：

- `k_forces = 0.08`

这项鼓励六轮受力更均匀，降低悬空轮和单轮过载。

### 10.8 纵向滑移项

当前实现不再对 6 个轮子的纵向滑移 gate 做乘积，否则在训练早期会非常容易整体塌到接近 `0`。

先计算 6 个轮子纵向滑移率绝对值均值：

$$
\bar{\lambda} = \frac{1}{6}\sum_{i=1}^{6} |\lambda_i|
$$

再定义：

$$
r_{slip\parallel} = \exp\left(-\frac{\bar{\lambda}}{k_\lambda}\right)
$$

当前：

- `k_lambda = 0.18`

这样可以保持“滑移越大，gate 越小”的方向不变，同时避免 reward 在训练早期失去分辨率。

### 10.9 侧滑角项

当前实现同样不再使用硬裁切余弦乘积，而是先计算 6 个轮子的侧滑角绝对值均值：

$$
\bar{\alpha} = \frac{1}{6}\sum_{i=1}^{6} |\alpha_i|
$$

再用：

$$
k_{\alpha,scale} = \frac{\pi}{k_\alpha}
$$

$$
r_{slip\perp} = \exp\left(-\frac{\bar{\alpha}}{k_{\alpha,scale}}\right)
$$

当前：

- `k_alpha = 8`

也就是当前侧滑 gate 的指数衰减尺度为：

$$
\frac{\pi}{8} \approx 0.393\ \text{rad}
$$

### 10.10 竖向速度抑制项

设中车世界系竖直速度为 $v_z$，则：

$$
r_{vertical} = \exp\left[-\frac{1}{2}\left(\frac{|v_z|}{k_{vertical}}\right)^2\right]
$$

当前：

- `k_vertical = 0.20`

这项直接抑制上下跳动。

### 10.11 球铰速度平滑项

设 6 个球铰角速度绝对值均值为：

$$
\bar{\omega}_{ball} = \frac{1}{6}\sum_{i=1}^{6} |\dot q_i|
$$

则：

$$
r_{ball\_speed} = \exp\left[-\frac{1}{2}\left(\frac{\bar{\omega}_{ball}}{k_{ball}}\right)^2\right]
$$

当前：

- `k_ball = 0.55`

### 10.12 当前配置参数总览

当前 `RewardParamsCfg` 生效值为：

- `target_bonus_ratio = 0.03`
- `target_position_tolerance = 0.3`
- `target_yaw_tolerance_deg = 9.0`
- `heading_distance_scale = 5.0`

### 10.13 当前 TensorBoard 奖励日志

当前 step 级别会输出：

- `Reward/target_bonus`
- `Reward/progress`
- `Reward/heading_gate`
- `Reward/gated_progress`
- `Reward/total`

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

## 12. 随机化配置

当前随机化总开关与子项如下：

- `enable_action_randomization = False`
- `joint_position_noise_scale = 0.0`
- `action_noise_std = 0.0`
- `action_bias_std = 0.0`

实际效果：

- 不做动作侧随机化
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

- `num_steps_per_env = 96`
- `num_envs = 64`

所以每轮 rollout 总样本数：

$$
96 \times 64 = 6144
$$

### 15.2 训练总轮数

- `max_iterations = 300`

### 15.3 Mini-batch

- `num_learning_epochs = 4`
- `num_mini_batches = 4`

每个 mini-batch 大小：

$$
\frac{6144}{4} = 1536
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

- `learning_rate = 2e-4`
- `schedule = "adaptive"`
- `desired_kl = 0.008`

这表示学习率会参考 KL 偏离程度自适应调整。

### 15.7 其他 PPO 超参数

- `entropy_coef = 0.002`
- `value_loss_coef = 0.7`
- `use_clipped_value_loss = True`
- `max_grad_norm = 0.7`

### 15.8 Actor / Critic 网络结构

Actor：

- 隐层：`[256, 128, 64]`
- 激活函数：`ELU`
- 观测归一化：开启
- 输出分布：Gaussian
- 初始标准差：`0.35`
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
2. 当前默认仅在 reset 时根据当前位姿采样一个目标全局位姿
3. env 把目标转成车体系下的 `[x_rel, y_rel, psi_rel]`
4. policy 读取 48 维 actor 观测
5. actor 输出 12 维标准化动作
6. 动作先裁剪到 `[-1, 1]`
7. 前 6 维映射成 6 个球铰目标角
8. 后 6 维映射成 6 个车轮速度目标
9. Isaac Sim 执行球铰位置控制和轮速控制
10. 环境读取新状态，生成下一时刻观测
11. 按当前 reward 配置计算当前奖励
12. 判断是否终止或超时
13. PPO 存 rollout，周期性更新 actor/critic

---

## 17. Stage0 当前默认参数摘要

如果只看最关键的 Stage0 默认值，可以简化成下面这张短表。

### 17.1 环境与仿真

- `num_envs = 64`
- `episode_length_s = 16`
- `sim_dt = 1/120`
- `control_dt = 1/60`
- 平地

### 17.2 动作与观测

- 动作维度：`12`
- Actor 观测维度：`48`
- Critic 观测维度：`48`
- 动作范围：逐轴 `[-1, 1]` 标准化，球铰映射到各自角度上下界，车轮映射到对称速度上限

### 17.3 命令

- 命令维度：`3`
- 每个 episode 只采样一次
- 目标距离固定 `12 m`
- 目标方向偏角范围 `[-18.43°, +18.43°]`
- 目标朝向附加偏置范围 `[-9.215°, +9.215°]`

### 17.4 奖励

- 总奖励：
  - `target_bonus + gated_progress`
- 其中：
  - `gated_progress = progress * heading_gate`

当前关键参数为：

- `target_bonus_ratio = 0.03`
- `target_position_tolerance = 0.3 m`
- `target_yaw_tolerance_deg = 9°`
- `heading_distance_scale = 5 m`

### 17.5 当前这一轮定向实验的保留/否决项

- 当前默认 reward 已按用户要求收口为最小主线：
  - `r_tar + r_prog * r_head`
- 当前 active reward 组件只有：
  - `target_bonus`
  - `progress`
  - `heading_gate`
  - `gated_progress`
- 以下旧 gate 已退出 active reward 主线：
  - `roll_gate`
  - `speed_gate`
  - `force_gate`
  - `vertical_speed_gate`
  - `ball_joint_speed_gate`
  - `wheel_action_rate_gate`
  - `longitudinal_slip_gate`
  - `lateral_slip_gate`
  - `composite_gate`

### 17.5 终止

- 姿态倾角 > `45°`
- 球铰越界
- 或超时

### 17.6 PPO

- `num_steps_per_env = 96`
- `num_learning_epochs = 4`
- `num_mini_batches = 4`
- `learning_rate = 2e-4`
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
