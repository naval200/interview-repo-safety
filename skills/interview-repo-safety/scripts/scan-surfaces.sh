#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-.}"
cd "$ROOT"
PATTERNS='preinstall|postinstall|child_process|execSync|spawnSync|new Function|eval\(|Buffer\.from\([^)]*base64|atob\(|curl |wget |folderOpen|postCreateCommand|postStartCommand|initializeCommand|~\/\.ssh|~\/\.aws|_authToken|AKIA[0-9A-Z]{16}'
echo "=== Static surface scan (read-only) root=$ROOT ==="
if command -v rg >/dev/null 2>&1; then
  rg -n -S -g '!node_modules' -g '!.git/objects' -e "$PATTERNS" . || true
else
  grep -R -n -E "$PATTERNS" --exclude-dir=node_modules --exclude-dir=.git . 2>/dev/null || true
fi
