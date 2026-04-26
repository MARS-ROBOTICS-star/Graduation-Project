# Stage0 当前底层运动学轮速分配与力矩控制链路详解

日期：2026-04-26

适用范围：

- 当前 `CompleteCar-Stage0` 主线
- 当前底层控制器：球铰轨迹生成器 + Isaac/PhysX 隐式 PD + 运动学轮速分配 + 接触感知低滑移车轮力矩控制

对应主要源码：

- `base/env.py`
- `baseline/complete_car_stage0_cfg.py`
- `base/complete_car_cfg.py`
- `kinematics/wheel_speed_allocator.py`
- `assets/actuators_cfg.py`
- `assets/robot_cfg.py`
- `mdp/observations.py`

本文目标是把当前实际运行的底层链路按数据流和公式展开，便于逐项检查：策略动作如何变成球铰目标、球铰如何由 Isaac/PhysX PD 执行、轮速参考如何由当前几何构型算出、最终车轮力矩如何根据纵滑、侧滑和接触状态被衰减。

## 1. 总链路

当前一个控制步内的完整链路是：

```text
RL policy action a
  -> 平面命令 u_d = [v_x^d, omega_z^d]
  -> 球铰最终目标姿态 q^d
  -> 球铰轨迹生成器输出 q_cmd, qdot_cmd
  -> Isaac/PhysX 隐式 PD 跟踪 q_cmd, qdot_cmd
  -> 实际球铰状态 q_actual, qdot_actual

同时：

q_actual + qdot_cmd + u_d + 接触力
  -> 当前轮心位置 p_j、滚动方向 t_j、侧向方向 n_j、轮心位置雅可比 J_j
  -> 接触权重 C_w,j
  -> 低侧滑平面命令整形 u*
  -> 轮速参考 Omega_ref,j
  -> 实际车轮速度、实际轮心纵向/侧向速度、纵滑率、侧滑角
  -> 车轮力矩 tau_j
  -> Isaac 车轮关节 effort target
```

关键点：

- 球铰执行器使用 `q_cmd` 和 `qdot_cmd`。
- 轮速分配器使用同一个 `qdot_cmd`，不再重新计算另一套球铰速度。
- 轮速分配器使用实际球铰姿态 `q_actual` 计算当前几何构型。
- `Omega_ref` 只是车轮力矩控制器内部的参考角速度，不是直接下发给 Isaac 的速度目标。
- 车轮最终下发的是 `tau_j`，即 `set_joint_effort_target(...)`。

## 2. 当前关节和车轮顺序

当前球铰顺序为：

| 序号 | 变量 | 关节名 | 含义 |
|---:|---|---|---|
| 1 | $q_1$ | `spm1_platform_joint_z` | 前段连接机构 z 轴转角 |
| 2 | $q_2$ | `spm1_platform_joint_y` | 前段连接机构 y 轴转角 |
| 3 | $q_3$ | `spm1_platform_joint_x` | 前段连接机构 x 轴转角 |
| 4 | $q_4$ | `spm2_platform_joint_z` | 后段连接机构 z 轴转角 |
| 5 | $q_5$ | `spm2_platform_joint_y` | 后段连接机构 y 轴转角 |
| 6 | $q_6$ | `spm2_platform_joint_x` | 后段连接机构 x 轴转角 |

当前代码中的车轮顺序为：

| 序号 | 变量 | 车轮关节名 | 直观位置 |
|---:|---|---|---|
| 1 | wheel 1 | `body_car_wheel_left_joint` | 中左 |
| 2 | wheel 2 | `body_car_wheel_right_joint` | 中右 |
| 3 | wheel 3 | `head_car_wheel_left_joint` | 前左 |
| 4 | wheel 4 | `head_car_wheel_right_joint` | 前右 |
| 5 | wheel 5 | `tail_car_wheel_left_joint` | 后左 |
| 6 | wheel 6 | `tail_car_wheel_right_joint` | 后右 |

因此在阅读 TensorBoard 的 `PerWheel/...` 日志和底层数组时，应以这个顺序为准。

## 3. 当前 Stage0 生效参数

