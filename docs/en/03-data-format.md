# Data format

**Level:** 2 — Use  
**Prerequisites:** [Quickstart](./02-quickstart.md).

## Supported containers

`flavfinder` reads `.csv` and `.json` tables. Each row is one MS/MS spectrum.

### CSV

```csv
id,mz,intensity,label
compound-1,"100.0,150.0,200.0","10,50,100",1
compound-2,"120.0,180.0,240.0","5,25,100",0
```

### JSON

```json
[
  {
    "id": "compound-1",
    "mz": "100.0,150.0,200.0",
    "intensity": "10,50,100",
    "label": 1
  }
]
```

## Columns

| Column | Required | Type | Notes |
|---|---|---|---|
| `mz` | yes | comma-separated numbers or numeric list | m/z values |
| `intensity` | yes | comma-separated numbers or numeric list | same length as `mz` |
| `label` | for training/evaluation | 0 or 1 | optional for prediction |
| `smiles` | for labeling | string | optional; used by `flavfinder label` |
| `id` / `name` | no | string or number | copied to prediction output |

The default column names can be changed in YAML or with CLI flags:

```bash
flavfinder train --train data.csv \
  --mz-col "precursor_mz" \
  --intensity-col "peaks_intensity" \
  --label-col "is_flavonoid"
```

## Validation rules

`prepare_frame` enforces:

- `mz` and `intensity` are non-empty.
- Their lengths match exactly.
- All values are finite numbers.
- m/z and intensity are non-negative.
- Spectra are sorted by m/z before transformation.
- Labels are integer `0` or `1`.

Rows are never silently dropped. Invalid input raises an error with the row
index so it can be fixed.

If you have structures, add a `smiles` column and use
[Build your own dataset](./15-build-your-own-dataset.md) to create `label`
values before training.

## Common mistakes

| Mistake | Error |
|---|---|
| `mz` has 10 values, `intensity` has 9 | `mz and intensity lengths differ` |
| trailing comma: `"100,200,"` | `contains an empty value` |
| `NaN` or `inf` | `contains non-finite values` |
| negative intensity | `intensities must be non-negative` |
| label `2` | `label must contain only 0 and 1` |

## Prediction output

Prediction writes the input columns plus:

| Column | Meaning |
|---|---|
| `score` | positive-class probability |
| `probability` | `high`, `mid`, or `low` bucket |

If the model has no thresholds, only `score` is added.

**Next:** [Preprocessing](./04-preprocessing.md)
