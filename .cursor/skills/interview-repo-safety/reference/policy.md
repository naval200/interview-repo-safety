# Interview Policy & Verdict Rules

## Package classification

| Class | Meaning | Effect |
|---|---|---|
| COMMON / EXPECTED | Normal for this assignment | Low concern |
| ESTABLISHED BUT NICHE | Real ecosystem package, uncommon here | REVIEW |
| OBSCURE / UNUSUAL | Little-known, new, or unexplained | REVIEW |
| SUSPICIOUS / HIGH RISK | Strong malicious / compromise indicators | BLOCK |

**Unpopular ≠ malicious.** Obscure packages get REVIEW, not an automatic malware label.

Core heuristic: *Does this dependency make sense for this take-home?*

Scrutinize especially:

- Unrelated to stated task (e.g. blockchain in CRUD, obscure animation in backend)
- Native binary packages with no need
- Unexpected private/org-internal packages in otherwise public projects
- Packages that add unrelated network access

Do **not** flag well-known public scopes (e.g. `@vitejs`, `@types`, `@babel`) as private merely because they use `@`.

## Assignment vs capability mismatch

Compare ASSIGNMENT PURPOSE to DEPENDENCY CAPABILITIES.

Flag for REVIEW (not automatic malware): wallet/blockchain stacks, native downloaders, obscure package managers, private registries, unrelated telemetry, shell-execution deps, credential-access libraries in a simple frontend/CRUD take-home.

## Verdict (exactly one)

### SAFE TO INSTALL

- No critical/high findings
- No suspicious supply-chain findings
- No suspicious credentials
- No unexplained private dependency
- No dangerous auto-run behavior
- Dependencies reasonably fit the assignment

### REVIEW BEFORE INSTALLING

- Obscure / unusual packages
- Suspicious naming or weak provenance
- Unusual registries
- Unexplained dependency
- Moderate security concerns

### DO NOT INSTALL / RUN

- Confirmed malware / malicious package
- RCE or suspicious remote code download/execution
- Malicious lifecycle script, Git hook, or auto-run task
- Credential theft behavior
- Strong supply-chain compromise evidence

## Confidence

Also output: `CONFIDENCE: HIGH | MEDIUM | LOW`

- HIGH: tools available + inventory complete + clear signals
- MEDIUM: partial tool coverage or incomplete lockfile/transitive graph
- LOW: missing manifests, tools unavailable, or large unverified surface

No numerical safety score.

## Recommendation mapping

| Verdict | Recommendation |
|---|---|
| SAFE TO INSTALL | SAFE TO PROCEED |
| REVIEW BEFORE INSTALLING | REVIEW BEFORE INSTALLING |
| DO NOT INSTALL / RUN | DO NOT RUN |

## Evidence attribution

Always distinguish:

- **tool reported** (Sonatype / Opsera / Socket if present)
- **our static analysis found**
- **not verified**
