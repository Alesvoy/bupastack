---
name: harness-engineering-plan-resume
description: Starts or continues a work session on a project that uses the harness-engineering ExecPlan harness under `docs/exec-plans/active/`, pairing each plan file with a sibling `.progress.json`. Runs the bearings ritual, parses last-checkpoint state, verifies the baseline is green, and proposes exactly one item to tackle before any code is touched. Then orchestrates the `implementor` plus `validator` plus optional `code-reviewer` loop. Use this at the start of a session, in a fresh context window with no memory of prior runs, whenever the user says things like "let's continue", "pick up where we left off", "resume the plan", "what's next on the plan", or `/harness-engineering-plan-resume`, or when you notice an active plan in `docs/exec-plans/active/` and the user is clearly resuming multi-step implementation work. Supports an optional `review` or `no-review` choice for the code-review pass.
---

# harness-engineering-plan-resume

You are starting a fresh work session on a project that uses the harness-engineering ExecPlan harness. Your context window has no memory of what previous sessions did. Every fact you need about the project's state lives on disk: in the ExecPlan markdown at `docs/exec-plans/active/<slug>.md`, in the sibling `<slug>.progress.json`, and in `git log`. Your job in this invocation is to:

1. Get your bearings from those files.
2. Verify the baseline is green, or explicitly confirm when it is not yet green by design.
3. Propose one clear target for this session before touching product code.
4. Orchestrate the `implementor` -> `validator` -> optional `code-reviewer` loop once the user confirms the target.

This skill is the counterpart to `/harness-engineering-plan`, `/harness-engineering-plan-init`, and `/harness-engineering-plan-checkpoint`. Together they turn a series of stateless sessions into monotonic progress.

## Prerequisites

1. An active ExecPlan exists: `docs/exec-plans/active/<slug>.md` and matching `<slug>.progress.json`.
2. You are in the project's working directory. Confirm with `pwd`.
3. You have not yet edited product code in this session.

If multiple active plans exist and the user did not pass a slug, list them and ask which one to resume. If none exist, this project is not using this harness.

## Workflow

### Step 1: The bearings ritual

Run these in order:

1. `pwd`
2. Read `docs/exec-plans/active/<slug>.md`, focusing on:
   - `Purpose / Big Picture`
   - `Progress`
   - recent `Surprises & Discoveries`
   - recent `Decision Log`
3. Read `docs/exec-plans/active/<slug>.progress.json` in full. Count `done: true` vs `done: false` per milestone.
4. Read `docs/validation-guide.md` if it exists. Extract only the validation rules relevant to this plan and the likely next item.
5. Read relevant repo instructions from `CLAUDE.md`, nested `CLAUDE.md`, `AGENTS.md`, and `ARCHITECTURE.md` only as needed for the target area.
6. Run `git log --oneline -20` and cross-check it against the plan and JSON.
7. Run the smoke test or dev server and confirm the baseline works before touching code.

Greenfield exception:

- If the earliest unfinished item is explicitly about making the project boot for the first time, or otherwise making the baseline green for the first time, the baseline may be **not yet green by design**.
- In that case, do not silently skip the smoke step. Instead:
  - confirm there is no stronger existing smoke target already promised by the plan,
  - surface that the baseline is intentionally red because the current item is "make it boot" or equivalent,
  - ask the user to confirm that this is the expected starting state before proceeding.

### Step 2: Parse last-checkpoint state

From the plan's recent `Surprises & Discoveries` and `Decision Log` entries, plus the JSON's most recent timestamps, extract:

- **Done last session**
- **Known broken or pending**
- **Recent decisions**

From `<slug>.progress.json`, identify the **next unfinished item**:

- Respect milestone order.
- Take the first `done: false` item in the earliest unfinished milestone.
- If every item is already `done: true`, the plan is complete. Say so and ask whether to move it to `docs/exec-plans/completed/`, extend it, or stop.

### Step 3: Cross-check and flag disagreements

Compare the plan narrative against the JSON's next unfinished item:

- If they agree, that is your proposed target.
- If they disagree, surface the disagreement and let the user choose.
- If the plan narrative is vague, fall back to the JSON's first unfinished item and say so.
- If the JSON is fully green but the plan implies more work, flag it. Do not "fix" it yourself.

### Step 4: Report bearings back to the user

Give the user one compact summary:

```text
Bearings for <plan title> (<slug>)
- Last checkpoint: <timestamp> - "<brief from most recent Decision Log entry>"
- Progress: <X> of <Y> items done (M1: a/b, M2: c/d)
- Baseline: <green / broken / couldn't run / not yet green by design>
- Validation rules: <relevant rules from docs/validation-guide.md, plan, or repo docs; or "none found">
- Known broken/pending: <one line, or "none noted">
- Recent decisions: <one line, or "none noted">
- First unfinished in progress JSON: <item id> - <description>
- Proposed target for this session: <description>
```

If Step 3 found a disagreement, make the final line an explicit question instead of a silent pick.

### Step 5: Propose the target for this session, then stop

Pick exactly one JSON item as the target. Default to the target from Step 4 unless the user redirects.

Before any implementation starts, show the user:

- the item's `description` verbatim, and
- the acceptance criteria that map to **that specific item**.
- the relevant validation rules from the plan, `docs/validation-guide.md` if present, and repo instructions that apply to the item.

Mapping rules for acceptance criteria:

- If the plan has per-item criteria, show those verbatim.
- If the plan only has milestone-wide criteria, extract only the lines that directly grade the chosen item.
- If you cannot map the milestone's criteria cleanly to the item, stop and ask the user rather than handing the implementor an ambiguous rubric.

