# Python API

**Level:** 4 — Reference  
**Prerequisites:** [CLI reference](./10-cli-reference.md).

## Schema and I/O

```python
from flavfinder import SpectrumSchema, prepare_frame, read_frame

schema = SpectrumSchema(
    mz_col="mz",
    intensity_col="intensity",
    label_col="label",
    id_col="id",
)
frame = read_frame("data.csv", schema)
prepared = prepare_frame(frame, schema, require_label=True)
```

`prepare_frame` adds `_mz_values` and `_intensity_values` object columns and
validates lengths, finiteness, and non-negativity.

## Preprocessing

```python
from flavfinder import BinningTransformer, FlavTokenizer

binning = BinningTransformer(
    mz_min=10.0,
    mz_max=500.0,
    bin_width=0.1,
    normalization="max",
    out_of_range="drop",
)
features = binning.transform(prepared, schema)
features = features[binning.feature_names_]

tokenizer = FlavTokenizer(
    mz_tol=5.0,
    mz_tol_unit="ppm",
    normalization="max",
).fit(prepared, mz_col="mz")
token_features = tokenizer.transform(prepared, schema)
```

Both support `save(path)` and `load(path)`. `FlavTokenizer.from_json(path)` is an
alias for `load`.

`DataTransformer` is a compatibility facade:

```python
from flavfinder import DataTransformer

transformer = DataTransformer(binning)
features = transformer.transform_df(frame)
```

## Training

```python
from flavfinder import (
    DataConfig,
    ModelConfig,
    PreprocessingConfig,
    TrainingConfig,
    train,
)

config = TrainingConfig(
    data=DataConfig(train="data/P/train.csv", test="data/P/test.csv"),
    preprocessing=PreprocessingConfig(method="binning"),
    model=ModelConfig(backend="lightgbm"),
    output_dir="artifacts/P",
    validation_size=0.2,
    seed=42,
)
metrics = train(config)
```

`train` returns a metrics dictionary and writes the model bundle. Supported
backends: `autogluon`, `lightgbm`, `sklearn`.

## Model bundle

```python
from flavfinder import ModelBundle

bundle = ModelBundle.load("artifacts/P")
output = bundle.predict_frame(frame, schema)
print(output[["score", "probability"]])
```

Useful attributes:

- `bundle.preprocessor` — fitted transformer
- `bundle.backend` — fitted backend
- `bundle.metadata` — config, feature names, provenance, versions
- `bundle.thresholds` — mid/high thresholds

## Prediction and evaluation

```python
from flavfinder import evaluate, predict

predictions = predict("artifacts/P", "input.json", "predictions.json")
metrics = evaluate("artifacts/P", "data/P/test.csv", "reports/P.json")
```

## Data audit

```python
from flavfinder import (
    audit_frame,
    groups_from_pairs,
    leakage_report,
    near_duplicate_pairs,
)

print(audit_frame(frame))
print(leakage_report(train_frame, test_frame))
pairs = near_duplicate_pairs(train_frame, binning, threshold=0.95)
groups = groups_from_pairs(len(train_frame), pairs)
```

## Metrics

```python
from flavfinder import (
    binary_metrics,
    bootstrap_ci,
    calibration_points,
    select_thresholds,
)

metrics = binary_metrics(y_true, y_score, threshold=0.5)
ci = bootstrap_ci(y_true, y_score, n_boot=1000, seed=42)
thresholds = select_thresholds(y_true, y_score, high_fpr=0.01)
points = calibration_points(y_true, y_score, n_bins=10)
```

## Labeling with RDKit

```python
from flavfinder import FlavonoidLabeler

labeler = FlavonoidLabeler()
result = labeler.label_smiles("O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12")
print(result.label, result.subclass, result.matched_patterns)

labeled = labeler.label_frame(frame, smiles_col="smiles", label_col="label")
summary = labeler.summary(labeled)
```

`LabelResult` fields:

| Field | Meaning |
|---|---|
| `label` | `1`, `0`, or `None` for invalid SMILES |
| `subclass` | first matching scaffold family |
| `matched_patterns` | every matching rule |
| `canonical_smiles` | RDKit canonical SMILES |
| `inchikey` | structure key |
| `error` | parse/standardization error |

Use `FlavonoidLabeler.from_yaml(path)` to override the ruleset. RDKit is an
optional extra: `pip install -e ".[chem]"`.

## Error behavior

The library raises standard exceptions with contextual messages:

- `FileNotFoundError` for missing inputs,
- `ValueError` for invalid data/config/parameters,
- `ImportError` for missing optional backends,
- `FileExistsError` for a non-empty output directory without `overwrite`.

The CLI catches these and returns exit code `2`.

**Next:** [Configuration](./12-configuration.md)
