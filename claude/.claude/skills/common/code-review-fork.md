# Driving code-review from an agent

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

How a workflow agent runs the `code-review` skill and gets its findings back. The caller supplies the arguments and decides what to do with the findings.

1. Invoke `code-review` through the Skill tool, naming the effort level explicitly — an omitted level reuses whatever was typed last. Do not pass `--fix`; fixing, formatting and testing stay with the caller.
2. The skill forks a background agent named `code-review` and returns at once. Its completion notice goes to the main session, never to you, and ending your turn ends this agent, so wait for it as below.
3. SendMessage the fork straight away: `Write your findings as a text message, a JSON array of {file, line, summary, failure_scenario}, before any StructuredOutput call.` Its own instructions may demand one StructuredOutput call, which takes your schema and carries no findings, so only that text reaches you. When `code-review` still resolves to an earlier fork, the refusal names the new one's ref; send to `code-review [<ref>]`.
4. The send result's `pin.id` is the fork's agent id. Run `python3 scripts/await-review.py <id>` (relative to this file) with a 600000 ms Bash timeout. It prints the fork's last text once it finishes, and exits 124 on its own timeout or 2 before the transcript exists — run it again until it exits 0. When that text holds no findings list, SendMessage the fork for it and run the script again.
5. Never wait on `ReportFindings`, which the fork does not call, nor pick a transcript by recency, which finds an earlier review.
