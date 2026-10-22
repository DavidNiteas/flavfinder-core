# flavfinder-core

**English** · [简体中文](#zh-cn)

<a id="english"></a>

## English

`flavfinder-core` is a code-only implementation of the flavfinder MS/MS flavonoid
classifier. It covers the whole pipeline: read spectra, preprocess, train,
predict, evaluate, and check for data leakage.

### Docs

- **English:** [Documentation index](docs/en/index.md)
- **简体中文：** [文档索引](docs/zh-CN/index.md)

The docs are ordered by how deep you want to go:

| If you need to... | Read |
|---|---|
| Run something once | [Installation](docs/en/01-installation.md) → [Quickstart](docs/en/02-quickstart.md) |
| Use your own spectra | [Data format](docs/en/03-data-format.md) → [Build your own dataset](docs/en/15-build-your-own-dataset.md) → [Training](docs/en/05-training.md) |
| Check whether a result is trustworthy | [Evaluation](docs/en/07-evaluation.md) → [Data audit](docs/en/08-data-audit.md) → [Method](docs/en/09-method.md) |
| Look up a command or signature | [CLI](docs/en/10-cli-reference.md) · [API](docs/en/11-python-api.md) · [Config](docs/en/12-configuration.md) |

### What's here

- MS/MS spectrum reading and validation
- Binning and tokenization
- AutoGluon, LightGBM, and scikit-learn backends
- Training, prediction, evaluation, and threshold selection
- Data audit: exact/near duplicates, leakage reports, group splits
- RDKit-based labeling from SMILES (`flavfinder label`)
- A small CLI and a Python API

Tests use synthetic spectra. There are no real spectra in the repository.

### No data or model files

The repo doesn't include training data or trained weights. Two reasons:

1. **Model bundles are big.** Training is reproducible, and a workstation run
   doesn't take long. How long depends on data size, feature width, and backend.
   It's easier to retrain on your own spectra than to pass around a large bundle.
2. **Bundled data goes stale.** GNPS, MassBank, and MoNA have more spectra, newer
   records, and better metadata than any snapshot we could commit. Shipping the
   old data would tie you to old labels and old instruments.

If you have MS/MS and SMILES, `flavfinder label` can build labels for you. The
rules match common flavonoid scaffolds and also record which one matched.

### Build labels from MS/MS + SMILES

```bash
flavfinder label \
  --input raw_with_smiles.csv \
  --output labeled.csv \
  --report label_report.json
```

The output adds `label`, `flavonoid_subclass`, `matched_patterns`,
`smiles_canonical`, `inchikey`, and `smiles_error`. Drop invalid SMILES, remove
duplicates, split by compound/InChIKey or near-duplicate groups, then train P/N
models separately.

RDKit is optional:

```bash
python -m pip install -e ".[chem]"
```

### Install

```bash
python -m pip install -e ".[dev]"
```

Extras:

```bash
python -m pip install -e ".[autogluon]"   # reference backend
python -m pip install -e ".[lightgbm]"    # lighter backend
python -m pip install -e ".[chem]"        # RDKit labeling
```

The build backend is **hatchling**. To build a wheel:

```bash
python -m build
python -m pip install dist/flavfinder_core-*.whl
```

### Commands

```bash
# Audit a table
flavfinder audit --input examples/input_format.json --output audit.json

# Label MS/MS + SMILES
flavfinder label --input raw_with_smiles.csv --output labeled.csv

# Train on your own data
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

A runnable synthetic example is in the [Quickstart](docs/en/02-quickstart.md).

### Status

The pipeline works and is covered by synthetic-data tests. AutoGluon is optional
and needs the `autogluon` extra; LightGBM is fine for local experiments. No data
or model files are shipped.

### Authors

- Lvjun Guo (Ficere) `<gljx898989@163.com>`
- David Niteas `<david.ql.d@foxmail.com>`

See [`AUTHORS`](./AUTHORS). What's shipped is described in [`NOTICE`](./NOTICE).

### License

MIT. See [`LICENSE`](./LICENSE).

---

<a id="zh-cn"></a>

## 简体中文

[English](#english) · **简体中文**

`flavfinder-core` 是 flavfinder MS/MS 黄酮分类器的纯代码实现。它覆盖完整流程：
读取谱图、预处理、训练、预测、评估，以及数据泄漏检查。

### 文档

- **English:** [Documentation index](docs/en/index.md)
- **简体中文：** [文档索引](docs/zh-CN/index.md)

文档按使用深度排列：

| 你要做什么 | 看哪里 |
|---|---|
| 先跑通一次 | [安装](docs/zh-CN/01-installation.md) → [快速开始](docs/zh-CN/02-quickstart.md) |
| 用自己的谱图 | [数据格式](docs/zh-CN/03-data-format.md) → [自建数据集](docs/zh-CN/15-build-your-own-dataset.md) → [训练](docs/zh-CN/05-training.md) |
| 判断结果能不能信 | [评估](docs/zh-CN/07-evaluation.md) → [数据审计](docs/zh-CN/08-data-audit.md) → [方法](docs/zh-CN/09-method.md) |
| 查命令或函数签名 | [CLI](docs/zh-CN/10-cli-reference.md) · [API](docs/zh-CN/11-python-api.md) · [配置](docs/zh-CN/12-configuration.md) |

### 仓库里有什么

- MS/MS 谱图读取与校验
- Binning 与 Tokenization
- AutoGluon、LightGBM、scikit-learn 后端
- 训练、预测、评估与阈值选择
- 数据审计：精确/近重复、泄漏报告、分组切分
- 基于 RDKit 的 SMILES 标注（`flavfinder label`）
- 一个小型 CLI 和 Python API

测试用的是合成谱图，仓库里没有真实谱图。

### 没有数据和模型文件

仓库里没有训练数据，也没有训练好的权重。原因有两个：

1. **模型 bundle 很大。** 训练可复现，工作站上跑一遍不算久；具体时间看数据量、
   特征维度和后端。相比之下，在自己的谱图上重训更省事。
2. **打包数据会过时。** GNPS、MassBank、MoNA 的谱图更多、更新、元数据更全，
   比我们提交的任何快照都好。把旧数据打包进来，只会把用户绑在旧标签和旧仪器上。

如果你有 MS/MS 和 SMILES，可以用 `flavfinder label` 生成标签。规则覆盖常见黄酮
骨架，同时记录命中的具体类型。

### 从 MS/MS + SMILES 生成标签

```bash
flavfinder label \
  --input raw_with_smiles.csv \
  --output labeled.csv \
  --report label_report.json
```

输出会增加 `label`、`flavonoid_subclass`、`matched_patterns`、
`smiles_canonical`、`inchikey` 和 `smiles_error`。过滤非法 SMILES、去重、
按化合物/InChIKey 或近重复组切分，然后分别训练 P/N 模型。

RDKit 是可选依赖：

```bash
python -m pip install -e ".[chem]"
```

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

构建后端是 **hatchling**。构建 wheel：

```bash
python -m build
python -m pip install dist/flavfinder_core-*.whl
```

### 常用命令

```bash
# 审计
flavfinder audit --input examples/input_format.json --output audit.json

# 标注 MS/MS + SMILES
flavfinder label --input raw_with_smiles.csv --output labeled.csv

# 用自己的数据训练
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

流程可用，并有合成数据测试覆盖。AutoGluon 是可选后端，需要 `autogluon` extra；
本地实验用 LightGBM 就够了。仓库不包含数据或模型文件。

### 作者

- Lvjun Guo (Ficere) `<gljx898989@163.com>`
- David Niteas `<david.ql.d@foxmail.com>`

见 [`AUTHORS`](./AUTHORS)。仓库包含什么见 [`NOTICE`](./NOTICE)。

### 许可证

MIT，见 [`LICENSE`](./LICENSE)。
