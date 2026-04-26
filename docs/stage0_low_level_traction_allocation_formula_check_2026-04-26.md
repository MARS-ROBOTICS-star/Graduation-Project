# Stage0 底层接触感知轮级牵引分配公式核对

日期：2026-04-26

核对对象：

- 训练 run：`RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-26_10-32-46_stage0_lowslip_gate_v2_min_lowlevel_800iter`
- 停止位置：iteration `522/800`
- 最新 checkpoint：`model_500.pt`
- 主要源码：
  - `base/env.py`
  - `mdp/actions.py`
  - `kinematics/wheel_speed_allocator.py`
  - `baseline/complete_car_stage0_cfg.py`
  - `assets/actuators_cfg.py`

本文目标是把当前底层控制器公式逐项展开，并把 2026-04-26 训练数据代入检查。本文已同步更新新的球铰控制链路：球铰轨迹生成器输出同一套 `q_cmd/qdot_cmd`，球铰执行器下发 `position_target=q_cmd` 与 `velocity_target=qdot_cmd`，轮速分配器也复用同一个 `qdot_cmd`。

## 1. 总体结论

当前底层链路确实是“力矩控制”，不是 Isaac 的车轮速度控制：

- `wheel_speed_reference` 只是底层控制器内部计算力矩用的参考量。
- 最终下发给车轮关节的是 `wheel_torque_targets`。
- 车轮 actuator 当前 `stiffness=0`、`damping=0`，`effort_limit_sim=15.0`，因此车轮主要通过 effort target 工作。
- 球铰不是直接 torque control，而是先由项目自己的轨迹生成器生成 `q_cmd/qdot_cmd`，再交给 Isaac/PhysX 的 `ImplicitActuator` 隐式 PD drive 执行。
- 当前代码已经把 `qdot_cmd` 作为 Isaac 的球铰速度目标下发，同时轮速分配器也使用同一个 `qdot_cmd`；不再让执行器和轮速分配器各自计算不同的球铰速度。

2026-04-26 已按用户要求，将车轮力矩控制器恢复为 `stage0_lowslip_gate_v2_min_lowlevel_522iter` 使用的旧版公式结构，并修正 signed 纵滑方向：

- signed 纵滑定义统一为 $\kappa_i=(r\Omega_i^{act}-s_i^{act})/\max(|s_i^{act}|,\epsilon)$。
- 车轮圆周速度大于实际纵向速度时，$\kappa_i>0$。
- 车轮力矩恢复为旧版直接纵滑反馈：$w_i[K_\Omega(\Omega_i^{ref}-\Omega_i^{act})-K_\kappa\kappa_i]$。
- 当前不再使用纵滑衰减 $g_{\kappa,i}$ 和侧滑衰减 $g_{\alpha,i}$ 削弱驱动力矩；这两个日志字段仅作为兼容字段保留，当前固定为 `1.0`。

换句话说：此前“纵滑方向判断衰减 + 侧滑衰减”的新控制器已被撤回，但旧版恢复时暴露出的 signed 纵滑反号问题已经修正。当前需要重新通过回放或训练验证该力矩控制器在新球铰 `q_cmd/qdot_cmd` 链路下的实际效果。

## 2. 当前底层执行链路

当前每个控制步的执行顺序如下：

```text
policy action a
  -> 平面命令 u_d = [v_x^d, omega_z^d]
  -> 球铰期望姿态 q^d
  -> 球铰轨迹生成器输出 q_cmd, qdot_cmd
  -> 根据当前 q 计算六个轮子的 p_i, t_i, n_i, J_i
  -> 轮速分配器复用同一个 qdot_cmd
  -> 根据接触力计算 contact weight w_i
  -> 用接触权重做低侧滑平面命令整形 u*
  -> 计算每个轮子的 Omega_ref
  -> 根据 Omega_ref、Omega_act、实际纵向/侧向速度、纵滑、侧滑角、接触权重计算 tau_cmd
  -> set_joint_position_target(q_cmd) 与 set_joint_velocity_target(qdot_cmd) 下发球铰目标
  -> set_joint_effort_target 下发车轮力矩
```

其中高层 policy 动作维度为 8：

$$
\mathbf a =
\left[
a_v,\ a_\omega,\ a_{q,1},\ldots,a_{q,6}
\right]
$$

前 2 维映射成底盘平面命令，后 6 维映射成球铰期望姿态。

## 3. 当前训练使用的主要参数

