# 预测

**层级：** 2 — 使用  
**前置条件：** [训练](./05-training.md)。

`flavfinder-core` 不附带预训练模型。请先训练或取得模型 bundle。

## CLI

```bash
flavfinder predict \
  --model artifacts/P \
  --input examples/input_format.json \
  --output predictions.json
```

输入可以是 CSV 或 JSON。默认列名为 `mz`、`intensity`、`id`；可用 `--mz-col`、`--intensity-col`、`--id-col` 覆盖。

## 输出

保留输入列，并增加：

| 列 | 含义 |
|---|---|
| `score` | 正类概率，范围 `[0, 1]` |
| `probability` | `score > high` 为 `high`；`score > mid` 为 `mid`；否则 `low` |

示例：

```json
[
  {
    "id": "compound-1",
    "mz": "100.0,150.0,200.0",
    "intensity": "10,50,100",
    "score": 0.82,
    "probability": "high"
  }
]
```

## Python API

```python
from flavfinder import predict

predictions = predict(
    model_dir="artifacts/P",
    input_path="examples/input_format.json",
    output_path="predictions.json",
)
print(predictions[["id", "score", "probability"]])
```

## 直接加载 bundle

```python
from flavfinder import ModelBundle

bundle = ModelBundle.load("artifacts/P")
print(bundle.metadata["backend"])
print(bundle.metadata["feature_names"][:3])
```

## 批处理行为

- 每行独立打分；
- 非法行报错，不静默跳过；
- 超出分箱网格的峰遵循训练时的 `out_of_range` 策略；
- 未知 token 峰在 `accumulate_unknown` 开启时累加到 `UNK`。

## 没有模型怎么办

先训练：

```bash
flavfinder train --config configs/P.yaml --train data/P/train.csv --output-dir artifacts/P
```

**下一页：** [评估](./07-evaluation.md)
