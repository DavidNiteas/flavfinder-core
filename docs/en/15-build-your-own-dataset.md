# Build your own dataset

**Level:** 2 — Use  
**Prerequisites:** [Data format](./03-data-format.md), [Why code-only](./14-why-code-only.md).

This guide builds a labeled training table from MS/MS spectra and SMILES. The
labeling step uses RDKit, which is an optional extra:

```bash
python -m pip install -e ".[chem]"
```

## Input schema

Your table must contain at least:

| Column | Meaning |
|---|---|
| `smiles` | structure of the compound |
| `mz` | comma-separated MS/MS m/z values |
| `intensity` | comma-separated intensities |

Optional columns are preserved in the output:

| Column | Use |
|---|---|
| `id` / `name` | identifier |
| `precursor_mz` | precursor m/z |
| `adduct` | adduct notation |
| `ion_mode` | `P` or `N` |
| `collision_energy` | collision energy |
| `source` | GNPS / MassBank / MoNA / other |
| `label` | existing label, if any |

Example:

```csv
id,smiles,mz,intensity,source
q1,"O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12","151.0,273.0,301.0","12,100,44",GNPS
c1,"Cn1cnc2c1c(=O)n(C)c(=O)n2C","110.0,138.0,195.0","20,100,35",MoNA
```

## 1. Label with RDKit

```bash
flavfinder label \
  --input raw_with_smiles.csv \
  --output labeled.csv \
  --report label_report.json
```

Optional flags:

```bash
--smiles-col smiles
--label-col label
--patterns configs/flavonoid_patterns.yaml
```

Output columns:

| Column | Meaning |
|---|---|
| `label` | 1 = flavonoid, 0 = non-flavonoid, empty = invalid SMILES |
| `label_original` | previous label, if the input had one |
| `flavonoid_label` | same 0/1 label, kept explicitly |
| `flavonoid_subclass` | first matching scaffold family |
| `matched_patterns` | all matching rules, `|`-separated |
| `smiles_canonical` | RDKit canonical SMILES |
| `inchikey` | InChIKey for deduplication |
| `smiles_error` | parse/standardization error, if any |

A summary report contains:

- total, valid, and invalid rows,
- positive/negative counts and positive rate,
- subclass distribution,
- duplicate InChIKey groups and rows.

## 2. Filter and inspect

- Drop rows with a non-empty `smiles_error`.
- Check the subclass distribution; a sudden spike may indicate a too-broad rule.
- Inspect false positives and false negatives on a manual sample.
- Keep the raw record and the rule version for reproducibility.

## 3. Deduplicate

Use `inchikey` for structure-level duplicates and a spectrum hash for
spectrum-level duplicates:

```python
from flavfinder import SpectrumSchema, prepare_frame
from flavfinder.data import spectrum_key

prepared = prepare_frame(labeled, SpectrumSchema())
prepared["spectrum_key"] = [
    spectrum_key(mz, intensity)
    for mz, intensity in zip(
        prepared["_mz_values"], prepared["_intensity_values"], strict=True
    )
]
```

Decide whether multiple spectra per compound (different collision energies) are
useful. If they are, keep them but group them for splitting.

## 4. Split without leakage

For compound-level splitting, use `inchikey` as the group:

```python
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

groups = labeled["inchikey"].fillna(labeled["id"]).to_numpy()
labels = labeled["label"].astype(int).to_numpy()
splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
```

For spectra without reliable structures, use the near-duplicate grouping in
[Data audit](./08-data-audit.md).

Never tune thresholds on the test split.

## 5. Train positive and negative modes separately

```bash
flavfinder train \
  --train P_train.csv \
  --validation P_validation.csv \
  --test P_test.csv \
  --output-dir artifacts/P \
  --backend lightgbm

flavfinder train \
  --train N_train.csv \
  --validation N_validation.csv \
  --test N_test.csv \
  --output-dir artifacts/N \
  --backend lightgbm
```

Use AutoGluon for the reference workflow:

```bash
flavfinder train --config configs/P.yaml --backend autogluon
```

## 6. Evaluate and audit

```bash
flavfinder evaluate --model artifacts/P --input P_test.csv --output reports/P_metrics.json
flavfinder audit --train P_train.csv --test P_test.csv --output reports/P_audit.json
```

Report AUPRC alongside AUROC, inspect calibration, and keep the test set
untouched.

## Public data sources

| Source | URL | Notes |
|---|---|---|
| GNPS | <https://gnps.ucsd.edu> | community libraries and molecular networks |
| MassBank | <https://massbank.eu> | public reference spectra |
| MoNA | <https://mona.fiehnlab.ucdavis.edu> | MassBank of North America |
| NIST | licensed | commercial library |
| METLIN | licensed | commercial library |

Check each source's license and metadata quality. A spectrum without a reliable
structure cannot be labeled by this tool.

## Caveats

- RDKit rules are scaffold heuristics; validate against NPClassifier/ClassyFire
  or manual review.
- Flavonoid definitions vary. Glycosides, salts, and mixtures should be
  standardized before matching.
- Ion mode, instrument, and collision energy shift spectra. Do not mix domains
  without checking.
- Public records can contain label noise, missing structures, and duplicates.
- A random split is optimistic; use group/compound-aware splits.

**Next:** [Training](./05-training.md)
