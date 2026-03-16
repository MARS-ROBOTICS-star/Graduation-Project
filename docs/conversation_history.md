# Conversation History

This file stores durable conclusions from past Codex sessions so that future sessions can continue work without relying on ephemeral chat history alone.

## 2026-03-16

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
