"""Prediction entry points."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from flavfinder.bundle import ModelBundle
from flavfinder.io import SpectrumSchema, read_frame, write_frame


def predict(
    model_dir: str | Path,
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    schema: SpectrumSchema | None = None,
) -> pd.DataFrame:
    """Load a model bundle and score every spectrum in ``input_path``."""

    bundle = ModelBundle.load(model_dir)
    if schema is None:
        schema_data = bundle.metadata.get("schema", {})
        schema = SpectrumSchema(
            mz_col=schema_data.get("mz_col", "mz"),
            intensity_col=schema_data.get("intensity_col", "intensity"),
            label_col=schema_data.get("label_col", "label"),
            id_col=schema_data.get("id_col"),
        )
    frame = read_frame(input_path, schema)
    output = bundle.predict_frame(frame, schema)
    if output_path is not None:
        write_frame(output, output_path)
    return output
