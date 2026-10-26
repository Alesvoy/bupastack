#!/bin/sh
# Symlink every skill in this repo into the folder its tool reads.
# An existing skill folder (not a symlink) is moved to ~/.skills-backup first.
set -e
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
link claude "$HOME/.claude/skills"
link codex "$HOME/.codex/skills"

# Claude reads shared skills through ~/.claude/skills.
for skill in "$repo"/shared/*/; do
  name=$(basename "$skill")
  [ -e "$HOME/.claude/skills/$name" ] || ln -s "$HOME/.agents/skills/$name" "$HOME/.claude/skills/$name"
done
