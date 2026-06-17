"""
Ticker universe service — FMP exchange screener.

Pure data layer: no Streamlit imports. Caching is handled by the caller
(app.py wraps with @st.cache_data). Future: swap FMP source for Supabase
ticker_master reads without changing the caller interface.
"""

import requests

US_EXCHANGES = ("NYSE", "NASDAQ", "AMEX")
MIN_MARKET_CAP = 100_000_000


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


def build_scanner_universe(fmp_stocks, curated_tickers, max_tickers=300):
    """Combine curated tickers with FMP market-cap leaders.

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
