"""Preprocessing transformers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from flavfinder.io import load_json
from flavfinder.preprocessing.binning import BinningTransformer, DataBinner
from flavfinder.preprocessing.facade import DataTransformer, Preprocessor
from flavfinder.preprocessing.tokenizer import FlavTokenizer


def load_preprocessor(path: str | Path) -> Preprocessor:
    """Load a saved preprocessor from its JSON state file."""

    state = load_json(path)
    method = state.get("method")
    if method == "binning":
        return BinningTransformer.from_dict(state)
    if method == "tokenization":
        return FlavTokenizer.from_dict(state)
    raise ValueError(f"unknown preprocessing method: {method!r}")


def preprocessor_from_params(method: str, params: dict[str, Any]) -> Preprocessor:
    """Build a preprocessor from a method name and parameter mapping."""

    if method == "binning":
        return BinningTransformer(**params)
    if method == "tokenization":
        return FlavTokenizer(**params)
    raise ValueError(f"unknown preprocessing method: {method!r}")


__all__ = [
    "BinningTransformer",
    "DataBinner",
    "DataTransformer",
    "FlavTokenizer",
    "Preprocessor",
    "load_preprocessor",
    "preprocessor_from_params",
]
