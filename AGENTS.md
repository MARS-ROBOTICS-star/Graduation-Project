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
The project is an undergraduate graduation design in robotics / mechatronics. The primary simulation and development stack is Isaac Sim 5.1 + Isaac Lab 2.3.x on Ubuntu 22.04. The project later will involve ROS integration, stereo cameras, LiDAR, and IMU.

## Core robot structure
The robot is a three-body articulated ground vehicle.
- head car
- body car
- tail car

The head-body and body-tail are connected through two 3RRR-spherical parallel mechanisms.
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
2. Build a stable simulation environment
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

---

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

---

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

---

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

---

## Priority and Conflict Resolution

If the files disagree, use this priority:
1. `docs/conversation_history.md` for long-term conclusions
2. `docs/current_status.md` for current active state
3. `logs/daily_work_log.md` for chronological record

Do not let `daily_work_log.md` become the only source of important decisions.
Important conclusions must be promoted into `conversation_history.md`.

---

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

---

## Quality Bar

When writing memory files:
- prefer concrete conclusions over vague summaries
- write what future sessions need, not what was merely discussed
- avoid redundant duplication across files
- keep terminology consistent with the graduation project
- if a conclusion changes, update the old default in `current_status.md` and add the new durable conclusion to `conversation_history.md`

## Non-goals unless explicitly requested
- perfect analytical fidelity of spherical parallel mechanism
- full sensor fusion stack before RL baseline
- excessive UI polishing
- broad refactors unrelated to making the environment trainable

## Current high-priority objective
Build a runnable Isaac Lab RL environment for the articulated car and obtain a first successful training result that demonstrates controllable body attitude / morphology behavior.

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
When project status changes, update `docs/current_status.md` in Chinese.
When repository organization changes, update `README.md`.
When research direction, constraints, or thesis priorities change, update `AGENTS.md`.
When a session yields durable conclusions, update `docs/conversation_history.md`.
When a session completes concrete work, append to `logs/daily_work_log.md` in Chinese.
