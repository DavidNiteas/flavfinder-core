# Method and design notes

**Level:** 3 — Understand  
**Prerequisites:** [Data audit](./08-data-audit.md).

## Task

Given a tandem mass spectrum (MS/MS), predict whether the underlying compound
belongs to the flavonoid class. Positive and negative ion modes are modeled
separately.

## Reference pipeline

1. Parse comma-separated m/z and intensity arrays.
2. Preprocess:
   - **Binning:** fixed m/z grid, default 10–500 at 0.1 width (4900 features),
     per-spectrum max normalization.
   - **Tokenization:** learned m/z vocabulary at 5 ppm tolerance, token-weight
     vector, per-spectrum normalization.
3. Fit a tabular binary classifier.
4. Select `mid` and `high` decision thresholds.
5. Report AUROC/AUPRC and threshold metrics.

The reference backend is AutoGluon `TabularPredictor` with `eval_metric=roc_auc`
and `presets=optimize_for_deployment`. LightGBM and scikit-learn backends are
provided for lighter local runs and tests.

## Thresholds

- `mid`: Youden point on the validation ROC curve.
- `high`: threshold closest to a target false-positive rate (default 1%).
- `high` is forced to be at least `mid`.
- `probability` buckets: `score > high` → high; `score > mid` → mid; else low.

## What this port changes

The port keeps the method recognizable but fixes engineering and evaluation
problems in the original implementation:

| Area | Original | This port |
|---|---|---|
| Tokenizer JSON | `FlavTokenizer.from_json(path)` was called as a class method on an instance method | `from_json` is a real class method; `load` is the primary API |
| Peak parsing | list inputs could raise `UnboundLocalError` | strings, lists, tuples, and arrays are supported and validated |
| Binning | per-peak `argmin` loop | vectorized nearest-bin assignment + `bincount` |
| Normalization | binning normalized, tokenization did not | both normalize by default, configurable |
| Out-of-range peaks | silently clamped/dropped | explicit `drop` / `error` / `clip` policy |
| Thresholds | selected and reported on the test set | selected on validation; test is evaluation-only |
| Data audit | none | exact/near-duplicate and leakage tooling |
| Parallelism | `pandarallel` global side effects | deterministic single-process default |

## Design constraints

- The public repository is **code only**; data and models are not distributed.
- The code must work on user-provided data, not only on the original dataset.
- The original provenance is recorded in `NOTICE` and `AUTHORS`.
- The public history is independent of the original repository's history.

## Limitations

- No compound identifiers are provided, so group splits are approximate.
- Binning discards peaks outside the configured m/z range.
- The model is a tabular classifier, not a structure elucidation method.
- Calibration is reported but not guaranteed.
- Domain shift across instruments, ionization modes, and sample preparation is
  not solved by this repository.

## Provenance

Original project: <https://github.com/Ficere/flavfinder>  
Original author: Lvjun Guo (Ficere) `<gljx898989@163.com>`  
Original HEAD at port time: `2517ca4da6100a918418c7e06e5a98ae67d687ce`

**Next:** [CLI reference](./10-cli-reference.md)
