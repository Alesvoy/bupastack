---
name: harness-engineering-plan
description: Produces a Lopopolo-style ExecPlan for work that needs a durable, multi-session artifact. First decides whether the ask should stay a conversational task brief or become an ExecPlan, then auto-triages plan-sized work as ticket / sprint / epic and writes it under `docs/exec-plans/active/`, following the OpenAI Codex ExecPlan template from https://developers.openai.com/cookbook/articles/codex_exec_plans. Use this whenever the user hands you a raw ask and wants it turned into something agents can execute, with phrases like "let's plan this", "write up this work", "plan this feature", "let's scope this bug", or `$harness-engineering-plan`, or whenever a repo that is ready for an execution plan is handed a multi-step ask. Replaces `$spec-planner` for harness-engineering workflows where humans steer and agents execute. Does NOT produce PRD-style prose, user stories, or vibe-coding expansions; the plan is a context-management artifact sized to the work, not a product spec.
---

# harness-engineering-plan

You are producing an **ExecPlan**: a context-management artifact that a human-steered, agent-executed loop can act on across sessions. The template comes from OpenAI's Codex ExecPlans cookbook at `https://developers.openai.com/cookbook/articles/codex_exec_plans`, adapted so the `Progress` section points at a sibling JSON file tracked by the harness.

This skill is the entry point. Your job is to:

1. **Decide whether the ask needs a durable artifact.** If not, keep it as a conversational task brief.
2. **If it needs a plan, auto-triage the plan-sized work** into one of three sizes: ticket, sprint, or epic.
3. **Produce output sized to the work**: a task brief for brief-sized work, a full ExecPlan for plan-sized work.
4. **Hand off correctly**: every ExecPlan, including ticket-sized ExecPlans, hands off to `$harness-engineering-plan-init` to scaffold the progress JSON. Brief-sized work does not.

You are not writing a PRD. You are not expanding scope ambitiously. You are not doing SDD-style interview flows. The ExecPlan's job is to be legible to agents and to survive across sessions. Nothing more.

## Core philosophy

From Ryan Lopopolo's *Harness engineering: leveraging Codex in an agent-first world*:

> "Humans steer. Agents execute."
> "From the agent's point of view, anything it can't access in-context while running effectively doesn't exist."
> "Give Codex a map, not a 1,000-page instruction manual."
> "In a system where agent throughput far exceeds human attention, corrections are cheap, and waiting is expensive."

Three operating implications:

- **The plan is a context-management tool**, not documentation. It earns its cost only when the work genuinely needs durable cross-session state. If the ask likely fits one focused session, write a task brief, not a plan file.
- **Ground truth is first-class.** If the ask references a design folder, existing code, a spec doc, a Figma URL, or any prior artifact, inventory it and cite file paths and lines. What is not in the plan is invisible to the agent.
- **Invariants over implementations.** The plan describes what must be true and how it will be verified. It does not prescribe the code path. That is the implementor's call.

## Workflow

### Step 1: Read the room

Before anything, establish context:

1. Run `pwd` to confirm where you are.
2. Look for signals:
   - `docs/exec-plans/active/`: if it exists and has files, is this a new plan or an extension?
   - `AGENTS.md`, `README.md`, `docs/`: the repo's map.
   - `INBOX.md`: if it exists, treat it as capture / intake context only, not as execution truth.
   - Any path, URL, or file the user referenced in the ask.
3. If there is already an active ExecPlan for this work, stop and ask: is this an extension of the existing plan, or a new plan with a different objective? Do not silently create duplicates.

### Step 2: Decide whether this needs a durable artifact, then size it

The first decision is **task brief vs. ExecPlan**. This decision is primary. The size label comes second.

Use a **task brief** when most of these are true:

- The work is likely finishable in one focused session.
- No `init` / `resume` / `checkpoint` loop is needed.
- No living `Decision Log` or `Surprises & Discoveries` section is likely to matter.
- The work has at most 1-2 observable changes.
- Blocker risk is low and external dependencies are unlikely.

Use an **ExecPlan** when any of these are true:

- The work is likely to span multiple agent sessions.
- The work needs durable state for checkpointing, resumability, or handoff.
- The work is a significant refactor, migration, or architectural change.
- The work has meaningful unknowns, likely discoveries, or likely changes of course.
- The work depends on client feedback, credentials, provisioning, or other external blockers.
- The work benefits from explicit milestones and a durable acceptance rubric.

Only ask the user if two signals strongly conflict. Ask one question, phrased as your current read. Example: "I'm reading this as a sprint, roughly six items across auth and billing. Say so if it's actually bigger or smaller."

