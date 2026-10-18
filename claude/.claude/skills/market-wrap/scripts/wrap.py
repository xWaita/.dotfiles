#!/usr/bin/env python3
"""Render a market wrap page, and rebuild a base folder's index of wraps.

Usage:
  wrap.py render --markets <markets.json> --content <content.json> --out <file.html>
  wrap.py index <base-dir>
  wrap.py history <base-dir> [--before YYYY-MM-DD]

`render` validates content.json against the contract in references/report.md and
fails with every problem listed. `history` prints the wraps found, newest first,
with the latest earlier wrap's wrap-data (or its title for legacy files).
Stdlib only, run with ``python3 -I``.
"""

import argparse
import collections
import dataclasses
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

_ASSETS = Path(__file__).resolve().parent.parent / "assets"
_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_WRAP_DATA_RE = re.compile(r'<script type="application/json" id="wrap-data">(.*?)</script>', re.DOTALL)
_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL | re.IGNORECASE)
_SCHEMA = 2

_GROUPS = {
    "equity": "Equities",
    "rates": "US rates",
    "fx": "FX",
    "commodity": "Commodities",
    "crypto": "Crypto",
    "vol_credit": "Volatility & credit",
}
_SESSIONS = (
    ("Asia", "NIKKEI"),
    ("Europe", "STOXX600"),
    ("Americas", "SPX"),
    ("Crypto 24/7", "BTC"),
)
# Columns of the index's closes-over-time table, and of its trend tiles.
INDEX_KEYS = (
    "SPX",
    "NDX",
    "STOXX600",
    "NIKKEI",
    "US10Y",
    "DXY",
    "USDJPY",
    "BRENT",
    "GOLD",
    "BTC",
    "VIX",
)
_IMPORTANCE = {"high", "medium", "low"}
# Calendar region codes and their hover names; a code outside this map needs `region_name`.
REGIONS = {
    "US": "United States",
    "UK": "United Kingdom",
    "EZ": "Euro area",
    "DE": "Germany",
    "FR": "France",
    "IT": "Italy",
    "ES": "Spain",
    "CH": "Switzerland",
    "SE": "Sweden",
    "NO": "Norway",
    "JP": "Japan",
    "CN": "China",
    "HK": "Hong Kong",
    "KR": "South Korea",
    "TW": "Taiwan",
    "IN": "India",
    "ID": "Indonesia",
    "SG": "Singapore",
    "AU": "Australia",
    "NZ": "New Zealand",
    "CA": "Canada",
    "MX": "Mexico",
    "BR": "Brazil",
    "ZA": "South Africa",
    "TR": "Turkey",
    "RU": "Russia",
    "SA": "Saudi Arabia",
    "OPEC": "OPEC+",
    "Global": "Global",
    "Crypto": "Crypto markets",
}
# Server-rendered calendar zone; must match the default in the page's calendar script.
_CAL_DEFAULT_TZ = ZoneInfo("Australia/Sydney")
_RESULTS = {"hit", "miss", "pending", "void"}
_DIRS = {"up": "▲", "down": "▼", "flat": "▬"}
_LEANS = _DIRS | {"two-way": "⇅"}
_BANNED_SCENARIO_NAMES = {"base", "bull", "bear", "base case", "bull case", "bear case"}
_EDITIONS = {"weekday", "weekend"}
_SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_PCT_RE = re.compile(r"\s*(\d+(?:\.\d+)?)\s*%\s*")


class ContentError(Exception):
    """content.json breaks the contract; the message lists every problem."""


# ---------- formatting ----------


def esc(text: object) -> str:
    """HTML-escape a plain-text field."""
    return html.escape(str(text), quote=True)


def fmt_last(value: float, unit: str, asset_class: str) -> str:
    """Format a level: yields with %, big crypto with no decimals, FX-size with 4."""
    if unit == "yield":
        return f"{value:.3f}%"
    if asset_class == "crypto" and value >= 1000:
        return f"{value:,.0f}"
    if abs(value) < 10:
        return f"{value:,.4f}"
    return f"{value:,.2f}"


def direction(value: float | None) -> str:
    """CSS class for a change's sign."""
    if value is None or value == 0:
        return "flat"
    return "up" if value > 0 else "down"


def change_text(value: float | None, unit: str) -> str:
    """Signed change, bp for yields, % otherwise, with a true minus sign."""
    if value is None:
        return "—"
    text = f"{value:+.1f}bp" if unit == "yield" else f"{value:+.2f}%"
    return text.replace("-", "−")


def fmt_change(value: float | None, unit: str) -> str:
    """Signed change cell; the sign carries direction alongside the color."""
    return f'<td class="num {direction(value)}">{change_text(value, unit)}</td>'


