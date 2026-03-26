
```matlab
%% 清理环境
clear; clc;

fprintf('=== 3-RRR 球面并联机构逆运动学推导（修正版，可对应论文式(9)-(13)）===\n\n');
```

```matlabTextOutput
=== 3-RRR 球面并联机构逆运动学推导（修正版，可对应论文式(9)-(13)）===
```

```matlab

%% 1) 符号变量
% 机构参数
syms eta gamma alpha1 alpha2 beta real

% 主动关节角 theta_i
syms theta_i real

% 平台姿态角：theta=roll, phi=pitch, psi=yaw
syms theta phi psi real

% 用于半角代换: t = tan(theta_i/2)
syms t real

% 先把 v_i 视为已知分量（这样才能得到论文式(10)-(12) 风格）
syms vix viy viz real

% 统一化简器
simp = @(expr) simplify(expand(expr), ...
    'Steps', 100, ...
    'IgnoreAnalyticConstraints', true);

%% 2) 旋转矩阵（列向量、右手系）
Rx = @(ang) [1, 0, 0;
             0, cos(ang), -sin(ang);
             0, sin(ang),  cos(ang)];

Ry = @(ang) [ cos(ang), 0, sin(ang);
              0,        1, 0;
             -sin(ang), 0, cos(ang)];

Rz = @(ang) [cos(ang), -sin(ang), 0;
             sin(ang),  cos(ang), 0;
             0,         0,        1];

ex = sym([1;0;0]);

%% 3) u_i：对应论文式(1)(2)
R01 = simp(Rz(eta + pi/2) * Ry(pi/2 - gamma));
disp('R01 =');
```

```matlabTextOutput
R01 =
```

```matlab
disp(R01);
```
 $\displaystyle \left(\begin{array}{ccc} -\sin \left(\eta \right)\,\sin \left(\gamma \right) & -\cos \left(\eta \right) & -\cos \left(\gamma \right)\,\sin \left(\eta \right)\newline \cos \left(\eta \right)\,\sin \left(\gamma \right) & -\sin \left(\eta \right) & \cos \left(\eta \right)\,\cos \left(\gamma \right)\newline -\cos \left(\gamma \right) & 0 & \sin \left(\gamma \right) \end{array}\right)$
 

```matlab

u_i = simp(R01(:,1));   % x-axis
disp('u_i =');
```

```matlabTextOutput
u_i =
```

```matlab
disp(u_i);
```
 $\displaystyle \left(\begin{array}{c} -\sin \left(\eta \right)\,\sin \left(\gamma \right)\newline \cos \left(\eta \right)\,\sin \left(\gamma \right)\newline -\cos \left(\gamma \right) \end{array}\right)$
 

```matlab

%% 4) w_i：按你修正后的方式
% 先绕局部 x 轴转 theta_i，再绕更新后的局部 z 轴转 alpha1
R_local = simp(Rx(theta_i) * Rz(alpha1));
disp('R_local =');
```

```matlabTextOutput
R_local =
```

```matlab
disp(R_local);
```
 $\displaystyle \left(\begin{array}{ccc} \cos \left(\alpha_1 \right) & -\sin \left(\alpha_1 \right) & 0\newline \sin \left(\alpha_1 \right)\,\cos \left(\theta_i \right) & \cos \left(\alpha_1 \right)\,\cos \left(\theta_i \right) & -\sin \left(\theta_i \right)\newline \sin \left(\alpha_1 \right)\,\sin \left(\theta_i \right) & \cos \left(\alpha_1 \right)\,\sin \left(\theta_i \right) & \cos \left(\theta_i \right) \end{array}\right)$
 

```matlab

R_w = simp(R01 * R_local);
disp('R_w =');
```

```matlabTextOutput
R_w =
```

```matlab
disp(R_w);
```
 $\displaystyle \left(\begin{array}{ccc} -\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta_i \right)-\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)-\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\theta_i \right) & \sin \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)-\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\theta_i \right)-\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)\,\sin \left(\eta \right)\,\sin \left(\theta_i \right) & \cos \left(\eta \right)\,\sin \left(\theta_i \right)-\cos \left(\gamma \right)\,\cos \left(\theta_i \right)\,\sin \left(\eta \right)\newline \cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)-\sin \left(\alpha_1 \right)\,\cos \left(\theta_i \right)\,\sin \left(\eta \right)+\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\theta_i \right) & \cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\theta_i \right)-\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\gamma \right)-\cos \left(\alpha_1 \right)\,\cos \left(\theta_i \right)\,\sin \left(\eta \right) & \sin \left(\eta \right)\,\sin \left(\theta_i \right)+\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\theta_i \right)\newline \sin \left(\alpha_1 \right)\,\sin \left(\gamma \right)\,\sin \left(\theta_i \right)-\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right) & \cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)+\cos \left(\alpha_1 \right)\,\sin \left(\gamma \right)\,\sin \left(\theta_i \right) & \cos \left(\theta_i \right)\,\sin \left(\gamma \right) \end{array}\right)$
 

```matlab

w_i = simp(R_w(:,1));   % x-axis
disp('w_i =');
```

```matlabTextOutput
w_i =
```

```matlab
disp(w_i);
```
 $\displaystyle \left(\begin{array}{c} -\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta_i \right)-\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)-\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\theta_i \right)\newline \cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)-\sin \left(\alpha_1 \right)\,\cos \left(\theta_i \right)\,\sin \left(\eta \right)+\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\theta_i \right)\newline \sin \left(\alpha_1 \right)\,\sin \left(\gamma \right)\,\sin \left(\theta_i \right)-\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right) \end{array}\right)$
 

```matlab

%% 5) v_i 的两种写法
% 5.1 论文式(10)-(12)风格：先把 v_i 看成已知分量
v_i_sym = [vix; viy; viz];
disp('v_i_sym =');
```

```matlabTextOutput
v_i_sym =
```

```matlab
disp(v_i_sym);
```
 $\displaystyle \left(\begin{array}{c} \textrm{vix}\newline \textrm{viy}\newline \textrm{viz} \end{array}\right)$
 

```matlab

% 5.2 你的真实平台姿态写法（后面再代入）
R03 = simp(Rz(eta + 5*pi/6) * Ry(beta - pi/2));   % 150° = 5*pi/6
disp('R03 (corrected) =');
```

```matlabTextOutput
R03 (corrected) =
```

