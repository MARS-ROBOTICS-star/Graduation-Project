# Stage1 model_725 30 Hz fine Kp/Kd sweep

- trace_dir: `/home/ubuntu/Graduation-Project/results/stage1_model725_allcols_30hz_fine_pd_2026-05-12/raw_traces`
- trace_glob: `model725_allcols_30hz_col*.csv`
- cases: `30`
- samples: `35972`
- Kp: `100:2000:10`
- Kd: `10:1000:10`
- plant calibration enabled: `True`
- plant calibration grid: `J=0.08:0.14:0.005`, `B=12:20:0.5`, `tau_load=-6:2:1`
- plant calibration base gains: `Kp=120.0`, `Kd=10.0`
- fixed plant used by sweep: `J=0.115`, `B=18.0`, `tau_load=-2.0`
- fixed limits: `tau_max=60.0`, `qdot_max=2.0`
- risk thresholds: `sat_threshold=0.7`, `qdot_limit_threshold=0.7`
- old_relative_error_mean: `0.891246`

## Plant Calibration Best

`J=0.115000, B=18.000000, tau_load=-2.000000`, `score=0.091909`, `rmse=0.078885`, `relative_error=0.554689`.

## Best Risk

`Kp=100, Kd=10`, `risk=0.869811`, `relative_error=0.790135`, `abs_error=0.102371`, `sat_ratio=0.000380`, `qdot_limit_rate=0.294929`.

## Best Tracking Under Configured Limits

`Kp=1690, Kd=10`, `risk=2.074574`, `relative_error=0.462546`, `abs_error=0.060708`, `sat_ratio=0.417033`, `qdot_limit_rate=0.698579`.

## Best Tracking Under 60% Qdot / 30% Torque Limits

`Kp=990, Kd=10`, `risk=1.760576`, `relative_error=0.493667`, `abs_error=0.063795`, `sat_ratio=0.299431`, `qdot_limit_rate=0.535233`.
