# flavfinder-core 文档（简体中文）

**语言：** [English](../en/index.md) · 简体中文

`flavfinder-core` 是 flavfinder MS/MS 黄酮分类器的独立、纯代码实现。它提供配置驱动的训练与评估流程，不附带训练数据或预训练模型。

## 从哪开始

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

## 怎么读这些文档

- **第一次用：** [安装](./01-installation.md)，然后跑 [快速开始](./02-quickstart.md)。
- **有自己的谱图：** [数据格式](./03-data-format.md) → [自建数据集](./15-build-your-own-dataset.md) → [训练](./05-training.md)。
- **要判断指标可不可信：** [评估](./07-evaluation.md) → [数据审计](./08-data-audit.md) → [方法](./09-method.md)。
- **查参数或函数签名：** [CLI](./10-cli-reference.md)、[Python API](./11-python-api.md)、[配置](./12-configuration.md)。

## 仓库里没有

- `train_datasets/` 或任何真实 MS/MS 谱图
- 预训练模型权重或 AutoGluon predictor
- 内部工单或开发笔记

作者见 [`AUTHORS`](../../AUTHORS)，包含内容见 [`NOTICE`](../../NOTICE)。

## 作者与许可

- Lvjun Guo (Ficere) `<gljx898989@163.com>`
- David Niteas `<david.ql.d@foxmail.com>`
- 许可证：MIT（仅代码）

**下一页：** [安装](./01-installation.md)