```matlab
disp(R03);
```
 $\displaystyle \left(\begin{array}{ccc} -\sin \left(\beta \right)\,\sin \left(\eta +\frac{\pi }{3}\right) & -\cos \left(\eta +\frac{\pi }{3}\right) & \cos \left(\beta \right)\,\sin \left(\eta +\frac{\pi }{3}\right)\newline \sin \left(\beta \right)\,\cos \left(\eta +\frac{\pi }{3}\right) & -\sin \left(\eta +\frac{\pi }{3}\right) & -\cos \left(\beta \right)\,\cos \left(\eta +\frac{\pi }{3}\right)\newline \cos \left(\beta \right) & 0 & \sin \left(\beta \right) \end{array}\right)$
 

```matlab

R_rpy = simp(Rz(psi) * Ry(phi) * Rx(theta));
disp('R_rpy =');
```

```matlabTextOutput
R_rpy =
```

```matlab
disp(R_rpy);
```
 $\displaystyle \left(\begin{array}{ccc} \cos \left(\phi \right)\,\cos \left(\psi \right) & \cos \left(\psi \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)-\cos \left(\theta \right)\,\sin \left(\psi \right) & \sin \left(\psi \right)\,\sin \left(\theta \right)+\cos \left(\psi \right)\,\cos \left(\theta \right)\,\sin \left(\phi \right)\newline \cos \left(\phi \right)\,\sin \left(\psi \right) & \cos \left(\psi \right)\,\cos \left(\theta \right)+\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right) & \cos \left(\theta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)-\cos \left(\psi \right)\,\sin \left(\theta \right)\newline -\sin \left(\phi \right) & \cos \left(\phi \right)\,\sin \left(\theta \right) & \cos \left(\phi \right)\,\cos \left(\theta \right) \end{array}\right)$
 

```matlab

R_v = simp(R_rpy * R03);
disp('R_v =');
```

```matlabTextOutput
R_v =
```

```matlab
disp(R_v);
```
 $\displaystyle \left(\begin{array}{ccc} \cos \left(\beta \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)+\cos \left(\beta \right)\,\cos \left(\psi \right)\,\cos \left(\theta \right)\,\sin \left(\phi \right)-\frac{\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)}{2}-\frac{\cos \left(\eta \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)}{2}+\frac{\sqrt{3}\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}+\frac{\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2} & \frac{\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}-\frac{\cos \left(\eta \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)}{2}+\frac{\sqrt{3}\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\eta \right)}{2}+\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\theta \right)\,\sin \left(\psi \right)}{2}-\frac{\cos \left(\psi \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2} & \sin \left(\beta \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)+\frac{\cos \left(\beta \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\eta \right)}{2}+\frac{\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\theta \right)\,\sin \left(\psi \right)}{2}+\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\phi \right)-\frac{\sqrt{3}\,\cos \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}-\frac{\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}+\frac{\sqrt{3}\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)}{2}+\frac{\sqrt{3}\,\cos \left(\beta \right)\,\cos \left(\psi \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}\newline \frac{\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)}{2}-\cos \left(\beta \right)\,\cos \left(\psi \right)\,\sin \left(\theta \right)+\cos \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)-\frac{\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)}{2}+\frac{\cos \left(\eta \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2} & \frac{\sqrt{3}\,\cos \left(\phi \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}-\frac{\cos \left(\psi \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\cos \left(\theta \right)}{2}-\frac{\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\psi \right)}{2}-\frac{\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2} & \frac{\cos \left(\beta \right)\,\cos \left(\phi \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}-\frac{\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\cos \left(\theta \right)}{2}-\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\theta \right)+\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)+\frac{\sqrt{3}\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\psi \right)}{2}+\frac{\sqrt{3}\,\cos \left(\beta \right)\,\cos \left(\psi \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)}{2}-\frac{\cos \left(\beta \right)\,\cos \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}+\frac{\sqrt{3}\,\cos \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}\newline \cos \left(\beta \right)\,\cos \left(\phi \right)\,\cos \left(\theta \right)+\frac{\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)}{2}+\frac{\sqrt{3}\,\cos \left(\eta \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)}{2}+\frac{\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\theta \right)}{2} & \frac{\cos \left(\eta \right)\,\sin \left(\phi \right)}{2}-\frac{\sqrt{3}\,\sin \left(\eta \right)\,\sin \left(\phi \right)}{2}-\frac{\cos \left(\phi \right)\,\sin \left(\eta \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\theta \right)}{2} & \cos \left(\phi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)-\frac{\cos \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)}{2}-\frac{\sqrt{3}\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\sin \left(\phi \right)}{2}-\frac{\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\theta \right)}{2}+\frac{\sqrt{3}\,\cos \left(\beta \right)\,\cos \left(\phi \right)\,\sin \left(\eta \right)\,\sin \left(\theta \right)}{2} \end{array}\right)$
 

```matlab

v_i_full = simp(R_v(:,1));   % 真正展开后的 v_i
disp('v_i_full =');
```

```matlabTextOutput
v_i_full =
```

```matlab
disp(v_i_full);
```
 $\displaystyle \left(\begin{array}{c} \cos \left(\beta \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)+\cos \left(\beta \right)\,\cos \left(\psi \right)\,\cos \left(\theta \right)\,\sin \left(\phi \right)-\frac{\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)}{2}-\frac{\cos \left(\eta \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)}{2}+\frac{\sqrt{3}\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}+\frac{\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}\newline \frac{\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)}{2}-\cos \left(\beta \right)\,\cos \left(\psi \right)\,\sin \left(\theta \right)+\cos \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)-\frac{\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)}{2}+\frac{\cos \left(\eta \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}\newline \cos \left(\beta \right)\,\cos \left(\phi \right)\,\cos \left(\theta \right)+\frac{\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)}{2}+\frac{\sqrt{3}\,\cos \left(\eta \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)}{2}+\frac{\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\theta \right)}{2} \end{array}\right)$
 

```matlab

%% 6) 核心约束：w_i · v_i = cos(alpha2)
% 先用 v_i_sym 推导，得到论文风格 A,B,C
constraint_eq = simp(dot(w_i, v_i_sym) - cos(alpha2));
disp('constraint_eq =');
```

```matlabTextOutput
constraint_eq =
```

```matlab
disp(constraint_eq);
```
 $\displaystyle \textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)-\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)-\cos \left(\alpha_2 \right)-\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta_i \right)-\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)-\textrm{viy}\,\sin \left(\alpha_1 \right)\,\cos \left(\theta_i \right)\,\sin \left(\eta \right)+\textrm{viz}\,\sin \left(\alpha_1 \right)\,\sin \left(\gamma \right)\,\sin \left(\theta_i \right)+\textrm{viy}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\theta_i \right)-\textrm{vix}\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\theta_i \right)$
 

