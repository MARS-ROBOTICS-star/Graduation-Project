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
- treat this `AGENTS.md` file as the authoritative source for research background, project goals, engineering constraints, and RL training route

If any of these files conflict:
- follow `AGENTS.md` first
- then `docs/current_status.md` for current stage and priority
- then `docs/conversation_history.md` for decision continuity
- then `logs/daily_work_log.md` for execution history
- then `README.md` for structure and file organization

## Project overview

### Project name
RL-based motion control and terrain-adaptive morphology control for a specialized articulated ground robot with spherical parallel joint mechanisms.

### Student background
The project is an undergraduate graduation design in robotics / mechatronics.
The primary simulation and development stack is Isaac Sim 5.1 + Isaac Lab 2.3.x on Ubuntu 22.04.
The project may later involve ROS integration, stereo cameras, LiDAR, and IMU.

### Core robot structure
The robot is a three-body articulated ground vehicle:
- head car
- body car
- tail car

The head-body and body-tail are connected through two 3RRR spherical parallel mechanisms.
For simulation and RL acceleration, each spherical parallel mechanism is equivalently simplified as a 3-DOF serial spherical joint between the moving platform and the base.

The vehicle has:
- six wheels total
- two equivalent 3-DOF spherical joints
- an overall goal of body attitude adaptation, terrain adaptation, and motion stabilization

### Technical interpretation of the mechanism
The equivalent simulation target is not a physically exact closed-loop spherical parallel mechanism.
Instead, the simulation uses an equivalent serial representation:
- base
- virtual links if needed
- three serial revolute joints representing x / y / z rotational DOFs
- moving platform

This is done to avoid closed-chain articulation limitations and to accelerate RL environment construction.

### Current modeling status
Already completed:
- basic joint and drive configuration in Isaac Sim
- equivalent simplification of spherical parallel mechanism into serial rotational DOFs
- initial URDF / USD related configuration attempts
- debugging around articulation, joints, keyboard control, and import pipeline

Known practical constraint:
- the advisor emphasized that the thesis priority is to run RL successfully as soon as possible
- kinematics, optimization, sensor enhancement, and richer terrain adaptation are secondary and should be treated as incremental improvements after the RL pipeline works

## Project priorities

### Supervisor guidance
Top priority:
1. Run a complete RL loop successfully.
2. Build a stable simulation environment.
3. Define observations, actions, rewards, termination, reset, and training loop.
4. Obtain a demonstrable behavior.

Secondary priorities:
- incorporate forward / inverse kinematics more rigorously
- improve morphology control logic
- add better sensor processing
- optimize policy and controller performance
- enrich thesis novelty after the baseline is working

### Current high-priority objective
Build a runnable Isaac Lab RL environment for the articulated car and obtain a first successful training result that demonstrates controllable body attitude / morphology behavior.

### Non-goals unless explicitly requested
- perfect analytical fidelity of the spherical parallel mechanism
- full sensor fusion stack before the RL baseline
- excessive UI polishing
- broad refactors unrelated to making the environment trainable

## RL training strategy

### Overall principle
For this project, RL training targets must be separated into:
- primary objectives: make the articulated car stable, controllable, and reproducible on basic motion tasks
- later enhancement objectives: add structure-aware control, terrain adaptation, and perception-driven decision making after the baseline works

The current stage must follow a shortest-path principle:
- first build the smallest trainable system
- then add structure complexity in layers
- do not couple kinematics, perception fusion, terrain diversity, and sim-to-real details into the first runnable baseline

### Layered RL objectives

#### 1. Basic survival objectives
These are the lowest-level stability constraints:
- avoid rollover
- keep spherical-joint platform attitude within bounds
- avoid hitting joint limits
- avoid obvious wheel runaway or high-speed free spinning
- keep actions continuous and avoid violent oscillation

These objectives are treated as stability constraints, not as the final research contribution.

#### 2. Basic motion objectives
This is the first formal training target and the current priority:
- track target linear velocity
- track target angular velocity
- move forward, backward, and turn on command
- maintain stable traversal on flat ground

