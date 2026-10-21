"""Binary classification metrics, threshold selection, and calibration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from flavfinder.io import coerce_binary_labels


def _arrays(y_true: Any, y_score: Any) -> tuple[np.ndarray, np.ndarray]:
    truth = coerce_binary_labels(y_true)
    score = np.asarray(y_score, dtype=float).ravel()
    if truth.size != score.size:
        raise ValueError(f"y_true and y_score lengths differ ({truth.size} vs {score.size})")
    if not np.all(np.isfinite(score)):
        raise ValueError("y_score contains non-finite values")
    return truth, score


def _threshold_metrics(truth: np.ndarray, score: np.ndarray, threshold: float) -> dict[str, Any]:
    predicted = (score >= threshold).astype(int)
    return {
        "accuracy": float(accuracy_score(truth, predicted)),
        "precision": float(precision_score(truth, predicted, zero_division=0)),
        "recall": float(recall_score(truth, predicted, zero_division=0)),
        "f1": float(f1_score(truth, predicted, zero_division=0)),
        "confusion_matrix": confusion_matrix(truth, predicted, labels=[0, 1]).tolist(),
    }


def binary_metrics(y_true: Any, y_score: Any, threshold: float = 0.5) -> dict[str, Any]:
    """Compute common binary metrics, with ``None`` for undefined AUC values."""

    truth, score = _arrays(y_true, y_score)
    result: dict[str, Any] = {
        "n": int(truth.size),
        "positive_rate": float(truth.mean()),
        "threshold": float(threshold),
    }
    try:
        result["auroc"] = float(roc_auc_score(truth, score))
        result["auprc"] = float(average_precision_score(truth, score))
    except ValueError:
        result["auroc"] = None
        result["auprc"] = None
    result["brier"] = float(brier_score_loss(truth, score))
    result.update(_threshold_metrics(truth, score, threshold))
    return result


def bootstrap_ci(
    y_true: Any,
    y_score: Any,
    *,
    n_boot: int = 1000,
    confidence: float = 0.95,
    seed: int = 42,
) -> dict[str, dict[str, float | int]]:
    """Bootstrap percentile confidence intervals for AUROC, AUPRC, and Brier."""

    truth, score = _arrays(y_true, y_score)
    if truth.size < 2:
        raise ValueError("bootstrap requires at least two samples")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    rng = np.random.default_rng(seed)
    values: dict[str, list[float]] = {"auroc": [], "auprc": [], "brier": []}
    for _ in range(int(n_boot)):
        indices = rng.integers(0, truth.size, size=truth.size)
        sample_truth = truth[indices]
        sample_score = score[indices]
        if np.unique(sample_truth).size < 2:
            continue
        values["auroc"].append(float(roc_auc_score(sample_truth, sample_score)))
        values["auprc"].append(float(average_precision_score(sample_truth, sample_score)))
        values["brier"].append(float(brier_score_loss(sample_truth, sample_score)))

    alpha = (1.0 - confidence) / 2.0
    out: dict[str, dict[str, float | int]] = {}
    for name, samples in values.items():
        if not samples:
            out[name] = {"mean": float("nan"), "low": float("nan"), "high": float("nan"), "n": 0}
            continue
        array = np.asarray(samples, dtype=float)
        out[name] = {
            "mean": float(array.mean()),
            "low": float(np.quantile(array, alpha)),
            "high": float(np.quantile(array, 1.0 - alpha)),
            "n": int(array.size),
        }
    return out


def select_thresholds(
    y_true: Any,
    y_score: Any,
    *,
    high_fpr: float = 0.01,
) -> dict[str, dict[str, Any]]:
    """Select a Youden-optimal ``mid`` threshold and a low-FPR ``high`` threshold."""

    truth, score = _arrays(y_true, y_score)
    if np.unique(truth).size < 2:
        raise ValueError("threshold selection requires both classes")
    if not 0 <= high_fpr < 1:
        raise ValueError("high_fpr must be in [0, 1)")

    fpr, tpr, thresholds = roc_curve(truth, score)
    safe_thresholds = np.asarray(thresholds, dtype=float).copy()
    safe_thresholds[0] = float(score.max()) + 1e-12

    mid_index = int(np.argmax(tpr - fpr))
    high_index = int(np.argmin(np.abs(fpr - high_fpr)))
    mid_value = float(safe_thresholds[mid_index])
    high_value = max(float(safe_thresholds[high_index]), mid_value)

    return {
        "mid": {
            "value": mid_value,
            "fpr": float(fpr[mid_index]),
            "tpr": float(tpr[mid_index]),
            **_threshold_metrics(truth, score, mid_value),
        },
        "high": {
            "value": high_value,
            "fpr": float(fpr[high_index]),
            "tpr": float(tpr[high_index]),
            **_threshold_metrics(truth, score, high_value),
        },
    }


def probability_bucket(scores: Any, thresholds: dict[str, Any]) -> np.ndarray:
    """Map scores to ``high`` / ``mid`` / ``low`` labels."""

    values = np.asarray(scores, dtype=float).ravel()
    high = float(thresholds["high"]["value"])
    mid = float(thresholds["mid"]["value"])
    return np.where(values > high, "high", np.where(values > mid, "mid", "low"))


def calibration_points(
    y_true: Any,
    y_score: Any,
    *,
    n_bins: int = 10,
) -> list[dict[str, float | int]]:
    """Return reliability-curve points using quantile bins."""

    truth, score = _arrays(y_true, y_score)
    if np.unique(truth).size < 2:
        raise ValueError("calibration requires both classes")
    fraction_positive, mean_predicted = calibration_curve(
        truth, score, n_bins=n_bins, strategy="quantile"
    )
    return [
        {
            "mean_predicted": float(mean),
            "fraction_positive": float(fraction),
        }
        for mean, fraction in zip(mean_predicted, fraction_positive, strict=True)
    ]


def evaluate_metrics(
    y_true: Any,
    y_score: Any,
    *,
    threshold: float = 0.5,
    with_bootstrap: bool = True,
    n_boot: int = 1000,
    seed: int = 42,
) -> dict[str, Any]:
    """Convenience wrapper returning metrics, bootstrap CIs, and calibration."""

    result = binary_metrics(y_true, y_score, threshold=threshold)
    if with_bootstrap and result["n"] >= 2:
        result["bootstrap"] = bootstrap_ci(
            y_true, y_score, n_boot=n_boot, seed=seed
        )
        try:
            result["calibration"] = calibration_points(y_true, y_score)
        except ValueError:
            result["calibration"] = []
    return result


MetricFn = Callable[[np.ndarray, np.ndarray], float]
