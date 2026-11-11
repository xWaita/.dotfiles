# Pre-create so stow links inside them instead of folding them into the repo.
mkdir -p ~/.claude ~/.codex ~/.agents
stow hyprland-end-4
stow nvim
stow code
stow kitty
stow claude
stow yazi
stow tmux

# Open-source skill repos: submodules under external/, stowed into the repo's skills dir
# (not ~/.claude/skills, which must stay one folded link so new skills land in the repo).
git -C ~/.dotfiles submodule update --init
stow -d ~/.dotfiles/external -t ~/.dotfiles/claude/.claude/skills \
  --ignore='CONTRIBUTING\.md' --ignore='\.ocamlformat' agent_skills
