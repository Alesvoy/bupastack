---
name: harness-engineering-project-bootstrap
description: 'Scaffold the minimum agent-first project surface for a greenfield repo or light retrofit: create `AGENTS.md`, `ARCHITECTURE.md`, `docs/exec-plans/active/`, `docs/exec-plans/completed/`, supporting docs folders, `INBOX.md` if missing, and a minimal domain-first layout when it is safe to do so. Use when starting a new project or lightly retrofitting a repo for harness-engineering workflows. Refuses broad source-tree refactors and routes those to `$harness-engineering-plan`.'
---

# harness-engineering-project-bootstrap

Scaffold the minimum repository surface needed for the harness-engineering workflow described in the OpenAI harness article and your local wiki. This skill is for **greenfield setup and light retrofits** only.

It creates missing structure. It does not kick off a broad refactor.

## What this skill owns

- Create `AGENTS.md` if missing.
- Create `ARCHITECTURE.md` if missing.
- Create `docs/exec-plans/active/` and `docs/exec-plans/completed/`.
- Create a minimal `docs/validation-guide.md` only when obvious validation commands already exist.
- Create supporting docs folders used by the agent-first map: `docs/design-docs/`, `docs/product-specs/`, `docs/references/`, `docs/generated/`.
- Create `INBOX.md` **only if it does not exist**, using the same template contract as `$harness-engineering-track-task`.
- Create a minimal domain-first layout only when that is safe and additive.

## What this skill does not own

- Rewriting or replacing an existing `AGENTS.md` or `ARCHITECTURE.md`.
- Converting a nontrivial existing source tree to domain-first layering.
- Performing a migration, architecture rewrite, or package move across a mature repo.
- Managing `CLAUDE.md`. Another skill already owns the shim from `CLAUDE.md` to `AGENTS.md`.

If the repo needs a real retrofit rather than additive scaffolding, stop and route the work to `$harness-engineering-plan`.

## Workflow

### Step 1: Read the room

Before writing anything:

1. Run `pwd`.
2. Inspect the repo root for:
   - `AGENTS.md`
   - `ARCHITECTURE.md`
   - `INBOX.md`
   - `docs/`
   - likely app roots such as `src/`, `app/`, `lib/`, `server/`, or a Python package root
3. Detect the likely stack:
   - `package.json`, `tsconfig*.json`, `jsconfig.json` -> `js-ts`
   - `pyproject.toml`, `setup.py`, `requirements.txt` -> `python`
   - otherwise -> `generic`
4. Look for obvious validation commands in package scripts, Makefiles, CI config, test config, or existing docs.

### Step 2: Classify the repo state

Choose one:

- **Greenfield** — little or no existing app source. Safe to scaffold the full surface, including the domain-first layout.
- **Light retrofit** — existing repo, but additive scaffolding is safe. Create missing docs and folders; only create the domain-first layout if it is clearly additive and not misleading.
- **Major retrofit** — the repo already has a nontrivial source tree and adopting the domain-first layout would require broad file moves, import-graph changes, or architectural rewriting.

If the repo is a **major retrofit**, do **not** kick off the refactor. Create only the clearly safe missing files if appropriate, then tell the user the structural retrofit should go through `$harness-engineering-plan`.

### Step 3: Pick the app root

Use this order:

- If the repo already has a clear app root, use it.
- For `js-ts`, default to `src/`.
- For `python`, prefer an existing package root under `src/<package>/` or `<package>/`. If none is obvious, default to `src/`.
- For `generic`, default to `src/`.

Ask once only if the app root is ambiguous and writing to the wrong location would be risky.

### Step 4: Scaffold only missing pieces

Use the bootstrap script for the actual write:

- [scripts/bootstrap_harness_project.py](/Users/alesvoy/.agents/skills/harness-engineering-project-bootstrap/scripts/bootstrap_harness_project.py)

The script must:

- create missing files only
- preserve existing files
- create `INBOX.md` only if missing, using the same template as `$harness-engineering-track-task`
- create a small `docs/validation-guide.md` only when validation commands are obvious from existing root `Makefile` targets, root/app/package `package.json` scripts, or obvious Python test config/files
- create the minimal docs folders
- create the minimal domain layout only when safe

Do not manually rewrite existing docs to “improve” them during bootstrap. Missing is fine; conflicting is not.

Validation guide rule:

- If obvious commands exist, the guide should be minimal: change type, command or tool, and what proof it provides.
- If validation is unclear or the bootstrap script skips the guide, report that `$harness-engineering-validation-map` should be run later.
- Do not force a large validation guide or a broader docs taxonomy during bootstrap.

### Step 5: Report what happened

Report:

- stack
- app root
- files created
- files preserved
- whether `docs/validation-guide.md` was created, preserved, or skipped
- whether the domain-first layout was created or skipped
- whether the repo should now route any broader structural work to `$harness-engineering-plan`

## Output contract

When bootstrap succeeds, the repo should have, at minimum:

- `AGENTS.md` or an explicit note that an existing one was preserved
- `ARCHITECTURE.md` or an explicit note that an existing one was preserved
- `docs/exec-plans/active/`
- `docs/exec-plans/completed/`
- `INBOX.md` if it did not already exist
- `docs/validation-guide.md` only when obvious validation commands were available

When the repo is too mature for safe structural scaffolding, the output should explicitly say:

`Domain-first layout not scaffolded automatically; route the retrofit to $harness-engineering-plan.`

## Guardrails

- Never overwrite an existing `AGENTS.md`, `ARCHITECTURE.md`, or `INBOX.md`.
- Never perform broad file moves or import rewrites from this skill.
- Never create a fake domain template folder just to satisfy the architecture doc.
- Never invent validation commands or tools that are not present in the repo.
- Never force `docs/validation-guide.md` when validation is unclear; recommend `$harness-engineering-validation-map` instead.
- Do not create `CLAUDE.md` here.
- If the repo needs a real architecture migration, say so plainly and route it to `$harness-engineering-plan`.

## Why this matters

The harness article’s lesson is to give agents a map, not a 1,000-page manual. This skill creates the map and the minimum filesystem shape that later skills can rely on. It is intentionally narrow: scaffold the environment, then let the planning and execution skills take over.
