# Stage1奖励函数设计草案

本文档记录 `CompleteCar-Stage1` 当前源码实际生效的奖励函数，以及后续拟采用的地形自适应奖励函数数学形式。

说明：

- 第 `2` 节记录当前源码实际 reward。
- 第 `3` 节之后记录后续拟采用 reward 草案。
- 草案部分目前不代表当前源码已生效。

设计目标：

- 只使用当前局部高程图 `terrain_height_patch`，不引入双目相机或 LiDAR 原始传感器输入。
- 奖励策略学会稳定沿地形列前进，并通过坡地、粗糙地形、台阶和离散障碍。
- 不使用球铰极限惩罚。
- 暂时不加入非轮体碰撞惩罚。
- 参考 MGDP 的动作变化惩罚思想，加入动作变化与动作软限幅惩罚。

## 1. 符号定义

单个并行环境在第 $t$ 个控制步的 policy 动作为：

$$
\mathbf a_t =
\left[
a_{v,t},\ a_{\omega,t},\
a_{q1,t},\ a_{q2,t},\ a_{q3,t},\
a_{q4,t},\ a_{q5,t},\ a_{q6,t}
\right] \in [-1,1]^8
$$

其中 $a_{v,t}$ 表示前进速度归一化动作，$a_{\omega,t}$ 表示 yaw rate 归一化动作，$a_{q1,t}$ 到 $a_{q6,t}$ 表示两组等效球铰姿态归一化动作。

沿地形列正方向的位移增量定义为：

$$
\Delta s_t =
\operatorname{clip}
\left(
x_t - x_{t-1},
-\Delta s_{\max},
\Delta s_{\max}
\right)
$$

其中 $x_t$ 为车辆 root 在世界坐标系下的前进方向坐标。当前 Stage1 reset 朝向固定为 $+x$，地形列目标也沿 $+x$ 推进，因此可直接使用世界 $x$ 方向。

正向和反向位移分别为：

$$
\Delta s_t^+ = \max(\Delta s_t, 0)
$$

$$
\Delta s_t^- = \max(-\Delta s_t, 0)
$$

第 $i$ 个车轮的接触权重定义为：

$$
c_{i,t} =
\sigma
\left(
\frac{n_{i,t} - n_{\mathrm{on}}}{\sigma_n}
\right)
$$

其中 $n_{i,t}$ 为第 $i$ 个车轮的法向接触力按整车重量归一化后的值，$\sigma(\cdot)$ 为 sigmoid 函数。

当前源码目标相关符号：

$$
D_t = \|\mathbf g_{xy,t}\|_2
$$

其中 $D_t$ 为当前相对目标平面距离，$\mathbf g_{xy,t}$ 为相对目标命令的平面位置分量。

目标朝向误差为：

$$
\psi_t = \operatorname{wrap}(\mathbf g_{\psi,t})
$$

最大 episode 步数为：

$$
N = 2400
$$

当前 episode 已运行步数为 $l_t$。

## 2. 当前 Stage1 源码实际奖励

当前 `rewards.py` 仍使用与 Stage0 共享的目标导向 reward 主干。Stage1 会计算以下 reward 分量：

1. `distance_to_target`
2. `progress_to_target`
3. `reached_target`
4. `far_from_target`
5. `angle_diff`
6. `slip_penalty`
7. `action_rate_penalty`
8. `contact_support_penalty`
9. `edge_speed_penalty`

`turn_speed_penalty` 已从当前源码中删除；`reached_target` 已启用，参数与 Stage0 相同。`action_rate_penalty` 已按 episode 最大步数归一化后接入 Stage1。`slip_penalty` 当前使用底层接触权重 mask，`contact_support_penalty` 已作为独立模块支撑惩罚接入 Stage1，`edge_speed_penalty` 已按前方局部高程突变强度接入 Stage1。

当前总 reward 可写为：

$$
r_t^{\mathrm{cur}}
=
w_D R_{D,t}
+
w_p R_{p,t}
+
w_{\mathrm{hit}} R_{\mathrm{hit},t}
-
w_{\mathrm{far}} P_{\mathrm{far},t}
+
w_{\psi} R_{\psi,t}
-
w_{\mathrm{slip}}^{\mathrm{cur}} P_{\mathrm{slip},t}^{\mathrm{cur}}
-
w_{\Delta a}^{\mathrm{cur}} P_{\Delta a,t}^{\mathrm{cur}}
-
w_{\mathrm{contact}}^{\mathrm{cur}} P_{\mathrm{contact},t}^{\mathrm{cur}}
-
w_{\mathrm{edge}}^{\mathrm{cur}} P_{\mathrm{edge},t}^{\mathrm{cur}}
$$

