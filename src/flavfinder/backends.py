"""Pluggable model backends.

The core package keeps AutoGluon as the reference backend and provides a
LightGBM backend for fast local runs plus a scikit-learn backend for tests.
Optional backends are imported lazily so the base install stays lightweight.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import joblib
import numpy as np
import pandas as pd


@runtime_checkable
class ModelBackend(Protocol):
    name: str

    def fit(self, X: pd.DataFrame, y: pd.Series, path: Path) -> None:
        """Fit the model and persist any backend-specific state under ``path``."""

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Return the probability of the positive class."""

    def save(self, path: Path) -> None:
        """Persist the backend under ``path``."""


def _positive_class_probability(proba: np.ndarray, classes: np.ndarray) -> np.ndarray:
    proba = np.asarray(proba, dtype=float)
    if proba.ndim == 1:
        return proba
    if proba.shape[1] == 1:
        return np.ones(proba.shape[0]) if classes[0] == 1 else np.zeros(proba.shape[0])
    positive = np.flatnonzero(np.asarray(classes) == 1)
    if positive.size == 0:
        raise ValueError("model has no positive class")
    return proba[:, int(positive[0])]


class SklearnBackend:
    """Logistic-regression backend intended for tests and tiny datasets."""

    name = "sklearn"

    def __init__(
        self,
        random_state: int = 42,
        max_iter: int = 1000,
        **params: Any,
    ) -> None:
        from sklearn.linear_model import LogisticRegression

        params = dict(params)
        params.setdefault("class_weight", "balanced")
        self.model = LogisticRegression(
            max_iter=int(max_iter),
            random_state=int(random_state),
            **params,
        )

    def fit(self, X: pd.DataFrame, y: pd.Series, path: Path) -> None:
        if len(X) != len(y):
            raise ValueError("X and y lengths differ")
        self.model.fit(X, y)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return _positive_class_probability(
            self.model.predict_proba(X), self.model.classes_
        )

    def save(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path / "model.joblib")

    @classmethod
    def load(cls, path: Path) -> SklearnBackend:
        backend = cls()
        backend.model = joblib.load(path / "model.joblib")
        return backend


class LightGBMBackend:
    """LightGBM backend for fast, reproducible local training."""

    name = "lightgbm"

    def __init__(self, random_state: int = 42, **params: Any) -> None:
        try:
            from lightgbm import LGBMClassifier
        except ImportError as exc:
            raise ImportError(
                "LightGBM is optional; install with: pip install 'flavfinder-core[lightgbm]'"
            ) from exc

        params = dict(params)
        params.setdefault("n_estimators", 300)
        params.setdefault("learning_rate", 0.05)
        params.setdefault("num_leaves", 31)
        params.setdefault("class_weight", "balanced")
        params.setdefault("n_jobs", -1)
        params.setdefault("verbosity", -1)
        self.model = LGBMClassifier(random_state=int(random_state), **params)

    def fit(self, X: pd.DataFrame, y: pd.Series, path: Path) -> None:
        if len(X) != len(y):
            raise ValueError("X and y lengths differ")
        self.model.fit(X, y)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return _positive_class_probability(
            self.model.predict_proba(X), self.model.classes_
        )

    def save(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path / "model.joblib")

    @classmethod
    def load(cls, path: Path) -> LightGBMBackend:
        backend = cls()
        backend.model = joblib.load(path / "model.joblib")
        return backend


class AutoGluonBackend:
    """Reference backend used by the original flavfinder implementation."""

    name = "autogluon"

    def __init__(
        self,
        eval_metric: str = "roc_auc",
        presets: str | list[str] | None = "optimize_for_deployment",
        time_limit: float | None = None,
        random_state: int = 42,
        **params: Any,
    ) -> None:
        try:
            from autogluon.tabular import TabularPredictor
        except ImportError as exc:
            raise ImportError(
                "AutoGluon is optional; install with: pip install 'flavfinder-core[autogluon]'"
            ) from exc

        self._predictor_cls = TabularPredictor
        self.eval_metric = eval_metric
        self.presets = presets
        self.time_limit = time_limit
        self.random_state = int(random_state)
        self.params = dict(params)
        self.predictor: Any = None

    def fit(self, X: pd.DataFrame, y: pd.Series, path: Path) -> None:
        if len(X) != len(y):
            raise ValueError("X and y lengths differ")
        path = Path(path)
        if path.exists() and any(path.iterdir()):
            raise FileExistsError(f"AutoGluon predictor path is not empty: {path}")
        train_data = X.copy()
        train_data["label"] = np.asarray(y)
        self.predictor = self._predictor_cls(
            label="label",
            eval_metric=self.eval_metric,
            path=str(path),
        )
        fit_params = dict(self.params)
        if self.presets is not None:
            fit_params.setdefault("presets", self.presets)
        if self.time_limit is not None:
            fit_params.setdefault("time_limit", self.time_limit)
        self.predictor.fit(train_data=train_data, **fit_params)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if self.predictor is None:
            raise RuntimeError("AutoGluon backend is not fitted")
        proba = self.predictor.predict_proba(X)
        if 1 in proba.columns:
            return proba[1].to_numpy(dtype=float)
        if "1" in proba.columns:
            return proba["1"].to_numpy(dtype=float)
        return proba.iloc[:, -1].to_numpy(dtype=float)

    def save(self, path: Path) -> None:
        # TabularPredictor persists itself during fit(path=...).
        return None

    @classmethod
    def load(cls, path: Path) -> AutoGluonBackend:
        backend = cls.__new__(cls)
        backend._predictor_cls = None
        backend.eval_metric = "roc_auc"
        backend.presets = None
        backend.time_limit = None
        backend.random_state = 42
        backend.params = {}
        from autogluon.tabular import TabularPredictor

        backend.predictor = TabularPredictor.load(str(path))
        return backend


_BACKENDS = {
    "autogluon": AutoGluonBackend,
    "lightgbm": LightGBMBackend,
    "sklearn": SklearnBackend,
    "toy": SklearnBackend,
}


def create_backend(name: str, params: dict[str, Any] | None = None) -> ModelBackend:
    key = name.lower()
    if key not in _BACKENDS:
        raise ValueError(f"unknown backend: {name!r}; choose from {sorted(_BACKENDS)}")
    return _BACKENDS[key](**(params or {}))


def load_backend(name: str, path: str | Path) -> ModelBackend:
    key = name.lower()
    if key not in _BACKENDS:
        raise ValueError(f"unknown backend: {name!r}; choose from {sorted(_BACKENDS)}")
    return _BACKENDS[key].load(Path(path))


__all__ = [
    "AutoGluonBackend",
    "LightGBMBackend",
    "ModelBackend",
    "SklearnBackend",
    "create_backend",
    "load_backend",
]
