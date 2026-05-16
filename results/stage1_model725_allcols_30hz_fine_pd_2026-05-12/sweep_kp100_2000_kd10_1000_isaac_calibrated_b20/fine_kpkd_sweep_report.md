# Stage1 model_725 30 Hz fine Kp/Kd sweep

- trace_dir: `/home/ubuntu/Graduation-Project/results/stage1_model725_allcols_30hz_fine_pd_2026-05-12/raw_traces`
- trace_glob: `model725_allcols_30hz_col*.csv`
- cases: `30`
- samples: `35972`
- Kp: `100:2000:10`
- Kd: `10:1000:10`
- plant calibration enabled: `True`
- plant calibration grid: `J=0.02:0.14:0.01`, `B=0:20:1`, `tau_load=-8:8:2`
- plant calibration base gains: `Kp=120.0`, `Kd=10.0`
- fixed plant used by sweep: `J=0.11`, `B=16.0`, `tau_load=-2.0`
- fixed limits: `tau_max=60.0`, `qdot_max=2.0`
- risk thresholds: `sat_threshold=0.7`, `qdot_limit_threshold=0.7`
- old_relative_error_mean: `0.891246`

## Plant Calibration Best

`J=0.110000, B=16.000000, tau_load=-2.000000`, `score=0.080072`, `rmse=0.079564`, `relative_error=0.553983`.

## Best

`Kp=100, Kd=10`, `risk=0.884339`, `relative_error=0.778557`, `abs_error=0.099802`, `sat_ratio=0.000376`, `qdot_limit_rate=0.003640`.
