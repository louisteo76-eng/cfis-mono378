"""
Data provider clients — FMP, Finnhub, SEC EDGAR, Finviz.

Each provider function handles its own timeout, retry (1 retry on
network error), and error logging. Returns None on failure so callers
degrade gracefully. No Streamlit dependency — logging goes to stdlib.
"""

import logging
import requests
from urllib.parse import quote as url_quote

log = logging.getLogger("cfis.providers")

_RETRY_EXCEPTIONS = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
)

EDGAR_UA = "CFIS-X/2.0 (louisteo76@gmail.com)"


def _request_json(url, params=None, headers=None, timeout=10, retries=1):
    """GET a URL and return parsed JSON, or None on failure.

    Retries once on transient network errors. Logs non-200 status codes
    and exceptions at WARNING level so failures are visible but not fatal.
    """
    last_err = None
    for attempt in range(1 + retries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                log.warning("Rate limited by %s (429)", url.split("/")[2])
                return None
            if r.status_code == 403:
                log.warning("Access denied by %s (403) — check API key", url.split("/")[2])
                return None
            log.warning("%s returned HTTP %d", url.split("?")[0], r.status_code)
            return None
        except _RETRY_EXCEPTIONS as e:
            last_err = e
            if attempt < retries:
                log.debug("Retry %s after %s", url.split("?")[0], e.__class__.__name__)
                continue
        except Exception as e:
            log.warning("%s request failed: %s", url.split("/")[2], e.__class__.__name__)
            return None
    if last_err:
        log.warning("%s failed after retry: %s", url.split("/")[2], last_err.__class__.__name__)
    return None


def fmp_request(endpoint, api_key, params=None, timeout=10):
    """Call FMP stable API. Returns parsed JSON or None."""
    if not api_key:
        return None
    p = dict(params or {})
    p["apikey"] = api_key
    return _request_json(
        f"https://financialmodelingprep.com/stable/{endpoint}",
        params=p, timeout=timeout,
    )


def finnhub_request(endpoint, api_key, params=None, timeout=10):
    """Call Finnhub API. Returns parsed JSON or None."""
    if not api_key:
        return None
    p = dict(params or {})
    p["token"] = api_key
    return _request_json(
        f"https://finnhub.io/api/v1/{endpoint}",
        params=p, timeout=timeout,
    )


def edgar_request(path, timeout=10):
    """Call SEC EDGAR. Returns parsed JSON or None."""
    return _request_json(
        f"https://data.sec.gov/{path}",
        headers={"User-Agent": EDGAR_UA},
        timeout=timeout,
    )


_CIK_CACHE = {}

def get_cik(ticker):
    """Look up SEC CIK for a ticker. Cached in-memory."""
    t = ticker.upper().replace(".TO", "").replace(".L", "")
    if t in _CIK_CACHE:
        return _CIK_CACHE[t]
    data = _request_json(
        "https://efts.sec.gov/LATEST/search-index?q=%22" + url_quote(t)
        + "%22&dateRange=custom&startdt=2020-01-01&forms=10-K",
        headers={"User-Agent": EDGAR_UA},
        timeout=8,
    )
    if not data:
        return None
    hits = data.get("hits", {}).get("hits", [])
    if hits:
        source = hits[0].get("_source", {})
        ciks = source.get("ciks", [])
        cik = str(ciks[0]) if ciks else str(source.get("entity_id", ""))
        if cik:
            _CIK_CACHE[t] = cik.zfill(10)
            return _CIK_CACHE[t]
    return None


def fetch_finviz_quote(ticker, timeout=10):
    """Scrape Finviz snapshot page. Returns dict of label->value or {}."""
    import re
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) CFIS-X/2.0"}
    try:
        r = requests.get(
            f"https://finviz.com/quote.ashx?t={ticker}&ty=c&p=d&b=1",
            headers=headers, timeout=timeout,
        )
        if r.status_code != 200:
            log.warning("Finviz returned HTTP %d for %s", r.status_code, ticker)
            return {}
        text = r.text
    except Exception as e:
        log.warning("Finviz request failed for %s: %s", ticker, e.__class__.__name__)
        return {}

    data = {}
    rows = re.findall(
        r'<div class="snapshot-td-label">(.*?)</div>.*?<div class="snapshot-td-content"><b>(.*?)</b></div>',
        text, re.DOTALL,
    )
    if not rows:
        rows = re.findall(
            r'<td[^>]*class="snapshot-td2-cp"[^>]*>(.*?)</td>\s*<td[^>]*class="snapshot-td2"[^>]*><b>(.*?)</b></td>',
            text, re.DOTALL,
        )
    if not rows:
        rows = re.findall(
            r'<td[^>]*>([\w\s/%.]+)</td>\s*<td[^>]*><b>([^<]+)</b></td>',
            text, re.DOTALL,
        )
    for label, value in rows:
        label = re.sub(r'<[^>]+>', '', label).strip()
        value = re.sub(r'<[^>]+>', '', value).strip()
        data[label] = value
    return data
