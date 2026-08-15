# Stage1 球铰直接目标 PD 控制与 MATLAB 预仿真方案

## 0. 2026-05-10 修订说明

本文件说明底层控制链路的总体修改方案。MATLAB 实验执行细节已单独拆到 `docs/Stage1球铰PD控制MATLAB真实轨迹仿真实验方案.md`。

2026-05-10 追加落地状态：当前源码已按扩展真实轨迹扫参结论采用 `Kp=120, Kd=10, tau_v=0.04 s`，并将 active 链路改为 `q_target = clamp(q^d)` 与 `qdot_alloc = LPF(qdot_actual)`；旧的 actual-pos-based `q + dt*qdot_cmd` 一阶规划器不再参与 Stage0 / Stage1 训练链路。

当前修订后的 MATLAB 原则为：

- 优先使用 IsaacLab 真实 policy 逐 control step 轨迹，而不是只用人工阶跃。
- 第一版球铰 PD 增益采用统一 $K_p,K_d$，不做分关节 gain。
- MATLAB 时间步按当前源码 `control.sim_dt = 1/120 s`、`control.control_dt = 1/60 s`，不沿用旧的 `1/240 s` 假设。

## 1. 目标和边界

本方案解决的是当前 Stage1 的一个底层执行链路问题：

> policy 后 6 维已经能给出较大的球铰目标姿态，但修改前的一阶球铰规划器把 `desired_target` 削弱成贴近 `actual_pos` 的 `position_target`，导致球铰姿态没有真正按 policy 意图参与台阶 / 离散障碍爬越。

本方案不重新设计 action 语义，不加入 `front_pitch_ref` 动作先验，不改变 Stage1 地形、reward、curriculum 的研究含义。它只改变底层执行链路：

- 球铰位置目标直接来自 policy 映射后的 $q^d$。
- 轮速分配所需的球铰姿态变化率从实际关节速度滤波得到。
- 通过 MATLAB 预仿真选择球铰 PD 参数和滤波参数，再进入 Isaac Sim 短回放验证。

当前用户已明确要求 Stage0 / Stage1 底层机器人配置一致，因此后续所有球铰和车轮底层参数必须在 Stage0、Stage1 和 Base 配置中同步。

## 2. 当前源码事实

当前 active 代码链路如下。

| 模块 | 当前作用 |
|---|---|
| `mdp/actions.py` | `map_ball_joint_actions_to_desired_positions()` 将 action 后 6 维映射为球铰目标姿态 $q^d$ |
| `base/env.py` | `_pre_physics_step()` 中生成 `desired_ball_joint_targets`，再调用 allocator |
| `kinematics/wheel_speed_allocator.py` | `compute_low_slip_control_targets()` 内部调用 `compute_ball_joint_command_outputs()`，直接生成 `q_target` 并使用 env 传入的 `qdot_alloc` |
| `assets/actuators_cfg.py` | 用 `ImplicitActuatorCfg` 构造球铰 position drive 和车轮 actuator |

修改前旧球铰规划器为：

$$
\dot q_{\mathrm{cmd}}
=
\operatorname{clip}
\left(
K(q^d-q),
-\dot q_{\max},
\dot q_{\max}
\right)
$$

$$
q_{\mathrm{cmd}}
=
\operatorname{clip}
\left(
q+\Delta t_c\dot q_{\mathrm{cmd}},
q_{\mathrm{lower}},
q_{\mathrm{upper}}
\right)
$$

其中：

- $q^d$ 是 policy action 映射后的目标姿态。
- $q$ 是 Isaac 当前球铰实际角度。
- $q_{\mathrm{cmd}}$ 是最终下发给 `set_joint_position_target()` 的目标。
- $\dot q_{\mathrm{cmd}}$ 还被传给 low-slip 整形和 wheel speed reference，用于计算 $\mathbf G_j\dot q$。

这正是当前问题的来源：`position_target` 每步都从 `actual_pos` 附近小步积分出来，而不是直接表达 policy 想要的姿态。

