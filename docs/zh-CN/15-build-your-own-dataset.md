# 自建数据集

**层级：** 2 — 使用  
**前置条件：** [数据格式](./03-data-format.md)、[为什么只发代码](./14-why-code-only.md)。

下面是从 MS/MS + SMILES 生成训练表的流程。标注需要 RDKit，它是可选依赖：

```bash
python -m pip install -e ".[chem]"
```

## 输入 schema

表里至少要有：

| 列 | 含义 |
|---|---|
| `smiles` | 化合物结构 |
| `mz` | 逗号分隔的 MS/MS m/z |
| `intensity` | 逗号分隔的强度 |

可选列会原样带出：

| 列 | 用途 |
|---|---|
| `id` / `name` | 标识 |
| `precursor_mz` | 母离子 m/z |
| `adduct` | 加合物 |
| `ion_mode` | `P` 或 `N` |
| `collision_energy` | 碰撞能 |
| `source` | GNPS / MassBank / MoNA / 其他 |
| `label` | 已有标签（如有） |

示例：

```csv
id,smiles,mz,intensity,source
q1,"O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12","151.0,273.0,301.0","12,100,44",GNPS
c1,"Cn1cnc2c1c(=O)n(C)c(=O)n2C","110.0,138.0,195.0","20,100,35",MoNA
```

## 1. 用 RDKit 标注

```bash
flavfinder label \
  --input raw_with_smiles.csv \
  --output labeled.csv \
  --report label_report.json
```

可选参数：

```bash
--smiles-col smiles
--label-col label
--patterns configs/flavonoid_patterns.yaml
```

输出列：

| 列 | 含义 |
|---|---|
| `label` | 1 = 黄酮，0 = 非黄酮，空 = 非法 SMILES |
| `label_original` | 输入中已有的标签 |
| `flavonoid_label` | 同样的 0/1 标签，显式保留 |
| `flavonoid_subclass` | 第一个命中的骨架家族 |
| `matched_patterns` | 所有命中规则，用 `|` 分隔 |
| `smiles_canonical` | RDKit canonical SMILES |
| `inchikey` | 用于去重的 InChIKey |
| `smiles_error` | 解析/标准化错误 |

报告里有：

- 总行数、有效/非法行数；
- 正/负样本数与正类比例；
- 亚类分布；
- 重复 InChIKey 组与行数。

## 2. 过滤和检查

- 删除 `smiles_error` 非空的行。
- 检查亚类分布；某个规则突然过多可能说明规则过宽。
- 人工抽样检查假阳性/假阴性。
- 保留输入记录与规则版本，便于复现。

## 3. 去重

用 `inchikey` 处理结构级重复，用谱图哈希处理谱图级重复：

```python
from flavfinder import SpectrumSchema, prepare_frame
from flavfinder.data import spectrum_key

prepared = prepare_frame(labeled, SpectrumSchema())
prepared["spectrum_key"] = [
    spectrum_key(mz, intensity)
    for mz, intensity in zip(
        prepared["_mz_values"], prepared["_intensity_values"], strict=True
    )
]
```

同一化合物不同碰撞能的谱图可能有用，可以保留，但切分时要按组。

## 4. 无泄漏切分

按化合物切分时，用 `inchikey` 作为组：

```python
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

groups = labeled["inchikey"].fillna(labeled["id"]).to_numpy()
labels = labeled["label"].astype(int).to_numpy()
splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
```

没有可靠结构时，使用 [数据审计](./08-data-audit.md) 中的近重复分组。

别在测试集上调阈值。

## 5. 正/负离子模式分别训练

```bash
flavfinder train \
  --train P_train.csv \
  --validation P_validation.csv \
  --test P_test.csv \
  --output-dir artifacts/P \
  --backend lightgbm

flavfinder train \
  --train N_train.csv \
  --validation N_validation.csv \
  --test N_test.csv \
  --output-dir artifacts/N \
  --backend lightgbm
```

要用 AutoGluon：

```bash
flavfinder train --config configs/P.yaml --backend autogluon
```

## 6. 评估与审计

```bash
flavfinder evaluate --model artifacts/P --input P_test.csv --output reports/P_metrics.json
flavfinder audit --train P_train.csv --test P_test.csv --output reports/P_audit.json
```

除了 AUROC 也报 AUPRC，检查校准，别动测试集。

## 公开数据源

| 来源 | URL | 说明 |
|---|---|---|
| GNPS | <https://gnps.ucsd.edu> | 社区谱库与分子网络 |
| MassBank | <https://massbank.eu> | 公开参考谱 |
| MoNA | <https://mona.fiehnlab.ucdavis.edu> | MassBank of North America |
| NIST | 商业授权 | 商业谱库 |
| METLIN | 商业授权 | 商业谱库 |

请检查每个来源的许可证与元数据质量。没有可靠结构的谱图无法用本工具标注。

## 需要注意

- RDKit 规则匹配的是骨架；用 NPClassifier/ClassyFire 或人工复核。
- “黄酮”的定义并不统一。糖苷、盐、混合物先标准化再匹配。
- 离子模式、仪器、碰撞能都会改变谱图，别在未检查的情况下混用。
- 公开记录可能有标签噪声、缺失结构和重复。
- 随机切分通常比真实情况好看，用分组/化合物级切分。

**下一页：** [训练](./05-training.md)
