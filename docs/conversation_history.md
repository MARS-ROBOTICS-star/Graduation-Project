# Conversation History

This file stores durable conclusions from past Codex sessions so that future sessions can continue work without relying on ephemeral chat history alone.

## 2026-04-10

### The active training mainline now vendors the RSL-RL runtime implementation into the repository
- Updated:
  - `RL_Training/rsl_rl/`
  - `RL_Training/scripts/rsl_rl/train.py`
  - `RL_Training/scripts/rsl_rl/play.py`
  - `RL_Training/setup.py`
  - `RL_Training/README.md`
  - `README.md`
- Durable implementation conclusion:
  - the repository now contains a vendored local copy of the active `rsl_rl` runtime under:
    - `RL_Training/rsl_rl/`
  - this vendored package now carries the actual runtime implementation chain used by training and playback, including:
    - `runners/on_policy_runner.py`
    - `algorithms/ppo.py`
    - `models/mlp_model.py`
    - `storage/rollout_storage.py`
    - `modules/distribution.py`
    - `modules/mlp.py`
    - `modules/normalization.py`
    - `utils/logger.py`
    - and the remaining package files needed to keep that chain closed locally
  - `train.py` and `play.py` now prepend `RL_Training/` to `sys.path` before importing `rsl_rl`, so the vendored package is preferred over the external site-packages copy at runtime
  - `setup.py` now also includes:
    - `rsl_rl`
    - `rsl_rl.*`
    in the editable-install package list, so the local implementation is part of the project install surface
  - the vendored package records:
    - `__version__ = "5.0.1-local"`
    in `RL_Training/rsl_rl/__init__.py`
  - `train.py` and `play.py` no longer use `importlib.metadata.version("rsl-rl-lib")` as the source of truth for the active runtime implementation
- Reason:
  - the user explicitly required that the real PPO / runner / network implementation body be copied into the project after noticing that earlier localization only copied config classes and local reward helpers
- Impact:
  - future PPO, runner, and network modifications should start from `RL_Training/rsl_rl/` instead of patching around the external `rsl-rl-lib` installation
  - future runtime validation should explicitly confirm that the training entrypoints import the vendored `RL_Training/rsl_rl/` package
  - future editable installs of `RL_Training/` should preserve this vendored runtime because it is now part of the project package manifest
- Status:
  - vendoring completed
  - `python3 -m compileall` passed for the vendored `rsl_rl` tree and the touched training scripts
  - direct import verification confirmed that `OnPolicyRunner`, `PPO`, and `MLPModel` now resolve to files under `RL_Training/rsl_rl/`

### Direct mainline now uses a measured-geometry wheel-speed allocator instead of the old heuristic left-right scaling
- Updated:
  - `RL_Training/kinematics/__init__.py`
  - `RL_Training/kinematics/wheel_speed_allocator.py`
  - `RL_Training/scripts/validate_wheel_speed_allocator.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
  - `README.md`
- Durable implementation conclusion:
  - the project now has a standalone wheel-speed allocation package under:
    - `RL_Training/kinematics/`
    so the thesis kinematic model can be validated independently from Isaac Lab
  - the allocator uses the measured geometry directly:
    - `a = [0.25632, 0.0, 0.0]`
    - `b1 = [-0.29665, 0.0, 0.00481]`
    - `b3 = [0.29665, 0.0, 0.00951]`
    - measured left/right wheel-center locations for all three modules
    - `r_wheel = 0.19`
  - the allocator explicitly constructs the thesis Jacobian chain:
    - `\mathbf K_1(\mathbf q), \mathbf K_2, \mathbf K_3(\mathbf q)`
    - measured `\mathbf H_i`
    - full wheel-speed Jacobian `\mathbf J_w(\mathbf q)`
    and then computes wheel targets from `\boldsymbol\Omega = \mathbf J_w(\mathbf q)\boldsymbol\xi`
  - the front/middle/rear formula order from the thesis is internally reordered to the actual wheel-joint output order required by the simulator:
    - `body_car_wheel_left_joint`
    - `body_car_wheel_right_joint`
    - `head_car_wheel_left_joint`
    - `head_car_wheel_right_joint`
    - `tail_car_wheel_left_joint`
    - `tail_car_wheel_right_joint`
  - the allocator now provides:
    - a NumPy interface for standalone verification
    - a Torch interface for Isaac Lab runtime use
  - the direct env no longer derives wheel targets from the old heuristic:
    - `lin_vel_x * scale +/- ang_vel_yaw * scale`
    and instead reads the current 6 ball-joint positions and velocities, combines them with the RL command, and generates 6 wheel angular-velocity targets from the measured-geometry Jacobian allocator
  - for the current RL command semantics, the allocator maps:
    - `lin_vel_x`
    - `lin_vel_y`
    - `ang_vel_yaw`
    into the middle-module instantaneous rigid-body velocity, while the separate `heading` command is intentionally not injected into the instantaneous wheel-speed mapping
  - the old control config fields:
    - `wheel_drive_lin_vel_scale`
    - `wheel_drive_yaw_rate_scale`
    were removed because they no longer match the active wheel-drive semantics
  - running:
    - `python3 scripts/validate_wheel_speed_allocator.py`
    from `RL_Training/`
    now passes the basic numerical checks for:
    - zero input
    - pure forward motion
    - pure yaw motion
  - running:
    - `python3 -m py_compile ...`
    on the touched files also passes
- Impact:
  - future wheel-drive changes should continue from `RL_Training/kinematics/wheel_speed_allocator.py` instead of reintroducing ad hoc left-right scaling inside the env
  - future direct-task code must preserve the strict joint-order contract between allocator output and simulator wheel joints
  - if command semantics change later, the mapping from RL command to middle-module rigid-body velocity should be updated in the allocator, not by adding another wheel-speed shortcut in the env
- Status:
  - completed
  - real Isaac Lab runtime validation still pending

### Thesis chapter03 Jacobian body was further tightened without changing the derivation backbone
- Updated:
  - `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- Durable writing conclusion:
  - after the earlier asymmetric `{}^{1}\mathbf b_1 / {}^{3}\mathbf b_3` revision, the same chapter03 Jacobian body was tightened again under a strict “keep the existing derivation backbone” rule instead of being rewritten
  - the wheel angular-velocity notation was unified from:
    - `\dot\phi_{iL}, \dot\phi_{iR}`
    to:
    - `\Omega_{iL}, \Omega_{iR}`
    across prose, scalar formulas, vector forms, and Jacobian expressions, so that wheel-speed symbols no longer conflict with the Euler angle `\phi`
  - the connection-center vector in `${B_2}` is now explicitly fixed as:
    - `${}^{2}\mathbf a = [a_x, 0, 0]^T`
    and the surrounding text now states the symmetry only for the front/rear connection centers along the `x_2` axis, not for a generic three-dimensional offset
  - the old wording that treated `${}^{2}\mathbf v_c` and `${}^{2}\boldsymbol\omega_c` as “motion commands” was replaced by the physically stricter interpretation of:
    - middle-module instantaneous rigid-body velocity
    - generalized-velocity description used in the kinematic analysis
    while explicitly keeping the three-dimensional general form and noting that planar control may use only a subset in practice
  - the old “pure rolling constraint” wording was replaced by rolling-direction no-slip wording; the text now explicitly states that this section only uses the rolling-direction velocity relation to map module rigid-body velocity to left/right wheel angular velocity, and does not claim a full lateral no-slip constraint set
  - the wheel-speed sign convention is now explicit: positive wheel angular velocity corresponds to positive rolling velocity of the wheel center along the local module `x_i` axis
  - the Euler-angle-rate mapping section now explicitly notes the `ZYX` parametrization singularity near `\theta = \pm \pi/2`, and the analysis is stated to assume configurations away from those singular poses
  - the derivation backbone remained unchanged:
    - frame and geometry definitions
    - front/middle/rear position relations
    - velocity propagation from position differentiation
    - Euler-rate to angular-velocity mapping
    - module rigid-body Jacobians
    - wheel-speed mapping
    - full vehicle Jacobian assembly
  - after the tightened revision, running:
    - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
    still succeeds and regenerates:
    - `毕业论文/毕业论文模板/LaTeX/main.pdf`
- Remaining non-blocking warnings:
  - two bibliography keys are still missing from `reference/ref.bib`:
    - `fang2015survey`
    - `MATSUMURA2017566`
- Impact:
  - future edits to this chapter03 section should preserve the current symbol system and terminology instead of reintroducing:
    - wheel-speed symbols based on `\dot\phi`
    - “motion command” wording for `${}^{2}\mathbf v_c` and `${}^{2}\boldsymbol\omega_c`
    - blanket “pure rolling constraint” wording for a relation that only uses rolling-direction speed
- Status:
  - completed and recompiled successfully

### Thesis chapter03 kinematic-model body now uses separate asymmetric fixed offsets `{}^{1}\mathbf b_1` and `{}^{3}\mathbf b_3` with minimal text disruption
- Updated:
  - `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- Durable writing conclusion:
  - the user explicitly required keeping the existing chapter03 prose structure as much as possible instead of replacing the whole body with a new remote-style rewrite
  - the active chapter03 main text now treats the front and rear fixed offsets separately as:
    - `${}^{1}\mathbf b_1`
    - `${}^{3}\mathbf b_3`
    instead of reusing one shared side-module offset vector `\mathbf b`
  - the corresponding position relations are now written as:
    - `${}^{2}\mathbf p_1={}^2\mathbf a+{}^2\mathbf R_1\,{}^{1}\mathbf b_1`
    - `${}^{2}\mathbf p_3=-{}^2\mathbf a+{}^2\mathbf R_3\,{}^{3}\mathbf b_3`
  - the front / rear module line-velocity propagation, the rigid-body mappings `\mathbf K_1(\mathbf q)` and `\mathbf K_3(\mathbf q)`, and the row-wise wheel-speed Jacobian expansion were updated consistently to match this asymmetric fixed-offset model
  - the wheel-center position template and the single-module wheel-speed matrix `\mathbf H_i` were intentionally kept in the original symbolic form; this revision did not switch the whole chapter body to a measured-geometry direct-substitution style
  - after the revision, running:
    - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
    succeeds again and regenerates:
    - `毕业论文/毕业论文模板/LaTeX/main.pdf`
- Remaining non-blocking warnings:
  - two bibliography keys are still missing from `reference/ref.bib`:
    - `fang2015survey`
    - `MATSUMURA2017566`
- Reason:
  - the user asked for an asymmetric fixed-offset derivation but explicitly rejected a full remote-style body rewrite, requiring a minimal-invasive update on top of the current text
- Impact:
  - future chapter03 edits should continue from this symbolic asymmetric `b_1 / b_3` version instead of reverting either to:
    - the older symmetric single-`\mathbf b` model
    - or a wholesale measured-geometry body rewrite that discards the current prose organization
- Status:
  - completed and recompiled successfully

### Direct complete-car mainline completed a structural migration to 4D commands, 6D policy actions, and attitude-centric observations
- Updated:
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/assets/robot_cfg.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/commands.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/observations.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/utils.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/rewards.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/local_velocity_tracking_reward.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents/local_rsl_rl_cfg.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/agents/ppo_cfg.py`
- Durable implementation conclusion:
  - the active command vector is now 4D:
    - `lin_vel_x`
    - `lin_vel_y`
    - `ang_vel_yaw`
    - `heading`
  - the active policy action space is now 6D and only controls the 6 spherical-joint-related articulation joints
  - wheel velocity is no longer emitted by the policy; the env now derives left/right wheel velocity targets from the sampled command
  - the active base policy observation is now attitude-centric and ordered as:
    - `roll, pitch, yaw`
    - `roll_rate, pitch_rate, yaw_rate`
    - `ball_joint_pos(6)`
    - `ball_joint_vel(6)`
    - `commands(4)`
    - `last_action(6)`
  - the resulting base proprioceptive observation dimension is:
    - `28`
  - Stage2 still appends optional sensor features after this 28D base observation instead of replacing it
- PPO localization conclusion:
  - the project no longer directly inherits the deprecated Isaac Lab PPO config template classes in `ppo_cfg.py`
  - project-local runner / model / PPO config classes now live in:
    - `tasks/direct/complete_car/agents/local_rsl_rl_cfg.py`
  - the active PPO config was simultaneously migrated to the native `actor / critic / distribution_cfg` structure expected by modern `rsl-rl`
- Reward localization conclusion:
  - the command-tracking reward kernel is now explicitly isolated in the local file:
    - `tasks/direct/complete_car/local_velocity_tracking_reward.py`
  - `rewards.py` now composes the complete reward from that local tracking kernel plus posture / joint / action-rate penalties
- Reason:
  - the user explicitly requested a structural migration rather than partial compatibility edits, and required the complete-car task to stop carrying the previous 12D action semantics and old body-state observation layout
- Impact:
  - future task changes must treat wheel driving as env-side command-following logic unless the user explicitly restores wheel actions to the policy
  - future observation changes should preserve the new 28D base ordering unless the task definition is intentionally changed again
  - future PPO updates should start from the local config copy instead of reintroducing direct inheritance from Isaac Lab's deprecated config template classes
- Status:
  - code migration completed
  - `python3 -m py_compile` passed for the touched direct-task files
  - real Isaac Lab runtime validation still pending