当前落地后的统一底层参数为：

| 参数 | 当前值 |
|---|---:|
| `ball_joint_stiffness` | `120.0 N*m/rad` |
| `ball_joint_damping` | `10.0 N*m*s/rad` |
| `ball_joint_effort_limit_sim` | `60.0 N*m` |
| `ball_joint_velocity_limit_sim` | `2.0 rad/s` |
| `ball_joint_qdot_alloc_filter_tau_s` | `0.04 s` |
| `wheel_joint_effort_limit_sim` | `20.0 N*m` |
| `low_slip_lambda_lateral` | `5.0` |
| `wheel_slip_feedback_gain` | `4.0` |

外部建议中提到的 Stage0 `8000 / 1000 / 20` 和 Stage1 `1000 / 10 / 20` 已不是当前源码口径。当前 direct-target 短验证以 `120 / 10 / 60` 作为真实起点，旧 `1000 / 10 / 60` 只作为 MATLAB 压力测试基线。

## 3. 核心修改原则

旧链路：

```text
policy action
  -> q_desired
  -> qdot_cmd = clip(K * (q_desired - q_actual))
  -> q_cmd = q_actual + dt * qdot_cmd
  -> set_joint_position_target(q_cmd)

same qdot_cmd
  -> low-slip command shaping
  -> wheel speed reference
```

新链路：

```text
policy action
  -> q_desired
  -> q_target = clamp(q_desired, q_lower, q_upper)
  -> set_joint_position_target(q_target)

qdot_actual
  -> qdot_alloc = LPF(qdot_actual)
  -> low-slip command shaping
  -> wheel speed reference
```

关键区别：

$$
q_{\mathrm{target}}
\neq
q+\Delta t_c\dot q_{\mathrm{cmd}}
$$

而是：

$$
q_{\mathrm{target}}
=
\operatorname{clip}
\left(
q^d,
q_{\mathrm{lower}},
q_{\mathrm{upper}}
\right)
$$

第一版不直接给球铰下发 `set_joint_velocity_target()`。原因是当前 `ImplicitActuatorCfg` 已有 `stiffness` 和 `damping`，球铰不是纯 P 控制；如果只下发 position target，PhysX drive 的直观等效形式为：

$$
\tau_{\mathrm{raw}}
=
K_p(q_{\mathrm{target}}-q)
-
K_d\dot q
$$

这里 D 项作用在角速度上，用于抑制运动；它不是“姿态加速度”。如果后续要显式使用速度目标，应作为单独实验，而不是第一版直接混入主线。

## 4. 为什么不继续用旧 $\dot q_{\mathrm{cmd}}$

轮速分配中的轮心名义速度包含：

$$
\mathbf v_j^{\mathrm{nom}}
=
v_x^*\mathbf e_x
+
\omega_z^*(\mathbf e_z\times\mathbf p_j)
+
\mathbf G_j\dot{\mathbf q}
$$

其中 $\mathbf G_j\dot{\mathbf q}$ 表示球铰实际转动对轮心速度的贡献。

如果删除旧位置规划器，但继续使用：

$$
\dot q_{\mathrm{alloc}}
=
\operatorname{clip}
\left(
K(q^d-q),
-\dot q_{\max},
\dot q_{\max}
\right)
$$

那只是把旧 planner 的速度假设留在 allocator 里。它不一定等于真实球铰速度，可能导致轮速参考提前或过度补偿。

第一版更合理的定义是：

$$
\dot q_{\mathrm{alloc},k}
=
(1-\alpha_v)\dot q_{\mathrm{alloc},k-1}
+
\alpha_v\dot q_{\mathrm{actual},k}
$$

$$
\alpha_v
=
1-\exp
\left(
-\frac{\Delta t_c}{\tau_v}
\right)
$$

再限幅：

$$
\dot q_{\mathrm{alloc}}
\leftarrow
\operatorname{clip}
\left(
\dot q_{\mathrm{alloc}},
-2.0,
2.0
\right)
$$

建议第一版：

