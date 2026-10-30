# 文献阅读工具（literature-reading-tool）

跨 Agent 可用的科研 PDF 阅读技能：**解析 PDF → 结构化 Markdown → 中文阅读笔记 / 全文译文 → Word（.docx）导出**。

- **仓库：** https://github.com/yanchy63/literature-reading-tool  
- 兼容 [Agent Skills](https://agentskills.io) / [Agent Plugins](https://agent-plugins.org)  
- 环境以 **`.venv` / 便携 Python + pip** 为主，**不需要 conda**

---

## 一键安装（全 Agent 通用）

安装器会把技能写入各 Agent 会扫描的目录（可多选）：

| 目标 | 用户级路径 |
|------|------------|
| 通用 Agent Skills | `~/.agents/skills/scientific-paper-reading` |
| Cursor | `~/.cursor/skills/scientific-paper-reading` |
| Claude | `~/.claude/skills/scientific-paper-reading` |
| Codex | `~/.codex/skills/scientific-paper-reading` |

### Windows（PowerShell）

**远程一键（推荐）：**

```powershell
irm https://raw.githubusercontent.com/yanchy63/literature-reading-tool/main/install.ps1 | iex
```

带环境初始化 / 便携 Python / Cursor 本地插件：

```powershell
# 先下载再带参数执行更稳妥
git clone https://github.com/yanchy63/literature-reading-tool.git
cd literature-reading-tool
.\install.ps1 -WithEnv -FetchPython -CursorPlugin
```

### macOS / Linux

**远程一键：**

```bash
curl -fsSL https://raw.githubusercontent.com/yanchy63/literature-reading-tool/main/install.sh | bash
```

带参数：

```bash
git clone https://github.com/yanchy63/literature-reading-tool.git
cd literature-reading-tool
bash install.sh --with-env --fetch-python --cursor-plugin
```

### 已有仓库时用 Python 安装器（跨平台）

```bash
python install_agent_skill.py --all
python install_agent_skill.py --agents agents,cursor,claude,codex --with-env
python install_agent_skill.py --project          # 额外装到当前项目
python install_agent_skill.py --cursor-plugin    # 整仓拷到 Cursor local plugin
python install_agent_skill.py --list-targets     # 查看将写入的路径
```

安装后请 **Reload Window / 重启 Agent**，技能名：`scientific-paper-reading`。

---

## 其他安装方式

### Cursor：从 GitHub 导入插件

1. Cursor → **Customize** → 从 GitHub Repository 导入  
2. 仓库 URL：`https://github.com/yanchy63/literature-reading-tool`  
3. 安装插件 `scientific-paper-reading`

### 手动拷贝

```bash
git clone https://github.com/yanchy63/literature-reading-tool.git
cp -r literature-reading-tool/skills/scientific-paper-reading ~/.agents/skills/
```

---

## 仓库结构

```text
literature-reading-tool/             ← Git 仓库根目录
├── install.ps1 / install.sh         # 一键安装入口
├── install_agent_skill.py           # 全 Agent 通用安装器
├── plugin.json                      # Agent Plugins 清单
├── .cursor-plugin/                  # Cursor GitHub 导入用
├── README.md
├── LICENSE
└── skills/
    └── scientific-paper-reading/    ← 技能本体
        ├── SKILL.md
        ├── requirements.txt
        ├── scripts/                 # 含 bootstrap / setup_env / 解析 / Word 导出
        ├── src/
        ├── references/
        └── runtime/                 # 可选便携 Python（下载后生成，不进 Git）
```

---

## 首次环境配置（每台电脑一次）

安装技能后，在**已安装的技能目录**或仓库内 `skills/scientific-paper-reading/` 配置运行时：

### 已有 Python 3.10+

```bash
cd skills/scientific-paper-reading   # 或 ~/.agents/skills/scientific-paper-reading
python scripts/setup_env.py
python scripts/setup_env.py --fetch-python   # 可选：下载便携 Python
```

### 没有系统 Python

```powershell
.\scripts\bootstrap.ps1    # Windows
```

```bash
bash scripts/bootstrap.sh  # macOS / Linux
```

或在一键安装时加 `-WithEnv` / `--with-env`（没有 Python 时会走 bootstrap 拷贝逻辑）。

---

## 快速使用

在文献工作区（将生成 `papers/`、`output/`、`notes/`）：

```bash
<recommended_python> .../scripts/start_reading.py paper.pdf
# Agent 按 SKILL.md 生成笔记与译文后：
<recommended_python> .../scripts/export_notes_docx.py notes/<slug>
```

```bash
export PAPER_READING_WORKSPACE=/path/to/your/project
```

| 产出 | 说明 |
|------|------|
| `output/<slug>/content.md` | 解析正文 |
| `notes/<slug>/reading_note.md` / `.docx` | 阅读笔记 |
| `notes/<slug>/translation_zh.md` / `.docx` | 正文译文 |
| `notes/<slug>/translation_si_zh.md` / `.docx` | SI 译文（若有） |

---

## 许可

MIT — 见 [LICENSE](LICENSE)。