def sparkline(values: list[float], width: int = 96, height: int = 24) -> str:
    """Inline SVG polyline with an endpoint dot, colored by first→last direction."""
    if len(values) < 2:
        return ""
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    pad = 3
    step = (width - 2 * pad) / (len(values) - 1)
    points = [
        (pad + i * step, pad + (height - 2 * pad) * (1 - (v - lo) / span)) for i, v in enumerate(values)
    ]
    path = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    cls = direction(values[-1] - values[0])
    ex, ey = points[-1]
    return (
        f'<svg class="{cls}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="trend {cls}">'
        f'<polyline points="{path}" fill="none" stroke="currentColor" stroke-width="1.5" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="2.5" fill="currentColor"/></svg>'
    )


def short_date(iso: str) -> str:
    """'2026-10-16' → '16 Oct'."""
    return dt.date.fromisoformat(iso).strftime("%-d %b")


def page_css() -> str:
    """The shared stylesheet inlined into every generated page."""
    return (_ASSETS / "wrap.css").read_text()


def fill(template: str, slots: dict[str, str]) -> str:
    """Replace every `<!--slot:name-->`; a slot left unfilled is a bug."""
    for name, value in slots.items():
        template = template.replace(f"<!--slot:{name}-->", value)
    if missing := re.findall(r"<!--slot:(\w+)-->", template):
        raise AssertionError(f"unfilled slots: {missing}")
    return template


def json_for_script(data: object) -> str:
    """JSON safe to embed inside a <script> element."""
    return json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")


# ---------- content contract ----------


def _require(obj: dict, keys: tuple[str, ...], where: str, errors: list[str]) -> None:
    for key in keys:
        if key not in obj or obj[key] in (None, ""):
            errors.append(f"{where}: missing '{key}'")


def _pct(text: object) -> float | None:
    return float(m.group(1)) if (m := _PCT_RE.fullmatch(str(text))) else None


def _validate_asset_ref(row: dict, market_keys: set[str], where: str, errors: list[str]) -> None:
    if row.get("key"):
        if row["key"] not in market_keys:
            errors.append(f"{where}.key: '{row['key']}' is not a markets.json key with data; use 'label'")
    elif not row.get("label"):
        errors.append(f"{where}: needs 'key' or 'label'")


def _validate_event(ev: dict, market_keys: set[str], where: str, errors: list[str]) -> None:
    _require(ev, ("id", "title", "when", "why", "scenarios", "assets"), where, errors)
    if ev.get("when") == "ongoing":
        _require(ev, ("resolves",), f"{where} (ongoing)", errors)
    else:
        try:
            dt.date.fromisoformat(str(ev.get("when")))
        except ValueError:
            errors.append(f"{where}.when: must be YYYY-MM-DD or 'ongoing'")
    if t := ev.get("time_utc"):
        try:
            dt.time.fromisoformat(t)
        except ValueError:
            errors.append(f"{where}.time_utc: must be HH:MM or empty")
    scenarios = ev.get("scenarios", [])
    if len(scenarios) != 3:
        errors.append(f"{where}.scenarios: need exactly 3")
    probs = []
    for j, sc in enumerate(scenarios):
        sw = f"{where}.scenarios[{j}]"
        _require(sc, ("id", "name", "probability", "body_html"), sw, errors)
        if not _SLUG_RE.fullmatch(str(sc.get("id", ""))):
            errors.append(f"{sw}.id: must be kebab-case")
        if str(sc.get("name", "")).strip().lower() in _BANNED_SCENARIO_NAMES:
            errors.append(f"{sw}.name: name the scenario by what happens, not Base/Bull/Bear")
        if (pct := _pct(sc.get("probability"))) is None:
            errors.append(f"{sw}.probability: must look like '55%'")
        else:
            probs.append(pct)
    if scenarios and len(probs) == len(scenarios):
        if abs(sum(probs) - 100) > 1:
            errors.append(f"{where}.scenarios: probabilities sum to {sum(probs):g}%, not 100%")
        if probs != sorted(probs, reverse=True):
            errors.append(f"{where}.scenarios: list them most likely first")
    sc_ids = [sc.get("id") for sc in scenarios]
    if len(set(sc_ids)) != len(sc_ids):
        errors.append(f"{where}.scenarios: duplicate ids")
    assets = ev.get("assets", [])
    if not 2 <= len(assets) <= 5:
        errors.append(f"{where}.assets: need 2–5")
    for k, a in enumerate(assets):
        aw = f"{where}.assets[{k}]"
        _validate_asset_ref(a, market_keys, aw, errors)
        moves = a.get("moves") or {}
        if extra := sorted(set(moves) - set(sc_ids)):
            errors.append(f"{aw}.moves: unknown scenario ids {extra}")
        for sid in sc_ids:
            if not (move := moves.get(sid)):
                errors.append(f"{aw}.moves: missing scenario '{sid}'")
            elif move.get("dir") not in _DIRS:
                errors.append(f"{aw}.moves.{sid}.dir: must be one of {sorted(_DIRS)}")


