# Stage0 load equalization training diagnosis - 2026-04-27

## 1. Run identification

- Run directory: `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-27_12-59-37_stage0_lateral0_load_eq_ball1000_qdot08_qddot15_contact_watch_700iter`
- Planned iterations: `700`
- Actual TensorBoard last step: `256`
- Stop mode: user requested stop; training process was interrupted and GPU released.
- Checkpoints saved: `model_0.pt`, `model_25.pt`, ..., `model_250.pt`
- Final available checkpoint: `model_250.pt`

## 2. Effective configuration

Run config confirmed from `params/env.yaml`:

- `low_slip_lambda_lateral = 0.0`
- `slip_penalty_weight = 0.0`
- `load_equalization_weight = 1.0`
- `load_equalization_k = 10.0`
- `low_slip_angle_threshold_rad = 0.5`
- `ball_joint_planner_qdot_limits = 0.8 rad/s`
- `ball_joint_planner_qddot_limits = 1.5 rad/s^2`
- `ball_joint_stiffness = 1000.0`
- `ball_joint_damping = 10.0`
- `ball_joint_effort_limit_sim = 30.0`

This run was not a pure single-variable test of load equalization against the previous high-success run. It also used the current ball-joint planner limits and the active `1000/10` ball-joint drive configuration.

## 3. Task outcome

The run did not recover stable target completion.

Last 25 TensorBoard steps:

- `success_rate`: `0.0149`
- final `success_rate`: `0.0`
- max observed `success_rate`: `0.201`
- `time_out_rate`: `0.985`
- `far_from_target_rate`: `0.0`
- `active_segment_completion_pct`: `61.24%`
- final `active_segment_completion_pct`: `61.94%`
- max `active_segment_completion_pct`: `68.23%`
- `active_waypoint_pos_error`: `3.88 m`
- `waypoints_completed_mean`: `0.113`
- `Tracking/episode_completion_pct`: `5.63%`

Episode-final metrics were also weak:

- `episode/waypoints_completed` last-25 mean: `0.268`
- `episode/waypoint_completion_pct` last-25 mean: `13.38%`

Interpretation: the policy learned to survive and move through part of the first waypoint segment, but did not learn a stable full-episode waypoint completion strategy.

## 4. Motion quality

Last 25 TensorBoard steps:

- `v_parallel_abs_mean_raw`: `0.209 m/s`
- `v_perp_abs_mean_raw`: `0.226 m/s`
- `wheel_speed_reference_abs_mean_raw`: `3.390`
- `wheel_torque_target_abs_mean_raw`: `1.925`
- longitudinal slip mean: `2.026`
- slip angle mean: `0.530 rad`
- `LowSlip/combined_pass_rate`: `0.155`
- `LowSlip/longitudinal_slip_pass_rate`: `0.175`
- `LowSlip/slip_angle_pass_rate`: `0.473`

The vehicle is still not rolling efficiently. The forward and lateral wheel-frame velocities are similar in magnitude, and longitudinal slip remains about `2.0`, far above the desired `0.15-0.20` range.

## 5. Six-wheel contact and load sharing

Last 25-step mean normal forces:

- middle/body left: `33.82 N`
- middle/body right: `42.36 N`
- front/head left: `78.04 N`
- front/head right: `61.95 N`
- rear/tail left: `74.15 N`
- rear/tail right: `77.36 N`

Pair-level load shares:

- middle/body pair: `20.72%`
- front/head pair: `38.07%`
- rear/tail pair: `41.21%`

Latest-step load shares:

- middle/body pair: `19.00%`
- front/head pair: `39.05%`
- rear/tail pair: `41.94%`

The middle body no longer behaves like the earlier near-airborne case, but it remains underloaded. A fully even six-wheel target would require the middle pair to carry about `33.33%` of the total normal force.

Load equalization did not become a clearly optimized objective:

- `LoadEqualization/error` first: `0.1668`
- `LoadEqualization/error` last-25 mean: `0.1811`
- `LoadEqualization/raw` first: `0.2408`
- `LoadEqualization/raw` last-25 mean: `0.2081`

The reward term was active, but the learned policy did not reduce the load-share error.

## 6. Diagnosis

The main positive signal is that middle-wheel contact improved compared with the previous high-success but middle-airborne run: the middle pair rose to about `20%` of total load instead of near `1-2%`.

The main failure is that target completion collapsed relative to the previous no-slip-penalty high-success run. The policy survived to timeout and partially approached the route, but did not reach targets reliably.

The most likely cause is reward competition and weak task dominance:

- `load_equalization` is a dense per-step reward, but it is small and not enough to force true six-wheel load sharing.
- `distance_to_target` and partial progress can reward being closer without completing the target.
- `reached_target` remains sparse, so once the policy finds a slow partial-progress behavior, it receives limited pressure to finish.
- The current ball-joint and contact dynamics still allow a local solution with low speed, high longitudinal slip, and front/rear dominant support.

## 7. Recommended next action

Do not continue this run as a successful training direction.

The clean next ablation is:

1. Set `load_equalization_weight = 0.0` while keeping the same current ball-joint parameters, to verify whether target completion recovers under the same controller.
2. If target completion recovers, reintroduce middle-load behavior as a gated or conditional term, not as an always-on equal six-wheel objective.
3. Evaluate middle contact as a success-quality metric first; only promote it to a reward term after target completion is stable.
