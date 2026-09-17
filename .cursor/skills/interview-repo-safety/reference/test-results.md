# Synthetic Fixture Test Results

Temporary fixtures were created under `/tmp/interview-repo-safety-fixtures`, validated **without installing**, then deleted.

| Fixture | Expected | Actual | Result |
|---|---|---|---|
| 01 Normal React | SAFE TO INSTALL | SAFE TO INSTALL (after public-scope allowlist fix for `@vitejs`) | PASS |
| 02 Obscure package | REVIEW BEFORE INSTALLING | REVIEW BEFORE INSTALLING | PASS |
| 03 Typosquat-like | REVIEW or DO NOT | REVIEW BEFORE INSTALLING | PASS |
| 04 Malicious lifecycle | DO NOT INSTALL / RUN | DO NOT INSTALL / RUN | PASS |
| 05 Suspicious Git hook | DO NOT INSTALL / RUN | DO NOT INSTALL / RUN | PASS |
| 06 VS Code folderOpen | DO NOT INSTALL / RUN | DO NOT INSTALL / RUN | PASS |
| 07 `.npmrc` credential | REVIEW or DO NOT | REVIEW BEFORE INSTALLING | PASS |
| 08 Dynamic + network | DO NOT INSTALL / RUN | DO NOT INSTALL / RUN | PASS |
| 09 Private dependency | REVIEW or DO NOT | REVIEW BEFORE INSTALLING | PASS |
| 10 Hidden git-history credential | REVIEW or DO NOT | REVIEW BEFORE INSTALLING | PASS |
| 11 Antfarm-style chain | DO NOT INSTALL / RUN | DO NOT INSTALL / RUN | PASS |

Notes:

- No `node_modules` were created.
- Initial false positive on `@vitejs/plugin-react` was fixed in policy/detection rules + inventory helper.
- Sonatype/Opsera were **not verified** in these synthetic runs (tools not invoked against fixtures); sections would be `not verified` in a live audit when unavailable.
