# Graduation Project

This repository is the long-term working tree for an undergraduate robotics thesis on an articulated ground vehicle with spherical-parallel-joint-inspired morphology. The project combines robot assets, Isaac Sim validation scripts, Isaac Lab RL training code, literature reading notes, and thesis-writing materials in one place.

## Active Mainline

The current engineering mainline is the single Isaac Lab project under `src/rl_lab/complete_car_rl_training/`.

The current research stage is:

1. Stage 0 completed: prove `reset -> step -> reward -> termination -> train` works end to end.
2. Stage 1 ongoing: flat ground, proprioception, fixed spherical joints, goal-directed locomotion, wheel control only.
3. Stage 2 later: add spherical-joint control, lower-level PID plus IK mapping, diverse terrain, and perception fusion.

## Repository Map

- `AGENTS.md`
  - Repository-level rules, project background, role boundary, and persistent-memory policy.
- `docs/`
  - Project memory, workflow notes, and literature workspace.
- `docs/project_file_map.md`
  - Detailed Chinese map of the repository structure and the role of each major file group.
- `logs/`
  - Date-based work log.
- `src/rl_lab/complete_car_rl_training/`
  - The only active Isaac Lab RL code workspace.
- `scripts/isaac_sim/`
  - Isaac Sim validation, keyboard control, USD inspection, and asset-repair helpers.
- `scripts/literature/`
  - MinerU conversion and literature-manifest helpers.
- `USD/`
  - Active USD entry files and their configuration sublayers.
- `complete_car_alternative/`, `complete_car_final/`
  - Robot package exports used as asset references and comparison baselines.
- `results/`
  - Saved outputs such as sensor validation dumps and IK keyboard logs.
- `refs/isaac_kb/`
  - Local Isaac Sim 5.1 and Isaac Lab 2.3.x manuals.
- `docs/literature/`
  - Local paper corpus, MinerU outputs, and curated PDF subsets.
- `毕业论文/`
  - Thesis template, LaTeX sources, and compiled thesis artifacts.
- `Drawing/`
  - CAD and illustration assets.
- `IK_iteration.md`, `IK_iteration.mlx`
  - Symbolic inverse-kinematics derivation workspace.

## Where To Work

- RL environment logic:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/`
- RL launch scripts:
  - `src/rl_lab/complete_car_rl_training/scripts/`
- Isaac Sim validation and teleoperation:
  - `scripts/isaac_sim/`
- Literature notes and PDFs:
  - `docs/literature/`
- Thesis writing:
  - `毕业论文/毕业论文模板/LaTeX/`

## Practical Rule

If a task is about runnable RL code, default to `src/rl_lab/complete_car_rl_training/`.

If a task is about robot assets or simulator-side validation, inspect `USD/` and `scripts/isaac_sim/` first.

If a task is about project continuity, start from `AGENTS.md`, `docs/current_status.md`, `docs/conversation_history.md`, `logs/daily_work_log.md`, and then this README.