| 参数 | 数值 | 作用 |
|---|---:|---|
| $r$ | `0.19 m` | 车轮半径 |
| $v_{x,\max}$ | `2.0 m/s` | 前进速度命令上限 |
| $\omega_{z,\max}$ | `2.0 rad/s` | 偏航角速度命令上限 |
| $\Delta t_c$ | `1/60 s` | 控制周期 |
| $K_q$ | `8.0` | 球铰姿态误差到球铰速度命令的比例增益 |
| $\dot q_{\max}$ | `1.5 rad/s` | 球铰速度命令限幅 |
| $\ddot q_{\max}$ | `12.0 rad/s^2` | 球铰速度命令变化率限幅 |
| $e_{track,\max}$ | `0.10 rad` | 参考轨迹相对实际球铰角的最大领先量 |
| $K_p^{sim}$ | `1000.0` | Isaac/PhysX 球铰位置 drive stiffness |
| $K_d^{sim}$ | `10.0` | Isaac/PhysX 球铰速度 drive damping |
| $\tau_{q,\max}^{sim}$ | `20.0 Nm` | Isaac/PhysX 球铰 effort limit |
| $\dot q_{limit}^{sim}$ | `2.0 rad/s` | Isaac/PhysX 球铰 velocity limit |
| $\lambda_{track}$ | `1.0` | 平面命令整形中保留原命令的权重 |
| $\lambda_{lat}$ | `10.0` | 平面命令整形中抑制名义侧向速度的权重 |
| $c_{off}$ | `0.01` | 接触权重为 0 的归一化接触力阈值 |
| $c_{on}$ | `0.08` | 接触权重为 1 的归一化接触力阈值 |
| $K_\Omega$ | `2.0` | 车轮角速度跟踪项增益 |
| $K_\kappa$ | `1.5` | 旧版纵滑反馈力矩增益；已降低以避免低速正滑转时反馈过强 |
| $\epsilon$ | `0.1` | 纵滑计算中的速度保护项 |
| $\tau_{\max}$ | `15.0 Nm` | 车轮力矩限幅 |

注意：$c_{off}$ 和 $c_{on}$ 不是牛顿单位。源码中先把车轮接触合力除以整车重量：

$$
c_i=\frac{\|\mathbf F_i\|}{W}
$$

其中 $W=mg$ 是整车重量。因此 $c_i=0.08$ 表示某个轮子承担约 8% 整车重量，而不是 `0.08 N`。

## 4. 公式展开

### 4.1 policy 动作到平面命令

当前不允许倒车，前进速度由归一化动作 $a_v\in[-1,1]$ 映射为：

$$
v_x^d=\frac{1}{2}(a_v+1)v_{x,\max}
$$

偏航角速度命令为：

$$
\omega_z^d=a_\omega\omega_{z,\max}
$$

因此平面命令为：

$$
\mathbf u_d=
\begin{bmatrix}
v_x^d\\
\omega_z^d
\end{bmatrix}
$$

### 4.2 policy 动作到球铰姿态目标

后 6 维动作被映射成球铰期望姿态：

$$
\mathbf q^d=
\begin{bmatrix}
q_1^d,\ldots,q_6^d
\end{bmatrix}^T
$$

映射结果被限制在当前 Stage0 的球铰上下限内：

$$
\mathbf q_{min}\le \mathbf q^d\le \mathbf q_{max}
$$

### 4.3 球铰位置/速度规划

底层不会把 $\mathbf q^d$ 直接下发给球铰，而是维护内部参考姿态 $\mathbf q^{ref}$ 和上一控制步速度命令 $\dot{\mathbf q}^{cmd}_{prev}$。新的链路要求球铰执行器和轮速分配器使用同一套最终速度命令。

第一步，先把策略给出的最终姿态目标限制在球铰物理范围内：

$$
\mathbf q^d
=
\mathrm{clip}
\left(
\mathbf q^d,
\mathbf q_{min},
\mathbf q_{max}
\right)
$$

第二步，防止内部参考姿态脱离真实球铰状态。设真实球铰角为 $\mathbf q$：

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

然后再次限制参考姿态：

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

第三步，用 $\mathbf q^d-\mathbf q^{ref}$ 生成原始速度命令，而不是直接用 $\mathbf q^d-\mathbf q$：

$$
\dot{\mathbf q}^{raw}
=
K_q
\left(
\mathbf q^d-\mathbf q^{ref}
\right)
$$

第四步，做速度限幅：

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

第五步，做加速度限幅：

$$
\Delta \dot{\mathbf q}
=
\mathrm{clip}
\left(
\dot{\mathbf q}^{sat}-\dot{\mathbf q}^{cmd}_{prev},
-\ddot{\mathbf q}_{max}\Delta t_c,
\ddot{\mathbf q}_{max}\Delta t_c
\right)
$$

$$
\dot{\mathbf q}^{cmd}
=
\dot{\mathbf q}^{cmd}_{prev}
+
\Delta \dot{\mathbf q}
$$

第六步，积分得到本控制步位置目标：

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

如果 $\mathbf q^{cmd}$ 被关节边界截断，则重新计算真正生效的速度命令：

$$
\dot{\mathbf q}^{cmd}
=
\frac{\mathbf q^{cmd}-\mathbf q^{ref}}{\Delta t_c}
$$

第七步，更新内部参考状态：

$$
\mathbf q^{ref}\leftarrow \mathbf q^{cmd}
$$

$$
\dot{\mathbf q}^{cmd}_{prev}\leftarrow \dot{\mathbf q}^{cmd}
$$

因此当前控制步满足：

$$
\mathbf q^{cmd}_{k+1}
=
\mathbf q^{ref}_{k}
+
\Delta t_c\dot{\mathbf q}^{cmd}_{k}
$$

球铰通过位置和速度目标执行，车轮通过力矩目标执行。轮速分配器直接复用这里得到的 $\dot{\mathbf q}^{cmd}$。

