# Portable Python runtime（可选）

本目录可存放**随技能分发的便携 Python**，换电脑时即使没有系统 Python / conda 也能跑解析脚本。

## 布局

```text
runtime/
  python/          ← 便携解释器根目录（勿提交到 Git，体积大）
    python.exe     # Windows
    bin/python3    # macOS / Linux
  python_version.json  ← 当前运行时元数据（可选）
```

## 获取方式

### 1. 一键脚本（推荐）

**已有任意 Python 时：**

```bash
python scripts/fetch_portable_python.py
python scripts/setup_env.py --prefer-bundled
```

**完全没有 Python 时：**

```powershell
# Windows PowerShell
.\scripts\bootstrap.ps1
```

```bash
# macOS / Linux
bash scripts/bootstrap.sh
```

### 2. 手动打包进 U 盘 / 内网机

在一台能上网的机器上执行 `fetch_portable_python.py`，然后把整个 `runtime/python/` 目录拷到目标机同一路径即可。

### 3. 为何不提交到 Git？

单平台便携包约 20–40 MB，三平台合计更大，不适合放进 Git 仓库。默认 `.gitignore` 忽略 `runtime/python/`；可用 GitHub Release 附件分发预构建包。

## 优先级

`check_env` / `setup_env` 查找顺序：

1. `runtime/python`（bundled）
2. 技能 `.venv`
3. 本机已有 Python / 可选 conda
4. 自动创建 `.venv` 并 pip 安装依赖
