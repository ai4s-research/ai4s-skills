#!/usr/bin/env bash
#
# Install AI4S skills into your Claude Code skills directory.
#
#   ./install.sh                      # install ALL skills into ./.claude/skills
#   ./install.sh literature-survey    # install specific skill(s)
#   SKILLS_DIR=~/.claude/skills ./install.sh   # install globally instead
#
# By default skills go to ./.claude/skills in the CURRENT directory (this project).
# Set SKILLS_DIR=~/.claude/skills to install globally (available in every session).
# Run it from your project root, e.g.:  /path/to/ai4s-skills/install.sh

set -euo pipefail

SRC="$(cd "$(dirname "$0")/skills" && pwd)"
DEST="${SKILLS_DIR:-.claude/skills}"

# Which skills to install: the args given, or all of them.
if [ "$#" -gt 0 ]; then
  names=("$@")
else
  names=()
  for d in "$SRC"/*/; do names+=("$(basename "$d")"); done
fi

mkdir -p "$DEST"
installed=0
for n in "${names[@]}"; do
  # Reject empty or path-like names: "" would expand to "$DEST/" and rm -rf
  # the whole skills directory; "../x" would escape it.
  if [ -z "$n" ] || [[ "$n" == */* ]]; then
    echo "  ✗ '$n' (invalid skill name — skipped)"
    continue
  fi
  if [ -d "$SRC/$n" ]; then
    rm -rf "${DEST:?}/$n"
    cp -R "$SRC/$n" "$DEST/$n"
    echo "  ✓ $n"
    installed=$((installed + 1))
  else
    echo "  ✗ $n (not found — skipped)"
  fi
done

echo ""
echo "Installed $installed skill(s) into: $DEST"
echo "Restart Claude Code (or reload skills) to pick them up."
