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
- `scripts/isaac_sim/`
  - Isaac Sim utility scripts for teleoperation and sensor validation.
- `results/sensor_validation/`
  - Saved outputs from camera, LiDAR, and IMU validation runs.
- `refs/isaac_kb/`
  - Searchable local knowledge base for Isaac Sim 5.1 and Isaac Lab 2.3.x manuals.
- `src/rl_lab/`
  - Reserved location for the minimal Isaac Lab RL environment and training code.

## Recommended next code placement

- Put the first runnable Isaac Lab task under `src/rl_lab/`.
- Keep task configs and reward/observation logic close to the environment code.
- Keep generated logs and training outputs under `logs/` and `results/`.

## Current priority

1. Build a minimal attitude stabilization environment.
2. Train only the equivalent spherical joint DOFs first.
3. Add wheels and terrain complexity only after the baseline policy runs.
