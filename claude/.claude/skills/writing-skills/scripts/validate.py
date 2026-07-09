#!/usr/bin/env python3
"""Structurally validate Claude Code skills.

Usage: ``validate.py [PATH ...]`` where each PATH is a skill directory, a
SKILL.md, or a plain ``.md`` file; with no args, sweeps ``~/.claude/skills``.
Prints ``ERROR|WARN <path>: <msg>`` lines plus a summary, and exits 0 (clean),
1 (errors found), or 2 (bad usage or unreadable path).

Frontmatter is parsed line-wise (flat ``key: value`` pairs; indented or list
lines continue the previous key), not as full YAML.
"""

import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")
BUNDLED_PATH_RE = re.compile(
    r"\b((?:references|scripts)/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*)"
)
RESERVED = ("claude", "anthropic")
KNOWN_KEYS = {
    "name", "description", "when_to_use", "argument-hint", "arguments",
    "allowed-tools", "disallowed-tools", "model", "effort",
    "disable-model-invocation", "user-invocable", "context", "agent",
    "hooks", "paths", "shell", "license", "version",
}
TRIGGER_CUES = ("use when", "trigger", "use this")
MARKER = "Self-describing:"
MAX_NAME, MAX_DESC, MAX_BODY, SOFT_BODY = 64, 1024, 500, 150


class Artifact:
    """One SKILL.md or command .md parsed into frontmatter and body."""

    def __init__(self, path, expected_name, is_skill):
        self.path = path
        self.expected_name = expected_name
        self.is_skill = is_skill
        self.meta = {}
        self.opened = False
        self.terminated = False
        self.body = ""
        self._parse(path.read_text(encoding="utf-8"))

    def _parse(self, text):
        lines = text.splitlines()
        self.opened = bool(lines) and lines[0].strip() == "---"
        if not self.opened:
            self.body = text
            return
        key = None
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                self.terminated = True
                self.body = "\n".join(lines[i + 1:])
                return
            if m := KEY_RE.match(line):
                key, self.meta[m[1]] = m[1], m[2]
            elif key and line.strip():
                self.meta[key] += " " + line.strip()

    def body_line_count(self):
        """Number of lines after the frontmatter block."""
        return len(self.body.splitlines())

    def missing_bundled_paths(self):
        """Bundled references/ or scripts/ paths mentioned in the body but absent on disk."""
        root = self.path.parent
        return [p for p in BUNDLED_PATH_RE.findall(self.body)
                if not (root / p).exists()]

    def is_manual_only(self):
        """True when frontmatter opts out of model invocation (manual /name only)."""
        return self.meta.get("disable-model-invocation", "").strip().lower() in ("true", "yes", "1")


def check(art):
    """Return (level, message) findings for one parsed artifact."""
    findings = []
    if not art.opened:
        findings.append(("ERROR", "missing frontmatter block"))
    elif not art.terminated:
        findings.append(("ERROR", "unterminated frontmatter block"))

    name = art.meta.get("name", art.expected_name)
    if not NAME_RE.fullmatch(name):
        findings.append(("ERROR", f"name {name!r} is not kebab-case"))
    if len(name) > MAX_NAME:
        findings.append(("ERROR", f"name exceeds {MAX_NAME} chars"))
    if any(w in name.lower() for w in RESERVED):
        findings.append(("ERROR", f"name {name!r} contains a reserved word"))
    if name != art.expected_name:
        findings.append(("ERROR",
                         f"name {name!r} does not match directory/file name"
                         f" {art.expected_name!r}"))

    if not (desc := art.meta.get("description", "").strip()):
        findings.append(("ERROR", "description missing or empty"))
    else:
        if len(desc) > MAX_DESC:
            findings.append(("ERROR", f"description exceeds {MAX_DESC} chars"))
        if art.is_skill and not art.is_manual_only() \
                and not any(c in desc.lower() for c in TRIGGER_CUES):
            findings.append(("WARN",
                             "description has no trigger cue"
                             " (Use when / Trigger / use this)"))

    if (n := art.body_line_count()) > MAX_BODY:
        findings.append(("ERROR", f"body has {n} lines (max {MAX_BODY})"))
    elif n > SOFT_BODY:
        findings.append(("WARN", f"body has {n} lines (aim under {SOFT_BODY})"))

    for key in art.meta:
        if key not in KNOWN_KEYS:
            findings.append(("WARN", f"unknown frontmatter key {key!r}"))
    if MARKER not in art.body:
        findings.append(("WARN", f"missing {MARKER!r} marker"))
    if art.is_skill:
        for p in art.missing_bundled_paths():
            findings.append(("ERROR", f"body references {p!r} which does not exist"))
    return findings


def check_skill_dir(skill_dir):
    """Findings for skill-directory structure (reference nesting depth)."""
    refs = skill_dir / "references"
    if refs.is_dir() and any(p.is_dir() for p in refs.iterdir()):
        return [("ERROR", "references/ contains nested directories (keep one level deep)")]
    return []


def resolve_target(raw):
    """Map one CLI path to a (kind, md_path, expected_name, skill_dir) target."""
    p = Path(raw).expanduser()
    if p.is_dir():
        return ("skill", p / "SKILL.md", p.name, p)
    if p.is_file() and p.suffix == ".md":
        if p.name == "SKILL.md":
            return ("skill", p, p.parent.name, p.parent)
        return ("command", p, p.stem, None)
    print(f"validate.py: not a skill directory or .md file: {raw}", file=sys.stderr)
    sys.exit(2)


def default_targets():
    """Sweep every user-level skill."""
    targets = []
    skills = Path.home() / ".claude" / "skills"
    if skills.is_dir():
        for d in sorted(p for p in skills.iterdir() if p.is_dir()):
            targets.append(("skill", d / "SKILL.md", d.name, d))
    return targets


def main(argv):
    """Validate all targets and report; return the process exit code."""
    targets = [resolve_target(raw) for raw in argv] if argv else default_targets()
    errors = warnings = 0
    for kind, md_path, expected_name, skill_dir in targets:
        findings = []
        if not md_path.is_file():
            findings.append(("ERROR", "SKILL.md missing"))
        else:
            try:
                findings += check(Artifact(md_path, expected_name, kind == "skill"))
            except OSError as e:
                print(f"validate.py: cannot read {md_path}: {e}", file=sys.stderr)
                sys.exit(2)
        if skill_dir is not None:
            findings += check_skill_dir(skill_dir)
        for level, msg in findings:
            print(f"{level} {md_path}: {msg}")
            errors += level == "ERROR"
            warnings += level == "WARN"
    print(f"{errors} errors, {warnings} warnings across {len(targets)} file(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