当前权重为：

| 项 | 符号 | 当前值 |
|---|---|---:|
| 距离奖励 | $w_D$ | $6.0$ |
| progress 奖励 | $w_p$ | $8.0$ |
| 目标命中奖励 | $w_{\mathrm{hit}}$ | $6.0$ |
| 远离目标惩罚 | $w_{\mathrm{far}}$ | $2.0$ |
| 朝向奖励 | $w_{\psi}$ | $6.0$ |
| 滑移惩罚 | $w_{\mathrm{slip}}^{\mathrm{cur}}$ | $2.0$ |
| 动作变化惩罚 | $w_{\Delta a}^{\mathrm{cur}}$ | $10.0$ |
| 模块支撑惩罚 | $w_{\mathrm{contact}}^{\mathrm{cur}}$ | $4.0$ |
| 地形突变前速度惩罚 | $w_{\mathrm{edge}}^{\mathrm{cur}}$ | $6.0$ |

### 2.1 距离奖励

$$
R_{D,t}
=
\frac{1}{1+k_D D_t^2}
\frac{1}{N}
$$

其中：

$$
k_D = 0.01
$$

因此：

$$
r_{D,t}
=
6.0
\frac{1}{1+0.01D_t^2}
\frac{1}{N}
$$

### 2.2 progress 奖励

目标距离变化量为：

$$
\Delta D_t
=
\operatorname{clip}
\left(
D_{t-1}-D_t,
-\Delta D_{\max},
\Delta D_{\max}
\right)
$$

其中：

$$
\Delta D_{\max} = 0.25\ \mathrm{m}
$$

当车辆接近目标时，当前源码会放松负 progress：

$$
D_t \le D_{\mathrm{relax}}
\Rightarrow
\Delta D_t \leftarrow \max(\Delta D_t,0)
$$

其中：

$$
D_{\mathrm{relax}} = 4.0\ \mathrm{m}
$$

正向和负向 progress 分别为：

$$
p_t^+
=
\frac{\max(\Delta D_t,0)}{d_{\mathrm{nom}}}
$$

$$
p_t^-
=
\frac{\min(\Delta D_t,0)}{d_{\mathrm{nom}}}
$$

其中：

$$
d_{\mathrm{nom}} = 8.0\ \mathrm{m}
$$

纵滑 gate 为：

$$
G_{\kappa,t}
=
\exp
\left[
-
\frac{1}{2}
\sum_{i=1}^{6}
\left(
\frac{\kappa_{i,t}}{k_{\kappa}}
\right)^2
\right]
$$

其中：

$$
k_{\kappa} = 3.0
$$

侧滑角 gate 为：

$$
G_{\alpha,t}
=
\prod_{i=1}^{6}
\left[
0.5
\cos
\left(
\operatorname{clip}
\left(
\frac{\pi|\alpha_{i,t}|}{k_{\alpha}},
0,
\pi
\right)
\right)
+
0.5
\right]
$$

其中：

$$
k_{\alpha} = 1.5\ \mathrm{rad}
$$

当前 progress gate 使用二者平均值：

$$
G_{p,t}
=
0.5
\left(
G_{\kappa,t}
+
G_{\alpha,t}
\right)
$$

progress multiplier 为：

$$
m_t
=
m_{\min}
+
(m_{\max}-m_{\min})G_{p,t}
$$

其中：

$$
m_{\min}=0.25,\qquad m_{\max}=1.5
$$

progress 奖励为：

$$
R_{p,t}
=
m_t p_t^+
+
p_t^-
$$

因此：

$$
r_{p,t}
=
8.0
\left(
m_t p_t^+
+
p_t^-
\right)
$$

### 2.3 目标命中奖励

目标命中指示量为：

$$
I_{\mathrm{hit},t}
=
\mathbb I(D_t < D_{\mathrm{tol}})
$$

其中：

$$
D_{\mathrm{tol}} = 0.5\ \mathrm{m}
$$

