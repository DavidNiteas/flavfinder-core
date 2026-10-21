from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from flavfinder.bundle import ModelBundle
from flavfinder.config import (
    DataConfig,
    ModelConfig,
    PreprocessingConfig,
    TrainingConfig,
)
from flavfinder.evaluate import evaluate
from flavfinder.predict import predict
from flavfinder.train import train


def _config(train_path: str, output_dir: Path, *, method: str = "binning") -> TrainingConfig:
    return TrainingConfig(
        data=DataConfig(train=train_path, test=train_path),
        preprocessing=PreprocessingConfig(method=method),
        model=ModelConfig(backend="sklearn", random_state=7),
        output_dir=str(output_dir),
        validation_size=0.25,
        with_bootstrap=False,
        seed=7,
        overwrite=True,
    )


def test_train_predict_evaluate(tmp_path, synthetic_csv) -> None:
    output = tmp_path / "model"
    metrics = train(_config(synthetic_csv, output))
    assert metrics["validation"]["auroc"] > 0.8
    for name in ("metadata.json", "preprocessing.json", "thresholds.json", "metrics.json"):
        assert (output / name).exists()

    predictions = predict(output, synthetic_csv)
    assert len(predictions) > 0
    assert predictions["score"].between(0, 1).all()
    assert set(predictions["probability"]) <= {"high", "mid", "low"}

    evaluation = evaluate(output, synthetic_csv, with_bootstrap=False)
    assert evaluation["auroc"] > 0.8
    assert "thresholds" in evaluation


def test_tokenization_pipeline(tmp_path, synthetic_csv) -> None:
    output = tmp_path / "model-token"
    metrics = train(_config(synthetic_csv, output, method="tokenization"))
    assert metrics["validation"]["auroc"] > 0.8
    bundle = ModelBundle.load(output)
    assert bundle.preprocessor.method == "tokenization"


def test_overwrite_protection(tmp_path, synthetic_csv) -> None:
    output = tmp_path / "model"
    config = _config(synthetic_csv, output)
    train(config)
    config.overwrite = False
    with pytest.raises(FileExistsError):
        train(config)


def test_missing_label_raises(tmp_path, synthetic_frame) -> None:
    path = tmp_path / "no-label.csv"
    synthetic_frame.drop(columns=["label"]).to_csv(path, index=False)
    with pytest.raises(ValueError, match="label"):
        train(_config(str(path), tmp_path / "model"))


def test_config_yaml_roundtrip(tmp_path) -> None:
    config = _config("train.csv", tmp_path / "model")
    path = tmp_path / "config.yaml"
    config.to_yaml(path)
    loaded = TrainingConfig.from_yaml(path)
    assert loaded.to_dict() == config.to_dict()


def test_metadata_records_feature_names(tmp_path, synthetic_csv) -> None:
    output = tmp_path / "model"
    train(_config(synthetic_csv, output))
    metadata = json.loads((output / "metadata.json").read_text())
    assert metadata["package"] == "flavfinder-core"
    assert len(metadata["feature_names"]) == 4900
    assert metadata["backend"] == "sklearn"
    assert np.isfinite(metadata["metrics"]["validation"]["auroc"])