### 4.3.1 Isaac/PhysX 球铰隐式 PD drive

上面的 $\dot{\mathbf q}^{cmd}$ 现在既是项目底层轨迹生成器的最终速度命令，也是 Isaac/PhysX 球铰 drive 收到的速度目标。

项目在 `_apply_action()` 中对球铰调用：

```text
set_joint_position_target(q_cmd, ball_joint_ids)
set_joint_velocity_target(qdot_cmd, ball_joint_ids)
```

因此球铰进入 Isaac/PhysX drive 的目标可以写成：

$$
q_j^{des,sim}=q_j^{cmd}
$$

$$
\dot q_j^{des,sim}=\dot q_j^{cmd}
$$

$$
\tau_j^{ff,sim}=0
$$

也就是说：

- $\dot q_j^{cmd}$ 既决定 $q_j^{cmd}$ 每个控制步移动多少，也作为 Isaac/PhysX 的速度目标。
- Isaac/PhysX 的 PD drive 会同时跟踪 $q_j^{cmd}$ 和 $\dot q_j^{cmd}$。
- 轮速分配器使用的 $\dot q_j^{cmd}$ 与球铰执行器收到的 $\dot q_j^{cmd}$ 是同一个量。

Isaac Lab `ImplicitActuator` 对应的近似 PD 力矩可写为：

$$
\tau_j^{pd}
=
K_p^{sim}(q_j^{des,sim}-q_j)
+
K_d^{sim}(\dot q_j^{des,sim}-\dot q_j)
+
\tau_j^{ff,sim}
$$

代入当前项目的球铰下发方式：

$$
\tau_j^{pd}
=
K_p^{sim}(q_j^{cmd}-q_j)
+
K_d^{sim}(\dot q_j^{cmd}-\dot q_j)
$$

然后由仿真 effort limit 约束：

$$
\tau_j^{applied}
\approx
\mathrm{clip}
\left(
\tau_j^{pd},
-\tau_{q,\max}^{sim},
\tau_{q,\max}^{sim}
\right)
$$

需要注意两点：

- `ImplicitActuator` 的 PD 是由仿真器隐式求解执行，Isaac Lab 中记录的 torque 是近似计算量；实际约束还会受 PhysX solver、关节速度限制和接触耦合影响。
- `velocity_limit_sim=2.0 rad/s` 是仿真中的关节速度限制，不是 $\dot q_j^{des,sim}=2.0$。实际速度目标由轨迹生成器输出的 $\dot q_j^{cmd}$ 决定，并受 $\dot q_{\max}=1.5 rad/s$ 和 $\ddot q_{\max}=12.0 rad/s^2$ 约束。

### 4.4 六轮几何量

对每个车轮 $i$，底层根据当前球铰角 $\mathbf q$ 计算：

| 符号 | 含义 |
|---|---|
| $\mathbf p_i(\mathbf q)$ | 轮心在中车体坐标系中的位置 |
| $\mathbf t_i(\mathbf q)$ | 车轮滚动方向单位向量 |
| $\mathbf n_i(\mathbf q)$ | 车轮侧向方向单位向量 |
| $\mathbf J_i(\mathbf q)$ | 球铰速度到轮心速度的雅可比 |

实现中的输出顺序为：

```text
body_left, body_right, head_left, head_right, tail_left, tail_right
```

本文的数据表为了直观阅读，按物理位置显示为：

```text
前左, 前右, 中左, 中右, 后左, 后右
```

### 4.5 接触权重

第 $i$ 个车轮的归一化接触力为：

$$
c_i=\frac{\|\mathbf F_i\|}{W}
$$

其中 $\mathbf F_i$ 是传感器汇总得到的轮地接触合力，$W$ 是整车重量。

接触权重为线性饱和函数：

$$
w_i
=
\mathrm{clip}
\left(
\frac{c_i-c_{off}}{c_{on}-c_{off}},
0,
1
\right)
$$

解释：

- 当 $c_i\le c_{off}$ 时，认为该轮接触不可靠，$w_i=0$。
- 当 $c_i\ge c_{on}$ 时，认为该轮接触充分，$w_i=1$。
- 中间区域线性插值。
- $w_i$ 同时进入低侧滑命令整形和轮级力矩分配。

### 4.6 接触感知低侧滑平面命令整形

对每个车轮，名义轮心速度写成。这里几何量 $\mathbf p_i,\mathbf t_i,\mathbf n_i,\mathbf J_i$ 使用当前实际球铰姿态 $\mathbf q$，而 $\dot{\mathbf q}^{cmd}$ 使用球铰轨迹生成器最终输出、并已经下发给 Isaac 的同一套速度命令：

$$
\mathbf v_i^{nom}
=
v_x\mathbf e_x
+\omega_z(\mathbf e_z\times \mathbf p_i)
+\mathbf J_i(\mathbf q)\dot{\mathbf q}^{cmd}
$$

其中待优化变量是平面命令：

$$
\mathbf u=
\begin{bmatrix}
v_x\\
\omega_z
\end{bmatrix}
$$

车轮侧向名义速度为：