def _validate_outlook(o: dict, market_keys: set[str], errors: list[str]) -> None:
    _require(o, ("horizon", "summary_html", "net", "events", "calls"), "outlook", errors)
    events = o.get("events", [])
    if not 2 <= len(events) <= 4:
        errors.append("outlook.events: need 2–4")
    for i, ev in enumerate(events):
        _validate_event(ev, market_keys, f"outlook.events[{i}]", errors)
        if not _SLUG_RE.fullmatch(str(ev.get("id", ""))):
            errors.append(f"outlook.events[{i}].id: must be kebab-case")
    ev_ids = [ev.get("id") for ev in events]
    if dupes := sorted({i for i in ev_ids if ev_ids.count(i) > 1}):
        errors.append(f"outlook.events: duplicate ids {dupes}")
    net = o.get("net", [])
    if not 3 <= len(net) <= 8:
        errors.append("outlook.net: need 3–8 rows")
    for i, row in enumerate(net):
        where = f"outlook.net[{i}]"
        _require(row, ("lean", "event", "level", "why"), where, errors)
        _validate_asset_ref(row, market_keys, where, errors)
        if row.get("lean") not in _LEANS:
            errors.append(f"{where}.lean: must be one of {sorted(_LEANS)}")
        if row.get("event") and row["event"] not in ev_ids:
            errors.append(f"{where}.event: '{row['event']}' is not an outlook event id")
    calls = o.get("calls", [])
    if not 3 <= len(calls) <= 5:
        errors.append("outlook.calls: need 3–5 calls")
    for i, call in enumerate(calls):
        _require(call, ("id", "text", "horizon", "check"), f"outlook.calls[{i}]", errors)
        if call.get("event") and call["event"] not in ev_ids:
            errors.append(f"outlook.calls[{i}].event: '{call['event']}' is not an outlook event id")
    ids = [call.get("id") for call in calls]
    if dupes := sorted({i for i in ids if ids.count(i) > 1}):
        errors.append(f"outlook.calls: duplicate ids {dupes}")


def validate_content(c: dict, market_keys: set[str]) -> None:
    """Raise ContentError listing every contract violation in content.json."""
    errors: list[str] = []
    _require(
        c,
        (
            "date",
            "edition",
            "headline",
            "dek",
            "takeaways",
            "sections",
            "events",
            "calendar",
            "outlook",
            "sources",
        ),
        "content",
        errors,
    )
    try:
        dt.date.fromisoformat(str(c.get("date")))
    except ValueError:
        errors.append("content.date: must be YYYY-MM-DD")
    if c.get("edition") not in _EDITIONS:
        errors.append(f"content.edition: must be one of {sorted(_EDITIONS)}")
    if not 3 <= len(c.get("takeaways", [])) <= 5:
        errors.append("content.takeaways: need 3–5 items")
    for i, s in enumerate(c.get("sections", [])):
        _require(s, ("id", "title", "body_html"), f"sections[{i}]", errors)
        for j, row in enumerate(s.get("extra_rows", [])):
            _require(row, ("label",), f"sections[{i}].extra_rows[{j}]", errors)
            if not (row.get("value") or row.get("change")):
                errors.append(f"sections[{i}].extra_rows[{j}]: needs 'value' or 'change'")
    for i, e in enumerate(c.get("events", [])):
        _require(e, ("title", "impact", "body_html"), f"events[{i}]", errors)
        if e.get("impact") not in _IMPORTANCE:
            errors.append(f"events[{i}].impact: must be one of {sorted(_IMPORTANCE)}")
    for i, row in enumerate(c.get("calendar", [])):
        _require(row, ("date", "region", "event", "importance"), f"calendar[{i}]", errors)
        if row.get("importance") not in _IMPORTANCE:
            errors.append(f"calendar[{i}].importance: must be one of {sorted(_IMPORTANCE)}")
        if row.get("region") not in REGIONS and not row.get("region_name"):
            errors.append(
                f"calendar[{i}].region: '{row.get('region')}' is not a known code; add 'region_name'"
            )
        if t := row.get("time_utc"):
            try:
                dt.time.fromisoformat(t)
            except ValueError:
                errors.append(f"calendar[{i}].time_utc: must be HH:MM or empty")
    _validate_outlook(c.get("outlook", {}), market_keys, errors)
    if sc := c.get("scorecard"):
        _require(sc, ("wrap_date", "items"), "scorecard", errors)
        for i, item in enumerate(sc.get("items", [])):
            _require(item, ("id", "text", "result", "note"), f"scorecard.items[{i}]", errors)
            if item.get("result") not in _RESULTS:
                errors.append(f"scorecard.items[{i}].result: must be one of {sorted(_RESULTS)}")
            if item.get("result") == "pending":
                _require(item, ("horizon", "check"), f"scorecard.items[{i}] (pending, carried)", errors)
    for i, src in enumerate(c.get("sources", [])):
        _require(src, ("title", "url"), f"sources[{i}]", errors)
    if errors:
        raise ContentError("content.json contract violations:\n  " + "\n  ".join(errors))