Do not start coding until the user confirms the target and the acceptance criteria.

Combine that confirmation with the code-review opt-in:

1. If the invocation already included `review`, review is on.
2. If it included `no-review`, review is off.
3. Otherwise ask once: "Target: <item description>. Acceptance criteria look right? And do you want a code-review pass after the validator approves?"

Default review to off if the user waves the question off.

### Step 6: Execution handoff

You are the orchestrator for the rest of the session. You do not write product code in the main thread. Route implementation through the `implementor` subagent, functional grading through the `validator` subagent, and optional quality review through the `code-reviewer` subagent.

Availability check:

- Confirm that the `implementor`, `validator`, and (if review is enabled) `code-reviewer` subagent types are registered in this environment. You can verify by attempting a small dispatch, or by reading the available agents list.
- If `implementor` or `validator` is missing, stop before implementation and tell the user orchestration mode is unavailable. You may ask whether they want to switch to a different workflow, but this skill must not silently fall back to same-thread product-code work.
- If review is enabled but `code-reviewer` is missing, tell the user and ask whether to proceed without it or stop.

The orchestration loop is capped at 3 validator failures.

1. Draft the implementor task:
   - item description from the JSON
   - acceptance criteria for that item, verbatim
   - relevant validation rules from `docs/validation-guide.md`, if present
   - relevant pointers from `Context and Orientation`
   - prior validator critique, if any
   - explicit guardrail: `Do not edit docs/exec-plans/active/<slug>.md or docs/exec-plans/active/<slug>.progress.json.`
2. Dispatch the `implementor` subagent with that task using the `Agent` tool.
3. Broker only the minimum context to the `validator`:
   - item description
   - acceptance criteria
   - relevant validation rules from the plan, `docs/validation-guide.md` if present, and repo instructions
   - changed files or diff location
   - validator-focus hints from the implementor, if any
   - no implementor summary, no self-grading
4. Dispatch the `validator` subagent.
   - Tell it to fail if required proof from the plan or validation guide is skipped without a concrete blocker.
   - Tell it to treat weaker substitute checks as coverage gaps unless it explains why stronger checks are unavailable or irrelevant.
5. Read the `validator` result:
   - `PASS`: continue to Step 6.5 if review is on; otherwise continue to Step 7.
   - `FAIL`: extract the actionable findings, attach them as prior critique, and re-dispatch the implementor.
   - 3 failed validator rounds: stop and surface the findings to the user.

Keep your own coordination notes compact.

### Step 6.5: Optional code-review pass

If review is off, skip this section.

Once the `validator` returns `PASS`, dispatch the `code-reviewer` subagent with cold context:

- item description for orientation only
- changed files or diff location
- project review criteria from `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, or repository docs
- the same guardrail not to edit `docs/exec-plans/`

Do not forward the implementor report. Do not forward the validator report.

If `code-reviewer` returns:

- `APPROVE`: proceed to Step 7.
- `REQUEST_CHANGES`: dispatch the `implementor` with the critical review findings, then re-run the `validator`, and only then re-run the `code-reviewer`.

Reviewer loop cap: 2 `REQUEST_CHANGES` rounds. Validator re-runs triggered by reviewer findings still count toward the 3-round validator cap.

### Step 7: Handoff to `/harness-engineering-plan-checkpoint`

Once the `validator` has returned `PASS` and, if enabled, `code-reviewer` has returned `APPROVE`, invoke `/harness-engineering-plan-checkpoint`.

That skill re-verifies the same acceptance criteria, flips the JSON item to `done: true`, updates the plan logs, refreshes the progress summary, and proposes the commit.

If the validator passed only with weaker evidence, for example a UI flow validated with `curl` instead of browser automation, surface that to the user before invoking checkpoint.

## Hard guardrails

You are never permitted to add, remove, reword, or reorder milestones or items in the progress JSON during resume.

You are never permitted to flip `done: true` during resume.

You are never permitted to edit the plan markdown during resume.

You are the orchestrator, not the implementer. Once the subagent loop starts, do not "just fix one thing quickly" in the main thread.

The code reviewer is advisory on code quality, not on whether the item functionally works. Functional truth comes from the validator.

## Degrading gracefully

- No active ExecPlan: tell the user this project is not using the harness and suggest `/harness-engineering-plan` for multi-session work.
- Plan exists but no progress JSON sibling: suggest running `/harness-engineering-plan-init` first.
- Progress JSON exists but no plan file: stop and surface it.
- No `docs/validation-guide.md`: proceed using the plan, `CLAUDE.md`, `AGENTS.md`, `ARCHITECTURE.md`, and discovered commands; mention that `/harness-engineering-validation-map` can create one later.
- Smoke test cannot be located: ask the user what "green" means before proceeding.
- Baseline is not yet green by design: surface that explicitly and get confirmation before continuing.
- Not a git repo: note it and skip `git log`; rely on the plan and JSON instead.

## When not to use this skill

- Mid-session continuation inside the same conversation
- Exploratory spikes with no ExecPlan yet
- When the user explicitly wants to skip orientation

## Why this matters

You do not share memory with prior sessions. The only reason long-running work is tractable is that earlier sessions wrote durable state to disk and this session actually reads it before acting. Skipping the bearings ritual feels faster, but it usually means rebuilding stale assumptions, redoing finished work, or implementing the wrong item. Read the plan. Read the JSON. Confirm the target. Then execute.
