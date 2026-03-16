# Graduation Design Project Context

## Session bootstrap
When Codex starts in this repository, treat the following files as the canonical startup context:

1. `AGENTS.md`
2. `README.md`
3. `docs/current_status.md`
4. `docs/conversation_history.md`
5. `logs/daily_work_log.md`

Expected behavior at the beginning of each new task:
- first inspect the repository structure if the request involves code or files
- use `README.md` for the current directory layout and file placement rules
- use `docs/current_status.md` for current phase, blockers, and immediate next step
- use `docs/conversation_history.md` for past session conclusions and major decisions
- use `logs/daily_work_log.md` for date-based completed work records
- treat this `AGENTS.md` file as the authoritative source for research background, project goals, and engineering constraints

If any of these files conflict:
- follow `AGENTS.md` first
- then `docs/current_status.md` for current stage and priority
- then `docs/conversation_history.md` for decision continuity
- then `logs/daily_work_log.md` for execution history
- then `README.md` for structure and file organization

## Project name
RL-based motion control and terrain-adaptive morphology control for a specialized articulated ground robot with spherical parallel joint mechanisms.

## Student background
The project is an undergraduate graduation design in robotics / mechatronics. The primary simulation and development stack is Isaac Sim 5.1 + Isaac Lab 2.3.x on Ubuntu 22.04. The project may later involve ROS integration, stereo cameras, LiDAR, and IMU.

## Core robot structure
The robot is a three-body articulated ground vehicle.
- Front body
- Middle body
- Rear body

The front-middle and middle-rear bodies are connected through two spherical parallel mechanisms.
For simulation and RL acceleration, each spherical parallel mechanism has been equivalently simplified as a 3-DOF serial spherical joint between the moving platform and the base.

The vehicle has:
- six wheels total
- two equivalent 3-DOF spherical joints
- overall goal: enable body attitude adaptation / terrain adaptation / motion stabilization

## Current modeling status
Already completed:
- basic joint and drive configuration in Isaac Sim
- equivalent simplification of spherical parallel mechanism into serial rotational DOFs
- initial URDF / USD related configuration attempts
- debugging around articulation, joints, keyboard control, and import pipeline

Known practical constraint:
- The advisor emphasized that the thesis priority is to run RL successfully as soon as possible.
- Kinematics / optimization / sensor enhancement are secondary and should be treated as incremental improvements after the RL pipeline works.

## Supervisor guidance / project priority
Top priority:
1. Run a complete RL loop successfully
2. Build a stable minimal simulation environment
3. Define observations, actions, rewards, termination, reset, and training loop
4. Obtain a demonstrable behavior

Secondary priorities:
- incorporate forward / inverse kinematics more rigorously
- improve morphology control logic
- add better sensor processing
- optimize policy and controller performance
- enrich thesis novelty after the baseline is working

## Technical interpretation of the mechanism
The equivalent simulation target is not a physically exact closed-loop spherical parallel mechanism.
Instead, the simulation uses an equivalent serial representation:
- base
- virtual links if needed
- three serial revolute joints representing x / y / z rotational DOFs
- moving platform
This is done to avoid closed-chain articulation limitations and to accelerate RL environment construction.

## RL framing
The RL problem should be framed as a minimal, trainable control problem first.

Recommended first task:
Train the robot (or the central articulated structure) to maintain or track desired body attitude under terrain disturbance or commanded posture targets.

Possible staged tasks:
Stage 1:
- control only the equivalent spherical joint DOFs
- flat terrain
- no vision
- only proprioceptive state and IMU-like state

Stage 2:
- add vehicle forward motion and wheel-ground interaction
- include attitude stabilization while moving

Stage 3:
- add terrain variation
- use simplified terrain descriptors

Stage 4:
- optionally integrate richer sensor-derived terrain features

## Observation design principles
Prefer compact low-dimensional observations first.
Candidate observations:
- body orientation (roll, pitch, yaw or quaternion)
- angular velocity
- joint positions of equivalent spherical joints
- joint velocities
- wheel velocities if needed
- target attitude / target body state
- terrain summary features if later added
Do not start with raw image or raw point cloud input.