### complete_car.usd now uses body_car_chassis as the articulation root and related scripts were aligned
- Updated:
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/assets/robot_cfg.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/sensors/sensor_runtime.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/terrain/terrain_runtime.py`
  - `scripts/isaac_sim/check_isaaclab_asset.py`
  - `scripts/isaac_sim/control_keyboard.py`
  - `scripts/isaac_sim/rover_control.py`
- Durable implementation conclusion:
  - the active `complete_car.usd` now places its articulation root at:
    - `/World/complete_car_alternative/body_car_chassis`
  - the direct RL asset config now sets:
    - `ArticulationCfg.articulation_root_prim_path = "/body_car_chassis"`
    while keeping the spawned asset namespace at `.../Robot`
  - scripts that directly instantiate the articulation from a USD stage now point to the new articulation root instead of the old parent prim
  - complete-car sensor and height-scanner defaults were aligned to the current asset structure:
    - IMU under `body_car_chassis`
    - camera and lidar under `head_car_chassis`
- Reason:
  - the user moved the articulation root in `complete_car.usd` and requested that dependent scripts be updated accordingly
- Impact:
  - future asset-related changes should distinguish between:
    - the asset namespace root, such as `/World/complete_car_alternative`
    - the articulation root prim, now `/World/complete_car_alternative/body_car_chassis`
  - when a script needs articulation APIs, it should target the articulation root, not just the parent asset prim
- Status:
  - code updates completed
  - `python3 -m py_compile` passed for the touched files

### Direct mainline template residue has been cleaned from the training entrypoints and env config trunk
- Updated:
  - `RL_Training/scripts/rsl_rl/train.py`
  - `RL_Training/scripts/rsl_rl/play.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env_cfg.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/complete_car_env.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/observations.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/utils.py`
  - `docs/complete_car_direct_workflow_architecture.md`
- Durable implementation conclusion:
  - the active `train.py` and `play.py` no longer keep manager-based or MARL template unions from Isaac Lab's generic launcher template
  - `train.py` no longer exposes the manager-based-only `--export_io_descriptors` branch
  - the command config no longer keeps unused fields such as:
    - `heading_command`
    - `rel_heading_envs`
    - `ranges.ang_vel_z`
    - `ranges.heading`
    - `debug_vis`
  - the reward config no longer keeps the unused `base_height_target`
  - action noise and observation noise are now routed through:
    - `DirectRLEnvCfg.action_noise_model`
    - `DirectRLEnvCfg.observation_noise_model`
    instead of being manually injected inside `CompleteCarEnv` and `observations.py`
- Reason:
  - the user explicitly asked to process the remaining template residue and unconnected fields instead of leaving them documented as known leftovers
- Impact:
  - future direct-mainline maintenance should treat the current launcher scripts as single-agent direct-task entrypoints rather than generic Isaac Lab templates
  - future noise-related changes should start from `CompleteCarEnvCfg.__post_init__()` because local noise parameters are now translated there into Isaac Lab base noise models
  - if observation history is enabled later, the observation-noise semantics should be rechecked explicitly because the base observation-noise hook runs after observation assembly
- Status:
  - code cleanup completed
  - `python3 -m py_compile` passed for the touched training and direct-task files

### Thesis chapter03 section 3.1.10 has been replaced with a full clean Jacobian-construction derivation
- Updated:
  - `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- Durable writing conclusion:
  - the subsection `3.1.10` "整车速度雅可比矩阵构造" was replaced as a whole using the user's longer derivation path instead of incremental local edits
  - the rewritten subsection now explicitly organizes the derivation as:
    - vehicle generalized velocity vector `\boldsymbol\xi`
    - skew-symmetric operator `\mathbf S(\mathbf x)`
    - rigid-body velocity mappings `\mathbf K_1(\mathbf q)`, `\mathbf K_2`, `\mathbf K_3(\mathbf q)`
    - per-module wheel Jacobians `\mathbf H_i`
    - full vehicle wheel-speed Jacobian `\mathbf J_w(\mathbf q)`
  - malformed pseudo-markup inside the user-provided draft, such as separator lines and invalid equation formatting, was converted back into valid XeLaTeX math environments
  - after the replacement, running:
    - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
    succeeds again and regenerates:
    - `毕业论文/毕业论文模板/LaTeX/main.pdf`
- Reason:
  - the user explicitly requested replacing the whole `3.1.10` subsection with the new text and fixing formatting until XeLaTeX compilation succeeds
- Impact:
  - future edits to the vehicle Jacobian subsection should continue from this clean expanded version instead of reusing the malformed draft text
  - the current Jacobian discussion in chapter03 is now aligned with the existing notation chain for front/middle/rear module velocity mappings
- Status:
  - completed and recompiled successfully

### Complete-car RL mainline has been fully refactored from manager-based to Isaac Lab direct workflow
- Updated:
  - `RL_Training/complete_car_rl_training/__init__.py`
  - `RL_Training/complete_car_rl_training/tasks/direct/complete_car/`
  - `scripts/isaac_sim/preview_stage1_terrain.py`
  - `scripts/isaac_sim/preview_stage1_tile.py`
  - `scripts/isaac_sim/preview_stage1_last_six.py`
  - `scripts/isaac_sim/control_keyboard.py`
- Durable implementation conclusion:
  - the active RL mainline no longer uses:
    - `envs/base/`
    - `envs/baseline/`
    - manager-based observation / action / event / termination config groups
  - the new active task tree is:
    - `tasks/direct/complete_car/complete_car_env.py`
    - `tasks/direct/complete_car/complete_car_env_cfg.py`
    - `tasks/direct/complete_car/stage0_flat_cfg.py`
    - `tasks/direct/complete_car/stage1_terrain_cfg.py`
    - `tasks/direct/complete_car/stage2_perception_cfg.py`
    - `tasks/direct/complete_car/assets/robot_cfg.py`
    - `tasks/direct/complete_car/terrain/terrain_generator.py`
    - `tasks/direct/complete_car/terrain/terrain_runtime.py`
    - `tasks/direct/complete_car/sensors/sensor_runtime.py`
    - `tasks/direct/complete_car/agents/ppo_cfg.py`
  - the direct task registration ids are now:
    - `Complete-Car-Stage0-Flat-Direct-v0`
    - `Complete-Car-Stage1-Terrain-Direct-v0`
    - `Complete-Car-Stage2-Perception-Direct-v0`
  - direct task logic is now organized so that:
    - `CompleteCarEnv` directly owns actions, commands, resets, rewards, dones, terrain runtime, and sensor runtime
    - `rewards.py / observations.py / commands.py / terminations.py` only hold task-specific tensor helpers
    - terrain and perception support are retained as runtime helpers instead of manager terms
- Reason:
  - the user explicitly decided to stop using manager-based architecture and requested a full cut to Isaac Lab's official direct workflow rather than a compatibility layer
- Impact:
  - future environment changes must continue under `tasks/direct/complete_car/`
  - future smoke tests, training commands, and documentation should use the new `-Direct` task ids
  - old `envs/base/*.py`, `envs/baseline/*.py`, and `utils/terrain.py` should be treated as retired mainline code and not restored by default
- Status:
  - code refactor completed
  - real Isaac Lab runtime validation still pending on a machine with the environment installed

### A standalone long-form architecture document now exists for the direct workflow mainline
- Updated:
  - `docs/complete_car_direct_workflow_architecture.md`
  - `README.md`
  - `docs/project_file_map.md`
  - `docs/current_status.md`
- Durable documentation conclusion:
  - the repository now contains a standalone architecture reference under:
    - `docs/complete_car_direct_workflow_architecture.md`
  - this document is intended to be the long-form internal reference for:
    - direct task registration
    - env / cfg / runtime-helper responsibilities
    - training call chain
    - stage organization
    - future modification entry points
  - future sessions that need to explain or extend the direct workflow should prefer this document over reconstructing the architecture ad hoc from scattered chat context
- Reason:
  - the user explicitly requested a code-based architectural explanation of the new direct mainline and wanted it preserved as a long-lived Markdown document inside the repository
- Impact:
  - future documentation, onboarding, and refactor discussions can use this file as the default architecture reference
  - the long-form architecture reference currently lives directly under `docs/` together with the project-memory files
- Status:
  - completed

## 2026-04-09

### Thesis chapter03 was rebuilt into clean LaTeX and the full thesis now compiles again
- Updated:
  - `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- Durable implementation conclusion:
  - the previous `chapter03.tex` had been contaminated by invalid pseudo-markdown and malformed math markup, including:
    - separator lines such as `=================`
    - stray `#` markers
    - broken matrix row separators
    - malformed subscripts and inline math
  - the chapter body was rewritten into clean XeLaTeX-compatible source while preserving the chapter structure and the main kinematics / Jacobian derivation flow
  - after the rewrite, running:
    - `latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex`
    now succeeds again and regenerates:
    - `毕业论文/毕业论文模板/LaTeX/main.pdf`
- Remaining non-blocking warnings:
  - two bibliography keys are still missing from `reference/ref.bib`:
    - `fang2015survey`
    - `MATSUMURA2017566`
- Impact:
  - future thesis-writing sessions should treat `chapter03.tex` as a clean LaTeX baseline again rather than trying to repair the old corrupted markup incrementally
  - if later compilation warnings are about bibliography only, they are separate from this chapter-format failure
- Status:
  - compile blocker resolved

### Thesis chapter03 line-velocity derivation now uses an inertial-frame-first explanation
- Updated:
  - `毕业论文/毕业论文模板/LaTeX/chapters/chapter03.tex`
- Durable writing conclusion:
  - the subsection for front/rear module linear velocity derivation was rewritten to introduce an inertial frame `${W}$` first
  - the expressions
    - `${}^{2}\mathbf v_1={}^2\mathbf v_2+{}^2\boldsymbol\omega_2\times{}^2\mathbf p_1+{}^2\dot{\mathbf p}_1`
    - `${}^{2}\mathbf v_3={}^2\mathbf v_2+{}^2\boldsymbol\omega_2\times{}^2\mathbf p_3+{}^2\dot{\mathbf p}_3`
    are now derived from:
    - absolute position in `${W}`
    - product differentiation
    - transport velocity caused by frame rotation
  - this replaces the previous shorter presentation that stated the velocity relation more directly
- Reason:
  - the user explicitly pointed out that the confusing part was why the extra derivative term appears, and requested a derivation that makes the term emerge naturally from absolute-position differentiation
- Impact:
  - future chapter03 edits should preserve this inertial-frame explanation path instead of reverting to a compact but less intuitive derivation
- Status:
  - completed and recompiled successfully

## 2026-04-07

### Stage1 wheel action remains six independent wheel velocities
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
  - `README.md`
- Durable implementation conclusion:
  - after a brief local experiment with axle-coupled wheel actions, the user decided to restore the Stage1 wheel action to:
    - six independent wheel-velocity targets
  - the current policy action dimension is therefore back to:
    - `12 = 6 ball + 6 wheel`
- Reason:
  - the user explicitly requested reverting the wheel action space back to six independently controlled wheels
- Impact:
  - future Stage1 training and result interpretation should continue to use the original six-wheel action semantics unless the user explicitly changes the task definition again
- Status:
  - reverted and verified with `py_compile`

### Stage1 velocity command now samples linear speed plus curvature instead of sampling yaw rate independently
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/commands.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- Durable implementation conclusion:
  - the Stage1 `base_velocity` command no longer samples `ang_vel_z` independently as the primary source
  - it now samples:
    - `v_x ~ U(v_min, v_max)`
    - `kappa ~ U(-kappa_max, kappa_max)`
  - and computes:
    - `omega_z = v_x * kappa`
  - additionally, when:
    - `|v_x| < v_th`
    the command generator forces:
    - `omega_z = 0`
- Current active default values:
  - `v_x ∈ [-2.0, 2.0]`
  - `kappa ∈ [-0.5, 0.5]`
  - `v_th = 0.1`
- Reason:
  - the user requested a command design closer to vehicle curvature semantics, avoiding the previous mismatch where yaw-rate was sampled independently of forward speed
- Impact:
  - future Stage1 training analysis should interpret yaw commands as speed-coupled turning commands
  - direct comparison with older runs that used independently sampled `ang_vel_z` should explicitly note this command-distribution change

### Active task default viewer pose now matches the user-picked map-preview viewpoint
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- Durable implementation conclusion:
  - the active task now sets:
    - `viewer.eye = (-53.885, 43.696, 64.903)`
    - `viewer.lookat = (-53.054, 43.698, 64.346)`
  - the viewer pose was taken from the current Isaac Sim viewport camera after the user manually adjusted a suitable overview of the preview map
- Impact:
  - future GUI launches of the active task should open from this same default overview instead of the older local close-up view
- Status:
  - completed and verified with `py_compile`

### Stage 1 baseline no longer uses chassis-collision reward or chassis contact sensors
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`
- Durable implementation conclusion:
  - the active Stage 1 baseline no longer includes:
    - chassis collision penalty
  - the three scene-level chassis contact sensors were removed together with that reward
  - the remaining reward set is now:
    - linear-velocity tracking
    - angular-velocity tracking
    - body-orientation stability
    - `lin_vel_z` penalty
    - `ang_vel_xy` penalty
    - action-rate penalty
    - spherical-joint deviation penalty
    - spherical-joint swing penalty
    - termination penalty
- Reason:
  - the user decided that the baseline should not depend on a simulator-only chassis-contact signal that is not part of the current real-robot default sensing route
- Impact:
  - future Stage 1 tuning should not assume any chassis-contact reward signal exists
  - if body-ground interference needs to be handled later, it should be reintroduced only after the sensing and deployment meaning are explicitly defined
- Status:
  - completed and verified with `py_compile`

## 2026-04-06

### Project paths are now centralized in complete_car_rl_training.paths
- Added:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/paths.py`
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
  - `src/rl_lab/complete_car_rl_training/tools/ik/test_ik_keyboard.py`
- Durable implementation conclusion:
  - repository-level paths for the active training project are now centralized in:
    - `complete_car_rl_training.paths`
  - current shared constants include:
    - `PROJECT_ROOT`
    - `USD_DIR`
    - `RESULTS_DIR`
    - `COMPLETE_CAR_USD`
  - business files should import these shared paths instead of re-implementing local `Path(__file__)` plus upward root-discovery logic
- Reason:
  - the user requested that root-path handling should be unified instead of being duplicated in task code and helper scripts
- Impact:
  - future path changes for the active training project should be made in one place first
  - future sessions should avoid adding new per-file root-discovery snippets under `src/rl_lab/complete_car_rl_training/`
- Status:
  - completed and verified with `py_compile`

### Code explanation style is now standardized in AGENTS.md
- Updated:
  - `AGENTS.md`
  - `docs/current_status.md`
  - `logs/daily_work_log.md`
- Durable collaboration conclusion:
  - future code walkthroughs should default to short local file names rather than full absolute paths
  - explanation order should be:
    - script structure first
    - then imports / constants / classes / functions in dependency order
    - then line-by-line or block-by-block teaching when requested
  - explanations should assume weak Python background and explicitly explain config objects, function references, and data flow
- Reason:
  - the user requested a more teaching-oriented and less path-heavy code explanation style
- Impact:
  - future teaching sessions should follow this explanation order by default instead of jumping straight to summaries
- Status:
  - completed

