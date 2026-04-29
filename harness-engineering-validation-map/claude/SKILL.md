---
name: harness-engineering-validation-map
description: Inspect a repository and create or update the smallest useful `docs/validation-guide.md`, mapping change types to real proof commands without inventing tools or imposing a broader docs taxonomy.
---

# harness-engineering-validation-map

Create or update a compact validation guide for a repo. The output is a practical map agents can use to choose the strongest relevant proof before claiming work is done.

This skill is for validation discovery only. It does not refactor the repo, add test infrastructure by default, or create a large documentation system.

## What this skill owns

- Inspect existing repo instructions and validation surfaces.
- Create or update `docs/validation-guide.md` with change-type-to-proof guidance.
- Add a short `CLAUDE.md` / `AGENTS.md` pointer when it helps agents find the guide.

## What this skill does not own

- Inventing commands, tools, or services that do not exist.
- Forcing a harness docs taxonomy onto a repo.
- Moving subtree-specific validation into a repo-wide guide when it belongs near the subtree.
- Writing broad new tests or scripts unless the user separately asks for that work.

## Workflow

### Step 1: Read the substrate

Before editing, inspect only the relevant validation sources:

1. Run `pwd`.
2. Read root `CLAUDE.md`, `AGENTS.md`, and nested `CLAUDE.md` / `AGENTS.md` files if present.
3. Read `README.md`, `ARCHITECTURE.md`, and existing docs that mention test, lint, build, check, smoke, e2e, CI, deploy, or validation.
4. Inspect package scripts, Makefiles, CI workflows, test configs, lint configs, typecheck configs, Docker or compose files, and framework config.
5. If `docs/validation-guide.md` already exists, read it before deciding what to change.

Use `rg` first. Do not scan unrelated generated output or dependency directories.

### Step 2: Identify real proof by change type

Map only commands and tools that exist in the repo. Typical change types:

- docs or instructions
- UI behavior
- visual or responsive UI
- API or service behavior
- database schema, migration, or query
- infrastructure or deployment config
- refactor with no intended behavior change
- tests, scripts, or developer tooling

For each relevant type, identify:

- required proof: commands, browser checks, smoke tests, screenshots, migrations, or review steps that must run
- fallback proof: what is acceptable when the strongest proof is blocked
- blocker standard: what counts as a concrete blocker rather than skipped validation
- source: the file or config that proves the command exists

If a change type has no discoverable validation, say that plainly. Do not fill the gap with guesses.

### Step 3: Write the smallest useful guide

Create or update `docs/validation-guide.md` using concise sections:

```markdown
# Validation Guide

Use this guide to choose proof by change type. Prefer the strongest relevant check that exists in this repo. If a required check cannot run, record the concrete blocker and the weaker proof used instead.

## General Rules

- <repo-wide validation rule>

## Change Types

### <Change type>

- Required proof: `<command>` or <tool/action>
- Also check: <secondary proof, if any>
- If blocked: <acceptable fallback and what to record>
- Source: `<path>`
```

Keep the guide short enough that agents will actually read it. Link to existing local docs instead of duplicating long instructions.

### Step 4: Add a `CLAUDE.md` / `AGENTS.md` pointer when useful

If a root `CLAUDE.md` or `AGENTS.md` exists and does not mention the guide, add one short pointer in the validation, commands, or working rules section. Do not turn the root instructions file into a validation manual.

If validation is subtree-specific, prefer a nested instructions pointer or local docs instead of a root pointer.

### Step 5: Validate the result

After editing:

- confirm every command named in `docs/validation-guide.md` exists in package scripts, Makefiles, CI, or docs
- confirm every pointer in `CLAUDE.md` / `AGENTS.md` exists
- confirm the guide does not require tools that are not configured
- confirm existing repo structure was preserved

## Report back

Report:

- files changed
- commands or configs used as sources
- change types covered
- known validation gaps left explicit
- any `CLAUDE.md` / `AGENTS.md` pointer added or skipped

## Guardrails

- Keep the guide concise and grounded.
- Do not invent commands.
- Do not require browser, database, cloud, or CI tools unless the repo already has them.
- Do not force validation for every imaginable change type; cover the types this repo actually supports.
- Do not use the root instructions file as a memory dump.
