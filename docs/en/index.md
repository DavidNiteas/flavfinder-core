# flavfinder-core documentation (English)

**Language:** English · [简体中文](../zh-CN/index.md)

`flavfinder-core` is an independent, code-only implementation of the flavfinder
MS/MS flavonoid classifier. It provides a config-driven training and evaluation
pipeline; it does not ship data or pretrained weights.

## Choose your path

| If you want to... | Read |
|---|---|
| Understand why data/models are not shipped | [Why code-only](./14-why-code-only.md) |
| Install and run a small example | [Installation](./01-installation.md) → [Quickstart](./02-quickstart.md) |
| Use your own spectra | [Data format](./03-data-format.md) → [Preprocessing](./04-preprocessing.md) → [Training](./05-training.md) |
| Build a fresh dataset from public data + SMILES | [Build your own dataset](./15-build-your-own-dataset.md) |
| Score new spectra | [Prediction](./06-prediction.md) |
| Measure model quality | [Evaluation](./07-evaluation.md) → [Data audit](./08-data-audit.md) |
| Understand the method and its limits | [Method](./09-method.md) |
| Look up a command | [CLI reference](./10-cli-reference.md) |
| Use the Python API | [Python API](./11-python-api.md) |
| Tune a run | [Configuration](./12-configuration.md) |
| Fix an error | [Troubleshooting](./13-troubleshooting.md) |

## Documentation levels

- **Level 0 — Scope:** why the repository is code-only and how to build your own
  dataset from public data.
- **Level 1 — Start:** installation and quickstart. No prior knowledge of the method is required.
- **Level 2 — Use:** data format, preprocessing, training, prediction, and
  evaluation. These pages show the normal workflow.
- **Level 3 — Understand:** method, thresholds, leakage, group-aware splits, and
  limitations. Read this before trusting a reported metric.
- **Level 4 — Reference:** exact CLI flags, Python signatures, configuration
  fields, and troubleshooting.

## What is not in this repository

- `train_datasets/` or any real MS/MS spectra
- pretrained model weights or AutoGluon predictors
- internal work orders or development notes

Authorship and distribution scope are recorded in [`NOTICE`](../../NOTICE) and
[`AUTHORS`](../../AUTHORS).

## Authors and license

- Lvjun Guo (Ficere) `<gljx898989@163.com>`
- David Niteas `<david.ql.d@foxmail.com>`
- License: MIT (code only)

**Next:** [Installation](./01-installation.md)
