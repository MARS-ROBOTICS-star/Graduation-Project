# Front Pitch Trace PD Controller Sweep

- trace: `/home/ubuntu/Graduation-Project/results/stage1_model725_allcols_30hz_fine_pd_2026-05-12/raw_traces/model725_allcols_30hz_col05_stairs_down.csv`
- env_id: `5`
- source_column: `q_desired_spm1_platform_joint_y`
- samples: `1198`
- candidates: `44160`
- plant: `J=0.115`, `B=18.0`, `tau_load=0.0`

## Best Risk

- `Kp=1150`, `Kd=5`, `tau_ref=0.100`, `qddot=16.0`, `velocity=2.0`, `effort=60.0`
- risk `3.194443`, cmd error mean `0.006426 rad`, raw error mean `0.151078 rad`, tau sat `0.000000`, qdot limit `0.051753`, qdot cmd delta mean `0.410754 rad/s`

## Best Stable

- `Kp=1000`, `Kd=5`, `tau_ref=0.100`, `qddot=4.0`, `velocity=1.5`, `effort=60.0`
- risk `3.583210`, cmd error mean `0.005421 rad`, raw error mean `0.254280 rad`, tau sat `0.000000`, qdot limit `0.024207`

## Best Tracking Under Loose Limits

- `Kp=1200`, `Kd=5`, `tau_ref=0.060`, `qddot=4.0`, `velocity=1.5`, `effort=60.0`
- risk `3.807275`, cmd error mean `0.004689 rad`, raw error mean `0.257688 rad`, tau sat `0.000000`, qdot limit `0.125209`
