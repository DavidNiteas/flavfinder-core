"""Small numeric and tolerance helpers."""

from __future__ import annotations

import numpy as np

_EPS = 1e-12


def _check_tolerance(mz_tol: float) -> float:
    tol = float(mz_tol)
    if tol < 0:
        raise ValueError(f"mz_tol must be non-negative, got {mz_tol!r}")
    return tol


def mz_tolerance(
    mz: float | np.ndarray,
    mz_tol: float,
    mz_tol_unit: str = "ppm",
) -> float | np.ndarray:
    """Return the absolute m/z tolerance for ``mz`` in the requested unit."""

    tol = _check_tolerance(mz_tol)
    unit = mz_tol_unit.lower()
    values = np.asarray(mz, dtype=float)
    if unit == "ppm":
        result = np.abs(values) * tol * 1e-6
    elif unit == "%":
        result = np.abs(values) * tol * 1e-2
    elif unit in {"abs", "da"}:
        result = np.full_like(values, tol, dtype=float)
    else:
        raise ValueError("mz_tol_unit must be one of: 'ppm', '%', 'abs', 'Da'")
    if result.ndim == 0:
        return float(result)
    return result


def is_same_mz(mz1: float, mz2: float, mz_tol: float, mz_tol_unit: str = "ppm") -> bool:
    """Return whether two m/z values fall within the requested tolerance."""

    tolerance = mz_tolerance(mz1, mz_tol, mz_tol_unit)
    return bool(abs(float(mz1) - float(mz2)) <= tolerance + _EPS)


def as_float_array(values: object, name: str = "values") -> np.ndarray:
    """Convert an iterable to a finite 1-D float array with a clear error."""

    try:
        array = np.asarray(values, dtype=float).ravel()
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if array.size == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains non-finite values")
    return array
