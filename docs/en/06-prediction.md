# Prediction

**Level:** 2 — Use  
**Prerequisites:** [Training](./05-training.md).

`flavfinder-core` does not ship pretrained models. Train or obtain a model
bundle first.

## CLI

```bash
flavfinder predict \
  --model artifacts/P \
  --input examples/input_format.json \
  --output predictions.json
```

The input may be CSV or JSON. Column names default to `mz`, `intensity`, and
`id`; override them with `--mz-col`, `--intensity-col`, and `--id-col`.

## Output

The output keeps the input columns and adds:

| Column | Meaning |
|---|---|
| `score` | positive-class probability in `[0, 1]` |
| `probability` | `high` if `score > high threshold`, `mid` if `score > mid`, otherwise `low` |

Example:

```json
[
  {
    "id": "compound-1",
    "mz": "100.0,150.0,200.0",
    "intensity": "10,50,100",
    "score": 0.82,
    "probability": "high"
  }
]
```

## Python API

```python
from flavfinder import predict

predictions = predict(
    model_dir="artifacts/P",
    input_path="examples/input_format.json",
    output_path="predictions.json",
)
print(predictions[["id", "score", "probability"]])
```

## Loading a bundle directly

```python
from flavfinder import ModelBundle

bundle = ModelBundle.load("artifacts/P")
print(bundle.metadata["backend"])
print(bundle.metadata["feature_names"][:3])
```

## Batch behavior

- Rows are scored independently.
- Invalid rows raise an error; they are not silently skipped.
- Spectra with peaks outside the binning grid follow the preprocessing
  `out_of_range` policy chosen at training time.
- Unknown tokenization peaks go to `UNK` if `accumulate_unknown` was enabled.

## No model? No problem

If you only have code and data, train first:

```bash
flavfinder train --config configs/P.yaml --train data/P/train.csv --output-dir artifacts/P
```

**Next:** [Evaluation](./07-evaluation.md)
