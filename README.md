# 文献阅读工具（scientific-paper-reading）

跨 Agent 可用的科研 PDF 阅读技能：**解析 PDF → 结构化 Markdown → 中文阅读笔记 / 全文译文 → Word（.docx）导出**。

> GitHub 仓库展示名建议改为「文献阅读工具」（Settings → General → Repository name）。

不绑定 Cursor；兼容 [Agent Skills](https://agentskills.io) / [Agent Plugins](https://agent-plugins.org) 约定。环境以 **`.venv` + pip** 为主，**不需要 conda**。

## 仓库结构

```text
scientific-paper-reading/          ← Git 仓库根目录
├── plugin.json                    # Agent Plugins 清单
├── .cursor-plugin/                # Cursor 从 GitHub 导入用
│   ├── plugin.json
│   └── marketplace.json
├── README.md
├── LICENSE
└── skills/
    └── scientific-paper-reading/  ← 技能本体
        ├── SKILL.md
        ├── requirements.txt
        ├── scripts/
        ├── src/
        ├── references/
        └── assets/
```

## 安装方式

### A. 任意 Agent（通用，推荐）

把技能目录拷到本机技能路径之一：

| Agent | 用户级目录 | 项目级目录 |
|-------|------------|------------|
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` |
| 通用 / Claude 等 | `~/.agents/skills/` | `.agents/skills/` |

```bash
git clone https://github.com/<你的用户名>/scientific-paper-reading.git
# 只安装技能本体
cp -r scientific-paper-reading/skills/scientific-paper-reading ~/.agents/skills/
# 或 Cursor：
# cp -r scientific-paper-reading/skills/scientific-paper-reading ~/.cursor/skills/
```

Windows PowerShell 示例：

```powershell
git clone https://github.com/<你的用户名>/scientific-paper-reading.git
Copy-Item -Recurse scientific-paper-reading\skills\scientific-paper-reading $HOME\.agents\skills\
# 或 Cursor：
# Copy-Item -Recurse ... $HOME\.cursor\skills\
```

### B. Cursor：从 GitHub 导入插件市场

1. 将本仓库推送到 GitHub（需含 `.cursor-plugin/marketplace.json`）
2. Cursor → **Customize** → 从 GitHub Repository 导入该仓库
3. 安装插件 `scientific-paper-reading`

### C. 本地插件调试（Cursor）

```text
~/.cursor/plugins/local/scientific-paper-reading/   ← 放整个仓库内容
```

然后 Reload Window，在 Customize 中确认技能出现。

## 首次环境配置（每台电脑一次）

**不需要 conda。** 按机器情况选一条路径：

### 路径 1：电脑上已有 Python 3.10+

```bash
cd skills/scientific-paper-reading
python scripts/setup_env.py
# 可选：同时下载便携 Python 到 runtime/python/（换机/内网友好）
python scripts/setup_env.py --fetch-python
```

### 路径 2：电脑上没有 Python（推荐）

```powershell
# Windows（只需 PowerShell，可联网）
cd skills\scientific-paper-reading
.\scripts\bootstrap.ps1
```

```bash
# macOS / Linux（只需 curl + tar）
cd skills/scientific-paper-reading
bash scripts/bootstrap.sh
```

会下载 [python-build-standalone](https://github.com/astral-sh/python-build-standalone) 便携包到 `runtime/python/`，再安装依赖。

### 路径 3：离线拷贝

在能上网的机器执行 bootstrap / `fetch_portable_python.py` 后，把整个 `runtime/python/` 拷到目标机同路径即可（约 20–40MB，**不进 Git**）。

之后一律用输出的 `recommended_python` 跑脚本。

## 快速使用

在你的文献工作区（含或将生成 `papers/`、`output/`、`notes/`）下：

```bash
# 解析
<recommended_python> /path/to/skill/scripts/start_reading.py paper.pdf

# 笔记与译文由 Agent 按 SKILL.md 写入 notes/<slug>/

# 导出 Word
<recommended_python> /path/to/skill/scripts/export_notes_docx.py notes/<slug>
```

也可设置工作区：

```bash
export PAPER_READING_WORKSPACE=/path/to/your/project   # Windows: set PAPER_READING_WORKSPACE=...
```

## 产出文件

| 文件 | 说明 |
|------|------|
| `output/<slug>/content.md` | 解析后的正文（Agent 主阅读源） |
| `notes/<slug>/reading_note.md` / `.docx` | 阅读笔记 |
| `notes/<slug>/translation_zh.md` / `.docx` | 正文译文 |
| `notes/<slug>/translation_si_zh.md` / `.docx` | SI 译文（若有） |

## 许可

MIT — 见 [LICENSE](LICENSE)。