# ---------- render ----------


def _reference_session(rows: list[dict]) -> str:
    """The most common session date: rows on another date get a date tag."""
    dates = collections.Counter(r["session_date"] for r in rows if "error" not in r)
    return dates.most_common(1)[0][0]


def _render_sessions(by_key: dict[str, dict]) -> str:
    cells = []
    for name, key in _SESSIONS:
        r = by_key.get(key, {})
        if "last" not in r:
            line = '<span class="session-label">no data</span>'
        else:
            chg = r["chg_1d"]
            sign = f"{chg:+.2f}%".replace("-", "−") if chg is not None else "—"
            line = (
                f'<span class="session-label">{esc(r["label"])}</span>'
                f'<span class="session-last">{fmt_last(r["last"], r["unit"], r["asset_class"])}</span>'
                f'<span class="session-last {direction(chg)}">{sign}</span>'
            )
        cells.append(
            f'<div class="session"><div class="session-name">{name}</div>'
            f'<div class="session-line">{line}</div></div>'
        )
    return "".join(cells)


def _render_dashboard(rows: list[dict], crypto_global: dict) -> str:
    ref = _reference_session(rows)
    head = (
        '<table class="dash"><thead><tr><th>Instrument</th><th class="num">Last</th><th class="num">1D</th>'
        '<th class="num">1W</th><th class="num">1M</th><th class="num">YTD</th>'
        "<th>1M trend</th></tr></thead><tbody>"
    )
    body = []
    for group, title in _GROUPS.items():
        body.append(f'<tr class="group"><td colspan="7">{title}</td></tr>')
        for r in (r for r in rows if r["asset_class"] == group):
            if "error" in r:
                body.append(
                    f'<tr><td class="inst">{esc(r["label"])}</td>'
                    f'<td class="num flat" colspan="6">unavailable</td></tr>'
                )
                continue
            stale = (
                f'<span class="stale">{short_date(r["session_date"])}</span>'
                if r["session_date"] != ref
                else ""
            )
            if r.get("contract_roll"):
                stale += '<span class="stale" title="1W/1M/YTD span a front-month roll">roll</span>'

            body.append(
                f'<tr><td class="inst">{esc(r["label"])}{stale}</td>'
                f'<td class="num">{fmt_last(r["last"], r["unit"], r["asset_class"])}</td>'
                + "".join(fmt_change(r[k], r["unit"]) for k in ("chg_1d", "chg_1w", "chg_1m", "chg_ytd"))
                + f'<td class="spark">{sparkline(r["spark"])}</td></tr>'
            )
        if group == "crypto" and "error" not in crypto_global:
            g = crypto_global
            chg = g["mcap_chg_24h_pct"]
            body.append(
                f'<tr><td class="inst muted" colspan="7">Total crypto market cap '
                f"${g['total_mcap_usd'] / 1e12:.2f}T "
                f'(<span class="{direction(chg)}">{chg:+.2f}% 24h</span>) · '
                f"BTC dominance {g['btc_dominance_pct']:.1f}% · ETH {g['eth_dominance_pct']:.1f}%</td></tr>"
            )
    return head + "".join(body) + "</tbody></table>"


def _render_sections(sections: list[dict]) -> str:
    out = []
    for s in sections:
        table = ""
        if rows := s.get("extra_rows"):
            trs = "".join(
                f'<tr><td>{esc(r["label"])} <span class="web-tag">web</span></td>'
                f'<td class="num">{esc(r.get("value") or "—")}</td>'
                f'<td class="num {r.get("direction", "flat")}">{esc(r.get("change", ""))}</td>'
                f'<td class="muted">{esc(r.get("note", ""))}</td></tr>'
                for r in rows
            )
            table = (
                '<div class="table-scroll"><table><thead><tr><th>Item</th><th class="num">Level</th>'
                f'<th class="num">Change</th><th>Note</th></tr></thead><tbody>{trs}</tbody></table></div>'
            )
        out.append(
            f'<section id="{esc(s["id"])}"><h2 class="eyebrow">{esc(s["title"])}</h2>'
            f'<div class="prose">{s["body_html"]}</div>{table}</section>'
        )
    return "".join(out)


def _render_events(events: list[dict]) -> str:
    if not events:
        return '<p class="muted">No market-moving events this session.</p>'
    return "".join(
        f'<div class="event"><div><span class="pill {e["impact"]}">{e["impact"]}</span></div>'
        f'<div><h3>{esc(e["title"])}</h3><div class="prose">{e["body_html"]}</div></div></div>'
        for e in events
    )


