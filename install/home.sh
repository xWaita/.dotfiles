#!/usr/bin/env bash
# Personal-machine packages; run after shared.sh. Safe to re-run.
set -euo pipefail
DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Pre-create so stow links inside them instead of folding them into the repo.
mkdir -p ~/.claude ~/.config
stow -d "$DOTFILES" -t ~ --restow bashrc claude-home hyprland-end-4