```matlab

%% 7) 先整理成 a*sin(theta_i) + b*cos(theta_i) + d = 0
% 方法：把 sin(theta_i), cos(theta_i) 视为独立基
d_term = simp(subs(constraint_eq, ...
    [sin(theta_i), cos(theta_i)], ...
    [0, 0]));

a_term = simp(subs(constraint_eq, ...
    [sin(theta_i), cos(theta_i)], ...
    [1, 0]) - d_term);

b_term = simp(subs(constraint_eq, ...
    [sin(theta_i), cos(theta_i)], ...
    [0, 1]) - d_term);

constraint_scd = simp(a_term*sin(theta_i) + b_term*cos(theta_i) + d_term);

disp('a_term ='); disp(a_term);
```

```matlabTextOutput
a_term =
```

 $\displaystyle \sin \left(\alpha_1 \right)\,{\left(\textrm{viz}\,\sin \left(\gamma \right)+\textrm{viy}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)-\textrm{vix}\,\cos \left(\gamma \right)\,\sin \left(\eta \right)\right)}$
 

```matlab
disp('b_term ='); disp(b_term);
```

```matlabTextOutput
b_term =
```

 $\displaystyle -\sin \left(\alpha_1 \right)\,{\left(\textrm{vix}\,\cos \left(\eta \right)+\textrm{viy}\,\sin \left(\eta \right)\right)}$
 

```matlab
disp('d_term ='); disp(d_term);
```

```matlabTextOutput
d_term =
```

 $\displaystyle \textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)-\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)-\cos \left(\alpha_2 \right)-\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)$
 

```matlab
disp('constraint_scd =');disp(constraint_scd);
```

```matlabTextOutput
constraint_scd =
```

 $\displaystyle \textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)-\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)-\cos \left(\alpha_2 \right)-\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta_i \right)-\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)-\textrm{viy}\,\sin \left(\alpha_1 \right)\,\cos \left(\theta_i \right)\,\sin \left(\eta \right)+\textrm{viz}\,\sin \left(\alpha_1 \right)\,\sin \left(\gamma \right)\,\sin \left(\theta_i \right)+\textrm{viy}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\theta_i \right)-\textrm{vix}\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\theta_i \right)$
 

```matlab
disp('check constraint_eq - constraint_scd =');
```

```matlabTextOutput
check constraint_eq - constraint_scd =
```

```matlab
disp(simp(constraint_eq - constraint_scd));
```
 $\displaystyle 0$
 

```matlab

%% 8) 半角代换：t = tan(theta_i/2)
% sin(theta_i) = 2t/(1+t^2), cos(theta_i) = (1-t^2)/(1+t^2)
constraint_t = subs(constraint_scd, ...
    [sin(theta_i), cos(theta_i)], ...
    [2*t/(1+t^2), (1-t^2)/(1+t^2)]);
constraint_t = simp(constraint_t);

disp('constraint_t =');
```

```matlabTextOutput
constraint_t =
```

```matlab
disp(constraint_t);
```
 $\displaystyle \textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)-\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)-\frac{\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)}{t^2 +1}-\frac{\textrm{viy}\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)}{t^2 +1}-\cos \left(\alpha_2 \right)-\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)+\frac{2\,t\,\textrm{viz}\,\sin \left(\alpha_1 \right)\,\sin \left(\gamma \right)}{t^2 +1}+\frac{t^2 \,\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)}{t^2 +1}+\frac{t^2 \,\textrm{viy}\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)}{t^2 +1}+\frac{2\,t\,\textrm{viy}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)}{t^2 +1}-\frac{2\,t\,\textrm{vix}\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)}{t^2 +1}$
 

```matlab

%% 9) 两边乘 (1+t^2)，整理成二次式
poly_eq = simp(expand((1 + t^2) * constraint_t));
poly_eq = collect(poly_eq, t);
poly_eq = simp(poly_eq);

disp('poly_eq =');
```

```matlabTextOutput
poly_eq =
```

```matlab
disp(poly_eq);
```
 $\displaystyle \textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)-t^2 \,\cos \left(\alpha_2 \right)-\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)-\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)-\textrm{viy}\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)-t^2 \,\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)-\cos \left(\alpha_2 \right)+t^2 \,\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)-\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)+t^2 \,\textrm{viy}\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)+2\,t\,\textrm{viz}\,\sin \left(\alpha_1 \right)\,\sin \left(\gamma \right)+t^2 \,\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)-t^2 \,\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)+2\,t\,\textrm{viy}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)-2\,t\,\textrm{vix}\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)$
 

```matlab

%% 10) 提取 A, B, C
coef_all = coeffs(poly_eq, t, 'All');
coef_all = simp(coef_all);

% 对二次式 A*t^2 + B*t + C
if numel(coef_all) ~= 3
    error('提取到的系数个数不是 3，请检查 poly_eq 是否确实是二次多项式。');
end

A_derived = simp(coef_all(1));
B_derived = simp(coef_all(2));
C_derived = simp(coef_all(3));

disp('[A, B, C] =');
```

```matlabTextOutput
[A, B, C] =
```

```matlab
disp(coef_all);
```
 $\displaystyle \begin{array}{l} \left(\begin{array}{ccc} \sigma_4 -\sigma_5 -\cos \left(\alpha_2 \right)+\sigma_3 +\sigma_2 -\sigma_1  & 2\,\sin \left(\alpha_1 \right)\,{\left(\textrm{viz}\,\sin \left(\gamma \right)+\textrm{viy}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)-\textrm{vix}\,\cos \left(\gamma \right)\,\sin \left(\eta \right)\right)} & \sigma_2 -\sigma_5 -\sigma_4 -\sigma_3 -\cos \left(\alpha_2 \right)-\sigma_1  \end{array}\right)\\\mathrm{}\\\textrm{where}\\\mathrm{}\\\;\;\sigma_1 =\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\\\mathrm{}\\\;\;\sigma_2 =\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)\\\mathrm{}\\\;\;\sigma_3 =\textrm{viy}\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)\\\mathrm{}\\\;\;\sigma_4 =\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\\\mathrm{}\\\;\;\sigma_5 =\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)\end{array}$
 

```matlab

disp('二次项系数 A =');
```

```matlabTextOutput
二次项系数 A =
```

```matlab
disp(A_derived);
```
 $\displaystyle \textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)-\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)-\cos \left(\alpha_2 \right)+\textrm{viy}\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)+\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)-\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)$
 

```matlab
disp('一次项系数 B =');
```

```matlabTextOutput
一次项系数 B =
```

```matlab
disp(B_derived);
```
 $\displaystyle 2\,\sin \left(\alpha_1 \right)\,{\left(\textrm{viz}\,\sin \left(\gamma \right)+\textrm{viy}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)-\textrm{vix}\,\cos \left(\gamma \right)\,\sin \left(\eta \right)\right)}$
 

