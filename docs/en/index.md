# flavfinder-core documentation (English)

**Language:** English · [简体中文](../zh-CN/index.md)

`flavfinder-core` is an independent, code-only implementation of the flavfinder
MS/MS flavonoid classifier. It provides a config-driven training and evaluation
pipeline; it does not ship data or pretrained weights.

## Pick a starting point

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

## How to read these docs

- **First time here?** [Install](./01-installation.md), then run the [Quickstart](./02-quickstart.md).
- **Have your own spectra?** [Data format](./03-data-format.md) → [Build your own dataset](./15-build-your-own-dataset.md) → [Training](./05-training.md).
- **Need to trust a metric?** [Evaluation](./07-evaluation.md) → [Data audit](./08-data-audit.md) → [Method](./09-method.md).
- **Looking for a flag or signature?** [CLI](./10-cli-reference.md), [Python API](./11-python-api.md), [Configuration](./12-configuration.md).

## Not in this repo

- `train_datasets/` or any real MS/MS spectra
- pretrained model weights or AutoGluon predictors
- internal work orders or development notes

Authors are in [`AUTHORS`](../../AUTHORS). What is shipped is in [`NOTICE`](../../NOTICE).

## Authors and license

- Lvjun Guo (Ficere) `<gljx898989@163.com>`
- David Niteas `<david.ql.d@foxmail.com>`
- License: MIT (code only)

**Next:** [Installation](./01-installation.md)
