#!/usr/bin/env bash
# Claude Code status line: model, session cost, context usage, cwd + git branch.
# Reads the status-line JSON payload on stdin (see `statusLine` in ~/.claude/settings.json).
# No `set -e`: any missing field or failing git call must drop its own segment, never
# blank the whole line.

c() { printf '\033[38;5;%sm%s\033[0m' "$1" "$2"; }

payload=$(cat)
fields=$(jq -r '[
  (.model.display_name // ""),
  (.effort.level // ""),
  (.cost.total_cost_usd // ""),
  (.context_window.used_percentage // ""),
  (.workspace.current_dir // "")
] | map(tostring) | join("\u001f")' <<<"$payload" 2>/dev/null) || exit 0

# Unit separator, not tab: bash collapses runs of IFS *whitespace*, which would shift
# every field left whenever an optional one is absent.
IFS=$'\037' read -r model effort cost ctx cwd <<<"$fields"

segments=()

if [[ -n $model ]]; then
    seg="$(c 111 "◆ $model")"
    [[ -n $effort ]] && seg+="$(c 243 " ·$effort")"
    segments+=("$seg")
fi

[[ -n $cost ]] && segments+=("$(c 223 "$(printf '$%.2f' "$cost")")")

if [[ -n $ctx ]]; then
    pct=$(printf '%.0f' "$ctx")
    if   (( pct >= 80 )); then ctx_color=211
    elif (( pct >= 50 )); then ctx_color=223
    else                       ctx_color=151
    fi
    segments+=("$(c 243 "ctx ")$(c "$ctx_color" "${pct}%")")
fi

if [[ -n $cwd ]]; then
    seg="$(c 243 "${cwd/#$HOME/\~}")"
    if git -C "$cwd" rev-parse --is-inside-work-tree &>/dev/null; then
        branch=$(git -C "$cwd" rev-parse --abbrev-ref HEAD 2>/dev/null)
        [[ $branch == HEAD ]] && branch=$(git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
        dirty=""
        git -C "$cwd" diff --quiet 2>/dev/null && git -C "$cwd" diff --cached --quiet 2>/dev/null || dirty="*"
        [[ -n $branch ]] && seg+=" $(c 141 "⎇ ${branch}${dirty}")"
    fi
    segments+=("$seg")
fi

line=""
for seg in "${segments[@]}"; do
    [[ -n $line ]] && line+="   "
    line+="$seg"
done
[[ -n $line ]] && printf '%s\n' "$line"

exit 0
