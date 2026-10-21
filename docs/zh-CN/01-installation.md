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

AutoGluon 依赖较大。需要复现原项目的表格模型流程时使用。

### LightGBM（快速本地后端）

```bash
python -m pip install -e ".[lightgbm]"
```

LightGBM 轻量得多，适合快速实验与本地验证。

### scikit-learn（测试与小数据）

scikit-learn 后端包含在基础安装中，仅用于冒烟测试和很小的数据集，不替代完整数据上的 AutoGluon / LightGBM。

## 验证安装

```bash
flavfinder --version
flavfinder --describe
```

- `--version` 输出包版本。
- `--describe` 说明这是独立的纯代码移植版本，不包含数据与模型。

## 构建 wheel

构建后端使用 **hatchling**：

```bash
python -m build
python -m pip install dist/flavfinder_core-*.whl
```

## 从 wheel 安装

```bash
python -m pip install flavfinder_core-0.1.0-py3-none-any.whl
```

## 常见安装问题

| 现象 | 处理 |
|---|---|
| `ModuleNotFoundError: autogluon` | `pip install -e ".[autogluon]"` |
| `ModuleNotFoundError: lightgbm` | `pip install -e ".[lightgbm]"` |
| 选中了 Python 3.13 | 使用 3.10–3.12（`requires-python` 已排除 3.13） |
| `hatchling` 构建失败 | 升级 `pip` 后重试；hatchling 已在 `pyproject.toml` 声明 |

**下一页：** [快速开始](./02-quickstart.md)