### Old local `src/` residue has been removed and operational entrypoints are now standardized to `RL_Training/`
- Updated:
  - `AGENTS.md`
  - `RL_Training/README.md`
  - `RL_Training/docs/training_workflow_and_tensorboard_guide.md`
  - `RL_Training/skills/isaac-rl-run-diagnosis/SKILL.md`
  - `docs/isaaclab模板使用指南.md`
  - `docs/isaaclab_rl_template_and_mgdp_structure.md`
  - `docs/current_status.md`
- Durable implementation conclusion:
  - the untracked old local residue under:
    - `src/`
    has been removed from the working tree
  - future operational commands should start from:
    - `/home/ubuntu/Graduation-Project/RL_Training`
  - current user-facing command and entrypoint docs now consistently point to:
    - `RL_Training/`
    instead of the deleted `src/rl_lab/complete_car_rl_training/`
  - the repository-local Isaac RL diagnosis skill now reads its guide and export script from:
    - `RL_Training/docs/training_workflow_and_tensorboard_guide.md`
    - `RL_Training/scripts/tensorboard_export.py`
- Reason:
  - after the GitHub sync, the local repository still had an untracked legacy `src/` tree and a few active docs still referenced the old path, which could mislead later execution
- Impact:
  - future sessions should treat the old `src/` location as history only
  - when giving runnable commands, default to `cd /home/ubuntu/Graduation-Project/RL_Training`
- Status:
  - completed

### Preferred teaching rhythm for code walkthroughs is now explicitly standardized
- Updated:
  - `AGENTS.md`
  - `docs/current_status.md`
  - `logs/daily_work_log.md`
- Durable collaboration conclusion:
  - future code teaching should follow this rhythm by default:
    - first explain the script's role in the larger system
    - then explain the top-level structure
    - then walk downward in source order block by block
    - for each block, explain its purpose first and then explain the important lines
    - explicitly distinguish between reference/registration and real executable logic
    - after each major section, reconnect the explanation to the RL loop
  - this rhythm was explicitly confirmed by the user as the preferred pacing, depth, and content balance
- Reason:
  - the user stated that this explanation rhythm, pacing, and content balance works well and requested that it become the default
- Impact:
  - future code walkthroughs should keep the same teaching cadence instead of switching to terse summaries or file-inventory style explanations
- Status:
  - completed

### Training default device is now unified to GPU and teleop remains on the Isaac Sim GPU path
- Updated:
  - `src/rl_lab/complete_car_rl_training/scripts/rsl_rl/train.py`
  - `scripts/isaac_sim/control_keyboard.py`
  - `src/rl_lab/complete_car_rl_training/docs/training_workflow_and_tensorboard_guide.md`
  - `docs/current_status.md`
- Durable implementation conclusion:
  - `train.py` now defaults to:
    - `cuda:0`
    when the user does not explicitly pass `--device`
  - the active training guide and current default launch command were updated from CPU to GPU
  - `control_keyboard.py` continues to run on Isaac Sim's default GPU path and does not provide a separate CPU execution mode
- Reason:
  - the user requested that the training script and keyboard teleop path should be unified to GPU operation
- Impact:
  - future sessions should treat GPU as the repository default for training and teleop
  - if a machine lacks a usable NVIDIA driver or CUDA device, that is now an environment blocker rather than the repository default behavior
- Status:
  - completed and verified with `train.py --help`, `control_keyboard.py --help`, and `py_compile`

### control_keyboard.py is currently narrowed to the real repository-supported terrain scope
- Updated:
  - `scripts/isaac_sim/control_keyboard.py`
  - `src/rl_lab/complete_car_rl_training/docs/training_workflow_and_tensorboard_guide.md`
- Durable implementation conclusion:
  - the teleop script now fixes the stale local path for the training terrain source:
    - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1_terrain.py`
  - current supported `--terrain` values are intentionally narrowed to:
    - `none`
    - `stage1`
  - `--terrain stage1` loads the real training terrain path
  - older options such as:
    - `gap`
    - `stage2`
    - `both`
    are no longer exposed because they depended on `scripts/isaac_sim/terrain_preview/` source modules that are absent in the current repository state
- Reason:
  - the user reported that `control_keyboard.py` could no longer open, and the immediate repo-level cause was a broken stage1 terrain path plus outdated terrain options pointing at missing modules
- Impact:
  - future sessions should treat `control_keyboard.py` as a teleop entry only for:
    - flat ground via `--terrain none`
    - the real training `stage1` terrain via `--terrain stage1`
  - if terrain geometry inspection is needed beyond that scope, use:
    - `preview_stage1_terrain.py`
    - `preview_stage1_tile.py`
    - `preview_stage1_last_six.py`
- Status:
  - completed and verified with `py_compile` plus `--help`

### A consolidated training operations guide now exists under the active RL docs
- Added:
  - `src/rl_lab/complete_car_rl_training/docs/training_workflow_and_tensorboard_guide.md`
- Durable documentation conclusion:
  - the active RL project now has one Chinese guide that consolidates:
    - train command
    - TensorBoard launch command
    - policy playback command
    - keyboard teleop command
    - terrain preview commands
    - local output locations
    - how to read the core TensorBoard figures
  - future sessions that need to explain the RL workflow should start from this guide instead of reconstructing the same commands and reading rules each time
- Status:
  - completed

### TensorBoard in env_isaacLab currently requires setuptools pinned below 81
- Updated:
  - local conda environment `env_isaacLab`
- Durable environment conclusion:
  - with `tensorboard==2.20.0`, `setuptools==82.0.1` in `env_isaacLab` does not provide `pkg_resources`, so the `tensorboard` CLI crashes at startup
  - downgrading to the locally cached `setuptools==80.10.2` restores `pkg_resources` and makes `tensorboard --version` / `tensorboard --logdir ...` work again
- Impact:
  - future package updates in `env_isaacLab` should avoid upgrading `setuptools` to `>=81` unless TensorBoard is updated to a version that no longer imports `pkg_resources`
- Status:
  - completed and verified locally

### Training stage1 terrain now uses an explicit black visual material
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
- Durable implementation conclusion:
  - the live RL terrain mesh at `/World/terrain/stage1` is now created with:
    - `PreviewSurfaceCfg(diffuse_color=(0.0, 0.0, 0.0))`
  - the change affects training-time viewport appearance only
  - physics material, terrain geometry, reset logic, and curriculum logic are unchanged
- Impact:
  - future appearance changes for the training terrain should be made in the runtime terrain env, not in `stage1_terrain.py`
- Status:
  - completed and verified with `py_compile`

### Stage 1 active task is now implemented as flat-only reset on top of the existing stage1 terrain runtime
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py`
- Durable implementation conclusion:
  - the active Stage 1 task now keeps the existing `stage1` terrain map and runtime env, but adds a dedicated:
    - `flat_only_reset`
    switch in `Stage1RuntimeCfg`
  - when `flat_only_reset=True`, all envs are assigned to the `flat` terrain column during reset while still reusing the same terrain mesh, origins table, and runtime-state machinery
  - terrain curriculum is now explicitly switchable through:
    - `Stage1RuntimeCfg.curriculum`
  - for the current default Stage 1 baseline:
    - `flat_only_reset=True`
    - `curriculum=False`
  - the terrain curriculum update function now early-returns when running the flat-only baseline, so the old mixed-terrain reset/curriculum path is preserved for later stages instead of being deleted
- Reason:
  - the user wanted a flat-ground baseline without forking a second flat-only terrain implementation or breaking the later mixed-terrain training path
- Impact:
  - future mixed-terrain work should reuse the same terrain runtime env and simply toggle these runtime settings instead of creating a parallel reset path
- Status:
  - completed and verified with `py_compile`

### Stage 1 observation, action, and reward wiring now matches the new flat-only baseline definition
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/rewards.py`
- Durable implementation conclusion:
  - policy observation order in the active task is now aligned with the agreed Stage 1 baseline:
    - base linear velocity
    - base angular velocity
    - projected gravity
    - 6 spherical-joint positions
    - 6 spherical-joint velocities
    - 6 wheel velocities
    - velocity commands
    - previous action
  - policy action space remains:
    - 6 spherical-joint position targets
    - 6 wheel velocity targets
  - the command space now samples:
    - `lin_vel_x`
    - `ang_vel_z`
    while keeping `lin_vel_y = 0`
  - the reward set now matches the Stage 1 plan:
    - linear-velocity tracking
    - angular-velocity tracking
    - body-orientation stability
    - `lin_vel_z` penalty
    - `ang_vel_xy` penalty
    - action-rate penalty
    - spherical-joint deviation penalty
    - spherical-joint swing penalty
    - termination penalty
  - the previous `alive` reward was removed
- Reason:
  - the user requested that the agreed Stage 1 flat-only baseline should stop living only in planning notes and be written into the active training task
- Impact:
  - future tuning should start from this observation/action/reward set rather than the older generic manager-based template terms
  - later additions such as terrain perception should be treated as explicit Stage 2+ changes, not silently mixed into this Stage 1 baseline
- Status:
  - completed and verified with `py_compile`

### src training helpers no longer use mgdp-prefixed function names
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1_terrain.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_env.py`
- Durable implementation conclusion:
  - helper function names inside the active training code under `src/` were normalized to remove `mgdp`-prefixed identifiers
  - examples:
    - `_mgdp_random_uniform_terrain -> _random_uniform_terrain`
    - `_maybe_add_mgdp_roughness -> _maybe_add_roughness`
    - `_offset_mesh_to_mgdp_frame -> _offset_mesh_to_stage1_frame`
- Reason:
  - the user requested that training-script function names should not be tied to `mgdp` naming
- Impact:
  - future additions in the active `src/` training path should follow neutral, task-local naming instead of reintroducing `mgdp` into helper identifiers
  - this naming cleanup did not change terrain-generation semantics or the stage1 training logic
- Status:
  - completed and verified with `py_compile` plus a follow-up repository search showing no remaining `mgdp` helper names under `src/`

### stage1_terrain.py terrain generator section is now ordered to match terrain_dict
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/stage1_terrain.py`
- Durable implementation conclusion:
  - the public terrain-generator section is now grouped into one contiguous block and ordered to match the configured terrain order:
    - `flat`
    - `slope down`
    - `slope up`
    - `uneven rough`
    - `stairs down`
    - `stairs up`
    - `discrete obstacles`
    - `hurdle`
    - `gap`
    - `ramp`
    - `beam`
    - `new stairs down`
    - `pit`
  - lightweight wrapper functions were added for order/readability:
    - `make_slope_down_tile`
    - `make_slope_up_tile`
    - `make_new_stairs_down_tile`
  - existing core generator names such as `make_slope_tile`, `make_pyramid_tile`, and `make_stairs_tile` were preserved
- Impact:
  - future sessions should keep the terrain-generator block aligned with `Stage1TerrainCfg.terrain_dict` so the file reads in the same order as the configured curriculum terrain list
  - this was a structure/readability cleanup only and did not change terrain-generation behavior
- Status:
  - completed and verified with `py_compile`

### Stage 1 baseline plan was redefined around joint-wheel co-control on low-difficulty mixed terrain
- Updated:
  - `docs/current_status.md`
  - `README.md`
  - `src/rl_lab/complete_car_rl_training/docs/rl_training_route.md`
- Durable research conclusion:
  - the previously used Stage 1 definition based on “fixed spherical joints + wheel-only control” is no longer the active plan
  - the new Stage 1 baseline is:
    - low-difficulty mixed terrain using the current `stage1` terrain source
    - first terrain column is `flat`
    - remaining columns keep different terrain types but under the lowest difficulty setting so they stay close to flat
    - policy observations:
      - base linear velocity
      - base angular velocity
      - projected gravity
      - 6 spherical-joint positions
      - 6 spherical-joint velocities
      - 6 wheel speeds
      - velocity commands
      - previous action
    - policy actions:
      - 6 spherical-joint position targets
      - 6 wheel velocity targets
    - control semantics:
      - spherical joints use position-target control
      - wheels use velocity-target control
    - reward terms:
      - linear-velocity tracking
      - angular-velocity tracking
      - body-posture stability
      - `lin_vel_z` penalty
      - `ang_vel_xy` penalty
      - action-change penalty
      - spherical-joint neutral-deviation / excessive-swing penalty
      - collision penalty
      - termination penalty
    - external terrain perception is explicitly **not** part of the current Stage 1 plan
- Reason:
  - the user decided to replan Stage 1 from scratch and directly validate joint-wheel co-control instead of keeping the older fixed-joint baseline
- Impact:
  - future implementation work should wire the active Isaac Lab task to this new Stage 1 definition
  - older “fixed spherical joints + wheel-only control” descriptions remain historical only and must not be treated as the current default
- Status:
  - planning updated; code implementation not yet switched to this new definition in the active task files

### Stage 1 terrain scope was further narrowed to a flat-only baseline
- Updated:
  - `docs/current_status.md`
  - `README.md`
  - `src/rl_lab/complete_car_rl_training/docs/rl_training_route.md`
- Durable research conclusion:
  - although Stage 1 had briefly been reframed as a low-difficulty mixed-terrain baseline, the user then made the stricter decision that Stage 1 should use a `flat-only baseline`
  - therefore the active Stage 1 terrain scope is now:
    - training uses only `flat` terrain
    - the existing `stage1` terrain set is retained for later non-flat stages or comparison experiments
  - the rest of the Stage 1 task definition stays unchanged:
    - proprioceptive observation
    - 6 spherical-joint position targets
    - 6 wheel velocity targets
    - velocity-tracking reward structure
    - no external terrain perception
- Reason:
  - the user explicitly decided that the first-stage “basic motion policy” should be a clean flat-ground baseline rather than a mixed-terrain baseline
- Impact:
  - future implementation of Stage 1 should not train on the non-flat columns of the current `stage1` terrain map by default
  - mixed terrain should be treated as a later-stage extension or a controlled follow-up experiment
- Status:
  - planning updated; code implementation not yet switched to this narrowed terrain scope in the active task files

### Terrain runtime env was renamed and reduced to terrain import plus runtime-state coordination
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/curriculums.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/events.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/__init__.py`
- Durable implementation conclusion:
  - the old runtime file name `complete_car_stage1_env.py` was replaced with:
    - `complete_car_stage1_terrain_env.py`
  - the registered env class is now:
    - `CompleteCarStage1TerrainEnv`
  - the runtime env file now keeps only:
    - stage1 terrain mesh import
    - terrain runtime tensors such as `terrain_origins / terrain_levels / terrain_types / terrain_class`
    - env-origin synchronization based on those tensors
    - reset-time orchestration that calls into `mdp.curriculums` and `mdp.events`
  - the terrain curriculum update rule was moved into:
    - `mdp/curriculums.py:update_stage1_terrain_curriculum`
  - the terrain-class spawn offset rule was moved into:
    - `mdp/events.py:apply_stage1_spawn_offsets`