$$
v_{lat,i}^{nom}
=
\mathbf n_i^T\mathbf v_i^{nom}
$$

把它写成关于 $\mathbf u$ 的仿射形式：

$$
v_{lat,i}^{nom}
=
\mathbf a_i^T\mathbf u+b_i
$$

其中：

$$
\mathbf a_i=
\begin{bmatrix}
\mathbf n_i^T\mathbf e_x\\
\mathbf n_i^T(\mathbf e_z\times\mathbf p_i)
\end{bmatrix}
$$

$$
b_i=
\mathbf n_i^T\mathbf J_i(\mathbf q)\dot{\mathbf q}^{cmd}
$$

底层通过以下加权最小二乘问题得到整形后的平面命令 $\mathbf u^*$：

$$
\mathbf u^*
=
\arg\min_{\mathbf u}
\left[
\lambda_{track}\|\mathbf u-\mathbf u_d\|^2
+
\lambda_{lat}\sum_{i=1}^{6}w_i(\mathbf a_i^T\mathbf u+b_i)^2
\right]
$$

闭式解为：

$$
\mathbf H
=
\lambda_{track}\mathbf I
+
\lambda_{lat}\sum_{i=1}^{6}w_i\mathbf a_i\mathbf a_i^T
$$

$$
\mathbf r
=
\lambda_{track}\mathbf u_d
-
\lambda_{lat}\sum_{i=1}^{6}w_i\mathbf a_i b_i
$$

$$
\mathbf u^*=\mathbf H^{-1}\mathbf r
$$

最后 $\mathbf u^*$ 被限制在平面命令范围内：

$$
|v_x^*|\le v_{x,\max},\qquad |\omega_z^*|\le \omega_{z,\max}
$$

解释：

- $w_i$ 越大，说明第 $i$ 个轮子接触越可信，该轮的侧向名义速度越会被压低。
- $w_i$ 越小，说明该轮接触弱或离地，该轮对低侧滑整形的影响越小。
- 该整形只抑制“名义运动学侧向速度”，不直接使用实际测得的侧滑角 $\alpha_i$ 做反馈。

### 4.7 轮速参考

整形后的轮心名义速度为：

$$
\mathbf v_i^{nom,*}
=
v_x^*\mathbf e_x
+\omega_z^*(\mathbf e_z\times \mathbf p_i)
+\mathbf J_i(\mathbf q)\dot{\mathbf q}^{cmd}
$$

沿车轮滚动方向投影得到参考滚动线速度：

$$
s_i^{ref}
=
\mathbf t_i^T\mathbf v_i^{nom,*}
$$

再除以车轮半径得到角速度参考：

$$
\Omega_i^{ref}
=
\frac{
\mathbf t_i^T(\mathbf q)
\left[
v_x^*\mathbf e_x
+
\omega_z^*(\mathbf e_z\times\mathbf p_i(\mathbf q))
+
\mathbf J_i(\mathbf q)\dot{\mathbf q}^{cmd}
\right]
}{r}
$$

这里的 $\Omega_i^{ref}$ 不是 Isaac 速度控制器目标，而是后续计算车轮力矩时使用的内部参考。关键约束是：轮速分配器不能重新估计另一套球铰速度，必须使用轨迹生成器最终输出的 $\dot{\mathbf q}^{cmd}$。

### 4.8 实际纵向滑移和侧滑角

实际轮心速度由仿真刚体状态得到。沿车轮滚动方向投影：

$$
s_i^{act}
=
\mathbf v_i^{act}\cdot\mathbf t_i
$$

沿车轮侧向方向投影：

$$
v_{\perp,i}^{act}
=
\mathbf v_i^{act}\cdot\mathbf n_i
$$

当前源码中的纵向滑移定义已经统一为：

$$
\kappa_i
=
\frac{r\Omega_i^{act}-s_i^{act}}
{\max(|s_i^{act}|,\epsilon)}
$$

因此：

- 若 $r\Omega_i^{act}>s_i^{act}$，则 $\kappa_i>0$。
- 若 $r\Omega_i^{act}<s_i^{act}$，则 $\kappa_i<0$。

侧滑角定义为：

$$
\alpha_i
=
\mathrm{atan2}
\left(
v_{\perp,i}^{act},
|s_i^{act}|+\epsilon
\right)
$$

当前训练日志里的 per-wheel `slip_angle` 是 signed mean，会被正负侧滑互相抵消。严格判断每个轮子的侧滑大小时，应优先看全局 abs 均值；若要逐轮严格判断，需要新增 per-wheel abs 侧滑日志。

### 4.9 接触感知轮级牵引分配

当前每个轮子的基础轮速跟踪力矩为：

$$
\tau_i^0
=
K_\Omega(\Omega_i^{ref}-\Omega_i^{act})
$$

旧版纵滑反馈后的力矩为：

$$
\tau_i^1
=
\tau_i^0
-
K_\kappa\kappa_i
$$

当前：

$$
K_\kappa=1.5
$$

最终车轮力矩为：

$$
\tau_i^{cmd}
=
\mathrm{clip}
\left(
w_i\tau_i^1,
-\tau_{max},
\tau_{max}
\right)
$$

