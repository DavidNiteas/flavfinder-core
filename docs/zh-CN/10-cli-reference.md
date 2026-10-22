# CLI 参考

**层级：** 4 — 参考  
**前置条件：** [训练](./05-training.md)。

## 全局

```bash
flavfinder --version
flavfinder --describe
flavfinder --help
```

## Schema 参数

`audit`、`train`、`predict`、`evaluate` 均支持：

| 参数 | 默认 |
|---|---|
| `--mz-col` | `mz` |
| `--intensity-col` | `intensity` |
| `--label-col` | `label` |
| `--id-col` | 无 |

`train` 中只有显式传入时才覆盖 YAML 值。

## `flavfinder audit`

```bash
flavfinder audit --input data.csv --output audit.json
flavfinder audit --train train.csv --test test.csv --output audit.json
```

| 参数 | 含义 |
|---|---|
| `--input` | 审计单表 |
| `--train` / `--test` | 审计两表并报告精确重叠 |
| `--output` | 写 JSON 报告 |

## `flavfinder label`

```bash
flavfinder label --input raw_with_smiles.csv --output labeled.csv \
  --report label_report.json
```

| 参数 | 含义 |
|---|---|
| `--input` | 含 SMILES 与 MS/MS 的 CSV/JSON |
| `--output` | 标注后的 CSV/JSON |
| `--smiles-col` | SMILES 列（默认 `smiles`） |
| `--label-col` | 目标标签列（默认 `label`） |
| `--patterns` | YAML SMARTS 规则覆盖 |
| `--report` | JSON 标注汇总 |

输出增加 `label`、`label_original`、`flavonoid_label`、`flavonoid_subclass`、
`matched_patterns`、`smiles_canonical`、`inchikey`、`smiles_error`。需要 RDKit
（`pip install -e ".[chem]"`）。

## `flavfinder train`

```bash
flavfinder train --config configs/P.yaml
flavfinder train --train data/P/train.csv --test data/P/test.csv \
  --output-dir artifacts/P --backend lightgbm --no-bootstrap --overwrite
```

| 参数 | 含义 |
|---|---|
| `--config` | YAML 训练配置 |
| `--train` | 覆盖训练表 |
| `--validation` | 覆盖验证表 |
| `--test` | 覆盖测试表 |
| `--output-dir` | 模型 bundle 目录 |
| `--backend` | `autogluon` / `lightgbm` / `sklearn` |
| `--method` | `binning` / `tokenization` |
| `--seed` | 覆盖切分/后端种子 |
| `--overwrite` | 替换非空输出目录 |
| `--no-bootstrap` | 跳过 bootstrap 置信区间 |
| `--n-boot` | bootstrap 次数 |

YAML 中的相对路径按**当前工作目录**解析，不按配置文件位置。

## `flavfinder predict`

```bash
flavfinder predict --model artifacts/P --input input.json --output predictions.json
```

| 参数 | 含义 |
|---|---|
| `--model` | 模型 bundle 目录 |
| `--input` | CSV/JSON 谱图表 |
| `--output` | CSV/JSON 输出路径 |

## `flavfinder evaluate`

```bash
flavfinder evaluate --model artifacts/P --input data/P/test.csv \
  --output reports/P_metrics.json --no-bootstrap
```

| 参数 | 含义 |
|---|---|
| `--model` | 模型 bundle 目录 |
| `--input` | 带标签的 CSV/JSON |
| `--output` | JSON 指标输出 |
| `--no-bootstrap` | 跳过重采样 |
| `--n-boot` | bootstrap 次数 |
| `--seed` | bootstrap 种子 |

## 退出码

| 码 | 含义 |
|---|---|
| `0` | 成功 |
| `2` | 已处理的输入/配置/导入错误 |

未处理异常不会被 CLI 吞掉。

## 示例

```bash
# 审计
flavfinder audit --train data/P/train.csv --test data/P/test.csv --output reports/P_audit.json

# 标注 SMILES + MS/MS
flavfinder label --input raw_with_smiles.csv --output labeled.csv --report label_report.json

# AutoGluon 训练
flavfinder train --config configs/P.yaml

# LightGBM 训练
flavfinder train --config configs/P.yaml --backend lightgbm --output-dir artifacts/P-lgbm

# 预测
flavfinder predict --model artifacts/P --input examples/input_format.json --output predictions.json

# 评估
flavfinder evaluate --model artifacts/P --input data/P/test.csv --output reports/P_metrics.json
```

**下一页：** [Python API](./11-python-api.md)