- Reason:
  - the user judged that the previous `complete_car_stage1_env.py` mixed too many responsibilities and was hard to understand
- Impact:
  - future work should treat the renamed terrain env as a terrain runtime coordinator rather than as the place to hold all curriculum and reset logic directly
  - new terrain curriculum rules should be added to `mdp/curriculums.py`
  - new spawn/reset offset rules should be added to `mdp/events.py`
- Status:
  - completed and verified with `py_compile`

### Active task no longer relies on a default plane-based TerrainImporter just to import stage1 mesh
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_stage1_terrain_env.py`
  - `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
- Durable implementation conclusion:
  - the active manager-based training scene no longer declares a default:
    - `TerrainImporterCfg(terrain_type="plane")`
  - instead, the terrain runtime env now imports the generated stage1 mesh directly with:
    - `isaaclab.terrains.utils.create_prim_from_mesh`
    - target prim path: `/World/terrain/stage1`
  - environment origins are no longer configured through `scene.terrain.configure_env_origins(...)`
  - they are now synchronized directly by the terrain runtime env through `scene.env_origins`
  - as a result, the previous “create default plane -> delete plane -> import stage1 mesh” workaround is no longer part of the active task path
- Reason:
  - the user explicitly asked to clean up terrain integration so the task does not define a default plane that is immediately removed
- Impact:
  - future work on the active task should treat stage1 terrain as a manually imported trimesh, not as a custom mesh piggybacking on a temporary plane-based terrain importer
  - any code that inspects `scene.terrain` must now handle the possibility that it is `None`
- Status:
  - completed and verified with `py_compile`

## 2026-04-03

### control_keyboard.py now uses the same drive semantics and core control parameters as the RL training task
- Updated:
  - `scripts/isaac_sim/control_keyboard.py`
- Durable implementation conclusion:
  - the keyboard teleop path no longer uses the older smoothed heuristic wheel-speed settings
  - it now mirrors the training task's control structure:
    - ball joints: position targets with `scale = 0.25`
    - wheel joints: velocity targets with `scale = 8.0`
    - same actuator-side gains and limits as training:
      - ball joints: `stiffness = 80`, `damping = 8`, `effort_limit = 120`, `velocity_limit = 6`
      - wheel joints: `stiffness = 0`, `damping = 10`, `effort_limit = 80`, `velocity_limit = 20`
  - the teleop world timing is now aligned to training:
    - `physics_dt = 1/120`
    - `action decimation = 2`
    - therefore keyboard commands are refreshed at `60 Hz` and held across two physics steps, matching the RL task timing structure
- Durable practical implication:
  - future manual tuning of `stiffness / damping` should use this teleop script first, because it now exercises the same position/velocity target semantics as training instead of an older convenience teleop profile
  - the most directly comparable manual wheel-target interval is now `[-8, 8] rad/s` from the action scale, while the PhysX hard cap remains `20 rad/s`

### Training terrain import path currently builds one global stage1 mesh, not one terrain per env
- Rechecked the active RL task registration and training environment implementation:
  - `Complete-Car-Rl-Training-v0` points to `complete_car_stage1_env:CompleteCarStage1Env`
  - inside that env, terrain setup is:
    - remove auto-created default plane under `/World/terrain/terrain`
    - build one `Stage1TerrainCfg` full-map heightfield
    - convert the full map into one trimesh
    - import it once through `self.scene.terrain.import_mesh("stage1", terrain_mesh)`
    - assign per-env spawn points via `configure_env_origins(...)`
- Durable conclusion:
  - the current training code path does **not** intentionally import one full terrain map per environment clone
  - if the user sees “several maps” in the training viewport, future debugging should first distinguish among:
    - one global terrain mesh
    - multiple robot env namespaces under `/World/envs/env_*`
    - leftover default plane or debug visualization artifacts
- Additional local data check:
  - current `stage1` build still produces one full map with:
    - `height_field_raw.shape == (2100, 1300)`
    - `env_origins.shape == (20, 10, 3)`
    - `vertices.shape == (2730000, 3)`
    - `faces.shape == (5453202, 3)`

### A dedicated training-stage export script now exists, but this workstation still cannot reliably save the live RL stage
- Added:
  - `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py`
- Script purpose:
  - instantiate the real training task
  - save the assembled stage to USD
  - dump the full prim tree and `/World/terrain` subtree for direct inspection
- Local execution outcome on this workstation:
  - the script can reach Isaac Lab scene creation for `Complete-Car-Rl-Training-v0`
  - but under the current no-driver / no-CUDA environment, the process exits during or immediately after `gym.make(...)` scene creation and never reaches the script's own `env.reset()` / `save_stage()` section
  - therefore no reliable training-stage USD was produced locally in this session
- Durable implication:
  - future sessions should use this script on a GPU-capable Isaac Lab host first when the goal is to inspect the **actual** training stage instead of the preview stage
  - on the present machine, preview scripts may still run headless, but they are not a substitute for exporting the live RL stage

### export_training_stage.py now rejects directory targets for --save-usd
- The user later attempted to run the export script with:
  - `--save-usd /home/ubuntu/Graduation-Project/results/`
  which is a directory, not a USD filename.
- Durable fix:
  - `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py` now validates that:
    - `--save-usd` is not an existing directory
    - the path ends with `.usd` or `.usda`
- Impact:
  - future stage-export runs should use explicit filenames such as:
    - `/home/ubuntu/Graduation-Project/results/training_stage_num_envs10.usda`
  - this prevents ambiguous “env seems not to start / no file was saved” debugging when the real issue is an invalid output target

### complete_car.usd no longer carries the stale /World/terrain_preview subtree
- The user then requested direct cleanup of the robot asset so the repeated fake terrain would stop appearing in exported training stages.
- Durable diagnosis from the saved training stage:
  - the real training terrain under `/World/terrain` contained only one mesh:
    - `/World/terrain/stage1`
  - the “multiple maps” effect came from:
    - `/World/envs/env_i/Robot/terrain_preview/...`
    repeated once per cloned environment
  - therefore the duplication source was the robot asset reference itself, not the training terrain importer
- Durable fix:
  - added `scripts/isaac_sim/remove_complete_car_terrain_preview.py`
  - created backup:
    - `USD/complete_car.usd.terrain_preview_cleanup.bak`
  - removed:
    - `/World/terrain_preview`
    from:
    - `USD/complete_car.usd`
- Verified:
  - reopening `USD/complete_car.usd` now reports `/World/terrain_preview` as invalid
  - top-level prims are now only:
    - `/World`
    - `/Render`
    - `/physicsScene`
- Impact:
  - future training-stage exports should no longer show one extra `terrain_preview` subtree per `env_i/Robot`
  - if extra terrain-like geometry is still seen later, it should be debugged in the live stage itself rather than blamed on the robot asset preview residue

### Added FK_iteration.m for Agile Eye forward-kinematics symbolic derivation
- Created a new root-level symbolic derivation script:
  - `FK_iteration.m`
- Durable scope now captured in that script:
  - zero-pose base axes are fixed as `u1=[1;0;0]`, `u2=[0;1;0]`, `u3=[0;0;1]`
  - platform-side zero-pose axes are fixed as `v1'=[0;-1;0]`, `v2'=[0;0;-1]`, `v3'=[-1;0;0]`
  - platform attitude is represented with the paper's `R = Rz(phi) * Ry(theta) * Rx(psi)`
  - the forward-kinematics derivation is organized as:
    - `v_i` expansion
    - `w_i` definition
    - three scalar constraints `w_i^T v_i = 0`
    - trivial branch `cos(theta)=0`
    - nontrivial branch `phi = theta3`
    - determinant elimination with `p1..p4` and `q1,q2`
- Important inherited note:
  - the second-leg constraint from the raw dot product `w2^T v2` is the negative of the paper's displayed Eq. (9c)
  - this is expected because the paper explicitly rewrites that equation after multiplying both sides by `-1`
  - future sessions should not treat this sign flip as a bug
- Verification result:
  - symbolic cross-check confirmed zero residual for the `v_i` expansions, Eqs. `(9b)`, `(9c)` up to global sign, `(9d)`, the trivial-branch reductions, the nontrivial linearized system, and the determinant form of Eq. `(17)`

## 2026-04-02

### preview_stage1_tile.py now defaults to an all-tile separated gallery instead of single-tile-only preview
- Updated:
  - `scripts/isaac_sim/preview_stage1_tile.py`
- Durable behavior:
  - default launch now loads the current `20 x 10` stage1 course map as:
    - `200` standalone tile meshes
    - each tile imported separately under `/World/terrain/tile_rXX_cYY_<terrain_name>`
    - tiles laid out with configurable spacing so they do not stitch into one continuous heightfield
  - the script still supports:
    - `--single-tile --row/--col` for the old single-tile inspection mode
    - `--terrain-name <name>` for generating one explicit terrain class as a standalone tile
  - origin markers are no longer tied to `TerrainImporter.configure_env_origins()`
  - instead, the script now places one explicit frame marker at each standalone tile origin
- Verified locally with:
  - `python3 -m py_compile scripts/isaac_sim/preview_stage1_tile.py`
  - `python scripts/isaac_sim/preview_stage1_tile.py --help`
  - `python scripts/isaac_sim/preview_stage1_tile.py --list-terrains`
  - `timeout 120s python -u scripts/isaac_sim/preview_stage1_tile.py --headless --device cpu --frames 1`
  - `timeout 90s python -u scripts/isaac_sim/preview_stage1_tile.py --headless --device cpu --frames 1 --single-tile --row 0 --col 0`
- Impact:
  - future sessions should treat `preview_stage1_tile.py` as the default entry for visually checking all individual stage1 tiles at once
  - use `preview_stage1_terrain.py` only when the goal is to inspect the fully stitched large terrain map

### A dedicated Isaac Sim single-tile preview entry now exists for stage1 terrains
- Added:
  - `scripts/isaac_sim/preview_stage1_tile.py`
- Durable behavior:
  - previews exactly one `stage1` terrain tile instead of the full `20 x 10` course map
  - supports two selection modes:
    - derive the tile from the current course map via `--row/--col`
    - explicitly choose a terrain class via `--terrain-name`
  - loads `stage1_terrain.py` directly from file path instead of importing the full task package tree, so:
    - `--list-terrains` works without booting Isaac Sim
    - the script avoids the earlier `pxr` import problem triggered by pre-app package imports
  - removes the auto-created default plane before importing the custom tile mesh
  - centers the tile at world origin by default
  - only spawns the robot when `--spawn-car` is explicitly requested
- Verified locally with:
  - `python3 -m py_compile scripts/isaac_sim/preview_stage1_tile.py`
  - `python scripts/isaac_sim/preview_stage1_tile.py --list-terrains`
  - `timeout 60s python -u scripts/isaac_sim/preview_stage1_tile.py --headless --device cpu --frames 1 --row 0 --col 0`
- Impact:
  - future sessions that need to inspect terrain geometry should use the single-tile preview first, instead of reopening the full-map preview path
  - if a user asks "what does one tile really look like", this script is now the default inspection entry

### complete_car.usd has now been inspected directly and still carries a top-level /physicsScene
- Generated a direct prim-tree dump of:
  - `USD/complete_car.usd`
  into:
  - `results/complete_car_usd_tree.txt`
- Durable structure summary:
  - robot root is under `/World/complete_car_alternative`
  - most rigid bodies follow a repeated pattern:
    - `visuals`
    - `collisions`
    - mesh/material children under those subtrees
  - wheel and equivalent spherical-joint articulation connections are stored under:
    - `/World/complete_car_alternative/joints`
  - onboard sensors currently present in the asset include:
    - `Imu_Sensor`
    - `Stereo_Vision_Camera/Camera_left`
    - `Stereo_Vision_Camera/Camera_right`
    - `Example_Rotary` lidar
  - the USD file still contains a top-level:
    - `/physicsScene :: PhysicsScene`
- Impact:
  - future sessions should remember that `complete_car.usd` is not a pure robot-only asset yet
  - when referenced into a larger scene, the embedded `/physicsScene` remains a cleanup target and should not be forgotten during later stage debugging

### preview_stage1_terrain.py --save-usd is not currently producing an exported USD file in this headless CPU environment
- Re-ran:
  - `python scripts/isaac_sim/preview_stage1_terrain.py --headless --device cpu --frames 1 --save-usd ...`
- Durable observation:
  - the script starts Isaac Sim headless and logs normal no-GPU / no-driver warnings for this workstation
  - however, no `stage1_preview.usd/usda` file is actually written to the repository
  - the current reproducible log capture is:
    - `results/preview_save_unbuffered.log`
- Important scope note:
  - this does **not** invalidate the earlier scene-placement diagnosis
  - it only means that in the present execution environment, the preview stage could not be inspected via an exported USD layer
- Impact:
  - future sessions should not assume `--save-usd` is currently reliable on this machine
  - if exact live-stage inspection is needed again, prefer either:
    - a GUI-capable Isaac Sim session, or
    - a purpose-built script that dumps stage prim paths directly instead of relying on `save_stage()`

### stage1 mesh must also be shifted by -border_size in x/y to line up with MGDP env_origins
- After the default-plane issue was already fixed, the user still reported that in Isaac Sim:
  - the terrain looked like two large maps stacked together
  - tile axes seemed to start from the right side of the map
  - the leftmost part of the map had no terrain-origin markers
- Durable diagnosis:
  - `preview_stage1_terrain.py` and `stage1_terrain.py` were already using the same terrain-generation source
  - the remaining mismatch was spatial placement, not generation parameters
  - MGDP places the full terrain mesh with an extra transform:
    - `x -= border_size`
    - `y -= border_size`
  - without this shift, the imported mesh still includes the `25 m` border in world coordinates, while `env_origins` are computed as if tile `(0, 0)` already starts at world `(0, 0)`
  - this makes the origin markers appear shifted right/up by about `border_size / terrain_size = 25 / 8 ~= 3.125` tiles
- Durable fix:
  - keep deleting the auto-created default plane
  - also shift the imported stage1 mesh by `(-border_size, -border_size, 0)` before calling `import_mesh(...)`
  - apply the same rule in both:
    - `scripts/isaac_sim/preview_stage1_terrain.py`
    - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
