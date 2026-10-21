from __future__ import annotations

import numpy as np
import pandas as pd

from flavfinder.data import (
    audit_frame,
    group_split_indices,
    groups_from_pairs,
    leakage_report,
    near_duplicate_pairs,
)
from flavfinder.preprocessing import BinningTransformer


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "mz": ["100,200", "100,200", "150,250"],
            "intensity": ["1,2", "1,2", "3,4"],
            "label": [0, 1, 0],
        }
    )


def test_audit_duplicates_and_conflicts() -> None:
    report = audit_frame(_frame())
    assert report["n_spectra"] == 3
    assert report["duplicates"]["duplicate_groups"] == 1
    assert report["duplicates"]["duplicate_rows"] == 2
    assert report["duplicates"]["conflicting_label_groups"] == 1


def test_leakage_report() -> None:
    train = _frame()
    test = _frame().iloc[[0]].copy()
    report = leakage_report(train, test)
    assert report["overlap_n"] == 1
    assert report["overlap_rate"] == 1.0


def test_near_duplicate_pairs() -> None:
    frame = _frame()
    transformer = BinningTransformer(mz_min=10.0, mz_max=300.0, bin_width=1.0)
    pairs = near_duplicate_pairs(frame, transformer, threshold=0.99)
    assert any(left == 0 and right == 1 for left, right, _score in pairs)


def test_groups_from_pairs() -> None:
    groups = groups_from_pairs(4, [(0, 1, 1.0), (2, 3, 1.0)])
    assert groups[0] == groups[1]
    assert groups[2] == groups[3]
    assert groups[0] != groups[2]


def test_group_split_indices_are_disjoint() -> None:
    groups = np.array([0, 0, 1, 1, 2, 2, 3, 3])
    split = group_split_indices(groups, test_size=0.25, validation_size=0.25, seed=1)
    train = set(split["train"])
    validation = set(split["validation"])
    test = set(split["test"])
    assert not (train & validation)
    assert not (train & test)
    assert not (validation & test)
    assert train | validation | test == set(range(8))


def test_group_split_stratified_keeps_both_classes() -> None:
    groups = np.repeat(np.arange(40), 2)
    labels = np.repeat(np.arange(40) % 2, 2)
    split = group_split_indices(
        groups,
        labels,
        test_size=0.2,
        validation_size=0.2,
        seed=3,
    )
    for indices in split.values():
        assert set(np.unique(labels[indices])) == {0, 1}
    group_sets = {name: set(np.unique(groups[idx])) for name, idx in split.items()}
    assert not (group_sets["train"] & group_sets["validation"])
    assert not (group_sets["train"] & group_sets["test"])
    assert not (group_sets["validation"] & group_sets["test"])
