"""Fixed-width m/z binning transformer."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from flavfinder.io import (
    SpectrumSchema,
    load_json,
    parse_peak_values,
    prepare_frame,
    save_json,
)

Normalization = Literal["none", "max", "l2"]
OutOfRange = Literal["drop", "error", "clip"]


class BinningTransformer:
    """Bin spectra onto a fixed m/z grid.

    Parameters
    ----------
    mz_min, mz_max, bin_width:
        Grid definition. The grid has ``round((mz_max - mz_min) / bin_width)``
        bins, centered at ``mz_min + i * bin_width``.
    normalization:
        Per-spectrum intensity normalization: ``none``, ``max``, or ``l2``.
    out_of_range:
        How to handle peaks outside the grid: ``drop`` (default), ``error``,
        or ``clip``.
    dtype:
        Output dtype. ``float64`` preserves full precision; ``float32`` halves memory use.
    """

    method = "binning"
    _STATE_VERSION = 1

    def __init__(
        self,
        mz_min: float = 10.0,
        mz_max: float = 500.0,
        bin_width: float = 0.1,
        normalization: Normalization = "max",
        out_of_range: OutOfRange = "drop",
        dtype: Literal["float32", "float64"] = "float64",
    ) -> None:
        if float(mz_max) <= float(mz_min):
            raise ValueError("mz_max must be greater than mz_min")
        if float(bin_width) <= 0:
            raise ValueError("bin_width must be positive")
        if normalization not in {"none", "max", "l2"}:
            raise ValueError("normalization must be one of: none, max, l2")
        if out_of_range not in {"drop", "error", "clip"}:
            raise ValueError("out_of_range must be one of: drop, error, clip")
        if dtype not in {"float32", "float64"}:
            raise ValueError("dtype must be float32 or float64")

        self.mz_min = float(mz_min)
        self.mz_max = float(mz_max)
        self.bin_width = float(bin_width)
        self.normalization = normalization
        self.out_of_range = out_of_range
        self.dtype = dtype
        self.n_bins = int(round((self.mz_max - self.mz_min) / self.bin_width))
        if self.n_bins <= 0:
            raise ValueError("grid must contain at least one bin")

    @property
    def bin_centers(self) -> np.ndarray:
        return self.mz_min + np.arange(self.n_bins, dtype=float) * self.bin_width

    @property
    def feature_names_(self) -> list[str]:
        return [f"bin_{index:04d}" for index in range(self.n_bins)]

    @property
    def n_features(self) -> int:
        return self.n_bins

    def fit(self, X: Any = None, y: Any = None, **kwargs: Any) -> BinningTransformer:
        """Binning has no learned parameters; provided for API consistency."""

        return self

    def _normalize(self, values: np.ndarray) -> np.ndarray:
        if self.normalization == "none":
            return values
        if self.normalization == "max":
            maximum = float(values.max())
            return values / maximum if maximum > 0 else values
        norm = float(np.linalg.norm(values))
        return values / norm if norm > 0 else values

    def transform_peaks(self, mzs: Any, intensities: Any) -> np.ndarray:
        """Transform one spectrum into a fixed-length vector."""

        mz = parse_peak_values(mzs, name="mz")
        intensity = parse_peak_values(intensities, name="intensity")
        if mz.size != intensity.size:
            raise ValueError(
                f"mz and intensity lengths differ ({mz.size} vs {intensity.size})"
            )

        indices = np.rint((mz - self.mz_min) / self.bin_width).astype(np.int64)
        valid = (indices >= 0) & (indices < self.n_bins)
        if not np.all(valid):
            if self.out_of_range == "error":
                count = int((~valid).sum())
                raise ValueError(
                    f"{count} peak(s) outside [{self.mz_min}, {self.mz_max}]"
                )
            if self.out_of_range == "clip":
                indices = np.clip(indices, 0, self.n_bins - 1)
                valid = np.ones_like(valid, dtype=bool)

        out = np.bincount(
            indices[valid],
            weights=intensity[valid],
            minlength=self.n_bins,
        ).astype(self.dtype, copy=False)
        return self._normalize(out)

    def transform(
        self,
        frame: pd.DataFrame,
        schema: SpectrumSchema | None = None,
    ) -> pd.DataFrame:
        """Transform every row of a spectrum frame into bin features."""

        schema = schema or SpectrumSchema()
        prepared = prepare_frame(frame, schema)
        rows = [
            self.transform_peaks(mz, intensity)
            for mz, intensity in zip(
                prepared["_mz_values"], prepared["_intensity_values"], strict=True
            )
        ]
        features = pd.DataFrame(
            np.vstack(rows) if rows else np.empty((0, self.n_bins), dtype=self.dtype),
            columns=self.feature_names_,
            index=prepared.index,
        )
        if schema.label_col in prepared.columns:
            features[schema.label_col] = prepared[schema.label_col]
        return features

    def fit_transform(
        self,
        frame: pd.DataFrame,
        schema: SpectrumSchema | None = None,
    ) -> pd.DataFrame:
        return self.fit(frame).transform(frame, schema)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "version": self._STATE_VERSION,
            "mz_min": self.mz_min,
            "mz_max": self.mz_max,
            "bin_width": self.bin_width,
            "normalization": self.normalization,
            "out_of_range": self.out_of_range,
            "dtype": self.dtype,
            "n_bins": self.n_bins,
            "feature_names": self.feature_names_,
        }

    @classmethod
    def from_dict(cls, state: dict[str, Any]) -> BinningTransformer:
        return cls(
            mz_min=state["mz_min"],
            mz_max=state["mz_max"],
            bin_width=state["bin_width"],
            normalization=state.get("normalization", "max"),
            out_of_range=state.get("out_of_range", "drop"),
            dtype=state.get("dtype", "float64"),
        )

    def save(self, path: str | Path) -> None:
        save_json(self.to_dict(), path)

    @classmethod
    def load(cls, path: str | Path) -> BinningTransformer:
        return cls.from_dict(load_json(path))

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(mz_min={self.mz_min}, mz_max={self.mz_max}, "
            f"bin_width={self.bin_width}, normalization={self.normalization!r}, "
            f"out_of_range={self.out_of_range!r})"
        )


# Backwards-compatible alias.
DataBinner = BinningTransformer
