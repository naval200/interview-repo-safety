# From prompt to skill

A long prompt is a one-shot instruction. A skill is a **repeatable procedure** the agent reloads on demand. This note explains how to convert the first into the second, using `interview-repo-safety` as the worked example.

It is **human documentation**. It is not loaded during `/interview-repo-safety`. Do not put teaching notes in `skills/*/reference/` — that directory is the agent’s working set.

---

## 1. What a skill actually is

A skill is a directory whose only required file is `SKILL.md`:

```text
<skill-name>/
  SKILL.md          # YAML frontmatter + markdown procedure
  README.md         # optional: humans
  reference/        # optional: details the agent reads when a step needs them
  scripts/          # optional: mechanical helpers the agent may run
```

Grok, Cursor, and Claude Code all discover skills this way. The markdown body is a **prompt for the agent**, not a blog post and not a product spec.

On invocation (`/skill-name`, or auto-invoke when allowed), the harness inlines `SKILL.md`. Supporting files are **not** all stuffed into context. The agent reads them when the procedure says to. That is why a 21-phase prompt should not become a 21-phase `SKILL.md`.

### Frontmatter that matters

| Field | Role |
|---|---|
| `name` | Identifier and slash command (`/interview-repo-safety`) |
| `description` | What it does **and when to use it**. Drives auto-invocation |
| `disable-model-invocation` | `true` → slash command only. The model will not start the skill on its own |

Most skills want a specific `description` so the model *can* auto-invoke. A **security gate** is the opposite: the user must opt in before install. That is why this skill copied `disable-model-invocation: true` from the original prompt.

`SKILL.md` is a procedure. `README.md` is for people (install, invoke, limitations). Do not make the agent “run the README.”

---

## 2. The mapping method (any prompt → any skill)

Paste-the-prompt-into-`SKILL.md` fails for three reasons:

1. Authoring leftovers (“create this file”, “test in `/tmp`”, “then self-review the skill”) run again on every later invocation.
2. Long lists burn the context window. Grok inlines at most the first ~25k tokens of a skill body; other harnesses are similar. Details belong in sibling files.
3. Colliding names. Specs often reuse “Phase 2” for a product stage *and* a workflow step.

Sort every paragraph of the original prompt into **one** of these buckets:

| Bucket | Question | Where it lives |
|---|---|---|
| **Authoring** | Is this how to *build* the skill? | Do it once. Keep a short record (git, a test-results file). Do **not** ship it as runtime instructions |
| **Product phases** | What are the modes of the workflow, and the hard stop between them? | Top of `SKILL.md` |
| **Hard bans** | What must never happen, regardless of step? | Short numbered list in `SKILL.md` |
| **Ordered workflow** | What does the agent do, in order? | Checklist in `SKILL.md` — titles only, plus a pointer |
| **Inventories** | File names, banned commands, ecosystems to scan | `reference/<topic>-checklist.md` |
| **Matchers** | Regexes, IOCs, attack *classes* | `reference/detection-rules.md` (or equivalent) |
| **Judgment** | How to classify, pass/fail, severity | `reference/policy.md` |
| **Output contract** | Exact headings, tables, enums the user expects | `reference/report-template.md` (or similar) |
| **Foreign tools** | What to reuse vs invent | `reference/capability-matrix.md` |
| **Later stage** | Optional second mode (sandbox, deploy, PR) | `reference/<stage>.md`; `SKILL.md` only points at it |
| **Mechanical count** | Parsing, hashing, grepping | `scripts/` + a markdown copy of the source |
| **Human how-to** | Install, invoke, caveats | `README.md` |

Rule of thumb: **SKILL.md tells the agent *what to do next*. Reference files own the facts.** One home per fact. If a list appears in two files, one of them will rot.

---

## 3. Standard layout

Minimum (what `/create-skill` scaffolds):

```text
.grok/skills/<name>/SKILL.md          # project skill
# or
~/.grok/skills/<name>/SKILL.md        # user skill
```

A skill that has outgrown one file (this repo):

```text
plugin-repo/
  plugin.json                         # portable / npx skills
  .cursor-plugin/plugin.json          # Cursor
  .claude-plugin/plugin.json          # Claude Code
  README.md                           # humans: install this plugin
  docs/                               # humans: design notes (this file)
  .cursor/skills/<name> → …           # symlink so Cursor sees it while you edit
  skills/<name>/                      # Agent Skill (source of truth)
    SKILL.md
    README.md
    reference/                        # agent working set
    scripts/                          # optional helpers
    sandbox/                          # this skill’s Phase 2 only
```

Notes that transfer to other projects:

- **Canonical path is `skills/<name>/`**, not `.cursor/skills/`. Cursor/Claude personal installs are copies or symlinks of that folder. Packaging as a plugin comes *after* the skill works.
- **`reference/` vs `references/`.** Grok’s scaffolder uses `references/`. Cursor/Anthropic examples often use `reference/`. Either is fine; this repo uses `reference/`. What matters is that `SKILL.md` links the files.
- **Do not put human essays in `reference/`.** Anything there is a candidate for the agent to read mid-task.
- **Scripts are optional and must be skippable.** If plan-mode cannot create executables, the procedure still has to work with Read / Grep / a language’s stdlib.