目标命中奖励的未加权形式为：

$$
R_{\mathrm{hit},t}
=
I_{\mathrm{hit},t}
r_{\mathrm{hit,base}}
\frac{N-l_t}{N}
$$

其中：

$$
r_{\mathrm{hit,base}} = 2.0
$$

当前 Stage1：

$$
w_{\mathrm{hit}} = 6.0
$$

所以：

$$
r_{\mathrm{hit},t}
=
6.0
I_{\mathrm{hit},t}
2.0
\frac{N-l_t}{N}
$$

### 2.4 远离目标惩罚

far-from-target 阈值为：

$$
D_{\mathrm{far}}
=
d_{\mathrm{nom}} + d_{\mathrm{far,margin}}
=
8.0 + 3.0
=
11.0\ \mathrm{m}
$$

远离目标惩罚指示量为：

$$
P_{\mathrm{far},t}
=
\mathbb I(D_t>D_{\mathrm{far}})
$$

因此：

$$
r_{\mathrm{far},t}
=
-2.0P_{\mathrm{far},t}
$$

### 2.5 朝向奖励

$$
R_{\psi,t}
=
\frac{1}{1+|\psi_t|}
\frac{1}{N}
$$

因此：

$$
r_{\psi,t}
=
6.0
\frac{1}{1+|\psi_t|}
\frac{1}{N}
$$

### 2.6 滑移惩罚

当前滑移惩罚复用底层力矩分配中的车轮接触权重：

$$
c_{i,t}
=
\operatorname{clip}
\left(
\frac{n_{i,t}-0.01}{0.08-0.01},
0,
1
\right)
$$

其中 $n_{i,t}$ 为第 $i$ 个车轮的接触力模长按整车重量归一化后的值。

滑移惩罚只对有效接触轮起主要作用：

$$
S_{c,t}
=
\max
\left(
\sum_{i=1}^{6}c_{i,t},
1.0
\right)
$$

$$
P_{\mathrm{slip},t}^{\mathrm{cur}}
=
\frac{
\lambda_{\kappa}^{\mathrm{cur}}
\frac{\sum_{i=1}^{6}c_{i,t}|\kappa_{i,t}|}{S_{c,t}}
+
\lambda_{\alpha}^{\mathrm{cur}}
\frac{\sum_{i=1}^{6}c_{i,t}|\alpha_{i,t}|}{S_{c,t}}
}{N}
$$

其中 $S_{c,t}$ 是有效接触权重和的保护分母。这样离地轮不会贡献滑移惩罚；当只有少数轮有效接地时，仍然评价这些接地轮自身的滑移，而不是因为除以固定 `6` 把惩罚压得过低。

其中：

$$
\lambda_{\kappa}^{\mathrm{cur}} = 5.0,\qquad
\lambda_{\alpha}^{\mathrm{cur}} = 1.0
$$

因此：

$$
r_{\mathrm{slip},t}
=
-2.0
\frac{
5.0\frac{\sum_{i=1}^{6}c_{i,t}|\kappa_{i,t}|}{S_{c,t}}
+
1.0\frac{\sum_{i=1}^{6}c_{i,t}|\alpha_{i,t}|}{S_{c,t}}
}{N}
$$

### 2.8 动作变化惩罚

当前 Stage1 动作变化惩罚采用 8 维 policy action 的加权均方变化，并用最大 episode 步数 $N$ 归一化：

$$
P_{\Delta a,t}^{\mathrm{cur}}
=
\frac{
\frac{1}{8}
\sum_{j=1}^{8}
\rho_j
(a_{j,t}-a_{j,t-1})^2
}{N}
$$

其中：

$$
\rho =
\left[
0.5,\ 0.5,\ 1.0,\ 1.0,\ 1.0,\ 1.0,\ 1.0,\ 1.0
\right]
$$

因此：

$$
r_{\Delta a,t}
=
-10.0
P_{\Delta a,t}^{\mathrm{cur}}
$$

前两个动作为底盘前进速度和 yaw rate，权重为 $0.5$；后六个球铰姿态动作为 $1.0$。

### 2.9 模块支撑惩罚

当前源码用前、中、后三个模块中每个模块左右轮的最大接触权重表示该模块是否至少有一侧支撑：

$$
C_{\mathrm{front},t}
=
\max(c_{2,t},c_{3,t})
$$