If the work should stay a task brief, skip to Step 5. Do not write a plan file.

If the work needs an ExecPlan, classify the **plan-sized work** into **ticket**, **sprint**, or **epic**:

- **Ticket** — compact plan-sized work. Usually one milestone and a small number of items, but still worth durable state because it is likely multi-session, higher-risk, or blocker-prone.
- **Sprint** — medium plan-sized work. Usually 1-3 milestones and roughly 3-15 items.
- **Epic** — large or multi-phase plan-sized work. Usually 3-8 milestones, 20 or more items, or meaningful dependency / blocker management.

Use these signals to choose the size label:

- **Verb shape.** `fix`, `update`, `tweak`, `rename`, `adjust` lean ticket. `port`, `add`, `implement`, `build` lean sprint. `migrate`, `rearchitect`, `launch`, `build the whole X` lean epic.
- **Ground-truth footprint.** One referenced file or small cluster usually means ticket. Several related areas usually means sprint. Multi-file design bundles, multiple subsystems, or broad existing-app changes usually mean epic.
- **Repo state.** Empty `docs/exec-plans/active/` on greenfield work leans sprint or epic. An existing harness already in flight may mean the ask is a ticket inside the broader body of work instead.
- **Estimated item count.** A handful of items leans ticket. Roughly 3-15 items leans sprint. Roughly 20 or more leans epic.
- **Risk of blockers or external dependencies.** If the work plausibly depends on unresolved client feedback, teammate input, credentials, or provisioning, treat it as epic even if the surface area looks smaller, because the plan becomes the durable blocker record.

### Step 3: Inventory the ground truth

For plan-sized work, for every referenced artifact:

1. Open it and inspect it. Do not summarize from the prompt.
2. Build a pointer catalog: file paths, key symbols, routes, components, endpoints, interactions, copy, breakpoints, whatever actually matters.
3. Cite file paths and lines for every concrete claim the plan makes. If you cannot cite it, do not claim it.

For design handoffs:

- Every page or route in the handoff becomes a Context entry.
- Every interaction in the design source becomes a concrete acceptance criterion.
- Every copy string, image reference, and breakpoint becomes a citation.

For bugs or refactors:

- Every file involved in the failure mode becomes a Context entry.
- Reproduction steps become the first acceptance criterion.
- Existing tests or invariants that must keep passing become explicit constraints.

If the ask has no ground truth and you cannot gather any, name that explicitly in `Context and Orientation` as: `No prior artifacts; plan derived from the ask alone.` Do not invent pointers.

### Step 4: Draft the ExecPlan

Write to `docs/exec-plans/active/<slug>.md`. Use a short kebab-case slug such as `denader-homepage-port` or `fix-checkout-tax-calc`.

Before you write, keep the section rules straight:

- **Mandatory per the OpenAI cookbook:** `Purpose / Big Picture`, `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective`.
- **Harness-required in this workflow:** `Context and Orientation`, `Plan of Work`, and `Validation and Acceptance`.
- **Conditional:** `Concrete Steps`, `Idempotence and Recovery`, `Artifacts and Notes`, and `Interfaces and Dependencies`. Include these only when they materially help the work.

Do not omit a mandatory section. Do not pad conditional sections just to look thorough.

Use this shape:

