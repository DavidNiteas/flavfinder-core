# 为什么仓库里没有数据和模型

**层级：** 0 — 范围  
**前置条件：** 无。

仓库只发代码，不带训练好的权重，也不带训练数据。原因有两个。

## 模型 bundle 很大

一个包含多个模型族的 AutoGluon predictor 可能到几百 MB。提交进仓库会让克隆变重，
也会把一个在旧快照上训练的模型固定下来，还容易让人在验证域之外使用它。

训练本身可复现。工作站上跑一遍通常几分钟到几十分钟，具体看数据量、特征维度和后端。
多数情况下，在自己的谱图上重训比传一个 bundle 更省事。生产环境请用自己的数据训练、
验证，再单独给模型产物做版本管理。

## 打包数据会过时

开发时用的数据是旧快照，公开 MS/MS 库更大、更新：

- **GNPS** — 社区谱库与分子网络
- **MassBank** — 公开参考谱
- **MoNA** — MassBank of North America
- **NIST / METLIN** — 商业授权库（如适用）

把旧数据打包进来，只会把用户绑在旧标签、旧仪器和旧类别比例上。从当前公开记录
重新做数据集更合适。

公开数据也要处理：

- 把每条谱图和结构（SMILES/InChIKey）对上；
- 按离子模式、仪器、碰撞能和质量过滤；
- 去重，处理标签冲突；
- 检查黄酮/非黄酮标签；
- 按化合物或近重复组切分，不要随机切。

## 仓库里有什么

标注和训练代码：

```bash
flavfinder label --input raw_with_smiles.csv --output labeled.csv --report label_report.json
flavfinder train --train labeled.csv --test heldout.csv --output-dir artifacts/model
```

`flavfinder label` 用 RDKit 和一组 SMARTS 规则，输出二分类标签、命中的骨架类型、
canonical SMILES、InChIKey，以及非法结构的错误。

## 标签是什么意思

规则匹配的是骨架，不是正式分类学。覆盖：

- 黄酮醇、黄酮、黄烷酮、二氢黄酮醇
- 黄烷-3-醇（儿茶素）
- 异黄酮
- 查尔酮与二氢查尔酮
- 橙酮
- 花青素

命中任意一条规则就算正类。规则顺序里的第一个命中作为 `flavonoid_subclass`，
所有命中写进 `matched_patterns`。

这只能当第一遍粗筛。把它当真实标签之前，抽一批用 NPClassifier、ClassyFire 或人工
对一下。

## 流程

1. 从你有权使用的库收集 MS/MS + SMILES。
2. 跑 `flavfinder label`。
3. 删掉非法 SMILES，看标注报告。
4. 按 InChIKey 和谱图内容去重。
5. 按化合物/InChIKey 或近重复组切分。
6. 正、负离子模式分别训练。
7. 用 AUPRC、校准和外部测试集评估。

**下一页：** [自建数据集](./15-build-your-own-dataset.md)
