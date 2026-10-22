# Evaluation

**Level:** 2 — Use  
**Prerequisites:** [Prediction](./06-prediction.md).

## CLI

```bash
flavfinder evaluate \
  --model artifacts/P \
  --input data/P/test.csv \
  --output reports/P_metrics.json
```

`--no-bootstrap` skips resampling for a faster report. `--n-boot` and `--seed`
control the bootstrap.

## Metrics

| Metric | Why it matters |
|---|---|
| AUROC | ranking quality across all thresholds |
| AUPRC | ranking quality under class imbalance |
| Brier | probabilistic calibration (lower is better) |
| Accuracy / precision / recall / F1 | behavior at the selected threshold |
| Confusion matrix | concrete false-positive / false-negative counts |
| Bootstrap CI | uncertainty from the finite test set |
| Calibration points | reliability curve (mean predicted vs observed) |

MS/MS data is often imbalanced, so **AUPRC is usually more informative than
accuracy**. A high AUROC with poor AUPRC can still be a weak screening model.

## Thresholds

The evaluation uses the `mid` threshold from the model bundle by default. The
bundle also stores the `high` threshold and the metrics at both thresholds:

```json
{
  "mid": {"value": 0.37, "fpr": 0.12, "tpr": 0.78, "accuracy": 0.81},
  "high": {"value": 0.82, "fpr": 0.01, "tpr": 0.42, "precision": 0.91}
}
```

Thresholds are selected on the validation split during training, never on the
test split. Reusing a test set to tune thresholds inflates the reported result.

## Python API

```python
from flavfinder import evaluate

metrics = evaluate(
    model_dir="artifacts/P",
    input_path="data/P/test.csv",
    output_path="reports/P_metrics.json",
    with_bootstrap=True,
    n_boot=1000,
    seed=42,
)
print(metrics["auroc"], metrics["auprc"])
```

## Interpreting a report

1. Check `n` and `positive_rate`: a tiny positive class makes AUPRC noisy.
2. Check the bootstrap interval, not just the point estimate.
3. Check the confusion matrix at the threshold you plan to use.
4. Check calibration if you interpret `score` as a probability.
5. Check [Data audit](./08-data-audit.md) for leakage before trusting any metric.
6. Report **random-split** and **group-split** metrics separately. Use the
   group-split result as the headline; the random-split result is an optimistic
   reference.

## What evaluation does not prove

A good test score does not establish:

- performance on a different instrument, collision energy, or sample prep,
- performance on a different chemical class,
- clinical or regulatory validity.

Document the domain shift and validate on an external set when possible.

**Next:** [Data audit](./08-data-audit.md)
