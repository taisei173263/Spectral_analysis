from __future__ import annotations

import argparse
import json
import os
from copy import deepcopy
from datetime import datetime
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(".matplotlib_cache").resolve()))

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold, KFold

from src.competition_io import load_competition_data, load_yaml, target_series, write_submission
from src.features import build_features
from src.models import build_estimator


def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def make_folds(y: pd.Series, groups: pd.Series, config: dict, seed: int):
    cv_config = config.get("cv", {})
    strategy = cv_config.get("strategy", "group_kfold")
    n_splits = int(cv_config.get("n_splits", 5))
    if strategy == "group_kfold":
        splitter = GroupKFold(n_splits=min(n_splits, groups.nunique()))
        return list(splitter.split(np.zeros(len(y)), y, groups))
    if strategy == "kfold":
        splitter = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
        return list(splitter.split(np.zeros(len(y)), y))
    raise ValueError(f"未知のCV戦略です: {strategy}")


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


def run_experiment(config_path: Path) -> dict:
    config = load_yaml(config_path)
    seed = int(config.get("seed", 42))
    experiment_id = config.get("experiment_id", config.get("name", "EXP-competition"))
    output_dir = Path(config["paths"].get("experiment_dir", f"outputs/experiments/{experiment_id}"))
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{experiment_id}] load data", flush=True)
    data = load_competition_data(config)
    y = target_series(data.train, config.get("target", {}).get("column", "含水率"))
    groups = data.train["species number"]
    print(f"[{experiment_id}] build features", flush=True)
    x, test_x = build_features(
        data.train,
        data.test,
        data.spectral_columns,
        data.wavelengths,
        config,
        seed,
    )
    print(f"[{experiment_id}] features ready: train={x.shape} test={test_x.shape}", flush=True)

    model_results = []
    errors = []
    for model_config in config.get("models", []):
        if not model_config.get("enabled", True):
            continue
        model_name = model_config["name"]
        print(f"[{experiment_id}] start model: {model_name}", flush=True)
        params = dict(model_config.get("params", {}))
        if model_name.lower() == "lightgbm" and config.get("optuna", {}).get("enabled", False):
            params = tune_lightgbm_with_optuna(x, y, groups, params, config, seed)
        try:
            result = evaluate_model(model_name, params, x, test_x, y, groups, config, seed)
            model_results.append(result)
            print(f"{model_name}: CV RMSE={result['cv_rmse']:.5f}", flush=True)
        except Exception as exc:
            message = f"{model_name}: {type(exc).__name__}: {exc}"
            print(f"SKIP {message}", flush=True)
            errors.append(message)

    if not model_results:
        raise RuntimeError("有効なモデル結果がありません。")

    weights_config = config.get("ensemble", {}).get("weights", {})
    if weights_config:
        weights = np.array([float(weights_config.get(r["name"], 0.0)) for r in model_results])
    else:
        inv = np.array([1.0 / max(r["cv_rmse"], 1e-9) for r in model_results])
        weights = inv
    weights = weights / weights.sum()

    ensemble_oof = sum(weight * result["oof"] for weight, result in zip(weights, model_results))
    ensemble_test = sum(weight * result["test_pred"] for weight, result in zip(weights, model_results))
    clip_config = config.get("postprocess", {}).get("clip", {})
    if clip_config.get("enabled", True):
        low = float(clip_config.get("min", max(0.0, y.min())))
        high = float(clip_config.get("max", y.max()))
        ensemble_test = np.clip(ensemble_test, low, high)

    submission_path = write_submission(
        data.test,
        ensemble_test,
        config["paths"]["output_submission_csv"],
        data.sample_submit,
    )

    fold_df = pd.DataFrame([row for result in model_results for row in result["folds"]])
    summary_df = pd.DataFrame(
        {
            "model": [result["name"] for result in model_results] + ["ensemble"],
            "cv_rmse": [result["cv_rmse"] for result in model_results] + [rmse(y, ensemble_oof)],
            "weight": list(weights) + [1.0],
        }
    )
    oof_df = pd.DataFrame({"sample number": data.train["sample number"], "target": y, "ensemble": ensemble_oof})
    for result in model_results:
        oof_df[result["name"]] = result["oof"]
    pred_df = pd.DataFrame({"sample number": data.test["sample number"], "ensemble": ensemble_test})
    for result in model_results:
        pred_df[result["name"]] = result["test_pred"]

    fold_df.to_csv(output_dir / "fold_scores.csv", index=False)
    summary_df.to_csv(output_dir / "model_summary.csv", index=False)
    oof_df.to_csv(output_dir / "oof_predictions.csv", index=False)
    pred_df.to_csv(output_dir / "test_predictions.csv", index=False)
    pd.Series(x.columns, name="feature").to_csv(output_dir / "feature_columns.csv", index=False)
    if config.get("artifacts", {}).get("save_models", False):
        joblib.dump(
            {"config": config, "models": [result["models"] for result in model_results], "weights": weights},
            output_dir / "fitted_models.joblib",
        )

    metadata = {
        "experiment_id": experiment_id,
        "config_path": str(config_path),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "n_train": int(len(data.train)),
        "n_test": int(len(data.test)),
        "n_features": int(x.shape[1]),
        "cv_strategy": config.get("cv", {}).get("strategy", "group_kfold"),
        "ensemble_cv_rmse": rmse(y, ensemble_oof),
        "submission_path": str(submission_path),
        "skipped_models": errors,
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    readme = (
        f"# {experiment_id}\n\n"
        f"- Config: `{config_path}`\n"
        f"- CV strategy: `{metadata['cv_strategy']}`\n"
        f"- Features: `{x.shape[1]}`\n"
        f"- Ensemble CV RMSE: `{metadata['ensemble_cv_rmse']:.5f}`\n"
        f"- Submission: `{submission_path}`\n"
    )
    (output_dir / "README.md").write_text(readme, encoding="utf-8")
    print(f"submission generated: {submission_path}", flush=True)
    print(f"experiment saved: {output_dir}", flush=True)
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Run spectral competition experiment.")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    run_experiment(args.config)


if __name__ == "__main__":
    main()
