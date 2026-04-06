# Complete Car RL Training

This directory is the single retained Isaac Lab training project for the articulated complete-car robot.
The project keeps Isaac Lab's normal extension root plus Python package split, and removes the extra task-name nesting
inside the task package so the layout stays shallow enough to maintain.

## Layout

- `complete_car_rl_training/`
  - Python package containing task registration and environment code.
- `docs/`
  - Local project notes such as the TensorBoard reading guide and the RL migration route.
- `scripts/`
  - Utility scripts for listing environments, smoke-testing with dummy agents, training, and playback.
- `tools/ik/`
  - Standalone inverse-kinematics utilities and keyboard test scripts.
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
cd /home/lbz/Graduation-Project/src/rl_lab/complete_car_rl_training
python -m pip install -e . --no-build-isolation
```

If you launch Isaac Sim or Isaac Lab from a non-interactive shell for the first time, accept the Omniverse EULA first or set:

```bash
export OMNI_KIT_ACCEPT_EULA=YES
```

## Task

The current Gym task id is:

```bash
Complete-Car-Rl-Training-v0
```

## Smoke Test

List registered environments:

```bash
python scripts/list_envs.py --keyword Complete-Car
```

Run a zero-action smoke test:

```bash
python scripts/zero_agent.py --task Complete-Car-Rl-Training-v0 --num_envs 32
```

Run a random-action smoke test:

```bash
python scripts/random_agent.py --task Complete-Car-Rl-Training-v0 --num_envs 32
```

## Train

First headless training smoke test:

```bash
python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --headless --device cpu --num_envs 100 --max_iterations 10
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
docs/tensorboard_reading_guide.md
```

The staged RL migration note is:

```bash
docs/rl_training_route.md
```

## Play

Replay the latest checkpoint:

```bash
python scripts/rsl_rl/play.py --task Complete-Car-Rl-Training-v0 --device cpu
```

## IK Tools

Keyboard IK debugging now lives under:

```bash
tools/ik/test_ik_keyboard.py
```

## Key Files

- `complete_car_rl_training/tasks/manager_based/__init__.py`
- `complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- `complete_car_rl_training/tasks/manager_based/complete_car_stage1_env.py`
- `complete_car_rl_training/tasks/manager_based/agents/rsl_rl_ppo_cfg.py`
- `complete_car_rl_training/tasks/manager_based/mdp/rewards.py`
- `tools/ik/test_ik_keyboard.py`
