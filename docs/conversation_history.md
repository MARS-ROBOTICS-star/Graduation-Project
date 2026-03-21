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

### Scene ownership fix for training assets
- Confirmed the correct Isaac Lab split for this project:
  - `USD/complete_car.usd` should contain only the articulated robot and robot-mounted sensor prims
  - ground and light should be spawned from the Isaac Lab scene configuration
  - world-level `PhysicsScene` and environment props should not be baked into the robot USD used for replicated RL environments
- Updated `CompleteCarRlTrainingSceneCfg` to own:
  - a ground asset
  - a dome light asset
- Clarified the two current remote asset references:
  - scene ground via `default_environment.usd`
  - robot-mounted lidar/sample sensor via `Example_Rotary.usda`
- The user chose to keep the scene ground on the standard Isaac Sim `default_environment.usd` path instead of the temporary local cuboid-ground workaround.
- Durable conclusion:
  - keep ground/light ownership in Isaac Lab scene config
  - keep `default_environment.usd` only as a scene-level dependency, not inside the robot USD
  - treat `Example_Rotary.usda` as the remaining robot-asset remote dependency to clean next

## 2026-03-18

### Direct Python launch revalidation in conda environment
- Revalidated the startup path in the active `env_isaacLab` conda environment instead of relying on the older `isaaclab.sh -p` wrapper documented earlier.
- Confirmed that Isaac Lab and Isaac Sim are importable directly from:
  - `/home/ubuntu/miniconda3/envs/env_isaacLab/bin/python`
- Confirmed that the training project package was not installed in that environment by default, which is why direct `python scripts/...` initially failed with:
  - `ModuleNotFoundError: No module named 'complete_car_rl_training'`
- Installed the project into the active conda environment with:
  - `python -m pip install -e . --no-build-isolation`
- After installation, revalidated that direct launch works with:
  - `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --num_envs 4 --headless --device cpu --max_iterations 1`
- The run reached environment creation, manager setup, and completed one learning iteration successfully.
- Current durable conclusion:
  - in this repository, the default startup path should now be "activate `env_isaacLab` -> install the project package once -> run `python scripts/...` directly"
  - the older `env -u CONDA_PREFIX -u CONDA_DEFAULT_ENV /home/ubuntu/IsaacLab/isaaclab.sh -p ...` path should be treated as a historical workaround, not the default instruction
  - for first non-interactive launches, `OMNI_KIT_ACCEPT_EULA=YES` may be required unless the Omniverse EULA has already been accepted interactively

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

## 2026-03-19

### RL training roadmap formalization
- Formalized the repository-level RL training route in `AGENTS.md` instead of keeping it as ad hoc chat guidance.
- Durable training order is now:
  - Stage 0: first prove the environment can train end to end
  - Stage 1: flat-ground basic velocity tracking baseline
  - Stage 2: add spherical-joint control on flat ground
  - later stages: add kinematic priors, terrain adaptation, and perception features

### Default baseline decision
- The preferred Stage 1 baseline is now explicitly:
  - flat ground
  - low-dimensional proprioceptive observations
  - velocity-command tracking
  - fixed spherical-joint posture
  - wheel locomotion control first
- Reason:
  - this is the shortest path to a stable, controllable, and reproducible RL baseline
  - it avoids mixing mechanism novelty, perception, terrain diversity, and training-loop debugging in the same first experiment

### Scope control for later phases
- Kinematics should first enter as a structure prior, not as an early hard dependency.
- The preferred first use of kinematics is an action-mapping layer:
  - RL outputs desired platform posture
  - inverse kinematics maps posture targets to driven-joint commands
- Sensor fusion and terrain diversity are explicitly delayed until after the flat-ground baseline is working.

### Impact on current code work
- The current environment code still contains a 12-dimensional wheel-plus-spherical-joint joint-control prototype.
- This should be treated as an exploratory intermediate artifact, not the default mainline training design.
- Future environment iteration should converge the first formal baseline toward the Stage 1 route above before expanding action and observation complexity again.

## 2026-03-19

### TensorBoard offline export workflow
- Added `src/rl_lab/complete_car_rl_training/scripts/tensorboard_export.py`.
- Updated `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py` to export TensorBoard scalar data automatically after each training run.
- Each completed run now writes:
  - `tensorboard_export/summary.json`
  - `tensorboard_export/latest_values.csv`
  - `tensorboard_export/scalars/*.csv`
- Durable conclusion:
  - future result inspection should not rely only on the TensorBoard web UI
  - the exported CSV/JSON files are the canonical offline artifacts for later review, explanation, and cross-session analysis

### 2026-03-19 training run interpretation
- Rechecked run `src/rl_lab/complete_car_rl_training/logs/rsl_rl/complete_car_rl_training/2026-03-19_13-13-03/`.
- Confirmed this run completed through `model_149.pt`, so it was a successful end-to-end training run rather than a startup-only run.
- The exported latest scalar values show:
  - `Train/mean_reward` increased from about `0.83` to about `9.20`
  - `Train/mean_episode_length` increased from `26.5` to `480.0`
  - `Episode_Termination/time_out` ended at `1.0`
  - `Episode_Termination/root_too_low` ended at `0.0`