```matlab
disp('常数项系数 C =');
```

```matlabTextOutput
常数项系数 C =
```

```matlab
disp(C_derived);
```
 $\displaystyle \textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)-\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)-\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)-\textrm{viy}\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)-\cos \left(\alpha_2 \right)-\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)$
 

```matlab

%% 11) 验证 poly_eq = A*t^2 + B*t + C
check_poly = simp(poly_eq - (A_derived*t^2 + B_derived*t + C_derived));
disp('check poly_eq - (A*t^2 + B*t + C) =');
```

```matlabTextOutput
check poly_eq - (A*t^2 + B*t + C) =
```

```matlab
disp(check_poly);
```
 $\displaystyle 0$
 

```matlab

%% 12) 论文式(13)对应的求解
Delta = simp(B_derived^2 - 4*A_derived*C_derived);

t_sol_1 = simp((-B_derived + sqrt(Delta)) / (2*A_derived));
t_sol_2 = simp((-B_derived - sqrt(Delta)) / (2*A_derived));

theta_i_sol_1 = simp(2 * atan(t_sol_1));
theta_i_sol_2 = simp(2 * atan(t_sol_2));

% 更稳健的 atan2 形式
theta_i_sol_1_atan2 = simp(2 * atan2(-B_derived + sqrt(Delta), 2*A_derived));
theta_i_sol_2_atan2 = simp(2 * atan2(-B_derived - sqrt(Delta), 2*A_derived));

disp('Delta =');
```

```matlabTextOutput
Delta =
```

```matlab
disp(Delta);
```
 $\displaystyle -4\,{\textrm{vix}}^2 \,{\cos \left(\alpha_1 \right)}^2 -4\,{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 +4\,{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 +4\,{\textrm{vix}}^2 \,{\cos \left(\gamma \right)}^2 -8\,\sin \left(\eta \right)\,\textrm{vix}\,\textrm{viy}\,\cos \left(\eta \right)\,{\cos \left(\gamma \right)}^2 +4\,\sin \left(2\,\eta \right)\,\textrm{vix}\,\textrm{viy}-8\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\textrm{viz}\,\cos \left(\gamma \right)-8\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)-4\,{\textrm{viy}}^2 \,{\cos \left(\alpha_1 \right)}^2 +4\,{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 -4\,{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 +4\,{\textrm{viy}}^2 +8\,\sin \left(\gamma \right)\,\textrm{viy}\,\textrm{viz}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)+8\,\sin \left(\gamma \right)\,\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\eta \right)-4\,{\textrm{viz}}^2 \,{\cos \left(\alpha_1 \right)}^2 -4\,{\textrm{viz}}^2 \,{\cos \left(\gamma \right)}^2 +4\,{\textrm{viz}}^2 -8\,\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\gamma \right)-4\,{\cos \left(\alpha_2 \right)}^2 $
 

```matlab

disp('t_sol_1 =');
```

```matlabTextOutput
t_sol_1 =
```

```matlab
disp(t_sol_1);
```
 $\displaystyle \begin{array}{l} -\frac{\sigma_1 }{\sigma_2 }-\frac{\sqrt{-{\textrm{vix}}^2 \,{\cos \left(\alpha_1 \right)}^2 -{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 +{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 +{\textrm{vix}}^2 \,{\cos \left(\gamma \right)}^2 -2\,\sin \left(\eta \right)\,\textrm{vix}\,\textrm{viy}\,\cos \left(\eta \right)\,{\cos \left(\gamma \right)}^2 +\sin \left(2\,\eta \right)\,\textrm{vix}\,\textrm{viy}-2\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\textrm{viz}\,\cos \left(\gamma \right)-2\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)-{\textrm{viy}}^2 \,{\cos \left(\alpha_1 \right)}^2 +{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 -{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 +{\textrm{viy}}^2 +2\,\sin \left(\gamma \right)\,\textrm{viy}\,\textrm{viz}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)+2\,\sin \left(\gamma \right)\,\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\eta \right)-{\textrm{viz}}^2 \,{\cos \left(\alpha_1 \right)}^2 -{\textrm{viz}}^2 \,{\cos \left(\gamma \right)}^2 +{\textrm{viz}}^2 -2\,\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\gamma \right)-{\cos \left(\alpha_2 \right)}^2 }-\frac{\sigma_1 \,{\left(\cos \left(\alpha_2 \right)+\sigma_5 -\sigma_4 +\sigma_3 \right)}}{\sigma_2 }}{\cos \left(\alpha_2 \right)+\sigma_5 -\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)-\textrm{viy}\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)-\sigma_4 +\sigma_3 }\newline \mathrm{}\newline \textrm{where}\newline \mathrm{}\newline \;\;\sigma_1 =\textrm{viz}\,\sin \left(\gamma \right)+\textrm{viy}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)-\textrm{vix}\,\cos \left(\gamma \right)\,\sin \left(\eta \right)\newline \mathrm{}\newline \;\;\sigma_2 =\textrm{vix}\,\cos \left(\eta \right)+\textrm{viy}\,\sin \left(\eta \right)\newline \mathrm{}\newline \;\;\sigma_3 =\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\newline \mathrm{}\newline \;\;\sigma_4 =\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)\newline \mathrm{}\newline \;\;\sigma_5 =\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right) \end{array}$
 

```matlab
disp('t_sol_2 =');
```

```matlabTextOutput
t_sol_2 =
```

```matlab
disp(t_sol_2);
```
 $\displaystyle \begin{array}{l} \frac{\sqrt{-{\textrm{vix}}^2 \,{\cos \left(\alpha_1 \right)}^2 -{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 +{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 +{\textrm{vix}}^2 \,{\cos \left(\gamma \right)}^2 -2\,\sin \left(\eta \right)\,\textrm{vix}\,\textrm{viy}\,\cos \left(\eta \right)\,{\cos \left(\gamma \right)}^2 +\sin \left(2\,\eta \right)\,\textrm{vix}\,\textrm{viy}-2\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\textrm{viz}\,\cos \left(\gamma \right)-2\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)-{\textrm{viy}}^2 \,{\cos \left(\alpha_1 \right)}^2 +{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 -{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 +{\textrm{viy}}^2 +2\,\sin \left(\gamma \right)\,\textrm{viy}\,\textrm{viz}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)+2\,\sin \left(\gamma \right)\,\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\eta \right)-{\textrm{viz}}^2 \,{\cos \left(\alpha_1 \right)}^2 -{\textrm{viz}}^2 \,{\cos \left(\gamma \right)}^2 +{\textrm{viz}}^2 -2\,\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\gamma \right)-{\cos \left(\alpha_2 \right)}^2 }+\frac{\sigma_1 \,{\left(\cos \left(\alpha_2 \right)+\sigma_5 -\sigma_4 +\sigma_3 \right)}}{\sigma_2 }}{\cos \left(\alpha_2 \right)+\sigma_5 -\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)-\textrm{viy}\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)-\sigma_4 +\sigma_3 }-\frac{\sigma_1 }{\sigma_2 }\newline \mathrm{}\newline \textrm{where}\newline \mathrm{}\newline \;\;\sigma_1 =\textrm{viz}\,\sin \left(\gamma \right)+\textrm{viy}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)-\textrm{vix}\,\cos \left(\gamma \right)\,\sin \left(\eta \right)\newline \mathrm{}\newline \;\;\sigma_2 =\textrm{vix}\,\cos \left(\eta \right)+\textrm{viy}\,\sin \left(\eta \right)\newline \mathrm{}\newline \;\;\sigma_3 =\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\newline \mathrm{}\newline \;\;\sigma_4 =\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)\newline \mathrm{}\newline \;\;\sigma_5 =\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right) \end{array}$
 

