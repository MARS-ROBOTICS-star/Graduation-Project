# Copyright (c) 2021-2026, ETH Zurich and NVIDIA CORPORATION
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause


from __future__ import annotations

import torch
import torch.nn as nn
from torch.distributions import Normal


_MIN_STD = 1.0e-6


def _finite_tensor(value: torch.Tensor, *, posinf: float = 0.0, neginf: float = 0.0) -> torch.Tensor:
    return torch.nan_to_num(value, nan=0.0, posinf=posinf, neginf=neginf)


def _positive_std(value: torch.Tensor, min_std: float = _MIN_STD) -> torch.Tensor:
    return _finite_tensor(value, posinf=1.0 / min_std, neginf=min_std).clamp_min(min_std)


class Distribution(nn.Module):
    """Base class for distribution modules.

    Distribution modules encapsulate the stochastic output of a neural model. They define the output structure expected
    from the MLP, manage learnable distribution parameters, and provide methods for sampling, log probability
    computation, and entropy calculation.

    Subclasses must implement all abstract methods and properties to define a specific distribution type.
    """

    def __init__(self, output_dim: int) -> None:
        """Initialize the distribution module.

        Args:
            output_dim: Dimension of the action/output space.
        """
        super().__init__()
        self.output_dim = output_dim

    def update(self, mlp_output: torch.Tensor) -> None:
        """Update the distribution parameters given the MLP output.

        Args:
            mlp_output: Raw output from the MLP.
        """
        raise NotImplementedError

    def sample(self) -> torch.Tensor:
        """Sample from the distribution.

        Returns:
            Sampled values.
        """
        raise NotImplementedError

    def deterministic_output(self, mlp_output: torch.Tensor) -> torch.Tensor:
        """Extract the deterministic (mean) output from the raw MLP output.

        Args:
            mlp_output: Raw output from the MLP.

        Returns:
            The deterministic output (typically the distribution mean).
        """
        raise NotImplementedError

    def as_deterministic_output_module(self) -> nn.Module:
        """Return an export-friendly module that extracts the deterministic output from the MLP output."""
        raise NotImplementedError

    @property
    def input_dim(self) -> int | list[int]:
        """Return the input dimension required by the distribution."""
        raise NotImplementedError

    @property
    def mean(self) -> torch.Tensor:
        """Return the mean of the distribution."""
        raise NotImplementedError

    @property
    def std(self) -> torch.Tensor:
        """Return the standard deviation (or spread measure) of the distribution."""
        raise NotImplementedError

    @property
    def entropy(self) -> torch.Tensor:
        """Return the entropy of the distribution, summed over the last dimension."""
        raise NotImplementedError

    @property
    def params(self) -> tuple[torch.Tensor, ...]:
        """Return the distribution parameters as a tuple of tensors.

        These are the distribution-specific parameters needed to reconstruct the distribution (e.g., mean and std for
        Gaussian, alpha and beta for Beta). They are stored during rollouts and used for KL divergence computation.
        """
        raise NotImplementedError

    def log_prob(self, outputs: torch.Tensor) -> torch.Tensor:
        """Compute the log probability of the given outputs, summed over the last dimension.

        Args:
            outputs: Values to compute the log probability for.

        Returns:
            Log probability summed over the last dimension.
        """
        raise NotImplementedError

    def kl_divergence(self, old_params: tuple[torch.Tensor, ...], new_params: tuple[torch.Tensor, ...]) -> torch.Tensor:
        """Compute the KL divergence KL(old || new) between two distributions of this type.

        The KL divergence measures how the old distribution diverges from the new distribution.
        This is used for adaptive learning rate scheduling in policy optimization.

        Args:
            old_params: Parameters of the old distribution (as returned by :attr:`params`).
            new_params: Parameters of the new distribution (as returned by :attr:`params`).

        Returns:
            KL divergence summed over the last dimension.
        """
        raise NotImplementedError

    def init_mlp_weights(self, mlp: nn.Module) -> None:
        """Initialize distribution-specific weights in the MLP.

        This is called after MLP creation to set up any special weight initialization
        required by the distribution (e.g., initializing std head weights).

        Args:
            mlp: The MLP module whose weights may need initialization.
        """
        pass


