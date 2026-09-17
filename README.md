# interview-repo-safety

Cursor / Claude Code plugin that runs a **pre-install security gate** for software-engineering interview and take-home repositories.

Treat every take-home as untrusted software. This does **not** prove a repository is safe; it produces an evidence-based categorical verdict.

## Develop in this repo

This workspace **is** the skill source. Edits under `skills/interview-repo-safety/` are what you ship.

While this folder is open in Cursor, the skill is available via a project symlink:

```text
.cursor/skills/interview-repo-safety → skills/interview-repo-safety
```

Invoke:

```text
/interview-repo-safety
```

## Layout

```text
skills/interview-repo-safety/   # Agent Skill (source of truth)
.cursor-plugin/plugin.json      # Cursor plugin manifest
plugin.json                     # Agent Plugins (portable) manifest
.claude-plugin/plugin.json      # Claude Code plugin manifest
.cursor/skills/…                # symlink for local Cursor development
```

## Install

### Cursor (personal skill — simplest)

```bash
git clone https://github.com/naval200/interview-repo-safety.git
cd interview-repo-safety
mkdir -p ~/.cursor/skills
ln -s "$(pwd)/skills/interview-repo-safety" ~/.cursor/skills/interview-repo-safety
```

Or copy the folder instead of symlinking. Restart Agent chat, then run `/interview-repo-safety`.

### Cursor (plugin)

1. Clone this repo (or open it).
2. For local plugin testing, link into Cursor’s local plugins dir, then reload the window:

```bash
mkdir -p ~/.cursor/plugins/local
ln -s "$(pwd)" ~/.cursor/plugins/local/interview-repo-safety
```

3. Later: submit at [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish).

### Claude Code

```bash
# Personal skill
mkdir -p ~/.claude/skills
ln -s /path/to/interview-repo-safety/skills/interview-repo-safety \
  ~/.claude/skills/interview-repo-safety
```

Or install as a Claude plugin from this repo once added as a marketplace source (`/plugin marketplace add naval200/interview-repo-safety`).

### Other agents (`npx skills`)

```bash
npx skills add naval200/interview-repo-safety
```

## Usage

```bash
git clone <interview-repo>
cd <interview-repo>
# DO NOT npm/yarn/pnpm/bun/pip install yet
```

Then in Agent chat:

```text
/interview-repo-safety
```

Do not `npm install` on the host. Phase 2 (only if you ask, and only after a non-blocking verdict) uses `sandbox/reposafety-run` (Docker jail, default-deny network).

Skill details: [skills/interview-repo-safety/README.md](skills/interview-repo-safety/README.md)
