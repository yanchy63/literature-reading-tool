#!/usr/bin/env bash
# 文献阅读工具 — 全 Agent 一键安装（macOS / Linux）
# 用法:
#   已在仓库内:  bash install.sh
#   远程一键:    curl -fsSL https://raw.githubusercontent.com/yanchy63/literature-reading-tool/main/install.sh | bash
#   参数:        bash install.sh --with-env --fetch-python --cursor-plugin

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/yanchy63/literature-reading-tool.git}"
INSTALL_DIR="${INSTALL_DIR:-$HOME/literature-reading-tool}"
AGENTS="${AGENTS:-agents,cursor,claude,codex}"
WITH_ENV=0
FETCH_PYTHON=0
CURSOR_PLUGIN=0
PROJECT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-env) WITH_ENV=1; shift ;;
    --fetch-python) FETCH_PYTHON=1; shift ;;
    --cursor-plugin) CURSOR_PLUGIN=1; shift ;;
    --project) PROJECT=1; shift ;;
    --agents) AGENTS="$2"; shift 2 ;;
    --install-dir) INSTALL_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
REPO_ROOT=""

if [[ -n "${SCRIPT_DIR}" && -f "${SCRIPT_DIR}/install_agent_skill.py" ]]; then
  REPO_ROOT="$SCRIPT_DIR"
elif [[ -f "./install_agent_skill.py" ]]; then
  REPO_ROOT="$(pwd)"
else
  if [[ ! -f "${INSTALL_DIR}/install_agent_skill.py" ]]; then
    echo "[install] Cloning ${REPO_URL} -> ${INSTALL_DIR}"
    rm -rf "${INSTALL_DIR}"
    git clone --depth 1 "${REPO_URL}" "${INSTALL_DIR}"
  fi
  REPO_ROOT="${INSTALL_DIR}"
fi

cd "${REPO_ROOT}"
echo "[install] Repo: ${REPO_ROOT}"

find_python() {
  for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then
      echo "$c"
      return 0
    fi
  done
  return 1
}

ARGS=(install_agent_skill.py --agents "${AGENTS}")
[[ "$PROJECT" -eq 1 ]] && ARGS+=(--project)
[[ "$CURSOR_PLUGIN" -eq 1 ]] && ARGS+=(--cursor-plugin)
[[ "$WITH_ENV" -eq 1 ]] && ARGS+=(--with-env)
[[ "$FETCH_PYTHON" -eq 1 ]] && ARGS+=(--fetch-python)

if PY="$(find_python)"; then
  echo "[install] Using Python: ${PY}"
  exec "$PY" "${ARGS[@]}"
fi

echo "[install] No Python found; copying skill folders directly..."
SRC="${REPO_ROOT}/skills/scientific-paper-reading"
[[ -f "${SRC}/SKILL.md" ]] || { echo "Skill source missing: ${SRC}"; exit 1; }

copy_one() {
  local dest="$1"
  rm -rf "$dest"
  mkdir -p "$(dirname "$dest")"
  cp -R "$SRC" "$dest"
  echo "[install] -> $dest"
}

IFS=',' read -ra WANT <<< "$AGENTS"
for k in "${WANT[@]}"; do
  k="$(echo "$k" | tr -d ' ')"
  case "$k" in
    agents) copy_one "$HOME/.agents/skills/scientific-paper-reading" ;;
    cursor) copy_one "$HOME/.cursor/skills/scientific-paper-reading" ;;
    claude) copy_one "$HOME/.claude/skills/scientific-paper-reading" ;;
    codex)  copy_one "$HOME/.codex/skills/scientific-paper-reading" ;;
  esac
done

echo "[install] For Python runtime: cd ~/.agents/skills/scientific-paper-reading && bash scripts/bootstrap.sh"
if [[ "$WITH_ENV" -eq 1 ]]; then
  cd "$HOME/.agents/skills/scientific-paper-reading"
  bash scripts/bootstrap.sh
fi
echo "[install] Done. https://github.com/yanchy63/literature-reading-tool"
