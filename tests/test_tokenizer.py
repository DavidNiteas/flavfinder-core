from __future__ import annotations

import pandas as pd
import pytest

from flavfinder.preprocessing import FlavTokenizer


def test_fit_merges_within_tolerance() -> None:
    tokenizer = FlavTokenizer(mz_tol=5.0, mz_tol_unit="ppm").fit(
        [100.0, 100.0002, 200.0]
    )
    assert tokenizer.n_tokens == 3
    assert len(tokenizer.mzs_) == 2


def test_fit_without_merging() -> None:
    tokenizer = FlavTokenizer(mz_tol=5.0, mz_tol_unit="ppm").fit(
        [100.0, 100.0002, 200.0], merge_mz_within_tol=False
    )
    assert tokenizer.n_tokens == 4


def test_unknown_token_accumulates_intensity() -> None:
    tokenizer = FlavTokenizer(
        mz_tol=5.0, mz_tol_unit="ppm", normalization="none"
    ).fit([100.0])
    vector = tokenizer.transform_peaks("100.0,150.0", "1,2")
    assert vector[0] == pytest.approx(2.0)
    assert vector[1] == pytest.approx(1.0)


def test_unknown_token_can_be_dropped() -> None:
    tokenizer = FlavTokenizer(
        mz_tol=5.0,
        mz_tol_unit="ppm",
        normalization="none",
        accumulate_unknown=False,
    ).fit([100.0])
    vector = tokenizer.transform_peaks("100.0,150.0", "1,2")
    assert vector[0] == 0.0


def test_token_mapping_helpers() -> None:
    tokenizer = FlavTokenizer(mz_tol=5.0, mz_tol_unit="ppm").fit([100.0, 200.0])
    assert tokenizer.mz_to_token(100.0) == 1
    assert tokenizer.token_to_mz(1) == "100.0"
    assert tokenizer.token_to_mz(0) == "UNK"
    assert tokenizer.mzs_to_tokens([100.0, 200.0]) == [1, 2]


def test_fit_rejects_empty() -> None:
    with pytest.raises(ValueError, match="empty"):
        FlavTokenizer().fit([])


def test_save_load_roundtrip(tmp_path) -> None:
    tokenizer = FlavTokenizer(mz_tol=10.0, mz_tol_unit="ppm").fit([100.0, 200.0])
    path = tmp_path / "tokenizer.json"
    tokenizer.save(path)
    loaded = FlavTokenizer.from_json(path)
    assert loaded.to_dict() == tokenizer.to_dict()
    assert loaded.transform_peaks("100,200", "1,2").shape == tokenizer.transform_peaks(
        "100,200", "1,2"
    ).shape


def test_transform_frame_includes_label() -> None:
    frame = pd.DataFrame({"mz": ["100,200"], "intensity": ["1,2"], "label": [1]})
    tokenizer = FlavTokenizer().fit(frame)
    transformed = tokenizer.transform(frame)
    assert transformed.shape == (1, tokenizer.n_tokens + 1)
    assert transformed["label"].iloc[0] == 1


def test_invalid_parameters() -> None:
    with pytest.raises(ValueError):
        FlavTokenizer(mz_tol=-1)
    with pytest.raises(ValueError):
        FlavTokenizer(mz_tol_unit="furlong")
    with pytest.raises(ValueError):
        FlavTokenizer(normalization="min")
