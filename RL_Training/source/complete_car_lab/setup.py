"""Installation script for the `complete_car_lab` package."""

from __future__ import annotations

import os

from setuptools import find_packages, setup

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


EXTENSION_ROOT = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(EXTENSION_ROOT, "config", "extension.toml"), "rb") as file:
    EXTENSION_TOML = tomllib.load(file)


setup(
    name="complete_car_lab",
    version=EXTENSION_TOML["package"]["version"],
    description=EXTENSION_TOML["package"]["description"],
    author=EXTENSION_TOML["package"]["author"],
    maintainer=EXTENSION_TOML["package"]["maintainer"],
    url=EXTENSION_TOML["package"]["repository"],
    keywords=EXTENSION_TOML["package"]["keywords"],
    packages=find_packages(include=["complete_car_lab", "complete_car_lab.*"]),
    install_requires=["psutil", "GitPython", "tensorboard"],
    include_package_data=True,
    python_requires=">=3.10",
    zip_safe=False,
)