- Durable conclusion:
  - compared with the earlier unhealthy `root_too_low` behavior, this run indicates much healthier rollout survival
  - current analysis should focus on reward composition and tracking quality, not only on whether episodes terminate too early

## 2026-03-19

### Training diagnosis documentation and skill packaging
- Added repository guide:
  - `src/rl_lab/complete_car_rl_training/docs/tensorboard_reading_guide.md`
- The guide standardizes:
  - how to read TensorBoard in this project
  - what each core scalar means
  - what curve changes imply
  - the fixed diagnosis order and report structure
- Added repository-local skill:
  - `src/rl_lab/complete_car_rl_training/skills/isaac-rl-run-diagnosis/`
- Installed the same skill to:
  - `/home/ubuntu/.codex/skills/isaac-rl-run-diagnosis/`
- Durable conclusion:
  - future run analysis should use the `isaac-rl-run-diagnosis` workflow with the Isaac log path as the minimum input
  - the diagnosis workflow now treats the log path as the entry point and resolves Hydra config, run outputs, TensorBoard exports, and report generation from there

## 2026-03-20

### Literature reading workflow with PDF and Markdown
- Added repository-local literature helpers:
  - `scripts/literature/mineru_batch_convert.sh`
  - `scripts/literature/build_literature_manifest.py`
- Added literature guidance files:
  - `docs/literature/README.md`
  - `docs/literature/catalog.md`
- Durable conclusion:
  - local literature should use a `PDF + Markdown` coexistence workflow instead of PDF-only storage
  - when a MinerU-converted Markdown file exists, future Codex sessions should read the Markdown first for extraction and comparison
  - the source PDF remains the verification authority for figures, equations, page numbers, and any suspicious converted text
- Status:
  - repository structure and reading policy are in place
  - MinerU installation is complete in the active `env_isaacLab` environment
  - first conversion validation is running with a single-paper smoke test

### MinerU first-run constraint on this machine
- The shell environment currently exports local proxy variables pointing to `127.0.0.1:7897`.
- In the current Codex execution environment, those proxy endpoints are not reachable, which blocks MinerU model downloads.
- Durable conclusion:
  - when MinerU needs to download its first model in this environment, clear the proxy variables and prefer `MINERU_MODEL_SOURCE=modelscope`
  - treat this as the default first-run command pattern for literature conversion on this machine


### RL environment literature reading priority
- Added `docs/literature/rl_env_reading_notes.md` as the durable reading-note file for literature related to RL environment configuration and training.
- Current recommended first-batch reading order for env design is:
  - `Wiberg 2022`
  - `Wiberg 2024`
  - `Bauer 2025`
  - `Xu 2024`
  - `Salvi 2022`
- Durable conclusion:
  - for the current project phase, literature should be prioritized by direct usefulness to `observation/action/reward/termination` design rather than by mechanism similarity alone
  - perception/fusion surveys are later-stage references, not first-batch baseline-task references
  - 3-RRR mechanism papers support thesis mechanism justification, but are not the main references for current RL env configuration

### Wiberg 2022 conversion and env-design takeaways
- Converted the local paper:
  - `docs/literature/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning.pdf`
  - into MinerU Markdown under:
  - `docs/literature/mineru_output/Wiberg 等 - 2022 - Control of Rough Terrain Vehicles Using Deep Reinforcement Learning/auto/`
- Confirmed the catalog entry is now `ready` and future sessions can read the Markdown first.
- Durable literature conclusion for the current project:
  - this paper is still the primary RL env-design reference for the complete-car thesis direction
  - its strongest transferable value is the task decomposition around `observation / action / reward / termination / curriculum`
  - for the current Stage 1 baseline, we should borrow its reward and termination design logic, but should not directly copy its high-dimensional terrain observation or its joint suspension-articulation-wheel co-control setup
- Impact:
  - use this paper mainly as a Stage 2/3 reference for terrain observation and joint structure control
  - use it immediately as a Stage 1 reference for physically meaningful reward shaping and failure-condition design

## 2026-03-21

### Literature-reading interaction protocol update
- Updated `AGENTS.md` to add a durable literature-reading interaction protocol for future Codex sessions.
- Durable collaboration rule:
  - when assisting with paper reading, Codex should first confirm the reading goal
  - if no explicit goal is given and the paper is highly thesis-relevant, default to:
    - first: overall understanding of the paper's content and logic
    - second: extraction of the parts relevant to the current project stage
  - questioning should follow the paper's writing order as much as possible and normally progress as:
    - what
    - why
    - association / reflection
  - after each student answer, Codex should correct, supplement, and reorganize the answer instead of only asking the next question mechanically
  - if understanding is incomplete, Codex may ask a second-round question on the same point until the core idea is clear
- Current literature-reading target confirmed in this session:
  - for `Wiberg 2022`, the primary goal is overall understanding of article content and logic
  - the secondary goal is extraction and learning of RL environment design
- Impact:
  - future literature assistance in this repository should behave more like guided teaching than direct summarization
  - for high-relevance papers, Codex should not jump too early to project transfer before the paper itself is understood
