# Report: content.json contract and writing rules

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read before writing `content.json`. `scripts/wrap.py render` builds the page from this file and `markets.json`. The script lays out the masthead, session strip, cross-asset dashboard, sparklines and the `wrap-data` block from `markets.json`, so content.json never restates a price the script already has. `render` rejects a file that breaks this contract and lists every problem; fix them all and re-run.

## Fields

Fields named `*_html` and `takeaways` items are inserted as raw HTML: use `<p>`, `<ul>`, `<b>`, `<em>`, `<a>`, and escape `&` as `&amp;`. Every other string is plain text and is escaped by the script.

```json
{
  "date": "2026-10-16",
  "edition": "weekday",
  "headline": "Tech slide drags Wall Street lower as oil tops $110",
  "dek": "One sentence: the session's story and why it matters.",
  "takeaways": ["<b>Nasdaq 100 −2.50%</b>: ...", "..."],
  "sections": [
    {"id": "equities", "title": "Equities", "body_html": "<p>...</p>",
     "extra_rows": [{"label": "Nvidia", "value": "$184.20", "change": "−6.1%", "direction": "down", "note": "guidance cut"}]}
  ],
  "events": [{"title": "Fed's Waller signals December cut", "impact": "high", "body_html": "<p>What happened. What it means.</p>"}],
  "calendar": [{"date": "2026-10-19", "time_utc": "02:00", "region": "CN", "event": "Q3 GDP y/y",
                "consensus": "4.6%", "prior": "4.8%", "importance": "high"}],
  "outlook": {
    "horizon": "Week of 19 Oct",
    "summary_html": "<p>...</p>",
    "net": [{"key": "BRENT", "lean": "up", "event": "hormuz", "level": "$110", "why": "Friday's high; a close above opens $126"},
            {"label": "JGB 10Y", "lean": "up", "event": "japan-cpi", "level": "3.00%", "why": "..."}],
    "events": [{
      "id": "hormuz", "title": "Strait of Hormuz attacks", "when": "ongoing", "time_utc": "",
      "resolves": "a verified supply loss, or a pause agreed in talks", "why": "One line: the exposure and why now.",
      "scenarios": [
        {"id": "harassment", "name": "Harassment, no supply loss", "probability": "55%", "body_html": "<p>...</p>"},
        {"id": "supply-hit", "name": "Confirmed supply hit", "probability": "30%", "body_html": "..."},
        {"id": "de-escalation", "name": "De-escalation", "probability": "15%", "body_html": "..."}],
      "assets": [
        {"key": "BRENT", "moves": {"harassment": {"dir": "flat", "target": "$105–112"},
                                   "supply-hit": {"dir": "up", "target": "$115–126"},
                                   "de-escalation": {"dir": "down", "target": "<$105"}}},
        {"label": "Brent 1–6M spread", "moves": {"...": "..."}}]}],
    "calls": [{"id": "20261016-1", "text": "Brent holds $105 into Friday", "horizon": "week",
               "check": "BRENT >= 105 on 2026-10-23", "event": "hormuz"}]
  },
  "scorecard": {"wrap_date": "2026-10-15", "items": [
    {"id": "20261015-2", "text": "Brent above $105", "result": "hit", "note": "Closed 109.86, +3.72%"},
    {"id": "20261013-1", "text": "...", "result": "pending", "note": "Resolves Fri", "horizon": "week", "check": "..."}]},
  "sources": [{"title": "Stocks fall as chip rout deepens", "url": "https://...", "publisher": "Reuters", "date": "2026-10-16"}]
}
```

