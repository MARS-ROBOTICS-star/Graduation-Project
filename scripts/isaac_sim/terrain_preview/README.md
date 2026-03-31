# MGDP Isaac Sim Terrain Preview

This folder now contains a copied and adapted MGDP terrain-generation path for Isaac Sim under the conda environment `env_isaacLab`.

It does not port the MGDP Isaac Gym training runtime.
It does port the terrain-generation and terrain-curriculum logic needed to inspect the generated terrain grid directly inside Isaac Sim or export it as USD.

## Included Files

- `mgdp_terrain_preview.py`
  - Isaac Sim entry script
- `run_terrain_preview.sh`
  - wrapper that activates `env_isaacLab` and launches the preview
- `terrain_builder.py`
  - shared Isaac Sim mesh / scene helpers
- `mgdp_port/`
  - copied MGDP terrain-generation code adapted to local relative imports
  - includes `terrain.py`, `terrain_utils.py`, `new_terrains/`, `configs.py`, `curriculum.py`

## What Is Ported

- Stage 1 terrain configuration from MGDP `mix`
- Stage 2 terrain configuration from MGDP `gap_parkour`
- Terrain grid construction
- Sub-terrain placement into one large heightfield / trimesh map
- Terrain curriculum origin assignment
- Visual curriculum markers for sampled environment origins

This is no longer only a conceptual reconstruction.
The preview is built from copied MGDP terrain logic adapted to run in Isaac Sim.

## Run In Isaac Sim

From the repository root:

```bash
./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --gallery both
```

Only stage 1:

```bash
./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --gallery stage1
```

Only stage 2:

```bash
./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --gallery stage2
```

The wrapper defaults to:

- conda env: `env_isaacLab`
- Isaac Sim root: `/home/ubuntu/isaacsim`

You can override the env name if needed:

```bash
ENV_NAME=env_isaacLab ./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh --gallery stage1
```

## Export USD Without Opening A Window

```bash
./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh \
  --headless \
  --gallery both \
  --save-usd outputs/isaacsim/mgdp_ported_terrain_both.usd
```

If `--save-usd` is omitted in headless mode, the script saves to:

```text
outputs/isaacsim/mgdp_ported_terrain_<gallery>.usd
```

## Runtime Notes

- The scene is terrain-only by design.
- The generated stage includes physics, collision, lights, and a camera view.
- The preview script uses `isaaclab.app.AppLauncher` and launches directly with `python` from `env_isaacLab`.
- This path has been validated locally with:
  - `--headless --frames 1 --gallery stage1`
  - `--headless --frames 1 --gallery stage2`
  - `--frames 1 --gallery stage1`
  - `--frames 1 --gallery stage2`

## Environment Requirement

For this workstation, Isaac Sim window startup required restoring the numerical stack inside `env_isaacLab` to an Isaac-Sim-compatible `numpy` line.

Validated local versions:

- `numpy == 1.26.0`
- `scipy == 1.14.1`

If the preview starts failing during Isaac Sim extension startup with `numpy` binary-compatibility errors, check the active versions first.
