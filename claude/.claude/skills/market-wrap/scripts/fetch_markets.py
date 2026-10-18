#!/usr/bin/env python3
"""Fetch closes and period changes for the market-wrap watchlist into one JSON file.

Usage: ``fetch_markets.py --out <path/markets.json>``. Prints a compact table to
stdout. Exits 1 only when every instrument fails. Stdlib only, so it runs with
``python3 -I`` and no environment.

Changes are measured from the latest daily close to the latest close on or before
7 / 30 calendar days earlier and the prior year-end. Yields change in bp, all else
in %. Yahoo's last daily candle is today's partial bar while a market is open.
1D uses Yahoo's own day change; `contract_roll` marks a future whose longer changes
span a front-month roll and so mix two contracts.
"""

import argparse
import concurrent.futures
import dataclasses
import datetime as dt
import enum
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# Yahoo answers 429 to a full browser UA string but serves a bare "Mozilla/5.0".
_UA = "Mozilla/5.0"
_YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{}?range=1y&interval=1d"
_COINGECKO_GLOBAL = "https://api.coingecko.com/api/v3/global"
_SPARK_POINTS = 23


class AssetClass(enum.StrEnum):
    EQUITY = "equity"
    RATES = "rates"
    FX = "fx"
    COMMODITY = "commodity"
    CRYPTO = "crypto"
    VOL_CREDIT = "vol_credit"


class Unit(enum.StrEnum):
    PRICE = "price"
    YIELD = "yield"  # quoted in percent; changes reported in bp


@dataclasses.dataclass(frozen=True, slots=True)
class Instrument:
    """One watchlist row; `key` is the stable id the wrap-data contract uses."""

    key: str
    label: str
    asset_class: AssetClass
    symbol: str
    unit: Unit = Unit.PRICE


_E, _R, _F, _C, _X, _V = (
    AssetClass.EQUITY,
    AssetClass.RATES,
    AssetClass.FX,
    AssetClass.COMMODITY,
    AssetClass.CRYPTO,
    AssetClass.VOL_CREDIT,
)
WATCHLIST: tuple[Instrument, ...] = (
    Instrument("SPX", "S&P 500", _E, "^GSPC"),
    Instrument("NDX", "Nasdaq 100", _E, "^NDX"),
    Instrument("DJI", "Dow Jones", _E, "^DJI"),
    Instrument("RUT", "Russell 2000", _E, "^RUT"),
    Instrument("STOXX600", "STOXX Europe 600", _E, "^STOXX"),
    Instrument("DAX", "DAX", _E, "^GDAXI"),
    Instrument("FTSE", "FTSE 100", _E, "^FTSE"),
    Instrument("CAC", "CAC 40", _E, "^FCHI"),
    Instrument("NIKKEI", "Nikkei 225", _E, "^N225"),
    Instrument("HSI", "Hang Seng", _E, "^HSI"),
    Instrument("SSE", "Shanghai Composite", _E, "000001.SS"),
    Instrument("KOSPI", "KOSPI", _E, "^KS11"),
    Instrument("ASX200", "S&P/ASX 200", _E, "^AXJO"),
    Instrument("SENSEX", "BSE Sensex", _E, "^BSESN"),
    Instrument("EEM", "MSCI EM (EEM)", _E, "EEM"),
    Instrument("US3M", "US 13-week bill", _R, "^IRX", Unit.YIELD),
    Instrument("US5Y", "US 5Y", _R, "^FVX", Unit.YIELD),
    Instrument("US10Y", "US 10Y", _R, "^TNX", Unit.YIELD),
    Instrument("US30Y", "US 30Y", _R, "^TYX", Unit.YIELD),
    Instrument("DXY", "US Dollar Index", _F, "DX-Y.NYB"),
    Instrument("EURUSD", "EUR/USD", _F, "EURUSD=X"),
    Instrument("USDJPY", "USD/JPY", _F, "JPY=X"),
    Instrument("GBPUSD", "GBP/USD", _F, "GBPUSD=X"),
    Instrument("USDCNY", "USD/CNY", _F, "CNY=X"),
    Instrument("AUDUSD", "AUD/USD", _F, "AUDUSD=X"),
    Instrument("WTI", "WTI crude", _C, "CL=F"),
    Instrument("BRENT", "Brent crude", _C, "BZ=F"),
    Instrument("NATGAS", "US natural gas", _C, "NG=F"),
    Instrument("GOLD", "Gold", _C, "GC=F"),
    Instrument("SILVER", "Silver", _C, "SI=F"),
    Instrument("COPPER", "Copper", _C, "HG=F"),
    Instrument("BTC", "Bitcoin", _X, "BTC-USD"),
    Instrument("ETH", "Ether", _X, "ETH-USD"),
    Instrument("SOL", "Solana", _X, "SOL-USD"),
    Instrument("VIX", "VIX", _V, "^VIX"),
    Instrument("MOVE", "MOVE index", _V, "^MOVE"),
    Instrument("HYG", "US high yield (HYG)", _V, "HYG"),
    Instrument("LQD", "US IG credit (LQD)", _V, "LQD"),
)


def _get_json(url: str, attempts: int = 3) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept": "application/json"})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.load(resp)
        except OSError:
            if attempt == attempts - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise AssertionError("unreachable")


