# Research lanes

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read before spawning lane agents. Each lane is one `general-purpose` subagent, and all lanes start in one message so they run in parallel. Fill the prompt template below once per lane.

## Lanes by edition

| Lane | Weekday | Weekend | Covers |
|---|---|---|---|
| `equities` | yes | — | Session moves by region (US, Europe, Japan, China/HK, Korea, India, EM) with drivers; sector and factor rotation; biggest single-stock movers and earnings reactions |
| `macro-rates-fx` | yes | — | Data released vs consensus; central bank decisions, minutes, speakers; UST 2Y and curve, Bund, Gilt, JGB 10Y levels and bp changes; FX drivers; IG/HY spreads |
| `commodities` | yes | — | Energy (OPEC+, inventories, sanctions, supply outages), gold and silver drivers (real yields, central bank buying), copper/industrial metals, ags only when moving |
| `crypto` | yes | yes | BTC/ETH/SOL and notable alts with causes; spot ETF flows; regulation and policy; exchange, stablecoin and hack news; funding rates, open interest, liquidations |
| `calendar` | yes | yes | Next 7 days, only what `calendar.json` lacks: the earnings that matter this week (any listing) with EPS consensus and year-ago EPS, elections and geopolitical dates, OPEC+ meetings, policy dates such as Treasury refunding, token unlocks and network upgrades. When `fetch_calendar.py` failed, the whole economic calendar too |
| `weekend-news` | — | yes | Since Friday's close: policy, geopolitics, macro and corporate news that moves Monday's open, including energy and metals |

## Prompt template

```
Research the {lane} lane of a global market wrap for {as-of date} ({edition} edition).

Covers: {lane row from the table above}
Window: {weekday: the latest trading session, which ended {session date} | weekend: since Friday's close on {date}} — Calendar lane: {as-of date} through {as-of date + 7}.

Exact prices for the watchlist are already in {markets.json path}. Read it, and use it to see which moves need explaining. Do not research prices it has. Find what it lacks (see Covers) and why things moved.
{calendar lane only: The economic calendar is already in {calendar.json path} (or: the fetch failed). Do not re-research its rows. Give each row you find under `## Facts` with date, UTC time, region, consensus and prior.}

Previous wrap's outlook and calls, for continuity: {summary from wrap.py history, or "none"}

Write notes to {base}/data/{date}/{lane}.md:
- `## Facts`: one bullet per fact, with number and unit, then the source as [publisher, YYYY-MM-DD](url).
- `## Drivers`: what moved, why, and who reported it.
- `## Watch`: what matters for the next session or week. For each catalyst give its date (or "ongoing") and the assets it would hit hardest.
- `## Gaps`: what you looked for and could not confirm.

Rules: use sources dated inside the window; label single-source or unconfirmed reports; never estimate a number; stop at ~15 searches. Keep the notes under ~80 lines: one line per fact, no restated prices, keep only what a desk brief would use. Reply with a 3-line summary only.
```

## Sources to prefer

- Breaking news and moves: Reuters, AP, CNBC, Bloomberg/FT headlines, MarketWatch, Nikkei Asia, SCMP.
- Data and calendars: national statistics agencies, central bank sites, company investor-relations pages for earnings dates, Investing.com and TradingEconomics pages via search.
- Rates: Treasury.gov, Bundesbank, Bank of England, MoF Japan, CNBC bond quotes for 2Y/Bund/Gilt/JGB levels.
- Energy: EIA, OPEC, IEA. Crypto: CoinDesk, The Block, Farside (ETF flows), CoinGlass (derivatives).

## Coordinator checks after lanes return

- Compare each lane's numbers with `markets.json`. Where they conflict, `markets.json` wins.
- Choose the outlook's 2–4 events from the lanes' `## Watch` sections, `calendar.json` and the calendar lane's rows.
- When a lane's `## Gaps` names a fact the wrap needs (a central bank decision, a headline mover's cause), run one targeted search yourself. Do not re-spawn the lane.
