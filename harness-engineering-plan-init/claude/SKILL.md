---
name: harness-engineering-plan-init
description: "Scaffolds the progress-tracking JSON sibling file for an ExecPlan created by `/harness-engineering-plan`. Creates a sibling `.progress.json` file under `docs/exec-plans/active/` with milestone and item structure derived from the plan file, with all items initialized as `done: false`. Use this immediately after `/harness-engineering-plan` finishes for any ExecPlan size: ticket, sprint, or epic; when the user says things like \"init this plan\", \"scaffold the progress file\", \"let's start tracking this\", or `/harness-engineering-plan-init`; or when you notice an ExecPlan in `docs/exec-plans/active/` but no sibling `.progress.json`. Does NOT create plan files and does NOT write to the legacy `.workflow/feature_list.json` harness."
---

# harness-engineering-plan-init

You are the scaffolding companion to `/harness-engineering-plan`. A plan file exists at `docs/exec-plans/active/<slug>.md`; your job is to create its sibling progress JSON so later sessions, via `/harness-engineering-plan-resume` and `/harness-engineering-plan-checkpoint`, have a structured source of truth for what is done and what is not.

This skill is not the planner. It does not add milestones, reword anything, or expand scope. It reads the plan's `Plan of Work` and optional `Concrete Steps`, translates them into JSON, and writes `done: false` everywhere.

Run this for every ExecPlan size: ticket, sprint, and epic. Ticket plans usually produce one milestone with one or a few items.

## Prerequisites

1. A plan file exists, typically `docs/exec-plans/active/<slug>.md`.
2. The plan file has a `Plan of Work` section with milestone headings like `### M1 - <title>`.
3. No existing `<slug>.progress.json` sibling exists.
4. You are in the project root, or the plan path is absolute. Confirm with `pwd`.

If any prerequisite fails, stop and surface it. Do not guess.

## Workflow

### Step 1: Read the plan file in full

Read `docs/exec-plans/active/<slug>.md`. Extract:

- **Plan title** from the `#` heading.
- **Milestones** from `## Plan of Work`, capturing each `### M<N> - <title>` heading plus the paragraph under it.
- **Concrete steps** from `## Concrete Steps`, if present.
- **Validation and Acceptance** criteria from the matching milestone section.

Primary source of `items[].description` is `Concrete Steps`:

- If a milestone has `Concrete Steps`, each bullet in that milestone becomes one JSON item description.
- Only if `Concrete Steps` is absent for that milestone do you derive one JSON item per `Validation and Acceptance` criterion.
- Do not mix the two sources within the same milestone unless the user explicitly tells you to.

If milestones exist but item boundaries are still unclear, ask once before writing.

### Step 2: Derive stable IDs

Each milestone and item gets a stable ID:

- Milestone IDs: `m1`, `m2`, and so on, matching `M1`, `M2`.
- Item IDs: `m<N>-<kebab-short-title>`, such as `m1-port-hero-carousel`.

Keep item IDs short and unique across the file.

### Step 3: Write `<slug>.progress.json`

Create `docs/exec-plans/active/<slug>.progress.json` with pretty-printed JSON and 2-space indentation.

Schema:

```json
{
  "plan_file": "docs/exec-plans/active/<slug>.md",
  "plan_title": "<exact title from the plan>",
  "slug": "<slug>",
  "created_at": "<YYYY-MM-DDTHH:MM:SSZ>",
  "last_checkpoint_at": null,
  "milestones": [
    {
      "id": "m1",
      "title": "<milestone title>",
      "description": "<first sentence of the milestone paragraph>",
      "items": [
        {
          "id": "m1-<kebab-title>",
          "description": "<one-line observable description>",
          "done": false,
          "completed_at": null,
          "commit": null,
          "notes": ""
        }
      ]
    }
  ]
}
```

Field rules:

- `plan_file`: relative path from the repo root.
- `plan_title`: copied verbatim from the plan heading.
- `slug`: shared by both filenames.
- `created_at`: now, in ISO 8601 UTC.
- `last_checkpoint_at`: `null` until the first checkpoint.
- `milestones[]`: in the same order as the plan.
- `items[]`: ordered exactly as their source appears in `Concrete Steps`, or in `Validation and Acceptance` when `Concrete Steps` is absent.
- `items[].description`: observable and concrete. Avoid vague wording.
- `done`: always `false` at init.
- `completed_at`: `null` at init.
- `commit`: `null` at init.
- `notes`: empty string at init.

### Step 4: Update the plan file's `Progress` summary

Open the plan file, find `## Progress`, and populate the `Summary` block with real milestone counts from the JSON you just created.

This is the only edit you make to the plan file's `Progress` section. Do not touch the paragraph that points to the JSON. Do not rewrite the plan narrative.

### Step 5: Append a Decision Log entry

In `## Decision Log`, append:

```markdown
- [YYYY-MM-DD, harness-engineering-plan-init] Progress JSON scaffolded at `<slug>.progress.json`. <total> items across <N> milestones.
```

Use the current date from the environment context.

### Step 6: Offer a baseline commit

If the repo is a git repo and the user wants a baseline commit, stage only the harness files:

```bash
git add -- docs/exec-plans/active/<slug>.md docs/exec-plans/active/<slug>.progress.json
```

Then use a commit message such as:

```text
chore(exec-plans): init progress tracking for <slug>
```

Ask before committing. Never use `git add .` or bundle unrelated changes.

### Step 7: Report back

End with a compact summary:

```text
Initialized: docs/exec-plans/active/<slug>.progress.json
Plan:        docs/exec-plans/active/<slug>.md
Milestones:  N (M1: X items, M2: Y items)
Total items: <total>, all done: false
Commit:      <sha> - or "no commit, at your request"

Next: run `/harness-engineering-plan-resume <slug>` to pick the first item and start work.
```

## Hard guardrails

You do not modify `Plan of Work`, `Concrete Steps`, `Validation and Acceptance`, or any other plan section except:

- `Progress` summary, and
- `Decision Log` as append-only.

You do not create milestones or items the plan does not describe.

You do not touch the legacy `.workflow/PROGRESS.md` or `.workflow/feature_list.json`.

You do not dispatch subagents.

## Degrading gracefully

- If the plan exists but has no `## Plan of Work`, stop and say it is too thin to scaffold from.
- If the plan exists but `## Decision Log` is missing, add it with today's init entry. That section is mandatory.
- If this is not a git repo, skip the commit step without blocking.

## When not to use this skill

- Brief-sized asks with no ExecPlan.
- The legacy `.workflow/` harness.
- Mid-flight plan amendments that change milestone structure.

## Why this matters

The progress JSON is the durable state every future session reads to know what is done. `/harness-engineering-plan-resume` uses it at session start to pick the next item. `/harness-engineering-plan-checkpoint` edits it at session end to flip items `done: true`. If the JSON is sparse or drifted from the plan, every downstream session pays the tax. Scaffold it carefully once so the rest of the loop can trust it.
