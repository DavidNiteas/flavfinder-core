# 为什么只发代码

**层级：** 0 — 范围  
**前置条件：** 无。

`flavfinder-core` 刻意只发布**代码**。本页解释两个决定：不发布预训练权重，不打包训练数据。

## 1. 不发布模型权重

训练好的模型 bundle 可能很大，尤其是包含多个模型族的 AutoGluon predictor。直接发布权重会：

- 让仓库变得笨重、难以克隆；
- 冻结一个在旧仪器、旧数据快照上训练的模型；
- 诱导用户在验证域之外使用模型。

本流水线的训练是可复现的，单台工作站即可完成；具体成本取决于数据量、特征宽度、后端与 CPU。我们发布配置、训练代码、评估代码与模型元数据，用户可以在自己的谱图上训练，并把模型保存在本地或自己的存储中。

如果生产或合规场景需要预训练模型，请在你自己的代表性数据上训练、验证，并单独做版本管理。

## 2. 不发布训练数据

开发时使用的数据是一个较旧的参考快照。公开 MS/MS 数据库更大、更新：

- **GNPS** — 社区谱库与分子网络
- **MassBank** — 公开 MS/MS 参考谱
- **MoNA** — MassBank of North America
- **NIST / METLIN** — 商业授权库（如适用）

发布冻结快照会把用户锚定到旧标签、旧仪器和旧类别比例。更好的做法是从当前公开记录构建数据集。

但公开数据不是即插即用的。你仍然需要：

- 把每条谱图与结构（SMILES/InChIKey）关联；
- 按离子模式、仪器、碰撞能和质量过滤；
- 去重并处理标签冲突；
- 验证黄酮/非黄酮标签；
- 按化合物或近重复组切分，而不是随机切分。

## 3. 我们提供什么

我们提供**标注与训练工具链**：

```bash
flavfinder label --input raw_with_smiles.csv --output labeled.csv --report label_report.json
flavfinder train --train labeled.csv --test heldout.csv --output-dir artifacts/model
```

`label` 命令使用 RDKit 与亚类感知的 SMARTS 规则集，输出二分类标签、命中的亚类、canonical SMILES、InChIKey，以及非法结构的错误字段。

## 4. 标签的含义

RDKit 规则是**骨架级启发式**，不是正式分类学。覆盖的常见黄酮家族包括：

- 黄酮醇、黄酮、黄烷酮、二氢黄酮醇
- 黄烷-3-醇（儿茶素）
- 异黄酮
- 查尔酮与二氢查尔酮
- 橙酮
- 花青素

只要命中至少一条规则就标为正类。规则顺序中的第一个命中作为 `flavonoid_subclass`，所有命中记录在 `matched_patterns`。

这适合快速构建训练集，但不能替代专家分类。作为真实标签使用前，请用 NPClassifier、ClassyFire 或人工复核抽样验证。

## 5. 推荐流程

1. 从你有权使用的公开库收集 MS/MS + SMILES。
2. 用 `flavfinder label` 标注。
3. 删除非法 SMILES，检查标注报告。
4. 按 InChIKey 与谱图内容去重。
5. 按化合物/InChIKey 或近重复组切分。
6. 正离子与负离子模式分别训练。
7. 用 AUPRC、校准和外部测试集评估。

继续阅读 [自建数据集](./15-build-your-own-dataset.md)。

**下一页：** [自建数据集](./15-build-your-own-dataset.md)
