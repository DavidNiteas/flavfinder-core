"""Independent, code-only implementation of the flavfinder MS/MS flavonoid classifier."""

# ruff: noqa: E402

from __future__ import annotations

__version__ = "0.2.1"

from flavfinder.bundle import ModelBundle
from flavfinder.chem import FlavonoidLabeler, LabelResult, label_frame
from flavfinder.config import (
    DataConfig,
    ModelConfig,
    PreprocessingConfig,
    TrainingConfig,
)
from flavfinder.data import (
    audit_frame,
    group_split_indices,
    groups_from_pairs,
    leakage_report,
    near_duplicate_pairs,
)
from flavfinder.io import SpectrumSchema, prepare_frame, read_frame, write_frame
from flavfinder.metrics import (
    binary_metrics,
    bootstrap_ci,
    calibration_points,
    evaluate_metrics,
    probability_bucket,
    select_thresholds,
)
from flavfinder.predict import predict
from flavfinder.preprocessing import (
    BinningTransformer,
    DataBinner,
    DataTransformer,
    FlavTokenizer,
)
from flavfinder.train import train

__all__ = [
    "BinningTransformer",
    "DataBinner",
    "DataConfig",
    "DataTransformer",
    "FlavTokenizer",
    "FlavonoidLabeler",
    "LabelResult",
    "ModelBundle",
    "ModelConfig",
    "PreprocessingConfig",
    "SpectrumSchema",
    "TrainingConfig",
    "__version__",
    "audit_frame",
    "binary_metrics",
    "bootstrap_ci",
    "calibration_points",
    "evaluate_metrics",
    "group_split_indices",
    "groups_from_pairs",
    "label_frame",
    "leakage_report",
    "near_duplicate_pairs",
    "predict",
    "prepare_frame",
    "probability_bucket",
    "read_frame",
    "select_thresholds",
    "train",
    "write_frame",
]
