下面按你的三点约束，重新整理一版更适合论文使用、且可被 Obsidian 直接编译的运动学—动力学统一符号定义表：

- 车轮索引统一使用 $k$，不再使用 $w$。
- 中车绕自身 $z$ 轴的角速度继续使用 $\omega_z$，命名为“中模块绕 $z_B$ 轴角速度”，不再叫“横摆角速度”。
- 球铰姿态继续使用 $\mathbf q$，并明确它表示“节间姿态参数向量”，不是整车完整广义坐标。

---

# 1. 坐标系与索引符号

| 符号 | 含义 | 说明 |
|---|---|---|
| ${I}$ | 惯性坐标系 | 固定于地面或世界坐标系 |
| ${B_i}$ | 第 $i$ 个车体模块坐标系 | $i=1,2,3$ 分别表示前、中、后模块 |
| ${B}$ | 中模块车体坐标系 | 为简化记号，令 ${B}\equiv{B_2}$ |
| $i$ | 车体模块编号 | $i\in\{1,2,3\}$ |
| $k$ | 车轮编号 | $k\in\mathcal K$ |
| $\mathcal K$ | 全车车轮索引集合 | $\mathcal K=\{1L,1R,2L,2R,3L,3R\}$ |
| $L,R$ | 左、右车轮标记 | $L$ 表示左轮，$R$ 表示右轮 |

---

# 2. 中模块运动状态符号

| 符号 | 含义 | 单位 | 说明 |
|---|---|---|---|
| $v_x$ | 中模块在自身 $x_B$ 轴方向的速度 | m/s | 车体系纵向速度 |
| $v_y$ | 中模块在自身 $y_B$ 轴方向的速度 | m/s | 车体系侧向速度 |
| $\omega_z$ | 中模块绕自身 $z_B$ 轴的角速度 | rad/s | 比“横摆角速度”更直观 |
| $\dot{\omega}_z$ | 中模块绕自身 $z_B$ 轴的角加速度 | rad/s$^2$ | 动力学方程中使用 |
| $\mathbf v_B$ | 中模块平动速度向量 | m/s | 可定义为 $\mathbf v_B=[v_x,v_y]^T$ |
| $\boldsymbol\nu_B$ | 中模块平面运动速度向量 | — | 推荐定义为 $\boldsymbol\nu_B=[v_x,v_y,\omega_z]^T$ |

如果论文中只考虑中模块纵向速度和绕 $z_B$ 轴角速度命令，可以定义：

$$
\boldsymbol\nu_B^{\mathrm{cmd}}
=
\begin{bmatrix}
v_x^{\mathrm{cmd}}\\
\omega_z^{\mathrm{cmd}}
\end{bmatrix}.
$$

其中：

| 符号 | 含义 |
|---|---|
| $v_x^{\mathrm{cmd}}$ | RL 输出或上层控制器给出的中模块 $x_B$ 轴速度命令 |
| $\omega_z^{\mathrm{cmd}}$ | RL 输出或上层控制器给出的中模块绕自身 $z_B$ 轴角速度命令 |

---

# 3. 球铰姿态符号

| 符号 | 含义 | 单位 | 说明 |
|---|---|---|---|
| $\mathbf q_f$ | 前模块相对中模块的球铰姿态参数 | rad | 对应前球铰 |
| $\mathbf q_r$ | 后模块相对中模块的球铰姿态参数 | rad | 对应后球铰 |
| $\mathbf q$ | 全车节间姿态参数向量 | rad | 包含前、后两个球铰的 6 个姿态自由度 |
| $\dot{\mathbf q}$ | 节间姿态参数变化率 | rad/s | 是姿态角变化率，不直接等于空间角速度 |
| $\ddot{\mathbf q}$ | 节间姿态参数二阶导数 | rad/s$^2$ | 用于球铰执行动力学 |
| $\mathbf q^{\mathrm{ref}}$ | 球铰姿态参考值 | rad | 由 RL 或高层控制器输出 |
| $\dot{\mathbf q}^{\mathrm{ref}}$ | 球铰姿态参考变化率 | rad/s | 可由 $\mathbf q^{\mathrm{ref}}$ 平滑规划得到 |

建议定义为：

$$
\mathbf q_f=
\begin{bmatrix}
\psi_f\\
\theta_f\\
\phi_f
\end{bmatrix},
\qquad
\mathbf q_r=
\begin{bmatrix}
\psi_r\\
\theta_r\\
\phi_r
\end{bmatrix},
$$

