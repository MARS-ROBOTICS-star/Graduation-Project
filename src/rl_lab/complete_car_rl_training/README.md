# Complete Car RL Training

This directory is the single retained Isaac Lab training project for the articulated complete-car robot.
The project has been cleaned up from the original template into one project root with one Python package.

## Layout

- `complete_car_rl_training/`
  - Python package containing task registration and environment code.
- `scripts/`
  - Utility scripts for listing environments, smoke-testing with dummy agents, training, and playback.
- `config/extension.toml`
  - Isaac Lab extension metadata.
- `setup.py`, `pyproject.toml`
  - Editable install and local tooling configuration.

## Install

Run from this directory:

```bash
cd /home/ubuntu/isaacsim/Graduation-Project/src/rl_lab/complete_car_rl_training
env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV /home/ubuntu/IsaacLab/isaaclab.sh -p -m pip install -e .
```

## Task

The current Gym task id is:

```bash
Complete-Car-Rl-Training-v0
```

## Smoke Test

List registered environments:

```bash
env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV /home/ubuntu/IsaacLab/isaaclab.sh -p scripts/list_envs.py --keyword Complete-Car
```

Run a zero-action smoke test:

```bash
env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV /home/ubuntu/IsaacLab/isaaclab.sh -p scripts/zero_agent.py --task Complete-Car-Rl-Training-v0 --num_envs 32
```

Run a random-action smoke test:

```bash
env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV /home/ubuntu/IsaacLab/isaaclab.sh -p scripts/random_agent.py --task Complete-Car-Rl-Training-v0 --num_envs 32
```

## Train

First headless training smoke test:

```bash
env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV /home/ubuntu/IsaacLab/isaaclab.sh -p scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --headless --num_envs 256 --max_iterations 10
```

Training logs are written under:

```bash
logs/rsl_rl/complete_car_rl_training/
```

## Play

Replay the latest checkpoint:

```bash
env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV /home/ubuntu/IsaacLab/isaaclab.sh -p scripts/rsl_rl/play.py --task Complete-Car-Rl-Training-v0
```

## Key Files

- `complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_rl_training_env_cfg.py`
- `complete_car_rl_training/tasks/manager_based/complete_car_rl_training/agents/rsl_rl_ppo_cfg.py`
- `complete_car_rl_training/tasks/manager_based/complete_car_rl_training/mdp/rewards.py`
