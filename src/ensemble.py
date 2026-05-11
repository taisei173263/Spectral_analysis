from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def compute_weights(model_results: list[dict[str, Any]], weights_config: dict) -> np.ndarray:
    if weights_config:
        weights = np.array([float(weights_config.get(r["name"], 0.0)) for r in model_results])
    else:
        inv = np.array([1.0 / max(r["cv_rmse"], 1e-9) for r in model_results])
        weights = inv
    return weights / weights.sum()


def blend_predictions(
    model_results: list[dict[str, Any]],
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    ensemble_oof = sum(weight * result["oof"] for weight, result in zip(weights, model_results))
    ensemble_test = sum(weight * result["test_pred"] for weight, result in zip(weights, model_results))
    return ensemble_oof, ensemble_test


def apply_postprocess_clip(ensemble_test: np.ndarray, y: pd.Series, clip_config: dict) -> np.ndarray:
    if clip_config.get("enabled", True):
        low = float(clip_config.get("min", max(0.0, y.min())))
        high = float(clip_config.get("max", y.max()))
        return np.clip(ensemble_test, low, high)
    return ensemble_test
