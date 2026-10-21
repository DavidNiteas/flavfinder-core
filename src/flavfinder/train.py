"""Training orchestration."""

from __future__ import annotations

import platform
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from flavfinder import __version__
from flavfinder.backends import create_backend
from flavfinder.bundle import ModelBundle
from flavfinder.config import TrainingConfig
from flavfinder.io import (
    SpectrumSchema,
    coerce_binary_labels,
    prepare_frame,
    read_frame,
    save_json,
)
from flavfinder.metrics import evaluate_metrics, select_thresholds


def _load_labeled(
    path: str | Path,
    schema: SpectrumSchema,
) -> tuple[pd.DataFrame, np.ndarray]:
    frame = prepare_frame(read_frame(path, schema), schema, require_label=True)
    labels = coerce_binary_labels(frame[schema.label_col], schema.label_col)
    if np.unique(labels).size < 2:
        raise ValueError(f"training data must contain both classes: {path}")
    return frame, labels


def _feature_frame(
    frame: pd.DataFrame,
    preprocessor: Any,
    schema: SpectrumSchema,
    feature_names: list[str],
) -> pd.DataFrame:
    transformed = preprocessor.transform(frame, schema)
    return transformed[feature_names]


def train(
    config: TrainingConfig,
    *,
    train_path: str | Path | None = None,
    validation_path: str | Path | None = None,
    test_path: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Train a model bundle and write it to ``output_dir``."""

    schema = SpectrumSchema(
        mz_col=config.data.mz_col,
        intensity_col=config.data.intensity_col,
        label_col=config.data.label_col,
        id_col=config.data.id_col,
    )
    train_source = train_path or config.data.train
    if train_source is None:
        raise ValueError("no training data path provided")
    validation_source = validation_path or config.data.validation
    test_source = test_path or config.data.test

    output = Path(output_dir or config.output_dir)
    if output.exists() and any(output.iterdir()):
        if not config.overwrite:
            raise FileExistsError(
                f"output directory is not empty: {output}; set overwrite=True to replace it"
            )
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    train_frame, train_labels = _load_labeled(train_source, schema)
    if validation_source is not None:
        validation_frame, validation_labels = _load_labeled(validation_source, schema)
    else:
        if not 0 < config.validation_size < 1:
            raise ValueError("validation_size must be between 0 and 1")
        train_frame, validation_frame, train_labels, validation_labels = train_test_split(
            train_frame,
            train_labels,
            test_size=config.validation_size,
            random_state=config.seed,
            stratify=train_labels,
        )

    preprocessor = config.preprocessing.build()
    preprocessor.fit(train_frame, mz_col=schema.mz_col)
    feature_names = list(preprocessor.feature_names_)

    train_features = _feature_frame(train_frame, preprocessor, schema, feature_names)
    validation_features = _feature_frame(
        validation_frame, preprocessor, schema, feature_names
    )

    backend = create_backend(config.model.backend, config.model.to_backend_params())
    backend.fit(
        train_features,
        pd.Series(train_labels, index=train_features.index),
        output / "backend",
    )

    train_scores = backend.predict_proba(train_features)
    validation_scores = backend.predict_proba(validation_features)

    thresholds = select_thresholds(
        validation_labels,
        validation_scores,
        high_fpr=config.threshold_high_fpr,
    )
    mid_threshold = float(thresholds["mid"]["value"])

    metrics: dict[str, Any] = {
        "train": evaluate_metrics(
            train_labels,
            train_scores,
            threshold=mid_threshold,
            with_bootstrap=False,
            seed=config.seed,
        ),
        "validation": evaluate_metrics(
            validation_labels,
            validation_scores,
            threshold=mid_threshold,
            with_bootstrap=config.with_bootstrap,
            n_boot=config.n_boot,
            seed=config.seed,
        ),
    }

    test_labels: np.ndarray | None = None
    if test_source is not None:
        test_frame = prepare_frame(read_frame(test_source, schema), schema)
        if schema.label_col in test_frame.columns:
            test_labels = coerce_binary_labels(
                test_frame[schema.label_col], schema.label_col
            )
        test_features = _feature_frame(test_frame, preprocessor, schema, feature_names)
        test_scores = backend.predict_proba(test_features)
        if test_labels is not None and np.unique(test_labels).size == 2:
            metrics["test"] = evaluate_metrics(
                test_labels,
                test_scores,
                threshold=mid_threshold,
                with_bootstrap=config.with_bootstrap,
                n_boot=config.n_boot,
                seed=config.seed,
            )

    metadata: dict[str, Any] = {
        "package": "flavfinder-core",
        "package_version": __version__,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "backend": config.model.backend,
        "preprocessing_method": config.preprocessing.method,
        "feature_names": feature_names,
        "schema": {
            "mz_col": schema.mz_col,
            "intensity_col": schema.intensity_col,
            "label_col": schema.label_col,
            "id_col": schema.id_col,
        },
        "config": config.to_dict(),
        "data": {
            "train": str(train_source),
            "validation": str(validation_source) if validation_source else None,
            "test": str(test_source) if test_source else None,
            "n_train": int(len(train_frame)),
            "n_validation": int(len(validation_frame)),
            "n_test": int(len(test_frame)) if test_source is not None else None,
            "positive_rate_train": float(np.mean(train_labels)),
            "positive_rate_validation": float(np.mean(validation_labels)),
        },
        "metrics": {
            name: {
                key: value
                for key, value in split_metrics.items()
                if key in {"n", "positive_rate", "auroc", "auprc", "brier"}
            }
            for name, split_metrics in metrics.items()
        },
        "python_version": platform.python_version(),
    }

    bundle = ModelBundle(
        preprocessor=preprocessor,
        backend=backend,
        metadata=metadata,
        thresholds=thresholds,
    )
    bundle.save(output)
    save_json(metrics, output / "metrics.json")
    return metrics