| 参数 | 建议值 |
|---|---:|
| `ball_joint_alloc_velocity_filter_tau_s` | `0.05 s` |
| `ball_joint_alloc_velocity_limit_radps` | `2.0 rad/s` |

这样 $\mathbf G_j\dot{\mathbf q}$ 描述的是实际球铰运动导致的轮心速度，而不是 policy target 的数学跳变。

## 5. 第一版代码落地方案

### 5.1 配置字段

`ControlCfg` 中建议移除 active path 对旧 planner 参数的依赖。新增字段：

```python
ball_joint_alloc_velocity_filter_tau_s: float = 0.05
ball_joint_alloc_velocity_limit_radps: float = 2.0
```

第一版球铰 gain 采用统一标量，不按关节分别设置：

```python
ball_joint_stiffness: float = Kp
ball_joint_damping: float = Kd
```

这样可以保持 Stage0 / Stage1 底层配置简单一致。Isaac Lab 虽然支持 `dict[str, float]` 形式的分关节 gain，但本轮不采用；只有在统一增益经过真实轨迹和 Isaac 短验证证明存在明确不可调和的单轴问题后，再单独讨论是否引入分轴增益。

### 5.2 `env.py` 修改点

当前 `_pre_physics_step()` 中的核心调用应从：

```python
low_level_outputs = allocator.compute_low_slip_control_targets(
    ball_joint_pos=ball_joint_pos,
    desired_ball_joint_pos=desired_ball_joint_targets,
    ball_joint_rate_targets=qdot_alloc,
    ...
)
```

改为：

```python
q_target = torch.clamp(
    desired_ball_joint_targets,
    min=ball_joint_lower_limits_tensor,
    max=ball_joint_upper_limits_tensor,
)

qdot_alloc = self._update_ball_joint_alloc_velocity(
    qdot_actual=self.robot.data.joint_vel[:, self._ball_joint_ids],
)

low_level_outputs = allocator.compute_low_slip_control_targets(
    ball_joint_pos=ball_joint_pos,
    desired_ball_joint_pos=desired_ball_joint_targets,
    ball_joint_rate_targets=qdot_alloc,
    desired_planar_command=planar_command,
    ...
)

self._joint_pos_targets = apply_ball_joint_position_targets(
    self._joint_pos_targets,
    self._ball_joint_ids,
    q_target,
)
```

新增 env 状态：

```python
self._ball_joint_alloc_rate_targets = torch.zeros((self.num_envs, 6), device=self.device)
```

滤波函数：

```python
def _update_ball_joint_alloc_velocity(self, qdot_actual: torch.Tensor) -> torch.Tensor:
    tau = max(float(self.cfg.control.ball_joint_alloc_velocity_filter_tau_s), 1.0e-6)
    alpha = 1.0 - math.exp(-float(self.cfg.control.control_dt) / tau)
    self._ball_joint_alloc_rate_targets.lerp_(qdot_actual, alpha)
    limit = float(self.cfg.control.ball_joint_alloc_velocity_limit_radps)
    self._ball_joint_alloc_rate_targets.clamp_(min=-limit, max=limit)
    return self._ball_joint_alloc_rate_targets
```

reset 时必须同步：

```python
self._ball_joint_alloc_rate_targets[env_ids] = 0.0
self._last_ball_joint_rate_targets[env_ids] = 0.0
```

否则 reset 后第一步会把旧 episode 的速度状态带入新 episode。

### 5.3 `wheel_speed_allocator.py` 修改点

当前 `compute_low_slip_control_targets()` 同时负责：

1. 生成球铰位置目标；
2. 生成球铰速度；
3. 低滑移整形；
4. 轮速参考；
5. 车轮力矩。

新结构应把第 1、2 项移出 allocator。allocator 只接收：

```python
ball_joint_pos
ball_joint_rate_targets
desired_planar_command
wheel_normal_contact_force
wheel_joint_vel
rolling_speed_actual
lateral_speed_actual
...
```

并直接把 `ball_joint_rate_targets` 传入：

