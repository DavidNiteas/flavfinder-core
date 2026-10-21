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


def _greedy_group_split(
    groups: np.ndarray,
    *,
    test_size: float,
    validation_size: float,
    seed: int,
) -> dict[str, np.ndarray]:
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


def _stratified_group_split(
    groups: np.ndarray,
    labels: np.ndarray,
    *,
    test_size: float,
    validation_size: float,
    seed: int,
) -> dict[str, np.ndarray] | None:
    from sklearn.model_selection import StratifiedGroupKFold

    n_total = groups.size
    target_test = n_total * test_size
    overall_positive_rate = float(labels.mean())
    n_splits = max(2, int(round(1.0 / test_size))) if test_size > 0 else 0
    if n_splits == 0:
        return None
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    best_test: tuple[float, np.ndarray] | None = None
    for _train_index, test_index in splitter.split(
        np.zeros(n_total), labels, groups
    ):
        if np.unique(labels[test_index]).size < 2:
            continue
        size_penalty = abs(len(test_index) - target_test) / max(target_test, 1.0)
        rate_penalty = abs(float(labels[test_index].mean()) - overall_positive_rate)
        score = size_penalty + 2.0 * rate_penalty
        if best_test is None or score < best_test[0]:
            best_test = (score, test_index)
    if best_test is None:
        return None

    test_index = best_test[1]
    remaining = np.setdiff1d(np.arange(n_total), test_index, assume_unique=True)
    if validation_size <= 0:
        return {"train": remaining, "validation": np.array([], dtype=int), "test": test_index}

    relative_validation = validation_size / (1.0 - test_size)
    n_splits_val = max(2, int(round(1.0 / relative_validation)))
    splitter_val = StratifiedGroupKFold(
        n_splits=n_splits_val, shuffle=True, random_state=seed
    )
    target_validation = n_total * validation_size
    best_val: tuple[float, np.ndarray] | None = None
    for _train_rel, val_rel in splitter_val.split(
        np.zeros(remaining.size), labels[remaining], groups[remaining]
    ):
        if np.unique(labels[remaining[val_rel]]).size < 2:
            continue
        size_penalty = abs(len(val_rel) - target_validation) / max(target_validation, 1.0)
        rate_penalty = abs(float(labels[remaining[val_rel]].mean()) - overall_positive_rate)
        score = size_penalty + 2.0 * rate_penalty
        if best_val is None or score < best_val[0]:
            best_val = (score, val_rel)
    if best_val is None:
        return None

    val_rel = best_val[1]
    train_index = remaining[np.setdiff1d(np.arange(remaining.size), val_rel, assume_unique=True)]
    validation_index = remaining[val_rel]
    return {"train": train_index, "validation": validation_index, "test": test_index}


def group_split_indices(
    groups: np.ndarray,
    labels: np.ndarray | None = None,
    *,
    test_size: float = 0.2,
    validation_size: float = 0.2,
    seed: int = 42,
) -> dict[str, np.ndarray]:
    """Group-aware split returning row indices for train/validation/test.

    When binary ``labels`` are provided and both classes are present, the split
    uses :class:`~sklearn.model_selection.StratifiedGroupKFold` to preserve class
    balance while keeping each group in exactly one split. Otherwise it falls
    back to a deterministic greedy split.
    """

    groups = np.asarray(groups)
    if groups.ndim != 1:
        raise ValueError("groups must be one-dimensional")
    if not 0 <= test_size < 1 or not 0 <= validation_size < 1:
        raise ValueError("test_size and validation_size must be in [0, 1)")
    if test_size + validation_size >= 1:
        raise ValueError("test_size + validation_size must be < 1")
    if labels is not None:
        labels_array = coerce_binary_labels(labels)
        if labels_array.size != groups.size:
            raise ValueError("labels and groups lengths differ")
        if np.unique(labels_array).size == 2:
            split = _stratified_group_split(
                groups,
                labels_array,
                test_size=test_size,
                validation_size=validation_size,
                seed=seed,
            )
            if split is not None:
                return split
    return _greedy_group_split(
        groups,
        test_size=test_size,
        validation_size=validation_size,
        seed=seed,
    )

