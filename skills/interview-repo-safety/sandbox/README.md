# Phase 2 runner

Docker jail used only after Phase 1, and only on an explicit user request.

```bash
./reposafety-run --repo /path/to/take-home -- npm install
```

- Filesystem: target bind-mounted at `/work` only
- Network: default-deny HTTP/HTTPS proxy; `registry.npmjs.org` allowed until you `--allow` more
- Logs: `ALLOW CONNECT …`, `TRANSFER CONNECT … bytes=`, `BLOCKED egress: host:port`

Policy and agent rules: [../reference/sandbox.md](../reference/sandbox.md).
