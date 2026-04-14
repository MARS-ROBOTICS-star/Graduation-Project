"""域随机化辅助逻辑。"""

from __future__ import annotations

import torch

from ..utils.math_utils import sample_uniform_tensor


def sample_motor_strength(cfg, env_ids: torch.Tensor, action_dim: int, device: torch.device) -> torch.Tensor:
    strength = torch.ones((env_ids.numel(), action_dim), device=device)
    if cfg.randomization.enable_action_randomization and cfg.randomization.randomize_motor_strength:
        strength = sample_uniform_tensor(cfg.randomization.motor_strength_range, (env_ids.numel(), action_dim), device)
    return strength


def apply_joint_position_noise(cfg, joint_pos: torch.Tensor) -> torch.Tensor:
    if cfg.randomization.joint_position_noise_scale <= 0.0:
        return joint_pos
    return joint_pos + torch.randn_like(joint_pos) * cfg.randomization.joint_position_noise_scale
