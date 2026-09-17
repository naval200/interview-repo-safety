---
name: interview-repo-safety
description: >
  Pre-install security gate for software-engineering interview and take-home
  repositories. Performs static repository, dependency, supply-chain, secret,
  and execution-surface analysis before allowing sandboxed execution.
disable-model-invocation: true
---

# Interview Repo Safety

Treat the target repository as **untrusted software**.

Answer: *Is this interview/take-home safe enough to install and develop on my machine, and what should I investigate first?*

Two phases only. **Never** auto-advance Phase 1 → Phase 2.

| Phase | Name | When |
|---|---|---|
| 1 | Static pre-install security audit | Always on invocation |
| 2 | Optional sandboxed execution | Only if user explicitly requests **and** verdict is SAFE or REVIEW |

Do **not** use or depend on `https://github.com/Swap03pathi/interview-assignment-scanner`. Detection rules live in this skill.

Read before acting:

- [reference/static-checklist.md](reference/static-checklist.md)
- [reference/detection-rules.md](reference/detection-rules.md)
- [reference/policy.md](reference/policy.md)
- [reference/report-template.md](reference/report-template.md)
- [reference/capability-matrix.md](reference/capability-matrix.md)
- [reference/sandbox.md](reference/sandbox.md) (Phase 2 only)

Optional readonly helpers (stdlib only; never `npm install` the target):

- `scripts/inventory-node.mjs <repo>`
- `scripts/scan-surfaces.sh <repo>`
- `scripts/hash-hooks.sh <repo>`

Canonical script sources: [reference/helper-scripts.md](reference/helper-scripts.md). If on-disk scripts drift, regenerate from that file. If scripts are missing, perform the same inspections with Read / Grep / read-only Git. Policy docs remain authoritative (e.g. do not treat `@vitejs` / `@types` as private scopes).

---

## Hard rules (Phase 1)

1. **NEVER execute** the target repository (no install, build, test, Docker, scripts, lifecycle, entrypoints).
2. **NEVER** run unsafe Git that can trigger hooks: `checkout`, `switch`, `commit`, `merge`, `pull`, `rebase`, `worktree add`.
3. Read-only Git OK: `show`, `ls-tree`, `log`, `cat-file`. Fetching source OK.
4. **devDependencies are in scope.** Transitive deps are in scope.
5. Never print secret values — redacted TYPE / FILE / LOCATION / SEVERITY only.
6. Do not claim Sonatype/Opsera findings unless the tool actually returned them.
7. Do not fetch remote C2 payloads; record IOCs only.
8. Do not install Socket or other analysis tools just for this audit (use only if already present).
9. Do not claim the skill proves a repository is safe.

Announce at start: *Static-only audit. No install/run of the target.*

---

## Workflow checklist

Copy and track:

```
Interview Repo Safety
- [ ] 1. Discover repository structure
- [ ] 2. Git / repository attack surface
- [ ] 3. IDE / auto-execution surfaces
- [ ] 4. Complete dependency inventory (incl. devDeps)
- [ ] 5. Interview-specific relevance classification
- [ ] 6. Sonatype (devDeps included)
- [ ] 7. Typosquat / package confusion
- [ ] 8. Lifecycle / execution surface
- [ ] 9. Network / C2 (IOC only)
- [ ] 10. Credentials / secret access
- [ ] 11. Opsera security-scan (if available, no project install)
- [ ] 12. Assignment vs dependency mismatch
- [ ] 13. Secrets in Git history
- [ ] 14. Verdict + confidence
- [ ] 15. Emit full report
- [ ] STOP — Phase 2 only on explicit user request
```

---

### 1. Discover the repository

Inspect manifests/lockfiles/configs listed in `reference/static-checklist.md` without executing anything.

Identify: languages, frameworks, package managers, workspaces, build/test tools, CI/CD, containers, custom registries, private scopes, Git/tarball/file deps.

---

### 2. Git / repository attack surface

Follow `reference/detection-rules.md` → Git hooks.

- Flag every non-`*.sample` hook; read suspicious hooks fully; SHA-256 them.
- Check `.git/objects` vs working tree via plumbing.
- Report non-empty: `git config --global --get core.hooksPath` and `init.templateDir`.
- Do not execute hooks.

---

### 3. IDE / auto-execution

Inspect `.vscode/tasks.json`, `settings.json`, `launch.json`, `.devcontainer/`, `.idea/`.

