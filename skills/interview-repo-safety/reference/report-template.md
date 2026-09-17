# Report Template

Emit exactly this structure. Fill every section (use `None found` or `Not verified` when empty).

```markdown
# Interview Take-home Security Audit

## VERDICT

SAFE TO INSTALL | REVIEW BEFORE INSTALLING | DO NOT INSTALL / RUN

## CONFIDENCE

HIGH | MEDIUM | LOW

## Executive Summary

[2–5 sentences: what was audited, top risks, why this verdict]

## Assignment Context

[What the interview task appears to be testing]

## Dependency Inventory

| Package | Version | Direct/Transitive | Assessment | Reason |
|---|---|---|---|---|
| … | … | … | … | … |

## Unusual Dependencies

[List with classification and why]

## Typosquat / Package Confusion

[Findings or None found]

## Git Hooks / Auto-run

[Hooks, IDE tasks, devcontainer lifecycle — or None found]

## Lifecycle Scripts

[preinstall/install/postinstall/… — or None found]

## Dynamic Execution / Obfuscation

[Findings — label CRITICAL when network + dynamic exec]

## Network / Remote Execution

[Domains/IPs/URLs and mechanisms — do not fetch payloads]

## Credentials / Secrets

| TYPE | FILE | LOCATION | SEVERITY |
|---|---|---|---|
| … | … | … | … |

Values redacted. Never print secrets.

## Git History Findings

[Historical credentials by path/commit — values redacted]

## Sonatype Findings

[Only results actually returned by Sonatype tools. Else: not verified / unavailable]

## Opsera Findings

[Only results actually returned by Opsera. Else: not verified / unavailable]

## Static Analysis Findings

[This skill's own static findings]

## IOCs

- domains:
- IPs:
- URLs:
- filenames:
- hook hashes:
- package names:
- suspicious commit identifiers:

## Limitations

[What was not verified: missing tools, incomplete lockfile, no install-time behavior observed, etc.]

## Recommendation

SAFE TO PROCEED | REVIEW BEFORE INSTALLING | DO NOT RUN
```
