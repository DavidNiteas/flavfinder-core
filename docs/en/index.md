# flavfinder-core documentation (English)

**Language:** English · [简体中文](../zh-CN/index.md)

`flavfinder-core` is an independent, code-only port of the flavfinder MS/MS
flavonoid classifier. It provides a config-driven training and evaluation
pipeline; it does not ship data or pretrained weights.

## Choose your path

| If you want to... | Read |
|---|---|
| Install and run a small example | [Installation](./01-installation.md) → [Quickstart](./02-quickstart.md) |
| Use your own spectra | [Data format](./03-data-format.md) → [Preprocessing](./04-preprocessing.md) → [Training](./05-training.md) |
| Score new spectra | [Prediction](./06-prediction.md) |
| Measure model quality | [Evaluation](./07-evaluation.md) → [Data audit](./08-data-audit.md) |
| Understand the method and its limits | [Method](./09-method.md) |
| Look up a command | [CLI reference](./10-cli-reference.md) |
| Use the Python API | [Python API](./11-python-api.md) |
| Tune a run | [Configuration](./12-configuration.md) |
| Fix an error | [Troubleshooting](./13-troubleshooting.md) |

## Documentation levels

- **Level 1 — Start:** installation and quickstart. No prior knowledge of the
  original implementation is required.
- **Level 2 — Use:** data format, preprocessing, training, prediction, and
  evaluation. These pages show the normal workflow.
- **Level 3 — Understand:** method, thresholds, leakage, group-aware splits, and
  limitations. Read this before trusting a reported metric.
- **Level 4 — Reference:** exact CLI flags, Python signatures, configuration
  fields, and troubleshooting.

## What is not in this repository

- `train_datasets/` or any real MS/MS spectra
- pretrained model weights or AutoGluon predictors
- internal work orders, development notes, or reference checkouts

The original project and its historical commits remain the authoritative source
for the data and provenance. See [`NOTICE`](../../NOTICE) and
[`AUTHORS`](../../AUTHORS).

## Provenance and license

- Original work: Lvjun Guo (Ficere) `<gljx898989@163.com>`
- Port maintainer: David Niteas `<david.ql.d@foxmail.com>`
- License: MIT (code only)

**Next:** [Installation](./01-installation.md)
