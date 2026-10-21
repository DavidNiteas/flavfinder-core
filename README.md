# flavfinder-core

An independent, code-only port of the **flavfinder** MS/MS flavonoid classifier.

> This is **not** the original repository. It has its own Git history and does **not**
> include the original training data, real MS/MS example spectra, or pretrained models.

## What this repository is

`flavfinder-core` is a from-scratch, release-oriented port of the original
[`Ficere/flavfinder`](https://github.com/Ficere/flavfinder) implementation. The goal is a
clean, installable, testable, and reproducible codebase that implements the full method:

- MS/MS spectrum ingestion and validation
- Binning and tokenization preprocessing
- Model training, prediction, and evaluation
- Data auditing and leakage checks
- Config-driven CLI workflows

## What is not included

- Training data (`train_datasets/`)
- Real example spectra
- Pretrained model weights or AutoGluon predictors
- Internal development notes, work orders, or reference checkouts

The original authors and the original HEAD at port time are recorded in [`NOTICE`](./NOTICE)
and [`AUTHORS`](./AUTHORS). The original project remains the reference for its data and
historical commits.

## Status

Early port. The package skeleton, attribution, and release guard are in place. The
preprocessing, model, evaluation, and CLI modules are being ported in subsequent commits.

## Install

```bash
python -m pip install -e ".[dev]"
```

Optional backends:

```bash
python -m pip install -e ".[autogluon]"   # reference backend
python -m pip install -e ".[lightgbm]"    # lightweight backend
```

## Quick check

```bash
flavfinder --describe
pytest
ruff check .
```

## Attribution

- Original work: Lvjun Guo (Ficere) `<gljx898989@163.com>`
- Port maintainer: David Niteas `<david.ql.d@foxmail.com>`

See [`NOTICE`](./NOTICE) for provenance and [`AUTHORS`](./AUTHORS) for the contributor list.

## License

Code is released under the MIT License. See [`LICENSE`](./LICENSE).
