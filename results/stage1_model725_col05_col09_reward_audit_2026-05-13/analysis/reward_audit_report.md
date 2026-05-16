# Stage1 model_725 col05-col09 reward audit 2026-05-13

Replay: old `model_725.pt`, current Stage1 reward code, columns `5-9`, terrain row `11`, `15` envs, `120` warmup steps, `1200` collected control steps. Done rows were excluded by the export script.

## Last 100 control steps by column

| col | terrain | progress | drop | rear_pen | front_post | module | rear_rew | q_gate | q_motion | drop_guard | rear_score | hard_pen | net | pen/prog |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 05 | stairs_down | 0.000087 | -0.003955 | -0.000923 | -0.005738 | 0.000727 | 0.000000 | 0.000000 | 0.320038 | 0.555184 | 0.000408 | -0.011013 | -0.010198 | 126.83 |
| 06 | stairs_down | 0.002223 | -0.006155 | -0.005061 | -0.004518 | 0.000771 | 0.000000 | 0.000000 | 0.335433 | 0.093960 | 0.000972 | -0.016116 | -0.013122 | 7.25 |
| 07 | stairs_down | 0.005359 | -0.000615 | -0.011165 | -0.002590 | 0.000853 | 0.000000 | 0.000000 | 0.390703 | 0.050000 | 0.180986 | -0.014692 | -0.008480 | 2.74 |
| 08 | discrete_obstacles | 0.009980 | -0.002993 | -0.030053 | -0.003595 | 0.000604 | 0.000954 | 0.000000 | 0.391887 | 0.556667 | 0.432254 | -0.036960 | -0.025423 | 3.70 |
| 09 | discrete_obstacles | 0.012574 | -0.003986 | 0.000000 | -0.001691 | 0.000212 | 0.000000 | 0.000000 | 0.426027 | 0.583333 | 0.173333 | -0.006016 | 0.006770 | 0.48 |

## Interpretation

- Reward ordering has changed: in the last 100 steps, hard-terrain penalties are now the same order as, or larger than, positive progress.
- Overall last-100 ratios to progress magnitude: `drop_anti_dive_penalty = 0.58x`, `step_up_front_posture_penalty = 0.60x`, `rear_follow_penalty = 1.56x`, `step_up_module_progress_reward = 0.10x`.
- `quality_gate_score` is `0` on all audited hard columns because the strict gate now includes module / rear-follow quality. This is acceptable only as a strict diagnostic while `quality_gated_terrain_advance = False`; it is too strict to re-enable as an advance gate without further relaxation.
- `motion_quality_score` remains informative rather than saturated: last-100 column means are about `0.32-0.43`, so it can be used as the softer motion-quality score.
- Drop guard is active in a large part of the last phase, especially col05, col08, and col09. This confirms the anti-dive latch is actually entering the reward calculation.
- Rear-follow penalty now dominates col08 and col07 where the rear module is not participating enough; this matches the intended correction.
