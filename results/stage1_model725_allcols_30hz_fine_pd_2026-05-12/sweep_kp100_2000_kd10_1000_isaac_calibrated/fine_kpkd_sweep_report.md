# Stage1 model_725 30 Hz fine Kp/Kd sweep

- trace_dir: `/home/ubuntu/Graduation-Project/results/stage1_model725_allcols_30hz_fine_pd_2026-05-12/raw_traces`
- trace_glob: `model725_allcols_30hz_col*.csv`
- cases: `30`
- samples: `35972`
- Kp: `100:2000:10`
- Kd: `10:1000:10`
- plant calibration enabled: `True`
- plant calibration grid: `J=0.02:0.12:0.01`, `B=0:6:0.5`, `tau_load=-8:8:4`
- plant calibration base gains: `Kp=120.0`, `Kd=10.0`
- fixed plant used by sweep: `J=0.07`, `B=6.0`, `tau_load=0.0`
- fixed limits: `tau_max=60.0`, `qdot_max=2.0`
- risk thresholds: `sat_threshold=0.7`, `qdot_limit_threshold=0.7`
- old_relative_error_mean: `0.891246`

## Plant Calibration Best

`J=0.070000, B=6.000000, tau_load=0.000000`, `score=0.085876`, `rmse=0.083668`, `relative_error=0.562451`.

## Best

`Kp=100, Kd=10`, `risk=0.993570`, `relative_error=0.711447`, `abs_error=0.089254`, `sat_ratio=0.000274`, `qdot_limit_rate=0.024080`.
