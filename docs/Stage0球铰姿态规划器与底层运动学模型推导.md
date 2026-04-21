# Stage0球铰姿态规划器与底层运动学模型推导

## 文档状态

- 日期：2026-04-20
- 状态：候选推导稿
- 目标：在不破坏论文 `chapter03.tex` 现有符号体系的前提下，为 `Stage0` 建立一套“球铰姿态规划器 + 改进底层轮速分配”的一致表达
- 当前工作假设：
  - 本推导仅服务于 `Stage0` 平地协同转向主线
  - 当前只保留前、后模块相对中模块的偏航自由度
  - 当前不把 `pitch/roll` 主动调节纳入该阶段主线

## 1. 与 `chapter03.tex` 的符号继承关系

本文档完全继承论文第 3 章已经固定的核心记号。

- 前、中、后模块分别记为 $M_1$、$M_2$、$M_3$
- 三个模块参考点分别为 $O_1$、$O_2$、$O_3$
- 主坐标系固定在中模块参考点 $O_2$，记为 $\{B_2\}$
- 前、后模块相对中模块的实际构型仍记为 $\mathbf q$
- 期望构型仍记为 $\mathbf q^d$
- 球铰姿态角命令仍记为 $\mathbf q^{cmd}$
- 中模块期望平面运动命令仍记为

$$
\mathbf u_v =
\begin{bmatrix}
V_x^d \\
\Omega_z^d
\end{bmatrix}
$$

- 六个驱动轮角速度目标仍记为

$$
\boldsymbol\Omega^d =
\begin{bmatrix}
\Omega_{1L}^d \\
\Omega_{1R}^d \\
\Omega_{2L}^d \\
\Omega_{2R}^d \\
\Omega_{3L}^d \\
\Omega_{3R}^d
\end{bmatrix}
$$

因此，本推导不是另起一套符号，而是在 `chapter03.tex` 现有记号的基础上，对 `Stage0` 所需的两个子问题做进一步具体化：

1. 如何由 $\mathbf u_v$ 生成适合 `Stage0` 的 $\mathbf q^d$
2. 如何在轮速分配中显式引入球铰偏航变化率，而不再仅仅使用当前几何构型 $\mathbf q$

## 2. `Stage0` 的构型约化

论文第 3 章的通用构型写为

$$
\mathbf q =
\begin{bmatrix}
\psi_f & \theta_f & \phi_f & \psi_r & \theta_r & \phi_r
\end{bmatrix}^T
$$

对应的期望构型为

$$
\mathbf q^d =
\begin{bmatrix}
\psi_f^d & \theta_f^d & \phi_f^d & \psi_r^d & \theta_r^d & \phi_r^d
\end{bmatrix}^T
$$

在当前 `Stage0` 主线中，采用如下约化假设：

$$
\theta_f = \phi_f = \theta_r = \phi_r = 0
$$

$$
\theta_f^d = \phi_f^d = \theta_r^d = \phi_r^d = 0
$$

于是，`Stage0` 中真正参与协同转向的构型子向量只有

$$
\boldsymbol\psi =
\begin{bmatrix}
\psi_f \\
\psi_r
\end{bmatrix},
\qquad
\boldsymbol\psi^d =
\begin{bmatrix}
\psi_f^d \\
\psi_r^d
\end{bmatrix}
$$

从而通用构型可以写成

$$
\mathbf q =
\begin{bmatrix}
\psi_f & 0 & 0 & \psi_r & 0 & 0
\end{bmatrix}^T
$$

$$
\mathbf q^d =
\begin{bmatrix}
\psi_f^d & 0 & 0 & \psi_r^d & 0 & 0
\end{bmatrix}^T
$$

这个约化并不否定论文第 3 章的通用模型，而只是表明：

- 第 3 章给出的是通用输入输出框架
- `Stage0` 是该框架下的一个平地偏航协同特例

## 3. 球铰姿态规划器模型

### 3.1 规划器的作用

在论文第 3 章的通用口径中，高层可直接给出 $\mathbf q^d$。  
但对于当前 `Stage0`，若仍让高层策略直接输出全部球铰目标，则策略既要学转向，又要学轮速协调，动作语义过于松散。

因此，`Stage0` 中引入球铰姿态规划器，其任务是：

