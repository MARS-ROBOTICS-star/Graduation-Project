# Stage1 80env Resume From M100 Results Config Package Manifest

## Run

- Run directory: `RL_Training/logs/rsl_rl/complete_car_stage1/2026-05-11_12-20-55_stage1_80env_resume_from_m100_1000iter_20260511_1220`
- Runtime log: `RL_Training/logs/runtime/stage1_80env_resume_from_m100_1000iter_20260511_1220.log`
- Task: `CompleteCar-Stage1`
- Env count: `80`
- Resume source: `2026-05-11_11-24-20_stage1_96env_1000iter_20260511_112415/model_100.pt`
- Planned iterations: `1000`
- Completed status: reached final checkpoint `model_1099.pt`

## Included

- TensorBoard event file and exported scalar CSV/JSON.
- Run `params/agent.yaml` and `params/env.yaml`.
- Run `git/Graduation-Project.diff`.
- Runtime console log.
- Current Stage1 configuration and related source files.
- Current Stage1 project notes and evaluation documents.

## Excluded

- Training checkpoints: `model_*.pt`.
- Exported policy files under `exported/`.
- Replay videos under `videos/`.
- Python bytecode caches: `__pycache__/`, `*.pyc`.

## Notes

- This package is intended for result/config analysis, not model replay.
- For hard terrain replay outside this package, current recommended overall checkpoint is `model_900.pt`.