$$
C_{\mathrm{mid},t}
=
\max(c_{0,t},c_{1,t})
$$

$$
C_{\mathrm{rear},t}
=
\max(c_{4,t},c_{5,t})
$$

其中 `0,1` 为中车左右轮，`2,3` 为前车左右轮，`4,5` 为后车左右轮。接触最低要求为：

$$
c_{\min}=0.3
$$

每个模块的支撑缺口为：

$$
d_{m,t}
=
\operatorname{clip}
\left(
\frac{c_{\min}-C_{m,t}}{c_{\min}},
0,
1
\right)
$$

模块支撑惩罚为：

$$
P_{\mathrm{contact},t}^{\mathrm{cur}}
=
\frac{1}{3}
\left(
d_{\mathrm{front},t}^2
+ d_{\mathrm{mid},t}^2
+ d_{\mathrm{rear},t}^2
\right)
\frac{1}{N}
$$

因此：

$$
r_{\mathrm{contact},t}
=
-4.0
P_{\mathrm{contact},t}^{\mathrm{cur}}
$$

该项不要求六轮同时接地，只要求前、中、后三段车体不要长期完全失去支撑。

### 2.10 地形突变前速度惩罚

当前源码使用局部高程图中车头前方的预览区域计算地形突变强度。Stage1 当前 height patch 已配置为：车体前端外再看 `1.0 m`，车体左右两侧各保留 `0.5 m` 预览空间。

设预览区域内相邻采样点的最大高度跳变为：

$$
E_{\mathrm{raw},t}
=
\max
\left(
|\Delta_x H_t|,
|\Delta_y H_t|
\right)
$$

其中 $H_t$ 表示局部高程图对应的地形高度。源码中 height patch 存储的是 `root_z - terrain_height`，但相邻差值取绝对值后与真实地形高度差等价。

结合 Stage1 当前地形生成函数：

- `stairs up/down` 的单级台阶高度约为 `0.05-0.22 m`；
- `discrete obstacles` 的相邻高度跳变从约 `0.10 m` 起，高 row 可更大；
- `slope up` 最高 row 的相邻网格高度差约为 `0.04 m`。

因此当前 edge strength 采用：

$$
E_t
=
\operatorname{clip}
\left(
\frac{E_{\mathrm{raw},t}-0.04}{0.10-0.04},
0,
1
\right)
$$

安全速度按 edge strength 从平地速度上限过渡到突变前速度上限：

$$
v_{\mathrm{safe},t}
=
2.0
-
E_t
\left(
2.0 - 0.5
\right)
$$

其中 $E_t=0$ 时 $v_{\mathrm{safe},t}=2.0\ \mathrm{m/s}$，等于 Stage1 当前底盘前进速度上限，因此平地不额外限速；$E_t=1$ 时 $v_{\mathrm{safe},t}=0.5\ \mathrm{m/s}$。

只惩罚正向超速：

$$
v_t^+
=
\max(v_{x,t},0)
$$

$$
e_{v,t}
=
\max
\left(
v_t^+ - v_{\mathrm{safe},t},
0
\right)
$$

$$
P_{\mathrm{edge},t}^{\mathrm{cur}}
=
E_t
\left(
\frac{e_{v,t}}{2.0}
\right)^2
\frac{1}{N}
$$

因此：

$$
r_{\mathrm{edge},t}
=
-6.0
P_{\mathrm{edge},t}^{\mathrm{cur}}
$$

### 2.11 当前 reward 的局限

当前 reward 已加入目标导向、滑移门控 progress、动作变化惩罚、模块支撑惩罚和地形突变前速度惩罚。它仍然没有显式奖励：

- 真实 row advance 事件；
- 悬空空转抑制；
- 相对局部地形姿态稳定；
- 动作软限幅。

因此在坡地高 row、rough seam、stairs up/down 和 discrete obstacles 中，策略可能学到“朝目标冲过去”，但没有足够奖励压力去形成提前调姿和稳定接触。

## 3. 拟采用奖励总形式

后续拟采用的 Stage1 总奖励定义为：

