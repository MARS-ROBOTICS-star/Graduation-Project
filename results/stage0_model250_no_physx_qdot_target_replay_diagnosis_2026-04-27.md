# Stage0 model_250 replay after removing PhysX ball-joint velocity target - 2026-04-27

## 1. Replay setup

- Checkpoint:
  - `RL_Training/logs/rsl_rl/complete_car_stage0/2026-04-27_12-59-37_stage0_lateral0_load_eq_ball1000_qdot08_qddot15_contact_watch_700iter/model_250.pt`
- Replay script:
  - `RL_Training/scripts/evaluate_contact_replay.py`
- Current code change under validation:
  - Internal ball-joint planner still computes `q_cmd/qdot_cmd`.
  - Wheel-speed allocator still uses the same `qdot_cmd`.
  - PhysX ball-joint drive now receives only `q_cmd`; `qdot_cmd` is not sent as a ball-joint velocity target.
- Replay settings:
  - `num_envs=8`
  - `steps=2400`
  - `warmup_steps=120`
  - label: `model250_no_physx_qdot_target`
- Effective replay parameters:
  - `ball_joint_stiffness=1000.0`
  - `ball_joint_damping=10.0`
  - `ball_joint_effort_limit_sim=30.0`
  - `ball_joint_planner_qdot_limit=0.8 rad/s`
  - `ball_joint_planner_qddot_limit=1.5 rad/s^2`
  - `low_slip_lambda_lateral=0.0`
  - `slip_penalty_weight=0.0`

## 2. Replay metrics

Samples after warmup: `2280`.

Middle wheel contact:

- middle/body left normal force mean: `33.13 N`
- middle/body right normal force mean: `28.14 N`
- middle pair normal force sum: `61.27 N`
- total six-wheel normal force mean: `365.82 N`
- middle pair load ratio: `16.75%`
- middle tail-window normal force:
  - left: `29.87 N`
  - right: `12.85 N`
- middle contact weight mean:
  - left: `0.3995`
  - right: `0.2876`

Other wheel normal force means:

- front/head left: `83.80 N`
- front/head right: `61.45 N`
- rear/tail left: `70.12 N`
- rear/tail right: `89.18 N`

Motion and posture:

- pitch mean: `1.106 deg`
- roll mean: `0.350 deg`
- ball-joint velocity absolute mean: `0.210 rad/s`
- ball-joint target error absolute mean: `0.0176 rad`
- `v_parallel_abs_mean`: `0.177 m/s`
- `v_perp_abs_mean`: `0.190 m/s`
- longitudinal slip absolute mean: `1.599`
- slip angle absolute mean: `0.471 rad`
- tail-window `active_segment_completion_pct`: `78.19%`

## 3. Comparison against the stopped training diagnosis

Previous TensorBoard last-25 training diagnosis for the same checkpoint family:

- middle pair load ratio: about `20.72%`
- middle left/right normal force: about `33.82 N / 42.36 N`
- `v_parallel_abs`: about `0.209 m/s`
- `v_perp_abs`: about `0.226 m/s`
- longitudinal slip: about `2.026`
- slip angle: about `0.530 rad`
- `active_segment_completion_pct`: about `61.24%`, max about `68.23%`

Current replay after removing PhysX ball-joint velocity target:

- middle pair load ratio: `16.75%`
- middle left/right normal force: `33.13 N / 28.14 N`
- `v_parallel_abs`: `0.177 m/s`
- `v_perp_abs`: `0.190 m/s`
- longitudinal slip: `1.599`
- slip angle: `0.471 rad`
- tail-window `active_segment_completion_pct`: `78.19%`

## 4. Conclusion

Removing the PhysX ball-joint velocity target did not improve middle-body contact for this checkpoint.

The middle pair load ratio decreased from the previous training-diagnosis reference of about `20.72%` to `16.75%` in this replay. The right middle wheel is especially weak in the replay tail window, dropping to about `12.85 N`.

Motion quality improved in two scalar metrics: longitudinal slip decreased from about `2.026` to `1.599`, and slip angle decreased from about `0.530 rad` to `0.471 rad`. However, both forward and lateral speeds also decreased, so this is not yet evidence of better rolling propulsion.

The route-progress metric improved in this replay window, but this is not directly equivalent to episode-level success. This replay did not prove that target completion has recovered.

Current interpretation:

- Removing `qdot_cmd` from the PhysX ball-joint drive reduces active velocity driving and appears to reduce slip.
- It does not by itself solve middle-body load sharing.
- The policy was trained under the old execution chain, so replaying it under the new execution chain is only a diagnostic, not a final training result.
- A new training run is required to test whether the policy can learn better contact behavior under the no-PhysX-qdot ball-joint execution chain.
