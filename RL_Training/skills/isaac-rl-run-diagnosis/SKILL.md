---
name: isaac-rl-run-diagnosis
description: Use this skill when the user provides an Isaac Lab log path or a run timestamp and wants a complete training diagnosis for the complete-car RL project, including simulator log inspection, Hydra and run config lookup, TensorBoard scalar export if missing, and a report based on core charts and CSV files.
---

# Isaac RL Run Diagnosis

## Overview

Use this skill for one job only: diagnose one Isaac Lab training run in the complete-car RL project from a log path or run timestamp.

Default input form:

- `/tmp/isaaclab/logs/isaaclab_YYYY-MM-DD_HH-MM-SS.log`

Expected output:

- one concise training diagnosis report
- based on simulator log, resolved config, TensorBoard offline export, and core scalar trends

## Required workflow

1. Parse the timestamp from the user input.
2. Read the Isaac Lab simulator log at the given path.
3. Locate the matching Hydra output directory:
   - `outputs/YYYY-MM-DD/HH-MM-SS/`
4. Locate the matching training run directory:
   - `logs/rsl_rl/complete_car_rl_training/YYYY-MM-DD_HH-MM-SS/`
5. Read these files when present:
   - Isaac log file
   - `outputs/.../.hydra/config.yaml`
   - `outputs/.../.hydra/overrides.yaml`
   - `logs/.../params/env.yaml`
   - `logs/.../params/agent.yaml`
6. If `tensorboard_export/` is missing under the run directory, run:
   - `python scripts/tensorboard_export.py --run_dir <run_dir>`
7. Read:
   - `tensorboard_export/latest_values.csv`
   - `tensorboard_export/summary.json`
   - the core scalar CSVs listed below
8. Produce a diagnosis report using the report structure in this skill.

## Core scalar CSVs to inspect

Always inspect these first:

- `Train__mean_reward.csv`
- `Train__mean_episode_length.csv`
- `Episode_Termination__time_out.csv`
- `Episode_Termination__root_too_low.csv`
- `Episode_Termination__bad_orientation.csv`
- `Metrics__base_velocity__error_vel_xy.csv`
- `Metrics__base_velocity__error_vel_yaw.csv`
- `Episode_Reward__track_lin_vel_xy_exp.csv`
- `Episode_Reward__track_ang_vel_z_exp.csv`
- `Episode_Reward__action_rate_l2.csv`
- `Loss__value.csv`
- `Loss__surrogate.csv`
- `Loss__entropy.csv`
- `Policy__mean_std.csv`

Inspect additional scalar CSVs only if they materially affect the diagnosis.

## Interpretation rules

Prioritize reading the run in this order:

1. Survival
   - `Train/mean_episode_length`
   - `Episode_Termination/*`
2. Task learning
   - `Train/mean_reward`
   - velocity error metrics
   - velocity tracking rewards
3. Control quality
   - action smoothness
   - stability penalties
4. Numerical stability
   - PPO losses
   - policy std
5. Throughput
   - `Perf/*`

Use these conclusions consistently:

- If `mean_episode_length` rises strongly and `time_out` approaches `1.0`, rollout survival improved.
- If `root_too_low` or `bad_orientation` stays high, the environment is still unhealthy.
- If episode length improves but velocity error remains high, the policy is learning to survive more than to track commands.
- If tracking rewards rise while velocity errors fall, the task objective is being learned.
- If `action_rate_l2` becomes strongly more negative, control is becoming jerky.
- If losses explode or become highly unstable, report numerical instability before reward interpretation.

## Report structure

Use this exact high-level structure:

### 1. Run Identification

- user-provided log path
- matched Hydra directory
- matched run directory
- whether checkpoints exist

### 2. Startup and Configuration

- device
- num_envs
- major simulator warnings or errors
- articulation / actuator / manager resolution status

### 3. Core Training Outcome

- `Train/mean_reward`: first -> last
- `Train/mean_episode_length`: first -> last
- dominant termination mode at the end
- whether this run is mainly:
  - failed startup
  - unhealthy rollout
  - survival improvement
  - tracking improvement

### 4. Reward and Error Diagnosis

- linear velocity tracking
- yaw tracking
- stability penalties
- action smoothness penalty

### 5. Numerical Stability

- value loss
- surrogate loss
- entropy
- policy mean std

### 6. Diagnosis

- one sentence on the biggest positive signal
- one sentence on the main current problem
- 1 to 3 next-step actions, ordered by priority

## Repository-specific references

For metric meaning and chart-reading rules, read this file when needed:

- `/home/ubuntu/Graduation-Project/RL_Training/docs/training_workflow_and_tensorboard_guide.md`

For exported TensorBoard files, use:

- `/home/ubuntu/Graduation-Project/RL_Training/scripts/tensorboard_export.py`

## Invocation example

Use `$isaac-rl-run-diagnosis` to diagnose this run from the Isaac Lab log path: `/tmp/isaaclab/logs/isaaclab_2026-03-19_13-13-03.log`
