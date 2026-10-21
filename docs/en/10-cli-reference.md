# CLI reference

**Level:** 4 — Reference  
**Prerequisites:** [Training](./05-training.md).

## Global

```bash
flavfinder --version
flavfinder --describe
flavfinder --help
```

## Schema flags

Available on `audit`, `train`, `predict`, and `evaluate`:

| Flag | Default |
|---|---|
| `--mz-col` | `mz` |
| `--intensity-col` | `intensity` |
| `--label-col` | `label` |
| `--id-col` | none |

On `train`, a flag overrides the YAML value only when explicitly provided.

## `flavfinder audit`

```bash
flavfinder audit --input data.csv --output audit.json
flavfinder audit --train train.csv --test test.csv --output audit.json
```

| Flag | Meaning |
|---|---|
| `--input` | audit one table |
| `--train` / `--test` | audit both tables and report exact overlap |
| `--output` | write JSON report |

## `flavfinder train`

```bash
flavfinder train --config configs/P.yaml
flavfinder train --train data/P/train.csv --test data/P/test.csv \
  --output-dir artifacts/P --backend lightgbm --no-bootstrap --overwrite
```

| Flag | Meaning |
|---|---|
| `--config` | YAML training config |
| `--train` | training table override |
| `--validation` | validation table override |
| `--test` | test table override |
| `--output-dir` | model bundle directory |
| `--backend` | `autogluon`, `lightgbm`, or `sklearn` |
| `--method` | `binning` or `tokenization` |
| `--seed` | split/backend seed override |
| `--overwrite` | replace a non-empty output directory |
| `--no-bootstrap` | skip bootstrap confidence intervals |
| `--n-boot` | bootstrap iterations |

Relative paths in YAML are resolved from the **current working directory**, not
from the config file.

## `flavfinder predict`

```bash
flavfinder predict --model artifacts/P --input input.json --output predictions.json
```

| Flag | Meaning |
|---|---|
| `--model` | model bundle directory |
| `--input` | CSV/JSON spectrum table |
| `--output` | CSV/JSON output path |

## `flavfinder evaluate`

```bash
flavfinder evaluate --model artifacts/P --input data/P/test.csv \
  --output reports/P_metrics.json --no-bootstrap
```

| Flag | Meaning |
|---|---|
| `--model` | model bundle directory |
| `--input` | labeled CSV/JSON table |
| `--output` | JSON metrics output |
| `--no-bootstrap` | skip resampling |
| `--n-boot` | bootstrap iterations |
| `--seed` | bootstrap seed |

## Exit codes

| Code | Meaning |
|---|---|
| `0` | success |
| `2` | handled input/configuration/import error |

Unhandled exceptions are not masked by the CLI.

## Examples

```bash
# Audit
flavfinder audit --train data/P/train.csv --test data/P/test.csv --output reports/P_audit.json

# Train with AutoGluon
flavfinder train --config configs/P.yaml

# Train with LightGBM
flavfinder train --config configs/P.yaml --backend lightgbm --output-dir artifacts/P-lgbm

# Predict
flavfinder predict --model artifacts/P --input examples/input_format.json --output predictions.json

# Evaluate
flavfinder evaluate --model artifacts/P --input data/P/test.csv --output reports/P_metrics.json
```

**Next:** [Python API](./11-python-api.md)
