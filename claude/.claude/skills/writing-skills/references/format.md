# Skill & Command Format Reference

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read when drafting frontmatter or command bodies. Source: code.claude.com/docs/en/skills.

## Frontmatter fields

All optional; `description` is the one that matters. House style: `allowed-tools` as a YAML flow list, e.g. `[Read, Grep, Bash]`.

| Field | Notes |
|---|---|
| `name` | Display name only — the typed command comes from the directory name (skill) or file stem (command). |
| `description` | The only auto-trigger surface; see hard limits below. |
| `argument-hint` | Autocomplete hint, e.g. `[file] [format]`. |
| `arguments` | Named positional args for `$name` substitution (space-separated or YAML list, mapped in order). |
| `allowed-tools` | Pre-approves tools while the skill is active; does not restrict the pool. |
| `disallowed-tools` | Removes tools from the pool while active. |
| `model` / `effort` | Per-turn overrides; `effort` is `low`–`max`, model-dependent. |
| `disable-model-invocation` | `true` → manual `/name` only; description not preloaded into context. |
| `user-invocable` | `false` → hidden from the `/` menu; model-only background knowledge. |
| `context: fork` + `agent` | Run the body as a subagent prompt (`Explore`, `Plan`, `general-purpose`, or a custom agent). |
| `hooks` | Hooks scoped to the skill's lifecycle. |
| `paths` | Globs limiting auto-activation to matching files. |
| `shell` | `bash` (default) or `powershell` for injection blocks. |
| `when_to_use` | Extra trigger phrases appended to the description in listings. |

## Invocation matrix

| Frontmatter | User invokes | Model invokes |
|---|---|---|
| (default) | yes | yes |
| `disable-model-invocation: true` | yes | no |
| `user-invocable: false` | no | yes |

## Substitution tokens (bodies)

- `$ARGUMENTS` — all args as typed; if absent from the body, args are appended as `ARGUMENTS: <value>`.
- `$0`, `$1`, … or `$ARGUMENTS[N]` — positional, 0-based, shell-style quoting; escape literals as `\$1`.
- `$name` — named args declared in `arguments`.
- `` !`cmd` `` — shell runs at load time, output replaces the placeholder (Claude never sees the command); multi-line via a fence opened with ```` ```! ````.
- `@path` — embed a file's content.
- `${CLAUDE_SKILL_DIR}` — directory containing SKILL.md; use for bundled script paths. `${CLAUDE_PROJECT_DIR}` — project root.

## Hard limits

- `name`: `^[a-z0-9]+(-[a-z0-9]+)*$`, ≤64 chars, must not contain "claude" or "anthropic", must match the directory/file name.
- `description`: ≤1024 chars (listings truncate around 1536 combined with `when_to_use` — front-load the key use case).
- Body ≤500 lines; supporting files one level deep; TOC for reference files past ~100 lines.