$$
\mathbf q=
\begin{bmatrix}
\mathbf q_f^T & \mathbf q_r^T
\end{bmatrix}^T
=
\begin{bmatrix}
\psi_f & \theta_f & \phi_f & \psi_r & \theta_r & \phi_r
\end{bmatrix}^T.
$$

其中：

| 符号 | 含义 |
|---|---|
| $\psi_f$ | 前模块相对中模块的绕 $z$ 轴姿态角 |
| $\theta_f$ | 前模块相对中模块的绕 $y$ 轴姿态角 |
| $\phi_f$ | 前模块相对中模块的绕 $x$ 轴姿态角 |
| $\psi_r$ | 后模块相对中模块的绕 $z$ 轴姿态角 |
| $\theta_r$ | 后模块相对中模块的绕 $y$ 轴姿态角 |
| $\phi_r$ | 后模块相对中模块的绕 $x$ 轴姿态角 |

建议在论文中明确写一句：

> 本文中的 $\mathbf q$ 表示前、后模块相对中模块的节间姿态参数向量，而非包含整车位姿和轮子转角的完整广义坐标。

这一句很重要，可以避免评审误解。

---

# 4. 车轮运动符号

| 符号 | 含义 | 单位 | 说明 |
|---|---|---|---|
| $k$ | 第 $k$ 个车轮 | — | $k\in\mathcal K$ |
| $\omega_k$ | 第 $k$ 个车轮的实际自转角速度 | rad/s | 车轮自身转动速度 |
| $\dot{\omega}_k$ | 第 $k$ 个车轮的角加速度 | rad/s$^2$ | 车轮转动动力学中使用 |
| $\omega_k^{\mathrm{ref}}$ | 第 $k$ 个车轮的参考自转角速度 | rad/s | 由运动学模型输出 |
| $\boldsymbol\omega_K$ | 六个车轮实际角速度向量 | rad/s | 下标 $K$ 表示 wheel index set |
| $\boldsymbol\omega_K^{\mathrm{ref}}$ | 六个车轮参考角速度向量 | rad/s | 运动学层输出 |
| $R_k$ | 第 $k$ 个车轮有效半径 | m | 建议用 $R_k$，比 $\rho_k$ 更直观 |
| $\tau_k$ | 第 $k$ 个车轮驱动力矩 | N·m | 动力学控制输入 |
| $I_k$ | 第 $k$ 个车轮等效转动惯量 | kg·m$^2$ | 不建议用 $J_k$，避免和雅可比混淆 |
| $B_k$ | 第 $k$ 个车轮等效阻尼系数 | N·m·s/rad | 轮系粘性阻尼 |

六轮实际角速度向量定义为：

$$
\boldsymbol\omega_K=
\begin{bmatrix}
\omega_{1L} &
\omega_{1R} &
\omega_{2L} &
\omega_{2R} &
\omega_{3L} &
\omega_{3R}
\end{bmatrix}^T.
$$

六轮参考角速度向量定义为：

$$
\boldsymbol\omega_K^{\mathrm{ref}}=
\begin{bmatrix}
\omega_{1L}^{\mathrm{ref}} &
\omega_{1R}^{\mathrm{ref}} &
\omega_{2L}^{\mathrm{ref}} &
\omega_{2R}^{\mathrm{ref}} &
\omega_{3L}^{\mathrm{ref}} &
\omega_{3R}^{\mathrm{ref}}
\end{bmatrix}^T.
$$

注意这里虽然中模块绕 $z_B$ 轴角速度和车轮角速度都使用 $\omega$，但通过下标可以清楚区分：

$$
\omega_z
$$

表示中模块绕自身 $z_B$ 轴角速度；

$$
\omega_k
$$

表示第 $k$ 个车轮的自转角速度。

这是可以接受的。

---

# 5. 几何参数与位置符号

