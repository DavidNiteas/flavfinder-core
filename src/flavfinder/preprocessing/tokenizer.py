"""Learned m/z tokenizer with tolerance-based vocabulary merging."""

from __future__ import annotations

from collections.abc import Iterable
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
from flavfinder.utils import as_float_array, is_same_mz, mz_tolerance

Normalization = Literal["none", "max", "l2"]


def _iter_mz_values(data: Any, mz_col: str = "mz") -> Iterable[float]:
    if isinstance(data, pd.DataFrame):
        prepared = prepare_frame(data, SpectrumSchema(mz_col=mz_col))
        for values in prepared["_mz_values"]:
            yield from values
        return
    if np.isscalar(data):
        yield float(data)
        return
    for item in data:
        if isinstance(item, str):
            yield from parse_peak_values(item, name="mz")
        elif isinstance(item, list | tuple | np.ndarray | pd.Series):
            yield from as_float_array(item, name="mz")
        else:
            yield float(item)


class FlavTokenizer:
    """Learn a vocabulary of m/z values and map peaks to token weights.

    Token ``0`` is reserved for unknown peaks. Learned m/z values start at
    token ``1``. When ``merge_mz_within_tol`` is true, consecutive sorted m/z
    values within the tolerance of the current cluster mean are merged into a
    single vocabulary entry.
    """

    method = "tokenization"
    _STATE_VERSION = 1
    unk_token = 0

    def __init__(
        self,
        mz_tol: float = 5.0,
        mz_tol_unit: str = "ppm",
        normalization: Normalization = "max",
        accumulate_unknown: bool = True,
    ) -> None:
        if float(mz_tol) < 0:
            raise ValueError("mz_tol must be non-negative")
        if mz_tol_unit.lower() not in {"ppm", "%", "abs", "da"}:
            raise ValueError("mz_tol_unit must be one of: 'ppm', '%', 'abs', 'Da'")
        if normalization not in {"none", "max", "l2"}:
            raise ValueError("normalization must be one of: none, max, l2")
        self.mz_tol = float(mz_tol)
        self.mz_tol_unit = str(mz_tol_unit)
        self.normalization = normalization
        self.accumulate_unknown = bool(accumulate_unknown)
        self.mzs_: np.ndarray = np.array([], dtype=float)

    @property
    def n_tokens(self) -> int:
        return len(self.mzs_) + 1

    @property
    def n_features(self) -> int:
        return self.n_tokens

    @property
    def feature_names_(self) -> list[str]:
        return ["UNK"] + [f"mz_{mz:.4f}" for mz in self.mzs_]

    def fit(
        self,
        data: Any,
        *,
        mz_col: str = "mz",
        merge_mz_within_tol: bool = True,
    ) -> FlavTokenizer:
        values = sorted({float(value) for value in _iter_mz_values(data, mz_col)})
        if not values:
            raise ValueError("cannot fit tokenizer on empty m/z values")
        if not np.all(np.isfinite(values)):
            raise ValueError("m/z values contain non-finite values")
        if np.any(np.asarray(values) < 0):
            raise ValueError("m/z values must be non-negative")

        if merge_mz_within_tol:
            clusters: list[list[float]] = [[values[0]]]
            for value in values[1:]:
                center = float(np.mean(clusters[-1]))
                if is_same_mz(value, center, self.mz_tol, self.mz_tol_unit):
                    clusters[-1].append(value)
                else:
                    clusters.append([value])
            self.mzs_ = np.asarray([np.mean(cluster) for cluster in clusters], dtype=float)
        else:
            self.mzs_ = np.asarray(values, dtype=float)
        return self

    def _nearest_tokens(self, mz: np.ndarray) -> np.ndarray:
        if self.mzs_.size == 0:
            raise ValueError("tokenizer is not fitted")
        right = np.searchsorted(self.mzs_, mz)
        left = np.clip(right - 1, 0, self.mzs_.size - 1)
        right = np.clip(right, 0, self.mzs_.size - 1)
        choose_left = np.abs(mz - self.mzs_[left]) <= np.abs(mz - self.mzs_[right])
        nearest = np.where(choose_left, left, right)
        within = np.abs(mz - self.mzs_[nearest]) <= mz_tolerance(
            mz, self.mz_tol, self.mz_tol_unit
        )
        return np.where(within, nearest + 1, self.unk_token).astype(np.int64)

    def _normalize(self, values: np.ndarray) -> np.ndarray:
        if self.normalization == "none":
            return values
        if self.normalization == "max":
            maximum = float(values.max()) if values.size else 0.0
            return values / maximum if maximum > 0 else values
        norm = float(np.linalg.norm(values))
        return values / norm if norm > 0 else values

    def transform_peaks(self, mzs: Any, intensities: Any) -> np.ndarray:
        mz = parse_peak_values(mzs, name="mz")
        intensity = parse_peak_values(intensities, name="intensity")
        if mz.size != intensity.size:
            raise ValueError(
                f"mz and intensity lengths differ ({mz.size} vs {intensity.size})"
            )
        order = np.argsort(mz)
        mz = mz[order]
        intensity = intensity[order]
        tokens = self._nearest_tokens(mz)
        out = np.bincount(tokens, weights=intensity, minlength=self.n_tokens).astype(
            np.float64, copy=False
        )
        if not self.accumulate_unknown:
            out[self.unk_token] = 0.0
        return self._normalize(out)

    def transform(
        self,
        frame: pd.DataFrame,
        schema: SpectrumSchema | None = None,
    ) -> pd.DataFrame:
        schema = schema or SpectrumSchema()
        prepared = prepare_frame(frame, schema)
        rows = [
            self.transform_peaks(mz, intensity)
            for mz, intensity in zip(
                prepared["_mz_values"], prepared["_intensity_values"], strict=True
            )
        ]
        features = pd.DataFrame(
            np.vstack(rows) if rows else np.empty((0, self.n_tokens)),
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
        *,
        merge_mz_within_tol: bool = True,
    ) -> pd.DataFrame:
        return self.fit(
            frame,
            mz_col=(schema or SpectrumSchema()).mz_col,
            merge_mz_within_tol=merge_mz_within_tol,
        ).transform(frame, schema)

    def mz_to_token(self, mz: float) -> int:
        return int(self._nearest_tokens(np.asarray([float(mz)], dtype=float))[0])

    def token_to_mz(self, token: int) -> str:
        if token == self.unk_token:
            return "UNK"
        index = int(token) - 1
        if index < 0 or index >= self.mzs_.size:
            raise KeyError(f"unknown token: {token}")
        return str(self.mzs_[index])

    def mzs_to_tokens(self, mzs: Iterable[float]) -> list[int]:
        return [self.mz_to_token(mz) for mz in mzs]

    def tokens_to_mzs(self, tokens: Iterable[int]) -> list[str]:
        return [self.token_to_mz(token) for token in tokens]

    def __call__(self, mz: Any) -> Any:
        if np.isscalar(mz):
            return self.mz_to_token(float(mz))
        return self.mzs_to_tokens(mz)

    def __len__(self) -> int:
        return self.n_tokens

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "version": self._STATE_VERSION,
            "mz_tol": self.mz_tol,
            "mz_tol_unit": self.mz_tol_unit,
            "normalization": self.normalization,
            "accumulate_unknown": self.accumulate_unknown,
            "mzs": self.mzs_.tolist(),
            "feature_names": self.feature_names_,
        }

    @classmethod
    def from_dict(cls, state: dict[str, Any]) -> FlavTokenizer:
        tokenizer = cls(
            mz_tol=state["mz_tol"],
            mz_tol_unit=state["mz_tol_unit"],
            normalization=state.get("normalization", "max"),
            accumulate_unknown=state.get("accumulate_unknown", True),
        )
        tokenizer.mzs_ = np.asarray(state.get("mzs", []), dtype=float)
        return tokenizer

    def save(self, path: str | Path) -> None:
        save_json(self.to_dict(), path)

    @classmethod
    def load(cls, path: str | Path) -> FlavTokenizer:
        return cls.from_dict(load_json(path))

    @classmethod
    def from_json(cls, path: str | Path) -> FlavTokenizer:
        """Backwards-compatible alias for :meth:`load`."""

        return cls.load(path)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(n_tokens={self.n_tokens}, "
            f"mz_tol={self.mz_tol}, mz_tol_unit={self.mz_tol_unit!r}, "
            f"normalization={self.normalization!r})"
        )
