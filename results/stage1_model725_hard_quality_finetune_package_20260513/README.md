# Stage1 model_725 hard-quality fine-tune package

## Package identity

- Run name: `stage1_model725_hard_quality_finetune_96env_300iter_20260513`
- Run directory: `RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-13_00-42-29_stage1_model725_hard_quality_finetune_96env_300iter_20260513`
- Task: `CompleteCar-Stage1`
- Launch mode: headless, `cuda:0`, `96 env`
- Resume source: `2026-05-11_12-20-55_stage1_80env_resume_from_m100_1000iter_20260511_1220/model_725.pt`
- Training range: PPO iteration `725 -> 1024`
- Final checkpoint: `run/model_1024.pt`

## Contents

- `run/`
  - full RSL-RL run directory
  - TensorBoard event file
  - checkpoints from `model_725.pt` through `model_1024.pt`
  - `params/env.yaml` and `params/agent.yaml`, which are the canonical environment and PPO config snapshots used by this run
  - `git/Graduation-Project.diff`, the code diff snapshot saved by the runner
- `logs/runtime.log`
  - runtime stdout/stderr log for the training command
- `logs/isaaclab.log`
  - IsaacLab startup log for this run
- `analysis/row_summary_last25.csv`
  - per-terrain level and row-advance summary using the last 25 PPO scalar points
- `analysis/hard_quality_last25.csv`
  - hard-terrain motion-quality diagnostic summary using the last 25 PPO scalar points
- `analysis/global_quality_last25.csv`
  - global quality and reward diagnostic summary using the last 25 PPO scalar points

## Main result summary

- Obstacles improved clearly: `col08_obstacles` last-25 mean level was about `14.52`, and `col09_obstacles` was about `12.32`.
- Stairs down regressed from the mid-run level around row `10` to last-25 mean row about `5.6-5.7`.
- Stairs quality remained weak:
  - rear follow about `0.22-0.23`
  - row contact support minimum about `0.027-0.030`
  - near-edge overspeed about `0.92-0.93`
  - quality advance score near `0`
- This package records the old single-frame-observation 725 fine-tune result. It is not the later history4 run.