- 输入：$\mathbf u_v$ 与当前实际构型 $\mathbf q$
- 输出：`Stage0` 所需的 $\mathbf q^d$、$\mathbf q^{cmd}$，以及轮速分配所需的 $\dot{\psi}_f^d$、$\dot{\psi}_r^d$

即：

$$
(\mathbf u_v,\mathbf q,\mathcal P_\psi)
\longmapsto
(\mathbf q^d,\mathbf q^{cmd},\dot{\psi}_f^d,\dot{\psi}_r^d)
$$

其中，$\mathcal P_\psi$ 表示姿态规划器参数集合。

### 3.2 由平面命令构造等效曲率需求

为保持与第 3 章主命令记号一致，规划器仍以 $\mathbf u_v$ 为输入，不另起新的高层动作记号。  
在 `Stage0` 中定义等效曲率需求

$$
\kappa^d =
\frac{\Omega_z^d}{V_x^d + \varepsilon_v}
$$

其中：

- $\varepsilon_v > 0$ 为低速保护量
- 当前 `Stage0` 默认只允许前进，因此上式不额外讨论倒车符号翻转

该式的物理意义是：

- 当 $V_x^d$ 较大时，$\kappa^d$ 表示单位纵向前进距离对应的转弯强度
- 当 $V_x^d$ 很小时，$\varepsilon_v$ 防止曲率计算发散

### 3.3 前后球铰目标偏航角

为使前后模块围绕相容的瞬时转动中心形成协同转向，定义球铰目标偏航角的准静态参考值为

$$
\psi_f^\ast =
\operatorname{sat}
\left(
k_f \arctan(L_f \kappa^d),
-\psi_f^{\max},
\psi_f^{\max}
\right)
$$

$$
\psi_r^\ast =
\operatorname{sat}
\left(
-k_r \arctan(L_r \kappa^d),
-\psi_r^{\max},
\psi_r^{\max}
\right)
$$

其中：

- $L_f$、$L_r$ 为前、后模块的等效转向尺度参数
- $k_f$、$k_r$ 为前、后球铰偏航增益
- $\psi_f^{\max}$、$\psi_r^{\max}$ 为偏航角限幅

这里采用反号关系

$$
\psi_r^\ast \sim -\psi_f^\ast
$$

其目的是让前后模块围绕中模块协同折转，而不是同向偏折。

### 3.4 由实际构型到期望构型的动态过渡

仅给出准静态参考角还不够，因为轮速分配需要知道球铰当前“正在怎样转”。  
因此，进一步定义球铰期望偏航角速度为

$$
\dot{\psi}_f^d =
\operatorname{sat}
\left(
k_{\psi_f}(\psi_f^\ast - \psi_f),
-\dot{\psi}_f^{\max},
\dot{\psi}_f^{\max}
\right)
$$

$$
\dot{\psi}_r^d =
\operatorname{sat}
\left(
k_{\psi_r}(\psi_r^\ast - \psi_r),
-\dot{\psi}_r^{\max},
\dot{\psi}_r^{\max}
\right)
$$

若控制周期记为 $\Delta t$，则本周期的姿态目标可以离散更新为

$$
\psi_f^d = \psi_f + \Delta t \, \dot{\psi}_f^d
$$

$$
\psi_r^d = \psi_r + \Delta t \, \dot{\psi}_r^d
$$

于是，`Stage0` 中的完整期望构型为

$$
\mathbf q^d =
\begin{bmatrix}
\psi_f^d & 0 & 0 & \psi_r^d & 0 & 0
\end{bmatrix}^T
$$

并保持与第 3 章一致的命令定义：

$$
\mathbf q^{cmd} = \mathbf q^d
$$

### 3.5 规划器输出的物理意义

经过上述构造，球铰姿态规划器提供了两类信息：

1. 位置型命令：

$$
\mathbf q^{cmd} = \mathbf q^d
$$

2. 速度型辅助量：

$$
\dot{\boldsymbol\psi}^d =
\begin{bmatrix}
\dot{\psi}_f^d \\
\dot{\psi}_r^d
\end{bmatrix}
$$

前者送往球铰执行器，后者送入改进后的轮速分配模型。  
这正是当前 `chapter03.tex` 与 `Stage0` 结构化控制方案之间最关键的桥梁。

## 4. 基于 `chapter03.tex` 的改进底层运动学模型

