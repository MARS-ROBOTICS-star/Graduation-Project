# Kinematic Reference Vectors

在默认装配姿态下，取 `body_car_chassis` 的质心为中车参考点，所有可动关节角均为零。以下向量均以米为单位。

记：

- `spm1` 等效关节中心为前球铰中心；
- `spm2` 等效关节中心为后球铰中心；
- 下标 `1,2,3` 分别对应前车、中车、后车；
- `L,R` 分别表示左轮和右轮。

## 1. `head_car_chassis` 与 `tail_car_chassis` 质心相对平台坐标

`head_car_chassis` 质心相对 `spm1_platform` 坐标系的坐标为

$$
{}^{\mathrm{spm1\_platform}}\mathbf{p}_{c_1}
=
\begin{bmatrix}
0.30654739 \\
0.00427533 \\
0.00609283
\end{bmatrix} .
$$

`tail_car_chassis` 质心相对 `spm2_platform` 坐标系的坐标为

$$
{}^{\mathrm{spm2\_platform}}\mathbf{p}_{c_3}
=
\begin{bmatrix}
-0.30633826 \\
0.00427687 \\
0.00609283
\end{bmatrix} .
$$

## 2. 以 `body_car_chassis` 质心为参考原点

前、后等效关节中心分别记为 $\mathbf{a}_1$ 与 $\mathbf{a}_3$，则有

$$
\mathbf{a}_1
=
\begin{bmatrix}
0.25633374 \\
-0.00614478 \\
0.01121736
\end{bmatrix} ,
\qquad
\mathbf{a}_3
=
\begin{bmatrix}
-0.25631226 \\
-0.00614478 \\
0.01121736
\end{bmatrix} .
$$

中车左、右轮坐标分别记为 $\mathbf{r}_{2L}$ 与 $\mathbf{r}_{2R}$，则有

$$
\mathbf{r}_{2L}
=
\begin{bmatrix}
0.00000932 \\
0.21754506 \\
-0.02578188
\end{bmatrix} ,
\qquad
\mathbf{r}_{2R}
=
\begin{bmatrix}
0.00000932 \\
-0.22983462 \\
-0.02578188
\end{bmatrix} .
$$

## 3. 以 `head_car_chassis` 质心为参考原点

前等效关节中心坐标记为 $\mathbf{b}_1$，则有

$$
\mathbf{b}_1
=
\begin{bmatrix}
-0.30654739 \\
-0.00428771 \\
-0.00608413
\end{bmatrix} .
$$

前车左、右轮坐标分别记为 $\mathbf{r}_{1L}$ 与 $\mathbf{r}_{1R}$，则有

$$
\mathbf{r}_{1L}
=
\begin{bmatrix}
-0.00989449 \\
0.21932649 \\
-0.04353780
\end{bmatrix} ,
\qquad
\mathbf{r}_{1R}
=
\begin{bmatrix}
-0.00989449 \\
-0.22805226 \\
-0.04262877
\end{bmatrix} .
$$

## 4. 以 `tail_car_chassis` 质心为参考原点

后等效关节中心坐标记为 $\mathbf{b}_3$，则有

$$
\mathbf{b}_3
=
\begin{bmatrix}
0.30633826 \\
-0.00426448 \\
-0.00610151
\end{bmatrix} .
$$

后车左、右轮坐标分别记为 $\mathbf{r}_{3L}$ 与 $\mathbf{r}_{3R}$，则有

$$
\mathbf{r}_{3L}
=
\begin{bmatrix}
0.00968251 \\
0.21950007 \\
-0.04264614
\end{bmatrix} ,
\qquad
\mathbf{r}_{3R}
=
\begin{bmatrix}
0.00968251 \\
-0.22787868 \\
-0.04355517
\end{bmatrix} .
$$

## 5. 汇总

为便于后续建模，上述关键向量可整理为

$$
\mathbf{a}_1=
\begin{bmatrix}
0.25633374 \\
-0.00614478 \\
0.01121736
\end{bmatrix},
\quad
\mathbf{a}_3=
\begin{bmatrix}
-0.25631226 \\
-0.00614478 \\
0.01121736
\end{bmatrix},
$$

$$
\mathbf{b}_1=
\begin{bmatrix}
-0.30654739 \\
-0.00428771 \\
-0.00608413
\end{bmatrix},
\quad
\mathbf{b}_3=
\begin{bmatrix}
0.30633826 \\
-0.00426448 \\
-0.00610151
\end{bmatrix},
$$

$$
\mathbf{r}_{1L}=
\begin{bmatrix}
-0.00989449 \\
0.21932649 \\
-0.04353780
\end{bmatrix},
\quad
\mathbf{r}_{1R}=
\begin{bmatrix}
-0.00989449 \\
-0.22805226 \\
-0.04262877
\end{bmatrix},
$$

$$
\mathbf{r}_{2L}=
\begin{bmatrix}
0.00000932 \\
0.21754506 \\
-0.02578188
\end{bmatrix},
\quad
\mathbf{r}_{2R}=
\begin{bmatrix}
0.00000932 \\
-0.22983462 \\
-0.02578188
\end{bmatrix},
$$

$$
\mathbf{r}_{3L}=
\begin{bmatrix}
0.00968251 \\
0.21950007 \\
-0.04264614
\end{bmatrix},
\quad
\mathbf{r}_{3R}=
\begin{bmatrix}
0.00968251 \\
-0.22787868 \\
-0.04355517
\end{bmatrix}.
$$
