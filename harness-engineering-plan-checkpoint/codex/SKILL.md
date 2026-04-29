---
name: harness-engineering-plan-checkpoint
description: "Closes out a work session on a harness-engineering ExecPlan by updating the matching `.progress.json` file under `docs/exec-plans/active/`, flipping items to `done: true` only after real verification, appending to the plan's `Decision Log` and `Surprises & Discoveries`, refreshing the `Progress` summary, and suggesting a clean-state commit. Use this whenever the user signals a session is wrapping up or an item or milestone is done, with phrases like \"let's checkpoint\", \"wrap this up\", \"done with this item\", \"call it here\", \"let's commit and stop\", \"mark this complete\", or `$harness-engineering-plan-checkpoint`, or at the natural end of focused work on a project with an active ExecPlan in `docs/exec-plans/active/`. Does NOT touch the legacy `.workflow/feature_list.json` or `.workflow/PROGRESS.md`."
---

# harness-engineering-plan-checkpoint

You are closing out a work session on a project that uses the harness-engineering ExecPlan harness. Your job is to leave the workspace in a state that the next session can pick up cheaply.

This skill implements the clean-state handoff contract from the OpenAI harness-engineering article plus the living-document discipline from the ExecPlans cookbook.

## Hard guardrails

You are never permitted to add, remove, reword, reorder, or otherwise rewrite items or milestones in `docs/exec-plans/active/<slug>.progress.json`.

The only JSON edits you may make are:

- `done`: `false` -> `true`
- `completed_at`: `null` -> timestamp
- `commit`: `null` -> short SHA only when the verified work is already contained in that commit
- append a short note to `notes`
- update top-level `last_checkpoint_at`

You may append to the plan's `Decision Log`, append to `Surprises & Discoveries`, and refresh the `Progress` summary. You may not rewrite any other section during a normal checkpoint. The only exception is plan completion: when all tracked items are done, you may fill in `Outcomes & Retrospective` as described in Step 7.

## Prerequisites

1. An active ExecPlan exists: `docs/exec-plans/active/<slug>.md` plus `<slug>.progress.json`.
2. You know what happened in this session.
3. You know which item or items this session addressed.

If any of those are uncertain, stop and ask.

## Workflow

### Step 1: Gather the facts

Before writing anything:

- run `git status`
- inspect recent commits with `git log --oneline`
- read the tail of the plan's `Decision Log` and `Surprises & Discoveries`
- read `<slug>.progress.json` and locate the candidate item IDs
- read `docs/validation-guide.md` if it exists
- read relevant `AGENTS.md`, nested `AGENTS.md` / `AGENTS.override.md`, and `ARCHITECTURE.md` rules for the changed area

### Step 2: Verify before flipping `done: true`

Before proposing any flip:

1. Walk through the matching acceptance criteria from the plan.
2. Compare actual verification against the item acceptance criteria, `docs/validation-guide.md` if present, and relevant `AGENTS.md` / `ARCHITECTURE.md` rules.
3. Confirm the work was actually exercised end to end, not just implemented, whenever those sources require runtime proof.
4. If verification was weak or missing, either run it now or leave the item incomplete and record why.

Required proof rule:

- If the plan, validation guide, or repo instructions require a stronger proof than was run, do not flip `done: true` unless there is a concrete blocker or the user explicitly accepts the risk.
- Record any accepted weaker proof in the item's `notes` and in `Decision Log`.

File-content-only exception:

- Some items are legitimately verified by file content plus strong local checks rather than a running app, for example documentation updates, static config work, or a refactor item whose acceptance is "the file now contains X and the relevant checks still pass."
- When the item's acceptance is truly file-content-only and there is no stronger runtime verification available, direct file inspection plus the strongest relevant static checks passing counts as verification before commit.
- Commit metadata is separate from verification. A later commit may record, omit, or defer the item SHA according to the commit metadata rule below, but a commit does not need to already exist to verify documentation, static config, or other file-content-only work.
- If you use this exception, say so explicitly in the item's `notes` and in the `Decision Log`. Do not silently treat static proof as runtime proof.

If the user insists on flipping without verification or with weaker proof than required, surface the specific missing proof once and then defer to them only after they explicitly accept the risk.

### Step 3: Update `<slug>.progress.json`

For each verified item:

1. Find it by `id`, not by description.
2. Edit only:
   - `done`
   - `completed_at`
   - `commit`
   - `notes`
