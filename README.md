# flavfinder-core

**English** · [简体中文](#zh-cn)

<a id="english"></a>

## English

An independent, code-only implementation of the **flavfinder** MS/MS flavonoid
classifier.

### Documentation

- **English:** [Documentation index](docs/en/index.md)
- **简体中文：** [文档索引](docs/zh-CN/index.md)

The docs use progressive disclosure:

| Level | English | 简体中文 |
|---|---|---|
| 0 — Scope | [Why code-only](docs/en/14-why-code-only.md) | [为什么只发代码](docs/zh-CN/14-why-code-only.md) |
| 1 — Install & run | [Installation](docs/en/01-installation.md) → [Quickstart](docs/en/02-quickstart.md) | [安装](docs/zh-CN/01-installation.md) → [快速开始](docs/zh-CN/02-quickstart.md) |
| 2 — Use your data | [Data format](docs/en/03-data-format.md) → [Build your own dataset](docs/en/15-build-your-own-dataset.md) → [Training](docs/en/05-training.md) | [数据格式](docs/zh-CN/03-data-format.md) → [自建数据集](docs/zh-CN/15-build-your-own-dataset.md) → [训练](docs/zh-CN/05-training.md) |
| 3 — Trust the result | [Evaluation](docs/en/07-evaluation.md) → [Data audit](docs/en/08-data-audit.md) → [Method](docs/en/09-method.md) | [评估](docs/zh-CN/07-evaluation.md) → [数据审计](docs/zh-CN/08-data-audit.md) → [方法](docs/zh-CN/09-method.md) |
| 4 — Reference | [CLI](docs/en/10-cli-reference.md) · [API](docs/en/11-python-api.md) · [Config](docs/en/12-configuration.md) | [CLI](docs/zh-CN/10-cli-reference.md) · [API](docs/zh-CN/11-python-api.md) · [配置](docs/zh-CN/12-configuration.md) |

### What this repository is

`flavfinder-core` is a from-scratch, release-oriented implementation of the
flavfinder MS/MS flavonoid classifier. It provides a clean, installable, testable,
and reproducible codebase with:

- MS/MS spectrum ingestion and validation
- Binning and tokenization preprocessing
- Pluggable model backends: AutoGluon, LightGBM, scikit-learn
- Training, prediction, evaluation, and threshold selection
- Data auditing: exact/near duplicates, leakage reports, group-aware splits
- RDKit-based flavonoid labeling from SMILES (`flavfinder label`)
- Config-driven CLI and Python API
- Synthetic-data tests only; no real spectra in the repository

### Why this repository is code-only

We intentionally do **not** distribute training data or pretrained models:

1. **Model weights are not convenient to ship.** A fitted tabular bundle can be
   large, while training is reproducible on a workstation and should be repeated
   on the user's own spectra. We ship the full training pipeline and configs.
2. **A frozen dataset would be stale.** Public MS/MS libraries such as GNPS,
   MassBank, and MoNA contain far more spectra, newer records, and richer
   metadata than any snapshot we could bundle. The data used during development
   is an older reference version, not a recommended training source.
3. **Users should build labels from current structures.** We provide an
   RDKit-based labeling tool that turns a table with MS/MS and SMILES into labeled
   flavonoid/non-flavonoid data using a subclass-aware SMARTS ruleset.

This is a deliberate distribution choice, not a missing feature. See
[Why code-only](docs/en/14-why-code-only.md) and
[Build your own dataset](docs/en/15-build-your-own-dataset.md).

### Build your own dataset

If your table has `smiles`, `mz`, and `intensity` columns:

```bash
flavfinder label \
  --input raw_with_smiles.csv \
  --output labeled.csv \
  --report label_report.json
```

The output adds `label`, `flavonoid_subclass`, `matched_patterns`,
`smiles_canonical`, `inchikey`, and `smiles_error`. Filter invalid SMILES, remove
duplicates, split by compound/InChIKey or near-duplicate groups, then train P/N
models separately.

RDKit is an optional extra:

```bash
python -m pip install -e ".[chem]"
```

### What is not included

- Training data (`train_datasets/`)
- Real example spectra
- Pretrained model weights or AutoGluon predictors
- Internal development notes or work orders

The authors are listed in [`AUTHORS`](./AUTHORS); distribution scope is recorded
in [`NOTICE`](./NOTICE).

### Install

```bash
python -m pip install -e ".[dev]"
```

Optional extras:

```bash
python -m pip install -e ".[autogluon]"   # reference backend
python -m pip install -e ".[lightgbm]"    # lightweight backend
python -m pip install -e ".[chem]"        # RDKit labeling
```

The build backend is **hatchling**; the package is pip-installable from a wheel:

```bash
python -m build
python -m pip install dist/flavfinder_core-*.whl
```

### Quick check

```bash
flavfinder --describe
pytest
ruff check .
```

### Minimal workflow

```bash
# Audit a table
flavfinder audit --input examples/input_format.json --output audit.json

# Label MS/MS + SMILES
flavfinder label --input raw_with_smiles.csv --output labeled.csv

# Train (user-provided data; no data ships here)
flavfinder train \
  --train data/train.csv \
  --test data/test.csv \
  --output-dir artifacts/model \
  --backend lightgbm

# Predict
flavfinder predict \
  --model artifacts/model \
  --input examples/input_format.json \
  --output predictions.json

# Evaluate
flavfinder evaluate \
  --model artifacts/model \
  --input data/test.csv \
  --output reports/metrics.json
```

See the [Quickstart](docs/en/02-quickstart.md) for a runnable synthetic example.

### Status

The core pipeline is implemented and covered by synthetic-data tests. The optional
AutoGluon reference backend requires the `autogluon` extra; LightGBM and
scikit-learn are suitable for local checks. Data and model artifacts are
intentionally not distributed.

### Authors

- Lvjun Guo (Ficere) `<gljx898989@163.com>`
- David Niteas `<david.ql.d@foxmail.com>`

See [`AUTHORS`](./AUTHORS) and [`NOTICE`](./NOTICE).

### License

Code is released under the MIT License. See [`LICENSE`](./LICENSE).

---

<a id="zh-cn"></a>

## 简体中文

[English](#english) · **简体中文**

**flavfinder** MS/MS 黄酮分类器的独立、纯代码实现。

### 文档

- **English:** [Documentation index](docs/en/index.md)
- **简体中文：** [文档索引](docs/zh-CN/index.md)

文档按渐进式组织：

| 层级 | English | 简体中文 |
|---|---|---|
| 0 — 范围 | [Why code-only](docs/en/14-why-code-only.md) | [为什么只发代码](docs/zh-CN/14-why-code-only.md) |
| 1 — 安装与运行 | [Installation](docs/en/01-installation.md) → [Quickstart](docs/en/02-quickstart.md) | [安装](docs/zh-CN/01-installation.md) → [快速开始](docs/zh-CN/02-quickstart.md) |
| 2 — 使用自己的数据 | [Data format](docs/en/03-data-format.md) → [Build your own dataset](docs/en/15-build-your-own-dataset.md) → [Training](docs/en/05-training.md) | [数据格式](docs/zh-CN/03-data-format.md) → [自建数据集](docs/zh-CN/15-build-your-own-dataset.md) → [训练](docs/zh-CN/05-training.md) |
| 3 — 信任结果 | [Evaluation](docs/en/07-evaluation.md) → [Data audit](docs/en/08-data-audit.md) → [Method](docs/en/09-method.md) | [评估](docs/zh-CN/07-evaluation.md) → [数据审计](docs/zh-CN/08-data-audit.md) → [方法](docs/zh-CN/09-method.md) |
| 4 — 参考 | [CLI](docs/en/10-cli-reference.md) · [API](docs/en/11-python-api.md) · [Config](docs/en/12-configuration.md) | [CLI](docs/zh-CN/10-cli-reference.md) · [API](docs/zh-CN/11-python-api.md) · [配置](docs/zh-CN/12-configuration.md) |

### 这个仓库是什么

`flavfinder-core` 是 flavfinder MS/MS 黄酮分类器的从零实现，面向可发布、可安装、
可测试、可复现的代码库：

- MS/MS 谱图读取与校验
- Binning 与 Tokenization 预处理
- 可插拔模型后端：AutoGluon、LightGBM、scikit-learn
- 训练、预测、评估与阈值选择
- 数据审计：精确/近重复、泄漏报告、分组切分
- 基于 RDKit 的 SMILES 黄酮标注（`flavfinder label`）
- 配置驱动 CLI 与 Python API
- 仅使用合成数据测试；仓库不含真实谱图

### 为什么只发代码

我们刻意**不**分发训练数据和预训练模型：

1. **模型权重不方便分发。** 拟合后的表格模型 bundle 可能很大；训练流程可复现，
   单机可完成，应该用户在自备谱图上重训。我们提供完整训练流程与配置。
2. **冻结数据会过时。** GNPS、MassBank、MoNA 等公开 MS/MS 库比任何快照都更大、
   更新、元数据更丰富。开发时使用的数据是较旧的参考版本，不推荐作为训练数据源。
3. **用户应基于当前结构生成标签。** 我们提供基于 RDKit 的标注工具，用亚类感知的
   SMARTS 规则把“MS/MS + SMILES”表转成黄酮/非黄酮标签。

这是刻意的分发选择，不是缺失功能。见
[为什么只发代码](docs/zh-CN/14-why-code-only.md) 与
[自建数据集](docs/zh-CN/15-build-your-own-dataset.md)。

### 自建数据集

如果表里有 `smiles`、`mz`、`intensity` 列：

```bash
flavfinder label \
  --input raw_with_smiles.csv \
  --output labeled.csv \
  --report label_report.json
```

输出会增加 `label`、`flavonoid_subclass`、`matched_patterns`、
`smiles_canonical`、`inchikey` 与 `smiles_error`。过滤非法 SMILES、去重、
按化合物/InChIKey 或近重复组切分，然后分别训练 P/N 模型。

RDKit 是可选 extra：

```bash
python -m pip install -e ".[chem]"
```

### 本仓库不包含

- 训练数据（`train_datasets/`）
- 真实示例谱图
- 预训练模型权重或 AutoGluon predictor
- 内部开发笔记或工单

作者见 [`AUTHORS`](./AUTHORS)，分发范围见 [`NOTICE`](./NOTICE)。

### 安装

```bash
python -m pip install -e ".[dev]"
```

可选 extra：

```bash
python -m pip install -e ".[autogluon]"   # 参考后端
python -m pip install -e ".[lightgbm]"    # 轻量后端
python -m pip install -e ".[chem]"        # RDKit 标注
```

构建后端是 **hatchling**，可从 wheel 安装：

```bash
python -m build
python -m pip install dist/flavfinder_core-*.whl
```

### 快速检查

```bash
flavfinder --describe
pytest
ruff check .
```

### 最小工作流

```bash
# 审计
flavfinder audit --input examples/input_format.json --output audit.json

# 标注 MS/MS + SMILES
flavfinder label --input raw_with_smiles.csv --output labeled.csv

# 训练（用户自备数据；仓库不含数据）
flavfinder train \
  --train data/train.csv \
  --test data/test.csv \
  --output-dir artifacts/model \
  --backend lightgbm

# 预测
flavfinder predict \
  --model artifacts/model \
  --input examples/input_format.json \
  --output predictions.json

# 评估
flavfinder evaluate \
  --model artifacts/model \
  --input data/test.csv \
  --output reports/metrics.json
```

可运行的合成数据示例见 [快速开始](docs/zh-CN/02-quickstart.md)。

### 状态

核心流程已实现并有合成数据测试覆盖。AutoGluon 参考后端需要 `autogluon` extra；
LightGBM 与 scikit-learn 适合本地检查。数据与模型产物刻意不分发。

### 作者

- Lvjun Guo (Ficere) `<gljx898989@163.com>`
- David Niteas `<david.ql.d@foxmail.com>`

见 [`AUTHORS`](./AUTHORS) 与 [`NOTICE`](./NOTICE)。

### 许可证

代码使用 MIT 许可证。见 [`LICENSE`](./LICENSE)。