展开后：

$$
\tau_i^{cmd}
=
\mathrm{clip}
\left(
w_i
\left[
K_\Omega(\Omega_i^{ref}-\Omega_i^{act})
-
K_\kappa\kappa_i
\right],
-\tau_{max},
\tau_{max}
\right)
$$

当前恢复为旧公式后，实际侧滑角 $\alpha_i$ 只作为诊断量记录，不再直接削弱车轮力矩。

## 5. 本轮训练数据代入

以下数据来自本轮 run 后 25 个 TensorBoard 记录点的平均值。注意：这组训练数据来自本次球铰 `q_cmd/qdot_cmd` 联合跟踪链路之前，但其车轮力矩公式与当前恢复后的旧版纵滑反馈控制器一致，可作为旧版力矩公式的历史参考。当前代码已保留新诊断字段，下一轮回放或训练仍需重新验证。

### 5.1 后段整体表现

| 指标 | 后 25 记录点均值 | 说明 |
|---|---:|---|
| 纵向滑移 abs mean | `3.066` | 明显高于低滑移阈值 `1.0` |
| 侧滑角 abs mean | `0.709 rad` | 高于目标约 `0.5 rad`，也高于当前评价阈值 `0.35 rad` |
| low-slip combined pass | `0.020` | 只有约 2% 环境同时满足低纵滑和低侧滑 |
| progress gate combined | `0.0279` | gate 已经接近低值 |
| progress multiplier | `0.139` | 接近下限 `0.10` |
| wheel speed reference abs mean | `6.752 rad/s` | 轮速参考均值 |
| wheel joint vel abs mean | `9.349 rad/s` | 实际轮速明显大于参考 |
| torque target abs mean | `3.066 Nm` | 下发力矩均值不大，但方向需要核查 |
| contact weight mean | `0.342` | 说明平均每轮按约 34% 权重参与牵引分配 |
| pitch_deg | `-2.950 deg` | 中车存在平均前俯趋势 |

### 5.2 历史数据按当前 signed 纵滑定义复算

以下训练数据来自 `stage0_lowslip_gate_v2_min_lowlevel_522iter` 诊断表。该 run 的日志使用过旧 signed 纵滑方向，因此旧日志中“车轮圆周速度大于实际纵向速度”的值为负。按当前定义重新解释时，符号需要翻转为正。

以前左轮为例，后段均值为：

$$
\Omega^{act}=9.311,\qquad
\Omega^{ref}=6.490,\qquad
C_w=0.351
$$

当前 signed 纵滑为：

$$
\kappa=+2.869
$$

基础轮速跟踪力矩为：

$$
\tau^0
=
2.0(6.490-9.311)
=
-5.642\ \mathrm{Nm}
$$

纵滑反馈项为：

$$
-K_\kappa\kappa
=
-1.5\times2.869
=
-4.304\ \mathrm{Nm}
$$

乘接触权重前：

$$
\tau^1
=
-5.642-4.304
=
-9.945\ \mathrm{Nm}
$$

最终下发力矩近似为：

$$
\tau
\approx
\mathrm{clip}(0.351\times -9.945,-15,15)
=
-3.491\ \mathrm{Nm}
$$

这说明当前符号下，前左轮同时满足两个条件：

- 实际角速度大于参考角速度，$\Omega^{act}>\Omega^{ref}$，速度跟踪项为负；
- 车轮圆周速度大于实际纵向速度，$\kappa>0$，纵滑反馈项也为负。

两项方向一致，都会降低车轮正向角速度，因此方向上符合抑制正向滑转的目标。

同一组数据代入三个代表车轮如下：

| 轮子 | $\Omega^{act}$ | $\Omega^{ref}$ | 当前 $\kappa$ | $\tau^0$ | $-K_\kappa\kappa$ | $\tau^1$ | $C_w$ | $\tau^{cmd}$ 近似 | 方向判断 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 前左 | `9.311` | `6.490` | `+2.869` | `-5.642` | `-4.304` | `-9.945` | `0.351` | `-3.491` | 制动，正确抑制正向滑转 |
| 中左 | `8.721` | `6.524` | `+2.657` | `-4.394` | `-3.986` | `-8.380` | `0.311` | `-2.606` | 制动，正确抑制正向滑转 |
| 后右 | `9.755` | `6.966` | `+3.062` | `-5.578` | `-4.593` | `-10.171` | `0.411` | `-4.180` | 制动，正确抑制正向滑转 |

因此当前公式的符号逻辑已经正确：当轮子转得过快并产生正向滑转时，$-K_\kappa\kappa$ 不再给正向附加力矩，而是给负向制动力矩。

当前 `K_\Omega=2.0`、`K_\kappa=1.5` 后，纵滑反馈项绝对值约 `4.0-4.6 Nm`，与速度跟踪项约 `4.4-5.6 Nm` 同量级，不再像 `K_\kappa=8.0` 时那样远大于速度跟踪项。这一组参数的目标是保留高正向滑转时的制动趋势，同时避免低速起步时反馈把轮子直接压死。

### 5.3 球铰 planner 到 Isaac PD 的数字例子

以下用单个球铰举例，参数采用当前 Stage0 配置：

