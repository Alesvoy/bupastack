---
name: harness-engineering-init-claude-md
description: Scaffolds a terse CLAUDE.md as a thin `@AGENTS.md` import with optional Claude-specific deltas. Assumes `$harness-engineering-project-bootstrap` has already been run (so `AGENTS.md` and the `docs/` substrate exist) — if not, stops and routes the user there first. Does NOT create or modify `AGENTS.md`, does NOT scaffold `docs/`, does NOT write product code. Use whenever the user is setting up a new repo for Claude Code, says things like "set up CLAUDE.md", "scaffold the Claude entry point", "make this repo agent-ready for Claude", "/harness-engineering-init-claude-md", or when they hand you a bootstrapped repo without a CLAUDE.md. Also suggest proactively when the existing CLAUDE.md is clearly bloated (>200 lines) or has rotted into a graveyard of stale rules. Does NOT scaffold the long-running harness (that's `plan-init` / `harness-engineering-plan-init`), does NOT install MCP servers (that's `harness-engineering-mcps-setup`). The point is the Claude-specific entry-point, not the repo substrate.
---

# harness-engineering-init-claude-md

You are scaffolding the **always-loaded entry point** that every Claude Code session in this repo will read from page one. In this skill's world, `AGENTS.md` is the vendor-neutral source of truth — `CLAUDE.md` is a thin `@AGENTS.md` import plus any Claude-specific deltas, and nothing more. Get this right and every future session starts with a sharp map at near-zero cost. Get it wrong — make it bloated, duplicate AGENTS.md, or pad it with prose — and every future session pays for it on every turn.

This skill implements the **AGENTS.md-as-table-of-contents pattern** from Ryan Lopopolo's *Harness engineering: leveraging Codex in an agent-first world* (OpenAI), confirmed by community consensus around CLAUDE.md (HumanLayer, Anthropic best-practices docs). The governing principle is [[concepts/agent-legibility]]:

> "From the agent's point of view, anything it can't access in-context while running effectively doesn't exist."

## Scope — what this skill does and does not do

This skill writes **exactly one file**: `CLAUDE.md` at the repo root. It does not create, edit, or touch any other file.

In particular, this skill does NOT:

- Create or modify `AGENTS.md` — that's `$harness-engineering-project-bootstrap`'s job.
- Scaffold the `docs/` substrate (`docs/INDEX.md`, `ARCHITECTURE.md`, `docs/design-docs/`, `docs/exec-plans/`, `docs/references/`, `docs/generated/`, `docs/product-specs/`) — also `$harness-engineering-project-bootstrap`'s job.
- Create `INBOX.md`, set up the long-running harness, or install MCP servers.
- Write product code.

## Prerequisite

`AGENTS.md` must already exist at the repo root. If it doesn't, stop and tell the user to run `$harness-engineering-project-bootstrap` first — that skill creates `AGENTS.md`, `ARCHITECTURE.md`, and the `docs/` substrate this CLAUDE.md will point into (via `@AGENTS.md`).

## What you are NOT writing

Before doing anything, internalize the anti-patterns Lopopolo names and that the wiki documents in `concepts/agents-md.md`:

- **Not a duplicate of AGENTS.md.** The whole point of `@AGENTS.md` is that the source of truth lives in one place. Never read AGENTS.md and copy its content into CLAUDE.md.
- **Not a 1,000-page instruction manual.** Crowds out the task, the code, and the relevant docs.
- **Not a list of every rule you'd like the agent to follow.** When everything is important, nothing is — the agent pattern-matches locally instead of navigating intentionally.
- **Not a place for prose, tutorials, or architectural essays.** Those go in `docs/` files AGENTS.md points at.
- **Not a replacement for linters, hooks, or tests.** If you'd repeat a rule more than once, it belongs in a hook (deterministic) or a lint (mechanical), not CLAUDE.md (probabilistic, ~70% adherence).

## Sizing — the load-bearing rule

In this setup, `CLAUDE.md` should almost always be **under 20 lines**. It's an `@AGENTS.md` import with at most a short "Claude-specific notes" section below. A two-line CLAUDE.md is a feature, not a bug.