3. Update top-level `last_checkpoint_at`.

Do not touch anything else in the file.

Commit metadata rule:

- If the verified work is already contained in an existing commit before this checkpoint update, set `commit` to that short SHA during this JSON update.
- If the clean-state commit will be created later in this workflow, leave `commit: null` and add a short item note such as `Completion lands in the checkpoint commit; commit metadata pending/unrecorded.`
- If the user explicitly asks for an extra metadata commit after the clean-state commit, that follow-up commit may set `commit` to the prior checkpoint commit's short SHA.
- Do not invent a SHA and do not record an older commit that does not contain the verified work.
- Do not amend a commit in order to add that same commit's SHA to the files inside it. That creates stale self-referential metadata because the amend changes the commit SHA.

### Step 4: Append to `Decision Log`

Append one bullet per completed item:

```markdown
- [YYYY-MM-DD, checkpoint] Completed <item-id>: <item description>. Commit: <short sha or pending>. <optional one-line note>
```

If a notable scope or implementation decision happened this session, add a separate decision bullet.

If `commit` is still pending because the clean-state commit has not been made yet, say that explicitly in the bullet. If the user later creates the clean-state commit, append a follow-up decision bullet that the completion landed in the checkpoint commit and commit metadata remains pending/unrecorded unless they ask for a separate metadata commit.

### Step 5: Append to `Surprises & Discoveries` when needed

If this session revealed an unexpected blocker, environment issue, tech-debt discovery, or behavioral surprise, append a brief dated entry. If nothing surprising happened, skip this section.

### Step 6: Refresh the `Progress` summary

Update only the summary bullets in `## Progress` so the milestone counts match the JSON.

### Step 7: Handle milestone or plan completion

- If the item completes a milestone, note milestone completion in `Decision Log`.
- If the item completes the entire plan:
  1. Fill in `Outcomes & Retrospective`.
  2. Propose moving the plan and JSON from `docs/exec-plans/active/` to `docs/exec-plans/completed/`.
  3. Ask before moving them.

### Step 8: Offer a clean-state commit

If the user wants a commit, stage only the files from this session plus the two harness files. Never use `git add .`.

Example pattern:

```bash
git add -- <explicit changed paths> docs/exec-plans/active/<slug>.md docs/exec-plans/active/<slug>.progress.json
```

Then use a message such as:

```text
feat(<area>): <item description>
```

If there are unrelated changes in the working tree, flag them and do not bundle them.

After the commit is created:

1. Capture the new short SHA with `git rev-parse --short HEAD`.
2. Leave any completed item `commit` fields that were `null` for this checkpoint unchanged in that commit.
3. Report that the completion landed in the checkpoint commit and that item commit metadata is pending/unrecorded.

Do not amend the checkpoint commit to include its own SHA. If the user explicitly asks for commit metadata to be recorded after the checkpoint commit exists, make a separate follow-up metadata commit that updates only the relevant completed item `commit` fields and notes. If the user declines a commit or declines the extra metadata commit, leave `commit: null` and record in the item notes and `Decision Log` that no commit metadata was recorded yet.

### Step 9: Report back

End with a short summary:

```text
Checkpointed: <plan title> (<slug>)
Items flipped done: <count>
  - <item-id>: <description>
Plan progress: <X> of <Y> items done (M1: a/b, M2: c/d)
Plan status: active / milestone-complete / plan-complete
Commit: <short sha> - or "no commit, at your request"

Next: run `$harness-engineering-plan-resume <slug>` for the next session. Suggested next item: <id> - <description>
```

## Degrading gracefully

- No matching item ID: stop and ask.
- Plan exists but no progress JSON: suggest running `$harness-engineering-plan-init`.
- Session work spans multiple items: flip each one separately with separate log entries.
- Working tree is broken: do not commit it as clean-state.
- Validator never ran: perform the acceptance verification yourself before flipping, or leave the item incomplete.

## When not to use this skill

- Mid-session pauses
- Projects without an active ExecPlan
- Reorganizing the plan or JSON
- Legacy `.workflow/` harness projects

## Why this matters

The next session learns project state from the plan logs, the progress JSON, and `git log`. If your checkpoint is vague or you flip `done: true` without proof, the next session inherits false confidence and the bugs compound. A careful checkpoint costs a few minutes and saves many more in the sessions after it.
