"""Data auditing, exact/near-duplicate detection, and group splits."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np
import pandas as pd

from flavfinder.io import SpectrumSchema, coerce_binary_labels, prepare_frame


def spectrum_key(mz: np.ndarray, intensity: np.ndarray) -> str:
    """Stable key for exact spectrum matching."""

    mz_text = ",".join(f"{value:.6f}" for value in np.asarray(mz, dtype=float))
    intensity_text = ",".join(f"{value:.6f}" for value in np.asarray(intensity, dtype=float))
    return f"{mz_text}|{intensity_text}"


def _keys_and_labels(
    frame: pd.DataFrame,
    schema: SpectrumSchema,
) -> tuple[list[int], list[str], list[int] | None]:
    prepared = prepare_frame(frame, schema)
    indices = list(prepared.index)
    keys = [
        spectrum_key(mz, intensity)
        for mz, intensity in zip(
            prepared["_mz_values"], prepared["_intensity_values"], strict=True
        )
    ]
    labels: list[int] | None = None
    if schema.label_col in prepared.columns:
        labels = coerce_binary_labels(
            prepared[schema.label_col], schema.label_col
        ).tolist()
    return indices, keys, labels


def _label_counts(labels: list[int] | None) -> dict[str, int] | None:
    if labels is None:
        return None
    values, counts = np.unique(np.asarray(labels), return_counts=True)
    return {str(int(value)): int(count) for value, count in zip(values, counts, strict=True)}


def audit_frame(
    frame: pd.DataFrame,
    schema: SpectrumSchema | None = None,
    *,
    mz_min: float = 10.0,
    mz_max: float = 500.0,
) -> dict[str, Any]:
    """Summarize a spectrum table and its duplicate structure."""

    schema = schema or SpectrumSchema()
    prepared = prepare_frame(frame, schema)
    mz_values = prepared["_mz_values"]
    intensity_values = prepared["_intensity_values"]
    peak_counts = np.asarray([len(values) for values in mz_values], dtype=int)
    all_mz = (
        np.concatenate([np.asarray(values) for values in mz_values])
        if len(prepared)
        else np.array([])
    )
    all_intensity = (
        np.concatenate([np.asarray(values) for values in intensity_values])
        if len(prepared)
        else np.array([])
    )

    indices, keys, labels = _keys_and_labels(prepared, schema)
    groups: dict[str, list[int]] = defaultdict(list)
    for index, key in zip(indices, keys, strict=True):
        groups[key].append(index)
    duplicate_groups = {key: members for key, members in groups.items() if len(members) > 1}
    conflicting_groups = 0
    if labels is not None:
        label_by_index = dict(zip(indices, labels, strict=True))
        for members in duplicate_groups.values():
            if len({label_by_index[member] for member in members}) > 1:
                conflicting_groups += 1

    return {
        "n_spectra": int(len(prepared)),
        "n_peaks": int(all_mz.size),
        "label_counts": _label_counts(labels),
        "peak_count": {
            "min": int(peak_counts.min()) if peak_counts.size else 0,
            "max": int(peak_counts.max()) if peak_counts.size else 0,
            "mean": float(peak_counts.mean()) if peak_counts.size else 0.0,
            "median": float(np.median(peak_counts)) if peak_counts.size else 0.0,
            "p95": float(np.quantile(peak_counts, 0.95)) if peak_counts.size else 0.0,
        },
        "mz": {
            "min": float(all_mz.min()) if all_mz.size else None,
            "max": float(all_mz.max()) if all_mz.size else None,
            "below_mz_min": int((all_mz < mz_min).sum()),
            "above_mz_max": int((all_mz > mz_max).sum()),
        },
        "intensity": {
            "min": float(all_intensity.min()) if all_intensity.size else None,
            "max": float(all_intensity.max()) if all_intensity.size else None,
            "mean": float(all_intensity.mean()) if all_intensity.size else None,
            "zeros": int((all_intensity == 0).sum()),
        },
        "duplicates": {
            "duplicate_groups": int(len(duplicate_groups)),
            "duplicate_rows": int(sum(len(members) for members in duplicate_groups.values())),
            "conflicting_label_groups": int(conflicting_groups),
        },
    }


def leakage_report(
    train_frame: pd.DataFrame,
    test_frame: pd.DataFrame,
    schema: SpectrumSchema | None = None,
    *,
    max_examples: int = 10,
) -> dict[str, Any]:
    """Report exact spectrum overlap between train and test tables."""

    schema = schema or SpectrumSchema()
    train_indices, train_keys, train_labels = _keys_and_labels(train_frame, schema)
    test_indices, test_keys, test_labels = _keys_and_labels(test_frame, schema)
    train_by_key = {key: index for index, key in zip(train_indices, train_keys, strict=True)}
    overlap = [
        {
            "test_index": index,
            "train_index": train_by_key[key],
            "key": key,
        }
        for index, key in zip(test_indices, test_keys, strict=True)
        if key in train_by_key
    ]
    conflicting = 0
    if train_labels is not None and test_labels is not None:
        train_label_by_key = {
            key: label
            for key, label in zip(train_keys, train_labels, strict=True)
        }
        for key, label in zip(test_keys, test_labels, strict=True):
            if key in train_label_by_key and train_label_by_key[key] != label:
                conflicting += 1
    return {
        "train_n": int(len(train_frame)),
        "test_n": int(len(test_frame)),
        "overlap_n": int(len(overlap)),
        "overlap_rate": float(len(overlap) / len(test_frame)) if len(test_frame) else 0.0,
        "label_conflicts": int(conflicting),
        "examples": overlap[:max_examples],
    }


def near_duplicate_pairs(
    frame: pd.DataFrame,
    preprocessor: Any,
    schema: SpectrumSchema | None = None,
    *,
    threshold: float = 0.95,
    chunk_size: int = 1000,
    max_pairs: int = 1_000_000,
) -> list[tuple[int, int, float]]:
    """Find pairwise cosine-similar spectra above ``threshold``.

    This is an O(n²) scan performed in row chunks; it is intended for audit
    notebooks and moderate datasets, not for online inference.
    """

    schema = schema or SpectrumSchema()
    features = preprocessor.transform(prepare_frame(frame, schema), schema)
    feature_names = list(preprocessor.feature_names_)
    matrix = features[feature_names].to_numpy(dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1)
    nonzero = norms > 0
    matrix[nonzero] /= norms[nonzero, None]

    pairs: list[tuple[int, int, float]] = []
    n_rows = matrix.shape[0]
    for start in range(0, n_rows, chunk_size):
        end = min(start + chunk_size, n_rows)
        similarity = matrix[start:end] @ matrix.T
        rows, cols = np.nonzero(similarity >= threshold)
        for row, col in zip(rows, cols, strict=True):
            left = start + int(row)
            right = int(col)
            if right <= left:
                continue
            pairs.append((left, right, float(similarity[row, col])))
            if len(pairs) >= max_pairs:
                return pairs
    return pairs


def groups_from_pairs(n_items: int, pairs: list[tuple[int, int, float]]) -> np.ndarray:
    """Union-find connected components from duplicate pairs."""

    parent = list(range(n_items))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for left, right, _score in pairs:
        union(left, right)
    roots = [find(item) for item in range(n_items)]
    mapping: dict[int, int] = {}
    groups = np.empty(n_items, dtype=int)
    for item, root in enumerate(roots):
        if root not in mapping:
            mapping[root] = len(mapping)
        groups[item] = mapping[root]
    return groups


def group_split_indices(
    groups: np.ndarray,
    *,
    test_size: float = 0.2,
    validation_size: float = 0.2,
    seed: int = 42,
) -> dict[str, np.ndarray]:
    """Greedy group-aware split returning row indices for train/validation/test."""

    groups = np.asarray(groups)
    if groups.ndim != 1:
        raise ValueError("groups must be one-dimensional")
    if not 0 <= test_size < 1 or not 0 <= validation_size < 1:
        raise ValueError("test_size and validation_size must be in [0, 1)")
    if test_size + validation_size >= 1:
        raise ValueError("test_size + validation_size must be < 1")

    rng = np.random.default_rng(seed)
    unique_groups = np.unique(groups)
    rng.shuffle(unique_groups)
    target_test = int(round(groups.size * test_size))
    target_validation = int(round(groups.size * validation_size))

    test_groups: list[int] = []
    validation_groups: list[int] = []
    test_rows = 0
    validation_rows = 0
    for group in unique_groups:
        size = int((groups == group).sum())
        if test_rows < target_test:
            test_groups.append(int(group))
            test_rows += size
        elif validation_rows < target_validation:
            validation_groups.append(int(group))
            validation_rows += size

    test_mask = np.isin(groups, test_groups)
    validation_mask = np.isin(groups, validation_groups)
    train_mask = ~(test_mask | validation_mask)
    return {
        "train": np.flatnonzero(train_mask),
        "validation": np.flatnonzero(validation_mask),
        "test": np.flatnonzero(test_mask),
    }
