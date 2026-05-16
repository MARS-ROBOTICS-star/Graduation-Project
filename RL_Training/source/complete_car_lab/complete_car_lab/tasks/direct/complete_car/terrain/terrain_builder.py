"""Training terrain builder for direct complete-car tasks."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.interpolate import RegularGridInterpolator


STAGE1_TERRAIN_CLASS_OTHER = 0
STAGE1_TERRAIN_CLASS_STEP = 1
STAGE1_TERRAIN_CLASS_GAP = 2

STAIRS_MIN_STEP_HEIGHT_M = 0.05
STAIRS_STEP_HEIGHT_RANGE_M = 0.13
DISCRETE_OBSTACLE_MIN_HEIGHT_M = 0.05
DISCRETE_OBSTACLE_HEIGHT_RANGE_M = 0.1159


@dataclass
class Stage1TerrainCfg:
    horizontal_scale: float = 0.1
    vertical_scale: float = 0.005
    border_size: float = 25.0
    terrain_length: float = 8.0
    terrain_width: float = 8.0
    num_rows: int = 20
    num_cols: int = 10
    slope_threshold: float = 0.75
    add_roughness: bool = False
    roughness_height_range: tuple[float, float] = (0.01, 0.04)
    roughness_downsampled_scale: float = 0.2
    terrain_dict: dict[str, float] = field(
        default_factory=lambda: {
            "flat": 0.10,
            "slope down": 0.10,
            "slope up": 0.10,
            "uneven rough": 0.20,
            "stairs down": 0.30,
            "discrete obstacles": 0.20,
        }
    )

    @property
    def terrain_proportions(self) -> list[float]:
        weights = list(self.terrain_dict.values())
        return [sum(weights[: i + 1]) for i in range(len(weights))]

    @property
    def width_per_env_pixels(self) -> int:
        return int(self.terrain_width / self.horizontal_scale)

    @property
    def length_per_env_pixels(self) -> int:
        return int(self.terrain_length / self.horizontal_scale)

    @property
    def border_pixels(self) -> int:
        return int(self.border_size / self.horizontal_scale)

    @property
    def total_rows(self) -> int:
        return self.num_rows * self.length_per_env_pixels + 2 * self.border_pixels

    @property
    def total_cols(self) -> int:
        return self.num_cols * self.width_per_env_pixels + 2 * self.border_pixels

    @property
    def terrain_names(self) -> list[str]:
        return list(self.terrain_dict.keys())

    @property
    def terrain_class_names(self) -> tuple[str, ...]:
        return ("other", "step", "gap")


@dataclass
class Stage1TerrainData:
    height_field_raw: np.ndarray
    env_origins: np.ndarray
    terrain_type: np.ndarray
    terrain_class: np.ndarray
    vertices: np.ndarray | None = None
    faces: np.ndarray | None = None
    x_edge_mask: np.ndarray | None = None


@dataclass
class _SubTerrain:
    width: int
    length: int
    vertical_scale: float
    horizontal_scale: float
    height_field_raw: np.ndarray


def create_empty_stage1_terrain_data(cfg: Stage1TerrainCfg | None = None) -> Stage1TerrainData:
    if cfg is None:
        cfg = Stage1TerrainCfg()

    return Stage1TerrainData(
        height_field_raw=np.zeros((cfg.total_rows, cfg.total_cols), dtype=np.int16),
        env_origins=np.zeros((cfg.num_rows, cfg.num_cols, 3), dtype=np.float32),
        terrain_type=np.zeros((cfg.num_rows, cfg.num_cols), dtype=np.int32),
        terrain_class=np.zeros((cfg.num_rows, cfg.num_cols), dtype=np.int32),
    )


def _tile_seed(cfg: Stage1TerrainCfg, row: int, col: int, terrain_idx: int) -> int:
    return terrain_idx * cfg.num_rows * cfg.num_cols + row * cfg.num_cols + col


def _make_subterrain(cfg: Stage1TerrainCfg) -> _SubTerrain:
    return _SubTerrain(
        width=cfg.length_per_env_pixels,
        length=cfg.width_per_env_pixels,
        vertical_scale=cfg.vertical_scale,
        horizontal_scale=cfg.horizontal_scale,
        height_field_raw=np.zeros((cfg.length_per_env_pixels, cfg.width_per_env_pixels), dtype=np.int16),
    )


def get_terrain_class_from_name(terrain_name: str) -> int:
    if terrain_name in {"stairs down", "stairs up", "discrete obstacles", "new stairs down"}:
        return STAGE1_TERRAIN_CLASS_STEP
    if terrain_name in {"gap", "pit"}:
        return STAGE1_TERRAIN_CLASS_GAP
    return STAGE1_TERRAIN_CLASS_OTHER


def _normalize_stairs_difficulty(cfg: Stage1TerrainCfg, difficulty: float) -> float:
    # The global curriculum passes row / num_rows. For stairs, normalize so the last row reaches max height.
    max_difficulty = max((cfg.num_rows - 1) / cfg.num_rows, 1.0e-6)
    return float(np.clip(difficulty / max_difficulty, 0.0, 1.0))


def _random_uniform_terrain(
    terrain: _SubTerrain,
    min_height: float,
    max_height: float,
    step: float = 0.005,
    downsampled_scale: float | None = None,
    rng: np.random.Generator | None = None,
) -> None:
    if downsampled_scale is None:
        downsampled_scale = terrain.horizontal_scale
    if rng is None:
        rng = np.random.default_rng()

    min_height_u = int(min_height / terrain.vertical_scale)
    max_height_u = int(max_height / terrain.vertical_scale)
    step_u = max(1, int(round(step / terrain.vertical_scale)))
    heights_range = np.arange(min_height_u, max_height_u + step_u, step_u, dtype=np.int16)

    ds_width = max(2, int(terrain.width * terrain.horizontal_scale / downsampled_scale))
    ds_length = max(2, int(terrain.length * terrain.horizontal_scale / downsampled_scale))
    height_field_downsampled = rng.choice(heights_range, size=(ds_width, ds_length))

    x = np.linspace(0, terrain.width * terrain.horizontal_scale, ds_width)
    y = np.linspace(0, terrain.length * terrain.horizontal_scale, ds_length)
    interpolator = RegularGridInterpolator((x, y), height_field_downsampled, method="linear")

    x_upsampled = np.linspace(0, terrain.width * terrain.horizontal_scale, terrain.width)
    y_upsampled = np.linspace(0, terrain.length * terrain.horizontal_scale, terrain.length)
    xx, yy = np.meshgrid(x_upsampled, y_upsampled, indexing="ij")
    z_upsampled = np.rint(interpolator(np.stack([xx, yy], axis=-1))).astype(np.int16)
    terrain.height_field_raw += z_upsampled


def _pyramid_sloped_terrain(terrain: _SubTerrain, slope: float = 1.0, platform_size: float = 1.0) -> None:
    x = np.arange(0, terrain.width)
    y = np.arange(0, terrain.length)
    center_x = int(terrain.width / 2)
    center_y = int(terrain.length / 2)
    xx, yy = np.meshgrid(x, y, sparse=True)
    xx = (center_x - np.abs(center_x - xx)) / center_x
    yy = (center_y - np.abs(center_y - yy)) / center_y
    xx = xx.reshape(terrain.width, 1)
    yy = yy.reshape(1, terrain.length)
    max_height = int(slope * (terrain.horizontal_scale / terrain.vertical_scale) * (terrain.width / 2))
    terrain.height_field_raw += (max_height * xx * yy).astype(np.int16)

    platform_size_px = int(platform_size / terrain.horizontal_scale / 2)
    x1 = terrain.width // 2 - platform_size_px
    x2 = terrain.width // 2 + platform_size_px
    y1 = terrain.length // 2 - platform_size_px
    y2 = terrain.length // 2 + platform_size_px
    min_h = min(terrain.height_field_raw[x1, y1], 0)
    max_h = max(terrain.height_field_raw[x1, y1], 0)
    terrain.height_field_raw = np.clip(terrain.height_field_raw, min_h, max_h).astype(np.int16)


def _pyramid_stairs_terrain(
    terrain: _SubTerrain,
    step_width: float,
    step_height: float,
    platform_size: float = 1.0,
) -> None:
    step_width_px = int(step_width / terrain.horizontal_scale)
    step_height_u = int(step_height / terrain.vertical_scale)
    platform_size_px = int(platform_size / terrain.horizontal_scale)

    height = 0
    start_x = 0
    stop_x = terrain.width
    start_y = 0
    stop_y = terrain.length
    while (stop_x - start_x) > platform_size_px and (stop_y - start_y) > platform_size_px:
        start_x += step_width_px
        stop_x -= step_width_px
        start_y += step_width_px
        stop_y -= step_width_px
        height += step_height_u
        terrain.height_field_raw[start_x:stop_x, start_y:stop_y] = height


def _discrete_obstacles_terrain(
    terrain: _SubTerrain,
    max_height: float,
    min_size: float,
    max_size: float,
    num_rects: int,
    platform_size: float = 1.0,
    rng: np.random.Generator | None = None,
) -> None:
    if rng is None:
        rng = np.random.default_rng()

    max_height_u = int(max_height / terrain.vertical_scale)
    min_size_px = int(min_size / terrain.horizontal_scale)
    max_size_px = int(max_size / terrain.horizontal_scale)
    platform_size_px = int(platform_size / terrain.horizontal_scale)

    height_range = np.array([-max_height_u, -max_height_u // 2, max_height_u // 2, max_height_u], dtype=np.int16)
    width_range = np.arange(min_size_px, max_size_px, 4)
    length_range = np.arange(min_size_px, max_size_px, 4)
    rows, cols = terrain.height_field_raw.shape

    for _ in range(num_rects):
        width = int(rng.choice(width_range))
        length = int(rng.choice(length_range))
        start_i = int(rng.choice(np.arange(0, max(1, rows - width), 4)))
        start_j = int(rng.choice(np.arange(0, max(1, cols - length), 4)))
        terrain.height_field_raw[start_i : start_i + width, start_j : start_j + length] = int(rng.choice(height_range))

    x1 = (terrain.width - platform_size_px) // 2
    x2 = (terrain.width + platform_size_px) // 2
    y1 = (terrain.length - platform_size_px) // 2
    y2 = (terrain.length + platform_size_px) // 2
    terrain.height_field_raw[x1:x2, y1:y2] = 0


def _parkour_step_terrain(
    terrain: _SubTerrain,
    difficulty: float,
    x_range: tuple[float, float] = (1.6, 2.0),
    rng: np.random.Generator | None = None,
) -> None:
    if rng is None:
        rng = np.random.default_rng()

    max_height = 1.0
    min_height = 0.0
    if difficulty < 0.1:
        hurdle_height_min_m = difficulty + 0.04
        hurdle_height_max_m = hurdle_height_min_m + 0.04
    else:
        hurdle_height_min_m = difficulty * (max_height - min_height) * 0.8
        hurdle_height_max_m = hurdle_height_min_m + 0.01

    dis_x_min = round(x_range[0] / terrain.horizontal_scale)
    dis_x_max = round(x_range[1] / terrain.horizontal_scale)
    hurdle_height_max = round(hurdle_height_max_m / terrain.vertical_scale)
    hurdle_height_min = round(hurdle_height_min_m / terrain.vertical_scale)
    step_height = int(rng.integers(hurdle_height_min, max(hurdle_height_min + 1, hurdle_height_max)))
    max_x = int(terrain.width + round(1.5 / terrain.horizontal_scale))

    start_y = 2
    end_y = int(terrain.length) - 2
    new_stair_height = 0

    start_x = int(rng.integers(60, 65))
    rand_x = int(rng.integers(dis_x_min, dis_x_max))
    new_stair_height += step_height
    end_x = int(np.clip(start_x + rand_x, start_x, max_x))
    terrain.height_field_raw[start_x:end_x, start_y:end_y] = new_stair_height


def _parkour_step_gap_terrain(
    terrain: _SubTerrain,
    gap_size: float,
    depth: float,
    platform_size: float = 2.0,
) -> None:
    gap_size_px = int(np.clip(int(gap_size), 1, 13))
    depth_u = int(depth / terrain.vertical_scale)
    platform_size_px = int(platform_size / terrain.horizontal_scale)

    start_y = 0
    end_y = int(terrain.length - platform_size_px / 8)
    start_x = platform_size_px
    center_x = terrain.width

    terrain.height_field_raw[start_x:center_x, start_y:end_y] = -depth_u
    terrain.height_field_raw[start_x + gap_size_px : center_x - gap_size_px, start_y + gap_size_px : end_y - gap_size_px] = 0


def _half_sloped_terrain(terrain: _SubTerrain, level_index: float, platform_size: float = 2.0) -> None:
    terrain_length = terrain.length
    slope_start = 5
    platform_size_px = int(platform_size / terrain.horizontal_scale)
    slope_end = int((terrain.width - platform_size_px) / 2)

    height2width_ratio = 2 * int(level_index + 1)
    xs = np.arange(slope_start, slope_end)
    max_height_int = height2width_ratio * (slope_end - slope_start)
    heights = (height2width_ratio * (xs - slope_start)).clip(max=max_height_int).astype(np.int16)
    terrain.height_field_raw[slope_start:slope_end, :] = heights[:, None]

    x1 = slope_end
    x2 = int((terrain.width + platform_size_px) / 2)
    terrain.height_field_raw[x1:x2, :] = max_height_int

    slope_start = x2
    slope_end = terrain_length - 5
    xs = np.arange(slope_start, slope_end)
    heights = (height2width_ratio * (xs - slope_start)).clip(max=max_height_int).astype(np.int16)
    reversed_index = len(heights) - 1
    for i in range(slope_start, slope_end):
        terrain.height_field_raw[i, :] = heights[reversed_index]
        reversed_index -= 1


def _stepping_beams_terrain(
    terrain: _SubTerrain,
    stone_size: float,
    stone_distance: float,
    max_height: float,
    platform_size: float = 2.0,
    depth: float = 0.5,
    rng: np.random.Generator | None = None,
) -> None:
    if rng is None:
        rng = np.random.default_rng()

    beam_length = int(stone_size / terrain.horizontal_scale)
    stone_distance_px = int(np.clip(int(stone_distance / terrain.horizontal_scale), 1, 5))
    platform_size_px = int(platform_size / terrain.horizontal_scale)
    max_height_u = int(np.clip(max_height / terrain.vertical_scale, 0, 30))
    height_range = np.arange(0, max_height_u, step=4, dtype=np.int16)
    if height_range.size == 0:
        height_range = np.array([0], dtype=np.int16)

    platform_y = terrain.length // 2 - platform_size_px // 2
    terrain.height_field_raw[:, :] = int(-depth / terrain.vertical_scale)
    min_beam_width = 15
    max_beam_width = 30

    x1 = terrain.width // 2 - platform_size_px // 2
    x2 = terrain.width // 2 + platform_size_px // 2

    start_x_front = terrain.width // 2 - platform_size_px // 2 - 1
    while start_x_front >= 0:
        beam_width = int(rng.integers(min_beam_width, max_beam_width + 1))
        row1_y = int(platform_y + platform_size_px / 2 - beam_width / 2)
        stop_x_front = max(0, start_x_front - beam_length)
        terrain.height_field_raw[stop_x_front:start_x_front, row1_y : row1_y + beam_width] = int(rng.choice(height_range))
        start_x_front -= beam_length + stone_distance_px

    start_x_back = terrain.width // 2 + platform_size_px // 2 + 1
    while start_x_back < terrain.width:
        beam_width = int(rng.integers(min_beam_width, max_beam_width + 1))
        row1_y = int(platform_y + platform_size_px / 2 - beam_width / 2)
        stop_x_back = min(terrain.width, start_x_back + beam_length)
        terrain.height_field_raw[start_x_back:stop_x_back, row1_y : row1_y + beam_width] = int(rng.choice(height_range))
        start_x_back += beam_length + stone_distance_px

    terrain.height_field_raw[x1:x2, platform_y : platform_y + platform_size_px] = 0


def _pit_terrain(terrain: _SubTerrain, depth: float, platform_size: float = 4.0) -> None:
    depth_u = int(depth / terrain.vertical_scale)
    platform_size_px = int(platform_size / terrain.horizontal_scale / 2)
    x1 = terrain.length // 2 - platform_size_px
    x2 = terrain.length // 2 + platform_size_px
    y1 = terrain.width // 2 - platform_size_px
    y2 = terrain.width // 2 + platform_size_px
    terrain.height_field_raw[x1:x2, y1:y2] = -depth_u


def _maybe_add_roughness(
    terrain: _SubTerrain,
    cfg: Stage1TerrainCfg,
    difficulty: float,
    rng: np.random.Generator,
) -> None:
    if not cfg.add_roughness:
        return
    min_height, max_height = cfg.roughness_height_range
    max_height = (max_height - min_height) * difficulty + min_height
    sampled_height = float(rng.uniform(min_height, max_height))
    _random_uniform_terrain(
        terrain,
        min_height=-sampled_height,
        max_height=sampled_height,
        step=0.005,
        downsampled_scale=cfg.roughness_downsampled_scale,
        rng=rng,
    )


def make_slope_tile(cfg: Stage1TerrainCfg, difficulty: float, descending: bool = False) -> np.ndarray:
    terrain = _make_subterrain(cfg)
    slope = difficulty * 0.65
    if descending:
        slope *= -1
    _pyramid_sloped_terrain(terrain, slope=slope, platform_size=3.0)
    return terrain.height_field_raw.copy()


def make_slope_down_tile(cfg: Stage1TerrainCfg, difficulty: float) -> np.ndarray:
    return make_slope_tile(cfg, difficulty, descending=True)


def make_slope_up_tile(cfg: Stage1TerrainCfg, difficulty: float) -> np.ndarray:
    return make_slope_tile(cfg, difficulty, descending=False)


def make_pyramid_tile(cfg: Stage1TerrainCfg, difficulty: float, seed: int) -> np.ndarray:
    terrain = _make_subterrain(cfg)
    rng = np.random.default_rng(seed)
    _pyramid_sloped_terrain(terrain, slope=difficulty * 0.4, platform_size=3.0)
    _random_uniform_terrain(terrain, min_height=-0.05, max_height=0.05, step=0.005, downsampled_scale=0.2, rng=rng)
    return terrain.height_field_raw.copy()


def make_stairs_tile(
    cfg: Stage1TerrainCfg,
    difficulty: float,
    descending: bool,
    step_width_m: float = 0.31,
    extra_step_height_m: float = 0.0,
) -> np.ndarray:
    terrain = _make_subterrain(cfg)
    stairs_difficulty = _normalize_stairs_difficulty(cfg, difficulty)
    step_height = STAIRS_MIN_STEP_HEIGHT_M + STAIRS_STEP_HEIGHT_RANGE_M * stairs_difficulty + extra_step_height_m
    if descending:
        step_height *= -1
    _pyramid_stairs_terrain(terrain, step_width=step_width_m, step_height=step_height, platform_size=3.0)
    return terrain.height_field_raw.copy()


def make_discrete_obstacles_tile(cfg: Stage1TerrainCfg, difficulty: float, seed: int) -> np.ndarray:
    terrain = _make_subterrain(cfg)
    rng = np.random.default_rng(seed)
    _discrete_obstacles_terrain(
        terrain,
        max_height=DISCRETE_OBSTACLE_MIN_HEIGHT_M + difficulty * DISCRETE_OBSTACLE_HEIGHT_RANGE_M,
        min_size=1.0,
        max_size=2.5,
        num_rects=20,
        platform_size=3.0,
        rng=rng,
    )
    return terrain.height_field_raw.copy()


def make_hurdle_tile(cfg: Stage1TerrainCfg, difficulty: float, seed: int) -> np.ndarray:
    terrain = _make_subterrain(cfg)
    rng = np.random.default_rng(seed)
    _parkour_step_terrain(terrain, difficulty=difficulty, x_range=(1.6, 2.0), rng=rng)
    _maybe_add_roughness(terrain, cfg, difficulty, rng)
    return terrain.height_field_raw.copy()


def make_gap_tile(cfg: Stage1TerrainCfg, difficulty: float, seed: int) -> np.ndarray:
    terrain = _make_subterrain(cfg)
    rng = np.random.default_rng(seed)
    gap_size = 0.5 * difficulty if difficulty < 0.1 else 0.1 + difficulty / terrain.horizontal_scale
    _parkour_step_gap_terrain(terrain, gap_size=gap_size, depth=0.5, platform_size=2.0)
    _maybe_add_roughness(terrain, cfg, difficulty, rng)
    return terrain.height_field_raw.copy()


def make_ramp_tile(cfg: Stage1TerrainCfg, difficulty: float, seed: int) -> np.ndarray:
    terrain = _make_subterrain(cfg)
    rng = np.random.default_rng(seed)
    _half_sloped_terrain(terrain, level_index=difficulty * 7, platform_size=2.0)
    _maybe_add_roughness(terrain, cfg, difficulty, rng)
    return terrain.height_field_raw.copy()


def make_beam_tile(cfg: Stage1TerrainCfg, difficulty: float, seed: int) -> np.ndarray:
    terrain = _make_subterrain(cfg)
    rng = np.random.default_rng(seed)
    beam_length = 1.0 if difficulty < 0.2 else -0.4 * difficulty + 0.9
    stone_distance = 0.1 if difficulty < 0.2 else 0.4 * int(10 * difficulty) / 10
    step_height = 0.05 + 0.18 * difficulty
    _stepping_beams_terrain(
        terrain,
        stone_size=beam_length,
        stone_distance=stone_distance,
        max_height=step_height,
        platform_size=2.0,
        depth=0.5,
        rng=rng,
    )
    _maybe_add_roughness(terrain, cfg, difficulty, rng)
    return terrain.height_field_raw.copy()


def make_new_stairs_down_tile(cfg: Stage1TerrainCfg, difficulty: float) -> np.ndarray:
    return make_stairs_tile(cfg, difficulty, descending=True, step_width_m=0.5, extra_step_height_m=0.2)


def make_pit_tile(cfg: Stage1TerrainCfg, difficulty: float) -> np.ndarray:
    terrain = _make_subterrain(cfg)
    _pit_terrain(terrain, depth=1.0 * difficulty, platform_size=4.0)
    return terrain.height_field_raw.copy()


def get_terrain_idx_from_choice(cfg: Stage1TerrainCfg, choice: float) -> int:
    for idx, upper_bound in enumerate(cfg.terrain_proportions):
        if choice < upper_bound:
            return idx
    return len(cfg.terrain_proportions) - 1


def get_terrain_name_from_idx(cfg: Stage1TerrainCfg, terrain_idx: int) -> str:
    return cfg.terrain_names[terrain_idx]


def make_tile_by_name(cfg: Stage1TerrainCfg, terrain_name: str, difficulty: float, choice: float, seed: int) -> np.ndarray:
    del choice
    if terrain_name == "flat":
        return _make_subterrain(cfg).height_field_raw.copy()
    if terrain_name == "slope down":
        return make_slope_down_tile(cfg, difficulty)
    if terrain_name == "slope up":
        return make_slope_up_tile(cfg, difficulty)
    if terrain_name == "uneven rough":
        return make_pyramid_tile(cfg, difficulty, seed=seed)
    if terrain_name == "stairs down":
        return make_stairs_tile(cfg, difficulty, descending=True)
    if terrain_name == "stairs up":
        return make_stairs_tile(cfg, difficulty, descending=False)
    if terrain_name == "discrete obstacles":
        return make_discrete_obstacles_tile(cfg, difficulty, seed)
    if terrain_name == "hurdle":
        return make_hurdle_tile(cfg, difficulty, seed)
    if terrain_name == "gap":
        return make_gap_tile(cfg, difficulty, seed)
    if terrain_name == "ramp":
        return make_ramp_tile(cfg, difficulty, seed)
    if terrain_name == "beam":
        return make_beam_tile(cfg, difficulty, seed)
    if terrain_name == "new stairs down":
        return make_new_stairs_down_tile(cfg, difficulty)
    if terrain_name == "pit":
        return make_pit_tile(cfg, difficulty)
    raise ValueError(f"Unsupported terrain name: {terrain_name}")


def make_tile_by_col(cfg: Stage1TerrainCfg, row: int, col: int) -> tuple[np.ndarray, int]:
    difficulty = row / cfg.num_rows
    choice = col / cfg.num_cols + 0.001
    terrain_idx = get_terrain_idx_from_choice(cfg, choice)
    terrain_name = get_terrain_name_from_idx(cfg, terrain_idx)
    seed = _tile_seed(cfg, row, col, terrain_idx)
    tile = make_tile_by_name(cfg, terrain_name, difficulty, choice, seed)
    return tile, terrain_idx


def get_origin_patch_center(cfg: Stage1TerrainCfg, terrain_name: str) -> tuple[int, int]:
    del terrain_name
    return cfg.length_per_env_pixels // 2, cfg.width_per_env_pixels // 2


def get_origin_patch_radius(cfg: Stage1TerrainCfg, terrain_name: str) -> tuple[int, int]:
    del terrain_name
    half_patch_x = int(1.0 / cfg.horizontal_scale)
    half_patch_y = int(1.0 / cfg.horizontal_scale)
    return half_patch_x, half_patch_y


def write_tile_to_map(data: Stage1TerrainData, tile: np.ndarray, row: int, col: int, terrain_idx: int, cfg: Stage1TerrainCfg) -> None:
    start_x = cfg.border_pixels + row * cfg.length_per_env_pixels
    end_x = start_x + cfg.length_per_env_pixels
    start_y = cfg.border_pixels + col * cfg.width_per_env_pixels
    end_y = start_y + cfg.width_per_env_pixels
    data.height_field_raw[start_x:end_x, start_y:end_y] = tile
    data.terrain_type[row, col] = terrain_idx


def set_tile_origin(data: Stage1TerrainData, row: int, col: int, terrain_name: str, cfg: Stage1TerrainCfg) -> None:
    center_x, center_y = get_origin_patch_center(cfg, terrain_name)
    origin_x = (row + 0.5) * cfg.terrain_length
    origin_y = (col + 0.5) * cfg.terrain_width
    radius_x, radius_y = get_origin_patch_radius(cfg, terrain_name)

    x1 = max(0, center_x - radius_x)
    x2 = min(cfg.length_per_env_pixels, center_x + radius_x)
    y1 = max(0, center_y - radius_y)
    y2 = min(cfg.width_per_env_pixels, center_y + radius_y)

    if x2 <= x1:
        x2 = min(cfg.length_per_env_pixels, x1 + 1)
    if y2 <= y1:
        y2 = min(cfg.width_per_env_pixels, y1 + 1)

    tile_center_patch = data.height_field_raw[
        cfg.border_pixels + row * cfg.length_per_env_pixels + x1 : cfg.border_pixels + row * cfg.length_per_env_pixels + x2,
        cfg.border_pixels + col * cfg.width_per_env_pixels + y1 : cfg.border_pixels + col * cfg.width_per_env_pixels + y2,
    ]
    origin_z = max(0.0, float(tile_center_patch.max()) * cfg.vertical_scale)
    data.env_origins[row, col] = [origin_x, origin_y, origin_z]


def set_tile_class(data: Stage1TerrainData, row: int, col: int, terrain_name: str) -> None:
    data.terrain_class[row, col] = get_terrain_class_from_name(terrain_name)


def build_stage1_map(cfg: Stage1TerrainCfg | None = None) -> Stage1TerrainData:
    if cfg is None:
        cfg = Stage1TerrainCfg()

    data = create_empty_stage1_terrain_data(cfg)
    for row in range(cfg.num_rows):
        for col in range(cfg.num_cols):
            tile, terrain_idx = make_tile_by_col(cfg, row, col)
            terrain_name = get_terrain_name_from_idx(cfg, terrain_idx)
            write_tile_to_map(data, tile, row=row, col=col, terrain_idx=terrain_idx, cfg=cfg)
            set_tile_origin(data, row=row, col=col, terrain_name=terrain_name, cfg=cfg)
            set_tile_class(data, row=row, col=col, terrain_name=terrain_name)
    return data


def convert_heightfield_to_trimesh(
    height_field_raw: np.ndarray,
    horizontal_scale: float,
    vertical_scale: float,
    slope_threshold: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    hf = height_field_raw
    num_rows = hf.shape[0]
    num_cols = hf.shape[1]

    y = np.linspace(0, (num_cols - 1) * horizontal_scale, num_cols)
    x = np.linspace(0, (num_rows - 1) * horizontal_scale, num_rows)
    yy, xx = np.meshgrid(y, x)

    if slope_threshold is not None:
        slope_threshold *= horizontal_scale / vertical_scale

        move_x = np.zeros((num_rows, num_cols))
        move_y = np.zeros((num_rows, num_cols))
        move_corners = np.zeros((num_rows, num_cols))

        move_x[: num_rows - 1, :] += hf[1:num_rows, :] - hf[: num_rows - 1, :] > slope_threshold
        move_x[1:num_rows, :] -= hf[: num_rows - 1, :] - hf[1:num_rows, :] > slope_threshold

        move_y[:, : num_cols - 1] += hf[:, 1:num_cols] - hf[:, : num_cols - 1] > slope_threshold
        move_y[:, 1:num_cols] -= hf[:, : num_cols - 1] - hf[:, 1:num_cols] > slope_threshold

        move_corners[: num_rows - 1, : num_cols - 1] += (
            hf[1:num_rows, 1:num_cols] - hf[: num_rows - 1, : num_cols - 1] > slope_threshold
        )
        move_corners[1:num_rows, 1:num_cols] -= (
            hf[: num_rows - 1, : num_cols - 1] - hf[1:num_rows, 1:num_cols] > slope_threshold
        )

        xx += (move_x + move_corners * (move_x == 0)) * horizontal_scale
        yy += (move_y + move_corners * (move_y == 0)) * horizontal_scale
    else:
        move_x = np.zeros((num_rows, num_cols))

    vertices = np.zeros((num_rows * num_cols, 3), dtype=np.float32)
    vertices[:, 0] = xx.flatten()
    vertices[:, 1] = yy.flatten()
    vertices[:, 2] = hf.flatten() * vertical_scale

    triangles = -np.ones((2 * (num_rows - 1) * (num_cols - 1), 3), dtype=np.uint32)
    for i in range(num_rows - 1):
        ind0 = np.arange(0, num_cols - 1) + i * num_cols
        ind1 = ind0 + 1
        ind2 = ind0 + num_cols
        ind3 = ind2 + 1

        start = 2 * i * (num_cols - 1)
        stop = start + 2 * (num_cols - 1)
        triangles[start:stop:2, 0] = ind0
        triangles[start:stop:2, 1] = ind3
        triangles[start:stop:2, 2] = ind1
        triangles[start + 1 : stop : 2, 0] = ind0
        triangles[start + 1 : stop : 2, 1] = ind2
        triangles[start + 1 : stop : 2, 2] = ind3

    return vertices, triangles, move_x != 0


def convert_heightfield_to_mesh(data: Stage1TerrainData, cfg: Stage1TerrainCfg) -> Stage1TerrainData:
    vertices, faces, x_edge_mask = convert_heightfield_to_trimesh(
        data.height_field_raw,
        cfg.horizontal_scale,
        cfg.vertical_scale,
        slope_threshold=cfg.slope_threshold,
    )
    data.vertices = vertices
    data.faces = faces
    data.x_edge_mask = x_edge_mask
    return data


def build_stage1_terrain_data(cfg: Stage1TerrainCfg | None = None) -> Stage1TerrainData:
    if cfg is None:
        cfg = Stage1TerrainCfg()
    data = build_stage1_map(cfg)
    return convert_heightfield_to_mesh(data, cfg)


__all__ = [
    "STAGE1_TERRAIN_CLASS_GAP",
    "STAGE1_TERRAIN_CLASS_OTHER",
    "STAGE1_TERRAIN_CLASS_STEP",
    "Stage1TerrainCfg",
    "Stage1TerrainData",
    "build_stage1_terrain_data",
    "convert_heightfield_to_mesh",
    "convert_heightfield_to_trimesh",
    "get_origin_patch_center",
    "get_origin_patch_radius",
    "get_terrain_idx_from_choice",
    "get_terrain_name_from_idx",
    "make_tile_by_col",
    "make_tile_by_name",
]