$$
\begin{aligned}
r_t ={}&
w_{\mathrm{prog}} R_{\mathrm{prog},t}
+ w_{\mathrm{row}} R_{\mathrm{row},t} \\
&- w_{\mathrm{slip}} P_{\mathrm{slip},t}
- w_{\mathrm{air}} P_{\mathrm{air},t}
- w_{\mathrm{contact}} P_{\mathrm{contact},t} \\
&- w_{\mathrm{att}} P_{\mathrm{att},t}
- w_{\mathrm{edge}} P_{\mathrm{edge},t} \\
&- w_{\Delta a} P_{\Delta a,t}
- w_{\mathrm{soft}} P_{\mathrm{soft},t}
- w_{\mathrm{fail}} P_{\mathrm{fail},t}
\end{aligned}
$$

各项含义如下：

| 项 | 含义 |
|---|---|
| $R_{\mathrm{prog},t}$ | 稳定前进奖励 |
| $R_{\mathrm{row},t}$ | 有效推进到下一 row 的事件奖励 |
| $P_{\mathrm{slip},t}$ | 接地滑移惩罚 |
| $P_{\mathrm{air},t}$ | 悬空空转惩罚 |
| $P_{\mathrm{contact},t}$ | 前、中、后三段车体支撑丢失惩罚 |
| $P_{\mathrm{att},t}$ | 车体姿态相对局部地形的失配惩罚 |
| $P_{\mathrm{edge},t}$ | 地形突变前高速冲击惩罚 |
| $P_{\Delta a,t}$ | 动作变化惩罚 |
| $P_{\mathrm{soft},t}$ | 动作软限幅惩罚 |
| $P_{\mathrm{fail},t}$ | 无 row 推进失败惩罚 |

## 4. 稳定前进奖励

前进奖励不再只奖励位移增量，而是用稳定门控调制：

$$
R_{\mathrm{prog},t}
=
\frac{\Delta s_t^+}{d_{\mathrm{nom}}}
G_{\mathrm{stable},t}
-
\lambda_{\mathrm{back}}
\frac{\Delta s_t^-}{d_{\mathrm{nom}}}
$$

稳定门控定义为：

$$
G_{\mathrm{stable},t}
=
g_{\min}
+
(1-g_{\min})
G_{\mathrm{slip},t}
G_{\mathrm{contact},t}
G_{\mathrm{att},t}
$$

其中 $g_{\min}$ 保留最小前进学习信号，避免训练早期因为门控过强导致 progress 奖励完全消失。

滑移门控：

$$
G_{\mathrm{slip},t}
=
\exp
\left(
-
\beta_{\kappa}
\overline{\kappa}_{t}^{\,2}
-
\beta_{\alpha}
\overline{\alpha}_{t}^{\,2}
\right)
$$

其中：

$$
\overline{\kappa}_{t}
=
\frac{1}{6}
\sum_{i=1}^{6}
c_{i,t}
\operatorname{clip}
\left(
\frac{|\kappa_{i,t}|}{\kappa_{\mathrm{ref}}},
0,
\kappa_{\mathrm{clip}}
\right)
$$

$$
\overline{\alpha}_{t}
=
\frac{1}{6}
\sum_{i=1}^{6}
c_{i,t}
\operatorname{clip}
\left(
\frac{|\alpha_{i,t}|}{\alpha_{\mathrm{ref}}},
0,
\alpha_{\mathrm{clip}}
\right)
$$

接触门控直接使用模块支撑得分：

$$
G_{\mathrm{contact},t} = S_{\mathrm{contact},t}
$$

姿态门控定义为：

$$
G_{\mathrm{att},t} =
\exp(-P_{\mathrm{att},t})
$$

推荐参数：

| 参数 | 推荐初始值 |
|---|---:|
| $\Delta s_{\max}$ | $0.25\ \mathrm{m}$ |
| $d_{\mathrm{nom}}$ | $8.0\ \mathrm{m}$ |
| $g_{\min}$ | $0.25$ |
| $\lambda_{\mathrm{back}}$ | $1.0$ |
| $\kappa_{\mathrm{ref}}$ | $1.0$ |
| $\alpha_{\mathrm{ref}}$ | $0.35\ \mathrm{rad}$ |
| $\kappa_{\mathrm{clip}}$ | $3.0$ |
| $\alpha_{\mathrm{clip}}$ | $3.0$ |
| $\beta_{\kappa}$ | $0.5$ |
| $\beta_{\alpha}$ | $0.5$ |

## 5. 有效 row advance 奖励