### 4.1 从第 3 章当前模型出发

论文第 3 章当前轮速分配关系为

$$
\boldsymbol\Omega^d = \mathbf J_w(\mathbf q)\mathbf u_v
$$

这个模型的优点是：

- 完全继承当前几何构型 $\mathbf q$
- 符号清晰
- 易于实现

但它默认：

- 球铰对轮速分配的影响只通过当前静态几何构型进入
- 球铰“正在转动”所引起的轮心附加速度没有显式写入

因此，当 $\psi_f$、$\psi_r$ 已明显变化，或者球铰正在快速转向时，该模型会低估轮心真实的滚动速度需求。

### 4.2 `Stage0` 下的姿态矩阵与模块参考点位置

由第 3 章“相对姿态矩阵”定义可知，在当前 `Stage0` 约化下有

$$
{}^{2}\mathbf R_1 = \mathbf R_z(\psi_f),
\qquad
{}^{2}\mathbf R_3 = \mathbf R_z(\psi_r)
$$

进一步由第 3 章“模块参考点位置”定义可得

$$
{}^{2}\mathbf p_1 =
\begin{bmatrix}
a_x - b \cos\psi_f \\
-b \sin\psi_f \\
0
\end{bmatrix}
$$

$$
{}^{2}\mathbf p_3 =
\begin{bmatrix}
-a_x + b \cos\psi_r \\
b \sin\psi_r \\
0
\end{bmatrix}
$$

中模块参考点仍为

$$
{}^{2}\mathbf p_2 = \mathbf 0
$$

### 4.3 六个轮心在主坐标系中的位置

仍沿用第 3 章的轮心安装向量定义。  
在 `Stage0` 约化下，六个轮心在主坐标系中的位置可写为

$$
{}^{2}\mathbf p_{1L}
=
{}^{2}\mathbf a
+ \mathbf R_z(\psi_f)
\begin{bmatrix}
l_1 - b \\
\dfrac{d_1}{2} \\
h_1
\end{bmatrix}
$$

$$
{}^{2}\mathbf p_{1R}
=
{}^{2}\mathbf a
+ \mathbf R_z(\psi_f)
\begin{bmatrix}
l_1 - b \\
-\dfrac{d_1}{2} \\
h_1
\end{bmatrix}
$$

$$
{}^{2}\mathbf p_{2L}
=
\begin{bmatrix}
l_2 \\
\dfrac{d_2}{2} \\
h_2
\end{bmatrix},
\qquad
{}^{2}\mathbf p_{2R}
=
\begin{bmatrix}
l_2 \\
-\dfrac{d_2}{2} \\
h_2
\end{bmatrix}
$$

$$
{}^{2}\mathbf p_{3L}
=
-{}^{2}\mathbf a
+ \mathbf R_z(\psi_r)
\begin{bmatrix}
l_3 + b \\
\dfrac{d_3}{2} \\
h_3
\end{bmatrix}
$$

$$
{}^{2}\mathbf p_{3R}
=
-{}^{2}\mathbf a
+ \mathbf R_z(\psi_r)
\begin{bmatrix}
l_3 + b \\
-\dfrac{d_3}{2} \\
h_3
\end{bmatrix}
$$

其中

$$
{}^{2}\mathbf a =
\begin{bmatrix}
a_x \\
0 \\
0
\end{bmatrix}
$$

### 4.4 六个车轮的滚动方向

在 `Stage0` 假设下，各模块车轮滚动方向仍与局部 $x_i$ 轴一致，因此有

$$
{}^{2}\mathbf t_{1L} = {}^{2}\mathbf t_{1R} =
\begin{bmatrix}
\cos\psi_f \\
\sin\psi_f \\
0
\end{bmatrix}
$$

$$
{}^{2}\mathbf t_{2L} = {}^{2}\mathbf t_{2R} =
\begin{bmatrix}
1 \\
0 \\
0
\end{bmatrix}
$$

$$
{}^{2}\mathbf t_{3L} = {}^{2}\mathbf t_{3R} =
\begin{bmatrix}
\cos\psi_r \\
\sin\psi_r \\
0
\end{bmatrix}
$$

### 4.5 引入球铰偏航变化率后的轮心速度

第 3 章当前模型使用的轮心速度是