| 参数 | 当前值 | 作用 |
|---|---:|---|
| $r$ | `0.19 m` | 车轮半径 |
| $\Delta t_c$ | `1/60 s` | RL 控制周期 |
| $v_{x,\max}$ | `2.0 m/s` | 前进速度命令上限 |
| $\omega_{z,\max}$ | `2.0 rad/s` | 偏航角速度命令上限 |
| $K_q$ | `8.0` | 球铰目标误差到速度命令的比例增益 |
| $\dot q_{\max}$ | `1.5 rad/s` | 球铰速度命令限幅 |
| $\ddot q_{\max}$ | `12.0 rad/s^2` | 球铰速度命令变化率限幅 |
| $e_{track,\max}$ | `0.10 rad` | 内部参考姿态相对实际姿态的最大领先量 |
| $K_p^{sim}$ | `1000.0` | Isaac/PhysX 球铰位置 drive stiffness |
| $K_d^{sim}$ | `10.0` | Isaac/PhysX 球铰速度 drive damping |
| $\tau_{q,\max}^{sim}$ | `20.0 Nm` | 球铰驱动器 effort limit |
| $\dot q_{limit}^{sim}$ | `2.0 rad/s` | 球铰驱动器 velocity limit |
| $\lambda_{track}$ | `1.0` | 平面命令整形中保持原命令的权重 |
| $\lambda_{lat}$ | `10.0` | 平面命令整形中抑制名义侧向速度的权重 |
| $c_{off}$ | `0.01` | 接触权重为 0 的归一化接触力阈值 |
| $c_{on}$ | `0.08` | 接触权重为 1 的归一化接触力阈值 |
| $K_\Omega$ | `2.0` | 轮速误差到基础力矩的比例增益 |
| $K_\kappa$ | `1.5` | 旧版纵滑反馈力矩增益；已降低以避免低速正滑转时反馈过强 |
| $\epsilon$ | `0.1 m/s` | 纵滑率和侧滑角计算的低速保护项 |
| $\tau_{\max}$ | `15.0 Nm` | 车轮最终力矩限幅 |

注意：$c_{off}$ 和 $c_{on}$ 使用的是归一化接触力，不是牛顿。代码中先计算：

$$
c_j=\frac{\lVert \mathbf F_{n,j}\rVert}{mg}
$$

因此 $c_j=0.08$ 表示第 $j$ 个车轮的接触合力约等于整车重量的 8%。

## 4. RL 动作到高层命令

当前 policy 动作为 8 维：

$$
\mathbf a =
\begin{bmatrix}
a_v & a_\omega & a_{q,1} & a_{q,2} & a_{q,3} & a_{q,4} & a_{q,5} & a_{q,6}
\end{bmatrix}^T
$$

前 2 维映射为平面运动命令：

$$
\mathbf u_d=
\begin{bmatrix}
v_x^d\\
\omega_z^d
\end{bmatrix}
$$

当前 Stage0 不允许倒车，所以前进速度使用半区间映射：

$$
v_x^d=\frac{a_v+1}{2}v_{x,\max}
$$

偏航角速度使用对称映射：

$$
\omega_z^d=a_\omega \omega_{z,\max}
$$

后 6 维动作映射为球铰最终目标姿态：

$$
\mathbf q^d=
\begin{bmatrix}
q_1^d & q_2^d & q_3^d & q_4^d & q_5^d & q_6^d
\end{bmatrix}^T
$$

该目标姿态首先被限制在当前 Stage0 的球铰角范围内：

$$
\mathbf q^d
\leftarrow
\mathrm{clip}
\left(
\mathbf q^d,
\mathbf q_{min},
\mathbf q_{max}
\right)
$$

Stage0 当前球铰上下限为：

$$
\mathbf q_{min}
=
\begin{bmatrix}
-0.6 & -1.0 & -0.5 & -0.6 & -1.0 & -0.5
\end{bmatrix}^T
$$

$$
\mathbf q_{max}
=
\begin{bmatrix}
0.6 & 0.4 & 0.5 & 0.6 & 0.4 & 0.5
\end{bmatrix}^T
$$

## 5. 球铰轨迹生成器

### 5.1 为什么不能直接下发 $q^d$

$\mathbf q^d$ 是 policy 想到达的最终球铰姿态。如果直接把 $\mathbf q^d$ 下发给 Isaac 的位置目标，关节目标会在一个控制步内突变，PhysX PD 会尝试用很大的驱动力矩快速追踪，容易造成：

- 球铰动作突变；
- 车轮几何构型突变；
- 轮速分配中的姿态变化速度与实际执行不一致；
- 轮地接触状态瞬间变化，导致纵滑和侧滑放大。

因此当前代码在 `env.py` 中维护内部参考姿态 $\mathbf q^{ref}$ 和上一时刻速度命令 $\dot{\mathbf q}^{cmd}_{prev}$，用轨迹生成器把最终目标 $\mathbf q^d$ 转成平滑的 $\mathbf q^{cmd}$ 和 $\dot{\mathbf q}^{cmd}$。

### 5.2 参考姿态跟踪保护

设当前真实球铰姿态为 $\mathbf q$。轨迹生成器先限制内部参考姿态相对真实姿态的领先量：

$$
\mathbf q^{ref}
\leftarrow
\mathbf q
+
\mathrm{clip}
\left(
\mathbf q^{ref}-\mathbf q,
-e_{track,\max},
e_{track,\max}
\right)
$$

再把参考姿态限制在关节范围内：

