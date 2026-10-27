# bupastack

My personal agent skills for **Claude Code** and **OpenAI Codex**.

## Layout

Each top-level folder installs into one directory:

| Folder | Installs into | Read by |
|---|---|---|
| `shared/` | `~/.agents/skills/` | Codex, and Claude through symlinks in `~/.claude/skills/` |
| `vendor/` | `~/.agents/skills/` | Codex, and Claude through symlinks in `~/.claude/skills/` |
| `claude/` | `~/.claude/skills/` | Claude Code |
| `codex/` | `~/.codex/skills/` | Codex |

The design skills have a Claude version and a Codex version because each one calls the other tool's features differently.

## Install

```bash
git clone git@github.com:Alesvoy/bupastack.git ~/ai/bupastack
~/ai/bupastack/install.sh
```

The script symlinks each skill into place, so edits in the repo take effect immediately. If a skill folder already exists, the script moves it to `~/.skills-backup/<timestamp>/` before linking.

## Skills

| Skill | Folder | Purpose |
|---|---|---|
| `raise-pr` | shared | Open or update a PR that is safe to merge, after running the repo's checks, QA, and a review. |
| `review-pr` | shared | Review a PR or branch with parallel reviewers and give a merge verdict. |
| `merge-pr` | shared | Merge a PR only when the user asks and every check is green. |
| `cleanup-pr` | shared | Remove worktrees, temp files, and local branches after a merge. |
| `qa` | shared | Prove a change works with a hands-on test plan run by a QA subagent. |
| `sign-in-with-1password` | shared | Sign into a website with 1Password autofill through computer use. |
| `grilling` | vendor | Question you in numbered rounds, each with a recommended answer, until a plan has no open decisions. From [mattpocock/skills](https://github.com/mattpocock/skills). |
| `grill-me` | vendor | Run `grilling` when you type `/grill-me`. From [mattpocock/skills](https://github.com/mattpocock/skills). |
| `sol-loop` | vendor | Review a change in rounds with a Sol reviewer, fixing what is valid. From [t3dotgg/tstack](https://github.com/t3dotgg/tstack). |
| `brainstorm-design` | claude, codex | Frame the problem, gather references, and build several design options in parallel. |
| `build-design` | claude, codex | Build one UI design from a direction and reference images, then review it once. |
| `design-previews` | claude, codex | Open each design option in its own browser tab and record the user's choice. |
| `design-system` | claude, codex | Set up or update an app's design system from a chosen design. |
| `implement-design` | claude, codex | Build a chosen design into the real app. |