---

## 4. Worked example: the original prompt

The original `interview-repo-safety` prompt looked like one 21-phase spec. It was actually **three documents**:

| In the prompt | Job | Fate |
|---|---|---|
| PHASE 19–21 | Author the skill, test fixtures, self-review the *skill* | Git history + `reference/test-results.md`. Not a runtime phase |
| GOAL + PHASE 0, 16–18 | Product: static audit, then optional sandbox; never auto-advance | Top of `SKILL.md` + `reference/sandbox.md` + later `sandbox/` |
| PHASE 1–15 | Runtime audit steps | Checklist 1–15 in `SKILL.md`; lists/rules/templates in `reference/` |

The prompt also used **Phase 2** twice: GOAL Phase 2 = sandbox, PHASE 2 = Git hooks. The skill reserved **Phase 1 / Phase 2** for the product gate and renamed audit steps to a **numbered checklist**. Original PHASE 0 (never execute the target) became **Hard rules**, not a check-box you finish and leave behind.

PHASE 19 asked only for:

```text
.cursor/skills/interview-repo-safety/SKILL.md
.cursor/skills/interview-repo-safety/README.md
```

and: *do not create a second scanner; orchestrate existing tools.* Extra files exist because dumping PHASE 0–18 into `SKILL.md` would mix authoring with auditing and duplicate every list.

### File-by-file (this skill)

| File | Owns | Came from |
|---|---|---|
| `SKILL.md` | Goal, two phases, hard bans, checklist, pointers, Antfarm chain, pre-report self-check | GOAL, PHASE 0, compressed 1–15, PHASE 21 minus authoring |
| `README.md` | Invoke, verdict meanings, limitations | PHASE 19 “also create README” |
| `reference/static-checklist.md` | Banned commands; manifests and config paths to open | PHASE 0 + 1 |
| `reference/detection-rules.md` | Attack **classes**: hooks, IDE auto-run, lifecycle, C2, secrets, typosquat, scopes | PHASE 2, 3, 7–10, 13 |
| `reference/policy.md` | COMMON→BLOCK, unpopular ≠ malware, verdicts, confidence, evidence labels | PHASE 5, 12, 14 |
| `reference/report-template.md` | Exact report headings | PHASE 15 |
| `reference/capability-matrix.md` | Sonatype/Opsera reuse vs what this skill owns; no Swap03pathi dependency | PHASE 6, 11 |
| `reference/sandbox.md` | Phase 2 entry rules, stop conditions, VM escalation | PHASE 16–18 |
| `reference/helper-scripts.md` | Canonical source of the helpers (policy outranks a stale `.sh`) | Not in the prompt; added so scripts can be regenerated |
| `reference/test-results.md` | Expected verdicts for synthetic fixtures | PHASE 20 residue (trees were deleted) |
| `scripts/*.sh`, `inventory-node.mjs` | Enumerate; never assign SAFE/REVIEW/BLOCK | PHASE 19 “orchestrate, don’t scan” |
| `sandbox/` | Docker jail that actually enforces PHASE 16 | Later; first version was “prefer Cursor’s restricted terminal” |

### Three commits, three layers

On `naval200/interview-repo-safety` (`master`):

1. **`475fc5a`** — Implement the prompt as a Cursor skill under `.cursor/skills/…`, with `reference/` + `scripts/`. Phase 2 is still policy (“restricted terminal”).
2. **`4918919`** — Move the skill to `skills/interview-repo-safety/`, add plugin manifests, make `.cursor/skills/…` a symlink. Same procedure, wider distribution.
3. **`3b29068`** — Replace “hope the host terminal is restricted” with `sandbox/reposafety-run` (folder jail + default-deny proxy). Intent of PHASE 16–18 stayed; the mechanism changed.

When you convert your own prompt: **first commit = the procedure. Later commits = packaging and enforcement.** Do not block shipping the skill on a perfect sandbox.

### What stayed a class, not a denylist

PHASE 21 asked: would this catch decoy animation package → private scoped dropper → raw-IP HTTP → base64 → `new Function`?

The skill stores that as a **chain to catch before install**, not as “flag `animatecss-tailwind-adapter`.” The named case lives on the website (`content/cases/antfarm-take-home.md`). Hardcoding package names would miss the next decoy.

Same idea as skill-design-principles: fix the *class* of problem, not the one instance you were shown.

---

## 5. Design rules that survive other projects

These are independent of interview malware.

