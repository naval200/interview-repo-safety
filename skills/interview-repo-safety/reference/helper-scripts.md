# Optional Readonly Helper Scripts

Plan mode may block creating executable files. If `scripts/*.sh` / `scripts/*.mjs` are absent, create them from the blocks below (stdlib only) **or** perform the same checks with Read/Grep/read-only Git.

These helpers must **never** install packages or execute repository code.

Phase 2 install/run is **not** these scripts. It is `sandbox/reposafety-run` (Docker). See [sandbox.md](sandbox.md).

---

## `scripts/hash-hooks.sh`

```bash
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
```

---

## `scripts/scan-surfaces.sh`

```bash
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
```

---

## `scripts/inventory-node.mjs`

```javascript
#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');
const root = path.resolve(process.argv[2] || '.');
const pkgPath = path.join(root, 'package.json');

const KNOWN_PUBLIC_SCOPES = new Set([
  '@types','@babel','@vitejs','@angular','@mui','@react-native','@testing-library',
  '@storybook','@nestjs','@aws-sdk','@firebase','@emotion','@chakra-ui','@tanstack',
  '@reduxjs','@eslint','@typescript-eslint','@radix-ui','@next','@swc','@rollup',
]);

function classifySource(spec) {
  const s = String(spec);
  if (s.startsWith('git+') || s.includes('github.com') || s.startsWith('git://')) return 'git';
  if (/^https?:\/\//.test(s) && /\.tgz|\.tar\.gz|tarball/i.test(s)) return 'tarball';
  if (s.startsWith('file:') || s.startsWith('.') || s.startsWith('/')) return 'file';
  if (s.startsWith('npm:')) return 'alias';
  return 'registry';
}

function scopeOf(name) {
  if (!name.startsWith('@') || !name.includes('/')) return null;
  return name.slice(0, name.indexOf('/'));
}

if (!fs.existsSync(pkgPath)) {
  console.log(JSON.stringify({ error: 'no package.json', root }, null, 2));
  process.exit(0);
}

const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
const sections = ['dependencies', 'devDependencies', 'optionalDependencies', 'peerDependencies'];
const entries = [];
for (const section of sections) {
  for (const [name, version] of Object.entries(pkg[section] || {})) {
    const scope = scopeOf(name);
    const knownPublic = scope ? KNOWN_PUBLIC_SCOPES.has(scope) : false;
    entries.push({
      name,
      version,
      directOrTransitive: 'direct',
      dependencyType: section,
      parent: null,
      source: classifySource(version),
      scoped: Boolean(scope),
      knownPublicScope: knownPublic,
      unexpectedPrivateScope: Boolean(scope) && !knownPublic,
      unusualSource: classifySource(version) !== 'registry',
    });
  }
}

const lockCandidates = [
  'package-lock.json', 'npm-shrinkwrap.json', 'pnpm-lock.yaml',
  'yarn.lock', 'bun.lock', 'bun.lockb',
];
const lifecycle = {};
for (const key of ['preinstall','install','postinstall','prepare','prepublish','prepack','prepublishOnly']) {
  if (pkg.scripts && pkg.scripts[key]) lifecycle[key] = pkg.scripts[key];
}

console.log(JSON.stringify({
  root,
  name: pkg.name || null,
  workspaces: pkg.workspaces || null,
  lockfiles: lockCandidates.filter((f) => fs.existsSync(path.join(root, f))),
  note: 'Transitive deps require lockfile parse; mark not verified if absent. unexpectedPrivateScope excludes known public scopes.',
  directDependencies: entries,
  lifecycleScripts: lifecycle,
  npmrcPresent: fs.existsSync(path.join(root, '.npmrc')),
}, null, 2));
```

If `scripts/inventory-node.mjs` on disk is missing the `KNOWN_PUBLIC_SCOPES` allowlist, overwrite it from this block (Plan mode may leave an older copy). Policy in `detection-rules.md` / `policy.md` is authoritative for agents either way.