当车辆沿当前地形列真正推进到下一 row 时，给事件奖励：

$$
R_{\mathrm{row},t}
=
I_{\mathrm{advance},t}
\left(
0.5
+
0.5G_{\mathrm{stable},t}
\right)
$$

其中 $I_{\mathrm{advance},t}$ 只在 terrain-column 目标正常推进时取 $1$。如果 episode 因 far from target、球铰越界、timeout 或 reset 结束，不应把该 reset 解释为有效 row advance。

## 6. 接地滑移惩罚

接地滑移惩罚只对有接触权重的车轮起主要作用：

$$
S_{c,t}
=
\max
\left(
\sum_{i=1}^{6}c_{i,t},
1.0
\right)
$$

$$
P_{\mathrm{slip},t}
=
\frac{1}{S_{c,t}}
\sum_{i=1}^{6}
c_{i,t}
\left[
\operatorname{clip}
\left(
\frac{|\kappa_{i,t}|}{\kappa_{\mathrm{ref}}},
0,
\kappa_{\mathrm{clip}}
\right)^2
+
\lambda_{\alpha}
\operatorname{clip}
\left(
\frac{|\alpha_{i,t}|}{\alpha_{\mathrm{ref}}},
0,
\alpha_{\mathrm{clip}}
\right)^2
\right]
$$

这里同样使用 $S_{c,t}$ 作为保护分母，避免离地轮被计入滑移评价，同时避免弱接触噪声被过度放大。

推荐参数：

| 参数 | 推荐初始值 |
|---|---:|
| $n_{\mathrm{on}}$ | $0.04$ |
| $\sigma_n$ | $0.02$ |
| $\lambda_{\alpha}$ | $3.0$ |

## 7. 悬空空转惩罚

悬空空转惩罚用于抑制车轮离地后仍高速旋转：

$$
P_{\mathrm{air},t}
=
\frac{1}{6}
\sum_{i=1}^{6}
(1-c_{i,t})
\operatorname{clip}
\left(
\frac{|r\omega_{i,t}|}{v_{\mathrm{air}}},
0,
v_{\mathrm{air,clip}}
\right)^2
$$

其中 $r$ 为车轮半径，$\omega_{i,t}$ 为第 $i$ 个车轮角速度。

推荐参数：

| 参数 | 推荐初始值 |
|---|---:|
| $v_{\mathrm{air}}$ | $1.0\ \mathrm{m/s}$ |
| $v_{\mathrm{air,clip}}$ | $3.0$ |

## 8. 模块支撑丢失惩罚

三节车体的支撑状态定义为：

$$
C_{\mathrm{front},t}
=
\max(c_{\mathrm{front,left},t}, c_{\mathrm{front,right},t})
$$

$$
C_{\mathrm{mid},t}
=
\max(c_{\mathrm{mid,left},t}, c_{\mathrm{mid,right},t})
$$

$$
C_{\mathrm{rear},t}
=
\max(c_{\mathrm{rear,left},t}, c_{\mathrm{rear,right},t})
$$

模块支撑得分：

$$
S_{\mathrm{contact},t}
=
\frac{
C_{\mathrm{front},t}
+
C_{\mathrm{mid},t}
+
C_{\mathrm{rear},t}
}{3}
$$

支撑丢失惩罚：

$$
P_{\mathrm{contact},t}
=
1 - S_{\mathrm{contact},t}
$$

这项不强制六轮同时接地，只要求前、中、后三段车体尽量都有支撑。

## 9. 姿态相对地形失配惩罚

从局部高程图中选取车体 footprint 附近区域 $\Omega_{\mathrm{body}}$，拟合局部地形平面：

$$
H(x,y)
\approx
b_0 + b_x x + b_y y
$$

局部地形参考 pitch 和 roll 定义为：

$$
\theta_{\mathrm{ref},t} = \arctan(b_x)
$$

$$
\phi_{\mathrm{ref},t} = -\arctan(b_y)
$$

车辆中车体姿态为 $\theta_t$ 和 $\phi_t$，分别表示 pitch 和 roll。姿态失配惩罚定义为：

