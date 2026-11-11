# Pre-create so stow links inside them instead of folding them into the repo.
mkdir -p ~/.claude ~/.codex ~/.agents
stow hyprland-end-4
stow nvim
stow code
stow kitty
stow claude
stow yazi
stow tmux

# Each submodule under external-skills/ is a skill collection: its top-level dirs holding
# a SKILL.md are stowed into the repo's skills dir, everything else is ignored. Target is
# the repo, not ~/.claude/skills, which must stay one folded link so new skills land in the repo.
git -C ~/.dotfiles submodule update --init
for c in ~/.dotfiles/external-skills/*/; do
  skills=$(cd "$c" && ls -d */SKILL.md | cut -d/ -f1 | paste -sd'|')
  stow -d ~/.dotfiles/external-skills -t ~/.dotfiles/claude/.claude/skills --restow \
    --ignore="^(?!($skills)(/|\$)).*" "$(basename "$c")"
done