- Impact:
  - future sessions should treat "left-side tiles missing origin markers" as a border-frame alignment bug first
  - do not reopen terrain-function debugging unless the mesh and env-origin frames are already confirmed aligned

### Stage1 preview and stage1 RL env were both stacking a default plane under the imported stage1 mesh
- Reproduced the user's report that in Isaac Sim the stage1 terrain looked overlapped and an extra grid-like ground still existed.
- Root cause was scene-side, not the MGDP heightfield conversion itself:
  - both
    - `scripts/isaac_sim/preview_stage1_terrain.py`
    - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
    initialized `TerrainImporterCfg` with `terrain_type="plane"`
  - Isaac Lab therefore auto-created `/World/terrain/terrain`
  - both paths then additionally called `import_mesh("stage1", ...)`
  - result: the default plane and the custom stage1 mesh coexisted in the same scene
- Durable fix:
  - after the scene terrain importer is created, explicitly delete the auto-created plane prim and remove it from `terrain_prim_paths`
  - only then import the custom stage1 mesh and configure terrain origins
- Verified locally with:
  - `python3 -m py_compile scripts/isaac_sim/preview_stage1_terrain.py`
  - `python3 -m py_compile src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/complete_car_stage1_env.py`
  - `python scripts/isaac_sim/preview_stage1_terrain.py --headless --frames 1`
- Impact:
  - future sessions should not misdiagnose the extra ground plane as an MGDP terrain-generation bug
  - any future custom-mesh terrain path that reuses `TerrainImporterCfg(terrain_type="plane")` must remove the auto-created plane before importing its own mesh

### stage1_terrain.py has now been pulled much closer to MGDP's stage1 geometry semantics
- Rechecked the local terrain generator against:
  - `/home/ubuntu/MGDP/legged_gym/models/MGDP/stage1/001/random_dog_config_stage1.py`
  - `/home/ubuntu/MGDP/legged_gym/legged_gym/utils/terrain.py`
  - `/home/ubuntu/MGDP/legged_gym/legged_gym/utils/new_terrains/add_mix_terrain.py`
  - `/home/ubuntu/MGDP/isaacgym/python/isaacgym/terrain_utils.py`
- Durable implementation update:
  - local `stage1_terrain.py` now uses MGDP-style generation semantics for:
    - `slope down`
    - `pyramid`
    - `stairs down`
    - `stairs up`
    - `discrete obstacles`
    - `hurdle`
    - `gap`
    - `ramp`
    - `beam`
    - `new stairs down`
    - `pit`
  - `env_origin` is now computed with the same center `2m x 2m` patch rule MGDP uses for `mix`, instead of the previous local special-case offsets for `gap/pit/hurdle/beam`
  - `preview_stage1_terrain.py` and `stage1_terrain.py` are consistent at the mesh-generation level because preview directly calls `Stage1TerrainCfg` and `build_stage1_terrain_data()`
- Important inherited caveat:
  - even with aligned generation logic, the default `terrain_dict` weights and `choice = col / num_cols + 0.001` still mean that with `num_cols = 10`, only the first five terrain classes appear in the curriculum map
  - this is a consequence of the current MGDP weight table combined with the chosen column count, not a mismatch between preview and generator code
- Verification:
  - `python3 -m py_compile .../stage1_terrain.py`
  - direct file-level import and `build_stage1_terrain_data()` succeeded locally
  - `python scripts/isaac_sim/preview_stage1_terrain.py --headless --frames 1` exited successfully on this workstation

### preview_stage1_terrain.py must not define --headless manually when using AppLauncher
- Reproduced a startup failure from:
  - `python scripts/isaac_sim/preview_stage1_terrain.py`
- Root cause:
  - the script manually added `--headless` to `argparse`
  - `isaaclab.app.AppLauncher.add_app_launcher_args()` also injects `--headless`
  - Isaac Lab therefore raised a duplicate-argument `ValueError` before app launch
- Durable fix:
  - remove the manual `parser.add_argument("--headless", ...)`
  - rely on `AppLauncher` to provide `--headless`
- Verified locally with:
  - `python3 -m py_compile scripts/isaac_sim/preview_stage1_terrain.py`
  - `python scripts/isaac_sim/preview_stage1_terrain.py --help`

### stage1_terrain.py has been expanded to a full MGDP-stage1 terrain-generation layer, but RL integration is still pending
- The teaching-mode implementation in:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/stage1_terrain.py`
  has now been extended beyond the earlier skeleton.
- Durable implementation status:
  - `Stage1TerrainCfg` / `Stage1TerrainData` are in place
  - the stage1 course map can generate `height_field_raw`, `env_origins`, `terrain_type`, `vertices`, `faces`, and `x_edge_mask`
  - all MGDP stage1 terrain names now have corresponding tile-generator functions:
    - `slope down`
    - `pyramid`
    - `stairs down`
    - `stairs up`
    - `discrete obstacles`
    - `hurdle`
    - `gap`
    - `ramp`
    - `beam`
    - `new stairs down`
    - `pit`
  - key geometry parameters have been connected to `difficulty`
- Important inherited caveat:
  - the current column-selection logic still follows MGDP's original style:
    - `choice = j / num_cols + 0.001`
    - thresholds from cumulative `terrain_proportions`
  - under the current stage1 weight table and `num_cols = 10`, the generated `20 x 10` map actually reaches only the early terrain indices during normal `build_stage1_map()` execution
  - this should be treated as a faithful consequence of the original configuration logic, not as a bug introduced by the local port
- Impact:
  - future sessions should treat terrain-generation groundwork as largely complete
  - the next engineering focus should move to origin refinement, preview/self-check tooling, and Isaac Lab environment integration rather than rebuilding terrain generators again

### Direct task-local MGDP stage1 RL integration was intentionally withdrawn
- The previous round had already added task-local rough-terrain files under:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/`
- The user explicitly rejected that working mode because it skipped the requested teaching process and jumped straight to a complete implementation.
- Durable conclusion:
  - do not assume the task package currently contains a valid `MGDP stage1` terrain-training integration
  - the rough-terrain code path was intentionally rolled back
  - future work must resume from the pre-integration baseline and rebuild step by step in teaching mode
- Impact:
  - future sessions should separate the confirmed stage-1 target scheme from the actual code state
  - the current codebase should be treated as “scheme chosen, implementation pending”

## 2026-04-01

### Stage-1 RL mainline switched from flat goal-navigation to MGDP stage1 rough-terrain velocity tracking
- The user explicitly chose to stop using the previously planned stage-1 task formulation:
  - flat ground
  - goal-directed locomotion
- The new durable stage-1 definition is now:
  - `MGDP stage1` mixed terrain
  - fixed spherical joints
  - wheel-only control
  - velocity-tracking task
- Engineering impact:
  - the active Isaac Lab task `Complete-Car-Rl-Training-v0` should no longer be treated as a flat-ground goal-navigation baseline
  - future stage-1 work should align commands, rewards, resets, and curriculum with rough-terrain velocity tracking first

### MGDP stage1 terrain generation was once integrated into the Isaac Lab task package, but this no longer reflects the current code state
- Added task-local terrain integration files under:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_rl_training/`
- Historical note:
  - that direct integration attempt was later withdrawn on `2026-04-02`
  - future sessions must not assume those files still exist

## 2026-03-31

### new interactive bash shells now default to env_isaacLab instead of base
- Rechecked the current global conda startup behavior on this workstation.
- Observed before the change:
  - `conda config --show auto_activate_base` returned `True`
  - a fresh interactive `bash` session entered `base` by default
- Updated the machine-level shell startup so that:
  - `~/.condarc` now sets `auto_activate: false`
  - `~/.bashrc` now auto-runs `conda activate env_isaacLab` for interactive shells after the normal `conda init` block
- Verified locally with:
  - `bash -ic 'printf "%s\n" "CONDA_DEFAULT_ENV=$CONDA_DEFAULT_ENV" "CONDA_PREFIX=$CONDA_PREFIX"'`
- Durable conclusion:
  - on this machine, future interactive `bash` sessions should be expected to start inside `env_isaacLab`, not `base`
  - if a later session unexpectedly lands in `base`, check `~/.bashrc` and `~/.condarc` before diagnosing repository code or Isaac environment issues

### control_keyboard teleop now survives Stop -> Play in Isaac Sim
- Rechecked the user's report that after pressing the Isaac Sim toolbar `Stop` and then `Play`, the vehicle no longer responded to keyboard teleop.
- Durable diagnosis:
  - this was not only a focus issue
  - `control_keyboard.py` initialized the articulation only once during startup
  - according to the local Isaac Sim 5.1 manual, articulation assets must be re-initialized when the timeline goes from `stopped` back to `playing`
- Updated `scripts/isaac_sim/control_keyboard.py` so interactive teleop now:
  - detects when the timeline stops back to timestep `0`
  - clears held key state on stop / pause transitions
  - calls `world.reset()` and re-runs `robot.initialize()` when `Play` resumes after a stop
  - refreshes wheel / ball-joint indices and resets command targets from the current articulation state
- Additional compatibility fix:
  - moved the `mgdp_gallery_builder` import in `control_keyboard.py` to lazy import inside the full-gallery branch
  - this prevents the old host `python.sh` path for `--terrain none` or single-tile terrain from failing early due to missing `pydelatin`
- Verified locally with:
  - `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`
  - `timeout 180s python3 -u scripts/isaac_sim/control_keyboard.py --terrain none --headless --frames 1`
- Durable conclusion:
  - future sessions should treat `Stop -> Play` as a state transition that requires articulation reinitialization inside this teleop script
  - full MGDP gallery support must remain lazily imported so the legacy host teleop path keeps working

### terrain_builder create_box is now idempotent for reused prim paths
- After the MGDP gallery integration, the user hit:
  - `pxr.Tf.ErrorException`
  - `The xformOp 'xformOp:translate' already exists in xformOpOrder`
- Root cause:
  - `scripts/isaac_sim/terrain_preview/terrain_builder.py:create_box()` always called `AddTranslateOp()` and `AddScaleOp()`
  - when the same prim path already existed in the stage, USD rejected the duplicate xform op creation
- Fixed behavior:
  - `create_box()` now scans existing ordered xform ops
  - it reuses an existing translate / scale op when present
  - it only adds the op if it does not already exist
- Durable conclusion:
  - terrain helper functions should be written to tolerate re-definition on an existing stage, especially for teleop and interactive workflows that may reuse the same prim paths across reruns

### control_keyboard teleop now supports full MGDP stage galleries
- Added a shared MGDP gallery builder at:
  - `scripts/isaac_sim/terrain_preview/mgdp_gallery_builder.py`
- Refactored `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py` to use that shared builder instead of keeping a separate copy of the stage1/stage2 construction logic.
- Updated `scripts/isaac_sim/control_keyboard.py` so `--terrain` now supports:
  - full MGDP `stage1`
  - full MGDP `stage2`
  - `both`
- Durable teleop behavior:
  - single-tile terrain options still use the previous lightweight tile injection path
  - full MGDP gallery options now build the complete terrain section into the same teleop stage before `World.reset()`
  - the terrain root `/World/terrain_preview` now also receives the shared physics material binding, not only the wheel collision roots
- Durable startup decision:
  - `control_keyboard.py` should still re-exec from conda into host `/home/ubuntu/isaacsim/python.sh` for the old single-tile / no-terrain path
  - but for `--terrain stage1|stage2|both`, it must stay in `env_isaacLab` Python because the MGDP gallery build depends on packages such as `pydelatin` that are available there
- Verified locally with:
  - `conda run -n env_isaacLab python -u scripts/isaac_sim/control_keyboard.py --terrain stage1 --headless --frames 1`
  - `conda run -n env_isaacLab python -u scripts/isaac_sim/control_keyboard.py --terrain stage2 --headless --frames 1`
- Observed result:
  - both commands completed successfully with exit code `0`
  - `stage1` built a full gallery with bounds about `[-4.0, -4.0, -1.98]` to `[205.9, 125.9, 1.98]`
  - `stage2` built a full gallery with bounds about `[-5.0, -2.0, -0.64]` to `[104.95, 47.95, 1.54]`
  - the robot origin is now aligned near the first gallery spawn hint around world `(0, 0, z)`

## 2026-03-30

### MGDP terrain-generation and curriculum port for Isaac Sim
- Copied the MGDP terrain-generation code needed for terrain preview into:
  - `scripts/isaac_sim/terrain_preview/mgdp_port/terrain.py`
  - `scripts/isaac_sim/terrain_preview/mgdp_port/terrain_utils.py`
  - `scripts/isaac_sim/terrain_preview/mgdp_port/new_terrains/`
- Added local Isaac-Sim-side support modules:
  - `scripts/isaac_sim/terrain_preview/mgdp_port/configs.py`
  - `scripts/isaac_sim/terrain_preview/mgdp_port/curriculum.py`
- Durable implementation decision:
  - this repository should not depend on importing MGDP's original `isaacgym` / `legged_gym` package layout at runtime for terrain preview
  - the preview path should use the copied local `mgdp_port` package with relative imports only
- The new preview entry:
  - `scripts/isaac_sim/terrain_preview/mgdp_terrain_preview.py`
  now builds actual MGDP-derived terrain meshes for `stage1` and `stage2` inside Isaac Sim and adds curriculum origin markers for inspection.

### Isaac Sim conda launch path for the MGDP terrain preview
- Reworked `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh` so it now:
  - sources conda
  - activates `env_isaacLab`
  - launches `python mgdp_terrain_preview.py`
- Durable repository rule for this preview path:
  - the default launch route is the conda environment `env_isaacLab`
  - do not switch this wrapper back to the old `isaacsim/python.sh` path unless the environment strategy for the whole repository changes explicitly

### Isaac Sim numerical-stack repair for window-mode startup
- Reproduced that the user's `env_isaacLab` had drifted to:
  - `numpy 2.4.3`
  - `scipy 1.17.1`
- Confirmed from installed package metadata that:
  - `isaacsim-kernel` requires `numpy==1.26.0`
  - `isaaclab` requires `numpy<2`
- Restored the active numerical stack to:
  - `numpy==1.26.0`
  - `scipy==1.14.1`
- After this repair, the MGDP terrain preview was verified locally with both headless and window startup:
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --headless --frames 1 --gallery stage1`
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --headless --frames 1 --gallery stage2`
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --frames 1 --gallery stage1`
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --frames 1 --gallery stage2`
- Durable conclusion:
  - for this repository, the MGDP terrain preview is now actually launchable inside Isaac Sim from `env_isaacLab`
  - if future Isaac Sim startup fails again with extension import or binary-compatibility errors, first check whether `numpy` has drifted away from `1.26.0`

### GitHub push blocker from SAT CAD files
- A full-repository push on `main` was rejected by GitHub because `Drawing/完整小车等效串联.SAT` is about 194 MB, exceeding GitHub's 100 MB normal-file limit.
- Durable repository rule for this project:
  - `.SAT` CAD files should be ignored by default and should not be uploaded through normal Git history
  - if these assets ever need versioned remote storage, use Git LFS or another artifact channel explicitly instead of plain `git push`

### Git ignore scope for local Isaac Sim artifacts
- Expanded the repository-root `.gitignore` so normal pushes on `main` now exclude local-only artifacts such as:
  - `.cache/`
  - `outputs/`
  - `__pycache__/`
  - `*.py[cod]`
  - `*.bak`
- Durable repository rule:
  - Isaac Sim runtime caches, generated USD exports, Python bytecode caches, and local backup files should stay out of normal Git history
  - only source files, documentation, and intentional result artifacts should be staged for routine pushes

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

### Isaac Sim terrain preview wrapper path and execute-bit fix
- Verified this workstation's available Isaac Sim launcher path is:
  - `/home/ubuntu/isaacsim/python.sh`
- Updated `scripts/isaac_sim/terrain_preview/run_terrain_preview.sh` to use that path as the default `ISAAC_SIM_ROOT`.
- Restored the wrapper's execute permission so it can be launched directly with:
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --gallery stage1`
- Durable conclusion:
  - for this machine, `/home/lbz/isaac-sim` is an outdated default and should not be reused in the terrain-preview wrapper
  - if the script still fails after this fix, the next diagnosis target remains the host graphics / driver stack rather than the wrapper path itself

