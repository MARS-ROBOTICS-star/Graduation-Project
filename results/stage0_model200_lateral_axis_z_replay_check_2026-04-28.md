# Stage0 model_200 local Z 侧向轴回放复查

## 背景

- checkpoint：`logs/rsl_rl/complete_car_stage0/2026-04-28_08-24-09_stage0_direct_velocity_no_shaping_resume_from75_625iter/model_200.pt`
- 目的：USD 检查确认 wheel local `Z` 是轮轴/水平侧向方向后，将 `env.py` 与 `mdp/observations.py` 的侧向速度口径从 local `Y` 改为 local `Z`，再做短回放探针。
- 重要限制：该 checkpoint 是修正侧向轴之前训练出来的，因此本次回放只是诊断一致性检查，不是修正后重新训练的有效结果。

## 命令

```bash
env TERM=xterm MPLCONFIGDIR=/tmp/matplotlib OMNI_KIT_ACCEPT_EULA=YES /home/ubuntu/IsaacLab/isaaclab.sh -p scripts/replay_probe.py --task CompleteCar-Stage0 --device cuda:0 --num_envs 1 --checkpoint logs/rsl_rl/complete_car_stage0/2026-04-28_08-24-09_stage0_direct_velocity_no_shaping_resume_from75_625iter/model_200.pt --steps 120 --warmup_steps 20
```

## 关键指标

| 指标 | 数值 |
|---|---:|
| `raw_action_all abs_mean` | `0.152056` |
| `raw_action_base abs_mean` | `0.058149` |
| `desired_planar_vx mean` | `-0.142561 m/s` |
| `desired_planar_vx abs_mean` | `0.143237 m/s` |
| `desired_planar_wz mean` | `0.065599 rad/s` |
| `desired_planar_wz abs_mean` | `0.089357 rad/s` |
| `wheel_ref abs_mean` | `0.870143 rad/s` |
| `wheel_joint_vel abs_mean` | `0.799792 rad/s` |
| `wheel_rolling_speed abs_mean` | `0.061036 m/s` |
| `wheel_lateral_speed abs_mean` | `0.015284 m/s` |
| `wheel_delta_v abs_mean` | `0.127479 m/s` |
| `wheel_longitudinal_slip abs_mean` | `1.262461` |
| `wheel_slip_angle abs_mean` | `0.145086 rad` |
| `progress_multiplier mean` | `0.250000` |
| `progress_multiplier max` | `0.250005` |
| `root_xy_displacement_mean_m` | `0.111931 m` |
| `goal_distance_delta_mean_m` | `-0.075492 m` |

各车轮尾段侧向速度均值：

| 车轮 | `v_perp` |
|---|---:|
| 中车左轮 | `-0.029721 m/s` |
| 中车右轮 | `-0.029721 m/s` |
| 前车左轮 | `0.001639 m/s` |
| 前车右轮 | `0.001639 m/s` |
| 后车左轮 | `0.007602 m/s` |
| 后车右轮 | `0.007602 m/s` |

## 解释

- 修正为 local `Z` 后，同一 checkpoint 测得的真实水平侧滑明显低于旧 local `Y` 诊断口径。旧口径回放约为 `v_perp_abs≈0.0716 m/s`、`wheel_slip_angle_abs≈0.443 rad`；修正后为 `v_perp_abs≈0.0153 m/s`、`wheel_slip_angle_abs≈0.145 rad`。
- 因此，修正前的侧滑日志混入了车轮竖直速度分量，不能作为真实水平侧滑证据。
- 该 checkpoint 仍没有解决行驶任务。本次探针位移只有约 `0.112 m`，目标距离反而变差约 `0.075 m`。
- `progress_multiplier` 仍停在约 `0.25` 的下限。由于修正后侧滑角已经明显变小，剩余瓶颈更可能是纵滑 gate 和 policy 给出的弱前进命令，而不是侧滑 gate 单独导致。
