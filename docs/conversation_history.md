# Conversation History

This file stores durable conclusions from past Codex sessions so that future sessions can continue work without relying on ephemeral chat history alone.

## 2026-03-16

### RL code path consolidation
- Removed the repository-local handwritten direct-workflow skeleton under `src/rl_lab/tasks/complete_car_attitude_direct/`.
- Kept `src/rl_lab/complete_car_rl_training/` as the single retained Isaac Lab project scaffold.
- Decided to use the external template project as the canonical place to evolve the complete-car RL task.
- For the current project stage, manager-based workflow is the preferred starting path because it exposes observations, actions, resets, rewards, and terminations as separate config-managed blocks while the baseline task is still being assembled.

### Repository organization baseline
- Reorganized the repository around a minimal Isaac Lab RL baseline workflow.
- Kept root-level USD files in place to avoid breaking existing relative references.
- Moved Isaac Sim helper scripts to `scripts/isaac_sim/`.
- Moved sensor validation outputs to `results/sensor_validation/`.
- Moved Isaac Sim and Isaac Lab local references to `refs/isaac_kb/`.
- Reserved `src/rl_lab/` for the runnable RL environment and training code.

### Path handling improvements
- Updated Isaac Sim scripts to resolve project paths from the repository root instead of relying on fixed absolute paths.

### Project memory policy
- Established that future Codex sessions should read `AGENTS.md`, `README.md`, `docs/current_status.md`, `docs/conversation_history.md`, and `logs/daily_work_log.md` as startup context.
- Established that Isaac Sim and Isaac Lab work should consult `refs/isaac_kb/` before online search.

### Current project stage
- The immediate target remains a minimal Isaac Lab RL environment for attitude stabilization using the two equivalent 3-DOF spherical joints.

## 2026-03-16

### Isaac Lab asset validation result
- Added `scripts/isaac_sim/check_isaaclab_asset.py` to validate the articulated car USD through Isaac Lab headless.
- Confirmed that the host Isaac Lab and Isaac Sim executables are available locally.
- Confirmed that the current asset entry file is `USD/complete_car_alternative.usd`.
- Validation showed that the USD cannot yet be used directly as an Isaac Lab articulation asset.

### Blocking issues found
- `USD/complete_car_alternative.usd` has no default prim.
- The USD still payloads `configuration/complete_car_alternative_physics.usd`, `configuration/complete_car_alternative_sensor.usd`, and `configuration/complete_car_alternative_robot.usd`.
- Those `configuration/*.usd` files are currently missing from the repository path expected by the USD.
- Isaac Lab reported an unresolved reference prim path when trying to spawn the asset under `/World/envs/env_0/Robot`.

### Consequence for next step
- Before building the RL environment, the robot USD package must be repaired or re-exported so Isaac Lab can spawn it as a valid articulation.

## 2026-03-16

### Revalidation with repaired asset entry
- Re-ran the Isaac Lab asset check after the user switched the entry file to `USD/complete_car.usd`.
- Confirmed that the file now opens and the stage contains `/World/complete_car_alternative`.
- Confirmed that `/World/complete_car` does not exist in the USD stage, so the effective robot root name is still `complete_car_alternative`.

### Remaining blocking issues
- `USD/complete_car.usd` still has no default prim.
- Isaac Sim reported unresolved references under `USD/configuration/default_scene_base.usd` to `default_scene_physics.usd`.
- Isaac Lab still reported an unresolved reference prim path when trying to spawn `USD/complete_car.usd` as an asset.

### Environment note
- The local `env_isaaclab` directory is a Python venv, not a conda environment.
- The currently reliable execution path on this machine is still `env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV /home/ubuntu/IsaacLab/isaaclab.sh -p ...`, which uses `/home/ubuntu/IsaacLab/_isaac_sim/python.sh`.

## 2026-03-16

### USD repair outcome
- Repaired `USD/complete_car.usd` by setting its default prim to `/World`.
- Cleared the four broken visual-only references in `USD/configuration/default_scene_base.usd`:
  - `spm1_spherical_virtual_y/visuals`
  - `spm1_spherical_virtual_z/visuals`
  - `spm2_spherical_virtual_y/visuals`
  - `spm2_spherical_virtual_z/visuals`
- After repair, USD inspection confirms:
  - `default prim = /World`
  - the problematic `visuals` prims no longer carry broken references
  - the robot root remains `/World/complete_car_alternative`

### Isaac Lab validation after repair
- Re-ran the Isaac Lab headless asset check on `USD/complete_car.usd`.
- Isaac Lab now reaches articulation initialization successfully.
- The log reports `0 != 12`, which confirms the asset is recognized as a 12-joint articulation.
- The remaining warning is expected for the check script because no actuators are configured yet.
- The check command tends to hang during shutdown, so timeout-based verification is currently more reliable than waiting for clean exit.

## 2026-03-17

### Complete-car manager-based env first pass
- Replaced the template cartpole env config in `src/rl_lab/complete_car_rl_training/.../complete_car_rl_training_env_cfg.py` with a complete-car manager-based configuration.
- The environment now uses `USD/complete_car.usd` through a repository-relative `ArticulationCfg`.
- The articulation is configured with two actuator groups:
  - 6 equivalent spherical-joint DOFs as position-controlled ball joints
  - 6 wheel joints as velocity-controlled wheel joints
- The action space is now 12-dimensional:
  - 6 ball-joint position actions
  - 6 wheel velocity actions