### Isaac Sim terrain preview conda-wrapper and import-order fix
- Reproduced the user's failure under the active `env_isaacLab` conda environment:
  - `ModuleNotFoundError: No module named 'omni.timeline'`
- Root cause was not the terrain logic itself. It was a startup-chain issue:
  - `run_terrain_preview.sh` inherited active `CONDA_*` variables
  - `mgdp_terrain_preview.py` imported `omni.*` before `SimulationApp` initialization
- Fixed both sides:
  - `run_terrain_preview.sh` now unsets the common `CONDA_*` variables before delegating to Isaac Sim's `python.sh`
  - `mgdp_terrain_preview.py` now creates `SimulationApp` first and imports `omni.timeline` / `omni.usd` afterward
- Revalidated with:
  - `./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --headless --frames 1 --gallery stage1`
- Observed result:
  - the script completed successfully and generated `outputs/isaacsim/mgdp_terrain_stage1.usd`
  - the previous `omni.timeline` import failure is resolved
- Durable conclusion:
  - on this repository, the terrain-preview script is now runnable from the active conda shell through the wrapper without requiring manual deactivation
  - remaining GPU / Vulkan / display warnings during Isaac Sim startup do not prevent the current headless USD export path from finishing successfully

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

### Keyboard teleop ground contact and speed tuning
- Rechecked `scripts/isaac_sim/control_keyboard.py` after the user reported that forward/backward motion looked like the chassis being dragged instead of the wheels driving.
- Durable diagnosis:
  - the wheel velocity command path itself was working
  - the real issue under `--terrain none` was that the stage had no usable ground contact, so the robot could fall or lose meaningful wheel-ground traction
- Fixed the teleop script so that when `--terrain none` is used it now:
  - creates a runtime `ground plane`
  - binds one shared physics material to the ground and all six wheel collision roots
  - uses `static_friction = 0.5`
  - uses `dynamic_friction = 0.5`
- Also reduced the default teleop aggressiveness:
  - `WHEEL_LINEAR_SPEED = 2.5`
  - `WHEEL_TURN_SPEED = 1.0`
  - `BALL_JOINT_DELTA = 0.005`
  - wheel smoothing alpha `= 0.10`
  - ball-joint smoothing alpha `= 0.10`
- Durable control logic summary for future sessions:
  - `W/S` drive all six wheels forward or backward with the same base wheel-speed target
  - `A/D` add left-right differential wheel speed for turning
  - numeric keypad keys increment the six equivalent spherical-joint pose targets
  - both wheel commands and ball-joint pose commands already use first-order smoothing
- Verification performed:
  - `python3 -m py_compile scripts/isaac_sim/control_keyboard.py`
  - `timeout 90s python -u scripts/isaac_sim/control_keyboard.py --terrain none --headless --frames 1` exited with code `0`
  - a standalone Isaac Sim diagnostic with the same ground/material setup showed the chassis moved forward by about `0.36 m` over 120 physics steps while wheel velocities stayed near `1 rad/s`

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

## 2026-03-30

### control_keyboard.py startup path revalidated
- Revalidated `USD/complete_car.usd` under host Isaac Sim and confirmed again that the live robot root is `/World/complete_car_alternative`, not `/World/complete_car_final`.
- Updated `scripts/isaac_sim/control_keyboard.py` to target `/World/complete_car_alternative`.
- Added an automatic re-exec path so that when the script is launched from an active conda shell it restarts itself through `/home/ubuntu/isaacsim/python.sh` before importing `SimulationApp`.
- Added headless-smoke support to the script:
  - `--headless`
  - `--frames`
  - automatic fallback to headless smoke mode when no usable X display is available
- Removed the earlier in-script `--portable-root` injection because it caused very slow or stalled host startup on this machine, while the normal host Isaac Sim cache path starts quickly and cleanly.
- Host verification outcome:
  - `python -u scripts/isaac_sim/control_keyboard.py --terrain none --headless --frames 1` now exits successfully
  - `python -u scripts/isaac_sim/control_keyboard.py --terrain none` now starts successfully and stays alive in interactive mode until externally interrupted
- Impact:
  - future sessions should treat `/World/complete_car_alternative` as the current runtime root for `control_keyboard.py`
  - if the script is reported as failing again, first distinguish between real Python/asset failures and host graphics-stack issues rather than reverting the prim path back to `complete_car_final`
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

## 2026-04-03

### Training-stage multiple-map diagnosis and complete_car asset cleanup
- Added `src/rl_lab/complete_car_rl_training/scripts/export_training_stage.py` to instantiate the real training task `Complete-Car-Rl-Training-v0`, save the assembled stage to `.usd/.usda`, and dump the full prim tree plus `/World/terrain` subtree.
- Durable inspection conclusion from exported training stage:
  - the real training terrain appears only once as `/World/terrain/stage1`
  - the "multiple maps" seen in Isaac Sim were not caused by repeated terrain import in the training env
  - the repeated fake maps came from `/World/terrain_preview` embedded in `USD/complete_car.usd`, which was then cloned under every `env_i/Robot`
- Durable engineering conclusion:
  - `complete_car_stage1_env.py` still imports the training terrain only once
  - if the stage visually shows many terrain copies in future, first inspect whether the robot asset itself contains preview geometry before modifying terrain-generation logic
- Removed `/World/terrain_preview` from `USD/complete_car.usd` and created backup `USD/complete_car.usd.terrain_preview_cleanup.bak`.
- Verification result after cleanup:
  - reopening `USD/complete_car.usd` confirms `/World/terrain_preview` is invalid
  - top-level prims remain `/World`, `/Render`, `/physicsScene`
- Status: inherited default for future sessions is that `complete_car.usd` should remain a robot-only asset and must not carry terrain preview content.

### Stage1 terrain dictionary now includes flat as the first entry
- Implemented the user's requested minimal change in `stage1_terrain.py`:
  - inserted `"flat": 0.2` as the first item in `terrain_dict`
  - added the corresponding `make_tile_by_name("flat") -> make_flat_tile(...)` dispatch
  - adjusted the `slope down` midpoint calculation so the old descending/ascending split still points to the `slope down` interval after `flat` was inserted ahead of it
- Durable consequence under the current unchanged `choice = col / num_cols + 0.001` logic and default `num_cols = 10`:
  - the first 10 columns now map to `flat x2 -> slope down x2 -> pyramid x2 -> stairs down x2 -> stairs up x2`
- Status: this is a deliberate implementation change to the current local Stage1 curriculum, while still preserving the existing `choice`-based column selection framework.

### Stage1 first-ten-column mapping changed to explicit single-type thresholds
- Updated `stage1_terrain.py` so the first part of `terrain_dict` now encodes an explicit per-column mapping under the existing `choice = col / num_cols + 0.001` rule.
- Durable current mapping for default `num_cols = 10`:
  - col 1: `flat`
  - col 2: `slope down`
  - col 3: `slope up`
  - col 4-5: `uneven rough`
  - col 6-7: `stairs down`
  - col 8-9: `stairs up`
  - col 10: `discrete obstacles`
- Implementation details:
  - added an explicit `slope up` terrain name
  - `slope down` is now always generated with `descending=True`
  - `slope up` is now always generated with `descending=False`
  - the former public terrain name `pyramid` has been renamed to `uneven rough` because the generated shape is better described as uneven / undulating rough terrain rather than a tower-like pyramid
- Status: this change preserves the existing threshold-based column-selection mechanism, but the first-ten-column curriculum is now intentionally hand-shaped to match the user's requested visual order.

### Independent preview path for the last six stage1 terrain types
- Added `scripts/isaac_sim/preview_stage1_last_six.py` as a separate Isaac Sim preview entry that does not modify `stage1_terrain.py`.
- Durable behavior:
  - default mode loads `terrain_names[-6:]` as a one-row gallery
  - the current selected set is `hurdle`, `gap`, `ramp`, `beam`, `new stairs down`, `pit`
  - each selected terrain is generated by `make_tile_by_name(...)` and imported as an independent mesh, following the same standalone-preview style used by `preview_stage1_tile.py`
- Project implication:
  - future visual inspection of the tail terrain set should use this dedicated script instead of temporarily reordering `terrain_dict` in the training generator.

### preview_stage1_tile.py restored and preview_stage1_last_six.py upgraded to 20x10 gallery mode
- Restored `scripts/isaac_sim/preview_stage1_tile.py` to its original responsibility:
  - default mode again shows the full `20 x 10` stage1 tile gallery
  - `--list-terrains` again reports the complete stage1 terrain set
- Updated `scripts/isaac_sim/preview_stage1_last_six.py` so it now follows the same gallery semantics as `preview_stage1_tile.py`, but only uses `terrain_names[-6:]`.
- Durable behavior from now on:
  - `preview_stage1_tile.py` remains the full stage1 gallery entry
  - `preview_stage1_last_six.py` is the dedicated `20 x 10` gallery entry for `hurdle`, `gap`, `ramp`, `beam`, `new stairs down`, `pit`
  - in `preview_stage1_last_six.py`, gallery tiles are assigned explicitly from the last-six terrain list by column cycling, rather than by the original full-curriculum column-selection logic

### control_keyboard.py stage1 now uses the real training terrain path
- Updated `scripts/isaac_sim/control_keyboard.py` so `--terrain stage1` no longer loads the old preview gallery terrain.
- Durable current behavior:
  - `--terrain stage1` directly calls the same local `build_stage1_terrain_data()` path used by training
  - the full terrain mesh is shifted by `-border_size` in `x/y`, matching `CompleteCarStage1Env`
  - the mesh is imported under `/World/terrain/stage1/mesh`
  - the robot is moved to the first training env origin `[4.0, 4.0, 0.3]`
- Durable scope boundary:
  - `--terrain stage2|both` still use the older MGDP gallery preview path
  - only the `stage1` teleop terrain path has been aligned to the real training terrain
- Verification result:
  - `timeout 90s python -u scripts/isaac_sim/control_keyboard.py --terrain stage1 --headless --frames 1` completed successfully in the current environment
  - runtime logs confirmed the new terrain import path, terrain friction binding target `/World/terrain/stage1/mesh`, robot spawn reposition, and completion of the smoke run

## 2026-04-07

### RSL-RL observation group mapping fix for Stage1 training
- Diagnosed the training launch failure after environment creation:
  - scene creation, action manager, observation manager, reward manager, and termination manager all initialized successfully
  - the actual failure happened when `OnPolicyRunner` constructed PPO and resolved observation sets
- Durable root cause:
  - the environment exports a single observation group named `FlatBaseline`
  - the local PPO config did not define `obs_groups`
  - with the current `rsl_rl` version, an empty `obs_groups` no longer auto-resolves to actor/critic unless the environment exposes groups named `actor`, `critic`, or `policy`
  - therefore runner construction failed with:
    - missing `actor` key in `obs_groups`
    - no suitable observation group found in environment observations
- Implemented fix:
  - in `tasks/manager_based/agents/rsl_rl_ppo_cfg.py`, added
    - `obs_groups = {"actor": ["FlatBaseline"], "critic": ["FlatBaseline"]}`
- Impact:
  - the current Stage1 baseline now explicitly tells `rsl_rl` to use the sole proprioceptive observation group for both actor and critic
  - future sessions should treat `obs_groups` as a required part of local PPO config whenever observation group names are custom and not `policy`

### Training comparison: 2026-04-07_12-25-02 vs 2026-04-06_21-59-12
- Compared the two Stage1 runs after the user observed that the newer policy tends to spin in place during playback.
- Durable conclusion:
  - the degradation in `2026-04-07_12-25-02` cannot be attributed to removing `chassis_collision`
  - in the older run, `Episode_Reward/chassis_collision` stayed at `0.0` through the end, so that term was not actively shaping behavior
- Quantitative comparison:
  - old run:
    - `Train/mean_reward`: `0.449 -> 2.972`
    - `Train/mean_episode_length`: `25 -> 397`
    - `Metrics/base_velocity/error_vel_xy`: `0.0 -> 1.293`
    - `Metrics/base_velocity/error_vel_yaw`: `0.0 -> 1.756`
  - new run:
    - `Train/mean_reward`: `0.354 -> 1.320`
    - `Train/mean_episode_length`: `29 -> 741.56`
    - `Metrics/base_velocity/error_vel_xy`: `0.0 -> 3.785`
    - `Metrics/base_velocity/error_vel_yaw`: `0.0 -> 3.913`
