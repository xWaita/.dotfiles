"""Block until a forked review agent finishes, then print its id and its report.

Usage: await-review.py (<agent_id> | --tag <tag>) [timeout_seconds]

`--tag` finds the fork by a string its caller put in the review arguments,
which open the fork's transcript. A fork finishes with an end_turn, with the
StructuredOutput call its own instructions may demand, or, when a message
resumed it, with a SubagentHandback call that carries the report.

Prints `agent: <id>` and then the report. Exit 0 on success, 124 on timeout
(re-run it), 2 when no transcript matches yet.
"""

import glob
import json
import os
import sys
import time

_SUBAGENTS = "~/.claude/projects/*/*/subagents"


def _records(path: str) -> list[dict]:
    """Conversation records of a transcript, skipping a line still being written."""
    records = []
    with open(path) as f:
        for line in f:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("type") in ("assistant", "user"):
                records.append(record)
    return records


def _blocks(record: dict) -> list[dict]:
    """Content blocks of a record, empty when its content is a plain string."""
    content = (record.get("message") or {}).get("content")
    return content if isinstance(content, list) else []


def find_by_tag(tag: str) -> str | None:
    """Path of the newest fork transcript whose opening prompt holds `tag`."""
    paths = glob.glob(os.path.expanduser(f"{_SUBAGENTS}/agent-*.jsonl"))
    for path in sorted(paths, key=os.path.getmtime, reverse=True):
        with open(path) as f:
            if tag in f.readline():
                return path
    return None


def finished_text(path: str) -> str | None:
    """Return the fork's report when its transcript shows it finished, else None."""
    records = _records(path)
    if not records:
        return None
    text = ""
    closing = {}  # id of a tool call that ends the run -> the report it ends with
    for record in records:
        if record["type"] != "assistant":
            continue
        for block in _blocks(record):
            if block.get("type") == "text" and block["text"].strip():
                text = block["text"]
            elif (
                block.get("type") == "tool_use"
                and block.get("name") == "StructuredOutput"
            ):
                closing[block["id"]] = text
            elif (
                block.get("type") == "tool_use"
                and block.get("name") == "SubagentHandback"
            ):
                closing[block["id"]] = block["input"].get("message") or text
    last = records[-1]
    if last["type"] == "assistant":
        return text if last["message"].get("stop_reason") == "end_turn" else None
    for block in _blocks(last):
        if block.get("type") == "tool_result" and block.get("tool_use_id") in closing:
            return closing[block["tool_use_id"]]
    return None


def main() -> int:
    """Wait for the fork named on the command line and print its report."""
    args = sys.argv[1:]
    tag = pattern = None
    if args[0] == "--tag":
        tag, args = args[1], args[2:]
    else:
        pattern = os.path.expanduser(f"{_SUBAGENTS}/agent-{args[0]}.jsonl")
        args = args[1:]
    deadline = time.monotonic() + (float(args[0]) if args else 570)
    path = None
    while time.monotonic() < deadline:
        path = path or (
            find_by_tag(tag) if tag else next(iter(glob.glob(pattern)), None)
        )
        if path and (text := finished_text(path)) is not None:
            agent_id = (
                os.path.basename(path).removeprefix("agent-").removesuffix(".jsonl")
            )
            print(f"agent: {agent_id}")
            print(text)
            return 0
        time.sleep(5)
    return 124 if path else 2


if __name__ == "__main__":
    sys.exit(main())
