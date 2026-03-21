# Graduation Project

This repository is organized around one immediate objective: get a minimal Isaac Lab RL baseline running for the articulated ground robot as quickly as possible.

## Current layout

- `complete_car*.usd`, `default_scene.usd`, `Spherical_Parallel_test.usd`
  - Root-level USD entry files kept in place to avoid breaking existing relative references.
- `complete_car_alternative/`
  - Main robot package currently used for Isaac Sim validation.
- `complete_car_final/`
  - Alternative/finalized robot package variant for comparison and later migration.
- `docs/`
  - Project notes, status tracking, and design decisions.
- `docs/literature/`
  - Local literature corpus. Keep source PDFs here and MinerU-derived Markdown under `docs/literature/mineru_output/`.
- `scripts/isaac_sim/`
  - Isaac Sim utility scripts for teleoperation and sensor validation.
- `scripts/literature/`
  - Literature conversion and catalog scripts for MinerU-based PDF to Markdown parsing.
- `results/sensor_validation/`
  - Saved outputs from camera, LiDAR, and IMU validation runs.
- `refs/isaac_kb/`
  - Searchable local knowledge base for Isaac Sim 5.1 and Isaac Lab 2.3.x manuals.
- `src/rl_lab/`
  - Isaac Lab RL workspace. The retained baseline is the cleaned single-project training workspace under `src/rl_lab/complete_car_rl_training/`.

## Recommended next code placement

- Build the first runnable complete-car task inside `src/rl_lab/complete_car_rl_training/`.
- Keep task configs and reward/observation logic inside `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/`.
- Keep generated logs and training outputs under `logs/` and `results/`.

## Current priority

1. Build a minimal attitude stabilization environment.
2. Train only the equivalent spherical joint DOFs first.
3. Add wheels and terrain complexity only after the baseline policy runs.
