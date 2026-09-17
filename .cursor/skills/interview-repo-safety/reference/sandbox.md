# Sandboxed Execution (Phase 2)

## Entry rules

- Do **not** install or run anything automatically after the static audit.
- Enter Phase 2 only when the user **explicitly** requests execution.
- Only allow if static verdict is `SAFE TO INSTALL` or `REVIEW BEFORE INSTALLING`.
- If verdict is `DO NOT INSTALL / RUN`, refuse sandboxed install/run and recommend disposable VM or discard.

## Preferred environment

Use Cursor's restricted / sandboxed terminal when available:

- Deny-by-default network
- Workspace-only filesystem access
- No sudo
- No SSH agent
- No `~/.ssh`, `~/.aws`, `~/.config`
- No browser profiles
- No global Git credentials
- No npm auth tokens / home directory mounts

## Registry allowlist

For npm installation, initially allow only:

- `registry.npmjs.org`

If installation contacts another domain:

1. **STOP**
2. Report domain, package responsible, reason if identifiable
3. Do **not** automatically allow it

## Stop conditions → `DO NOT CONTINUE`

Immediately stop sandboxed execution if the project attempts to:

- Read SSH keys / browser credentials / unrelated files
- Access cloud credentials
- Establish persistence / modify shell startup files
- Install launch agents/daemons
- Execute downloaded remote code
- Contact unexplained external IPs / unrelated domains
- Establish unexplained raw TCP connections
- Execute obfuscated payloads
- Spawn unexplained shell commands

Change execution status to: **DO NOT CONTINUE**

## VM escalation → `DISPOSABLE VM REQUIRED`

If the repository requires unrestricted filesystem, unrestricted network, sudo, host SSH agent, cloud credentials, Docker socket, or browser profile access:

- Do **not** weaken the sandbox
- Recommend: **DISPOSABLE VM REQUIRED**