- `shape_planar_command_for_low_slip()`
- `compute_wheel_speed_references()`

`compute_ball_joint_planner_outputs()` 已从 active 代码中移除，当前对应接口为 `compute_ball_joint_command_outputs()`。

### 5.4 `validate_wheel_speed_allocator.py` 和测试

当前 `validate_wheel_speed_allocator.py` 已改为测试 direct target 和显式 `ball_joint_rate_targets` 输入：

- `ball_joint_rate_targets=0` 时，静态目标和纯前进 wheel speed reference 保持可校验。
- `compute_ball_joint_command_outputs()` 只负责把 $q^d$ 限幅为 $q_{target}$，不再按实际位置积分。
- zero contact、forward command、traction target 等测试继续保留。

必须跑：

```text
python3 -m py_compile <changed python files>
python3 RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/validate_wheel_speed_allocator.py --run-smoke-cases
python3 RL_Training/tests/test_stage1_curriculum.py
python3 RL_Training/tests/test_stage1_eval_metrics.py
python3 RL_Training/tests/test_terrain_features.py
```

## 6. 是否需要 command-side target filter

第一版不加 target filter：

$$
q_{\mathrm{target}}=q^d
$$

如果短回放发现 policy 输出高频抖动，再加入 command-side 低通，而不是恢复旧的 actual-pos-based planner。

滤波形式：

$$
q_{\mathrm{ref},k}
=
(1-\alpha_q)q_{\mathrm{ref},k-1}
+
\alpha_q q^d_k
$$

$$
\alpha_q
=
1-\exp
\left(
-\frac{\Delta t_c}{\tau_q}
\right)
$$

建议扫描：

| 参数 | 范围 |
|---|---:|
| $\tau_q$ | `0, 0.03, 0.05, 0.08 s` |

这个滤波只抑制 policy target 高频噪声。它不依赖 actual position，因此不会把目标压回当前实际角度附近。

## 7. PD 参数的重新理解

当前 `ball_joint_stiffness=1000`、`ball_joint_damping=10`、`effort_limit=60` 在旧 planner 下能稳定，是因为旧 planner 让 `position_target - actual_pos` 很小。

如果直接下发 $q^d$，误差可能达到 `0.2 rad`。此时名义 P 项为：

$$
\tau_P=1000\times0.2=200\ \mathrm{N*m}
$$

但当前 effort limit 为 `60 N*m`，所以大误差阶段会饱和。饱和不一定错误，但如果长期饱和，会产生 bang-bang 响应、速度限幅、接触扰动和球铰高频抖动。

因此 MATLAB 预仿真必须覆盖三组参数族：

| 参数族 | 含义 | 用途 |
|---|---|---|
| Low-gain | 接近外部建议的 `120 / 160 / 100` | 检查低增益是否太慢 |
| Mid-gain | 让 `0.2 rad` 误差产生约 `40-60 N*m` | 当前 `effort=60` 下的主候选 |
| Current-stress | 当前 `1000 / 10 / 60` | 检查直接 target 后饱和风险 |

第一版不要直接把 `effort_limit_sim` 改回 `20`。用户已明确统一为 `60`，MATLAB 也应以 `60` 为主线固定值。

## 8. MATLAB 单关节模型

预仿真不追求完整三节车接触动力学，只用于筛掉明显不稳定或长期饱和的 PD 参数。

单轴模型：

$$
J\ddot q
=
\tau
-
B\dot q
-
\tau_{\mathrm{load}}
$$

PD drive：

$$
\tau_{\mathrm{raw}}
=
K_p(q_{\mathrm{target}}-q)
-
K_d\dot q
$$

力矩限幅：

$$
\tau
=
\operatorname{clip}
\left(
\tau_{\mathrm{raw}},
-\tau_{\max},
\tau_{\max}
\right)
$$

速度限制：

$$
\dot q
\leftarrow
\operatorname{clip}
\left(
\dot q,
-\dot q_{\max},
\dot q_{\max}
\right)
$$