This layer corresponds to the baseline wheeled locomotion control task.

#### 3. Structure-coordination objectives
These objectives express the thesis-specific mechanism value, but should not enter the very first training phase:
- determine whether spherical-joint attitude regulation improves whole-body stability
- determine whether head, body, and tail relative posture better adapts to terrain
- determine whether morphology changes improve passability, reduce impact, and reduce slip

At this stage RL should learn:
- when to adjust the mechanism
- how much to adjust
- whether the adjustment is worth the control cost

#### 4. Environment-adaptation objectives
These are higher-level objectives and should be added later:
- slopes, steps, waves, and rough terrain traversal
- maintaining stability under low-adhesion conditions
- robustness to unseen terrain
- adjusting speed or spherical-joint posture in advance based on terrain cues

### Required execution order

#### Stage 0: make the environment trainable
The goal of this stage is not control quality.
The goal is to close the RL loop.

Must be true:
- the robot can reset stably in Isaac Sim / Isaac Lab
- actions can be applied correctly
- observations can be read correctly
- rewards can be computed correctly
- episodes can terminate correctly
- the training program can start and show reward change

Do not add at this stage:
- complex sensors
- perception fusion
- diversified terrain
- deep kinematic compensation
- sim-to-real details

Core conclusion:
- first prove the environment can run end to end

#### Stage 1: flat-ground basic velocity tracking
This is the highest-priority formal baseline.

Task targets:
- move forward
- move backward
- turn
- perform combined motion on flat ground

Action-space default for the first baseline:
- fix the spherical-joint posture
- train wheel locomotion control only

Reason:
- verify that chassis locomotion can be learned first
- keep action dimension low
- avoid early instability caused by spherical-joint control

Observation-space default:
- body linear velocity
- body angular velocity
- attitude-related information such as projected gravity or roll / pitch
- wheel speed
- target command
- optional current spherical-joint angle

Reward default:
- velocity tracking reward
- heading / yaw-rate tracking reward
- posture stability penalty
- action smoothness penalty
- joint-limit penalty

Termination default:
- rollover
- attitude beyond threshold
- abnormal key-body collision
- episode timeout

Stage target:
- obtain a baseline that trains stably, can move and turn, and shows rising reward

#### Stage 2: add spherical-joint control on flat ground
After the flat-ground baseline is stable, RL can start learning:
- wheel actuation
- spherical-joint actuation

Environment constraints for this stage:
- still flat ground
- still no complex external perception

Reason to delay spherical-joint control until this stage:
- if training fails, the cause is more likely in action design, reward design, or control scale, not in the basic environment loop

Preferred RL output design:
- RL outputs desired platform posture
- inverse kinematics maps posture targets to the three joint commands

This is the recommended structure because it is more physically meaningful, easier to constrain, and more interpretable.

### When kinematics should be added
Conclusion:
- kinematics should not be deeply coupled into the first runnable training environment

Recommended timing:
- Stage 2 or Stage 3
- only after the flat-ground trainable baseline is working and spherical-joint DOFs are controllable

Recommended roles of kinematics:
1. Action mapping layer
   RL outputs desired platform posture, then inverse kinematics maps it to the three driven joints.
2. Observation enhancement
   Add platform posture or relative pose computed by forward kinematics into observations.
3. Reward construction
   Reward target posture achievement, reasonable mechanism configuration, and staying away from singular configurations.

The action-mapping role is the preferred first use.

### When sensor fusion should be added
Conclusion:
- sensor fusion should be added clearly later, not in the early baseline

Recommended order:

#### Stage 1
Use only proprioceptive / body-state information:
- base pose / velocity
- IMU-equivalent state
- joint states
- command

This is a pure proprioceptive control baseline without external perception.

#### Stage 2
Still acceptable to use only body-state information without vision or LiDAR.

#### Stage 3
When terrain-adaptation tasks begin, introduce simplified terrain features gradually:
- height map
- sampled forward terrain heights
- contact information under the chassis or wheels
- local slope estimate

