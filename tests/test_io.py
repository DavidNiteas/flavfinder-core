from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from flavfinder.io import (
    SpectrumSchema,
    coerce_binary_labels,
    parse_peak_values,
    prepare_frame,
    read_frame,
    write_frame,
)


def test_parse_peak_values_supports_strings_and_lists() -> None:
    assert np.allclose(parse_peak_values("1.0, 2.0,3.0"), [1.0, 2.0, 3.0])
    assert np.allclose(parse_peak_values([1.0, 2.0]), [1.0, 2.0])


def test_parse_peak_values_rejects_bad_input() -> None:
    with pytest.raises(ValueError):
        parse_peak_values("")
    with pytest.raises(ValueError):
        parse_peak_values("1,,2")
    with pytest.raises(TypeError):
        parse_peak_values(1.0)


def test_prepare_frame_sorts_and_validates() -> None:
    frame = pd.DataFrame({"mz": ["200,100"], "intensity": ["2,1"], "label": [1]})
    prepared = prepare_frame(frame)
    assert np.allclose(prepared["_mz_values"].iloc[0], [100.0, 200.0])
    assert np.allclose(prepared["_intensity_values"].iloc[0], [1.0, 2.0])


def test_prepare_frame_rejects_mismatched_lengths() -> None:
    frame = pd.DataFrame({"mz": ["100,200"], "intensity": ["1"]})
    with pytest.raises(ValueError, match="lengths differ"):
        prepare_frame(frame)


def test_prepare_frame_rejects_negative_values() -> None:
    frame = pd.DataFrame({"mz": ["100"], "intensity": ["-1"]})
    with pytest.raises(ValueError, match="non-negative"):
        prepare_frame(frame)


def test_coerce_binary_labels() -> None:
    assert np.array_equal(coerce_binary_labels([0, 1, 1]), [0, 1, 1])
    with pytest.raises(ValueError):
        coerce_binary_labels([0, 2])


def test_read_write_roundtrip(tmp_path, synthetic_frame) -> None:
    csv_path = tmp_path / "data.csv"
    json_path = tmp_path / "data.json"
    write_frame(synthetic_frame, csv_path)
    write_frame(synthetic_frame, json_path)
    schema = SpectrumSchema()
    assert len(read_frame(csv_path, schema)) == len(synthetic_frame)
    assert len(read_frame(json_path, schema)) == len(synthetic_frame)


def test_read_frame_missing_column(tmp_path) -> None:
    path = tmp_path / "bad.csv"
    pd.DataFrame({"mz": ["100"]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="missing required"):
        read_frame(path)


def test_unsupported_suffix(tmp_path) -> None:
    path = tmp_path / "data.txt"
    path.write_text("x")
    with pytest.raises(ValueError, match="unsupported"):
        read_frame(path)
