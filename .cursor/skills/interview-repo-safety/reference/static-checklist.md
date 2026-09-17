# Static Checklist

## Banned during Phase 1 (static audit)

Never run against the target repository:

- `npm install` / `npm ci` / `yarn install` / `pnpm install` / `bun install`
- `pip install` / `cargo build` / `go build` / `make`
- `npm run *` / `yarn *` / `pnpm *` / `bun *`
- `pytest` / `jest` / `vitest` / `playwright`
- Docker containers / compose up
- Repository shell scripts / application entry points
- Package lifecycle scripts

Unsafe Git (may trigger hooks) — do **not** run inside untrusted repos:

- `git checkout` / `git switch` / `git commit` / `git merge`
- `git pull` / `git rebase` / `git worktree add`

## Allowed read-only Git

- `git show` / `git ls-tree` / `git log` / `git cat-file`
- Fetching/cloning source into an isolated location is allowed
- `git config --global --get core.hooksPath`
- `git config --global --get init.templateDir`

## Manifests and lockfiles to discover

- `package.json`, `package-lock.json`, `npm-shrinkwrap.json`
- `pnpm-lock.yaml`, `yarn.lock`, `bun.lock*`
- `requirements.txt`, `pyproject.toml`, `setup.py`, `setup.cfg`
- `Cargo.toml`, `go.mod`, `Gemfile`, `pom.xml`, `build.gradle*`
- `Makefile`, `Dockerfile*`, `docker-compose*`, `Taskfile*`

## Config / IDE / agent surfaces

- `.npmrc`, `.nvmrc`, `.yarnrc*`, `.pnpmfile.*`
- `.env*`
- `.github/`, `.git/`, `.git/hooks/`, `.git/objects/`
- `.cursor/`, `.claude/`, `.vscode/` (tasks/settings/launch), `.devcontainer/`, `.idea/`

## Identify

Languages, frameworks, package managers, monorepo/workspaces, build/test tools, CI/CD, containers, custom registries, private scopes, Git/tarball/file dependencies.
