#!/usr/bin/env bash
# Bootstrap portable Python + deps WITHOUT requiring a preinstalled Python
# (needs curl + tar only).
# Usage (from skill directory):
#   bash scripts/bootstrap.sh
#   bash scripts/bootstrap.sh --force

set -euo pipefail
FORCE=0
VERSION="3.12.11"
RELEASE="20250808"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) FORCE=1; shift ;;
    --version) VERSION="$2"; shift 2 ;;
    --release) RELEASE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_DIR="$SKILL_ROOT/runtime"
PYTHON_DIR="$RUNTIME_DIR/python"

OS="$(uname -s)"
ARCH="$(uname -m)"
if [[ "$OS" == "Darwin" ]]; then
  if [[ "$ARCH" == "arm64" ]]; then TARGET="aarch64-apple-darwin"; else TARGET="x86_64-apple-darwin"; fi
else
  if [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then TARGET="aarch64-unknown-linux-gnu"; else TARGET="x86_64-unknown-linux-gnu"; fi
fi

ASSET="cpython-${VERSION}+${RELEASE}-${TARGET}-install_only.tar.gz"
URL="https://github.com/astral-sh/python-build-standalone/releases/download/${RELEASE}/${ASSET}"

find_py() {
  for c in \
    "$PYTHON_DIR/bin/python3" \
    "$PYTHON_DIR/bin/python" \
    "$PYTHON_DIR/python/bin/python3" \
    "$PYTHON_DIR/python.exe"
  do
    [[ -x "$c" ]] && { echo "$c"; return 0; }
  done
  return 1
}

EXISTING="$(find_py || true)"
if [[ -n "${EXISTING}" && "$FORCE" -eq 0 ]]; then
  echo "[bootstrap] Found bundled Python: $EXISTING"
else
  mkdir -p "$RUNTIME_DIR"
  TMP="$(mktemp -d)"
  ARCHIVE="$TMP/$ASSET"
  echo "[bootstrap] Downloading $URL"
  curl -L --fail --retry 3 -o "$ARCHIVE" "$URL"
  rm -rf "$PYTHON_DIR"
  mkdir -p "$PYTHON_DIR"
  tar -xzf "$ARCHIVE" -C "$TMP"
  # move extracted top-level into PYTHON_DIR
  TOP="$(find "$TMP" -mindepth 1 -maxdepth 1 -type d ! -name "$(basename "$ARCHIVE" .tar.gz)" | head -1)"
  # install_only usually extracts a "python" directory
  if [[ -d "$TMP/python" ]]; then
    TOP="$TMP/python"
  fi
  if [[ -z "${TOP}" || ! -d "$TOP" ]]; then
    # copy whatever was extracted
    cp -R "$TMP"/* "$PYTHON_DIR/" 2>/dev/null || true
  else
    cp -R "$TOP"/. "$PYTHON_DIR/"
  fi
  rm -rf "$TMP"
  EXISTING="$(find_py)"
  if [[ -z "${EXISTING}" ]]; then
    echo "[bootstrap] python executable not found after extract" >&2
    exit 1
  fi
  echo "[bootstrap] Installed: $EXISTING"
fi

"$EXISTING" "$SKILL_ROOT/scripts/setup_env.py" --prefer-bundled --reinstall
echo "[bootstrap] Done. Use the recommended_python from setup_env output."
