"""
Ticker universe service — FMP exchange screener + Supabase ticker_master.

Data flow:
  1. Try reading from Supabase ticker_master (fast, no API quota)
  2. If Supabase is empty or not configured, fetch from FMP
  3. If FMP data was fetched AND Supabase is available, save it

No Streamlit imports. Caching is handled by the caller (app.py wraps
with @st.cache_data).
"""

import logging
from datetime import datetime, timezone

import requests

from services.supabase_client import get_supabase_client

log = logging.getLogger("cfis.universe")

US_EXCHANGES = ("NYSE", "NASDAQ", "AMEX")
MIN_MARKET_CAP = 100_000_000
TICKER_MASTER_TABLE = "ticker_master"


# ── FMP source ──────────────────────────────────────────────

def fetch_fmp_exchange(exchange, api_key, timeout=30):
    """Fetch stocks for one exchange from FMP stock screener."""
    url = (
        f"https://financialmodelingprep.com/api/v3/stock-screener"
        f"?exchange={exchange}"
        f"&marketCapMoreThan={MIN_MARKET_CAP}"
        f"&limit=10000"
        f"&apikey={api_key}"
    )
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code != 200:
            return []
        data = resp.json()
        if not isinstance(data, list):
            return []
    except Exception:
        return []

    rows = []
    for s in data:
        sym = s.get("symbol", "")
        if not sym or "." in sym or "^" in sym or len(sym) > 5:
            continue
        rows.append({
            "symbol": sym,
            "name": s.get("companyName", sym),
            "market_cap": s.get("marketCap", 0),
            "sector": s.get("sector", ""),
            "exchange": exchange,
        })
    return rows


def fetch_fmp_us_universe(api_key):
    """Fetch all US-listed stocks from FMP across NYSE/NASDAQ/AMEX.

    Returns list of dicts sorted by market cap descending.
    Returns empty list if api_key is missing or all exchanges fail.
    """
    if not api_key:
        return []
    all_stocks = []
    for exchange in US_EXCHANGES:
        all_stocks.extend(fetch_fmp_exchange(exchange, api_key))
    all_stocks.sort(key=lambda x: x.get("market_cap", 0), reverse=True)
    return all_stocks


# ── Supabase ticker_master ──────────────────────────────────

def load_from_supabase(limit=10000):
    """Read ticker_master from Supabase. Returns list of dicts or []."""
    client = get_supabase_client()
    if client is None:
        return []
    try:
        result = (
            client.table(TICKER_MASTER_TABLE)
            .select("symbol,name,sector,industry,market_cap,exchange,is_etf")
            .eq("is_active", True)
            .order("market_cap", desc=True)
            .limit(limit)
            .execute()
        )
        data = getattr(result, "data", None) or []
        log.info("Loaded %d tickers from Supabase", len(data))
        return data
    except Exception as e:
        log.warning("Supabase read failed: %s", e)
        return []


def save_to_supabase(stocks):
    """Upsert FMP stock list into Supabase ticker_master.

    Called after a successful FMP fetch. Silently skips if Supabase
    is not configured. Uses chunked upsert to stay under row limits.
    """
    client = get_supabase_client()
    if client is None or not stocks:
        return 0
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for s in stocks:
        rows.append({
            "symbol": s["symbol"],
            "name": s.get("name", s["symbol"]),
            "sector": s.get("sector") or None,
            "industry": s.get("industry") or None,
            "market_cap": s.get("market_cap") or 0,
            "exchange": s.get("exchange", ""),
            "is_etf": s.get("is_etf", False),
            "is_active": True,
            "source": "fmp",
            "refreshed_at": now,
            "updated_at": now,
        })
    chunk_size = 500
    total = 0
    try:
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            client.table(TICKER_MASTER_TABLE).upsert(chunk, on_conflict="symbol").execute()
            total += len(chunk)
        log.info("Saved %d tickers to Supabase", total)
    except Exception as e:
        log.warning("Supabase upsert failed after %d rows: %s", total, e)
    return total


# ── Combined fetch: Supabase first, FMP fallback ───────────

def fetch_us_universe(api_key):
    """Get US stock universe: Supabase cache first, FMP fallback.

    If Supabase has data, returns it without hitting FMP.
    If Supabase is empty/unconfigured, fetches from FMP and saves.
    """
    supabase_data = load_from_supabase()
    if supabase_data:
        return supabase_data

    fmp_data = fetch_fmp_us_universe(api_key)
    if fmp_data:
        save_to_supabase(fmp_data)
    return fmp_data


# ── Scanner universe builder ───────────────────────────────

def build_scanner_universe(fmp_stocks, curated_tickers, max_tickers=300):
    """Combine curated tickers with FMP/Supabase market-cap leaders.

    curated_tickers always come first (preserving the handpicked watchlist).
    FMP fills remaining slots up to max_tickers, skipping duplicates.
    Returns curated_tickers unchanged if fmp_stocks is empty.
    """
    if not fmp_stocks:
        return list(curated_tickers)
    existing = set(curated_tickers)
    fmp_tickers = [s["symbol"] for s in fmp_stocks[:2000] if s["symbol"] not in existing]
    combined = list(curated_tickers) + fmp_tickers[:max_tickers - len(curated_tickers)]
    return combined[:max_tickers]