class GaussianDistribution(Distribution):
    """Gaussian (Normal) distribution module with state-independent standard deviation.

    This distribution parameterizes actions using a multivariate Gaussian with diagonal covariance. The standard
    deviation is a learnable parameter that is independent of the model input. It can be parameterized in either
    "scalar" space (directly) or "log" space.
    """

    def __init__(
        self,
        output_dim: int,
        init_std: float = 1.0,
        std_type: str = "scalar",
    ) -> None:
        """Initialize the Gaussian distribution module.

        Args:
            output_dim: Dimension of the action/output space.
            init_std: Initial standard deviation.
            std_type: Parameterization of the standard deviation: "scalar" or "log".
        """
        super().__init__(output_dim)
        self.std_type = std_type

        # Learnable std parameters
        if std_type == "scalar":
            self.std_param = nn.Parameter(init_std * torch.ones(output_dim))
        elif std_type == "log":
            self.log_std_param = nn.Parameter(torch.log(init_std * torch.ones(output_dim)))
        else:
            raise ValueError(f"Unknown standard deviation type: {std_type}. Should be 'scalar' or 'log'.")

        # Internal torch distribution (populated by update())
        self._distribution: Normal | None = None

        # Disable args validation for speedup
        Normal.set_default_validate_args(False)

    def update(self, mlp_output: torch.Tensor) -> None:
        """Update the Gaussian distribution from MLP output."""
        mean = _finite_tensor(mlp_output)
        if self.std_type == "scalar":
            safe_std_param = _positive_std(self.std_param)
            if not torch.equal(safe_std_param, self.std_param):
                with torch.no_grad():
                    self.std_param.copy_(safe_std_param)
            std = safe_std_param.expand_as(mean)
        elif self.std_type == "log":
            safe_log_std_param = _finite_tensor(self.log_std_param)
            if not torch.equal(safe_log_std_param, self.log_std_param):
                with torch.no_grad():
                    self.log_std_param.copy_(safe_log_std_param)
            std = _positive_std(torch.exp(safe_log_std_param)).expand_as(mean)
        self._distribution = Normal(mean, std)

    def sample(self) -> torch.Tensor:
        """Sample from the Gaussian distribution."""
        return self._distribution.sample()  # type: ignore

    def deterministic_output(self, mlp_output: torch.Tensor) -> torch.Tensor:
        """Extract the mean from the MLP output."""
        return _finite_tensor(mlp_output)

    def as_deterministic_output_module(self) -> nn.Module:
        """Return an export-friendly module that extracts the mean from the MLP output."""
        return _IdentityDeterministicOutput()

    @property
    def input_dim(self) -> int:
        """Return the input dimension required by the distribution."""
        return self.output_dim

    @property
    def mean(self) -> torch.Tensor:
        """Return the mean of the Gaussian distribution."""
        return self._distribution.mean  # type: ignore

    @property
    def std(self) -> torch.Tensor:
        """Return the standard deviation of the Gaussian distribution."""
        return self._distribution.stddev  # type: ignore

    @property
    def entropy(self) -> torch.Tensor:
        """Return the entropy of the Gaussian distribution, summed over the last dimension."""
        return self._distribution.entropy().sum(dim=-1)  # type: ignore

    @property
    def params(self) -> tuple[torch.Tensor, ...]:
        """Return (mean, std) of the current Gaussian distribution."""
        return (self.mean, self.std)

    def log_prob(self, outputs: torch.Tensor) -> torch.Tensor:
        """Compute the log probability under the Gaussian, summed over the last dimension."""
        return self._distribution.log_prob(_finite_tensor(outputs)).sum(dim=-1)  # type: ignore

    def kl_divergence(self, old_params: tuple[torch.Tensor, ...], new_params: tuple[torch.Tensor, ...]) -> torch.Tensor:
        """Compute KL(old || new) between two Gaussian distributions using torch.distributions."""
        old_mean, old_std = old_params
        new_mean, new_std = new_params
        old_mean = _finite_tensor(old_mean)
        new_mean = _finite_tensor(new_mean)
        old_std = _positive_std(old_std)
        new_std = _positive_std(new_std)
        old_dist = Normal(old_mean, old_std)
        new_dist = Normal(new_mean, new_std)
        return torch.distributions.kl_divergence(old_dist, new_dist).sum(dim=-1)


