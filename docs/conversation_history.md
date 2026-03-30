# Conversation History

This file stores durable conclusions from past Codex sessions so that future sessions can continue work without relying on ephemeral chat history alone.

## 2026-03-30

### GitHub push blocker from SAT CAD files
- A full-repository push on `main` was rejected by GitHub because `Drawing/完整小车等效串联.SAT` is about 194 MB, exceeding GitHub's 100 MB normal-file limit.
- Durable repository rule for this project:
  - `.SAT` CAD files should be ignored by default and should not be uploaded through normal Git history
  - if these assets ever need versioned remote storage, use Git LFS or another artifact channel explicitly instead of plain `git push`

### Isaac Sim terrain preview script organization and validation
- Organized the user's terrain-preview additions under `scripts/isaac_sim/terrain_preview/`:
  - `mgdp_terrain_preview.py`
  - `run_terrain_preview.sh`
  - `terrain_builder.py`
  - `README.md`
- Fixed the Python script's repository-root discovery so default USD export now resolves from the actual repo root instead of walking too far upward.
- Fixed the README launch examples to use the real folder path `scripts/isaac_sim/terrain_preview/`.
- Verified local static checks pass:
  - `python3 -m py_compile scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
  - `bash -n scripts/isaac_sim/terrain_preview/run_terrain_preview.sh`
- Attempted a minimal Isaac Sim launch with:
  - `/home/lbz/isaac-sim/python.sh scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py --headless --frames 1 --gallery stage1`
- Durable conclusion:
  - the script package is structurally runnable from the repository and the wrapper path is correct
  - the current workstation cannot complete Isaac Sim startup because the host graphics stack fails before scene execution, with `Vulkan 1.1 is not supported`, `no CUDA-capable device is detected`, and a subsequent segmentation fault
  - treat this as an environment-side blocker, not as evidence of a bug in the terrain-preview script itself

### Keyboard teleop now injects one terrain tile into the same stage
- Refactored the terrain-generation code into a reusable helper module:
  - `scripts/isaac_sim/terrain_preview/terrain_builder.py`
- Updated `scripts/isaac_sim/control_keyboard.py` so teleop can now add one terrain tile into the same Isaac Sim stage before `World.reset()`.
- Current teleop terrain behavior:
  - default terrain is `slope_ramp`
  - switch terrain with `--terrain <name>`
  - disable terrain injection with `--terrain none`
- The teleop script also attempts to deactivate several common default ground prim paths before injecting terrain so negative-height features such as `gap` are less likely to be neutralized by an existing plane.
- Verified the edited teleop and terrain scripts pass `python3 -m py_compile`.

### Isaac Sim keyboard teleop wheel restore and smoothing
- Refined `scripts/isaac_sim/control_keyboard.py` again after the numpad remap.
- Wheel teleop is now restored using the existing repository convention:
  - `W/S` for forward and backward
  - `A/D` for differential left and right turning
  - `SPACE` to zero the wheel target
- The six spherical-joint DOFs remain on the numeric keypad bindings:
  - `NUMPAD_1` to `NUMPAD_9`
  - `NUMPAD_DIVIDE`
  - `NUMPAD_MULTIPLY`
  - `NUMPAD_SUBTRACT`
- Added first-order smoothing to both command paths:
  - wheel velocity commands
  - ball-joint position commands
- Verified the edited script passes `python3 -m py_compile`.

### Isaac Sim keyboard teleop remap
- Updated `scripts/isaac_sim/control_keyboard.py` to open `USD/complete_car.usd` instead of the old repository-root `complete_car_alternative.usd`.
- Updated the articulation root path in that script to `/World/complete_car_final`.
- Replaced the old letter-key mapping with numeric keypad bindings using:
  - `NUMPAD_1` to `NUMPAD_9`
  - `NUMPAD_DIVIDE`
  - `NUMPAD_MULTIPLY`
  - `NUMPAD_SUBTRACT`
- In this numpad-only mode, the script no longer exposes wheel teleop keys; wheel joints are held at zero velocity while the six spherical-joint DOFs are adjusted incrementally.
- Verified the edited script passes `python3 -m py_compile`.

### Thesis chapter03 rewrite and build dependency
- Replaced `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex` with the new "运动学模型" draft provided by the user.
- The chapter now covers:
  - spatial position / orientation / pose
  - rotation matrices
  - homogeneous transforms
  - 3-RRR spherical parallel mechanism inverse kinematics
- The new draft uses `tikzpicture` figures, so `毕业论文/毕业论文模板/LaTeX/main.tex` now loads:
  - `\usepackage{tikz}`
  - `\usetikzlibrary{arrows.meta}`
- Rebuilt the thesis with `xelatex` twice and confirmed the document now compiles successfully with the new chapter content.
- Residual warnings are not caused by this replacement alone:
  - existing undefined citations remain in `chapter01`
  - the new chapter has some overfull equation boxes, but no blocking LaTeX errors

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

## 2026-03-29

### Repository file-map consolidation
- Added `docs/project_file_map.md` as the repository-wide structure map.
- Rewrote the root `README.md` so it matches the actual current mainline instead of the earlier minimal-baseline placeholder.
- Durable file-organization conclusion:
  - `src/rl_lab/complete_car_rl_training/` remains the only active RL code workspace
  - `USD/`, `scripts/isaac_sim/`, and `complete_car_*` should be treated as the asset and simulator-validation line
  - `docs/literature/` is the literature line
  - `毕业论文/` is the thesis-writing line
  - `IK_iteration.*` and `Drawing/` belong to the derivation / illustration line
  - `results/` is evidence output, not source code
- Impact:
  - future sessions can orient around the file map instead of rediscovering directory roles from scratch
  - README is now aligned with the current Stage 1 RL baseline route

## 2026-03-29

### Thesis chapter 3 inverse kinematics draft
- Wrote the spherical-joint inverse kinematics section into `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`.
- Fixed the thesis notation so that platform attitude is written as `(\phi,\vartheta,\psi)` and active joint angles remain `\theta_i`, avoiding symbol collision in the derivation.
- For the thesis coordinate convention, the distal reference orientation is recorded as `R_{03}^{(i)} = R_z(\eta_i + 5\pi/6) R_y(\beta - \pi/2)`, consistent with the local symbolic verification workflow.
- The durable derivation route for future thesis edits is now:
  - rotation matrices and homogeneous transform basics
  - direction-vector constraint `w_i^\mathrm{T} v_i = \cos\alpha_2`
  - half-angle substitution `t_i = \tan(\theta_i/2)`
  - quadratic solution for the closed-form inverse kinematics
- Added the BibTeX entry `sadeqi2017` to `毕业论文/毕业论文模板/LaTeX/reference/ref.bib` for subsequent thesis citations.

## 2026-03-28

### Literature note skill installation
- Promoted the repository draft `literature_note_skill.md` into a discoverable local Codex skill at `/home/lbz/.codex/skills/literature-reading-notes/`.
- The canonical invocation name is now `literature-reading-notes`.
- The installed skill is intended for source-faithful structured reading notes from full papers, sections, excerpts, screenshots, and OCR text, with emphasis on paper structure, paragraph extraction, bilingual terminology, reference linkage, and reusable related-work text.
- Impact:
  - future sessions can invoke `$literature-reading-notes` directly instead of reusing the raw draft markdown
  - the original root-level `literature_note_skill.md` should be treated as the drafting source, not the discoverable runtime skill
- Status: installed and ready for use.
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


## 2026-03-22

### MARCEL motivation-reference decision
- Reviewed `Bouton和Gao - 2023 - MARCEL mobile active rover chassis for enhanced locomotion` and concluded it is not a primary RL environment-design paper for the current stage.
- Durable use for this project:
  - keep it as a motivation / mechanism-reference paper for the thesis writing stage
  - revisit it when drafting why a wheeled platform should include a small number of active internal joints instead of remaining purely passive or becoming fully over-actuated
- Reason:
  - high relevance to the project's structural motivation and physical mechanism explanation
  - lower direct relevance to the current RL env cfg design than `Wiberg 2022` and `Xu 2024`
- Impact:
  - for now, literature reading should stay focused on RL environment configuration papers
  - when writing the thesis motivation section, MARCEL should be revisited explicitly

## 2026-03-23

### Two-stage RL training route confirmation
- Replaced the previous default roadmap of “flat-ground velocity tracking first, then add spherical-joint control on flat ground” with a stricter two-stage route tied to the thesis discussion.
- Stage 1 is now defined as:
  - flat ground
  - proprioception only
  - fixed spherical-joint posture
  - goal-directed mobility
  - 6 wheel-speed actions only
- Stage 2 is now defined as:
  - spherical-joint control added to the policy stack
  - high-level RL outputs plus low-level PID and inverse-kinematics mapping
  - diverse terrain introduced
  - exteroceptive terrain sensing fused with proprioception
- Durable boundary:
  - Stage 1 is only for proving stable goal-directed locomotion and does not claim spherical-joint contribution
  - Stage 2 is the first stage where structure control, terrain adaptation, and sensor fusion enter the main task
  - dynamics/torque-level realism is intentionally postponed until after the Stage 2 route is completed

## 2026-03-26

### complete_car.usd robot-subtree alignment
- Aligned the robot subtree in `USD/complete_car.usd` with the equivalent asset layout, but only within `/World/complete_car_final` and its local `joints/` scope.
- Removed the extra SPM leg rigid bodies:
  - `spm1_leg1_proximal`, `spm1_leg1_distal`, `spm1_leg2_proximal`, `spm1_leg2_distal`, `spm1_leg3_proximal`, `spm1_leg3_distal`
  - `spm2_leg1_proximal`, `spm2_leg1_distal`, `spm2_leg2_proximal`, `spm2_leg2_distal`, `spm2_leg3_proximal`, `spm2_leg3_distal`
- Removed the matching fixed joints under `/World/complete_car_final/joints/` so the remaining articulation chain now matches the equivalent main path:
  - `base -> virtual_z -> virtual_y -> platform`
- Added a reusable edit script:
  - `scripts/isaac_sim/align_complete_car_structure_to_equivalent.py`
- Created a backup before editing:
  - `USD/complete_car.usd.spm_leg_cleanup.bak`
- Impact:
  - future sessions should treat the cleaned robot subtree as the current default asset structure for `complete_car.usd`
  - this edit does not yet resolve the remaining asset issues such as unresolved visual references, the remote `Example_Rotary` reference, wheel zero-velocity drives, or the embedded `PhysicsScene` risk

### Wheel friction material added to complete_car.usd
- Added a shared wheel physics material to `USD/complete_car.usd` at:
  - `/World/complete_car_final/Looks/wheel_physics_material`
- Authored material parameters:
  - `physics:staticFriction = 1.0`
  - `physics:dynamicFriction = 1.0`
  - `physxMaterial:frictionCombineMode = multiply`
- Bound this material with physics-purpose material binding to all six wheel collision roots under `/World/complete_car_final/*/collisions`.
- Added a reusable edit script:
  - `scripts/isaac_sim/add_wheel_friction_material.py`
- Created a backup before editing:
  - `USD/complete_car.usd.wheel_friction.bak`
- Impact:
  - future sessions should treat the six wheel collision subtrees as explicitly friction-authored rather than relying on scene defaults

### IK static-consistency validation script redesign
- Replaced the earlier `test_ik_keyboard.py` validation logic of “keyboard pose target -> IK -> send joint target -> compare commanded/actual joint angles” with a stricter static-consistency validation path.
- Current durable validation logic is now:
  - keyboard directly perturbs the six equivalent spherical-joint angles
  - script reads the current front/rear platform orientation relative to each base from the live USD transforms
  - IK is evaluated on that current measured platform orientation
  - mapped IK joint predictions are compared directly against the current measured Isaac Sim joint angles
- Reason:
  - the previous version mixed geometric validation with drive tracking, which makes command-following error appear even when the IK model itself is correct
  - for the user's current modeling assumption, the immediate need is to validate whether “current platform pose -> IK-predicted equivalent motor angles” matches “current simulated joint angles” under a unified zero/sign/bias calibration
- Implementation details retained in the script:
  - CSV logging under `results/ik_keyboard_logs/`
  - zero/sign/bias mapping through `compute_home_offsets()` and `map_to_sim_joints()`
  - front/rear branch continuity through `prev_q`
- Impact:
  - future sessions should interpret `test_ik_keyboard.py` as a geometric consistency checker, not as a drive-tracking controller test
  - if the user later wants command-following validation, that should be treated as a separate script or separate validation mode
## 2026-03-27

### IK keyboard log diagnosis
- Analyzed `results/ik_keyboard_logs/ik_keyboard_2026-03-27_09-58-33.csv`, which was generated by the Isaac Sim keyboard-based IK consistency script.
- Durable conclusion:
  - the script did not hit numerical IK failure on this run
  - all logged `ik_error` fields were empty
  - all six residual terms stayed at `0.0`
  - the commanded joint angles still tracked the simulated joint positions closely
  - but the logged `q_ik` predictions stayed tens of degrees away from `q_sim` for both front and rear spherical joints
- Reason:
  - the current comparison chain is validating "the pose has a mathematically valid IK solution" rather than "the IK solution maps back to the current Isaac Sim joint branch"
  - `test_ik_keyboard.py` initializes `q_home` from `compute_home_offsets()` at mathematical `(roll, pitch, yaw) = (0, 0, 0)` and also seeds `front_prev_q/rear_prev_q` from that same branch
  - the later `map_to_sim_joints()` then applies fixed `signs + biases`, which is not yet sufficient to recover the actual simulation-side zero and branch convention
- Impact:
  - future debugging should focus on branch/zero-pose/mapping calibration first
  - residuals near zero should not be interpreted as proof that the sim joint mapping is correct
  - command tracking and IK mapping should be treated as separate checks

## 2026-03-27

### Zero-pose base reference frames for SPM attitude reading
- Inspected `USD/complete_car.usd` and confirmed that the zero-pose orientation bias is authored between each `spm*_base` and `spm*_spherical_virtual_z` frame.
- Durable conclusion: `spm*_base` is base-fixed but is not the correct zero-pose attitude reference for platform RPY reading.
- Added two new helper frames under the base rigid bodies:
  - `/World/complete_car_final/spm1_base/spm1_base_ref`
  - `/World/complete_car_final/spm2_base/spm2_base_ref`
- Each `spm*_base_ref` is authored with the same local transform as `spm*_spherical_virtual_z` relative to `spm*_base`, so the static zero-pose relation becomes approximately:
  - `spm*_base_ref -> spm*_platform = identity`
- Verification after reopening the stage shows `base_ref -> platform` ZYX RPY is numerically near zero for both front and rear SPMs.
- Impact: future attitude-reading and IK-consistency scripts should use `spm*_base_ref -> spm*_platform` as the zero-pose reference pair instead of `spm*_base -> spm*_platform`.

### IK script switched to base_ref pose reading
- Updated `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` so platform attitude is now read from `spm*_base_ref -> spm*_platform` instead of `spm*_base -> spm*_platform`.
- Rechecked the mechanical zero pose with the same ZYX Euler extraction used in the script. The resulting platform RPY is numerically near zero:
  - front: `[5.493e-06, 6.94e-07, -2.571e-06] deg`
  - rear: `[-1.4661e-05, -1.3655e-05, 4.951e-06] deg`
- Durable conclusion: the platform RPY reference-frame issue is resolved at the USD/frame-selection layer; subsequent IK debugging should focus on `q_math -> q_sim` mapping, branch selection, and zero offsets rather than on the pose-reading frame pair.

### Startup zero-bias calibration for platform RPY
- Updated `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py` to perform a startup zero-bias calibration before entering the normal keyboard-control loop.
- The script now holds zero wheel velocity and zero spherical-joint targets, waits for a short settle window, then averages `spm*_base_ref -> spm*_platform` raw RPY over a sample window to obtain `front_rpy_bias` and `rear_rpy_bias`.
- Subsequent IK input uses `raw_rpy - rpy_bias` instead of the raw USD relative attitude directly.
- The CSV log format now records three RPY groups for both front and rear SPMs:
  - raw RPY
  - bias RPY
  - corrected RPY used by IK
- Durable implication: future log analysis must distinguish between raw physical steady-state attitude and bias-corrected IK input attitude.

### Zero-bias calibration validation from 2026-03-27 17-20-44 log
- Analyzed `results/ik_keyboard_logs/ik_keyboard_2026-03-27_17-20-44.csv` after startup zero-bias calibration was added to `test_ik_keyboard.py`.
- In zero-command steady state, raw platform RPY still shows the expected small physical offset:
  - front raw mean: `[-0.075509, 0.080931, -0.000474] deg`
  - rear raw mean: `[0.040113, -0.012936, 0.00093] deg`
- The recorded calibration bias is constant across the log:
  - front bias: `[-0.089244, 0.091766, 0.005836] deg`
  - rear bias: `[0.04199, -0.013355, -0.002309] deg`
- After bias subtraction, corrected RPY is close to zero:
  - front corrected mean: `[0.013734, -0.010834, -0.00631] deg`
  - rear corrected mean: `[-0.001878, 0.000419, 0.003239] deg`
- Durable conclusion: the platform-attitude frame problem is effectively solved for IK input; remaining mismatch is dominated by the `q_math -> q_sim` mapping rather than by pose reading.
- Same log still shows nontrivial average joint mismatch under zero command:
  - front `q_ik - q_sim`: `[0.198438, -0.021383, 0.107781] deg`
  - rear `q_ik - q_sim`: `[0.062153, 0.027717, 0.044014] deg`
- Therefore future debugging should prioritize branch/offset/sign mapping in `IK_model.py` and `test_ik_keyboard.py`, not further coordinate-frame changes.

### test_ik_keyboard redesign to attitude-target IK tracking
- Replaced the older workflow of “keyboard directly edits sim joint targets, then compare current pose-derived IK result against actual sim joints” with a new control-chain validation workflow in `src/rl_lab/complete_car_rl_training/test_ik_keyboard.py`.
- The script now validates this chain explicitly:
  - keyboard updates platform attitude targets `rpy_des`
  - first-order smoothing generates `rpy_cmd`
  - IK converts `rpy_cmd` into joint targets
  - startup calibration aligns platform `rpy` zero bias and sim joint zero offsets
  - first-order smoothing generates applied joint targets `q_cmd`
  - articulation controller tracks `q_cmd`
  - logs record `rpy_des`, `rpy_cmd`, `q_ik`, `q_cmd`, `q_sim`, and tracking error
- Durable implication: future discussion of this script should treat it as an end-to-end control-chain validator for “attitude target -> IK -> joint target -> articulation tracking”, not as a pure static reverse-IK checker.
- Remaining open point: `IK_SIGNS_FRONT/REAR` are still first-pass assumptions and should eventually be identified from single-axis scans.

### 2026-03-27 attitude-target IK tracking log conclusion
- Analyzed `results/ik_keyboard_logs/ik_keyboard_2026-03-27_18-53-34.csv` after `test_ik_keyboard.py` was redesigned to run the chain `rpy_des -> rpy_cmd -> IK -> q_cmd -> articulation tracking`.
- The articulation controller tracks commanded joint targets well:
  - front `q_cmd - q_sim` mean absolute error: `[0.064982, 0.048758, 0.037857] deg`
  - rear `q_cmd - q_sim` mean absolute error: `[0.040734, 0.021173, 0.023743] deg`
- IK itself remains numerically well-posed throughout the log:
  - front and rear residual max abs values stay at `0.0`
  - `ik_error` stays empty
- But the commanded platform attitude is not realized by the current sim model:
  - front `rpy_cmd - rpy_meas` mean absolute error: `[5.616359, 4.685832, 4.710154] deg`
  - rear `rpy_cmd - rpy_meas` mean absolute error: `[2.423783, 0.499323, 2.202885] deg`
- Segment examples show axis/sign mismatch at the platform level:
  - front yaw command `+12 deg` produces measured front pose approximately `[-11.24, +0.98, -0.93] deg` instead of a dominant positive yaw response
  - front pitch command `+12 deg` produces measured front pose approximately `[-0.88, -10.84, -5.60] deg`
  - front roll command `+12 deg` produces measured front pose approximately `[-1.26, -7.62, +9.30] deg`
- Durable conclusion: in the current asset, feeding IK motor angles directly into the USD equivalent spherical-joint coordinates is not a valid semantic mapping. The failure is not due to articulation tracking quality; it is due to a coordinate/abstraction mismatch between real 3-RRR motor coordinates and the equivalent ball-joint coordinates used in simulation.
- Future work should not keep treating `IK_SIGNS_*` tuning as the main fix for this issue. The next step is a research-level decision on architecture: either keep the simulator at the attitude-coordinate level and use IK only as a parallel mapping to real motor angles, or introduce a lower-level model/control interface whose coordinates actually represent motor angles.

### RL/IK role separation after equivalent spherical-joint clarification
- Clarified the modeling semantics for the current simulator asset: the three equivalent spherical-joint coordinates in USD should be treated as the moving-platform attitude coordinates, not as proxies for real 3-RRR motor coordinates.
- Durable design decision:
  - RL in simulation should directly control the equivalent spherical-joint attitude coordinates
  - IK should consume platform attitude and output real motor angles only as a parallel mapping layer for future hardware / physical interpretation
  - IK motor angles are not part of the current sim control loop and should not be fed back as the direct command to the equivalent joints
- Impact:
  - the previous attempt to validate `attitude target -> IK motor angles -> sim equivalent joints` is no longer the target architecture
  - future RL work should return to the baseline of directly controlling the equivalent joints in simulation
  - IK remains useful for later hardware-facing stages or for thesis discussion of the real mechanism mapping

## 2026-03-28

### Ha 2025 survey reading note outcome
- Added a first structured reading note for `Learning-based legged locomotion: State of the art and future perspectives` at `docs/literature/mineru_output/Ha 等 - 2025 - Learning-based legged locomotion State of the art and future perspectives/auto/reading_notes.md`.
- Durable reading conclusion:
  - the paper is best treated as a research-design survey rather than as an algorithm survey
  - its main reusable structure for this project is:
    - `MDP` design (`observation`, `reward`, `action`)
    - learning framework selection (`end-to-end`, `curriculum`, `hierarchical`, `privileged learning`)
    - `sim-to-real` strategy ordering (`good system design` before `randomization`)
    - control-learning combinations for staged architectures
- Project-specific implication:
  - the current two-stage complete-car RL roadmap remains aligned with the survey's logic
  - Stage 1 should continue to prioritize a minimal trainable baseline with proprioception and goal-related inputs
  - richer exteroception, hierarchical control, privileged learning, and stronger sim-to-real machinery belong to later stages after the baseline stabilizes
- Status: first-pass note completed from the source PDF; suitable as a reusable survey reference for future environment-design discussions.
