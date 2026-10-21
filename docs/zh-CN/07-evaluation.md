# 评估

**层级：** 2 — 使用  
**前置条件：** [预测](./06-prediction.md)。

## CLI

```bash
flavfinder evaluate \
  --model artifacts/P \
  --input data/P/test.csv \
  --output reports/P_metrics.json
```

`--no-bootstrap` 跳过重采样以加快速度；`--n-boot` 与 `--seed` 控制 bootstrap。

## 指标

| 指标 | 作用 |
|---|---|
| AUROC | 全阈值排序质量 |
| AUPRC | 类别不平衡下的排序质量 |
| Brier | 概率校准（越低越好） |
| Accuracy / precision / recall / F1 | 所选阈值下的表现 |
| 混淆矩阵 | 具体假阳性/假阴性数量 |
| Bootstrap CI | 有限测试集带来的不确定性 |
| 校准点 | 可靠性曲线（预测均值 vs 实际比例） |

原始数据不平衡，**AUPRC 通常比 accuracy 更有信息量**。AUROC 高但 AUPRC 差，仍可能不是好的筛选模型。

## 阈值

评估默认使用 bundle 的 `mid` 阈值。bundle 同时保存 `high` 阈值及两者指标：

```json
{
  "mid": {"value": 0.37, "fpr": 0.12, "tpr": 0.78, "accuracy": 0.81},
  "high": {"value": 0.82, "fpr": 0.01, "tpr": 0.42, "precision": 0.91}
}
```

阈值在训练时由验证集选出，绝不在测试集上调参。用测试集选阈值会高估结果。

## Python API

```python
from flavfinder import evaluate

metrics = evaluate(
    model_dir="artifacts/P",
    input_path="data/P/test.csv",
    output_path="reports/P_metrics.json",
    with_bootstrap=True,
    n_boot=1000,
    seed=42,
)
print(metrics["auroc"], metrics["auprc"])
```

## 如何读报告

1. 看 `n` 与 `positive_rate`：正类太少会让 AUPRC 很噪。
2. 看 bootstrap 区间，不只看点估计。
3. 看准备使用的阈值下的混淆矩阵。
4. 若把 `score` 当概率解释，先看校准。
5. 信任指标前先看 [数据审计](./08-data-audit.md) 的泄漏结论。
6. 分别报告 **random split** 与 **group split** 指标。以 group split 为主结果，random split 只作为乐观参考。

## 评估不能证明什么

好的测试分数不能证明：

- 换仪器、碰撞能、样品制备后仍有效；
- 对其他化学类别仍有效；
- 具备临床或监管效力。

应记录域偏移，并尽可能在外部数据集上验证。

**下一页：** [数据审计](./08-data-audit.md)
