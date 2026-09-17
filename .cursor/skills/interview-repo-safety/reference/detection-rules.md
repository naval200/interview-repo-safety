# Detection Rules

Encoded from the interview-repo-safety specification.  
**Do not** clone or depend on Swap03pathi/interview-assignment-scanner.

Label every finding: `our static analysis found` | `tool reported` | `not verified`.

---

## Git hooks (HIGH → BLOCK when clearly malicious)

1. List `.git/hooks/` — flag every non-`*.sample` file.
2. Read suspicious hooks completely (do not execute).
3. Flag patterns:
   - `curl` / `wget` / `curl | sh` / `wget | sh` / `curl | bash` / `wget | bash`
   - `child_process` / shell command execution
   - raw IP addresses / HTTP(S) URLs
   - background execution (`&`)
   - `uname` / `$OSTYPE` / platform detection
   - `/dev/null` redirection hiding output
   - encoded / base64 payloads
   - credential path access (`~/.ssh`, `~/.aws`, tokens)
4. Compute SHA-256 of each suspicious hook; add to IOCs.
5. Via read-only plumbing, check for objects in `.git/objects/` not represented in the normal working tree.
6. Report non-empty global: `core.hooksPath`, `init.templateDir`.

---

## IDE / auto-execution (HIGH)

Inspect `.vscode/tasks.json`, `settings.json`, `launch.json`, `.devcontainer/`, `.idea/`.

Flag:

- `folderOpen` / `runOn` / auto-run on open
- terminal / shell tasks that run without user action
- `postCreateCommand` / `postStartCommand` / `initializeCommand`
- launch configs that auto-start dangerous processes

Any command that runs when a developer **opens** the repo is HIGH risk → typically **DO NOT INSTALL / RUN** or strong REVIEW with BLOCK if clearly malicious.

---

## Lifecycle scripts

In `package.json` (and workspace packages), flag keys:

`preinstall`, `install`, `postinstall`, `prepare`, `prepublish`, `prepack`, `prepublishOnly`

Treat network + download + shell in these as CRITICAL.

---

## Dynamic execution / obfuscation

Static-search source and scripts for:

- `child_process`, `exec`, `execSync`, `spawn`, `spawnSync`, `shell`
- `eval`, `new Function`
- dynamic `require(` / `import(`
- `atob`, `Buffer.from(..., 'base64')`, long base64 blobs
- obfuscation patterns, very long encoded strings
- `curl`, `wget`, `powershell`
- remote JS/shell retrieval
- HTTP(S), WebSockets, raw TCP, DNS lookups

**CRITICAL:** REMOTE NETWORK ACCESS + DYNAMIC CODE EXECUTION (unless clear legitimate reason documented in Limitations).

Do not execute findings. Do not fetch remote payloads.

---

## Network / C2

Collect every domain, URL, IP, webhook, download endpoint, raw TCP destination.

Flag:

- raw IP over HTTP
- unexplained / unrelated domains
- dynamic remote code or shell retrieval
- hardcoded C2-like endpoints, unusual ports
- connections unrelated to assignment purpose

Record as IOCs; never fetch the payload.

---

## Credentials / secret access

Inspect `.npmrc`, `.env*`, GitHub Actions, Dockerfiles, shell scripts, CI, application code.

Detect presence of (never print values):

- npm tokens, private registry credentials
- GitHub / cloud / AWS / DB / API keys, SSH keys, Authorization headers

Also flag code accessing:

- `~/.ssh`, `~/.aws`, `~/.config`
- browser profiles, Keychain, password stores, crypto wallet extensions

Report: **TYPE | FILE | LOCATION | SEVERITY** (value redacted).

---

## Git history secrets

Using `git log` / `git show` / `git cat-file` only:

- Look for historical `.npmrc`, `.env`, credentials, tokens, API keys, private keys removed from the working tree.
- Report file/path/commit; never expose secret values.

---

## Scoped packages (do not over-flag)

Scoped names are **not** automatically private or suspicious.

Treat as COMMON / EXPECTED when the scope is a well-known public ecosystem scope, for example:

`@types`, `@babel`, `@vitejs`, `@angular`, `@mui`, `@react-native`, `@testing-library`, `@storybook`, `@nestjs`, `@aws-sdk`, `@firebase`, `@emotion`, `@chakra-ui`, `@tanstack`, `@reduxjs`, `@eslint`, `@typescript-eslint`

Flag as **unexpected private / unusual scope** (REVIEW) when:

- Scope looks org-internal (`@acme-corp`, `@company-internal`, `@private-*`)
- Scope is unknown and unrelated to the assignment
- `.npmrc` maps that scope to a non-public registry

---

## Typosquat / package confusion

For unusual dependencies, check resemblance to popular packages (e.g. `lodash`→`lodahs`, `express`→`expres`, `dotenv`→`dotenv-plus`, fake helpers of popular names). Prefer Sonatype intelligence. Optional Socket only if already installed.
