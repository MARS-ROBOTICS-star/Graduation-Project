# GitHub upload notes

This run contains the final Stage1 `model_150.pt` checkpoint and its raw TensorBoard event file plus exported TensorBoard scalars under `tensorboard_export/`.

One reward trace exceeded GitHub's normal 100 MB single-file limit:

- `best_terrain_video_records/20260516_005458/reward_traces/stairs_cols05_07_trace.csv`

The original CSV remains in the local run directory. For GitHub archival, the same data is included as:

- `best_terrain_video_records/20260516_005458/reward_traces/stairs_cols05_07_trace.csv.gz`

Recover it with:

```bash
gzip -dk best_terrain_video_records/20260516_005458/reward_traces/stairs_cols05_07_trace.csv.gz
```