$$
K_q=8,\qquad
\Delta t_c=\frac{1}{60}\ \mathrm{s},\qquad
\dot q_{max}=1.5\ \mathrm{rad/s},\qquad
\ddot q_{max}=12.0\ \mathrm{rad/s^2}
$$

$$
K_p^{sim}=1000,\qquad
K_d^{sim}=10,\qquad
\tau_{q,\max}^{sim}=20\ \mathrm{Nm}
$$

因此单个控制步速度变化量最多为：

$$
\Delta \dot q_{max}
=
\ddot q_{max}\Delta t_c
=
12\times\frac{1}{60}
=
0.2\ \mathrm{rad/s}
$$

#### 例子 A：目标较远时先被加速度限幅，而不是一步跳到目标

假设某个球铰内部参考和策略目标为：

$$
q^{ref}=0.100\ \mathrm{rad},\qquad
q^d=0.400\ \mathrm{rad},\qquad
\dot q^{cmd}_{prev}=0
$$

第一步，计算原始速度命令：

$$
\dot q^{raw}
=
K_q(q^d-q^{ref})
=
8(0.400-0.100)
=
2.400\ \mathrm{rad/s}
$$

第二步，按 $\dot q_{max}=1.5$ 限幅：

$$
\dot q^{sat}
=
\mathrm{clip}(2.400,-1.5,1.5)
=
1.500\ \mathrm{rad/s}
$$

第三步，按加速度限制更新速度命令：

$$
\Delta \dot q
=
\mathrm{clip}(1.500-0,-0.2,0.2)
=
0.200\ \mathrm{rad/s}
$$

$$
\dot q^{cmd}
=
0+0.200
=
0.200\ \mathrm{rad/s}
$$

第四步，积分得到位置目标：

$$
q^{cmd}
=
q^{ref}+\Delta t_c\dot q^{cmd}
=
0.100+\frac{1}{60}\times0.200
=
0.1033\ \mathrm{rad}
$$

第五步，Isaac/PhysX PD drive 收到的是：

$$
q^{des,sim}=0.1033,\qquad
\dot q^{des,sim}=0.200
$$

如果实际球铰此刻为：

$$
q=0.100\ \mathrm{rad},\qquad
\dot q=0.000\ \mathrm{rad/s}
$$

则近似 PD 力矩为：

$$
\tau^{pd}
=
1000(0.1033-0.100)
+
10(0.200-0.000)
=
3.3+2.0
=
5.3\ \mathrm{Nm}
$$

未触发 `20 Nm` effort limit：

$$
\tau^{applied}
\approx
\mathrm{clip}(5.3,-20,20)
=
5.3\ \mathrm{Nm}
$$

这个例子说明：新的轨迹生成器不会让位置目标一步跳到 `0.4 rad`，也不会让速度目标一步跳到 `1.5 rad/s`。第一步只给 `0.2 rad/s` 的速度目标和 `0.1033 rad` 的位置目标。

#### 例子 B：连续几个控制步的速度上升

如果目标仍然足够远，并且没有触发关节限位或跟踪误差保护，则速度命令会按每步 `0.2 rad/s` 上升：

```text
0.0 -> 0.2 -> 0.4 -> 0.6 -> 0.8 -> 1.0 -> 1.2 -> 1.4 -> 1.5
```

前两步位置目标可写成：

$$
q^{cmd}_1
=
0.100+\frac{1}{60}\times0.200
=
0.1033\ \mathrm{rad}
$$

$$
q^{cmd}_2
=
0.1033+\frac{1}{60}\times0.400
=
0.1100\ \mathrm{rad}
$$

也就是说，虽然最终目标是 `0.4 rad`，轨迹参考会在约 `0.2-0.4 s` 内平滑逼近，而不是一控制步到位。

#### 例子 C：实际球铰已经向目标方向运动时，速度目标会减少反向阻尼

仍使用例子 A 的第一步结果：

$$
q^{cmd}=0.1033,\qquad
\dot q^{cmd}=0.200
$$

假设实际球铰状态为：

$$
q=0.100\ \mathrm{rad},\qquad
\dot q=0.500\ \mathrm{rad/s}
$$

则 PD 力矩为：

$$
\tau^{pd}
=
1000(0.1033-0.100)
+
10(0.200-0.500)
=
3.3-3.0
=
0.3\ \mathrm{Nm}
$$

旧链路没有下发速度目标时，这一项会变成 $10(0-0.500)=-5.0 Nm$。新链路显式下发 $\dot q^{cmd}=0.2 rad/s$ 后，阻尼项不再一律把速度目标当成 0，而是围绕轨迹生成器的速度目标做跟踪。

#### 例子 D：触及球铰边界时必须回算真正生效的速度

假设：

$$
q^{ref}=0.595\ \mathrm{rad},\qquad
q_{max}=0.600\ \mathrm{rad},\qquad
\dot q^{cmd}=1.500\ \mathrm{rad/s}
$$

直接积分会得到：

$$
q^{ref}+\Delta t_c\dot q^{cmd}
=
0.595+\frac{1}{60}\times1.500
=
0.620\ \mathrm{rad}
$$

