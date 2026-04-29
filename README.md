# personal_skills

Mirror of the harness-engineering skill family in both **Claude Code** and **OpenAI Codex** flavors, so a fresh machine can install them into either CLI without re-porting them.

## Layout

```
<skill-name>/
├── claude/      # drop into ~/.claude/skills/<skill-name>/
└── codex/       # drop into ~/.agents/skills/<skill-name>/
```

The two flavors are functionally equivalent. They differ only in the platform-specific substitutions each CLI requires:

| Aspect | Claude Code | Codex |
|---|---|---|
| Slash invocation | `/skill-name` | `$skill-name` |
| User-scope skills dir | `~/.claude/skills/` | `~/.agents/skills/` |
| User-scope MCP config | `~/.claude.json` | `~/.codex/config.toml` |
| Project-scope MCP config | `.mcp.json` | `.codex/config.toml` |
| Repo instructions file | `CLAUDE.md` (+ `AGENTS.md`) | `AGENTS.md` (+ `AGENTS.override.md`) |
| MCP CLI | `claude mcp ...` | `codex mcp ...` |
| Subagent definition | `~/.claude/agents/*.md` (frontmatter + body) | `~/.codex/agents/*.toml` |

## Install on a new machine

### Claude Code

```bash
git clone <this-repo> ~/personal_skills
for s in ~/personal_skills/*/; do
  name=$(basename "$s")
  if [ -d "$s/claude" ] && [ -f "$s/claude/SKILL.md" ]; then
    mkdir -p ~/.claude/skills/"$name"
    cp -R "$s/claude/." ~/.claude/skills/"$name"/
  fi
done
```

### Codex

```bash
git clone <this-repo> ~/personal_skills
for s in ~/personal_skills/*/; do
  name=$(basename "$s")
  if [ -d "$s/codex" ] && [ -f "$s/codex/SKILL.md" ]; then
    mkdir -p ~/.agents/skills/"$name"
    cp -R "$s/codex/." ~/.agents/skills/"$name"/
  fi
done
```

## Skill catalog

| Skill | Purpose |
|---|---|
| `harness-engineering-project-bootstrap` | Scaffold a greenfield repo with `AGENTS.md`, `ARCHITECTURE.md`, `docs/exec-plans/`, etc. |
| `harness-engineering-init-claude-md` | (Claude-only) Add a thin `CLAUDE.md` shim that imports `AGENTS.md`. |
| `harness-engineering-agents-md-retrofit` | Trim a bloated `AGENTS.md`/`CLAUDE.md` into a repo map. |
| `harness-engineering-mcps-setup` | Recommend repo-needed MCPs and write project config. |
| `harness-engineering-validation-map` | Generate `docs/validation-guide.md` mapping change types to proof commands. |
| `harness-engineering-plan` | Turn a raw ask into a Lopopolo-style ExecPlan under `docs/exec-plans/active/`. |
| `harness-engineering-plan-init` | Scaffold the `<slug>.progress.json` sibling for an ExecPlan. |
| `harness-engineering-plan-resume` | Start/continue a session: bearings → pick item → orchestrate `implementor` + `validator` (+ `code-reviewer`). |
| `harness-engineering-plan-checkpoint` | Close a session: verify, flip `done: true`, append to log, suggest commit. |
| `harness-engineering-plan-loop` | Autonomously loop through remaining ExecPlan items without per-item confirmations. |
| `harness-engineering-track-task` | Append capture-only entries to a workspace-level `INBOX.md`. |
| `harness-engineering-failure-retro` | Turn an agent failure into the smallest durable repo improvement. |

## Subagents (not included here)

The harness-engineering flow expects three subagents — `implementor`, `validator`, `code-reviewer`. They live in `~/.claude/agents/*.md` (Claude) and `~/.codex/agents/*.toml` (Codex), not under `skills/`. They are not mirrored in this repo because they have a different install path; manage them separately.