class SquashedGaussianDistribution(Distribution):
    """Tanh-squashed diagonal Gaussian with state-independent log standard deviation."""

    def __init__(
        self,
        output_dim: int,
        init_std: float = 1.0,
        log_std_min: float = -5.0,
        log_std_max: float = 2.0,
        squash_epsilon: float = 1e-6,
    ) -> None:
        super().__init__(output_dim)
        self.log_std_min = log_std_min
        self.log_std_max = log_std_max
        self.squash_epsilon = squash_epsilon

        init_std_tensor = torch.full((output_dim,), init_std, dtype=torch.float32)
        init_log_std = torch.log(torch.clamp(init_std_tensor, min=squash_epsilon))
        self.log_std_param = nn.Parameter(init_log_std)

        self._distribution: Normal | None = None
        self._base_mean: torch.Tensor | None = None
        self._base_std: torch.Tensor | None = None
        self._warned_invalid_mean = False
        self._warned_invalid_log_std = False

        Normal.set_default_validate_args(False)

    def update(self, mlp_output: torch.Tensor) -> None:
        """Update the base Gaussian before tanh squashing."""
        safe_mean = _finite_tensor(mlp_output, posinf=1.0, neginf=-1.0)
        if not torch.equal(safe_mean, mlp_output) and not self._warned_invalid_mean:
            print("[WARN] SquashedGaussianDistribution received non-finite action mean; sanitizing values.", flush=True)
            self._warned_invalid_mean = True
        self._base_mean = safe_mean

        safe_log_std_param = torch.nan_to_num(
            self.log_std_param,
            nan=0.0,
            posinf=self.log_std_max,
            neginf=self.log_std_min,
        )
        if not torch.equal(safe_log_std_param, self.log_std_param) and not self._warned_invalid_log_std:
            print(
                "[WARN] SquashedGaussianDistribution received non-finite log_std parameters; clamping values.",
                flush=True,
            )
            self._warned_invalid_log_std = True
        if not torch.equal(safe_log_std_param, self.log_std_param):
            with torch.no_grad():
                self.log_std_param.copy_(safe_log_std_param)

        clamped_log_std = torch.clamp(safe_log_std_param, min=self.log_std_min, max=self.log_std_max)
        self._base_std = _positive_std(torch.exp(clamped_log_std), self.squash_epsilon).expand_as(self._base_mean)
        self._distribution = Normal(self._base_mean, self._base_std)

    def sample(self) -> torch.Tensor:
        """Sample from the base Gaussian and squash into (-1, 1)."""
        return torch.tanh(self._distribution.sample())  # type: ignore[arg-type]

    def deterministic_output(self, mlp_output: torch.Tensor) -> torch.Tensor:
        """Return the squashed mean action for deterministic inference."""
        return torch.tanh(_finite_tensor(mlp_output, posinf=1.0, neginf=-1.0))

    def as_deterministic_output_module(self) -> nn.Module:
        """Return export-friendly module that applies tanh to the mean."""
        return _TanhDeterministicOutput()

    @property
    def input_dim(self) -> int:
        """Return the input dimension required by the distribution."""
        return self.output_dim

    @property
    def mean(self) -> torch.Tensor:
        """Return the squashed mean action."""
        return torch.tanh(_finite_tensor(self._base_mean))  # type: ignore[arg-type]

    @property
    def std(self) -> torch.Tensor:
        """Return the base Gaussian standard deviation."""
        return self._base_std  # type: ignore[return-value]

    @property
    def entropy(self) -> torch.Tensor:
        """Return the base Gaussian entropy as the exploration proxy."""
        return self._distribution.entropy().sum(dim=-1)  # type: ignore[union-attr]

    @property
    def params(self) -> tuple[torch.Tensor, ...]:
        """Return the base Gaussian parameters for KL computation."""
        return (self._base_mean, self._base_std)  # type: ignore[return-value]

    def log_prob(self, outputs: torch.Tensor) -> torch.Tensor:
        """Compute exact log-probability with tanh change-of-variables correction."""
        clipped_outputs = torch.clamp(
            _finite_tensor(outputs),
            -1.0 + self.squash_epsilon,
            1.0 - self.squash_epsilon,
        )
        unsquashed_outputs = torch.atanh(clipped_outputs)
        log_prob = self._distribution.log_prob(unsquashed_outputs).sum(dim=-1)  # type: ignore[union-attr]
        log_det_jacobian = torch.log(1.0 - clipped_outputs.pow(2) + self.squash_epsilon).sum(dim=-1)
        return log_prob - log_det_jacobian

    def kl_divergence(self, old_params: tuple[torch.Tensor, ...], new_params: tuple[torch.Tensor, ...]) -> torch.Tensor:
        """KL is computed in the pre-squash Gaussian space."""
        old_mean, old_std = old_params
        new_mean, new_std = new_params
        old_mean = _finite_tensor(old_mean)
        new_mean = _finite_tensor(new_mean)
        old_std = _positive_std(old_std, self.squash_epsilon)
        new_std = _positive_std(new_std, self.squash_epsilon)
        old_dist = Normal(old_mean, old_std)
        new_dist = Normal(new_mean, new_std)
        return torch.distributions.kl_divergence(old_dist, new_dist).sum(dim=-1)


