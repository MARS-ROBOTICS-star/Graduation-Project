# Stage0 lateral0 + no slip penalty early-stop diagnosis

## 1. Run identification

- Run directory: `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-27_10-11-39_stage0_lateral0_no_slip_penalty_ball1500_d30_700iter`
- Isaac Lab log: `/tmp/isaaclab/logs/isaaclab_2026-04-27_10-11-39.log`
- Original plan: `700` iterations
- Actual stop point: terminal printed iteration `393/700`
- Stop reason: success rate had reached a high plateau, so training was manually stopped
- Latest saved checkpoint: `model_375.pt`
- TensorBoard export: `tensorboard_export/`

## 2. Configuration

The run config and Isaac log confirmed the active parameters:

| Item | Value |
|---|---:|
| `num_envs` | `64` |
| `num_waypoints_per_episode` | `2` |
| `goal_distance` | `10.0 m` |
| `target_position_tolerance` | `0.5 m` |
| `low_slip_lambda_lateral` | `0.0` |
| `slip_penalty_weight` | `0.0` |
| `wheel_torque_tracking_gain` | `2.0` |
| `wheel_slip_feedback_gain` | `1.5` |
| `wheel_joint_effort_limit_sim` | `15.0 Nm` |
| `ball_joint_stiffness` | `1500.0` |
| `ball_joint_damping` | `30.0` |

The terminal confirmed that planar command shaping was disabled in this run:

- `Action/desired_planar_command_abs_mean_raw == Action/shaped_planar_command_abs_mean_raw`
- `Action/planar_command_shaping_delta_abs_mean_raw = 0.0`
- `Reward/slip_penalty = 0.0`

## 3. Task completion

The run restored target completion.

| Metric | Last | Last 10 mean | Last 25 mean |
|---|---:|---:|---:|
| `Termination/success_rate` | `1.000` | `0.989` | `0.965` |
| `Termination/time_out_rate` | `0.000` | `0.011` | `0.035` |
| `episode/waypoint_completion_pct` | `100.00%` | `99.39%` | `97.41%` |
| `episode/waypoints_completed` | `2.000` | `1.988` | `1.948` |
| `Train/mean_reward` | `20.612` | `20.433` | `20.227` |
| `Train/mean_episode_length` | `1611.8` | `1634.9` | `1659.5` |

Important metric interpretation:

- `Termination/success_rate` is an episode-final reset-batch success rate.
- `episode/waypoint_completion_pct` is the matching episode-final waypoint completion percentage.
- `Tracking/episode_completion_pct` is only the instantaneous average completed-waypoint ratio among currently alive parallel envs.
- Therefore the last-25 `Tracking/episode_completion_pct ≈ 24.97%` does not contradict the last-25 `success_rate ≈ 96.55%`.

## 4. Motion quality

Although the target task was recovered, motion quality remained poor.

| Metric | Last | Last 10 mean | Last 25 mean |
|---|---:|---:|---:|
| `LowLevel/v_parallel_abs_mean_raw` | `0.468 m/s` | `0.462 m/s` | `0.453 m/s` |
| `LowLevel/v_perp_abs_mean_raw` | `0.483 m/s` | `0.481 m/s` | `0.473 m/s` |
| `Observation/wheel_longitudinal_slip_abs_mean_raw` | `2.314` | `2.309` | `2.308` |
| `Observation/wheel_slip_angle_abs_mean_raw` | `0.717 rad` | `0.718 rad` | `0.714 rad` |
| `LowSlip/combined_pass_rate` | `0.0039` | `0.0055` | `0.0064` |
| `ProgressGate/multiplier` | `0.128` | `0.132` | `0.135` |
| `Action/wheel_speed_reference_abs_mean_raw` | `6.397` | `6.330` | `6.236` |
| `Action/wheel_torque_target_abs_mean_raw` | `1.897 Nm` | `1.895 Nm` | `1.900 Nm` |

Interpretation:

- Removing direct slip penalty allowed the policy to run and hit the waypoints.
- The learned motion is still a high-slip, high-side-drift completion mode.
- `v_perp` remains slightly larger than `v_parallel`, so the vehicle is still moving with substantial lateral drift.
- Wheel torque target remains far below the `15 Nm` limit, so the immediate bottleneck is not the wheel torque ceiling.
- The progress gate is near its floor because slip metrics are poor, but `reached_target` remains strong enough to drive learning to high success.

## 5. Contact and middle-body support

Global contact did not collapse:

| Metric | Last | Last 10 mean | Last 25 mean |
|---|---:|---:|---:|
| `Observation/wheel_normal_contact_force_sum_raw` | `1.009` | `1.006` | `1.006` |
| `Observation/pitch_deg` | `0.154 deg` | `0.016 deg` | `-0.106 deg` |

But middle-body wheel support remained very weak.

### Last 25 iterations

| Wheel | Normal force | Contact weight | Torque target |
|---|---:|---:|---:|
| front left | `106.051 N` | `0.916` | `0.634 Nm` |
| front right | `70.071 N` | `0.672` | `0.841 Nm` |
| middle left | `2.438 N` | `0.027` | `0.046 Nm` |
| middle right | `5.190 N` | `0.057` | `0.055 Nm` |
| rear left | `77.259 N` | `0.754` | `0.720 Nm` |
| rear right | `105.583 N` | `0.907` | `1.486 Nm` |

Middle-body total normal-force share:

- Last 25 mean: `2.08%`
- Last 10 mean: `1.39%`
- Last step: `1.05%`

Interpretation:

- This is not a whole-vehicle contact loss; front and rear wheels carry most of the load.
- The middle wheels are almost only lightly touching the ground.
- Because the current torque controller multiplies by contact weight, low middle contact directly produces very low middle-wheel torque participation.
- The weak middle contact persists even after removing direct slip penalty, so it should be treated as a load distribution / geometry / posture issue, not as a direct slip-penalty artifact.

## 6. Conclusion

This run proves that `low_slip_lambda_lateral=0.0` plus `slip_penalty_weight=0.0` restores Stage0 waypoint completion under the current `1500/30` ball-joint drive.

It does not solve the motion-quality problem. The policy reaches targets by accepting high longitudinal slip, high side drift, and front/rear-wheel-dominant support while the middle wheels are weakly loaded.

For the next research decision, `success_rate` should be treated as recovered, while low-slip behavior and middle-body load sharing remain unsolved evaluation targets.
