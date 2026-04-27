from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT_DIR / ".matplotlib_cache"))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.competition_io import find_spectral_columns, read_csv_with_fallback


def main() -> None:
    output_dir = Path("outputs/experiments/EDA-001")
    output_dir.mkdir(parents=True, exist_ok=True)

    train = read_csv_with_fallback("data/raw/train.csv")
    test = read_csv_with_fallback("data/raw/test.csv")
    spectral_columns = find_spectral_columns(train.columns)
    wavelengths = [float(column) for column in spectral_columns]

    species_counts = pd.concat(
        [
            train.groupby(["species number", "樹種"]).size().rename("train_count"),
            test.groupby(["species number", "樹種"]).size().rename("test_count"),
        ],
        axis=1,
    ).fillna(0).astype(int)
    species_counts.to_csv(output_dir / "species_counts.csv")

    y_summary = train["含水率"].describe()
    y_summary.to_csv(output_dir / "target_summary.csv")

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.histplot(train["含水率"], bins=50, ax=axes[0])
    axes[0].set_title("Target Distribution")
    sns.boxplot(data=train, x="species number", y="含水率", ax=axes[1])
    axes[1].set_title("Target by Species")
    fig.tight_layout()
    fig.savefig(output_dir / "target_distribution.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5))
    for _, row in train.groupby("species number").head(3).iterrows():
        ax.plot(wavelengths, row[spectral_columns].to_numpy(dtype=float), alpha=0.25)
    ax.invert_xaxis()
    ax.set_title("Train Spectra Samples")
    ax.set_xlabel("Wavenumber cm^-1")
    ax.set_ylabel("Absorbance")
    fig.tight_layout()
    fig.savefig(output_dir / "spectra_samples.png", dpi=150)
    plt.close(fig)

    readme = f"""# EDA-001

## Data Shape
- Train: `{train.shape[0]}` rows x `{train.shape[1]}` columns
- Test: `{test.shape[0]}` rows x `{test.shape[1]}` columns
- Spectral columns: `{len(spectral_columns)}`
- Wavenumber range: `{min(wavelengths):.2f}` to `{max(wavelengths):.2f}` cm^-1

## Key Findings
- Train and test species are disjoint in the provided split, so GroupKFold by `species number` is the primary local validation.
- `sample number` is contiguous by species; it can encode acquisition order but may overfit if used without a group-aware validation.
- Main water-related NIR regions around 6900 and 5200 cm^-1 are included in hand-crafted band features.

## Artifacts
- `species_counts.csv`
- `target_summary.csv`
- `target_distribution.png`
- `spectra_samples.png`
"""
    (output_dir / "README.md").write_text(readme, encoding="utf-8")
    print(f"EDA report saved: {output_dir}")


if __name__ == "__main__":
    main()
