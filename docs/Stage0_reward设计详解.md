# Stage0 Reward设计详解

> 2026-04-17 更新：
> 当前 active Stage0 reward 已不再使用本文后续展开的多 gate 版本。
> 当前默认代码已收口为：
> `R = r_tar + r_prog * r_comp * r_roll`
> 其中：
> `r_tar = target_bonus`
> `r_prog = progress`
> `r_head = heading_gate`
> `r_long = longitudinal_slip_gate`
> `r_lat = lateral_slip_gate`
> `r_comp = (r_head + r_long + r_lat) / 3`
> `r_roll = roll_gate`
> 本文其余内容保留为 2026-04-16 的历史说明，仅用于回溯旧实验。

本文档整理当前 active `Stage0` 的 reward 设计。  
目标是把每一项奖励的：

- 数学公式
- 参数含义
- 当前取值
- 为什么这样取

全部说明清楚，便于后续：

- 对照代码
- 分析训练结果
- 讨论 reward 是否合理
- 做下一轮修改

当前代码位置：

- reward 实现：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/rewards.py`
- 当前 Stage0 参数值：
  - `RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/baseline/complete_car_stage0_cfg.py`

---

## 1. 总体结构

当前总奖励公式是：

\[
R = B + G
\]

其中：

\[
G
=
P
\cdot
g_{\mathrm{roll}}
\cdot
g_{\mathrm{spd}}
\cdot
g_{\mathrm{force}}
\cdot
g_{\mathrm{vert}}
\cdot
g_{\mathrm{ball}}
\cdot
g_{\mathrm{wheel}}
\cdot
g_{\mathrm{comp}}
\]

而：

\[
g_{\mathrm{comp}}
=
\frac{
g_{\mathrm{head}}
+
g_{\mathrm{long}}
+
g_{\mathrm{lat}}
}{3}
\]

所以当前 reward 不是“很多项直接相加”，而是：

- 一个离散成功奖励：
  - \(B\)
- 一个连续推进奖励：
  - \(P\)
- 再用一串 gate 去约束“这个推进是不是高质量的”

### 1.1 符号说明

后文统一使用以下数学符号：

- \(R\)
  - 总奖励
- \(B\)
  - 到点奖励
- \(P\)
  - 裸推进项
- \(G\)
  - 门控后的有效推进项
- \(d_t\)
  - 第 \(t\) 步时车体到目标点的平面距离
- \(\psi_e\)
  - 目标朝向误差
- \(v_{xy}\)
  - 水平速度模长
- \(v_z\)
  - 竖向速度
- \(\delta_{\mathrm{wheel}}\)
  - 轮速动作步间变化量
- \(s_{\mathrm{long}}\)
  - 平均纵向滑移
- \(s_{\mathrm{lat}}\)
  - 平均侧滑角
- \(\sigma_F\)
  - 六轮法向载荷标准差

---

## 2. 当前 reward 项总览

当前代码里记录的 reward term 有：

- `target_bonus`
- `progress`
- `roll_gate`
- `speed_gate`
- `force_gate`
- `vertical_speed_gate`
- `ball_joint_speed_gate`
- `wheel_action_rate_gate`
- `heading_gate`
- `longitudinal_slip_gate`
- `lateral_slip_gate`
- `composite_gate`
- `gated_progress`

最终总奖励是：

- `reward = target_bonus + gated_progress`

---

## 3. 当前 Stage0 reward 参数值

当前 Stage0 生效值为：

- `target_bonus_ratio = 0.03`
- `target_position_tolerance = 0.3`
- `target_yaw_tolerance_deg = 9.0`
- `heading_distance_scale = 12.0`
- `roll_gate_activation_roll_deg = 5.0`
- `body_car_roll_gate = pi / 16`
- `longitudinal_slip_gate_scale = 0.3`
- `lateral_slip_gate_scale = 4.0`

同时当前 Stage0 命令和控制相关值为：

- `goal_distance = 12.0 m`
- `goal_direction_max_deg = 30.0`
- `goal_heading_delta_max_deg = 12.0`
- `control_dt = 1/60 s`

---

## 4. `target_bonus`

### 4.1 公式

\[
\mathbb{I}_{\mathrm{reach}}
=
\mathbb{I}
\Bigl(
d_t < \varepsilon_p
\;\land\;
|\psi_e| < \varepsilon_{\psi}
\Bigr)
\]

其中：

\[
B
=
\mathbb{I}_{\mathrm{reach}}
\cdot
B_0
\]

\[
B_0
=
\frac{H\,\rho}{1-\rho}
\]

\[
H
=
\frac{d_{\mathrm{goal}}}{\Delta t}
\]

### 4.2 当前数值

当前：

- `goal_distance = 12.0`
- `control_dt = 1/60`
- `target_bonus_ratio = 0.03`

所以：

- `progress_horizon = 12 / (1/60) = 720`
- `bonus_value ≈ 720 * 0.03 / 0.97 ≈ 22.27`

### 4.3 参数含义

- `target_position_tolerance = 0.3 m`
  - 位置到点容差
- `target_yaw_tolerance_deg = 9°`
  - 朝向到点容差
- `target_bonus_ratio = 0.03`
  - bonus 相对“理想整段 progress”的比例系数

### 4.4 为什么这样取

- `0.3 m`
  - 对 `12 m` 目标来说是 2.5% 量级，不算宽松，也不算极严。
- `9°`
  - 给了朝向一定要求，但又不至于让 yaw 对齐过难。
- `0.03`
  - 设计意图是：bonus 只是“到点奖励”，不该压过连续推进。
  - 但在当前 `goal_distance = 12m` 下，它对应的实际数值已经约 `22.27`，并不小。

---

## 5. `progress`

### 5.1 公式

\[
P
=
(d_{t-1} - d_t)\, f_c
\]

\[
f_c = \frac{1}{\Delta t}
\]

### 5.2 含义

- 比上一步更接近目标了多少
- 再乘控制频率
- 近似可以理解成：
  - 朝目标逼近的速度
  - 单位接近 `m/s`

### 5.3 为什么这样取

- 这是最直接的“朝目标推进速度”
- 物理意义非常清楚
- 优点：
  - 连续、密集、易解释
- 缺点：
  - 如果没有 gate，策略很容易靠高滑移硬冲出 progress

---

## 6. `heading_gate`

### 6.1 公式

\[
\sigma_h
=
\max\!\left(\frac{d_t}{k_h},\,10^{-6}\right)
\]

\[
g_{\mathrm{head}}
=
\exp\!\left(
-\frac{1}{2}
\left(\frac{\psi_e}{\sigma_h}\right)^2
\right)
\]

### 6.2 当前参数

- `heading_distance_scale = 5.0`

### 6.3 参数含义

这个 gate 的逻辑是：

- 距离目标越远：
  - 朝向误差容忍度越大
- 距离目标越近：
  - 朝向误差容忍度越小

举例：

- 距离 `10 m`
  - 分母约 `2.0 rad`
  - gate 比较宽松
- 距离 `1 m`
  - 分母约 `0.2 rad`
  - gate 更严格

### 6.4 为什么这样取

- 远距离时，不想让策略过度原地摆头
- 近距离时，又希望它对准姿态
- `5.0` 是一个折中值：
  - 先靠近
  - 再逐渐强调朝向

---

## 7. `roll_gate`

### 7.1 公式

\[
\phi_f = \operatorname{rad}(\theta_f)
\]

\[
g_{\mathrm{roll}}
=
\begin{cases}
1, & |\phi| \le \phi_f \\
\exp\!\left(
-\frac{1}{2}
\left(\frac{|\phi|}{\sigma_r}\right)^2
\right), & |\phi| > \phi_f
\end{cases}
\]

### 7.2 当前参数

- `roll_free_deg = 3.0°`
- `roll_gaussian_scale = pi / 24 ≈ 0.1309 rad ≈ 7.5°`

### 7.3 参数含义

- `roll_free_deg`
  - 小侧倾免罚区
- `roll_gaussian_scale`
  - 超出免罚区后的衰减速度

### 7.4 为什么这样取

- Stage0 是平地基础运动阶段
- 所以希望车体姿态尽量正
- `3°` 表示：
  - 对小幅正常姿态波动宽容
- `7.5°` 表示：
  - 超过免罚区后平滑惩罚，而不是硬截断

---

## 8. `speed_gate`

### 8.1 公式

\[
g_{\mathrm{spd}}
=
\min\!\left(
1,\;
\exp\!\bigl(k_v (v_{\max} - v_{xy})\bigr)
\right)
\]

### 8.2 当前参数

- `speed_limit = 1.6 m/s`
- `speed_gain = 3.0`

### 8.3 参数含义

- `speed_limit`
  - 允许的水平速度软上限
- `speed_gain`
  - 超速后惩罚下降有多快

例如：

- 当 `horizontal_speed = 1.6`
  - `gate = 1`
- 当 `horizontal_speed = 2.0`
  - `gate = exp(3*(1.6-2.0)) ≈ 0.30`

### 8.4 为什么这样取

- 当前项目前面已经验证过：
  - 长目标距离会逼策略堆速度
- `1.6 m/s` 是当前 Stage0 想控制住的基础运行速度量级
- `3.0` 表示：
  - 超速后要比较明显地压下去

---

## 9. `vertical_speed_gate`

### 9.1 公式

\[
g_{\mathrm{vert}}
=
\exp\!\left(
-\frac{1}{2}
\left(\frac{|v_z|}{\sigma_z}\right)^2
\right)
\]

### 9.2 当前参数

- `vertical_speed_scale = 0.20 m/s`

### 9.3 参数含义

- 控制对上下跳动的容忍度

### 9.4 为什么这样取

- 平地阶段不希望车体靠跳动换推进
- `0.20` 取值比较严格
- 说明当前对竖向跳动不宽容

---

## 10. `force_gate`

### 10.1 公式

\[
\sigma_F = \operatorname{Std}(F_1,F_2,\dots,F_6)
\]

\[
g_{\mathrm{force}}
=
\exp\!\left(
-\frac{1}{2}
\left(\frac{\sigma_F}{\sigma_{F0}}\right)^2
\right)
\]

### 10.2 当前参数

- `force_std_scale = 0.08`

### 10.3 参数含义

- 它关注的是：
  - 六个轮子的法向载荷分布均不均匀
- 不关注：
  - 六轮总法向载荷和是否接近 `1`

### 10.4 为什么这样取

- 轮地受力分布不均通常意味着：
  - 姿态偏斜
  - 局部卸载
  - 接触质量差
- `0.08` 取值偏严格
- 说明当前希望受力分布尽量均匀

需要注意：

- 它只能约束“分布均匀性”
- 不能单独解决“总支撑掉了”的问题

---

## 11. `ball_joint_speed_gate`

### 11.1 公式

\[
\bar{\omega}_b
=
\frac{1}{6}
\sum_{i=1}^{6} |\omega_{b,i}|
\]

\[
g_{\mathrm{ball}}
=
\exp\!\left(
-\frac{1}{2}
\left(\frac{\bar{\omega}_b}{\sigma_b}\right)^2
\right)
\]

### 11.2 当前参数

- `ball_joint_speed_scale = 0.55 rad/s`

### 11.3 参数含义

- 惩罚球铰动作是否过快、过猛

### 11.4 为什么这样取

- 之前多轮实验已经说明：
  - 球铰动作过激会连带破坏姿态和接触质量
- 但也不能太严，否则球铰根本不参与
- `0.55` 是当前“允许参与，但不允许乱甩”的折中值

---

## 12. `wheel_action_rate_gate`

### 12.1 公式

\[
\delta_{\mathrm{wheel}}
=
\frac{1}{6}
\sum_{i=1}^{6}
|a_{w,i}^{(t)} - a_{w,i}^{(t-1)}|
\]

\[
g_{\mathrm{wheel}}
=
\exp\!\left(
-\frac{\delta_{\mathrm{wheel}}}{\sigma_w}
\right)
\]

### 12.2 当前参数

- `wheel_action_rate_scale = 0.25`

### 12.3 参数含义

- 惩罚轮速动作在相邻控制步之间突变过大

### 12.4 为什么这样取

- 这是专门为了缓解“轮速控制太直接”补的一层软约束
- `0.25` 取值偏小，说明希望明显抑制轮速跳变
- 前面实验已经验证：
  - 这一项对缓解纵滑和 critic 不稳有帮助

---

## 13. `longitudinal_slip_gate`

### 13.1 公式

\[
s_{\mathrm{long}}
=
\frac{1}{6}
\sum_{i=1}^{6} |s_{\mathrm{long},i}|
\]

\[
g_{\mathrm{long}}
=
\exp\!\left(
-\frac{s_{\mathrm{long}}}{\sigma_{\mathrm{long}}}
\right)
\]

### 13.2 当前参数

- `longitudinal_slip_scale = 0.18`

### 13.3 参数含义

- 控制对纵滑的容忍度
- scale 越小，纵滑一大，gate 掉得越快

例如：

- 当平均纵滑 `0.18`
  - `gate = exp(-1) ≈ 0.368`
- 当平均纵滑 `0.86`
  - `gate ≈ exp(-4.78) ≈ 0.008`

### 13.4 为什么这样取

- 纵滑是当前 Stage0 最核心的问题
- 所以这里用了很严格的尺度 `0.18`
- 它的设计意图很明确：
  - 只要车轮明显空转，就不要保留太多 progress

---

## 14. `lateral_slip_gate`

### 14.1 公式

\[
\sigma_{\mathrm{lat}}
=
\frac{\pi}{k_{\mathrm{lat}}}
\]

\[
s_{\mathrm{lat}}
=
\frac{1}{6}
\sum_{i=1}^{6} |s_{\mathrm{lat},i}|
\]

\[
g_{\mathrm{lat}}
=
\exp\!\left(
-\frac{s_{\mathrm{lat}}}{\sigma_{\mathrm{lat}}}
\right)
\]

### 14.2 当前参数

- `lateral_slip_gain = 8.0`
- 所以：
  - `slip_angle_scale = pi / 8 ≈ 0.3927 rad ≈ 22.5°`

### 14.3 参数含义

- `lateral_slip_gain` 越大
  - 等效 scale 越小
  - 惩罚越严格

例如：

- 平均侧滑角 `22.5°`
  - gate ≈ `exp(-1) ≈ 0.368`
- 平均侧滑角 `40°`
  - gate 会掉到 `0.17 ~ 0.20`

### 14.4 为什么这样取

- 之前多轮诊断里，侧滑一直压不住
- 所以当前用了偏严格版本
- 但又没有纵滑那么严，因为平地转向仍需要允许一定侧偏

---

## 15. `composite_gate`

### 15.1 公式

\[
g_{\mathrm{comp}}
=
\frac{
g_{\mathrm{head}}
+
g_{\mathrm{long}}
+
g_{\mathrm{lat}}
}{3}
\]

### 15.2 含义

- 它不是一个新的物理量
- 只是把三件关键事情合成一层：
  - 朝向对不对
  - 纵滑高不高
  - 侧滑高不高

### 15.3 为什么这样取

- 设计思路是把“目标相关质量项”单独收成一层
- 用平均而不是乘积，是为了避免这三项过早一起掉死

但它也有明显缺点：

- 只要其中一项特别差，平均值还是会被明显拖低
- 又没有乘积那么强硬

---

## 16. `gated_progress`

### 16.1 公式

\[
G
=
P
\cdot
g_{\mathrm{roll}}
\cdot
g_{\mathrm{spd}}
\cdot
g_{\mathrm{force}}
\cdot
g_{\mathrm{vert}}
\cdot
g_{\mathrm{ball}}
\cdot
g_{\mathrm{wheel}}
\cdot
g_{\mathrm{comp}}
\]

### 16.2 含义

- 它是当前真正的连续奖励主线
- 不是简单看“有没有前进”
- 而是看“是不是以高质量方式前进”

### 16.3 为什么这样取

- 当前 reward 的核心思想不是：
  - 直接把一堆 penalty 加起来
- 而是：
  - 让 `progress` 成为主线
  - 所有坏行为都去扣掉 progress 的有效性

优点：

- 物理解释清楚
- 所有约束都围绕“高质量推进”

缺点：

- 只要某个关键 gate 过低，`progress` 会几乎全被吃掉
- 当前最典型的就是：
  - `longitudinal_slip_gate`

---

## 17. `total_reward`

### 17.1 公式

\[
R = B + G
\]

当前：

- `only_positive_rewards = False`

所以不会做额外正值裁切。

### 17.2 为什么这样取

- 逻辑上就是：
  - 平时靠 `gated_progress`
  - 到点时额外给 `target_bonus`

这也是当前 reward 最大的结构风险来源：

- 如果 `target_bonus` 太强
  - 训练会变成“冲着吃 bonus 去”
- 如果 `gated_progress` 太弱
  - 策略会缺少稳定连续的学习信号

最近几轮 run 的现象，正是在这两个极端之间来回摆：

- 短目标版本更容易变成：
  - bonus 主导
- 长目标版本更容易变成：
  - progress 驱动，但 traction 很差

---

## 18. 当前 reward 设计的核心哲学

当前 reward 的核心不是“鼓励小车快点跑”，而是：

- 鼓励朝目标推进
- 但这个推进必须同时满足：
  - 姿态不要太歪
  - 速度不要太高
  - 受力不要太偏
  - 不要跳
  - 球铰不要乱甩
  - 轮速不要乱跳
  - 朝向合理
  - 纵滑低
  - 侧滑低

所以它本质上是一个：

- `progress` 主线
- 一串质量门控
- 一个到点 bonus

也就是：

**`progress` 主线 + 质量 gate + 成功 bonus**

---

## 19. 当前结构的关键风险

从 reward 结构本身看，当前最大的几个风险是：

### 19.1 `target_bonus` 可能主导回报

- 只要到点奖励足够大
- 策略就可能更多学“怎么吃 bonus”
- 而不是学“持续稳定地推进”

### 19.2 全乘 gate 很容易把 `progress` 吃光

- 乘法结构的优点是约束强
- 缺点是只要有一项极低，`gated_progress` 就会非常小

### 19.3 `force_gate` 只看分布，不看总和

- 它能约束轮载均匀性
- 但不能单独约束总法向支撑是否接近 `1`

### 19.4 `heading + slip` 合成平均值可能过于粗糙

- 这让三种不同性质的问题被压成一个平均量
- 会损失诊断分辨率

---

## 20. 一句话总结

当前 Stage0 reward 的本质是：

- **鼓励朝目标推进**
- 但只有在：
  - 低倾斜
  - 低超速
  - 低失载
  - 低跳动
  - 球铰平滑
  - 轮速平滑
  - 朝向合理
  - 低纵滑
  - 低侧滑

这些条件同时满足时，`progress` 才会真正变成有效奖励。

所以它不是“简单的到点奖励”，而是一个：

**高质量推进奖励系统**
