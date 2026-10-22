# flavfinder-core

An independent, code-only port of the **flavfinder** MS/MS flavonoid classifier.

> This is **not** the original repository. It has its own Git history and does **not**
> include the original training data, real MS/MS example spectra, or pretrained models.

## Documentation

Start with the language you prefer:

- **English:** [Documentation index](docs/en/index.md)
- **简体中文：** [文档索引](docs/zh-CN/index.md)

The docs use progressive disclosure:

| Level | English | 简体中文 |
|---|---|---|
| 0 — Scope | [Why code-only](docs/en/14-why-code-only.md) | [为什么只发代码](docs/zh-CN/14-why-code-only.md) |
| 1 — Install & run | [Installation](docs/en/01-installation.md) → [Quickstart](docs/en/02-quickstart.md) | [安装](docs/zh-CN/01-installation.md) → [快速开始](docs/zh-CN/02-quickstart.md) |
| 2 — Use your data | [Data format](docs/en/03-data-format.md) → [Build your own dataset](docs/en/15-build-your-own-dataset.md) → [Training](docs/en/05-training.md) | [数据格式](docs/zh-CN/03-data-format.md) → [自建数据集](docs/zh-CN/15-build-your-own-dataset.md) → [训练](docs/zh-CN/05-training.md) |
| 3 — Trust the result | [Evaluation](docs/en/07-evaluation.md) → [Data audit](docs/en/08-data-audit.md) → [Method](docs/en/09-method.md) | [评估](docs/zh-CN/07-evaluation.md) → [数据审计](docs/zh-CN/08-data-audit.md) → [方法](docs/zh-CN/09-method.md) |
| 4 — Reference | [CLI](docs/en/10-cli-reference.md) · [API](docs/en/11-python-api.md) · [Config](docs/en/12-configuration.md) | [CLI](docs/zh-CN/10-cli-reference.md) · [API](docs/zh-CN/11-python-api.md) · [配置](docs/zh-CN/12-configuration.md) |

## What this repository is

`flavfinder-core` is a from-scratch, release-oriented port of the original
[`Ficere/flavfinder`](https://github.com/Ficere/flavfinder) implementation. It provides
a clean, installable, testable, and reproducible codebase that implements the method:

- MS/MS spectrum ingestion and validation
- Binning and tokenization preprocessing
- Pluggable model backends: AutoGluon, LightGBM, scikit-learn
- Training, prediction, evaluation, and threshold selection
- Data auditing: exact/near duplicates, leakage reports, group-aware splits
- RDKit-based flavonoid labeling from SMILES (`flavfinder label`)
- Config-driven CLI and Python API
- Synthetic-data tests only; no real spectra in the repository

## Why this repository is code-only

We intentionally do **not** distribute training data or pretrained models:

1. **Model weights are not convenient to ship.** A fitted tabular bundle can be
   large, while training is reproducible on a workstation and should be repeated
   on the user's own spectra. We ship the full training pipeline and configs.
2. **A frozen dataset would be stale.** Public MS/MS libraries such as GNPS,
   MassBank, and MoNA contain far more spectra, newer records, and richer
   metadata than any snapshot we could bundle. The original data used here is an
   older reference version, not a recommended training source.
3. **Users should build labels from current structures.** We provide an
   RDKit-based labeling tool (`flavfinder label`) that turns a table with MS/MS
   and SMILES into labeled flavonoid/non-flavonoid data using a subclass-aware
   SMARTS ruleset.

This is a deliberate distribution choice, not a missing feature. See
[Why code-only](docs/en/14-why-code-only.md) and
[Build your own dataset](docs/en/15-build-your-own-dataset.md).

## Build your own dataset

If your table has `smiles`, `mz`, and `intensity` columns:

```bash
flavfinder label \
  --input raw_with_smiles.csv \
  --output labeled.csv \
  --report label_report.json
```

The output adds `label`, `flavonoid_subclass`, `matched_patterns`,
`smiles_canonical`, `inchikey`, and `smiles_error`. Filter invalid SMILES, remove
duplicates, split by compound/InChIKey or near-duplicate groups, then train P/N
models separately.

RDKit is an optional extra:

```bash
python -m pip install -e ".[chem]"
```

## What is not included

- Training data (`train_datasets/`)
- Real example spectra
- Pretrained model weights or AutoGluon predictors
- Internal development notes, work orders, or reference checkouts

The original authors and the original HEAD at port time are recorded in [`NOTICE`](./NOTICE)
and [`AUTHORS`](./AUTHORS).

## Install

```bash
python -m pip install -e ".[dev]"
```

Optional backends:

```bash
python -m pip install -e ".[autogluon]"   # reference backend
python -m pip install -e ".[lightgbm]"    # lightweight backend
```

The build backend is **hatchling**; the package is pip-installable from a wheel:

```bash
python -m build
python -m pip install dist/flavfinder_core-*.whl
```

## Quick check

```bash
flavfinder --describe
pytest
ruff check .
```

## Minimal workflow

```bash
# Audit a table
flavfinder audit --input examples/input_format.json --output audit.json

# Train (synthetic or user-provided data; no data ships here)
flavfinder train \
  --train data/train.csv \
  --test data/test.csv \
  --output-dir artifacts/model \
  --backend lightgbm

# Predict
flavfinder predict \
  --model artifacts/model \
  --input examples/input_format.json \
  --output predictions.json

# Evaluate
flavfinder evaluate \
  --model artifacts/model \
  --input data/test.csv \
  --output reports/metrics.json
```

See the [Quickstart](docs/en/02-quickstart.md) for a runnable synthetic example.

## Status

The core pipeline is implemented and covered by synthetic-data tests. The optional
AutoGluon reference backend is provided but requires the `autogluon` extra; the
LightGBM and scikit-learn backends are suitable for local checks. Data and model
artifacts are intentionally not distributed.

## Attribution

- Original work: Lvjun Guo (Ficere) `<gljx898989@163.com>`
- Port maintainer: David Niteas `<david.ql.d@foxmail.com>`

See [`NOTICE`](./NOTICE) for provenance and [`AUTHORS`](./AUTHORS) for the contributor list.

## License

Code is released under the MIT License. See [`LICENSE`](./LICENSE).
