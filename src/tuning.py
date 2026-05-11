from __future__ import annotations

from copy import deepcopy

import numpy as np
import pandas as pd
from sklearn.base import clone

from src.cv import make_folds
from src.metrics import rmse
from src.models import build_estimator


def tune_lightgbm_with_optuna(
    x: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    base_params: dict,
    config: dict,
    seed: int,
) -> dict:
    try:
        import optuna
    except ImportError:
        print("optuna がないため探索をスキップします。")
        return base_params

    optuna_config = config.get("optuna", {})
    n_trials = int(optuna_config.get("n_trials", 0))
    if n_trials <= 0:
        return base_params

    folds = make_folds(y, groups, config, seed)

    def objective(trial):
        params = deepcopy(base_params)
        params.update(
            {
                "n_estimators": trial.suggest_int("n_estimators", 300, 1200),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.08, log=True),
                "num_leaves": trial.suggest_int("num_leaves", 16, 96),
                "min_child_samples": trial.suggest_int("min_child_samples", 5, 80),
                "subsample": trial.suggest_float("subsample", 0.65, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.45, 1.0),
                "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
                "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 50.0, log=True),
            }
        )
        estimator = build_estimator("lightgbm", params, seed)
        scores = []
        for train_idx, valid_idx in folds:
            model = clone(estimator)
            model.fit(x.iloc[train_idx], y.iloc[train_idx])
            pred = model.predict(x.iloc[valid_idx])
            scores.append(rmse(y.iloc[valid_idx], pred))
        return float(np.mean(scores))

    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=seed))
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    tuned = deepcopy(base_params)
    tuned.update(study.best_params)
    return tuned