$$
\mathbf q^{ref}
\leftarrow
\mathrm{clip}
\left(
\mathbf q^{ref},
\mathbf q_{min},
\mathbf q_{max}
\right)
$$

含义是：如果真实球铰因为接触冲击、驱动力矩不足或关节限位而没跟上，内部参考不会无限向前积分。当前 $e_{track,\max}=0.10\ \mathrm{rad}$。

### 5.3 由目标姿态生成原始速度命令

轨迹生成器根据目标姿态和内部参考姿态的误差生成原始速度：

$$
\dot{\mathbf q}^{raw}
=
K_q
\left(
\mathbf q^d-\mathbf q^{ref}
\right)
$$

这里用的是 $\mathbf q^d-\mathbf q^{ref}$，不是 $\mathbf q^d-\mathbf q$。这样轨迹是由内部参考状态连续推进的，而不是每步直接追真实状态。

### 5.4 速度限幅

$$
\dot{\mathbf q}^{sat}
=
\mathrm{clip}
\left(
\dot{\mathbf q}^{raw},
-\dot{\mathbf q}_{max},
\dot{\mathbf q}_{max}
\right)
$$

当前 $\dot q_{\max}=1.5\ \mathrm{rad/s}$。

### 5.5 加速度限幅

先计算本步希望改变的速度量：

$$
\Delta \dot{\mathbf q}
=
\dot{\mathbf q}^{sat}
-
\dot{\mathbf q}^{cmd}_{prev}
$$

然后限制速度变化率：

$$
\Delta \dot{\mathbf q}
\leftarrow
\mathrm{clip}
\left(
\Delta \dot{\mathbf q},
-\ddot{\mathbf q}_{max}\Delta t_c,
\ddot{\mathbf q}_{max}\Delta t_c
\right)
$$

最终速度命令为：

$$
\dot{\mathbf q}^{cmd}
=
\dot{\mathbf q}^{cmd}_{prev}
+
\Delta \dot{\mathbf q}
$$

当前 $\ddot q_{\max}=12.0\ \mathrm{rad/s^2}$，$\Delta t_c=1/60\ \mathrm{s}$，所以每个控制步速度最多变化：

$$
\ddot q_{\max}\Delta t_c
=
12.0\times\frac{1}{60}
=
0.2\ \mathrm{rad/s}
$$

### 5.6 积分得到位置目标

轨迹生成器用速度命令积分得到本步球铰位置目标：

$$
\mathbf q^{cmd}
=
\mathrm{clip}
\left(
\mathbf q^{ref}
+
\Delta t_c\dot{\mathbf q}^{cmd},
\mathbf q_{min},
\mathbf q_{max}
\right)
$$

如果 $\mathbf q^{cmd}$ 被上下限截断，需要重新计算真实生效的速度命令：

$$
\dot{\mathbf q}^{cmd}
=
\frac{
\mathbf q^{cmd}-\mathbf q^{ref}
}{
\Delta t_c
}
$$

这一步保证了：

$$
\mathbf q^{cmd}
=
\mathbf q^{ref}
+
\Delta t_c\dot{\mathbf q}^{cmd}
$$

也就是说，轮速分配器拿到的 $\dot{\mathbf q}^{cmd}$ 与真正下发给 Isaac 的 $\mathbf q^{cmd}$ 是一致的。

### 5.7 球铰轨迹生成数值例子

假设某一个球铰当前：

$$
q^{ref}=0.10\ \mathrm{rad}
$$

policy 给出的最终目标为：

$$
q^d=0.40\ \mathrm{rad}
$$

上一控制步速度命令为：

$$
\dot q^{cmd}_{prev}=0
$$

第一步计算原始速度：

$$
\dot q^{raw}
=
8.0\times(0.40-0.10)
=
2.4\ \mathrm{rad/s}
$$

速度限幅后：

$$
\dot q^{sat}
=
1.5\ \mathrm{rad/s}
$$

由于每步速度最多增加 $0.2\ \mathrm{rad/s}$，所以本步最终速度命令为：

$$
\dot q^{cmd}
=
0+0.2
=
0.2\ \mathrm{rad/s}
$$

积分得到位置目标：

$$
q^{cmd}
=
0.10+\frac{1}{60}\times0.2
=
0.1033\ \mathrm{rad}
$$

下一步如果误差仍然较大，速度会继续按 $0.2\ \mathrm{rad/s}$ 的步长增加：

```text
0.0 -> 0.2 -> 0.4 -> 0.6 -> 0.8 -> 1.0 -> 1.2 -> 1.4 -> 1.5 rad/s
```

因此球铰不会一步跳到 $0.40\ \mathrm{rad}$，而是按速度和加速度限制平滑逼近。

## 6. Isaac/PhysX 球铰隐式 PD 执行层

### 6.1 当前下发方式

