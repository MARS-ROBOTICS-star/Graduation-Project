# Stage1 model_725 30 Hz fine Kp/Kd sweep

- trace_dir: `/home/ubuntu/Graduation-Project/results/stage1_model725_allcols_30hz_fine_pd_2026-05-12/raw_traces`
- trace_glob: `model725_allcols_30hz_col*.csv`
- cases: `30`
- samples: `35972`
- Kp: `100:2000:10`
- Kd: `10:1000:10`
- fixed plant: `J=0.1`, `B=0.5`, `tau_load=0.0`
- fixed limits: `tau_max=60.0`, `qdot_max=2.0`, `tau_v=0.04`
- risk thresholds: `sat_threshold=0.7`, `qdot_limit_threshold=0.7`
- old_relative_error_mean: `0.891246`

## Best

`Kp=170, Kd=30`, `risk=1.021631`, `relative_error=0.816030`, `abs_error=0.103978`, `sat_ratio=0.371340`, `qdot_limit_rate=0.699424`.
