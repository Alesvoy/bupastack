# OpenAI AGENTS.md guidance

Use this reference when deciding what belongs in the root `AGENTS.md`, what should move into `docs/`, and what should live in nested instructions files.

## Why the root file should stay short

OpenAI's harness article says the failure mode is "one big `AGENTS.md`". Their reasons are:

- a large root file crowds out task context, code, and relevant docs
- when everything is important, the agent stops navigating intentionally
- monolithic instruction files rot quickly
- a single prose blob is hard to verify mechanically

Their documented replacement is a short root `AGENTS.md`, roughly 100 lines, that acts as a map into a structured repository knowledge base.

## What OpenAI says belongs in AGENTS.md

OpenAI's Codex guidance says `AGENTS.md` should provide persistent context that the code alone does not reliably convey. Good candidates include:

- naming conventions
- business logic and workflow expectations
- known quirks
- dependencies or operational constraints the agent cannot infer from the code alone

This supports keeping a small number of high-value repo-wide rules at the root even when the root file is mostly a table of contents.

## Root versus nested placement

OpenAI's Codex docs recommend a layered instruction chain:

- `~/.codex/AGENTS.md` for reusable personal defaults
- repo-root `AGENTS.md` for basic setup and repository expectations
- nested `AGENTS.md` or `AGENTS.override.md` files close to specialized work

Two operational consequences matter for this skill:

- Codex stops searching once it reaches the current working directory, so local instructions should sit as close to the specialized code as possible.
- Codex enforces a combined instruction-size limit, `project_doc_max_bytes`, which defaults to 32 KiB. Splitting guidance across nested directories is part of the intended design.

If both `AGENTS.md` and `AGENTS.override.md` exist in the same directory, Codex uses the override file for that directory.

## Planning guidance

OpenAI's ExecPlans cookbook shows one specific kind of root guidance that belongs in `AGENTS.md`: a brief rule that tells Codex when to use a separate planning document such as `PLANS.md` or an ExecPlan. The planning process belongs in the dedicated plan file, not in the root instructions file.

## Retrofit heuristics

When auditing an existing root `AGENTS.md`, prefer these moves:

- keep at root: short repo-wide rules, commands, and pointers to source-of-truth docs
- move to `ARCHITECTURE.md`: layering, dependency direction, invariants, integration boundaries
- move to `docs/`: product, design, reference, vendor, or generated material
- move to nested instructions: rules that only apply to one subtree or one team
- drop or flag: stale, duplicated, unverifiable, or contradictory material

## Codex verification commands

When `codex` is available, OpenAI recommends using these checks after reorganizing instruction files:

```bash
codex --ask-for-approval never "Summarize the current instructions."
codex --cd <subdir> --ask-for-approval never "List the instruction sources you loaded."
```

Expected result:

- the root command reflects global plus repository guidance
- the subdirectory command reflects the root file plus the nearest nested instructions file in precedence order

## Source basis

This reference is distilled from these official OpenAI sources:

- Codex docs: `Custom instructions with AGENTS.md`
- OpenAI business guide: `How OpenAI uses Codex`
- OpenAI blog: `Harness engineering: leveraging Codex in an agent-first world`
- OpenAI cookbook: `Using PLANS.md for multi-hour problem solving`
- OpenAI cookbook: `Codex Prompting Guide`