当前 `_apply_action()` 对球铰同时下发位置目标和速度目标：

```text
set_joint_position_target(q_cmd)
set_joint_velocity_target(qdot_cmd)
```

球铰 actuator 类型为 `ImplicitActuatorCfg`，参数为：

| 参数 | 当前值 |
|---|---:|
| stiffness | `1000.0` |
| damping | `10.0` |
| effort_limit_sim | `20.0 Nm` |
| velocity_limit_sim | `2.0 rad/s` |

因此球铰不是项目代码直接输出力矩，而是项目代码输出 $\mathbf q^{cmd}$ 与 $\dot{\mathbf q}^{cmd}$，再由 Isaac/PhysX 的隐式 drive 近似执行 PD 跟踪。

### 6.2 近似执行公式

对第 $i$ 个球铰，可把 Isaac/PhysX drive 理解为近似执行：

$$
\tau_{q,i}^{pd}
=
K_p^{sim}
\left(
q_i^{cmd}-q_i
\right)
+
K_d^{sim}
\left(
\dot q_i^{cmd}-\dot q_i
\right)
$$

然后受到力矩上限约束：

$$
\tau_{q,i}^{sim}
=
\mathrm{clip}
\left(
\tau_{q,i}^{pd},
-\tau_{q,\max}^{sim},
\tau_{q,\max}^{sim}
\right)
$$

这里：

- $q_i$ 是 Isaac 当前实际球铰角；
- $\dot q_i$ 是 Isaac 当前实际球铰角速度；
- $q_i^{cmd}$ 是轨迹生成器输出的位置目标；
- $\dot q_i^{cmd}$ 是轨迹生成器输出的速度目标；
- $K_p^{sim}=1000.0$；
- $K_d^{sim}=10.0$；
- $\tau_{q,\max}^{sim}=20.0\ \mathrm{Nm}$。

### 6.3 PD 数值例子

沿用上面的轨迹生成器例子：

$$
q=0.1000,\qquad
q^{cmd}=0.1033,\qquad
\dot q=0,\qquad
\dot q^{cmd}=0.2
$$

则：

$$
\tau_q^{pd}
=
1000.0\times(0.1033-0.1000)
+
10.0\times(0.2-0)
$$

$$
\tau_q^{pd}
=
3.3+2.0
=
5.3\ \mathrm{Nm}
$$

如果实际球铰已经转得更快，例如：

$$
\dot q=0.5\ \mathrm{rad/s}
$$

则阻尼项会变成负值：

$$
\tau_q^{pd}
=
3.3
+
10.0\times(0.2-0.5)
=
0.3\ \mathrm{Nm}
$$

这说明速度目标不是装饰项。它会通过 Isaac 的 damping 项影响实际球铰驱动力矩，也会同时进入轮速分配模型。

## 7. 轮速分配所用的几何量

### 7.1 当前几何计算使用实际球铰姿态

轮速分配器不是用 $\mathbf q^d$，也不是用 $\mathbf q^{cmd}$ 计算当前轮子几何，而是用实际球铰姿态：

$$
\mathbf q=\mathbf q^{actual}
$$

根据当前 $\mathbf q$，对每个车轮 $j$ 计算：

| 符号 | 含义 |
|---|---|
| $\mathbf p_j(\mathbf q)$ | 第 $j$ 个轮心在中车体坐标系中的位置 |
| $\mathbf t_j(\mathbf q)$ | 第 $j$ 个车轮滚动方向单位向量 |
| $\mathbf n_j(\mathbf q)$ | 第 $j$ 个车轮侧向单位向量 |
| $\mathbf J_j(\mathbf q)$ | 球铰速度到第 $j$ 个轮心速度的雅可比 |

前车体和后车体轮子的 $\mathbf p_j$、$\mathbf t_j$、$\mathbf n_j$ 随球铰姿态变化；中车体两个轮子的方向和位置相对中车体固定。

### 7.2 姿态速度使用轨迹生成器的最终速度命令

轮速分配器中用于预测构型变化速度的是：

$$
\dot{\mathbf q}^{cmd}
$$

也就是球铰执行器同一控制步下发的速度目标，而不是重新由 $\mathbf q^d-\mathbf q$ 算出的另一个速度。

因此当前链路满足：

$$
\boxed{
\text{球铰执行器用 } \mathbf q^{cmd},\dot{\mathbf q}^{cmd}
}
$$

$$
\boxed{
\text{轮速分配器也用同一个 } \dot{\mathbf q}^{cmd}
}
$$

这可以避免“球铰执行层认为应该慢慢动，轮速分配层却认为球铰正在快速动”的不一致。

## 8. 接触权重

传感器获得每个车轮的接触合力 $\mathbf F_{n,j}$，代码中先归一化：

$$
c_j
=
\frac{
\lVert\mathbf F_{n,j}\rVert
}{
mg
}
$$

