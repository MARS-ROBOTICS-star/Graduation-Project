# Front Pitch Trace PD Controller Sweep

- trace: `/home/ubuntu/Graduation-Project/results/stage1_model725_allcols_30hz_fine_pd_2026-05-12/raw_traces/model725_allcols_30hz_col05_stairs_down.csv`
- env_id: `5`
- source_column: `q_desired_spm1_platform_joint_y`
- samples: `1198`
- candidates: `25600`
- plant: `J=0.115`, `B=18.0`, `tau_load=0.0`

## Best Risk

- `Kp=1350`, `Kd=2.5`, `tau_ref=0.12`, `qddot=16`, `velocity=2`, `effort=60`
- risk `2.881641`, cmd error mean `0.003636 rad`, raw error mean `0.147541 rad`, tau sat `0.000000`, qdot limit `0.060100`, qdot cmd delta mean `0.406107 rad/s`

## Best Stable

- `Kp=850`, `Kd=2.5`, `tau_ref=0.12`, `qddot=16`, `velocity=2`, `effort=60`
- risk `3.030968`, cmd error mean `0.007977 rad`, raw error mean `0.150158 rad`, tau sat `0.000000`, qdot limit `0.009182`

## Best Smooth

- `Kp=1250`, `Kd=2.5`, `tau_ref=0.12`, `qddot=3`, `velocity=1.2`, `effort=60`
- risk `3.072634`, cmd error mean `0.002298 rad`, raw error mean `0.237549 rad`, tau sat `0.000000`, qdot limit `0.045910`, qdot cmd delta mean `0.093893 rad/s`

## Best Tracking Under Loose Limits

- `Kp=2000`, `Kd=2.5`, `tau_ref=0.1`, `qddot=10`, `velocity=1.2`, `effort=60`
- risk `3.478254`, cmd error mean `0.001705 rad`, raw error mean `0.170956 rad`, tau sat `0.000000`, qdot limit `0.359766`
