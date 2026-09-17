#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-.}"
HOOKS="$ROOT/.git/hooks"
if [[ ! -d "$HOOKS" ]]; then
  echo "No .git/hooks directory"
  exit 0
fi
shopt -s nullglob
found=0
for f in "$HOOKS"/*; do
  base=$(basename "$f")
  [[ "$base" == *.sample ]] && continue
  [[ -f "$f" ]] || continue
  found=1
  if command -v shasum >/dev/null 2>&1; then
    hash=$(shasum -a 256 "$f" | awk '{print $1}')
  else
    hash=$(sha256sum "$f" | awk '{print $1}')
  fi
  echo "HOOK non-sample path=$f sha256=$hash"
done
if [[ "$found" -eq 0 ]]; then
  echo "No non-sample hooks"
fi
