from __future__ import annotations

import numpy as np


def snv(x: np.ndarray) -> np.ndarray:
    mean = x.mean(axis=1, keepdims=True)
    std = x.std(axis=1, keepdims=True)
    std = np.where(std == 0, 1.0, std)
    return (x - mean) / std


def msc_fit(x: np.ndarray) -> np.ndarray:
    return x.mean(axis=0)


def msc_transform(x: np.ndarray, reference: np.ndarray) -> np.ndarray:
    corrected = np.empty_like(x, dtype=float)
    ref = np.asarray(reference, dtype=float)
    for i, spectrum in enumerate(x):
        slope, intercept = np.polyfit(ref, spectrum, 1)
        if abs(slope) < 1e-12:
            corrected[i] = spectrum - intercept
        else:
            corrected[i] = (spectrum - intercept) / slope
    return corrected


def savgol(x: np.ndarray, window_length: int, polyorder: int, deriv: int = 0) -> np.ndarray:
    window_length = int(window_length)
    if window_length % 2 == 0:
        window_length += 1
    window_length = max(window_length, polyorder + 2 + (polyorder + 2) % 2)
    window_length = min(window_length, x.shape[1] - (1 - x.shape[1] % 2))
    try:
        from scipy.signal import savgol_filter

        return savgol_filter(x, window_length=window_length, polyorder=polyorder, deriv=deriv, axis=1)
    except Exception:
        if deriv == 0:
            kernel = np.ones(window_length) / window_length
            return np.apply_along_axis(lambda row: np.convolve(row, kernel, mode="same"), 1, x)
        return np.gradient(x, axis=1)


def derivative(x: np.ndarray, order: int = 1) -> np.ndarray:
    out = x
    for _ in range(order):
        out = np.gradient(out, axis=1)
    return out


def apply_named_preprocess(
    train_x: np.ndarray,
    test_x: np.ndarray,
    name: str,
    params: dict | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    params = params or {}
    name = name.lower()
    if name == "raw":
        return train_x.astype(float), test_x.astype(float)
    if name == "snv":
        return snv(train_x), snv(test_x)
    if name == "msc":
        reference = msc_fit(train_x)
        return msc_transform(train_x, reference), msc_transform(test_x, reference)
    if name == "savgol":
        window = int(params.get("window_length", 21))
        polyorder = int(params.get("polyorder", 2))
        deriv = int(params.get("deriv", 0))
        return savgol(train_x, window, polyorder, deriv), savgol(test_x, window, polyorder, deriv)
    if name == "derivative1":
        return derivative(train_x, 1), derivative(test_x, 1)
    if name == "derivative2":
        return derivative(train_x, 2), derivative(test_x, 2)
    raise ValueError(f"未知の前処理です: {name}")
