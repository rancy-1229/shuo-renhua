#!/usr/bin/env bash
# 说人话 · 一键安装到你的 agent harness
# 用法: curl -fsSL <raw-url>/install.sh | bash
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="shuo-renhua"
installed=()

install_to() {
    local dest="$1"
    if [ -d "$(dirname "$dest")" ]; then
        mkdir -p "$dest"
        cp -R "$SRC/SKILL.md" "$SRC/rules" "$SRC/renhua" "$dest/"
        installed+=("$dest")
    fi
}

# Claude Code / Cursor / 通用 agents 目录
[ -d "$HOME/.claude" ] && install_to "$HOME/.claude/skills/$NAME"
# pi coding agent
[ -d "$HOME/.pi" ] && install_to "$HOME/.pi/agent/skills/$NAME"
# Codex
[ -d "$HOME/.codex" ] && install_to "$HOME/.codex/skills/$NAME"
# 通用 ~/.agents/skills（paseo 等读取）
install_to "$HOME/.agents/skills/$NAME"

if [ ${#installed[@]} -eq 0 ]; then
    echo "没找到已知的 agent 目录。手动安装："
    echo "  cp -R $SRC ~/.claude/skills/$NAME"
    exit 1
fi

echo "✓ 说人话 已安装到："
for d in "${installed[@]}"; do echo "  $d"; done
echo
echo "试一下（不需要 agent，直接跑检测器）："
echo "  python3 ${installed[0]}/renhua check 你的文件.md"