class HeteroscedasticGaussianDistribution(GaussianDistribution):
    """Gaussian (Normal) distribution module with state-dependent standard deviation.

    This distribution parameterizes actions using a multivariate Gaussian with diagonal covariance. The standard
    deviation is output by the MLP alongside the mean, making it state-dependent (heteroscedastic). It can be
    parameterized in either "scalar" space (directly) or "log" space.
    """

    def __init__(
        self,
        output_dim: int,
        init_std: float = 1.0,
        std_type: str = "scalar",
    ) -> None:
        """Initialize the heteroscedastic Gaussian distribution module.

        Args:
            output_dim: Dimension of the action/output space.
            init_std: Initial standard deviation (used to initialize MLP std head bias).
            std_type: Parameterization of the standard deviation: "scalar" or "log".
        """
        # Skip GaussianDistribution.__init__ to avoid creating unnecessary learnable std parameters.
        Distribution.__init__(self, output_dim)
        self.std_type = std_type
        self.init_std = init_std

        if std_type not in ("scalar", "log"):
            raise ValueError(f"Unknown standard deviation type: {std_type}. Should be 'scalar' or 'log'.")

        # Internal torch distribution (populated by update())
        self._distribution: Normal | None = None

        # Disable args validation for speedup
        Normal.set_default_validate_args(False)

    def update(self, mlp_output: torch.Tensor) -> None:
        """Update the Gaussian distribution from MLP output."""
        if self.std_type == "scalar":
            mean, std = torch.unbind(mlp_output, dim=-2)
        elif self.std_type == "log":
            mean, log_std = torch.unbind(mlp_output, dim=-2)
            std = torch.exp(_finite_tensor(log_std))
        mean = _finite_tensor(mean)
        std = _positive_std(std)
        self._distribution = Normal(mean, std)

    def deterministic_output(self, mlp_output: torch.Tensor) -> torch.Tensor:
        """Extract the mean from the MLP output (first slice of the second-to-last dimension)."""
        return _finite_tensor(mlp_output[..., 0, :])

    def as_deterministic_output_module(self) -> nn.Module:
        """Return export-friendly module that extracts the mean from the MLP output."""
        return _MeanSliceDeterministicOutput()

    @property
    def input_dim(self) -> list[int]:
        """Return the input dimension required by the distribution.

        The MLP must output a tensor of shape ``[..., 2, output_dim]`` where the first slice along the second-to-last
        dimension is the mean and the second is the standard deviation (or log standard deviation).
        """
        return [2, self.output_dim]

    def init_mlp_weights(self, mlp: nn.Module) -> None:
        """Initialize the std head weights in the MLP."""
        # Initialize weights and biases for the std portion of the last layer
        torch.nn.init.zeros_(mlp[-2].weight[self.output_dim :])  # type: ignore
        if self.std_type == "scalar":
            torch.nn.init.constant_(mlp[-2].bias[self.output_dim :], self.init_std)  # type: ignore
        elif self.std_type == "log":
            init_std_log = torch.log(torch.tensor(self.init_std + 1e-7))
            torch.nn.init.constant_(mlp[-2].bias[self.output_dim :], init_std_log)  # type: ignore


class _IdentityDeterministicOutput(nn.Module):
    """Exportable module that returns the MLP output as is."""

    def forward(self, mlp_output: torch.Tensor) -> torch.Tensor:
        return mlp_output


class _MeanSliceDeterministicOutput(nn.Module):
    """Exportable module that extracts the mean from the MLP output (first slice of the second-to-last dimension)."""

    def forward(self, mlp_output: torch.Tensor) -> torch.Tensor:
        return mlp_output[..., 0, :]


class _TanhDeterministicOutput(nn.Module):
    """Exportable module that applies tanh to bounded action means."""

    def forward(self, mlp_output: torch.Tensor) -> torch.Tensor:
        return torch.tanh(mlp_output)