1. **Strip authoring from the runtime skill.** “Create this file / test in `/tmp` / review the skill” belongs in the commit that built it.
2. **Collapse colliding phase numbers.** Product stages keep “Phase N.” Workflow steps become a checklist.
3. **SKILL.md stays a prompt.** Goal, bans, ordered steps, pointers, stop conditions. Not the full spec.
4. **One home per fact.** New hook pattern → detection-rules. New verdict implication → policy. SKILL.md may *point*; it should not *repeat the list*.
5. **Orchestrate tools; don’t reimplement them.** Optional scanners stay optional. Missing tool → `not verified`. Never install a tool merely to finish the run.
6. **Scripts count; markdown judges.** Helpers may print JSON or hashes. Verdicts stay in the agent + policy.
7. **Keep a markdown canonical copy of scripts** if plan-mode or copy-paste installs can drop executables. This repo: `helper-scripts.md` wins if `scripts/` drifts. (Today `inventory-node.mjs` still flags every `@scope` as private; `helper-scripts.md` has `KNOWN_PUBLIC_SCOPES`. The agent is told the markdown wins.)
8. **`description` for discovery; `disable-model-invocation` for safety.** Most skills auto-invoke. Gates, destructive ops, and anything that must not start from a side remark should be slash-only.
9. **Golden path, not a denylist.** One canonical attack chain (or one canonical good run) is the regression test.
10. **Human README vs agent SKILL.md.** Humans need install/invoke/limits. The agent needs procedure.

A larger skill (Impeccable) uses the same split at more scale: `SKILL.md` is routing + principles; each command has `reference/<command>.md`; scripts load product context. If your prompt has many subcommands, add a routing table in `SKILL.md` and one reference file per command — do not grow a single checklist forever.

---

## 6. Adding a newly discovered pattern (this skill)

Suppose a take-home drops a malicious Cursor rule under `.cursor/rules/` that tells the agent to fetch a payload.

1. **Name the class**, not the filename. This is IDE / agent auto-execution, same family as `folderOpen` and `postCreateCommand`.
2. **Discovery list** → `reference/static-checklist.md` (add the path).
3. **Detection** → `reference/detection-rules.md` (network + dynamic exec stays CRITICAL).
4. **Verdict** → `reference/policy.md` only if severity is new. Existing HIGH / BLOCK often already covers “runs on open.”
5. **Grep helper** → edit `reference/helper-scripts.md` **first**, then `scripts/scan-surfaces.sh`.
6. **Workflow** → `SKILL.md` only if this is a *new step*. If it fits checklist item 3, leave the checklist alone.
7. **Report** → `reference/report-template.md` only for a new section. Most findings fit Auto-run, Dynamic Execution, Network, or IOCs.
8. **Prove it** the PHASE 20 way: tiny repo in `/tmp`, never install, expected verdict, row in `test-results.md`, delete the tree. A real take-home writeup belongs on the website, not as a package denylist.
9. **Self-check** PHASE 21: caught before install? devDeps/transitives in scope? secrets unprinted? target uneexecuted?

Do **not**: add a second scanner; hardcode one package in `SKILL.md`; patch only `scripts/`; invent a numeric safety score; auto-advance to Phase 2 “to confirm.”

---

## 7. Converting your next prompt (checklist)

- [ ] Highlight every “create the skill / write tests for the skill / review the skill” paragraph. Those are authoring. Do them; don’t leave them in `SKILL.md`.
- [ ] Write the `description` as “what + when.” Decide `disable-model-invocation` explicitly.
- [ ] Name the product phases (usually 1–3). Put hard stop conditions at the top.
- [ ] Turn remaining steps into a short checklist. Each item is a title + a link to the file that owns the details.
- [ ] Split leftover text by *kind* (inventory / matcher / policy / template / foreign tools / later stage).
- [ ] Add `scripts/` only for work that is mechanical and skippable.
- [ ] Write `README.md` for a human who was not in the authoring chat.
- [ ] Run the skill once on a fixture you understand. Record expected vs actual somewhere durable, then delete throwaway trees.
- [ ] Package (`skills/` + plugin manifests + symlink) only after the procedure works.

Mental picture:

```text
Original long prompt
        │
        ├─ authoring                         → do once (git / test-results)
        ├─ product phases + hard bans        → SKILL.md top
        ├─ ordered workflow                  → SKILL.md checklist
        ├─ inventories                       → reference/*-checklist.md
        ├─ matchers / attack classes         → reference/detection-rules.md
        ├─ how to judge                      → reference/policy.md
        ├─ required output                   → reference/report-template.md
        ├─ optional external tools           → reference/capability-matrix.md
        ├─ later-stage policy                → reference/<stage>.md
        ├─ mechanical enumeration            → scripts/ + helper-scripts.md
        └─ human how-to                      → README.md
```

---

## 8. Where to read more in this repo

| Path | Audience |
|---|---|
| [`skills/interview-repo-safety/SKILL.md`](../skills/interview-repo-safety/SKILL.md) | Agent procedure |
| [`skills/interview-repo-safety/README.md`](../skills/interview-repo-safety/README.md) | How to invoke the gate |
| [`../README.md`](../README.md) | How to install the plugin |
| [`skills/interview-repo-safety/reference/`](../skills/interview-repo-safety/reference/) | Agent working set (not this essay) |

The skill does not prove a repository is safe. This document does not prove a prompt was converted perfectly. Both are procedures you can inspect and extend.
