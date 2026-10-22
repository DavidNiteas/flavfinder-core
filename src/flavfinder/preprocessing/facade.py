"""Facade preserving the ``DataTransformer`` entry point."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from flavfinder.io import SpectrumSchema, read_frame
from flavfinder.preprocessing.binning import BinningTransformer, DataBinner
from flavfinder.preprocessing.tokenizer import FlavTokenizer

Preprocessor = BinningTransformer | FlavTokenizer


class DataTransformer:
    """Small facade over a binning or tokenization preprocessor."""

    def __init__(
        self,
        transformer: Preprocessor | None = None,
        *,
        tokenizer: FlavTokenizer | None = None,
    ) -> None:
        if transformer is None:
            transformer = tokenizer
        if transformer is None:
            raise ValueError("a BinningTransformer or FlavTokenizer is required")
        self.transformer = transformer

    @property
    def feature_names_(self) -> list[str]:
        return list(self.transformer.feature_names_)

    def transform_peaks(self, mzs: Any, intensities: Any) -> Any:
        return self.transformer.transform_peaks(mzs, intensities)

    def transform_df(
        self,
        frame: pd.DataFrame,
        mz_col: str = "mz",
        intensity_col: str = "intensity",
        label_col: str = "label",
    ) -> pd.DataFrame:
        schema = SpectrumSchema(
            mz_col=mz_col,
            intensity_col=intensity_col,
            label_col=label_col,
        )
        return self.transformer.transform(frame, schema)

    def transform_json(
        self,
        json_path: str | Path,
        mz_col: str = "mz",
        intensity_col: str = "intensity",
        label_col: str = "label",
    ) -> pd.DataFrame:
        schema = SpectrumSchema(
            mz_col=mz_col,
            intensity_col=intensity_col,
            label_col=label_col,
        )
        return self.transform_df(read_frame(json_path, schema), mz_col, intensity_col, label_col)


__all__ = ["BinningTransformer", "DataBinner", "DataTransformer", "FlavTokenizer"]