Do not directly use raw images or point clouds unless explicitly required.
For this project, the research focus is morphology control and terrain adaptation, not end-to-end visual navigation.

Preferred perception representation:
- local height difference ahead
- left-right wheel contact height difference
- ground slope
- ground roughness
- distance to a step edge
- traversability score

The preferred pipeline is:
- sensors gather environment data
- preprocessing extracts compact terrain descriptors
- RL consumes low-dimensional terrain features

### When terrain diversification should be added
Conclusion:
- add terrain diversity only after flat-ground training is stable

Recommended rhythm:

#### Stage 1
Single flat terrain:
- learn stable motion
- obtain the first baseline

#### Stage 2
Slightly perturbed flat terrain:
- friction randomization
- small mass perturbation
- initial pose perturbation
- light external pushes

Goal:
- improve baseline robustness

#### Stage 3
Simple structured terrain:
- gentle slopes
- small waves
- low obstacles
- small steps

#### Stage 4
Programmatic diverse terrain:
- random slopes
- uneven continuous terrain
- random pits
- different friction conditions
- mixed obstacles

### Recommended roadmap

#### Stage A: run the RL framework first
Content:
- fixed spherical joints
- flat terrain
- low-dimensional state input
- velocity tracking task

Expected output:
- first trainable environment
- first reward curve
- first baseline demo video

#### Stage B: let spherical-joint DOFs participate in control
Content:
- flat terrain
- wheels plus spherical joints controlled together
- still no external perception
- compare whether spherical joints improve stability or maneuverability

Expected output:
- RL results with structure DOFs participating
- comparison with the fixed-spherical-joint baseline

#### Stage C: add kinematic priors
Content:
- RL outputs higher-level targets
- inverse kinematics maps them to spherical-joint commands
- posture-related rewards and constraints are added

Expected output:
- a control framework with mechanism priors
- improved interpretability of actions

#### Stage D: add terrain adaptation
Content:
- start from simple slopes
- then expand toward rough terrain
- early versions may use terrain ground-truth or sampled height values instead of raw visual sensing

Expected output:
- terrain adaptation ability
- evidence that morphology regulation improves passability

#### Stage E: add sensors and perception fusion
Content:
- start from IMU and contact information
- then add local height maps or sparse depth
- only later consider stereo cameras or LiDAR

Expected output:
- a complete perception-to-morphology-control loop
- an enhanced thesis contribution after the baseline is proven

### Current default RL path
Unless the user explicitly changes the research plan, future work should inherit the following default route:
1. Finish Stage 0 completely and keep the training loop stable.
2. Use Stage 1 as the current mainline baseline:
   - flat ground
   - low-dimensional proprioceptive observations
   - velocity-tracking task
   - fixed spherical-joint posture as the preferred first baseline
3. Only after Stage 1 is stable, move to Stage 2 and let spherical-joint control participate.
4. Add kinematics, terrain adaptation, and sensor fusion only after the baseline is already trainable and explainable.

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
2. avoid overengineering
3. write concrete commands and file changes
4. keep comments clear and ASCII-safe if encoding issues are possible
5. when debugging, prioritize environment boot, articulation correctness, observation-action loop, and training launch success

## 第一性原理
请使用第一性原理思考，你不能总是假设我非常清楚自己想要什么和该怎么得到。
请保持审慎，从原始需求和问题出发，如果动机和目标不清晰，停下来和我讨论。

## 方案规范
当需要你给出修改或重构方案时必须符合以下规范：
- 不允许给出兼容性或补丁性的方案
- 不允许过渡设计
- 保持最短路径实现且不能违反第一条要求
- 不允许自行给出我提供的需求以外的方案，例如一些兜底和降级方案，这可能导致业务逻辑偏移问题
- 必须确保方案的逻辑正确
- 必须经过全链路的逻辑验证

## Knowledge lookup policy
When the task involves Isaac Sim or Isaac Lab:
- consult `refs/isaac_kb/` before using web search
- use web search when local references are insufficient, outdated, or the user explicitly asks for online lookup
- prefer official Isaac Sim, Isaac Lab, and upstream documentation when browsing is needed

