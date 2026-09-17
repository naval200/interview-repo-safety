# Existing Capability Matrix

Source: local Cursor plugin cache for Sonatype + Opsera (read-only inspection).  
Do **not** depend on https://github.com/Swap03pathi/interview-assignment-scanner.

| EXISTING CAPABILITY | WHAT IT DOES | CAN WE REUSE IT? | GAP |
|---|---|---|---|
| Sonatype `audit-dependencies` | Full project dependency audit via Guide MCP (CVEs, license, quality). **Skips devDependencies by default.** | **YES** — force include `devDependencies` | No git/IDE attack surface, interview relevance, lifecycle/C2, history secrets, categorical gate |
| Sonatype `check-dependency` | Deep dive one package: vulns, license, Developer Trust Score | **YES** — for unusual / flagged packages | Same |
| Sonatype `dependency-advisor` (agent) | Provenance, typosquat/malicious signals, maintainer trust, transitive analysis | **YES** — deepen flagged packages | Not a pre-install gate by itself |
| Sonatype `find-safer-version` | Safer version recommendations | Optional / low priority for gate | Not needed for verdict |
| Sonatype rule `dependency-hygiene` | Edit-time guidance when changing manifests | Context only | Wrong lifecycle (edit-time, not pre-install) |
| Sonatype rule `security-first-deps` | Prefer high trust / avoid known vulns when adding deps | Context only | Wrong lifecycle |
| Opsera `security-scan` | Secrets, SAST, containers, IaC (phased MCP) | **YES** when scanners work **without** installing project deps | May need host scanner binaries; document limitation |

## Boundary of this skill

**Owns:** static-first ban list; unsafe Git ban; repo discovery; git hooks + SHA-256; orphaned objects; global hooksPath/templateDir; IDE/devcontainer auto-run; full dependency inventory (incl. devDeps); interview relevance classification; typosquat heuristics (prefer Sonatype); lifecycle + dynamic exec + network/C2/IOC collection; credential presence + history secrets; categorical verdict + confidence; report template; sandbox/VM policy.

**Does not own:** CVE databases, malware DBs, reputation engines, replacement typosquat engines, generic SAST rule packs.
