from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import OneHotEncoder

from src.preprocessing import apply_named_preprocess


WATER_BANDS = {
    "water_6900": (6600.0, 7200.0),
    "water_5200": (5000.0, 5400.0),
    "oh_4700": (4500.0, 4900.0),
}


def _safe_ratio(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a / np.where(np.abs(b) < 1e-12, np.nan, b)


def spectral_summary_features(x: np.ndarray, prefix: str) -> pd.DataFrame:
    q10, q25, q50, q75, q90 = np.quantile(x, [0.10, 0.25, 0.50, 0.75, 0.90], axis=1)
    data = {
        f"{prefix}_mean": x.mean(axis=1),
        f"{prefix}_std": x.std(axis=1),
        f"{prefix}_min": x.min(axis=1),
        f"{prefix}_max": x.max(axis=1),
        f"{prefix}_range": x.max(axis=1) - x.min(axis=1),
        f"{prefix}_q10": q10,
        f"{prefix}_q25": q25,
        f"{prefix}_q50": q50,
        f"{prefix}_q75": q75,
        f"{prefix}_q90": q90,
        f"{prefix}_edge_diff": x[:, -1] - x[:, 0],
        f"{prefix}_area": np.trapezoid(x, axis=1),
    }
    return pd.DataFrame(data)


def band_features(x: np.ndarray, wavelengths: np.ndarray, prefix: str) -> pd.DataFrame:
    features: dict[str, np.ndarray] = {}
    means: dict[str, np.ndarray] = {}
    for name, (low, high) in WATER_BANDS.items():
        mask = (wavelengths >= low) & (wavelengths <= high)
        if not mask.any():
            continue
        block = x[:, mask]
        means[name] = block.mean(axis=1)
        features[f"{prefix}_{name}_mean"] = means[name]
        features[f"{prefix}_{name}_max"] = block.max(axis=1)
        features[f"{prefix}_{name}_area"] = np.trapezoid(block, axis=1)
    if {"water_6900", "water_5200"} <= set(means):
        features[f"{prefix}_water_6900_5200_ratio"] = _safe_ratio(
            means["water_6900"], means["water_5200"]
        )
    return pd.DataFrame(features).replace([np.inf, -np.inf], np.nan).fillna(0.0)


def pca_features(
    train_x: np.ndarray,
    test_x: np.ndarray,
    n_components: int,
    prefix: str,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    n_components = min(int(n_components), train_x.shape[0] - 1, train_x.shape[1])
    pca = PCA(n_components=n_components, random_state=seed)
    train_scores = pca.fit_transform(train_x)
    test_scores = pca.transform(test_x)
    columns = [f"{prefix}_pca_{i:02d}" for i in range(n_components)]
    return pd.DataFrame(train_scores, columns=columns), pd.DataFrame(test_scores, columns=columns)


def metadata_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    config: dict,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    meta_config = config.get("metadata", {})
    train_parts: list[pd.DataFrame] = []
    test_parts: list[pd.DataFrame] = []

    if meta_config.get("numeric", False):
        cols = ["sample number", "species number"]
        train_parts.append(train_df[cols].reset_index(drop=True).astype(float))
        test_parts.append(test_df[cols].reset_index(drop=True).astype(float))

        for df, parts in ((train_df, train_parts), (test_df, test_parts)):
            by_species = df.groupby("species number")["sample number"]
            sequence = pd.DataFrame(
                {
                    "species_seq_index": by_species.rank(method="first").to_numpy(),
                    "species_seq_fraction": by_species.rank(method="first").to_numpy()
                    / by_species.transform("count").to_numpy(),
                }
            )
            parts.append(sequence)

    if meta_config.get("one_hot_species", False):
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        train_encoded = encoder.fit_transform(train_df[["樹種"]])
        test_encoded = encoder.transform(test_df[["樹種"]])
        columns = [f"species_{name}" for name in encoder.get_feature_names_out(["樹種"])]
        train_parts.append(pd.DataFrame(train_encoded, columns=columns))
        test_parts.append(pd.DataFrame(test_encoded, columns=columns))

    if not train_parts:
        return pd.DataFrame(index=train_df.index), pd.DataFrame(index=test_df.index)
    return (
        pd.concat(train_parts, axis=1).reset_index(drop=True),
        pd.concat(test_parts, axis=1).reset_index(drop=True),
    )


def build_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    spectral_columns: list[str],
    wavelengths: list[float],
    config: dict,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    feature_config = config.get("features", {})
    preprocess_blocks = feature_config.get("preprocess_blocks", [{"name": "raw"}])
    include_full_spectra = bool(feature_config.get("include_full_spectra", True))
    include_summary = bool(feature_config.get("include_summary", True))
    include_bands = bool(feature_config.get("include_bands", True))
    pca_components = int(feature_config.get("pca_components", 0))

    raw_train = train_df[spectral_columns].to_numpy(dtype=float)
    raw_test = test_df[spectral_columns].to_numpy(dtype=float)
    wave = np.asarray(wavelengths, dtype=float)

    train_parts: list[pd.DataFrame] = []
    test_parts: list[pd.DataFrame] = []

    for block in preprocess_blocks:
        name = block["name"] if isinstance(block, dict) else str(block)
        params = block.get("params", {}) if isinstance(block, dict) else {}
        prefix = params.get("prefix", name)
        train_x, test_x = apply_named_preprocess(raw_train, raw_test, name, params)

        if include_full_spectra:
            columns = [f"{prefix}_{column}" for column in spectral_columns]
            train_parts.append(pd.DataFrame(train_x, columns=columns))
            test_parts.append(pd.DataFrame(test_x, columns=columns))
        if include_summary:
            train_parts.append(spectral_summary_features(train_x, prefix))
            test_parts.append(spectral_summary_features(test_x, prefix))
        if include_bands:
            train_parts.append(band_features(train_x, wave, prefix))
            test_parts.append(band_features(test_x, wave, prefix))
        if pca_components > 0:
            pca_train, pca_test = pca_features(train_x, test_x, pca_components, prefix, seed)
            train_parts.append(pca_train)
            test_parts.append(pca_test)

    meta_train, meta_test = metadata_features(train_df, test_df, feature_config)
    train_parts.append(meta_train)
    test_parts.append(meta_test)

    train_features = pd.concat(train_parts, axis=1).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    test_features = pd.concat(test_parts, axis=1).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return train_features, test_features