```markdown
# <Short, action-oriented title>

This ExecPlan is a living document. Revise `Progress`, `Surprises & Discoveries`, and `Decision Log` as work proceeds. When changing course, log it in `Decision Log` with date and rationale, and append a revision note at the bottom.

## Purpose / Big Picture

<2-4 sentences: what this plan delivers and why it is needed. Name the user-visible outcome, not the implementation. If there is a stakeholder, name them.>

## Progress

Progress is tracked in the sibling JSON file **`<slug>.progress.json`** (created by `$harness-engineering-plan-init`). That file is the authoritative item list with timestamps, grouped by milestone. This section holds a rolling summary only.

**Summary (updated at each checkpoint):**
- M1 - <title>: 0/N done
- M2 - <title>: 0/N done

## Surprises & Discoveries

<Append-only log of things discovered during execution that were not known at plan time. Each entry dated and brief.>

- (empty at plan creation; agents append as they discover)

## Decision Log

<Every course change: what changed, why, date, author. Mandatory; do not omit.>

- [YYYY-MM-DD, plan-author] Plan created. Triage: ticket, sprint, or epic. Ground truth: <where the truth lives>.

## Outcomes & Retrospective

<Filled in when the plan moves to `docs/exec-plans/completed/`. What shipped, what was learned, what would you do differently. Mandatory section.>

- (empty until completion)

## Context and Orientation

<Pointer catalog for the agent. Cite file paths and lines for every reference. This is the map the agent uses; anything not here is invisible.>

- **Ground-truth artifact:** <path or URL>
- **Existing code to extend:** `<path>:<line>` - <what lives here>
- **Key architectural constraint:** <e.g. must use existing provider from a specific file>
- **Copy / content source:** <path or URL>
- **Breakpoints / viewports:** <list if UI work>

## Plan of Work

<Milestone-level narrative. Each milestone is a paragraph describing scope, outcome, and proof. Each milestone must be independently verifiable.>

### M1 - <title>

<paragraph: goal, work, result, proof>

### M2 - <title>

<paragraph>

## Concrete Steps

<Optional but recommended for epics. Detailed human-readable steps inside each milestone. Checkbox tracking lives in the JSON, not here.>

### M1 - <title>
- <step>
- <step>

### M2 - <title>
- <step>

## Validation and Acceptance

<Observable acceptance criteria per milestone. Prefer Given-When-Then for user-visible behavior. These are the grading rubric the validator will use. Cite file paths and lines where relevant so the validator knows what to exercise.>

### M1
- **Given** <initial state> **when** <action> **then** <observable result>
- <criterion>

### M2
- **Given** <...> **when** <...> **then** <...>

## Idempotence and Recovery

<Optional: how to pick up safely if a session is interrupted mid-milestone. Important for migrations, data backfills, or long-running tasks.>

## Artifacts and Notes

<Optional: links to related docs, commits, decisions. Grows over the plan's life.>

## Interfaces and Dependencies

<Optional but important when non-obvious: external systems touched, teammates or clients whose input is needed, credentials required, services that must be provisioned.>
```

Sizing guidance:

- **Ticket:** usually 1 milestone and a small number of JSON items, but still worth a durable artifact.
- **Sprint:** 1-3 milestones, usually 3-15 JSON items total.
- **Epic:** 3-8 milestones, usually 20 or more JSON items total.

Do not put checkbox items in the plan file. The plan describes milestones narratively. The JSON tracks completion atomically.

### Step 5: If Step 2 chose a task brief, emit it in the conversation

For brief-sized work, do not create `docs/exec-plans/`. Do not call `$harness-engineering-plan-init`. Instead emit a task brief in the conversation. Write it the way you would describe a well-scoped GitHub issue: concrete, pointer-rich, and outcome-focused.

```markdown
## Task brief (brief-sized - no plan file)

**Objective:** <one sentence>

**Context pointers:**
- `<path>:<line>` - <what is here>

**Constraints:**
- <architectural invariant, style rule, or prior convention to respect - cite source>
- (or "none noted")

**Done when:**
1. <observable>
2. <observable>

**Suggested dispatch:** `implementor` with the above. No validator or code-reviewer loop unless the user opts in; brief-sized work usually does not justify the full resume loop.
```

Do not dispatch `implementor` yourself from this skill. Let the user decide.

### Step 6: Hand off for plan-sized work

After writing the plan file:

1. Tell the user the plan path, the triage decision, the milestone count, and the estimated item count.
2. Propose the next step: run `$harness-engineering-plan-init <slug>` to scaffold the progress JSON and optional baseline commit.
3. Do not create the JSON yourself. That separation keeps each skill focused on one job.

This handoff applies to every ExecPlan size: ticket, sprint, and epic. A ticket-sized ExecPlan usually becomes one milestone with one or a few progress JSON items.

## Hard guardrails

You do not write product code in this skill. Planning only.

You do not expand scope beyond the user's ask. If you notice adjacent work that would be nice to have, record it in `Surprises & Discoveries` as a note. Do not add it to `Plan of Work`.

You do not ask the user a battery of clarifying questions. Ask once only when the triage genuinely conflicts or a referenced artifact is missing.

You do not skip `Decision Log` or `Outcomes & Retrospective`. Seed them as empty if needed; do not omit them.

You do not invent ground truth. Every citation must come from something you actually read this session.

## When not to use this skill

- Extending an existing active plan that already covers the work. Amend that plan instead of creating a duplicate.
- Raw capture or parking-lot items. Route those to `$harness-engineering-track-task`, not to an ExecPlan.
- Pure orientation or research. Answer the question instead of planning.
- One-off shell work. Just do it.
- When the user explicitly says "just do it". Respect that.

## Why this matters

The default failure mode of planning skills is over-ceremony: a heavyweight PRD for every ask, regardless of whether the work needs one. That tax compounds across every session. The only planning that earns its cost is planning sized to the work. For brief-sized work, a task brief is enough. For plan-sized work, choose the smallest durable shape that keeps the work legible to future sessions: ticket, sprint, or epic. Nothing more.
