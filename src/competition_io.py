from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
import yaml


ENCODINGS = ("utf-8", "cp932", "shift_jis")
META_COLUMNS = ("sample number", "species number", "樹種")
TARGET_COLUMN = "含水率"


@dataclass(frozen=True)
class CompetitionData:
    train: pd.DataFrame
    test: pd.DataFrame
    sample_submit: pd.DataFrame
    spectral_columns: list[str]
    wavelengths: list[float]


def read_csv_with_fallback(path: str | Path, **kwargs) -> pd.DataFrame:
    for encoding in ENCODINGS:
        try:
            return pd.read_csv(path, encoding=encoding, **kwargs)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, **kwargs)


def load_yaml(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_spectral_columns(columns: Iterable[str]) -> list[str]:
    spectral_columns: list[str] = []
    for column in columns:
        try:
            float(column)
        except (TypeError, ValueError):
            continue
        spectral_columns.append(str(column))
    if not spectral_columns:
        raise ValueError("波数列が見つかりませんでした。")
    return spectral_columns


def load_competition_data(config: dict) -> CompetitionData:
    paths = config["paths"]
    train = read_csv_with_fallback(paths["train_csv"])
    test = read_csv_with_fallback(paths["test_csv"])
    sample_submit = read_csv_with_fallback(paths["sample_submit_csv"], header=None)
    spectral_columns = find_spectral_columns(train.columns)
    wavelengths = [float(column) for column in spectral_columns]

    missing_in_test = sorted(set(spectral_columns) - set(test.columns))
    if missing_in_test:
        raise ValueError(f"testに存在しない波数列があります: {missing_in_test[:5]}")

    return CompetitionData(
        train=train,
        test=test,
        sample_submit=sample_submit,
        spectral_columns=spectral_columns,
        wavelengths=wavelengths,
    )


def target_series(train: pd.DataFrame, target_column: str = TARGET_COLUMN) -> pd.Series:
    if target_column in train.columns:
        return train[target_column].astype(float)
    return train.iloc[:, 3].astype(float)


def write_submission(
    test_df: pd.DataFrame,
    predictions,
    output_path: str | Path,
    sample_submit: pd.DataFrame | None = None,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    submission = pd.DataFrame({0: test_df["sample number"], 1: predictions})
    if sample_submit is not None and submission.shape != sample_submit.shape:
        raise ValueError(
            f"提出形式がsample_submitと一致しません: {submission.shape} != {sample_submit.shape}"
        )
    submission.to_csv(output_path, index=False, header=False)
    return output_path