如果忽略被动阻尼 $B$，二阶系统近似关系为：

$$
K_p=J\omega_n^2
$$

$$
K_d=2\zeta J\omega_n
$$

建议阻尼比和闭环频率：

| 参数 | 建议范围 |
|---|---:|
| $\zeta$ | `0.9 ~ 1.3` |
| $\omega_n$ | `10 ~ 18 rad/s` |

这对应约 `1.6 ~ 2.9 Hz` 的闭环频率，对 `60 Hz` 控制周期较安全。

## 9. MATLAB 扫参范围

未知等效惯量：

```text
J = 0.03, 0.05, 0.10, 0.20, 0.40 kg*m^2
```

固定限制：

```text
tau_max = 60 N*m
qdot_max = 2 rad/s
dt_ctrl = 1/60 s
dt_sim = 1/120 s
```

统一增益候选：

| 类型 | 统一候选 |
|---|---:|
| 低增益 | `Kp=120,160,220; Kd=10,16,24` |
| 中增益 | `Kp=320,500; Kd=24,32,48` |
| 压力测试 | `Kp=800,1000; Kd=10,32,64` |

第一版不做分关节增益。所有 `spm*_platform_joint_[xyz]` 使用同一组 $K_p,K_d$，这样 MATLAB 结果可以直接对应 IsaacLab 里的统一底层配置。只有当统一增益在真实轨迹和 Isaac 短验证中暴露出明确的单轴不可调和问题，才重新讨论分轴增益。

command-side target filter 扫描：

```text
tau_cmd = 0, 0.03, 0.05, 0.08 s
```

allocator 速度滤波扫描：

```text
tau_v = 0.03, 0.05, 0.08 s
```

外部负载：

```text
tau_load = -15, -10, -5, 0, 5, 10, 15 N*m
```

## 10. MATLAB 输入轨迹

必须优先测试 IsaacLab 真实策略轨迹；人工轨迹只用于 sanity check 和压力测试。

| 轨迹 | 数值 | 目的 |
|---|---|---|
| 真实 policy 轨迹 | 从 IsaacLab 回放逐 control step 导出 `q_desired`、`q_actual`、`qdot_actual` | 主测试输入，判断真实策略动作在 direct-target PD 下是否可跟踪 |
| 真实地形片段 | flat、stairs_down、discrete obstacles 的典型片段 | 检查不同地形动作幅值、频率和饱和占比 |
| 小阶跃 | `0 -> 0.05 rad` | 检查小动作是否过阻尼或死区明显 |
| 中阶跃 | `0 -> 0.20 rad` | 对应当前典型 `desired - actual` 量级 |
| 大阶跃 | `0 -> 0.50 rad` | 检查限位附近是否长期饱和 |
| 释放 | `0 -> 0.25 rad -> 0` | 检查越障后回中 |
| 正弦 | `0.2*sin(2*pi*f*t)`，`f=0.5,1,2,3 Hz` | 检查频率响应和相位滞后 |
| 噪声目标 | 阶跃叠加 `0.01,0.03,0.05 rad` 噪声 | 检查是否放大 policy 抖动 |
| 训练日志回放 | 导入真实 `q_desired` 序列 | 检查真实 policy 目标下的响应 |

## 11. MATLAB 验收指标

| 指标 | 建议阈值 |
|---|---:|
| `overshoot_ratio` | `< 5% ~ 10%` |
| `settling_time_0p2` | `0.2 rad` 阶跃 `< 0.25 ~ 0.40 s` |
| `steady_error` | `< 0.02 rad` |
| `max_abs_qdot` | `<= 2.0 rad/s` 附近 |
| `sat_ratio` | 中阶跃 `< 30%`，大阶跃可放宽 |
| `ringing_count` | 无持续振荡 |
| `rms_tracking_error` | 越小越好，但不能靠长期饱和硬压 |
| `qdot_alloc_rmse` | `qdot_alloc` 与实际 $\dot q$ 不严重脱节 |
| `smoothness_cost` | 速度变化平方和越小越好 |

