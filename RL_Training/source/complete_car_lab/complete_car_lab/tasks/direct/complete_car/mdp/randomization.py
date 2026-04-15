"""域随机化辅助逻辑。"""

from __future__ import annotations

import torch

def apply_joint_position_noise(cfg, joint_pos: torch.Tensor) -> torch.Tensor:
    if cfg.randomization.joint_position_noise_scale <= 0.0:
        return joint_pos
    return joint_pos + torch.randn_like(joint_pos) * cfg.randomization.joint_position_noise_scale
