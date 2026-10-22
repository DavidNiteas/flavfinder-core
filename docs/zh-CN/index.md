# flavfinder-core 文档（简体中文）

**语言：** [English](../en/index.md) · 简体中文

`flavfinder-core` 是 flavfinder MS/MS 黄酮分类器的独立、纯代码移植版本。它提供配置驱动的训练与评估流程，不附带训练数据或预训练模型。

## 选择你的阅读路径

| 你想做什么 | 阅读顺序 |
|---|---|
| 理解为什么不发布数据/模型 | [为什么只发代码](./14-why-code-only.md) |
| 安装并跑通一个小例子 | [安装](./01-installation.md) → [快速开始](./02-quickstart.md) |
| 使用自己的谱图 | [数据格式](./03-data-format.md) → [预处理](./04-preprocessing.md) → [训练](./05-training.md) |
| 从公开数据 + SMILES 构建新数据集 | [自建数据集](./15-build-your-own-dataset.md) |
| 对新谱图打分 | [预测](./06-prediction.md) |
| 评估模型质量 | [评估](./07-evaluation.md) → [数据审计](./08-data-audit.md) |
| 理解方法与局限 | [方法](./09-method.md) |
| 查命令参数 | [CLI 参考](./10-cli-reference.md) |
| 使用 Python API | [Python API](./11-python-api.md) |
| 调整训练配置 | [配置](./12-configuration.md) |
| 排查报错 | [故障排查](./13-troubleshooting.md) |

## 文档层级

- **第 0 层 — 范围**：为什么只发代码，以及如何从公开数据构建自己的数据集。
- **第 1 层 — 开始**：安装与快速开始，不要求了解原实现。
- **第 2 层 — 使用**：数据格式、预处理、训练、预测、评估，覆盖日常工作流。
- **第 3 层 — 理解**：方法、阈值、泄漏、分组切分与局限。报告指标前应先读。
- **第 4 层 — 参考**：CLI、Python API、配置字段、故障排查。

## 本仓库不包含

- `train_datasets/` 或任何真实 MS/MS 谱图
- 预训练模型权重或 AutoGluon predictor
- 内部工单、开发笔记、参考库 checkout

原始项目及其历史提交仍是数据与来源的权威出处。见 [`NOTICE`](../../NOTICE) 与 [`AUTHORS`](../../AUTHORS)。

## 来源与许可

- 原始工作：Lvjun Guo (Ficere) `<gljx898989@163.com>`
- 移植维护者：David Niteas `<david.ql.d@foxmail.com>`
- 许可证：MIT（仅代码）

**下一页：** [安装](./01-installation.md)