Flag `folderOpen`, `runOn`, auto-run, postCreate/postStart/initializeCommand. Auto-exec on open = **HIGH** risk.

---

### 4. Dependency inventory

Include: `dependencies`, `devDependencies`, `optionalDependencies`, `peerDependencies`, workspaces, transitives.

For each package record: name, version, direct/transitive, type, parent, registry, source, exact resolved version.

Flag: Git/GitHub deps, HTTP(S) tarballs, file/path, aliases, custom registries, **unexpected** private/org scopes (not well-known public scopes like `@vitejs` / `@types` / `@babel`), unusual provenance.

If lockfile absent/unparsed: mark transitive graph **not verified** and lower confidence.

---

### 5. Interview-specific relevance

Read README / assignment / manifests / app + test structure. Infer what the take-home tests.

For every unusual dependency ask: *Why does this exist in this interview assignment?*

Classify per `reference/policy.md`: COMMON / ESTABLISHED BUT NICHE / OBSCURE / SUSPICIOUS. Unpopular ≠ malicious.

---

### 6. Sonatype

Reuse installed Sonatype capabilities when available:

1. `audit-dependencies` — **include devDependencies** (override default skip)
2. Unusual packages → `check-dependency`
3. Deeper supply-chain → `dependency-advisor`

Use for: vulns, malicious intel, provenance, typosquat, maintainer trust, repo/package health, transitives.

If unavailable: section = `not verified` / unavailable; do not invent results.

---

### 7. Typosquat / package confusion

For unusual names, check resemblance to popular packages / fake extensions. Prefer Sonatype. Optional Socket only if already installed.

---

### 8. Lifecycle / execution surface

Flag lifecycle script keys and static patterns in `reference/detection-rules.md`.

**CRITICAL:** remote network access + dynamic code execution (unless clear legitimate reason). Do not execute.

---

### 9. Network / C2

Collect domains, URLs, IPs, webhooks, download endpoints, TCP destinations. Flag raw-IP HTTP, unexplained domains, remote payload fetch mechanisms. **Do not fetch payloads.** Add to IOCs.

---

### 10. Credentials / secret access

Inspect `.npmrc`, `.env*`, CI, Docker, scripts, code + home-dir credential access patterns. Report redacted rows only.

---

### 11. Opsera

If Opsera `security-scan` is available, invoke for SAST / secrets / config / containers / IaC. **Do not** install project dependencies merely to run it. Separate Opsera findings from this skill's analysis.

---

### 12. Interview context mismatch

Compare ASSIGNMENT PURPOSE vs DEPENDENCY CAPABILITIES. Flag mismatches for REVIEW (not automatic malware without more evidence).

---

### 13. Secrets in Git history

Read-only `git log` / `git show` / `git cat-file` for historical credentials. Report path/commit; never values.

---

### 14. Verdict

Exactly one of: `SAFE TO INSTALL` | `REVIEW BEFORE INSTALLING` | `DO NOT INSTALL / RUN`  
Plus: `CONFIDENCE: HIGH | MEDIUM | LOW`  
Rules: `reference/policy.md`. No numerical score.

Antfarm-style chain must be caught **before** install: obscure/legit-looking animation dep → private scoped dep → malicious JS → HTTP to hardcoded IP → base64 → `new Function(...)`.

---

### 15. Report

Emit the full template in `reference/report-template.md`. Then **STOP**.

Offer Phase 2 only if the user asks and verdict is SAFE or REVIEW. Otherwise refuse install/run.

---

## Phase 2 — Optional sandboxed execution

Follow `reference/sandbox.md`:

- Explicit user request required
- Prefer restricted terminal (deny network by default, workspace FS only, no sudo/SSH agent/home secrets)
- npm allowlist starts at `registry.npmjs.org`; other domain → STOP
- Stop conditions → `DO NOT CONTINUE`
- Unrestricted needs → `DISPOSABLE VM REQUIRED` (never weaken sandbox)

---

## Final self-check before delivering the report

- [ ] Would the Antfarm-style chain be flagged before install?
- [ ] Were `devDependencies` and transitives considered?
- [ ] Was `.npmrc` inspected?
- [ ] Was task relevance considered?
- [ ] Was any target code executed? (must be no)
- [ ] Were secrets printed? (must be no)
- [ ] Were unsafe Git ops used? (must be no)
- [ ] Were IDE auto-run tasks checked?
