---
name: harness-engineering-agents-md-retrofit
description: Retrofit an existing root `AGENTS.md` (and/or `CLAUDE.md`) into a concise repo map plus repo-wide expectations, moving deeper material into `ARCHITECTURE.md`, `docs/`, or nested `AGENTS.md` / `CLAUDE.md`. Use when a repo already has agent-instruction files and they are too long, stale, or mixing global guidance with area-specific rules. Route broad docs migrations to `/harness-engineering-plan`; do not use for greenfield bootstrap.
---

# harness-engineering-agents-md-retrofit

Convert an existing `AGENTS.md` (and/or Claude Code's `CLAUDE.md`) from a monolithic manual into a short repo entry point. Keep repo-wide, high-signal guidance at the root and move detailed or local material closer to the source of truth.

Read [references/openai-agents-md-guidance.md](/Users/alesvoy/.claude/skills/harness-engineering-agents-md-retrofit/references/openai-agents-md-guidance.md) when you need the rationale behind the TOC shape, need to decide whether something belongs at the root or in a nested instructions file, or need the exact verification commands.

## What this skill owns

- Audit the existing root `AGENTS.md` and / or `CLAUDE.md` and classify each section.
- Rewrite the root file into a TOC / repo-map shape.
- Move deep architecture and reference material into `ARCHITECTURE.md` and `docs/` when that move is safe and grounded.
- Move repo-wide validation instructions into `docs/validation-guide.md` when that creates a clearer source of truth.
- Create nested `AGENTS.md` / `CLAUDE.md` where a subdirectory needs local rules.
- Validate that pointers and instruction layering still make sense after the rewrite.

## What this skill does not own

- Greenfield scaffolding. Use `/harness-engineering-project-bootstrap`.
- Broad knowledge-base creation or large documentation migrations. Use `/harness-engineering-plan`.
- Inventing architecture, workflow, or product rules that are not supported by the repository.

## Root-file target shape

Root `CLAUDE.md` (and `AGENTS.md` if also present) should usually stay around 60-120 lines and cover only:

- `Start Here`: where agents orient first.
- `Repo Map`: high-value pointers to `ARCHITECTURE.md`, `docs/`, code roots, and other durable sources of truth.
- `Working Rules`: a short list of repo-wide rules that matter on most tasks.
- `Commands`: dev, test, lint, typecheck, or build commands when known.
- `Validation`: a short pointer to `docs/validation-guide.md` when repo-wide validation rules live there.
- `Planning Rule`: when to use ExecPlans, `PLANS.md`, or the local planning harness.

If a section needs more than a few bullets, it probably belongs elsewhere.

## Classification rules

Keep content at the root only when most of these are true:

- The instruction is repo-wide.
- The instruction is stable across many tasks.
- The instruction is high-signal on most runs.
- The instruction is not obvious from code alone.
- The instruction is short enough to keep the root file lean.

Move content to `ARCHITECTURE.md` when it describes layering, dependency direction, invariants, or integration boundaries.

Move repo-wide validation instructions to `docs/validation-guide.md` when they apply across the repository. Keep only a short root pointer such as "Use `docs/validation-guide.md` to choose validation by change type."

Move content to `docs/design-docs/`, `docs/product-specs/`, `docs/references/`, or `docs/generated/` when it is deeper reference material, product behavior, vendor docs, schemas, or generated artifacts.

Move content to nested `AGENTS.md` or `CLAUDE.md` when the rule only applies to a subtree, service, team, or workflow. Subtree-specific validation stays in nested instructions or local docs instead of being generalized into the repo-wide validation guide. Prefer one instructions file per directory.

Drop or flag content when it is stale, duplicated, unverifiable, or conflicts with better-grounded repository artifacts.

## Workflow

### Step 1: Read the current substrate

Before editing:

1. Run `pwd`.
2. Inspect the repo root for:
   - `CLAUDE.md`
   - `AGENTS.md`
   - `ARCHITECTURE.md`
   - `docs/`
   - existing nested `CLAUDE.md` / `AGENTS.md`
   - likely app roots
3. Read the current `CLAUDE.md` and `AGENTS.md` in full.
4. Read the docs and reference files they already point to.
5. If the repo already uses an ExecPlan harness, read `docs/exec-plans/active/` only enough to avoid contradicting it.

### Step 2: Inventory and classify the existing root file

Build a compact classification table for each meaningful block in the current root instructions file:

- keep at root
- move to top-level doc
- move to nested instructions file
- drop or flag

Do not rewrite until you know where each section will land.

### Step 3: Decide whether this is a safe retrofit

Proceed only when the rewrite is additive and bounded:

- safe: shorten the root file, move grounded content, create a small number of missing target docs or nested instruction files
- not safe: the repo has no durable docs surface, most instructions are tacit, or the retrofit would create a large new system of record from scratch

If it is not safe, stop and route the work to `/harness-engineering-plan`.

### Step 4: Rewrite the root file

Rewrite it as a short map plus repo-wide expectations.

Keep only:

- repo-wide naming, workflow, or validation rules
- key commands
- short pointers to `docs/validation-guide.md` when validation details moved there
- planning handoff rules
- high-value pointers to durable docs

Do not duplicate long architecture or product rules at the root. Point to the deeper file instead.

### Step 5: Relocate deeper material

Use these defaults:

- architecture / layers / boundaries -> `ARCHITECTURE.md`
- repo-wide validation instructions -> `docs/validation-guide.md`
- design rationale / UX decisions -> `docs/design-docs/`
- product behavior / feature intent / copy -> `docs/product-specs/`
- vendor docs / schemas / operational references -> `docs/references/`
- generated inventories / schemas / reports -> `docs/generated/`
- subtree-specific coding or operational rules -> `<subdir>/CLAUDE.md` or `<subdir>/AGENTS.md`
- subtree-specific validation commands -> nested instructions or local docs near that subtree

Create missing target files only when:

- the content is already grounded in the repo or the current root file
- the target file has a clear owner and purpose
- the file can be created without inventing broad new doctrine

### Step 6: Validate the result

After rewriting:

- every pointer in the root file must exist
- no critical repo-wide rule should exist only in a deep subtree
- no subsystem-specific rule should remain at the root if it can live closer to the code
- verify file placement and nested-instruction precedence manually

### Step 7: Report back

Report:

- files changed
- what stayed at root
- what moved and where
- any dropped or flagged stale instructions
- whether broader repository documentation should be planned next

## Guardrails

- Never turn the root instructions file into the encyclopedia again.
- Never invent project truths to fill empty docs.
- Never create a large docs taxonomy just to satisfy the pattern.
- Never move subtree-specific validation into a repo-wide guide just to centralize it.
- Never keep the same rule in root and nested instructions unless duplication is intentional and clearly justified.
- Never leave broken pointers in the root file.
- Prefer editing existing source-of-truth docs over creating redundant new ones.
- When an existing `CLAUDE.md` / `AGENTS.md` is already short and layered correctly, make only the minimal improvements needed.