$$
{}^{2}\mathbf v_w^d =
{}^{2}\mathbf v_c^d
+ {}^{2}\boldsymbol\omega_c^d \times {}^{2}\mathbf p_w
$$

其中

$$
{}^{2}\mathbf v_c^d =
\begin{bmatrix}
V_x^d \\
0 \\
0
\end{bmatrix},
\qquad
{}^{2}\boldsymbol\omega_c^d =
\begin{bmatrix}
0 \\
0 \\
\Omega_z^d
\end{bmatrix}
$$

为把球铰“正在转向”的影响显式引入轮速分配，本推导在此基础上增加相对转动项。  
记前、后球铰连接中心分别为 $J_f$、$J_r$，则它们在主坐标系中的位置分别为

$$
{}^{2}\mathbf p_{J_f} = {}^{2}\mathbf a,
\qquad
{}^{2}\mathbf p_{J_r} = -{}^{2}\mathbf a
$$

于是定义改进后的轮心速度为

$$
{}^{2}\mathbf v_w^d =
{}^{2}\mathbf v_c^d
+ {}^{2}\boldsymbol\omega_c^d \times {}^{2}\mathbf p_w
+ {}^{2}\mathbf v_{w,art}^d
$$

其中，相对转动项按轮子所属模块分段写为

$$
{}^{2}\mathbf v_{w,art}^d =
\begin{cases}
\dot{\psi}_f^d \left( \mathbf e_z \times \left( {}^{2}\mathbf p_w - {}^{2}\mathbf p_{J_f} \right) \right), & w \in \{1L,1R\} \\
\mathbf 0, & w \in \{2L,2R\} \\
\dot{\psi}_r^d \left( \mathbf e_z \times \left( {}^{2}\mathbf p_w - {}^{2}\mathbf p_{J_r} \right) \right), & w \in \{3L,3R\}
\end{cases}
$$

这一步的物理意义是：

- 第一项：中模块期望纵向平动
- 第二项：中模块期望偏航运动对轮心的牵连速度
- 第三项：前/后模块相对中模块绕球铰偏航时，在轮心处诱导的附加速度

### 4.6 滚动投影与无滑移条件

与第 3 章保持一致，仍有

$$
v_{w,\parallel}^d =
\left( {}^{2}\mathbf t_w \right)^T
{}^{2}\mathbf v_w^d
$$

$$
\rho_i \Omega_w^d = v_{w,\parallel}^d
$$

因此单轮角速度表达式变为

$$
\Omega_w^d =
\frac{1}{\rho_i}
\left( {}^{2}\mathbf t_w \right)^T
\left(
{}^{2}\mathbf v_c^d
+ {}^{2}\boldsymbol\omega_c^d \times {}^{2}\mathbf p_w
+ {}^{2}\mathbf v_{w,art}^d
\right)
$$

## 5. `Stage0` 下的显式轮速解析式

### 5.1 扩展输入向量

为了保持与第 3 章 $\mathbf u_v$ 的连续性，这里不废弃 $\mathbf u_v$，而是在其后追加球铰目标偏航角速度，定义扩展命令向量

$$
\bar{\mathbf u}_v =
\begin{bmatrix}
V_x^d \\
\Omega_z^d \\
\dot{\psi}_f^d \\
\dot{\psi}_r^d
\end{bmatrix}
$$

对应地，引入 `Stage0` 的扩展轮速分配矩阵

$$
\bar{\mathbf J}_w(\mathbf q) \in \mathbb R^{6 \times 4}
$$

使得

$$
\boldsymbol\Omega^d = \bar{\mathbf J}_w(\mathbf q)\bar{\mathbf u}_v
$$

### 5.2 前轮的附加投影项

对前左轮，由于

$$
{}^{2}\mathbf p_{1L} - {}^{2}\mathbf p_{J_f}
=
\mathbf R_z(\psi_f)
\begin{bmatrix}
l_1 - b \\
\dfrac{d_1}{2} \\
h_1
\end{bmatrix}
$$

且

$$
{}^{2}\mathbf t_{1L} =
\mathbf R_z(\psi_f)
\begin{bmatrix}
1 \\
0 \\
0
\end{bmatrix}
$$

利用 $\mathbf R_z(\psi_f)$ 与 $\mathbf e_z$ 的交换性质，可得

