from pathlib import Path


def _find_project_root(start: Path) -> Path:
    for parent in (start, *start.parents):
        if (parent / "AGENTS.md").exists():
            return parent
    raise RuntimeError(f"Failed to locate project root from: {start}")


PACKAGE_ROOT = Path(__file__).resolve().parent
EXTENSION_ROOT = PACKAGE_ROOT.parent
PROJECT_ROOT = _find_project_root(EXTENSION_ROOT)
USD_DIR = PROJECT_ROOT / "USD"
RESULTS_DIR = PROJECT_ROOT / "results"
COMPLETE_CAR_USD = USD_DIR / "complete_car.usd"


__all__ = [
    "COMPLETE_CAR_USD",
    "EXTENSION_ROOT",
    "PACKAGE_ROOT",
    "PROJECT_ROOT",
    "RESULTS_DIR",
    "USD_DIR",
]
