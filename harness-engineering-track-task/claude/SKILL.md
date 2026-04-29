---
name: harness-engineering-track-task
description: Append one capture-only entry to a workspace-level `INBOX.md`, resolving the workspace root from either `~/liturga/clients/<client>/...` or the current git repository. Create the standard four-section inbox when needed, infer the target section from `--open` / `--in-flight` / `--waiting` / `--shipped` or the user's wording, keep the inbox append-only, and route scope-ready asks to `/harness-engineering-plan` instead of expanding them here. Use when the user wants to log an ask, blocker, in-flight item, or shipped item without planning it yet, or explicitly invokes `/harness-engineering-track-task`.
---

# Harness Engineering Track Task

Append one concise entry to the right workspace-level `INBOX.md`. This skill is for capture, not planning.

## Inputs

- Accept explicit section hints in the request: `--open`, `--in-flight`, `--waiting`, `--shipped`.
- If no flag is provided, infer the section from the request:
  - `waiting`: blocked on client, awaiting approval, waiting for assets, pending feedback, needs client input
  - `shipped`: shipped, deployed, sent, delivered, handed off
  - `in-flight`: building, implementing, fixing, working on, in progress
  - `open`: default fallback
- Distill the request into one short entry. Preserve the user's wording when it carries the important context.
- If the ask is too vague to capture faithfully, show the proposed bullet and ask the user to confirm instead of inventing details.

## Workspace Resolution

1. Prefer the current working directory.
2. If `pwd` is under `~/liturga/clients/<client>/...`, the target file is `~/liturga/clients/<client>/INBOX.md`.
3. Otherwise run `git rev-parse --show-toplevel`; if it succeeds, the target file is `<repo-root>/INBOX.md`.
4. If neither rule resolves a workspace, ask the user where to put the inbox entry. Do not guess.
5. If the user names a Liturga client and that client directory does not exist, stop and tell the user.

## Entry Format

- Keep the entry to one bullet and at most two lines total.
- Use today's date from the environment context.
- `open`: `- [YYYY-MM-DD] <task description>`
- `in-flight`: `- [YYYY-MM-DD] <short title> (<optional note>)` or `- <slug-or-short-title> - see \`docs/exec-plans/active/<slug>.md\`` when that pointer is already known.
- `waiting`: `- [YYYY-MM-DD] <what is blocked>; requested: <missing input>` when that missing input is clear.
- `shipped`: `- [YYYY-MM-DD] <what shipped> (<PR / commit / plan reference>)` when a concrete reference is already known.
- Do not expand the entry into a mini-spec or break it into subtasks.

## Use the Script

Use [scripts/track_task.py](/Users/alesvoy/.claude/skills/harness-engineering-track-task/scripts/track_task.py) for every write. It resolves the workspace root, creates the inbox template when missing, removes first-entry placeholders, matches both the older and newer inbox headings, appends without rewriting existing items, and returns section counts for the reply.

- Default workspace resolution:
  - `python scripts/track_task.py --text "<entry>" --section <section>`
- Explicit Liturga client outside the client tree:
  - `python scripts/track_task.py --client <client> --text "<entry>" --section <section>`
- Explicit non-Liturga workspace after the user confirms the target:
  - `python scripts/track_task.py --workspace-root /abs/path/to/workspace --text "<entry>" --section <section>`
- The script also accepts `--cwd` and `--base-dir` for debugging or tests.

## Guardrails

- Capture only. Do not scope, decompose, implement, or dispatch anything.
- If the entry is starting to look like a small project instead of a single inbox bullet, capture it once and then surface:
  - `This looks scoped enough to plan. Want me to route it to /harness-engineering-plan?`
- Do not inspect or modify plan files to decide whether an item belongs in the inbox.
- Never reorder, rewrite, deduplicate, or delete existing inbox entries.
- Do not write anywhere except the resolved workspace-level `INBOX.md`.

## Report Back

After appending, report:

- workspace or client
- section, and whether it was inferred
- target path
- exact bullet that was added
- inbox status counts when the script returns them
- whether `INBOX.md` had to be created first
