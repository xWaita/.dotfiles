---
name: market-wrap
description: Research and write a global cross-asset market wrap (equities, rates, FX, commodities, crypto, volatility/credit, market-moving events, 7-day economic calendar, outlook with scored calls) as a dated HTML file in a base folder, and keep that folder's index of wraps. `--schedule` sets up a daily run. Manual only; run with /market-wrap <base-dir> [--schedule].
argument-hint: "<base-dir> [--schedule]"
disable-model-invocation: true
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Agent, CronCreate, CronList, CronDelete]
---

# Market Wrap

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Arguments: $ARGUMENTS

Paths `scripts/`, `assets/`, `references/` below are relative to this skill's directory; pass them to Bash as absolute paths. Run every script with `python3 -I`.

## `<base-dir> --schedule` — set up the daily run

This creates the job only; it does not write a wrap now.

1. Resolve `<base-dir>` to an absolute path. The cron is always `7 22 * * *`: 22:07 local time (UTC here), after the US close. Saturday and Sunday runs produce the weekend edition by themselves.
2. `CronList`: if a job's prompt is already `/market-wrap <same dir>`, report it and stop.
3. `CronCreate` with `recurring: true` and the prompt `/market-wrap <abs base-dir>`.
4. Report the next fire time from the result, and these limits:
   - The job lives only in this session.
   - It fires only while the session is idle.
   - It expires after 7 days; re-run with `--schedule` weekly to renew it.

## `<base-dir>` — write a wrap

1. **Setup.**
   - Resolve the base dir and `mkdir -p` it. The as-of `date` is `date -u +%F`.
   - The edition follows the as-of date: `weekday` Mon–Fri, `weekend` Sat–Sun.
   - The data dir is `<base>/data/<date>/`.
2. **Prices.** Run `scripts/fetch_markets.py --out <data>/markets.json`. Its table is the price truth for the wrap. If it exits non-zero, every price must come from research instead: tag those rows "web" via `extra_rows` and tell the user.
3. **History.** Run `scripts/wrap.py history <base> --before <date>`.
   - `previous.wrap_data.calls` are the calls to score.
   - `previous.wrap_data.outlook_events` holds the event and scenario ids to reuse for events that carry over; `render` then shows each probability's change.
   - When `previous` is a legacy wrap, `wrap_data` is null: Read that file and take its outlook and predictions from the text.
   - Existing files are never edited, renamed or deleted. A file for today under another name stays; this run writes `market-wrap-<date>.html` alongside it.
4. **Research.** Read `references/research.md`. Spawn its lanes for this edition as parallel subagents in one message. Then run its coordinator checks.
5. **Write.** Read `references/report.md`, then write `<data>/content.json` to its contract. Score the previous calls against `markets.json` and the lane notes.
6. **Render.** Run `scripts/wrap.py render --markets <data>/markets.json --content <data>/content.json --out <base>/market-wrap-<date>.html`. If it reports contract violations, fix `content.json` and re-run. A re-run on the same date overwrites that file and nothing else.
7. **Index.** Run `scripts/wrap.py index <base>`.
8. **Report.** Reply with the file path, the headline, the takeaways, and the scorecard tally.

## Gotchas

- Yahoo answers 429 to a full browser User-Agent; `fetch_markets.py` sends a bare `Mozilla/5.0`. If every Yahoo symbol fails anyway, it is rate limiting: wait a minute and re-run once.
- Session dates differ by market. The dashboard tags any row whose session date is older than most, so a stale close is never presented as today's.
- Futures (`=F`) are Yahoo's continuous contract, which rolls to the next month before expiry. News may quote the expiring contract's settle, which can differ by dollars. Keep the dashboard's figure, and name the contract in prose when the two diverge. The dashboard tags rolled rows "roll": their 1W/1M/YTD and sparkline mix two contracts. Their 1D is Yahoo's own day change on the new contract, which is correct even when it disagrees with the sparkline.
- Non-US yields, the UST 2Y and single stocks are not in the watchlist. They come from the `macro-rates-fx` and `equities` lanes and render as `extra_rows`.
- To change the watchlist, edit `WATCHLIST` in `scripts/fetch_markets.py`. The index columns are `INDEX_KEYS` in `scripts/wrap.py`. Page styling lives in `assets/wrap.css`, shared by every wrap and the index.
