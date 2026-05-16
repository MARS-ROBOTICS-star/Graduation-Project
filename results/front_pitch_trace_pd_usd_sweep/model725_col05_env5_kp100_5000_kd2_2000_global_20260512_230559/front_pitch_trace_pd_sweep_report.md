# Front Pitch Trace PD Controller Sweep

- trace: `/home/ubuntu/Graduation-Project/results/stage1_model725_allcols_30hz_fine_pd_2026-05-12/raw_traces/model725_allcols_30hz_col05_stairs_down.csv`
- env_id: `5`
- source_column: `q_desired_spm1_platform_joint_y`
- samples: `1198`
- candidates: `640000`
- plant: `J=0.115`, `B=18.0`, `tau_load=0.0`

## Best Risk

- `Kp=1500`, `Kd=2`, `tau_ref=0.12`, `qddot=16`, `velocity=2`, `effort=60`
- risk `2.870816`, cmd error mean `0.002923 rad`, raw error mean `0.147072 rad`, tau sat `0.000000`, qdot limit `0.082638`, qdot cmd delta mean `0.406107 rad/s`

## Best Stable

- `Kp=900`, `Kd=2`, `tau_ref=0.12`, `qddot=16`, `velocity=1.8`, `effort=60`
- risk `2.977894`, cmd error mean `0.007152 rad`, raw error mean `0.148007 rad`, tau sat `0.000000`, qdot limit `0.026711`

## Best Smooth

- `Kp=1400`, `Kd=2`, `tau_ref=0.12`, `qddot=3`, `velocity=1.2`, `effort=60`
- risk `3.055148`, cmd error mean `0.001825 rad`, raw error mean `0.237467 rad`, tau sat `0.000000`, qdot limit `0.055092`, qdot cmd delta mean `0.093893 rad/s`

## Best Tracking Under Loose Limits

- `Kp=2000`, `Kd=2`, `tau_ref=0.06`, `qddot=10`, `velocity=1.2`, `effort=60`
- risk `3.535155`, cmd error mean `0.001549 rad`, raw error mean `0.171164 rad`, tau sat `0.000000`, qdot limit `0.380634`