```matlab

disp('theta_i_sol_1 =');
```

```matlabTextOutput
theta_i_sol_1 =
```

```matlab
disp(theta_i_sol_1);
```
 $\displaystyle -2\,\textrm{atan}\left(\frac{\sqrt{-{\textrm{vix}}^2 \,{\cos \left(\alpha_1 \right)}^2 -{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 +{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 +{\textrm{vix}}^2 \,{\cos \left(\gamma \right)}^2 -2\,\sin \left(\eta \right)\,\textrm{vix}\,\textrm{viy}\,\cos \left(\eta \right)\,{\cos \left(\gamma \right)}^2 +\sin \left(2\,\eta \right)\,\textrm{vix}\,\textrm{viy}-2\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\textrm{viz}\,\cos \left(\gamma \right)-2\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)-{\textrm{viy}}^2 \,{\cos \left(\alpha_1 \right)}^2 +{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 -{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 +{\textrm{viy}}^2 +2\,\sin \left(\gamma \right)\,\textrm{viy}\,\textrm{viz}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)+2\,\sin \left(\gamma \right)\,\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\eta \right)-{\textrm{viz}}^2 \,{\cos \left(\alpha_1 \right)}^2 -{\textrm{viz}}^2 \,{\cos \left(\gamma \right)}^2 +{\textrm{viz}}^2 -2\,\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\gamma \right)-{\cos \left(\alpha_2 \right)}^2 }-\textrm{viz}\,\sin \left(\alpha_1 \right)\,\sin \left(\gamma \right)-\textrm{viy}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)+\textrm{vix}\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)}{\cos \left(\alpha_2 \right)+\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)-\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)-\textrm{viy}\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)-\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)+\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)}\right)$
 

```matlab
disp('theta_i_sol_2 =');
```

```matlabTextOutput
theta_i_sol_2 =
```

```matlab
disp(theta_i_sol_2);
```
 $\displaystyle 2\,\textrm{atan}\left(\frac{\sqrt{-{\textrm{vix}}^2 \,{\cos \left(\alpha_1 \right)}^2 -{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 +{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 +{\textrm{vix}}^2 \,{\cos \left(\gamma \right)}^2 -2\,\sin \left(\eta \right)\,\textrm{vix}\,\textrm{viy}\,\cos \left(\eta \right)\,{\cos \left(\gamma \right)}^2 +\sin \left(2\,\eta \right)\,\textrm{vix}\,\textrm{viy}-2\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\textrm{viz}\,\cos \left(\gamma \right)-2\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)-{\textrm{viy}}^2 \,{\cos \left(\alpha_1 \right)}^2 +{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 -{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 +{\textrm{viy}}^2 +2\,\sin \left(\gamma \right)\,\textrm{viy}\,\textrm{viz}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)+2\,\sin \left(\gamma \right)\,\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\eta \right)-{\textrm{viz}}^2 \,{\cos \left(\alpha_1 \right)}^2 -{\textrm{viz}}^2 \,{\cos \left(\gamma \right)}^2 +{\textrm{viz}}^2 -2\,\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\gamma \right)-{\cos \left(\alpha_2 \right)}^2 }+\textrm{viz}\,\sin \left(\alpha_1 \right)\,\sin \left(\gamma \right)+\textrm{viy}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)-\textrm{vix}\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)}{\cos \left(\alpha_2 \right)+\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)-\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)-\textrm{viy}\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)-\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)+\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)}\right)$
 

```matlab

disp('theta_i_sol_1_atan2 =');
```

```matlabTextOutput
theta_i_sol_1_atan2 =
```

```matlab
disp(theta_i_sol_1_atan2);
```
 $\displaystyle 2\,\textrm{atan2}\left(2\,\sqrt{-{\textrm{vix}}^2 \,{\cos \left(\alpha_1 \right)}^2 -{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 +{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 +{\textrm{vix}}^2 \,{\cos \left(\gamma \right)}^2 -2\,\sin \left(\eta \right)\,\textrm{vix}\,\textrm{viy}\,\cos \left(\eta \right)\,{\cos \left(\gamma \right)}^2 +\sin \left(2\,\eta \right)\,\textrm{vix}\,\textrm{viy}-2\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\textrm{viz}\,\cos \left(\gamma \right)-2\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)-{\textrm{viy}}^2 \,{\cos \left(\alpha_1 \right)}^2 +{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 -{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 +{\textrm{viy}}^2 +2\,\sin \left(\gamma \right)\,\textrm{viy}\,\textrm{viz}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)+2\,\sin \left(\gamma \right)\,\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\eta \right)-{\textrm{viz}}^2 \,{\cos \left(\alpha_1 \right)}^2 -{\textrm{viz}}^2 \,{\cos \left(\gamma \right)}^2 +{\textrm{viz}}^2 -2\,\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\gamma \right)-{\cos \left(\alpha_2 \right)}^2 }-2\,\textrm{viz}\,\sin \left(\alpha_1 \right)\,\sin \left(\gamma \right)-2\,\textrm{viy}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)+2\,\textrm{vix}\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right),2\,\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)-2\,\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)-2\,\cos \left(\alpha_2 \right)+2\,\textrm{viy}\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)+2\,\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)-2\,\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\right)$
 

```matlab
disp('theta_i_sol_2_atan2 =');
```

```matlabTextOutput
theta_i_sol_2_atan2 =
```

