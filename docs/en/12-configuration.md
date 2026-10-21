# Configuration

**Level:** 4 — Reference  
**Prerequisites:** [Python API](./11-python-api.md).

Training is configured with a YAML file. See `configs/P.yaml` and
`configs/N.yaml`.

## Full example

```yaml
data:
  train: data/P/train.csv
  validation: null
  test: data/P/test.csv
  mz_col: mz
  intensity_col: intensity
  label_col: label
  id_col: null

preprocessing:
  method: binning
  mz_min: 10.0
  mz_max: 500.0
  bin_width: 0.1
  mz_tol: 5.0
  mz_tol_unit: ppm
  normalization: max
  out_of_range: drop
  accumulate_unknown: true
  dtype: float64

model:
  backend: autogluon
  eval_metric: roc_auc
  presets: optimize_for_deployment
  time_limit: null
  random_state: 42
  params: {}

output_dir: artifacts/P
validation_size: 0.2
threshold_high_fpr: 0.01
seed: 42
overwrite: false
with_bootstrap: true
n_boot: 1000
```

## `data`

| Field | Default | Meaning |
|---|---|---|
| `train` | none | training table (required unless `--train`) |
| `validation` | none | optional validation table |
| `test` | none | optional test table |
| `mz_col` | `mz` | m/z column |
| `intensity_col` | `intensity` | intensity column |
| `label_col` | `label` | label column |
| `id_col` | none | optional identifier column |

## `preprocessing`

| Field | Default | Meaning |
|---|---|---|
| `method` | `binning` | `binning` or `tokenization` |
| `mz_min` | `10.0` | binning lower bound |
| `mz_max` | `500.0` | binning upper bound |
| `bin_width` | `0.1` | binning width |
| `mz_tol` | `5.0` | tokenization tolerance |
| `mz_tol_unit` | `ppm` | `ppm`, `%`, `abs`, `Da` |
| `normalization` | `max` | `none`, `max`, `l2` |
| `out_of_range` | `drop` | `drop`, `error`, `clip` |
| `accumulate_unknown` | `true` | keep unknown token intensity |
| `dtype` | `float64` | binning output dtype |

Fields not used by the selected method are ignored.

## `model`

| Field | Default | Meaning |
|---|---|---|
| `backend` | `autogluon` | `autogluon`, `lightgbm`, `sklearn` |
| `eval_metric` | `roc_auc` | AutoGluon metric |
| `presets` | `optimize_for_deployment` | AutoGluon presets |
| `time_limit` | none | AutoGluon time limit (seconds) |
| `random_state` | `42` | backend seed |
| `params` | `{}` | backend-specific parameters |

### Backend parameter examples

**LightGBM**

```yaml
model:
  backend: lightgbm
  params:
    n_estimators: 500
    learning_rate: 0.03
    num_leaves: 31
```

**AutoGluon**

```yaml
model:
  backend: autogluon
  presets: best_quality
  time_limit: 600
  params:
    num_bag_folds: 5
```

**scikit-learn**

```yaml
model:
  backend: sklearn
  params:
    max_iter: 2000
    C: 1.0
```

## Top-level

| Field | Default | Meaning |
|---|---|---|
| `output_dir` | `artifacts/model` | model bundle directory |
| `validation_size` | `0.2` | split when `validation` is absent |
| `threshold_high_fpr` | `0.01` | target FPR for the high threshold |
| `seed` | `42` | split and bootstrap seed |
| `overwrite` | `false` | replace a non-empty output directory |
| `with_bootstrap` | `true` | bootstrap validation/test metrics |
| `n_boot` | `1000` | bootstrap iterations |

## Path resolution

Paths are resolved relative to the **current working directory**, not the config
file. Run commands from the repository root or use absolute paths.

## CLI overrides

```bash
flavfinder train --config configs/P.yaml \
  --train /abs/path/train.csv \
  --test /abs/path/test.csv \
  --output-dir /abs/path/artifacts/P \
  --backend lightgbm \
  --method tokenization \
  --seed 123 \
  --overwrite
```

Schema flags override YAML only when explicitly provided.

**Next:** [Troubleshooting](./13-troubleshooting.md)
