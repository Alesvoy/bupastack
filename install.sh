#!/bin/sh
# Symlink every skill in this repo into the folder its tool reads.
# An existing skill folder (not a symlink) is moved to ~/.skills-backup first.
# It also registers the kickoff hook in ~/.claude/settings.json, which needs node.
set -e
command -v node >/dev/null || { echo "install.sh needs node to register the kickoff hook. Install node and run it again." >&2; exit 1; }
repo=$(cd "$(dirname "$0")" && pwd)
backup="$HOME/.skills-backup/$(date +%Y%m%d-%H%M%S)"

link() { # link <repo subfolder> <install dir>
  mkdir -p "$2"
  for skill in "$repo/$1"/*/; do
    name=$(basename "$skill")
    dest="$2/$name"
    if [ -e "$dest" ] && [ ! -L "$dest" ]; then
      mkdir -p "$backup/$1" && mv "$dest" "$backup/$1/"
    fi
    ln -sfn "${skill%/}" "$dest"
    echo "$dest -> ${skill%/}"
  done
}

link shared "$HOME/.agents/skills"
link vendor "$HOME/.agents/skills"
link claude "$HOME/.claude/skills"
link codex "$HOME/.codex/skills"

# Claude reads shared and vendor skills through ~/.claude/skills.
for skill in "$repo"/shared/*/ "$repo"/vendor/*/; do
  name=$(basename "$skill")
  [ -e "$HOME/.claude/skills/$name" ] || ln -s "$HOME/.agents/skills/$name" "$HOME/.claude/skills/$name"
done

NODE_BIN="$(command -v node)" node "$repo/shared/handoff-to-engineer/scripts/register-hook.mjs"
