# Complete Car RL Training

This directory is the single retained Isaac Lab training project for the articulated complete-car robot.
The project keeps Isaac Lab's normal extension root plus Python package split, and currently uses a flat staged package
layout under `complete_car_rl_training/`.

## Layout

- `complete_car_rl_training/`
  - Python package containing task registration and environment code.
  - `tasks/direct/complete_car/`
    - Direct-workflow task package.
    - `complete_car_env.py`
      - shared `DirectRLEnv` implementation.
    - `complete_car_env_cfg.py`
      - shared direct config trunk.
    - `stage0_flat_cfg.py`
      - Stage 0 flat baseline.
    - `stage1_terrain_cfg.py`
      - Stage 1 terrain + curriculum.
    - `stage2_perception_cfg.py`
      - Stage 2 perception-ready config.
    - `rewards.py`, `observations.py`, `commands.py`, `terminations.py`
      - pure tensor helpers.
    - `terrain/`
      - terrain generator and terrain runtime helper.
    - `sensors/`
      - camera / lidar / imu runtime helper.
    - `assets/robot_cfg.py`
      - robot articulation config and joint-name constants.
    - `agents/ppo_cfg.py`
      - RSL-RL runner configs for the three direct stages.
  - `paths.py`
    - Shared project-root and asset-path discovery.
- `docs/`
  - Local project notes such as the TensorBoard reading guide and the RL migration route.
- `rsl_rl/`
  - Vendored local copy of the active RSL-RL runner / PPO / model implementation used by training and playback.
- `scripts/`
  - Utility scripts for listing environments, smoke-testing with dummy agents, training, and playback.
- `Kinematic Model/IK/`
  - Inverse-kinematics utilities and keyboard validation scripts.
- `skills/`
  - Repository-local skill definitions before installation into `~/.codex/skills/`.
- `config/extension.toml`
  - Isaac Lab extension metadata.
- `setup.py`, `pyproject.toml`
  - Editable install and local tooling configuration. These stay at the project root because Isaac Lab resolves the
    extension from this directory.

## Install

Run from this directory:

```bash
cd /home/ubuntu/Graduation-Project/RL_Training
python -m pip install -e . --no-build-isolation
```

This editable install now also exposes the vendored local `rsl_rl/` package bundled in this repository, so the
training entrypoints no longer depend on the external `rsl-rl-lib` implementation at runtime.

If you launch Isaac Sim or Isaac Lab from a non-interactive shell for the first time, accept the Omniverse EULA first or set:

```bash
export OMNI_KIT_ACCEPT_EULA=YES
```

## Tasks

Current Gym task ids:

```bash
Complete-Car-Stage0-Flat-Direct-v0
Complete-Car-Stage1-Terrain-Direct-v0
Complete-Car-Stage2-Perception-Direct-v0
```

## Smoke Test

List registered environments:

```bash
python scripts/list_envs.py --keyword Complete-Car
```

Run a zero-action smoke test:

```bash
python scripts/zero_agent.py --task Complete-Car-Stage0-Flat-Direct-v0 --num_envs 32
```

Run a random-action smoke test:

```bash
python scripts/random_agent.py --task Complete-Car-Stage0-Flat-Direct-v0 --num_envs 32
```

## Train

First headless training smoke test:

```bash
python scripts/rsl_rl/train.py --task Complete-Car-Stage0-Flat-Direct-v0 --headless --num_envs 100 --max_iterations 10
```

Training logs are written under:

```bash
logs/rsl_rl/complete_car_rl_training/
```

After each training run, TensorBoard scalar data is also exported automatically into plain files under:

```bash
logs/rsl_rl/complete_car_rl_training/<run_timestamp>/tensorboard_export/
```

You can re-export an existing run manually with:

```bash
python scripts/tensorboard_export.py --run_dir logs/rsl_rl/complete_car_rl_training/<run_timestamp>
```

The project-level reading guide for TensorBoard and offline diagnosis is:

```bash
docs/training_workflow_and_tensorboard_guide.md
```

## Play

Replay the latest checkpoint:

```bash
python scripts/rsl_rl/play.py --task Complete-Car-Stage0-Flat-Direct-v0
```

## IK Tools

Keyboard IK debugging now lives under:

```bash
Kinematic Model/IK/test_ik_keyboard.py
```

## Key Files

- `complete_car_rl_training/__init__.py`
- `complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
- `complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
- `complete_car_rl_training/tasks/direct/complete_car/assets/robot_cfg.py`
- `complete_car_rl_training/tasks/direct/complete_car/terrain/terrain_generator.py`
- `complete_car_rl_training/tasks/direct/complete_car/terrain/terrain_runtime.py`
- `Kinematic Model/IK/test_ik_keyboard.py`
