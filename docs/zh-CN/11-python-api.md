# Python API

**层级：** 4 — 参考  
**前置条件：** [CLI 参考](./10-cli-reference.md)。

## Schema 与 I/O

```python
from flavfinder import SpectrumSchema, prepare_frame, read_frame

schema = SpectrumSchema(
    mz_col="mz",
    intensity_col="intensity",
    label_col="label",
    id_col="id",
)
frame = read_frame("data.csv", schema)
prepared = prepare_frame(frame, schema, require_label=True)
```

`prepare_frame` 增加 `_mz_values` 与 `_intensity_values` 对象列，并校验长度、有限性、非负性。

## 预处理

```python
from flavfinder import BinningTransformer, FlavTokenizer

binning = BinningTransformer(
    mz_min=10.0,
    mz_max=500.0,
    bin_width=0.1,
    normalization="max",
    out_of_range="drop",
)
features = binning.transform(prepared, schema)
features = features[binning.feature_names_]

tokenizer = FlavTokenizer(
    mz_tol=5.0,
    mz_tol_unit="ppm",
    normalization="max",
).fit(prepared, mz_col="mz")
token_features = tokenizer.transform(prepared, schema)
```

两者都支持 `save(path)` / `load(path)`。`FlavTokenizer.from_json(path)` 是 `load` 的别名。

`DataTransformer` 是兼容门面：

```python
from flavfinder import DataTransformer

transformer = DataTransformer(binning)
features = transformer.transform_df(frame)
```

## 训练

```python
from flavfinder import (
    DataConfig,
    ModelConfig,
    PreprocessingConfig,
    TrainingConfig,
    train,
)

config = TrainingConfig(
    data=DataConfig(train="data/P/train.csv", test="data/P/test.csv"),
    preprocessing=PreprocessingConfig(method="binning"),
    model=ModelConfig(backend="lightgbm"),
    output_dir="artifacts/P",
    validation_size=0.2,
    seed=42,
)
metrics = train(config)
```

`train` 返回指标字典并写出模型 bundle。后端：`autogluon` / `lightgbm` / `sklearn`。

## 模型 bundle

```python
from flavfinder import ModelBundle

bundle = ModelBundle.load("artifacts/P")
output = bundle.predict_frame(frame, schema)
print(output[["score", "probability"]])
```

常用属性：

- `bundle.preprocessor` — 已拟合变换器
- `bundle.backend` — 已拟合后端
- `bundle.metadata` — 配置、特征名、来源、版本
- `bundle.thresholds` — mid/high 阈值

## 预测与评估

```python
from flavfinder import evaluate, predict

predictions = predict("artifacts/P", "input.json", "predictions.json")
metrics = evaluate("artifacts/P", "data/P/test.csv", "reports/P.json")
```

## 数据审计

```python
from flavfinder import (
    audit_frame,
    groups_from_pairs,
    leakage_report,
    near_duplicate_pairs,
)

print(audit_frame(frame))
print(leakage_report(train_frame, test_frame))
pairs = near_duplicate_pairs(train_frame, binning, threshold=0.95)
groups = groups_from_pairs(len(train_frame), pairs)
```

## 指标

```python
from flavfinder import (
    binary_metrics,
    bootstrap_ci,
    calibration_points,
    select_thresholds,
)

metrics = binary_metrics(y_true, y_score, threshold=0.5)
ci = bootstrap_ci(y_true, y_score, n_boot=1000, seed=42)
thresholds = select_thresholds(y_true, y_score, high_fpr=0.01)
points = calibration_points(y_true, y_score, n_bins=10)
```

## 错误行为

- 输入缺失：`FileNotFoundError`
- 数据/配置/参数非法：`ValueError`
- 可选后端未安装：`ImportError`
- 输出目录非空且未覆盖：`FileExistsError`

CLI 会捕获这些错误并返回退出码 `2`。

**下一页：** [配置](./12-configuration.md)