- Important interpretation constraint:
  - `mean_episode_length` is not directly comparable in absolute value because `episode_length_s` changed from `8s` to `16s`
  - normalized by max horizon, the new run is not better on survival
  - both runs finish with `Episode_Termination/time_out = 1.0` and no `root_too_low / bad_orientation / ball_joint_out_of_bounds`, so the new policy is mainly learning to survive, not to track
- Additional confounding changes between the two runs:
  - `wheel_joints.damping: 10.0 -> 1e4`
  - `ball_joints.stiffness/damping: 80/8 -> 100/10`
  - `lin_vel_x` command range: `[-1, 1] -> [-2, 2]`
  - `episode_length_s: 8 -> 16`
- Durable diagnosis:
  - the current “spin in place / weak locomotion” behavior is more consistent with a stable-but-unproductive local optimum caused by changed actuation and harder commands than with removal of the collision term
  - without wheel-ground contact metrics, playback alone cannot prove that the wheels are airborne; current scalars only prove poor task execution, not the exact contact failure mode
- Status:
  - future comparisons that aim to isolate the effect of reward removal must revert to single-variable changes instead of bundling actuator, command, and horizon edits into the same run

### Training diagnosis: 2026-04-07_13-13-46 with wheel damping 1e3, 512 envs, 400 iterations
- Diagnosed run `2026-04-07_13-13-46` after the user changed:
  - wheel damping to `1e3`
  - `num_envs` to `512`
  - `max_iterations` to `400`
- Durable result:
  - compared with `2026-04-07_12-53-43`, this run shows a genuine improvement in task performance, not just a reward-rescaling artifact
- Key metrics at the end of training:
  - `Train/mean_reward`: `26.43`
  - `Train/mean_episode_length`: `880.97`
  - `Metrics/base_velocity/error_vel_xy`: `0.713`
  - `Metrics/base_velocity/error_vel_yaw`: `1.946`
  - `Episode_Reward/track_lin_vel_xy`: `1.79`
  - `Episode_Reward/track_ang_vel_z`: `0.23`
- Comparison with `2026-04-07_12-53-43`:
  - `mean_reward`: `5.90 -> 26.43`
  - `mean_episode_length`: `741.56 -> 880.97`
  - `error_vel_xy`: `3.52 -> 0.71`
  - `error_vel_yaw`: `4.32 -> 1.95`
- Interpretation:
  - the baseline has moved out of the previous “survival-first, poor-tracking” regime
  - linear velocity tracking is now meaningfully learned
  - yaw tracking is improved but still materially weaker than xy tracking
  - this run is a usable Stage1 baseline, but not yet a polished final baseline
- Remaining issues at the end of the run:
  - `Episode_Termination/time_out ≈ 0.754`
  - `Episode_Termination/root_too_low ≈ 0.182`
  - `Episode_Termination/ball_joint_out_of_bounds ≈ 0.064`
  - thus a non-trivial fraction of episodes still end by failure rather than timeout
- Durable recommendation:
  - keep `wheel damping = 1e3`, `num_envs = 512`, and `max_iterations = 400` as the current default baseline training scale
  - subsequent work should focus on small adjustments around yaw tracking and failure reduction rather than another large redefinition of the baseline

### Training comparison: 2026-04-07_13-32-34 vs 2026-04-07_13-13-46 after raising yaw reward weight
- Compared run `2026-04-07_13-32-34` against `2026-04-07_13-13-46`.
- The only material config change was:
  - `track_ang_vel_z.weight: 0.5 -> 2.0`
- Durable outcome:
  - raising yaw reward weight to match linear velocity weight materially improved yaw tracking
  - but it slightly degraded linear velocity tracking and did not materially reduce failure terminations
- Quantitative comparison at the end:
  - `error_vel_yaw: 1.946 -> 0.880`
  - `error_vel_xy: 0.713 -> 0.834`
  - `time_out: 0.754 -> 0.757` (essentially unchanged)
  - `root_too_low: 0.182 -> 0.176` (essentially unchanged)
  - `ball_joint_out_of_bounds: 0.064 -> 0.066` (essentially unchanged)
- Important interpretation rule:
  - `Train/mean_reward` jumped from `26.43` to `41.21`, but this is not a fair apples-to-apples improvement signal because the yaw reward weight itself was multiplied by 4
  - for this pair of runs, the correct primary comparison metrics are the velocity errors and termination distribution, not total reward
- Durable diagnosis:
  - the policy responded to the stronger yaw incentive exactly as expected: it spent more capacity improving yaw tracking
  - however, this rebalancing traded away some xy tracking quality and did not improve survival
  - therefore `track_ang_vel_z.weight = 2.0` is likely too aggressive for the intended simple Stage1 baseline
- Recommended next direction:
  - use an intermediate yaw weight, likely `1.0` or `1.5`, instead of either `0.5` or `2.0`
  - keep `wheel damping = 1e3`, `num_envs = 512`, `max_iterations = 400`, and current reward std settings unchanged while testing that intermediate weight

### Training comparison: 2026-04-07_13-41-53 vs 2026-04-07_13-32-34 after lowering yaw reward weight
- Compared run `2026-04-07_13-41-53` against `2026-04-07_13-32-34`.
- The only material config change was:
  - `track_ang_vel_z.weight: 2.0 -> 1.5`
- Durable outcome:
  - lowering yaw weight slightly improved xy tracking but did not further improve yaw tracking
  - it also worsened survival and failure-term distribution
- Quantitative comparison at the end:
  - `error_vel_xy: 0.834 -> 0.677` (improved)
  - `error_vel_yaw: 0.880 -> 0.885` (essentially unchanged / slightly worse)
  - `time_out: 0.757 -> 0.678` (worse)
  - `root_too_low: 0.176 -> 0.207` (worse)
  - `ball_joint_out_of_bounds: 0.066 -> 0.117` (worse)
- Interpretation:
  - reducing yaw reward from `2.0` to `1.5` gave some optimization capacity back to linear-velocity tracking
  - however, the policy became less stable overall and did not gain a meaningful yaw benefit
- Durable current judgment:
  - among the two runs, `2026-04-07_13-32-34` remains the better Stage1 baseline candidate because it preserves much better survival while already delivering strong yaw improvement
  - `1.5` is not clearly better than `2.0` for the current task definition

### Direct follow-up tuning confirmed 2026-04-07_13-32-34 as today's default Stage1 baseline
- After the earlier pairwise comparisons, three direct GPU follow-up runs were executed outside the sandbox using:
  - `python scripts/rsl_rl/train.py --task Complete-Car-Rl-Training-v0 --num_envs 512 --max_iterations 400 --headless`
- Baseline reference:
  - `2026-04-07_13-32-34`
  - final metrics:
    - `mean_reward = 41.21`
    - `mean_episode_length = 841.79`
    - `error_vel_xy = 0.834`
    - `error_vel_yaw = 0.880`
    - `time_out = 0.757`
    - `root_too_low = 0.176`
    - `ball_joint_out_of_bounds = 0.066`
- Follow-up run `2026-04-07_13-56-35`:
  - config changes relative to `13-32-34`:
    - tightened `reset_base` z/roll/pitch perturbations
    - tightened `reset_ball_joints`
    - reduced `ball_joint_pos` action scale from `0.25` to `0.20`
  - outcome:
    - `error_vel_xy = 0.756`
    - `error_vel_yaw = 0.870`
    - `time_out = 0.690`
    - `root_too_low = 0.215`
    - `ball_joint_out_of_bounds = 0.096`
  - durable conclusion:
    - tightening reset plus reducing ball-joint authority did not improve balance
    - it mainly hurt survival and joint-bound behavior
- Follow-up run `2026-04-07_14-02-02`:
  - only material change relative to `13-32-34`:
    - `ball_joint_deviation.weight: -0.05 -> -0.08`
  - outcome:
    - `mean_reward = 38.07`
    - `mean_episode_length = 802.05`
    - `error_vel_xy = 0.938`
    - `error_vel_yaw = 1.063`
    - `time_out = 0.652`
    - `root_too_low = 0.202`
    - `ball_joint_out_of_bounds = 0.146`
  - durable conclusion:
    - directly strengthening spherical-joint deviation regularization was harmful for this task
    - it worsened both tracking and failure-term distribution
- Follow-up run `2026-04-07_14-06-10`:
  - only material change relative to `13-32-34`:
    - `termination.weight: -2.0 -> -4.0`
  - outcome:
    - `mean_reward = 40.07`
    - `mean_episode_length = 840.76`
    - `error_vel_xy = 0.937`
    - `error_vel_yaw = 1.006`
    - `time_out = 0.714`
    - `root_too_low = 0.176`
    - `ball_joint_out_of_bounds = 0.110`
  - durable conclusion:
    - making termination penalty harsher did not improve overall balance
    - it preserved episode length roughly, but worsened timeout share and joint-bound failures
- Durable current judgment:
  - among all runs tested today, `2026-04-07_13-32-34` remains the most balanced Stage1 flat-only baseline
  - keep as default:
    - `wheel_joints.damping = 1e3`
    - `track_lin_vel_xy.std = 1.0`
    - `track_ang_vel_z.weight = 2.0`
    - `termination.weight = -2.0`
    - original reset perturbations
    - `ball_joint_pos.scale = 0.25`
  - do not immediately retest these four directions without a new hypothesis:
    - tighter reset perturbations
    - lower spherical-joint action scale
    - stronger `ball_joint_deviation`
    - stronger termination penalty

