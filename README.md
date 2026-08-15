# Environment-Adaptive Morphological Control for Specialized Robots Based on Reinforcement Learning

Isaac Lab reinforcement-learning project for a three-body articulated ground vehicle with a spherical-parallel-joint-inspired morphology. 


## Released Contents

This repository is a personal research workspace, not a copy of the original run records or a complete results archive. The publicly tracked parts are:

- `AGENTS.md`: project research background, constraints, role boundaries, and execution route.
- `docs/`: research documents in Markdown, including SVG diagram assets under `docs/assets/`; only the third-party full-text files listed in `.gitignore` are excluded.
- `scripts/`: auxiliary scripts, including Isaac Sim validation / teleoperation, literature conversion helpers, and MATLAB research files.
- `RL_Training/`: Isaac Lab direct-workflow training project.
  - `RL_Training/source/complete_car_lab/`: Isaac Lab direct-workflow task package.
  - `RL_Training/scripts/train.py`: training entry point.
  - `RL_Training/scripts/play.py`: checkpoint replay and video capture entry point.
  - `RL_Training/scripts/`: additional analysis and replay helper scripts.
  - `RL_Training/tests/`: smoke and unit tests.
  - `RL_Training/README.md`: project-internal training / replay quick start.
- `USD/`: robot USD assets used by the task and equivalent / test USD variants (backup files are ignored).
- `URDF/`: robot URDF packages and meshes, including research URDF variants.
- `checkpoints/stage1_model150/model_150.pt`: released Stage1 policy checkpoint.
- `checkpoints/stage1_model150/env.yaml` and `agent.yaml`: saved environment and PPO configuration for the released run.

Kept local only, never uploaded to GitHub:

- `logs/`, `RL_Training/logs/`, `RL_Training/outputs/`, `outputs/`, `results/`
- third-party full-text documents, PDFs, and templates
- caches, credentials, local configuration, and backups

## Dependencies

Tested target stack:

- Ubuntu 22.04
- NVIDIA GPU with a working CUDA driver
- Isaac Sim 5.1
- Isaac Lab 2.3.x
- Python 3.10 from the Isaac Lab environment
- PyTorch version bundled with the Isaac Lab installation

Python packages used by the local extension:

- `psutil`
- `GitPython`
- `tensorboard`
- `gymnasium`
- `imageio` with ffmpeg support for `--stream_video`

## Installation

Set the Isaac Lab root path first:

```bash
export ISAACLAB_PATH=/path/to/IsaacLab
```

Clone and install the task extension:

```bash
git clone git@github.com:MARS-ROBOTICS-star/Graduation-Project.git
cd Graduation-Project/RL_Training
${ISAACLAB_PATH}/isaaclab.sh -p -m pip install -e source/complete_car_lab
```

List the registered tasks:

```bash
${ISAACLAB_PATH}/isaaclab.sh -p source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/utils/list_envs.py
```

Expected task ids:

- `CompleteCar-Stage0`
- `CompleteCar-Stage1`
- `CompleteCar-Stage2`

## Replay

From `RL_Training/`, replay the released Stage1 checkpoint in the Isaac Sim GUI:

```bash
${ISAACLAB_PATH}/isaaclab.sh -p scripts/play.py \
  --task CompleteCar-Stage1 \
  --num_envs 32 \
  --checkpoint ../checkpoints/stage1_model150/model_150.pt \
  --terrain_replay_columns all \
  --terrain_replay_level_range 0:7 \
  --record_global_dolly_view \
  --show_goal_vis
```

Record the same global dolly replay to mp4:

```bash
${ISAACLAB_PATH}/isaaclab.sh -p scripts/play.py \
  --task CompleteCar-Stage1 \
  --headless \
  --num_envs 32 \
  --checkpoint ../checkpoints/stage1_model150/model_150.pt \
  --terrain_replay_columns all \
  --terrain_replay_level_range 0:7 \
  --record_global_dolly_view \
  --show_goal_vis \
  --video \
  --stream_video \
  --video_length 2000 \
  --video_resolution 2560x1440 \
  --video_output_dir ../outputs/replay_videos \
  --video_output_name stage1_model150_global_dolly.mp4
```

For a simpler single-view replay:

```bash
${ISAACLAB_PATH}/isaaclab.sh -p scripts/play.py \
  --task CompleteCar-Stage1 \
  --num_envs 1 \
  --checkpoint ../checkpoints/stage1_model150/model_150.pt \
  --terrain_replay_columns obs \
  --terrain_replay_level 19 \
  --create_follow_views \
  --show_goal_vis
```

## Training

Start a new Stage1 training run:

```bash
cd RL_Training
${ISAACLAB_PATH}/isaaclab.sh -p scripts/train.py \
  --task CompleteCar-Stage1 \
  --headless \
  --device cuda:0 \
  --num_envs 96 \
  --max_iterations 200 \
  --run_name stage1_new_run
```

Warm-start from the released checkpoint:

```bash
${ISAACLAB_PATH}/isaaclab.sh -p scripts/train.py \
  --task CompleteCar-Stage1 \
  --headless \
  --device cuda:0 \
  --num_envs 96 \
  --resume \
  --warmstart \
  --checkpoint ../checkpoints/stage1_model150/model_150.pt \
  --max_iterations 200 \
  --run_name stage1_warmstart_model150
```

Training outputs are written under `RL_Training/logs/` and are ignored by Git by default.

## Notes

- Research documents, auxiliary tools, and training code are public; training logs, TensorBoard exports, results, and generated outputs remain local only and are not part of this GitHub repository.
- This is a personal research workspace, not a complete archive of the original run records or a full original-results repository.
- The released Stage1 checkpoint is useful for visual replay, but it should not be treated as a formal stability proof by itself.
