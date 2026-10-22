# Troubleshooting

**Level:** 4 — Reference  
**Prerequisites:** any of the guides.

## Data errors

### `missing required column(s): mz, intensity`

Your table does not use the default columns. Pass `--mz-col` /
`--intensity-col`, or set them in YAML.

### `mz and intensity lengths differ`

Each row must have exactly one intensity per m/z value. Check trailing commas
and truncated fields.

### `contains an empty value`

A comma-separated field has an empty element, for example `"100,200,"`.
Remove the trailing comma.

### `contains non-finite values`

`NaN`, `inf`, or non-numeric text is present. Empty cells are not supported.

### `label must contain only 0 and 1`

Training and evaluation labels are binary. Encode classes explicitly.

### `training data must contain both classes`

The training split has only one class. Provide both, or check that your label
column is not constant.

## Preprocessing errors

### `peak(s) outside [mz_min, mz_max]`

The preprocessing method is `out_of_range: error` and a peak is outside the
grid. Use `drop`/`clip`, or widen the grid.

### `tokenizer is not fitted`

Call `fit` before `transform`, or load a saved preprocessor.

### `cannot fit tokenizer on empty m/z values`

Every training spectrum was empty or the selected column is wrong.

## Model errors

### `AutoGluon is optional; install with ...`

```bash
python -m pip install -e ".[autogluon]"
```

### `LightGBM is optional; install with ...`

```bash
python -m pip install -e ".[lightgbm]"
```

### `RDKit is optional; install with ...`

```bash
python -m pip install -e ".[chem]"
```

### `flavfinder label` reports invalid SMILES

The row is kept with `smiles_error` set and `label` empty. Drop these rows before
training. Don't use them as negatives.

### `output directory is not empty`

Set `overwrite: true` or pass `--overwrite`. This prevents accidentally
overwriting a previous model.

### `threshold selection requires both classes`

The validation split contains one class. Use a larger validation set, provide
an explicit validation table, or inspect the split.

### AutoGluon is slow or runs out of memory

- Reduce `time_limit` or use `presets: medium_quality`.
- Use `--backend lightgbm` for a quick baseline.
- Reduce `mz_max` / increase `bin_width` to shrink the feature matrix.
- Close other processes; 4900 features × tens of thousands of rows is large.

## Prediction errors

### `No such file or directory: .../metadata.json`

`--model` must point to a model **directory**, not to a file inside it.

### Scores look shifted compared with training

Check that the same preprocessing method and parameters are used. The bundle
stores the fitted preprocessor; do not re-fit it on new data.

### All probabilities are `low`

The `high`/`mid` thresholds were selected on a validation split that may not
match your new data distribution. Inspect `thresholds.json`; consider
recalibrating on a representative validation set.

## Reproducibility

- Set `seed` and `model.random_state`.
- Record `metadata.json` (package/Python versions, config, feature names).
- Keep the exact input files; do not edit them between runs.
- Use the same backend and parameters when comparing metrics.

## Build problems

### `python -m build` fails with `ensurepip is not available`

The isolated build environment cannot create a virtualenv. Use a normal Python
installation/venv, or install hatchling and build without isolation:

```bash
python -m pip install hatchling build
python -m build --no-isolation
```

## Still stuck?

Open an issue with:

1. the command you ran,
2. the full error message,
3. the shape/columns of your input (not the raw spectra if sensitive),
4. `flavfinder --version` and `python --version`.

**Next:** [Documentation index](./index.md)
