"""Dry-run checks for rollout train-mask filtering."""

from __future__ import annotations

import sys
from pathlib import Path

import torch
from tensordict import TensorDict


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = (
    REPO_ROOT
    / "RL_Training/source/complete_car_lab/complete_car_lab/tasks/direct/complete_car"
)
sys.path.insert(0, str(PACKAGE_ROOT))

from rsl_rl.storage.rollout_storage import RolloutStorage  # noqa: E402


def main() -> None:
    num_envs = 4
    num_steps = 2
    action_dim = 2
    obs = TensorDict(
        {
            "actor": torch.zeros(num_envs, 2),
            "critic": torch.zeros(num_envs, 3),
        },
        batch_size=[num_envs],
    )
    storage = RolloutStorage("rl", num_envs, num_steps, obs, [action_dim], device="cpu")

    active_mask = torch.tensor([True, False, True, False])
    for step in range(num_steps):
        transition = RolloutStorage.Transition()
        env_ids = torch.arange(num_envs, dtype=torch.float32)
        transition.observations = TensorDict(
            {
                "actor": torch.stack((env_ids + step * 10.0, torch.zeros_like(env_ids)), dim=1),
                "critic": torch.zeros(num_envs, 3),
            },
            batch_size=[num_envs],
        )
        transition.actions = torch.zeros(num_envs, action_dim)
        transition.rewards = torch.ones(num_envs)
        transition.dones = torch.zeros(num_envs)
        transition.train_mask = active_mask
        transition.values = torch.zeros(num_envs, 1)
        transition.actions_log_prob = torch.zeros(num_envs, 1)
        transition.distribution_params = (
            torch.zeros(num_envs, action_dim),
            torch.ones(num_envs, action_dim),
        )
        storage.add_transition(transition)

    storage.returns.copy_(storage.values)
    storage.advantages.fill_(1.0)
    total_samples = 0
    seen_actor_ids: list[float] = []
    for batch in storage.mini_batch_generator(num_mini_batches=3, num_epochs=1):
        actor_first_dim = batch.observations["actor"][:, 0]
        total_samples += int(actor_first_dim.numel())
        seen_actor_ids.extend(actor_first_dim.tolist())

    assert total_samples == num_steps * int(active_mask.sum().item())
    assert set(seen_actor_ids) == {0.0, 2.0, 10.0, 12.0}


if __name__ == "__main__":
    main()
