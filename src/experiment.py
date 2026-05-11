from __future__ import annotations

from pathlib import Path

from src.competition_io import load_competition_data, load_yaml, target_series, write_submission
from src.ensemble import apply_postprocess_clip, blend_predictions, compute_weights
from src.evaluation import evaluate_model
from src.features import build_features
from src.outputs import save_experiment_artifacts
from src.tuning import tune_lightgbm_with_optuna


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
    weights = compute_weights(model_results, weights_config)
    ensemble_oof, ensemble_test = blend_predictions(model_results, weights)
    clip_config = config.get("postprocess", {}).get("clip", {})
    ensemble_test = apply_postprocess_clip(ensemble_test, y, clip_config)

    submission_path = write_submission(
        data.test,
        ensemble_test,
        config["paths"]["output_submission_csv"],
        data.sample_submit,
    )

    metadata = save_experiment_artifacts(
        output_dir=output_dir,
        config=config,
        config_path=config_path,
        data=data,
        x=x,
        y=y,
        model_results=model_results,
        weights=weights,
        ensemble_oof=ensemble_oof,
        ensemble_test=ensemble_test,
        submission_path=submission_path,
        errors=errors,
        experiment_id=experiment_id,
    )
    print(f"submission generated: {submission_path}", flush=True)
    print(f"experiment saved: {output_dir}", flush=True)
    return metadata
