# 环境配置指南

> **不绑定 conda**。换电脑后只需系统 Python 3.10+；优先在技能目录创建 `.venv`。

## 需要什么？

1. **Python 3.10+**（python.org 或系统包管理器即可）
2. 本技能目录下的 `requirements.txt`
3. Conda **完全可选**；无 Conda 时用技能内 `.venv`

## 首次配置（推荐，不依赖 conda）

### 已有系统 Python

```bash
python scripts/setup_env.py
python scripts/setup_env.py --fetch-python   # 可选：下载便携 Python
```

### 没有系统 Python

```powershell
.\scripts\bootstrap.ps1          # Windows
```

```bash
bash scripts/bootstrap.sh        # macOS / Linux
```

便携解释器位于 `runtime/python/`（默认不提交 Git）。详见 `runtime/README.md`。

## 一键检测（新对话必跑）

```bash
python scripts/check_env.py
# 若上面失败，可试：
py -3 scripts/check_env.py
```

输出 `"ready": true` 表示已有可用环境；缓存写入技能目录 `.cache/python_env.json`（不是 `.cursor/`）。

### 返回值说明

| 字段 | 含义 |
|------|------|
| `ready` | 是否可直接跑项目脚本 |
| `recommended_python` | 应使用的解释器完整路径 |
| `recommended_source` | 来源：`cache` / `project_venv` / `conda:某名字` / `system` |
| `action` | `use_existing` / `install_deps` / `create_venv` |

## 首次配置（仅当 `ready: false`）

### 优先：项目 .venv（推荐所有人）

```bash
cd artical_review
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python scripts/check_env.py
```

### 可选：使用你已有的 conda 环境（任意名字）

若你已有 conda 环境（名字随意），**不必新建**，只需在该环境中装依赖：

```bash
conda activate 你的环境名
pip install -r requirements.txt
python scripts/check_env.py
```

检测脚本会扫描**所有** conda 环境，找到依赖齐全的那个。

## 防误建环境的三条规则

1. **AI 不会自动 `conda create`**——避免每人造出一个重复环境
2. **`ready: true` 时绝不新建**——哪怕 shell 里 `python` 指向别的解释器
3. **优先复用**——本机缓存 → 项目 `.venv` → 任意已装依赖的 conda/系统 Python

## 新对话「检测不到环境」？

常见原因：Cursor 终端默认是 conda `base` 或未激活你的环境。

**不代表你的环境不存在。** 正确做法：

1. 跑 `scripts/check_env.py`（扫描全部环境）
2. 用输出的 `recommended_python` 跑脚本
3. 不要因 base 缺包就去 `conda create`

## 没有 Python 时能做什么？

| 功能 | 可否 |
|------|------|
| 阅读已有 `output/`、笔记、答疑 | ✅ |
| 解析新 PDF | ❌ 需 Python + 依赖 |

## AI 自动处理

见 `.cursor/rules/environment-setup.mdc`。
