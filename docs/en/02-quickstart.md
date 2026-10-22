# Quickstart

**Level:** 1 — Start  
**Prerequisites:** [Installation](./01-installation.md).

Here is the whole pipeline on a tiny **synthetic** dataset. You do not need real
training data.

## 1. Generate a synthetic labeled table

Save this as `make_demo.py` and run it. It creates `synthetic.csv` with two
classes and a discriminative peak at m/z 300.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(0)
rows = []
for i in range(80):
    label = int(i % 2 == 0)
    mz = rng.uniform(50, 450, size=8)
    intensity = rng.uniform(1, 100, size=8)
    mz = np.append(mz, 300.0 if label else 150.0)
    intensity = np.append(intensity, 100.0)
    order = np.argsort(mz)
    rows.append({
        "id": f"synthetic-{i}",
        "mz": ",".join(f"{v:.4f}" for v in mz[order]),
        "intensity": ",".join(f"{v:.4f}" for v in intensity[order]),
        "label": label,
    })
pd.DataFrame(rows).to_csv("synthetic.csv", index=False)
```

```bash
python make_demo.py
```

## 2. Audit the table

```bash
flavfinder audit --input synthetic.csv --output audit.json
```

`audit.json` contains peak-count statistics, m/z range, class balance, and
duplicate information.

## 3. Train a small model

The scikit-learn backend is included in the base install and is fast enough for
this demo.

```bash
flavfinder train \
  --train synthetic.csv \
  --test synthetic.csv \
  --output-dir artifacts/demo \
  --backend sklearn \
  --no-bootstrap \
  --overwrite
```

Artifacts written to `artifacts/demo`:

| File | Meaning |
|---|---|
| `preprocessing.json` | Fitted binning/tokenization state |
| `backend/` | Fitted model |
| `thresholds.json` | mid/high decision thresholds |
| `metrics.json` | train/validation/test metrics |
| `metadata.json` | config, feature names, provenance |

## 4. Predict

```bash
flavfinder predict \
  --model artifacts/demo \
  --input examples/input_format.json \
  --output predictions.json
```

Each output record keeps the input columns and adds `score` and `probability`
(`high` / `mid` / `low`).

## 5. Evaluate

```bash
flavfinder evaluate \
  --model artifacts/demo \
  --input synthetic.csv \
  --output evaluation.json \
  --no-bootstrap
```

## What just happened?

1. Peaks were binned into a fixed m/z grid (default 10–500, 0.1 width).
2. Intensities were normalized per spectrum (default max).
3. A classifier was trained on the binned features.
4. `mid` and `high` thresholds were selected on the validation split.
5. The model bundle was saved as a directory you can reload.

## Next steps

- Use your own data: [Data format](./03-data-format.md)
- Replace the demo backend with AutoGluon: [Training](./05-training.md)
- Check for leakage before trusting metrics: [Data audit](./08-data-audit.md)

**Next:** [Data format](./03-data-format.md)