| 符号 | 含义 | 单位 | 说明 |
|---|---|---|---|
| ${}^B\mathbf p_k$ | 第 $k$ 个轮心在中模块坐标系下的位置向量 | m | 由当前构型 $\mathbf q$ 决定 |
| ${}^{B_i}\mathbf r_{iL}$ | 第 $i$ 个模块左轮轮心在本模块坐标系下的安装向量 | m | 局部固定几何量 |
| ${}^{B_i}\mathbf r_{iR}$ | 第 $i$ 个模块右轮轮心在本模块坐标系下的安装向量 | m | 局部固定几何量 |
| $l_i$ | 第 $i$ 个模块轮心纵向安装偏置 | m | 相对模块参考点 |
| $T_i$ | 第 $i$ 个模块轮距 | m | 建议使用 $T_i$，不要用 $d_i$ |
| $h_i$ | 第 $i$ 个模块轮心竖向安装偏置 | m | 轮心高度偏置 |
| $\mathbf R_{Bi}$ | 第 $i$ 个模块坐标系到中模块坐标系的旋转矩阵 | — | 由 $\mathbf q$ 决定 |
| ${}^B\mathbf t_k$ | 第 $k$ 个车轮滚动方向单位向量 | — | 在中模块坐标系中表示 |

轮心安装向量建议写为：

$$
{}^{B_i}\mathbf r_{iL}=
\begin{bmatrix}
l_i\\
T_i/2\\
h_i
\end{bmatrix},
\qquad
{}^{B_i}\mathbf r_{iR}=
\begin{bmatrix}
l_i\\
-T_i/2\\
h_i
\end{bmatrix}.
$$

第 $k$ 个轮心在中模块坐标系下的位置写为：

$$
{}^B\mathbf p_k
=
{}^B\mathbf p_{B_i}
+
\mathbf R_{Bi}\,{}^{B_i}\mathbf r_k.
$$

其中 ${}^B\mathbf p_{B_i}$ 表示第 $i$ 个模块参考点在中模块坐标系下的位置。

---

# 6. 运动学雅可比与轮速分配符号

| 符号 | 含义 | 维度 | 说明 |
|---|---|---|---|
| ${}^B\mathbf J_{p,k}(\mathbf q)$ | 第 $k$ 个轮心位置对球铰姿态的雅可比矩阵 | $3\times 6$ | 描述构型变化对轮心速度的影响 |
| $\mathbf J_{\omega v}(\mathbf q)$ | 中模块速度命令到六轮角速度的映射矩阵 | $6\times 2$ | 由几何构型和轮心位置决定 |
| $\mathbf J_{\omega q}(\mathbf q)$ | 球铰姿态变化率到六轮角速度修正量的映射矩阵 | $6\times 6$ | 描述主动构型变化对轮速的影响 |

建议写成：

$$
{}^B\mathbf J_{p,k}(\mathbf q)
=
\frac{\partial {}^B\mathbf p_k(\mathbf q)}{\partial \mathbf q}.
$$

第 $k$ 个车轮的参考角速度为：

$$
\omega_k^{\mathrm{ref}}
=
\frac{1}{R_k}
\left({}^B\mathbf t_k\right)^T
\left(
{}^B\mathbf v_B^{\mathrm{cmd}}
+
{}^B\boldsymbol\omega_B^{\mathrm{cmd}}\times{}^B\mathbf p_k
+
{}^B\mathbf J_{p,k}(\mathbf q)\dot{\mathbf q}^{\mathrm{ref}}
\right).
$$

其中：

$$
{}^B\mathbf v_B^{\mathrm{cmd}}
=
\begin{bmatrix}
v_x^{\mathrm{cmd}}\\
0\\
0
\end{bmatrix},
\qquad
{}^B\boldsymbol\omega_B^{\mathrm{cmd}}
=
\begin{bmatrix}
0\\
0\\
\omega_z^{\mathrm{cmd}}
\end{bmatrix}.
$$

六轮整体轮速分配关系写为：

$$
\boldsymbol\omega_K^{\mathrm{ref}}
=
\mathbf J_{\omega v}(\mathbf q)\boldsymbol\nu_B^{\mathrm{cmd}}
+
\mathbf J_{\omega q}(\mathbf q)\dot{\mathbf q}^{\mathrm{ref}}.
$$

其中：

$$
\boldsymbol\nu_B^{\mathrm{cmd}}
=
\begin{bmatrix}
v_x^{\mathrm{cmd}}\\
\omega_z^{\mathrm{cmd}}
\end{bmatrix}.
$$

---

# 7. 轮胎接触与滑移符号

