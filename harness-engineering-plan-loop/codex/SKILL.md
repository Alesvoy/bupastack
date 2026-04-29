---
name: harness-engineering-plan-loop
description: Autonomously loop through an already initialized harness-engineering ExecPlan under `docs/exec-plans/active/`, repeatedly running the `$harness-engineering-plan-resume` agent implementation/validation flow for the next unfinished item, then `$harness-engineering-plan-checkpoint` and a clean commit after each verified subtask. Use when the user asks to loop through a plan, continue all remaining ExecPlan items, run the plan item-by-item, or proceed without stopping for routine per-item confirmations. Stop for final plan completion before flipping the final item complete, human verification gates, deployment/release steps, destructive or high-impact assumptions, or discoveries that break the plan.
---

# harness-engineering-plan-loop

## Overview

Run an initialized harness-engineering ExecPlan as an autonomous item loop. This skill wraps the existing resume and checkpoint contracts, changing only the confirmation model: the user's request to loop is advance approval to choose the next ordinary item, implement it through agents, verify it, checkpoint it, commit it, and continue.

This skill is for already initialized plans only. It must never create, reorder, rewrite, or expand plan items.

## Required Inputs

- Active plan markdown: `docs/exec-plans/active/<slug>.md`
- Active progress file: `docs/exec-plans/active/<slug>.progress.json`
- A git repository unless the user explicitly accepts no commits
- Usable `implementor` and `validator` subagents, plus `code-reviewer` if review is requested

If multiple active plans exist and the user did not pass a slug, ask which plan to loop. If no initialized plan exists, stop and point them to `$harness-engineering-plan` and `$harness-engineering-plan-init`.

## Autonomy Contract

Treat the invocation of this skill as advance confirmation for routine loop decisions:

- Select the first unfinished item in progress JSON order.
- Use the plan's mapped acceptance criteria and validation guide without asking for per-item approval.
- Choose the recommended path at ordinary implementation forks.
- Run the implementor, validator, and optional reviewer loops from `$harness-engineering-plan-resume`.
- Invoke `$harness-engineering-plan-checkpoint` after the item has passed verification.
- Create a clean commit after each checkpointed item.
- Continue to the next item.

Do not stop for routine uncertainty. Stop only when the stop conditions below apply.

## Stop Conditions

Stop the loop and report the exact blocker when any condition is true:

1. **Final completion gate**: the next unfinished item is the last unfinished item in the entire plan, or checkpointing the current item would make every tracked item `done: true`. Stop before flipping that final item complete, before filling `Outcomes & Retrospective`, before moving files to `completed/`, and before making the final completion commit. Summarize what is ready and ask the user to approve the final checkpoint.
2. **Human verification required**: the plan, validation guide, repo instructions, or the nature of the work requires manual verification, production credentials, external review, payment, legal/compliance review, app-store submission, release approval, or deployment.
3. **Plan-breaking discovery**: an agent or local verification discovers that the plan's assumptions are wrong, acceptance criteria no longer match the product, dependencies are unavailable, or the next item cannot be completed without changing the plan.
4. **Destructive or high-impact fork**: proceeding would delete or rewrite user data, alter unrelated product behavior, rewrite history, remove files not owned by the current item, migrate live data, or make an irreversible infrastructure change.
5. **Guessing with negative plan impact**: the agent would be guessing about requirements and that guess could meaningfully change plan scope, acceptance criteria, architecture, or user-facing behavior.
6. **Verification failure cap**: the validator has failed the same item 3 times, or the reviewer has requested changes twice.
7. **Dirty or ambiguous commit scope**: unrelated working-tree changes make it impossible to stage only the current item plus harness files safely.

When a stop condition triggers, do not partially checkpoint the item. Leave durable notes only if the corresponding checkpoint skill permits them without falsely marking progress.

## Loop Workflow

### 1. Load the Existing Contracts

Read and follow these skills as the source of truth:

- `$harness-engineering-plan-resume` for bearings, next-item selection, acceptance criteria mapping, and implementor -> validator -> optional reviewer orchestration.
- `$harness-engineering-plan-checkpoint` for verification before flipping `done: true`, progress JSON edits, plan log updates, and clean-state commits.

This skill overrides only the resume skill's normal "propose one target, then stop for confirmation" behavior. The loop request itself supplies that confirmation for ordinary non-final items.

### 2. Run Bearings Once, Then Recheck Lightly

At loop start, run the full `$harness-engineering-plan-resume` bearings ritual:

- `pwd`
- plan markdown
- progress JSON
- `docs/validation-guide.md` if present
- relevant `AGENTS.md`, nested agent rules, and `ARCHITECTURE.md`
- `git log --oneline -20`
- baseline smoke test or explicit "not yet green by design" handling

After each commit, reread the progress JSON, inspect `git status`, and identify the next unfinished item. Rerun the full bearings ritual when the repo structure, validation rules, or plan context changed materially.

### 3. Select the Next Item