def _calendar_row(r: dict) -> str:
    name = r.get("region_name") or REGIONS[r["region"]]
    region = (
        f'<abbr class="region" tabindex="0" data-name="{esc(name)}" aria-label="{esc(name)}">'
        f"{esc(r['region'])}</abbr>"
    )
    if t := r.get("time_utc"):
        when = dt.datetime.fromisoformat(f"{r['date']}T{t}+00:00")
        local = when.astimezone(_CAL_DEFAULT_TZ)
        attrs = f'data-utc="{when.isoformat()}"'
        date_cell, time_cell = local.strftime("%a %-d %b"), local.strftime("%H:%M")
    else:
        attrs = ""
        date_cell, time_cell = dt.date.fromisoformat(r["date"]).strftime("%a %-d %b"), "—"
    return (
        f'<tr data-impact="{r["importance"]}" {attrs}>'
        f'<td class="mono cal-date">{date_cell}</td><td class="mono cal-time">{time_cell}</td>'
        f"<td>{region}</td><td>{esc(r['event'])}</td>"
        f'<td class="num">{esc(r.get("consensus", "") or "—")}</td>'
        f'<td class="num">{esc(r.get("prior", "") or "—")}</td>'
        f'<td><span class="pill {r["importance"]}">{r["importance"]}</span></td></tr>'
    )


def _render_calendar(rows: list[dict]) -> dict[str, str]:
    head = (
        '<table id="cal-table"><thead><tr><th>Date</th><th>Time</th><th>Region</th><th>Event</th>'
        '<th class="num">Consensus</th><th class="num">Prior</th><th>Impact</th></tr></thead><tbody>'
    )
    ordered = sorted(rows, key=lambda r: (r["date"], r.get("time_utc") or "99:99"))
    empty = (
        '<tr class="cal-empty" hidden><td colspan="7" class="muted">No events at this impact level.</td></tr>'
    )
    zone = (
        dt.datetime.fromisoformat(f"{ordered[0]['date']}T12:00+00:00").astimezone(_CAL_DEFAULT_TZ)
        if ordered
        else None
    )
    return {
        "calendar": head + "".join(_calendar_row(r) for r in ordered) + empty + "</tbody></table>",
        "calendar_tz": zone.tzname() if zone else "AEDT",
    }


@dataclasses.dataclass(frozen=True, slots=True)
class PrevOutlook:
    """Scenario probabilities from the previous wrap, keyed by (event id, scenario id)."""

    date: dt.date
    probs: dict[tuple[str, str], float]


def _asset_label(ref: dict, by_key: dict[str, dict]) -> str:
    if ref.get("key"):
        return esc(by_key[ref["key"]]["label"])
    return f'{esc(ref["label"])} <span class="web-tag">web</span>'


def _asset_now(ref: dict, by_key: dict[str, dict]) -> str:
    if not (r := by_key.get(ref.get("key"))):
        return "—"
    return fmt_last(r["last"], r["unit"], r["asset_class"])


def _prob_delta(key: tuple[str, str], pct: float, prev: PrevOutlook | None) -> str:
    if prev is None:
        return ""
    if key not in prev.probs:
        return '<span class="delta">new</span>'
    was = prev.probs[key]
    title = f' title="{was:g}% on {short_date(prev.date.isoformat())}"'
    if abs(diff := pct - was) < 0.5:
        return f'<span class="delta"{title}>unch</span>'
    return f'<span class="delta"{title}>{"▲" if diff > 0 else "▼"}{abs(diff):g}pp</span>'


def _move_cell(move: dict, extra_class: str = "") -> str:
    target = f" {esc(move['target'])}" if move.get("target") else ""
    return (
        f'<td class="num {move["dir"]}{extra_class}" aria-label="{move["dir"]}{target}">'
        f"{_DIRS[move['dir']]}{target}</td>"
    )