Hard ceiling: 200 lines (Anthropic's soft cap, past which adherence measurably drops). **Refuse to exceed this.** If you feel the repo needs more Claude-specific guidance than ~50 lines, push it into a `docs/claude-notes.md` and link from CLAUDE.md — never inline it.

## Workflow

### Step 1 — Orient (cheap, read-only)

Run `pwd` and confirm you're at a project root (not `~/`, not `~/.claude/`, not a parent directory). The project root is the directory that contains `.git/`, or a manifest file (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, `composer.json`, etc.). If CWD doesn't look like a project root, **stop and ask the user where the project actually lives** — don't guess.

Then check preconditions:

- Glob the root for `AGENTS.md`. **If it does not exist, stop.** Tell the user verbatim: "`AGENTS.md` is missing. Run `$harness-engineering-project-bootstrap` first — that skill creates `AGENTS.md` and the `docs/` substrate this CLAUDE.md will point into." Do not proceed, do not offer to scaffold a standalone CLAUDE.md.
- Glob the root for `CLAUDE.md` (does one already exist? how big?).
- Glob for `.claude/` (any existing skills, subagents, hooks, settings — potential source of Claude-specific deltas to surface).

Do **not** read `AGENTS.md`'s contents to mirror them. You only need to know it exists.

### Step 2 — Decide posture

Based on what you found:

- **If `CLAUDE.md` already exists and is >200 lines** → tell the user, propose a refactor to the thin-import form, ask before overwriting. Preserve any genuinely-useful Claude-specific content by moving it into the "Claude-specific notes" section of the new file, or into `docs/claude-notes.md` if it's substantial.
- **If `CLAUDE.md` already exists and is reasonable (<200 lines)** → ask whether they want a clean rewrite or a minimal touch-up. Don't blow away their work.
- **If no `CLAUDE.md` exists** → proceed to Step 3.

### Step 3 — Brief Claude-specific interview (optional, 1–3 questions max)

`AGENTS.md` covers the vendor-neutral rules. This step asks only what is **Claude-specific**. Examples:

1. "Any areas where Claude should prefer plan mode before making changes?"
2. "Are there Claude Code skills, subagents, or hooks under `.claude/` that future sessions should know about?"
3. "Anything about Claude Code's behavior you've had to correct repeatedly that belongs in the always-loaded context?"

If there are no Claude-specific deltas, **skip this step entirely** and write a two-line CLAUDE.md. That is the ideal outcome, not a degenerate one.

Skip any question whose answer is already in the README, a manifest, or AGENTS.md.

### Step 4 — Write `CLAUDE.md`

Only ever write `CLAUDE.md`. Never write, create, or touch any other file — not `AGENTS.md`, not anything under `docs/`, not `INBOX.md`, not `ARCHITECTURE.md`, not files under `.claude/`.

```markdown
@AGENTS.md

## Claude-specific notes

<Only deltas that apply to Claude Code specifically. Examples:
- "Prefer plan mode for changes under `src/billing/`."
- "Skills live under `.claude/skills/`. Run `/find-skills` if unsure what's available."
- "The `cleanup-stale-docs` subagent runs nightly via cron; don't manually invoke it."
If there are no Claude-specific deltas, leave this section out entirely — a two-line CLAUDE.md is the goal.>
```

### Step 5 — Report

Tell the user, succinctly:

- File created: `CLAUDE.md` (with line count — prove the import stayed thin).
- Whether any existing `CLAUDE.md` was preserved or overwritten.
- A pointer to the next logical step: "Set up MCP servers? → `/harness-engineering-mcps-setup`. Start a multi-session project here? → `/plan-init` or `/harness-engineering-plan`."
- Optionally: "This pattern relies on the `docs/` substrate staying fresh. Lopopolo's playbook adds a doc-gardening agent that auto-PRs stale docs — worth setting up later if this repo grows."

## Things to refuse

- **Refuse to proceed if `AGENTS.md` does not exist.** Route the user to `$harness-engineering-project-bootstrap` first. This skill has no standalone mode — there is no "Case B".
- **Refuse to create or edit `AGENTS.md`.** Out of scope — full stop. That's `$harness-engineering-project-bootstrap`'s job. You never read AGENTS.md to mirror content, and you never touch it.
- **Refuse to scaffold the `docs/` substrate** (`docs/INDEX.md`, `docs/design-docs/`, `docs/exec-plans/`, `docs/references/`, `docs/generated/`, `docs/product-specs/`). That's `$harness-engineering-project-bootstrap`'s job. If those paths are missing, the prerequisite hasn't been met — stop and route.
- **Refuse to create `ARCHITECTURE.md` or `INBOX.md` at the repo root.** Same reason.
- **Refuse to duplicate AGENTS.md content into CLAUDE.md.** Use `@AGENTS.md`. The whole point of the import is that the source of truth lives in one place.
- **Refuse to write a CLAUDE.md longer than 200 lines.** Push back, propose moving substantive content into `docs/claude-notes.md`.
- **Refuse to embed long prose explanations.** Link to a `docs/<topic>.md` file instead.
- **Refuse to invent Claude-specific gotchas the user didn't tell you about.** A scaffolder can scaffold structure; only the user knows their landmines.
- **Refuse to commit anything.** This skill writes files; the user reviews and commits. Never `git add` / `git commit` autonomously.

## When this skill is wrong for the job

- **`AGENTS.md` and the `docs/` substrate haven't been scaffolded yet** → use `$harness-engineering-project-bootstrap` first. Come back to this skill afterward.
- The user wants to set up the **long-running multi-session harness** (PROGRESS.md, feature_list.json) → use `plan-init` instead.
- The user wants the **harness-engineering ExecPlan flavor** of the same → use `harness-engineering-plan-init` instead.
- The user wants to **install MCP servers** for this repo → use `harness-engineering-mcps-setup` instead.
- The user wants you to **write the actual product code** → this skill is the wrong tool.

## Why this works (one paragraph for future-you)

`CLAUDE.md` is the most general (applies everywhere) and the most expensive (loaded every time) of Claude Code's customization layers. The mistake everyone makes is treating "always loaded" as "more is better" — the opposite is true. In a harness-engineering repo, the split is clean: `$harness-engineering-project-bootstrap` owns the vendor-neutral substrate (`AGENTS.md` + `ARCHITECTURE.md` + the `docs/` tree), and this skill owns only the Claude-specific entry point, which should be as thin as possible. The pattern pays off when CLAUDE.md imports AGENTS.md via `@AGENTS.md` and adds nothing it doesn't strictly need — the agent gets a sharp map at near-zero always-loaded cost, and the deep substrate loads only when a task demands it. The load-bearing job of this skill is **enforcing that thinness at the moment of creation**; after that, the user's job (or a future doc-gardening agent's job) is keeping it that way.
