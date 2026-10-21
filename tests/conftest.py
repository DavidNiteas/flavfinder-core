"""Shared synthetic fixtures.

All spectra here are generated deterministically and are not taken from the
original training data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def make_synthetic_frame(n_spectra: int = 80, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for index in range(n_spectra):
        label = int(index % 2 == 0)
        mz = rng.uniform(50.0, 450.0, size=8)
        intensity = rng.uniform(1.0, 100.0, size=mz.size)
        if label:
            mz = np.append(mz, 300.0)
            intensity = np.append(intensity, 100.0)
        else:
            mz = np.append(mz, 150.0)
            intensity = np.append(intensity, 100.0)
        order = np.argsort(mz)
        mz = mz[order]
        intensity = intensity[order]
        rows.append(
            {
                "id": f"synthetic-{index}",
                "mz": ",".join(f"{value:.4f}" for value in mz),
                "intensity": ",".join(f"{value:.4f}" for value in intensity),
                "label": label,
            }
        )
    return pd.DataFrame(rows)


@pytest.fixture
def synthetic_frame() -> pd.DataFrame:
    return make_synthetic_frame()


@pytest.fixture
def synthetic_csv(tmp_path, synthetic_frame) -> str:
    path = tmp_path / "synthetic.csv"
    synthetic_frame.to_csv(path, index=False)
    return str(path)
