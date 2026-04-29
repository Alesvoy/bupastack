---
name: harness-engineering-mcps-setup
description: Analyze the current repository, infer which MCP-backed capabilities would improve accurate validation and agent work, and recommend a Codex-native split between user scope (`~/.codex/config.toml`) and project scope (`.codex/config.toml`). Distinguish repo-needed MCPs from already-installed MCPs; write project config only after confirmation; never invent server commands or silently remove user-scope MCPs.
---

# Harness Engineering MCP Setup

This skill ports the Claude `/mcps-setup` workflow to Codex. In Codex, project MCPs live in `.codex/config.toml`, user MCPs live in `~/.codex/config.toml`, and repo guidance belongs in `AGENTS.md`.

This skill has two distinct jobs, in this order:

1. **Capability recommendation**: inspect the repo and infer which MCP-backed capabilities would materially improve validation or agent legibility, whether or not those MCPs are currently installed.
2. **Scope/config planning**: for MCPs that already exist in the user's environment, or whose exact setup details are known, recommend whether they belong in user scope or project scope.

Installed MCP inventory informs what can be configured safely right now. It must **not** cap the recommendation set.

## Native Codex Targets

- Project scope: `.codex/config.toml` in the repo root. Commit it when the team should share the setup.
- User scope: `~/.codex/config.toml`.
- Repo rationale: `AGENTS.md` in the repo root.
- If the repo still has `CLAUDE.md`, read it as context, but do not treat it as the default Codex instruction target unless the repo is explicitly configured that way.

## Signals to Inspect

Inspect the smallest relevant set:

- repo root and current working directory
- existing `.codex/config.toml`
- `package.json`, lockfiles, and framework configs such as `next.config.*`, `vite.config.*`, `astro.config.*`, `playwright.config.*`
- `docker-compose*.yml`, `compose.yml`, or container configs
- `AGENTS.md`, `CLAUDE.md`, `README*`, and docs that describe the development workflow
- test scripts, CI workflows, and docs that describe validation expectations
- observability or runtime-debugging signals such as logging, metrics, tracing, Sentry, Grafana, Prometheus, Vector, or similar tooling references
- design-system or design-handoff signals such as Figma references, design tokens, or component-mapping docs
- current user MCPs from `~/.codex/config.toml`
- optionally `codex mcp list` for the active user-level inventory

## Recommendation Policy

Primary question: **what capabilities does this repo need for accurate validation and high-legibility agent work?**

Use repo signals to recommend MCPs even when they are not currently installed. Treat the current user MCP inventory as:

- evidence of what is already available
- a clue about the user's preferred tooling
- a constraint on what can be configured immediately

It is **not** the limit of what you may recommend.

When a capability is clearly needed but the exact MCP package, command, URL, or auth setup is unknown, still recommend the capability. Clearly label it as a recommendation that is **not yet safely configurable**.

## Default Scope Policy

Use these defaults when the named MCPs are already part of the user’s setup:

- Keep global: `github`, `sequential-thinking`, `context7`
- Prefer project scope: `playwright`
- Review case-by-case: `vercel`

For `vercel`, keep it global only if most active projects are Vercel projects. Otherwise, recommend moving it to project scope.

These are **scope defaults only**. They do not define the full recommendation set for a repo.

## Important Codex-Specific Behavior

- `codex mcp add` writes to `~/.codex/config.toml`, not to the nearest project config.
- For project-scoped MCPs, edit `.codex/config.toml` directly.
- Project-scoped `.codex/config.toml` files are loaded only for trusted projects.
- Never silently remove a user-scope MCP. If cleanup is needed, surface the exact command for the user to run, for example `codex mcp remove playwright`.

## Workflow

1. Confirm the repo root and inspect the signals above.
2. Infer which MCP-backed capabilities would materially improve validation or agent execution in this repo.
3. Summarize the current state:
   - existing user-scope MCPs
   - existing project-scoped MCPs
   - repo signals that justify project-specific tooling
   - repo signals that justify MCP recommendations that are not currently installed
4. Produce a recommendation with five buckets:
   - recommend for this repo, regardless of install status
   - available now and safe to configure
   - keep global
   - move or keep at project scope
   - review manually / blocked by unknown install or auth details
5. If you do not know the exact MCP command, package name, URL, or auth detail, stop before configuration changes and say so explicitly. Never invent package names, server URLs, or auth settings.
6. Only after explicit user confirmation, write or update `.codex/config.toml` for MCPs whose setup details are known.
7. If the repo should record why a project MCP is expected, add or update a short `AGENTS.md` note so future agents know which MCPs matter and why.

## Writing Rules

- Preserve unrelated settings in `.codex/config.toml`.
- Add only the needed `[mcp_servers.<name>]` tables.
- Keep server names stable across user and project config when you are moving an MCP.
- Do not write placeholder config for a recommended MCP if its command, package, URL, or auth details are unknown.
- Do not install, remove, or log into MCP servers as part of this skill unless the user separately asks.
- Do not touch `~/.codex/config.toml` unless the user explicitly asks for a user-scope change.

## `AGENTS.md` Note

When you update `AGENTS.md`, keep it short and operational. Prefer a section like:

```md
## MCP expectations

- This repo expects the `playwright` MCP at project scope via `.codex/config.toml` for browser validation flows.
- Keep general-purpose MCPs such as `github` and `context7` at user scope unless there is a repo-specific override.
```

If the repo already has a better place for this guidance, use the existing structure instead of forcing a new heading.

## Report Back

Before any write, report:

- what you inspected
- which MCP capabilities you recommend for this repo, even if not currently installed
- which of those are already available now
- which MCPs should stay global
- which MCPs should be project-scoped
- any unknown MCP command, package, URL, or auth detail that blocks a safe change

After a confirmed write, report:

- exact files changed
- the MCP entries added or updated
- any recommended MCPs that were intentionally left unconfigured because setup details were unknown
- any `codex mcp remove <name>` cleanup commands the user may want to run manually
