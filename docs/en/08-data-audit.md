# Data audit and leakage

**Level:** 3 — Understand  
**Prerequisites:** [Evaluation](./07-evaluation.md).

A random split can put near-identical spectra in both train and test. Always
audit before reporting metrics.

## CLI

```bash
flavfinder audit \
  --train data/P/train.csv \
  --test data/P/test.csv \
  --output reports/P_audit.json
```

The report contains:

- number of spectra and peaks,
- class balance,
- peak-count distribution,
- m/z range and out-of-grid counts,
- exact duplicate groups and conflicting labels,
- exact train/test overlap.

## Exact duplicates

```python
from flavfinder import audit_frame, leakage_report

audit = audit_frame(train_frame)
leak = leakage_report(train_frame, test_frame)
print(audit["duplicates"])
print(leak["overlap_n"])
```

Exact matching uses a stable key over sorted m/z and intensity values.

## Near duplicates

```python
from flavfinder import BinningTransformer, near_duplicate_pairs

transformer = BinningTransformer()
pairs = near_duplicate_pairs(
    train_frame,
    transformer,
    threshold=0.95,
)
```

This computes cosine similarity over binned vectors in row chunks. It is an
**audit tool**, not an online index; the cost is quadratic in the number of rows.

## Group-aware splits

Use connected components from duplicate pairs:

```python
from flavfinder import groups_from_pairs, group_split_indices

groups = groups_from_pairs(len(train_frame), pairs)
split = group_split_indices(
    groups,
    train_frame["label"],
    test_size=0.2,
    validation_size=0.2,
    seed=42,
)
print({name: len(indices) for name, indices in split.items()})
```

When binary labels are provided, `group_split_indices` uses stratified group
cross-validation (`StratifiedGroupKFold`) to keep both classes and keep groups
disjoint. Without labels it falls back to a greedy split.

`group_split_indices` is a greedy, group-aware split. It keeps all members of a
duplicate/near-duplicate group in the same split. It is not a substitute for
true compound-level grouping.

## The compound-ID limitation

The provided data has only `mz`, `intensity`, and `label`. There is no compound
identifier, so strict “split by molecule” is impossible without external
metadata. Near-duplicate clustering is a proxy; report it as such.

## Recommended audit workflow

1. Check schema and invalid rows.
2. Count exact duplicates and conflicting labels.
3. Measure exact train/test overlap.
4. Run near-duplicate clustering at several thresholds (0.90, 0.95, 0.99).
5. Build a group-aware split.
6. Re-train and compare random-split vs group-split metrics.
7. Report both, and explain the difference.

## What to do with duplicates

- Identical spectra with conflicting labels: fix the source data or drop the
  ambiguous group.
- Identical spectra split across train/test: move the whole group to one side.
- Near duplicates across splits: treat as leakage and use a group-aware split.

**Next:** [Method](./09-method.md)