$$
P_{\mathrm{att},t}
=
\left(
\frac{\theta_t-\theta_{\mathrm{ref},t}}{\theta_{\mathrm{scale}}}
\right)^2
+
\left(
\frac{\phi_t-\phi_{\mathrm{ref},t}}{\phi_{\mathrm{scale}}}
\right)^2
+
\lambda_{\omega}
\frac{
\omega_{\mathrm{roll},t}^{2}
+
\omega_{\mathrm{pitch},t}^{2}
}{\omega_{\mathrm{scale}}^2}
$$

推荐参数：

| 参数 | 推荐初始值 |
|---|---:|
| $\Omega_{\mathrm{body}}$ | 车体 footprint 附近，不使用最前方 preview 区域 |
| $\theta_{\mathrm{scale}}$ | $15^\circ$ |
| $\phi_{\mathrm{scale}}$ | $12^\circ$ |
| $\omega_{\mathrm{scale}}$ | $2.0\ \mathrm{rad/s}$ |
| $\lambda_{\omega}$ | $0.2$ |

## 10. 地形突变前高速冲击惩罚

从高程图前方预瞄区域 $\Omega_{\mathrm{edge}}$ 中计算高度突变强度：

$$
\Omega_{\mathrm{edge}}
=
\left\{
(x,y)
\mid
x_{\mathrm{front}}
\le x
\le
x_{\mathrm{front}} + 1.0,
\ |y| \le y_{\mathrm{half}} + 0.5
\right\}
$$

其中 $x_{\mathrm{front}}$ 为车体前端相对中车参考点的位置，$y_{\mathrm{half}}$ 为半车宽。当前配置中 $x_{\mathrm{front}}=0.942209\ \mathrm{m}$、$y_{\mathrm{half}}=0.280374\ \mathrm{m}$。

相邻采样点的最大高度差为：

$$
E_{\mathrm{raw},t}
=
\max
\left(
|\Delta_x H_t|,
|\Delta_y H_t|
\right)
$$

归一化突变强度：

$$
E_t =
\operatorname{clip}
\left(
\frac{E_{\mathrm{raw},t}-h_{\mathrm{edge,low}}}
{h_{\mathrm{edge,high}}-h_{\mathrm{edge,low}}},
0,
1
\right)
$$

根据地形突变强度定义安全前进速度：

$$
v_{\mathrm{safe},t}
=
v_{\max}
-
E_t
\left(
v_{\max}-v_{\mathrm{edge}}
\right)
$$

高速冲击惩罚：

$$
P_{\mathrm{edge},t}
=
E_t
\left[
\frac{
\max(v_{x,t}^+-v_{\mathrm{safe},t},0)
}{v_{\max}}
\right]^2
\frac{1}{N}
$$

其中 $v_{x,t}^+=\max(v_{x,t},0)$，只惩罚向前冲击，不惩罚倒车。

推荐参数：

| 参数 | 推荐初始值 |
|---|---:|
| $h_{\mathrm{edge,low}}$ | $0.04\ \mathrm{m}$ |
| $h_{\mathrm{edge,high}}$ | $0.10\ \mathrm{m}$ |
| $v_{\mathrm{edge}}$ | $0.5\ \mathrm{m/s}$ |
| $v_{\max}$ | $2.0\ \mathrm{m/s}$ |

参数依据：Stage1 当前 `stairs up/down` 单级台阶高度约为 `0.05-0.22 m`，`discrete obstacles` 相邻高度跳变从约 `0.10 m` 起，而 `slope up` 最高 row 的相邻高度差约为 `0.04 m`。因此 $0.04\ \mathrm{m}$ 用于排除普通坡面，$0.10\ \mathrm{m}$ 用于把明确台阶/障碍边缘视为强突变。

## 11. 动作变化惩罚

参考 MGDP 的 action rate penalty，动作变化惩罚定义为：

$$
P_{\Delta a,t}
=
\frac{
\frac{1}{8}
\sum_{j=1}^{8}
\rho_j
(a_{j,t}-a_{j,t-1})^2
}{N}
$$

推荐动作权重：

$$
\rho =
\left[
0.5,\ 0.5,\ 1.0,\ 1.0,\ 1.0,\ 1.0,\ 1.0,\ 1.0
\right]
$$

说明：

- 底盘速度和 yaw rate 动作允许略微灵活。
- 球铰姿态动作变化更容易造成车体冲击，因此权重更高。
- 当前源码已实现该项，Stage1 初始权重取 $w_{\Delta a}=10.0$。
- 若实现时改为不用 $\frac{1}{8}$ 的求和形式，则对应权重需要约按维度缩小。