Use the first `done: false` item in the earliest unfinished milestone. Before implementation, check:

- Whether this is the final unfinished item. If yes, stop under the final completion gate.
- Whether acceptance criteria can be mapped cleanly. If not, stop and ask.
- Whether the item implies a stop condition. If yes, stop and explain.

If the plan narrative and JSON disagree, prefer the JSON order only when the disagreement is harmless and the plan text is merely stale. Stop if the disagreement changes scope, priority, acceptance, or risk.

### 4. Execute One Item Through Agents

For each ordinary item:

1. Dispatch `implementor` with the same task shape required by `$harness-engineering-plan-resume`, including the guardrail not to edit plan markdown or progress JSON.
2. Dispatch `validator` with acceptance criteria and validation rules, not the implementor's self-report.
3. On validator `FAIL`, send actionable findings back to `implementor` and retry, capped at 3 validator failures.
4. If review is enabled, dispatch `code-reviewer` after validator `PASS` with the explicit policy that Critical, Major, and Medium findings require `REQUEST_CHANGES`; on requested changes, rerun implementor and validator before reviewer, capped at 2 review rounds.
5. If validation passes only with weaker proof than required, stop before checkpointing unless the plan explicitly allows that weaker proof.

Do not write product code in the main thread while this skill is orchestrating agents.

### 5. Checkpoint the Verified Item

After validator `PASS` and reviewer approval if enabled, invoke `$harness-engineering-plan-checkpoint` for that item.

Checkpoint must:

- Re-verify the acceptance criteria.
- Flip only the verified item's `done` from `false` to `true`.
- Set `completed_at` and `last_checkpoint_at`.
- Leave `commit: null` when the clean-state commit has not yet been created.
- Append concise plan log entries.
- Refresh only the `Progress` summary.

Do not checkpoint when it would complete the entire plan. Stop before the final flip.

### 6. Commit After Each Checkpointed Item

After each successful checkpoint, create one clean commit for that item:

1. Run `git status --short`.
2. Stage only files changed for the item plus `docs/exec-plans/active/<slug>.md` and `docs/exec-plans/active/<slug>.progress.json`.
3. Do not use `git add .`.
4. Commit with a concise item-oriented message, for example `feat(<area>): <item description>`.
5. Capture the short SHA and report it in the loop progress update.

Do not amend the commit to insert its own SHA into the progress JSON. Leave item commit metadata pending/unrecorded unless the user explicitly asks for a separate metadata commit.

### 7. Continue or Stop

After the commit:

1. Confirm `git status` is clean except for known unrelated user changes.
2. Reread the progress JSON.
3. Find the next unfinished item.
4. Continue unless a stop condition applies.

Give short progress updates after each committed item:

```text
Loop progress: completed <item-id> - <description>
Commit: <short sha>
Next candidate: <item-id> - <description>
Continuing unless a stop condition appears.
```

## Completion Handoff

When only the final item remains, stop before implementing or checkpointing it unless the user explicitly asks to proceed through final completion in the same session.

Report:

- Plan title and slug
- Items completed in this loop
- Current progress counts
- The final remaining item
- The exact final checkpoint risk: completing it will mark the plan complete and may trigger retrospective/completed-plan handling
- Suggested next command: `$harness-engineering-plan-resume <slug>` or `$harness-engineering-plan-checkpoint <slug>` depending on the state

## Forks in the Road

Use engineering judgment for ordinary forks:

- Choose the smallest implementation that satisfies the item.
- Prefer existing repo patterns over new abstractions.
- Prefer reversible local changes over broad migrations.
- Prefer stronger validation when available.
- Record meaningful decisions in the checkpoint.

Stop for the user only when the fork requires guessing and the guess could negatively affect the plan, user data, architecture, deployment, scope, or acceptance criteria.

## Hard Guardrails

- Do not create a plan or progress JSON.
- Do not add, remove, reword, or reorder progress JSON milestones or items.
- Do not mark the final unfinished item done without explicit user approval after the loop stops.
- Do not move active plan files to `docs/exec-plans/completed/` during the autonomous loop.
- Do not commit unrelated changes.
- Do not use destructive git commands.
- Do not deploy, publish, migrate production data, or call paid/external release systems without explicit user approval.
- Do not continue after a broken baseline unless the current item is explicitly meant to make the baseline green and the user already accepted that starting state.

## Degrading Gracefully

- Missing active plan: stop and suggest `$harness-engineering-plan` plus `$harness-engineering-plan-init`.
- Missing progress JSON: stop and suggest `$harness-engineering-plan-init`.
- Missing agent configuration: stop before implementation and report which agent role is unavailable.
- Missing validation guide: proceed using the plan and repo docs, and mention `$harness-engineering-validation-map` as a later improvement.
- Cannot produce a clean commit: stop after checkpoint only if the checkpoint is already written, report the exact dirty paths, and do not continue to another item.
- User asks for `review`: enable the code-review pass for every item. User asks for `no-review`: skip it for every item.
