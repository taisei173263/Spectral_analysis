from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error


def rmse(y_true: pd.Series | np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))
