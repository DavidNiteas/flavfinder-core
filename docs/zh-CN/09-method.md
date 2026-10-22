# 方法与设计说明

**层级：** 3 — 理解  
**前置条件：** [数据审计](./08-data-audit.md)。

## 任务

给定二级质谱（MS/MS），预测对应化合物是否属于黄酮类。正离子与负离子模式分别建模。

## 流程

1. 解析逗号分隔的 m/z 与强度数组。
2. 预处理：
   - **Binning**：固定 m/z 网格，默认 10–500、步长 0.1（4900 维），按谱图最大强度归一化。
   - **Tokenization**：按 5 ppm 容差学习 m/z 词表，token 权重向量，按谱图归一化。
3. 拟合表格二分类模型。
4. 选择 `mid` 与 `high` 决策阈值。
5. 报告 AUROC/AUPRC 与阈值指标。

参考后端是 AutoGluon `TabularPredictor`，`eval_metric=roc_auc`，`presets=optimize_for_deployment`。另提供 LightGBM 与 scikit-learn 后端用于轻量本地运行与测试。

## 阈值

- `mid`：验证集 ROC 上的 Youden 点。
- `high`：最接近目标假阳性率（默认 1%）的阈值。
- `high` 强制不小于 `mid`。
- 概率档位：`score > high` → high；`score > mid` → mid；否则 low。

## 实现说明

有几处很容易写错，这里说明代码实际怎么处理：

| 方面 | 常见坑 | 本实现 |
|---|---|---|
| Tokenizer JSON | 把 `from_json(path)` 当类方法调用 | `from_json` 是真正的类方法；主 API 为 `load` |
| 峰解析 | list 输入可能运行时失败 | 支持并校验字符串、list、tuple、数组 |
| Binning | 逐峰 `argmin` 循环 | 向量化最近 bin + `bincount` |
| 归一化 | 两种方法默认不一致 | 两者默认归一化，可配置 |
| 超范围峰 | 静默钳制/丢弃 | 显式 `drop` / `error` / `clip` |
| 阈值 | 在测试集上选择并报告 | 在验证集选择；测试集只评估 |
| 数据审计 | 没有泄漏工具 | 精确/近重复与泄漏工具 |
| 并行 | 全局并行副作用 | 默认可复现的单进程 |

## 范围

- 不发布数据或模型文件。
- 代码要能用于你带来的数据，而不是只适配开发数据集。

## 局限

- 如果数据没有化合物标识，分组切分只是近似。
- Binning 会丢弃配置范围外的峰。
- 模型是表格分类器，不是结构解析方法。
- 会报告校准，但别默认它一定好。
- 仪器、离子模式、样品制备造成的域偏移，本仓库不解决。

## 作者

- Lvjun Guo (Ficere) `<gljx898989@163.com>`
- David Niteas `<david.ql.d@foxmail.com>`

**下一页：** [CLI 参考](./10-cli-reference.md)
