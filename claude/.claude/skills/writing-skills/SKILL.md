---
name: writing-skills
description: Write, update, or review Claude Code skills and slash commands. Trigger on "write a skill", "create a slash command", "new command", "update/edit a skill", frontmatter questions, or any edit to SKILL.md files or files under ~/.claude/skills.
argument-hint: skill/command to create or update
---

# Writing Skills & Slash Commands

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

## Workflow

1. **Research first.** Read 1–2 existing artifacts in the target scope for house conventions; read `references/format.md` when using anything beyond name/description/argument-hint/allowed-tools. For domain skills, gather the non-obvious facts (docs, code, command output) the skill must encode — a skill is only worth the tokens it saves.
2. **Choose the form** (see Choosing the shape).
3. **Draft `name` + `description` first** — they are the only preloaded surface; the body loads only on invocation.
4. **Write the body** (rules below).
5. **Bundle scripts** for fragile or recurring mechanical steps (see scripts/).
6. **Validate:** run `python3 ${CLAUDE_SKILL_DIR}/scripts/validate.py <path>`; no args sweeps all user-level skills.
7. **Test:** invoke via `/name`; sanity-check auto-triggering by matching the description against phrasings a user would actually type.

## Placement

- Every artifact is a skill directory: `~/.claude/skills/<name>/SKILL.md`. Project-level `.claude/skills/…` only when asked. Claude Code still accepts single-file `commands/<name>.md`, but this setup keeps everything as skill dirs — one form, one place — so a manual slash-only workflow is just a skill with `disable-model-invocation: true`, not a separate command file.
- `~/.claude/skills` symlinks into `~/.dotfiles/claude/.claude/`. Write via `~/.claude` paths, then commit everything — SKILL.md, references, and scripts alike — in `~/.dotfiles` (new files stay untracked until committed).

## Choosing the shape

Skills and commands are one system: a single `SKILL.md` whose frontmatter sets how it's invoked (see the invocation matrix in `references/format.md`).

- Default (no guard) — both auto-triggers from `description` and runs on `/name`.
- Manual `/name` only → `disable-model-invocation: true`. This is the old bare-command form; use it for side-effecting workflows the user should time (e.g. `/ralph`) and `\$ARGUMENTS`-driven prompts.
- Background knowledge with no `/` entry → `user-invocable: false`.

A plain prompt body is still just a `SKILL.md`; add `references/`/`scripts/` subdirs only when the skill needs bundled docs or executables.

## Writing the description

- ≤1024 chars, third person: what it does, then "Use when / Trigger on …" with the concrete words a user would type (quote them).
- Include filename and path triggers (e.g. `SKILL.md`, `PRD.md`) — they fire when work touches those files.
- Never rely on the body for triggering; it isn't loaded yet.

## Writing the body

- Imperative bullets under `#`/`##`; explain why instead of shouting MUST.
- Assume Claude is smart: encode only non-obvious decisions, contracts, and gotchas. The context window is a public good — ≤500 lines hard, ~150 soft.
- Match freedom to fragility: prose for judgment calls, exact commands or scripts for fragile operations.
- No time-sensitive facts; write for the file's whole lifetime.
- Bodies get token substitution at load time — escape literal mentions of tokens, e.g. `\$ARGUMENTS`.
- Required in every authored artifact, immediately under the H1 (or, for a prompt-style body with no H1, as an HTML comment at the top):

  > Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

## scripts/

- When a session produces a throwaway script this workflow will need again, persist it into the owning skill's `scripts/` dir and reference it from the body as "Run `${CLAUDE_SKILL_DIR}/scripts/<script>` …" — "Run" means execute; "See" means read as reference.
- Maintain scripts like code: when one fails or the workflow drifts, fix it in place — the self-describing rule applied to code. Version-control them in `~/.dotfiles` like every other skill file.
- Prefer stdlib-only Python with Google-style docstrings.

## references/

- One level deep, linked from SKILL.md with a when-to-read instruction; never inline their content.
- Split lookup material out of SKILL.md once it isn't needed on every invocation; add a TOC past ~100 lines.

## Heavyweight authoring

For evals across models, benchmarking, description tuning, or packaging a skill for distribution, install the official plugin: `/plugin install skill-creator@claude-plugins-official`. This skill covers the lean everyday path.

## Checklist

- [ ] Researched conventions and domain before drafting
- [ ] `name` kebab-case, ≤64 chars, no "claude"/"anthropic", matches its directory name
- [ ] `description` third person with concrete triggers, ≤1024 chars
- [ ] Self-describing + style note under the H1
- [ ] Body concise (≤500 hard, ~150 soft), no time-sensitive facts
- [ ] Recurring temp scripts persisted into `scripts/` and referenced with "Run"
- [ ] `validate.py` passes clean
- [ ] Committed in `~/.dotfiles`
