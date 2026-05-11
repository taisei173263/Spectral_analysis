from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(".matplotlib_cache").resolve()))

from src.experiment import run_experiment


def main() -> None:
    parser = argparse.ArgumentParser(description="Run spectral competition experiment.")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    run_experiment(args.config)


if __name__ == "__main__":
    main()
