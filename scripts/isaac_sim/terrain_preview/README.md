# MGDP Isaac Sim Terrain Preview

This folder adds a terrain-only Isaac Sim preview path for this repository.

It does not port the Isaac Gym training runtime.
It does provide an Isaac Sim scene builder for representative MGDP terrain categories, so you can inspect the terrain layout and overall visual effect in an Isaac Sim window or export a USD stage.

## What It Builds

- `stage1 mix` gallery:
  - `slope_ramp`
  - `stairs_up`
  - `discrete_obstacles`
  - `gap`
- `stage2 gap_parkour` gallery:
  - `single_gap`
  - `stepping_stones`
  - `single_bridge`
  - `air_beams`
  - `corridor`

These previews follow the project's terrain categories and proportions conceptually, but they are viewer-oriented reconstructions for Isaac Sim, not a byte-for-byte port of the Isaac Gym terrain runtime.

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

## Export USD Without Opening A Window

```bash
./scripts/isaac_sim/terrain_preview/run_terrain_preview.sh \
  --headless \
  --gallery both \
  --save-usd outputs/isaacsim/mgdp_terrain_both.usd
```

If `--save-usd` is omitted in headless mode, the script saves to:

```text
outputs/isaacsim/mgdp_terrain_<gallery>.usd
```

## Notes

- The wrapper uses `ISAAC_SIM_ROOT` if set, otherwise defaults to `/home/lbz/isaac-sim`.
- The scene is terrain-only by design.
- The generated stage includes physics, collision, lights, and a camera view.

## Use With Keyboard Teleop

`scripts/isaac_sim/control_keyboard.py` can now build one terrain tile under the car before teleop starts.

Default teleop startup uses `slope_ramp`:

```bash
python3 scripts/isaac_sim/control_keyboard.py
```

Specify another tile explicitly:

```bash
python3 scripts/isaac_sim/control_keyboard.py --terrain stairs_up
python3 scripts/isaac_sim/control_keyboard.py --terrain gap
python3 scripts/isaac_sim/control_keyboard.py --terrain corridor
```

Disable terrain injection:

```bash
python3 scripts/isaac_sim/control_keyboard.py --terrain none
```
