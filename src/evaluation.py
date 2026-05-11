from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import clone

from src.cv import make_folds
from src.metrics import rmse
from src.models import build_estimator


def evaluate_model(
    model_name: str,
    params: dict,
    x: pd.DataFrame,
    test_x: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    config: dict,
    seed: int,
):
    folds = make_folds(y, groups, config, seed)
    oof = np.zeros(len(y), dtype=float)
    test_pred = np.zeros(len(test_x), dtype=float)
    fold_rows = []

    estimator = build_estimator(model_name, params, seed)
    fitted_models = []
    for fold, (train_idx, valid_idx) in enumerate(folds, start=1):
        model = clone(estimator)
        model.fit(x.iloc[train_idx], y.iloc[train_idx])
        valid_pred = np.asarray(model.predict(x.iloc[valid_idx])).ravel()
        fold_test_pred = np.asarray(model.predict(test_x)).ravel()
        oof[valid_idx] = valid_pred
        test_pred += fold_test_pred / len(folds)
        fitted_models.append(model)
        fold_rows.append(
            {
                "model": model_name,
                "fold": fold,
                "rmse": rmse(y.iloc[valid_idx], valid_pred),
                "valid_size": len(valid_idx),
                "valid_species": ",".join(sorted(groups.iloc[valid_idx].astype(str).unique())),
            }
        )

    return {
        "name": model_name,
        "params": params,
        "oof": oof,
        "test_pred": test_pred,
        "cv_rmse": rmse(y, oof),
        "folds": fold_rows,
        "models": fitted_models,
    }
