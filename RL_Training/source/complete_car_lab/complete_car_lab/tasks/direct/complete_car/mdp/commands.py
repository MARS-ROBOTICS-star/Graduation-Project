"""Goal-conditioned command sampling and relative-goal conversion."""

from __future__ import annotations

import math

import torch

from ..utils.math_utils import wrap_to_pi_tensor, world_xy_to_body_xy


def resample_goal_commands(
    command_targets_w: torch.Tensor,
    command_time_left: torch.Tensor,
    env_ids: torch.Tensor,
    base_pos_xy_w: torch.Tensor,
    base_yaw_w: torch.Tensor,
    cfg,
) -> tuple[torch.Tensor, torch.Tensor]:
    if env_ids.numel() == 0:
        empty = torch.empty(0, device=command_targets_w.device, dtype=command_targets_w.dtype)
        return empty, empty

    device = command_targets_w.device
    dtype = command_targets_w.dtype
    num_envs = env_ids.numel()

    goal_direction_max = math.radians(cfg.goal_direction_max_deg)
    goal_heading_delta_max = math.radians(cfg.goal_direction_max_deg/2)

    u = torch.rand(num_envs, device=device, dtype=dtype) #[0,1)均匀分布
    signs = torch.where(
        torch.rand(num_envs, device=device) < 0.5,
        -torch.ones(num_envs, device=device, dtype=dtype),
        torch.ones(num_envs, device=device, dtype=dtype),
    ) #以 50% 的概率生成 +1 或 -1

    phi = signs * goal_direction_max * torch.sqrt(u)# 使用 phi = s * phi_max * sqrt(u) 实现边缘强化采样。
    theta_los = wrap_to_pi_tensor(base_yaw_w + phi) #目标点在世界坐标系下的绝对方位角
    delta = torch.empty(num_envs, device=device, dtype=dtype).uniform_(-goal_heading_delta_max, goal_heading_delta_max)#生成目标航向的随机偏差 delta
    psi_target = wrap_to_pi_tensor(theta_los + delta) #计算最终要求小车到达目标点时的车头朝向 psi

    command_targets_w[env_ids, 0] = base_pos_xy_w[:, 0] + cfg.goal_distance * torch.cos(theta_los)
    command_targets_w[env_ids, 1] = base_pos_xy_w[:, 1] + cfg.goal_distance * torch.sin(theta_los)
    command_targets_w[env_ids, 2] = psi_target
    # 按概率让一部分小车的目标点就是它当前的位置，让它们练习“原地保持不动”.
    if cfg.rel_standing_envs > 0.0:
        standing_mask = torch.rand(num_envs, device=device) < cfg.rel_standing_envs
        if torch.any(standing_mask):
            command_targets_w[env_ids[standing_mask], 0] = base_pos_xy_w[standing_mask, 0]
            command_targets_w[env_ids[standing_mask], 1] = base_pos_xy_w[standing_mask, 1]
            command_targets_w[env_ids[standing_mask], 2] = base_yaw_w[standing_mask]
            phi = torch.where(standing_mask, torch.zeros_like(phi), phi)
            delta = torch.where(standing_mask, torch.zeros_like(delta), delta)
    # 强制所有小车的目标点设为当前位置
    if cfg.zero_command:
        command_targets_w[env_ids, 0] = base_pos_xy_w[:, 0]
        command_targets_w[env_ids, 1] = base_pos_xy_w[:, 1]
        command_targets_w[env_ids, 2] = base_yaw_w
        phi.zero_()
        delta.zero_()

    command_time_left[env_ids] = cfg.resampling_time
    return phi, delta

# 计算在小车坐标系下的目标及朝向
def compute_relative_goal_commands(
    command_targets_w: torch.Tensor,
    base_pos_xy_w: torch.Tensor,
    base_yaw_w: torch.Tensor,
) -> torch.Tensor:
    delta_xy_w = command_targets_w[:, :2] - base_pos_xy_w
    relative_xy_b = world_xy_to_body_xy(delta_xy_w, base_yaw_w)
    relative_yaw = wrap_to_pi_tensor(command_targets_w[:, 2] - base_yaw_w)
    return torch.cat((relative_xy_b, relative_yaw.unsqueeze(-1)), dim=-1)


def step_command_timer(command_time_left: torch.Tensor, step_dt: float) -> torch.Tensor:
    command_time_left -= step_dt
    return torch.nonzero(command_time_left <= 0.0, as_tuple=False).flatten()