def _close_on_or_before(series: list[tuple[dt.date, float]], day: dt.date) -> float | None:
    found = None
    for d, close in series:
        if d > day:
            break
        found = close
    return found


def _change(last: float, base: float | None, unit: Unit) -> float | None:
    if base is None or base == 0:
        return None
    if unit is Unit.YIELD:
        return round((last - base) * 100, 1)
    return round((last / base - 1) * 100, 2)


def fetch_instrument(inst: Instrument) -> dict:
    """Return the instrument's latest close, period changes and 1M sparkline series."""
    row = {
        "key": inst.key,
        "label": inst.label,
        "asset_class": inst.asset_class.value,
        "symbol": inst.symbol,
        "unit": inst.unit.value,
    }
    try:
        result = _get_json(_YAHOO.format(urllib.parse.quote(inst.symbol)))["chart"]["result"][0]
    except (OSError, KeyError, IndexError, TypeError, ValueError) as e:
        return row | {"error": f"{type(e).__name__}: {e}"}
    meta = result["meta"]
    offset = dt.timedelta(seconds=meta.get("gmtoffset", 0))
    closes = result["indicators"]["quote"][0]["close"]
    series = [
        ((dt.datetime.fromtimestamp(ts, dt.UTC) + offset).date(), close)
        for ts, close in zip(result.get("timestamp", []), closes, strict=True)
        if close is not None
    ]
    if len(series) < 2:
        return row | {"error": "no price history"}
    last_day, last = series[-1]
    # Yahoo's own day change compares like with like; on a continuous future (=F) the
    # history's previous close can belong to the expiring contract after a roll.
    chg_1d = _change(last, series[-2][1], inst.unit)
    roll = False
    pct = meta.get("regularMarketChangePercent")
    if pct is not None and abs(meta["regularMarketPrice"] - last) < 1e-6 * max(abs(last), 1):
        meta_1d = _change(last, last / (1 + pct / 100), inst.unit)
        roll = inst.symbol.endswith("=F") and chg_1d is not None and abs(meta_1d - chg_1d) > 0.5
        chg_1d = meta_1d
    market_time = dt.datetime.fromtimestamp(meta["regularMarketTime"], dt.UTC)
    return row | {
        "last": round(last, 4),
        "session_date": last_day.isoformat(),
        "market_time_utc": market_time.isoformat(timespec="minutes"),
        "currency": meta.get("currency"),
        "chg_1d": chg_1d,
        "contract_roll": roll,
        "chg_1w": _change(
            last,
            _close_on_or_before(series, last_day - dt.timedelta(days=7)),
            inst.unit,
        ),
        "chg_1m": _change(
            last,
            _close_on_or_before(series, last_day - dt.timedelta(days=30)),
            inst.unit,
        ),
        "chg_ytd": _change(
            last,
            _close_on_or_before(series, dt.date(last_day.year - 1, 12, 31)),
            inst.unit,
        ),
        "spark": [round(c, 4) for _, c in series[-_SPARK_POINTS:]],
    }


def fetch_crypto_global() -> dict:
    """Return total crypto market cap, 24h change and BTC/ETH dominance."""
    try:
        data = _get_json(_COINGECKO_GLOBAL)["data"]
    except (OSError, KeyError, ValueError) as e:
        return {"error": f"{type(e).__name__}: {e}"}
    return {
        "total_mcap_usd": round(data["total_market_cap"]["usd"]),
        "mcap_chg_24h_pct": round(data["market_cap_change_percentage_24h_usd"], 2),
        "btc_dominance_pct": round(data["market_cap_percentage"]["btc"], 2),
        "eth_dominance_pct": round(data["market_cap_percentage"]["eth"], 2),
    }


def _fmt(value: float | None, unit: Unit, *, is_change: bool) -> str:
    if value is None:
        return "—"
    if is_change:
        return f"{value:+.1f}bp" if unit is Unit.YIELD else f"{value:+.2f}%"
    return f"{value:,.4f}" if abs(value) < 10 else f"{value:,.2f}"


def _print_table(rows: list[dict], crypto_global: dict) -> None:
    print(f"{'key':<10}{'last':>14}  {'session':<11}{'1D':>9}{'1W':>9}{'1M':>9}{'YTD':>9}")
    for r in rows:
        if "error" in r:
            print(f"{r['key']:<10}  ERROR {r['error']}")
            continue
        unit = Unit(r["unit"])
        changes = "".join(
            f"{_fmt(r[k], unit, is_change=True):>9}" for k in ("chg_1d", "chg_1w", "chg_1m", "chg_ytd")
        )
        last = _fmt(r["last"], unit, is_change=False)
        print(f"{r['key']:<10}{last:>14}  {r['session_date']:<11}{changes}")
    print(f"crypto_global: {json.dumps(crypto_global)}")


def main() -> int:
    """Parse args, fetch everything in parallel, write JSON and print the table."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(fetch_instrument, WATCHLIST))
        crypto_global = fetch_crypto_global()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="minutes"),
        "instruments": rows,
        "crypto_global": crypto_global,
    }
    args.out.write_text(json.dumps(payload, indent=1))
    _print_table(rows, crypto_global)
    print(f"wrote {args.out}")
    return 1 if all("error" in r for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
