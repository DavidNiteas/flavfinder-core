# AGENTS.md

Instructions for AI assistants working in `flavfinder-core`.

## What this repo is

`flavfinder-core` is a Python package for MS/MS flavonoid classification. It reads
spectra, preprocesses them, trains a model, predicts, evaluates, and checks for
data leakage. It does not ship training data or model weights.

RDKit is optional. It is only needed for `flavfinder label`.

## First, figure out what the user wants

| User asks for | What to do |
|---|---|
| "Train a model" | check the data, label it if SMILES are available, audit, split, train |
| "Predict these spectra" | find a trained bundle; if none, train one first |
| "Build a dataset" | label SMILES, deduplicate, split by compound or near-duplicate group |
| "Is this a flavonoid?" | explain that the model returns a score, not a structure assignment |
| "Just run something" | use the synthetic quickstart and say it is a smoke test |

Do not start a long training run before checking the data, ion mode, and backend.
Do not invent a result if no data or model is available.

## Hard rules

- Do not commit training data, real spectra, model weights, or generated artifacts.
- Do not report a metric you did not compute. Say which split and command produced it.
- Do not treat invalid SMILES as negative examples. Drop them.
- Do not tune thresholds on the test split. Use validation.
- Split by compound/InChIKey or near-duplicate group. A random split is only an
  optimistic reference.
- Train positive and negative ion modes separately.
- Do not add private repository URLs, private paths, or references to internal
  work orders.
- Keep changes small and run the checks before answering.

## Setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev,lightgbm]"
```

Optional:

```bash
python -m pip install -e ".[chem]"       # RDKit, for flavfinder label
python -m pip install -e ".[autogluon]"  # reference tabular backend
```

There is no CI in this repo. Run the checks locally.

## Data sources: talk to the user first

Don't pick a database silently. The source determines coverage, label quality,
ion mode, and licensing. Ask the user:

- Do you already have MS/MS data, or do you want to pull from a public library?
- Which ion mode: positive, negative, or both?
- Do the records have SMILES or InChIKey? Without structures, `flavfinder label`
  cannot assign labels.
- Which instrument and collision energy? Do you want one domain or a mix?
- Which license can you accept? Some libraries are commercial.
- Do you need curated reference spectra, or raw LC-MS/MS runs that still need
  processing?

| Source | Good for | Structures | Notes |
|---|---|---|---|
| **GNPS** | natural products, community libraries, molecular networks | often in library exports | open/community; check each library's license |
| **MassBank** (EU/JP) | curated reference MS/MS | many records | free; license and metadata vary per record |
| **MoNA** | aggregated public libraries | often | free; check each record's license |
| **HMDB** | human metabolites | yes | academic terms; commercial use may need a license |
| **NIST** | high-quality reference spectra | yes | commercial; do not redistribute |
| **METLIN** | standards and reference spectra | yes | commercial; do not redistribute |
| **mzCloud** | high-resolution MS/MS | yes | commercial; do not redistribute |
| **MassIVE** | raw LC-MS/MS datasets | not always | raw data; needs processing and structure linking |
| **MetaboLights** | study-level metabolomics data | not always | raw/processed; metadata quality varies |
| **Metabolomics Workbench** | study-level metabolomics data | not always | raw/processed; metadata quality varies |

Recommendations:

- **Free/open starting point:** GNPS + MassBank + MoNA.
- **Human metabolites:** HMDB + MoNA/GNPS.
- **Commercial access already available:** NIST, METLIN, or mzCloud.
- **Raw runs:** MassIVE, MetaboLights, or Metabolomics Workbench; expect
  preprocessing and structure matching before training.
- **No structures:** stop and ask for SMILES/InChIKey. Do not label by m/z alone.
- **No preference:** start with one source, manually check 20–50 records, then
  scale. Don't mix sources until you've checked ion mode, collision energy, and
  instrument effects.

Keep `source`, license, ion mode, instrument, and collision energy in the output
table. Don't redistribute licensed spectra.

## Data gate

A spectrum table needs `mz`, `intensity`, and a `label` for training. Each row is
one spectrum; `mz` and `intensity` are comma-separated strings.

Check the input before training:

```bash
flavfinder audit --input data.csv --output audit.json
```

If the table has SMILES:

```bash
flavfinder label \
  --input data.csv \
  --output labeled.csv \
  --report label_report.json
```

Then check:

- `smiles_error` is empty,
- `label` is not empty,
- duplicate InChIKeys and conflicting labels are handled,
- P and N modes are separated.

If the user has no data, ask for an MS/MS + SMILES table. Do not fabricate
spectra. The synthetic quickstart is for smoke tests, not for scientific claims.

## Split

For compound-level data, use InChIKey as the group. For spectra without reliable
structures, use near-duplicate groups:

```python
from flavfinder import BinningTransformer, near_duplicate_pairs, groups_from_pairs

pairs = near_duplicate_pairs(train_frame, BinningTransformer(), threshold=0.95)
groups = groups_from_pairs(len(train_frame), pairs)
```

Then use `StratifiedGroupKFold` or `flavfinder.group_split_indices` with labels.
Keep the test split untouched.

## Train

```bash
flavfinder train \
  --train train.csv \
  --validation validation.csv \
  --test test.csv \
  --output-dir artifacts/model \
  --backend lightgbm
```

If `--validation` is omitted, the trainer uses 20% of the training data,
stratified by label. Use `--backend autogluon` only when the user wants the
reference backend and has the extra installed. Use `--overwrite` only when the
user agrees to replace an existing model.

Outputs:

```text
artifacts/model/
├── preprocessing.json
├── backend/
├── thresholds.json
├── metrics.json
└── metadata.json
```

## Predict and evaluate

```bash
flavfinder predict --model artifacts/model --input new.csv --output predictions.json
flavfinder evaluate --model artifacts/model --input test.csv --output metrics.json
```

`score` is the positive-class probability. `probability` is `high`, `mid`, or
`low` based on the stored thresholds. Do not reinterpret `score` as a calibrated
clinical risk.

## Missing dependencies

| Error | Fix |
|---|---|
| `RDKit is optional` | `python -m pip install -e ".[chem]"` |
| `LightGBM is optional` | `python -m pip install -e ".[lightgbm]"` |
| `AutoGluon is optional` | `python -m pip install -e ".[autogluon]"` |

## Before you answer

Run what is relevant:

```bash
ruff check .
mypy src/flavfinder
pytest
flavfinder --version
```

Also check:

```bash
git status --short
```

If a file is a data or model artifact, stop and remove it from the commit.

When you report results, include:

- the command,
- the split (train/validation/test),
- the metrics (AUROC, AUPRC, and the threshold used),
- what was not run or not available.

## If the user says "just give me the result"

1. Look for attached data or a data directory. If there is none, ask for the
   table or the public library export.
2. If they only want to see the pipeline work, run the synthetic quickstart and
   label it as a demo.
3. Never make up scores or predictions.

## 中文速览

先确认用户是要训练、预测、建数据集，还是只跑个示例。没有数据就不要编，先和用户
讨论来源：开放数据优先 GNPS + MassBank + MoNA；人类代谢物可看 HMDB；NIST、METLIN、
mzCloud 是商业库，先确认用户有授权。确认许可证、离子模式、仪器和碰撞能，再要
MS/MS + SMILES 表。有 SMILES 就用 `flavfinder label`，删掉非法结构，去重，按
化合物/InChIKey 或近重复组切分。正负离子模式分开训练，测试集不调阈值。不要提交
数据、真实谱图、模型权重或生成产物。回答时给出实际命令、数据切分和指标，不要编造
没跑过的结果。
