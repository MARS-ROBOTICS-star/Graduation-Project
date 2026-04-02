from dataclasses import dataclass, field

import numpy as np

@dataclass(frozen=True)
class Stage1TerrainCfg:
    horizontal_scale: float = 0.1
    vertical_scale: float = 0.005
    border_size: float = 25.0
    terrain_length: float = 8.0
    terrain_width: float = 8.0
    num_rows: int = 20
    num_cols: int = 10
    slope_threshold: float = 0.75
    terrain_dict: dict[str, float] = field(
        default_factory=lambda: {
            "slope down": 0.2,
            "pyramid": 0.2,
            "stairs down": 0.2,
            "stairs up": 0.2,
            "discrete obstacles": 1.1,
            "hurdle": 0.2,
            "gap": 1.2,
            "ramp": 1.1,
            "beam": 0.0,
            "new stairs down": 0.3,
            "pit": 1.0,
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

@dataclass
class Stage1TerrainData:
    height_field_raw: np.ndarray
    env_origins: np.ndarray
    terrain_type: np.ndarray
    vertices: np.ndarray | None = None
    faces: np.ndarray | None = None
    x_edge_mask: np.ndarray | None = None


def create_empty_stage1_terrain_data(
    cfg: Stage1TerrainCfg | None = None,
) -> Stage1TerrainData:
    if cfg is None:
        cfg = Stage1TerrainCfg()

    return Stage1TerrainData(
        height_field_raw=np.zeros((cfg.total_rows, cfg.total_cols), dtype=np.int16),
        env_origins=np.zeros((cfg.num_rows, cfg.num_cols, 3), dtype=np.float32),
        terrain_type=np.zeros((cfg.num_rows, cfg.num_cols), dtype=np.int32),
    )


def make_flat_tile(cfg: Stage1TerrainCfg) -> np.ndarray:
    return np.zeros(
        (cfg.length_per_env_pixels, cfg.width_per_env_pixels),
        dtype=np.int16,
    )


def _meters_to_height_units(cfg: Stage1TerrainCfg, value_m: float) -> int:
    return int(round(value_m / cfg.vertical_scale))


def _meters_to_pixels(cfg: Stage1TerrainCfg, value_m: float) -> int:
    return max(1, int(round(value_m / cfg.horizontal_scale)))


def _tile_seed(cfg: Stage1TerrainCfg, row: int, col: int, terrain_idx: int) -> int:
    return terrain_idx * cfg.num_rows * cfg.num_cols + row * cfg.num_cols + col


def _apply_roughness(
    tile: np.ndarray,
    cfg: Stage1TerrainCfg,
    difficulty: float,
    seed: int,
) -> np.ndarray:
    roughness_units = _meters_to_height_units(cfg, 0.05 * difficulty)
    if roughness_units <= 0:
        return tile

    rng = np.random.default_rng(seed)
    noise = rng.integers(
        -roughness_units,
        roughness_units + 1,
        size=tile.shape,
        dtype=np.int16,
    )
    return (tile.astype(np.int32) + noise.astype(np.int32)).astype(np.int16)


def make_slope_tile(
    cfg: Stage1TerrainCfg,
    difficulty: float,
    max_height: int = 20,
    descending: bool = False,
) -> np.ndarray:
    tile = np.zeros(
        (cfg.length_per_env_pixels, cfg.width_per_env_pixels),
        dtype=np.int16,
    )

    for i in range(cfg.length_per_env_pixels):
        height = int(max_height * difficulty * i / cfg.length_per_env_pixels)
        tile[i, :] = -height if descending else height

    return tile


def make_pyramid_tile(
    cfg: Stage1TerrainCfg,
    difficulty: float,
    max_height: int = 20,
    seed: int | None = None,
) -> np.ndarray:
    tile = np.zeros(
        (cfg.length_per_env_pixels, cfg.width_per_env_pixels),
        dtype=np.int16,
    )

    center_x = cfg.length_per_env_pixels / 2
    center_y = cfg.width_per_env_pixels / 2
    height_scale = max_height * difficulty

    for i in range(cfg.length_per_env_pixels):
        for j in range(cfg.width_per_env_pixels):
            dx = abs(i - center_x) / center_x
            dy = abs(j - center_y) / center_y
            value = max(0.0, 1.0 - max(dx, dy))
            tile[i, j] = int(height_scale * value)

    if seed is not None:
        tile = _apply_roughness(tile, cfg, difficulty, seed)
    return tile


def make_stairs_tile(
    cfg: Stage1TerrainCfg,
    difficulty: float,
    descending: bool,
    step_width_m: float = 0.31,
    extra_step_height_m: float = 0.0,
) -> np.ndarray:
    tile = np.zeros(
        (cfg.length_per_env_pixels, cfg.width_per_env_pixels),
        dtype=np.int16,
    )
    step_width_px = _meters_to_pixels(cfg, step_width_m)
    step_height_units = max(
        1,
        _meters_to_height_units(cfg, 0.05 + 0.18 * difficulty + extra_step_height_m),
    )
    platform_px = _meters_to_pixels(cfg, 3.0)
    stair_end = max(step_width_px, (cfg.length_per_env_pixels - platform_px) // 2)
    num_steps = int(np.ceil(stair_end / step_width_px))
    current_height = step_height_units * max(num_steps - 1, 0) if descending else 0

    for start_x in range(0, stair_end, step_width_px):
        end_x = min(cfg.length_per_env_pixels, start_x + step_width_px)
        tile[start_x:end_x, :] = current_height
        current_height += -step_height_units if descending else step_height_units

    plateau_start = stair_end
    plateau_end = min(cfg.length_per_env_pixels, plateau_start + platform_px)
    plateau_height = int(tile[max(0, plateau_start - 1), 0]) if plateau_start > 0 else 0
    tile[plateau_start:plateau_end, :] = plateau_height

    if descending:
        tile[plateau_end:, :] = 0
    else:
        tile[plateau_end:, :] = plateau_height

    return tile


def make_discrete_obstacles_tile(
    cfg: Stage1TerrainCfg,
    difficulty: float,
    seed: int,
) -> np.ndarray:
    tile = np.zeros(
        (cfg.length_per_env_pixels, cfg.width_per_env_pixels),
        dtype=np.int16,
    )
    rng = np.random.default_rng(seed)
    obstacle_height_units = max(1, _meters_to_height_units(cfg, 0.05 + difficulty * 0.2))
    rect_min = _meters_to_pixels(cfg, 1.0)
    rect_max = _meters_to_pixels(cfg, 2.5)

    for _ in range(20):
        rect_w = int(rng.integers(rect_min, rect_max + 1))
        rect_h = int(rng.integers(rect_min, rect_max + 1))
        start_x = int(rng.integers(0, max(1, cfg.length_per_env_pixels - rect_w)))
        start_y = int(rng.integers(0, max(1, cfg.width_per_env_pixels - rect_h)))
        height = int(rng.integers(max(1, obstacle_height_units // 2), obstacle_height_units + 1))
        tile[start_x:start_x + rect_w, start_y:start_y + rect_h] = height

    platform_px = _meters_to_pixels(cfg, 3.0)
    center_x = cfg.length_per_env_pixels // 2
    center_y = cfg.width_per_env_pixels // 2
    x1 = max(0, center_x - platform_px // 2)
    x2 = min(cfg.length_per_env_pixels, center_x + platform_px // 2)
    y1 = max(0, center_y - platform_px // 2)
    y2 = min(cfg.width_per_env_pixels, center_y + platform_px // 2)
    tile[x1:x2, y1:y2] = 0
    return tile


def make_hurdle_tile(
    cfg: Stage1TerrainCfg,
    difficulty: float,
    seed: int,
) -> np.ndarray:
    tile = np.zeros(
        (cfg.length_per_env_pixels, cfg.width_per_env_pixels),
        dtype=np.int16,
    )
    rng = np.random.default_rng(seed)
    hurdle_height_m = difficulty + 0.04 if difficulty < 0.1 else difficulty * 0.8 + 0.04
    hurdle_height_units = max(1, _meters_to_height_units(cfg, hurdle_height_m))
    hurdle_length_px = int(
        rng.integers(
            _meters_to_pixels(cfg, 1.6),
            _meters_to_pixels(cfg, 2.0) + 1,
        )
    )
    start_x = min(cfg.length_per_env_pixels - hurdle_length_px - 1, int(cfg.length_per_env_pixels * 0.75))
    side_margin = _meters_to_pixels(cfg, 0.2)
    tile[start_x:start_x + hurdle_length_px, side_margin:cfg.width_per_env_pixels - side_margin] = hurdle_height_units
    return _apply_roughness(tile, cfg, difficulty, seed + 1)


def make_gap_tile(
    cfg: Stage1TerrainCfg,
    difficulty: float,
    seed: int,
) -> np.ndarray:
    tile = np.zeros(
        (cfg.length_per_env_pixels, cfg.width_per_env_pixels),
        dtype=np.int16,
    )
    gap_depth_units = max(1, _meters_to_height_units(cfg, 0.5))
    gap_half_width_px = max(
        1,
        int(0.5 * difficulty) if difficulty < 0.1 else int(0.1 + difficulty / cfg.horizontal_scale),
    )
    gap_half_width_px = int(np.clip(gap_half_width_px, 1, 13))
    center_x = cfg.length_per_env_pixels // 2
    x1 = max(0, center_x - gap_half_width_px)
    x2 = min(cfg.length_per_env_pixels, center_x + gap_half_width_px)
    tile[x1:x2, :] = -gap_depth_units
    return _apply_roughness(tile, cfg, difficulty, seed)


def make_ramp_tile(
    cfg: Stage1TerrainCfg,
    difficulty: float,
    seed: int,
) -> np.ndarray:
    tile = np.zeros(
        (cfg.length_per_env_pixels, cfg.width_per_env_pixels),
        dtype=np.int16,
    )
    platform_px = _meters_to_pixels(cfg, 2.0)
    slope_start = 5
    plateau_start = int((cfg.length_per_env_pixels - platform_px) / 2)
    plateau_end = int((cfg.length_per_env_pixels + platform_px) / 2)
    height_per_px = max(1, 2 * int(difficulty * 7 + 1))

    if plateau_start > slope_start:
        xs = np.arange(slope_start, plateau_start)
        heights = (height_per_px * (xs - slope_start)).astype(np.int16)
        tile[slope_start:plateau_start, :] = heights[:, None]
        plateau_height = int(heights[-1])
    else:
        plateau_height = 0

    tile[plateau_start:plateau_end, :] = plateau_height

    tail_end = max(plateau_end + 1, cfg.length_per_env_pixels - 5)
    if tail_end > plateau_end:
        xs = np.arange(plateau_end, tail_end)
        descending = plateau_height - height_per_px * (xs - plateau_end)
        descending = np.clip(descending, a_min=0, a_max=None).astype(np.int16)
        tile[plateau_end:tail_end, :] = descending[:, None]

    return _apply_roughness(tile, cfg, difficulty, seed)


def make_beam_tile(
    cfg: Stage1TerrainCfg,
    difficulty: float,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    tile = np.full(
        (cfg.length_per_env_pixels, cfg.width_per_env_pixels),
        -max(1, _meters_to_height_units(cfg, 0.5)),
        dtype=np.int16,
    )
    beam_length_m = 1.0 if difficulty < 0.2 else -0.4 * difficulty + 0.9
    stone_distance_m = 0.1 if difficulty < 0.2 else 0.4 * int(10 * difficulty) / 10
    beam_length_px = _meters_to_pixels(cfg, beam_length_m)
    stone_distance_px = int(np.clip(_meters_to_pixels(cfg, stone_distance_m), 1, 5))
    platform_px = _meters_to_pixels(cfg, 2.0)
    max_height_units = max(1, _meters_to_height_units(cfg, 0.05 + 0.18 * difficulty))
    height_choices = np.arange(0, max_height_units + 1, 4, dtype=np.int16)
    if height_choices.size == 0:
        height_choices = np.array([0], dtype=np.int16)

    platform_y = cfg.width_per_env_pixels // 2 - platform_px // 2
    start_x_front = cfg.length_per_env_pixels // 2 - platform_px // 2 - 1
    while start_x_front >= 0:
        beam_width = int(rng.integers(15, 31))
        y1 = int(platform_y + platform_px / 2 - beam_width / 2)
        y1 = max(0, y1)
        y2 = min(cfg.width_per_env_pixels, y1 + beam_width)
        stop_x_front = max(0, start_x_front - beam_length_px)
        tile[stop_x_front:start_x_front, y1:y2] = rng.choice(height_choices)
        start_x_front -= beam_length_px + stone_distance_px

    start_x_back = cfg.length_per_env_pixels // 2 + platform_px // 2 + 1
    while start_x_back < cfg.length_per_env_pixels:
        beam_width = int(rng.integers(15, 31))
        y1 = int(platform_y + platform_px / 2 - beam_width / 2)
        y1 = max(0, y1)
        y2 = min(cfg.width_per_env_pixels, y1 + beam_width)
        stop_x_back = min(cfg.length_per_env_pixels, start_x_back + beam_length_px)
        tile[start_x_back:stop_x_back, y1:y2] = rng.choice(height_choices)
        start_x_back += beam_length_px + stone_distance_px

    center_x = cfg.length_per_env_pixels // 2 - platform_px // 2
    tile[center_x:center_x + platform_px, platform_y:platform_y + platform_px] = 0
    return _apply_roughness(tile, cfg, difficulty, seed + 1)


def make_pit_tile(
    cfg: Stage1TerrainCfg,
    difficulty: float,
    pit_depth: int = 20,
) -> np.ndarray:
    tile = np.zeros(
        (cfg.length_per_env_pixels, cfg.width_per_env_pixels),
        dtype=np.int16,
    )

    center_x = cfg.length_per_env_pixels // 2
    center_y = cfg.width_per_env_pixels // 2

    x1 = center_x - 10
    x2 = center_x + 10
    y1 = center_y - 10
    y2 = center_y + 10

    tile[x1:x2, y1:y2] = -int(pit_depth * difficulty)
    return tile


def get_terrain_idx_from_choice(cfg: Stage1TerrainCfg, choice: float) -> int:
    for idx, upper_bound in enumerate(cfg.terrain_proportions):
        if choice < upper_bound:
            return idx

    return len(cfg.terrain_proportions) - 1


def get_terrain_name_from_idx(cfg: Stage1TerrainCfg, terrain_idx: int) -> str:
    return cfg.terrain_names[terrain_idx]


def make_tile_by_name(
    cfg: Stage1TerrainCfg,
    terrain_name: str,
    difficulty: float,
    choice: float,
    seed: int,
) -> np.ndarray:
    if terrain_name == "slope down":
        descending = choice < cfg.terrain_proportions[0] / 2
        return make_slope_tile(cfg, difficulty, descending=descending)

    if terrain_name == "pyramid":
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
        return make_stairs_tile(
            cfg,
            difficulty,
            descending=True,
            step_width_m=0.5,
            extra_step_height_m=0.2,
        )

    if terrain_name == "pit":
        return make_pit_tile(cfg, difficulty)

    raise ValueError(f"Unsupported terrain name: {terrain_name}")


def make_tile_by_col(
    cfg: Stage1TerrainCfg,
    row: int,
    col: int,
) -> tuple[np.ndarray, int]:
    difficulty = row / cfg.num_rows
    choice = col / cfg.num_cols + 0.001
    terrain_idx = get_terrain_idx_from_choice(cfg, choice)
    terrain_name = get_terrain_name_from_idx(cfg, terrain_idx)
    seed = _tile_seed(cfg, row, col, terrain_idx)
    tile = make_tile_by_name(cfg, terrain_name, difficulty, choice, seed)
    return tile, terrain_idx

def get_origin_patch_center(
    cfg: Stage1TerrainCfg,
    terrain_name: str,
) -> tuple[int,int]:
    center_x = cfg.length_per_env_pixels //2
    center_y = cfg.width_per_env_pixels //2

    if terrain_name == "gap":
          return cfg.length_per_env_pixels // 4, center_y

    if terrain_name == "pit":
          return cfg.length_per_env_pixels // 4, center_y

    if terrain_name == "hurdle":
          return cfg.length_per_env_pixels // 4, center_y

    if terrain_name == "beam":
        return center_x, center_y

    return center_x, center_y

def get_origin_patch_radius(
      cfg: Stage1TerrainCfg,
      terrain_name: str,
  ) -> tuple[int, int]:
      if terrain_name in {"gap", "pit", "hurdle", "beam"}:
          return 6, 6

      if terrain_name in {"stairs down", "stairs up", "new stairs down"}:
          return 8, 8

      return 10, 10

def write_tile_to_map(
    data: Stage1TerrainData,
    tile: np.ndarray,
    row: int,
    col: int,
    terrain_idx: int,
    cfg: Stage1TerrainCfg,
) -> None:
    start_x = cfg.border_pixels + row * cfg.length_per_env_pixels
    end_x = start_x + cfg.length_per_env_pixels

    start_y = cfg.border_pixels + col * cfg.width_per_env_pixels
    end_y = start_y + cfg.width_per_env_pixels

    data.height_field_raw[start_x:end_x, start_y:end_y] = tile
    data.terrain_type[row, col] = terrain_idx


def set_tile_origin(
    data: Stage1TerrainData,
    row: int,
    col: int,
    terrain_name:str,
    cfg: Stage1TerrainCfg,
) -> None:
    center_x, center_y = get_origin_patch_center(cfg, terrain_name)

    origin_x = row * cfg.terrain_length + center_x * cfg.horizontal_scale
    origin_y = col * cfg.terrain_width + center_y * cfg.horizontal_scale

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
        cfg.border_pixels + row * cfg.length_per_env_pixels + x1:
        cfg.border_pixels + row * cfg.length_per_env_pixels + x2,
        cfg.border_pixels + col * cfg.width_per_env_pixels + y1:
        cfg.border_pixels + col * cfg.width_per_env_pixels + y2,
    ]
    origin_z = max(0.0,float(tile_center_patch.max()) * cfg.vertical_scale)

    data.env_origins[row, col] = [origin_x, origin_y, origin_z]


def build_stage1_map(cfg: Stage1TerrainCfg | None = None) -> Stage1TerrainData:
    if cfg is None:
        cfg = Stage1TerrainCfg()

    data = create_empty_stage1_terrain_data(cfg)

    for row in range(cfg.num_rows):
        for col in range(cfg.num_cols):
            tile, terrain_idx = make_tile_by_col(cfg, row, col)
            terrain_name = get_terrain_name_from_idx(cfg,terrain_idx)
            write_tile_to_map(data, tile, row=row, col=col, terrain_idx=terrain_idx, cfg=cfg)
            set_tile_origin(data, row=row, col=col, terrain_name=terrain_name,cfg=cfg)
    # Mesh data will be filled in a later step after heightfield generation is complete.
    return data

##二维高度数据”转换为“三维三角形网格模型”
def convert_heightfield_to_trimesh(
    height_field_raw:np.ndarray,
    horizontal_scale:float,
    vertical_scale:float,
    slope_threshold: float | None =None,
) ->tuple[np.ndarray,np.ndarray,np.ndarray]:
    hf = height_field_raw
    num_rows = hf.shape[0]
    num_cols = hf.shape[1]

    y= np.linspace(0,(num_cols -1)*horizontal_scale,num_cols)
    x= np.linspace(0,(num_rows -1)* horizontal_scale,num_rows)
    yy,xx = np.meshgrid(y,x)

    if slope_threshold is not None:
        slope_threshold *= horizontal_scale /vertical_scale

        move_x = np.zeros((num_rows,num_cols))
        move_y = np.zeros((num_rows,num_cols))
        move_corners = np.zeros((num_rows,num_cols))

        move_x[: num_rows - 1, :] += (
            hf[1:num_rows, :] - hf[: num_rows - 1, :] > slope_threshold
        )
        move_x[1:num_rows, :] -= (
            hf[: num_rows - 1, :] - hf[1:num_rows, :] > slope_threshold
        )

        move_y[:, : num_cols - 1] += (
            hf[:, 1:num_cols] - hf[:, : num_cols - 1] > slope_threshold
        )
        move_y[:, 1:num_cols] -= (
            hf[:, : num_cols - 1] - hf[:, 1:num_cols] > slope_threshold
        )

        move_corners[: num_rows - 1, : num_cols - 1] += (
            hf[1:num_rows, 1:num_cols] - hf[: num_rows - 1, : num_cols - 1] >slope_threshold
        )
        move_corners[1:num_rows, 1:num_cols] -= (
            hf[: num_rows - 1, : num_cols - 1] - hf[1:num_rows, 1:num_cols] >slope_threshold
        )

        xx += (move_x + move_corners * (move_x == 0)) * horizontal_scale
        yy += (move_y + move_corners * (move_y == 0)) * horizontal_scale
    else:
        move_x = np.zeros((num_rows, num_cols))

    vertices = np.zeros((num_rows * num_cols, 3), dtype=np.float32)
    vertices[:, 0] = xx.flatten()
    vertices[:, 1] = yy.flatten()
    vertices[:, 2] = hf.flatten() * vertical_scale

    triangles = -np.ones(
        (2 * (num_rows - 1) * (num_cols - 1), 3),
          dtype=np.uint32,
      )

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

        triangles[start + 1:stop:2, 0] = ind0
        triangles[start + 1:stop:2, 1] = ind2
        triangles[start + 1:stop:2, 2] = ind3

    return vertices, triangles, move_x != 0    

def convert_heightfield_to_mesh(
    data: Stage1TerrainData,
    cfg: Stage1TerrainCfg,
) -> Stage1TerrainData:
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



def build_stage1_terrain_data(
    cfg: Stage1TerrainCfg | None = None,
) -> Stage1TerrainData:
    if cfg is None:
        cfg = Stage1TerrainCfg()

    data = build_stage1_map(cfg)
    data = convert_heightfield_to_mesh(data, cfg)
    return data
