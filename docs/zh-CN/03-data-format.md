# 数据格式

**层级：** 2 — 使用  
**前置条件：** [快速开始](./02-quickstart.md)。

## 支持的容器

`flavfinder` 读取 `.csv` 与 `.json` 表格。每行是一条 MS/MS 谱图。

### CSV

```csv
id,mz,intensity,label
compound-1,"100.0,150.0,200.0","10,50,100",1
compound-2,"120.0,180.0,240.0","5,25,100",0
```

### JSON

```json
[
  {
    "id": "compound-1",
    "mz": "100.0,150.0,200.0",
    "intensity": "10,50,100",
    "label": 1
  }
]
```

## 列定义

| 列 | 是否必需 | 类型 | 说明 |
|---|---|---|---|
| `mz` | 是 | 逗号分隔数字或数字列表 | m/z 值 |
| `intensity` | 是 | 逗号分隔数字或数字列表 | 长度必须与 `mz` 一致 |
| `label` | 训练/评估必需 | 0 或 1 | 预测时可省略 |
| `id` / `name` | 否 | 字符串或数字 | 原样复制到预测输出 |

默认列名可在 YAML 或 CLI 中修改：

```bash
flavfinder train --train data.csv \
  --mz-col "precursor_mz" \
  --intensity-col "peaks_intensity" \
  --label-col "is_flavonoid"
```

## 校验规则

`prepare_frame` 会强制检查：

- `mz` 与 `intensity` 非空；
- 两者长度完全一致；
- 所有数值有限；
- m/z 与强度非负；
- 变换前按 m/z 排序；
- 标签为整数 `0` 或 `1`。

不会静默丢弃行。非法输入会带行号报错。

## 常见错误

| 错误 | 报错 |
|---|---|
| `mz` 10 个值、`intensity` 9 个 | `mz and intensity lengths differ` |
| 尾随逗号 `"100,200,"` | `contains an empty value` |
| `NaN` / `inf` | `contains non-finite values` |
| 负强度 | `intensities must be non-negative` |
| 标签为 2 | `label must contain only 0 and 1` |

## 预测输出

预测会保留原列，并增加：

| 列 | 含义 |
|---|---|
| `score` | 正类概率 |
| `probability` | `high` / `mid` / `low` 档位 |

若模型没有阈值，则只增加 `score`。

**下一页：** [预处理](./04-preprocessing.md)
