# 数据审计与泄漏

**层级：** 3 — 理解  
**前置条件：** [评估](./07-evaluation.md)。

随机切分可能把近似相同的谱图同时放进训练集与测试集。报告指标前必须审计。

## CLI

```bash
flavfinder audit \
  --train data/P/train.csv \
  --test data/P/test.csv \
  --output reports/P_audit.json
```

报告包含：

- 谱图数与峰数；
- 类别比例；
- 峰数分布；
- m/z 范围与超网格计数；
- 精确重复组与标签冲突；
- 训练/测试精确重叠。

## 精确重复

```python
from flavfinder import audit_frame, leakage_report

audit = audit_frame(train_frame)
leak = leakage_report(train_frame, test_frame)
print(audit["duplicates"])
print(leak["overlap_n"])
```

精确匹配使用排序后的 m/z 与强度生成的稳定键。

## 近重复

```python
from flavfinder import BinningTransformer, near_duplicate_pairs

transformer = BinningTransformer()
pairs = near_duplicate_pairs(
    train_frame,
    transformer,
    threshold=0.95,
)
```

在分箱向量上分块计算余弦相似度。它是**审计工具**，不是在线索引，复杂度随行数平方增长。

## 分组切分

用重复对做连通分量：

```python
from flavfinder import groups_from_pairs, group_split_indices

groups = groups_from_pairs(len(train_frame), pairs)
split = group_split_indices(
    groups,
    train_frame["label"],
    test_size=0.2,
    validation_size=0.2,
    seed=42,
)
print({name: len(indices) for name, indices in split.items()})
```

提供二分类标签时，`group_split_indices` 使用分层分组交叉验证
（`StratifiedGroupKFold`），同时保持两类样本和组不交叉；没有标签时退回贪心切分。

`group_split_indices` 是贪心的分组切分，保证同一重复/近重复组只落在一侧。它不是真正的化合物级分组。

## 化合物 ID 的限制

提供的数据只有 `mz`、`intensity`、`label`，没有化合物标识，因此没有外部元数据时无法严格“按分子切分”。近重复聚类只是代理，报告中必须说明。

## 推荐审计流程

1. 检查 schema 与非法行。
2. 统计精确重复与标签冲突。
3. 计算训练/测试精确重叠。
4. 在 0.90 / 0.95 / 0.99 等阈值下做近重复聚类。
5. 构建分组切分。
6. 重训并比较 random split 与 group split 指标。
7. 两者都报告，并解释差异。

## 重复数据怎么处理

- 同一谱图标签冲突：修源数据或删除歧义组。
- 同一谱图跨 train/test：整组移到一侧。
- 跨切分近重复：视为泄漏，改用分组切分。

**下一页：** [方法](./09-method.md)
