# Sandboxed Execution (Phase 2)

Phase 2 is **not** “run it in Cursor’s terminal.” It is the Docker jail in `sandbox/reposafety-run`.

## Entry rules

- Do **not** install or run anything automatically after the static audit.
- Do **not** install or run the target on the host. Not even with a “restricted terminal.”
- Enter Phase 2 only when the user **explicitly** requests execution (`install in the sandbox`, `run phase 2`, `npm install in the jail`).
- Only allow a normal Phase 2 run if the static verdict is `SAFE TO INSTALL` or `REVIEW BEFORE INSTALLING`.
- If verdict is `DO NOT INSTALL / RUN`, refuse Phase 2. Recommend discard or a disposable VM.
- **Observe exception:** if the user explicitly says **observe** / `/interview-repo-safety observe` after a BLOCK verdict, you may start the same jail so they can watch install-time behavior. Warn that this is observation only. Default-deny egress stays on. Do **not** whitelist C2 IPs, raw IPs, or unexplained hosts. Do **not** weaken the jail.

## Runner

From this skill directory:

```bash
sandbox/reposafety-run --repo <absolute-or-relative-target> -- <command...>
```

Examples the agent should use (never the host equivalents):

```bash
sandbox/reposafety-run --repo "$TARGET" -- npm install
sandbox/reposafety-run --repo "$TARGET" -- npm run dev
sandbox/reposafety-run --repo "$TARGET" --allow pypi.org --allow files.pythonhosted.org \
  --image python:3.12-bookworm-slim -- pip install -r requirements.txt
```

- `--allow registry.npmjs.org` is already the default. Extra `--allow` is **additive**.
- `--image` defaults to `node:22-bookworm-slim`. Pick `python:3.12-bookworm-slim` (or similar) from Phase 1 language. Do not build or run the target’s Dockerfile.
- Docker Desktop (or an equivalent daemon) must be running. If `reposafety-run` exits **2**, report that and stop. Do not fall back to host install.
- Exit **3** means the proxy logged `BLOCKED egress:` → treat as **DO NOT CONTINUE**. Print the blocked host. Do **not** pass `--allow` for it unless the user explicitly names that host.

If `sandbox/reposafety-run` is missing, do **not** invent a weaker substitute. Stop and tell the user Phase 2 requires the runner.

## What the jail enforces

| Control | Mechanism |
|---|---|
| Filesystem | Bind-mount **only** the target repo at `/work`. Read-only container root. tmpfs home + `/tmp`. No `$HOME`, `~/.ssh`, `~/.aws`, `~/.npmrc`, Git creds, browser profiles, Docker socket. |
| Privilege | Non-root (`uid:gid` of the caller). `cap_drop: ALL`. `no-new-privileges`. No sudo. |
| Network | Sandbox sits on an **internal** Compose network (no default internet). The only egress is an HTTP/HTTPS proxy on that network. |
| Egress allowlist | Proxy default-deny. Default host: `registry.npmjs.org`. Anything else is `BLOCKED egress: host:port` (HTTP 403) and the runner exits 3. |
| Download log | Proxy prints `ALLOW CONNECT host:port`, `ALLOW HTTP …`, and `TRANSFER CONNECT host:port bytes=N`. HTTPS URLs are not decrypted (no MITM). Host + bytes are the monitor. |
| Cleanup | Compose project is torn down on exit. |

The runner does **not** mount `/var/run/docker.sock` and does **not** run `--privileged` / `--network host`.

## Registry allowlist

Initially allow only:

- `registry.npmjs.org`

If installation contacts another domain:

1. **STOP** (`BLOCKED egress`, exit 3)
2. Report the host from the proxy log
3. Do **not** automatically `--allow` it
4. Ask the user. Only add `--allow <host>` if they name that host.

GitHub, raw IPs, and extra CDNs are **not** implied.

## Stop conditions → `DO NOT CONTINUE`

Stop Phase 2 (kill the runner if it is still up) if you observe:

- `BLOCKED egress:` in the proxy log
- Attempts to read SSH keys / cloud credentials / unrelated files (should fail in the jail; still stop)
- Persistence / launch agents / shell rc edits on the **host** (must not be possible; if you see it, the jail failed — stop and say so)
- Execute downloaded remote code from a non-allowlisted host
- Unexplained raw TCP, obfuscated payloads, unexplained shells

Change execution status to: **DO NOT CONTINUE**

## VM escalation → `DISPOSABLE VM REQUIRED`

If the repository requires unrestricted filesystem, unrestricted network, sudo, host SSH agent, cloud credentials, Docker socket, browser profile access, or Docker-in-Docker:

- Do **not** weaken the jail
- Do **not** add `--privileged` or mount the Docker socket
- Recommend: **DISPOSABLE VM REQUIRED**

## Agent checklist (Phase 2)

```
Phase 2
- [ ] User explicitly requested install/run
- [ ] Verdict is SAFE or REVIEW (or explicit observe after BLOCK)
- [ ] Docker is available (reposafety-run not exit 2)
- [ ] Command is sandbox/reposafety-run … -- <cmd>  (not host npm/pip)
- [ ] Default allowlist only, unless user named extra hosts
- [ ] Proxy log reviewed for BLOCKED egress and ALLOW lines
- [ ] Jail not weakened
```
