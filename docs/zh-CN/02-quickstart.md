# 快速开始

**层级：** 1 — 开始  
**前置条件：** [安装](./01-installation.md)。

下面用一份很小的**合成数据**跑一遍完整流程，不需要真实训练数据。

## 1. 生成合成数据

保存为 `make_demo.py` 并运行，生成 `synthetic.csv`：两个类别，正类在 m/z 300 有一个判别峰。

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(0)
rows = []
for i in range(80):
    label = int(i % 2 == 0)
    mz = rng.uniform(50, 450, size=8)
    intensity = rng.uniform(1, 100, size=8)
    mz = np.append(mz, 300.0 if label else 150.0)
    intensity = np.append(intensity, 100.0)
    order = np.argsort(mz)
    rows.append({
        "id": f"synthetic-{i}",
        "mz": ",".join(f"{v:.4f}" for v in mz[order]),
        "intensity": ",".join(f"{v:.4f}" for v in intensity[order]),
        "label": label,
    })
pd.DataFrame(rows).to_csv("synthetic.csv", index=False)
```

```bash
python make_demo.py
```

## 2. 审计数据

```bash
flavfinder audit --input synthetic.csv --output audit.json
```

`audit.json` 包含峰数统计、m/z 范围、类别比例、重复信息。

## 3. 训练一个小模型

scikit-learn 后端在基础安装中，适合本示例：

```bash
flavfinder train \
  --train synthetic.csv \
  --test synthetic.csv \
  --output-dir artifacts/demo \
  --backend sklearn \
  --no-bootstrap \
  --overwrite
```

输出目录：

| 文件 | 含义 |
|---|---|
| `preprocessing.json` | 已拟合的分箱/分词状态 |
| `backend/` | 已拟合模型 |
| `thresholds.json` | mid/high 决策阈值 |
| `metrics.json` | train/validation/test 指标 |
| `metadata.json` | 配置、特征名、来源信息 |

## 4. 预测

```bash
flavfinder predict \
  --model artifacts/demo \
  --input examples/input_format.json \
  --output predictions.json
```

每条输出保留输入列，并增加 `score` 与 `probability`（`high` / `mid` / `low`）。

## 5. 评估

```bash
flavfinder evaluate \
  --model artifacts/demo \
  --input synthetic.csv \
  --output evaluation.json \
  --no-bootstrap
```

## 刚才发生了什么？

1. 峰被分到固定 m/z 网格（默认 10–500，步长 0.1）。
2. 每个谱图按最大强度归一化。
3. 在分箱特征上训练分类器。
4. 在验证集上选择 `mid` / `high` 阈值。
5. 模型 bundle 保存为目录，可重新加载。

## 下一步

- 使用自己的数据：[数据格式](./03-data-format.md)
- 换用 AutoGluon：[训练](./05-training.md)
- 报告指标前检查泄漏：[数据审计](./08-data-audit.md)

**下一页：** [数据格式](./03-data-format.md)