然后计算接触权重：

$$
C_{w,j}
=
\mathrm{clip}
\left(
\frac{
c_j-c_{off}
}{
c_{on}-c_{off}
},
0,
1
\right)
$$

当前：

$$
c_{off}=0.01,\qquad c_{on}=0.08
$$

含义：

- 当 $c_j\le 0.01$ 时，认为该轮接触不可靠，$C_{w,j}=0$。
- 当 $c_j\ge 0.08$ 时，认为该轮接触可靠，$C_{w,j}=1$。
- 中间线性过渡。

数值例子：

| $c_j$ | $C_{w,j}$ | 含义 |
|---:|---:|---|
| `0.005` | `0.000` | 接触太弱，该轮力矩被关掉 |
| `0.020` | `0.143` | 接触较弱，只保留约 14.3% 权重 |
| `0.045` | `0.500` | 中等接触，保留 50% 权重 |
| `0.080` | `1.000` | 接触可靠，保留完整权重 |
| `0.120` | `1.000` | 超过阈值后仍为 1 |

## 9. 低侧滑平面命令整形

### 9.1 名义轮心速度

设整车平面命令为：

$$
\mathbf u=
\begin{bmatrix}
v_x\\
\omega_z
\end{bmatrix}
$$

第 $j$ 个轮心的名义速度由三部分组成：

$$
\mathbf v_j^{nom}
=
v_x\mathbf e_x
+
\omega_z
\left(
\mathbf e_z\times\mathbf p_j(\mathbf q)
\right)
+
\mathbf J_j(\mathbf q)\dot{\mathbf q}^{cmd}
$$

三项含义分别是：

- $v_x\mathbf e_x$：中车体前进速度造成的轮心速度；
- $\omega_z(\mathbf e_z\times\mathbf p_j)$：中车体偏航造成的轮心速度；
- $\mathbf J_j\dot{\mathbf q}^{cmd}$：球铰构型变化造成的轮心速度。

### 9.2 轮心名义侧向速度

第 $j$ 个轮子的名义侧向速度为：

$$
v_{j,\perp}^{nom}
=
\mathbf n_j^T
\mathbf v_j^{nom}
$$

把上式展开成关于 $\mathbf u$ 的线性形式：

$$
v_{j,\perp}^{nom}
=
\mathbf a_j^T\mathbf u
+
b_j
$$

其中：

$$
\mathbf a_j
=
\begin{bmatrix}
\mathbf n_j^T\mathbf e_x\\
\mathbf n_j^T(\mathbf e_z\times\mathbf p_j)
\end{bmatrix}
$$

$$
b_j
=
\mathbf n_j^T\mathbf J_j\dot{\mathbf q}^{cmd}
$$

### 9.3 加权最小二乘整形

低侧滑整形的目标是：尽量接近 policy 给出的原平面命令 $\mathbf u_d$，同时压低有接触轮子的名义侧向速度。

当前优化目标为：

$$
\mathbf u^*
=
\arg\min_{\mathbf u}
\left[
\lambda_{track}
\lVert
\mathbf u-\mathbf u_d
\rVert^2
+
\lambda_{lat}
\sum_{j=1}^{6}
C_{w,j}
\left(
\mathbf a_j^T\mathbf u+b_j
\right)^2
\right]
$$

其中：

$$
\lambda_{track}=1.0,\qquad
\lambda_{lat}=10.0
$$

该问题是二维加权最小二乘，代码中构造：

$$
\mathbf H
=
\lambda_{track}\mathbf I
+
\lambda_{lat}
\sum_{j=1}^{6}
C_{w,j}
\mathbf a_j\mathbf a_j^T
$$

$$
\mathbf r
=
\lambda_{track}\mathbf u_d
-
\lambda_{lat}
\sum_{j=1}^{6}
C_{w,j}
\mathbf a_j b_j
$$

然后求解：

$$
\mathbf H\mathbf u^*=\mathbf r
$$

最后对 $\mathbf u^*$ 做速度命令限幅：

$$
\mathbf u^*
\leftarrow
\mathrm{clip}
\left(
\mathbf u^*,
-
\begin{bmatrix}
v_{x,\max}\\
\omega_{z,\max}
\end{bmatrix},
\begin{bmatrix}
v_{x,\max}\\
\omega_{z,\max}
\end{bmatrix}
\right)
$$

### 9.4 整形的物理含义

如果某些轮子接触可靠，且当前平面命令会让这些轮子产生较大名义侧向速度，则优化会改变 $v_x$ 和 $\omega_z$，让几何上更接近“沿轮子滚动方向运动”。

如果某个轮子几乎离地，$C_{w,j}\approx 0$，则这个轮子的侧向速度不会强烈影响平面命令整形。

这一步是运动学层面的低侧滑处理，作用在轮速参考生成之前。

