from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from flavfinder.preprocessing import BinningTransformer


def test_shape_features_and_label() -> None:
    frame = pd.DataFrame({"mz": ["100,200"], "intensity": ["1,2"], "label": [1]})
    transformer = BinningTransformer()
    transformed = transformer.transform(frame)
    assert transformed.shape == (1, transformer.n_bins + 1)
    assert transformed["label"].iloc[0] == 1
    assert transformer.feature_names_[0] == "bin_0000"


def test_peak_binning_and_max_normalization() -> None:
    transformer = BinningTransformer(mz_min=10.0, mz_max=10.3, bin_width=0.1)
    vector = transformer.transform_peaks("10.0,10.2", "50,100")
    assert vector.shape == (3,)
    assert np.allclose(vector, [0.5, 0.0, 1.0])


def test_none_and_l2_normalization() -> None:
    raw = BinningTransformer(
        mz_min=10.0, mz_max=10.2, bin_width=0.1, normalization="none"
    ).transform_peaks("10.0,10.1", "3,4")
    assert np.allclose(raw, [3.0, 4.0])
    l2 = BinningTransformer(
        mz_min=10.0, mz_max=10.2, bin_width=0.1, normalization="l2"
    ).transform_peaks("10.0,10.1", "3,4")
    assert np.allclose(l2, [0.6, 0.8])


def test_all_zero_intensity_is_finite() -> None:
    vector = BinningTransformer(mz_min=10.0, mz_max=10.2, bin_width=0.1).transform_peaks(
        "10.0", "0"
    )
    assert np.all(np.isfinite(vector))
    assert np.allclose(vector, 0.0)


def test_out_of_range_drop_error_clip() -> None:
    dropped = BinningTransformer(
        mz_min=10.0,
        mz_max=11.0,
        bin_width=0.1,
        normalization="none",
        out_of_range="drop",
    ).transform_peaks("9.0,10.0,20.0", "1,2,3")
    assert dropped.sum() == 2.0
    with pytest.raises(ValueError, match="outside"):
        BinningTransformer(
            mz_min=10.0, mz_max=11.0, bin_width=0.1, out_of_range="error"
        ).transform_peaks("20.0", "1")
    clipped = BinningTransformer(
        mz_min=10.0, mz_max=11.0, bin_width=0.1, out_of_range="clip"
    ).transform_peaks("20.0", "1")
    assert clipped[-1] == 1.0


def test_transform_peaks_accepts_lists() -> None:
    transformer = BinningTransformer(
        mz_min=10.0, mz_max=10.2, bin_width=0.1, normalization="none"
    )
    assert np.allclose(transformer.transform_peaks([10.0, 10.1], [1, 2]), [1.0, 2.0])


def test_save_load_roundtrip(tmp_path) -> None:
    transformer = BinningTransformer(mz_min=10.0, mz_max=11.0, bin_width=0.1)
    path = tmp_path / "binning.json"
    transformer.save(path)
    loaded = BinningTransformer.load(path)
    assert loaded.to_dict() == transformer.to_dict()


def test_invalid_parameters() -> None:
    with pytest.raises(ValueError):
        BinningTransformer(mz_min=10.0, mz_max=10.0)
    with pytest.raises(ValueError):
        BinningTransformer(normalization="min")
    with pytest.raises(ValueError):
        BinningTransformer(out_of_range="ignore")
