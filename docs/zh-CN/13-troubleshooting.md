# 故障排查

**层级：** 4 — 参考  
**前置条件：** 任一指南。

## 数据错误

### `missing required column(s): mz, intensity`

表没有使用默认列名。传 `--mz-col` / `--intensity-col`，或在 YAML 中配置。

### `mz and intensity lengths differ`

每行必须 m/z 与强度一一对应。检查尾随逗号和截断字段。

### `contains an empty value`

逗号分隔字段中有空元素，例如 `"100,200,"`。去掉尾随逗号。

### `contains non-finite values`

存在 `NaN`、`inf` 或非数字文本。不支持空单元格。

### `label must contain only 0 and 1`

训练/评估标签必须是二分类。请显式编码类别。

### `training data must contain both classes`

训练切分只有一类。请提供两类数据，或检查标签列是否常量。

## 预处理错误

### `peak(s) outside [mz_min, mz_max]`

预处理为 `out_of_range: error` 且有峰超出网格。改用 `drop`/`clip`，或扩大网格。

### `tokenizer is not fitted`

先 `fit` 再 `transform`，或加载已保存的预处理器。

### `cannot fit tokenizer on empty m/z values`

所有训练谱图都为空，或选错了列。

## 模型错误

### `AutoGluon is optional; install with ...`

```bash
python -m pip install -e ".[autogluon]"
```

### `LightGBM is optional; install with ...`

```bash
python -m pip install -e ".[lightgbm]"
```

### `RDKit is optional; install with ...`

```bash
python -m pip install -e ".[chem]"
```

### `flavfinder label` 报非法 SMILES

该行会保留，`smiles_error` 有值，`label` 为空。训练前把这些行删掉，别当负样本。

### `output directory is not empty`

设置 `overwrite: true` 或传 `--overwrite`。这是为了防止误覆盖旧模型。

### `threshold selection requires both classes`

验证切分只有一类。增大验证集、提供显式验证表，或检查切分。

### AutoGluon 很慢或内存不足

- 降低 `time_limit` 或使用 `presets: medium_quality`。
- 用 `--backend lightgbm` 快速跑基线。
- 减小 `mz_max` / 增大 `bin_width` 以缩小特征矩阵。
- 关闭其他进程；4900 维 × 数万行是很大的矩阵。

## 预测错误

### `No such file or directory: .../metadata.json`

`--model` 必须指向模型**目录**，不是目录内文件。

### 分数分布与训练时不同

检查预处理方法与参数是否一致。bundle 保存了已拟合预处理器；不要在新数据上重新 fit。

### 所有概率都是 `low`

`high`/`mid` 阈值是在验证集上选的，可能不匹配新数据分布。查看 `thresholds.json`，考虑在有代表性的验证集上重新校准。

## 可复现性

- 固定 `seed` 与 `model.random_state`。
- 保存 `metadata.json`（版本、配置、特征名）。
- 保留输入文件；两次运行之间不要编辑。
- 比较指标时使用相同后端与参数。

## 构建问题

### `python -m build` 报 `ensurepip is not available`

隔离构建环境无法创建虚拟环境。请使用正常的 Python/venv，或安装 hatchling 后关闭隔离构建：

```bash
python -m pip install hatchling build
python -m build --no-isolation
```

## 仍然无法解决？

开 issue 时附上：

1. 执行的命令；
2. 完整报错；
3. 输入的形状/列名（敏感数据不要贴真实谱图）；
4. `flavfinder --version` 与 `python --version`。

**下一页：** [文档索引](./index.md)