$$
\left( {}^{2}\mathbf t_{1L} \right)^T
\left(
\mathbf e_z \times
\left( {}^{2}\mathbf p_{1L} - {}^{2}\mathbf p_{J_f} \right)
\right)
=
-\dfrac{d_1}{2}
$$

同理，

$$
\left( {}^{2}\mathbf t_{1R} \right)^T
\left(
\mathbf e_z \times
\left( {}^{2}\mathbf p_{1R} - {}^{2}\mathbf p_{J_f} \right)
\right)
=
\dfrac{d_1}{2}
$$

后轮完全同理，有

$$
\left( {}^{2}\mathbf t_{3L} \right)^T
\left(
\mathbf e_z \times
\left( {}^{2}\mathbf p_{3L} - {}^{2}\mathbf p_{J_r} \right)
\right)
=
-\dfrac{d_3}{2}
$$

$$
\left( {}^{2}\mathbf t_{3R} \right)^T
\left(
\mathbf e_z \times
\left( {}^{2}\mathbf p_{3R} - {}^{2}\mathbf p_{J_r} \right)
\right)
=
\dfrac{d_3}{2}
$$

### 5.3 六轮角速度最终显式表达式

记

$$
c_\alpha = \cos\alpha,
\qquad
s_\alpha = \sin\alpha
$$

则六个车轮的角速度目标可以整理为

$$
\Omega_{1L}^d =
\frac{1}{\rho_1}
\left[
c_{\psi_f} V_x^d
+ \left( a_x s_{\psi_f} - \dfrac{d_1}{2} \right)\Omega_z^d
- \dfrac{d_1}{2}\dot{\psi}_f^d
\right]
$$

$$
\Omega_{1R}^d =
\frac{1}{\rho_1}
\left[
c_{\psi_f} V_x^d
+ \left( a_x s_{\psi_f} + \dfrac{d_1}{2} \right)\Omega_z^d
+ \dfrac{d_1}{2}\dot{\psi}_f^d
\right]
$$

$$
\Omega_{2L}^d =
\frac{1}{\rho_2}
\left(
V_x^d - \dfrac{d_2}{2}\Omega_z^d
\right)
$$

$$
\Omega_{2R}^d =
\frac{1}{\rho_2}
\left(
V_x^d + \dfrac{d_2}{2}\Omega_z^d
\right)
$$

$$
\Omega_{3L}^d =
\frac{1}{\rho_3}
\left[
c_{\psi_r} V_x^d
+ \left( -a_x s_{\psi_r} - \dfrac{d_3}{2} \right)\Omega_z^d
- \dfrac{d_3}{2}\dot{\psi}_r^d
\right]
$$

$$
\Omega_{3R}^d =
\frac{1}{\rho_3}
\left[
c_{\psi_r} V_x^d
+ \left( -a_x s_{\psi_r} + \dfrac{d_3}{2} \right)\Omega_z^d
+ \dfrac{d_3}{2}\dot{\psi}_r^d
\right]
$$

### 5.4 单轮行向量形式

于是六个单轮分配行向量分别为

$$
\bar{\mathbf j}_{1L}(\mathbf q) =
\frac{1}{\rho_1}
\begin{bmatrix}
c_{\psi_f} &
a_x s_{\psi_f} - \dfrac{d_1}{2} &
-\dfrac{d_1}{2} &
0
\end{bmatrix}
$$

$$
\bar{\mathbf j}_{1R}(\mathbf q) =
\frac{1}{\rho_1}
\begin{bmatrix}
c_{\psi_f} &
a_x s_{\psi_f} + \dfrac{d_1}{2} &
\dfrac{d_1}{2} &
0
\end{bmatrix}
$$

$$
\bar{\mathbf j}_{2L} =
\frac{1}{\rho_2}
\begin{bmatrix}
1 &
-\dfrac{d_2}{2} &
0 &
0
\end{bmatrix},
\qquad
\bar{\mathbf j}_{2R} =
\frac{1}{\rho_2}
\begin{bmatrix}
1 &
\dfrac{d_2}{2} &
0 &
0
\end{bmatrix}
$$

$$
\bar{\mathbf j}_{3L}(\mathbf q) =
\frac{1}{\rho_3}
\begin{bmatrix}
c_{\psi_r} &
-a_x s_{\psi_r} - \dfrac{d_3}{2} &
0 &
-\dfrac{d_3}{2}
\end{bmatrix}
$$

