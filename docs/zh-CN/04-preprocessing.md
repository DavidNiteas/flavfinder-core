# 预处理

**层级：** 2 — 使用  
**前置条件：** [数据格式](./03-data-format.md)。

实现了两种预处理：

- **Binning（默认）**：固定宽度 m/z 网格。
- **Tokenization**：带容差合并的 m/z 词表。

两者默认都对每个谱图做强度归一化。

## Binning

```python
from flavfinder import BinningTransformer

transformer = BinningTransformer(
    mz_min=10.0,
    mz_max=500.0,
    bin_width=0.1,
    normalization="max",
    out_of_range="drop",
)
vector = transformer.transform_peaks("100.0,300.0", "10,100")
```

### 默认值与维度

| 参数 | 默认 | 含义 |
|---|---|---|
| `mz_min` | `10.0` | 首个 bin 中心 |
| `mz_max` | `500.0` | 网格上界 |
| `bin_width` | `0.1` | bin 间距 |
| `normalization` | `max` | `none` / `max` / `l2` |
| `out_of_range` | `drop` | `drop` / `error` / `clip` |

默认 `n_bins = 4900`，特征名为 `bin_0000` … `bin_4899`。

峰被分配到最近的 bin 中心。超出网格的峰：

- `drop`：忽略（默认）；
- `error`：报错；
- `clip`：钳到首/末 bin。

原始数据约 10% 的峰超过 m/z 500。如果这些峰重要，请增大 `mz_max` 或使用 `error` 让损失可见。

### 归一化

- `max`：除以最大强度；全零谱图保持全零。
- `l2`：除以 L2 范数。
- `none`：保留原始累加强度。

## Tokenization

```python
from flavfinder import FlavTokenizer

tokenizer = FlavTokenizer(
    mz_tol=5.0,
    mz_tol_unit="ppm",
    normalization="max",
    accumulate_unknown=True,
).fit(["100.0,200.0", "100.0002,200.0"])

vector = tokenizer.transform_peaks("100.0,300.0", "10,100")
```

- token `0` 是 `UNK`；
- 学到的 m/z 从 token `1` 开始；
- 容差内的 m/z 合并为一个词表项；
- `accumulate_unknown=True` 把未知峰强度累加到 token `0`；设为 `False` 则丢弃；
- 向量长度为 `1 + 词表大小`。

## 在 YAML 中选择方法

```yaml
preprocessing:
  method: tokenization
  mz_tol: 5.0
  mz_tol_unit: ppm
  normalization: max
  accumulate_unknown: true
```

CLI 覆盖：

```bash
flavfinder train --config configs/P.yaml --method tokenization
```

## 持久化

两种变换器都可序列化为 JSON，并保存在模型 bundle 中：

```text
artifacts/P/preprocessing.json
```

直接加载：

```python
from flavfinder.preprocessing import load_preprocessor

preprocessor = load_preprocessor("artifacts/P/preprocessing.json")
```

## 性能说明

- Binning 使用向量化最近 bin 分配与 `bincount`，避免原实现逐峰 `argmin`。
- 默认单进程以保证可复现；需要吞吐时在外部批处理。
- 25k × 4900 的 float64 矩阵约 1 GB；`float32` 可减半。

**下一页：** [训练](./05-training.md)
