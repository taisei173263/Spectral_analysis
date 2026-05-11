from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, KFold


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