## Action design principles
Prefer simple continuous actions:
- target joint position / velocity / torque for the equivalent 3-DOF spherical joints
Later:
- wheel velocity commands
- combined morphology + locomotion commands

## Reward design principles
Baseline reward should prioritize:
- body stabilization
- target attitude tracking
- smooth control
- low unnecessary joint motion
- avoiding rollover / instability
Keep reward sparse structure minimal at first.

## Sensor strategy
Do not make rich sensors a dependency for the first successful RL run.
Minimal first-pass sensing:
- IMU-like signals from the middle body
Optional later:
- front and rear stereo cameras
- front LiDAR or front+rear LiDAR
- terrain feature extraction into compact descriptors
Raw point clouds / depth images should be converted into structured terrain information before entering RL if used.

## Thesis strategy
The thesis should be organized around:
1. mechanism simplification for simulation
2. RL environment design
3. control policy training and validation
4. optional enhancement with kinematics / terrain perception / optimization

The project should avoid getting stuck on high-fidelity modeling too early.

## Toolchain
Primary:
- Isaac Sim 5.1
- Isaac Lab 2.3.x
- Python 3.11
- Ubuntu 22.04
Potential:
- ROS / ROS 2 later
- VS Code
- URDF / USD conversion tools

## Coding expectations
When modifying code:
- prefer executable, complete code over fragmented snippets
- include exact file paths when possible
- explain where to place files and how to run them
- avoid placeholders when the exact structure can be inferred
- preserve compatibility with Isaac Sim 5.1 and Isaac Lab 2.3.x unless explicitly changing target version

## Working style for this repository
When asked to help:
1. first inspect existing repository structure
2. identify minimal path to a runnable RL baseline
3. avoid overengineering
4. write concrete commands and file changes
5. keep comments clear and ASCII-safe if encoding issues are possible
6. when debugging, prioritize environment boot, articulation correctness, observation-action loop, and training launch success

## Knowledge lookup policy
When the task involves Isaac Sim or Isaac Lab:
- consult `refs/isaac_kb/` before using web search
- use web search when local references are insufficient, outdated, or the user explicitly asks for online lookup
- prefer official Isaac Sim, Isaac Lab, and upstream documentation when browsing is needed

## Persistent project memory
This repository should act as long-term memory for the graduation project.

Required behavior:
- keep important conclusions from past sessions in `docs/conversation_history.md`
- keep date-stamped completed work in `logs/daily_work_log.md`
- after each substantial work session, append a concise summary of what was completed, with the date
- do not rely only on chat history for continuity; write durable summaries into project files

What to record in `docs/conversation_history.md`:
- major decisions
- structure changes
- environment design choices
- training/debugging conclusions
- assumptions that future sessions must inherit

What to record in `logs/daily_work_log.md`:
- date
- completed tasks
- files changed
- short next-step note if useful

## Non-goals unless explicitly requested
- perfect analytical fidelity of spherical parallel mechanism
- full sensor fusion stack before RL baseline
- excessive UI polishing
- broad refactors unrelated to making the environment trainable

## Current high-priority objective
Build a minimal but runnable Isaac Lab RL environment for the articulated car and obtain a first successful training result that demonstrates controllable body attitude / morphology behavior.

## Canonical project files
Use these files as the main project map instead of inferring from scattered artifacts alone:

- `AGENTS.md`
  - stable research background, constraints, and project priorities
- `README.md`
  - top-level repository structure and intended code placement
- `docs/current_status.md`
  - latest phase, blockers, and immediate next action
- `docs/conversation_history.md`
  - durable cross-session memory distilled from previous work
- `logs/daily_work_log.md`
  - chronological record of completed daily work
- `scripts/isaac_sim/`
  - Isaac Sim validation and teleoperation scripts
- `src/rl_lab/`
  - target location for the runnable Isaac Lab RL baseline
- `results/`
  - generated outputs and validation artifacts
- `refs/isaac_kb/`
  - local searchable Isaac Sim and Isaac Lab reference material

## Maintenance rule
When project status changes, update `docs/current_status.md`.
When repository organization changes, update `README.md`.
When research direction, constraints, or thesis priorities change, update `AGENTS.md`.
When a session yields durable conclusions, update `docs/conversation_history.md`.
When a session completes concrete work, append to `logs/daily_work_log.md`.