def _render_event(ev: dict, by_key: dict[str, dict], prev: PrevOutlook | None) -> str:
    if ev["when"] == "ongoing":
        meta = ["Ongoing", f"resolves on: {esc(ev['resolves'])}"]
    else:
        day = dt.date.fromisoformat(ev["when"]).strftime("%a %-d %b")
        meta = [day + (f" {esc(ev['time_utc'])} UTC" if ev.get("time_utc") else "")]
        if ev.get("resolves"):
            meta.append(esc(ev["resolves"]))
    cards = []
    for j, sc in enumerate(ev["scenarios"]):
        pct = _pct(sc["probability"])
        cards.append(
            f'<div class="ol-card{" likely" if j == 0 else ""}"><div class="ol-card-head">'
            f'<h4>{esc(sc["name"])}</h4><span class="prob">{pct:g}%</span>'
            f"{_prob_delta((ev['id'], sc['id']), pct, prev)}</div>"
            f'<div class="prob-bar" aria-hidden="true"><span style="width:{pct:g}%"></span></div>'
            + ('<div class="scenario-tag">Most likely</div>' if j == 0 else "")
            + f'<div class="prose">{sc["body_html"]}</div></div>'
        )
    head = '<th>Asset</th><th class="num">Now</th>' + "".join(
        f'<th class="num{" likely" if j == 0 else ""}">{esc(sc["name"])}</th>'
        for j, sc in enumerate(ev["scenarios"])
    )
    rows = "".join(
        f'<tr><td class="inst">{_asset_label(a, by_key)}</td>'
        f'<td class="num muted">{_asset_now(a, by_key)}</td>'
        + "".join(
            _move_cell(a["moves"][sc["id"]], " likely" if j == 0 else "")
            for j, sc in enumerate(ev["scenarios"])
        )
        + "</tr>"
        for a in ev["assets"]
    )
    return (
        f'<section class="ol-event" id="ev-{ev["id"]}"><div class="ol-head"><h3>{esc(ev["title"])}</h3>'
        f'<span class="ol-when">{" · ".join(meta)}</span></div>'
        f'<p class="ol-why">{esc(ev["why"])}</p><div class="ol-cards">{"".join(cards)}</div>'
        f'<div class="table-scroll"><table class="ev"><thead><tr>{head}</tr></thead>'
        f"<tbody>{rows}</tbody></table></div></section>"
    )


def _render_net(o: dict, by_key: dict[str, dict]) -> str:
    titles = {ev["id"]: ev["title"] for ev in o["events"]}
    rows = "".join(
        f'<tr><td class="inst">{_asset_label(row, by_key)}</td>'
        f'<td class="num muted">{_asset_now(row, by_key)}</td>'
        f'<td class="lean {row["lean"]}">{_LEANS[row["lean"]]} {esc(row["lean"])}</td>'
        f'<td><a href="#ev-{row["event"]}">{esc(titles[row["event"]])}</a></td>'
        f'<td class="num">{esc(row["level"])}</td><td class="why">{esc(row["why"])}</td></tr>'
        for row in o["net"]
    )
    return (
        '<table class="net"><thead><tr><th>Asset</th><th class="num">Now</th><th>Lean</th>'
        '<th>Driven by</th><th class="num">Level</th><th>Why the level</th></tr></thead>'
        f"<tbody>{rows}</tbody></table>"
    )


def _render_outlook(o: dict, by_key: dict[str, dict], prev: PrevOutlook | None) -> dict[str, str]:
    titles = {ev["id"]: ev["title"] for ev in o["events"]}
    calls = "".join(
        f'<li><span class="call-id">{esc(c["id"])}</span><span>{esc(c["text"])} '
        f'<span class="muted">({esc(c["horizon"])})</span>'
        + (
            f' <a class="call-event" href="#ev-{c["event"]}">{esc(titles[c["event"]])}</a>'
            if c.get("event")
            else ""
        )
        + f'</span><span class="call-check">Check: {esc(c["check"])}</span></li>'
        for c in o["calls"]
    )
    return {
        "outlook_horizon": esc(o["horizon"]),
        "outlook_summary": o["summary_html"],
        "outlook_net": _render_net(o, by_key),
        "outlook_events": "".join(_render_event(ev, by_key, prev) for ev in o["events"]),
        "calls": calls,
    }


def _render_scorecard(sc: dict | None) -> str:
    if not sc:
        return ""
    tally = collections.Counter(i["result"] for i in sc["items"])
    summary = " · ".join(f"{tally[k]} {k}" for k in ("hit", "miss", "pending", "void") if tally[k])
    rows = "".join(
        f'<tr><td class="mono">{esc(i["id"])}</td><td>{esc(i["text"])}</td>'
        f'<td><span class="pill {i["result"]}">{i["result"]}</span></td>'
        f'<td class="muted">{esc(i["note"])}</td></tr>'
        for i in sc["items"]
    )
    return (
        f'<section id="scorecard"><h2 class="eyebrow">Scorecard: calls from '
        f"{esc(short_date(sc['wrap_date']))} <small>{summary}</small></h2>"
        '<div class="table-scroll"><table><thead><tr><th>Call</th><th>Text</th><th>Result</th>'
        f"<th>Why</th></tr></thead><tbody>{rows}</tbody></table></div></section>"
    )


def _render_sources(sources: list[dict]) -> str:
    return "".join(
        f'<li><a href="{esc(s["url"])}">{esc(s["title"])}</a>'
        + (f' <span class="muted">· {esc(s["publisher"])}</span>' if s.get("publisher") else "")
        + (f' <span class="muted">· {esc(s["date"])}</span>' if s.get("date") else "")
        + "</li>"
        for s in sources
    )


