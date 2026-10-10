"""Block until a forked review agent finishes, then print its last text message.

Usage: await-review.py <agent_id> [timeout_seconds]

A fork finishes either with an end_turn or with the StructuredOutput call its
own instructions may demand, which leaves a tool result as the last record.
Exit 0 with the text on stdout, 124 on timeout (re-run it), 2 when no
transcript for the id exists yet.
"""

import glob
import json
import os
import sys
import time


def finished_text(path: str) -> str | None:
    """Return the fork's last text when its transcript shows it finished, else None."""
    last = None
    structured_ids = set()
    text = ""
    with open(path) as f:
        for line in f:
            record = json.loads(line)
            if record.get("type") not in ("assistant", "user"):
                continue
            last = record
            content = (record.get("message") or {}).get("content")
            if record["type"] != "assistant" or not isinstance(content, list):
                continue
            for block in content:
                if block.get("type") == "text" and block["text"].strip():
                    text = block["text"]
                elif block.get("type") == "tool_use" and block.get("name") == "StructuredOutput":
                    structured_ids.add(block["id"])
    if last is None:
        return None
    message = last.get("message") or {}
    if last["type"] == "assistant":
        return text if message.get("stop_reason") == "end_turn" else None
    content = message.get("content")
    answered = isinstance(content, list) and any(
        b.get("type") == "tool_result" and b.get("tool_use_id") in structured_ids for b in content
    )
    return text if answered else None


def main() -> int:
    agent_id = sys.argv[1]
    deadline = time.monotonic() + (float(sys.argv[2]) if len(sys.argv) > 2 else 570)
    pattern = os.path.expanduser(f"~/.claude/projects/*/*/subagents/agent-{agent_id}.jsonl")
    while time.monotonic() < deadline:
        paths = glob.glob(pattern)
        if paths and (text := finished_text(paths[0])) is not None:
            print(text)
            return 0
        time.sleep(10)
    return 124 if glob.glob(pattern) else 2


if __name__ == "__main__":
    sys.exit(main())