但上限是 `0.600 rad`，因此：

$$
q^{cmd}=0.600\ \mathrm{rad}
$$

此时必须重新计算真实生效的速度命令：

$$
\dot q^{cmd}
=
\frac{q^{cmd}-q^{ref}}{\Delta t_c}
=
\frac{0.600-0.595}{1/60}
=
0.300\ \mathrm{rad/s}
$$

如果不做这一步，轮速分配器会继续以为球铰正在按 `1.5 rad/s` 运动，但真实位置目标已经被边界挡住。这会导致球铰执行层和轮速分配层脱节。

#### 例子 E：参考轨迹不能长期领先真实球铰

假设内部参考因为之前的积分已经到：

$$
q^{ref}=0.350\ \mathrm{rad}
$$

但真实球铰因为接触耦合或力矩不足只到：

$$
q=0.200\ \mathrm{rad}
$$

若 $e_{track,\max}=0.10 rad$，保护后参考只能领先真实状态 `0.10 rad`：

$$
q^{ref}
\leftarrow
0.200+\mathrm{clip}(0.350-0.200,-0.10,0.10)
=
0.300\ \mathrm{rad}
$$

这一步防止 planner 在实际球铰跟不上时继续向前积分，避免 `q_ref`、`q_cmd`、实际 `q` 三者长期脱节。

#### 例子 F：较大误差时仍可能触发 effort limit

如果某一时刻实际状态明显落后参考：

$$
q^{cmd}=0.300\ \mathrm{rad},\qquad
q=0.270\ \mathrm{rad},\qquad
\dot q^{cmd}=1.500\ \mathrm{rad/s},\qquad
\dot q=0.000\ \mathrm{rad/s}
$$

则：

$$
\tau^{pd}
=
1000(0.300-0.270)
+
10(1.500-0)
=
30+15
=
45\ \mathrm{Nm}
$$

最终仍会被 `20 Nm` effort limit 截断：

$$
\tau^{applied}
\approx
\mathrm{clip}(45,-20,20)
=
20\ \mathrm{Nm}
$$

因此新链路不是“完全不会饱和”，而是把原来高刚度、高阻尼导致的一步冲击显著降低，并让速度目标、位置目标、轮速分配使用同一套轨迹。

### 5.4 球铰执行链路的可审查结论

当前球铰链路应理解为两层：

第一层是项目自己的离散轨迹生成器：

$$
q^d
\rightarrow
\dot q^{raw}
\rightarrow
\dot q^{sat}
\rightarrow
\dot q^{cmd}
\rightarrow
q^{cmd}
$$

第二层是 Isaac/PhysX 的隐式 PD drive：

$$
q^{cmd}
\ ,\ 
\dot q^{cmd}
\rightarrow
\tau^{pd}
\rightarrow
\tau^{applied}
\rightarrow
q,\dot q
$$

二者不是同一个控制器。旧链路中曾经存在的关键问题是：

$$
\dot q^{cmd}
\ne
\dot q^{des,sim}
$$

当前实际情况已经改为：

$$
\dot q^{des,sim}
=
\dot q^{cmd}
$$

所以球铰轨迹生成器的速度限幅 `1.5 rad/s` 和加速度限幅 `12.0 rad/s^2` 同时约束 `q_cmd` 的积分速度和 Isaac 的速度目标。Isaac damping 项不再默认追踪 0 速度，而是追踪 $\dot q^{cmd}$。由于 $\tau_{q,\max}^{sim}=20 Nm$ 仍然存在，球铰实际执行仍可能在误差较大时饱和，但控制链路已经从“限力矩位置伺服”改为“限力矩位置-速度联合跟踪”。

## 6. 严格检查项

### 6.1 接触权重公式本身是清楚的

接触权重使用的是无量纲归一化接触力 $c_i=\|\mathbf F_i\|/W$。本轮后段 `contact_weight mean≈0.342`，说明控制器认为六轮平均接触可靠性中等。

这部分没有发现公式和实现不一致的问题。

### 6.2 车轮不是速度控制，而是“轮速参考参与力矩计算”

当前控制链路中：

$$
\Omega^{ref}\rightarrow \tau^{cmd}\rightarrow \mathrm{set\_joint\_effort\_target}
$$

不是：

$$
\Omega^{ref}\rightarrow \mathrm{set\_joint\_velocity\_target}
$$

因此“速度跟踪”这个说法只表示力矩公式中存在 $K_\Omega(\Omega^{ref}-\Omega^{act})$ 这一项，不表示 Isaac 在做速度闭环。

这部分没有发现实现口径错误。

### 6.3 旧纵滑反馈符号风险已由 signed 纵滑方向修正

旧源码约定下曾出现：

$$
\kappa_i<0
\quad\Longleftrightarrow\quad
r\Omega_i^{act}>s_i^{act}
$$

这会导致高正向滑转时 $-K_\kappa\kappa_i>0$，从而给出正向附加力矩，方向不符合抑制正向滑转的目标。

当前源码已改为：

$$
\kappa_i
=
\frac{r\Omega_i^{act}-s_i^{act}}{\max(|s_i^{act}|,\epsilon)}
$$

