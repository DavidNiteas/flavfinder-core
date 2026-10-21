# Training

**Level:** 2 — Use  
**Prerequisites:** [Preprocessing](./04-preprocessing.md).

## Config-driven run

Use `configs/P.yaml` or `configs/N.yaml` as a starting point:

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
  normalization: max
  out_of_range: drop

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

Run it:

```bash
flavfinder train --config configs/P.yaml
```

## What the trainer does

1. Reads and validates the training table.
2. Uses `validation` if provided; otherwise splits `train` with
   `validation_size`, stratified by label.
3. Fits the preprocessor **on the training split only**.
4. Fits the selected backend.
5. Selects `mid` and `high` thresholds on the validation split.
6. Evaluates train/validation/test and writes a model bundle.

## Backends

| Backend | Extra | Use |
|---|---|---|
| `autogluon` | `.[autogluon]` | reference workflow; installs the full AutoGluon tabular model zoo |
| `lightgbm` | `.[lightgbm]` | fast local experiments |
| `sklearn` | base install | tests and tiny datasets |

```bash
flavfinder train --config configs/P.yaml --backend lightgbm
```

## Outputs

```text
artifacts/P/
├── preprocessing.json   # fitted binning/tokenization state
├── backend/             # model files or AutoGluon predictor
├── thresholds.json      # mid/high thresholds and their metrics
├── metrics.json         # train/validation/test metrics
└── metadata.json        # config, feature names, provenance, versions
```

`metadata.json` records the input paths, feature names, package version, Python
version, and a compact metric summary. It does not copy the training data.

## Threshold selection

- `mid` = Youden-optimal point (`argmax(TPR - FPR)`).
- `high` = point closest to the target false-positive rate
  (`threshold_high_fpr`, default 1%).
- Thresholds are selected on validation, not on test.
- The high threshold is constrained to be at least the mid threshold.

## Reproducibility

- `seed` controls the train/validation split and bootstrap sampling.
- `model.random_state` controls the backend.
- The exact package versions are recorded in `metadata.json`.
- Use `overwrite: true` or `--overwrite` to replace an existing output
  directory.

## Class imbalance

The original data is imbalanced. Do not rely on accuracy alone:

- report **AUPRC** alongside AUROC,
- inspect the confusion matrix at the chosen thresholds,
- check calibration before interpreting probabilities as risk.

See [Evaluation](./07-evaluation.md).

**Next:** [Prediction](./06-prediction.md)
