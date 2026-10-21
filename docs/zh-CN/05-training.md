# 训练

**层级：** 2 — 使用  
**前置条件：** [预处理](./04-preprocessing.md)。

## 配置驱动

以 `configs/P.yaml` / `configs/N.yaml` 为模板：

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
  normalization: max
  out_of_range: drop

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

运行：

```bash
flavfinder train --config configs/P.yaml
```

## 训练器做了什么

1. 读取并校验训练表。
2. 有 `validation` 就用；否则按 `validation_size` 分层切分 `train`。
3. **只在训练集上**拟合预处理器。
4. 拟合所选后端。
5. 在验证集上选择 `mid` / `high` 阈值。
6. 评估 train/validation/test 并写出模型 bundle。

## 后端

| 后端 | 额外安装 | 用途 |
|---|---|---|
| `autogluon` | `.[autogluon]` | 参考流程；依赖较大 |
| `lightgbm` | `.[lightgbm]` | 快速本地实验 |
| `sklearn` | 基础安装 | 测试与极小数据 |

```bash
flavfinder train --config configs/P.yaml --backend lightgbm
```

## 输出

```text
artifacts/P/
├── preprocessing.json   # 已拟合的预处理状态
├── backend/             # 模型文件或 AutoGluon predictor
├── thresholds.json      # mid/high 阈值及其指标
├── metrics.json         # train/validation/test 指标
└── metadata.json        # 配置、特征名、来源、版本
```

`metadata.json` 记录输入路径、特征名、包版本、Python 版本与指标摘要，不复制训练数据。

## 阈值选择

- `mid`：Youden 最优点（`argmax(TPR - FPR)`）。
- `high`：最接近目标假阳性率（`threshold_high_fpr`，默认 1%）的点。
- 阈值只在验证集上选，不用测试集。
- `high` 强制不小于 `mid`。

## 可复现性

- `seed` 控制切分与 bootstrap。
- `model.random_state` 控制后端。
- `metadata.json` 记录精确版本。
- 用 `overwrite: true` 或 `--overwrite` 替换已有输出目录。

## 类别不平衡

原始数据不平衡，不要只看 accuracy：

- 同时报告 **AUPRC** 与 AUROC；
- 查看所选阈值下的混淆矩阵；
- 解释概率前检查校准。

见 [评估](./07-evaluation.md)。

**下一页：** [预测](./06-prediction.md)
