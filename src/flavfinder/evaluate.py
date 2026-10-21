"""Evaluation entry points."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from flavfinder.bundle import ModelBundle
from flavfinder.io import (
    SpectrumSchema,
    coerce_binary_labels,
    prepare_frame,
    read_frame,
    save_json,
)
from flavfinder.metrics import evaluate_metrics


def evaluate(
    model_dir: str | Path,
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    schema: SpectrumSchema | None = None,
    with_bootstrap: bool = True,
    n_boot: int = 1000,
    seed: int = 42,
) -> dict[str, Any]:
    """Evaluate a saved model bundle on a labeled spectrum table."""

    bundle = ModelBundle.load(model_dir)
    if schema is None:
        schema_data = bundle.metadata.get("schema", {})
        schema = SpectrumSchema(
            mz_col=schema_data.get("mz_col", "mz"),
            intensity_col=schema_data.get("intensity_col", "intensity"),
            label_col=schema_data.get("label_col", "label"),
            id_col=schema_data.get("id_col"),
        )
    frame = prepare_frame(read_frame(input_path, schema), schema, require_label=True)
    labels = coerce_binary_labels(frame[schema.label_col], schema.label_col)
    output = bundle.predict_frame(frame, schema)
    scores = output["score"].to_numpy(dtype=float)
    threshold = 0.5
    if bundle.thresholds:
        threshold = float(bundle.thresholds["mid"]["value"])
    metrics = evaluate_metrics(
        labels,
        scores,
        threshold=threshold,
        with_bootstrap=with_bootstrap,
        n_boot=n_boot,
        seed=seed,
    )
    metrics["thresholds"] = bundle.thresholds
    if output_path is not None:
        save_json(metrics, output_path)
    return metrics
