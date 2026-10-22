# 安装

**层级：** 1 — 开始  
**前置条件：** Python 3.10–3.12 与 `pip`。

## 从代码仓库安装

```bash
git clone https://github.com/DavidNiteas/flavfinder-core.git
cd flavfinder-core
python -m pip install -e ".[dev]"
```

基础安装包含 NumPy、pandas、SciPy、scikit-learn、PyYAML、tqdm 与 joblib。可选后端单独安装。

## 可选后端

### AutoGluon（参考后端）

```bash
python -m pip install -e ".[autogluon]"
```

AutoGluon 依赖较大。`autogluon` extra 安装 `autogluon.tabular[all]`，包含参考流程使用的
CatBoost、XGBoost、LightGBM、FastAI 与 Torch 模型族。需要复现原项目的表格模型流程时使用。

### LightGBM（快速本地后端）

```bash
python -m pip install -e ".[lightgbm]"
```

LightGBM 轻量得多，适合快速实验与本地验证。

### scikit-learn（测试与小数据）

scikit-learn 后端包含在基础安装中，仅用于冒烟测试和很小的数据集，不替代完整数据上的 AutoGluon / LightGBM。

### RDKit（标注）

```bash
python -m pip install -e ".[chem]"
```

`flavfinder label` 用 RDKit 匹配 SMILES 中的黄酮骨架。若数据已有标签，训练/预测不需要它。

## 验证安装

```bash
flavfinder --version
flavfinder --describe
```

- `--version` 输出包版本。
- `--describe` 说明这是独立的纯代码实现，不包含数据与模型。

## 构建 wheel

构建后端使用 **hatchling**：

```bash
python -m build
python -m pip install dist/flavfinder_core-*.whl
```

## Docker

仓库包含纯代码 Dockerfile，不包含数据、模型、测试或文档：

```bash
docker build -t flavfinder-core:local .
docker run --rm flavfinder-core:local --describe
```

Dockerfile 只安装基础包。需要 AutoGluon 或 LightGBM 时，请扩展镜像或在运行时安装 extra。

## 从 wheel 安装

```bash
python -m pip install flavfinder_core-*.whl
```

## 常见安装问题

| 现象 | 处理 |
|---|---|
| `ModuleNotFoundError: autogluon` | `pip install -e ".[autogluon]"` |
| `ModuleNotFoundError: lightgbm` | `pip install -e ".[lightgbm]"` |
| `ModuleNotFoundError: rdkit` | `pip install -e ".[chem]"` |
| 选中了 Python 3.13 | 使用 3.10–3.12（`requires-python` 已排除 3.13） |
| `hatchling` 构建失败 | 升级 `pip` 后重试；hatchling 已在 `pyproject.toml` 声明 |

**下一页：** [快速开始](./02-quickstart.md)
