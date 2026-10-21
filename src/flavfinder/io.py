"""Reading, validating, and writing spectrum tables."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from flavfinder.utils import as_float_array

_MZ_VALUES = "_mz_values"
_INTENSITY_VALUES = "_intensity_values"


@dataclass(frozen=True)
class SpectrumSchema:
    """Column names and optional identifier for a spectrum table."""

    mz_col: str = "mz"
    intensity_col: str = "intensity"
    label_col: str = "label"
    id_col: str | None = None

    def required_columns(self) -> list[str]:
        return [self.mz_col, self.intensity_col]


def read_frame(path: str | Path, schema: SpectrumSchema | None = None) -> pd.DataFrame:
    """Read a CSV or JSON spectrum table."""

    schema = schema or SpectrumSchema()
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        frame = pd.read_csv(path)
    elif suffix in {".json", ".jsonl"}:
        try:
            frame = pd.read_json(path, orient="records" if suffix == ".jsonl" else None)
        except ValueError:
            frame = pd.read_json(path, orient="records")
    else:
        raise ValueError(f"unsupported input type: {suffix!r}; use .csv or .json")
    missing = [col for col in schema.required_columns() if col not in frame.columns]
    if missing:
        raise ValueError(f"missing required column(s): {', '.join(missing)}")
    return frame


def parse_peak_values(value: Any, *, name: str = "peak values") -> np.ndarray:
    """Parse a comma-separated string, list, tuple, or array of numbers."""

    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError(f"{name} must not be empty")
        parts = [part.strip() for part in text.split(",")]
        if any(not part for part in parts):
            raise ValueError(f"{name} contains an empty value")
        return as_float_array(parts, name=name)
    if isinstance(value, list | tuple | np.ndarray | pd.Series):
        return as_float_array(value, name=name)
    raise TypeError(f"{name} must be a comma-separated string or a numeric sequence")


def prepare_frame(
    frame: pd.DataFrame,
    schema: SpectrumSchema | None = None,
    *,
    sort_mz: bool = True,
    require_label: bool = False,
) -> pd.DataFrame:
    """Validate spectra and attach parsed m/z and intensity arrays.

    The returned frame keeps the original columns and adds two object columns:
    ``_mz_values`` and ``_intensity_values``. Parsing is idempotent.
    """

    schema = schema or SpectrumSchema()
    if _MZ_VALUES in frame.columns and _INTENSITY_VALUES in frame.columns:
        prepared = frame.copy()
    else:
        missing = [col for col in schema.required_columns() if col not in frame.columns]
        if missing:
            raise ValueError(f"missing required column(s): {', '.join(missing)}")
        mz_values: list[np.ndarray] = []
        intensity_values: list[np.ndarray] = []
        for index, row in frame.iterrows():
            mz = parse_peak_values(row[schema.mz_col], name=f"row {index} mz")
            intensity = parse_peak_values(
                row[schema.intensity_col], name=f"row {index} intensity"
            )
            if mz.size != intensity.size:
                raise ValueError(
                    f"row {index}: mz and intensity lengths differ "
                    f"({mz.size} vs {intensity.size})"
                )
            if np.any(mz < 0):
                raise ValueError(f"row {index}: m/z values must be non-negative")
            if np.any(intensity < 0):
                raise ValueError(f"row {index}: intensities must be non-negative")
            if sort_mz:
                order = np.argsort(mz)
                mz = mz[order]
                intensity = intensity[order]
            mz_values.append(mz)
            intensity_values.append(intensity)
        prepared = frame.copy()
        prepared[_MZ_VALUES] = pd.Series(mz_values, index=frame.index, dtype=object)
        prepared[_INTENSITY_VALUES] = pd.Series(
            intensity_values, index=frame.index, dtype=object
        )

    if require_label and schema.label_col not in prepared.columns:
        raise ValueError(f"missing required label column: {schema.label_col}")
    return prepared


def get_spectra(frame: pd.DataFrame) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Return parsed m/z and intensity arrays from a prepared frame."""

    prepared = prepare_frame(frame)
    return (
        list(prepared[_MZ_VALUES]),
        list(prepared[_INTENSITY_VALUES]),
    )


def coerce_binary_labels(
    labels: pd.Series | np.ndarray,
    label_name: str = "label",
) -> np.ndarray:
    """Convert labels to a validated 1-D integer array of 0/1 values."""

    values = np.asarray(labels)
    if values.ndim != 1:
        raise ValueError(f"{label_name} must be one-dimensional")
    try:
        numeric = values.astype(int)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label_name} must contain integer 0/1 values") from exc
    if not np.all(np.isin(numeric, (0, 1))):
        raise ValueError(f"{label_name} must contain only 0 and 1")
    return numeric


def write_frame(frame: pd.DataFrame, path: str | Path) -> None:
    """Write a frame as CSV or JSON based on the suffix."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        frame.to_csv(path, index=False)
    elif suffix == ".json":
        frame.to_json(path, orient="records", indent=2)
    else:
        raise ValueError(f"unsupported output type: {suffix!r}; use .csv or .json")


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return data


def save_json(data: Any, path: str | Path, *, indent: int = 2) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=indent, ensure_ascii=False)
        handle.write("\n")