### Forward/backward training design choice
- Chose to support both forward and backward motion through `UniformVelocityCommandCfg` instead of hard-coding a forward-only reward.
- The command range is currently:
  - `lin_vel_x in [-1.0, 1.0]`
  - `lin_vel_y = 0.0`
  - `ang_vel_z = 0.0`
- Policy observations now include the sampled velocity command so one policy can respond to both positive and negative target speeds.

### Observation/reset/reward/termination baseline
- Observation design now avoids using wheel joint positions because continuous wheel rotation would create unbounded observations.
- The current policy observation baseline is:
  - base linear velocity
  - base angular velocity
  - projected gravity
  - commanded base velocity
  - ball-joint relative positions
  - ball-joint relative velocities
  - wheel relative velocities
  - previous action
- Reset baseline now includes:
  - random root pose/yaw and small root velocity perturbations
  - random ball-joint offsets
  - wheel joints reset to zero
- Reward baseline now uses velocity tracking plus posture/stability penalties.
- Termination baseline now uses:
  - timeout
  - bad orientation
  - root height below threshold
  - ball-joint manual limit violation

### Validation status
- Python syntax validation of the updated env config passed with `python3 -m py_compile`.
- Isaac Lab runtime validation has not yet been executed after the env rewrite, so actuator values and reward weights remain provisional.

## 2026-03-18

### Scene ownership decision
- Removed the manager-scene `ground` and `dome_light` definitions from the complete-car environment config.
- The current default assumption is that `USD/complete_car.usd` already contains the required ground and lighting for the first baseline run.
- This avoids duplicating scene elements at the config layer, but the multi-environment runtime behavior still needs validation.

### Collaboration constraints update
- Added two repository-level instructions to `AGENTS.md`:
  - use first-principles thinking and stop to clarify when the real goal is ambiguous
  - when proposing modification/refactor plans, avoid compatibility patches, transition designs, fallback branches, and unvalidated logic
- These constraints should be treated as durable collaboration rules for future sessions.

### PPO logging name cleanup
- Updated the RSL-RL runner `experiment_name` from the leftover template value `cartpole_direct` to `complete_car_rl_training`.
- Training logs should now be grouped under the complete-car task name instead of the cartpole template name.

### Training project structure cleanup
- Flattened `src/rl_lab/complete_car_rl_training/` into a single project root.
- Removed the duplicated template shell under `source/complete_car_rl_training/`.
- Moved the live package to `src/rl_lab/complete_car_rl_training/complete_car_rl_training/`.
- Moved `setup.py` and `config/extension.toml` to the project root and changed the editable install path to `pip install -e .`.
- Removed the nested `.git`, `.vscode`, UI example module, and the empty legacy `src/rl_lab/tasks/` leftover.
- Updated `setup.py` to use standard-library `tomllib` on Python 3.11, with `tomli` fallback for Python 3.10, so editable install no longer depends on the third-party `toml` package in the common case.
- Future sessions should treat the cleaned single-root structure as canonical and should not reintroduce the old template shell.

## 2026-03-18

### First end-to-end training launch result
- The correct Gym task id is `Complete-Car-Rl-Training-v0`.
- The previously used underscored / misspelled form `Complete_Car_RL_Trainging-v0` is not registered and should not be reused.
- From the cleaned project root, the reliable launch path remains:
  - `env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV /home/ubuntu/IsaacLab/isaaclab.sh -p ...`

### Install and launch constraint in this environment
- `pip install -e .` is not a reliable default in the current restricted terminal session:
  - build isolation tried to fetch `setuptools<82.0.0` from the network
  - `--no-build-isolation` progressed further but then failed because the user site path under `/home/ubuntu/.local/lib` is read-only in this sandbox
- For this session, adding the training project root to `PYTHONPATH` was sufficient to run the scripts without editable install.

### Training runner device fix
- Updated `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py` so `--device` overrides both:
  - `env_cfg.sim.device`
  - `agent_cfg.device`
- Reason: before this fix, `--device cpu` only moved the environment to CPU while the RSL-RL runner still tried to place the policy on CUDA and crashed with `RuntimeError: No CUDA GPUs are available`.
- Impact: the same launch script can now be used for CPU smoke training when CUDA is unavailable in the current session.

### CPU training smoke result
- Ran headless training successfully with:
  - task `Complete-Car-Rl-Training-v0`
  - `num_envs = 100`
  - `device = cpu`
- The environment completed creation, simulation start, manager setup, and entered stable RSL-RL learning iterations.
- A training run directory was created at:
  - `src/rl_lab/complete_car_rl_training/logs/rsl_rl/complete_car_rl_training/2026-03-18_17-14-07/`
- Confirmed outputs include:
  - `events.out.tfevents...`
  - `model_0.pt`
  - `model_50.pt`

### Runtime issues found during the first real training run
- `USD/complete_car.usd` still contains remote asset references that fail in offline execution:
  - `defaultGroundPlane` references `default_environment.usd`
  - `Example_Rotary` references `Example_Rotary.usda`
- The replicated multi-environment run reported:
  - `Replication of this type is not supported ... /World/envs/env_0/Robot/PhysicsScene`
- This indicates the robot USD should not carry an embedded `PhysicsScene` when used as a replicated Isaac Lab asset.

### Training behavior conclusion
- The RL loop is now proven end-to-end, but the current task is not yet healthy.
- During the observed learning iterations, `Episode_Termination/root_too_low` stayed at `1.0`, while mean episode length remained around `12.3`.
- Conclusion: the immediate next work is no longer "make training launch", but rather:
  - clean the USD for offline replicated use
  - remove embedded physics-scene ownership from the robot asset
  - tune reset / height threshold / reward terms so episodes do not terminate almost immediately by low root height
