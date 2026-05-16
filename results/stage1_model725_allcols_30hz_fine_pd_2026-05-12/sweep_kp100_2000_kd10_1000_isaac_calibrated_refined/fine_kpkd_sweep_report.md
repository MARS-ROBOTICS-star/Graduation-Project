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
- fixed plant used by sweep: `J=0.125`, `B=19.5`, `tau_load=-1.0`
- fixed limits: `tau_max=60.0`, `qdot_max=2.0`
- risk thresholds: `sat_threshold=0.7`, `qdot_limit_threshold=0.7`
- old_relative_error_mean: `0.891246`

## Plant Calibration Best

`J=0.125000, B=19.500000, tau_load=-1.000000`, `score=0.079890`, `rmse=0.079604`, `relative_error=0.558309`.

## Best

`Kp=120, Kd=10`, `risk=0.888774`, `relative_error=0.764959`, `abs_error=0.098087`, `sat_ratio=0.000969`, `qdot_limit_rate=0.004748`.
