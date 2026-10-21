from __future__ import annotations

import numpy as np
import pytest

from flavfinder.utils import as_float_array, is_same_mz, mz_tolerance


def test_is_same_mz_ppm() -> None:
    assert is_same_mz(100.0, 100.0004, 5.0, "ppm")
    assert not is_same_mz(100.0, 100.0006, 5.0, "ppm")


def test_is_same_mz_percent_and_abs() -> None:
    assert is_same_mz(100.0, 100.4, 0.5, "%")
    assert not is_same_mz(100.0, 100.6, 0.5, "%")
    assert is_same_mz(100.0, 100.4, 0.5, "abs")
    assert is_same_mz(100.0, 100.4, 0.5, "Da")


def test_invalid_unit() -> None:
    with pytest.raises(ValueError):
        is_same_mz(100.0, 100.0, 5.0, "furlong")


def test_negative_tolerance() -> None:
    with pytest.raises(ValueError):
        mz_tolerance(100.0, -1.0)


def test_mz_tolerance_array() -> None:
    values = mz_tolerance(np.array([100.0, 200.0]), 10.0, "ppm")
    assert np.allclose(values, [0.001, 0.002])


def test_as_float_array_rejects_empty_and_non_finite() -> None:
    with pytest.raises(ValueError):
        as_float_array([])
    with pytest.raises(ValueError):
        as_float_array([1.0, np.nan])
    with pytest.raises(ValueError):
        as_float_array(["a"])