- `date`: the as-of date (UTC date of the run). `edition`: `weekday` or `weekend`.
- `takeaways`: 3–5 items. Each leads with the instrument and move in bold, then the reason.
- `sections`: order them Equities, Rates, FX, Commodities, Crypto, Volatility & credit. On a weekend edition, use Crypto, then one Weekend news section, and skip the rest. `extra_rows` hold only data `markets.json` lacks — non-US yields, the UST 2Y, sector or single-stock moves, ETF flows, funding rates. Each `extra_rows` entry renders tagged "web" under the columns Item / Level / Change / Note. An entry needs `value` (the level) or `change`, or both. `change` is 1D unless suffixed with its period (`+12bp 1W`). `direction` is `up`, `down` or `flat`, and the `change` text keeps its sign.
- `events`: 2–6, impact `high`/`medium`/`low`. An event is something that happened; scheduled releases go in `calendar`.
- `calendar`: the as-of date through as-of + 7 days, every high-importance release plus the medium ones the outlook relies on. `time_utc` is `HH:MM` UTC, or empty when unconfirmed; the page converts timed rows to the reader's chosen zone (Sydney by default), and untimed rows keep their listed date. `region` is a code from `REGIONS` in `scripts/wrap.py` (US, UK, EZ, CN, JP, …), shown with its full name on hover; for any other region add `region_name`. `consensus`/`prior` are empty when no figure applies (meetings, auctions). For earnings, `consensus` is EPS consensus and `prior` is year-ago EPS. When sources disagree on consensus, give the range (`$6.11–6.35`). Mark single-source or doubtful items in the event text (`(unconfirmed)`).
- `outlook.events`: the 2–4 catalysts that would most change prices over the horizon, scheduled (a release, earnings, a meeting) or ongoing (a conflict, a credit scare). Pick them from the lanes' `## Watch` sections and the calendar. Each renders as its own block.
  - `id` is kebab-case. While an event carries over from the previous wrap (`history` → `previous.wrap_data.outlook_events`), reuse its `id` and its scenario ids so the page shows each probability's change. Drop an event once it resolves.
  - `when` is `YYYY-MM-DD` or `ongoing`; `time_utc` is `HH:MM` or empty. `resolves` says what settles the event (required for `ongoing`). `why` is one line on the exposure.
- `scenarios`: exactly 3 per event, most likely first, probabilities summing to 100%. Each is conditional on that event alone — interactions between events go in `net` and the summary. Name each by what happens; `Base`/`Bull`/`Bear` are rejected. `body_html` is 1–2 sentences: what happens, then what confirms it.
- `assets`: the 2–5 instruments the event moves most, and only those. A `markets.json` `key` shows its current level; use `label` for anything outside the watchlist (JGB 10Y, a single stock). `moves` has a cell per scenario id: `dir` is `up`, `down` or `flat` (for yields, `up` means yields rise); `target` is an optional level or range in the instrument's units.
- `outlook.net`: 3–8 rows, the bottom line per asset across all events. `lean` is `up`, `down`, `flat` or `two-way`, judged by hand from the events' skew, not computed. `event` is the id of the event that drives it. `level` is the line to watch and `why` says what kind of level it is (technical, round number, event).
- `outlook.calls`: 3–5. Tag each with the `event` id it rests on when there is one. Write `check` as a test the next run can settle from the next `markets.json` or a cited source: `<KEY> <op> <level> on <YYYY-MM-DD>`, using a `markets.json` key where one exists. The date is the next session for a `next session` horizon and the last trading day of the coming week for `week`. The `id` is `<YYYYMMDD>-<n>`.
- `scorecard`: score every call in the previous wrap's `wrap-data.calls`. Omit it when there is no previous wrap. For a legacy wrap, score the outlook claims you can find in its text, with ids `legacy-<n>`. A result is `hit`, `miss`, `pending` (horizon not reached; `horizon` and `check` are required, so the call carries forward) or `void` (made untestable by events). The note cites the deciding number.
- `sources`: every URL the notes cited that the wrap relies on, with `publisher` and `date` whenever known.

## Writing rules

- Every number is exact and has a unit: `−2.50%`, `+14bp`, `$109.86`, `5.098%`. Use the minus sign `−` in prose.
- Prices come from `markets.json`. Its `chg_*` fields are bp for `unit: yield` rows and % otherwise. A figure it lacks comes from the lane notes with a source; never estimate one.
- When sources conflict on a figure, prefer the primary source (statistics agency, central bank, exchange). If there is none, use the most recent, and name the other figure in the row's note or the prose.
- Run time decides which quotes are current. Crypto and weekend FX are live at run time; other rows are their last close.- Explain moves by attributing them to a reported cause ("on the CPI beat", "after Nvidia's guidance"). A move with no reported cause is described, not explained.
- Desk-brief register: lead with the conclusion, one idea per sentence, no throat-clearing ("markets were mixed today as investors…"). Flag unconfirmed reports as such.
- Use the same name for each instrument the dashboard uses.
- Weekend edition: legacy markets are closed. Say so once, mark Friday closes as Friday's, and put the weight on crypto, weekend news and the week-ahead calendar.
- The outlook contains views, and every view is tied to a level, a date or a catalyst. Scenarios name what would confirm each one. `summary_html` names the events and how they interact.
