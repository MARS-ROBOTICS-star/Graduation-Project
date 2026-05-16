# Front Pitch Trace PD Controller Sweep

- trace: `/home/ubuntu/Graduation-Project/results/stage1_model725_allcols_30hz_fine_pd_2026-05-12/raw_traces/model725_allcols_30hz_col05_stairs_down.csv`
- env_id: `5`
- source_column: `q_desired_spm1_platform_joint_y`
- samples: `1198`
- candidates: `176256`
- plant: `J=0.115`, `B=18.0`, `tau_load=0.0`

## Best Risk

- `Kp=1390`, `Kd=2`, `tau_ref=0.12`, `qddot=16`, `velocity=2`, `effort=60`
- risk `2.859702`, cmd error mean `0.003308 rad`, raw error mean `0.147381 rad`, tau sat `0.000000`, qdot limit `0.063439`, qdot cmd delta mean `0.406107 rad/s`

## Best Stable

- `Kp=1470`, `Kd=2`, `tau_ref=0.12`, `qddot=3`, `velocity=1.2`, `effort=60`
- risk `3.045750`, cmd error mean `0.001706 rad`, raw error mean `0.237393 rad`, tau sat `0.000000`, qdot limit `0.055927`

## Best Smooth

- `Kp=1470`, `Kd=2`, `tau_ref=0.12`, `qddot=3`, `velocity=1.2`, `effort=60`
- risk `3.045750`, cmd error mean `0.001706 rad`, raw error mean `0.237393 rad`, tau sat `0.000000`, qdot limit `0.055927`, qdot cmd delta mean `0.093893 rad/s`

## Best Tracking Under Loose Limits

- `Kp=1585`, `Kd=2`, `tau_ref=0.12`, `qddot=3`, `velocity=1.2`, `effort=60`
- risk `3.077872`, cmd error mean `0.001627 rad`, raw error mean `0.237233 rad`, tau sat `0.000000`, qdot limit `0.066778`
