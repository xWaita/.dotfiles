"""Summarise a refine ledger as a per-round table of findings and plan growth.

Reads REFINE.md and prints the markdown table the run report ends with, plus
five-round means of the blocking count — the trend that says whether the loop
is converging or holding at a rate its own edits sustain.
"""

import argparse
import re
import sys

ROUND = re.compile(r"^## Round (\d+)(?: · (.*))?$")
GROWTH = re.compile(r"(\d+)→(\d+) lines")
ENTRY = re.compile(r"^- F\d+ · (CRITICAL|HIGH|MEDIUM|LOW) \([^)]*\) · (applied|declined|conflict)")
SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
BLOCK = 5


def parse(text):
    """Return one dict per round section of a ledger, in file order."""
    rounds = []
    for line in text.splitlines():
        if header := ROUND.match(line):
            spans = GROWTH.findall(header.group(2) or "")
            rounds.append(
                {
                    "n": int(header.group(1)),
                    "before": sum(int(a) for a, _ in spans),
                    "after": sum(int(b) for _, b in spans),
                    "severities": [],
                    "statuses": [],
                }
            )
        elif (entry := ENTRY.match(line)) and rounds:
            rounds[-1]["severities"].append(entry.group(1))
            rounds[-1]["statuses"].append(entry.group(2))
    return rounds


def render(rounds):
    """Return the markdown table and its trailing summary lines."""
    out = [
        "| Round | C | H | M | L | Total | Blocking | Applied | Declined | Cumulative | Lines | Δ |",
        "|------:|--:|--:|--:|--:|------:|---------:|--------:|---------:|-----------:|------:|--:|",
    ]
    cumulative = conflicts = 0
    blocking_by_round = []
    for r in rounds:
        counts = [r["severities"].count(s) for s in SEVERITIES]
        blocking = sum(counts[:3])
        blocking_by_round.append(blocking)
        applied = r["statuses"].count("applied")
        conflicts += r["statuses"].count("conflict")
        cumulative += len(r["severities"])
        lines = str(r["after"]) if r["after"] else "—"
        delta = f"{r['after'] - r['before']:+d}" if r["after"] else "—"
        out.append(
            f"| {r['n']} | {counts[0]} | {counts[1]} | {counts[2]} | {counts[3]} "
            f"| {len(r['severities'])} | {blocking} | {applied} | {len(r['statuses']) - applied} "
            f"| {cumulative} | {lines} | {delta} |"
        )

    means = []
    for start in range(0, len(rounds), BLOCK):
        chunk = blocking_by_round[start : start + BLOCK]
        first, last = rounds[start]["n"], rounds[min(start + BLOCK, len(rounds)) - 1]["n"]
        means.append(f"{first}–{last} **{sum(chunk) / len(chunk):.1f}**")
    applied = sum(r["statuses"].count("applied") for r in rounds)
    out += [
        "",
        f"Blocking per round, {BLOCK}-round means: " + ", ".join(means) + ".",
        f"{cumulative} findings raised, {applied} applied, {cumulative - applied - conflicts} declined, {conflicts} conflicts.",
    ]
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ledger", help="path to REFINE.md")
    args = parser.parse_args()
    with open(args.ledger) as handle:
        rounds = parse(handle.read())
    if not rounds:
        sys.exit(f"{args.ledger}: no round sections")
    print(render(rounds))


if __name__ == "__main__":
    main()