```matlab
disp(theta_i_sol_2_atan2);
```
 $\displaystyle 2\,\textrm{atan2}\left(2\,\textrm{vix}\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)-2\,\textrm{viz}\,\sin \left(\alpha_1 \right)\,\sin \left(\gamma \right)-2\,\textrm{viy}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)-2\,\sqrt{-{\textrm{vix}}^2 \,{\cos \left(\alpha_1 \right)}^2 -{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 +{\textrm{vix}}^2 \,{\cos \left(\eta \right)}^2 +{\textrm{vix}}^2 \,{\cos \left(\gamma \right)}^2 -2\,\sin \left(\eta \right)\,\textrm{vix}\,\textrm{viy}\,\cos \left(\eta \right)\,{\cos \left(\gamma \right)}^2 +\sin \left(2\,\eta \right)\,\textrm{vix}\,\textrm{viy}-2\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\textrm{viz}\,\cos \left(\gamma \right)-2\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\textrm{vix}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)-{\textrm{viy}}^2 \,{\cos \left(\alpha_1 \right)}^2 +{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 \,{\cos \left(\gamma \right)}^2 -{\textrm{viy}}^2 \,{\cos \left(\eta \right)}^2 +{\textrm{viy}}^2 +2\,\sin \left(\gamma \right)\,\textrm{viy}\,\textrm{viz}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)+2\,\sin \left(\gamma \right)\,\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\eta \right)-{\textrm{viz}}^2 \,{\cos \left(\alpha_1 \right)}^2 -{\textrm{viz}}^2 \,{\cos \left(\gamma \right)}^2 +{\textrm{viz}}^2 -2\,\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\alpha_2 \right)\,\cos \left(\gamma \right)-{\cos \left(\alpha_2 \right)}^2 },2\,\textrm{vix}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)-2\,\textrm{viz}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)-2\,\cos \left(\alpha_2 \right)+2\,\textrm{viy}\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)+2\,\textrm{viy}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\gamma \right)-2\,\textrm{vix}\,\cos \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\right)$
 

```matlab

%% 13) 第二步：把真实的 v_i_full 代回 A,B,C
A_full = simp(subs(A_derived, [vix, viy, viz], transpose(v_i_full)));
B_full = simp(subs(B_derived, [vix, viy, viz], transpose(v_i_full)));
C_full = simp(subs(C_derived, [vix, viy, viz], transpose(v_i_full)));

disp('A_full (substitute v_i_full) =');
```

```matlabTextOutput
A_full (substitute v_i_full) =
```

```matlab
disp(A_full);
```
 $\displaystyle \cos \left(\beta \right)\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)-\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\cos \left(\theta \right)-\frac{\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)}{2}-\cos \left(\alpha_2 \right)-\cos \left(\beta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\theta \right)-\frac{{\cos \left(\eta \right)}^2 \,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\psi \right)}{2}-\frac{\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,{\sin \left(\eta \right)}^2 \,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,{\cos \left(\eta \right)}^2 \,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)}{2}-\frac{\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\theta \right)}{2}-\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\gamma \right)\,\sin \left(\theta \right)-\frac{\sqrt{3}\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,{\sin \left(\eta \right)}^2 }{2}+\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta \right)\,\sin \left(\phi \right)-\frac{\cos \left(\eta \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)}{2}+\frac{\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)}{2}-\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)+\cos \left(\beta \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)+\frac{\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)}{2}+\frac{\cos \left(\alpha_1 \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,{\sin \left(\eta \right)}^2 \,\sin \left(\gamma \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)}{2}+\frac{{\cos \left(\eta \right)}^2 \,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,{\sin \left(\eta \right)}^2 \,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}+\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)-\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\psi \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)-\frac{\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}+\frac{\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,{\sin \left(\eta \right)}^2 \,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}+\frac{\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}+\frac{\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}+\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}+\frac{\sqrt{3}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}+\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,{\sin \left(\eta \right)}^2 \,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}-\frac{\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}+\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)}{2}-\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}$
 

```matlab
disp('B_full (substitute v_i_full) =');
```

```matlabTextOutput
B_full (substitute v_i_full) =
```

```matlab
disp(B_full);
```
 $\displaystyle \sin \left(\alpha_1 \right)\,{\left(2\,\cos \left(\beta \right)\,\cos \left(\phi \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)+\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)+\sqrt{3}\,\cos \left(\eta \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)-2\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\psi \right)\,\sin \left(\theta \right)+\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\theta \right)-2\,\cos \left(\beta \right)\,\cos \left(\gamma \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)+{\cos \left(\eta \right)}^2 \,\cos \left(\gamma \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)+\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,{\sin \left(\eta \right)}^2 -\sqrt{3}\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\theta \right)-\sqrt{3}\,{\cos \left(\eta \right)}^2 \,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\psi \right)-\sqrt{3}\,\cos \left(\gamma \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,{\sin \left(\eta \right)}^2 \,\sin \left(\psi \right)+2\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\theta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)-2\,\cos \left(\beta \right)\,\cos \left(\gamma \right)\,\cos \left(\psi \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)-\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)+\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)+{\cos \left(\eta \right)}^2 \,\cos \left(\gamma \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)+\sqrt{3}\,\cos \left(\gamma \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,{\sin \left(\eta \right)}^2 \,\sin \left(\phi \right)\,\sin \left(\theta \right)-\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)+\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)-\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)-\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)\right)}$
 

```matlab
disp('C_full (substitute v_i_full) =');
```

```matlabTextOutput
C_full (substitute v_i_full) =
```

```matlab
disp(C_full);
```
 $\displaystyle \cos \left(\beta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\theta \right)-\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\cos \left(\theta \right)-\frac{\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)}{2}-\cos \left(\beta \right)\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)-\cos \left(\alpha_2 \right)+\frac{{\cos \left(\eta \right)}^2 \,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\psi \right)}{2}+\frac{\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,{\sin \left(\eta \right)}^2 \,\sin \left(\psi \right)}{2}+\frac{\sqrt{3}\,{\cos \left(\eta \right)}^2 \,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)}{2}-\frac{\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\theta \right)}{2}-\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\gamma \right)\,\sin \left(\theta \right)+\frac{\sqrt{3}\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,{\sin \left(\eta \right)}^2 }{2}-\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta \right)\,\sin \left(\phi \right)+\frac{\cos \left(\eta \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)}{2}-\frac{\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)}{2}-\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)-\cos \left(\beta \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)+\frac{\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)}{2}+\frac{\cos \left(\alpha_1 \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,{\sin \left(\eta \right)}^2 \,\sin \left(\gamma \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)}{2}-\frac{{\cos \left(\eta \right)}^2 \,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,{\sin \left(\eta \right)}^2 \,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}+\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)-\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\psi \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)-\frac{\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}+\frac{\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}+\frac{\sqrt{3}\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,{\sin \left(\eta \right)}^2 \,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}-\frac{\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}+\frac{\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}+\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\theta \right)}{2}+\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}+\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,{\sin \left(\eta \right)}^2 \,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}-\frac{\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}+\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)}{2}+\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}$
 

