"""Dry-run checks for Stage1Eval metric formulas."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import torch


REPO_ROOT = Path(__file__).resolve().parents[2]
STAGE1_EVAL_PATH = (
    REPO_ROOT
    / "RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/mdp/stage1_eval.py"
)
DISTRIBUTION_PATH = (
    REPO_ROOT
    / "RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car/rsl_rl/modules/distribution.py"
)


def _load_stage1_eval_module():
    spec = importlib.util.spec_from_file_location("stage1_eval", STAGE1_EVAL_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_distribution_module():
    spec = importlib.util.spec_from_file_location("distribution", DISTRIBUTION_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    stage1_eval = _load_stage1_eval_module()
    distribution = _load_distribution_module()

    terrain_types = torch.tensor([0, 1, 2, 9], dtype=torch.long)
    terrain_levels = torch.tensor([2, 3, 4, 5], dtype=torch.float32)
    forward_x = torch.tensor([6.0, 4.0, 2.0, 1.0])
    rows_advanced = torch.tensor([2.0, 1.0, 0.0, 0.0])
    max_row_reached_mask = torch.tensor([False, False, False, False])
    valid_target_masked = torch.tensor([False, False, False, False])
    tile_start_x = torch.tensor([0.0, 0.0, 0.0, 0.0])
    tile_origin_x = torch.tensor([4.0, 4.0, 4.0, 4.0])
    tile_end_x = torch.tensor([8.0, 8.0, 8.0, 8.0])
    root_x = forward_x.clone()
    target_x = torch.tensor([8.0, 8.0, 8.0, 8.0])
    far_mask = torch.tensor([False, True, False, False])
    ball_limit_mask = torch.tensor([False, False, True, False])
    timeout_mask = torch.tensor([False, False, True, False])
    base_lin_vel = torch.tensor(
        [
            [1.18, 0.01, 0.0],
            [0.05, 0.20, 0.0],
            [-0.20, 0.01, 0.0],
            [0.02, 0.10, 0.0],
        ],
        dtype=torch.float32,
    )
    base_ang_vel = torch.tensor(
        [
            [0.0, 0.0, 0.01],
            [0.0, 0.0, 0.20],
            [0.0, 0.0, -0.30],
            [0.0, 0.0, 0.40],
        ],
        dtype=torch.float32,
    )
    wheel_longitudinal_slip = torch.tensor(
        [
            [3.0, 3.0, 3.0, 3.0, 3.0, 3.0],
            [1.2, 1.2, 1.2, 1.2, 1.2, 1.2],
            [0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
            [0.5, 0.5, 0.5, 0.5, 0.5, 2.0],
        ],
        dtype=torch.float32,
    )
    wheel_slip_angle = torch.tensor(
        [
            [0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
            [0.10, 0.10, 0.10, 0.10, 0.10, 0.10],
            [0.10, 0.10, 0.10, 0.10, 0.10, 0.10],
            [0.40, 0.40, 0.40, 0.40, 0.40, 0.40],
        ],
        dtype=torch.float32,
    )
    wheel_normal_contact_force = torch.tensor(
        [
            [0.20, 0.20, 0.20, 0.20, 0.20, 0.20],
            [0.00, 0.02, 0.03, 0.04, 0.05, 0.06],
            [0.10, 0.10, 0.10, 0.10, 0.10, 0.10],
            [0.00, 0.00, 0.00, 0.10, 0.10, 0.10],
        ],
        dtype=torch.float32,
    )
    roll_deg = torch.tensor([1.0, 16.0, 1.0, 1.0])
    pitch_deg = torch.tensor([1.0, 1.0, 21.0, 1.0])
    ball_joint_limit_usage = torch.tensor(
        [
            [0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
            [0.95, 0.2, 0.2, 0.2, 0.2, 0.2],
            [0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
            [0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
        ],
        dtype=torch.float32,
    )
    actions = torch.tensor(
        [
            [0.10, 0.20, 0.00, 0.00],
            [0.96, 0.10, 0.00, 0.00],
            [0.20, 0.20, 0.00, 0.00],
            [0.30, 0.20, 0.00, 0.00],
        ],
        dtype=torch.float32,
    )
    last_actions = torch.zeros_like(actions)
    active_waypoint_distance = torch.tensor([2.0, 2.0, 2.0, 2.0])

    metrics = stage1_eval.compute_stage1_eval_metrics(
        terrain_types=terrain_types,
        terrain_levels=terrain_levels,
        forward_x_from_current_tile_start=forward_x,
        rows_advanced=rows_advanced,
        max_row_reached_mask=max_row_reached_mask,
        valid_target_masked=valid_target_masked,
        tile_start_x=tile_start_x,
        tile_origin_x=tile_origin_x,
        tile_end_x=tile_end_x,
        root_x=root_x,
        target_x=target_x,
        far_mask=far_mask,
        ball_joint_limit_mask=ball_limit_mask,
        timeout_mask=timeout_mask,
        base_lin_vel=base_lin_vel,
        base_ang_vel=base_ang_vel,
        wheel_longitudinal_slip=wheel_longitudinal_slip,
        wheel_slip_angle=wheel_slip_angle,
        wheel_normal_contact_force=wheel_normal_contact_force,
        roll_deg=roll_deg,
        pitch_deg=pitch_deg,
        ball_joint_limit_usage=ball_joint_limit_usage,
        actions=actions,
        last_actions=last_actions,
        active_waypoint_distance=active_waypoint_distance,
        terrain_length=8.0,
    )

    assert math.isclose(metrics["Stage1Eval/flat/rows_advanced_mean"], 2.0)
    assert math.isclose(metrics["Stage1Eval/flat/row_advance_rate"], 1.0)
    flat_ratio = 0.01 / (1.18 + 0.1)
    expected_retention = 0.30 + 0.25 + 0.20 + 0.10 * (1.0 - flat_ratio / 0.20) + 0.10 + 0.05
    assert math.isclose(metrics["Stage1Eval/flat/retention_score"], expected_retention, rel_tol=1.0e-5)

    expected_col1_difficulty = 0.35 * 0.5 + 0.20 + 0.15 + 0.10 + 0.10 + 0.05 + 0.05
    assert math.isclose(
        metrics["Stage1Eval/col01_slope_down/difficulty_score"],
        expected_col1_difficulty,
        rel_tol=1.0e-6,
    )
    assert metrics["Stage1Eval/global/hardest_col_index"] == 1.0
    assert math.isclose(metrics["Stage1Eval/global/hardest_col_difficulty_score"], expected_col1_difficulty)

    assert metrics["Stage1Eval/col03_rough/rows_advanced_mean"] == 0.0
    assert metrics["Stage1Eval/col03_rough/difficulty_score"] == 0.0
    assert not any(not math.isfinite(value) for value in metrics.values())

    masked_metrics = stage1_eval.compute_stage1_eval_metrics(
        terrain_types=terrain_types,
        terrain_levels=terrain_levels,
        forward_x_from_current_tile_start=forward_x,
        rows_advanced=rows_advanced,
        max_row_reached_mask=max_row_reached_mask,
        valid_target_masked=valid_target_masked,
        tile_start_x=tile_start_x,
        tile_origin_x=tile_origin_x,
        tile_end_x=tile_end_x,
        root_x=root_x,
        target_x=target_x,
        far_mask=far_mask,
        ball_joint_limit_mask=ball_limit_mask,
        timeout_mask=timeout_mask,
        base_lin_vel=base_lin_vel,
        base_ang_vel=base_ang_vel,
        wheel_longitudinal_slip=wheel_longitudinal_slip,
        wheel_slip_angle=wheel_slip_angle,
        wheel_normal_contact_force=wheel_normal_contact_force,
        roll_deg=roll_deg,
        pitch_deg=pitch_deg,
        ball_joint_limit_usage=ball_joint_limit_usage,
        actions=actions,
        last_actions=last_actions,
        active_waypoint_distance=active_waypoint_distance,
        terrain_length=8.0,
        train_active_mask=torch.tensor([True, False, True, True]),
    )
    assert masked_metrics["Stage1Eval/global/env_count"] == 3.0
    assert math.isclose(
        masked_metrics["Stage1Eval/global/current_level_mean"],
        (2.0 + 4.0 + 5.0) / 3.0,
        rel_tol=1.0e-6,
    )
    assert masked_metrics["Stage1Eval/col01_slope_down/env_count"] == 0.0
    assert masked_metrics["Stage1Eval/col01_slope_down/difficulty_score"] == 0.0

    squashed = distribution.SquashedGaussianDistribution(2, init_std=0.2, log_std_min=-4.0, log_std_max=0.0)
    squashed.update(torch.tensor([[float("nan"), float("inf")]], dtype=torch.float32))
    assert torch.isfinite(squashed.mean).all()
    assert torch.isfinite(squashed.std).all()
    assert torch.all(squashed.std > 0.0)

    gaussian = distribution.GaussianDistribution(2, init_std=0.2)
    with torch.no_grad():
        gaussian.std_param[0] = float("nan")
        gaussian.std_param[1] = -1.0
    gaussian.update(torch.tensor([[float("nan"), float("-inf")]], dtype=torch.float32))
    assert torch.isfinite(gaussian.mean).all()
    assert torch.isfinite(gaussian.std).all()
    assert torch.all(gaussian.std > 0.0)

    hetero = distribution.HeteroscedasticGaussianDistribution(2, init_std=0.2, std_type="log")
    hetero.update(
        torch.tensor(
            [
                [
                    [float("nan"), float("inf")],
                    [float("-inf"), float("nan")],
                ]
            ],
            dtype=torch.float32,
        )
    )
    assert torch.isfinite(hetero.mean).all()
    assert torch.isfinite(hetero.std).all()
    assert torch.all(hetero.std > 0.0)


if __name__ == "__main__":
    main()
