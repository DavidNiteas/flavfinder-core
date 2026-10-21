# Configs

`P.yaml` and `N.yaml` are templates for positive and negative ion modes.

Data is **not** included in this repository. Put your CSV/JSON tables under a local
`data/` directory (ignored by Git), or pass explicit paths:

```bash
flavfinder train --config configs/P.yaml \
  --train /path/to/P/train.csv \
  --test /path/to/P/test.csv \
  --output-dir artifacts/P
```

To use the lightweight backend:

```bash
flavfinder train --config configs/P.yaml --backend lightgbm --output-dir artifacts/P-lightgbm
```

To use tokenization instead of binning:

```bash
flavfinder train --config configs/P.yaml --method tokenization --output-dir artifacts/P-token
```