## 10. 轮速参考计算

用整形后的平面命令 $\mathbf u^*=[v_x^*,\omega_z^*]^T$ 重新计算第 $j$ 个轮心名义速度：

$$
\mathbf v_j^{nom}
=
v_x^*\mathbf e_x
+
\omega_z^*
\left(
\mathbf e_z\times\mathbf p_j(\mathbf q)
\right)
+
\mathbf J_j(\mathbf q)\dot{\mathbf q}^{cmd}
$$

沿车轮滚动方向投影，得到滚动线速度参考：

$$
s_j^{ref}
=
\mathbf t_j^T(\mathbf q)
\mathbf v_j^{nom}
$$

再除以车轮半径得到参考角速度：

$$
\Omega_j^{ref}
=
\frac{
s_j^{ref}
}{
r
}
$$

合起来就是：

$$
\Omega_j^{ref}
=
\frac{
\mathbf t_j^T(\mathbf q)
\left[
v_x^*\mathbf e_x
+
\omega_z^*
\left(
\mathbf e_z\times\mathbf p_j(\mathbf q)
\right)
+
\mathbf J_j(\mathbf q)\dot{\mathbf q}^{cmd}
\right]
}{
r
}
$$

这里再次强调：

- $\mathbf q$ 使用真实球铰姿态 $\mathbf q^{actual}$；
- $\dot{\mathbf q}^{cmd}$ 使用轨迹生成器输出的最终球铰速度命令；
- $\Omega_j^{ref}$ 只是力矩控制器的内部参考，不是 Isaac 的车轮速度目标。

### 10.1 简化数值例子

假设某个中车体轮子的几何方向刚好满足：

$$
\mathbf t_j=\mathbf e_x,\qquad
\mathbf J_j\dot{\mathbf q}^{cmd}=0
$$

且整形后的命令为：

$$
v_x^*=1.2\ \mathrm{m/s},\qquad
\omega_z^*=0
$$

则滚动线速度参考为：

$$
s_j^{ref}=1.2\ \mathrm{m/s}
$$

车轮半径 $r=0.19\ \mathrm{m}$，所以：

$$
\Omega_j^{ref}
=
\frac{1.2}{0.19}
=
6.316\ \mathrm{rad/s}
$$

如果某个前轮因为球铰姿态和偏航命令，沿滚动方向投影后只有：

$$
s_j^{ref}=0.8\ \mathrm{m/s}
$$

则：

$$
\Omega_j^{ref}
=
\frac{0.8}{0.19}
=
4.211\ \mathrm{rad/s}
$$

这说明六个轮子的参考角速度本来就可以不同，因为它们的位置、方向和球铰引起的轮心速度不同。

## 11. 实际轮心速度、纵滑率和侧滑角

### 11.1 实际轮心纵向速度

代码从 Isaac 读取每个车轮 body 的世界系线速度 $\mathbf v_j$，再投影到车轮实际滚动方向：

$$
V_{j,\parallel}
=
\mathbf v_j^T\mathbf t_j
$$

这是真实轮心速度沿滚动方向的分量。

### 11.2 实际轮心侧向速度

同理，投影到车轮实际侧向方向：

$$
V_{j,\perp}
=
\mathbf v_j^T\mathbf n_j
$$

这是车轮横向滑动速度的直接来源。

### 11.3 纵向滑移率

车轮圆周速度与实际纵向速度的差值为：

$$
\Delta V_j
=
r\Omega_j
-
V_{j,\parallel}
$$

当前纵向滑移率定义为：

$$
\kappa_j
=
\frac{
r\Omega_j
-
V_{j,\parallel}
}{
\max
\left(
\lvert V_{j,\parallel}\rvert,
\epsilon
\right)
}
$$

其中 $\Omega_j$ 是实际车轮角速度，$\epsilon=0.1\ \mathrm{m/s}$。

符号含义：

- $\kappa_j>0$：车轮圆周速度大于轮心实际前进速度，存在正向滑转趋势。
- $\kappa_j<0$：车轮圆周速度小于轮心实际前进速度，存在制动拖滑趋势。
- $\kappa_j=0$：车轮圆周速度和实际滚动速度匹配。

### 11.4 侧滑角

当前侧滑角定义为：

$$
\alpha_j
=
\operatorname{atan2}
\left(
V_{j,\perp},
\lvert V_{j,\parallel}\rvert+\epsilon
\right)
$$

其中 $\epsilon=0.1\ \mathrm{m/s}$。这个定义会在低纵向速度时避免分母过小导致侧滑角突变。

如果 $V_{j,\perp}=0$，则 $\alpha_j=0$。如果侧向速度较大且纵向速度很小，则 $\alpha_j$ 会接近较大角度。

## 12. 车轮力矩控制器