筛选优先级：

1. 无持续振荡。
2. 不长期力矩饱和。
3. `0.2 rad` 目标能在约 `0.25 ~ 0.40 s` 内接近。
4. 实际速度不长期顶到 `2 rad/s`。
5. `qdot_alloc` 平滑且能代表实际球铰运动。

## 12. MATLAB 主脚本建议

建议在 MATLAB 中建立以下文件：

```text
run_ball_joint_direct_target_presim.m
simulate_ball_joint_direct_target.m
make_ball_joint_reference.m
compute_ball_joint_metrics.m
plot_ball_joint_presim_cases.m
```

最小可运行主脚本如下，可先作为单文件使用：

```matlab
function run_ball_joint_direct_target_presim()
    clear; clc;

    dt_sim = 1/120;
    dt_ctrl = 1/60;
    T = 2.0;
    t = 0:dt_sim:T;

    tau_max = 60.0;
    qdot_max = 2.0;

    J_list = [0.03, 0.05, 0.10, 0.20, 0.40];
    B_list = [0.0, 0.5, 1.0];
    load_list = [-10, 0, 10];
    tau_cmd_list = [0, 0.03, 0.05, 0.08];
    tau_v_list = [0.03, 0.05, 0.08];
    Kp_list = [120, 160, 220, 320, 500, 800, 1000];
    Kd_list = [10, 16, 24, 32, 48, 64];

    results = table();

    for J = J_list
        for B = B_list
            for load_tau = load_list
                for Kp = Kp_list
                    for Kd = Kd_list
                        for tau_cmd = tau_cmd_list
                            for tau_v = tau_v_list
                                q_desired = make_reference(t, "step_medium");
                                sim = simulate_one_case( ...
                                    t, dt_sim, dt_ctrl, q_desired, ...
                                    J, B, load_tau, Kp, Kd, tau_max, qdot_max, ...
                                    tau_cmd, tau_v);
                                m = compute_metrics(t, sim, tau_max);
                                row = struct2table(m);
                                row.J = J;
                                row.B = B;
                                row.load_tau = load_tau;
                                row.Kp = Kp;
                                row.Kd = Kd;
                                row.tau_cmd = tau_cmd;
                                row.tau_v = tau_v;
                                results = [results; row]; %#ok<AGROW>
                            end
                        end
                    end
                end
            end
        end
    end

    results = movevars(results, ["J","B","load_tau","Kp","Kd","tau_cmd","tau_v"], "Before", 1);
    writetable(results, "ball_joint_direct_target_presim_metrics.csv");
    disp(sortrows(results, ["rms_error", "sat_ratio"]));
end

function q_desired = make_reference(t, mode)
    q_desired = zeros(size(t));
    switch mode
        case "step_small"
            q_desired(t >= 0.2) = 0.05;
        case "step_medium"
            q_desired(t >= 0.2) = 0.20;
        case "step_large"
            q_desired(t >= 0.2) = 0.50;
        case "release"
            q_desired(t >= 0.2 & t < 0.8) = 0.25;
        otherwise
            error("unknown reference mode");
    end
end

function sim = simulate_one_case(t, dt_sim, dt_ctrl, q_desired, J, B, load_tau, Kp, Kd, tau_max, qdot_max, tau_cmd, tau_v)
    n = numel(t);
    q = zeros(1, n);
    qdot = zeros(1, n);
    tau = zeros(1, n);
    q_target = zeros(1, n);
    qdot_alloc = zeros(1, n);

    q_now = 0.0;
    qdot_now = 0.0;
    q_ref = q_desired(1);
    qdot_alloc_now = 0.0;

    ctrl_stride = max(1, round(dt_ctrl / dt_sim));

    for k = 1:n
        if mod(k - 1, ctrl_stride) == 0
            q_cmd = q_desired(k);
            if tau_cmd <= 0
                q_ref = q_cmd;
            else
                alpha_q = 1.0 - exp(-dt_ctrl / tau_cmd);
                q_ref = (1.0 - alpha_q) * q_ref + alpha_q * q_cmd;
            end

            alpha_v = 1.0 - exp(-dt_ctrl / tau_v);
            qdot_alloc_now = (1.0 - alpha_v) * qdot_alloc_now + alpha_v * qdot_now;
            qdot_alloc_now = min(max(qdot_alloc_now, -qdot_max), qdot_max);
        end

        tau_raw = Kp * (q_ref - q_now) - Kd * qdot_now;
        tau_now = min(max(tau_raw, -tau_max), tau_max);

        qddot = (tau_now - B * qdot_now - load_tau) / J;
        qdot_now = qdot_now + dt_sim * qddot;
        qdot_now = min(max(qdot_now, -qdot_max), qdot_max);
        q_now = q_now + dt_sim * qdot_now;

        q(k) = q_now;
        qdot(k) = qdot_now;
        tau(k) = tau_now;
        q_target(k) = q_ref;
        qdot_alloc(k) = qdot_alloc_now;
    end

    sim.q = q;
    sim.qdot = qdot;
    sim.tau = tau;
    sim.q_target = q_target;
    sim.qdot_alloc = qdot_alloc;
end

function metric = compute_metrics(t, sim, tau_max)
    err = sim.q_target - sim.q;
    final_target = sim.q_target(end);
    tol = max(0.02 * abs(final_target), 0.005);

    overshoot = max(sim.q) - final_target;
    if abs(final_target) > 1.0e-8
        overshoot_ratio = max(0, overshoot / abs(final_target));
    else
        overshoot_ratio = 0;
    end

    outside = find(abs(err) > tol);
    if isempty(outside)
        settling_time = 0;
    else
        settling_time = t(outside(end));
    end

    metric.rms_error = sqrt(mean(err.^2));
    metric.steady_error = abs(err(end));
    metric.overshoot = overshoot;
    metric.overshoot_ratio = overshoot_ratio;
    metric.settling_time = settling_time;
    metric.max_abs_qdot = max(abs(sim.qdot));
    metric.sat_ratio = mean(abs(sim.tau) >= 0.98 * tau_max);
    metric.qdot_alloc_rmse = sqrt(mean((sim.qdot_alloc - sim.qdot).^2));
    metric.smoothness_cost = mean(diff(sim.qdot).^2);
end
```

