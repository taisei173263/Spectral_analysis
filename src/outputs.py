from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.competition_io import CompetitionData
from src.metrics import rmse


def save_experiment_artifacts(
    output_dir: Path,
    config: dict,
    config_path: Path,
    data: CompetitionData,
    x: pd.DataFrame,
    y: pd.Series,
    model_results: list[dict[str, Any]],
    weights: np.ndarray,
    ensemble_oof: np.ndarray,
    ensemble_test: np.ndarray,
    submission_path: Path,
    errors: list[str],
    experiment_id: str,
) -> dict:
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
    return metadata