2026-04-26 已按用户要求，将车轮力矩控制器恢复为 `stage0_lowslip_gate_v2_min_lowlevel_522iter` 使用的旧版公式。当前不再使用纵滑衰减 $g_{\kappa,j}$ 和侧滑衰减 $g_{\alpha,j}$ 削弱驱动力矩；这两个 TensorBoard 字段仅作为兼容日志保留，当前值固定为 `1.0`。

### 12.1 基础轮速跟踪力矩

当前车轮基础力矩为：

$$
\tau_j^0
=
K_\Omega
\left(
\Omega_j^{ref}
-
\Omega_j
\right)
$$

其中：

- $\Omega_j^{ref}$ 是运动学轮速分配得到的参考角速度；
- $\Omega_j$ 是 Isaac 中读到的实际车轮关节角速度；
- $K_\Omega=2.0$。

### 12.2 当前 signed 纵滑率

旧版恢复时曾短暂使用反号定义。当前已按检查结果统一修正为正向滑转为正：

$$
\kappa_j
=
\frac{
\rho\Omega_j
-
V_{j,\parallel}
}{
\max(|V_{j,\parallel}|,\epsilon)
}
$$

其中 $\rho=0.19\ \mathrm{m}$，$\epsilon=0.1\ \mathrm{m/s}$。

在当前定义下：

- 当车轮圆周速度大于实际纵向速度时，$\kappa_j>0$；
- 当车轮圆周速度小于实际纵向速度时，$\kappa_j<0$。

### 12.3 纵滑反馈力矩

旧版纵滑反馈力矩为：

$$
\tau_j^{slip}
=
-
K_\kappa
\kappa_j
$$

当前 Stage0 使用：

$$
K_\kappa=1.5
$$

基础轮速跟踪力矩和纵滑反馈力矩相加后，得到乘接触权重之前的力矩：

$$
\tau_j^1
=
\tau_j^0
-
K_\kappa\kappa_j
$$

### 12.4 最终车轮力矩

最终下发车轮力矩为：

$$
\tau_j
=
\mathrm{clip}
\left(
C_{w,j}
\left[
K_\Omega
\left(
\Omega_j^{ref}-\Omega_j
\right)
-
K_\kappa\kappa_j
\right],
-\tau_{\max},
\tau_{\max}
\right)
$$

当前 $\tau_{\max}=15.0\ \mathrm{Nm}$。

也就是说，当前车轮力矩只受三项直接影响：

- 轮速参考与实际轮速误差；
- 当前 signed 纵滑反馈项；
- 接触权重 $C_{w,j}$。

## 13. 力矩控制数值例子

### 13.1 车轮圆周速度大于实际纵向速度

假设某个车轮：

$$
\rho=0.19,\qquad
\Omega_j=8.0\ \mathrm{rad/s},\qquad
V_{j,\parallel}=1.0\ \mathrm{m/s}
$$

则：

$$
\rho\Omega_j=0.19\times8.0=1.52\ \mathrm{m/s}
$$

当前 signed 纵滑率为：

$$
\kappa_j
=
\frac{1.52-1.0}{\max(1.0,0.1)}
=
0.52
$$

若轮速参考为：

$$
\Omega_j^{ref}=10.0\ \mathrm{rad/s}
$$

基础轮速跟踪力矩为：

$$
\tau_j^0
=
2.0\times(10.0-8.0)
=
4.0\ \mathrm{Nm}
$$

纵滑反馈项为：

$$
-K_\kappa\kappa_j
=
-1.5\times0.52
=
-0.78\ \mathrm{Nm}
$$

乘接触权重前：

$$
\tau_j^1
=
4.0-0.78
=
3.22\ \mathrm{Nm}
$$

若该轮接触可靠 $C_{w,j}=1$，最终力矩为：

$$
\tau_j=3.22\ \mathrm{Nm}
$$

这表示：当轮速跟踪项仍强烈要求加速时，较小的纵滑反馈不会直接把净力矩反向压死，而是削弱加速力矩。若实际轮速已经高于参考轮速，轮速跟踪项和纵滑反馈项会同向制动。

### 13.2 接触力不足

假设某个轮子的归一化接触力为：

$$
c_j=0.02
$$

则：

$$
C_{w,j}
=
\frac{0.02-0.01}{0.08-0.01}
=
0.143
$$

如果 $\tau_j^1=3.0\ \mathrm{Nm}$，最终力矩为：

$$
\tau_j
=
0.143\times3.0
=
0.429\ \mathrm{Nm}
$$

因此接触不足的轮子仍会被接触权重削弱。恢复旧版力矩控制器后，车轮力矩不再受侧滑角衰减，但仍受接触权重限制。

## 14. 当前链路中两类低滑移机制

当前底层控制不是单一惩罚项，而是两类机制叠加：

