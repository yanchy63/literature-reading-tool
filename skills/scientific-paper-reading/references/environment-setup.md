# 环境检测与自动配置

## 核心原则（防止误建多余环境）

1. **不绑定 `artical` 或任何固定 conda 名**——每人环境名不同，甚至没有 conda
2. **配置前必须先跑** `scripts/check_env.py`（或读 `.cursor/python_env.json`）
3. **`ready: true` 则禁止任何新建**（conda create / venv 都不行）
4. **禁止 AI 自动执行 `conda create`**——即使用户有 conda，新建环境只用项目内 `.venv`
5. 终端裸 `python` 失败 **≠** 没有可用环境（shell 可能未激活）

## 检测优先级（脚本自动完成）

1. 本机缓存 `.cursor/python_env.json`（上次在本项目成功的解释器）
2. 项目 `.venv`
3. 当前 shell 激活的 conda 环境
4. **全部** conda 环境（任意名称，逐个验证依赖）
5. PATH 中的 python / py

任一通过依赖检查 → `action: use_existing`，直接用 `recommended_python`。

## 运行项目脚本

```bash
# ✅ 始终用 check_env 返回的 recommended_python 完整路径
<recommended_python> scripts/process_pdf.py papers/unread/xxx.pdf

# ❌ 禁止新对话中直接用裸 python
python scripts/process_pdf.py ...
```

## action 含义与允许的操作

| action | 含义 | 允许操作 | 禁止 |
|--------|------|----------|------|
| `use_existing` | 已有可用环境 | 直接跑脚本 | 任何新建 |
| `install_deps` | 有 Python 但缺包 | 对该解释器 `pip install -r requirements.txt` | conda create |
| `create_venv` | 无任何 Python 3.10+ | 仅 `python -m venv .venv` + pip install | conda create |

## 触发配置的条件

- `check_env.py` 返回 `"ready": false`，或脚本明确报 ModuleNotFoundError
- **不是** output 缺失、**不是** base 环境缺包、**不是** shell 未 activate

## AI 行为

- `ready: true` → 一句话确认（说明来源如 project_venv / conda:xxx），不展开教程
- 发现多个可用环境 → 用优先级最高的，不重复创建
- 配置后必须重跑 `check_env.py` 验证