## 13. Isaac Sim 短验证

MATLAB 只能筛掉明显不合适的参数，不能替代接触仿真。进入训练前必须做 Isaac 短验证。

### 13.1 空载 / 平地球铰 step test

固定或低速平地状态下，给球铰目标：

```text
0 -> 0.1 rad
0 -> 0.2 rad
0 -> -0.2 rad
0 -> 0.4 rad
```

必须记录：

```text
q_desired
q_target
q_actual
qdot_actual
qdot_alloc
ball_joint_target_error
ball_joint_velocity
applied_torque 或 drive effort 近似量
```

验收：

- `desired_target - position_target` 应接近 `0`。
- `position_target - actual_pos` 会变大，但不应出现持续振荡。
- `actual_pos` 能在 `0.25 ~ 0.40 s` 量级明显靠近目标。
- `qdot_actual` 不长期顶到 `2 rad/s`。
- 不出现 reset 后第一步速度尖峰。

### 13.2 平地闭环 + wheel allocator

开启完整轮速分配，在平地跑固定 policy 或 scripted action，检查：

```text
q_actual tracking
qdot_alloc
wheel_speed_reference
wheel_torque_targets
v_parallel
v_perp
contact_weights
slip
```

验收：

- `wheel_speed_reference` 不因 `qdot_alloc` 出现高频尖峰。
- 车轮 torque target 不出现异常饱和。
- 平地目标捕捉能力不明显恶化。

### 13.3 旧 policy 回放

删除 planner 会改变 action dynamics。旧 policy 可能依赖原 planner 的慢响应，所以回放只是检查工程稳定，不用于直接下结论。

回放时重点看：

