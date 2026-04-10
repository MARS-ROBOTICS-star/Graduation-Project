# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Terrain generation and runtime helpers for direct complete-car tasks."""

from .terrain_generator import (
    STAGE1_TERRAIN_CLASS_GAP,
    STAGE1_TERRAIN_CLASS_OTHER,
    STAGE1_TERRAIN_CLASS_STEP,
    Stage1TerrainCfg,
    Stage1TerrainData,
    build_stage1_terrain_data,
    convert_heightfield_to_mesh,
    convert_heightfield_to_trimesh,
    get_origin_patch_center,
    get_origin_patch_radius,
    get_terrain_idx_from_choice,
    get_terrain_name_from_idx,
    make_tile_by_col,
    make_tile_by_name,
)
from .terrain_runtime import CompleteCarTerrainRuntime, CompleteCarTerrainRuntimeCfg

__all__ = [
    "CompleteCarTerrainRuntime",
    "CompleteCarTerrainRuntimeCfg",
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
