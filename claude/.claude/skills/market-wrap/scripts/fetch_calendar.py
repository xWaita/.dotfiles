#!/usr/bin/env python3
"""Fetch the economic calendar for the wrap's 7-day window from FXStreet into one JSON file.

Usage: ``fetch_calendar.py --date <as-of> --out <path/calendar.json>``. Prints the
high-impact rows to stdout. Exits 1 when the fetch fails. Stdlib only, so it runs
with ``python3 -I`` and no environment.

FXStreet's calendar API answers 401 unless `Referer`/`Origin` name fxstreet.com.
Rows keep FXStreet's `volatility` as importance (HIGH/MEDIUM; LOW and NONE are
dropped). Rate decisions and coupon auctions FXStreet rates LOW are raised to
medium so the wrap can include them. The prior is the revised figure when one exists.
"""

import argparse
import datetime as dt
import json
import sys
import time
import urllib.request
from pathlib import Path

_URL = "https://calendar-api.fxstreet.com/en/api/v1/eventDates/{}/{}"
_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.fxstreet.com/",
    "Origin": "https://www.fxstreet.com",
}
_IMPORTANCE = {"HIGH": "high", "MEDIUM": "medium"}
_PROMOTED = ("Interest Rate Decision", "Note Auction", "Bond Auction", "TIPS Auction")
# FXStreet country codes that differ from wrap.py's REGIONS codes.
_REGION = {"EMU": "EZ"}
_WINDOW_DAYS = 7


def _get_json(url: str, attempts: int = 3) -> list[dict]:
    req = urllib.request.Request(url, headers=_HEADERS)
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.load(resp)
        except OSError:
            if attempt == attempts - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise AssertionError("unreachable")


def _figure(value: float | None, unit: str | None) -> str:
    """Format a consensus or prior; `%` follows the number, currency symbols lead it."""
    if value is None:
        return ""
    text = str(value).replace("-", "−")
    if unit == "%":
        return f"{text}%"
    return f"{unit}{text}" if unit else text


def to_row(event: dict) -> dict | None:
    """Map one FXStreet event to a content.json calendar row, or None when below medium impact."""
    importance = _IMPORTANCE.get(event["volatility"])
    if importance is None and any(k in event["name"] for k in _PROMOTED):
        importance = "medium"
    if importance is None:
        return None
    when = dt.datetime.fromisoformat(event["dateUtc"].replace("Z", "+00:00"))
    untimed = event["isAllDay"] or event["isTentative"]
    prior = event["revised"] if event["revised"] is not None else event["previous"]
    return {
        "id": f"fxs:{event['id']}",
        "date": when.date().isoformat(),
        "time_utc": "" if untimed else when.strftime("%H:%M"),
        "region": _REGION.get(event["countryCode"], event["countryCode"]),
        "event": event["name"].strip() + (" (tentative)" if event["isTentative"] else ""),
        "consensus": _figure(event["consensus"], event["unit"]),
        "prior": _figure(prior, event["unit"]),
        "importance": importance,
    }


def fetch(as_of: dt.date) -> list[dict]:
    """Return medium- and high-impact rows from `as_of` through `as_of` + 7 days, in time order."""
    end = as_of + dt.timedelta(days=_WINDOW_DAYS)
    events = _get_json(_URL.format(f"{as_of}T00:00:00Z", f"{end}T23:59:59Z"))
    rows = [r for e in events if (r := to_row(e))]
    return sorted(rows, key=lambda r: (r["date"], r["time_utc"] or "99:99"))


def main() -> int:
    """Parse args, fetch, write JSON and print the high-impact rows."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--date", required=True, type=dt.date.fromisoformat)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    try:
        rows = fetch(args.date)
    except (OSError, KeyError, TypeError, ValueError) as e:
        print(f"FXStreet calendar failed: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"date": args.date.isoformat(), "rows": rows}, indent=1))
    for r in rows:
        if r["importance"] == "high":
            when = f"{r['date']} {r['time_utc'] or '--:--'}"
            print(f"{when}  {r['region']:<4}{r['event']:<45}{r['consensus']:>10}{r['prior']:>10}")
    medium = sum(r["importance"] == "medium" for r in rows)
    print(f"{len(rows) - medium} high, {medium} medium; wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