- `desired_target -> position_target` 是否已经打通。
- 球铰真实姿态是否更接近 policy 目标。
- 接触丢失率是否突然升高。
- 台阶 / 障碍处是否出现更明显的球铰姿态参与。

## 14. 训练实验顺序

不要直接做长训。建议：

1. MATLAB 单关节扫参。
2. Isaac 平地球铰 step test。
3. Isaac 平地闭环 wheel allocator test。
4. Stage0 短训或短回放，确认平地目标捕捉不崩。
5. Stage1 `100 ~ 200` iteration 短训，观察球铰跟踪和运动质量。
6. 再决定是否进行 `700` iteration Stage1 训练。

Stage1 短训重点看：

```text
Debug/Stage1/BallJoint/*/desired_target
Debug/Stage1/BallJoint/*/position_target
Debug/Stage1/BallJoint/*/actual_pos
Action/*_rate_target_raw
Observation/ball_joint_vel_abs_mean_raw
Action/wheel_speed_reference_abs_mean_raw
Stage1Eval/*/row_advance_rate
Stage1Eval/*/contact_loss_rate
Stage1Eval/*/stagnation_rate
Stage1Eval/*/pitch_abs_mean
Stage1Eval/*/quality_row_advance_rate
```

预期有效现象：

- `desired_target - position_target` 从约 `0.1 ~ 0.2 rad` 降到接近 `0`。
- `position_target - actual_pos` 上升，但曲线平滑。
- `actual_pos` 不再长期贴着旧小目标，而是真正靠近 policy 目标。
- 台阶 / 障碍处球铰姿态参与更明显。
- 如果低 row 仍靠冲，高 row 仍失败，则说明还需要继续改 reward / curriculum，而不是底层 target 没打通。

## 15. 第一版参数建议

在 MATLAB 结果出来前，不把以下数值视为最终结论。它们只是第一轮扫参的候选中心。

考虑当前 effort limit 已统一为 `60 N*m`，比外部建议的 `20 N*m` 高三倍，因此只测试很低增益可能偏保守。第一版不做分关节 gain，所有球铰轴统一使用同一组 $K_p,K_d$。

建议候选：

| 类型 | 统一增益候选 |
|---|---:|
| 保守候选 | `Kp=160, Kd=16` |
| 中等候选 | `Kp=320, Kd=32` |
| 偏强候选 | `Kp=500, Kd=48` |
| 压力测试 | `Kp=1000, Kd=10` |

如果中增益下无振荡、饱和不长、响应足够快，优先用中增益进入 Isaac 短验证。如果中增益抖动或接触扰动明显，退到低增益或增加 damping。

当前 `1000 / 10 / 60` 不建议直接作为最终 direct-target 参数，但必须作为压力测试基线保留在 MATLAB 中，用来量化“原参数直接 target”到底有多饱和。

## 16. 最终敲定的第一版实现形态

第一版落地应采用：

$$
q_{\mathrm{target}}
=
\operatorname{clip}
\left(
q^d,
q_{\mathrm{lower}},
q_{\mathrm{upper}}
\right)
$$

$$
\tau_q
=
K_p(q_{\mathrm{target}}-q)
-
K_d\dot q
$$

$$
\dot q_{\mathrm{alloc}}
=
\mathrm{LPF}
\left(
\dot q_{\mathrm{actual}}
\right)
$$

$$
\mathbf v_j^{\mathrm{nom}}
=
v_x^*\mathbf e_x
+
\omega_z^*(\mathbf e_z\times\mathbf p_j)
+
\mathbf G_j\dot q_{\mathrm{alloc}}
$$

也就是：

```text
去掉 actual_pos-based q_cmd planner
保留 Isaac/PhysX implicit position drive
不在第一版下发 ball joint velocity target
allocator 的 qdot 使用 filtered actual joint velocity
必要时只加入 command-side target filter，不恢复旧 planner
```

这条路线直接针对当前训练数据暴露出的 `desired_target -> position_target` 削弱问题，同时保留轮速分配中球铰姿态变化率对轮心速度的补偿项。