### Current user-tuned config snapshot and Stage1 no-ball-reset decision
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/agents/rsl_rl_ppo_cfg.py`
- Durable implementation conclusion:
  - the user manually changed the current working config away from the `13-32-34` baseline in two directions:
    - environment/reward/termination became much stricter
    - PPO model and rollout scale became larger
  - key current environment-side changes include:
    - `track_lin_vel_xy.std = sqrt(0.5)`
    - `body_orientation = -5.0`
    - `lin_vel_z = -2.0`
    - `ang_vel_xy = -1.0`
    - `ball_joint_deviation = -0.5`
    - `ball_joint_swing = -0.1`
    - `bad_orientation.limit_angle = 45 deg`
    - `root_too_low.minimum_height = 0.15`
  - key current PPO-side changes include:
    - `num_steps_per_env = 24`
    - `max_iterations = 1000`
    - `save_interval = 200`
    - observation normalization enabled for actor and critic
    - hidden dims changed to `[256, 128, 64]`
    - `learning_rate = 3e-3`
- Durable Stage1 decision:
  - spherical-joint reset perturbation is not needed for the current simple Stage1 baseline
  - therefore `reset_ball_joints` has been changed to:
    - `position_range = (0.0, 0.0)`
    - `velocity_range = (0.0, 0.0)`
- Reason:
  - the user judged that ball-joint random reset is a robustness-oriented disturbance and should be postponed until later robustness testing, not mixed into the current baseline stage
- Impact:
  - future Stage1 baseline runs should not assume any spherical-joint initial randomization
  - if robustness experiments are started later, ball-joint reset perturbation can be reintroduced explicitly as a new experiment variable rather than staying silently enabled

### Root-height logging is now available in Stage1 training metrics
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/commands.py`
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/mdp/__init__.py`
- Durable implementation conclusion:
  - the local velocity command config now uses a custom command-term subclass that extends the existing velocity-tracking metrics
  - future training runs will additionally log:
    - `Metrics/base_velocity/root_height_mean`
    - `Metrics/base_velocity/root_height_min`
- Reason:
  - the user wants to determine whether the current `root_too_low.minimum_height` threshold is appropriate and needs direct height traces in TensorBoard/log exports instead of inferring only from termination rate
- Durable semantic conclusion:
  - in Isaac Lab articulation data:
    - `root_pos_w == root_link_pos_w`
  - therefore the current `root_too_low` termination is checking the articulation root link actor-frame height, not the root-link COM height
  - COM state is tracked separately through:
    - `root_com_state_w`
- Impact:
  - future diagnosis of the `root_too_low` termination should use the newly logged root-height metrics together with the semantic fact that this threshold is tied to the root link frame, not directly to the vehicle COM

### Run `2026-04-07_15-29-34` failed mainly through `root_too_low`, not startup or PPO instability
- Diagnosed run:
  - `src/rl_lab/complete_car_rl_training/logs/rsl_rl/complete_car_rl_training/2026-04-07_15-29-34`
- Durable diagnosis conclusion:
  - the run completed and saved checkpoints through:
    - `model_999.pt`
  - therefore it was not a startup failure
  - at the end of training:
    - `Episode_Termination/root_too_low = 1.0`
    - `Episode_Termination/time_out = 0.0`
    - `Episode_Termination/bad_orientation = 0.0`
    - `Episode_Termination/ball_joint_out_of_bounds = 0.0`
    - `Train/mean_episode_length ≈ 10.57`
    - `Metrics/base_velocity/root_height_mean ≈ 0.242`
    - `Metrics/base_velocity/root_height_min ≈ 0.164`
  - with `root_too_low.minimum_height = 0.15`, the active root-link height margin was only about `1.4 cm`
  - because the termination uses instantaneous root-link height, this threshold is very likely too tight for the current root frame and is the direct dominant failure mode of this run
- Important caution:
  - this run also changed multiple other factors at the same time:
    - much stronger stability penalties
    - stricter `bad_orientation = 45 deg`
    - larger PPO model
    - `learning_rate = 3e-3`
    - `num_steps_per_env = 24`
    - `max_iterations = 1000`
  - therefore the correct inherited conclusion is:
    - `0.15` is strongly implicated as the immediate rollout-killing threshold
    - but it was not the only variable changed in that experiment
- Impact:
  - future threshold validation should use single-variable comparison around:
    - `root_too_low.minimum_height`
  - the next fair test of the height threshold should avoid simultaneously retuning rewards and PPO hyperparameters

### Stage1 baseline no longer uses `root_too_low` termination
- Updated:
  - `src/rl_lab/complete_car_rl_training/complete_car_rl_training/tasks/manager_based/complete_car_env_cfg.py`
- Durable Stage1 decision:
  - the current simple Stage1 baseline has removed:
    - `root_too_low`
  - active termination terms are now:
    - `time_out`
    - `bad_orientation`
    - `ball_joint_out_of_bounds`
- Reason:
  - the user decided that the current Stage1 baseline should not keep a hard height cutoff whose semantics are tied to the articulation root-link frame rather than vehicle COM or terrain-relative clearance
  - the immediately previous run `2026-04-07_15-29-34` showed that `minimum_height = 0.15` likely dominated failure before the intended task could be learned
- Impact:
  - future Stage1 analysis should no longer interpret rollout failure through `Episode_Termination/root_too_low`
  - the logged metrics
    - `Metrics/base_velocity/root_height_mean`
    - `Metrics/base_velocity/root_height_min`
    remain useful for later redesign of a more physically meaningful height or clearance constraint

### Run `2026-04-07_15-57-27` validates that removing `root_too_low` immediately restored healthy Stage1 rollouts
- Diagnosed run:
  - `src/rl_lab/complete_car_rl_training/logs/rsl_rl/complete_car_rl_training/2026-04-07_15-57-27`
- Durable diagnosis conclusion:
  - compared with `2026-04-07_15-29-34`, the dominant change was:
    - `root_too_low` removed
  - the resulting rollout statistics became:
    - `Train/mean_episode_length = 960.0`
    - `Episode_Termination/time_out = 1.0`
    - `Episode_Termination/bad_orientation = 0.0`
    - `Episode_Termination/ball_joint_out_of_bounds = 0.0`
  - task metrics at the end were:
    - `error_vel_xy ≈ 0.62`
    - `error_vel_yaw ≈ 0.68`
    - `track_lin_vel_xy ≈ 1.84`
    - `track_ang_vel_z ≈ 1.72`
  - this is strong inherited evidence that the previous run failure was indeed dominated by the `root_too_low` cutoff rather than PPO instability
- Important caution:
  - after removing the height termination, the logged root-frame height became very low:
    - `root_height_mean` over the last 20 points was only about `0.132`
    - `root_height_min` over the last 20 points averaged about `0.090`, with minima down to about `0.017`
  - therefore the current Stage1 policy is now trainable and performs tracking, but it should not be interpreted as proving that the vehicle maintains a large or physically meaningful body-clearance margin
- Impact:
  - current Stage1 baseline can proceed without `root_too_low`
  - if body clearance becomes a later research target, it should be reintroduced with a better-defined relative-height or clearance signal, not by restoring the old absolute root-link threshold unchanged

### Run `2026-04-07_19-42-44` improved yaw tracking while keeping full rollout health
- Diagnosed run:
  - `src/rl_lab/complete_car_rl_training/logs/rsl_rl/complete_car_rl_training/2026-04-07_19-42-44`
- Parameter changes relative to `2026-04-07_15-57-27`:
  - `agent.max_iterations: 600 -> 500`
  - `reset_base.velocity_range`:
    - `x/y/z/roll/pitch/yaw` all changed from random perturbation ranges to `0`
  - `base_velocity` command added curvature-coupled turning:
    - `curvature_range = (-0.5, 0.5)`
    - `turn_lin_vel_threshold = 0.1`
- Durable diagnosis conclusion:
  - rollout health stayed perfect:
    - `Train/mean_episode_length = 960.0`
    - `Episode_Termination/time_out = 1.0`
    - `bad_orientation = 0.0`
    - `ball_joint_out_of_bounds = 0.0`
  - compared with `2026-04-07_15-57-27`, task metrics improved:
    - `mean_reward: 48.14 -> 50.92`
    - `error_vel_xy: 0.616 -> 0.613`
    - `error_vel_yaw: 0.676 -> 0.542`
    - `track_lin_vel_xy: 1.843 -> 1.859`
    - `track_ang_vel_z: 1.716 -> 1.800`
  - root-frame height also improved:
    - `root_height_mean: 0.111 -> 0.139`
    - `root_height_min: 0.051 -> 0.111`
- Important interpretation:
  - this run is inherited evidence that removing initial root-velocity perturbations and using the new speed-curvature command distribution did not destabilize training
  - however, the policy still operates with a relatively low root frame, so this should not yet be interpreted as solving clearance or body-height quality
- Impact:
  - for the current simple Stage1 baseline, `2026-04-07_19-42-44` is a stronger reference run than `2026-04-07_15-57-27`
  - future comparisons with older runs that used independently sampled `ang_vel_z` must explicitly note the command-distribution change

### Manager-based RL task architecture has been split into `common/` and `stage1/`
- Date:
  - 2026-04-08
- Decision:
  - remove the old monolithic Stage1 task layout under:
    - `tasks/manager_based/complete_car_env_cfg.py`
    - `tasks/manager_based/mdp/`
    - `tasks/manager_based/agents/`
    - `tasks/manager_based/complete_car_stage1_terrain_env.py`
    - `tasks/manager_based/stage1_terrain.py`
  - replace it with:
    - `tasks/manager_based/common/`
    - `tasks/manager_based/stage1/`
- Reason:
  - the user explicitly wants MGDP-style staged task growth, but adapted to Isaac Lab manager-based instead of recreating old `legged_gym`-style giant env classes
  - the previous single-file Stage1 config made it too easy to overwrite old parameters and too hard to preserve stage-by-stage comparisons
- Durable structure conclusion:
  - `common/` now holds the reusable manager-based template layer:
    - robot asset config
    - scene config
    - shared MDP terms
    - `CompleteCarBaseEnvCfg`
    - `CompleteCarBasePPORunnerCfg`
  - `stage1/` now holds only Stage1-specific logic:
    - `stage1_env_cfg.py`
    - `stage1_env.py`
    - `stage1_terrain.py`
    - `stage1/mdp/`
    - `stage1/agents/rsl_rl_ppo_cfg.py`
- Impact:
  - future Stage2 / Stage3 work should be added as sibling stage packages, not by reopening a new monolithic `complete_car_env_cfg.py`
  - future reusable terms should go into `common/`, while terrain/perception/curriculum logic that belongs only to one stage should stay inside that stage package
  - Isaac Sim preview and keyboard scripts now treat `stage1/stage1_terrain.py` as the training-aligned terrain source of truth
- Status:
  - Python-level import and syntax checks passed after the refactor

### RL mainline has now moved from `src/rl_lab/complete_car_rl_training/` to `RL_Training/`
- Date:
  - 2026-04-08
- Decision:
  - treat `RL_Training/` as the only active Isaac Lab RL workspace
  - stop using the deleted `src/rl_lab/complete_car_rl_training/` tree as the default engineering mainline
- Reason:
  - the user performed a bulk repository reorganization and moved the live RL project, IK utilities, and project docs into `RL_Training/`
  - leaving scripts and memory files on the old path would cause future sessions to follow dead entry points
- Durable implementation conclusion:
  - the current active package root is:
    - `RL_Training/complete_car_rl_training/`
  - the current active training/play/list scripts are:
    - `RL_Training/scripts/`
  - root Isaac Sim helper scripts under:
    - `scripts/isaac_sim/`
    now resolve package imports and stage1 terrain paths against `RL_Training/`
- Impact:
  - future sessions should default to `RL_Training/` whenever the task is about runnable RL code
  - old historical references to `src/rl_lab/complete_car_rl_training/` remain valid only as history, not as the current working location
- Status:
  - stale code imports and file-path references that would break task registration were fixed

### RL mainline structure has now converged to `envs/base + envs/baseline`, and base shared logic is merged into `complete_car_config.py`
- Date:
  - 2026-04-08
- Decision:
  - stop using the intermediate `common/ + stage1/` package split as the active structure
  - use:
    - `RL_Training/complete_car_rl_training/envs/base/`
    - `RL_Training/complete_car_rl_training/envs/baseline/`
    as the current task layout
  - merge the previous base shared files into:
    - `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
- Reason:
  - the user further simplified the project and explicitly requested that the shared template layer should no longer be scattered across:
    - `base_env_cfg.py`
    - `scene_cfg.py`
    - `envs/base/agents/`
    - `envs/base/mdp/`
  - the engineering goal is to keep one clear shared trunk file while preserving stage-specific extension files
- Durable structure conclusion:
  - `envs/base/complete_car_config.py` now holds:
    - shared scene class
    - shared command / observation / action / event / termination / reward helper logic
    - shared RL env base class
    - shared env cfg class `CompleteCarCfg`
    - shared PPO cfg class `CompleteCarCfgPPO`
  - `envs/base/robot_cfg.py` remains separate as the robot asset definition file
  - `envs/baseline/` now holds only Stage1-specific logic:
    - `stage1_env_cfg.py`
    - `stage1_env.py`
    - `stage1_terrain.py`
    - `baseline/mdp/`
    - `baseline/agents/rsl_rl_ppo_cfg.py`
  - package registration now flows through:
    - `complete_car_rl_training/__init__.py`
    - `complete_car_rl_training/envs/__init__.py`
    - `complete_car_rl_training/envs/baseline/__init__.py`
- Impact:
  - future Stage2 / Stage3 should continue to add sibling stage packages under `envs/`
  - future shared changes should go into `envs/base/complete_car_config.py` first instead of recreating new shared subdirectories
  - root Isaac Sim preview / teleop scripts must treat `envs/baseline/stage1_terrain.py` as the active terrain source of truth
- Status:
  - stale imports and task registration entry points were updated

### Shared trunk now uses a MGDP-style nested config tree while staying Isaac Lab manager-based
- Date:
  - 2026-04-09
- Updated:
  - `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
  - `RL_Training/complete_car_rl_training/envs/base/__init__.py`
  - `RL_Training/complete_car_rl_training/envs/baseline/complete_car_config_baseline.py`
- Durable implementation conclusion:
  - the shared trunk `complete_car_config.py` now exposes a MGDP-style top-level config tree centered on:
    - `CompleteCarCfg`
  - inside `CompleteCarCfg`, the user-facing root config sections now explicitly include:
    - `env`
    - `env_init_info`
    - `IMU`
    - `camera`
    - `Radar`
    - `terrain`
    - `commands`
    - `init_state`
    - `control`
    - `asset`
    - `domain_rand`
    - `rewards`
    - `evals`
    - `normalization`
    - `noise`
    - `viewer`
    - `sim`
    - `randomization`
    - `privInfo`
  - the file still preserves Isaac Lab manager-based execution by auto-configuring:
    - `scene`
    - `observations`
    - `actions`
    - `events`
    - `terminations`
    - `curriculum`
    inside `__post_init__`
  - the shared PPO trunk class is now:
    - `CompleteCarPPoCfg`
    instead of the earlier `CompleteCarCfgPPO`
  - `camera` and `IMU` now follow Isaac Lab sensor-config style, while `Radar` is currently kept as a standard reserved config slot and remains disabled by default
- Reason:
  - the user explicitly requested rewriting the shared trunk in the style of `/MGDP/legged_robot_config.py`, but without abandoning Isaac Lab's manager-based task organization
- Impact:
  - future baseline / Stage2 / Stage3 config files should inherit from `CompleteCarCfg` and override nested fields first, rather than recreating full reward or command config classes
  - future shared PPO overrides should inherit from `CompleteCarPPoCfg`
  - future sensor-stage work can enable `camera / IMU / Radar` through the shared config tree instead of reopening the base-file structure debate
- Status:
  - static `py_compile` validation passed

### `complete_car_config.py` is now reduced to only `CompleteCarCfg` and `CompleteCarPPoCfg`
- Date:
  - 2026-04-09
- Updated:
  - `RL_Training/complete_car_rl_training/envs/base/complete_car_config.py`
  - `RL_Training/complete_car_rl_training/envs/base/complete_car_env.py`
  - `RL_Training/complete_car_rl_training/envs/base/manager_helpers.py`
  - `RL_Training/complete_car_rl_training/envs/base/__init__.py`
- Durable structure conclusion:
  - the user clarified that `complete_car_config.py` should be a parameter-definition file only
  - after this clarification, `complete_car_config.py` now contains only two top-level classes:
    - `CompleteCarCfg`
    - `CompleteCarPPoCfg`
  - runtime environment logic moved to:
    - `envs/base/complete_car_env.py`
    where:
    - `CompleteCarRLEnv`
    is defined
  - command / reward helper callables and Isaac Lab manager helper classes moved to:
    - `envs/base/manager_helpers.py`
  - `CompleteCarCfg.__post_init__` now serves as the assembly point that maps the nested parameter tree into Isaac Lab manager-based runtime config objects
- Reason:
  - the user explicitly rejected mixing runnable env logic and helper function definitions into the shared config trunk file
- Impact:
  - future work should keep `complete_car_config.py` focused on parameter tree definition and runtime-config assembly only
  - new helper functions, custom command classes, and env runtime code should be added to sibling files under `envs/base/`, not back into `complete_car_config.py`
- Status:
  - static `py_compile` validation passed

### RL mainline has been simplified again: `baseline/` now keeps only one override file, and terrain generation moved to `utils/terrain.py`
- Date:
  - 2026-04-09
- Decision:
  - treat `envs/base/complete_car_config.py` as the single shared RL framework file
  - treat `envs/baseline/complete_car_config_baseline.py` as the single current baseline-stage override file
  - move the terrain builder out of `envs/baseline/` into:
    - `complete_car_rl_training/utils/terrain.py`
- Reason:
  - the user explicitly wanted the shared framework file to read more like MGDP's config trunk, with clear sections for:
    - terrain
    - perception
    - observation
    - action
    - reward
    - termination
  - the user also wanted the current baseline layer to stop carrying extra runtime/agent/mdp files and instead remain only as a parameter-overriding stage config
- Durable structure conclusion:
  - `envs/base/complete_car_config.py` now owns:
    - shared env settings
    - shared terrain settings
    - shared perception settings
    - shared control settings
    - scene / commands / observations / actions / events / terminations / reward helper logic
    - the shared runtime env class `CompleteCarRLEnv`
    - the shared PPO trunk `CompleteCarCfgPPO`
  - `envs/baseline/` now contains only:
    - `complete_car_config_baseline.py`
  - `utils/terrain.py` now owns:
    - terrain generation
    - `terrain_type / terrain_class / env_origins`
    - terrain curriculum helper
    - terrain spawn-offset helper
  - Gym task registration now happens inside:
    - `envs/baseline/complete_car_config_baseline.py`
  - `envs/__init__.py` imports that module directly for registration side effects
- Impact:
  - future Stage2 / Stage3 should continue to add sibling override files or sibling stage packages, but the current baseline layer should remain thin
  - future terrain changes should first update `utils/terrain.py`, not recreate another terrain file inside `baseline/`
  - root Isaac Sim preview / teleop scripts should now treat `utils/terrain.py` as the active terrain source of truth
- Status:
  - code structure updated
  - static syntax validation passed
  - static syntax validation passed