| 符号 | 含义 | 单位 | 说明 |
|---|---|---|---|
| ${}^{T_k}v_{x,k}$ | 第 $k$ 个车轮在轮胎坐标系下的纵向速度 | m/s | 沿车轮滚动方向 |
| ${}^{T_k}v_{y,k}$ | 第 $k$ 个车轮在轮胎坐标系下的侧向速度 | m/s | 垂直于滚动方向 |
| $\kappa_k$ | 第 $k$ 个车轮纵向滑移率 | — | 表示空转或拖滑程度 |
| $\alpha_k$ | 第 $k$ 个车轮侧偏角 | rad | 表示侧向滑移程度 |
| $\mu_k$ | 第 $k$ 个车轮接触处地面摩擦系数 | — | 由地形决定 |
| $F_{z,k}$ | 第 $k$ 个车轮法向接触力 | N | 来自仿真接触或估计模型 |
| $C_{\kappa,k}$ | 第 $k$ 个车轮纵向刚度系数 | N | 滑移率到纵向力的比例系数 |
| $C_{\alpha,k}$ | 第 $k$ 个车轮侧偏刚度系数 | N/rad | 侧偏角到侧向力的比例系数 |

滑移率建议定义为：

$$
\kappa_k
=
\frac{R_k\omega_k-{}^{T_k}v_{x,k}}
{\max\left(|R_k\omega_k|,\ |{}^{T_k}v_{x,k}|,\ \varepsilon\right)}.
$$

侧偏角定义为：

$$
\alpha_k
=
\operatorname{atan2}
\left(
{}^{T_k}v_{y,k},
|{}^{T_k}v_{x,k}|+\varepsilon
\right).
$$

---

# 8. 轮胎力符号

| 符号 | 含义 | 单位 | 说明 |
|---|---|---|---|
| ${}^{T_k}F_{x,k}$ | 第 $k$ 个车轮在轮胎坐标系下的纵向力 | N | 沿滚动方向 |
| ${}^{T_k}F_{y,k}$ | 第 $k$ 个车轮在轮胎坐标系下的侧向力 | N | 垂直滚动方向 |
| ${}^{B}F_{x,k}$ | 第 $k$ 个车轮力在中模块坐标系下的 $x_B$ 分量 | N | 用于整车动力学 |
| ${}^{B}F_{y,k}$ | 第 $k$ 个车轮力在中模块坐标系下的 $y_B$ 分量 | N | 用于整车动力学 |
| $F_{rr,k}$ | 第 $k$ 个车轮滚动阻力 | N | 可简化建模 |

未饱和轮胎力可写为：

$$
\widetilde F_{x,k}^{T}
=
C_{\kappa,k}\kappa_k,
$$

$$
\widetilde F_{y,k}^{T}
=
C_{\alpha,k}\alpha_k.
$$

摩擦饱和系数：

$$
\lambda_k
=
\min
\left(
1,
\frac{\mu_k F_{z,k}}
{\sqrt{
\left(\widetilde F_{x,k}^{T}\right)^2+
\left(\widetilde F_{y,k}^{T}\right)^2+
\varepsilon
}}
\right).
$$

实际轮胎力：

$$
{}^{T_k}F_{x,k}
=
\lambda_k\widetilde F_{x,k}^{T},
\qquad
{}^{T_k}F_{y,k}
=
\lambda_k\widetilde F_{y,k}^{T}.
$$

---

# 9. 车轮转动动力学符号

| 符号 | 含义 | 单位 | 说明 |
|---|---|---|---|
| $I_k$ | 第 $k$ 个车轮等效转动惯量 | kg·m$^2$ | 推荐用 $I_k$，不用 $J_k$ |
| $\tau_k$ | 第 $k$ 个车轮驱动力矩 | N·m | 底层执行器输入 |
| $B_k$ | 第 $k$ 个车轮粘性阻尼系数 | N·m·s/rad | 轮系内部阻尼 |
| $R_k{}^{T_k}F_{x,k}$ | 地面对车轮造成的反作用力矩 | N·m | 与驱动力矩方向相反 |
| $R_kF_{rr,k}$ | 滚动阻力矩 | N·m | 抵抗车轮转动 |

车轮转动动力学建议写为：

$$
I_k\dot{\omega}_k
=
\tau_k
-R_k{}^{T_k}F_{x,k}
-R_kF_{rr,k}
-B_k\omega_k.
$$

---

# 10. 整车平面动力学符号

