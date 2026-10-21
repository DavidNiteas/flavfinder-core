"""Typed configuration objects for training and evaluation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

import yaml

from flavfinder.io import save_json
from flavfinder.preprocessing import Preprocessor, preprocessor_from_params


def _reject_unknown(cls: type, data: dict[str, Any]) -> None:
    allowed = {item.name for item in fields(cls)}
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValueError(f"unknown {cls.__name__} field(s): {', '.join(unknown)}")


@dataclass
class DataConfig:
    train: str | None = None
    validation: str | None = None
    test: str | None = None
    mz_col: str = "mz"
    intensity_col: str = "intensity"
    label_col: str = "label"
    id_col: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> DataConfig:
        data = data or {}
        _reject_unknown(cls, data)
        return cls(**data)


@dataclass
class PreprocessingConfig:
    method: str = "binning"
    mz_min: float = 10.0
    mz_max: float = 500.0
    bin_width: float = 0.1
    mz_tol: float = 5.0
    mz_tol_unit: str = "ppm"
    normalization: str = "max"
    out_of_range: str = "drop"
    accumulate_unknown: bool = True
    dtype: str = "float64"

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> PreprocessingConfig:
        data = data or {}
        _reject_unknown(cls, data)
        return cls(**data)

    def to_params(self) -> dict[str, Any]:
        if self.method == "binning":
            return {
                "mz_min": self.mz_min,
                "mz_max": self.mz_max,
                "bin_width": self.bin_width,
                "normalization": self.normalization,
                "out_of_range": self.out_of_range,
                "dtype": self.dtype,
            }
        if self.method == "tokenization":
            return {
                "mz_tol": self.mz_tol,
                "mz_tol_unit": self.mz_tol_unit,
                "normalization": self.normalization,
                "accumulate_unknown": self.accumulate_unknown,
            }
        raise ValueError(f"unknown preprocessing method: {self.method!r}")

    def build(self) -> Preprocessor:
        return preprocessor_from_params(self.method, self.to_params())


@dataclass
class ModelConfig:
    backend: str = "autogluon"
    eval_metric: str = "roc_auc"
    presets: str | list[str] | None = "optimize_for_deployment"
    time_limit: float | None = None
    random_state: int = 42
    params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ModelConfig:
        data = data or {}
        _reject_unknown(cls, data)
        return cls(**data)

    def to_backend_params(self) -> dict[str, Any]:
        params = dict(self.params)
        params.setdefault("random_state", self.random_state)
        if self.backend == "autogluon":
            params.setdefault("eval_metric", self.eval_metric)
            if self.presets is not None:
                params.setdefault("presets", self.presets)
            if self.time_limit is not None:
                params.setdefault("time_limit", self.time_limit)
        return params


@dataclass
class TrainingConfig:
    data: DataConfig = field(default_factory=DataConfig)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    output_dir: str = "artifacts/model"
    validation_size: float = 0.2
    threshold_high_fpr: float = 0.01
    seed: int = 42
    overwrite: bool = False
    with_bootstrap: bool = True
    n_boot: int = 1000

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrainingConfig:
        _reject_unknown(cls, data)
        return cls(
            data=DataConfig.from_dict(data.get("data")),
            preprocessing=PreprocessingConfig.from_dict(data.get("preprocessing")),
            model=ModelConfig.from_dict(data.get("model")),
            output_dir=data.get("output_dir", "artifacts/model"),
            validation_size=float(data.get("validation_size", 0.2)),
            threshold_high_fpr=float(data.get("threshold_high_fpr", 0.01)),
            seed=int(data.get("seed", 42)),
            overwrite=bool(data.get("overwrite", False)),
            with_bootstrap=bool(data.get("with_bootstrap", True)),
            n_boot=int(data.get("n_boot", 1000)),
        )

    @classmethod
    def from_yaml(cls, path: str | Path) -> TrainingConfig:
        with Path(path).open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        if not isinstance(data, dict):
            raise ValueError(f"expected a YAML mapping in {path}")
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_yaml(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(self.to_dict(), handle, sort_keys=False, allow_unicode=True)

    def save_json(self, path: str | Path) -> None:
        save_json(self.to_dict(), path)
