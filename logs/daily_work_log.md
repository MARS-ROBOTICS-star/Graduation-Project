# Daily Work Log

## 2026-03-16

Completed:
- Reorganized the repository into clearer `scripts/`, `results/`, `refs/`, and `src/` areas.
- Added repository-level startup context rules to `AGENTS.md`.
- Added durable session memory file `docs/conversation_history.md`.
- Added date-based progress log `logs/daily_work_log.md`.
- Updated Isaac Sim helper scripts to use repository-relative paths.
- Confirmed `.codex/config.toml` exists and web search is enabled.

Files changed:
- `AGENTS.md`
- `README.md`
- `docs/conversation_history.md`
- `logs/daily_work_log.md`
- `scripts/isaac_sim/control_keyboard.py`
- `scripts/isaac_sim/validate_sensors.py`
- `refs/isaac_kb/README.md`
- `src/rl_lab/README.md`

Next:
- Build the first minimal Isaac Lab attitude-stabilization task under `src/rl_lab/`.