| 符号 | 含义 | 单位 | 说明 |
|---|---|---|---|
| $m$ | 整车等效质量 | kg | 可视为三模块总质量 |
| $I_z$ | 整车绕中模块 $z_B$ 轴的等效转动惯量 | kg·m$^2$ | 对应 $\omega_z$ |
| $c_x$ | 纵向等效阻尼系数 | N·s/m | 简化阻力项 |
| $c_y$ | 侧向等效阻尼系数 | N·s/m | 简化侧向阻尼 |
| $c_z$ | 绕 $z_B$ 轴旋转阻尼系数 | N·m·s/rad | 对应 $\omega_z$ |
| $x_k$ | 第 $k$ 个轮心在中模块坐标系下的 $x_B$ 坐标 | m | 来自 ${}^B\mathbf p_k$ |
| $y_k$ | 第 $k$ 个轮心在中模块坐标系下的 $y_B$ 坐标 | m | 来自 ${}^B\mathbf p_k$ |

整车平面动力学建议写为：

$$
m(\dot v_x-\omega_z v_y)
=
\sum_{k\in\mathcal K}{}^{B}F_{x,k}
-c_xv_x,
$$

$$
m(\dot v_y+\omega_z v_x)
=
\sum_{k\in\mathcal K}{}^{B}F_{y,k}
-c_yv_y,
$$

$$
I_z\dot{\omega}_z
=
\sum_{k\in\mathcal K}
\left(
x_k{}^{B}F_{y,k}
-y_k{}^{B}F_{x,k}
\right)
-c_z\omega_z.
$$

这里不再使用“横摆角速度”这个名称，而统一称为：

$$
\omega_z:\text{中模块绕自身 }z_B\text{ 轴的角速度}.
$$

---

# 11. 球铰执行动力学符号

| 符号 | 含义 | 单位 | 说明 |
|---|---|---|---|
| $q_j$ | 第 $j$ 个球铰姿态自由度 | rad | $j=1,\dots,6$ |
| $\dot q_j$ | 第 $j$ 个球铰姿态自由度变化率 | rad/s | 姿态角变化率 |
| $\ddot q_j$ | 第 $j$ 个球铰姿态自由度加速度 | rad/s$^2$ | 执行动力学中使用 |
| $I_{q,j}$ | 第 $j$ 个球铰自由度等效转动惯量 | kg·m$^2$ | 建议用 $I_{q,j}$，不用 $J_{a,j}$ |
| $B_{q,j}$ | 第 $j$ 个球铰自由度等效阻尼 | N·m·s/rad | 执行器阻尼 |
| $\tau_{q,j}$ | 第 $j$ 个球铰执行器输出力矩 | N·m | 物理控制输入 |
| $\tau_{q,j}^{\mathrm{dist}}$ | 第 $j$ 个球铰自由度外部扰动力矩 | N·m | 包含地形冲击、未建模耦合等 |

单自由度执行动力学：

$$
I_{q,j}\ddot q_j
+
B_{q,j}\dot q_j
=
\tau_{q,j}
+
\tau_{q,j}^{\mathrm{dist}}.
$$

PD 控制律：

$$
\tau_{q,j}
=
K_{p,j}\left(q_j^{\mathrm{ref}}-q_j\right)
+
K_{d,j}\left(\dot q_j^{\mathrm{ref}}-\dot q_j\right).
$$

向量形式：

$$
\mathbf I_q\ddot{\mathbf q}
+
\mathbf B_q\dot{\mathbf q}
=
\boldsymbol\tau_q
+
\boldsymbol\tau_q^{\mathrm{dist}}.
$$

其中：

$$
\boldsymbol\tau_q=
\begin{bmatrix}
\tau_{q,1} &
\tau_{q,2} &
\tau_{q,3} &
\tau_{q,4} &
\tau_{q,5} &
\tau_{q,6}
\end{bmatrix}^T.
$$

---

# 12. RL、运动学层、动力学层接口符号

| 符号 | 含义 | 说明 |
|---|---|---|
| $\mathbf a_{\mathrm{RL}}$ | RL 策略输出动作 | 高层目标，不是直接物理力矩 |
| $\boldsymbol\nu_B^{\mathrm{cmd}}$ | 中模块运动命令 | 包含 $v_x^{\mathrm{cmd}}$ 和 $\omega_z^{\mathrm{cmd}}$ |
| $\mathbf q^{\mathrm{ref}}$ | 球铰姿态参考目标 | RL 输出或由规划器生成 |
| $\boldsymbol\omega_K^{\mathrm{ref}}$ | 六轮参考角速度 | 运动学模型输出 |
| $\mathbf u_{\mathrm{int}}$ | 运动学层传递给动力学层的接口输入 | 包含轮速参考和球铰姿态参考 |
| $\boldsymbol\tau_K$ | 六轮驱动力矩向量 | 动力学或底层控制器输出 |
| $\boldsymbol\tau_q$ | 六个球铰执行器力矩向量 | 动力学或底层控制器输出 |

