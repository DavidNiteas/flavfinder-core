# Installation

**Level:** 1 — Start  
**Prerequisites:** Python 3.10–3.12 and `pip`.

## Install from a checkout

```bash
git clone https://github.com/DavidNiteas/flavfinder-core.git
cd flavfinder-core
python -m pip install -e ".[dev]"
```

The base install includes NumPy, pandas, SciPy, scikit-learn, PyYAML, tqdm, and
joblib. Optional backends are installed separately.

## Optional backends

### AutoGluon (reference backend)

```bash
python -m pip install -e ".[autogluon]"
```

AutoGluon is a large dependency. Use it when you want to reproduce the
reference tabular-model workflow.

### LightGBM (fast local backend)

```bash
python -m pip install -e ".[lightgbm]"
```

LightGBM is much lighter and is useful for quick experiments and local checks.

### scikit-learn (tests and tiny datasets)

The scikit-learn backend is included in the base install and is intended for
smoke tests and very small datasets. It is not a replacement for AutoGluon or
LightGBM on the full data.

## Verify the install

```bash
flavfinder --version
flavfinder --describe
```

Expected behavior:

- `--version` prints the package version.
- `--describe` explains that this is an independent code-only port and that data
  and models are not included.

## Build a wheel

The build backend is **hatchling**:

```bash
python -m build
python -m pip install dist/flavfinder_core-*.whl
```

## Docker

The repository includes a code-only Dockerfile. It does **not** include data,
models, tests, or docs:

```bash
docker build -t flavfinder-core:local .
docker run --rm flavfinder-core:local --describe
```

The Dockerfile installs the base package only. For AutoGluon or LightGBM, extend
the image or install the extra at runtime.

## Install from a wheel

```bash
python -m pip install flavfinder_core-0.1.0-py3-none-any.whl
```

## Common installation problems

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: autogluon` | `pip install -e ".[autogluon]"` |
| `ModuleNotFoundError: lightgbm` | `pip install -e ".[lightgbm]"` |
| Python 3.13 selected | Use Python 3.10–3.12 (`requires-python` excludes 3.13) |
| Build fails on `hatchling` | Upgrade `pip` and retry; hatchling is declared in `pyproject.toml` |

**Next:** [Quickstart](./02-quickstart.md)