| 层级 | 位置 | 作用对象 | 主要作用 |
|---|---|---|---|
| 平面命令整形 | 轮速参考生成前 | $v_x,\omega_z$ | 让有接触轮子的名义侧向速度更低 |
| 旧版纵滑反馈 | 力矩控制内部 | $\kappa_j$ | 通过 $-K_\kappa\kappa_j$ 直接修正力矩 |
| 接触权重 | 轮速整形和最终力矩 | $C_{w,j}$ | 接触不可靠时降低该轮影响和力矩 |

其中：

- 运动学整形处理的是“预计会不会侧滑”；
- 力矩控制处理的是“实际纵滑率如何修正轮速跟踪力矩”；
- 接触权重处理的是“这个轮子当前是否值得信任”。

## 15. 当前日志可用于审查的量

当前 TensorBoard / metrics 中已写入每个轮子的关键状态：

| 日志项 | 含义 |
|---|---|
| `wheel_joint_vel` | 实际车轮关节角速度 $\Omega_j$ |
| `wheel_speed_reference` | 轮速分配得到的参考角速度 $\Omega_j^{ref}$ |
| `wheel_torque_target` | 最终下发车轮力矩 $\tau_j$ |
| `contact_weight` | 接触权重 $C_{w,j}$ |
| `normal_force` | 车轮接触合力，单位 N |
| `longitudinal_slip` | 纵向滑移率 $\kappa_j$ |
| `slip_angle` | 侧滑角 $\alpha_j$ |

当前也已加入中车体姿态日志：

| 日志项 | 含义 |
|---|---|
| `Observation/roll_deg` | 中车体 roll 均值 |
| `Observation/tilt_deg` | 当前仍等价于 roll 的绝对值均值 |
| `Observation/pitch_deg` | 中车体 pitch 均值 |
| `Observation/pitch_abs_deg` | 中车体 pitch 绝对值均值 |

如果后续要更严格审查力矩控制器，建议继续补充以下中间量日志：

| 建议日志项 | 用途 |
|---|---|
| $V_{j,\parallel}$ | 判断纵滑率来自实际低速还是轮速过高 |
| $V_{j,\perp}$ | 判断侧滑角来自横向速度还是低速分母 |
| $\Delta V_j$ | 判断纵滑方向 |
| $\tau_j^0$ | 查看基础轮速跟踪力矩 |
| $g_{\kappa,j}$ | 兼容字段；当前固定为 `1.0` |
| $\tau_j^1$ | 查看旧版纵滑反馈后的力矩 |
| $g_{\alpha,j}$ | 兼容字段；当前固定为 `1.0` |

这些不是当前链路正确运行的必要条件，但对严格定位“为什么某个轮子力矩被压低或没有被压低”很有用。

## 16. 当前链路的检查重点

后续检查底层模型时，重点应按下面顺序排查：

1. 球铰轨迹是否真实跟上 `q_cmd/qdot_cmd`。如果球铰跟踪明显滞后，轮速分配使用的 $\dot{\mathbf q}^{cmd}$ 可能仍然高估实际构型变化。
2. `wheel_speed_reference` 是否与当前几何构型一致。特别是前轮和后轮在大球铰角时，$\mathbf t_j$ 和 $\mathbf J_j\dot{\mathbf q}^{cmd}$ 会显著改变 $\Omega_j^{ref}$。
3. `wheel_joint_vel` 是否长期大于 `wheel_speed_reference`。如果是，基础力矩 $\tau_j^0$ 应该多为负，起减速作用。
4. 当前 signed 纵滑率和 $-K_\kappa\kappa_j$ 项的符号是否符合预期。当前定义下，正向滑转对应 $\kappa_j>0$，反馈项会提供负向力矩贡献。
5. 接触权重是否过低。若 $C_{w,j}$ 长期低，说明轮子接触不足，该轮最终力矩仍会被大幅压低。
6. 中车体 pitch 是否长期为负或正。如果车体持续前俯，会改变轮地载荷分配，导致某些轮子接触权重和纵滑异常。

## 17. 一句话总结

当前底层控制链路可以概括为：

$$
\boxed{
\mathbf q^d
\rightarrow
\mathbf q^{cmd},\dot{\mathbf q}^{cmd}
\rightarrow
\text{Isaac/PhysX PD}
\rightarrow
\mathbf q,\dot{\mathbf q}
}
$$

$$
\boxed{
\mathbf q^{actual},\dot{\mathbf q}^{cmd},\mathbf u_d,C_w
\rightarrow
\mathbf u^*
\rightarrow
\Omega^{ref}
\rightarrow
\tau
}
$$

其中球铰控制器解决“构型如何平滑执行”，轮速分配器解决“当前构型下每个轮子应该转多快”，力矩控制器解决“在实际纵滑、侧滑和接触状态下，最终还应该给多少力矩”。