因此当 $r\Omega_i^{act}>s_i^{act}$ 时：

$$
\kappa_i>0
\qquad\Rightarrow\qquad
-K_\kappa\kappa_i<0
$$

本轮代表数据按当前参数复算后，纵滑反馈项约为 `-4.0` 到 `-4.6 Nm`，速度跟踪项约为 `-4.4` 到 `-5.6 Nm`，二者同向制动。因此当前代码中的力矩输出方向已经与“抑制正向滑转”一致，且反馈强度已从原先过强状态降到与轮速跟踪项同量级。

后续仍建议做单轮正/负力矩符号测试，用于确认 actuator 关节轴方向、`wheel_joint_vel` 正方向和力矩正方向是否一致；但从公式和日志量纲代入看，当前 signed 纵滑方向已经不再是反号。

### 6.4 当前侧滑处理只保留名义整形和奖励/评价约束

低侧滑整形优化的是：

$$
\sum_i w_i(v_{lat,i}^{nom})^2
$$

这里的 $v_{lat,i}^{nom}$ 是运动学模型根据 $\mathbf u^*$、$\mathbf q$、$\dot{\mathbf q}^{cmd}$ 推出来的名义侧向速度。

实际侧滑角 $\alpha_i$ 来自仿真中的真实轮心速度：

$$
\alpha_i=\mathrm{atan2}(v_{lat,i}^{act}, |v_{x,i}^{act}|+\epsilon)
$$

当前恢复旧版力矩控制器后，实际侧滑角 $\alpha_i$ 不再直接进入车轮力矩衰减。因此现在侧滑主要有两层影响：

- 平面命令整形层：通过加权最小二乘压低名义侧向速度 $v_{lat,i}^{nom}$。
- 奖励和评价层：`slip_penalty`、low-slip progress gate 和 low-slip pass rate 使用侧滑角约束行为。

这仍不是直接让侧滑角闭环跟踪 0。实际侧滑能否下降，需要看整形后的平面命令、球铰构型、接触载荷和策略奖励共同作用。

### 6.5 当前 per-wheel 侧滑日志不能严格说明每个轮子的绝对侧滑大小

逐轮表里的 `slip_angle signed rad` 很小，例如前左 `-0.033 rad`。这不能说明前左轮实际侧滑很小，因为该指标是 signed mean，正负侧滑可能在环境和时间维度上抵消。

全局 `Observation/wheel_slip_angle_abs_mean_raw≈0.709 rad` 才说明整体侧滑仍然偏大。

若要逐轮严格核查侧滑，需要新增逐轮：

- `slip_angle_abs`
- `longitudinal_slip_abs`
- `rolling_speed_actual`
- `lateral_speed_actual`
- `wheel_circumferential_speed = r * wheel_joint_vel`
- `torque_tracking_term`
- `longitudinal_slip_decay`
- `slip_angle_decay`
- `torque_after_longitudinal_gate`
- `torque_raw_before_clip`

这些量可以直接验证公式每一步的符号和数值。

## 7. 当前最小核验建议

在继续正式训练前，建议做一个最小符号核验：

1. 固定单个车轮或低速直线状态，给该轮一个正的 `wheel_torque_target`。
2. 观察该轮 `wheel_joint_vel` 是否向正方向增加。
3. 如果正力矩使正向轮速增加，则当前 $-K_\kappa\kappa$ 项的符号判断与关节正方向一致。
4. 如果正力矩实际使该轮制动，则必须检查车轮关节轴符号，否则 `wheel_joint_vel`、`wheel_speed_reference` 和力矩符号可能整体需要重排。

这个测试仍然有价值；当前已经恢复 $-K_\kappa\kappa$ 附加力矩项，因此该测试可以进一步验证公式符号与 Isaac 关节轴方向是否一致。

## 8. 可审查结论

当前接触感知轮级牵引分配可以概括为：

$$
\tau_i^0
=
K_\Omega(\Omega_i^{ref}-\Omega_i^{act})
$$

$$
\tau_i^1
=
\tau_i^0-K_\kappa\kappa_i
$$

$$
\tau_i^{cmd}
=
\mathrm{clip}
\left(
w_i\tau_i^1,
-\tau_{max},
\tau_{max}
\right)
$$

其中：

$$
\Omega_i^{ref}
=
\frac{
\mathbf t_i^T
\left[
v_x^*\mathbf e_x
+\omega_z^*(\mathbf e_z\times\mathbf p_i)
+\mathbf J_i(\mathbf q)\dot{\mathbf q}^{cmd}
\right]
}{r}
$$

$$
w_i
=
\mathrm{clip}
\left(
\frac{\|\mathbf F_i\|/W-c_{off}}{c_{on}-c_{off}},
0,
1
\right)
$$

本次代码改动后：

- 纵滑正号表示车轮圆周速度大于实际滚动速度。
- 当前旧版结构中的 $-K_\kappa\kappa_i$ 项会在正向滑转时提供负向制动力矩贡献。
- `g_kappa` 和 `g_alpha` 只作为兼容诊断字段保留，当前固定为 `1.0`。
- 接触越弱，最终力矩按 $w_i$ 衰减。
