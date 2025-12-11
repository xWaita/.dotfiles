# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '

alias gs='git status'
alias gd='git diff'
alias gf='git fetch'
alias gl='git log'
alias gr='git rebase'
alias ga='git add .'
alias gc='git commit -m '
alias gp='git push'
alias gr='git rebase'
function gacp() {
    git add . && git commit -m "$1" && git push
}
function gco() {
    git checkout "$1" && git pull
}
alias s="source .venv/bin/activate"

eval $(thefuck --alias fuck)

function y() {
	local tmp="$(mktemp -t "yazi-cwd.XXXXXX")" cwd
	yazi "$@" --cwd-file="$tmp"
	IFS= read -r -d '' cwd < "$tmp"
	[ -n "$cwd" ] && [ "$cwd" != "$PWD" ] && builtin cd -- "$cwd"
	rm -f -- "$tmp"
}

fastfetch

# Only load Liquid Prompt in interactive shells, not from a script or from scp
[[ $- = *i* ]] && source liquidprompt
source /usr/share/liquidprompt/themes/powerline/powerline.theme
lp_theme powerline

. "$HOME/.cargo/env"
