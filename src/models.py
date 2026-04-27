from __future__ import annotations

from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.cross_decomposition import PLSRegression
from sklearn.svm import SVR


def build_estimator(name: str, params: dict | None = None, seed: int = 42):
    params = dict(params or {})
    name = name.lower()

    if name == "ridge":
        return make_pipeline(StandardScaler(), Ridge(**params))
    if name == "elasticnet":
        params.setdefault("random_state", seed)
        params.setdefault("max_iter", 20000)
        return make_pipeline(StandardScaler(), ElasticNet(**params))
    if name == "pls":
        return PLSRegression(**params)
    if name == "svr":
        return make_pipeline(StandardScaler(), SVR(**params))
    if name == "kernel_ridge":
        return make_pipeline(StandardScaler(), KernelRidge(**params))
    if name == "extra_trees":
        params.setdefault("random_state", seed)
        params.setdefault("n_jobs", -1)
        return ExtraTreesRegressor(**params)
    if name == "random_forest":
        params.setdefault("random_state", seed)
        params.setdefault("n_jobs", -1)
        return RandomForestRegressor(**params)
    if name == "hist_gradient_boosting":
        params.setdefault("random_state", seed)
        return HistGradientBoostingRegressor(**params)
    if name == "lightgbm":
        try:
            from lightgbm import LGBMRegressor
        except ImportError as exc:
            raise ImportError("lightgbm がインストールされていません。") from exc
        params.setdefault("random_state", seed)
        params.setdefault("n_jobs", -1)
        params.setdefault("verbosity", -1)
        return LGBMRegressor(**params)
    if name == "catboost":
        try:
            from catboost import CatBoostRegressor
        except ImportError as exc:
            raise ImportError("catboost がインストールされていません。") from exc
        params.setdefault("random_seed", seed)
        params.setdefault("loss_function", "RMSE")
        params.setdefault("verbose", False)
        return CatBoostRegressor(**params)

    raise ValueError(f"未知のモデルです: {name}")
