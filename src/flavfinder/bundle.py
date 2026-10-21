"""Serializable bundle combining a preprocessor and a model backend."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from flavfinder.backends import ModelBackend, load_backend
from flavfinder.io import (
    SpectrumSchema,
    load_json,
    prepare_frame,
    read_frame,
    save_json,
    write_frame,
)
from flavfinder.metrics import probability_bucket
from flavfinder.preprocessing import Preprocessor, load_preprocessor


@dataclass
class ModelBundle:
    """A preprocessor, a fitted backend, and JSON metadata."""

    preprocessor: Preprocessor
    backend: ModelBackend
    metadata: dict[str, Any] = field(default_factory=dict)
    thresholds: dict[str, Any] | None = None

    @property
    def feature_names(self) -> list[str]:
        names = self.metadata.get("feature_names")
        return list(names) if names else list(self.preprocessor.feature_names_)

    def predict_frame(
        self,
        frame: pd.DataFrame,
        schema: SpectrumSchema | None = None,
    ) -> pd.DataFrame:
        """Add ``score`` and, when thresholds exist, ``probability`` columns."""

        schema = schema or SpectrumSchema()
        prepared = prepare_frame(frame, schema)
        transformed = self.preprocessor.transform(prepared, schema)
        features = transformed[self.feature_names]
        scores = self.backend.predict_proba(features)
        output = frame.copy()
        output["score"] = scores
        if self.thresholds:
            output["probability"] = probability_bucket(scores, self.thresholds)
        return output

    def predict_file(
        self,
        input_path: str | Path,
        output_path: str | Path,
        schema: SpectrumSchema | None = None,
    ) -> pd.DataFrame:
        schema = schema or SpectrumSchema()
        frame = read_frame(input_path, schema)
        output = self.predict_frame(frame, schema)
        write_frame(output, output_path)
        return output

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        self.preprocessor.save(path / "preprocessing.json")
        self.backend.save(path / "backend")
        save_json(self.metadata, path / "metadata.json")
        if self.thresholds is not None:
            save_json(self.thresholds, path / "thresholds.json")

    @classmethod
    def load(cls, path: str | Path) -> ModelBundle:
        path = Path(path)
        metadata = load_json(path / "metadata.json")
        preprocessor = load_preprocessor(path / "preprocessing.json")
        backend = load_backend(metadata["backend"], path / "backend")
        thresholds_path = path / "thresholds.json"
        thresholds = load_json(thresholds_path) if thresholds_path.exists() else None
        return cls(
            preprocessor=preprocessor,
            backend=backend,
            metadata=metadata,
            thresholds=thresholds,
        )

    @property
    def backend_name(self) -> str:
        return str(self.metadata.get("backend", self.backend.name))