# Persistent Project Memory Rules

This repository is the long-term memory store for the graduation project.
Do not rely only on chat history for continuity.
After substantial work, write durable summaries into the project files below.

---

## Memory Files and Their Roles

### 1. `docs/conversation_history.md`
Purpose:
- Store long-lived project memory that must persist across sessions.

Record here:
- major decisions
- structure changes
- environment design choices
- training conclusions
- debugging conclusions
- validated assumptions
- rejected approaches that should not be retried blindly

Do NOT record here:
- routine chat back-and-forth
- temporary experiments with no conclusion
- verbose step-by-step logs better suited for daily logs

Writing style:
- concise but information-dense
- each entry should be reusable in future sessions
- prefer structure such as:
  - date
  - decision / conclusion
  - reason
  - impact
  - status

Rule:
- if a session produces a conclusion that future sessions must inherit, update this file

### 2. `docs/current_status.md`
Purpose:
- Provide a compact Chinese snapshot of the project's current state.

Must always reflect:
- current overall goal
- current phase
- completed milestone summary
- active work in progress
- blockers
- immediate next priorities
- current default design choices

Requirements:
- maintain in Chinese
- keep it short, accurate, and easy to scan
- overwrite outdated status rather than appending large historical notes

Rule:
- if the project state changes materially, update this file before ending the session

### 3. `logs/daily_work_log.md`
Purpose:
- Maintain a date-stamped Chinese work log of completed tasks.

Each new entry should include:
- date
- completed tasks
- files changed
- outputs or conclusions
- short next-step note if useful

Requirements:
- all new entries must be in Chinese
- append new entries; do not rewrite older dates unless correcting factual errors
- keep entries concise and factual

Rule:
- after each substantial work session, append a new dated entry

## Update Triggers

A session counts as substantial if it includes any of the following:
- a design decision
- code or file structure changes
- environment/task definition changes
- training/debugging conclusions
- resolved blockers
- a completed research summary that affects future work

When substantial work occurs:
1. update `docs/current_status.md`
2. append durable conclusions to `docs/conversation_history.md` if needed
3. append a dated entry to `logs/daily_work_log.md`

## Priority and Conflict Resolution

If the files disagree, use this priority:
1. `docs/conversation_history.md` for long-term conclusions
2. `docs/current_status.md` for current active state
3. `logs/daily_work_log.md` for chronological record

Do not let `daily_work_log.md` become the only source of important decisions.
Important conclusions must be promoted into `conversation_history.md`.

## Formatting Standards

### For `docs/conversation_history.md`
Prefer sections such as:
- 项目总原则
- 关键设计决策
- 环境与建模结论
- 训练设计结论
- 调试与排错结论
- 已否定路线
- 需持续继承的假设

### For `docs/current_status.md`
Prefer sections such as:
- 当前总目标
- 当前阶段
- 已完成
- 正在进行
- 当前阻塞点
- 下一步优先事项
- 当前默认方案
- 关键文件

### For `logs/daily_work_log.md`
Prefer date-based entries:
- 已完成任务
- 涉及文件
- 产出/结论
- 下一步

## Quality Bar
When writing memory files:
- prefer concrete conclusions over vague summaries
- write what future sessions need, not what was merely discussed
- avoid redundant duplication across files
- keep terminology consistent with the graduation project
- if a conclusion changes, update the old default in `current_status.md` and add the new durable conclusion to `conversation_history.md`

## Canonical project files
Use these files as the main project map instead of inferring from scattered artifacts alone:
- `AGENTS.md`
  - stable research background, constraints, project priorities, and RL training route
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
When project status changes, update `docs/current_status.md` in Chinese.
When repository organization changes, update `README.md`.
When research direction, constraints, or thesis priorities change, update `AGENTS.md`.
When a session yields durable conclusions, update `docs/conversation_history.md`.
When a session completes concrete work, append to `logs/daily_work_log.md` in Chinese.
