# Graduation Project

This repository is the long-term working tree for an undergraduate robotics thesis on an articulated ground vehicle with spherical-parallel-joint-inspired morphology. The project combines robot assets, Isaac Sim validation scripts, Isaac Lab RL training code, literature reading notes, and thesis-writing materials in one place.

## Active Mainline

The current engineering mainline is the single Isaac Lab project under `RL_Training/`.
Its active RL package structure now uses Isaac Lab's direct workflow:

- `complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
  - the single `DirectRLEnv` task implementation
- `complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
  - the shared direct config trunk
- `complete_car_rl_training/tasks/direct/complete_car/stage0_flat_cfg.py`
  - Stage 0 flat-ground config
- `complete_car_rl_training/tasks/direct/complete_car/stage1_terrain_cfg.py`
  - Stage 1 terrain + curriculum config
- `complete_car_rl_training/tasks/direct/complete_car/stage2_perception_cfg.py`
  - Stage 2 perception config
- `kinematics/wheel_speed_allocator.py`
  - measured-geometry wheel-speed allocation and Jacobian helper shared by validation and direct env runtime
- `complete_car_rl_training/tasks/direct/complete_car/terrain/`
  - terrain generation and runtime helper
- `complete_car_rl_training/tasks/direct/complete_car/sensors/`
  - camera / lidar / imu runtime helper

The current research stage is:

1. Stage 0 completed: prove `reset -> step -> reward -> termination -> train` works end to end.
2. Current code mainline has been refactored to direct workflow, with staged configs for `flat -> terrain -> perception`.
3. Runtime smoke in a real Isaac Lab environment is still pending after the direct refactor.

## Repository Map

- `AGENTS.md`
  - Repository-level rules, project background, role boundary, and persistent-memory policy.
- `docs/`
  - Project memory, workflow notes, and literature workspace.
- `docs/complete_car_direct_workflow_architecture.md`
  - Long-form architecture reference for the active direct-workflow RL mainline.
- `docs/project_file_map.md`
  - Detailed Chinese map of the repository structure and the role of each major file group.
- `logs/`
  - Date-based work log.
- `RL_Training/`
  - The only active Isaac Lab RL code workspace, including the Python package, launch scripts, docs, skills, and IK utilities.
- `RL_Training/kinematics/`
  - Standalone vehicle-kinematics helpers, including the wheel-speed allocator used by the direct RL mainline.
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
- `RL_Training/Kinematic Model/`
  - Current forward/inverse-kinematics derivation workspace and IK validation utilities.

## Where To Work

- RL environment logic:
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/`
- Wheel-speed allocation and vehicle Jacobian helpers:
  - `RL_Training/kinematics/`
- RL terrain runtime:
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terrain/`
- RL sensor runtime:
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/sensors/`
- RL launch scripts:
  - `RL_Training/scripts/`
- Architecture reference docs:
  - `docs/complete_car_direct_workflow_architecture.md`
- Isaac Sim validation and teleoperation:
  - `scripts/isaac_sim/`
- Literature notes and PDFs:
  - `docs/literature/`
- Thesis writing:
  - `毕业论文/毕业论文模板/LaTeX/`

## Practical Rule

If a task is about runnable RL code, default to `RL_Training/`.

If a task is about robot assets or simulator-side validation, inspect `USD/` and `scripts/isaac_sim/` first.

If a task is about project continuity, start from `AGENTS.md`, `docs/current_status.md`, `docs/conversation_history.md`, `logs/daily_work_log.md`, and then this README.