RL 输出建议定义为：

$$
\mathbf a_{\mathrm{RL}}
=
\begin{bmatrix}
\left(\boldsymbol\nu_B^{\mathrm{cmd}}\right)^T &
\left(\mathbf q^{\mathrm{ref}}\right)^T
\end{bmatrix}^T.
$$

其中：

$$
\boldsymbol\nu_B^{\mathrm{cmd}}
=
\begin{bmatrix}
v_x^{\mathrm{cmd}}\\
\omega_z^{\mathrm{cmd}}
\end{bmatrix}.
$$

运动学层输出：

$$
\boldsymbol\omega_K^{\mathrm{ref}}
=
\mathbf J_{\omega v}(\mathbf q)\boldsymbol\nu_B^{\mathrm{cmd}}
+
\mathbf J_{\omega q}(\mathbf q)\dot{\mathbf q}^{\mathrm{ref}}.
$$

动力学接口输入：

$$
\mathbf u_{\mathrm{int}}
=
\begin{bmatrix}
\left(\boldsymbol\omega_K^{\mathrm{ref}}\right)^T &
\left(\mathbf q^{\mathrm{ref}}\right)^T
\end{bmatrix}^T.
$$

---

# 13. 动力学状态变量符号

建议最终动力学状态定义为：

$$
\mathbf x=
\begin{bmatrix}
v_x &
v_y &
\omega_z &
\boldsymbol\omega_K^T &
\mathbf q^T &
\dot{\mathbf q}^T
\end{bmatrix}^T.
$$

各部分含义如下：

| 符号 | 含义 |
|---|---|
| $v_x$ | 中模块沿自身 $x_B$ 轴速度 |
| $v_y$ | 中模块沿自身 $y_B$ 轴速度 |
| $\omega_z$ | 中模块绕自身 $z_B$ 轴角速度 |
| $\boldsymbol\omega_K$ | 六个车轮实际角速度 |
| $\mathbf q$ | 六维球铰姿态参数 |
| $\dot{\mathbf q}$ | 六维球铰姿态参数变化率 |

状态空间模型可写为：

$$
\dot{\mathbf x}
=
\mathbf f
\left(
\mathbf x,
\mathbf u_{\mathrm{int}},
\mathcal P_{\mathrm{dyn}},
\mathcal H
\right).
$$

其中：

| 符号 | 含义 |
|---|---|
| $\mathcal P_{\mathrm{dyn}}$ | 动力学模型参数集合 |
| $\mathcal H$ | 地形与接触信息集合 |

不要再用 $\mathbf p$ 表示参数集合，因为 $\mathbf p_k$ 已经表示轮心位置。

---

# 14. 最终推荐符号总表