## 12. 动作软限幅惩罚

动作软限幅惩罚不检查实际球铰角度，只检查 policy 输出动作是否长期贴近 $-1$ 或 $1$：

$$
P_{\mathrm{soft},t}
=
\frac{1}{8}
\sum_{j=1}^{8}
\rho_j
\left[
\frac{
\max(|a_{j,t}|-a_{\mathrm{soft},j},0)
}{
1-a_{\mathrm{soft},j}
}
\right]^2
$$

推荐软限幅阈值：

$$
a_{\mathrm{soft}}
=
\left[
0.95,\ 0.90,\ 0.85,\ 0.85,\ 0.85,\ 0.85,\ 0.85,\ 0.85
\right]
$$

说明：

- 该项允许策略在必要时输出大动作。
- 该项只抑制长期贴边输出，不替代物理关节限位。
- 该项不等价于球铰极限惩罚。

## 13. 无 row 推进失败惩罚

如果 episode 结束时没有完成任何 row advance，则给失败惩罚：

$$
P_{\mathrm{fail},t}
=
I_{\mathrm{done},t}
I_{\mathrm{row\_advance\_count}=0}
$$

其中 $I_{\mathrm{done},t}$ 只在 episode 结束步取 $1$。

该项用于抑制在 stairs down、stairs up 和 discrete obstacles 中长时间冲撞、打滑、reset 但没有真正推进的行为。

## 14. 推荐初始权重

| 奖励/惩罚项 | 符号 | 推荐初始值 |
|---|---|---:|
| 稳定前进奖励 | $w_{\mathrm{prog}}$ | $8.0$ |
| 有效 row advance 奖励 | $w_{\mathrm{row}}$ | $1.5$ |
| 接地滑移惩罚 | $w_{\mathrm{slip}}$ | $0.03$ |
| 悬空空转惩罚 | $w_{\mathrm{air}}$ | $0.01$ |
| 模块支撑丢失惩罚 | $w_{\mathrm{contact}}$ | $0.03$ |
| 姿态相对地形失配惩罚 | $w_{\mathrm{att}}$ | $0.02$ |
| 地形突变前高速冲击惩罚 | $w_{\mathrm{edge}}$ | $6.0$ |
| 动作变化惩罚 | $w_{\Delta a}$ | $10.0$ |
| 动作软限幅惩罚 | $w_{\mathrm{soft}}$ | $0.02$ |
| 无 row 推进失败惩罚 | $w_{\mathrm{fail}}$ | $0.5$ |

若动作变化惩罚仍保留 $\frac{1}{N}$，但采用求和形式而不是本文的平均形式，可从下列量级开始：

$$
w_{\Delta a}^{\mathrm{sum}} = 1.0 \sim 2.0
$$

## 15. 预期作用

| 地形 | 主要起作用的奖励项 | 预期行为 |
|---|---|---|
| slope up | 稳定前进、姿态相对地形、接触保持、滑移惩罚 | 上坡时允许车体顺坡倾斜，但抑制车头栽下、轮子悬空和高滑移 |
| uneven rough | 地形突变前高速冲击、接触保持、姿态相对地形 | 通过 seam 和粗糙区域前减速，利用球铰保持三段支撑 |
| stairs up | 地形突变前高速冲击、row advance、接触保持、动作软限幅 | 台阶前降低速度，避免直接撞台阶，并通过姿态和推进配合进入下一 row |
| stairs down | 地形突变前高速冲击、姿态相对地形、悬空空转惩罚 | 下台阶前减速，抑制前车体突然下坠和后轮空转 |
| discrete obstacles | 接触保持、滑移惩罚、悬空空转惩罚、无推进失败惩罚 | 减少靠打滑、撞击和 reset 的侥幸通过，促使逐段稳定越障 |

## 16. 实现边界

该奖励函数草案当前明确不包含：

- 双目相机或 LiDAR 原始感知输入；
- 球铰极限惩罚；
- 非轮体碰撞惩罚；
- 前端传感器 clearance 惩罚；
- 针对某一地形硬编码的指定球铰姿态。

核心思路是：奖励“看到局部高度突变后，低滑移、多轮支撑、姿态稳定、动作平滑地推进到下一 row”的结果，而不是直接规定某一种固定跨越动作。
