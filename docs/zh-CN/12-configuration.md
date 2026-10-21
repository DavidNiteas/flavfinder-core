# 配置

**层级：** 4 — 参考  
**前置条件：** [Python API](./11-python-api.md)。

训练使用 YAML 配置。参考 `configs/P.yaml` 与 `configs/N.yaml`。

## 完整示例

```yaml
data:
  train: data/P/train.csv
  validation: null
  test: data/P/test.csv
  mz_col: mz
  intensity_col: intensity
  label_col: label
  id_col: null

preprocessing:
  method: binning
  mz_min: 10.0
  mz_max: 500.0
  bin_width: 0.1
  mz_tol: 5.0
  mz_tol_unit: ppm
  normalization: max
  out_of_range: drop
  accumulate_unknown: true
  dtype: float64

model:
  backend: autogluon
  eval_metric: roc_auc
  presets: optimize_for_deployment
  time_limit: null
  random_state: 42
  params: {}

output_dir: artifacts/P
validation_size: 0.2
threshold_high_fpr: 0.01
seed: 42
overwrite: false
with_bootstrap: true
n_boot: 1000
```

## `data`

| 字段 | 默认 | 含义 |
|---|---|---|
| `train` | 无 | 训练表（除非 CLI `--train`，否则必需） |
| `validation` | 无 | 可选验证表 |
| `test` | 无 | 可选测试表 |
| `mz_col` | `mz` | m/z 列 |
| `intensity_col` | `intensity` | 强度列 |
| `label_col` | `label` | 标签列 |
| `id_col` | 无 | 可选标识列 |

## `preprocessing`

| 字段 | 默认 | 含义 |
|---|---|---|
| `method` | `binning` | `binning` / `tokenization` |
| `mz_min` | `10.0` | 分箱下界 |
| `mz_max` | `500.0` | 分箱上界 |
| `bin_width` | `0.1` | 分箱宽度 |
| `mz_tol` | `5.0` | 分词容差 |
| `mz_tol_unit` | `ppm` | `ppm` / `%` / `abs` / `Da` |
| `normalization` | `max` | `none` / `max` / `l2` |
| `out_of_range` | `drop` | `drop` / `error` / `clip` |
| `accumulate_unknown` | `true` | 保留未知 token 强度 |
| `dtype` | `float64` | 分箱输出类型 |

未使用的字段会被忽略。

## `model`

| 字段 | 默认 | 含义 |
|---|---|---|
| `backend` | `autogluon` | `autogluon` / `lightgbm` / `sklearn` |
| `eval_metric` | `roc_auc` | AutoGluon 指标 |
| `presets` | `optimize_for_deployment` | AutoGluon presets |
| `time_limit` | 无 | AutoGluon 时间上限（秒） |
| `random_state` | `42` | 后端种子 |
| `params` | `{}` | 后端专属参数 |

### 后端参数示例

**LightGBM**

```yaml
model:
  backend: lightgbm
  params:
    n_estimators: 500
    learning_rate: 0.03
    num_leaves: 31
```

**AutoGluon**

```yaml
model:
  backend: autogluon
  presets: best_quality
  time_limit: 600
  params:
    num_bag_folds: 5
```

**scikit-learn**

```yaml
model:
  backend: sklearn
  params:
    max_iter: 2000
    C: 1.0
```

## 顶层

| 字段 | 默认 | 含义 |
|---|---|---|
| `output_dir` | `artifacts/model` | 模型 bundle 目录 |
| `validation_size` | `0.2` | 无 `validation` 时的切分比例 |
| `threshold_high_fpr` | `0.01` | high 阈值的目标 FPR |
| `seed` | `42` | 切分与 bootstrap 种子 |
| `overwrite` | `false` | 替换非空输出目录 |
| `with_bootstrap` | `true` | 是否对验证/测试做 bootstrap |
| `n_boot` | `1000` | bootstrap 次数 |

## 路径解析

路径按**当前工作目录**解析，不按配置文件位置。请在仓库根目录运行，或使用绝对路径。

## CLI 覆盖

```bash
flavfinder train --config configs/P.yaml \
  --train /abs/path/train.csv \
  --test /abs/path/test.csv \
  --output-dir /abs/path/artifacts/P \
  --backend lightgbm \
  --method tokenization \
  --seed 123 \
  --overwrite
```

Schema 参数仅在显式传入时覆盖 YAML。

**下一页：** [故障排查](./13-troubleshooting.md)
