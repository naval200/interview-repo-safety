# interview-repo-safety

Pre-install security gate for **software engineering interview / take-home** repositories.

Treat every take-home as **untrusted software**. This skill does **not** prove a repository is safe; it produces an evidence-based categorical verdict to help you decide what to do next.

## Purpose

Answer:

> Is this interview/take-home repository safe enough to install and develop on my machine, and what should I investigate before doing so?

## Invocation

In Cursor Agent chat (with this skill available):

```text
/interview-repo-safety
```

Or ask explicitly:

```text
Run interview-repo-safety on this repository
```

**Typical workflow:**

```bash
git clone <interview-repo>
cd <interview-repo>
# DO NOT npm install / yarn / pnpm / bun / pip / etc.
```

Then invoke `/interview-repo-safety` before any install or run.

## Phases

### Phase 1 — Static pre-install audit (always)

Read-only inspection. No install, build, test, Docker, lifecycle scripts, or unsafe Git operations that can trigger hooks.

Covers:

- Repository discovery
- Git hooks / orphaned objects / global hooksPath
- IDE / devcontainer auto-run
- Full dependency inventory (**including devDependencies** and transitives when lockfiles allow)
- Interview-specific relevance / task mismatch
- Sonatype reuse (when available)
- Typosquat / confusion heuristics
- Lifecycle + dynamic execution + network/C2 IOCs
- Credentials (redacted) + secrets in Git history
- Opsera `security-scan` when available without installing project deps
- Categorical verdict + confidence + full report

### Phase 2 — Optional sandboxed execution (never automatic)

Only if you **explicitly** request it and Phase 1 verdict is `SAFE TO INSTALL` or `REVIEW BEFORE INSTALLING`.

Uses restricted terminal preferences: deny-by-default network, workspace-only FS, no sudo/SSH agent/home credential mounts. npm starts allowlisted to `registry.npmjs.org`. Unexpected domains → STOP. Dangerous behavior → `DO NOT CONTINUE`. Needs that break the sandbox → `DISPOSABLE VM REQUIRED` (sandbox is not weakened).

## Verdict meanings

| Verdict | Meaning |
|---|---|
| **SAFE TO INSTALL** | No critical/high findings; deps fit the assignment; no dangerous auto-run / suspicious credentials / unexplained private deps |
| **REVIEW BEFORE INSTALLING** | Obscure/unusual packages, weak provenance, unusual registries, unexplained deps, or moderate concerns — investigate before install |
| **DO NOT INSTALL / RUN** | Strong malicious / RCE / malicious hook-lifecycle-autorun / credential theft / supply-chain compromise indicators |

Also: `CONFIDENCE: HIGH | MEDIUM | LOW`. No numerical “% safe” score.

Recommendation line: `SAFE TO PROCEED` | `REVIEW BEFORE INSTALLING` | `DO NOT RUN`.

## How Sonatype is reused

When installed/configured:

- `audit-dependencies` with **devDependencies included**
- `check-dependency` for unusual packages
- `dependency-advisor` for deeper supply-chain analysis

Used for vulns, malicious package intelligence, provenance, typosquatting, maintainer trust, quality/health, transitives.

Findings appear only under **Sonatype Findings** when tools actually return data.

## How Opsera is reused

When available: `security-scan` for SAST, secrets, security config, containers, IaC — **without** installing the take-home’s dependencies merely to scan.

Findings appear only under **Opsera Findings** when tools actually return data.

## New interview-specific logic (this skill)

- Static-first + unsafe-Git bans
- Assignment relevance classification (COMMON → SUSPICIOUS)
- Git hook / IDE auto-run / history-secret focus for take-homes
- Network+dynamic-exec CRITICAL heuristic and IOC listing without fetching payloads
- Categorical gate + confidence + structured report
- Sandbox / VM escalation policy

## Layout

Canonical path in this plugin repo:

```text
skills/interview-repo-safety/
  SKILL.md
  README.md
  reference/
    capability-matrix.md
    detection-rules.md
    policy.md
    report-template.md
    static-checklist.md
    sandbox.md
  scripts/          # optional readonly helpers (stdlib only)
```

For local Cursor development, `.cursor/skills/interview-repo-safety` symlinks here. Personal installs may live under `~/.cursor/skills/`, `~/.claude/skills/`, or `~/.agents/skills/`.
## Limitations

- Does not execute the target; install-time and runtime behavior are **not verified** in Phase 1
- Transitive graphs may be incomplete without parseable lockfiles
- Sonatype/Opsera/Socket results appear only when those tools are available and actually run
- Heuristic relevance and typosquat checks can false-positive; obscure ≠ malicious
- Does not replace a disposable VM for high-risk work

## Exact invoke command

```text
/interview-repo-safety
```