def build_wrap_data(content: dict, markets: dict) -> dict:
    """The machine-readable block later runs and the index read back."""
    closes = {
        r["key"]: {
            k: r[k]
            for k in (
                "label",
                "asset_class",
                "unit",
                "last",
                "session_date",
                "chg_1d",
                "chg_1w",
                "chg_1m",
                "chg_ytd",
                "spark",
            )
        }
        for r in markets["instruments"]
        if "error" not in r
    }
    return {
        "schema": _SCHEMA,
        "date": content["date"],
        "edition": content["edition"],
        "headline": content["headline"],
        "generated_at_utc": markets["generated_at_utc"],
        "closes": closes,
        "crypto_global": markets["crypto_global"],
        "outlook_events": [
            {
                "id": ev["id"],
                "title": ev["title"],
                "scenarios": [{k: sc[k] for k in ("id", "name", "probability")} for sc in ev["scenarios"]],
            }
            for ev in content["outlook"]["events"]
        ],
        # Pending calls carry forward so the next run scores them again.
        "calls": content["outlook"]["calls"]
        + [
            {k: item[k] for k in ("id", "text", "horizon", "check")}
            for item in (content.get("scorecard") or {}).get("items", [])
            if item["result"] == "pending"
        ],
    }


def previous_outlook(base: Path, before: dt.date) -> PrevOutlook | None:
    """Probabilities from the latest wrap before `before`; None if it is legacy or predates events."""
    prior = next((w for w in discover(base) if w.date < before), None)
    if prior is None or not prior.data or "outlook_events" not in prior.data:
        return None
    return PrevOutlook(
        prior.date,
        {
            (ev["id"], sc["id"]): _pct(sc["probability"])
            for ev in prior.data["outlook_events"]
            for sc in ev["scenarios"]
        },
    )


def render(content: dict, markets: dict, base: Path) -> str:
    """Build the full wrap page from validated content and fetched markets; `base` holds earlier wraps."""
    rows = markets["instruments"]
    by_key = {r["key"]: r for r in rows}
    validate_content(content, {r["key"] for r in rows if "error" not in r})
    day = dt.date.fromisoformat(content["date"])
    prev = previous_outlook(base, day)
    slots = (
        {
            "date": content["date"],
            "date_long": day.strftime("%A %-d %B %Y"),
            "edition": esc(content["edition"]),
            "as_of": markets["generated_at_utc"].replace("T", " ").removesuffix("+00:00"),
            "css": page_css(),
            "wrap_data": json_for_script(build_wrap_data(content, markets)),
            "sessions": _render_sessions(by_key),
            "headline": esc(content["headline"]),
            "dek": esc(content["dek"]),
            "takeaways": "".join(f"<li>{t}</li>" for t in content["takeaways"]),
            "dashboard": _render_dashboard(rows, markets["crypto_global"]),
            "sections": _render_sections(content["sections"]),
            "events": _render_events(content["events"]),
            "scorecard": _render_scorecard(content.get("scorecard")),
            "source_count": str(len(content["sources"])),
            "sources": _render_sources(content["sources"]),
            "generated": dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M"),
        }
        | _render_outlook(content["outlook"], by_key, prev)
        | _render_calendar(content["calendar"])
    )
    return fill((_ASSETS / "template.html").read_text(), slots)


# ---------- history & index ----------


@dataclasses.dataclass(frozen=True, slots=True)
class WrapFile:
    """One wrap found in a base folder; `data` is None for legacy files without wrap-data."""

    path: Path
    date: dt.date
    title: str
    data: dict | None


def discover(base: Path) -> list[WrapFile]:
    """Every dated *.html in `base` except index.html, newest first."""
    found = []
    for path in base.glob("*.html"):
        if path.name == "index.html" or not (m := _DATE_RE.search(path.name)):
            continue
        try:
            day = dt.date.fromisoformat(m.group(1))
        except ValueError:
            continue
        text = path.read_text(errors="replace")
        data = None
        if dm := _WRAP_DATA_RE.search(text):
            try:
                data = json.loads(dm.group(1))
            except json.JSONDecodeError:
                data = None
        title = tm.group(1).strip() if (tm := _TITLE_RE.search(text)) else path.stem
        found.append(WrapFile(path, day, html.unescape(title), data))
    return sorted(found, key=lambda w: (w.date, w.path.name), reverse=True)


