# Preprocessing

**Level:** 2 — Use  
**Prerequisites:** [Data format](./03-data-format.md).

Two preprocessing methods are implemented:

- **Binning** (default): fixed-width m/z grid.
- **Tokenization**: learned m/z vocabulary with tolerance merging.

Both normalize the per-spectrum intensity vector by default.

## Binning

```python
from flavfinder import BinningTransformer

transformer = BinningTransformer(
    mz_min=10.0,
    mz_max=500.0,
    bin_width=0.1,
    normalization="max",
    out_of_range="drop",
)
vector = transformer.transform_peaks("100.0,300.0", "10,100")
```

### Defaults and shape

| Parameter | Default | Meaning |
|---|---|---|
| `mz_min` | `10.0` | first bin center |
| `mz_max` | `500.0` | grid upper bound |
| `bin_width` | `0.1` | bin spacing |
| `normalization` | `max` | `none`, `max`, or `l2` |
| `out_of_range` | `drop` | `drop`, `error`, or `clip` |

With the defaults, `n_bins = 4900` and feature names are `bin_0000` …
`bin_4899`.

A peak is assigned to the nearest bin center. Peaks outside the grid are:

- `drop` — ignored (default; the number is not silently reported per row),
- `error` — raise,
- `clip` — clamped to the first/last bin.

The data used during development has roughly 10% of peaks above m/z 500; if those peaks matter
for your application, increase `mz_max` or choose `error` to make the loss
visible.

### Normalization

- `max`: divide by the largest intensity; all-zero spectra stay all-zero.
- `l2`: divide by the L2 norm.
- `none`: keep raw summed intensities.

## Tokenization

```python
from flavfinder import FlavTokenizer

tokenizer = FlavTokenizer(
    mz_tol=5.0,
    mz_tol_unit="ppm",
    normalization="max",
    accumulate_unknown=True,
).fit(["100.0,200.0", "100.0002,200.0"])

vector = tokenizer.transform_peaks("100.0,300.0", "10,100")
```

- Token `0` is `UNK`.
- Learned m/z values start at token `1`.
- Close m/z values are merged into one vocabulary entry.
- `accumulate_unknown=True` keeps unknown intensity in token `0`; set it to
  `False` to discard it.
- The vector length is `1 + number_of_vocabulary_entries`.

## Selecting a method in YAML

```yaml
preprocessing:
  method: tokenization
  mz_tol: 5.0
  mz_tol_unit: ppm
  normalization: max
  accumulate_unknown: true
```

Or override the config from the CLI:

```bash
flavfinder train --config configs/P.yaml --method tokenization
```

## Persistence

Both transformers are JSON-serializable and are saved inside the model bundle:

```text
artifacts/P/preprocessing.json
```

Reload directly:

```python
from flavfinder.preprocessing import load_preprocessor

preprocessor = load_preprocessor("artifacts/P/preprocessing.json")
```

## Performance notes

- Binning uses vectorized nearest-bin assignment and `bincount`; it avoids the
  a per-peak `argmin` loop.
- Transformation is single-process by default for reproducibility. Use external
  batching if you need more throughput.
- A 25k × 4900 float64 matrix is about 1 GB; `float32` halves that at a small
  numerical cost.

**Next:** [Training](./05-training.md)
