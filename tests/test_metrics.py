from __future__ import annotations

import numpy as np
import pytest

from flavfinder.metrics import (
    binary_metrics,
    bootstrap_ci,
    calibration_points,
    probability_bucket,
    select_thresholds,
)


def test_perfect_separation_metrics() -> None:
    truth = np.array([0, 0, 1, 1])
    score = np.array([0.1, 0.2, 0.8, 0.9])
    metrics = binary_metrics(truth, score, threshold=0.5)
    assert metrics["auroc"] == pytest.approx(1.0)
    assert metrics["auprc"] == pytest.approx(1.0)
    assert metrics["accuracy"] == 1.0
    assert metrics["confusion_matrix"] == [[2, 0], [0, 2]]


def test_select_thresholds_and_buckets() -> None:
    truth = np.array([0, 0, 0, 1, 1, 1])
    score = np.array([0.05, 0.15, 0.25, 0.75, 0.85, 0.95])
    thresholds = select_thresholds(truth, score, high_fpr=0.0)
    assert thresholds["high"]["value"] >= thresholds["mid"]["value"]
    buckets = probability_bucket(score, thresholds)
    assert set(buckets) <= {"high", "mid", "low"}


def test_bootstrap_is_deterministic() -> None:
    truth = np.array([0, 0, 1, 1, 0, 1])
    score = np.array([0.1, 0.2, 0.8, 0.9, 0.3, 0.7])
    first = bootstrap_ci(truth, score, n_boot=50, seed=7)
    second = bootstrap_ci(truth, score, n_boot=50, seed=7)
    assert first == second
    assert first["auroc"]["n"] > 0


def test_calibration_points() -> None:
    truth = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    score = np.array([0.1, 0.2, 0.8, 0.9, 0.3, 0.7, 0.4, 0.6])
    points = calibration_points(truth, score, n_bins=4)
    assert points
    assert all(0.0 <= point["mean_predicted"] <= 1.0 for point in points)


def test_threshold_requires_both_classes() -> None:
    with pytest.raises(ValueError):
        select_thresholds([0, 0], [0.1, 0.2])


def test_invalid_high_fpr() -> None:
    with pytest.raises(ValueError):
        select_thresholds([0, 1], [0.1, 0.9], high_fpr=1.0)