$$
\bar{\mathbf j}_{3R}(\mathbf q) =
\frac{1}{\rho_3}
\begin{bmatrix}
c_{\psi_r} &
-a_x s_{\psi_r} + \dfrac{d_3}{2} &
0 &
\dfrac{d_3}{2}
\end{bmatrix}
$$

从而

$$
\bar{\mathbf J}_w(\mathbf q) =
\begin{bmatrix}
\bar{\mathbf j}_{1L}(\mathbf q) \\
\bar{\mathbf j}_{1R}(\mathbf q) \\
\bar{\mathbf j}_{2L} \\
\bar{\mathbf j}_{2R} \\
\bar{\mathbf j}_{3L}(\mathbf q) \\
\bar{\mathbf j}_{3R}(\mathbf q)
\end{bmatrix}
$$

## 6. 与论文第 3 章当前模型的关系

### 6.1 一致性

本推导与第 3 章保持一致的部分包括：

- 坐标系定义不变
- 几何参数 ${}^{2}\mathbf a$、${}^{1}\mathbf b$、${}^{3}\mathbf b$ 的含义不变
- 实际构型 $\mathbf q$、期望构型 $\mathbf q^d$、球铰命令 $\mathbf q^{cmd}$ 的含义不变
- 六轮命名顺序与 $\boldsymbol\Omega^d$ 写法不变

### 6.2 相对第 3 章的阶段性增强

`Stage0` 当前采用的结构化控制，不是推翻第 3 章，而是在其基础上增加两步：

1. 用球铰姿态规划器内部生成 `Stage0` 所需的 $\mathbf q^d$
2. 在轮速分配中把 $\dot{\psi}_f^d$、$\dot{\psi}_r^d$ 显式写入轮心速度传播

因此，`Stage0` 的整体输入输出可以写为

$$
(\mathbf u_v,\mathbf q,\mathcal P,\mathcal P_\psi)
\longmapsto
(\boldsymbol\Omega^d,\mathbf q^{cmd})
$$

其中：

- $\mathcal P$ 为第 3 章已有的固定几何参数集合
- $\mathcal P_\psi$ 为球铰姿态规划器参数集合

### 6.3 退化检验

若球铰偏航角速度为零，即

$$
\dot{\psi}_f^d = \dot{\psi}_r^d = 0
$$

则有

$$
\bar{\mathbf J}_w(\mathbf q)\bar{\mathbf u}_v
\;\Longrightarrow\;
\mathbf J_w(\mathbf q)\mathbf u_v
$$

并退化回论文第 3 章当前的静态几何轮速分配模型。  
因此，这个改进模型与 `chapter03.tex` 在数学上是前后兼容的，而不是两套彼此割裂的表达。

## 7. 当前结论

在 `Stage0` 的工作假设下，更合适的控制链路可以概括为：

1. 高层给出 $\mathbf u_v$
2. 球铰姿态规划器由 $\mathbf u_v$ 与当前 $\mathbf q$ 生成 $\mathbf q^d$ 与 $\mathbf q^{cmd}$
3. 改进底层运动学模型由 $\mathbf u_v$、$\mathbf q$ 与 $\dot{\boldsymbol\psi}^d$ 生成 $\boldsymbol\Omega^d$

这样处理后：

- 球铰是否参与转向，不再靠策略随机试探
- 前后模块已经偏航或正在转向时，轮速会随之解析变化
- 整个表达仍然保持与第 3 章一致的主符号体系

## 8. 后续落地含义

若后续确认采用该方案，则工程实现应按如下顺序推进：

1. 在环境中新增球铰姿态规划器
2. 将策略高层动作口径收缩为与 $\mathbf u_v$ 一致的平面命令
3. 将当前 $\mathbf J_w(\mathbf q)\mathbf u_v$ 替换为 $\bar{\mathbf J}_w(\mathbf q)\bar{\mathbf u}_v$
4. 在更下一层再叠加接触加权驱动力/力矩分配器

需要强调的是：

- 本文档完成的是“姿态规划器 + 改进底层运动学模型”的建模与推导
- 轮胎接地权重、滑移抑制和驱动力分配属于其后的动力学/牵引分配层，不在本文档的纯运动学推导范围内