| 类别 | 推荐符号 | 含义 |
|---|---|---|
| 车体坐标系 | ${B}$ | 中模块坐标系，${B}\equiv{B_2}$ |
| 模块编号 | $i$ | $i=1,2,3$，分别表示前、中、后模块 |
| 车轮编号 | $k$ | $k\in\mathcal K$ |
| 车轮集合 | $\mathcal K$ | $\{1L,1R,2L,2R,3L,3R\}$ |
| 中模块纵向速度 | $v_x$ | 沿 $x_B$ 轴速度 |
| 中模块侧向速度 | $v_y$ | 沿 $y_B$ 轴速度 |
| 中模块 $z_B$ 轴角速度 | $\omega_z$ | 中车绕自身 $z$ 轴转动速度 |
| 中模块速度命令 | $\boldsymbol\nu_B^{\mathrm{cmd}}$ | $[v_x^{\mathrm{cmd}},\omega_z^{\mathrm{cmd}}]^T$ |
| 球铰姿态 | $\mathbf q$ | 六维节间姿态参数 |
| 球铰姿态参考 | $\mathbf q^{\mathrm{ref}}$ | RL 或规划器输出的参考姿态 |
| 球铰姿态变化率 | $\dot{\mathbf q}$ | 姿态参数变化率 |
| 第 $k$ 个轮速 | $\omega_k$ | 第 $k$ 个车轮实际自转角速度 |
| 第 $k$ 个参考轮速 | $\omega_k^{\mathrm{ref}}$ | 运动学模型输出 |
| 六轮实际轮速 | $\boldsymbol\omega_K$ | 六个车轮实际角速度向量 |
| 六轮参考轮速 | $\boldsymbol\omega_K^{\mathrm{ref}}$ | 六个车轮参考角速度向量 |
| 第 $k$ 个轮半径 | $R_k$ | 车轮有效半径 |
| 第 $k$ 个轮心位置 | ${}^B\mathbf p_k$ | 轮心在中模块坐标系下的位置 |
| 第 $k$ 个轮滚动方向 | ${}^B\mathbf t_k$ | 轮胎滚动方向单位向量 |
| 轮心位置雅可比 | ${}^B\mathbf J_{p,k}(\mathbf q)$ | $\partial{}^B\mathbf p_k/\partial\mathbf q$ |
| 速度到轮速映射 | $\mathbf J_{\omega v}(\mathbf q)$ | $\boldsymbol\nu_B^{\mathrm{cmd}}\rightarrow\boldsymbol\omega_K^{\mathrm{ref}}$ |
| 球铰变化到轮速映射 | $\mathbf J_{\omega q}(\mathbf q)$ | $\dot{\mathbf q}^{\mathrm{ref}}\rightarrow\boldsymbol\omega_K^{\mathrm{ref}}$ |
| 纵向滑移率 | $\kappa_k$ | 第 $k$ 个车轮纵向滑移 |
| 侧偏角 | $\alpha_k$ | 第 $k$ 个车轮侧向滑移 |
| 法向接触力 | $F_{z,k}$ | 第 $k$ 个轮子的法向力 |
| 轮胎纵向力 | ${}^{T_k}F_{x,k}$ | 轮胎坐标系下纵向力 |
| 轮胎侧向力 | ${}^{T_k}F_{y,k}$ | 轮胎坐标系下侧向力 |
| 车轮驱动力矩 | $\tau_k$ | 第 $k$ 个轮子的驱动输入 |
| 车轮转动惯量 | $I_k$ | 第 $k$ 个车轮等效转动惯量 |
| 球铰驱动力矩 | $\tau_{q,j}$ | 第 $j$ 个球铰自由度执行力矩 |
| 球铰等效惯量 | $I_{q,j}$ | 第 $j$ 个球铰自由度等效转动惯量 |
| 整车质量 | $m$ | 三模块总等效质量 |
| 绕 $z_B$ 轴等效转动惯量 | $I_z$ | 对应 $\omega_z$ |
| 动力学参数集合 | $\mathcal P_{\mathrm{dyn}}$ | 质量、惯量、阻尼、轮胎参数等 |
| 地形接触信息 | $\mathcal H$ | 高度、摩擦系数、接触状态、法向力等 |

---

# 15. 最终建议

按照你的偏好，最合适的核心符号体系是：

$$
\mathbf q
$$

表示球铰节间姿态；

$$
\omega_z
$$

表示中模块绕自身 $z_B$ 轴角速度；

$$
\omega_k
$$

表示第 $k$ 个车轮自转角速度；

$$
\boldsymbol\omega_K
$$

表示六轮角速度向量；

$$
\boldsymbol\omega_K^{\mathrm{ref}}
$$

表示运动学模型输出的六轮参考角速度。

最终控制链路可以统一写成：

$$
\mathbf a_{\mathrm{RL}}
=
\begin{bmatrix}
v_x^{\mathrm{cmd}} &
\omega_z^{\mathrm{cmd}} &
\left(\mathbf q^{\mathrm{ref}}\right)^T
\end{bmatrix}^T,
$$

$$
\boldsymbol\omega_K^{\mathrm{ref}}
=
\mathbf J_{\omega v}(\mathbf q)\boldsymbol\nu_B^{\mathrm{cmd}}
+
\mathbf J_{\omega q}(\mathbf q)\dot{\mathbf q}^{\mathrm{ref}},
$$

$$
\mathbf x=
\begin{bmatrix}
v_x &
v_y &
\omega_z &
\boldsymbol\omega_K^T &
\mathbf q^T &
\dot{\mathbf q}^T
\end{bmatrix}^T.
$$

这套符号既保留了你认为直观的 $\mathbf q$ 和 $\omega_z$，又避免了车轮索引 $w$ 与轮速符号混杂的问题。