def _index_latest(wraps: list[WrapFile]) -> str:
    """Tiles of fixed-horizon changes and a 1M sparkline, as of the newest wrap with data."""
    latest = next((w for w in wraps if w.data), None)
    if latest is None:
        return ""
    tiles = []
    for key in INDEX_KEYS:
        if not (c := latest.data["closes"].get(key)):
            continue
        horizons = "".join(
            f'<span class="muted">{name}</span>'
            f'<span class="{direction(c.get(field))}">{change_text(c.get(field), c["unit"])}</span>'
            for name, field in (("1D", "chg_1d"), ("1W", "chg_1w"), ("1M", "chg_1m"), ("YTD", "chg_ytd"))
            if field in c
        )
        tiles.append(
            f'<div class="trend"><div class="trend-label">{esc(c["label"])}</div>'
            f'<div class="trend-last">{fmt_last(c["last"], c["unit"], c["asset_class"])}</div>'
            f'<div class="horizons">{horizons}</div>'
            f"{sparkline(c.get('spark', []), width=126, height=28)}</div>"
        )
    return "".join(tiles)


def _index_table(wraps: list[WrapFile]) -> str:
    head = (
        "<table><thead><tr><th>Date</th><th>Headline</th>"
        + "".join(f'<th class="num">{k}</th>' for k in INDEX_KEYS)
        + "</tr></thead><tbody>"
    )
    rows = []
    for w in wraps:
        link = f'<a href="{esc(w.path.name)}">{w.date.strftime("%a %-d %b %Y")}</a>'
        if not w.data:
            rows.append(
                f'<tr><td class="mono">{link}</td><td class="headline">{esc(w.title)} '
                f'<span class="web-tag">legacy</span></td>'
                f'<td class="num flat" colspan="{len(INDEX_KEYS)}">—</td></tr>'
            )
            continue
        cells = []
        for key in INDEX_KEYS:
            if c := w.data.get("closes", {}).get(key):
                cls = direction(c["chg_1d"])
                cells.append(
                    f'<td class="num">{fmt_last(c["last"], c["unit"], c["asset_class"])}'
                    f'<br><span class="tiny {cls}">' + change_text(c["chg_1d"], c["unit"]) + "</span></td>"
                )
            else:
                cells.append('<td class="num flat">—</td>')
        rows.append(
            f'<tr><td class="mono">{link}<br><span class="tiny muted">'
            f"{esc(w.data.get('edition', ''))}</span></td>"
            f'<td class="headline">{esc(w.data.get("headline", w.title))}</td>{"".join(cells)}</tr>'
        )
    return head + "".join(rows) + "</tbody></table>"


def render_index(base: Path) -> str:
    """Build index.html for every wrap in `base`."""
    wraps = discover(base)
    span = f"{wraps[-1].date:%-d %b %Y} – {wraps[0].date:%-d %b %Y}" if wraps else "no wraps yet"
    slots = {
        "css": page_css(),
        "count": f"{len(wraps)} wrap{'' if len(wraps) == 1 else 's'}",
        "span": span,
        "latest_date": next((f"{w.date:%-d %b %Y}" for w in wraps if w.data), "—"),
        "trends": _index_latest(wraps) or '<p class="muted">Appears once a wrap with data exists.</p>',
        "table": _index_table(wraps),
        "generated": dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M"),
    }
    return fill((_ASSETS / "index.html").read_text(), slots)


def history(base: Path, before: dt.date) -> dict:
    """The wraps in `base`, and the full data of the latest one dated before `before`."""
    wraps = discover(base)
    prior = next((w for w in wraps if w.date < before), None)
    return {
        "wraps": [
            {
                "file": w.path.name,
                "date": w.date.isoformat(),
                "has_wrap_data": w.data is not None,
                "title": w.title,
            }
            for w in wraps
        ],
        "previous": None
        if prior is None
        else {
            "file": str(prior.path),
            "date": prior.date.isoformat(),
            "wrap_data": prior.data,
            "note": None if prior.data else "legacy wrap: read the file's text for its outlook and calls",
        },
    }


def main() -> int:
    """CLI entry: dispatch the subcommand."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_render = sub.add_parser("render")
    p_render.add_argument("--markets", required=True, type=Path)
    p_render.add_argument("--content", required=True, type=Path)
    p_render.add_argument("--out", required=True, type=Path)
    p_index = sub.add_parser("index")
    p_index.add_argument("base", type=Path)
    p_hist = sub.add_parser("history")
    p_hist.add_argument("base", type=Path)
    p_hist.add_argument("--before", type=dt.date.fromisoformat, default=dt.datetime.now(dt.UTC).date())
    args = parser.parse_args()

    if args.cmd == "render":
        content = json.loads(args.content.read_text())
        markets = json.loads(args.markets.read_text())
        try:
            page = render(content, markets, args.out.parent)
        except ContentError as e:
            print(e, file=sys.stderr)
            return 2
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(page)
        print(f"wrote {args.out}")
    elif args.cmd == "index":
        out = args.base / "index.html"
        out.write_text(render_index(args.base))
        print(f"wrote {out}")
    else:
        print(json.dumps(history(args.base, args.before), indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
