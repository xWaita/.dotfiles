#!/usr/bin/env bash
# Dev setup shared by every machine. Safe to re-run.
set -euo pipefail
DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Pre-create so stow links inside them instead of folding them into the repo.
mkdir -p ~/.claude ~/.codex ~/.agents ~/.config ~/.local/bin
stow -d "$DOTFILES" -t ~ --restow claude code git kitty nvim tmux yazi zed

# git: .gitconfig-custom is only read via an include in ~/.gitconfig.
git config --global --get-all include.path | grep -qxF ~/.gitconfig-custom \
  || git config --global --add include.path ~/.gitconfig-custom

# Each submodule under external-skills/ is a skill collection: its top-level dirs holding
# a SKILL.md are stowed into the repo's skills dir, everything else is ignored. Target is
# the repo, not ~/.claude/skills, which must stay one folded link so new skills land in the repo.
git -C "$DOTFILES" submodule update --init
for c in "$DOTFILES"/external-skills/*/; do
  skills=$(cd "$c" && ls -d */SKILL.md | cut -d/ -f1 | paste -sd'|')
  stow -d "$DOTFILES/external-skills" -t "$DOTFILES/claude/.claude/skills" --restow \
    --ignore="^(?!($skills)(/|\$)).*" "$(basename "$c")"
done