```matlab

%% 14) 再用 full 形式验证一次
constraint_eq_full = simp(dot(w_i, v_i_full) - cos(alpha2));
poly_eq_full = simp(subs(A_full*t^2 + B_full*t + C_full, t, t));

constraint_t_full = subs(constraint_eq_full, ...
    [sin(theta_i), cos(theta_i)], ...
    [2*t/(1+t^2), (1-t^2)/(1+t^2)]);
constraint_t_full = simp(constraint_t_full);

poly_eq_full_from_constraint = simp(expand((1+t^2) * constraint_t_full));
poly_eq_full_from_constraint = collect(poly_eq_full_from_constraint, t);
poly_eq_full_from_constraint = simp(poly_eq_full_from_constraint);

disp('poly_eq_full_from_constraint =');
```

```matlabTextOutput
poly_eq_full_from_constraint =
```

```matlab
disp(poly_eq_full_from_constraint);
```
 $\displaystyle \frac{\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\psi \right)}{2}-t^2 \,\cos \left(\alpha_2 \right)-\cos \left(\alpha_2 \right)+\frac{\sqrt{3}\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)}{2}-\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\cos \left(\theta \right)+\frac{\cos \left(\alpha_1 \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)}{2}-\frac{\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)}{2}-\cos \left(\beta \right)\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)+\cos \left(\beta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\theta \right)-\frac{t^2 \,\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\psi \right)}{2}-\frac{{\cos \left(\eta \right)}^2 \,\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\psi \right)}{2}+\frac{{\cos \left(\eta \right)}^2 \,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\psi \right)}{2}+t\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)+\frac{\sqrt{3}\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}-t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\cos \left(\theta \right)+\frac{\sqrt{3}\,{\cos \left(\eta \right)}^2 \,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)}{2}-\frac{\sqrt{3}\,{\cos \left(\eta \right)}^2 \,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)}{2}-\frac{\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\theta \right)}{2}-\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\gamma \right)\,\sin \left(\theta \right)+\frac{t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)}{2}-\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta \right)\,\sin \left(\phi \right)+\frac{\cos \left(\eta \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)}{2}-\frac{t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)}{2}-\frac{\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)}{2}+t^2 \,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)-t^2 \,\cos \left(\beta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\theta \right)-\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)-\cos \left(\beta \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)-\frac{\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)}{2}+\frac{\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)}{2}+\frac{t^2 \,{\cos \left(\eta \right)}^2 \,\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\psi \right)}{2}-\frac{t^2 \,{\cos \left(\eta \right)}^2 \,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)}{2}-\frac{{\cos \left(\eta \right)}^2 \,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,t^2 \,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}+t\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)+2\,t\,\cos \left(\beta \right)\,\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)-\frac{\sqrt{3}\,t^2 \,{\cos \left(\eta \right)}^2 \,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)}{2}+\frac{\sqrt{3}\,t^2 \,{\cos \left(\eta \right)}^2 \,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}+\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}-t\,{\cos \left(\eta \right)}^2 \,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)-\frac{t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\theta \right)}{2}+t\,{\cos \left(\eta \right)}^2 \,\cos \left(\gamma \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)-t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\gamma \right)\,\sin \left(\theta \right)+t^2 \,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta \right)\,\sin \left(\phi \right)-\frac{t^2 \,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)}{2}+\frac{t^2 \,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)}{2}+\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)-\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\psi \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)-\frac{\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}+\frac{\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}-t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)-\frac{\sqrt{3}\,{\cos \left(\eta \right)}^2 \,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}+t^2 \,\cos \left(\beta \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)-\frac{\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}-\sqrt{3}\,t\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\psi \right)+\sqrt{3}\,t\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)-\frac{t^2 \,\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)}{2}+\frac{t^2 \,\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)}{2}-\frac{\sqrt{3}\,t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)}{2}+\frac{t^2 \,{\cos \left(\eta \right)}^2 \,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}+\frac{\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}+\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\theta \right)}{2}-2\,t\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\theta \right)+\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,t^2 \,\cos \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}+\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}+t\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\theta \right)-2\,t\,\cos \left(\beta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)-\frac{\sqrt{3}\,t^2 \,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}+t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)-t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\beta \right)\,\cos \left(\psi \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)-\frac{t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}+\frac{t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}+\frac{\sqrt{3}\,t^2 \,{\cos \left(\eta \right)}^2 \,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}-\frac{\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}+t\,{\cos \left(\eta \right)}^2 \,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)+\frac{t^2 \,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}+\sqrt{3}\,t\,\cos \left(\gamma \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)-\sqrt{3}\,t\,\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\theta \right)+\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)}{2}+\frac{t^2 \,\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)}{2}-\sqrt{3}\,t\,{\cos \left(\eta \right)}^2 \,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\psi \right)+\frac{\sqrt{3}\,t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\theta \right)}{2}+\sqrt{3}\,t\,{\cos \left(\eta \right)}^2 \,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\psi \right)-\frac{\sqrt{3}\,t^2 \,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}+\frac{\sqrt{3}\,t^2 \,\cos \left(\eta \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)}{2}+2\,t\,\cos \left(\beta \right)\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)-2\,t\,\cos \left(\beta \right)\,\cos \left(\gamma \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)-t\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)+t\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\psi \right)+\frac{\sqrt{3}\,t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}+\frac{\sqrt{3}\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,t^2 \,\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\cos \left(\phi \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}+\frac{\sqrt{3}\,t^2 \,\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\gamma \right)\,\sin \left(\psi \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}+\frac{\sqrt{3}\,t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)}{2}-\frac{\sqrt{3}\,t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)}{2}-\sqrt{3}\,t\,{\cos \left(\eta \right)}^2 \,\cos \left(\gamma \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)-\frac{\sqrt{3}\,t^2 \,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}-\frac{\sqrt{3}\,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}-t\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)-\frac{\sqrt{3}\,t^2 \,\cos \left(\alpha_1 \right)\,{\cos \left(\eta \right)}^2 \,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}-\frac{t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\cos \left(\psi \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\theta \right)}{2}+\sqrt{3}\,t\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\phi \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)-\sqrt{3}\,t\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\cos \left(\psi \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\cos \left(\theta \right)\,\sin \left(\eta \right)-\frac{\sqrt{3}\,t^2 \,\cos \left(\alpha_1 \right)\,\cos \left(\eta \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\gamma \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)}{2}-\sqrt{3}\,t\,\cos \left(\eta \right)\,\cos \left(\gamma \right)\,\sin \left(\alpha_1 \right)\,\sin \left(\beta \right)\,\sin \left(\eta \right)\,\sin \left(\phi \right)\,\sin \left(\psi \right)\,\sin \left(\theta \right)$
 

```matlab

disp('check full polynomial consistency =');
```

```matlabTextOutput
check full polynomial consistency =
```

```matlab
disp(simp(poly_eq_full_from_constraint - poly_eq_full));
```
 $\displaystyle 0$
 

```matlab

fprintf('\n=== 推导完成 ===\n');
```

```matlabTextOutput
=== 推导完成 ===
```

```matlab
fprintf('说明：\n');
```

```matlabTextOutput
说明：
```

```matlab
fprintf('1) A_derived, B_derived, C_derived 是论文式(10)-(12)风格；\n');
```

```matlabTextOutput
1) A_derived, B_derived, C_derived 是论文式(10)-(12)风格；
```

```matlab
fprintf('2) A_full, B_full, C_full 是把真实 v_i_full 代回后的完整表达；\n');
```

```matlabTextOutput
2) A_full, B_full, C_full 是把真实 v_i_full 代回后的完整表达；
```

```matlab
fprintf('3) theta_i_sol_1/2 对应论文式(13)的两组解。\n');
```

```matlabTextOutput
3) theta_i_sol_1/2 对应论文式(13)的两组解。
```

```matlab

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 15) 数值赋值（按论文参数）
fprintf('\n=== 数值验证：代入论文参数 ===\n');
```

```matlabTextOutput
=== 数值验证：代入论文参数 ===
```

```matlab

deg = @(x) x*pi/180;

alpha1_num = deg(90);
alpha2_num = deg(90);
beta_num   = deg(54.75);
gamma_num  = deg(54.75);

% 三条支链的 eta_i
eta_list = [deg(0), deg(120), deg(240)];

% 这里先取 home 姿态作为示例
% 你后面可以改成任意目标姿态
theta_num = deg(0);   % roll
phi_num   = deg(0);   % pitch
psi_num   = deg(0);   % yaw

fprintf('使用姿态: roll = %.2f deg, pitch = %.2f deg, yaw = %.2f deg\n', ...
    theta_num*180/pi, phi_num*180/pi, psi_num*180/pi);
```

```matlabTextOutput
使用姿态: roll = 0.00 deg, pitch = 0.00 deg, yaw = 0.00 deg
```

```matlab

for k = 1:3
    eta_num = eta_list(k);

    % 代入真实 v_i_full 到 A_full, B_full, C_full
    A_num = double(subs(A_full, ...
        [alpha1, alpha2, beta, gamma, eta, theta, phi, psi], ...
        [alpha1_num, alpha2_num, beta_num, gamma_num, eta_num, theta_num, phi_num, psi_num]));

    B_num = double(subs(B_full, ...
        [alpha1, alpha2, beta, gamma, eta, theta, phi, psi], ...
        [alpha1_num, alpha2_num, beta_num, gamma_num, eta_num, theta_num, phi_num, psi_num]));

    C_num = double(subs(C_full, ...
        [alpha1, alpha2, beta, gamma, eta, theta, phi, psi], ...
        [alpha1_num, alpha2_num, beta_num, gamma_num, eta_num, theta_num, phi_num, psi_num]));

    Delta_num = B_num^2 - 4*A_num*C_num;

    fprintf('\n--- Leg %d ---\n', k);
    fprintf('eta_%d = %.2f deg\n', k, eta_num*180/pi);
    fprintf('A = %.12f\n', A_num);
    fprintf('B = %.12f\n', B_num);
    fprintf('C = %.12f\n', C_num);
    fprintf('Delta = %.12f\n', Delta_num);

    if Delta_num < 0
        fprintf('该支链无实数解（当前姿态不可达）\n');
        continue;
    end

    t1 = (-B_num + sqrt(Delta_num)) / (2*A_num);
    t2 = (-B_num - sqrt(Delta_num)) / (2*A_num);

    theta_i_1 = 2*atan(t1);
    theta_i_2 = 2*atan(t2);

    fprintf('t1 = %.12f\n', t1);
    fprintf('t2 = %.12f\n', t2);
    fprintf('theta_i^(1) = %.12f rad = %.6f deg\n', theta_i_1, theta_i_1*180/pi);
    fprintf('theta_i^(2) = %.12f rad = %.6f deg\n', theta_i_2, theta_i_2*180/pi);

    % 代回原始约束检查残差
    res1 = double(subs(constraint_eq_full, ...
        [alpha1, alpha2, beta, gamma, eta, theta, phi, psi, theta_i], ...
        [alpha1_num, alpha2_num, beta_num, gamma_num, eta_num, theta_num, phi_num, psi_num, theta_i_1]));

    res2 = double(subs(constraint_eq_full, ...
        [alpha1, alpha2, beta, gamma, eta, theta, phi, psi, theta_i], ...
        [alpha1_num, alpha2_num, beta_num, gamma_num, eta_num, theta_num, phi_num, psi_num, theta_i_2]));

    fprintf('residual(theta_i^(1)) = %.3e\n', res1);
    fprintf('residual(theta_i^(2)) = %.3e\n', res2);
end
```

```matlabTextOutput
--- Leg 1 ---
eta_1 = 0.00 deg
A = -0.707232332556
B = 1.413962236638
C = 0.707232332556
Delta = 3.999999495490
t1 = -0.414317622553
t2 = 2.413607207530
theta_i^(1) = -0.785575798700 rad = -45.010178 deg
theta_i^(2) = 2.356016854890 rad = 134.989822 deg
residual(theta_i^(1)) = -4.692e-17
residual(theta_i^(2)) = -5.266e-17
--- Leg 2 ---
eta_2 = 120.00 deg
A = -0.707232332556
B = 1.413962236638
C = 0.707232332556
Delta = 3.999999495490
t1 = -0.414317622553
t2 = 2.413607207530
theta_i^(1) = -0.785575798700 rad = -45.010178 deg
theta_i^(2) = 2.356016854890 rad = 134.989822 deg
residual(theta_i^(1)) = -4.692e-17
residual(theta_i^(2)) = -5.266e-17
--- Leg 3 ---
eta_3 = 240.00 deg
A = -0.707232332556
B = 1.413962236638
C = 0.707232332556
Delta = 3.999999495490
t1 = -0.414317622553
t2 = 2.413607207530
theta_i^(1) = -0.785575798700 rad = -45.010178 deg
theta_i^(2) = 2.356016854890 rad = 134.989822 deg
residual(theta_i^(1)) = -4.692e-17
residual(theta_i^(2)) = -5.266e-17
```


