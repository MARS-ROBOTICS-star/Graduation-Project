# Graduation Project

This repository is the long-term working tree for an undergraduate robotics thesis on an articulated ground vehicle with spherical-parallel-joint-inspired morphology. It contains robot assets, Isaac Sim validation scripts, Isaac Lab RL projects, literature notes, and thesis-writing materials.

## Active RL Mainline

The active runnable RL mainline is now the in-place refactored `RL_Training/` project.

- `RL_Training/`
  - new Isaac Lab direct-workflow project with `source/complete_car_lab/...` extension layout
  - shared env main class:
    - `source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/env.py`
  - shared config trunk:
    - `source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/base/complete_car_cfg.py`
  - stage configs:
    - `baseline/complete_car_stage0_cfg.py`
    - `baseline/complete_car_stage1_cfg.py`
    - `environment_adaptive/complete_car_stage2_cfg.py`
  - vendored PPO runtime body:
    - `source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/`
  - helper utilities:
    - `source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/`
  - preserved kinematics references:
    - `kinematics/ik_solver.py`
    - `kinematics/fk_solver.py`
    - `kinematics/legacy_ik/`
    - `kinematics/legacy_fk/`
  - task ids:
    - `CompleteCar-Stage0`
    - `CompleteCar-Stage1`
    - `CompleteCar-Stage2`
  - launch scripts:
    - `scripts/train.py`
    - `scripts/play.py`

The temporary parallel directory created in the previous round has been removed. Future RL refactor work should only target `RL_Training/`.

## Repository Map

- `AGENTS.md`
  - Repository-level rules, project background, role boundary, and memory-update policy.
- `docs/`
  - Persistent project memory, workflow notes, literature notes, and architecture references.
  - `stage0_baseline参数详情表.md` records the active Stage0 baseline parameters, `best_baseline_2` run config, and low-level motion model.
  - `Stage1参数详情表.md` records the active Stage1 RL environment, terrain curriculum, height patch, PPO, and warm-start parameters.
- `logs/`
  - Date-based work log.
- `RL_Training/`
  - Current active Isaac Lab RL refactor project.
- `scripts/isaac_sim/`
  - Isaac Sim validation, keyboard control, USD inspection, and asset-repair helpers.
- `USD/`
  - Active USD assets and configuration sublayers.
- `results/`
  - Generated outputs such as logs and sensor validation artifacts.
- `refs/isaac_kb/`
  - Local Isaac Sim 5.1 and Isaac Lab 2.3.x references.
- `docs/literature/`
  - Local paper corpus and converted markdown outputs.
  - Source PDFs are organized under `综述论文/` and `研究论文/`; converted Markdown stays in `opendataloader_output/`.
  - `lunwen/` currently stores the Chapter 1 thesis-reading corpus, grouped by writing function into development/application, morphology/structure, model-based control, terrain perception/planning, RL terrain control, and learning-transfer subfolders.
- `毕业论文/`
  - Thesis template, LaTeX sources, and compiled artifacts.

## Where To Work

- Active RL refactor code:
  - `RL_Training/`
- Isaac Sim validation and teleoperation:
  - `scripts/isaac_sim/`
- Robot USD assets:
  - `USD/`
- Literature notes and PDFs:
  - `docs/literature/`
- Thesis writing:
  - `毕业论文/毕业论文模板/LaTeX/`

## Practical Rule

If a task is about the current runnable RL refactor, default to `RL_Training/`.

If a task is about project continuity, start from `AGENTS.md`, `docs/current_status.md`, `docs/conversation_history.md`, `logs/daily_work_log.md`, and then this README.
