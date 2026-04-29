---
name: harness-engineering-failure-retro
description: Turn an agent failure into the smallest durable repo improvement by classifying the failure and routing the correction to docs, validation, tests, planning artifacts, inbox capture, or a focused skill.
---

# harness-engineering-failure-retro

Use this skill after an agent failure, bad handoff, missed validation, repeated mistake, or confusing task outcome. The goal is not to write a postmortem for its own sake. The goal is to prevent the same failure with the smallest durable correction.

## What this skill owns

- Classify the failure.
- Decide whether any durable repo change is warranted.
- Write or recommend the smallest correction in the right place.

## What this skill does not own

- Turning root `AGENTS.md` into a memory dump.
- Creating broad new process for a one-off issue.
- Rewriting architecture or tests unless the failure proves that is the right fix.
- Blaming an agent instead of improving the operating surface.

## Failure classes

Classify the failure before editing:

- **Missing context**: the agent could not find or was not given needed repo facts.
- **Weak validation**: the agent claimed completion without the strongest relevant proof.
- **Architecture drift**: the change violated layering, dependency direction, or ownership rules.
- **Task too vague**: acceptance criteria or scope were ambiguous.
- **Repeated workflow**: the same operational steps are being rediscovered across tasks.
- **One-off issue**: unlikely to recur, not worth durable docs or tooling.

If more than one applies, choose the primary class and mention the secondary one in the report.

## Routing rules

Pick the smallest useful destination:

- Missing context -> `AGENTS.md` pointer, `ARCHITECTURE.md`, existing docs, or a nested `AGENTS.md` near the affected subtree.
- Weak validation -> `docs/validation-guide.md`, a test/check/lint/script if the missing proof should be automated, or tighter ExecPlan acceptance criteria.
- Architecture drift -> `ARCHITECTURE.md`, nested instructions, or a focused code check if one already fits the repo.
- Task too vague -> update the ExecPlan acceptance criteria or record a checkpoint note; for unplanned work, ask for a sharper task brief next time.
- Repeated workflow -> focused skill only if the workflow is stable, frequent, and not repo-specific enough for docs.
- One-off issue -> checkpoint note or `INBOX.md` entry if it still matters; otherwise no durable change.

Do not always write docs. A missing assertion belongs in a test. A missing command belongs in a script or validation guide. A vague plan belongs in the plan. A future idea belongs in `INBOX.md`.

## Workflow

### Step 1: Reconstruct the failure

Read the minimum evidence needed:

- the user report or failed validator/reviewer finding
- changed files or diff, if relevant
- `AGENTS.md`, nested instructions, `ARCHITECTURE.md`, `docs/validation-guide.md`, and active ExecPlan acceptance criteria when they apply
- logs, test output, screenshots, or command output when available

State the failure in one sentence: expected behavior, actual behavior, and where the agent got misled.

### Step 2: Choose a durable correction

Use the routing rules to choose one correction. Prefer updating an existing source of truth over creating a new file.

Good corrections are small:

- add one validation-guide row for a skipped proof
- add one root `AGENTS.md` pointer to an existing doc
- add one nested instruction for a subtree-specific rule
- tighten one ExecPlan acceptance criterion
- add or adjust one existing test/check/script
- append one `INBOX.md` item for future nonblocking work

Bad corrections are broad:

- dumping incident history into root `AGENTS.md`
- creating a new taxonomy for a single failure
- adding a skill for a rare, repo-specific mistake
- documenting behavior that should be enforced by tests

### Step 3: Edit only if the fix is clear

If the smallest correction is obvious and grounded, make it. If not, report the classification and recommend the next action without editing.

When editing:

- preserve existing tone and structure
- keep changes close to the source of truth
- do not remove existing guardrails
- do not touch product code unless the user explicitly asked this retro to include the fix

### Step 4: Report back

Report:

- failure class
- root cause in one sentence
- files changed, or "none"
- why this destination was chosen
- what future agents should do differently
- any larger follow-up that belongs in `INBOX.md` or an ExecPlan

## Guardrails

- Smallest durable correction wins.
- Do not use root `AGENTS.md` as a scratchpad.
- Do not turn one-off failures into permanent process.
- Do not invent validation tools.
- Prefer enforceable checks over prose when the repo already supports them.
