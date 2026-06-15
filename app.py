"""
mono378 — 18-Category Stock Intelligence Platform
"""
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import math
import requests
import xml.etree.ElementTree as ET
import re
import json
import time as _time
from collections import Counter
from urllib.parse import quote as url_quote

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
# Clear stale cache on first load of each session
if "cache_cleared" not in st.session_state:
    st.cache_data.clear()
    st.session_state["cache_cleared"] = True

st.set_page_config(
    page_title="CFIS-X by mono378",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# LOGIN GATE
# ─────────────────────────────────────────────────────────────
ACCESS_PASSWORD = "mono378"

def render_login():
    """Render the login page with Wall Street aesthetic."""
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: #080b12; }
    [data-testid="stSidebar"]          { display: none !important; }
    [data-testid="stHeader"]           { background: transparent !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # Centered login card
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("""
        <div style="text-align:center;margin-top:12vh">
            <div style="font-size:48px;font-weight:900;color:#ffffff;letter-spacing:6px;
                        font-family:'SF Mono','Fira Code',monospace">CFIS-X</div>
            <div style="font-size:11px;color:#4a5568;letter-spacing:4px;margin-top:4px">
                STOCK INTELLIGENCE TERMINAL</div>
            <div style="width:60px;height:2px;background:linear-gradient(90deg,#4CAF50,#FFC107,#f44336);
                        margin:20px auto;border-radius:2px"></div>
            <div style="font-size:13px;color:#6a7a9a;margin-top:8px">
                18-Category Composite · Louis Intuition Engine · Reddit Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

        # Login form
        st.markdown("""
        <div style="text-align:center;margin-bottom:12px">
            <span style="font-size:12px;color:#4a5568;letter-spacing:2px">ENTER ACCESS CODE</span>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            pwd = st.text_input("Access Code", type="password",
                               placeholder="Enter password",
                               label_visibility="collapsed",
                               key="login_pwd")
            submitted = st.form_submit_button("ACCESS TERMINAL", type="primary", use_container_width=True)
            if submitted:
                if pwd == ACCESS_PASSWORD:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Access denied. Invalid code.")

        st.markdown("""
        <div style="text-align:center;margin-top:60px">
            <div style="font-size:10px;color:#2d3748;letter-spacing:1px">
                mono378 INTELLIGENCE SYSTEMS</div>
            <div style="font-size:10px;color:#1a202c;margin-top:4px">
                For authorised personnel only</div>
        </div>
        """, unsafe_allow_html=True)


# Check authentication
if not st.session_state.get("authenticated", False):
    render_login()
    st.stop()


# ─────────────────────────────────────────────────────────────
# WORLD INDEX TICKER TAPE
# ─────────────────────────────────────────────────────────────
WORLD_INDICES = [
    ("^GSPC",   "S&P 500"),
    ("^IXIC",   "NASDAQ"),
    ("^DJI",    "DOW 30"),
    ("^RUT",    "Russell 2K"),
    ("^VIX",    "VIX"),
    ("^FTSE",   "FTSE 100"),
    ("^N225",   "Nikkei 225"),
    ("^HSI",    "Hang Seng"),
    ("^GDAXI",  "DAX"),
    ("CL=F",    "Crude Oil"),
    ("GC=F",    "Gold"),
    ("BTC-USD", "Bitcoin"),
    ("ETH-USD", "Ethereum"),
    ("DX-Y.NYB","USD Index"),
    ("^TNX",    "10Y Yield"),
]

@st.cache_data(ttl=120)
def fetch_index_tape():
    """Fetch world index prices for the ticker tape."""
    items = []
    for sym, name in WORLD_INDICES:
        try:
            h = yf.Ticker(sym).history(period="5d")
            if h.empty or len(h) < 2:
                continue
            cur  = float(h["Close"].iloc[-1])
            prev = float(h["Close"].iloc[-2])
            chg  = (cur - prev) / prev * 100
            # Format price based on magnitude
            if cur > 10000:    p_str = f"{cur:,.0f}"
            elif cur > 100:    p_str = f"{cur:,.2f}"
            else:              p_str = f"{cur:,.2f}"
            items.append({"name": name, "price": p_str, "chg": chg})
        except Exception:
            continue
    return items

# Fetch and render ticker tape
tape_items = fetch_index_tape()
if tape_items:
    tape_html = ""
    for item in tape_items:
        c = "#4CAF50" if item["chg"] >= 0 else "#f44336"
        arrow = "+" if item["chg"] >= 0 else ""
        tape_html += (
            f'<span style="display:inline-flex;align-items:center;gap:6px;padding:0 20px;white-space:nowrap">'
            f'<span style="color:#6a7a9a;font-size:11px;font-weight:500">{item["name"]}</span>'
            f'<span style="color:#e8ecf4;font-size:11px;font-weight:700">{item["price"]}</span>'
            f'<span style="color:{c};font-size:11px;font-weight:700">{arrow}{item["chg"]:.2f}%</span>'
            f'</span>'
        )
    # Duplicate for seamless loop
    full_tape = tape_html + tape_html

    st.markdown(f"""
    <div style="position:fixed;top:0;left:0;right:0;z-index:999999;
                background:#080b12;border-bottom:1px solid #1a2035;height:32px;
                overflow:hidden;display:flex;align-items:center">
        <div style="display:inline-flex;animation:tickerScroll 45s linear infinite;
                    white-space:nowrap">
            {full_tape}
        </div>
    </div>
    <style>
    @keyframes tickerScroll {{
        0%   {{ transform: translateX(0); }}
        100% {{ transform: translateX(-50%); }}
    }}
    /* Make Streamlit header transparent (keep sidebar toggle for mobile) */
    [data-testid="stHeader"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    [data-testid="stHeader"] > div {{
        background: transparent !important;
    }}
    /* Move sidebar toggle above ticker tape on mobile */
    [data-testid="stSidebarCollapsedControl"] {{
        z-index: 1000000 !important;
        top: 36px !important;
    }}
    /* Push content below ticker tape */
    [data-testid="stAppViewContainer"] > div:first-child {{ padding-top: 36px !important; }}
    [data-testid="stSidebar"] > div:first-child {{ padding-top: 36px !important; }}
    </style>
    """, unsafe_allow_html=True)
else:
    # Just hide the header if no data
    st.markdown('<style>[data-testid="stHeader"] { background: transparent !important; border: none !important; box-shadow: none !important; }</style>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# MAIN APP CSS — Wall Street Professional
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Global font ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── App background ── */
[data-testid="stAppViewContainer"] { background: #0a0e17; }
[data-testid="stSidebar"]          { background: #0d1320 !important; border-right: 1px solid #1a2035 !important; }

/* ── All readable text — target precisely, not * ── */
h1,h2,h3,h4,h5,h6                  { color: #f0f4fc !important; font-family: 'Inter', sans-serif !important; }
h1 { letter-spacing: -0.5px !important; }
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span { color: #dce4f0 !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span      { color: #c8d4e8 !important; }
[data-testid="stMetricLabel"] p     { color: #7a8ba8 !important; font-size: 11px !important;
                                       letter-spacing: 0.5px !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"]       { color: #ffffff !important; font-weight: 800 !important;
                                       font-family: 'Inter', sans-serif !important; }
[data-testid="stMetricDelta"] p     { font-weight: 600 !important; }
[data-testid="stCaptionContainer"] p{ color: #6a7a9a !important; }
.stRadio label                      { color: #c8d4e8 !important; }
.stSelectbox label                  { color: #c8d4e8 !important; }

/* ── Input: dark bg ── */
.stTextInput input {
    color: #ffffff !important;
    background-color: #111827 !important;
    border: 1px solid #1e2a40 !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
}
.stTextInput input::placeholder { color: #4a5568 !important; }
.stTextInput label              { color: #c8d4e8 !important; }

/* ── Buttons ── */
.stButton > button {
    background-color: #111827 !important;
    color: #e8ecf4 !important;
    border: 1px solid #1e2a40 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.3px !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background-color: #1a2540 !important;
    border-color: #3b82f6 !important;
    color: #ffffff !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1a4a1a, #0a2a0a) !important;
    border-color: #4CAF50 !important;
    color: #ffffff !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1e5e1e, #0e3a0e) !important;
}

/* ── Expander ── */
.stExpander { border: 1px solid #1a2035 !important; border-radius: 8px !important; }
.stExpander summary p           { color: #c8d4e8 !important; }

/* ── Alerts / info boxes ── */
div[data-testid="stInfo"] p,
div[data-testid="stAlert"] p    { color: #dce4f0 !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] th  { color: #ffffff !important; }

/* ── Dividers ── */
hr { border-color: #1a2035 !important; opacity: 0.6 !important; }

.score-row {
    display: flex; align-items: flex-start; gap: 16px;
    background: #111827; border-radius: 8px;
    padding: 16px 20px; margin: 5px 0;
    border-left: 4px solid #1a2035;
    transition: background 0.15s ease;
}
.score-row:hover { background: #151d2e; }
.score-row.green  { border-left-color: #4CAF50; }
.score-row.yellow { border-left-color: #FFC107; }
.score-row.red    { border-left-color: #f44336; }

.score-num {
    font-size: 28px; font-weight: 900; min-width: 52px;
    text-align: center; padding-top: 2px;
    font-family: 'Inter', sans-serif;
}
.score-num.green  { color: #4CAF50; }
.score-num.yellow { color: #FFC107; }
.score-num.red    { color: #f44336; }

.score-body { flex: 1; }
.score-name { font-size: 14px; font-weight: 700; color: #f0f4fc; margin-bottom: 3px;
              letter-spacing: 0.2px; }
.score-what { font-size: 11px; color: #6a7a9a; line-height: 1.5; margin-bottom: 5px; }
.score-analysis { font-size: 12px; color: #b8c8e0; line-height: 1.55; font-style: italic; }

.bar-bg {
    background: #1a2035; border-radius: 3px; height: 6px;
    margin-top: 8px; overflow: hidden;
}
.bar-fill { height: 100%; border-radius: 3px; }

.tier-badge {
    font-size: 10px; font-weight: 700; padding: 2px 10px;
    border-radius: 4px; white-space: nowrap; margin-top: 4px;
    letter-spacing: 0.5px; text-transform: uppercase;
}
.tier-badge.green  { background: #0a2a0a; color: #4CAF50; border: 1px solid #1a4a1a; }
.tier-badge.yellow { background: #2a2200; color: #FFC107; border: 1px solid #4a3a00; }
.tier-badge.red    { background: #2a0a0a; color: #f44336; border: 1px solid #4a1a1a; }

.big-score {
    border-radius: 12px; padding: 28px; text-align: center;
}
.section-box {
    background: #111827; border-radius: 8px; padding: 18px;
    border: 1px solid #1a2035; margin: 8px 0;
    color: #dce4f0; line-height: 1.65; font-size: 13px;
}
.outlook-card {
    background: #111827; border-radius: 8px; padding: 18px;
    text-align: center; border: 1px solid #1a2035;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def fmt(val, prefix="", suffix="", dec=2):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "N/A"
    try:
        val = float(val)
    except:
        return "N/A"
    if abs(val) >= 1e12: return f"{prefix}{val/1e12:.{dec}f}T{suffix}"
    if abs(val) >= 1e9:  return f"{prefix}{val/1e9:.{dec}f}B{suffix}"
    if abs(val) >= 1e6:  return f"{prefix}{val/1e6:.{dec}f}M{suffix}"
    return f"{prefix}{val:,.{dec}f}{suffix}"

def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, round(v)))

def tier(s):
    if s >= 70: return "green"
    if s >= 45: return "yellow"
    return "red"

def tier_label(s):
    if s >= 80: return "Excellent"
    if s >= 65: return "Good"
    if s >= 50: return "Above Average"
    if s >= 35: return "Below Average"
    return "Weak"

def safe(info, *keys, default=None):
    for k in keys:
        v = info.get(k)
        if v is not None:
            try:
                f = float(v)
                if not math.isnan(f): return f
            except:
                return v
    return default


# ─────────────────────────────────────────────────────────────
# MULTI-SOURCE DATA INTELLIGENCE LAYER
# FMP (250/day), Finnhub (60/min), SEC EDGAR (free), Finviz
# ─────────────────────────────────────────────────────────────

FMP_KEY = st.secrets.get("FMP_API_KEY", "") if hasattr(st, "secrets") else ""
FINNHUB_KEY = st.secrets.get("FINNHUB_API_KEY", "") if hasattr(st, "secrets") else ""
EDGAR_UA = "CFIS-X/2.0 (louisteo76@gmail.com)"

_CIK_CACHE = {}

def _fmp(endpoint, params=None):
    if not FMP_KEY:
        return None
    p = params or {}
    p["apikey"] = FMP_KEY
    try:
        r = requests.get(f"https://financialmodelingprep.com/stable/{endpoint}", params=p, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def _finnhub(endpoint, params=None):
    if not FINNHUB_KEY:
        return None
    p = params or {}
    p["token"] = FINNHUB_KEY
    try:
        r = requests.get(f"https://finnhub.io/api/v1/{endpoint}", params=p, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def _edgar(path):
    try:
        r = requests.get(f"https://data.sec.gov/{path}", headers={"User-Agent": EDGAR_UA}, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def _get_cik(ticker):
    t = ticker.upper().replace(".TO", "").replace(".L", "")
    if t in _CIK_CACHE:
        return _CIK_CACHE[t]
    try:
        r = requests.get("https://efts.sec.gov/LATEST/search-index?q=%22" + url_quote(t) + "%22&dateRange=custom&startdt=2020-01-01&forms=10-K",
                         headers={"User-Agent": EDGAR_UA}, timeout=8)
        if r.status_code == 200:
            data = r.json()
            hits = data.get("hits", {}).get("hits", [])
            if hits:
                source = hits[0].get("_source", {})
                ciks = source.get("ciks", [])
                cik = str(ciks[0]) if ciks else str(source.get("entity_id", ""))
                if cik:
                    _CIK_CACHE[t] = cik.zfill(10)
                    return _CIK_CACHE[t]
    except Exception:
        pass
    return None

@st.cache_data(ttl=3600)
def fetch_finviz(ticker):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) CFIS-X/2.0"}
        r = requests.get(f"https://finviz.com/quote.ashx?t={ticker}&ty=c&p=d&b=1", headers=headers, timeout=10)
        if r.status_code != 200:
            return {}
        from html.parser import HTMLParser
        text = r.text
        data = {}
        import re as _re
        rows = _re.findall(r'<div class="snapshot-td-label">(.*?)</div>.*?<div class="snapshot-td-content"><b>(.*?)</b></div>', text, _re.DOTALL)
        if not rows:
            rows = _re.findall(r'<td[^>]*class="snapshot-td2-cp"[^>]*>(.*?)</td>\s*<td[^>]*class="snapshot-td2"[^>]*><b>(.*?)</b></td>', text, _re.DOTALL)
        if not rows:
            rows = _re.findall(r'<td[^>]*>([\w\s/%.]+)</td>\s*<td[^>]*><b>([^<]+)</b></td>', text, _re.DOTALL)
        for label, value in rows:
            label = _re.sub(r'<[^>]+>', '', label).strip()
            value = _re.sub(r'<[^>]+>', '', value).strip()
            data[label] = value
        return data
    except Exception:
        return {}

def _parse_finviz_pct(val):
    if not val or val == "-":
        return None
    try:
        return float(val.replace("%", "")) / 100
    except Exception:
        return None

def _parse_finviz_num(val):
    if not val or val == "-":
        return None
    try:
        val = val.replace(",", "")
        if val.endswith("B"):
            return float(val[:-1]) * 1e9
        if val.endswith("M"):
            return float(val[:-1]) * 1e6
        if val.endswith("K"):
            return float(val[:-1]) * 1e3
        return float(val)
    except Exception:
        return None

@st.cache_data(ttl=21600)
def fetch_finnhub_recommendations(ticker):
    return _finnhub("stock/recommendation", {"symbol": ticker})

@st.cache_data(ttl=21600)
def fetch_finnhub_insider(ticker):
    return _finnhub("stock/insider-transactions", {"symbol": ticker})

@st.cache_data(ttl=3600)
def fetch_finnhub_news(ticker):
    today = datetime.now().strftime("%Y-%m-%d")
    past = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    return _finnhub("company-news", {"symbol": ticker, "from": past, "to": today})

@st.cache_data(ttl=21600)
def fetch_finnhub_earnings_calendar(ticker):
    return _finnhub("calendar/earnings", {"symbol": ticker})

@st.cache_data(ttl=86400)
def fetch_fmp_profile(ticker):
    data = _fmp("profile", {"symbol": ticker})
    if data and isinstance(data, list) and len(data) > 0:
        return data[0]
    return None

@st.cache_data(ttl=86400)
def fetch_fmp_key_metrics(ticker):
    return _fmp("key-metrics", {"symbol": ticker, "limit": 4})

@st.cache_data(ttl=86400)
def fetch_edgar_facts(ticker):
    cik = _get_cik(ticker)
    if not cik:
        return None
    return _edgar(f"api/xbrl/companyfacts/CIK{cik}.json")

def get_edgar_metric(facts, concept, taxonomy="us-gaap"):
    if not facts:
        return None
    try:
        units = facts.get("facts", {}).get(taxonomy, {}).get(concept, {}).get("units", {})
        for unit_key in ["USD", "USD/shares", "pure", "shares"]:
            if unit_key in units:
                vals = units[unit_key]
                quarterly = [v for v in vals if v.get("form") in ("10-Q", "10-K") and "val" in v]
                if quarterly:
                    quarterly.sort(key=lambda x: x.get("end", ""), reverse=True)
                    return quarterly
        return None
    except Exception:
        return None

@st.cache_data(ttl=600)
def fetch_enriched_data(ticker):
    enriched = {
        "inst_pct": None,
        "analyst_count": None,
        "analyst_rec": None,
        "short_float": None,
        "insider_pct": None,
        "target_price": None,
        "earnings_date": None,
        "recent_insider_buys": 0,
        "recent_insider_sells": 0,
        "news_headlines": [],
        "news_narrative_density": 0,
        "rd_expense": None,
        "quarterly_revenues": [],
        "roic": None,
        "roe": None,
        "recommendation_trend": None,
        "data_sources": [],
        "data_quality": 0,
    }
    fields_filled = 0
    total_fields = 10

    fv = fetch_finviz(ticker)
    if fv:
        enriched["data_sources"].append("finviz")
        v = _parse_finviz_pct(fv.get("Insider Own"))
        if v is not None:
            enriched["insider_pct"] = v; fields_filled += 1
        v = _parse_finviz_pct(fv.get("Inst Own"))
        if v is not None:
            enriched["inst_pct"] = v; fields_filled += 1
        v = _parse_finviz_pct(fv.get("Short Float"))
        if v is not None:
            enriched["short_float"] = v; fields_filled += 1
        v = _parse_finviz_num(fv.get("Target Price"))
        if v is not None:
            enriched["target_price"] = v; fields_filled += 1

    recs = fetch_finnhub_recommendations(ticker)
    if recs and isinstance(recs, list) and len(recs) > 0:
        enriched["data_sources"].append("finnhub")
        latest = recs[0]
        total_analysts = sum(latest.get(k, 0) for k in ["strongBuy", "buy", "hold", "sell", "strongSell"])
        if total_analysts > 0:
            enriched["analyst_count"] = total_analysts
            weighted = (latest.get("strongBuy", 0) * 1 + latest.get("buy", 0) * 2 +
                        latest.get("hold", 0) * 3 + latest.get("sell", 0) * 4 +
                        latest.get("strongSell", 0) * 5)
            enriched["analyst_rec"] = weighted / total_analysts
            fields_filled += 1
        enriched["recommendation_trend"] = recs[:6]

    insider = fetch_finnhub_insider(ticker)
    if insider and isinstance(insider, dict):
        txns = insider.get("data", [])
        cutoff = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        buys = sum(1 for t in txns if t.get("transactionType") == "P - Purchase" and (t.get("transactionDate", "") >= cutoff))
        sells = sum(1 for t in txns if t.get("transactionType") == "S - Sale" and (t.get("transactionDate", "") >= cutoff))
        enriched["recent_insider_buys"] = buys
        enriched["recent_insider_sells"] = sells
        if buys + sells > 0:
            fields_filled += 1

    news = fetch_finnhub_news(ticker)
    if news and isinstance(news, list):
        enriched["news_headlines"] = [n.get("headline", "") for n in news[:20]]
        enriched["news_narrative_density"] = min(100, len(news) * 3)
        if len(news) > 0:
            fields_filled += 1

    earnings = fetch_finnhub_earnings_calendar(ticker)
    if earnings and isinstance(earnings, dict):
        cal = earnings.get("earningsCalendar", [])
        future = [e for e in cal if e.get("date", "") >= datetime.now().strftime("%Y-%m-%d")]
        if future:
            enriched["earnings_date"] = future[0].get("date")
            fields_filled += 1

    facts = fetch_edgar_facts(ticker)
    if facts:
        enriched["data_sources"].append("edgar")
        rd = get_edgar_metric(facts, "ResearchAndDevelopmentExpense")
        if rd:
            enriched["rd_expense"] = rd[0].get("val")
            fields_filled += 1

        rev = get_edgar_metric(facts, "Revenues") or get_edgar_metric(facts, "RevenueFromContractWithCustomerExcludingAssessedTax")
        if rev and len(rev) >= 2:
            enriched["quarterly_revenues"] = [(r.get("end", ""), r.get("val", 0)) for r in rev[:8]]
            fields_filled += 1

    fmp_prof = fetch_fmp_profile(ticker)
    if fmp_prof:
        enriched["data_sources"].append("fmp")
        if enriched["inst_pct"] is None and fmp_prof.get("institutionalOwnership"):
            enriched["inst_pct"] = fmp_prof["institutionalOwnership"]
            fields_filled += 1

    fmp_km = fetch_fmp_key_metrics(ticker)
    if fmp_km and isinstance(fmp_km, list) and len(fmp_km) > 0:
        latest_km = fmp_km[0]
        roic = latest_km.get("returnOnInvestedCapital") or latest_km.get("roic")
        if roic is not None:
            enriched["roic"] = roic
        roe = latest_km.get("returnOnEquity") or latest_km.get("roe")
        if roe is not None:
            enriched["roe"] = roe

    enriched["data_quality"] = round(fields_filled / total_fields * 100)
    return enriched


# ─────────────────────────────────────────────────────────────
# REDDIT SOCIAL INTELLIGENCE SCANNER
# ─────────────────────────────────────────────────────────────
REDDIT_SUBS = {
    "wallstreetbets":  {"weight": 1.5, "type": "momentum"},
    "stocks":          {"weight": 1.0, "type": "fundamental"},
    "options":         {"weight": 1.3, "type": "options"},
    "cryptocurrency":  {"weight": 1.2, "type": "crypto"},
    "investing":       {"weight": 0.8, "type": "fundamental"},
    "Shortsqueeze":    {"weight": 1.4, "type": "squeeze"},
    "StockMarket":     {"weight": 0.9, "type": "general"},
}

# Topic keyword buckets — each maps to a CFIS-X category boost
SOCIAL_TOPIC_MAP = {
    "dark_pool": {
        "keywords": ["dark pool","darkpool","dark-pool","off exchange","institutional accumulation",
                     "block trade","hidden order","iceberg","large block","whale"],
        "categories": ["Dark Pool Intelligence"],
    },
    "options_flow": {
        "keywords": ["call","put","options","iron condor","straddle","strangle","spread",
                     "gamma squeeze","gamma","iv crush","implied volatility","expiry","strike",
                     "otm","itm","leaps","covered call","naked put","wheel strategy"],
        "categories": ["Options Warfare"],
    },
    "squeeze": {
        "keywords": ["short squeeze","squeeze","shorts covering","short interest","si%",
                     "days to cover","borrow rate","ftd","failure to deliver","naked short"],
        "categories": ["Options Warfare", "Dark Pool Intelligence"],
    },
    "crypto_fintech": {
        "keywords": ["bitcoin","btc","ethereum","eth","crypto","blockchain","stablecoin",
                     "defi","tokeniz","web3","nft","digital asset","cbdc","lightning network",
                     "fintech","digital payment","digital wallet"],
        "categories": ["Future Civilization Exposure"],
    },
    "insider_move": {
        "keywords": ["insider buy","insider purchase","ceo bought","cfo bought","insider selling",
                     "form 4","sec filing","insider ownership","10b5","buyback","share repurchase"],
        "categories": ["Insider Conviction"],
    },
    "institutional": {
        "keywords": ["institutional","hedge fund","blackrock","vanguard","ark invest",
                     "13f","whale watching","smart money","fund manager","pension fund",
                     "sovereign wealth"],
        "categories": ["Institutional Power", "ETF Gravity"],
    },
    "government": {
        "keywords": ["government contract","defense contract","dod","pentagon","fda approval",
                     "fda","regulation","subsidy","tariff","sanctions","chips act","ira act",
                     "infrastructure bill","national security"],
        "categories": ["Government Influence", "Sovereign Capital", "Political Intelligence"],
    },
    "catalyst": {
        "keywords": ["earnings","er play","earnings report","guidance","product launch",
                     "fda decision","analyst upgrade","price target","pt raised","beat estimates",
                     "revenue beat","eps beat","conference","investor day"],
        "categories": ["Catalyst Calendar"],
    },
    "moat_competition": {
        "keywords": ["monopoly","moat","competitive advantage","market leader","dominant",
                     "pricing power","switching cost","no competition","only company","market share"],
        "categories": ["Economic Moat", "Industry Dominance"],
    },
    "ai_tech": {
        "keywords": ["artificial intelligence","ai","machine learning","gpu","data center",
                     "semiconductor","chip","inference","llm","generative","autonomous",
                     "robotics","quantum"],
        "categories": ["Future Civilization Exposure"],
    },
    "balance_sheet": {
        "keywords": ["cash rich","debt free","balance sheet","cash pile","war chest",
                     "net cash","no debt","cash flow","free cash flow","dividend"],
        "categories": ["War Chest", "Fortress Balance Sheet"],
    },
    "acquisition": {
        "keywords": ["acquisition","merger","m&a","buyout","takeover","target","bid",
                     "deal","acquiring","acquired by","strategic investment"],
        "categories": ["M&A Probability"],
    },
    "macro_boj_carry": {
        "keywords": ["boj","bank of japan","yen carry","carry trade","yen","japan rate",
                     "rate hike japan","nikkei","usd/jpy","usdjpy","carry unwind",
                     "forced liquidation","margin call","deleveraging","risk off"],
        "categories": ["Market Regime Intelligence"],
    },
    "macro_fed": {
        "keywords": ["fed rate","fomc","powell","rate cut","rate hike","hawkish","dovish",
                     "tightening","quantitative","treasury yield","10 year","bond","recession"],
        "categories": ["Market Regime Intelligence"],
    },
    "leverage_risk": {
        "keywords": ["leverage","margin","liquidat","overleveraged","forced selling",
                     "capitulation","vol spike","vix","crash","correction","sell-off",
                     "risk-off","de-risk","unwind","black swan"],
        "categories": ["Market Regime Intelligence", "Fortress Balance Sheet"],
    },
}

# Sentiment keywords
BULLISH_WORDS = {"bull","bullish","moon","rocket","calls","long","buy","buying","undervalued",
                 "breakout","squeeze","upside","beat","growth","strong","soar","rally","accumulate",
                 "diamond hands","hold","conviction","gem","opportunity","load up","dip buy"}
BEARISH_WORDS = {"bear","bearish","puts","short","sell","selling","overvalued","crash","dump",
                 "bubble","decline","downside","miss","weak","falling","drop","avoid","exit",
                 "bag holder","loss","tanking","warning","red flag","fade"}


@st.cache_data(ttl=600)
def scan_reddit(ticker):
    """Scan Reddit for ticker mentions. Returns social intelligence dict."""
    result = {
        "total_mentions": 0,
        "sub_counts": {},
        "bullish": 0,
        "bearish": 0,
        "neutral": 0,
        "sentiment_score": 50,  # 0-100, 50 = neutral
        "topic_hits": Counter(),
        "category_boosts": Counter(),
        "top_posts": [],
        "buzz_score": 0,
        "has_data": False,
    }

    headers = {"User-Agent": "CFIS-X-StockApp/2.0 (educational stock research)"}
    all_titles = []

    for sub, meta in REDDIT_SUBS.items():
        try:
            url = (f"https://www.reddit.com/r/{sub}/search/.rss"
                   f"?q={ticker}&sort=new&limit=20&t=week&restrict_sr=1")
            r = requests.get(url, headers=headers, timeout=8)
            if r.status_code != 200:
                continue

            ns = {"atom": "http://www.w3.org/2005/Atom"}
            root = ET.fromstring(r.text)
            entries = root.findall("atom:entry", ns)

            count = len(entries)
            if count == 0:
                continue

            result["sub_counts"][sub] = count
            result["total_mentions"] += count
            result["has_data"] = True

            for entry in entries:
                title_el = entry.find("atom:title", ns)
                title = (title_el.text or "").lower() if title_el is not None else ""
                all_titles.append(title)

                # Sentiment
                title_words = set(re.findall(r'[a-z]+', title))
                bull_hits = len(title_words & BULLISH_WORDS)
                bear_hits = len(title_words & BEARISH_WORDS)
                if bull_hits > bear_hits:
                    result["bullish"] += 1
                elif bear_hits > bull_hits:
                    result["bearish"] += 1
                else:
                    result["neutral"] += 1

                # Topic detection
                for topic, tdata in SOCIAL_TOPIC_MAP.items():
                    if any(kw in title for kw in tdata["keywords"]):
                        result["topic_hits"][topic] += 1
                        for cat in tdata["categories"]:
                            result["category_boosts"][cat] += meta["weight"]

                # Save top posts (by subreddit importance)
                if len(result["top_posts"]) < 12:
                    link_el = entry.find("atom:link", ns)
                    link = link_el.get("href", "") if link_el is not None else ""
                    result["top_posts"].append({
                        "sub": sub,
                        "title": (title_el.text or "")[:120] if title_el is not None else "",
                        "link": link,
                        "type": meta["type"],
                    })
        except Exception:
            continue

    # Compute sentiment score (0-100)
    total_sent = result["bullish"] + result["bearish"] + result["neutral"]
    if total_sent > 0:
        result["sentiment_score"] = clamp(
            50 + (result["bullish"] - result["bearish"]) / total_sent * 50
        )

    # Buzz score: how much attention this ticker is getting
    m = result["total_mentions"]
    if m >= 30:   result["buzz_score"] = 95
    elif m >= 20: result["buzz_score"] = 80
    elif m >= 12: result["buzz_score"] = 65
    elif m >= 6:  result["buzz_score"] = 50
    elif m >= 3:  result["buzz_score"] = 35
    elif m >= 1:  result["buzz_score"] = 20
    else:         result["buzz_score"] = 5

    return result


def apply_social_boosts(scores, social):
    """Apply Reddit-derived boosts to CFIS-X category scores. Returns modified scores dict."""
    if not social["has_data"]:
        return scores

    boosted = dict(scores)
    for cat, boost_val in social["category_boosts"].items():
        if cat in boosted:
            # Each category boost point adds 1-3 points, capped at +15
            addition = clamp(boost_val * 2.5, 0, 15)
            boosted[cat] = clamp(boosted[cat] + addition)

    # Sentiment also slightly boosts/penalises Options Warfare and Catalyst Calendar
    sent = social["sentiment_score"]
    if sent > 65:
        boosted["Catalyst Calendar"] = clamp(boosted.get("Catalyst Calendar", 50) + 5)
        boosted["Options Warfare"] = clamp(boosted.get("Options Warfare", 50) + 4)
    elif sent < 35:
        boosted["Options Warfare"] = clamp(boosted.get("Options Warfare", 50) - 4)

    return boosted


def render_social_intelligence(social, ticker):
    """Render the Reddit Social Intelligence section."""
    st.subheader("📡 Reddit Social Intelligence")
    st.caption("Live scan of Reddit discussions (r/wallstreetbets, r/stocks, r/options, r/cryptocurrency, r/investing) · refreshes every 10 min")

    if not social["has_data"]:
        st.info(f"No Reddit discussions found for **{ticker}** in the past week. This stock may be under the radar — which can be bullish or just low-interest.")
        return

    # Key metrics
    m = social["total_mentions"]
    sent = social["sentiment_score"]
    buzz = social["buzz_score"]
    sent_c = "#4CAF50" if sent >= 60 else ("#f44336" if sent <= 40 else "#FFC107")
    buzz_c = "#4CAF50" if buzz >= 60 else ("#FFC107" if buzz >= 35 else "#8a9bb5")

    if sent >= 65:   sent_label = "🟢 Bullish"
    elif sent <= 35:  sent_label = "🔴 Bearish"
    else:             sent_label = "🟡 Mixed"

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Mentions", f"{m}", help="Posts mentioning this ticker across all scanned subreddits in the past week")
    c2.metric("Sentiment", f"{sent}/100", delta=sent_label)
    c3.metric("Buzz Score", f"{buzz}/100")
    c4.metric("Bullish Posts", f"{social['bullish']}", delta=f"{social['bullish']/(social['bullish']+social['bearish']+social['neutral'])*100:.0f}%" if m > 0 else "N/A")
    c5.metric("Bearish Posts", f"{social['bearish']}")

    st.markdown("---")

    # Subreddit breakdown + Topic hits side by side
    col_sub, col_topic = st.columns(2)

    with col_sub:
        st.markdown("**📊 Subreddit Breakdown**")
        for sub, count in sorted(social["sub_counts"].items(), key=lambda x: x[1], reverse=True):
            sub_type = REDDIT_SUBS[sub]["type"]
            type_badge = {"momentum": "🔥", "fundamental": "📈", "options": "🎲", "crypto": "🪙", "squeeze": "💥", "general": "📊"}.get(sub_type, "📊")
            bar_w = min(count / max(social["total_mentions"], 1) * 100, 100)
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
                f'<span style="font-size:12px;color:#e8ecf4;min-width:140px">{type_badge} r/{sub}</span>'
                f'<div style="flex:1;background:#2e3550;border-radius:4px;height:8px;overflow:hidden">'
                f'<div style="width:{bar_w}%;height:100%;background:{sent_c};border-radius:4px"></div></div>'
                f'<span style="font-size:12px;font-weight:700;color:#ffffff;min-width:24px">{count}</span>'
                f'</div>', unsafe_allow_html=True
            )

    with col_topic:
        st.markdown("**🏷️ Discussion Topics Detected**")
        if social["topic_hits"]:
            topic_labels = {
                "dark_pool": "🌑 Dark Pool / Institutional Flow",
                "options_flow": "🎲 Options & Derivatives",
                "squeeze": "💥 Short Squeeze / Shorts",
                "crypto_fintech": "🪙 Crypto / Fintech",
                "insider_move": "👤 Insider Activity",
                "institutional": "🏛️ Institutional / Smart Money",
                "government": "🏛️ Government / Regulation",
                "catalyst": "📅 Earnings / Catalysts",
                "moat_competition": "🏰 Moat / Competition",
                "ai_tech": "🤖 AI / Technology",
                "balance_sheet": "💰 Balance Sheet / Cash",
                "acquisition": "🤝 M&A / Acquisition",
            }
            for topic, count in social["topic_hits"].most_common(8):
                label = topic_labels.get(topic, topic)
                st.markdown(
                    f'<div style="background:#1c2130;border-radius:8px;padding:6px 12px;margin:3px 0;'
                    f'display:flex;justify-content:space-between;align-items:center">'
                    f'<span style="font-size:12px;color:#e8ecf4">{label}</span>'
                    f'<span style="font-size:13px;font-weight:700;color:#FFC107">{count}</span>'
                    f'</div>', unsafe_allow_html=True
                )
        else:
            st.markdown('<span style="font-size:12px;color:#6a7a9a">No specific topic patterns detected in recent discussions.</span>', unsafe_allow_html=True)

    st.markdown("---")

    # Category boosts
    if social["category_boosts"]:
        st.markdown("**⚡ CFIS-X Categories Boosted by Social Signals**")
        boost_html = ""
        for cat, val in social["category_boosts"].most_common(6):
            pts = clamp(val * 2.5, 0, 15)
            boost_html += (
                f'<span style="background:#1a3a1a;border:1px solid #4CAF50;border-radius:20px;'
                f'padding:4px 12px;font-size:11px;color:#66d166;margin:3px;display:inline-block">'
                f'{cat} <b>+{pts:.0f}</b></span>'
            )
        st.markdown(f'<div style="margin-bottom:12px">{boost_html}</div>', unsafe_allow_html=True)

    # Top posts
    if social["top_posts"]:
        with st.expander(f"💬 Recent Reddit Discussions ({len(social['top_posts'])} posts)", expanded=False):
            for p in social["top_posts"]:
                type_icon = {"momentum": "🔥", "fundamental": "📈", "options": "🎲", "crypto": "🪙", "squeeze": "💥", "general": "📊"}.get(p["type"], "📊")
                st.markdown(
                    f'<div style="background:#0e1117;border-radius:8px;padding:8px 12px;margin:4px 0;'
                    f'border-left:3px solid #3a4460">'
                    f'<span style="font-size:11px;color:#8a9bb5">{type_icon} r/{p["sub"]}</span><br>'
                    f'<span style="font-size:13px;color:#e8ecf4">{p["title"]}</span>'
                    f'</div>', unsafe_allow_html=True
                )

    # Summary interpretation
    if m >= 10 and sent >= 65:
        interp = f"🟢 **High Social Conviction** — {ticker} is generating significant bullish discussion across Reddit. {m} mentions with {sent}/100 sentiment suggests retail traders are actively accumulating. The crowd isn't always right — but when volume and sentiment align, momentum tends to follow."
    elif m >= 10 and sent <= 35:
        interp = f"🔴 **Negative Social Sentiment** — {ticker} is being discussed heavily but the tone is bearish. {m} mentions with only {sent}/100 sentiment. Reddit is flagging concerns — whether it's overvaluation, competition, or sector headwinds. Use caution."
    elif m >= 5:
        interp = f"🟡 **Moderate Attention** — {ticker} has some Reddit buzz ({m} mentions) with mixed sentiment ({sent}/100). Not a high-conviction crowd trade yet, but interest is building. Watch for a sentiment shift."
    elif m >= 1:
        interp = f"📡 **Under the Radar** — Only {m} Reddit mentions for {ticker} this week. Low social interest can mean the stock hasn't been discovered yet — or that the crowd has moved on. Contrarian opportunity if fundamentals are strong."
    else:
        interp = f"🔇 **Silent** — No Reddit discussions about {ticker}. This stock is completely off the retail radar."

    st.markdown(f'<div style="background:#1c2130;border-radius:10px;padding:14px 18px;margin-top:12px;'
                f'font-size:13px;color:#e8ecf4;line-height:1.7">{interp}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# DATA FETCH
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch(ticker):
    t = yf.Ticker(ticker)
    info = t.info
    hist = t.history(period="1y")
    try:
        inst = t.institutional_holders
    except:
        inst = None
    try:
        maj = t.major_holders
    except:
        maj = None
    try:
        dates = list(t.options)
        if dates:
            chain = t.option_chain(dates[0])
            opts_calls = chain.calls.reset_index(drop=True)
            opts_puts  = chain.puts.reset_index(drop=True)
        else:
            opts_calls = opts_puts = None
    except:
        opts_calls = opts_puts = None
        dates = []
    return info, hist, inst, maj, opts_calls, opts_puts, dates


# ─────────────────────────────────────────────────────────────
# 18 CFIS-X SCORING CATEGORIES
# ─────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────
# CFIS-X 18 INTELLIGENCE CATEGORIES
# ─────────────────────────────────────────────────────────────
CATEGORIES = [
    "Future Civilization Exposure",
    "Institutional Power",
    "Sovereign Capital",
    "Political Intelligence",
    "ETF Gravity",
    "Dark Pool Intelligence",
    "Options Warfare",
    "Insider Conviction",
    "Leadership Intelligence",
    "Economic Moat",
    "Revenue Quality",
    "Government Influence",
    "War Chest",
    "Fortress Balance Sheet",
    "M&A Probability",
    "Industry Dominance",
    "Catalyst Calendar",
    "Market Regime Intelligence",
]

DESCRIPTIONS = {
    "Future Civilization Exposure":
        "How essential is this company to the next 20 years? Scores exposure to AI, energy transition, biotech, space, and automation — the industries that will define civilization.",
    "Institutional Power":
        "How much big money owns this stock? High institutional concentration means hedge funds, pension funds, and sovereign wealth managers have done the homework and committed.",
    "Sovereign Capital":
        "Is this company attracting government-level capital? Measures government contracts, sovereign wealth fund interest, and national-security-grade business relationships.",
    "Political Intelligence":
        "How politically protected is this company? Defense contractors, utilities, and regulated monopolies have moats built by legislation, not just competition.",
    "ETF Gravity":
        "How deeply embedded is this stock in passive fund flows? Large ETF weightings create structural buying pressure — index inclusion is forced capital.",
    "Dark Pool Intelligence":
        "Is institutional money moving off-exchange? Elevated dark pool activity relative to average volume signals large players accumulating or distributing quietly.",
    "Options Warfare":
        "What is smart money doing in the options market? Unusual call or put activity, elevated IV, and skewed open interest reveal where sophisticated traders are positioning.",
    "Insider Conviction":
        "Are the people who know the most buying or holding? High insider ownership and purchases are one of the most reliable signals of management conviction.",
    "Leadership Intelligence":
        "Who is running this company and how good are they? Visionary founders and proven operators drive outsized long-term returns. Management quality is the ultimate moat.",
    "Economic Moat":
        "How durable is this company's competitive advantage? Pricing power, switching costs, network effects, and brand strength determine how long profits can be defended.",
    "Revenue Quality":
        "Is revenue growing, recurring, and real? High-quality revenue is predictable, diversified, and expanding — not one-time or dependent on a single customer.",
    "Government Influence":
        "Does the government fund, protect, or depend on this company? Defense, infrastructure, pharma, and utilities often receive invisible subsidies through contracts and regulation.",
    "War Chest":
        "How much cash does this company have to fight, acquire, and survive? Cash is optionality — it enables buybacks, M&A, R&D, and survival in downturns.",
    "Fortress Balance Sheet":
        "Can this company survive a crisis? Strong current ratios, manageable debt, and positive free cash flow mean it won't need emergency capital when markets freeze.",
    "M&A Probability":
        "Is this company likely to be acquired or to acquire? Strategic acquirers pay premiums — and serial acquirers compound value through smart capital deployment.",
    "Industry Dominance":
        "Is this company the undisputed leader in its sector? Market share leaders command pricing power, attract the best talent, and receive the most analyst coverage.",
    "Catalyst Calendar":
        "Are there near-term events that could move this stock? Earnings, FDA decisions, government contracts, product launches, and index additions are all binary catalysts.",
    "Market Regime Intelligence":
        "How does this stock behave when markets shift? Understanding whether a stock thrives in risk-on, risk-off, inflationary, or recessionary regimes is critical for timing.",
}


# ── 18 Scoring Functions ──────────────────────────────────────

def score_future_civilization(info, hist):
    """Future Civilization Exposure — AI, energy, biotech, space, automation."""
    s = 40
    summary = (info.get("longBusinessSummary","") or "").lower()
    sector  = (info.get("sector","") or "").lower()
    keywords = ["artificial intelligence","machine learning","semiconductor","nuclear",
                "renewable","genomic","space","satellite","autonomous","quantum",
                "robotics","biotech","drug discovery","ev","battery","clean energy"]
    hits = sum(1 for kw in keywords if kw in summary)
    s += min(hits * 7, 42)
    if sector in ["technology","healthcare"]: s += 8
    mc = safe(info, "marketCap", default=0) or 0
    if mc > 1e11: s += 8
    rd  = safe(info, "researchAndDevelopment", default=0) or 0
    rev = safe(info, "totalRevenue", default=1) or 1
    if rd / rev > 0.15: s += 10
    return clamp(s)

def score_institutional_power(info, hist, inst):
    """Institutional Power — concentration and size of institutional holders."""
    s = 50
    hld = safe(info, "heldPercentInstitutions", default=None)
    if hld is not None:
        if hld > 0.85:   s += 35
        elif hld > 0.70: s += 25
        elif hld > 0.55: s += 15
        elif hld > 0.35: s += 5
        else:            s -= 10
    elif inst is not None and not inst.empty:
        s += 8
    return clamp(s)

def score_sovereign_capital(info, hist):
    """Sovereign Capital — government contracts, sovereign-grade relationships."""
    s = 35
    summary  = (info.get("longBusinessSummary","") or "").lower()
    industry = (info.get("industry","") or "").lower()
    gov_kw   = ["government","department of defense","dod","pentagon","nato","military",
                "federal","contract","intelligence","classified","department of energy",
                "sovereign","strategic reserve","critical infrastructure"]
    hits = sum(1 for kw in gov_kw if kw in summary)
    s += min(hits * 10, 50)
    if "defense" in industry or "aerospace" in industry: s += 15
    return clamp(s)

def score_political_intelligence(info, hist):
    """Political Intelligence — regulatory moat, lobbying power, protected status."""
    s = 40
    sector   = (info.get("sector","") or "").lower()
    industry = (info.get("industry","") or "").lower()
    summary  = (info.get("longBusinessSummary","") or "").lower()
    # Regulated industries have political moats
    if sector in ["utilities","energy"]:           s += 25
    if "defense" in industry:                      s += 30
    if "pharmaceutical" in industry:               s += 20
    if "semiconductor" in industry:                s += 15
    if any(kw in summary for kw in ["regulatory","fda","fcc","patent","exclusive","license"]): s += 10
    # Very high market cap = too big to fail
    mc = safe(info, "marketCap", default=0) or 0
    if mc > 5e11: s += 10
    return clamp(s)

def score_etf_gravity(info, hist):
    """ETF Gravity — structural passive fund buying pressure."""
    s = 40
    mc = safe(info, "marketCap", default=0) or 0
    # Larger cap = higher index weighting = more ETF flows
    if mc > 2e12:   s += 40
    elif mc > 5e11: s += 30
    elif mc > 1e11: s += 20
    elif mc > 2e10: s += 10
    elif mc > 5e9:  s += 3
    else:           s -= 5
    # SP500 sector affects ETF inclusion breadth
    sector = (info.get("sector","") or "").lower()
    if sector == "technology":    s += 8
    if sector == "healthcare":    s += 5
    return clamp(s)

def score_dark_pool(info, hist):
    """Dark Pool Intelligence — off-exchange institutional flow signals."""
    s = 45
    inst_pct = safe(info, "heldPercentInstitutions", default=0.4) or 0.4
    # High institutional = high dark pool usage
    s += clamp((inst_pct - 0.5) * 60, -20, 30)
    avg_vol  = safe(info, "averageVolume", default=1) or 1
    avg10    = safe(info, "averageVolume10days", default=1) or 1
    vol_ratio = avg10 / avg_vol if avg_vol else 1
    if vol_ratio > 1.5: s += 15   # recent volume spike
    elif vol_ratio > 1.2: s += 8
    elif vol_ratio < 0.7: s -= 10
    sf = safe(info, "shortPercentOfFloat", default=0) or 0
    if sf > 0.20: s -= 10  # heavy short = unusual flow may be bearish
    return clamp(s)

def score_options_warfare(info, hist):
    """Options Warfare — smart money options positioning (proxy from public data)."""
    s = 50
    # Use short interest and volume as proxy for options flow intelligence
    sf = safe(info, "shortPercentOfFloat", default=0.05) or 0.05
    sr = safe(info, "shortRatio", default=3) or 3
    # Low short = call bias, high short = put bias; score neutral-to-bullish when low
    if sf < 0.03:      s += 20
    elif sf < 0.07:    s += 12
    elif sf < 0.15:    s += 0
    elif sf < 0.25:    s -= 12
    else:              s -= 22
    if sr < 2:   s += 10
    elif sr > 8: s -= 10
    # Analyst buy ratings = options community aligned
    rec = safe(info, "recommendationMean", default=3)
    s += (3 - rec) * 8
    return clamp(s)

def score_insider_conviction(info, hist, maj):
    """Insider Conviction — insider ownership and buy signal."""
    s = 45
    ins = safe(info, "heldPercentInsiders", default=None)
    if ins is not None:
        if ins > 0.25:   s += 35
        elif ins > 0.15: s += 25
        elif ins > 0.08: s += 15
        elif ins > 0.03: s += 5
        elif ins > 0.01: s += 0
        else:            s -= 10
    return clamp(s)

def score_leadership_intelligence(info, hist):
    """Leadership Intelligence — CEO quality, founder-led, execution track record."""
    s = 50
    roe = safe(info, "returnOnEquity", default=0) or 0
    roa = safe(info, "returnOnAssets", default=0) or 0
    pm  = safe(info, "profitMargins", default=0) or 0
    s += clamp(roe * 90, -20, 28)
    s += clamp(roa * 130, -15, 20)
    s += clamp(pm * 70, -10, 12)
    # Analyst confidence in leadership proxy
    rec = safe(info, "recommendationMean", default=3)
    s += (3 - rec) * 6
    return clamp(s)

def score_economic_moat(info, hist):
    """Economic Moat — pricing power, margins, competitive durability."""
    s = 45
    gm = safe(info, "grossMargins", default=0) or 0
    pm = safe(info, "profitMargins", default=0) or 0
    mc = safe(info, "marketCap", default=0) or 0
    s += clamp((gm - 0.30) * 80, -20, 30)
    s += clamp((pm - 0.10) * 100, -15, 20)
    if mc > 5e11: s += 12   # dominance = moat
    elif mc > 1e11: s += 6
    # Low P/S at high margin = pricing power
    ps = safe(info, "priceToSalesTrailing12Months", default=None)
    if ps and ps < 5 and gm > 0.40: s += 8
    return clamp(s)

def score_revenue_quality(info, hist):
    """Revenue Quality — growth, consistency, and margin expansion."""
    s = 40
    rg = safe(info, "revenueGrowth", default=0) or 0
    if rg > 0.30:    s = 90
    elif rg > 0.20:  s = 78
    elif rg > 0.10:  s = 65
    elif rg > 0.05:  s = 55
    elif rg > 0:     s = 44
    elif rg > -0.05: s = 32
    else:            s = 18
    gm = safe(info, "grossMargins", default=0) or 0
    s += clamp((gm - 0.35) * 50, -12, 12)
    eg = safe(info, "earningsGrowth", default=0) or 0
    s += clamp(eg * 40, -10, 15)
    return clamp(s)

def score_government_influence(info, hist):
    """Government Influence — contracts, subsidies, regulatory protection, critical status."""
    s = 35
    summary  = (info.get("longBusinessSummary","") or "").lower()
    sector   = (info.get("sector","") or "").lower()
    industry = (info.get("industry","") or "").lower()
    kw = ["government contract","federal","department of","defense","military","intelligence",
          "subsidy","grant","regulation","utility","critical infrastructure","strategic"]
    hits = sum(1 for k in kw if k in summary)
    s += min(hits * 9, 45)
    if sector == "utilities":             s += 20
    if "defense" in industry:             s += 25
    if "pharmaceutical" in industry:      s += 12
    if sector in ["energy","industrials"]: s += 8
    return clamp(s)

def score_war_chest(info, hist):
    """War Chest — cash position, optionality, and firepower for M&A/buybacks/R&D."""
    s = 40
    cash = safe(info, "totalCash", default=0) or 0
    mc   = safe(info, "marketCap", default=1) or 1
    debt = safe(info, "totalDebt", default=0) or 0
    net_cash = cash - debt
    # Net cash as % of market cap
    pct = net_cash / mc
    if pct > 0.20:    s += 40
    elif pct > 0.10:  s += 28
    elif pct > 0.05:  s += 16
    elif pct > 0:     s += 8
    elif pct > -0.10: s -= 5
    else:             s -= 18
    # Raw cash scale
    if cash > 1e11:  s += 10
    elif cash > 1e10: s += 5
    return clamp(s)

def score_fortress_balance_sheet(info, hist):
    """Fortress Balance Sheet — liquidity, debt management, financial resilience."""
    s = 50
    cr = safe(info, "currentRatio", default=1) or 1
    de = safe(info, "debtToEquity", default=100) or 100
    s += clamp((cr - 1.0) * 20, -22, 25)
    s -= clamp(de * 0.10, 0, 30)
    cash = safe(info, "totalCash", default=0) or 0
    debt = safe(info, "totalDebt", default=1) or 1
    if debt > 0:
        cdr = cash / debt
        s += clamp((cdr - 0.5) * 22, -10, 18)
    if not hist.empty and len(hist) > 20:
        vol = hist["Close"].pct_change().std() * (252 ** 0.5)
        s -= clamp((vol - 0.25) * 60, 0, 15)
    return clamp(s)

def score_ma_probability(info, hist):
    """M&A Probability — likelihood of acquisition or value-creating deal-making."""
    s = 35
    mc  = safe(info, "marketCap", default=0) or 0
    rg  = safe(info, "revenueGrowth", default=0) or 0
    gm  = safe(info, "grossMargins", default=0) or 0
    ps  = safe(info, "priceToSalesTrailing12Months", default=None)
    sector   = (info.get("sector","") or "").lower()
    industry = (info.get("industry","") or "").lower()
    # Sweet spot for acquisition: $1B-$50B market cap with strong margins
    if 1e9 < mc < 5e10:    s += 20
    elif 5e10 < mc < 2e11: s += 10
    # High margin + moderate growth = attractive acquisition target
    if gm > 0.50 and rg > 0.10: s += 18
    if ps and 3 < ps < 12:      s += 10
    # Consolidating sectors
    if any(k in industry for k in ["software","semiconductor","biotech","health"]): s += 12
    if sector == "technology": s += 8
    return clamp(s)

def score_industry_dominance(info, hist):
    """Industry Dominance — market share leadership and sector authority."""
    s = 45
    mc  = safe(info, "marketCap", default=0) or 0
    rev = safe(info, "totalRevenue", default=0) or 0
    gm  = safe(info, "grossMargins", default=0) or 0
    if mc > 1e12:   s += 35
    elif mc > 2e11: s += 25
    elif mc > 5e10: s += 15
    elif mc > 1e10: s += 7
    else:           s -= 5
    if gm > 0.60: s += 12
    elif gm > 0.40: s += 6
    rec = safe(info, "recommendationMean", default=3)
    s += (3 - rec) * 5
    return clamp(s)

def score_catalyst_calendar(info, hist):
    """Catalyst Calendar — upcoming earnings, product launches, regulatory events."""
    s = 50
    # Proxy: analyst coverage + earnings growth as forward catalyst signal
    n = safe(info, "numberOfAnalystOpinions", default=0) or 0
    if n >= 20: s += 15
    elif n >= 10: s += 8
    elif n >= 5:  s += 3
    rec = safe(info, "recommendationMean", default=3)
    s += (3 - rec) * 10
    current = safe(info, "currentPrice", "regularMarketPrice", default=0)
    target  = safe(info, "targetMeanPrice", default=0)
    if current and target:
        upside = (target - current) / current
        s += clamp(upside * 60, -18, 22)
    eg = safe(info, "earningsGrowth", default=0) or 0
    s += clamp(eg * 40, -12, 15)
    return clamp(s)

def score_market_regime(info, hist):
    """Market Regime Intelligence — behavior across risk-on, risk-off, and macro regimes."""
    s = 55
    beta  = safe(info, "beta", default=1) or 1
    sector = (info.get("sector","") or "").lower()
    de    = safe(info, "debtToEquity", default=50) or 50
    # Defensive sectors score higher (resilient across regimes)
    if sector in ["consumer staples","utilities","healthcare"]: s += 18
    elif sector in ["real estate","financial services"]:        s -= 8
    elif sector in ["technology","communication services"]:     s -= 5
    # Low beta = regime resilience
    s -= clamp((beta - 1) * 14, 0, 20)
    # High debt = rate-regime sensitivity
    s -= clamp(de * 0.04, 0, 12)
    if not hist.empty and len(hist) > 60:
        vol = hist["Close"].pct_change().std() * (252 ** 0.5)
        s -= clamp((vol - 0.25) * 55, 0, 15)
    return clamp(s)


def compute_all_scores(info, hist, inst, maj):
    return {
        "Future Civilization Exposure": score_future_civilization(info, hist),
        "Institutional Power":          score_institutional_power(info, hist, inst),
        "Sovereign Capital":            score_sovereign_capital(info, hist),
        "Political Intelligence":       score_political_intelligence(info, hist),
        "ETF Gravity":                  score_etf_gravity(info, hist),
        "Dark Pool Intelligence":       score_dark_pool(info, hist),
        "Options Warfare":              score_options_warfare(info, hist),
        "Insider Conviction":           score_insider_conviction(info, hist, maj),
        "Leadership Intelligence":      score_leadership_intelligence(info, hist),
        "Economic Moat":                score_economic_moat(info, hist),
        "Revenue Quality":              score_revenue_quality(info, hist),
        "Government Influence":         score_government_influence(info, hist),
        "War Chest":                    score_war_chest(info, hist),
        "Fortress Balance Sheet":       score_fortress_balance_sheet(info, hist),
        "M&A Probability":              score_ma_probability(info, hist),
        "Industry Dominance":           score_industry_dominance(info, hist),
        "Catalyst Calendar":            score_catalyst_calendar(info, hist),
        "Market Regime Intelligence":   score_market_regime(info, hist),
    }

WEIGHTS = {
    "Future Civilization Exposure": 0.09,
    "Institutional Power":          0.07,
    "Sovereign Capital":            0.05,
    "Political Intelligence":       0.04,
    "ETF Gravity":                  0.04,
    "Dark Pool Intelligence":       0.05,
    "Options Warfare":              0.06,
    "Insider Conviction":           0.05,
    "Leadership Intelligence":      0.07,
    "Economic Moat":                0.08,
    "Revenue Quality":              0.07,
    "Government Influence":         0.04,
    "War Chest":                    0.05,
    "Fortress Balance Sheet":       0.06,
    "M&A Probability":              0.03,
    "Industry Dominance":           0.06,
    "Catalyst Calendar":            0.04,
    "Market Regime Intelligence":   0.05,
}

def cfis_composite(scores):
    return clamp(sum(scores[k] * WEIGHTS[k] for k in CATEGORIES))

def opportunity_score(cfis, info, hist):
    s = cfis * 0.55
    current = safe(info, "currentPrice", "regularMarketPrice", default=0)
    target = safe(info, "targetMeanPrice", default=0)
    if current and target:
        upside = (target - current) / current
        s += clamp(upside * 55, -12, 22)
    if len(hist) > 50:
        close = hist["Close"]
        hi = close.max(); lo = close.min()
        pos = (close.iloc[-1] - lo) / (hi - lo + 0.001)
        s += (1 - pos) * 18
    return clamp(s)


# ─────────────────────────────────────────────────────────────
# OUTLOOKS
# ─────────────────────────────────────────────────────────────
def generate_outlooks(info, hist, score):
    current = safe(info, "currentPrice", "regularMarketPrice", default=0)
    target = safe(info, "targetMeanPrice", default=current) or current
    rev_growth = safe(info, "revenueGrowth", default=0.05) or 0.05
    analyst_annual = ((target - current) / current) if current and target else 0
    score_annual = (score - 50) / 100 * 0.50
    annual = score_annual * 0.60 + analyst_annual * 0.25 + rev_growth * 0.15
    if score < 42:
        annual = min(annual, -0.02)
    elif score < 55:
        annual = max(-0.08, min(annual, 0.06))
    results = {}
    for label, days in [("30 Day", 30), ("90 Day", 90), ("150 Day", 150), ("1 Year", 365)]:
        frac = days / 365
        pct = annual * frac
        price_t = current * (1 + pct) if current else 0
        if score >= 72:    direction = "📈 Bullish"
        elif score >= 60:  direction = "📈 Mild Bullish"
        elif score >= 45:  direction = "➡️ Neutral"
        elif score >= 32:  direction = "📉 Mild Bearish"
        else:              direction = "📉 Bearish"
        results[label] = {"pct": pct * 100, "price": price_t, "direction": direction}
    return results


# ─────────────────────────────────────────────────────────────
# BULL / BEAR / RECOMMENDATION
# ─────────────────────────────────────────────────────────────
def generate_cases(info, scores, cfis, opp, outlooks):
    name = info.get("shortName", info.get("longName", "This company"))
    current = safe(info, "currentPrice", "regularMarketPrice", default=0)
    target = safe(info, "targetMeanPrice", default=0)
    sector = info.get("sector", "")

    top3 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    bot3 = sorted(scores.items(), key=lambda x: x[1])[:3]

    strength_str = ", ".join(f"{k} ({v})" for k, v in top3)
    weakness_str = ", ".join(f"{k} ({v})" for k, v in bot3)

    upside_str = ""
    if current and target:
        upside = (target - current) / current * 100
        upside_str = f"with analyst targets implying {upside:+.1f}% {'upside' if upside > 0 else 'downside'}"

    outlook_1y = outlooks.get("1 Year", {})
    outlook_pct = outlook_1y.get("pct", 0)

    bull = (
        f"**Bull Case:** {name} is well-positioned for outperformance driven by strong {strength_str}. "
        f"If the sector continues to benefit from current tailwinds and management executes on growth initiatives, "
        f"the stock could deliver {max(outlook_pct, 10):+.0f}–{max(outlook_pct * 1.6, 20):+.0f}% returns over 12 months {upside_str}. "
        f"Institutional and analyst confidence supports the thesis."
    )

    bear = (
        f"**Bear Case:** Risks stem from weakness in {weakness_str}. "
        f"A deteriorating macro environment, rising interest rates, or sector rotation could pressure valuation multiples. "
        f"If growth disappoints, downside could reach {min(outlook_pct * 1.5, -8):+.0f}% or more. "
        f"High short interest or insider selling would accelerate the move lower."
    )

    if cfis >= 70:
        rec_text = "BUY"
        rec_color = "#4CAF50"
        rec_detail = f"CFIS-X score of {cfis}/100 signals a high-quality opportunity with favorable risk/reward."
    elif cfis >= 55:
        rec_text = "MODERATE BUY"
        rec_color = "#8BC34A"
        rec_detail = f"CFIS-X score of {cfis}/100 indicates above-average quality. Consider scaling in on pullbacks."
    elif cfis >= 42:
        rec_text = "HOLD"
        rec_color = "#FFC107"
        rec_detail = f"CFIS-X score of {cfis}/100 suggests mixed signals. Hold existing positions; wait for clarity before adding."
    elif cfis >= 28:
        rec_text = "CAUTION"
        rec_color = "#FF9800"
        rec_detail = f"CFIS-X score of {cfis}/100 flags material weaknesses. Reduce position or avoid new entries."
    else:
        rec_text = "AVOID"
        rec_color = "#f44336"
        rec_detail = f"CFIS-X score of {cfis}/100 indicates significant risk. Not suitable for new investment at this time."

    # Confidence = function of score spread + data availability
    spread = max(scores.values()) - min(scores.values())
    confidence = clamp(55 + (cfis - 50) * 0.4 - spread * 0.05)

    return bull, bear, rec_text, rec_color, rec_detail, confidence


# ─────────────────────────────────────────────────────────────
# OPTIONS ANALYSIS
# ─────────────────────────────────────────────────────────────
def render_options(calls, puts, dates, info, ticker):
    st.subheader("⚙️ Options Analysis")
    if calls is None or puts is None or not dates:
        st.info("No options data available for this ticker.")
        return

    current = safe(info, "currentPrice", "regularMarketPrice", default=0)

    with st.container():
        st.markdown(f"**Nearest Expiry:** {dates[0]}  |  **Current Price:** ${current:.2f}")

        c1, c2, c3 = st.columns(3)

        # Put/Call ratio
        total_call_oi = calls["openInterest"].sum() if "openInterest" in calls else 0
        total_put_oi  = puts["openInterest"].sum()  if "openInterest" in puts  else 0
        pc_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else None

        c1.metric("Total Call Open Interest", f"{total_call_oi:,.0f}")
        c2.metric("Total Put Open Interest",  f"{total_put_oi:,.0f}")
        if pc_ratio:
            pc_label = "Bearish" if pc_ratio > 1.2 else ("Bullish" if pc_ratio < 0.7 else "Neutral")
            c3.metric("Put/Call Ratio", f"{pc_ratio:.2f}", delta=pc_label)

        st.markdown("---")

        col_c, col_p = st.columns(2)

        with col_c:
            st.markdown("**📗 Top Calls by Open Interest**")
            if not calls.empty:
                show_cols = [c for c in ["strike", "lastPrice", "impliedVolatility", "openInterest", "volume"] if c in calls.columns]
                top_calls = calls[show_cols].sort_values("openInterest", ascending=False).head(8)
                top_calls.columns = [c.replace("impliedVolatility","IV%").replace("openInterest","OI").replace("lastPrice","Last").replace("strike","Strike").replace("volume","Vol") for c in top_calls.columns]
                if "IV%" in top_calls.columns:
                    top_calls["IV%"] = (top_calls["IV%"] * 100).round(1).astype(str) + "%"
                st.dataframe(top_calls, use_container_width=True, hide_index=True)

        with col_p:
            st.markdown("**📕 Top Puts by Open Interest**")
            if not puts.empty:
                show_cols = [c for c in ["strike", "lastPrice", "impliedVolatility", "openInterest", "volume"] if c in puts.columns]
                top_puts = puts[show_cols].sort_values("openInterest", ascending=False).head(8)
                top_puts.columns = [c.replace("impliedVolatility","IV%").replace("openInterest","OI").replace("lastPrice","Last").replace("strike","Strike").replace("volume","Vol") for c in top_puts.columns]
                if "IV%" in top_puts.columns:
                    top_puts["IV%"] = (top_puts["IV%"] * 100).round(1).astype(str) + "%"
                st.dataframe(top_puts, use_container_width=True, hide_index=True)

        # IV chart
        if "impliedVolatility" in calls.columns and "strike" in calls.columns:
            fig_iv = go.Figure()
            atm_calls = calls[(calls["strike"] > current * 0.8) & (calls["strike"] < current * 1.2)]
            atm_puts  = puts[(puts["strike"]  > current * 0.8) & (puts["strike"]  < current * 1.2)]
            if not atm_calls.empty:
                fig_iv.add_trace(go.Scatter(x=atm_calls["strike"], y=atm_calls["impliedVolatility"]*100,
                    mode="lines+markers", name="Call IV", line=dict(color="#4CAF50")))
            if not atm_puts.empty:
                fig_iv.add_trace(go.Scatter(x=atm_puts["strike"], y=atm_puts["impliedVolatility"]*100,
                    mode="lines+markers", name="Put IV", line=dict(color="#f44336")))
            fig_iv.add_vline(x=current, line_dash="dash", line_color="#FFC107",
                annotation_text="Current Price")
            fig_iv.update_layout(
                title="Implied Volatility Smile (ATM ±20%)",
                template="plotly_dark", height=300,
                xaxis_title="Strike", yaxis_title="IV %",
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig_iv, use_container_width=True)

        # Interpretation
        if pc_ratio:
            if pc_ratio > 1.3:
                interp = "🔴 **Bearish Signal:** Elevated put buying suggests hedging activity or directional bearish bets. Options market is pricing in downside risk."
            elif pc_ratio < 0.6:
                interp = "🟢 **Bullish Signal:** Strong call demand relative to puts indicates options traders are positioned for upside. Momentum may continue."
            else:
                interp = "🟡 **Neutral:** Put/call ratio near 1.0 suggests balanced sentiment. No strong directional signal from options market."
            st.markdown(f'<div class="section-box">{interp}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# DARK POOL ANALYSIS
# ─────────────────────────────────────────────────────────────
def render_dark_pool(info, hist):
    st.subheader("🌑 Dark Pool Analysis")
    st.caption("Dark pool activity is estimated from volume patterns, short interest, and institutional flow proxies. Direct dark pool data requires premium data feeds.")

    with st.container():
        current = safe(info, "currentPrice", "regularMarketPrice", default=0)
        avg_vol  = safe(info, "averageVolume", default=1) or 1
        avg10    = safe(info, "averageVolume10days", default=1) or 1
        vol_ratio = avg10 / avg_vol if avg_vol else 1

        # Estimate dark pool % (typically 30-50% of total volume in US markets)
        # Higher institutional ownership = higher dark pool usage
        inst_pct = safe(info, "heldPercentInstitutions", default=0.5) or 0.5
        est_dp_pct = 0.25 + inst_pct * 0.30  # rough proxy

        c1, c2, c3 = st.columns(3)
        c1.metric("Avg Daily Volume", f"{avg_vol:,.0f}")
        c2.metric("10-Day Avg Volume", f"{avg10:,.0f}")
        c3.metric("Est. Dark Pool Activity", f"{est_dp_pct*100:.0f}% of volume")

        st.markdown("---")

        # Volume vs price chart
        if not hist.empty and len(hist) > 20:
            recent = hist.tail(60)
            fig_vol = go.Figure()
            colors = ["#4CAF50" if c >= o else "#f44336"
                      for c, o in zip(recent["Close"], recent["Open"])]
            fig_vol.add_trace(go.Bar(
                x=recent.index, y=recent["Volume"],
                marker_color=colors, name="Volume", opacity=0.7
            ))
            fig_vol.add_trace(go.Scatter(
                x=recent.index, y=recent["Volume"].rolling(10).mean(),
                mode="lines", name="10-day MA", line=dict(color="#FFC107", width=2)
            ))
            fig_vol.update_layout(
                title="60-Day Volume Pattern (Green = Up Day, Red = Down Day)",
                template="plotly_dark", height=280,
                margin=dict(l=0, r=0, t=40, b=0), showlegend=True
            )
            st.plotly_chart(fig_vol, use_container_width=True)

        # Signals
        signals = []
        if vol_ratio > 1.3:
            signals.append(("🟢", "Recent volume spike above 20-day average — possible accumulation or institutional positioning."))
        elif vol_ratio < 0.7:
            signals.append(("🟡", "Below-average recent volume — quiet trading period, possible distribution or lack of conviction."))

        sf = safe(info, "shortPercentOfFloat", default=None)
        if sf and sf > 0.15:
            signals.append(("🔴", f"High short float ({sf*100:.1f}%) may indicate elevated dark pool hedging activity."))
        elif sf and sf < 0.03:
            signals.append(("🟢", f"Low short float ({sf*100:.1f}%) — minimal bearish dark pool hedging activity detected."))

        if inst_pct > 0.75:
            signals.append(("🟢", f"High institutional ownership ({inst_pct*100:.0f}%) correlates with significant dark pool usage — large blocks traded off-exchange."))

        if not signals:
            signals.append(("🟡", "Dark pool activity appears in line with historical norms. No unusual off-exchange flow detected."))

        st.markdown("**Signals:**")
        for icon, msg in signals:
            st.markdown(f"{icon} {msg}")


# ─────────────────────────────────────────────────────────────
# INSTITUTIONAL ACCUMULATION
# ─────────────────────────────────────────────────────────────
def render_institutional(info, inst, maj):
    st.subheader("🏛️ Institutional Accumulation")

    inst_pct = safe(info, "heldPercentInstitutions", default=None)
    ins_pct  = safe(info, "heldPercentInsiders", default=None)

    c1, c2, c3 = st.columns(3)
    c1.metric("Institutional Ownership", f"{inst_pct*100:.1f}%" if inst_pct else "N/A")
    c2.metric("Insider Ownership",       f"{ins_pct*100:.1f}%"  if ins_pct  else "N/A")
    sf = safe(info, "shortPercentOfFloat", default=None)
    c3.metric("Short % of Float",        f"{sf*100:.1f}%"       if sf       else "N/A")

    st.markdown("---")

    if inst is not None and not inst.empty:
        st.markdown("**Top Institutional Holders**")
        display = inst.copy()
        if "% Out" in display.columns:
            display["% Out"] = display["% Out"].apply(
                lambda x: f"{x*100:.2f}%" if pd.notna(x) and x < 1 else (f"{x:.2f}%" if pd.notna(x) else "N/A")
            )
        if "Shares" in display.columns:
            display["Shares"] = display["Shares"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
        if "Value" in display.columns:
            display["Value"] = display["Value"].apply(lambda x: fmt(x, "$") if pd.notna(x) else "N/A")
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("Detailed institutional holder list not available via free data feed.")

    if maj is not None and not maj.empty:
        st.markdown("**Major Holders Summary**")
        st.dataframe(maj, use_container_width=True, hide_index=True)

    # Interpretation
    if inst_pct:
        if inst_pct > 0.80:
            interp = "🟢 **Heavy institutional accumulation** — over 80% held by institutions. Strong vote of confidence from sophisticated money managers."
        elif inst_pct > 0.60:
            interp = "🟢 **Strong institutional presence** — institutions hold a majority stake, indicating broad professional interest."
        elif inst_pct > 0.35:
            interp = "🟡 **Moderate institutional ownership** — meaningful but not dominant institutional position. Room for further accumulation."
        else:
            interp = "🔴 **Low institutional ownership** — limited interest from professional money managers. May reflect early-stage or overlooked stock."
        st.markdown(f'<div class="section-box" style="margin-top:12px">{interp}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SCORECARD RENDERER
# ─────────────────────────────────────────────────────────────
ANALYSIS_TEMPLATES = {
    "Future Civilization Exposure": {
        "high": "This company is deeply embedded in the infrastructure of the next 20 years — AI, energy, biotech, or space. Capital will keep flowing here as civilization evolves.",
        "mid":  "Some exposure to future-defining sectors, but not at the core of any major megatrend. Solid business, limited civilization-scale upside.",
        "low":  "Limited exposure to the industries that will define the next decade. May face structural headwinds as capital rotates toward future-oriented sectors.",
    },
    "Institutional Power": {
        "high": "Dominated by institutional holders — hedge funds, pension funds, and sovereign managers. Big money has underwritten this stock. That concentration creates structural support.",
        "mid":  "Moderate institutional ownership. Professionals are present but haven't made this a core conviction holding. Interest is selective, not dominant.",
        "low":  "Low institutional ownership. Big money has largely passed. Could be an undiscovered gem — or a stock the smartest rooms in finance have already rejected.",
    },
    "Sovereign Capital": {
        "high": "This company has government-grade relationships — defense contracts, critical infrastructure status, or sovereign capital exposure. That's durable, recession-resistant revenue.",
        "mid":  "Some government adjacency, but not a primary revenue driver. Political relationships exist but aren't core to the business model.",
        "low":  "No meaningful government or sovereign capital exposure. Revenue depends entirely on commercial relationships, which are more cyclical and competitive.",
    },
    "Political Intelligence": {
        "high": "Politically protected — operates in a regulated industry, holds critical licenses, or is too strategically important to fail. The government is effectively a partner.",
        "mid":  "Some political exposure, but not a defining moat. Operates under standard commercial regulation with moderate lobbying or government interaction.",
        "low":  "Politically exposed without protection. Subject to regulatory disruption, new competition, or policy changes that could rapidly erode competitive advantages.",
    },
    "ETF Gravity": {
        "high": "This stock is a major index component with heavy ETF weighting. Passive capital flows in automatically as AUM grows. That's structural, non-discretionary buying.",
        "mid":  "Meaningful ETF inclusion, but not a dominant index weight. Some passive flow benefit, offset by less priority in rebalancing cycles.",
        "low":  "Limited ETF presence. Passive flows are minimal. Stock performance depends entirely on active fund conviction and retail interest.",
    },
    "Dark Pool Intelligence": {
        "high": "Elevated off-exchange activity signals institutional accumulation happening away from public markets. Large players are quietly building — often a precursor to price movement.",
        "mid":  "Dark pool activity appears in line with norms. No unusual off-exchange flow detected. Institutional activity is standard for this market cap.",
        "low":  "Low off-exchange activity. Either institutions aren't interested, or they're distributing. Low dark pool volume can signal a lack of institutional conviction.",
    },
    "Options Warfare": {
        "high": "Options flow is bullish — call buying dominates, put/call ratio is low, and smart money appears to be positioning for upside. The options market is aligned with the bull case.",
        "mid":  "Balanced options positioning. Neither strong call nor put bias. Smart money hasn't made a clear directional bet — wait for conviction to develop.",
        "low":  "Put-heavy options positioning or high short interest suggests the options market is hedging downside or betting against the stock. Respect the signal.",
    },
    "Insider Conviction": {
        "high": "Insiders hold a significant stake. When executives own large portions of their own company, their financial incentives align perfectly with shareholders. That's the strongest possible signal.",
        "mid":  "Moderate insider ownership. Leadership has exposure but it isn't the dominant shareholder dynamic. Interests are aligned, but not maximally so.",
        "low":  "Minimal insider ownership. Executives with little personal stake have less skin in the game. Compensation incentives may diverge from shareholder value creation.",
    },
    "Leadership Intelligence": {
        "high": "Exceptional management — high returns on equity, strong operating leverage, and a proven track record. This team knows how to compound capital and execute through cycles.",
        "mid":  "Competent management. Returns are adequate, operations are stable. No red flags, but no evidence of exceptional capital allocation or strategic vision.",
        "low":  "Weak management metrics. Low ROE, poor asset utilisation, or thin margins suggest the leadership team is not maximising the business's potential.",
    },
    "Economic Moat": {
        "high": "Deep competitive moat — pricing power, high switching costs, and dominant gross margins. Competitors can't easily take share. This business can defend its profits for years.",
        "mid":  "Moderate competitive advantages. Some pricing power or differentiation exists, but the moat isn't insurmountable. Competition could intensify over time.",
        "low":  "Thin or no discernible moat. Competing on price or in a commoditised market. Margins are vulnerable and market share can be taken by better-capitalised rivals.",
    },
    "Revenue Quality": {
        "high": "Revenue is growing fast, recurring, and accompanied by expanding margins. This is the kind of top-line that drives sustained stock appreciation over years.",
        "mid":  "Revenue is growing modestly and margins are stable. Steady but not exciting — needs a catalyst to accelerate.",
        "low":  "Revenue is declining or stagnant. Margins are under pressure. A company that can't grow its top line faces compounding problems downstream.",
    },
    "Government Influence": {
        "high": "Government contracts, subsidies, or regulatory protection are core to this business. The state is effectively a co-investor — providing revenue stability others can't match.",
        "mid":  "Some government adjacency — regulated industry or occasional contracts — but not a primary revenue driver or structural moat.",
        "low":  "No material government influence. Revenue is entirely market-driven. Exposed to competition and cyclical demand without the safety net of public sector relationships.",
    },
    "War Chest": {
        "high": "Substantial net cash position gives this company enormous optionality — to buy back shares, acquire competitors, fund R&D, or simply survive a downturn without dilution.",
        "mid":  "Adequate cash reserves relative to operations. Not positioned to make transformational moves, but has sufficient liquidity to fund normal business activity.",
        "low":  "Tight cash position or net debt. Limited ability to invest in growth, make acquisitions, or weather a revenue shortfall without diluting shareholders or raising expensive debt.",
    },
    "Fortress Balance Sheet": {
        "high": "Balance sheet is a genuine fortress — strong current ratio, manageable debt, and healthy cash flow. This company won't need emergency capital when markets freeze.",
        "mid":  "Adequate balance sheet. Debt and liquidity are within normal bounds. Not vulnerable to near-term financial stress under normal operating conditions.",
        "low":  "Balance sheet shows stress — high debt, weak liquidity, or poor cash flow. A revenue miss or market freeze could force dilutive capital raises.",
    },
    "M&A Probability": {
        "high": "High probability of M&A activity — either as an attractive acquisition target or as an active acquirer. Valuations, sector dynamics, and size support deal potential.",
        "mid":  "Some M&A optionality, but no clear catalyst. Could be involved in sector consolidation, but timing and probability are uncertain.",
        "low":  "Low M&A probability. Either too large to be acquired, in a non-consolidating sector, or with a balance sheet that makes deal-making unlikely.",
    },
    "Industry Dominance": {
        "high": "Clear sector leader — largest market cap, highest revenue, and strongest brand in its space. Dominance attracts talent, pricing power, and media attention that compounds over time.",
        "mid":  "Strong position but not dominant. Competes effectively in its segment without controlling the industry. Vulnerable to disruption from above or below.",
        "low":  "Small player in a competitive market. Limited pricing power, lower brand recognition, and fewer resources to sustain long-term market share gains.",
    },
    "Catalyst Calendar": {
        "high": "Near-term catalysts are stacked — analyst upgrades, earnings beats, product launches, or regulatory approvals could accelerate the thesis faster than the market expects.",
        "mid":  "Some catalysts on the horizon, but timing is uncertain. Earnings or product news could move the stock, but there's no imminent binary event.",
        "low":  "No clear near-term catalysts. The stock is in a quiet period — movement will depend on macro conditions or surprise news rather than scheduled events.",
    },
    "Market Regime Intelligence": {
        "high": "This stock performs well across multiple market regimes — defensive in downturns, participates in rallies. A true all-weather holding with regime resilience.",
        "mid":  "Moderate regime sensitivity. Performs well in risk-on environments but may underperform in rate-rising or recessionary cycles.",
        "low":  "Highly regime-sensitive — strong in one condition, weak in another. Requires precise macro timing to hold effectively. Not suitable for passive long-term positions.",
    },
}

def get_analysis(cat, val):
    tmpl = ANALYSIS_TEMPLATES.get(cat, {})
    if val >= 63:   return tmpl.get("high", "")
    if val >= 42:   return tmpl.get("mid", "")
    return tmpl.get("low", "")


def render_scorecard(scores):
    st.subheader("📋 CFIS-X 18-Category Scorecard")

    for cat in CATEGORIES:
        val  = scores[cat]
        t    = tier(val)
        bar_color = {"green": "#4CAF50", "yellow": "#FFC107", "red": "#f44336"}[t]
        what = DESCRIPTIONS[cat]
        analysis = get_analysis(cat, val)
        st.markdown(f"""
        <div class="score-row {t}">
            <div class="score-num {t}">{val}</div>
            <div class="score-body">
                <div class="score-name">{cat}</div>
                <div class="score-what">{what}</div>
                <div class="score-analysis">💬 {analysis}</div>
                <div class="bar-bg">
                    <div class="bar-fill" style="width:{val}%;background:{bar_color}"></div>
                </div>
            </div>
            <div style="text-align:right;padding-top:2px">
                <span class="tier-badge {t}">{tier_label(val)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# STRENGTHS & WEAKNESSES
# ─────────────────────────────────────────────────────────────
def render_strengths_weaknesses(scores):
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    strengths = [s for s in sorted_scores if s[1] >= 60][:6]
    weaknesses = [s for s in reversed(sorted_scores) if s[1] < 50][:6]

    col_s, col_w = st.columns(2)

    with col_s:
        st.markdown("### ✅ Strengths")
        if strengths:
            for cat, val in strengths:
                st.markdown(f"""
                <div style="background:#1a3a1a;border-radius:8px;padding:10px 14px;margin:4px 0;border-left:3px solid #4CAF50">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <span style="color:#fff;font-size:13px;font-weight:600">{cat}</span>
                        <span style="color:#4CAF50;font-size:18px;font-weight:800">{val}</span>
                    </div>
                    <div style="font-size:11px;color:#b0b8cc;margin-top:3px">{DESCRIPTIONS[cat][:80]}…</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No strong categories detected.")

    with col_w:
        st.markdown("### ⚠️ Weaknesses")
        if weaknesses:
            for cat, val in weaknesses:
                st.markdown(f"""
                <div style="background:#3a1a1a;border-radius:8px;padding:10px 14px;margin:4px 0;border-left:3px solid #f44336">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <span style="color:#fff;font-size:13px;font-weight:600">{cat}</span>
                        <span style="color:#f44336;font-size:18px;font-weight:800">{val}</span>
                    </div>
                    <div style="font-size:11px;color:#b0b8cc;margin-top:3px">{DESCRIPTIONS[cat][:80]}…</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No significant weaknesses identified.")


# ─────────────────────────────────────────────────────────────
# LOUIS INTUITION ENGINE
# ─────────────────────────────────────────────────────────────

##################################################################
# LOUIS INTUITION ENGINE v2
##################################################################

# ── Known Visionary Leaders ───────────────────────────────────
# Score = how much this leader moves markets and drives conviction
LEADER_MAP = {
    "NVDA":  ("Jensen Huang",    98, "Architect of the AI compute era. Every AI dollar flows through his silicon."),
    "TSLA":  ("Elon Musk",       95, "Polarising genius. Where he goes, capital follows — and media never sleeps."),
    "META":  ("Mark Zuckerberg", 88, "Rebuilt himself post-2022. Now executing on AI+AR with founder precision."),
    "MSFT":  ("Satya Nadella",   90, "Quietly turned Microsoft into the enterprise AI backbone. Steady and lethal."),
    "AMZN":  ("Andy Jassy",      78, "Operational beast. AWS is the cloud floor everything else stands on."),
    "GOOGL": ("Sundar Pichai",   75, "DeepMind + Search + Cloud. Powerful but slow to move. Watch Gemini."),
    "AAPL":  ("Tim Cook",        80, "Distribution king. When Apple enters a space, the space gets legitimised."),
    "AMD":   ("Lisa Su",         92, "Best turnaround CEO of the decade. Took AMD from near-dead to NVDA rival."),
    "PLTR":  ("Alex Karp",       88, "Visionary contrarian. Sells to governments others won't touch. Sticky moat."),
    "AVGO":  ("Hock Tan",        85, "M&A genius. Turns acquisitions into cash machines. Quiet but deadly."),
    "COIN":  ("Brian Armstrong",  82, "Crypto's most credible CEO. Built through every bear market. Regulation is his moment."),
    "RKLB":  ("Peter Beck",       90, "The man making space access routine. Smallsat launch leader with real conviction."),
    "ASTS":  ("Abel Avellan",     87, "Betting the entire business on space-based broadband. Audacious and focused."),
    "IONQ":  ("Peter Chapman",    80, "Quantum computing before it's obvious. High risk, generational upside."),
    "HOOD":  ("Vlad Tenev",       75, "Retail finance democratiser. Crypto + equities on one platform."),
    "XYZ":   ("Jack Dorsey",      82, "Payments meets Bitcoin conviction. Builder, not a manager."),
    "SHOP":  ("Tobi Lütke",       88, "Founder-led, long-term thinker. Commerce infrastructure for the next decade."),
    "MSTR":  ("Michael Saylor",   85, "100% Bitcoin conviction. Most concentrated macro bet by any public CEO."),
    "SMCI":  ("Charles Liang",    80, "AI server builder nobody talked about until everyone needed him."),
    "ARM":   ("Rene Haas",        78, "Designs the chips inside everything. Royalty model = durable cash flow."),
    "CEG":   ("Joe Dominguez",    80, "Nuclear power comeback leader. AI data centres need what he sells."),
    "NOW":   ("Bill McDermott",   82, "Enterprise software operator. AI workflow automation at scale."),
    "CRM":   ("Marc Benioff",     80, "Cloud pioneer turned AI agent platform. Opinionated and vocal."),
    "MRVL":  ("Matt Murphy",      78, "Custom silicon for cloud giants. Behind the scenes but critical."),
    "ANET":  ("Jayshree Ullal",   85, "Networking for AI data centres. Quiet monopolist in cloud switching."),
    "SNOW":  ("Sridhar Ramaswamy",77, "Data cloud plus AI. The place enterprises land their data first."),
    "PATH":  ("Daniel Dines",     80, "RPA and agentic automation. Robotic process automation before it was cool."),
    "UBER":  ("Dara Khosrowshahi",75, "Turned a burning platform into a logistics and delivery machine."),
    "NFLX":  ("Ted Sarandos",     78, "Content machine + advertising pivot. Streaming wars survivor and winner."),
    "ADBE":  ("Shantanu Narayen", 80, "Creative cloud monopolist adding AI generation. Designers can't leave."),
}

LOUIS_THEMES = {
    "AI Extension": {
        "icon": "🤖", "color": "#7c3aed", "border": "#a855f7",
        "keywords": ["semiconductor","artificial intelligence","machine learning","cloud","data center",
                     "gpu","chip","inference","compute","neural","language model","generative"],
        "sectors": ["Technology","Communication Services"],
        "why": "AI is rewriting every industry. The picks here sit inside the actual compute stack — the picks and shovels of the AI gold rush.",
    },
    "Energy Infrastructure": {
        "icon": "⚡", "color": "#b45309", "border": "#f59e0b",
        "keywords": ["nuclear","uranium","solar","wind","grid","lng","power","electricity",
                     "energy","oil","gas","pipeline","utility","renewable","hydrogen","battery"],
        "sectors": ["Energy","Utilities"],
        "why": "AI data centres need massive power. Nuclear is back. Energy independence is now national security. The grid is the next battleground.",
    },
    "Space Tech": {
        "icon": "🚀", "color": "#0e7490", "border": "#06b6d4",
        "keywords": ["space","satellite","launch","orbital","rocket","aerospace","lunar","constellation","broadband"],
        "sectors": ["Industrials"],
        "why": "Governments and billionaires are racing for orbital dominance. Low-Earth orbit is the new contested terrain. Satellite broadband is the infrastructure layer beneath everything.",
    },
    "Robotics & Automation": {
        "icon": "🦾", "color": "#065f46", "border": "#10b981",
        "keywords": ["robot","automation","autonomous","humanoid","surgical","factory","manufacturing","drone","lidar","cobots"],
        "sectors": ["Industrials","Technology","Healthcare"],
        "why": "Labour shortage + reshoring = robotics supercycle. Humanoid robots are moving from labs to factory floors. The physical world is being automated.",
    },
    "Tokenized Finance": {
        "icon": "🪙", "color": "#1e3a5f", "border": "#3b82f6",
        "keywords": ["crypto","bitcoin","blockchain","digital asset","tokeniz","defi","stablecoin","web3",
                     "payment","settlement","custody","institutional","placement"],
        "sectors": ["Financial Services","Technology"],
        "why": "Stablecoins are clearing trillions. Real-world asset tokenisation is live. Institutional block trades are moving on-chain. The rails of finance are being rebuilt.",
    },
    "Medical AI": {
        "icon": "🧬", "color": "#7f1d1d", "border": "#ef4444",
        "keywords": ["biotech","pharma","genomic","diagnostic","medical","drug","therapeutics",
                     "clinical","precision medicine","cancer","ai health","radiology","pathology"],
        "sectors": ["Healthcare"],
        "why": "Biology meets computation. AI diagnostics, drug discovery, and precision medicine are compressing decades of R&D into years. Defensible and sticky.",
    },
    "Future Food Supply": {
        "icon": "🌾", "color": "#3f6212", "border": "#84cc16",
        "keywords": ["food","agriculture","fertilizer","crop","protein","vertical farm","agtech",
                     "seed","potash","nutrition","aquaculture","alternative protein","supply chain"],
        "sectors": ["Consumer Staples","Materials","Industrials"],
        "why": "Feeding 10 billion people is an engineering problem. Water scarcity, climate disruption, and fertiliser supply shocks make agtech a national security issue.",
    },
    "Defense / Geopolitical": {
        "icon": "🛡️", "color": "#374151", "border": "#9ca3af",
        "keywords": ["defense","military","missile","weapon","intelligence","cybersecurity",
                     "surveillance","nato","pentagon","government","classified","security"],
        "sectors": ["Industrials","Technology"],
        "why": "The world is re-arming. NATO budgets are up. Cyber warfare is daily. Defense spending is the most durable government budget line — recession-proof.",
    },
    "HNWI Wealth Infrastructure": {
        "icon": "🏛️", "color": "#78350f", "border": "#d97706",
        "keywords": ["private equity","wealth management","asset management","investment bank",
                     "hedge fund","real estate","luxury","private banking","family office","alternative"],
        "sectors": ["Financial Services","Real Estate"],
        "why": "The ultra-wealthy are growing their share of global capital. The infrastructure that moves, protects, and multiplies serious wealth is a durable business.",
    },
    "Scarcity / Strategic Asset": {
        "icon": "💎", "color": "#1e1b4b", "border": "#818cf8",
        "keywords": ["rare earth","lithium","cobalt","copper","gold","silver","mining","uranium",
                     "water","critical mineral","commodity","strategic reserve","helium"],
        "sectors": ["Basic Materials","Energy"],
        "why": "The energy transition and tech buildout need materials the world is running short of. Whoever controls the inputs controls the output.",
    },
}


def detect_louis_theme(info):
    sector   = (info.get("sector", "") or "").lower()
    industry = (info.get("industry", "") or "").lower()
    summary  = (info.get("longBusinessSummary", "") or "").lower()
    combined = f"{sector} {industry} {summary}"
    hit_scores = {}
    for theme, data in LOUIS_THEMES.items():
        hits = sum(1 for kw in data["keywords"] if kw in combined)
        sec_hit = any(s.lower() in sector for s in data["sectors"])
        hit_scores[theme] = hits * 2 + (5 if sec_hit else 0)
    return max(hit_scores, key=hit_scores.get)


def get_leader_intel(info, ticker):
    """Return (name, power_score, commentary) for the CEO/founder."""
    if ticker.upper() in LEADER_MAP:
        return LEADER_MAP[ticker.upper()]
    # Proxy: use insider ownership + company description
    ins = safe(info, "heldPercentInsiders", default=0) or 0
    name = info.get("companyOfficers", [{}])[0].get("name", "Unknown CEO") if info.get("companyOfficers") else "Unknown CEO"
    if ins > 0.15:
        return (name, 75, "Significant insider ownership signals the leader has real skin in the game.")
    elif ins > 0.05:
        return (name, 60, "Moderate insider ownership. Leadership is invested but not dominant.")
    else:
        return (name, 45, "Low insider ownership. Hard to gauge leadership conviction from public data.")


def options_gambling_signal(opts_calls, opts_puts, info):
    """
    Detect smart-money gambling behaviour from options flow.
    Returns: signal dict with bias, intensity, unusual flags.
    """
    current = safe(info, "currentPrice", "regularMarketPrice", default=0) or 1
    result = {
        "bias": "Neutral", "bias_color": "#FFC107",
        "pc_ratio": None, "call_oi": 0, "put_oi": 0,
        "unusual_calls": False, "unusual_puts": False,
        "iv_signal": "Normal", "smart_money_note": "",
        "has_data": False,
    }
    if opts_calls is None or opts_puts is None:
        result["smart_money_note"] = "No options data available for this ticker."
        return result

    result["has_data"] = True
    call_oi = int(opts_calls["openInterest"].sum()) if "openInterest" in opts_calls else 0
    put_oi  = int(opts_puts["openInterest"].sum())  if "openInterest" in opts_puts  else 0
    result["call_oi"] = call_oi
    result["put_oi"]  = put_oi

    # Put/Call ratio
    pc = put_oi / call_oi if call_oi > 0 else 1.0
    result["pc_ratio"] = pc

    # Detect far-OTM speculative call buying (gambling on moonshot)
    if "strike" in opts_calls.columns and "volume" in opts_calls.columns:
        otm_calls = opts_calls[opts_calls["strike"] > current * 1.20]
        total_vol  = opts_calls["volume"].sum() or 1
        otm_vol    = otm_calls["volume"].sum()
        if otm_vol / total_vol > 0.30:
            result["unusual_calls"] = True

    # Detect defensive put buying
    if "strike" in opts_puts.columns and "volume" in opts_puts.columns:
        otm_puts  = opts_puts[opts_puts["strike"] < current * 0.85]
        total_pvol = opts_puts["volume"].sum() or 1
        otm_pvol   = otm_puts["volume"].sum()
        if otm_pvol / total_pvol > 0.30:
            result["unusual_puts"] = True

    # Average implied volatility signal
    if "impliedVolatility" in opts_calls.columns:
        avg_iv = opts_calls["impliedVolatility"].median() * 100
        if avg_iv > 80:   result["iv_signal"] = "🔥 Explosive — market pricing huge move"
        elif avg_iv > 50: result["iv_signal"] = "⚡ Elevated — smart money expects volatility"
        elif avg_iv > 30: result["iv_signal"] = "📊 Normal — routine pricing"
        else:             result["iv_signal"] = "😴 Suppressed — complacency or dull period"

    # Final bias
    if pc < 0.6 and result["unusual_calls"]:
        result["bias"] = "🟢 Heavy Call Buying — Bullish Speculation"
        result["bias_color"] = "#4CAF50"
        result["smart_money_note"] = (
            "Options traders are loading up on calls, including far out-of-the-money strikes. "
            "This is classic gambling behaviour on a big move up — someone expects a catalyst."
        )
    elif pc < 0.75:
        result["bias"] = "🟢 Call Bias — Bullish Lean"
        result["bias_color"] = "#4CAF50"
        result["smart_money_note"] = (
            "More call open interest than puts. The options market is leaning bullish. "
            "No extreme speculation, but institutional money is positioned for upside."
        )
    elif pc > 1.4 and result["unusual_puts"]:
        result["bias"] = "🔴 Heavy Put Buying — Bearish Hedge"
        result["bias_color"] = "#f44336"
        result["smart_money_note"] = (
            "Deep out-of-the-money puts are being bought aggressively. "
            "This is either someone hedging a large long position — or betting on a crash. Either way, respect it."
        )
    elif pc > 1.1:
        result["bias"] = "🔴 Put Bias — Bearish Lean"
        result["bias_color"] = "#f44336"
        result["smart_money_note"] = (
            "More put open interest than calls. The options market is defensive. "
            "Could be hedging by institutions — but elevated puts are a yellow flag."
        )
    else:
        result["bias"] = "🟡 Neutral — Balanced Flow"
        result["bias_color"] = "#FFC107"
        result["smart_money_note"] = (
            "Put/call ratio near 1:1. No strong directional conviction from options traders. "
            "Wait for unusual activity to develop before reading too much into this."
        )
    return result


def louis_intuition_engine(info, hist, ticker, opts_calls, opts_puts):
    """9-dimension strategic scoring."""
    sector  = (info.get("sector", "") or "").lower()
    summary = (info.get("longBusinessSummary", "") or "").lower()
    combined = f"{sector} {summary}"

    mc       = safe(info, "marketCap", default=0) or 0
    rd       = safe(info, "researchAndDevelopment", default=0) or 0
    rev      = safe(info, "totalRevenue", default=1) or 1
    rd_ratio = rd / rev if rev > 0 else 0
    inst_pct = safe(info, "heldPercentInstitutions", default=0.4) or 0.4
    _, leader_power, _ = get_leader_intel(info, ticker)

    def kw(words, base=35, per=9, cap=45):
        return min(base + sum(1 for w in words if w in combined) * per, base + cap)

    fcr     = kw(["ai","semiconductor","nuclear","space","gene","robot","quantum","autonomous","biotech","energy transition"])
    if mc > 5e11: fcr = min(fcr + 10, 100)

    geo     = kw(["semiconductor","defense","nuclear","lng","rare earth","satellite","cyber","military","critical","chip"], base=30, per=10)
    if "china" in summary or "taiwan" in summary: geo = min(geo + 15, 100)

    scar    = kw(["uranium","lithium","cobalt","rare earth","copper","patent","proprietary","exclusive","monopoly"], base=25, per=12)
    if rd_ratio > 0.15: scar = min(scar + 12, 100)
    if mc > 1e12: scar = min(scar + 8, 100)

    cap_mag = clamp(40 + min(20, inst_pct * 25) + (leader_power - 50) * 0.3 +
                    kw(["ai","infrastructure","defense","semiconductor"], base=0, per=7, cap=20))

    nsr     = kw(["defense","military","intelligence","cybersecurity","nuclear","satellite","government","classified"], base=20, per=12)

    infra   = kw(["cloud","grid","pipeline","network","platform","data center","exchange","utility","backbone","critical"], base=35, per=9)
    if mc > 5e10: infra = min(infra + 8, 100)

    ai_lev  = kw(["artificial intelligence","machine learning","gpu","inference","generative","autonomous","algorithm","ai-powered"], base=25, per=10)
    if rd_ratio > 0.12: ai_lev = min(ai_lev + 12, 100)

    energy  = kw(["uranium","nuclear","lng","solar","wind","grid","power generation","pipeline","energy storage","hydrogen"], base=25, per=12)

    scc     = kw(["supply chain","semiconductor","rare earth","pharmaceutical","critical","sole supplier","largest producer","market leader"], base=30, per=10)

    return {
        "Future Civilization Relevance": clamp(fcr),
        "Geopolitical Importance":       clamp(geo),
        "Strategic Scarcity":            clamp(scar),
        "Capital Magnet Potential":      clamp(cap_mag),
        "National Security Relevance":   clamp(nsr),
        "Infrastructure Importance":     clamp(infra),
        "AI Leverage":                   clamp(ai_lev),
        "Energy Control":                clamp(energy),
        "Supply Chain Criticality":      clamp(scc),
    }


def louis_conviction_score(dims, leader_power):
    w = {
        "Future Civilization Relevance": 0.17,
        "Geopolitical Importance":       0.14,
        "Strategic Scarcity":            0.12,
        "Capital Magnet Potential":      0.12,
        "National Security Relevance":   0.10,
        "Infrastructure Importance":     0.11,
        "AI Leverage":                   0.10,
        "Energy Control":                0.07,
        "Supply Chain Criticality":      0.07,
    }
    base = sum(dims[k] * w[k] for k in dims)
    # Leader power has a 15% influence on conviction
    return clamp(base * 0.85 + leader_power * 0.15)


def generate_15day_scenario(info, hist, dims, conviction, opts_signal):
    current = safe(info, "currentPrice", "regularMarketPrice", default=0) or 0
    beta    = safe(info, "beta", default=1) or 1

    mom_15 = 0
    if len(hist) >= 15:
        mom_15 = (hist["Close"].iloc[-1] - hist["Close"].iloc[-15]) / hist["Close"].iloc[-15]

    strategic = (dims["Geopolitical Importance"] + dims["Strategic Scarcity"] +
                 dims["AI Leverage"] + dims["Infrastructure Importance"]) / 4
    opt_boost = 8 if opts_signal["bias_color"] == "#4CAF50" else (-8 if opts_signal["bias_color"] == "#f44336" else 0)
    total = conviction * 0.45 + strategic * 0.30 + mom_15 * 100 * 0.15 + opt_boost * 0.10

    if total >= 60:
        bias, opt_rec, oc, direction = "📈 Bullish", "Calls", "#4CAF50", 1
        lo, hi = max(2.5, beta * 3), max(6.0, beta * 7)
    elif total <= 38:
        bias, opt_rec, oc, direction = "📉 Bearish", "Puts", "#f44336", -1
        lo, hi = max(2.0, beta * 2.5), max(5.5, beta * 6)
    else:
        bias, opt_rec, oc, direction = "➡️ Neutral", "Straddle / Hold", "#FFC107", 0
        lo, hi = 1.0, max(3.5, beta * 3)

    lo_p  = current * (1 + direction * lo / 100) if current else 0
    hi_p  = current * (1 + direction * hi / 100) if current else 0
    if direction == -1: lo_p, hi_p = hi_p, lo_p

    return {"bias": bias, "opt_rec": opt_rec, "opt_color": oc,
            "lo_pct": lo, "hi_pct": hi, "lo_price": lo_p, "hi_price": hi_p,
            "mom_15": mom_15 * 100, "total_signal": total}


def louis_plain_reason(info, ticker, theme, dims, conviction, leader_name, leader_power, leader_note, opts_signal, scenario):
    name = info.get("shortName") or info.get("longName", ticker)

    openers = {
        "AI Extension":              f"{name} is inside the AI compute stack — every dollar of AI spend has to flow through infrastructure like this.",
        "Energy Infrastructure":     f"{name} sits on the energy systems civilization literally cannot switch off. AI data centres need what they sell.",
        "Space Tech":                f"{name} is playing in the new contested frontier — low-Earth orbit and beyond. Governments are the biggest customers.",
        "Robotics & Automation":     f"{name} is automating the physical world at a time when labour is scarce and reshoring is policy.",
        "Tokenized Finance":         f"{name} is building on the new financial rails — stablecoins, tokenised assets, or the institutional pipes that move serious capital.",
        "Medical AI":                f"{name} sits where biology meets computation. Drug discovery or AI diagnostics — the moat here is scientific, not just technical.",
        "Future Food Supply":        f"{name} is inside the food and agri supply chain at a time when water, land, and fertiliser scarcity are escalating.",
        "Defense / Geopolitical":    f"{name} is a direct beneficiary of a world re-arming and re-securing its borders. Government revenue is recession-proof.",
        "HNWI Wealth Infrastructure":f"{name} manages or moves serious capital. HNWI flows are growing faster than GDP — this is durable business.",
        "Scarcity / Strategic Asset":f"{name} controls or has exposure to something the world needs more of and can't easily replace.",
    }
    lines = [openers.get(theme, f"{name} fits my strategic worldview in the {theme} space.")]

    # Leader line
    if leader_power >= 80:
        lines.append(f"**{leader_name}** is one of the leaders I track closely — {leader_note}")
    elif leader_power >= 65:
        lines.append(f"**{leader_name}** is running this with credibility. {leader_note}")
    else:
        lines.append(f"Leadership is a question mark here. {leader_note}")

    # Dimension-specific commentary
    if dims["Geopolitical Importance"] >= 65:
        lines.append("Geopolitically, this is a name that governments want to protect or own — that's a tailwind no analyst model captures.")
    if dims["Strategic Scarcity"] >= 65:
        lines.append("The scarcity angle is genuine — what they control isn't easy to replicate or substitute.")
    if dims["AI Leverage"] >= 65:
        lines.append("AI is a direct multiplier on their model — not a marketing slide, an actual revenue lever.")
    if dims["National Security Relevance"] >= 60:
        lines.append("National security relevance means government contracts, protected moats, and sticky multi-year revenue.")

    # Options read
    lines.append(f"Options flow says: {opts_signal['smart_money_note']}")

    # Close with conviction voice
    if conviction >= 75:
        lines.append("My conviction is high. This is the type of name I'd hold through volatility and add on weakness.")
    elif conviction >= 55:
        lines.append("Solid conviction — size it right and watch the next catalyst.")
    else:
        lines.append("This is speculative in my framework. Small size, defined risk, patience.")

    lines.append(f"⚠️ The 15-Day Scenario is {scenario['bias']} ({scenario['lo_pct']:.1f}–{scenario['hi_pct']:.1f}% estimated move). "
                 "This is a scenario based on signal — not a promise. Markets don't care about our logic.")

    return " ".join(lines)


def render_louis_pick(info, hist, cfis_scores, ticker="", opts_calls=None, opts_puts=None):
    theme       = detect_louis_theme(info)
    theme_data  = LOUIS_THEMES[theme]
    dims        = louis_intuition_engine(info, hist, ticker, opts_calls, opts_puts)
    leader_name, leader_power, leader_note = get_leader_intel(info, ticker)
    conviction  = louis_conviction_score(dims, leader_power)
    opts_signal = options_gambling_signal(opts_calls, opts_puts, info)
    scenario    = generate_15day_scenario(info, hist, dims, conviction, opts_signal)
    reason      = louis_plain_reason(info, ticker, theme, dims, conviction,
                                     leader_name, leader_power, leader_note, opts_signal, scenario)

    # ── Determine CALL / PUT / HOLD verdict ──────────────────
    sig = scenario["total_signal"]
    if sig >= 62:
        verdict, verdict_color, verdict_bg, verdict_emoji = "CALL PICK", "#4CAF50", "#0a2a0a", "📈"
        verdict_desc = "Louis sees bullish alignment — conviction, leadership, and options flow support the long side."
    elif sig <= 38:
        verdict, verdict_color, verdict_bg, verdict_emoji = "PUT PICK", "#f44336", "#2a0a0a", "📉"
        verdict_desc = "Louis sees bearish signals — weak strategic fit, poor options flow, or deteriorating momentum."
    else:
        verdict, verdict_color, verdict_bg, verdict_emoji = "HOLD / WATCH", "#FFC107", "#2a2200", "⏸️"
        verdict_desc = "Mixed signals. No strong directional conviction right now. Wait for a clearer setup."

    icon   = theme_data["icon"]
    col    = theme_data["color"]
    border = theme_data["border"]
    lp_c   = "#4CAF50" if leader_power >= 75 else ("#FFC107" if leader_power >= 55 else "#f44336")
    conv_c = "#4CAF50" if conviction >= 65 else ("#FFC107" if conviction >= 45 else "#f44336")

    # ── 1. BIG VERDICT ───────────────────────────────────────
    st.markdown(f"""
    <div style="background:{verdict_bg};border:2px solid {verdict_color};border-radius:16px;
                padding:24px;text-align:center;margin-bottom:16px">
        <div style="font-size:13px;color:#b0bcd4;letter-spacing:2px;margin-bottom:8px">
            👁️ LOUIS PICK
        </div>
        <div style="font-size:52px;font-weight:900;color:{verdict_color};line-height:1">
            {verdict_emoji} {verdict}
        </div>
        <div style="font-size:14px;color:#e8ecf4;margin-top:12px;line-height:1.5">
            {verdict_desc}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 2. THEME + 4 KEY NUMBERS ─────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"""<div style="background:#0e1117;border-radius:10px;padding:14px;text-align:center;border-top:3px solid {col}">
        <div style="font-size:22px">{icon}</div>
        <div style="font-size:11px;color:#b0bcd4;margin-top:4px">THEME</div>
        <div style="font-size:12px;font-weight:700;color:#ffffff;margin-top:2px">{theme}</div>
    </div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div style="background:#0e1117;border-radius:10px;padding:14px;text-align:center;border-top:3px solid {conv_c}">
        <div style="font-size:30px;font-weight:900;color:{conv_c}">{conviction}</div>
        <div style="font-size:11px;color:#b0bcd4;margin-top:2px">CONVICTION /100</div>
    </div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div style="background:#0e1117;border-radius:10px;padding:14px;text-align:center;border-top:3px solid {lp_c}">
        <div style="font-size:30px;font-weight:900;color:{lp_c}">{leader_power}</div>
        <div style="font-size:11px;color:#b0bcd4;margin-top:2px">LEADER POWER /100</div>
    </div>""", unsafe_allow_html=True)
    c4.markdown(f"""<div style="background:#0e1117;border-radius:10px;padding:14px;text-align:center;border-top:3px solid {opts_signal['bias_color']}">
        <div style="font-size:14px;font-weight:800;color:{opts_signal['bias_color']};margin-top:4px">{scenario['opt_rec']}</div>
        <div style="font-size:11px;color:#b0bcd4;margin-top:6px">OPTIONS LEAN</div>
        <div style="font-size:10px;color:#8a9bb5;margin-top:2px">P/C: {f"{opts_signal['pc_ratio']:.2f}" if opts_signal['pc_ratio'] else 'N/A'}</div>
    </div>""", unsafe_allow_html=True)

    # ── 3. LEADER ────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:#0e1117;border-radius:12px;padding:14px 18px;margin:8px 0;
                border-left:4px solid {lp_c}">
        <div style="font-size:10px;color:#8a9bb5;letter-spacing:1px;margin-bottom:6px">
            👑 WHO'S DRIVING THIS
        </div>
        <div style="font-size:16px;font-weight:700;color:#ffffff">{leader_name}
            <span style="font-size:12px;color:{lp_c};margin-left:8px">Power Score: {leader_power}/100</span>
        </div>
        <div style="font-size:13px;color:#c8d4e8;margin-top:6px;line-height:1.6">{leader_note}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 4. OPTIONS FLOW ───────────────────────────────────────
    unusual = ""
    if opts_signal.get("unusual_calls"):
        unusual += '<div style="font-size:12px;color:#4CAF50;margin-top:6px">⚡ Unusual far-OTM call buying — someone is betting on a big upside move.</div>'
    if opts_signal.get("unusual_puts"):
        unusual += '<div style="font-size:12px;color:#f44336;margin-top:6px">⚡ Deep OTM put buying detected — defensive hedging or bearish bet.</div>'

    st.markdown(f"""
    <div style="background:#0e1117;border-radius:12px;padding:14px 18px;margin:8px 0;
                border-left:4px solid {opts_signal['bias_color']}">
        <div style="font-size:10px;color:#8a9bb5;letter-spacing:1px;margin-bottom:6px">
            🎲 OPTIONS SMART MONEY
        </div>
        <div style="font-size:15px;font-weight:700;color:{opts_signal['bias_color']};margin-bottom:8px">
            {opts_signal['bias']}
        </div>
        <div style="display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:#c8d4e8;margin-bottom:4px">
            <span>📗 Calls OI: <b>{opts_signal['call_oi']:,}</b></span>
            <span>📕 Puts OI: <b>{opts_signal['put_oi']:,}</b></span>
            <span>IV: <b>{opts_signal['iv_signal']}</b></span>
        </div>
        {unusual}
        <div style="font-size:12px;color:#c8d4e8;margin-top:8px;line-height:1.6">
            {opts_signal['smart_money_note']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 5. 15-DAY SCENARIO ───────────────────────────────────
    st.markdown(f"""
    <div style="background:#0e1117;border-radius:12px;padding:14px 18px;margin:8px 0;
                border-left:4px solid {scenario['opt_color']}">
        <div style="font-size:10px;color:#8a9bb5;letter-spacing:1px;margin-bottom:8px">
            ⚠️ 15-DAY SCENARIO &nbsp;·&nbsp; NOT A PREDICTION — A SIGNAL-BASED VIEW
        </div>
        <div style="display:flex;gap:20px;flex-wrap:wrap;align-items:center">
            <div style="text-align:center">
                <div style="font-size:22px;font-weight:800;color:#ffffff">{scenario['bias']}</div>
                <div style="font-size:10px;color:#8a9bb5">Direction</div>
            </div>
            <div style="text-align:center">
                <div style="font-size:20px;font-weight:700;color:{scenario['opt_color']}">{scenario['lo_pct']:.1f}%–{scenario['hi_pct']:.1f}%</div>
                <div style="font-size:10px;color:#8a9bb5">Est. Move Range</div>
            </div>
            <div style="text-align:center">
                <div style="font-size:18px;font-weight:700;color:#e8ecf4">${scenario['lo_price']:.2f}–${scenario['hi_price']:.2f}</div>
                <div style="font-size:10px;color:#8a9bb5">Price Target Range</div>
            </div>
            <div style="text-align:center">
                <div style="font-size:16px;font-weight:700;color:#FFC107">{scenario['mom_15']:+.1f}%</div>
                <div style="font-size:10px;color:#8a9bb5">Last 15 Days</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 6. LOUIS' PLAIN ENGLISH REASONING ────────────────────
    st.markdown(f"""
    <div style="background:#0e1117;border-radius:12px;padding:14px 18px;margin:8px 0">
        <div style="font-size:10px;color:#8a9bb5;letter-spacing:1px;margin-bottom:8px">
            💬 LOUIS' TAKE
        </div>
        <div style="font-size:13px;color:#e8ecf4;line-height:1.8">{reason}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 7. INTUITION ENGINE BARS (compact) ───────────────────
    with st.expander("🧠 Louis Intuition Engine — 9 Dimensions", expanded=False):
        for dim, val in dims.items():
            bc = "#4CAF50" if val >= 65 else ("#FFC107" if val >= 45 else "#f44336")
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:7px">
                <div style="font-size:12px;color:#e2e8f0;min-width:200px">{dim}</div>
                <div style="flex:1;background:#1c2130;border-radius:4px;height:8px;overflow:hidden">
                    <div style="width:{val}%;height:100%;background:{bc};border-radius:4px"></div>
                </div>
                <div style="font-size:12px;font-weight:700;color:{bc};min-width:30px;text-align:right">{val}</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# CAPITAL MIGRATION INTELLIGENCE ENGINE — REASONING FIRST
# ─────────────────────────────────────────────────────────────

# ── THEME KNOWLEDGE BASE ─────────────────────────────────────
# Every theme must answer: why is capital flowing here, what
# drives demand, what can go wrong, and what triggers the move.

THEME_KNOWLEDGE = {
    "Artificial Intelligence": {
        "icon": "🧠", "tier": "$10T+", "horizon": "3-10y",
        "capital_flow": "accelerating",
        "keywords": ["artificial intelligence","machine learning","deep learning","neural","generative","language model","gpu","inference","compute"],
        "investment_thesis": "AI is the largest technology shift since the internet. Enterprise AI spending is compounding at 40%+ annually. Every major corporation is reallocating capex toward AI infrastructure, training, and deployment. The companies that supply compute, data, and software for this buildout are capturing a generational transfer of corporate spending.",
        "demand_drivers": ["Enterprise AI adoption accelerating across all industries", "Hyperscaler capex ($200B+ annually) flowing into AI infrastructure", "Government AI initiatives (CHIPS Act, EU AI Act) directing public capital", "Agentic AI creating new software categories and revenue streams"],
        "risks": ["AI revenue concentration in few hyperscalers creates customer risk", "Open-source models may commoditize proprietary AI software", "Regulatory backlash could slow enterprise adoption", "Power grid constraints may bottleneck data center expansion"],
        "catalysts": ["Quarterly hyperscaler capex guidance (signals demand trajectory)", "Enterprise AI revenue acceleration in earnings reports", "New model releases that unlock new use cases", "Government AI procurement contracts"],
        "invalidation": "If enterprise AI spending decelerates or hyperscaler capex guidance is cut, the entire supply chain reprices downward. Watch Microsoft, Google, and Amazon capex commentary.",
    },
    "Semiconductor Infrastructure": {
        "icon": "🔬", "tier": "$5T+", "horizon": "3-10y",
        "capital_flow": "accelerating",
        "keywords": ["semiconductor","chip","foundry","wafer","silicon","fab","lithography","memory","processor"],
        "investment_thesis": "Semiconductors are the foundation layer of every technology theme. AI, EVs, defense, IoT, and autonomous systems all require more silicon. Global governments are subsidizing domestic chip production as a national security priority. The industry is consolidating into fewer, more powerful players with deep competitive moats.",
        "demand_drivers": ["AI training and inference require exponentially more compute", "CHIPS Act subsidies funding $280B+ in new US fab capacity", "Automotive semiconductor content per vehicle rising 3x by 2030", "Edge AI and IoT creating new demand categories"],
        "risks": ["Cyclical inventory corrections can compress margins temporarily", "China export restrictions may reduce addressable market", "Foundry overcapacity if demand growth slows", "Customer concentration in hyperscaler accounts"],
        "catalysts": ["Monthly semiconductor sales data (SIA reports)", "Foundry utilization rates and pricing power signals", "New chip architecture announcements", "Geopolitical events affecting Taiwan/TSMC supply chain"],
        "invalidation": "A sustained semiconductor inventory correction or sharp decline in hyperscaler orders would compress the entire sector. Monitor TSMC monthly revenue and ASML order backlog.",
    },
    "Energy & Electrification": {
        "icon": "⚡", "tier": "$8T+", "horizon": "5-10y",
        "capital_flow": "accelerating",
        "keywords": ["nuclear","uranium","solar","grid","power","electricity","energy","utility","renewable","hydrogen","battery","electrification"],
        "investment_thesis": "The world needs 2-3x more electricity by 2035. AI data centers alone will consume more power than most countries. Nuclear is being rehabilitated as the only baseload carbon-free source that can scale. Grid infrastructure hasn't been upgraded in decades. Every electrification pathway — EVs, heat pumps, industrial automation — requires more power generation and transmission capacity.",
        "demand_drivers": ["AI data center power demand growing 30%+ annually", "Nuclear plant restarts and new SMR development programs", "Grid modernization spending accelerating globally", "EV charging infrastructure buildout requiring grid upgrades"],
        "risks": ["Nuclear permitting delays and public opposition", "Interest rates increasing cost of capital-intensive energy projects", "Natural gas price volatility affecting power economics", "Renewable intermittency requiring expensive storage solutions"],
        "catalysts": ["Nuclear plant restart announcements and NRC approvals", "Utility rate case decisions allowing capex recovery", "Hyperscaler power purchase agreements (PPAs)", "Government energy infrastructure spending bills"],
        "invalidation": "If AI data center growth slows materially, the incremental power demand thesis weakens. Also watch for nuclear project cancellations or major cost overruns that sour investor appetite.",
    },
    "Robotics & Automation": {
        "icon": "🦾", "tier": "$3T+", "horizon": "3-10y",
        "capital_flow": "early acceleration",
        "keywords": ["robot","automation","autonomous","humanoid","surgical","manufacturing","drone","cobots","rpa"],
        "investment_thesis": "Labour shortages are structural and worsening in developed economies. Reshoring manufacturing to the US and Europe requires automation — there simply aren't enough workers. Humanoid robots are transitioning from research to commercial deployment. Surgical robotics is expanding into new procedures. The physical world is being automated the way the digital world was automated by software.",
        "demand_drivers": ["Demographic decline creating permanent labour shortages", "Reshoring and friend-shoring requiring automated factories", "Surgical robotics expanding addressable procedures", "Warehouse automation driven by e-commerce growth"],
        "risks": ["Humanoid robotics timelines may be longer than expected", "High upfront capital cost limits SME adoption", "Safety certification slowing deployment in some sectors", "AI software for physical world less mature than digital AI"],
        "catalysts": ["Humanoid robot commercial deployment milestones", "Factory automation order backlog reports", "New surgical procedure FDA approvals for robotic systems", "Labor cost data confirming automation ROI"],
        "invalidation": "If humanoid robotics fails to reach commercial viability or if reshoring trends reverse, the growth premium in this theme contracts. Watch Tesla Optimus milestones and industrial automation order books.",
    },
    "Space Economy": {
        "icon": "🚀", "tier": "$1T+", "horizon": "5-10y",
        "capital_flow": "early stage",
        "keywords": ["space","satellite","launch","orbital","rocket","lunar","constellation","quantum"],
        "investment_thesis": "Space is transitioning from government-only to commercial infrastructure. Satellite broadband is becoming essential connectivity for underserved populations. Earth observation data is a growing intelligence market. Launch costs are falling exponentially. Defense spending on space assets is increasing as orbit becomes contested territory.",
        "demand_drivers": ["Satellite broadband addressing 3B+ unconnected population", "Defense spending on space-based surveillance and communications", "Launch cost reduction enabling new commercial applications", "Earth observation data becoming critical for agriculture, insurance, and defense"],
        "risks": ["Revenue generation timelines longer than most investors expect", "Capital intensity requiring repeated dilutive financing rounds", "Orbital debris risk increasing regulatory burden", "Technology risk in unproven systems like direct-to-device satellite"],
        "catalysts": ["Successful commercial launches and revenue milestones", "Government defense contracts for space capabilities", "Satellite constellation activation and subscriber growth", "Strategic partnerships with telecom carriers"],
        "invalidation": "If key space companies fail to convert technology into revenue, or if government space budgets are cut, the investment thesis weakens. Watch launch success rates and commercial revenue ramp.",
    },
    "Cybersecurity": {
        "icon": "🛡️", "tier": "$2T+", "horizon": "3-7y",
        "capital_flow": "steady",
        "keywords": ["cybersecurity","security","firewall","zero trust","threat","encryption","endpoint","siem"],
        "investment_thesis": "Cyber attacks are increasing in frequency, sophistication, and cost. Every company, government, and critical infrastructure operator must spend on cybersecurity — it's not discretionary. AI is both expanding the attack surface and enabling more sophisticated defense. The shift to cloud and remote work permanently expanded the security perimeter.",
        "demand_drivers": ["Ransomware and state-sponsored attacks increasing urgency", "AI-powered threats requiring AI-powered defense", "Regulatory compliance mandates (SEC, GDPR, DORA) forcing spend", "Cloud migration expanding the security perimeter"],
        "risks": ["Vendor consolidation may compress smaller players' margins", "Free/open-source security tools competing at the low end", "Customer budget fatigue from too many security vendors", "A major vendor breach could destroy category trust"],
        "catalysts": ["High-profile breaches driving emergency security spending", "New compliance regulations mandating specific capabilities", "Platform consolidation deals", "Government cybersecurity budget increases"],
        "invalidation": "Cybersecurity spending is relatively recession-resistant, but a severe economic downturn could delay enterprise renewal cycles. Watch net retention rates and billings growth.",
    },
    "Digital Asset Infrastructure": {
        "icon": "🪙", "tier": "$5T+", "horizon": "3-10y",
        "capital_flow": "cyclical acceleration",
        "keywords": ["crypto","bitcoin","blockchain","digital asset","tokeniz","defi","stablecoin","web3"],
        "investment_thesis": "Stablecoins are processing trillions in settlement volume. Bitcoin ETFs brought institutional capital into the asset class. Real-world asset tokenization is moving from concept to production. The infrastructure companies — exchanges, custodians, miners, and payment rails — capture value regardless of which token wins.",
        "demand_drivers": ["Institutional adoption via ETFs and custodial services", "Stablecoin settlement volume growing faster than traditional rails", "Real-world asset tokenization entering production", "Regulatory clarity enabling mainstream financial integration"],
        "risks": ["Regulatory crackdowns in major jurisdictions", "Bitcoin price volatility compressing miner and exchange revenue", "Security breaches eroding institutional trust", "Central bank digital currencies competing with private stablecoins"],
        "catalysts": ["Bitcoin halving cycle and ETF flow data", "New regulatory frameworks providing operational clarity", "Major financial institution tokenization announcements", "Stablecoin legislation progress"],
        "invalidation": "A sustained crypto bear market or major exchange failure would compress all infrastructure revenue. Watch Bitcoin ETF flows and stablecoin market cap as leading indicators.",
    },
    "Defense Technology": {
        "icon": "🎖️", "tier": "$3T+", "horizon": "5-10y",
        "capital_flow": "accelerating",
        "keywords": ["defense","military","missile","weapon","intelligence","pentagon","nato","classified"],
        "investment_thesis": "The world is re-arming. NATO allies are increasing defense budgets to 2-3% of GDP. The US defense budget is bipartisan and growing. Modern warfare requires AI, space, cyber, and autonomous systems — not just legacy platforms. Defense primes have multi-decade backlogs and cost-plus contract structures that protect margins.",
        "demand_drivers": ["NATO budget increases driven by geopolitical instability", "US defense budget bipartisan growth trajectory", "Modernization of aging military platforms globally", "AI and autonomous systems becoming core defense capabilities"],
        "risks": ["Political shifts could slow defense budget growth", "Program delays and cost overruns are endemic to defense", "Export control restrictions limiting international sales", "Workforce shortages in cleared defense engineering"],
        "catalysts": ["Annual defense budget authorization and appropriation", "Major contract awards (ICBM, NGAD, submarine programs)", "International arms deals and NATO procurement", "Geopolitical escalation driving emergency supplementals"],
        "invalidation": "A sustained period of geopolitical de-escalation or fiscal austerity targeting defense budgets would remove the growth premium. This is unlikely in the current environment but worth monitoring.",
    },
    "Longevity & Regeneration": {
        "icon": "🧬", "tier": "$2T+", "horizon": "5-10y",
        "capital_flow": "early acceleration",
        "keywords": ["genomic","biotech","drug discovery","precision medicine","crispr","longevity","regenerat","therapeutics"],
        "investment_thesis": "Biology is becoming an engineering discipline. AI is compressing drug discovery timelines from decades to years. Gene editing (CRISPR) is moving from labs to approved therapies. The obesity/GLP-1 revolution proved that breakthrough drugs can create $100B+ markets overnight. Aging populations in every developed economy guarantee growing healthcare demand.",
        "demand_drivers": ["AI accelerating drug discovery and clinical trial design", "GLP-1 and obesity drugs creating massive new market categories", "Gene therapy approvals expanding treatable conditions", "Aging demographics in developed economies increasing demand"],
        "risks": ["FDA approval timelines remain unpredictable", "Drug pricing pressure from governments and PBMs", "Clinical trial failures can destroy company value overnight", "Patent cliffs exposing revenue to generic competition"],
        "catalysts": ["FDA approval decisions for novel therapies", "Clinical trial data readouts (Phase 2/3)", "Major pharmaceutical M&A targeting biotech innovation", "Reimbursement and coverage decisions for new drug classes"],
        "invalidation": "Biotech is binary — a single clinical trial failure can eliminate 50%+ of a company's value. Diversify across the theme rather than concentrating in single-drug companies.",
    },
    "Data Center Infrastructure": {
        "icon": "🏗️", "tier": "$3T+", "horizon": "3-7y",
        "capital_flow": "accelerating",
        "keywords": ["data center","server","networking","cooling","rack","hyperscale","colocation"],
        "investment_thesis": "AI is driving the largest data center buildout in history. Hyperscalers are spending $200B+ annually on infrastructure. Every AI workload requires servers, networking, cooling, and power distribution. The companies supplying this physical infrastructure are in a multi-year demand supercycle with order backlogs extending 2-3 years out.",
        "demand_drivers": ["Hyperscaler capex running at record levels ($200B+ annually)", "AI workloads requiring 5-10x more power and cooling per rack", "Enterprise on-premise AI deployments creating new demand", "Edge computing requiring distributed data center buildout"],
        "risks": ["Hyperscaler capex could be cut if AI revenue disappoints", "Supply chain bottlenecks in power equipment and cooling", "Overbuilding risk if AI demand growth slows", "Component commoditization compressing hardware margins"],
        "catalysts": ["Quarterly hyperscaler capex and data center expansion announcements", "Server and networking order backlog reports", "New data center campus announcements", "Power and cooling technology breakthroughs"],
        "invalidation": "If hyperscaler capex guidance is cut or AI workload growth decelerates, data center infrastructure demand reprices. Watch quarterly capex commentary from MSFT, GOOGL, AMZN, META.",
    },
    "Water & Critical Resources": {
        "icon": "💧", "tier": "$1T+", "horizon": "5-10y",
        "capital_flow": "steady",
        "keywords": ["water","lithium","copper","rare earth","gold","mining","critical mineral","uranium"],
        "investment_thesis": "The energy transition and technology buildout need materials the world is running short of. Copper is essential for electrification — every EV, data center, and wind turbine requires it. Lithium demand for batteries is outpacing supply development. Rare earth elements are controlled by China, creating strategic vulnerability. Water infrastructure is aging and underfunded globally.",
        "demand_drivers": ["Electrification requiring massive copper and lithium volumes", "EV battery demand outpacing lithium supply development", "Rare earth supply chain diversification from China dependence", "Water infrastructure requiring trillions in deferred maintenance"],
        "risks": ["Commodity price volatility compressing mining margins", "New supply discoveries or substitution reducing scarcity premiums", "Environmental permitting delays slowing new mine development", "Demand destruction if EV adoption slows"],
        "catalysts": ["Supply deficit reports for copper, lithium, uranium", "Government critical mineral stockpiling and subsidy programs", "New mine approvals or production expansions", "Trade restrictions on critical mineral exports"],
        "invalidation": "If commodity prices collapse due to demand destruction or major new supply, the scarcity thesis weakens. Watch copper and lithium spot prices as leading indicators.",
    },
}

# ── VALUE CHAIN KNOWLEDGE ─────────────────────────────────────
VALUE_CHAIN = {
    "Artificial Intelligence": [
        ("L1 — Platform Owners",   {"MSFT","GOOGL","META","AMZN","AAPL"}, "Own the end-user relationship and AI distribution. Capture the most value but also fund the entire stack."),
        ("L2 — Compute / GPU",     {"NVDA","AMD","INTC"}, "Design the processors that train and run AI models. Bottleneck layer — supply is constrained and demand is insatiable."),
        ("L3 — Memory & Storage",  {"MU","WDC"}, "AI models require massive memory bandwidth. HBM demand is outstripping supply, creating pricing power."),
        ("L4 — Networking",        {"AVGO","MRVL","ANET"}, "Connect GPU clusters at scale. Custom silicon and high-speed switching are essential for AI training efficiency."),
        ("L5 — Foundry & Litho",   {"TSM","ASML","LRCX","AMAT"}, "Manufacture the chips. TSMC and ASML are irreplaceable bottlenecks in the global semiconductor supply chain."),
        ("L6 — AI Software",       {"PLTR","CRM","NOW","ADBE","SNOW","DDOG","AI","SOUN"}, "Deploy AI into enterprise workflows. Capture recurring software revenue from AI-powered products."),
        ("L7 — Power & Cooling",   {"ETN","GEV","VRT"}, "AI data centers need 5-10x more power and cooling per rack. Electrical and thermal management are the physical bottleneck."),
        ("L8 — Energy Supply",     {"CEG","VST","NEE","OKLO"}, "Provide the electrons. Nuclear and utility companies benefit from long-term power purchase agreements with hyperscalers."),
    ],
    "Semiconductor Infrastructure": [
        ("Design Leaders",     {"NVDA","AMD","AVGO","QCOM","ARM","MRVL"}, "Design the chip architectures. IP and design moats are the deepest in tech."),
        ("Foundry & Litho",    {"TSM","ASML","LRCX","AMAT"}, "Only TSMC can manufacture leading-edge chips. ASML is the sole supplier of EUV lithography."),
        ("Memory",             {"MU","INTC"}, "HBM and advanced memory are supply-constrained and essential for AI workloads."),
        ("Equipment",          {"LRCX","AMAT","ON"}, "Semiconductor manufacturing equipment has 1-2 year lead times. Demand visibility is high."),
    ],
    "Energy & Electrification": [
        ("Nuclear Generation", {"CEG","OKLO","SMR","NNE"}, "Only scalable carbon-free baseload power. Nuclear restarts and SMR development are government priorities."),
        ("Fuel Supply",        {"UEC","CCJ"}, "Uranium supply is constrained. Existing mines can't meet projected reactor demand."),
        ("Renewables",         {"FSLR","ENPH","NEE"}, "Solar and wind provide variable power. Cost-competitive but require storage and grid upgrades."),
        ("Grid & Power Mgmt",  {"ETN","GEV","VST"}, "Electrical distribution and grid management. Every watt of new generation needs transmission infrastructure."),
        ("Oil & Gas",          {"XOM","CVX","COP","SHEL"}, "Bridge fuel generating massive cash flow. Funding dividends and energy transition investments."),
    ],
    "Space Economy": [
        ("Launch",             {"SPCX","RKLB","BA"}, "Getting payloads to orbit. SpaceX owns 60%+ market share. Launch costs falling but demand is rising faster."),
        ("Satellite Operators",{"SPCX","ASTS","PL","SPIR"}, "Building and operating satellite constellations for broadband, imaging, and IoT. Starlink is the dominant constellation."),
        ("Lunar & Exploration",{"LUNR","RKLB","SPCX"}, "NASA and commercial lunar programs creating new revenue opportunities. Starship is the key enabler."),
        ("Quantum Computing",  {"IONQ","QBTS","RGTI"}, "Pre-revenue but potentially transformative. National security implications drive government funding."),
        ("Defense Space",      {"LMT","NOC","LHX"}, "Military space assets and anti-satellite capabilities. Growing defense budget allocation."),
    ],
    "Defense Technology": [
        ("Prime Contractors",  {"LMT","RTX","NOC","GD","BA"}, "Multi-decade backlogs with cost-plus margins. The backbone of US and allied defense capability."),
        ("Specialty / Niche",  {"BWXT","KTOS","LHX","BAESY"}, "Nuclear propulsion, drone defense, and electronic warfare. Niche capabilities with few competitors."),
        ("Defense Software",   {"PLTR"}, "AI-powered intelligence and battlefield decision systems. Software margins with defense contract stickiness."),
    ],
    "Digital Asset Infrastructure": [
        ("Exchanges & Custody",{"COIN","HOOD"}, "On-ramps for institutional and retail capital. Revenue scales with trading volume and assets under custody."),
        ("Corporate Bitcoin",  {"MSTR"}, "Bitcoin treasury strategy. A leveraged proxy for BTC with equity market access."),
        ("Mining",             {"MARA","RIOT","CLSK","BTDR"}, "Secure the Bitcoin network. Revenue tied to BTC price and network fees."),
        ("Payments & Rails",   {"XYZ"}, "Building payment infrastructure for digital assets and traditional finance convergence."),
    ],
}

# ── STOCK-LEVEL KNOWLEDGE BASE ────────────────────────────────
# For known stocks: pre-written thesis, risk, and catalyst.
# For unknown stocks: generated from financial data + theme.
STOCK_THESIS = {
    "NVDA": {
        "layer": "L2 — Compute / GPU",
        "bottleneck": True,
        "bottleneck_reason": "Only provider of AI training GPUs at scale. CUDA ecosystem creates 10+ year switching cost. No viable alternative for frontier model training.",
        "investment_thesis": "NVIDIA owns the computational bottleneck of the AI era. Every dollar of AI capex flows through their silicon. Data center revenue is growing 100%+ YoY with no deceleration. The CUDA software moat makes switching costs astronomical.",
        "risk_thesis": "Customer concentration in hyperscalers. AMD and custom silicon (Google TPU, Amazon Trainium) are credible long-term alternatives. Valuation assumes sustained hypergrowth with no cyclical correction.",
        "catalyst": "Quarterly earnings showing data center revenue acceleration. New chip architecture launches (Blackwell ramp). Hyperscaler capex guidance increases.",
        "invalidation": "If hyperscalers meaningfully shift to custom silicon and NVIDIA's data center growth decelerates to <30%, the growth premium collapses.",
    },
    "AVGO": {
        "layer": "L4 — Networking",
        "bottleneck": True,
        "bottleneck_reason": "Designs custom AI accelerators for Google (TPU), Meta, and Apple. Also dominates networking silicon for AI clusters. Dual bottleneck position.",
        "investment_thesis": "Broadcom is the quiet backbone of AI infrastructure — designing custom silicon for the largest AI companies while dominating the networking chips that connect GPU clusters. The VMware acquisition adds enterprise software recurring revenue. Hock Tan's M&A playbook has compounded value for 15 years.",
        "risk_thesis": "VMware integration execution risk. Custom silicon contracts are lumpy and customer-dependent. Networking competition from Marvell and merchant silicon alternatives.",
        "catalyst": "AI revenue guidance increases. VMware cross-selling traction. New custom silicon design wins from hyperscalers.",
        "invalidation": "If major custom silicon customers (Google, Meta) bring chip design in-house or if VMware integration stalls, growth trajectory weakens.",
    },
    "MSFT": {
        "layer": "L1 — Platform Owners",
        "bottleneck": False,
        "bottleneck_reason": "Platform owner, not a bottleneck. Competes with Google and Amazon for AI cloud. Dominant through distribution and enterprise relationships, not supply scarcity.",
        "investment_thesis": "Microsoft is the enterprise gateway to AI through Azure + OpenAI partnership. Copilot is monetizing AI across 400M+ Office users. Azure is the enterprise cloud leader with AI workload share gains. Enterprise relationships are the deepest distribution moat in technology.",
        "risk_thesis": "OpenAI partnership terms may become less favorable. Google Gemini and open-source models creating credible alternatives. Azure margins could compress under AI infrastructure investment.",
        "catalyst": "Azure AI revenue growth rate acceleration. Copilot enterprise adoption metrics. New OpenAI model capabilities integrated into Microsoft products.",
        "invalidation": "If Azure loses AI workload share to Google or AWS, or if OpenAI's competitive position weakens, the AI premium in Microsoft's valuation compresses.",
    },
    "TSM": {
        "layer": "L5 — Foundry & Litho",
        "bottleneck": True,
        "bottleneck_reason": "Only foundry capable of manufacturing leading-edge chips (3nm, 2nm). 90%+ market share in advanced nodes. No alternative exists or will exist for 5+ years.",
        "investment_thesis": "TSMC is the most critical single company in the global technology supply chain. Every advanced chip in the world — from NVIDIA GPUs to Apple processors — is manufactured by TSMC. The moat is physics: building a competing foundry takes 5-10 years and $100B+. AI demand is filling capacity for years ahead.",
        "risk_thesis": "Geopolitical risk from Taiwan-China tensions is the single biggest overhang. US fab construction is expensive and behind schedule. Cyclical semiconductor inventory corrections affect utilization.",
        "catalyst": "Monthly revenue reports showing AI chip demand. US fab construction milestones. Geopolitical de-escalation in Taiwan strait. Leading-edge node pricing power.",
        "invalidation": "A military conflict involving Taiwan would be catastrophic. Short of that, a sustained semiconductor downcycle or successful Intel foundry comeback (unlikely in near term) would challenge the thesis.",
    },
    "ETN": {
        "layer": "L7 — Power & Cooling",
        "bottleneck": True,
        "bottleneck_reason": "Critical electrical infrastructure provider for data centers, grid modernization, and industrial electrification. Long lead times and limited competition in high-voltage power distribution.",
        "investment_thesis": "Eaton sits at the intersection of every electrification megatrend — AI data centers, grid modernization, EV infrastructure, and industrial automation all require power management and distribution equipment. Order backlogs are at record highs with multi-year visibility. The company has pricing power in a supply-constrained market.",
        "risk_thesis": "Industrial cyclicality could slow non-data-center orders. Valuation has expanded significantly on the electrification narrative. Interest rate sensitivity on capital-intensive project decisions.",
        "catalyst": "Data center order backlog growth. Grid modernization spending bills. Utility capital expenditure increases. Quarterly earnings showing margin expansion.",
        "invalidation": "If data center buildout slows or industrial capex enters a downcycle, Eaton's growth rate normalizes. Watch hyperscaler capex and utility capex plans.",
    },
    "GEV": {
        "layer": "L7 — Power & Cooling",
        "bottleneck": True,
        "bottleneck_reason": "Largest manufacturer of gas and wind turbines globally. Critical supplier for grid-scale power generation and transmission equipment with multi-year backlogs.",
        "investment_thesis": "GE Vernova is the pure-play electrification company spun out of GE. It manufactures the turbines, grid equipment, and power systems the world needs for the energy transition. Order backlogs extend years out. The company benefits from both AI data center power demand and broader grid modernization. Post-spinoff operational improvements are expanding margins.",
        "risk_thesis": "Wind turbine segment has historically been margin-negative. Execution risk on operational turnaround. Competition from Siemens Energy in gas turbines and grid equipment.",
        "catalyst": "Wind segment reaching profitability. Gas turbine order acceleration from AI data center demand. Grid equipment backlog growth. Margin expansion milestones post-spinoff.",
        "invalidation": "If the wind segment continues to lose money or if gas turbine orders decelerate, the stock loses its growth premium. Watch quarterly segment margins closely.",
    },
    "CEG": {
        "layer": "L8 — Energy Supply",
        "bottleneck": True,
        "bottleneck_reason": "Largest nuclear fleet operator in the US. Nuclear plants take 10-20 years to build. Existing fleet is irreplaceable supply of carbon-free baseload power.",
        "investment_thesis": "Constellation Energy operates the largest nuclear fleet in America at a time when AI data centers are desperate for carbon-free baseload power. Nuclear is the only generation source that can provide 24/7 reliable power at scale. Hyperscaler PPAs are locking in premium pricing for decades. The Three Mile Island restart signals how scarce and valuable nuclear capacity has become.",
        "risk_thesis": "Nuclear regulatory risk and public perception challenges. Power price volatility if gas prices decline. Execution risk on Three Mile Island restart.",
        "catalyst": "Three Mile Island restart milestones. New hyperscaler PPA announcements. Nuclear-friendly policy developments. Power price firming.",
        "invalidation": "If natural gas prices collapse and make nuclear uneconomic relative to gas generation, or if AI data center power demand disappoints, the premium valuation compresses.",
    },
    "PLTR": {
        "layer": "L6 — AI Software",
        "bottleneck": False,
        "bottleneck_reason": "Not a supply bottleneck but has deep operational embedding in government intelligence systems. Switching costs are extremely high once deployed.",
        "investment_thesis": "Palantir is the only company with production AI/ML platforms deployed across US intelligence, military, and now commercial enterprise. The AIP (Artificial Intelligence Platform) is accelerating commercial revenue growth. Government contracts provide recession-resistant baseload revenue while commercial is the growth engine. Deep operational embedding creates switching costs that approach infrastructure-level stickiness.",
        "risk_thesis": "Valuation is extremely elevated relative to revenue. Government contract renewal risk. Commercial competition from hyperscaler AI platforms. Key-man risk with Alex Karp's unconventional leadership style.",
        "catalyst": "Commercial revenue acceleration. New government contract wins (especially international). AIP bootcamp conversions to production contracts. FedRAMP and defense certifications for new products.",
        "invalidation": "If commercial revenue growth decelerates or government contracts are not renewed, the growth narrative breaks. The stock trades at a premium that assumes sustained 30%+ growth.",
    },
    "ASTS": {
        "layer": "Satellite Operators",
        "bottleneck": False,
        "bottleneck_reason": "Not a bottleneck — speculative technology play. If direct-to-device satellite works, AST has first-mover advantage. If it doesn't, the company has no fallback revenue.",
        "investment_thesis": "AST SpaceMobile is building the first and only space-based cellular broadband network that works with existing smartphones. If successful, it connects 5B+ mobile subscribers who lack reliable coverage. Carrier partnerships with AT&T, Verizon, and Vodafone provide distribution. The technology is unproven at commercial scale but the addressable market is enormous.",
        "risk_thesis": "Pre-revenue company with massive capital requirements. Technology risk — commercial-scale direct-to-device satellite is unproven. Dilution risk from ongoing capital raises. Competition from SpaceX Starlink direct-to-cell.",
        "catalyst": "BlueBird satellite constellation deployment milestones. Commercial service launch with carrier partners. Successful technology demonstrations at scale. Strategic investment or partnership announcements.",
        "invalidation": "If BlueBird satellites fail to perform at commercial scale, or if SpaceX direct-to-cell captures the market first, the thesis is broken. This is a binary technology bet.",
    },
    "LUNR": {
        "layer": "Lunar & Exploration",
        "bottleneck": False,
        "bottleneck_reason": "One of few commercial lunar landers but not irreplaceable. NASA has multiple lunar delivery providers. Contract-dependent with limited commercial revenue visibility.",
        "investment_thesis": "Intuitive Machines is one of NASA's primary commercial lunar delivery partners. The Artemis program and broader lunar economy are in early stages. Successful lunar landings build reputation and contract pipeline. Data services from lunar surface operations add recurring revenue potential.",
        "risk_thesis": "High mission failure risk — lunar landing is extremely difficult. Revenue is lumpy and contract-dependent. Limited commercial revenue beyond government contracts. Cash burn rate requires ongoing funding.",
        "catalyst": "Successful lunar landing missions. New NASA task order awards. Commercial payload contracts. Lunar data services revenue growth.",
        "invalidation": "A failed lunar mission or NASA budget cuts to Artemis would seriously damage the thesis. The company needs consistent mission success to build credibility.",
    },
    "AMD": {
        "layer": "L2 — Compute / GPU",
        "bottleneck": False,
        "bottleneck_reason": "Credible GPU alternative to NVIDIA but not yet a bottleneck. MI300 gaining traction but CUDA ecosystem gives NVIDIA the switching cost moat.",
        "investment_thesis": "AMD is the only credible GPU competitor to NVIDIA in AI training and inference. The MI300 series is gaining hyperscaler adoption. CPU market share gains from Intel continue. Lisa Su's execution track record is exceptional. As hyperscalers diversify GPU supply, AMD captures the second-source demand.",
        "risk_thesis": "CUDA ecosystem lock-in limits AMD's ability to take GPU share from NVIDIA. AI GPU margins may compress as competition intensifies. CPU growth may slow as server refresh cycles normalize.",
        "catalyst": "MI300 revenue ramp and new design wins. Data center GPU market share gains. New chip architecture announcements. Hyperscaler diversification away from NVIDIA sole-source.",
        "invalidation": "If AMD's AI GPU revenue growth stalls or hyperscalers don't diversify away from NVIDIA, the AI premium in AMD's valuation fades.",
    },
    "COIN": {
        "layer": "Exchanges & Custody",
        "bottleneck": False,
        "bottleneck_reason": "Largest US crypto exchange but not irreplaceable. Competition from traditional finance entering crypto custody. Revenue heavily tied to trading volume and crypto prices.",
        "investment_thesis": "Coinbase is the regulated gateway for institutional crypto adoption in the US. Custody services, staking revenue, and Base (L2 blockchain) provide diversification beyond trading fees. Regulatory clarity is Coinbase's moat — they invested in compliance when others didn't. Bitcoin ETF custody relationships are sticky multi-year revenue.",
        "risk_thesis": "Revenue remains correlated to crypto prices and trading volume. Regulatory risk from SEC and state regulators. Competition from traditional finance firms entering crypto. Fee compression as market matures.",
        "catalyst": "Bitcoin price appreciation driving trading volume. New regulatory frameworks favoring compliant exchanges. Institutional custody mandate wins. Base ecosystem growth metrics.",
        "invalidation": "A sustained crypto bear market compresses trading revenue. If traditional finance captures institutional crypto custody, Coinbase's competitive position weakens.",
    },
    "RKLB": {
        "layer": "Launch",
        "bottleneck": False,
        "bottleneck_reason": "Second most frequently launching orbital rocket company after SpaceX. Not a bottleneck but has launch cadence that most competitors lack.",
        "investment_thesis": "Rocket Lab is the second most prolific orbital launch company globally. The Neutron medium-lift rocket targets the largest segment of the launch market. Space Systems division (satellites, components) provides higher-margin recurring revenue. Peter Beck's execution has been exceptional — Electron has the most reliable small-launch track record after SpaceX.",
        "risk_thesis": "Neutron development requires significant capital and carries technical risk. SpaceX dominance in launch creates pricing pressure. Government launch contracts are competitive. Cash burn until Neutron achieves commercial scale.",
        "catalyst": "Neutron development milestones and first launch. Increasing Electron launch cadence. New government and commercial launch contracts. Space Systems revenue growth and backlog expansion.",
        "invalidation": "If Neutron is significantly delayed or fails, the medium-lift thesis collapses. Continued SpaceX pricing pressure could make launch economics unsustainable for smaller providers.",
    },
    "MU": {
        "layer": "L3 — Memory & Storage",
        "bottleneck": True,
        "bottleneck_reason": "One of only three companies (with Samsung and SK Hynix) that can manufacture HBM for AI GPUs. HBM supply is sold out for 2+ years ahead.",
        "investment_thesis": "Micron is one of three companies in the world that can manufacture High Bandwidth Memory (HBM) — the memory type essential for AI GPUs. HBM is supply-constrained and sold out years in advance. AI is shifting Micron's revenue mix toward higher-margin products with better pricing power. The memory oligopoly (3 players) gives structural pricing stability that didn't exist in previous cycles.",
        "risk_thesis": "Memory is historically cyclical — oversupply can crash pricing. HBM premium could compress if all three manufacturers scale simultaneously. Consumer DRAM and NAND segments remain commoditized.",
        "catalyst": "HBM revenue ramp and pricing power. Memory cycle upturn in traditional segments. New AI memory architectures. Data center memory demand forecasts.",
        "invalidation": "If memory enters an oversupply cycle or HBM pricing collapses, margins revert to historical lows. Watch industry supply/demand forecasts from analysts.",
    },
    "CRWD": {
        "layer": "Cybersecurity Leader",
        "bottleneck": False,
        "bottleneck_reason": "Market leader but not irreplaceable. Competes with Palo Alto, SentinelOne, and Microsoft in endpoint security. Strong brand but switching is possible.",
        "investment_thesis": "CrowdStrike is the platform consolidation winner in cybersecurity. The Falcon platform is expanding from endpoint to cloud, identity, and data security — becoming the single-pane-of-glass for enterprise security operations. Net retention rates above 120% show customers are spending more, not switching. AI-native threat detection is a genuine technical moat.",
        "risk_thesis": "The July 2024 outage damaged trust and may slow new customer acquisition. Palo Alto's platformization strategy is competing directly. Valuation assumes sustained 30%+ growth. Customer concentration in large enterprises.",
        "catalyst": "Post-outage customer retention data proving stickiness. New module adoption driving net retention. Large enterprise competitive wins vs Palo Alto. International expansion milestones.",
        "invalidation": "If post-outage customer churn accelerates or net retention drops below 115%, the platform consolidation thesis weakens. Watch closely for competitive losses to Palo Alto.",
    },
    "SPCX": {
        "layer": "L1 — Platform Owners (Space)",
        "bottleneck": True,
        "bottleneck_reason": "Only company with reusable orbital-class rockets at scale. Starship is the sole super-heavy launch vehicle operational. Starlink dominates LEO broadband with 6,000+ satellites — no competitor is within 5 years of matching this constellation.",
        "investment_thesis": "SpaceX owns the launch bottleneck of the space economy. Every satellite, every space station resupply, every deep space mission depends on affordable launch — and SpaceX has 60%+ global market share with costs 10x lower than legacy providers. Starlink is building a $30B+ annual revenue broadband monopoly in orbit. Starship unlocks Mars colonization, lunar infrastructure, and point-to-point Earth transport. This is the most important infrastructure company of the 21st century.",
        "risk_thesis": "Elon Musk key-man risk and attention split across Tesla, xAI, and government roles. Regulatory risk from FCC, FAA, and international spectrum allocation. Starship development delays could slow Starlink V2 deployment. Blue Origin's New Glenn is a credible future competitor in heavy launch.",
        "catalyst": "Starship operational cadence acceleration. Starlink direct-to-cell launch. Government defense contracts (Starshield). Revenue growth from Starlink subscriber base crossing 10M+. Potential Starlink spinoff or further capital raises at higher valuations.",
        "invalidation": "If Starship fails to achieve rapid reusability or if a major launch failure grounds the fleet, the cost advantage thesis collapses. If Starlink subscriber growth stalls or ARPU declines significantly, the broadband monopoly thesis weakens.",
    },
}


def detect_capital_themes(info, ticker):
    summary = (info.get("longBusinessSummary", "") or "").lower()
    sector = (info.get("sector", "") or "").lower()
    industry = (info.get("industry", "") or "").lower()
    combined = f"{sector} {industry} {summary}"
    tk = ticker.upper()
    matched = []
    for theme, data in THEME_KNOWLEDGE.items():
        score = 0
        known_tickers = set()
        if theme in VALUE_CHAIN:
            for _, tickers, _ in VALUE_CHAIN[theme]:
                known_tickers |= tickers
        if tk in known_tickers:
            score += 50
        kw_hits = sum(1 for kw in data["keywords"] if kw in combined)
        score += min(kw_hits * 8, 40)
        if score >= 15:
            matched.append((theme, score))
    matched.sort(key=lambda x: x[1], reverse=True)
    if not matched:
        matched = [("Uncategorized", 10)]
    return matched


def find_value_chain_position(ticker, theme_name):
    tk = ticker.upper()
    if theme_name not in VALUE_CHAIN:
        return []
    positions = []
    for layer_name, layer_tickers, layer_role in VALUE_CHAIN[theme_name]:
        if tk in layer_tickers:
            positions.append({"layer": layer_name, "role": layer_role})
    return positions


def determine_bottleneck(info, ticker):
    tk = ticker.upper()
    if tk in STOCK_THESIS:
        st_data = STOCK_THESIS[tk]
        return st_data["bottleneck"], st_data["bottleneck_reason"]
    gm = safe(info, "grossMargins", default=0) or 0
    mc = safe(info, "marketCap", default=0) or 0
    summary = (info.get("longBusinessSummary", "") or "").lower()
    scarcity_kw = ["sole supplier","only provider","monopoly","proprietary","patent","exclusive","leading provider","dominant","market leader","largest"]
    hits = sum(1 for kw in scarcity_kw if kw in summary)
    is_bottleneck = (gm > 0.55 and mc > 5e10) or hits >= 3
    if is_bottleneck:
        reason = f"High gross margins ({gm*100:.0f}%) and market position suggest pricing power and limited substitutes. "
        if hits >= 2:
            reason += "Business description indicates a dominant or exclusive position in its market."
        else:
            reason += "Scale and profitability suggest competitive advantages, but not necessarily an irreplaceable position."
    else:
        reason = f"Gross margins ({gm*100:.0f}%) and competitive landscape suggest this company can be substituted or competed against. Not a structural bottleneck in its value chain."
    return is_bottleneck, reason


def assess_capital_flow(info, hist):
    inst = safe(info, "heldPercentInstitutions", default=0.4) or 0.4
    avg_vol = safe(info, "averageVolume", default=1) or 1
    avg10 = safe(info, "averageVolume10days", default=1) or 1
    vol_ratio = avg10 / avg_vol if avg_vol else 1
    sf = safe(info, "shortPercentOfFloat", default=0.05) or 0.05
    signals = []
    if inst > 0.80:
        signals.append("Institutional ownership above 80% — heavy professional accumulation.")
    elif inst > 0.60:
        signals.append("Strong institutional presence — majority held by professional money managers.")
    elif inst < 0.35:
        signals.append("Low institutional ownership — professionals have limited exposure.")
    if vol_ratio > 1.3:
        signals.append(f"Recent volume {vol_ratio:.1f}x above average — accumulation or repositioning in progress.")
    elif vol_ratio < 0.7:
        signals.append(f"Recent volume {vol_ratio:.1f}x below average — quiet period, possible distribution.")
    if sf > 0.15:
        signals.append(f"Short interest elevated at {sf*100:.1f}% — bears are positioned against this name.")
    elif sf < 0.03:
        signals.append(f"Short interest minimal at {sf*100:.1f}% — no significant bearish positioning.")
    if not hist.empty and len(hist) > 50:
        close = hist["Close"]
        hi52 = close.max()
        pos = close.iloc[-1] / hi52 if hi52 > 0 else 0.5
        if pos > 0.90:
            signals.append(f"Trading near 52-week high ({pos*100:.0f}% of high) — price confirms capital inflow.")
        elif pos < 0.50:
            signals.append(f"Trading at {pos*100:.0f}% of 52-week high — capital has been leaving.")
    direction = "Inflow" if (inst > 0.60 and vol_ratio > 1.0 and sf < 0.10) else ("Outflow" if (inst < 0.40 or sf > 0.15) else "Neutral")
    return direction, signals


def generate_thesis(info, hist, ticker, themes, positions, is_bottleneck, bottleneck_reason, capital_direction, capital_signals):
    tk = ticker.upper()
    name = info.get("shortName") or info.get("longName", tk)
    primary_theme = themes[0][0] if themes else "Uncategorized"
    theme_data = THEME_KNOWLEDGE.get(primary_theme, {})
    if tk in STOCK_THESIS:
        known = STOCK_THESIS[tk]
        inv_thesis = known["investment_thesis"]
        risk_thesis = known["risk_thesis"]
        catalyst_thesis = known["catalyst"]
        invalidation = known["invalidation"]
    else:
        rg = safe(info, "revenueGrowth", default=0) or 0
        gm = safe(info, "grossMargins", default=0) or 0
        mc = safe(info, "marketCap", default=0) or 0
        sector = info.get("sector", "")
        layer_desc = positions[0]["role"] if positions else f"participant in the {primary_theme} theme"
        growth_desc = f"Revenue is growing at {rg*100:.0f}%" if rg > 0 else "Revenue growth is negative"
        margin_desc = f"gross margins of {gm*100:.0f}%" if gm > 0 else "thin margins"
        scale = "mega-cap" if mc > 2e11 else ("large-cap" if mc > 1e10 else ("mid-cap" if mc > 2e9 else "small-cap"))
        inv_thesis = (
            f"{name} is a {scale} {sector} company positioned as a {layer_desc}. "
            f"{growth_desc} with {margin_desc}. "
            f"The company's exposure to {primary_theme} provides a structural demand tailwind as "
            f"{theme_data.get('investment_thesis', 'this theme grows.').split('.')[0].lower()}."
        )
        risk_thesis = (
            f"{'As a commodity player, ' if not is_bottleneck else ''}"
            f"{'competition could compress margins and market share. ' if not is_bottleneck else 'Even bottleneck positions can erode if technology shifts or new supply emerges. '}"
            f"Theme-level risks include: {theme_data['risks'][0].lower() if theme_data.get('risks') else 'cyclical demand variability'}. "
            f"Valuation may not reflect these risks if the market is pricing in sustained growth."
        )
        catalyst_thesis = theme_data["catalysts"][0] if theme_data.get("catalysts") else "Earnings reports and sector momentum will determine near-term direction."
        invalidation = theme_data.get("invalidation", "If the theme decelerates or competition intensifies, the investment thesis weakens.")
    demand_event = theme_data.get("demand_drivers", ["Structural demand growth"])[0] if theme_data else "Structural demand growth"
    return {
        "investment_thesis": inv_thesis,
        "risk_thesis": risk_thesis,
        "catalyst": catalyst_thesis,
        "invalidation": invalidation,
        "demand_event": demand_event,
        "theme_thesis": theme_data.get("investment_thesis", ""),
        "theme_risks": theme_data.get("risks", []),
        "theme_catalysts": theme_data.get("catalysts", []),
        "theme_capital_flow": theme_data.get("capital_flow", "unknown"),
    }


def compute_capital_migration(info, hist, ticker):
    themes = detect_capital_themes(info, ticker)
    primary_theme = themes[0][0] if themes else "Uncategorized"
    positions = find_value_chain_position(ticker, primary_theme)
    all_positions = []
    for tname, _ in themes:
        all_positions.extend(find_value_chain_position(ticker, tname))
    is_bottleneck, bottleneck_reason = determine_bottleneck(info, ticker)
    capital_direction, capital_signals = assess_capital_flow(info, hist)
    thesis = generate_thesis(info, hist, ticker, themes, positions,
                             is_bottleneck, bottleneck_reason,
                             capital_direction, capital_signals)
    theme_data = THEME_KNOWLEDGE.get(primary_theme, {})
    rg = safe(info, "revenueGrowth", default=0) or 0
    rec = safe(info, "recommendationMean", default=3)
    theme_strength = clamp(40 + clamp(rg * 120, -15, 30) + clamp((3 - rec) * 8, -12, 16) + clamp(theme_data.get("growth_pct", 15) * 0.3, 0, 12))
    inst = safe(info, "heldPercentInstitutions", default=0.4) or 0.4
    avg_vol = safe(info, "averageVolume", default=1) or 1
    avg10 = safe(info, "averageVolume10days", default=1) or 1
    vol_ratio = avg10 / avg_vol if avg_vol else 1
    cap_score = clamp(40 + clamp((inst - 0.5) * 50, -15, 25) + (15 if vol_ratio > 1.3 else (8 if vol_ratio > 1.1 else (-10 if vol_ratio < 0.7 else 0))))
    gm = safe(info, "grossMargins", default=0) or 0
    mc = safe(info, "marketCap", default=0) or 0
    bn_score = clamp(35 + clamp((gm - 0.30) * 80, -15, 30) + (15 if mc > 5e11 else (10 if mc > 1e11 else (5 if mc > 2e10 else 0))) + (15 if is_bottleneck else 0))
    overall = clamp(theme_strength * 0.20 + cap_score * 0.25 + bn_score * 0.25 + clamp(40 + clamp(rg * 100, -15, 30) + clamp((3 - rec) * 8, -10, 15)) * 0.30)
    return {
        "themes": themes,
        "primary_theme": primary_theme,
        "positions": all_positions if all_positions else positions,
        "is_bottleneck": is_bottleneck,
        "bottleneck_reason": bottleneck_reason,
        "capital_direction": capital_direction,
        "capital_signals": capital_signals,
        "thesis": thesis,
        "theme_data": theme_data,
        "scores": {"theme_strength": theme_strength, "capital_flow": cap_score, "bottleneck": bn_score, "overall": overall},
    }


def render_capital_migration(cm, ticker):
    st.subheader("🌊 Capital Migration Intelligence")
    primary = cm["primary_theme"]
    td = cm["theme_data"]
    icon = td.get("icon", "📊")
    thesis = cm["thesis"]
    st.markdown(f"""
    <div style="background:#0a1628;border-left:4px solid #7c3aed;border-radius:0 12px 12px 0;padding:18px 20px;margin-bottom:16px">
        <div style="font-size:11px;color:#8a9bb5;letter-spacing:2px;margin-bottom:6px">FUTURE ECONOMY THEME</div>
        <div style="font-size:22px;font-weight:800;color:#ffffff">{icon} {primary}</div>
        <div style="display:flex;gap:16px;margin-top:8px;flex-wrap:wrap">
            <span style="font-size:12px;color:#b0bcd4">Addressable: <b style="color:#FFC107">{td.get('tier','N/A')}</b></span>
            <span style="font-size:12px;color:#b0bcd4">Horizon: <b style="color:#FFC107">{td.get('horizon','N/A')}</b></span>
            <span style="font-size:12px;color:#b0bcd4">Capital Flow: <b style="color:{'#4CAF50' if td.get('capital_flow')=='accelerating' else '#FFC107'}">{td.get('capital_flow','unknown').upper()}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if thesis.get("theme_thesis"):
        st.markdown(f"""
        <div style="background:#161b27;border-radius:10px;padding:16px 18px;margin-bottom:12px">
            <div style="font-size:11px;color:#8a9bb5;letter-spacing:1px;margin-bottom:8px">WHY CAPITAL IS FLOWING HERE</div>
            <div style="font-size:13px;color:#e8ecf4;line-height:1.8">{thesis['theme_thesis']}</div>
        </div>
        """, unsafe_allow_html=True)
    if cm["positions"]:
        layer_html = ""
        for pos in cm["positions"]:
            layer_html += (
                f'<div style="background:#1a2a1a;border-left:3px solid #4CAF50;border-radius:0 8px 8px 0;padding:10px 14px;margin:6px 0">'
                f'<div style="font-size:13px;font-weight:700;color:#66d166">{pos["layer"]}</div>'
                f'<div style="font-size:12px;color:#c8d4e8;margin-top:4px">{pos["role"]}</div>'
                f'</div>'
            )
        st.markdown(f"""
        <div style="margin-bottom:12px">
            <div style="font-size:11px;color:#8a9bb5;letter-spacing:1px;margin-bottom:6px">VALUE CHAIN POSITION</div>
            {layer_html}
        </div>
        """, unsafe_allow_html=True)
    bn = cm["is_bottleneck"]
    bn_color = "#4CAF50" if bn else "#FF9800"
    bn_label = "BOTTLENECK" if bn else "COMMODITY / COMPETITIVE"
    st.markdown(f"""
    <div style="background:#161b27;border-radius:10px;padding:14px 18px;margin-bottom:12px;border-left:4px solid {bn_color}">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
            <span style="font-size:11px;color:#8a9bb5;letter-spacing:1px">SUPPLY POSITION</span>
            <span style="background:{'#1a3a1a' if bn else '#3a2a1a'};border:1px solid {bn_color};border-radius:20px;padding:2px 12px;font-size:11px;font-weight:700;color:{bn_color}">{bn_label}</span>
        </div>
        <div style="font-size:13px;color:#e8ecf4;line-height:1.7">{cm['bottleneck_reason']}</div>
    </div>
    """, unsafe_allow_html=True)
    cap_dir = cm["capital_direction"]
    cap_color = "#4CAF50" if cap_dir == "Inflow" else ("#f44336" if cap_dir == "Outflow" else "#FFC107")
    signals_html = "".join(f'<div style="font-size:12px;color:#c8d4e8;margin:4px 0;padding-left:12px;border-left:2px solid #3a4460">• {s}</div>' for s in cm["capital_signals"])
    st.markdown(f"""
    <div style="background:#161b27;border-radius:10px;padding:14px 18px;margin-bottom:12px;border-left:4px solid {cap_color}">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
            <span style="font-size:11px;color:#8a9bb5;letter-spacing:1px">CAPITAL FLOW</span>
            <span style="font-size:14px;font-weight:800;color:{cap_color}">{cap_dir.upper()}</span>
        </div>
        {signals_html}
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#0a1628;border:1px solid #3a4460;border-radius:12px;padding:18px 20px;margin-bottom:12px">
        <div style="font-size:11px;color:#7c3aed;letter-spacing:2px;font-weight:700;margin-bottom:10px">INVESTMENT THESIS</div>
        <div style="font-size:13px;color:#e8ecf4;line-height:1.8">{thesis['investment_thesis']}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#1a0a0a;border:1px solid #5a2020;border-radius:12px;padding:18px 20px;margin-bottom:12px">
        <div style="font-size:11px;color:#f44336;letter-spacing:2px;font-weight:700;margin-bottom:10px">RISK THESIS</div>
        <div style="font-size:13px;color:#e8ecf4;line-height:1.8">{thesis['risk_thesis']}</div>
    </div>
    """, unsafe_allow_html=True)
    cat_col, inv_col = st.columns(2)
    with cat_col:
        st.markdown(f"""
        <div style="background:#161b27;border:1px solid #3a4460;border-radius:12px;padding:16px 18px;height:100%">
            <div style="font-size:11px;color:#FFC107;letter-spacing:2px;font-weight:700;margin-bottom:10px">CATALYST THESIS</div>
            <div style="font-size:13px;color:#e8ecf4;line-height:1.8">{thesis['catalyst']}</div>
            <div style="font-size:11px;color:#8a9bb5;margin-top:12px;border-top:1px solid #2a3040;padding-top:8px">
                <b style="color:#b0bcd4">Demand Event:</b> {thesis['demand_event']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with inv_col:
        st.markdown(f"""
        <div style="background:#2a1a0a;border:1px solid #5a3a10;border-radius:12px;padding:16px 18px;height:100%">
            <div style="font-size:11px;color:#FF9800;letter-spacing:2px;font-weight:700;margin-bottom:10px">WHAT INVALIDATES THIS</div>
            <div style="font-size:13px;color:#e8ecf4;line-height:1.8">{thesis['invalidation']}</div>
        </div>
        """, unsafe_allow_html=True)
    if len(cm["themes"]) > 1:
        theme_html = ""
        for tname, _ in cm["themes"][:6]:
            t_d = THEME_KNOWLEDGE.get(tname, {})
            theme_html += (
                f'<span style="background:#1c2130;border:1px solid #3a4460;border-radius:20px;'
                f'padding:5px 14px;font-size:12px;color:#e8ecf4;display:inline-block;margin:3px">'
                f'{t_d.get("icon","📊")} {tname} <span style="color:#8a9bb5">· {t_d.get("tier","")}</span></span>'
            )
        st.markdown(f"""
        <div style="margin:12px 0">
            <div style="font-size:11px;color:#8a9bb5;margin-bottom:6px">ALL THEMES THIS STOCK TOUCHES</div>
            {theme_html}
        </div>
        """, unsafe_allow_html=True)
    if thesis.get("theme_risks"):
        with st.expander(f"⚠️ Theme-Level Risks — {primary}", expanded=False):
            for r in thesis["theme_risks"]:
                st.markdown(f"• {r}")
    if thesis.get("theme_catalysts"):
        with st.expander(f"⚡ Theme-Level Catalysts — {primary}", expanded=False):
            for c in thesis["theme_catalysts"]:
                st.markdown(f"• {c}")


# ─────────────────────────────────────────────────────────────
# V7 THREE-BRAIN ARCHITECTURE
# ─────────────────────────────────────────────────────────────

BRAIN_QUANT = {
    "name": "Quant", "icon": "📊", "color": "#2196F3",
    "cats": ["Dark Pool Intelligence", "Options Warfare", "ETF Gravity", "Market Regime Intelligence", "Catalyst Calendar"],
    "weight": 0.30,
}
BRAIN_FUNDAMENTAL = {
    "name": "Fundamental", "icon": "💰", "color": "#4CAF50",
    "cats": ["Revenue Quality", "War Chest", "Fortress Balance Sheet", "Economic Moat", "M&A Probability", "Industry Dominance"],
    "weight": 0.30,
}
BRAIN_CAPITAL_MIGRATION = {
    "name": "Capital Migration", "icon": "🌊", "color": "#7c3aed",
    "cats": ["Future Civilization Exposure", "Institutional Power", "Sovereign Capital", "Political Intelligence", "Government Influence", "Insider Conviction", "Leadership Intelligence"],
    "weight": 0.40,
}

THREE_BRAINS = [BRAIN_CAPITAL_MIGRATION, BRAIN_FUNDAMENTAL, BRAIN_QUANT]


def score_narrative_legacy(info, hist, cm):
    s = 35
    theme_data = cm.get("theme_data", {})
    flow = theme_data.get("capital_flow", "unknown")
    if flow == "accelerating":
        s += 20
    elif flow == "early acceleration":
        s += 14
    elif flow == "steady":
        s += 8
    elif flow == "cyclical acceleration":
        s += 10
    inst = safe(info, "heldPercentInstitutions", default=0.4) or 0.4
    if inst > 0.75:
        s += 15
    elif inst > 0.55:
        s += 10
    elif inst < 0.30:
        s -= 5
    rg = safe(info, "revenueGrowth", default=0) or 0
    if rg > 0.30:
        s += 15
    elif rg > 0.15:
        s += 10
    elif rg > 0.05:
        s += 5
    elif rg < 0:
        s -= 8
    rec = safe(info, "recommendationMean", default=3)
    s += clamp((3 - rec) * 6, -8, 12)
    themes = cm.get("themes", [])
    s += min(len(themes) * 3, 9)
    if cm.get("is_bottleneck"):
        s += 8
    return clamp(s)


def compute_brain_score(scores, brain):
    cats = brain["cats"]
    return sum(scores[c] for c in cats) / len(cats)


def compute_conviction(quant_score, fundamental_score, cm_brain_score, cm_engine_score, narrative):
    cm_combined = cm_brain_score * 0.4 + cm_engine_score * 0.6
    conviction = cm_combined * 0.40 + fundamental_score * 0.30 + quant_score * 0.30
    narrative_boost = (narrative - 50) * 0.08
    return clamp(conviction + narrative_boost)


def conviction_decision(conviction):
    if conviction >= 72:
        return "BUY", "#4CAF50", "Capital is migrating here. The company occupies a critical position. Future demand is increasing. Risk-reward is attractive."
    elif conviction >= 60:
        return "ACCUMULATE", "#8BC34A", "Structural tailwinds are present. Build position over time on pullbacks. The theme supports medium-term appreciation."
    elif conviction >= 45:
        return "HOLD", "#FFC107", "Mixed signals. The theme has merit but the company's position or timing doesn't warrant new capital allocation."
    elif conviction >= 32:
        return "REDUCE", "#FF9800", "Capital is migrating elsewhere. Reallocate toward stronger thematic positioning and bottleneck positions."
    else:
        return "AVOID", "#f44336", "No capital migration tailwind. The theme is weakening or the company is a commodity participant in a competitive market."


def render_three_brains(scores, cm, info, hist):
    quant_s = compute_brain_score(scores, BRAIN_QUANT)
    fund_s = compute_brain_score(scores, BRAIN_FUNDAMENTAL)
    cm_brain_s = compute_brain_score(scores, BRAIN_CAPITAL_MIGRATION)
    cm_engine_s = cm["scores"]["overall"]
    narrative = score_narrative_legacy(info, hist, cm)
    conviction = compute_conviction(quant_s, fund_s, cm_brain_s, cm_engine_s, narrative)
    decision, dec_color, dec_reason = conviction_decision(conviction)

    st.subheader("🧠 Three-Brain Conviction Engine")
    st.caption("Capital Migration 40% · Fundamental 30% · Quant 30% — Future demand over historical performance")

    d1, d2 = st.columns([1, 2])
    with d1:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a1628,#141e35);border:2px solid {dec_color};
                    border-radius:16px;padding:24px;text-align:center">
            <div style="font-size:11px;color:#8a9bb5;letter-spacing:2px;margin-bottom:4px">CONVICTION SCORE</div>
            <div style="font-size:64px;font-weight:900;color:{dec_color};line-height:1">{conviction:.0f}</div>
            <div style="font-size:22px;font-weight:800;color:{dec_color};margin-top:8px">{decision}</div>
            <div style="font-size:12px;color:#c8d4e8;margin-top:10px;line-height:1.6">{dec_reason}</div>
        </div>
        """, unsafe_allow_html=True)

    with d2:
        brains = [
            ("🌊 Capital Migration", cm_brain_s * 0.4 + cm_engine_s * 0.6, "#7c3aed", "40%"),
            ("💰 Fundamental", fund_s, "#4CAF50", "30%"),
            ("📊 Quant", quant_s, "#2196F3", "30%"),
            ("📡 Narrative", narrative, "#FF9800", "boost"),
        ]
        for label, val, color, wt in brains:
            vc = "#4CAF50" if val >= 65 else ("#FFC107" if val >= 45 else "#f44336")
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin:8px 0;padding:10px 16px;
                        background:#161b27;border-radius:10px;border-left:4px solid {color}">
                <div style="min-width:200px;font-size:14px;font-weight:700;color:#e8ecf4">{label}</div>
                <div style="flex:1">
                    <div style="background:#0d1117;border-radius:6px;height:20px;overflow:hidden">
                        <div style="width:{val:.0f}%;height:100%;background:linear-gradient(90deg,{color},{vc});border-radius:6px"></div>
                    </div>
                </div>
                <div style="min-width:45px;font-size:18px;font-weight:800;color:{vc};text-align:right">{val:.0f}</div>
                <div style="min-width:35px;font-size:11px;color:#8a9bb5;text-align:right">{wt}</div>
            </div>
            """, unsafe_allow_html=True)

    return conviction, decision, dec_color, dec_reason, narrative, quant_s, fund_s, cm_brain_s, cm_engine_s


def render_louis_action_signal(ticker, cm, conviction, decision, dec_color, narrative, quant_s, fund_s, cm_brain_s, cm_engine_s):
    primary = cm["primary_theme"]
    td = cm.get("theme_data", {})
    layers = cm.get("positions", [])
    layer_str = layers[0]["layer"] if layers else "—"
    bn_score = cm["scores"]["bottleneck"]
    cm_score = cm["scores"]["overall"]

    st.markdown(f"""
    <div style="background:#0a1628;border:2px solid {dec_color};border-radius:14px;padding:20px;margin:16px 0">
        <div style="font-size:11px;color:#8a9bb5;letter-spacing:2px;margin-bottom:12px">LOUIS ACTION SIGNAL — {ticker}</div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px">
            <div style="text-align:center;padding:10px;background:#161b27;border-radius:8px">
                <div style="font-size:10px;color:#8a9bb5">THEME</div>
                <div style="font-size:13px;font-weight:700;color:#e8ecf4;margin-top:4px">{td.get('icon','')} {primary}</div>
            </div>
            <div style="text-align:center;padding:10px;background:#161b27;border-radius:8px">
                <div style="font-size:10px;color:#8a9bb5">VALUE CHAIN</div>
                <div style="font-size:13px;font-weight:700;color:#e8ecf4;margin-top:4px">{layer_str}</div>
            </div>
            <div style="text-align:center;padding:10px;background:#161b27;border-radius:8px">
                <div style="font-size:10px;color:#8a9bb5">BOTTLENECK</div>
                <div style="font-size:22px;font-weight:900;color:{'#4CAF50' if bn_score >= 60 else '#FFC107'};margin-top:2px">{bn_score:.0f}</div>
            </div>
            <div style="text-align:center;padding:10px;background:#161b27;border-radius:8px">
                <div style="font-size:10px;color:#8a9bb5">CAP MIGRATION</div>
                <div style="font-size:22px;font-weight:900;color:{'#4CAF50' if cm_score >= 60 else '#FFC107'};margin-top:2px">{cm_score:.0f}</div>
            </div>
            <div style="text-align:center;padding:10px;background:#161b27;border-radius:8px">
                <div style="font-size:10px;color:#8a9bb5">NARRATIVE</div>
                <div style="font-size:22px;font-weight:900;color:{'#4CAF50' if narrative >= 60 else '#FFC107'};margin-top:2px">{narrative:.0f}</div>
            </div>
            <div style="text-align:center;padding:10px;background:#161b27;border-radius:8px">
                <div style="font-size:10px;color:#8a9bb5">QUANT</div>
                <div style="font-size:22px;font-weight:900;color:{'#4CAF50' if quant_s >= 60 else '#FFC107'};margin-top:2px">{quant_s:.0f}</div>
            </div>
            <div style="text-align:center;padding:10px;background:#161b27;border-radius:8px">
                <div style="font-size:10px;color:#8a9bb5">FUNDAMENTAL</div>
                <div style="font-size:22px;font-weight:900;color:{'#4CAF50' if fund_s >= 60 else '#FFC107'};margin-top:2px">{fund_s:.0f}</div>
            </div>
            <div style="text-align:center;padding:10px;background:#161b27;border-radius:8px;border:2px solid {dec_color}">
                <div style="font-size:10px;color:#8a9bb5">CONVICTION</div>
                <div style="font-size:22px;font-weight:900;color:{dec_color};margin-top:2px">{conviction:.0f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_grouped_scorecard(scores):
    st.subheader("📋 18-Category Breakdown by Brain")
    for brain in THREE_BRAINS:
        cats = brain["cats"]
        brain_avg = sum(scores[c] for c in cats) / len(cats)
        gc = "#4CAF50" if brain_avg >= 63 else ("#FFC107" if brain_avg >= 42 else "#f44336")
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin:20px 0 8px 0;padding:8px 12px;
                    background:#161b27;border-radius:10px;border-left:4px solid {brain['color']}">
            <span style="font-size:18px">{brain['icon']}</span>
            <span style="font-size:15px;font-weight:800;color:#ffffff">{brain['name']} Brain</span>
            <span style="font-size:12px;color:#8a9bb5;margin-left:4px">({brain['weight']:.0%} weight)</span>
            <span style="font-size:14px;font-weight:800;color:{gc};margin-left:auto">{brain_avg:.0f}</span>
        </div>
        """, unsafe_allow_html=True)
        for cat in cats:
            val = scores[cat]
            t = tier(val)
            bar_color = {"green": "#4CAF50", "yellow": "#FFC107", "red": "#f44336"}[t]
            analysis = get_analysis(cat, val)
            st.markdown(f"""
            <div class="score-row {t}">
                <div class="score-num {t}">{val}</div>
                <div class="score-body">
                    <div class="score-name">{cat}</div>
                    <div class="score-analysis">💬 {analysis}</div>
                    <div class="bar-bg">
                        <div class="bar-fill" style="width:{val}%;background:{bar_color}"></div>
                    </div>
                </div>
                <div style="text-align:right;padding-top:2px">
                    <span class="tier-badge {t}">{tier_label(val)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# V10 — MACRO RADAR
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def fetch_macro_radar():
    tickers = {"VIX": "^VIX", "DXY": "DX-Y.NYB", "Gold": "GC=F", "Oil": "CL=F",
               "10Y": "^TNX", "2Y": "^IRX", "SPY": "SPY", "QQQ": "QQQ"}
    data = {}
    for label, sym in tickers.items():
        try:
            h = yf.Ticker(sym).history(period="3mo")
            if not h.empty:
                current = float(h["Close"].iloc[-1])
                prev_20 = float(h["Close"].iloc[-20]) if len(h) >= 20 else current
                chg = ((current - prev_20) / prev_20) * 100
                data[label] = {"value": current, "chg_20d": chg}
        except Exception:
            pass
    if not data:
        raise RuntimeError("No macro data")
    return data


def macro_regime(macro):
    vix = macro.get("VIX", {}).get("value", 20)
    dxy_chg = macro.get("DXY", {}).get("chg_20d", 0)
    tnx = macro.get("10Y", {}).get("value", 4.0)
    gold_chg = macro.get("Gold", {}).get("chg_20d", 0)
    spy_chg = macro.get("SPY", {}).get("chg_20d", 0)
    risk_signals = 0
    if vix > 25: risk_signals += 2
    elif vix > 20: risk_signals += 1
    if tnx > 4.8: risk_signals += 1
    if dxy_chg > 3: risk_signals += 1
    if spy_chg < -5: risk_signals += 2
    elif spy_chg < -2: risk_signals += 1
    if gold_chg > 5: risk_signals += 1
    if risk_signals >= 4:
        return "RED", "Risk Off — Protect Capital / Hedge / Raise Cash", "#f44336"
    elif risk_signals >= 2:
        return "YELLOW", "Neutral — Selective / Observe", "#FFC107"
    else:
        return "GREEN", "Risk On — Attack / Accumulate", "#4CAF50"


def render_macro_radar(macro):
    regime, regime_desc, regime_color = macro_regime(macro)
    st.markdown(f"""
    <div style="background:#0a1628;border:2px solid {regime_color};border-radius:14px;padding:20px;text-align:center;margin-bottom:16px">
        <div style="font-size:11px;color:#8a9bb5;letter-spacing:2px">MARKET REGIME</div>
        <div style="font-size:48px;font-weight:900;color:{regime_color};margin:8px 0">{regime}</div>
        <div style="font-size:14px;color:#e8ecf4">{regime_desc}</div>
    </div>
    """, unsafe_allow_html=True)
    cols = st.columns(4)
    indicators = [
        ("VIX", "Fear Index", ""),
        ("DXY", "Dollar Index", ""),
        ("10Y", "10Y Yield", "%"),
        ("Gold", "Gold", "$"),
        ("Oil", "Crude Oil", "$"),
        ("SPY", "S&P 500 ETF", "$"),
        ("QQQ", "Nasdaq ETF", "$"),
        ("2Y", "2Y Yield", "%"),
    ]
    for i, (key, label, prefix) in enumerate(indicators):
        d = macro.get(key, {})
        val = d.get("value", 0)
        chg = d.get("chg_20d", 0)
        chg_color = "#4CAF50" if chg >= 0 else "#f44336"
        if key == "VIX":
            chg_color = "#f44336" if chg >= 0 else "#4CAF50"
        with cols[i % 4]:
            fmt_val = f"${val:,.2f}" if prefix == "$" else (f"{val:.2f}%" if prefix == "%" else f"{val:.2f}")
            st.markdown(f"""
            <div style="background:#161b27;border-radius:10px;padding:12px;text-align:center;margin-bottom:8px;border-top:3px solid {chg_color}">
                <div style="font-size:10px;color:#8a9bb5">{label}</div>
                <div style="font-size:18px;font-weight:800;color:#e8ecf4">{fmt_val}</div>
                <div style="font-size:12px;font-weight:700;color:{chg_color}">{chg:+.1f}% (20d)</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# V10 — MARKET HEALTH 5-GROUP STRUCTURE
# ─────────────────────────────────────────────────────────────

MARKET_HEALTH_GROUPS = {
    "Quality": {
        "icon": "💎", "color": "#4CAF50",
        "cats": ["Revenue Quality", "Fortress Balance Sheet", "War Chest", "Economic Moat"],
    },
    "Momentum": {
        "icon": "🚀", "color": "#2196F3",
        "cats": ["Catalyst Calendar", "Market Regime Intelligence", "Industry Dominance"],
    },
    "Institutional": {
        "icon": "🏛️", "color": "#7c3aed",
        "cats": ["Institutional Power", "ETF Gravity", "Dark Pool Intelligence", "Options Warfare"],
    },
    "Strategic": {
        "icon": "🎯", "color": "#FF9800",
        "cats": ["Future Civilization Exposure", "Sovereign Capital", "Government Influence", "Leadership Intelligence"],
    },
    "Risk": {
        "icon": "🛡️", "color": "#f44336",
        "cats": ["Fortress Balance Sheet", "Insider Conviction", "Political Intelligence", "M&A Probability"],
    },
}


def compute_health_scores(scores):
    result = {}
    for group, data in MARKET_HEALTH_GROUPS.items():
        cats = data["cats"]
        result[group] = sum(scores.get(c, 50) for c in cats) / len(cats)
    result["Overall"] = sum(result.values()) / len(result)
    return result


def render_market_health_scores(scores, health):
    st.subheader("📊 Market Health Assessment")
    cols = st.columns(6)
    groups = list(MARKET_HEALTH_GROUPS.items()) + [("Overall", {"icon": "⚡", "color": "#ffffff"})]
    for col, (name, data) in zip(cols, groups):
        val = health.get(name, health.get("Overall", 50))
        vc = "#4CAF50" if val >= 65 else ("#FFC107" if val >= 45 else "#f44336")
        col.markdown(f"""
        <div style="background:#161b27;border-radius:10px;padding:14px 8px;text-align:center;border-top:3px solid {data['color']}">
            <div style="font-size:28px;font-weight:900;color:{vc}">{val:.0f}</div>
            <div style="font-size:11px;font-weight:700;color:#e8ecf4;margin-top:4px">{data['icon']} {name}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("")
    for group_name, group_data in MARKET_HEALTH_GROUPS.items():
        cats = group_data["cats"]
        group_avg = health[group_name]
        gc = "#4CAF50" if group_avg >= 63 else ("#FFC107" if group_avg >= 42 else "#f44336")
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin:16px 0 6px 0;padding:8px 12px;
                    background:#161b27;border-radius:10px;border-left:4px solid {group_data['color']}">
            <span style="font-size:16px">{group_data['icon']}</span>
            <span style="font-size:14px;font-weight:800;color:#ffffff">{group_name}</span>
            <span style="font-size:14px;font-weight:800;color:{gc};margin-left:auto">{group_avg:.0f}</span>
        </div>
        """, unsafe_allow_html=True)
        for cat in cats:
            val = scores.get(cat, 50)
            t = tier(val)
            bar_color = {"green": "#4CAF50", "yellow": "#FFC107", "red": "#f44336"}[t]
            analysis = get_analysis(cat, val)
            st.markdown(f"""
            <div class="score-row {t}">
                <div class="score-num {t}">{val}</div>
                <div class="score-body">
                    <div class="score-name">{cat}</div>
                    <div class="score-analysis">💬 {analysis}</div>
                    <div class="bar-bg">
                        <div class="bar-fill" style="width:{val}%;background:{bar_color}"></div>
                    </div>
                </div>
                <div style="text-align:right;padding-top:2px">
                    <span class="tier-badge {t}">{tier_label(val)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# CFIS HUNTER — CAPITAL FLOW PREDICTION ENGINE
# Objective: Predict future capital flow before the market recognizes it
# 7 scores → Hunter Score → Classification → Zone Signal
# ─────────────────────────────────────────────────────────────

FUTURE_THEMES = {
    "AI": {"keywords": ["artificial intelligence","machine learning","deep learning","neural","llm","generative ai","gpu","compute","inference","training","ai model","natural language","chatbot","copilot","ai agent"], "tickers": {"NVDA","AMD","AVGO","MSFT","GOOGL","META","AMZN","AAPL","ORCL","CRM","NOW","PLTR","SNOW","ARM","MRVL","SMCI","DELL","VRT","DDOG","PATH"}},
    "Robotics": {"keywords": ["robot","automation","autonomous","self-driving","industrial automation","humanoid","cobot","warehouse automation","surgical robot","drone"], "tickers": {"TSLA","ISRG","DE","CAT","HON","KTOS","PATH"}},
    "Energy": {"keywords": ["energy","power","grid","electricity","solar","wind","renewable","clean energy","battery","storage","utility","electrification"], "tickers": {"CEG","VST","NEE","FSLR","ENPH","ETN","GEV","XOM","CVX"}},
    "Nuclear": {"keywords": ["nuclear","uranium","fission","fusion","small modular reactor","smr","nuclear power","enrichment","fuel cycle"], "tickers": {"OKLO","SMR","NNE","UEC","CCJ","CEG","BWXT"}},
    "Space": {"keywords": ["space","satellite","orbital","launch","rocket","starlink","lunar","mars","constellation","leo","geo orbit","starship"], "tickers": {"SPCX","RKLB","ASTS","LUNR","RDW","MNTS","SPIR","LMT","NOC","BA"}},
    "Defense": {"keywords": ["defense","military","weapon","missile","radar","fighter","navy","army","pentagon","nato","hypersonic","electronic warfare","intelligence"], "tickers": {"LMT","RTX","NOC","GD","BWXT","KTOS","PLTR"}},
    "Cybersecurity": {"keywords": ["cybersecurity","cyber","firewall","endpoint","zero trust","threat detection","siem","soc","ransomware","encryption","identity security"], "tickers": {"CRWD","PANW","ZS","FTNT","NET"}},
    "Biotech": {"keywords": ["biotech","gene","crispr","mrna","drug discovery","clinical trial","fda","therapeutic","oncology","immunotherapy","cell therapy","genome","protein"], "tickers": {"LLY","NVO","MRNA","REGN","VRTX","RXRX","CRSP","ISRG"}},
    "Tokenization": {"keywords": ["tokenization","tokenize","real world asset","rwa","digital securities","blockchain settlement","on-chain","programmable money","stablecoin"], "tickers": {"COIN","BX","KKR","GS","APO"}},
    "Digital Assets": {"keywords": ["bitcoin","crypto","blockchain","defi","web3","digital asset","mining","exchange","custody","wallet","ethereum","nft"], "tickers": {"COIN","MSTR","HOOD","XYZ","MARA","RIOT"}},
}


def score_narrative(info, hist, cm, enriched=None):
    """Narrative Score: How strongly does this stock ride future capital migration themes?"""
    s = 15
    reasons = []
    enriched = enriched or {}
    summary = (info.get("longBusinessSummary", "") or "").lower()
    sector = (info.get("sector", "") or "").lower()
    industry = (info.get("industry", "") or "").lower()
    ticker = (info.get("symbol", "") or "").upper()
    headlines = " ".join(enriched.get("news_headlines", [])).lower()
    text = summary + " " + sector + " " + industry + " " + headlines

    themes_hit = []
    for theme_name, theme_data in FUTURE_THEMES.items():
        kw_hits = sum(1 for kw in theme_data["keywords"] if kw in text)
        ticker_hit = ticker in theme_data["tickers"]
        if ticker_hit or kw_hits >= 2:
            themes_hit.append((theme_name, kw_hits, ticker_hit))

    if len(themes_hit) >= 3:
        s += 30
        reasons.append(f"Multi-theme convergence: positioned across {len(themes_hit)} future capital themes ({', '.join(t[0] for t in themes_hit[:4])})")
    elif len(themes_hit) == 2:
        s += 22
        reasons.append(f"Dual-theme exposure: {themes_hit[0][0]} + {themes_hit[1][0]}")
    elif len(themes_hit) == 1:
        s += 14
        reasons.append(f"Single-theme: {themes_hit[0][0]}")
    else:
        reasons.append("No strong future theme alignment — this is an old-economy stock")

    # Theme capital flow acceleration from CM engine
    theme_data = cm.get("theme_data", {})
    flow = theme_data.get("capital_flow", "unknown")
    if flow == "accelerating":
        s += 22
        reasons.append("Theme capital flow is ACCELERATING — institutional money actively migrating")
    elif flow == "early acceleration":
        s += 16
        reasons.append("EARLY ACCELERATION — smart money positioning before the crowd")
    elif flow == "steady":
        s += 8
        reasons.append("Steady capital flow — established but not accelerating")

    # Revenue growth as demand confirmation
    rg = safe(info, "revenueGrowth", default=0) or 0
    if rg > 0.30:
        s += 15
        reasons.append(f"Revenue growing {rg*100:.0f}% — demand thesis confirmed by real spending")
    elif rg > 0.15:
        s += 10
        reasons.append(f"Revenue growing {rg*100:.0f}% — solid demand growth")
    elif rg > 0.05:
        s += 5
    elif rg < 0:
        s -= 8
        reasons.append(f"Revenue declining {rg*100:.0f}% — narrative may not match reality")

    if cm.get("is_bottleneck"):
        s += 10
        reasons.append("Bottleneck in a future theme — narrative is backed by supply scarcity")

    nd = enriched.get("news_narrative_density", 0)
    if nd > 60:
        s += 5
        reasons.append(f"High news narrative density ({nd:.0f}) — theme is actively in headlines")

    verdict = "Powerful future narrative. Capital will be drawn here by structural forces." if s >= 70 else ("Some narrative alignment but not a dominant theme play." if s >= 45 else "Weak narrative. Capital has no structural reason to flow here.")
    return {"score": clamp(s), "reasons": reasons, "verdict": verdict, "themes": [t[0] for t in themes_hit]}


def score_positioning(info, hist, scores, cm, enriched=None):
    """Positioning Score: How under-owned is this? High = under-owned opportunity."""
    s = 50
    reasons = []
    enriched = enriched or {}

    inst_raw = safe(info, "heldPercentInstitutions", default=None)
    inst_enriched = enriched.get("inst_pct")
    inst = inst_enriched if inst_enriched is not None else inst_raw
    if inst is not None:
        if inst < 0.30:
            s += 25
            reasons.append(f"Only {inst*100:.0f}% institutional ownership — severely under-owned")
        elif inst < 0.50:
            s += 15
            reasons.append(f"Institutional ownership {inst*100:.0f}% — below average, room for discovery")
        elif inst < 0.70:
            s += 8
            reasons.append(f"Institutional ownership {inst*100:.0f}% — moderate, room for further accumulation")
        elif inst < 0.85:
            s += 3
            reasons.append(f"Institutional ownership {inst*100:.0f}% — well-owned but not saturated")
        else:
            s -= 5
            reasons.append(f"Institutional ownership {inst*100:.0f}% — fully owned, limited marginal buyer")
    else:
        reasons.append("Institutional ownership data unavailable — cannot assess positioning")

    n_analysts_raw = safe(info, "numberOfAnalystOpinions", default=None)
    n_analysts_enriched = enriched.get("analyst_count")
    n_analysts = n_analysts_enriched if n_analysts_enriched is not None else n_analysts_raw
    if n_analysts is not None:
        n_analysts = int(n_analysts)
        if n_analysts <= 3:
            s += 18
            reasons.append(f"Only {n_analysts} analysts cover this — Wall Street is sleeping on it")
        elif n_analysts <= 8:
            s += 10
            reasons.append(f"{n_analysts} analysts — below average coverage, still under-followed")
        elif n_analysts <= 20:
            s += 3
            reasons.append(f"{n_analysts} analysts — moderate coverage")
        elif n_analysts >= 40:
            s -= 5
            reasons.append(f"{n_analysts} analysts — heavily covered, consensus risk")
    else:
        reasons.append("Analyst coverage data unavailable")

    price = safe(info, "currentPrice", "regularMarketPrice", default=0) or 0
    target = safe(info, "targetMeanPrice", default=0) or 0
    enr_tp = enriched.get("target_price")
    if enr_tp and price and enr_tp > price * 0.5:
        target = enr_tp
    if price and target and target > 0:
        upside = (target - price) / price * 100
        if upside > 40:
            s += 15
            reasons.append(f"Analyst target implies {upside:.0f}% upside — market hasn't priced the thesis")
        elif upside > 20:
            s += 8
            reasons.append(f"Analyst target implies {upside:.0f}% upside")
        elif upside < -10:
            s -= 10
            reasons.append(f"Analyst target implies {upside:.0f}% — analysts see downside risk")

    mc = safe(info, "marketCap", default=None)
    if mc is not None:
        if mc < 5e9:
            s += 10
            reasons.append(f"Market cap ${mc/1e9:.1f}B — small enough to be invisible to large institutions")
        elif mc < 20e9:
            s += 5
            reasons.append(f"Market cap ${mc/1e9:.1f}B — mid-cap, partially discovered")

    insider_pct = enriched.get("insider_pct")
    if insider_pct is not None and insider_pct > 0.15:
        s += 5
        reasons.append(f"Insider ownership {insider_pct*100:.0f}% — skin in the game")

    verdict = "Severely under-owned and under-followed. Capital hasn't arrived yet — this is the opportunity window." if s >= 70 else ("Partially discovered but room for more institutional adoption." if s >= 45 else "Fully owned and fully covered. The discovery trade is over.")
    return {"score": clamp(s), "reasons": reasons, "verdict": verdict}


def score_force(info, hist, scores, cm, enriched=None):
    """Force Score: Structural forces that COMPEL capital to flow — ETF, benchmark, government, squeeze."""
    s = 25
    reasons = []
    enriched = enriched or {}

    mc = safe(info, "marketCap", default=0) or 0
    rg = safe(info, "revenueGrowth", default=0) or 0
    if mc > 50e9 and rg > 0.15:
        s += 15
        reasons.append(f"Large cap ${mc/1e9:.0f}B + {rg*100:.0f}% growth — strong ETF inclusion/weight increase candidate")
    elif mc > 15e9:
        s += 8
        reasons.append(f"Market cap ${mc/1e9:.0f}B — meets S&P 500 threshold, passive fund demand building")
    elif mc > 5e9:
        s += 4
        reasons.append(f"Market cap ${mc/1e9:.0f}B — mid-cap index eligible")

    summary = (info.get("longBusinessSummary", "") or "").lower()
    headlines = " ".join(enriched.get("news_headlines", [])).lower()
    search_text = summary + " " + headlines
    gov_kw = ["government","defense","national security","pentagon","doe","department of energy","nasa","darpa","strategic","critical infrastructure","chips act","ira","inflation reduction"]
    gov_hits = sum(1 for kw in gov_kw if kw in search_text)
    if gov_hits >= 3:
        s += 18
        reasons.append(f"Government-backed: {gov_hits} strategic keywords — policy tailwinds force capital allocation")
    elif gov_hits >= 1:
        s += 8
        reasons.append("Some government/strategic alignment")

    sf_enriched = enriched.get("short_float")
    sf_raw = safe(info, "shortPercentOfFloat", default=None)
    sf = sf_enriched if sf_enriched is not None else sf_raw
    avg_vol = safe(info, "averageVolume", default=1) or 1
    avg10 = safe(info, "averageVolume10days", default=1) or 1
    vol_ratio = avg10 / avg_vol if avg_vol else 1
    if sf is not None:
        if sf > 0.15 and vol_ratio > 1.3:
            s += 15
            reasons.append(f"Short squeeze setup: {sf*100:.0f}% short + {vol_ratio:.1f}x volume surge — forced buying imminent")
        elif sf > 0.10:
            s += 8
            reasons.append(f"Short interest {sf*100:.0f}% — squeeze potential exists")

    opts_score = scores.get("Options Warfare", 50)
    if opts_score >= 75:
        s += 12
        reasons.append(f"Options flow score {opts_score:.0f} — heavy call positioning suggests gamma squeeze potential")
    elif opts_score >= 60:
        s += 6

    if cm.get("is_bottleneck"):
        s += 10
        reasons.append("Bottleneck position amplifies all structural forces — capital has no alternative")

    if rg > 0.25:
        s += 8
        reasons.append(f"Revenue acceleration {rg*100:.0f}% creates gravitational pull for benchmark inclusion")

    insider_buys = enriched.get("recent_insider_buys", 0)
    insider_sells = enriched.get("recent_insider_sells", 0)
    if insider_buys >= 3 and insider_buys > insider_sells:
        s += 6
        reasons.append(f"{insider_buys} insider buys vs {insider_sells} sells — insider force confirms thesis")

    verdict = "Multiple structural forces are COMPELLING capital inflow. ETF, government, and squeeze mechanics all align." if s >= 70 else ("Some structural forces present but not overwhelming." if s >= 45 else "No structural forces compel capital here. Flow depends on voluntary discovery only.")
    return {"score": clamp(s), "reasons": reasons, "verdict": verdict}


def score_scarcity(info, hist, scores, cm, enriched=None):
    """Scarcity Score: How irreplaceable is this company? Moats, patents, regulatory protection."""
    s = 20
    reasons = []
    enriched = enriched or {}

    gm = safe(info, "grossMargins", default=0) or 0
    if gm > 0.70:
        s += 22
        reasons.append(f"Gross margins {gm*100:.0f}% — extreme pricing power")
    elif gm > 0.50:
        s += 15
        reasons.append(f"Gross margins {gm*100:.0f}% — strong pricing power")
    elif gm > 0.35:
        s += 8
        reasons.append(f"Gross margins {gm*100:.0f}% — moderate")
    elif gm > 0:
        reasons.append(f"Gross margins {gm*100:.0f}% — commodity-like")

    if cm.get("is_bottleneck"):
        s += 20
        bn_reason = ""
        ticker = cm.get("ticker", (info.get("symbol","") or "").upper())
        if ticker in STOCK_THESIS:
            bn_reason = STOCK_THESIS[ticker].get("bottleneck_reason", "")
        reasons.append(f"CONFIRMED BOTTLENECK — {bn_reason[:120]}" if bn_reason else "Supply bottleneck — irreplaceable in the value chain")
    else:
        s -= 5

    summary = (info.get("longBusinessSummary", "") or "").lower()
    moat_kw = ["patent","proprietary","exclusive","sole supplier","only provider","monopoly","irreplaceable","dominant","market leader","leading provider","regulatory approval","fda approved","licensed","classified","security clearance"]
    hits = sum(1 for kw in moat_kw if kw in summary)
    if hits >= 4:
        s += 22
        reasons.append(f"Deep moat: {hits} scarcity/moat keywords — patents, regulatory barriers, or monopoly position")
    elif hits >= 2:
        s += 12
        reasons.append(f"Moderate moat: {hits} competitive protection keywords")
    elif hits >= 1:
        s += 5

    roic = enriched.get("roic")
    roe = enriched.get("roe")
    if roic is not None and roic > 0.20:
        s += 10
        reasons.append(f"ROIC {roic*100:.0f}% — high returns on invested capital confirm pricing power")
    elif roic is not None and roic > 0.12:
        s += 5

    moat = scores.get("Economic Moat", 50)
    if moat >= 75:
        s += 8
        reasons.append(f"Economic moat score {moat:.0f} — wide competitive advantage")
    elif moat >= 60:
        s += 4
    elif moat < 35:
        s -= 5
        reasons.append(f"Economic moat score {moat:.0f} — narrow, vulnerable to competition")

    rd_expense = enriched.get("rd_expense")
    if rd_expense is not None:
        mc = safe(info, "marketCap", default=0) or 0
        if mc > 0:
            rd_ratio = rd_expense / mc
            if rd_ratio > 0.15:
                s += 8
                reasons.append(f"R&D intensity {rd_ratio*100:.0f}% of market cap — building deep technology moat")
            elif rd_ratio > 0.05:
                s += 4
                reasons.append(f"R&D intensity {rd_ratio*100:.0f}% — investing in future moat")
    else:
        rd_kw = ["research","r&d","innovation","breakthrough","first-of-its-kind","pioneering"]
        rd_hits = sum(1 for kw in rd_kw if kw in summary)
        if rd_hits >= 2:
            s += 6
            reasons.append("R&D/innovation focus in business description")

    verdict = "Deeply scarce. Protected by patents, bottleneck position, and regulatory barriers. Cannot be replicated." if s >= 70 else ("Some competitive protection but not irreplaceable." if s >= 45 else "Commodity business. No scarcity advantage — competitors can easily replicate.")
    return {"score": clamp(s), "reasons": reasons, "verdict": verdict}


def score_timing(info, hist, scores, cm, enriched=None):
    """Timing Score: Is the catalyst window opening NOW? Product launches, earnings, M&A, regulatory."""
    s = 40
    reasons = []
    enriched = enriched or {}

    if not hist.empty and len(hist) >= 20:
        close = hist["Close"]
        mom_20 = (close.iloc[-1] - close.iloc[-20]) / close.iloc[-20] * 100 if len(hist) >= 20 else 0
        mom_5 = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100 if len(hist) >= 5 else 0

        if mom_20 > 15 and mom_5 > 3:
            s += 20
            reasons.append(f"Strong momentum: +{mom_20:.1f}% in 20 days, +{mom_5:.1f}% in 5 days — catalysts are firing NOW")
        elif mom_20 > 8:
            s += 14
            reasons.append(f"Building momentum: +{mom_20:.1f}% in 20 days — capital is starting to arrive")
        elif mom_20 > 3:
            s += 8
            reasons.append(f"Positive momentum: +{mom_20:.1f}% in 20 days — trend forming")
        elif mom_20 > 0:
            s += 4
            reasons.append(f"Mild uptrend: +{mom_20:.1f}% in 20 days")
        elif mom_20 > -10:
            s -= 3
            reasons.append(f"Mild pullback: {mom_20:.1f}% in 20 days — may be entry window")
        elif mom_20 < -10:
            s -= 5
            reasons.append(f"Negative momentum: {mom_20:.1f}% in 20 days — timing may be early")

    rg = safe(info, "revenueGrowth", default=0) or 0
    qrg = safe(info, "quarterlyRevenueGrowth", default=0) or 0
    quarterly_revs = enriched.get("quarterly_revenues", [])
    if qrg and qrg > rg and qrg > 0.15:
        s += 12
        reasons.append(f"Revenue ACCELERATING: quarterly {qrg*100:.0f}% vs annual {rg*100:.0f}% — inflection point")
    elif len(quarterly_revs) >= 2:
        vals = [v for _, v in quarterly_revs if v and v > 0]
        if len(vals) >= 4 and vals[0] > vals[3]:
            q_growth = (vals[0] - vals[3]) / vals[3]
            if q_growth > 0.20:
                s += 14
                reasons.append(f"Revenue ACCELERATING (EDGAR): {q_growth*100:.0f}% YoY quarterly growth")
            elif q_growth > 0.10:
                s += 8
                reasons.append(f"Revenue growing (EDGAR): {q_growth*100:.0f}% YoY quarterly")
        elif len(vals) >= 2 and vals[0] > vals[1]:
            seq_growth = (vals[0] - vals[1]) / vals[1]
            if seq_growth > 0.05:
                s += 8
                reasons.append(f"Sequential revenue growth (EDGAR): {seq_growth*100:.0f}% QoQ")
    elif rg > 0.20:
        s += 8
        reasons.append(f"Revenue growing {rg*100:.0f}% — catalyst is sustained demand")

    avg_vol = safe(info, "averageVolume", default=1) or 1
    avg10 = safe(info, "averageVolume10days", default=1) or 1
    vol_ratio = avg10 / avg_vol if avg_vol else 1
    if vol_ratio > 2.0:
        s += 15
        reasons.append(f"Volume {vol_ratio:.1f}x above average — something is happening, attention spiking")
    elif vol_ratio > 1.4:
        s += 8
        reasons.append(f"Volume {vol_ratio:.1f}x above average — increasing attention")

    price = safe(info, "currentPrice", "regularMarketPrice", default=0) or 0
    target = safe(info, "targetMeanPrice", default=0) or 0
    enr_tp = enriched.get("target_price")
    if enr_tp and price and enr_tp > price * 0.5:
        target = enr_tp
    if price and target:
        upside = (target - price) / price * 100
        if upside > 30:
            s += 10
            reasons.append(f"Analyst target {upside:.0f}% above — re-rating catalyst pending")
        elif upside < 0:
            s -= 5
            reasons.append(f"Below analyst target — may need thesis reset")

    summary = (info.get("longBusinessSummary", "") or "").lower()
    headlines = " ".join(enriched.get("news_headlines", [])).lower()
    search_text = summary + " " + headlines
    ma_kw = ["acquisition","partnership","joint venture","strategic alliance","merger","contract win","deal","agreement"]
    ma_hits = sum(1 for kw in ma_kw if kw in search_text)
    if ma_hits >= 2:
        s += 8
        reasons.append("M&A/partnership language detected — deal catalysts possible")

    earnings_date = enriched.get("earnings_date")
    if earnings_date:
        try:
            ed = datetime.strptime(earnings_date, "%Y-%m-%d")
            days_to_er = (ed - datetime.now()).days
            if 0 <= days_to_er <= 14:
                s += 6
                reasons.append(f"Earnings in {days_to_er} days — potential catalyst imminent")
            elif 0 <= days_to_er <= 30:
                s += 3
                reasons.append(f"Earnings in {days_to_er} days — approaching catalyst window")
        except Exception:
            pass

    insider_buys = enriched.get("recent_insider_buys", 0)
    if insider_buys >= 3:
        s += 8
        reasons.append(f"{insider_buys} insider buys in 90 days — insiders see upcoming catalyst")
    elif insider_buys >= 1:
        s += 4
        reasons.append(f"{insider_buys} recent insider buy — insider confidence signal")

    verdict = "Timing is NOW. Momentum, volume, and catalysts are all firing. Capital flow window is open." if s >= 70 else ("Timing is developing. Catalysts exist but haven't fully triggered yet. PATIENCE ZONE." if s >= 45 else "Timing is early or adverse. No near-term catalyst visible.")
    return {"score": clamp(s), "reasons": reasons, "verdict": verdict}


def score_cap(info, hist, scores, cm, narrative_s, positioning_s, force_s, timing_s):
    """CAP Score: Capital Attraction Probability — probability capital flows here at each time horizon."""
    reasons = []

    # Derive time-horizon probabilities
    # 3 months: timing-heavy (is capital flowing NOW?)
    cap_3m = clamp(timing_s * 0.40 + force_s * 0.30 + narrative_s * 0.20 + positioning_s * 0.10)
    # 6 months: balanced
    cap_6m = clamp(narrative_s * 0.25 + force_s * 0.30 + timing_s * 0.25 + positioning_s * 0.20)
    # 12 months: narrative + force dominate
    cap_12m = clamp(narrative_s * 0.35 + force_s * 0.25 + positioning_s * 0.25 + timing_s * 0.15)
    # 24 months: narrative + positioning (discovery trade)
    cap_24m = clamp(narrative_s * 0.40 + positioning_s * 0.30 + force_s * 0.20 + timing_s * 0.10)

    # Overall CAP is weighted toward medium-term
    overall = cap_3m * 0.15 + cap_6m * 0.25 + cap_12m * 0.35 + cap_24m * 0.25

    # Capital flow direction from CM engine
    cap_dir = cm.get("capital_direction", "Neutral")
    if cap_dir == "Inflow":
        overall += 10
        reasons.append("Active capital INFLOW detected — institutions are already moving money here")
    elif cap_dir == "Outflow":
        overall -= 10
        reasons.append("Capital OUTFLOW detected — money is leaving, probability drops")

    # Institutional demand signals
    inst = safe(info, "heldPercentInstitutions", default=0.5) or 0.5
    inst_change = scores.get("Institutional Power", 50)
    if inst_change >= 70 and inst < 0.70:
        overall += 8
        reasons.append("Institutional demand rising + still under-owned — classic pre-migration setup")

    # Theme migration
    theme_flow = cm.get("theme_data", {}).get("capital_flow", "unknown")
    if theme_flow == "accelerating":
        overall += 8
        reasons.append("Theme is accelerating — entire sector attracting capital regardless of individual stock picking")

    overall = clamp(overall)

    if overall >= 70:
        reasons.append(f"HIGH probability of capital attraction across all time horizons")
    elif overall >= 50:
        reasons.append(f"MODERATE probability — capital likely arrives within 6-12 months")
    else:
        reasons.append(f"LOW probability — no structural pull for capital in the near term")

    verdict = f"Capital attraction is highly probable. 3M: {cap_3m:.0f}% · 6M: {cap_6m:.0f}% · 12M: {cap_12m:.0f}% · 24M: {cap_24m:.0f}%"
    return {"score": overall, "reasons": reasons, "verdict": verdict,
            "cap_3m": cap_3m, "cap_6m": cap_6m, "cap_12m": cap_12m, "cap_24m": cap_24m}


def score_crowding(info, hist, scores, enriched=None):
    """Crowding Index: How crowded is the trade? 100 = crowded, 0 = ignored. LOWER is better for hunters."""
    s = 20
    reasons = []
    enriched = enriched or {}

    inst_raw = safe(info, "heldPercentInstitutions", default=None)
    inst_enriched = enriched.get("inst_pct")
    inst = inst_enriched if inst_enriched is not None else inst_raw
    if inst is not None:
        if inst > 0.90:
            s += 25
            reasons.append(f"Institutional ownership {inst*100:.0f}% — extremely crowded, no marginal buyer")
        elif inst > 0.75:
            s += 15
            reasons.append(f"Institutional ownership {inst*100:.0f}% — heavily owned")
        elif inst > 0.60:
            s += 8
        elif inst < 0.30:
            s -= 5
            reasons.append(f"Institutional ownership {inst*100:.0f}% — barely noticed by institutions")

    n_analysts_raw = safe(info, "numberOfAnalystOpinions", default=None)
    n_analysts_enriched = enriched.get("analyst_count")
    n_analysts = n_analysts_enriched if n_analysts_enriched is not None else n_analysts_raw
    if n_analysts is not None:
        n_analysts = int(n_analysts)
        if n_analysts >= 35:
            s += 20
            reasons.append(f"{n_analysts} analysts — Wall Street consensus already formed, no edge")
        elif n_analysts >= 20:
            s += 10
            reasons.append(f"{n_analysts} analysts — well-covered")
        elif n_analysts <= 3:
            s -= 5
            reasons.append(f"Only {n_analysts} analysts — information asymmetry exists")

    avg_vol = safe(info, "averageVolume", default=1) or 1
    mc = safe(info, "marketCap", default=0) or 0
    price = safe(info, "currentPrice", "regularMarketPrice", default=1) or 1
    if mc > 0:
        turnover = (avg_vol * price) / mc * 252
        if turnover > 5.0:
            s += 15
            reasons.append(f"Annual turnover {turnover:.1f}x float — extremely active trading")
        elif turnover > 2.0:
            s += 8

    if mc > 500e9:
        s += 15
        reasons.append(f"Mega-cap ${mc/1e9:.0f}B — in every index, ETF, and portfolio already")
    elif mc > 100e9:
        s += 8

    news_density = enriched.get("news_narrative_density", 0)
    if news_density > 80:
        s += 5
        reasons.append("High media attention — stock is in the spotlight")

    s = clamp(s)
    if s >= 70:
        verdict = "Extremely crowded. Everyone owns it, everyone covers it. The alpha is gone."
    elif s >= 45:
        verdict = "Moderately crowded. Some discovery left but diminishing edge."
    else:
        verdict = "Under-the-radar. Few own it, few cover it. This is where capital flow hunters find alpha."
    return {"score": s, "reasons": reasons, "verdict": verdict}


def compute_conviction_score(info, hist, scores, cm, hunter_components):
    """Separate Conviction Score: measures confidence in the capital flow thesis, not the thesis itself."""
    s = 30
    reasons = []

    n = hunter_components
    ns, ps, fs, ss, ts, cs, crs = n["narrative"]["score"], n["positioning"]["score"], n["force"]["score"], n["scarcity"]["score"], n["timing"]["score"], n["cap"]["score"], n["crowding"]["score"]
    high_scores = sum(1 for x in [ns, ps, fs, ss, ts, cs] if x >= 70)
    if high_scores >= 5:
        s += 15; reasons.append(f"Signal consistency: {high_scores}/6 scores above 70 — multi-dimensional confirmation")
    elif high_scores >= 3:
        s += 8; reasons.append(f"Moderate signal alignment: {high_scores}/6 scores above 70")

    inst_pct = (info.get("heldPercentInstitutions", 0) or 0)
    if inst_pct > 0.6:
        s += 8; reasons.append(f"Institutional confirmation: {inst_pct:.0%} held by institutions")
    elif inst_pct > 0.3:
        s += 4

    cap_data = n["cap"]
    h_vals = [cap_data.get(k, 0) for k in ("cap_3m", "cap_6m", "cap_12m", "cap_24m") if isinstance(cap_data.get(k), (int, float))]
    if h_vals and min(h_vals) >= 60:
        s += 10; reasons.append(f"CAP confirmation: positive probability across all time horizons (min {min(h_vals):.0f}%)")
    elif h_vals and max(h_vals) >= 80:
        s += 5; reasons.append(f"CAP partial: strongest horizon at {max(h_vals):.0f}%")

    cm_overall = cm.get("scores", {}).get("overall", 0)
    if cm_overall >= 70:
        s += 8; reasons.append(f"Capital Migration Engine confirms thesis: {cm_overall:.0f}/100")
    elif cm_overall >= 50:
        s += 4

    if ts >= 70 and fs >= 70:
        s += 8; reasons.append("Catalyst confirmation: timing + force both strong — entry window active")
    elif ts >= 60:
        s += 3

    rev_g = info.get("revenueGrowth", 0) or 0
    earn_g = info.get("earningsGrowth", 0) or 0
    if rev_g > 0.2 and earn_g > 0.2:
        s += 6; reasons.append(f"Fundamental confirmation: revenue {rev_g:.0%} + earnings {earn_g:.0%} growth")
    elif rev_g > 0.1:
        s += 3

    if cm.get("is_bottleneck"):
        s += 5; reasons.append("Bottleneck asset — structurally scarce in its theme")

    analyst_count = info.get("numberOfAnalystOpinions", 0) or 0
    rec = info.get("recommendationMean", 3) or 3
    if analyst_count >= 10 and rec <= 2.0:
        s += 5; reasons.append(f"Analyst consensus strong: {analyst_count} analysts, mean rec {rec:.1f}")

    if len(hist) >= 60:
        vol_recent = hist["Volume"].iloc[-20:].mean()
        vol_prior = hist["Volume"].iloc[-60:-20].mean()
        if vol_prior > 0 and vol_recent > vol_prior * 1.3:
            s += 5; reasons.append("Volume confirmation: recent 20-day average 30%+ above prior period")

    return {"score": max(0, min(100, s)), "reasons": reasons}


def compute_hunter(info, hist, scores, cm, enriched=None):
    """Compute all 7 Hunter scores, Conviction Score, and GO/WAIT/PASS action."""
    enriched = enriched or {}
    narrative = score_narrative(info, hist, cm, enriched)
    positioning = score_positioning(info, hist, scores, cm, enriched)
    force = score_force(info, hist, scores, cm, enriched)
    scarcity = score_scarcity(info, hist, scores, cm, enriched)
    timing = score_timing(info, hist, scores, cm, enriched)
    cap = score_cap(info, hist, scores, cm, narrative["score"], positioning["score"], force["score"], timing["score"])
    crowding = score_crowding(info, hist, scores, enriched)

    hunter_score = clamp(
        narrative["score"] * 0.15 +
        positioning["score"] * 0.15 +
        force["score"] * 0.20 +
        scarcity["score"] * 0.10 +
        timing["score"] * 0.10 +
        cap["score"] * 0.20 +
        (100 - crowding["score"]) * 0.10
    )

    components = {"narrative": narrative, "positioning": positioning, "force": force,
                  "scarcity": scarcity, "timing": timing, "cap": cap, "crowding": crowding}
    conviction = compute_conviction_score(info, hist, scores, cm, components)

    # CALIBRATION TARGETS: 90-100 top 1%, 85-90 top 5%, 80-85 top 10%, 60-75 average, <60 weak
    if hunter_score >= 90: classification = "High Conviction"
    elif hunter_score >= 85: classification = "Watch Closely"
    elif hunter_score >= 80: classification = "Monitor"
    elif hunter_score >= 60: classification = "Average"
    else: classification = "Weak"

    hs = hunter_score
    conv = conviction["score"]
    cap_s = cap["score"]
    force_s = force["score"]
    timing_s = timing["score"]
    crowding_s = crowding["score"]
    dq = enriched.get("data_quality", 0)

    if hs >= 95 and conv >= 90 and cap_s >= 90 and force_s >= 90 and timing_s >= 85:
        action = "STRONG GO"
        action_color = "#00E676"
        action_icon = "⚡"
        action_desc = "Maximum conviction. All engines aligned. Capital flow confirmed. Timing locked. Deploy capital."
    elif hs >= 90 and conv >= 80 and cap_s >= 85 and force_s >= 80 and timing_s >= 75:
        action = "GO"
        action_color = "#4CAF50"
        action_icon = "🔥"
        action_desc = "High conviction. Capital flow confirmed. Timing aligned. Enter position."
    elif hs >= 80:
        wait_reasons = []
        if timing_s < 75: wait_reasons.append("Timing not mature")
        if conv < 80: wait_reasons.append("Conviction needs confirmation")
        if force_s < 80: wait_reasons.append("Force insufficient")
        if cap_s < 85: wait_reasons.append("Capital flow not fully confirmed")
        if crowding_s >= 70: wait_reasons.append("Crowding elevated")
        action = "WAIT"
        action_color = "#FFC107"
        action_icon = "🟡"
        action_desc = "Future opportunity. " + ". ".join(wait_reasons) + "."
    else:
        action = "PASS"
        action_color = "#78909C"
        action_icon = "❌"
        action_desc = "Insufficient conviction. Capital not migrating here."

    hunt_alert = (cap_s >= 90 and force_s >= 90 and timing_s >= 85 and conv >= 90 and crowding_s < 60)

    return {
        "narrative": narrative, "positioning": positioning, "force": force,
        "scarcity": scarcity, "timing": timing, "cap": cap, "crowding": crowding,
        "hunter_score": hunter_score, "conviction": conviction,
        "classification": classification,
        "data_quality": dq,
        "action": action, "action_color": action_color, "action_icon": action_icon, "action_desc": action_desc,
        "hunt_alert": hunt_alert,
        "zone": action, "zone_color": action_color, "zone_label": action, "zone_desc": action_desc,
    }


def check_hunter_calibration(rows):
    """Check if Hunter Engine scoring is overly restrictive. Returns warning dict or None."""
    if not rows:
        return None
    hunter_scores = sorted([r.get("conviction", r.get("hunter_score", 0)) for r in rows], reverse=True)
    max_score = hunter_scores[0] if hunter_scores else 0
    above_85 = sum(1 for s in hunter_scores if s >= 85)
    above_80 = sum(1 for s in hunter_scores if s >= 80)
    above_60 = sum(1 for s in hunter_scores if s >= 60)
    total = len(hunter_scores)
    avg = sum(hunter_scores) / total if total else 0

    warnings = []
    if max_score < 85:
        warnings.append(f"Highest score in universe is {max_score:.0f} — no stock qualifies as Watch Closely or above")
    if total > 20 and above_85 / total < 0.01:
        warnings.append(f"Only {above_85}/{total} stocks ({above_85/total*100:.1f}%) above 85 — expected ~5%")
    if total > 20 and above_80 / total < 0.03:
        warnings.append(f"Only {above_80}/{total} stocks above 80 — expected ~10%")
    if avg < 50:
        warnings.append(f"Average score {avg:.0f} — expected 60-75 range")
    if avg > 80:
        warnings.append(f"Average score {avg:.0f} — scoring too generous, expected 60-75")

    if warnings:
        return {
            "is_restrictive": max_score < 85,
            "is_generous": avg > 80,
            "max_score": max_score,
            "avg_score": avg,
            "above_85": above_85,
            "above_80": above_80,
            "total": total,
            "warnings": warnings,
        }
    return None


def render_hunter(hunter, ticker, cm):
    """Render the full CFIS Hunter intelligence panel — V2 CIO-style."""
    hs = hunter["hunter_score"]
    ac = hunter["action_color"]
    conv = hunter.get("conviction", {})
    conv_score = conv.get("score", 0) if isinstance(conv, dict) else 0

    # ── HUNT ALERT ───────────────────────────────────
    if hunter.get("hunt_alert"):
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a0a00,#2a1500);border:2px solid #FF6B00;border-radius:16px;padding:20px;text-align:center;margin-bottom:16px;animation:pulse 2s infinite">
            <div style="font-size:28px;font-weight:900;color:#FF9800;letter-spacing:3px">🔥 HUNT ALERT</div>
            <div style="font-size:12px;color:#FFB74D;margin-top:6px">All conditions met: CAP &gt; 90 • Force &gt; 90 • Timing &gt; 85 • Conviction &gt; 90 • Crowding &lt; 60</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Header: Hunter Score + Action + Conviction ───
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0a0a1e,#0a1a2e);border:2px solid {ac};
                border-radius:16px;padding:28px;margin-bottom:16px">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap">
            <div style="text-align:center;flex:1;min-width:200px">
                <div style="font-size:10px;color:#8a9bb5;letter-spacing:3px">HUNTER SCORE</div>
                <div style="font-size:64px;font-weight:900;color:{ac};line-height:1;margin:8px 0">{hs:.0f}</div>
                <div style="font-size:16px;font-weight:800;color:{ac};letter-spacing:2px">{hunter['classification'].upper()}</div>
            </div>
            <div style="text-align:center;flex:0;min-width:160px;padding:0 20px">
                <div style="display:inline-block;background:{ac};color:#000;font-weight:900;font-size:20px;padding:10px 32px;border-radius:24px;letter-spacing:3px">{hunter['action_icon']} {hunter['action']}</div>
                <div style="font-size:11px;color:#c8d4e8;margin-top:10px;max-width:280px">{hunter['action_desc']}</div>
            </div>
            <div style="text-align:center;flex:1;min-width:150px">
                <div style="font-size:10px;color:#8a9bb5;letter-spacing:3px">CONVICTION</div>
                <div style="font-size:48px;font-weight:900;color:{'#4CAF50' if conv_score>=85 else ('#FFC107' if conv_score>=60 else '#ef5350')};line-height:1;margin:8px 0">{conv_score:.0f}</div>
                <div style="font-size:10px;color:#8a9bb5">SIGNAL CONFIDENCE</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 7 Score Tiles ────────────────────────────────
    score_defs = [
        ("Narrative", hunter["narrative"], "🌊", "15%"),
        ("Positioning", hunter["positioning"], "🎯", "15%"),
        ("Force", hunter["force"], "⚡", "20%"),
        ("Scarcity", hunter["scarcity"], "🔒", "10%"),
        ("Timing", hunter["timing"], "⏰", "10%"),
        ("CAP", hunter["cap"], "💰", "20%"),
        ("Crowding", hunter["crowding"], "👥", "10%"),
    ]

    cols1 = st.columns(4)
    for i, (name, data, icon, weight) in enumerate(score_defs[:4]):
        val = data["score"]
        vc = ("#4CAF50" if val < 40 else ("#FFC107" if val < 65 else "#f44336")) if name == "Crowding" else ("#4CAF50" if val >= 70 else ("#FFC107" if val >= 45 else "#f44336"))
        with cols1[i]:
            st.markdown(f"""
            <div style="background:#161b27;border-radius:10px;padding:12px;text-align:center;margin-bottom:6px;border-top:3px solid {vc}">
                <div style="font-size:18px">{icon}</div>
                <div style="font-size:26px;font-weight:900;color:{vc}">{val:.0f}</div>
                <div style="font-size:11px;font-weight:700;color:#e8ecf4">{name}</div>
                <div style="font-size:9px;color:#8a9bb5">Weight: {weight}</div>
            </div>
            """, unsafe_allow_html=True)

    cols2 = st.columns(3)
    for i, (name, data, icon, weight) in enumerate(score_defs[4:]):
        val = data["score"]
        vc = ("#4CAF50" if val < 40 else ("#FFC107" if val < 65 else "#f44336")) if name == "Crowding" else ("#4CAF50" if val >= 70 else ("#FFC107" if val >= 45 else "#f44336"))
        with cols2[i]:
            st.markdown(f"""
            <div style="background:#161b27;border-radius:10px;padding:12px;text-align:center;margin-bottom:6px;border-top:3px solid {vc}">
                <div style="font-size:18px">{icon}</div>
                <div style="font-size:26px;font-weight:900;color:{vc}">{val:.0f}</div>
                <div style="font-size:11px;font-weight:700;color:#e8ecf4">{name}</div>
                <div style="font-size:9px;color:#8a9bb5">Weight: {weight}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── CAP Time Horizon ─────────────────────────────
    cap = hunter["cap"]
    st.markdown(f"""
    <div style="background:#161b27;border:1px solid #3a4460;border-radius:12px;padding:16px;margin:10px 0">
        <div style="font-size:11px;color:#FFC107;letter-spacing:2px;font-weight:700;margin-bottom:10px">CAPITAL ATTRACTION PROBABILITY BY HORIZON</div>
        <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
            <div style="text-align:center;min-width:80px">
                <div style="font-size:22px;font-weight:900;color:{'#4CAF50' if cap['cap_3m']>=65 else ('#FFC107' if cap['cap_3m']>=45 else '#f44336')}">{cap['cap_3m']:.0f}%</div>
                <div style="font-size:10px;color:#8a9bb5">3 MONTHS</div>
            </div>
            <div style="text-align:center;min-width:80px">
                <div style="font-size:22px;font-weight:900;color:{'#4CAF50' if cap['cap_6m']>=65 else ('#FFC107' if cap['cap_6m']>=45 else '#f44336')}">{cap['cap_6m']:.0f}%</div>
                <div style="font-size:10px;color:#8a9bb5">6 MONTHS</div>
            </div>
            <div style="text-align:center;min-width:80px">
                <div style="font-size:22px;font-weight:900;color:{'#4CAF50' if cap['cap_12m']>=65 else ('#FFC107' if cap['cap_12m']>=45 else '#f44336')}">{cap['cap_12m']:.0f}%</div>
                <div style="font-size:10px;color:#8a9bb5">12 MONTHS</div>
            </div>
            <div style="text-align:center;min-width:80px">
                <div style="font-size:22px;font-weight:900;color:{'#4CAF50' if cap['cap_24m']>=65 else ('#FFC107' if cap['cap_24m']>=45 else '#f44336')}">{cap['cap_24m']:.0f}%</div>
                <div style="font-size:10px;color:#8a9bb5">24 MONTHS</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Conviction Reasons ───────────────────────────
    if conv.get("reasons"):
        with st.expander("🔐 Conviction Score Intelligence"):
            for r in conv["reasons"]:
                st.markdown(f"<div style='color:#c9d1d9;font-size:13px;padding:4px 0;border-bottom:1px solid #21262d'>• {r}</div>", unsafe_allow_html=True)

    # ── Detailed Intelligence per Score ───────────────
    st.markdown("---")
    st.markdown("### 🔍 Hunter Intelligence — Why Capital Will (or Won't) Flow Here")

    for name, data, icon, weight in score_defs:
        val = data["score"]
        vc = ("#4CAF50" if val < 40 else ("#FFC107" if val < 65 else "#f44336")) if name == "Crowding" else ("#4CAF50" if val >= 70 else ("#FFC107" if val >= 45 else "#f44336"))
        reasons = data.get("reasons", [])
        verdict = data.get("verdict", "")
        reasons_html = "".join(
            f'<div style="font-size:12px;color:#e8ecf4;line-height:1.6;padding:3px 0;border-bottom:1px solid #1e2540">• {r}</div>'
            for r in reasons
        )
        st.markdown(f"""
        <div style="background:#161b27;border:1px solid #2a3050;border-radius:12px;padding:16px;margin-bottom:8px;border-left:4px solid {vc}">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                <span style="font-size:20px">{icon}</span>
                <div style="font-size:14px;font-weight:800;color:#ffffff">{name} <span style="font-size:11px;color:#8a9bb5">(Weight: {weight})</span></div>
                <div style="margin-left:auto;font-size:26px;font-weight:900;color:{vc}">{val:.0f}</div>
            </div>
            {reasons_html}
            <div style="background:#0a0e17;border-radius:8px;padding:8px 12px;margin-top:8px">
                <div style="font-size:10px;color:{vc};letter-spacing:1px;font-weight:700;margin-bottom:3px">VERDICT</div>
                <div style="font-size:12px;color:#e8ecf4;font-weight:600;line-height:1.5">{verdict}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Investment Thesis from CM engine ──────────────
    thesis = cm.get("thesis", {})
    if thesis.get("investment_thesis"):
        st.markdown("---")
        st.markdown("### 📜 Capital Migration Thesis")
        t1, t2 = st.columns(2)
        with t1:
            st.markdown(f"""
            <div style="background:#0a1628;border-left:4px solid #7c3aed;border-radius:0 10px 10px 0;padding:14px 16px;margin-bottom:8px">
                <div style="font-size:10px;color:#7c3aed;letter-spacing:2px;font-weight:700;margin-bottom:6px">INVESTMENT THESIS</div>
                <div style="font-size:12px;color:#e8ecf4;line-height:1.7">{thesis['investment_thesis']}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:#1a0a0a;border-left:4px solid #f44336;border-radius:0 10px 10px 0;padding:14px 16px;margin-bottom:8px">
                <div style="font-size:10px;color:#f44336;letter-spacing:2px;font-weight:700;margin-bottom:6px">RISK THESIS</div>
                <div style="font-size:12px;color:#e8ecf4;line-height:1.7">{thesis['risk_thesis']}</div>
            </div>
            """, unsafe_allow_html=True)
        with t2:
            st.markdown(f"""
            <div style="background:#161b27;border-left:4px solid #FFC107;border-radius:0 10px 10px 0;padding:14px 16px;margin-bottom:8px">
                <div style="font-size:10px;color:#FFC107;letter-spacing:2px;font-weight:700;margin-bottom:6px">CATALYST</div>
                <div style="font-size:12px;color:#e8ecf4;line-height:1.7">{thesis['catalyst']}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:#2a1a0a;border-left:4px solid #FF9800;border-radius:0 10px 10px 0;padding:14px 16px;margin-bottom:8px">
                <div style="font-size:10px;color:#FF9800;letter-spacing:2px;font-weight:700;margin-bottom:6px">INVALIDATION</div>
                <div style="font-size:12px;color:#e8ecf4;line-height:1.7">{thesis.get('invalidation','')}</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# CAPITAL FLOW INTELLIGENCE ENGINE
# 6 layers → Hunt Trigger → Capital Probability Ranking
# Weight: Institutional 30%, Alt Data 20%, Options 15%,
#         Fundamentals 15%, News 10%, Social 10%
# ─────────────────────────────────────────────────────────────

SOVEREIGN_FUNDS = ["gic","temasek","adia","abu dhabi","norway","norges","qatar","saudi","kuwait","china investment","safe investment","hong kong monetary","korea investment","national pension"]
PENSION_FUNDS = ["calpers","calstrs","ontario teachers","cpp","canada pension","new york state","florida state","texas teachers","wisconsin","pension"]


@st.cache_data(ttl=600)
def intel_institutional_flow(ticker):
    """Layer 1: Institutional Flow Intelligence. Detects fund accumulation, sovereign/pension participation."""
    result = {"score": 30, "signals": [], "accumulating": [], "distributing": [], "sovereign": False, "pension": False, "net_direction": "neutral"}
    try:
        tk = yf.Ticker(ticker)
        info = tk.info or {}
        inst_pct = info.get("heldPercentInstitutions", 0) or 0

        try:
            ih = tk.institutional_holders
        except Exception:
            ih = None
        try:
            mh = tk.mutualfund_holders
        except Exception:
            mh = None

        s = 30

        if inst_pct > 0.8:
            s += 10; result["signals"].append(f"Heavy institutional ownership: {inst_pct:.0%}")
        elif inst_pct > 0.6:
            s += 6; result["signals"].append(f"Strong institutional ownership: {inst_pct:.0%}")
        elif inst_pct > 0.4:
            s += 3; result["signals"].append(f"Moderate institutional ownership: {inst_pct:.0%}")
        elif inst_pct < 0.2:
            s -= 5; result["signals"].append(f"Low institutional ownership: {inst_pct:.0%} — under-discovered")

        if ih is not None and not ih.empty and "pctChange" in ih.columns:
            acc_count = 0
            dist_count = 0
            for _, row in ih.iterrows():
                name = str(row.get("Holder", "")).lower()
                pct_chg = row.get("pctChange", 0) or 0

                for sf in SOVEREIGN_FUNDS:
                    if sf in name:
                        result["sovereign"] = True
                        s += 8
                        result["signals"].append(f"🏛️ Sovereign fund detected: {row['Holder']}")
                        break
                for pf in PENSION_FUNDS:
                    if pf in name:
                        result["pension"] = True
                        s += 5
                        result["signals"].append(f"🏦 Pension fund detected: {row['Holder']}")
                        break

                if pct_chg > 0.02:
                    acc_count += 1
                    result["accumulating"].append(f"{row['Holder']} (+{pct_chg:.1%})")
                elif pct_chg < -0.02:
                    dist_count += 1
                    result["distributing"].append(f"{row['Holder']} ({pct_chg:.1%})")

            if acc_count >= 5:
                s += 15; result["signals"].append(f"Strong accumulation: {acc_count}/10 top holders adding")
                result["net_direction"] = "strong_accumulation"
            elif acc_count >= 3:
                s += 8; result["signals"].append(f"Accumulation detected: {acc_count}/10 top holders adding")
                result["net_direction"] = "accumulation"
            elif dist_count >= 5:
                s -= 10; result["signals"].append(f"Distribution detected: {dist_count}/10 top holders reducing")
                result["net_direction"] = "distribution"

        if mh is not None and not mh.empty and "pctChange" in mh.columns:
            fund_acc = sum(1 for _, r in mh.iterrows() if (r.get("pctChange", 0) or 0) > 0.01)
            if fund_acc >= 6:
                s += 8; result["signals"].append(f"Mutual fund accumulation: {fund_acc}/10 funds adding")
            elif fund_acc >= 3:
                s += 4; result["signals"].append(f"Moderate fund interest: {fund_acc}/10 funds adding")

        result["score"] = max(0, min(100, s))
    except Exception:
        pass
    return result


@st.cache_data(ttl=600)
def intel_options_flow(ticker):
    """Layer 2: Options Flow Intelligence. Detects unusual activity, large premiums, gamma squeeze setup."""
    result = {"score": 30, "signals": [], "unusual_calls": 0, "unusual_puts": 0, "total_call_premium": 0,
              "total_put_premium": 0, "pc_ratio": 1.0, "gamma_squeeze": False, "large_bets": []}
    try:
        tk = yf.Ticker(ticker)
        info = tk.info or {}
        dates = tk.options
        if not dates:
            return result

        price = info.get("currentPrice", info.get("regularMarketPrice", 0)) or 0
        short_pct = info.get("shortPercentOfFloat", 0) or 0
        s = 30
        total_call_oi = 0
        total_put_oi = 0
        total_call_vol = 0
        total_put_vol = 0
        call_premium = 0
        put_premium = 0
        unusual_calls = 0
        unusual_puts = 0
        large_bets = []

        for d in dates[:6]:
            try:
                chain = tk.option_chain(d)
                calls = chain.calls
                puts = chain.puts

                for _, c in calls.iterrows():
                    vol = c.get("volume", 0) or 0
                    oi = c.get("openInterest", 0) or 0
                    lp = c.get("lastPrice", 0) or 0
                    strike = c.get("strike", 0) or 0
                    total_call_oi += oi
                    total_call_vol += vol
                    prem = vol * lp * 100
                    call_premium += prem
                    if vol > 0 and oi > 0 and vol > oi * 2:
                        unusual_calls += 1
                    if prem > 500000 and strike > price * 1.1:
                        large_bets.append(f"CALL {d} ${strike:.0f} — ${prem/1e6:.1f}M premium (OTM)")

                for _, p in puts.iterrows():
                    vol = p.get("volume", 0) or 0
                    oi = p.get("openInterest", 0) or 0
                    lp = p.get("lastPrice", 0) or 0
                    total_put_oi += oi
                    total_put_vol += vol
                    prem = vol * lp * 100
                    put_premium += prem
                    if vol > 0 and oi > 0 and vol > oi * 2:
                        unusual_puts += 1
            except Exception:
                continue

        result["unusual_calls"] = unusual_calls
        result["unusual_puts"] = unusual_puts
        result["total_call_premium"] = call_premium
        result["total_put_premium"] = put_premium
        result["large_bets"] = large_bets[:5]
        pc_ratio = put_premium / max(call_premium, 1)
        result["pc_ratio"] = pc_ratio

        if unusual_calls >= 10:
            s += 18; result["signals"].append(f"Heavy unusual call activity: {unusual_calls} contracts with vol > 2x OI")
        elif unusual_calls >= 5:
            s += 10; result["signals"].append(f"Unusual call activity: {unusual_calls} contracts with vol > 2x OI")
        elif unusual_calls >= 2:
            s += 4; result["signals"].append(f"Minor unusual calls detected: {unusual_calls}")

        if call_premium > 100_000_000:
            s += 12; result["signals"].append(f"Massive call premium: ${call_premium/1e6:.0f}M — institutional conviction")
        elif call_premium > 20_000_000:
            s += 6; result["signals"].append(f"Strong call premium: ${call_premium/1e6:.0f}M")

        if pc_ratio < 0.4:
            s += 10; result["signals"].append(f"Extreme bullish skew — P/C premium ratio: {pc_ratio:.2f}")
        elif pc_ratio < 0.7:
            s += 5; result["signals"].append(f"Bullish options skew — P/C premium ratio: {pc_ratio:.2f}")
        elif pc_ratio > 1.5:
            s -= 8; result["signals"].append(f"Bearish options skew — P/C premium ratio: {pc_ratio:.2f}")

        if large_bets:
            s += 8; result["signals"].append(f"Large OTM call bets detected: {len(large_bets)}")

        if total_call_oi > 0 and total_put_oi > 0:
            oi_ratio = total_put_oi / total_call_oi
            if oi_ratio < 0.5:
                s += 5; result["signals"].append(f"Call OI dominance — ratio: {oi_ratio:.2f}")

        if short_pct > 0.15 and unusual_calls >= 5 and pc_ratio < 0.6:
            result["gamma_squeeze"] = True
            s += 15; result["signals"].append(f"⚡ GAMMA SQUEEZE SETUP — short {short_pct:.0%}, heavy call buying, bullish skew")

        result["score"] = max(0, min(100, s))
    except Exception:
        pass
    return result


@st.cache_data(ttl=600)
def intel_dark_pool(ticker):
    """Layer 3: Dark Pool Activity (approximated from volume patterns). Detects stealth accumulation/distribution."""
    result = {"score": 40, "signals": [], "accumulation_days": 0, "distribution_days": 0, "block_trades": 0, "stealth_pattern": "none"}
    try:
        tk = yf.Ticker(ticker)
        info = tk.info or {}
        hist = tk.history(period="3mo")
        if hist.empty or len(hist) < 20:
            return result

        avg_vol = info.get("averageVolume", 0) or 0
        avg_vol_10 = info.get("averageVolume10days", 0) or 0
        if avg_vol == 0:
            avg_vol = hist["Volume"].mean()

        s = 40
        acc_days = 0
        dist_days = 0
        block_days = 0
        stealth_acc_streak = 0
        max_stealth = 0

        for i in range(max(1, len(hist) - 30), len(hist)):
            row = hist.iloc[i]
            prev = hist.iloc[i - 1]
            vol = row["Volume"]
            close = row["Close"]
            prev_close = prev["Close"]
            pct_chg = (close - prev_close) / max(prev_close, 0.01)
            vol_ratio = vol / max(avg_vol, 1)

            if vol_ratio > 1.3 and abs(pct_chg) < 0.01:
                block_days += 1
            if vol_ratio > 1.2 and pct_chg > 0 and pct_chg < 0.015:
                acc_days += 1
                stealth_acc_streak += 1
                max_stealth = max(max_stealth, stealth_acc_streak)
            elif vol_ratio > 1.2 and pct_chg < 0:
                dist_days += 1
                stealth_acc_streak = 0
            else:
                stealth_acc_streak = 0

        result["accumulation_days"] = acc_days
        result["distribution_days"] = dist_days
        result["block_trades"] = block_days

        if acc_days >= 10:
            s += 20; result["signals"].append(f"Heavy stealth accumulation: {acc_days} days of above-avg volume with contained price moves")
            result["stealth_pattern"] = "heavy_accumulation"
        elif acc_days >= 5:
            s += 10; result["signals"].append(f"Stealth accumulation detected: {acc_days} days")
            result["stealth_pattern"] = "accumulation"

        if dist_days >= 10:
            s -= 15; result["signals"].append(f"Distribution pattern: {dist_days} days of selling pressure")
            result["stealth_pattern"] = "distribution"
        elif dist_days >= 5:
            s -= 5; result["signals"].append(f"Minor distribution: {dist_days} days")

        if block_days >= 8:
            s += 12; result["signals"].append(f"Repeated block trades: {block_days} days of large volume with minimal price impact — institutional footprint")
        elif block_days >= 4:
            s += 6; result["signals"].append(f"Block trade activity: {block_days} days")

        if max_stealth >= 5:
            s += 10; result["signals"].append(f"Sustained stealth streak: {max_stealth} consecutive accumulation days — patient institutional buyer")

        if avg_vol_10 > 0 and avg_vol > 0:
            vol_accel = avg_vol_10 / avg_vol
            if vol_accel > 1.5:
                s += 8; result["signals"].append(f"Volume acceleration: 10-day avg is {vol_accel:.1f}x normal — increasing interest")
            elif vol_accel > 1.2:
                s += 4; result["signals"].append(f"Volume uptick: 10-day avg is {vol_accel:.1f}x normal")

        result["score"] = max(0, min(100, s))
    except Exception:
        pass
    return result


@st.cache_data(ttl=600)
def intel_narrative_momentum(ticker):
    """Layer 4: Narrative Momentum. Scans news for theme alignment and capital narrative signals."""
    result = {"score": 25, "signals": [], "theme_hits": {}, "narrative_rising": False, "news_count": 0, "top_headlines": []}
    try:
        tk = yf.Ticker(ticker)
        info = tk.info or {}
        news = tk.news or []
        summary = (info.get("longBusinessSummary", "") or "").lower()

        s = 25
        theme_hits = {}
        all_text = summary

        headlines = []
        for n in news:
            content = n.get("content", {})
            title = content.get("title", "")
            desc = content.get("summary", content.get("description", ""))
            headlines.append(title)
            all_text += " " + title.lower() + " " + (desc or "").lower()

        result["news_count"] = len(news)
        result["top_headlines"] = headlines[:5]

        for theme_name, theme_data in FUTURE_THEMES.items():
            hits = sum(1 for kw in theme_data["keywords"] if kw in all_text)
            if hits > 0:
                theme_hits[theme_name] = hits

        result["theme_hits"] = theme_hits

        if len(theme_hits) >= 3:
            s += 15; result["signals"].append(f"Multi-theme narrative: aligned with {len(theme_hits)} capital migration themes")
        elif len(theme_hits) >= 2:
            s += 10; result["signals"].append(f"Dual-theme narrative: {', '.join(theme_hits.keys())}")
        elif len(theme_hits) == 1:
            s += 5; result["signals"].append(f"Single theme: {list(theme_hits.keys())[0]}")

        total_hits = sum(theme_hits.values())
        if total_hits >= 10:
            s += 12; result["signals"].append(f"Strong narrative density: {total_hits} theme keyword matches")
            result["narrative_rising"] = True
        elif total_hits >= 5:
            s += 6; result["signals"].append(f"Moderate narrative presence: {total_hits} theme keyword matches")
            result["narrative_rising"] = True
        elif total_hits >= 2:
            s += 3

        capital_keywords = ["institutional","fund","acquisition","merger","ipo","capital","investment","billion","partnership","contract","government","defense contract","ai deal","data center"]
        cap_hits = sum(1 for kw in capital_keywords if kw in all_text)
        if cap_hits >= 5:
            s += 12; result["signals"].append(f"Capital narrative strong: {cap_hits} capital flow keywords in news/filings")
        elif cap_hits >= 3:
            s += 6; result["signals"].append(f"Capital narrative present: {cap_hits} capital keywords")

        if len(news) >= 8:
            s += 5; result["signals"].append(f"High news velocity: {len(news)} recent articles — narrative accelerating")
            result["narrative_rising"] = True
        elif len(news) >= 4:
            s += 2

        result["score"] = max(0, min(100, s))
    except Exception:
        pass
    return result


@st.cache_data(ttl=600)
def intel_alternative_data(ticker):
    """Layer 5: Alternative Data (proxied from fundamentals). Employee growth, revenue accel, R&D, FCF."""
    result = {"score": 30, "signals": [], "hiring_signal": "neutral", "revenue_accel": False, "innovation_score": 0}
    try:
        tk = yf.Ticker(ticker)
        info = tk.info or {}

        s = 30

        employees = info.get("fullTimeEmployees", 0) or 0
        rev_growth = info.get("revenueGrowth", 0) or 0
        earn_growth = info.get("earningsGrowth", 0) or 0
        gross_margin = info.get("grossMargins", 0) or 0
        op_margin = info.get("operatingMargins", 0) or 0
        roe = info.get("returnOnEquity", 0) or 0
        fcf = info.get("freeCashflow", 0) or 0
        revenue = info.get("totalRevenue", 0) or 0
        rd = info.get("researchDevelopment") or 0
        mcap = info.get("marketCap", 0) or 0

        if rev_growth > 0.5:
            s += 15; result["signals"].append(f"Revenue acceleration: {rev_growth:.0%} YoY — hypergrowth territory")
            result["revenue_accel"] = True
        elif rev_growth > 0.25:
            s += 10; result["signals"].append(f"Strong revenue growth: {rev_growth:.0%} YoY")
            result["revenue_accel"] = True
        elif rev_growth > 0.1:
            s += 5; result["signals"].append(f"Healthy revenue growth: {rev_growth:.0%} YoY")
        elif rev_growth < 0:
            s -= 5; result["signals"].append(f"Revenue declining: {rev_growth:.0%} YoY")

        if earn_growth > 1.0:
            s += 8; result["signals"].append(f"Earnings explosion: {earn_growth:.0%} growth — operating leverage")
        elif earn_growth > 0.3:
            s += 4; result["signals"].append(f"Strong earnings growth: {earn_growth:.0%}")

        if op_margin > gross_margin * 0.7 and gross_margin > 0.5:
            s += 5; result["signals"].append(f"Operating leverage: {op_margin:.0%} op margin on {gross_margin:.0%} gross — efficient scaling")

        if employees > 50000:
            result["hiring_signal"] = "large_employer"
            result["signals"].append(f"Large employer: {employees:,} — established scale")
        elif employees > 10000:
            result["hiring_signal"] = "scaling"
            s += 3; result["signals"].append(f"Scaling workforce: {employees:,} employees")
        elif employees > 0 and employees < 1000:
            result["hiring_signal"] = "early_stage"
            result["signals"].append(f"Early stage: {employees:,} employees — high growth potential or high risk")

        if rd > 0 and revenue > 0:
            rd_pct = rd / revenue
            if rd_pct > 0.3:
                s += 8; result["signals"].append(f"Heavy R&D investment: {rd_pct:.0%} of revenue — innovation-driven")
                result["innovation_score"] = 90
            elif rd_pct > 0.15:
                s += 4; result["signals"].append(f"Strong R&D: {rd_pct:.0%} of revenue")
                result["innovation_score"] = 70
            elif rd_pct > 0.05:
                result["innovation_score"] = 50

        if fcf > 0 and mcap > 0:
            fcf_yield = fcf / mcap
            if fcf_yield > 0.08:
                s += 6; result["signals"].append(f"Strong FCF yield: {fcf_yield:.1%} — self-funding growth")
            elif fcf_yield > 0.04:
                s += 3; result["signals"].append(f"Healthy FCF yield: {fcf_yield:.1%}")
        elif fcf < 0:
            s -= 3; result["signals"].append("Negative FCF — burning cash")

        if roe > 0.5:
            s += 5; result["signals"].append(f"Exceptional ROE: {roe:.0%} — capital efficiency machine")
        elif roe > 0.2:
            s += 3

        result["score"] = max(0, min(100, s))
    except Exception:
        pass
    return result


def intel_social_acceleration(ticker):
    """Layer 6: Social Acceleration. Wraps existing Reddit scanner for narrative velocity."""
    result = {"score": 30, "signals": [], "velocity": "none", "mention_count": 0, "sentiment": "neutral"}
    try:
        social = scan_reddit(ticker)
        if not social["has_data"]:
            result["signals"].append("No social signal detected — under the radar (potential opportunity)")
            return result

        s = 30
        mentions = social["total_mentions"]
        result["mention_count"] = mentions
        buzz = social["buzz_score"]
        sentiment_s = social["sentiment_score"]

        if mentions >= 30:
            s += 10; result["signals"].append(f"High social velocity: {mentions} mentions across Reddit")
            result["velocity"] = "high"
        elif mentions >= 10:
            s += 5; result["signals"].append(f"Moderate social presence: {mentions} mentions")
            result["velocity"] = "moderate"
        elif mentions >= 3:
            s += 2; result["signals"].append(f"Emerging social interest: {mentions} mentions")
            result["velocity"] = "emerging"
        else:
            result["signals"].append(f"Minimal social presence: {mentions} mentions — still under the radar")

        if sentiment_s >= 75:
            s += 10; result["signals"].append(f"Strong bullish sentiment: {sentiment_s}/100")
            result["sentiment"] = "bullish"
        elif sentiment_s >= 60:
            s += 5; result["signals"].append(f"Lean bullish sentiment: {sentiment_s}/100")
            result["sentiment"] = "lean_bullish"
        elif sentiment_s <= 30:
            s -= 5; result["signals"].append(f"Bearish social sentiment: {sentiment_s}/100")
            result["sentiment"] = "bearish"

        if buzz >= 70:
            s += 8; result["signals"].append(f"Buzz score: {buzz}/100 — narrative gaining traction")
        elif buzz >= 40:
            s += 3

        if social.get("bullish", 0) > social.get("bearish", 0) * 3 and mentions >= 5:
            s += 5; result["signals"].append("Overwhelming bullish ratio — crowd conviction building")

        result["score"] = max(0, min(100, s))
    except Exception:
        pass
    return result


def compute_capital_intelligence(ticker, info=None, hist=None, scores=None, cm=None, hunter=None):
    """Master orchestrator: computes all 6 layers + weighted composite + hunt trigger."""
    inst = intel_institutional_flow(ticker)
    opts = intel_options_flow(ticker)
    dark = intel_dark_pool(ticker)
    narr = intel_narrative_momentum(ticker)
    alt = intel_alternative_data(ticker)
    social = intel_social_acceleration(ticker)

    weighted = (
        inst["score"] * 0.30 +
        alt["score"] * 0.20 +
        opts["score"] * 0.15 +
        (alt["score"] * 0.5 + (scores.get("revenue_quality", 50) if scores else 50) * 0.5) * 0.15 +
        narr["score"] * 0.10 +
        social["score"] * 0.10
    )

    hunt_candidate = False
    hunt_reasons_for = []
    hunt_reasons_against = []

    cap_score = hunter.get("cap", {}).get("score", 0) if hunter else 0
    force_score = hunter.get("force", {}).get("score", 0) if hunter else 0
    crowding_score = hunter.get("crowding", {}).get("score", 0) if hunter else 100
    timing_score = hunter.get("timing", {}).get("score", 0) if hunter else 0

    if (cap_score > 90 and force_score > 85 and dark["score"] > 80
            and narr["narrative_rising"] and crowding_score < 60 and timing_score > 75):
        hunt_candidate = True

    if inst["net_direction"] in ("accumulation", "strong_accumulation"):
        hunt_reasons_for.append(f"Institutional accumulation — {len(inst['accumulating'])} top holders adding positions")
    if inst["sovereign"]:
        hunt_reasons_for.append("Sovereign wealth fund participation detected — long-duration capital commitment")
    if opts["gamma_squeeze"]:
        hunt_reasons_for.append("Gamma squeeze setup — high short interest + heavy call buying creates forced buying pressure")
    if opts["unusual_calls"] >= 5:
        hunt_reasons_for.append(f"Unusual options activity — {opts['unusual_calls']} call contracts with volume exceeding open interest by 2x+")
    if dark["stealth_pattern"] in ("accumulation", "heavy_accumulation"):
        hunt_reasons_for.append(f"Dark pool accumulation pattern — {dark['accumulation_days']} days of above-average volume with contained price moves")
    if narr["narrative_rising"]:
        themes = ", ".join(narr["theme_hits"].keys()) if narr["theme_hits"] else "capital flow"
        hunt_reasons_for.append(f"Narrative momentum rising — aligned with {themes} themes")
    if alt.get("revenue_accel"):
        hunt_reasons_for.append("Revenue acceleration — fundamental tailwind supporting capital attraction")
    if social["velocity"] in ("high", "moderate") and social["sentiment"] in ("bullish", "lean_bullish"):
        hunt_reasons_for.append("Social sentiment accelerating bullish — crowd conviction building without crowding")
    if cap_score > 90:
        hunt_reasons_for.append(f"CAP score {cap_score:.0f} — very high probability of attracting future capital")
    if force_score > 85:
        hunt_reasons_for.append(f"Force score {force_score:.0f} — structural catalysts in place")

    if inst["net_direction"] == "distribution":
        hunt_reasons_against.append(f"Institutional distribution — {len(inst['distributing'])} top holders reducing positions")
    if opts["pc_ratio"] > 1.3:
        hunt_reasons_against.append(f"Bearish options skew — put/call premium ratio {opts['pc_ratio']:.2f}")
    if dark["stealth_pattern"] == "distribution":
        hunt_reasons_against.append(f"Dark pool distribution — {dark['distribution_days']} days of selling pressure")
    if crowding_score >= 80:
        hunt_reasons_against.append(f"Crowding index {crowding_score:.0f} — already consensus, limited upside surprise")
    if not narr["narrative_rising"] and not narr["theme_hits"]:
        hunt_reasons_against.append("No narrative momentum — not aligned with major capital migration themes")
    if alt.get("revenue_accel") is False and (info or {}).get("revenueGrowth", 0) and (info.get("revenueGrowth", 0) or 0) < 0:
        hunt_reasons_against.append("Revenue declining — fundamental headwind")
    if social["sentiment"] == "bearish":
        hunt_reasons_against.append("Bearish social sentiment — crowd turning negative")
    if timing_score < 50:
        hunt_reasons_against.append(f"Timing score {timing_score:.0f} — momentum not yet aligned")
    if opts["unusual_puts"] > opts["unusual_calls"] and opts["unusual_puts"] >= 5:
        hunt_reasons_against.append(f"Unusual put activity — {opts['unusual_puts']} contracts with heavy volume")
    if cap_score < 70:
        hunt_reasons_against.append(f"CAP score {cap_score:.0f} — low probability of near-term capital attraction")

    while len(hunt_reasons_for) < 5:
        hunt_reasons_for.append("—")
    while len(hunt_reasons_against) < 5:
        hunt_reasons_against.append("—")

    return {
        "institutional": inst,
        "options": opts,
        "dark_pool": dark,
        "narrative": narr,
        "alternative": alt,
        "social": social,
        "composite_score": round(weighted, 1),
        "hunt_candidate": hunt_candidate,
        "reasons_for": hunt_reasons_for[:5],
        "reasons_against": hunt_reasons_against[:5],
    }


def render_capital_intelligence(ci, ticker, hunter=None):
    """Render the full Capital Flow Intelligence dashboard."""
    comp = ci["composite_score"]
    is_hunt = ci["hunt_candidate"]

    if is_hunt:
        badge_html = '<span style="background:linear-gradient(135deg,#FF6B00,#FF9800);padding:6px 18px;border-radius:20px;font-size:14px;font-weight:800;letter-spacing:1px;color:#000">🔥 CFIS HUNT CANDIDATE</span>'
    elif comp >= 70:
        badge_html = '<span style="background:#1B5E20;padding:5px 14px;border-radius:16px;font-size:12px;font-weight:700;color:#4CAF50;letter-spacing:1px">HIGH SIGNAL</span>'
    elif comp >= 50:
        badge_html = '<span style="background:#33291a;padding:5px 14px;border-radius:16px;font-size:12px;font-weight:700;color:#FFC107;letter-spacing:1px">MODERATE</span>'
    else:
        badge_html = '<span style="background:#2a1a1a;padding:5px 14px;border-radius:16px;font-size:12px;font-weight:700;color:#ef5350;letter-spacing:1px">LOW SIGNAL</span>'

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d1117,#151b23);border:1px solid #21262d;border-radius:16px;padding:28px;margin:20px 0">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px">
            <div>
                <div style="font-size:10px;color:#8b949e;letter-spacing:3px;font-weight:700">CAPITAL FLOW INTELLIGENCE</div>
                <div style="font-size:28px;font-weight:800;color:#e6edf3;margin-top:4px">{ticker}</div>
            </div>
            <div style="text-align:right">
                <div style="font-size:36px;font-weight:900;color:{'#FF9800' if is_hunt else '#4CAF50' if comp>=70 else '#FFC107' if comp>=50 else '#ef5350'}">{comp:.0f}</div>
                <div style="margin-top:4px">{badge_html}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    layers = [
        ("INSTITUTIONAL FLOW", ci["institutional"], "30%", "#4FC3F7"),
        ("OPTIONS FLOW", ci["options"], "15%", "#AB47BC"),
        ("DARK POOL ACTIVITY", ci["dark_pool"], "15%*", "#FF7043"),
        ("NARRATIVE MOMENTUM", ci["narrative"], "10%", "#66BB6A"),
        ("ALTERNATIVE DATA", ci["alternative"], "20%", "#FFA726"),
        ("SOCIAL ACCELERATION", ci["social"], "10%", "#EC407A"),
    ]

    cols = st.columns(3)
    for idx, (name, data, weight, color) in enumerate(layers):
        sc = data["score"]
        with cols[idx % 3]:
            st.markdown(f"""
            <div style="background:#0d1117;border:1px solid #21262d;border-radius:12px;padding:16px;margin-bottom:12px;min-height:100px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div style="font-size:9px;color:{color};letter-spacing:2px;font-weight:700">{name}</div>
                    <div style="font-size:9px;color:#8b949e">WT: {weight}</div>
                </div>
                <div style="font-size:28px;font-weight:900;color:{color};margin:6px 0">{sc}</div>
                <div style="background:#21262d;border-radius:4px;height:4px;margin-top:6px">
                    <div style="background:{color};height:4px;border-radius:4px;width:{min(sc,100)}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    for name, data, weight, color in layers:
        if data["signals"]:
            with st.expander(f"{name} — Intelligence Detail"):
                for sig in data["signals"]:
                    st.markdown(f"<div style='color:#c9d1d9;font-size:13px;padding:4px 0;border-bottom:1px solid #21262d'>• {sig}</div>", unsafe_allow_html=True)

                if name == "INSTITUTIONAL FLOW":
                    if data.get("accumulating"):
                        st.markdown("<div style='color:#4CAF50;font-size:11px;margin-top:8px;font-weight:700'>ACCUMULATING:</div>", unsafe_allow_html=True)
                        for a in data["accumulating"][:5]:
                            st.markdown(f"<div style='color:#81C784;font-size:12px;padding:2px 0'>  ▲ {a}</div>", unsafe_allow_html=True)
                    if data.get("distributing"):
                        st.markdown("<div style='color:#ef5350;font-size:11px;margin-top:8px;font-weight:700'>DISTRIBUTING:</div>", unsafe_allow_html=True)
                        for d in data["distributing"][:5]:
                            st.markdown(f"<div style='color:#e57373;font-size:12px;padding:2px 0'>  ▼ {d}</div>", unsafe_allow_html=True)

                if name == "OPTIONS FLOW":
                    if data.get("large_bets"):
                        st.markdown("<div style='color:#FFC107;font-size:11px;margin-top:8px;font-weight:700'>LARGE BETS:</div>", unsafe_allow_html=True)
                        for b in data["large_bets"]:
                            st.markdown(f"<div style='color:#FFD54F;font-size:12px;padding:2px 0'>  💰 {b}</div>", unsafe_allow_html=True)

                if name == "NARRATIVE MOMENTUM":
                    if data.get("top_headlines"):
                        st.markdown("<div style='color:#66BB6A;font-size:11px;margin-top:8px;font-weight:700'>RECENT HEADLINES:</div>", unsafe_allow_html=True)
                        for h in data["top_headlines"][:3]:
                            st.markdown(f"<div style='color:#A5D6A7;font-size:12px;padding:2px 0'>  📰 {h}</div>", unsafe_allow_html=True)

    if is_hunt or comp >= 60:
        for_color = "#4CAF50"
        against_color = "#ef5350"
        st.markdown(f"""
        <div style="background:#0d1117;border:{'2px solid #FF9800' if is_hunt else '1px solid #21262d'};border-radius:16px;padding:24px;margin:20px 0">
            <div style="text-align:center;margin-bottom:16px">
                <div style="font-size:11px;color:{'#FF9800' if is_hunt else '#8b949e'};letter-spacing:3px;font-weight:700">{'🔥 HUNT TRIGGER ACTIVATED' if is_hunt else 'CAPITAL FLOW ASSESSMENT'}</div>
            </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div style='font-size:10px;color:{for_color};letter-spacing:2px;font-weight:700;margin-bottom:10px'>TOP 5 — WHY CAPITAL MAY FLOW IN</div>", unsafe_allow_html=True)
            for i, r in enumerate(ci["reasons_for"][:5], 1):
                st.markdown(f"<div style='color:#c9d1d9;font-size:12px;padding:6px 0;border-bottom:1px solid #21262d'><span style='color:{for_color};font-weight:700'>{i}.</span> {r}</div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div style='font-size:10px;color:{against_color};letter-spacing:2px;font-weight:700;margin-bottom:10px'>TOP 5 — WHY CAPITAL MAY AVOID</div>", unsafe_allow_html=True)
            for i, r in enumerate(ci["reasons_against"][:5], 1):
                st.markdown(f"<div style='color:#c9d1d9;font-size:12px;padding:6px 0;border-bottom:1px solid #21262d'><span style='color:{against_color};font-weight:700'>{i}.</span> {r}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SMART MONEY PRESSURE MAP™
# Evidence-based institutional pressure detection
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def compute_smart_money_pressure(ticker):
    """Compute Smart Money Pressure Map: 7 evidence-based pressure components."""
    try:
        tk = yf.Ticker(ticker)
        info = tk.info or {}
        hist = tk.history(period="6mo")
    except Exception:
        return {"score": 50, "signal": "Neutral", "evidence": "Insufficient data", "risk": "Cannot assess", "components": {}}

    if hist.empty:
        return {"score": 50, "signal": "Neutral", "evidence": "No price history available", "risk": "Cannot assess", "components": {}}

    enriched = fetch_enriched_data(ticker)
    signals = []
    components = {}

    # 1. DARK POOL ACTIVITY (20%)
    dp_score = 50
    dp_signals = []
    avg_vol = safe(info, "averageVolume", default=0) or 0
    avg10 = safe(info, "averageVolume10days", default=0) or 0
    if avg_vol > 0 and len(hist) >= 20:
        recent_vol = hist["Volume"].iloc[-5:].mean()
        hist_vol = hist["Volume"].iloc[-60:-20].mean() if len(hist) >= 60 else hist["Volume"].mean()
        vol_ratio = recent_vol / hist_vol if hist_vol > 0 else 1

        price_chg_5d = (hist["Close"].iloc[-1] - hist["Close"].iloc[-5]) / hist["Close"].iloc[-5] * 100 if len(hist) >= 5 else 0
        price_chg_20d = (hist["Close"].iloc[-1] - hist["Close"].iloc[-20]) / hist["Close"].iloc[-20] * 100 if len(hist) >= 20 else 0

        high_low_range = hist["High"].iloc[-20:] - hist["Low"].iloc[-20:]
        avg_range = high_low_range.mean()
        close_range = abs(hist["Close"].iloc[-20:] - hist["Open"].iloc[-20:]).mean()
        absorption = 1 - (close_range / avg_range) if avg_range > 0 else 0.5

        if vol_ratio > 1.5 and abs(price_chg_5d) < 2:
            dp_score = 80
            dp_signals.append("High volume with muted price action — possible stealth accumulation/distribution")
        elif vol_ratio > 1.8 and price_chg_5d > 3:
            dp_score = 75
            dp_signals.append("Elevated volume + rising price — institutional accumulation pattern")
        elif vol_ratio > 1.8 and price_chg_5d < -3:
            dp_score = 70
            dp_signals.append("Elevated volume + falling price — possible institutional distribution")
        elif vol_ratio > 1.3:
            dp_score = 60
            dp_signals.append(f"Volume {vol_ratio:.1f}x above baseline — above-normal activity")

        if absorption > 0.6:
            dp_score += 10
            dp_signals.append(f"High price absorption ({absorption:.0%}) — large orders absorbing selling pressure")

        large_vol_days = sum(1 for v in hist["Volume"].iloc[-20:] if v > avg_vol * 2)
        if large_vol_days >= 3:
            dp_score += 8
            dp_signals.append(f"{large_vol_days} block trade days in 20 sessions")
    components["dark_pool"] = {"score": min(100, dp_score), "signals": dp_signals, "weight": 0.20}

    # 2. OFF-EXCHANGE VOLUME (15%)
    oe_score = 50
    oe_signals = []
    if avg_vol > 0 and avg10 > 0:
        vol_trend_10 = avg10 / avg_vol if avg_vol else 1
        if len(hist) >= 30:
            vol_30d = hist["Volume"].iloc[-30:].mean()
            vol_prior = hist["Volume"].iloc[-60:-30].mean() if len(hist) >= 60 else avg_vol
            vol_trend_30 = vol_30d / vol_prior if vol_prior > 0 else 1
        else:
            vol_trend_30 = 1

        if vol_trend_10 > 1.5 and vol_trend_30 > 1.3:
            oe_score = 78
            oe_signals.append(f"Rising volume trend: 10d={vol_trend_10:.1f}x, 30d={vol_trend_30:.1f}x — sustained institutional interest")
        elif vol_trend_10 > 1.3:
            oe_score = 65
            oe_signals.append(f"10-day volume {vol_trend_10:.1f}x above average — short-term activity spike")
        elif vol_trend_10 < 0.7:
            oe_score = 35
            oe_signals.append("Volume declining — institutional interest may be waning")

        if len(hist) >= 10:
            vol_std = hist["Volume"].iloc[-20:].std()
            vol_mean = hist["Volume"].iloc[-20:].mean()
            if vol_mean > 0 and vol_std / vol_mean > 0.8:
                oe_score += 8
                oe_signals.append("High volume volatility — sporadic large orders detected")
    components["off_exchange"] = {"score": min(100, oe_score), "signals": oe_signals, "weight": 0.15}

    # 3. OPTIONS FLOW (20%)
    of_score = 50
    of_signals = []
    opt_dates = []
    try:
        opt_dates = list(tk.options)
        if opt_dates:
            chain = tk.option_chain(opt_dates[0])
            calls = chain.calls
            puts = chain.puts

            total_call_vol = calls["volume"].sum() if "volume" in calls.columns else 0
            total_put_vol = puts["volume"].sum() if "volume" in puts.columns else 0
            total_call_oi = calls["openInterest"].sum() if "openInterest" in calls.columns else 0
            total_put_oi = puts["openInterest"].sum() if "openInterest" in puts.columns else 0

            pc_vol = total_put_vol / total_call_vol if total_call_vol > 0 else 1
            pc_oi = total_put_oi / total_call_oi if total_call_oi > 0 else 1

            price = safe(info, "currentPrice", "regularMarketPrice", default=0) or 0
            if price > 0:
                otm_calls = calls[calls["strike"] > price * 1.10] if not calls.empty else calls
                otm_call_vol = otm_calls["volume"].sum() if not otm_calls.empty and "volume" in otm_calls.columns else 0
                if otm_call_vol > total_call_vol * 0.3 and total_call_vol > 100:
                    of_score += 15
                    of_signals.append(f"Heavy OTM call volume ({otm_call_vol:.0f}) — bullish directional bets")

            if pc_vol < 0.5 and total_call_vol > 500:
                of_score = 80
                of_signals.append(f"Put/call volume ratio {pc_vol:.2f} — strong bullish options pressure")
            elif pc_vol < 0.7:
                of_score = 65
                of_signals.append(f"Put/call ratio {pc_vol:.2f} — moderately bullish positioning")
            elif pc_vol > 1.5:
                of_score = 30
                of_signals.append(f"Put/call ratio {pc_vol:.2f} — heavy put buying, bearish pressure")
            elif pc_vol > 1.0:
                of_score = 40
                of_signals.append(f"Put/call ratio {pc_vol:.2f} — slight bearish tilt")

            if total_call_vol > 5000:
                of_score += 5
                of_signals.append(f"High call volume ({total_call_vol:,.0f}) — active options market")

            if len(opt_dates) >= 2:
                near_exp = opt_dates[0]
                of_signals.append(f"Near-term expiry concentration: {near_exp}")
    except Exception:
        pass
    components["options_flow"] = {"score": min(100, of_score), "signals": of_signals, "weight": 0.20}

    # 4. GAMMA / DEALER POSITIONING (15%)
    gd_score = 50
    gd_signals = []
    try:
        if opt_dates and len(opt_dates) > 0:
            chain = tk.option_chain(opt_dates[0])
            calls = chain.calls
            puts = chain.puts
            price = safe(info, "currentPrice", "regularMarketPrice", default=0) or 0

            if price > 0 and not calls.empty and not puts.empty:
                call_oi = calls[["strike", "openInterest"]].copy() if "openInterest" in calls.columns else pd.DataFrame()
                put_oi = puts[["strike", "openInterest"]].copy() if "openInterest" in puts.columns else pd.DataFrame()

                if not call_oi.empty:
                    call_wall_idx = call_oi["openInterest"].idxmax()
                    call_wall = float(call_oi.loc[call_wall_idx, "strike"])
                    gd_signals.append(f"Call wall at ${call_wall:.0f}")

                    if price > call_wall * 0.97:
                        gd_score += 15
                        gd_signals.append("Price near call wall — breakout could trigger dealer squeeze")

                if not put_oi.empty:
                    put_wall_idx = put_oi["openInterest"].idxmax()
                    put_wall = float(put_oi.loc[put_wall_idx, "strike"])
                    gd_signals.append(f"Put wall at ${put_wall:.0f}")

                    if price < put_wall * 1.03:
                        gd_score -= 10
                        gd_signals.append("Price near put wall — downside acceleration risk")

                total_call_oi = call_oi["openInterest"].sum() if not call_oi.empty else 0
                total_put_oi = put_oi["openInterest"].sum() if not put_oi.empty else 0

                if total_call_oi > total_put_oi * 1.5:
                    gd_score += 10
                    gd_signals.append("Positive gamma exposure — price likely to be stable/drift higher")
                elif total_put_oi > total_call_oi * 1.5:
                    gd_score -= 5
                    gd_signals.append("Negative gamma — price may move violently")

                if not calls.empty and "lastPrice" in calls.columns and "strike" in calls.columns:
                    weighted_prices = (calls["openInterest"] * calls["strike"]).sum()
                    total_oi = calls["openInterest"].sum() + puts["openInterest"].sum()
                    if total_oi > 0:
                        all_weighted = (calls["openInterest"] * calls["strike"]).sum() + (puts["openInterest"] * puts["strike"]).sum()
                        max_pain = all_weighted / total_oi
                        gd_signals.append(f"Max pain estimate: ${max_pain:.0f}")
    except Exception:
        pass
    components["gamma_dealer"] = {"score": max(0, min(100, gd_score)), "signals": gd_signals, "weight": 0.15}

    # 5. SHORT INTEREST / BORROW PRESSURE (15%)
    si_score = 50
    si_signals = []
    sf_enriched = enriched.get("short_float")
    sf_raw = safe(info, "shortPercentOfFloat", default=None)
    sf = sf_enriched if sf_enriched is not None else sf_raw

    if sf is not None:
        si_signals.append(f"Short float: {sf*100:.1f}%")
        if sf > 0.20:
            si_score = 80
            si_signals.append("Very high short interest — squeeze risk elevated")
        elif sf > 0.10:
            si_score = 65
            si_signals.append("Elevated short interest — potential squeeze setup")
        elif sf < 0.02:
            si_score = 40
            si_signals.append("Low short interest — no squeeze catalyst")

        short_ratio = safe(info, "shortRatio", default=None)
        if short_ratio is not None:
            si_signals.append(f"Days to cover: {short_ratio:.1f}")
            if short_ratio > 5:
                si_score += 15
                si_signals.append("Days-to-cover >5 — shorts are trapped if price rises")
            elif short_ratio > 3:
                si_score += 8

        price_chg = 0
        if len(hist) >= 20:
            price_chg = (hist["Close"].iloc[-1] - hist["Close"].iloc[-20]) / hist["Close"].iloc[-20] * 100
        if sf > 0.15 and price_chg > 10:
            si_score += 10
            si_signals.append(f"Short squeeze in progress: {sf*100:.0f}% short + price up {price_chg:.0f}% in 20d")
    else:
        si_signals.append("Short interest data unavailable")
    components["short_interest"] = {"score": max(0, min(100, si_score)), "signals": si_signals, "weight": 0.15}

    # 6. ETF FLOW (10%)
    ef_score = 50
    ef_signals = []
    mc = safe(info, "marketCap", default=0) or 0
    sector = (info.get("sector", "") or "")
    if mc > 100e9:
        ef_score = 65
        ef_signals.append(f"Mega-cap ${mc/1e9:.0f}B — held by many ETFs, receives passive inflow")
    elif mc > 20e9:
        ef_score = 58
        ef_signals.append(f"Large-cap ${mc/1e9:.0f}B — included in major indexes")
    elif mc < 2e9:
        ef_score = 40
        ef_signals.append(f"Small-cap ${mc/1e9:.1f}B — limited ETF exposure")

    rg = safe(info, "revenueGrowth", default=0) or 0
    if rg > 0.30 and mc > 10e9:
        ef_score += 10
        ef_signals.append(f"High growth {rg*100:.0f}% + mid/large cap — likely receiving thematic ETF inflow")

    if sector in ("Technology", "Energy"):
        ef_score += 5
        ef_signals.append(f"Sector ({sector}) is seeing active ETF rotation")
    components["etf_flow"] = {"score": max(0, min(100, ef_score)), "signals": ef_signals, "weight": 0.10}

    # 7. FAILS-TO-DELIVER / SETTLEMENT (5%)
    ftd_score = 50
    ftd_signals = []
    if len(hist) >= 10:
        close_prices = hist["Close"].iloc[-10:]
        volumes = hist["Volume"].iloc[-10:]
        high_vol_low_move = 0
        for i in range(1, len(close_prices)):
            daily_ret = abs(close_prices.iloc[i] - close_prices.iloc[i-1]) / close_prices.iloc[i-1]
            if volumes.iloc[i] > avg_vol * 2 and daily_ret < 0.01:
                high_vol_low_move += 1
        if high_vol_low_move >= 3:
            ftd_score = 70
            ftd_signals.append(f"{high_vol_low_move} settlement stress signals in 10 days — high volume with minimal price impact")
        elif high_vol_low_move >= 1:
            ftd_score = 55
            ftd_signals.append("Some settlement anomaly detected")
        else:
            ftd_signals.append("No FTD pressure signals detected")
    components["ftd"] = {"score": max(0, min(100, ftd_score)), "signals": ftd_signals, "weight": 0.05}

    # COMPOSITE SCORE
    composite = sum(c["score"] * c["weight"] for c in components.values())
    composite = max(0, min(100, round(composite)))

    # SIGNAL DETERMINATION
    dp = components["dark_pool"]["score"]
    of = components["options_flow"]["score"]
    si = components["short_interest"]["score"]
    gd = components["gamma_dealer"]["score"]

    if composite >= 75 and dp >= 70 and of >= 65:
        signal = "Strong Accumulation"
    elif composite >= 65 and of >= 60:
        signal = "Accumulation"
    elif si >= 75 and of >= 60 and dp >= 65:
        signal = "Squeeze Setup"
    elif composite <= 35:
        signal = "Distribution"
    elif si >= 70 and composite <= 45:
        signal = "Short Pressure"
    elif composite <= 30 and dp <= 40:
        signal = "Danger Zone"
    else:
        signal = "Neutral"

    # EVIDENCE SENTENCE
    evidence_parts = []
    if dp >= 65:
        evidence_parts.append("dark pool volume is elevated")
    if of >= 65:
        evidence_parts.append("call premium is rising")
    if si >= 65:
        evidence_parts.append("short interest remains high")
    if gd >= 65:
        evidence_parts.append("positive gamma supports price stability")
    if ef_score >= 60:
        evidence_parts.append("ETF inflow is supportive")
    if dp <= 40:
        evidence_parts.append("institutional volume is declining")
    if of <= 35:
        evidence_parts.append("options flow is bearish")

    if evidence_parts:
        evidence = ", ".join(evidence_parts[:3]).capitalize()
        if signal in ("Squeeze Setup",):
            evidence += ", creating a possible squeeze setup."
        elif signal in ("Strong Accumulation", "Accumulation"):
            evidence += ", indicating institutional accumulation."
        elif signal in ("Distribution", "Danger Zone"):
            evidence += ", suggesting distribution pressure."
        else:
            evidence += "."
    else:
        evidence = "Mixed signals across pressure indicators."

    # RISK WARNING
    risk_parts = []
    if signal in ("Squeeze Setup",) and of < 70:
        risk_parts.append("Signal is not confirmed unless price breaks resistance with volume")
    elif signal in ("Strong Accumulation",) and si >= 60:
        risk_parts.append("Short sellers may defend aggressively — watch for failed breakouts")
    elif signal in ("Distribution",):
        risk_parts.append("Distribution may accelerate on any negative catalyst")
    elif signal == "Neutral":
        risk_parts.append("No clear directional pressure — wait for confirmation")
    else:
        risk_parts.append("Pressure signals should be confirmed by price action before acting")
    risk = risk_parts[0] if risk_parts else "Monitor for confirmation."

    return {
        "score": composite,
        "signal": signal,
        "evidence": evidence,
        "risk": risk,
        "components": components,
        "ticker": ticker,
    }


def render_smart_money_pressure(smp, ticker):
    """Render the Smart Money Pressure Map display."""
    score = smp["score"]
    signal = smp["signal"]

    signal_colors = {
        "Strong Accumulation": "#4CAF50",
        "Accumulation": "#66BB6A",
        "Squeeze Setup": "#FF9800",
        "Neutral": "#78909C",
        "Distribution": "#f44336",
        "Short Pressure": "#AB47BC",
        "Danger Zone": "#D32F2F",
    }
    sc = signal_colors.get(signal, "#78909C")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d1117,#151b23);border:1px solid #21262d;border-radius:16px;padding:24px;margin:16px 0">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
            <div>
                <div style="font-size:10px;color:#8b949e;letter-spacing:3px;font-weight:700">SMART MONEY PRESSURE MAP</div>
                <div style="font-size:24px;font-weight:800;color:#e6edf3;margin-top:4px">{ticker}</div>
            </div>
            <div style="text-align:right">
                <div style="font-size:36px;font-weight:900;color:{sc}">{score}</div>
                <div style="background:{sc}22;color:{sc};padding:4px 14px;border-radius:12px;font-size:12px;font-weight:700;display:inline-block">{signal.upper()}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    comp_meta = [
        ("DARK POOL", "dark_pool", "#FF7043"),
        ("OFF-EXCHANGE", "off_exchange", "#FF9800"),
        ("OPTIONS FLOW", "options_flow", "#AB47BC"),
        ("GAMMA / DEALER", "gamma_dealer", "#4FC3F7"),
        ("SHORT INTEREST", "short_interest", "#f44336"),
        ("ETF FLOW", "etf_flow", "#66BB6A"),
        ("FTD / SETTLEMENT", "ftd", "#FFC107"),
    ]

    cols = st.columns(4)
    for idx, (label, key, color) in enumerate(comp_meta[:4]):
        c = smp["components"].get(key, {})
        cs = c.get("score", 50)
        wt = f"{c.get('weight', 0)*100:.0f}%"
        with cols[idx]:
            st.markdown(f"""
            <div style="background:#0d1117;border:1px solid #21262d;border-radius:10px;padding:12px;margin-bottom:8px;min-height:80px">
                <div style="font-size:8px;color:{color};letter-spacing:1.5px;font-weight:700">{label}</div>
                <div style="font-size:9px;color:#8b949e">WT: {wt}</div>
                <div style="font-size:24px;font-weight:900;color:{color};margin:4px 0">{cs}</div>
                <div style="background:#21262d;border-radius:3px;height:3px;margin-top:4px">
                    <div style="background:{color};height:3px;border-radius:3px;width:{min(cs,100)}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    cols2 = st.columns(3)
    for idx, (label, key, color) in enumerate(comp_meta[4:]):
        c = smp["components"].get(key, {})
        cs = c.get("score", 50)
        wt = f"{c.get('weight', 0)*100:.0f}%"
        with cols2[idx]:
            st.markdown(f"""
            <div style="background:#0d1117;border:1px solid #21262d;border-radius:10px;padding:12px;margin-bottom:8px;min-height:80px">
                <div style="font-size:8px;color:{color};letter-spacing:1.5px;font-weight:700">{label}</div>
                <div style="font-size:9px;color:#8b949e">WT: {wt}</div>
                <div style="font-size:24px;font-weight:900;color:{color};margin:4px 0">{cs}</div>
                <div style="background:#21262d;border-radius:3px;height:3px;margin-top:4px">
                    <div style="background:{color};height:3px;border-radius:3px;width:{min(cs,100)}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#0d1117;border:1px solid #21262d;border-radius:12px;padding:16px;margin:8px 0">
        <div style="font-size:10px;color:#66BB6A;letter-spacing:2px;font-weight:700;margin-bottom:8px">EVIDENCE</div>
        <div style="font-size:13px;color:#e6edf3;line-height:1.8">{smp['evidence']}</div>
    </div>
    <div style="background:#0d1117;border:1px solid #21262d;border-radius:12px;padding:16px;margin:8px 0">
        <div style="font-size:10px;color:#FFC107;letter-spacing:2px;font-weight:700;margin-bottom:8px">RISK WARNING</div>
        <div style="font-size:13px;color:#FFD54F;line-height:1.8">{smp['risk']}</div>
    </div>
    """, unsafe_allow_html=True)

    for label, key, color in comp_meta:
        c = smp["components"].get(key, {})
        sigs = c.get("signals", [])
        if sigs:
            with st.expander(f"{label} — Detail ({c.get('score', 50)}/100)"):
                for sig in sigs:
                    st.markdown(f"<div style='color:#c9d1d9;font-size:12px;padding:3px 0;border-bottom:1px solid #21262d'>• {sig}</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# V10 — OPPORTUNITY ENGINE SCANNER
# ─────────────────────────────────────────────────────────────

FULL_UNIVERSE = [
    # ── USA — AI & Compute ──
    "NVDA","AMD","AVGO","MSFT","GOOGL","META","AMZN","AAPL","TSM","ASML",
    "ORCL","CRM","NOW","ADBE","PLTR","SNOW","ARM","MRVL","ANET","QCOM",
    "MU","INTC","SMCI","DELL","VRT","HPE","NET","DDOG","CRWD","PANW",
    "ZS","FTNT","COIN","MSTR","HOOD","XYZ","MARA","RIOT",
    # ── USA — Energy & Nuclear ──
    "CEG","VST","NEE","OKLO","SMR","NNE","UEC","CCJ","FSLR","ENPH",
    "ETN","GEV","XOM","CVX",
    # ── USA — Robotics & Industrial ──
    "TSLA","ISRG","PATH","DE","CAT","HON",
    # ── USA — Space & Defense ──
    "SPCX","RKLB","ASTS","LUNR","RDW","MNTS","SPIR","IONQ","QBTS",
    "LMT","RTX","NOC","GD","BWXT","KTOS",
    # ── USA — Biotech ──
    "LLY","NVO","MRNA","REGN","VRTX","RXRX","CRSP",
    # ── USA — Finance & Capital ──
    "BX","KKR","APO","GS",
    # ── USA — Resources ──
    "MP","FCX","NEM","LAC","GOLD",
    # ── Canada (ADRs + .TO) ──
    "SHOP","BB","MDA.TO","NXE","DML.TO",
    # ── Europe (ADRs) ──
    "SAP","SIEGY","NXPI","INFY","UMC","STM","GRAB",
    # ── Japan (ADRs) ──
    "SONY","TM","FANUY",
    # ── Singapore / HK / Asia (ADRs) ──
    "SE","BABA","BIDU","JD","PDD",
    # ── Quantum & Frontier ──
    "RGTI","QUBT",
    # ── Underdogs & Below Radar — Small/Mid Cap with Potential ──
    "AEHR","GSAT","IREN","CORZ","WULF","BTDR","HUT","CIFR",  # AI/Crypto infra
    "ACHR","JOBY","LILM","EVTL",  # eVTOL / Air mobility
    "PSNY","RIVN","LCID","GOEV",  # EV underdogs
    "DNA","ARKG","BEAM","NTLA","EDIT",  # Genomics / Gene editing
    "SOFI","UPST","AFRM","NU",  # Fintech underdogs
    "RBOT","SERV","ORGN",  # Robotics / DeepTech
    "IQ","FUTU","TIGR",  # China tech underdogs
    "U","RBLX","MTTR",  # Metaverse / Gaming
    "SOUN","BBAI","AI",  # AI small-caps
    "APLD","CLSK",  # Data center / Mining
]


def _prefetch_yfinance(tickers):
    """Parallel prefetch yfinance data — returns dict of ticker -> (info, hist)."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    results = {}
    def _fetch(t):
        try:
            tk_obj = yf.Ticker(t)
            info = tk_obj.info or {}
            hist = tk_obj.history(period="1y")
            return t, info, hist
        except Exception:
            return t, None, None
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(_fetch, t) for t in tickers]
        for f in as_completed(futures):
            t, info, hist = f.result()
            if info is not None and hist is not None and not hist.empty:
                results[t] = (info, hist)
    return results


def _build_row(t, info, hist, enriched=None):
    """Build a single opportunity row from preloaded data."""
    price = safe(info, "currentPrice", "regularMarketPrice", default=0)
    if not price and not hist.empty:
        price = float(hist["Close"].iloc[-1])
    if not price:
        return None
    scores = compute_all_scores(info, hist, None, None)
    cfis = cfis_composite(scores)
    cm = compute_capital_migration(info, hist, t)
    if enriched is None:
        enriched = {"data_quality": 0}
    hunter = compute_hunter(info, hist, scores, cm, enriched)
    name = (info.get("shortName") or info.get("longName", t))[:25]
    primary_theme = cm["primary_theme"]
    td = cm.get("theme_data", {})
    thesis_obj = cm.get("thesis", {})
    one_sentence = ""
    if t.upper() in STOCK_THESIS:
        inv = STOCK_THESIS[t.upper()]["investment_thesis"]
        one_sentence = inv.split(".")[0] + "." if "." in inv else inv[:120]
    elif thesis_obj.get("investment_thesis"):
        inv = thesis_obj["investment_thesis"]
        one_sentence = inv.split(".")[0] + "." if "." in inv else inv[:120]
    target = safe(info, "targetMeanPrice", default=price)
    expected_ret = ((target - price) / price * 100) if price and target else 0
    mom_15 = 0
    if len(hist) >= 15:
        mom_15 = (hist["Close"].iloc[-1] - hist["Close"].iloc[-15]) / hist["Close"].iloc[-15] * 100
    mom_5 = 0
    if len(hist) >= 5:
        mom_5 = (hist["Close"].iloc[-1] - hist["Close"].iloc[-5]) / hist["Close"].iloc[-5] * 100
    narr = hunter["narrative"]
    return {
        "ticker": t, "name": name, "price": price,
        "theme": primary_theme, "theme_icon": td.get("icon", "📊"),
        "cfis": cfis,
        "conviction": hunter["hunter_score"],
        "signal": hunter["zone_label"],
        "signal_color": hunter["zone_color"],
        "classification": hunter["classification"],
        "bottleneck": cm["scores"]["bottleneck"],
        "cm_score": cm["scores"]["overall"],
        "narrative": narr["score"] if isinstance(narr, dict) else narr,
        "mom_15": mom_15, "mom_5": mom_5,
        "expected_ret": expected_ret,
        "is_bottleneck": cm.get("is_bottleneck", False),
        "one_sentence": one_sentence,
        "risk": scores.get("Fortress Balance Sheet", 50),
        "quality": (scores.get("Revenue Quality", 50) + scores.get("Economic Moat", 50)) / 2,
        "cap_score": hunter.get("cap", {}).get("score", 0) if isinstance(hunter.get("cap"), dict) else 0,
        "force_score": hunter.get("force", {}).get("score", 0) if isinstance(hunter.get("force"), dict) else 0,
        "crowding_score": hunter.get("crowding", {}).get("score", 0) if isinstance(hunter.get("crowding"), dict) else 100,
        "timing_score": hunter.get("timing", {}).get("score", 0) if isinstance(hunter.get("timing"), dict) else 0,
        "conviction_score": hunter.get("conviction", {}).get("score", 0) if isinstance(hunter.get("conviction"), dict) else 0,
        "action": hunter.get("action", "PASS"),
        "action_color": hunter.get("action_color", "#78909C"),
        "action_icon": hunter.get("action_icon", "❌"),
        "action_desc": hunter.get("action_desc", ""),
        "hunt_alert": hunter.get("hunt_alert", False),
    }


@st.cache_data(ttl=600)
def scan_opportunities(universe_tuple):
    prefetched = _prefetch_yfinance(universe_tuple)

    # Phase 1: Fast scan with yfinance only (no enriched API calls)
    fast_rows = []
    for t in universe_tuple:
        if t not in prefetched:
            continue
        try:
            info, hist = prefetched[t]
            row = _build_row(t, info, hist)
            if row:
                fast_rows.append(row)
        except Exception:
            pass

    if not fast_rows:
        raise RuntimeError("No opportunity data")

    # Phase 2: Enrich only top 30 candidates with multi-source APIs
    fast_rows.sort(key=lambda x: x["conviction"], reverse=True)
    top_tickers = {r["ticker"] for r in fast_rows[:30]}

    rows = []
    for r in fast_rows:
        t = r["ticker"]
        if t in top_tickers and t in prefetched:
            try:
                info, hist = prefetched[t]
                enriched = fetch_enriched_data(t)
                enriched_row = _build_row(t, info, hist, enriched)
                if enriched_row:
                    rows.append(enriched_row)
                    continue
            except Exception:
                pass
        rows.append(r)

    return rows


@st.cache_data(ttl=600)
def scan_validation_periods(universe_tuple, start_date_str="2026-03-01"):
    import time
    from datetime import datetime, timedelta
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
    today = datetime.now()
    periods = []
    p_start = start_dt
    p_num = 1
    while p_start < today:
        p_end = p_start + timedelta(days=30)
        if p_end > today:
            p_end = today
        periods.append({"num": p_num, "start": p_start, "end": p_end, "label": f"Day {(p_num-1)*30+1}-{p_num*30}"})
        p_start = p_end
        p_num += 1

    rows = []
    for i, t in enumerate(universe_tuple):
        try:
            tk_obj = yf.Ticker(t)
            info = tk_obj.info or {}
            hist = tk_obj.history(start=start_date_str, end=today.strftime("%Y-%m-%d"))
            if hist.empty or len(hist) < 5:
                continue
            hist_1y = tk_obj.history(period="1y")
            if hist_1y.empty:
                continue
            scores = compute_all_scores(info, hist_1y, None, None)
            cm = compute_capital_migration(info, hist_1y, t)
            enriched = fetch_enriched_data(t)
            hunter = compute_hunter(info, hist_1y, scores, cm, enriched)
            conviction = hunter["hunter_score"]
            signal = hunter["zone_label"]
            signal_color = hunter["zone_color"]
            name = (info.get("shortName") or info.get("longName", t))[:25]
            primary_theme = cm["primary_theme"]
            td = cm.get("theme_data", {})
            base_price = float(hist["Close"].iloc[0])
            current_price = float(hist["Close"].iloc[-1])
            total_ret = (current_price - base_price) / base_price * 100

            period_returns = []
            for p in periods:
                p_hist = hist[(hist.index >= p["start"].strftime("%Y-%m-%d")) & (hist.index < p["end"].strftime("%Y-%m-%d"))]
                if len(p_hist) >= 2:
                    p_open = float(p_hist["Close"].iloc[0])
                    p_close = float(p_hist["Close"].iloc[-1])
                    p_ret = (p_close - p_open) / p_open * 100
                    period_returns.append({"period": p["label"], "ret": p_ret, "open": p_open, "close": p_close})
                elif len(p_hist) == 1:
                    period_returns.append({"period": p["label"], "ret": 0.0, "open": float(p_hist["Close"].iloc[0]), "close": float(p_hist["Close"].iloc[0])})
                else:
                    period_returns.append({"period": p["label"], "ret": None, "open": None, "close": None})

            rows.append({
                "ticker": t, "name": name, "conviction": conviction,
                "signal": signal, "signal_color": signal_color,
                "theme": primary_theme, "theme_icon": td.get("icon", "📊"),
                "base_price": base_price, "current_price": current_price,
                "total_ret": total_ret, "periods": period_returns,
                "is_bottleneck": cm.get("is_bottleneck", False),
            })
        except Exception:
            pass
        if (i + 1) % 6 == 0:
            time.sleep(0.3)
    if not rows:
        raise RuntimeError("No validation data")
    return rows, [p["label"] for p in periods]


def filter_opportunities(rows, horizon):
    if horizon == "15d":
        scored = sorted(rows, key=lambda r: r["mom_15"] * 0.35 + r["conviction"] * 0.35 + r["narrative"] * 0.30, reverse=True)
    elif horizon == "30d":
        scored = sorted(rows, key=lambda r: r["conviction"] * 0.40 + r["mom_15"] * 0.25 + r["cm_score"] * 0.35, reverse=True)
    elif horizon == "90d":
        scored = sorted(rows, key=lambda r: r["conviction"] * 0.40 + r["cm_score"] * 0.35 + r["quality"] * 0.25, reverse=True)
    elif horizon == "legacy":
        scored = sorted(rows, key=lambda r: r["conviction"] * 0.30 + r["bottleneck"] * 0.25 + r["quality"] * 0.25 + r["risk"] * 0.20, reverse=True)
    else:
        scored = sorted(rows, key=lambda r: r["conviction"], reverse=True)
    return scored


def render_opportunity_table(rows, count=12, show_thesis=True):
    for i, r in enumerate(rows[:count]):
        sig_c = r["signal_color"]
        conv_c = "#4CAF50" if r["conviction"] >= 65 else ("#FFC107" if r["conviction"] >= 45 else "#f44336")
        ret_c = "#4CAF50" if r["expected_ret"] >= 0 else "#f44336"
        bn_badge = '<span style="background:#1a3a1a;border:1px solid #4CAF50;border-radius:12px;padding:1px 8px;font-size:9px;color:#66d166;margin-left:6px">BOTTLENECK</span>' if r["is_bottleneck"] else ""
        thesis_html = f'<div style="font-size:11px;color:#b0bcd4;margin-top:6px;line-height:1.5">{r["one_sentence"]}</div>' if show_thesis and r["one_sentence"] else ""
        st.markdown(f"""
        <div style="background:#161b27;border-radius:10px;padding:12px 16px;margin-bottom:6px;border-left:4px solid {sig_c};display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap">
            <div style="min-width:60px">
                <div style="font-size:16px;font-weight:900;color:#ffffff">{r['ticker']}</div>
                <div style="font-size:10px;color:#8a9bb5">{r['name']}</div>
            </div>
            <div style="min-width:65px;text-align:center">
                <div style="font-size:20px;font-weight:900;color:{conv_c}">{r['conviction']:.0f}</div>
                <div style="font-size:9px;color:#8a9bb5">CONVICTION</div>
            </div>
            <div style="min-width:65px;text-align:center">
                <div style="font-size:14px;font-weight:800;color:{sig_c}">{r['signal']}</div>
                <div style="font-size:9px;color:#8a9bb5">SIGNAL</div>
            </div>
            <div style="min-width:70px;text-align:center">
                <div style="font-size:12px;color:#e8ecf4">{r['theme_icon']} {r['theme'][:18]}</div>
                <div style="font-size:9px;color:#8a9bb5">THEME</div>
            </div>
            <div style="min-width:50px;text-align:center">
                <div style="font-size:14px;font-weight:700;color:#e8ecf4">${r['price']:.2f}</div>
                <div style="font-size:9px;color:#8a9bb5">PRICE</div>
            </div>
            <div style="min-width:60px;text-align:center">
                <div style="font-size:14px;font-weight:700;color:{ret_c}">{r['expected_ret']:+.0f}%</div>
                <div style="font-size:9px;color:#8a9bb5">ANALYST TARGET</div>
            </div>
            <div style="min-width:70px;text-align:center">
                <div style="font-size:14px;font-weight:700;color:{'#4CAF50' if r['mom_15'] >= 0 else '#f44336'}">{r['mom_15']:+.1f}%</div>
                <div style="font-size:9px;color:#8a9bb5">15D MOMENTUM</div>
                {'<div style="font-size:8px;font-weight:700;color:#000;background:#f44336;border-radius:6px;padding:1px 6px;margin-top:2px">⚠️ FALLING</div>' if r['mom_15'] < -10 else ('<div style="font-size:8px;font-weight:700;color:#000;background:#FFC107;border-radius:6px;padding:1px 6px;margin-top:2px">⚠️ WEAK</div>' if r['mom_15'] < -5 else '')}
            </div>
            <div style="flex:1;min-width:100px">
                {bn_badge}{thesis_html}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# TOP 30
# ─────────────────────────────────────────────────────────────
# Why each stock is on this list — plain English
TOP_30_WHY = {
    "NVDA":  "Owns AI compute. Every AI model trains on NVIDIA chips. No real alternative at scale.",
    "MSFT":  "Azure cloud + OpenAI investment. Enterprise AI is running through Microsoft.",
    "AAPL":  "1 billion devices. When Apple adds AI, the installed base is the distribution.",
    "GOOGL": "DeepMind + Search + YouTube + Cloud. AI across every product they own.",
    "META":  "AI-powered ad targeting. Rebuilt itself post-2022. Llama open source strategy.",
    "AMZN":  "AWS is the cloud floor. Bedrock for enterprise AI. Logistics automation at scale.",
    "TSLA":  "EV leader + Optimus humanoid robot + FSD autonomous driving. Elon factor.",
    "AMD":   "Only real GPU rival to NVIDIA. Data centre CPUs and AI accelerators growing fast.",
    "AVGO":  "Custom AI chips for Google, Meta, Apple. Networking for AI infrastructure.",
    "ORCL":  "AI database and cloud contracts surging. Larry Ellison's cloud pivot is working.",
    "CRM":   "AI agents for enterprise sales. Agentforce platform across 150K+ customers.",
    "NFLX":  "Streaming winner + ad tier + AI content personalisation. Subscribers keep growing.",
    "ADBE":  "Firefly AI generation inside Creative Cloud. Designers can't leave Adobe.",
    "PLTR":  "AI for governments and defense. AIP platform. Stickiest enterprise AI contracts.",
    "SNOW":  "Data cloud where enterprises store everything before AI processes it.",
    "UBER":  "Autonomous vehicle platform partner. Logistics network + robotaxi ready.",
    "ARM":   "Designs chips inside 99% of smartphones. AI edge computing royalties.",
    "SMCI":  "Builds the servers AI runs in. Direct beneficiary of data centre buildout.",
    "MRVL":  "Custom silicon for AWS, Google, Microsoft. AI networking and storage chips.",
    "ANET":  "Ethernet networking for AI data centres. Dominant in cloud switching.",
    "NOW":   "AI workflow automation. ServiceNow inside every large enterprise IT stack.",
    "SHOP":  "Commerce infrastructure for the internet. AI tools for 2M+ merchants.",
    "XYZ":   "Cash App + Bitcoin + payments. Jack Dorsey building the crypto-native finance layer.",
    "COIN":  "Crypto's most credible exchange. Regulation clarity is its biggest catalyst.",
    "RBLX":  "Virtual world platform for Gen Z. AI-generated content and economy.",
    "U":     "Unity. 3D engine powering games, simulation, and industrial digital twins.",
    "PATH":  "Robotic process automation. AI agents replacing repetitive office work.",
    "AI":    "C3.ai. Enterprise AI applications across energy, defense, and manufacturing.",
    "IONQ":  "Quantum computing. Early stage but the compute paradigm after classical silicon.",
    "QBTS":  "D-Wave quantum. Annealing quantum computers solving real logistics problems now.",
}

TOP_30 = list(TOP_30_WHY.keys())

@st.cache_data(ttl=600, show_spinner=False)
def fetch_top30():
    import time
    rows = []
    for i, t in enumerate(TOP_30):
        try:
            tk = yf.Ticker(t)
            info = tk.info or {}
            hist = tk.history(period="1y")
            price = safe(info, "currentPrice", "regularMarketPrice", default=0)
            if not price and not hist.empty:
                price = float(hist["Close"].iloc[-1])
            if not price:
                continue
            scores = compute_all_scores(info, hist, None, None)
            cfis  = cfis_composite(scores)
            opp   = opportunity_score(cfis, info, hist)

            # 30-day and 90-day outlook
            outlooks = generate_outlooks(info, hist, cfis)
            o30  = outlooks.get("30 Day",  {})
            o90  = outlooks.get("90 Day",  {})
            p30  = o30.get("price", 0)
            p90  = o90.get("price", 0)
            pct30 = o30.get("pct", 0)
            pct90 = o90.get("pct", 0)

            # Louis verdict
            dims       = louis_intuition_engine(info, hist, t, None, None)
            _, lp, _   = get_leader_intel(info, t)
            conviction = louis_conviction_score(dims, lp)
            dummy_opts = options_gambling_signal(None, None, info)
            scenario   = generate_15day_scenario(info, hist, dims, conviction, dummy_opts)
            sig        = scenario["total_signal"]
            verdict    = "📈 CALL" if sig >= 62 else ("📉 PUT" if sig <= 38 else "⏸ HOLD")

            rows.append({
                "Ticker":         t,
                "Name":           info.get("shortName", t)[:20],
                "Price":          f"${price:.2f}" if price else "N/A",
                "Louis Pick":     verdict,
                "CFIS-X":         cfis,
                "Opportunity":    opp,
                "30D Target":     f"${p30:.2f} ({pct30:+.1f}%)" if p30 else "N/A",
                "90D Target":     f"${p90:.2f} ({pct90:+.1f}%)" if p90 else "N/A",
                "Econ. Moat":     scores["Economic Moat"],
                "Rev. Quality":   scores["Revenue Quality"],
                "Fin. Fortress":  scores["Fortress Balance Sheet"],
                "Why It's Here":  TOP_30_WHY.get(t, ""),
            })
        except Exception:
            pass
        # Small delay every 5 stocks to avoid rate limit
        if (i + 1) % 5 == 0:
            time.sleep(0.5)
    if not rows:
        raise RuntimeError("No stock data fetched — possible rate limit")
    df = pd.DataFrame(rows)
    df = df.sort_values("CFIS-X", ascending=False).reset_index(drop=True)
    df.index += 1
    return df


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────
# COMBO PLAYS ENGINE
# ─────────────────────────────────────────────────────────────
COMBO_UNIVERSE = [
    # AI / Tech
    "NVDA","AMD","PLTR","SMCI","ARM","AVGO","MRVL","ANET","NOW","IONQ",
    # Energy / Nuclear
    "CEG","VST","CCJ","UEC","NNE","SMR","OKLO","FSLR","ENPH","NEE",
    # Defense
    "LMT","RTX","NOC","BWXT","CACI","GD",
    # Space
    "RKLB","ASTS","LUNR",
    # Crypto / Fintech
    "COIN","MSTR","MARA","HOOD","XYZ","PYPL",
    # Robotics
    "TSLA","PATH","ISRG",
    # Biotech
    "RXRX","ILMN","CRSP",
    # Commodities
    "MP","FCX","CCJ","NEM","LAC",
]

@st.cache_data(ttl=600)
def scan_combo_plays():
    """Scan universe for optimal CALL and PUT combo plays."""
    import time
    candidates = []
    for i, t in enumerate(COMBO_UNIVERSE):
        try:
            tk = yf.Ticker(t)
            info = tk.info or {}
            hist = tk.history(period="1y")
            if hist.empty or len(hist) < 15:
                continue
            price = safe(info, "currentPrice", "regularMarketPrice", default=0)
            if not price:
                price = float(hist["Close"].iloc[-1])
            if not price:
                continue
            if (i + 1) % 6 == 0:
                time.sleep(0.3)

            scores = compute_all_scores(info, hist, None, None)
            cfis   = cfis_composite(scores)
            opp    = opportunity_score(cfis, info, hist)
            outlooks = generate_outlooks(info, hist, cfis)

            o30 = outlooks.get("30 Day", {})
            o90 = outlooks.get("90 Day", {})
            pct30 = o30.get("pct", 0)
            pct90 = o90.get("pct", 0)
            p30   = o30.get("price", 0)
            p90   = o90.get("price", 0)

            # Momentum
            mom15 = (hist["Close"].iloc[-1] - hist["Close"].iloc[-15]) / hist["Close"].iloc[-15] * 100

            # Louis verdict
            dims      = louis_intuition_engine(info, hist, t, None, None)
            _, lp, _  = get_leader_intel(info, t)
            conviction = louis_conviction_score(dims, lp)
            dummy_opts = options_gambling_signal(None, None, info)
            scenario  = generate_15day_scenario(info, hist, dims, conviction, dummy_opts)
            sig       = scenario["total_signal"]

            sector = info.get("sector", "Unknown") or "Unknown"

            candidates.append({
                "ticker": t,
                "name": (info.get("shortName", t) or t)[:22],
                "price": price,
                "sector": sector,
                "cfis": cfis,
                "opp": opp,
                "conviction": conviction,
                "pct30": pct30,
                "pct90": pct90,
                "p30": p30,
                "p90": p90,
                "mom15": mom15,
                "signal": sig,
                "lo_pct": scenario["lo_pct"],
                "hi_pct": scenario["hi_pct"],
            })
        except Exception:
            continue

    # ── Build CALL combo: highest combined 30-90 day upside ──
    # Pick top stocks by (pct90 + conviction weight), diversify by sector
    # Pick best stocks by combined score — even small positive outlook counts
    bull_pool = sorted(
        [c for c in candidates if c["cfis"] >= 40],
        key=lambda x: x["pct90"] * 0.4 + x["conviction"] * 0.25 + x["opp"] * 0.15 + x["mom15"] * 0.2,
        reverse=True
    )
    # Diversify: max 2 per sector
    call_combo = []
    sector_count = Counter()
    for c in bull_pool:
        if sector_count[c["sector"]] < 2 and len(call_combo) < 5:
            call_combo.append(c)
            sector_count[c["sector"]] += 1

    # ── Build PUT combo: worst outlook, bearish signals ──
    # Pick worst stocks — lowest combined outlook + weakest scores
    bear_pool = sorted(
        candidates,
        key=lambda x: x["pct90"] * 0.4 + x["conviction"] * 0.25 + x["opp"] * 0.15 + x["mom15"] * 0.2,
    )
    put_combo = []
    sector_count_p = Counter()
    for c in bear_pool:
        if sector_count_p[c["sector"]] < 2 and len(put_combo) < 5:
            put_combo.append(c)
            sector_count_p[c["sector"]] += 1

    # Combined profit estimates
    if not candidates:
        raise RuntimeError("No combo data fetched")

    call_combined_30 = sum(c["pct30"] for c in call_combo) / len(call_combo) if call_combo else 0
    call_combined_90 = sum(c["pct90"] for c in call_combo) / len(call_combo) if call_combo else 0
    put_combined_30  = sum(abs(c["pct30"]) for c in put_combo) / len(put_combo) if put_combo else 0
    put_combined_90  = sum(abs(c["pct90"]) for c in put_combo) / len(put_combo) if put_combo else 0

    return call_combo, put_combo, call_combined_30, call_combined_90, put_combined_30, put_combined_90


# ─────────────────────────────────────────────────────────────
# MACRO EVENT REDDIT SCANNER
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def scan_reddit_macro():
    """Scan Reddit for macro event signals — BOJ, yen carry, Fed, risk-off."""
    headers = {"User-Agent": "CFIS-X-StockApp/2.0 (educational)"}
    macro_queries = [
        ("BOJ rate hike", "boj"),
        ("yen carry trade", "carry"),
        ("carry trade unwind", "carry"),
        ("Japan interest rate", "boj"),
        ("forced liquidation", "leverage"),
        ("margin call crash", "leverage"),
        ("risk off sell", "risk"),
        ("rate hike inflation", "fed"),
    ]
    macro_subs = ["wallstreetbets", "stocks", "investing", "options", "economics"]
    signals = {
        "boj_mentions": 0, "carry_mentions": 0, "leverage_mentions": 0,
        "risk_off_mentions": 0, "fed_mentions": 0,
        "total": 0, "top_posts": [], "themes": [],
    }
    for query, bucket in macro_queries:
        for sub in macro_subs:
            try:
                url = (f"https://www.reddit.com/r/{sub}/search/.rss"
                       f"?q={query}&sort=new&limit=8&t=month&restrict_sr=1")
                r = requests.get(url, headers=headers, timeout=6)
                if r.status_code != 200:
                    continue
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                root = ET.fromstring(r.text)
                entries = root.findall("atom:entry", ns)
                count = len(entries)
                if count == 0:
                    continue
                signals["total"] += count
                if bucket == "boj":      signals["boj_mentions"] += count
                elif bucket == "carry":  signals["carry_mentions"] += count
                elif bucket == "leverage": signals["leverage_mentions"] += count
                elif bucket == "risk":   signals["risk_off_mentions"] += count
                elif bucket == "fed":    signals["fed_mentions"] += count

                for e in entries[:2]:
                    title_el = e.find("atom:title", ns)
                    title = title_el.text if title_el is not None and title_el.text else ""
                    if title and len(signals["top_posts"]) < 10:
                        signals["top_posts"].append({"sub": sub, "query": query, "title": title[:120]})
            except Exception:
                continue

    # Determine dominant macro themes
    if signals["boj_mentions"] + signals["carry_mentions"] >= 8:
        signals["themes"].append("🇯🇵 BOJ Rate Hike / Yen Carry Unwind")
    if signals["leverage_mentions"] >= 5:
        signals["themes"].append("💥 Forced Liquidation / Margin Risk")
    if signals["risk_off_mentions"] >= 4:
        signals["themes"].append("🔴 Risk-Off Rotation")
    if signals["fed_mentions"] >= 5:
        signals["themes"].append("🏦 Fed Policy / Rate Uncertainty")

    return signals


# ── YEN CARRY VULNERABLE STOCKS ──────────────────────────────
# Stocks most exposed to a yen carry trade unwind:
# High-beta, high-leverage, speculative, derivatives-heavy, momentum-dependent
YEN_CARRY_VULNERABLE = {
    # High-beta growth with no/thin earnings — funded by cheap leverage
    "IONQ":  "Quantum speculative play, no earnings, pure momentum — first to sell in risk-off.",
    "RIVN":  "Cash-burning EV startup, high beta. Carry trade money funded the SPAC/growth era.",
    "NIO":   "China EV + high short interest. Double exposure: yen carry + China risk.",
    "SOFI":  "Fintech growth name. Trades on rate expectations — BOJ tightening hits the thesis.",
    "MARA":  "Bitcoin miner. Crypto is the ultimate carry trade proxy — leveraged risk-on.",
    "RIOT":  "Bitcoin mining, extreme beta to crypto. Carry unwind = BTC dump = RIOT dumps harder.",
    "RBLX":  "No profits, metaverse speculation. Pure momentum name that unwinds in risk-off.",
    "U":     "Unity. Loss-making, high beta. Growth-at-any-price stocks get hit first.",
    "AI":    "C3.ai. AI hype name with minimal revenue quality. Momentum-dependent.",
    "SOUN":  "SoundHound. Speculative AI micro-cap. First out the door when leverage unwinds.",
    "SMCI":  "SuperMicro. Accounting concerns + high beta + AI hype premium. Fragile.",
    "ENPH":  "Enphase. Solar growth name that trades on rate expectations. Higher yen = pressure.",
    "CRSP":  "CRISPR. Biotech with no revenue. Speculative positioning unwinds in deleveraging.",
    "COIN":  "Coinbase. Crypto exchange = maximum carry trade exposure. If BTC drops, COIN drops faster.",
    "HOOD":  "Robinhood. Retail broker that thrives on speculation. Carry unwind kills retail flow.",
    "ASTS":  "AST SpaceMobile. Pre-revenue space speculation. Pure optionality that gets crushed in risk-off.",
    "LUNR":  "Intuitive Machines. Pre-revenue lunar play. Sells off first in forced liquidation.",
    "QBTS":  "D-Wave quantum. Speculative micro-cap. No moat against a macro sell-off.",
    "RGTI":  "Rigetti quantum. Same thesis — speculative, pre-revenue, high beta.",
    "ACHR":  "Archer Aviation. eVTOL pre-revenue. Carry trade funded these SPAC-era names.",
}


@st.cache_data(ttl=600)
def scan_macro_put_combo():
    """Build aggressive PUT combo targeting yen carry trade vulnerable stocks."""
    import time
    results = []
    for i, (t, thesis) in enumerate(YEN_CARRY_VULNERABLE.items()):
        try:
            tk = yf.Ticker(t)
            info = tk.info or {}
            hist = tk.history(period="6mo")
            if hist.empty or len(hist) < 15:
                continue
            price = safe(info, "currentPrice", "regularMarketPrice", default=0)
            if not price:
                price = float(hist["Close"].iloc[-1])
            if not price:
                continue
            if (i + 1) % 6 == 0:
                time.sleep(0.3)

            beta = safe(info, "beta", default=1) or 1
            pe   = safe(info, "trailingPE", default=None)
            pm   = safe(info, "profitMargins", default=0) or 0
            de   = safe(info, "debtToEquity", default=50) or 50
            mc   = safe(info, "marketCap", default=0) or 0

            # 15-day momentum
            mom15 = (hist["Close"].iloc[-1] - hist["Close"].iloc[-15]) / hist["Close"].iloc[-15] * 100
            # Annualised volatility
            vol = hist["Close"].pct_change().std() * (252 ** 0.5) if len(hist) > 20 else 0.5

            # Vulnerability score: higher = more exposed to carry unwind
            vuln = 50
            vuln += clamp((beta - 1) * 30, 0, 30)         # high beta = more exposed
            vuln += clamp(vol * 40, 0, 25)                 # high vol = fragile
            if pe is None or (pe and pe < 0): vuln += 20   # no earnings = speculative
            elif pe and pe > 80:              vuln += 15   # absurd PE
            vuln += clamp((0 - pm) * 80, 0, 20)           # negative margins = burning cash
            vuln += clamp(de * 0.05, 0, 10)                # leveraged balance sheet
            if mc < 5e9:  vuln += 10                        # small cap = less liquidity
            if mom15 > 15: vuln += 10                       # overextended momentum = snap-back risk

            # Estimated drawdown in carry unwind scenario
            # Base: beta * 8% (Aug 2024 carry unwind was ~8-12% on Nikkei, 3-5% on S&P)
            est_drop_15d = beta * 8 + (vol - 0.3) * 15
            est_drop_30d = est_drop_15d * 1.3

            results.append({
                "ticker": t,
                "name": (info.get("shortName", t) or t)[:22],
                "price": price,
                "beta": beta,
                "vol": vol * 100,
                "pe": pe,
                "mom15": mom15,
                "vuln": clamp(vuln),
                "thesis": thesis,
                "est_drop_15d": est_drop_15d,
                "est_drop_30d": est_drop_30d,
                "sector": info.get("sector", "Unknown") or "Unknown",
            })
        except Exception:
            continue

    results.sort(key=lambda x: x["vuln"], reverse=True)
    return results[:8]  # Top 8 most vulnerable


with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:8px 0 4px 0">
        <div style="font-size:22px;font-weight:900;color:#ffffff;letter-spacing:4px;
                    font-family:'Inter',sans-serif">CFIS</div>
        <div style="font-size:8px;color:#7c3aed;letter-spacing:3px;margin-top:2px;font-weight:700">
            CAPITAL FLOW INTELLIGENCE</div>
        <div style="width:40px;height:1px;background:linear-gradient(90deg,#7c3aed,#4CAF50);
                    margin:8px auto"></div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("by mono378 · Institutional Intelligence")
    st.divider()
    page = st.radio("Navigation", [
        "1️⃣ Market Health",
        "2️⃣ Capital Migration",
        "3️⃣ Opportunity Engine",
        "4️⃣ Portfolio Commander",
        "5️⃣ Validation Engine",
        "6️⃣ Hunter Command by Louis Teo",
    ], label_visibility="collapsed")
    st.divider()
    st.caption("Data: Yahoo Finance · Cache: 5 min")
    st.caption("CFIS V10 by mono378")
    st.divider()
    if st.button("🔒 Logout", use_container_width=True, key="logout_btn"):
        st.session_state["authenticated"] = False
        st.cache_data.clear()
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# STOCK ANALYZER PAGE


# ─────────────────────────────────────────────────────────────
# FETCH THEME — module level so @st.cache_data works correctly
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def fetch_theme(tickers_tuple):
    import time
    rows = []
    for i, t in enumerate(tickers_tuple):
        try:
            tk = yf.Ticker(t)
            info = tk.info or {}
            hist = tk.history(period="1y")
            scores = compute_all_scores(info, hist, None, None)
            cfis   = cfis_composite(scores)
            opp    = opportunity_score(cfis, info, hist)
            price  = safe(info, "currentPrice", "regularMarketPrice", default=0)
            if not price and not hist.empty:
                price = float(hist["Close"].iloc[-1])
            if not price:
                continue
            if (i + 1) % 5 == 0:
                time.sleep(0.3)
            prev   = safe(info, "previousClose", default=price) or price
            chgp   = ((price - prev) / prev * 100) if prev else 0
            mc     = safe(info, "marketCap", default=0)
            dims       = louis_intuition_engine(info, hist, t, None, None)
            _, lp, _   = get_leader_intel(info, t)
            conviction = louis_conviction_score(dims, lp)
            dummy_opts = options_gambling_signal(None, None, info)
            scenario   = generate_15day_scenario(info, hist, dims, conviction, dummy_opts)
            sig        = scenario["total_signal"]
            if sig >= 62:   verdict, v_color, v_bg = "📈 CALL", "#4CAF50", "#0a2a0a"
            elif sig <= 38: verdict, v_color, v_bg = "📉 PUT",  "#f44336", "#2a0a0a"
            else:           verdict, v_color, v_bg = "⏸ HOLD",  "#FFC107", "#2a2200"
            # Momentum proxy: 15-day return if enough history
            mom = 0
            if len(hist) >= 15:
                mom = (hist["Close"].iloc[-1] - hist["Close"].iloc[-15]) / hist["Close"].iloc[-15] * 100

            # Risk proxy: fortress balance sheet score (higher = safer)
            risk_score = scores.get("Fortress Balance Sheet", 50)

            rows.append({
                "Ticker":     t,
                "Name":       info.get("shortName", t)[:22],
                "Price":      price,
                "Chg %":      chgp,
                "Mkt Cap":    mc,
                "CFIS-X":     cfis,
                "Opp":        opp,
                "Conviction": conviction,
                "Momentum":   round(mom, 1),
                "Risk":       risk_score,
                "Industry":   scores.get("Industry Dominance", 50),
                "Moat":       scores.get("Economic Moat", 50),
                "Regime":     scores.get("Market Regime Intelligence", 50),
                "_verdict":   verdict,
                "_v_color":   v_color,
                "_v_bg":      v_bg,
                "_lo_pct":    scenario["lo_pct"],
                "_hi_pct":    scenario["hi_pct"],
                "_opt_rec":   scenario["opt_rec"],
            })
        except Exception:
            pass
    if not rows:
        raise RuntimeError("No theme data fetched")
    df = pd.DataFrame(rows)
    df = df.sort_values("CFIS-X", ascending=False).reset_index(drop=True)
    df.index += 1
    return df


# ─────────────────────────────────────────────────────────────
# 15-DAY HOT RADAR — universe + scanner (module level for caching)
# ─────────────────────────────────────────────────────────────
RADAR_UNIVERSE = [
    # AI / Semiconductors
    "NVDA","AMD","SMCI","PLTR","IONQ","QBTS","RGTI","SOUN","AI","ARM",
    # Energy / Nuclear
    "CEG","VST","CCJ","UEC","DNN","NNE","SMR","OKLO","FSLR","ENPH",
    # Defense / Geopolitical
    "LMT","RTX","NOC","BWXT","CACI","KTOS","AVAV","HII","GD",
    # Space
    "RKLB","ASTS","LUNR","PL",
    # Crypto / Tokenized Finance
    "COIN","MSTR","MARA","RIOT","CLSK","HOOD","XYZ","PYPL",
    # Robotics / Automation
    "TSLA","PATH","ISRG","TER","ACHR","JOBY",
    # Biotech / Medical AI
    "RXRX","TDOC","ILMN","PACB","EDIT","CRSP",
    # High momentum
    "GME","SOFI","RIVN","NIO",
    # Commodities / Scarcity
    "MP","FCX","NEM","LAC","ALB","UUUU","GOLD",
]

@st.cache_data(ttl=300)
def scan_radar(universe):
    import time
    results = []
    for i, t in enumerate(universe):
        try:
            ticker_obj = yf.Ticker(t)
            info = ticker_obj.info or {}
            hist = ticker_obj.history(period="3mo")
            if hist.empty or len(hist) < 15:
                continue

            price = safe(info, "currentPrice", "regularMarketPrice", default=0) or 0
            if price == 0:
                price = float(hist["Close"].iloc[-1])
            if price == 0:
                continue

            close  = hist["Close"]
            vol    = hist["Volume"]
            ret_15 = (close.iloc[-1] - close.iloc[-15]) / close.iloc[-15] * 100
            ret_5  = (close.iloc[-1] - close.iloc[-5])  / close.iloc[-5]  * 100
            ret_1  = (close.iloc[-1] - close.iloc[-2])  / close.iloc[-2]  * 100

            avg_vol_20 = vol.rolling(20).mean().iloc[-1]
            recent_vol = vol.iloc[-5:].mean()
            vol_spike  = (recent_vol / avg_vol_20) if avg_vol_20 > 0 else 1.0

            short_pct   = safe(info, "shortPercentOfFloat", default=0) or 0
            short_ratio = safe(info, "shortRatio", default=0) or 0
            squeeze_score = 0
            if short_pct > 0.15 and ret_15 > 5:
                squeeze_score = min(100, int(short_pct * 200 + ret_15 * 2))

            try:
                dates = list(ticker_obj.options)
                if dates:
                    chain  = ticker_obj.option_chain(dates[0])
                    call_v = chain.calls["volume"].sum() if "volume" in chain.calls else 0
                    put_v  = chain.puts["volume"].sum()  if "volume" in chain.puts  else 0
                    call_oi= chain.calls["openInterest"].sum() if "openInterest" in chain.calls else 1
                    opt_activity = (call_v / call_oi) if call_oi > 0 else 0
                    pc_ratio     = (put_v / call_v)  if call_v  > 0 else 1.0
                else:
                    opt_activity = 0; pc_ratio = 1.0; call_v = put_v = 0
            except:
                opt_activity = 0; pc_ratio = 1.0; call_v = put_v = 0

            dims      = louis_intuition_engine(info, hist, t, None, None)
            geo_score = dims["Geopolitical Importance"]
            ai_score  = dims["AI Leverage"]
            _, lp, _  = get_leader_intel(info, t)

            hot = (
                min(ret_15 * 1.5, 40)            +
                min((vol_spike - 1) * 20, 20)    +
                (geo_score + ai_score) / 2 * 0.25+
                min(opt_activity * 10, 15)
            )
            hot = max(0, min(100, round(hot)))

            tags = []
            if ret_15 > 20:    tags.append("🚀 Strong Breakout")
            elif ret_15 > 10:  tags.append("📈 Momentum Building")
            elif ret_15 > 5:   tags.append("↗️ Trending Up")
            elif ret_15 < -10: tags.append("📉 Under Pressure")
            if vol_spike > 2.5:  tags.append("🔊 Volume Surge 2.5x+")
            elif vol_spike > 1.5:tags.append("🔊 Volume Elevated")
            if squeeze_score > 30: tags.append(f"💥 Squeeze Setup ({int(short_pct*100)}% short)")
            if opt_activity > 1.5: tags.append("🎲 Unusual Call Activity")
            if pc_ratio < 0.5:     tags.append("📗 Heavy Call Buying")
            if pc_ratio > 2.0:     tags.append("📕 Heavy Put Buying")
            if geo_score > 65:     tags.append("🌍 Geopolitical Catalyst")
            if ai_score > 65:      tags.append("🤖 AI Tailwind")
            if lp >= 85:           tags.append("👑 Visionary CEO")

            reasons = []
            if vol_spike > 2.0:
                reasons.append(f"Volume is {vol_spike:.1f}x the 20-day average — unusual accumulation or retail surge.")
            if squeeze_score > 30:
                reasons.append(f"{int(short_pct*100)}% of float is shorted — a move up forces covering, which accelerates the rally.")
            if opt_activity > 1.5:
                reasons.append("Options volume is running far above open interest — traders placing fresh directional bets.")
            if geo_score > 65:
                reasons.append("Geopolitically relevant — benefits from current world events (defense spend, energy, chip wars).")
            if ai_score > 65:
                reasons.append("Direct AI exposure — capital rotating into AI-leveraged companies right now.")
            if ret_15 > 15:
                reasons.append(f"Up {ret_15:.1f}% in 15 days — strong price action that often attracts more buyers.")
            if not reasons:
                reasons.append("Moderate signals across momentum, volume, and theme relevance. Worth monitoring.")

            results.append({
                "ticker": t, "name": info.get("shortName", t)[:20],
                "price": price, "ret_15": ret_15, "ret_5": ret_5, "ret_1": ret_1,
                "vol_spike": vol_spike, "short_pct": short_pct * 100,
                "squeeze": squeeze_score, "opt_activity": opt_activity,
                "pc_ratio": pc_ratio, "geo": geo_score, "ai": ai_score,
                "hot_score": hot, "tags": tags, "reason": " ".join(reasons),
                "call_vol": int(call_v), "put_vol": int(put_v),
            })
        except Exception:
            pass
        if (i + 1) % 6 == 0:
            time.sleep(0.3)

    results.sort(key=lambda x: x["hot_score"], reverse=True)
    return results


if page == "1️⃣ Market Health":
    st.title("📊 Market Health™")
    st.caption("Is the market environment favorable or dangerous? Analyze any stock through the full CFIS pipeline.")

    # ── MACRO RADAR ───────────────────────────────────────────
    with st.spinner("Loading Macro Radar…"):
        try:
            macro = fetch_macro_radar()
            render_macro_radar(macro)
        except Exception:
            macro = None
            st.info("Macro data temporarily unavailable.")

    st.divider()

    # Name → Ticker lookup so typing "Tesla" works
    NAME_TO_TICKER = {
        # Mega-caps / FAANG+
        "tesla":"TSLA","apple":"AAPL","microsoft":"MSFT","google":"GOOGL",
        "alphabet":"GOOGL","amazon":"AMZN","meta":"META","facebook":"META",
        "nvidia":"NVDA","netflix":"NFLX","berkshire":"BRK-B","berkshire hathaway":"BRK-B",
        # Semiconductors
        "intel":"INTC","amd":"AMD","broadcom":"AVGO","arm":"ARM",
        "qualcomm":"QCOM","texas instruments":"TXN","micron":"MU",
        "marvell":"MRVL","supermicro":"SMCI","asml":"ASML","tsmc":"TSM",
        "lam research":"LRCX","applied materials":"AMAT","on semi":"ON",
        "skyworks":"SWKS","mobileye":"MBLY",
        # AI / Software
        "palantir":"PLTR","salesforce":"CRM","adobe":"ADBE","oracle":"ORCL",
        "servicenow":"NOW","snowflake":"SNOW","shopify":"SHOP",
        "coinbase":"COIN","uber":"UBER","roblox":"RBLX","unity":"U",
        "uipath":"PATH","pathways":"PATH","microstrategy":"MSTR",
        "c3ai":"AI","c3.ai":"AI","soundhound":"SOUN","bigbear":"BBAI",
        "crowdstrike":"CRWD","datadog":"DDOG","cloudflare":"NET",
        "mongo":"MDB","mongodb":"MDB","elastic":"ESTC","twilio":"TWLO",
        "hubspot":"HUBS","okta":"OKTA","zscaler":"ZS","palo alto":"PANW",
        "fortinet":"FTNT","sentinelone":"S",
        # Meme / Retail Favorites
        "gamestop":"GME","gme":"GME","amc":"AMC","bbby":"BBBYQ",
        "bed bath":"BBBYQ","sofi":"SOFI","wish":"WISH",
        "clover health":"CLOV","lucid":"LCID","rivian":"RIVN",
        "nio":"NIO","xpeng":"XPEV","li auto":"LI",
        "virgin galactic":"SPCE","chamath":"SPCE",
        # Finance / Crypto
        "robinhood":"HOOD","paypal":"PYPL","square":"XYZ","block":"XYZ",
        "visa":"V","mastercard":"MA","jpmorgan":"JPM","jp morgan":"JPM",
        "bank of america":"BAC","morgan stanley":"MS","charles schwab":"SCHW",
        "blackstone":"BX","blackrock":"BLK","kkr":"KKR","apollo":"APO","brookfield":"BAM",
        "goldman":"GS","goldman sachs":"GS","marathon digital":"MARA",
        "riot":"RIOT","cleanspark":"CLSK","bitdeer":"BTDR",
        "citigroup":"C","wells fargo":"WFC","american express":"AXP",
        # Defense / Aerospace
        "lockheed":"LMT","lockheed martin":"LMT","raytheon":"RTX",
        "northrop":"NOC","northrop grumman":"NOC","boeing":"BA",
        "general dynamics":"GD","bae systems":"BAESY","l3harris":"LHX",
        "bwxt":"BWXT","kratos":"KTOS",
        # Industrials / Power
        "eaton":"ETN","ge vernova":"GEV","vernova":"GEV",
        # Energy
        "nextera":"NEE","constellation energy":"CEG","cameco":"CCJ",
        "first solar":"FSLR","exxon":"XOM","exxonmobil":"XOM",
        "chevron":"CVX","conocophillips":"COP","enphase":"ENPH",
        "vistra":"VST","uranium energy":"UEC","oklo":"OKLO","nuscale":"SMR",
        "nano nuclear":"NNE","shell":"SHEL","bp":"BP",
        # Space
        "spacex":"SPCX","space x":"SPCX","space exploration":"SPCX","starlink":"SPCX",
        "rocket lab":"RKLB","ast spacemobile":"ASTS","intuitive machines":"LUNR",
        "redwire":"RDW","momentus":"MNTS","spire":"SPIR","spire global":"SPIR",
        "planet labs":"PL","ionq":"IONQ","d-wave":"QBTS","rigetti":"RGTI",
        # Biotech / Healthcare
        "intuitive surgical":"ISRG","illumina":"ILMN","teladoc":"TDOC",
        "veeva":"VEEV","recursion":"RXRX","crispr":"CRSP",
        "moderna":"MRNA","pfizer":"PFE","unitedhealth":"UNH",
        "johnson":"JNJ","johnson & johnson":"JNJ","abbvie":"ABBV",
        "eli lilly":"LLY","lilly":"LLY","novo nordisk":"NVO",
        "merck":"MRK","amgen":"AMGN","gilead":"GILD",
        "regeneron":"REGN","vertex":"VRTX","biogen":"BIIB",
        # Industrial / Agri
        "deere":"DE","john deere":"DE","caterpillar":"CAT",
        "honeywell":"HON","3m":"MMM","ge":"GE","general electric":"GE",
        "archer daniels":"ADM","mosaic":"MOS","nutrien":"NTR",
        "union pacific":"UNP","ups":"UPS","fedex":"FDX",
        # Mining / Materials
        "newmont":"NEM","freeport":"FCX","mp materials":"MP",
        "lithium americas":"LAC","albemarle":"ALB","southern copper":"SCCO",
        "barrick gold":"GOLD","vale":"VALE",
        # Consumer
        "costco":"COST","walmart":"WMT","target":"TGT",
        "nike":"NKE","starbucks":"SBUX","mcdonalds":"MCD",
        "disney":"DIS","coca cola":"KO","coke":"KO","pepsi":"PEP",
        "procter":"PG","procter & gamble":"PG","home depot":"HD","lowes":"LOW",
        # Telecom / Media
        "att":"T","at&t":"T","verizon":"VZ","t-mobile":"TMUS",
        "comcast":"CMCSA","roku":"ROKU","spotify":"SPOT",
        # Chinese / Intl
        "alibaba":"BABA","baba":"BABA","tencent":"TCEHY","jd":"JD",
        "pinduoduo":"PDD","pdd":"PDD","baidu":"BIDU",
        "sea limited":"SE","grab":"GRAB","mercadolibre":"MELI",
        "samsung":"SSNLF","toyota":"TM","sony":"SONY",
        # ETFs (popular)
        "spy":"SPY","qqq":"QQQ","arkk":"ARKK","ark":"ARKK",
        "dia":"DIA","iwm":"IWM","voo":"VOO","vti":"VTI",
        "soxx":"SOXX","xlf":"XLF","xle":"XLE",
    }

    # Build reverse map: TICKER → display name for autocomplete
    TICKER_DISPLAY = {}
    for name, tick in NAME_TO_TICKER.items():
        if tick not in TICKER_DISPLAY or len(name) > len(TICKER_DISPLAY[tick]):
            TICKER_DISPLAY[tick] = name.title()
    SEARCH_OPTIONS = [""] + sorted(
        [f"{t} — {TICKER_DISPLAY.get(t, t)}" for t in set(NAME_TO_TICKER.values())]
    )

    # Safe pre-fill from quick-analyze buttons
    if "quick_ticker" in st.session_state:
        st.session_state["selected_ticker"] = st.session_state.pop("quick_ticker")
    if "selected_ticker" not in st.session_state:
        st.session_state["selected_ticker"] = ""

    # Capture and consume selected_ticker from Analyze buttons
    direct_ticker = ""
    if st.session_state["selected_ticker"]:
        direct_ticker = st.session_state["selected_ticker"]
        st.session_state["selected_ticker"] = ""

    col_s, col_or, col_c, col_b = st.columns([5, 0.5, 2.5, 1])
    with col_s:
        search_pick = st.selectbox(
            "Search stocks",
            options=SEARCH_OPTIONS,
            index=0,
            placeholder="🔍 Search — type name or ticker (e.g. Intel, TSLA, Nvidia)",
            label_visibility="collapsed",
            key="search_box",
        )
    with col_or:
        st.markdown("<div style='text-align:center;color:#6a7a9a;padding-top:8px;font-size:13px'>or</div>", unsafe_allow_html=True)
    with col_c:
        custom_ticker = st.text_input("Custom ticker",
                                      placeholder="Any ticker — BABA, SPOT…",
                                      label_visibility="collapsed",
                                      key="custom_text")
    with col_b:
        go_btn = st.button("Analyze", type="primary", use_container_width=True)

    # Resolve input: direct_ticker (from button click) > dropdown > custom text
    ticker_input = ""
    if direct_ticker:
        ticker_input = direct_ticker
    elif search_pick:
        ticker_input = search_pick.split(" — ")[0].strip()
    elif custom_ticker:
        ticker_input = custom_ticker.strip()
        resolved = NAME_TO_TICKER.get(ticker_input.lower())
        if resolved:
            ticker_input = resolved

    if not ticker_input:
        st.markdown("### 👁️ Louis' Standard Picks — by Theme")
        st.caption("These are Louis' pre-set conviction stocks per theme. Click any to analyze.")

        # Each entry: (ticker, why Louis likes it)
        LOUIS_STANDARD_PICKS = {
            "🤖 AI Extension": [
                ("NVDA",  "Jensen Huang. Owns the AI compute stack. Every AI dollar runs on his silicon."),
                ("AMD",   "Lisa Su's comeback. NVDA's only real rival for GPU dominance."),
                ("PLTR",  "AI for governments and defense. Stickiest enterprise AI contracts on earth."),
                ("SMCI",  "Builds the servers AI runs on. Quietly essential infrastructure."),
                ("IONQ",  "Quantum computing before it's obvious. High risk, generational upside."),
            ],
            "⚡ Energy Infrastructure": [
                ("CEG",   "Nuclear power comeback leader. AI data centres are its biggest new customer."),
                ("VST",   "Power generation giant. Benefits from surging electricity demand from AI."),
                ("CCJ",   "Uranium miner. Nuclear renaissance means uranium scarcity is real."),
                ("NEE",   "Largest clean energy operator in the US. Wind, solar, and grid scale."),
                ("FSLR",  "US-made solar panels. Trade war shields it from Chinese competition."),
            ],
            "🚀 Space Tech": [
                ("RKLB",  "Peter Beck's rocket company. Making small satellite launch routine and cheap."),
                ("ASTS",  "Space-based broadband. Connecting every phone on earth via satellite."),
                ("LUNR",  "Lunar logistics. First private lander on the moon. NASA contracts."),
                ("LMT",   "Lockheed Martin. Hypersonics, F-35, missile defense. War spending goes here."),
                ("NOC",   "Northrop Grumman. B-21 stealth bomber and space systems. Defense royalty."),
            ],
            "🦾 Robotics": [
                ("TSLA",  "Optimus humanoid robot. Elon's next moonshot after EVs."),
                ("ISRG",  "Surgical robotics monopoly. Da Vinci is in every major hospital."),
                ("PATH",  "Robotic process automation. Automates office work at enterprise scale."),
                ("TER",   "Tests the chips and robots that run AI. Behind the scenes but critical."),
                ("HON",   "Industrial automation giant. Smart factories and building intelligence."),
            ],
            "🪙 Tokenized Finance": [
                ("COIN",  "Crypto's most credible exchange. Regulation is its moment, not its threat."),
                ("MSTR",  "Michael Saylor's Bitcoin treasury bet. Most concentrated BTC proxy."),
                ("XYZ",   "Jack Dorsey's payments + Bitcoin play. Cash App is the retail crypto wallet."),
                ("HOOD",  "Retail trading platform adding crypto. Young money's first broker."),
                ("PYPL",  "PayPal adding stablecoin and crypto rails to 400M+ user base."),
            ],
            "🧬 Medical AI": [
                ("ISRG",  "Surgical robot monopoly. AI-guided precision surgery is its next layer."),
                ("ILMN",  "DNA sequencing at scale. The foundation of precision medicine."),
                ("RXRX",  "AI drug discovery. Using machine learning to find drugs faster."),
                ("TDOC",  "Telehealth + AI diagnostics. Virtual care at scale with AI triage."),
                ("VEEV",  "Cloud software for life sciences. Every pharma company runs on it."),
            ],
            "🌾 Future Food Supply": [
                ("DE",    "John Deere. Autonomous farming equipment. Precision ag at scale."),
                ("ADM",   "Archer-Daniels-Midland. Largest grain trader. Controls global food flow."),
                ("MOS",   "Mosaic. Potash and phosphate. Ukraine war proved fertiliser is strategic."),
                ("NTR",   "Nutrien. World's largest fertiliser producer. Food security is its moat."),
                ("VITL",  "Vital Farms. Ethical food brand growing fast. Premium consumer shift."),
            ],
            "🛡️ Defense / Geopolitical": [
                ("LMT",   "Lockheed Martin. F-35, hypersonics, missile defense. NATO's backbone."),
                ("RTX",   "Raytheon. Patriot missiles, Stinger, and guided munitions. In high demand."),
                ("NOC",   "Northrop. B-21 bomber and space defense. Long-cycle government contracts."),
                ("BWXT",  "Nuclear propulsion for navy ships and submarines. Pure scarcity play."),
                ("CACI",  "Government IT and intelligence contractor. Cyber and surveillance growth."),
            ],
            "🏛️ HNWI Wealth": [
                ("BX",    "Blackstone. Largest alternative asset manager. HNWI money flows here."),
                ("KKR",   "KKR. Private equity powerhouse expanding into retail wealth products."),
                ("APO",   "Apollo Global. Credit and private markets giant. Fastest growing alt manager."),
                ("BAM",   "Brookfield. Real assets and infrastructure. Serious capital, serious returns."),
                ("GS",    "Goldman Sachs. The bank that moves elite money globally."),
            ],
            "💎 Scarcity / Strategic Asset": [
                ("MP",    "MP Materials. Only rare earth miner in the US. Critical for magnets and EVs."),
                ("CCJ",   "Cameco. Top uranium miner. Nuclear revival means uranium demand spikes."),
                ("FCX",   "Freeport-McMoRan. Copper king. EV and AI infrastructure need copper."),
                ("NEM",   "Newmont. Gold. Inflation hedge and crisis safe haven."),
                ("LAC",   "Lithium Americas. US lithium for EV batteries. Government-backed."),
            ],
        }

        for seg, picks in LOUIS_STANDARD_PICKS.items():
            st.markdown(f"<div style='font-size:15px;font-weight:700;color:#ffffff;margin:16px 0 8px 0'>{seg}</div>",
                        unsafe_allow_html=True)
            cols = st.columns(5)
            for col_obj, (t, why) in zip(cols, picks):
                with col_obj:
                    st.markdown(f"""
                    <div style="background:#1c2130;border-radius:10px;padding:12px;
                                border-top:3px solid #3a4460;margin-bottom:4px">
                        <div style="font-size:16px;font-weight:800;color:#ffffff">{t}</div>
                        <div style="font-size:11px;color:#b0bcd4;margin-top:4px;line-height:1.4">{why}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Analyze {t}", key=f"lp_{seg}_{t}", use_container_width=True):
                        st.session_state["selected_ticker"] = t
                        st.rerun()
        st.divider()

    if ticker_input:
        ticker = ticker_input.strip().upper()
        with st.spinner(f"Loading {ticker}…"):
            try:
                info, hist, inst, maj, opts_calls, opts_puts, opt_dates = fetch(ticker)
            except Exception as e:
                st.error(f"Error fetching {ticker}: {e}")
                st.stop()

        price = safe(info, "currentPrice", "regularMarketPrice", default=None)
        if price is None:
            st.error(f"No data found for **{ticker}**. Check the symbol and try again.")
            st.stop()

        # ── HEADER ────────────────────────────────────────────
        name  = info.get("longName") or info.get("shortName", ticker)
        prev  = safe(info, "previousClose", default=price)
        chg   = price - prev
        chgp  = chg / prev * 100 if prev else 0

        st.markdown(f"## {name}  `{ticker}`")
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("Price",      f"${price:,.2f}", f"{chg:+.2f} ({chgp:+.2f}%)")
        h2.metric("Market Cap", fmt(safe(info, "marketCap"), "$"))
        h3.metric("Sector",     info.get("sector", "N/A"))
        h4.metric("52W Range",  f"${safe(info,'fiftyTwoWeekLow',default=0):.0f} – ${safe(info,'fiftyTwoWeekHigh',default=0):.0f}")

        # ── PRICE CHART ───────────────────────────────────────
        if not hist.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"], mode="lines", name="Price",
                line=dict(color="#4CAF50", width=2),
                fill="tozeroy", fillcolor="rgba(76,175,80,0.08)"
            ))
            if len(hist) >= 50:
                fig.add_trace(go.Scatter(
                    x=hist.index, y=hist["Close"].rolling(50).mean(),
                    mode="lines", name="50-day MA",
                    line=dict(color="#FFC107", width=1.5, dash="dot")
                ))
            if len(hist) >= 200:
                fig.add_trace(go.Scatter(
                    x=hist.index, y=hist["Close"].rolling(200).mean(),
                    mode="lines", name="200-day MA",
                    line=dict(color="#2196F3", width=1.5, dash="dot")
                ))
            fig.update_layout(
                template="plotly_dark", height=320,
                margin=dict(l=0, r=0, t=10, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                xaxis_title="", yaxis_title="USD"
            )
            st.plotly_chart(fig, use_container_width=True)

        # ── KEY FINANCIALS ────────────────────────────────────
        st.subheader("📊 Key Financials")
        f1, f2, f3, f4, f5, f6, f7 = st.columns(7)
        f1.metric("Revenue",    fmt(safe(info,"totalRevenue"), "$"))
        f2.metric("Cash",       fmt(safe(info,"totalCash"), "$"))
        f3.metric("Total Debt", fmt(safe(info,"totalDebt"), "$"))
        f4.metric("Assets",     fmt(safe(info,"totalAssets"), "$"))
        f5.metric("EPS (TTM)",  fmt(safe(info,"trailingEps"), "$", dec=2))
        f6.metric("P/E",        fmt(safe(info,"trailingPE"), dec=1))
        f7.metric("Profit Mgn", f"{(safe(info,'profitMargins',default=0) or 0)*100:.1f}%")

        st.divider()

        # ── COMPUTE SCORES ────────────────────────────────────
        scores = compute_all_scores(info, hist, inst, maj)

        # ── REDDIT SOCIAL INTELLIGENCE (boosts scores) ────────
        with st.spinner("Scanning Reddit discussions…"):
            social = scan_reddit(ticker)
        scores = apply_social_boosts(scores, social)

        cfis   = cfis_composite(scores)
        opp    = opportunity_score(cfis, info, hist)

        # ── MARKET HEALTH ASSESSMENT ───────────────────────────
        health = compute_health_scores(scores)
        render_market_health_scores(scores, health)

        st.divider()

        # ── CAPITAL MIGRATION INTELLIGENCE (REASONING FIRST) ──
        cm = compute_capital_migration(info, hist, ticker)
        render_capital_migration(cm, ticker)

        st.divider()

        # ── THREE-BRAIN CONVICTION ENGINE ─────────────────────
        conviction, decision, dec_color, dec_reason, narrative, quant_s, fund_s, cm_brain_s, cm_engine_s = render_three_brains(scores, cm, info, hist)

        st.divider()

        # ── CFIS HUNTER — CAPITAL FLOW PREDICTION ─────────────
        enriched = fetch_enriched_data(ticker)
        hunter = compute_hunter(info, hist, scores, cm, enriched)
        render_hunter(hunter, ticker, cm)

        st.divider()

        # ── CAPITAL FLOW INTELLIGENCE ─────────────────────────
        with st.spinner("Running Capital Flow Intelligence…"):
            ci = compute_capital_intelligence(ticker, info, hist, scores, cm, hunter)
            render_capital_intelligence(ci, ticker, hunter)

        st.divider()

        # ── LOUIS ACTION SIGNAL ───────────────────────────────
        render_louis_action_signal(ticker, cm, conviction, decision, dec_color, narrative, quant_s, fund_s, cm_brain_s, cm_engine_s)

        st.divider()

        # ── OPTIONS ANALYSIS ──────────────────────────────────
        render_options(opts_calls, opts_puts, opt_dates, info, ticker)

        st.divider()

        # ── DARK POOL ANALYSIS ────────────────────────────────
        render_dark_pool(info, hist)

        st.divider()

        # ── INSTITUTIONAL ACCUMULATION ────────────────────────
        render_institutional(info, inst, maj)

        st.divider()

        # ── REDDIT SOCIAL INTELLIGENCE ────────────────────────
        render_social_intelligence(social, ticker)

        st.divider()

        # ── OUTLOOKS ──────────────────────────────────────────
        st.subheader("🔮 Price Outlooks")
        outlooks = generate_outlooks(info, hist, conviction)
        o1, o2, o3, o4 = st.columns(4)
        for col, (period, data) in zip([o1, o2, o3, o4], outlooks.items()):
            pct = data["pct"]
            pc  = "#4CAF50" if pct >= 0 else "#f44336"
            col.markdown(f"""
            <div class="outlook-card">
                <div style="font-size:11px;color:#8a9bb5;margin-bottom:8px">{period.upper()}</div>
                <div style="font-size:22px;font-weight:700">{data['direction']}</div>
                <div style="font-size:20px;font-weight:700;color:{pc};margin:4px 0">{pct:+.1f}%</div>
                <div style="font-size:12px;color:#b0b8cc">${data['price']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ── FINAL INVESTMENT DECISION ─────────────────────────
        st.subheader("📌 Final Investment Decision")
        thesis = cm["thesis"]
        h_zc = hunter["action_color"]
        h_conv = hunter.get("conviction", {})
        h_conv_s = h_conv.get("score", 0) if isinstance(h_conv, dict) else 0

        r1, r2 = st.columns([1, 2])
        with r1:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0a0a1e,#1a0a2e);border-radius:14px;padding:24px;text-align:center;border:2px solid {h_zc}">
                <div style="font-size:10px;color:#8a9bb5;letter-spacing:2px;margin-bottom:4px">CIO DECISION</div>
                <div style="display:inline-block;background:{h_zc};color:#000;font-weight:900;font-size:20px;padding:8px 28px;border-radius:24px;letter-spacing:3px">{hunter['action_icon']} {hunter['action']}</div>
                <div style="font-size:12px;color:#c8d4e8;margin-top:8px">{hunter['action_desc']}</div>
                <div style="margin-top:16px;display:flex;justify-content:center;gap:20px">
                    <div>
                        <div style="font-size:10px;color:#8a9bb5">HUNTER</div>
                        <div style="font-size:28px;font-weight:800;color:{h_zc}">{hunter['hunter_score']:.0f}</div>
                    </div>
                    <div>
                        <div style="font-size:10px;color:#8a9bb5">CONVICTION</div>
                        <div style="font-size:28px;font-weight:800;color:{'#4CAF50' if h_conv_s>=85 else ('#FFC107' if h_conv_s>=60 else '#ef5350')}">{h_conv_s:.0f}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with r2:
            st.markdown(f"""<div class="section-box">
                <b style="color:#7c3aed">Investment Thesis:</b> {thesis['investment_thesis']}
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="section-box">
                <b style="color:#f44336">Risk Thesis:</b> {thesis['risk_thesis']}
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="section-box">
                <b style="color:#FFC107">Catalyst:</b> {thesis['catalyst']}
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="section-box">
                <b style="color:#FF9800">Invalidation:</b> {thesis.get('invalidation','')}
            </div>""", unsafe_allow_html=True)

        st.divider()

        # ── COMPANY DETAILS ───────────────────────────────────
        with st.expander("📋 Full Company Details"):
            bio = info.get("longBusinessSummary", "")
            if bio:
                st.markdown(bio[:600] + ("…" if len(bio) > 600 else ""))
            cols = {
                "Exchange": info.get("exchange","N/A"),
                "Country": info.get("country","N/A"),
                "Employees": f"{info.get('fullTimeEmployees',0):,}" if info.get("fullTimeEmployees") else "N/A",
                "Dividend Yield": f"{(safe(info,'dividendYield',default=0) or 0)*100:.2f}%",
                "Beta": fmt(safe(info,"beta"), dec=2),
                "Forward P/E": fmt(safe(info,"forwardPE"), dec=1),
                "Price/Book": fmt(safe(info,"priceToBook"), dec=2),
                "Analyst Target": fmt(safe(info,"targetMeanPrice"), "$"),
                "Analyst Rating": info.get("recommendationKey","N/A").replace("_"," ").title(),
                "# Analysts": str(int(safe(info,"numberOfAnalystOpinions",default=0) or 0)),
                "Short Ratio": fmt(safe(info,"shortRatio"), dec=1),
                "Shares Outstanding": fmt(safe(info,"sharesOutstanding")),
            }
            for k, v in cols.items():
                st.markdown(f"**{k}:** {v}")


# ═══════════════════════════════════════════════════════════════
# TOP 30 PAGE
# ═══════════════════════════════════════════════════════════════
elif page == "2️⃣ Capital Migration":
    st.title("🌊 Capital Migration™")
    st.caption("Where is capital flowing now, and where is capital likely to flow next?")

    # ── WHY THIS LIST EXISTS — THESIS HEADER ──────────────────
    TOP30_SECTORS = {
        "🤖 AI & Compute":       ["NVDA","AMD","AVGO","PLTR","SNOW","CRM","ADBE","ORCL","NOW"],
        "☁️ Cloud & Platform":    ["MSFT","AMZN","GOOGL","META","AAPL","NFLX","UBER","SHOP"],
        "🪙 Crypto & Fintech":   ["COIN","XYZ","HOOD"],
        "🔬 Quantum & Frontier":  ["IONQ","QBTS"],
        "🦾 Robotics & Auto":    ["TSLA","PATH","U","RBLX"],
        "🛡️ Enterprise AI":      ["AI","ARM","SMCI","MRVL","ANET"],
    }

    st.markdown(
        '<div style="background:#111827;border:1px solid #2e3550;border-radius:14px;padding:20px 24px;margin-bottom:20px">'
        '<div style="font-size:16px;font-weight:800;color:#ffffff;margin-bottom:10px">📐 What is this list?</div>'
        '<div style="font-size:13px;color:#e2e8f0;line-height:1.8;margin-bottom:14px">'
        '<b>Time Horizon: 3–10 years.</b> These are not swing trades. '
        'This is a conviction list of 30 companies Louis believes will define the next decade of civilization — '
        'the infrastructure of AI, energy, space, finance, and automation. '
        'Every stock here is scored on 18 CFIS-X categories and ranked by composite quality. '
        'The question isn\'t "will this go up next week?" — it\'s "will capital keep flowing here for years?"'
        '</div>'
        '<div style="font-size:13px;color:#b0bcd4;line-height:1.7;margin-bottom:14px">'
        '<b>Why these 30?</b> Three filters: '
        '<b>(1)</b> They sit inside a structural megatrend — AI, energy transition, tokenized finance, robotics, or space. '
        '<b>(2)</b> They have a durable competitive advantage — moat, network effects, or government dependency. '
        '<b>(3)</b> The smartest capital in the world — institutions, sovereign funds, and visionary founders — is already positioned.'
        '</div>'
        '</div>', unsafe_allow_html=True
    )

    # Sector breakdown pills
    sector_html = ""
    for seg, tickers in TOP30_SECTORS.items():
        t_list = ", ".join(tickers)
        sector_html += (
            f'<div style="background:#1c2130;border-radius:10px;padding:10px 14px;margin:4px 0;'
            f'display:flex;align-items:center;gap:10px">'
            f'<span style="font-size:14px;font-weight:700;color:#ffffff;min-width:170px">{seg}</span>'
            f'<span style="font-size:11px;color:#8a9bb5">{t_list}</span>'
            f'<span style="font-size:11px;color:#FFC107;font-weight:700;min-width:20px;text-align:right">{len(tickers)}</span>'
            f'</div>'
        )
    st.markdown(
        f'<div style="margin-bottom:16px">'
        f'<div style="font-size:13px;font-weight:700;color:#8a9bb5;margin-bottom:6px;letter-spacing:1px">SECTOR BREAKDOWN</div>'
        f'{sector_html}</div>', unsafe_allow_html=True
    )

    cap_col, btn_col = st.columns([6, 1])
    cap_col.caption("Ranked by CFIS-X score · Click any column header to sort · Hover for details")
    if btn_col.button("🔄 Refresh", key="refresh_top30"):
        fetch_top30.clear()
        st.rerun()

    try:
        with st.spinner("Scoring 30 stocks… ~45s on first load"):
            df = fetch_top30()
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        st.error("Could not load data. Click 🔄 Refresh above or try again in a minute.")
    else:
        # ── Top 3 podium ──────────────────────────────────────
        top3 = df.head(3)
        t1, t2, t3 = st.columns(3)
        for col_obj, (_, row), medal in zip([t1,t2,t3], top3.iterrows(), ["🥇","🥈","🥉"]):
            sc = row["CFIS-X"]
            c  = "#4CAF50" if sc >= 65 else "#FFC107"
            why = TOP_30_WHY.get(row["Ticker"], "")
            col_obj.markdown(f"""
            <div style="background:#1c2130;border-radius:12px;padding:20px;text-align:center;border:2px solid {c}">
                <div style="font-size:28px">{medal}</div>
                <div style="font-size:24px;font-weight:900;color:#fff">{row['Ticker']}</div>
                <div style="font-size:12px;color:#b0bcd4;margin-bottom:6px">{row['Name']}</div>
                <div style="font-size:42px;font-weight:900;color:{c};line-height:1">{sc}</div>
                <div style="font-size:11px;color:#8a9bb5;margin-bottom:6px">CFIS-X Score</div>
                <div style="font-size:13px;color:#2196F3">Opportunity: {row['Opportunity']}</div>
                <div style="font-size:12px;color:#e8ecf4;margin-top:4px">{row['Price']}</div>
                <div style="font-size:11px;color:#b0bcd4;margin-top:8px;line-height:1.4;font-style:italic">{why}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Clean ranked table — no segments ─────────────────
        st.dataframe(
            df,
            use_container_width=True,
            height=800,
            column_config={
                "Ticker":       st.column_config.TextColumn("Ticker", width="small"),
                "Name":         st.column_config.TextColumn("Company", width="medium"),
                "Price":        st.column_config.TextColumn("Price", width="small"),
                "Louis Pick":   st.column_config.TextColumn(
                    "👁️ Louis Pick",
                    help="Louis' CALL / PUT / HOLD verdict based on strategic intuition + options flow",
                    width="small"
                ),
                "CFIS-X": st.column_config.ProgressColumn(
                    "CFIS-X", min_value=0, max_value=100, format="%d",
                    help="Composite score across 18 categories"
                ),
                "Opportunity": st.column_config.ProgressColumn(
                    "Opportunity", min_value=0, max_value=100, format="%d",
                    help="How attractive the current entry point is"
                ),
                "30D Target":   st.column_config.TextColumn(
                    "⚠️ 30D Scenario",
                    help="30-day price scenario — signal-based estimate, not a prediction",
                    width="medium"
                ),
                "90D Target":   st.column_config.TextColumn(
                    "⚠️ 90D Scenario",
                    help="90-day price scenario — signal-based estimate, not a prediction",
                    width="medium"
                ),
                "Econ. Moat": st.column_config.ProgressColumn(
                    "Economic Moat", min_value=0, max_value=100, format="%d",
                    help="Pricing power, margins, competitive durability"
                ),
                "Rev. Quality": st.column_config.ProgressColumn(
                    "Revenue Quality", min_value=0, max_value=100, format="%d",
                    help="Revenue growth, consistency, and margin expansion"
                ),
                "Fin. Fortress": st.column_config.ProgressColumn(
                    "Fortress Balance Sheet", min_value=0, max_value=100, format="%d",
                    help="Liquidity, debt management, financial resilience"
                ),
                "Why It's Here": st.column_config.TextColumn(
                    "Why It's Here", width="large",
                    help="Louis' plain-English reason for this stock being in the Top 30"
                ),
            }
        )

        # ── Bar chart ─────────────────────────────────────────
        fig_bar = px.bar(
            df.head(15), x="Ticker", y="CFIS-X",
            color="CFIS-X", color_continuous_scale=["#f44336","#FFC107","#4CAF50"],
            range_color=[0,100], title="Top 15 by CFIS-X Score",
            template="plotly_dark", text="CFIS-X"
        )
        fig_bar.update_traces(textposition="outside", textfont_color="#ffffff")
        fig_bar.update_layout(height=380, margin=dict(t=50,b=0))
        st.plotly_chart(fig_bar, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# LOUIS' PICKS PAGE
# ═══════════════════════════════════════════════════════════════
elif page == "3️⃣ Opportunity Engine":

    # ── Theme definitions ──────────────────────────────────────
    THEMES = {
        "🤖 AI Extended": {
            "tickers": ["NVDA", "AMD", "SMCI", "PLTR", "AI", "IONQ", "SOUN", "BBAI", "ARBB", "GFAI"],
            "color": "#7c3aed",
            "border": "#a855f7",
            "geo": (
                "The AI arms race is no longer just Silicon Valley — it's geopolitical. "
                "The US, China, and EU are racing to dominate AI infrastructure, compute, and models. "
                "Export controls on chips are reshaping supply chains. "
                "Companies controlling compute, data pipelines, and enterprise AI deployment sit at the center of this decade's most important power shift."
            ),
            "thesis": "Own the picks and shovels of the AI gold rush — chips, inference infrastructure, and enterprise AI platforms.",
        },
        "⚡ Energy": {
            "tickers": ["CEG", "VST", "NRG", "NEE", "FSLR", "ENPH", "CCJ", "UEC", "CVX", "XOM"],
            "color": "#b45309",
            "border": "#f59e0b",
            "geo": (
                "Energy is the new leverage point in global power. Russia's war in Ukraine rewired Europe's energy dependency. "
                "The Middle East remains a flashpoint. Meanwhile, AI data centers are driving explosive electricity demand — "
                "nuclear is making a comeback, and clean energy is now a national security priority across G7 nations. "
                "Energy stocks sit at the crossroads of geopolitics, climate policy, and industrial demand."
            ),
            "thesis": "Power the world — from nuclear renaissance and LNG exports to solar and grid modernization plays.",
        },
        "🚀 Space Tech": {
            "tickers": ["RKLB", "ASTS", "LUNR", "PL", "SPCE", "BWXT", "BA", "LMT", "NOC", "RTX"],
            "color": "#0e7490",
            "border": "#06b6d4",
            "geo": (
                "Space is the new geopolitical frontier. The US, China, and private capital are racing to control low-Earth orbit, "
                "lunar resources, and satellite communications. Starlink changed the battlefield in Ukraine. "
                "GPS, surveillance, and communications infrastructure increasingly runs through space. "
                "Governments are spending aggressively — and private launch economics are collapsing costs."
            ),
            "thesis": "The new space economy — launch, satellite broadband, lunar logistics, and defense contractors pivoting to space.",
        },
        "🦾 Robotics": {
            "tickers": ["TSLA", "ISRG", "ABB", "HON", "FANUY", "NVDA", "PATH", "BRZE", "IROBOT", "TER"],
            "color": "#065f46",
            "border": "#10b981",
            "geo": (
                "Demographics are destiny. Aging populations in the US, Europe, Japan, and China are creating a labour shortage "
                "that only automation can solve. Meanwhile, reshoring of manufacturing to the US and allied nations is driving "
                "massive investment in smart factories. Humanoid robots are moving from science fiction to factory floors — "
                "Tesla, Figure, and Boston Dynamics are all racing to deploy at scale."
            ),
            "thesis": "Automate the physical world — industrial robots, surgical systems, humanoids, and the software that runs them.",
        },
        "🪙 Tokenized Finance": {
            "tickers": ["COIN", "MSTR", "HOOD", "XYZ", "PYPL", "CME", "ICE", "MARA", "RIOT", "CLSK"],
            "color": "#1e3a5f",
            "border": "#3b82f6",
            "geo": (
                "The financial system is being quietly rebuilt on blockchain rails. Tokenization of real-world assets — "
                "treasuries, real estate, equities — is accelerating as institutions seek programmable, 24/7 settlement. "
                "US crypto regulation is finally clearing, opening institutional floodgates. "
                "Central banks are exploring digital currencies. The companies building the on-ramps, exchanges, "
                "and custody infrastructure for this transition are in a once-in-a-generation position."
            ),
            "thesis": "Own the plumbing of the new financial system — crypto exchanges, digital asset infrastructure, and fintech bridges.",
        },
        "🌾 Future Food": {
            "tickers": ["BYND", "APPH", "AQB", "VITL", "SMPL", "ADM", "BG", "MOS", "NTR", "DE"],
            "color": "#3f6212",
            "border": "#84cc16",
            "geo": (
                "Feeding 10 billion people by 2050 is one of civilization's hardest problems. Climate disruption is hitting "
                "crop yields. Water scarcity is a growing crisis from the American West to the Middle East. "
                "Fertilizer supply was disrupted by the Ukraine war — Russia and Belarus control ~40% of global potash. "
                "Alternative proteins, vertical farming, precision agriculture, and agricultural biotech are all racing "
                "to solve the equation. The companies that crack affordable, sustainable nutrition will be enormous."
            ),
            "thesis": "Feed the future — agtech, alternative proteins, fertilizer supply chains, and precision farming.",
        },
    }

    pass  # fetch_theme defined at module level below THEMES dict

    # ── Page header ────────────────────────────────────────────
    st.markdown("""
    <div style="margin-bottom:8px">
        <span style="font-size:32px;font-weight:900;color:#ffffff">🎯 Opportunity Engine™</span><br>
        <span style="font-size:15px;color:#b0bcd4">What should you buy, observe, avoid, or prepare for now?</span>
    </div>
    """, unsafe_allow_html=True)

    # ── AUTO-GENERATED OPPORTUNITY LISTS ──────────────────────
    opp_tab = st.radio("Time Horizon", ["15-Day", "30-Day", "90-Day", "3-10 Year Legacy", "All Themes"], horizontal=True, label_visibility="collapsed")
    with st.spinner(f"Scanning {len(FULL_UNIVERSE)} stocks…"):
        try:
            all_opps = scan_opportunities(tuple(FULL_UNIVERSE))
        except Exception:
            all_opps = []
    if all_opps:
        if opp_tab == "15-Day":
            st.subheader("🔥 Best 15-Day Opportunities")
            st.caption("Focus: momentum, catalyst, options flow, technical breakout")
            filtered = filter_opportunities(all_opps, "15d")
            render_opportunity_table(filtered, count=12)
        elif opp_tab == "30-Day":
            st.subheader("📈 Best 30-Day Opportunities")
            st.caption("Focus: momentum + theme strength + near-term catalyst")
            filtered = filter_opportunities(all_opps, "30d")
            render_opportunity_table(filtered, count=12)
        elif opp_tab == "90-Day":
            st.subheader("🌊 Best 90-Day Opportunities")
            st.caption("Focus: capital migration, earnings revision, institutional flow")
            filtered = filter_opportunities(all_opps, "90d")
            render_opportunity_table(filtered, count=12)
        elif opp_tab == "3-10 Year Legacy":
            st.subheader("🏛️ Long-Term Legacy Holdings")
            st.caption("Focus: moat, bottleneck, cash flow, balance sheet, future demand")
            filtered = filter_opportunities(all_opps, "legacy")
            render_opportunity_table(filtered, count=25)
        else:
            st.subheader("📊 All Stocks by Theme")
            themes_found = {}
            for r in all_opps:
                t = r["theme"]
                if t not in themes_found:
                    themes_found[t] = []
                themes_found[t].append(r)
            for theme_name, theme_stocks in sorted(themes_found.items(), key=lambda x: -len(x[1])):
                td = THEME_KNOWLEDGE.get(theme_name, {})
                with st.expander(f"{td.get('icon','📊')} {theme_name} ({len(theme_stocks)} stocks)", expanded=False):
                    sorted_stocks = sorted(theme_stocks, key=lambda r: r["conviction"], reverse=True)
                    render_opportunity_table(sorted_stocks, count=len(sorted_stocks))
    else:
        st.info("Loading opportunity data…")

    st.divider()

    # ── COMBO PLAYS ───────────────────────────────────────────
    with st.expander("🎯 **Louis' Combo Plays** — CALL & PUT Strategies (30–90 Day)", expanded=True):
        try:
            with st.spinner("Scanning 40+ stocks for optimal combo plays…"):
                call_combo, put_combo, c30, c90, p30, p90 = scan_combo_plays()
        except Exception:
            call_combo, put_combo, c30, c90, p30, p90 = [], [], 0, 0, 0, 0

        # ── CALL COMBO ────────────────────────────────────────
        if call_combo:
            c90_color = "#4CAF50" if c90 >= 10 else "#FFC107"
            combo_tickers = " + ".join(c["ticker"] for c in call_combo)
            sectors_hit = ", ".join(sorted(set(c["sector"] for c in call_combo)))

            st.markdown(
                f'<div style="background:#0a2a0a;border:2px solid #4CAF50;border-radius:14px;padding:20px;margin-bottom:16px">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-bottom:14px">'
                f'<div>'
                f'<div style="font-size:12px;color:#8a9bb5;letter-spacing:2px">📈 CALL COMBO — BUY CALLS ON</div>'
                f'<div style="font-size:22px;font-weight:900;color:#4CAF50;margin-top:4px">{combo_tickers}</div>'
                f'<div style="font-size:11px;color:#8a9bb5;margin-top:4px">Sectors: {sectors_hit}</div>'
                f'</div>'
                f'<div style="text-align:right">'
                f'<div style="font-size:11px;color:#8a9bb5">Combined Avg Return Target</div>'
                f'<div style="font-size:14px;color:#4CAF50;font-weight:700">30D: {c30:+.1f}%</div>'
                f'<div style="font-size:22px;color:{c90_color};font-weight:900">90D: {c90:+.1f}%</div>'
                f'</div>'
                f'</div>', unsafe_allow_html=True
            )
            # Individual stock rows
            rows_html = ""
            for c in call_combo:
                sc_c = "#4CAF50" if c["cfis"] >= 65 else ("#FFC107" if c["cfis"] >= 45 else "#f44336")
                mom_c = "#4CAF50" if c["mom15"] >= 0 else "#f44336"
                rows_html += (
                    f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0;'
                    f'border-bottom:1px solid #1a3a1a">'
                    f'<div style="min-width:60px;font-size:15px;font-weight:800;color:#ffffff">{c["ticker"]}</div>'
                    f'<div style="min-width:140px;font-size:11px;color:#b0bcd4">{c["name"]}</div>'
                    f'<div style="min-width:70px;font-size:13px;color:#fff">${c["price"]:.2f}</div>'
                    f'<div style="min-width:60px;text-align:center">'
                    f'<div style="font-size:14px;font-weight:700;color:{sc_c}">{c["cfis"]}</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">CFIS-X</div></div>'
                    f'<div style="min-width:60px;text-align:center">'
                    f'<div style="font-size:14px;font-weight:700;color:#FFC107">{c["conviction"]}</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">Conviction</div></div>'
                    f'<div style="min-width:70px;text-align:center">'
                    f'<div style="font-size:13px;font-weight:700;color:#4CAF50">{c["pct30"]:+.1f}%</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">30D Target</div></div>'
                    f'<div style="min-width:70px;text-align:center">'
                    f'<div style="font-size:15px;font-weight:800;color:#4CAF50">{c["pct90"]:+.1f}%</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">90D Target</div></div>'
                    f'<div style="min-width:70px;text-align:center">'
                    f'<div style="font-size:13px;font-weight:700;color:{mom_c}">{c["mom15"]:+.1f}%</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">15D Momentum</div></div>'
                    f'</div>'
                )
            st.markdown(f'{rows_html}</div>', unsafe_allow_html=True)

            st.markdown(
                f'<div style="background:#0a2a0a;border-radius:8px;padding:10px 14px;margin:8px 0;'
                f'font-size:12px;color:#c8d4e8;line-height:1.6">'
                f'<strong style="color:#4CAF50">Why this combo:</strong> '
                f'These {len(call_combo)} stocks are selected for the highest combined 90-day upside across diversified sectors. '
                f'Each has CFIS-X ≥ 45, positive outlook, and bullish Louis signal alignment. '
                f'Buying calls on this basket spreads risk across {len(set(c["sector"] for c in call_combo))} sectors '
                f'while targeting a combined avg return of <b>{c90:+.1f}%</b> over 90 days.'
                f'</div>', unsafe_allow_html=True
            )

        if not call_combo:
            st.warning("CALL combo could not be generated — data still loading or market is closed. Try refreshing in a minute.")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── PUT COMBO ─────────────────────────────────────────
        if put_combo:
            p90_color = "#f44336" if p90 >= 5 else "#FFC107"
            put_tickers = " + ".join(c["ticker"] for c in put_combo)
            put_sectors = ", ".join(sorted(set(c["sector"] for c in put_combo)))

            st.markdown(
                f'<div style="background:#2a0a0a;border:2px solid #f44336;border-radius:14px;padding:20px;margin-bottom:16px">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-bottom:14px">'
                f'<div>'
                f'<div style="font-size:12px;color:#8a9bb5;letter-spacing:2px">📉 PUT COMBO — BUY PUTS ON</div>'
                f'<div style="font-size:22px;font-weight:900;color:#f44336;margin-top:4px">{put_tickers}</div>'
                f'<div style="font-size:11px;color:#8a9bb5;margin-top:4px">Sectors: {put_sectors}</div>'
                f'</div>'
                f'<div style="text-align:right">'
                f'<div style="font-size:11px;color:#8a9bb5">Combined Avg Downside Target</div>'
                f'<div style="font-size:14px;color:#f44336;font-weight:700">30D: {p30:+.1f}%</div>'
                f'<div style="font-size:22px;color:{p90_color};font-weight:900">90D: {p90:+.1f}%</div>'
                f'</div>'
                f'</div>', unsafe_allow_html=True
            )
            rows_html_p = ""
            for c in put_combo:
                sc_c = "#4CAF50" if c["cfis"] >= 65 else ("#FFC107" if c["cfis"] >= 45 else "#f44336")
                mom_c = "#4CAF50" if c["mom15"] >= 0 else "#f44336"
                rows_html_p += (
                    f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0;'
                    f'border-bottom:1px solid #3a1515">'
                    f'<div style="min-width:60px;font-size:15px;font-weight:800;color:#ffffff">{c["ticker"]}</div>'
                    f'<div style="min-width:140px;font-size:11px;color:#b0bcd4">{c["name"]}</div>'
                    f'<div style="min-width:70px;font-size:13px;color:#fff">${c["price"]:.2f}</div>'
                    f'<div style="min-width:60px;text-align:center">'
                    f'<div style="font-size:14px;font-weight:700;color:{sc_c}">{c["cfis"]}</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">CFIS-X</div></div>'
                    f'<div style="min-width:60px;text-align:center">'
                    f'<div style="font-size:14px;font-weight:700;color:#FFC107">{c["conviction"]}</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">Conviction</div></div>'
                    f'<div style="min-width:70px;text-align:center">'
                    f'<div style="font-size:13px;font-weight:700;color:#f44336">{c["pct30"]:+.1f}%</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">30D Target</div></div>'
                    f'<div style="min-width:70px;text-align:center">'
                    f'<div style="font-size:15px;font-weight:800;color:#f44336">{c["pct90"]:+.1f}%</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">90D Target</div></div>'
                    f'<div style="min-width:70px;text-align:center">'
                    f'<div style="font-size:13px;font-weight:700;color:{mom_c}">{c["mom15"]:+.1f}%</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">15D Momentum</div></div>'
                    f'</div>'
                )
            st.markdown(f'{rows_html_p}</div>', unsafe_allow_html=True)

            st.markdown(
                f'<div style="background:#2a0a0a;border-radius:8px;padding:10px 14px;margin:8px 0;'
                f'font-size:12px;color:#c8d4e8;line-height:1.6">'
                f'<strong style="color:#f44336">Why this combo:</strong> '
                f'These {len(put_combo)} stocks show the weakest combined outlook — low CFIS-X, poor momentum, '
                f'or bearish Louis signals. Buying puts on this basket targets a combined avg downside of '
                f'<b>{p90:+.1f}%</b> over 90 days across {len(set(c["sector"] for c in put_combo))} sectors. '
                f'Best used as a hedge or directional bearish play.'
                f'</div>', unsafe_allow_html=True
            )

        st.markdown(
            '<div style="font-size:11px;color:#6a7a9a;margin-top:8px;line-height:1.5">'
            '⚠️ <b>Disclaimer:</b> Combo plays are signal-based scenarios, not financial advice. '
            'Combined return targets are averaged estimates from CFIS-X outlooks — actual results depend on '
            'entry timing, strike selection, expiry, and market conditions. Always size positions appropriately '
            'and define your risk before entering any options trade.</div>', unsafe_allow_html=True
        )

    # ── MACRO EVENT: BOJ / YEN CARRY PUT COMBO ────────────────
    with st.expander("🇯🇵 **Macro Event PUT** — BOJ Rate Hike / Yen Carry Unwind (June 17)", expanded=True):

        # Reddit macro signals
        with st.spinner("Scanning Reddit for macro event signals…"):
            macro_signals = scan_reddit_macro()

        # Macro context header
        boj_total = macro_signals["boj_mentions"] + macro_signals["carry_mentions"]
        st.markdown(
            f'<div style="background:#1a0a2a;border:1px solid #7c3aed;border-radius:12px;padding:16px 20px;margin-bottom:16px">'
            f'<div style="font-size:14px;font-weight:800;color:#a855f7;margin-bottom:8px">🌍 MACRO THESIS — WHY THIS MATTERS RIGHT NOW</div>'
            f'<div style="font-size:13px;color:#e2e8f0;line-height:1.8;margin-bottom:12px">'
            f'<b>BOJ is targeting a historic 1% interest rate on June 17.</b> This is the biggest monetary policy shift in Japan in decades. '
            f'When Japan raises rates, the yen strengthens → yen carry trade unwinds → forced selling of US risk assets. '
            f'The August 2024 carry unwind crashed the Nikkei 12% in one day and dragged the S&P down 3-5%. '
            f'Stocks funded by cheap yen leverage — high-beta growth, crypto, pre-revenue speculation — get hit hardest. '
            f'Hedge funds and prop desks running leveraged long positions on yen-funded margin face forced liquidation.'
            f'</div>'
            f'<div style="display:flex;gap:16px;flex-wrap:wrap">'
            f'<div style="background:#7c3aed22;border-radius:8px;padding:8px 14px;text-align:center">'
            f'<div style="font-size:20px;font-weight:900;color:#a855f7">{boj_total}</div>'
            f'<div style="font-size:10px;color:#8a9bb5">BOJ/Carry Reddit Posts</div></div>'
            f'<div style="background:#7c3aed22;border-radius:8px;padding:8px 14px;text-align:center">'
            f'<div style="font-size:20px;font-weight:900;color:#f44336">{macro_signals["leverage_mentions"]}</div>'
            f'<div style="font-size:10px;color:#8a9bb5">Liquidation/Margin Posts</div></div>'
            f'<div style="background:#7c3aed22;border-radius:8px;padding:8px 14px;text-align:center">'
            f'<div style="font-size:20px;font-weight:900;color:#FFC107">{macro_signals["risk_off_mentions"]}</div>'
            f'<div style="font-size:10px;color:#8a9bb5">Risk-Off Posts</div></div>'
            f'</div>'
            f'</div>', unsafe_allow_html=True
        )

        # Reddit macro themes detected
        if macro_signals["themes"]:
            theme_pills = " ".join(
                f'<span style="background:#2a1040;border:1px solid #7c3aed;border-radius:20px;'
                f'padding:4px 14px;font-size:12px;color:#c084fc;display:inline-block;margin:3px">{t}</span>'
                for t in macro_signals["themes"]
            )
            st.markdown(f'<div style="margin-bottom:12px">{theme_pills}</div>', unsafe_allow_html=True)

        # Scan vulnerable stocks
        try:
            with st.spinner("Scoring 20 yen-carry-vulnerable stocks…"):
                macro_puts = scan_macro_put_combo()
        except Exception:
            macro_puts = []

        if macro_puts:
            combo_tickers = " + ".join(p["ticker"] for p in macro_puts[:5])
            avg_drop_15 = sum(p["est_drop_15d"] for p in macro_puts[:5]) / 5
            avg_drop_30 = sum(p["est_drop_30d"] for p in macro_puts[:5]) / 5
            avg_vuln = sum(p["vuln"] for p in macro_puts[:5]) / 5

            st.markdown(
                f'<div style="background:#2a0a0a;border:2px solid #f44336;border-radius:14px;padding:20px;margin-bottom:12px">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-bottom:14px">'
                f'<div>'
                f'<div style="font-size:12px;color:#f44336;letter-spacing:2px;font-weight:700">🇯🇵 MACRO EVENT PUT — AGGRESSIVE</div>'
                f'<div style="font-size:20px;font-weight:900;color:#f44336;margin-top:4px">{combo_tickers}</div>'
                f'<div style="font-size:11px;color:#8a9bb5;margin-top:4px">Yen carry vulnerable · High beta · Pre-revenue / Speculative</div>'
                f'</div>'
                f'<div style="text-align:right">'
                f'<div style="font-size:11px;color:#8a9bb5">Estimated Carry Unwind Drawdown</div>'
                f'<div style="font-size:14px;color:#f44336;font-weight:700">15D: -{avg_drop_15:.1f}%</div>'
                f'<div style="font-size:22px;color:#f44336;font-weight:900">30D: -{avg_drop_30:.1f}%</div>'
                f'<div style="font-size:10px;color:#8a9bb5;margin-top:4px">Avg Vulnerability: {avg_vuln:.0f}/100</div>'
                f'</div>'
                f'</div>', unsafe_allow_html=True
            )

            # Individual stock rows
            rows_html = ""
            for p in macro_puts:
                vuln_c = "#f44336" if p["vuln"] >= 75 else ("#FFC107" if p["vuln"] >= 55 else "#8a9bb5")
                mom_c = "#4CAF50" if p["mom15"] >= 0 else "#f44336"
                pe_str = f'{p["pe"]:.0f}' if p["pe"] and p["pe"] > 0 else "N/E"
                rows_html += (
                    f'<div style="display:flex;align-items:center;gap:10px;padding:10px 0;'
                    f'border-bottom:1px solid #3a1515">'
                    f'<div style="min-width:55px;font-size:14px;font-weight:800;color:#ffffff">{p["ticker"]}</div>'
                    f'<div style="min-width:130px;font-size:11px;color:#b0bcd4">{p["name"]}</div>'
                    f'<div style="min-width:65px;font-size:12px;color:#fff">${p["price"]:.2f}</div>'
                    f'<div style="min-width:50px;text-align:center">'
                    f'<div style="font-size:14px;font-weight:700;color:{vuln_c}">{p["vuln"]}</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">Vuln</div></div>'
                    f'<div style="min-width:45px;text-align:center">'
                    f'<div style="font-size:12px;font-weight:700;color:#f44336">{p["beta"]:.1f}</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">Beta</div></div>'
                    f'<div style="min-width:45px;text-align:center">'
                    f'<div style="font-size:12px;font-weight:700;color:#FFC107">{p["vol"]:.0f}%</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">Vol</div></div>'
                    f'<div style="min-width:40px;text-align:center">'
                    f'<div style="font-size:12px;color:#8a9bb5">{pe_str}</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">P/E</div></div>'
                    f'<div style="min-width:60px;text-align:center">'
                    f'<div style="font-size:13px;font-weight:700;color:{mom_c}">{p["mom15"]:+.1f}%</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">15D Mom</div></div>'
                    f'<div style="min-width:60px;text-align:center">'
                    f'<div style="font-size:13px;font-weight:700;color:#f44336">-{p["est_drop_15d"]:.1f}%</div>'
                    f'<div style="font-size:9px;color:#8a9bb5">Est 15D</div></div>'
                    f'<div style="flex:1;font-size:10px;color:#c8a0a0;line-height:1.4;padding-left:6px">{p["thesis"]}</div>'
                    f'</div>'
                )
            st.markdown(f'{rows_html}</div>', unsafe_allow_html=True)

            # Why explanation
            st.markdown(
                f'<div style="background:#2a0a0a;border-radius:8px;padding:12px 16px;margin:8px 0;'
                f'font-size:12px;color:#e8c8c8;line-height:1.7">'
                f'<strong style="color:#f44336">Why these stocks:</strong> '
                f'Each is scored on <b>Vulnerability</b> (0-100) — a composite of beta, volatility, P/E, profit margins, '
                f'leverage, and market cap. The higher the score, the more exposed to forced liquidation in a yen carry unwind. '
                f'These are the names that hedge funds and prop desks will sell first when margin calls hit. '
                f'Reddit is showing <b>{boj_total}</b> BOJ/carry-related discussions and <b>{macro_signals["leverage_mentions"]}</b> '
                f'forced liquidation posts this month — the market is aware and positioning.'
                f'</div>', unsafe_allow_html=True
            )

        # Reddit macro posts
        if macro_signals["top_posts"]:
            with st.expander(f"📡 Reddit Macro Discussion ({len(macro_signals['top_posts'])} posts)", expanded=False):
                for p in macro_signals["top_posts"]:
                    st.markdown(
                        f'<div style="background:#0e1117;border-radius:6px;padding:6px 10px;margin:3px 0;'
                        f'border-left:3px solid #7c3aed">'
                        f'<span style="font-size:10px;color:#8a9bb5">r/{p["sub"]} · {p["query"]}</span><br>'
                        f'<span style="font-size:12px;color:#e8ecf4">{p["title"]}</span>'
                        f'</div>', unsafe_allow_html=True
                    )

        st.markdown(
            '<div style="font-size:11px;color:#6a7a9a;margin-top:10px;line-height:1.5">'
            '⚠️ <b>This is an event-driven scenario, not a prediction.</b> '
            'If BOJ does not raise rates on June 17, or raises less than expected, these puts could lose value rapidly. '
            'Size positions for the scenario — not the certainty. Macro event trades require defined risk and strict exits.</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # Theme selector
    theme_names = list(THEMES.keys())
    selected = st.selectbox("Select Theme", theme_names, label_visibility="collapsed")

    theme = THEMES[selected]
    tickers_tuple = tuple(theme["tickers"])
    col = theme["color"]
    border = theme["border"]

    # Theme banner
    st.markdown(f"""
    <div style="background:{col}22;border:1px solid {border};border-radius:14px;padding:22px 24px;margin:12px 0 20px 0">
        <div style="font-size:24px;font-weight:800;color:#ffffff;margin-bottom:10px">{selected}</div>
        <div style="font-size:14px;color:#dde8f8;line-height:1.7;margin-bottom:14px">{theme['geo']}</div>
        <div style="background:{col}44;border-radius:8px;padding:10px 14px;font-size:13px;color:#ffffff">
            <strong>Investment Thesis:</strong> {theme['thesis']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch & score
    try:
        with st.spinner(f"Scoring {selected} picks…"):
            df = fetch_theme(tickers_tuple)
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        st.error("Could not load data for this theme. Click 🔄 Refresh or try again.")
    else:
        # Top pick highlight
        top = df.iloc[0]
        top_cfis = top["CFIS-X"]
        top_c = "#4CAF50" if top_cfis >= 65 else ("#FFC107" if top_cfis >= 45 else "#f44336")
        price_val  = top["Price"]
        chg_val    = top["Chg %"]
        chg_color  = "#4CAF50" if chg_val >= 0 else "#f44336"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{col}33,{col}11);border:2px solid {border};
                    border-radius:16px;padding:24px;margin-bottom:20px;display:flex;gap:24px;align-items:center">
            <div style="text-align:center;min-width:90px">
                <div style="font-size:13px;color:#b0bcd4">🏆 TOP PICK</div>
                <div style="font-size:36px;font-weight:900;color:#ffffff">{top['Ticker']}</div>
                <div style="font-size:12px;color:#b0bcd4">{top['Name']}</div>
            </div>
            <div style="flex:1;display:flex;gap:20px;flex-wrap:wrap">
                <div style="text-align:center">
                    <div style="font-size:11px;color:#8a9bb5">PRICE</div>
                    <div style="font-size:22px;font-weight:700;color:#fff">${price_val:.2f}</div>
                    <div style="font-size:13px;color:{chg_color}">{chg_val:+.2f}%</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:11px;color:#8a9bb5">CFIS-X</div>
                    <div style="font-size:36px;font-weight:900;color:{top_c}">{top_cfis}</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:11px;color:#8a9bb5">OPPORTUNITY</div>
                    <div style="font-size:36px;font-weight:900;color:#2196F3">{top['Opp']}</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:11px;color:#8a9bb5">MOMENTUM</div>
                    <div style="font-size:28px;font-weight:800;color:#FFC107">{top['Momentum']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── CALL / PUT Summary Strip ──────────────────────────
        st.markdown("### 📊 Louis' Verdict — All Picks at a Glance")
        calls  = [r for _, r in df.iterrows() if "CALL" in str(r.get("_verdict",""))]
        puts   = [r for _, r in df.iterrows() if "PUT"  in str(r.get("_verdict",""))]
        holds  = [r for _, r in df.iterrows() if "HOLD" in str(r.get("_verdict",""))]

        v1, v2, v3 = st.columns(3)
        v1.markdown(f"""<div style="background:#0a2a0a;border:1.5px solid #4CAF50;border-radius:10px;
            padding:14px;text-align:center">
            <div style="font-size:13px;color:#4CAF50;font-weight:700">📈 CALL PICKS</div>
            <div style="font-size:28px;font-weight:900;color:#4CAF50">{len(calls)}</div>
            <div style="font-size:12px;color:#c8d4e8">{' · '.join(r['Ticker'] for r in calls)}</div>
        </div>""", unsafe_allow_html=True)
        v2.markdown(f"""<div style="background:#2a0a0a;border:1.5px solid #f44336;border-radius:10px;
            padding:14px;text-align:center">
            <div style="font-size:13px;color:#f44336;font-weight:700">📉 PUT PICKS</div>
            <div style="font-size:28px;font-weight:900;color:#f44336">{len(puts)}</div>
            <div style="font-size:12px;color:#c8d4e8">{' · '.join(r['Ticker'] for r in puts)}</div>
        </div>""", unsafe_allow_html=True)
        v3.markdown(f"""<div style="background:#2a2200;border:1.5px solid #FFC107;border-radius:10px;
            padding:14px;text-align:center">
            <div style="font-size:13px;color:#FFC107;font-weight:700">⏸ HOLD / WATCH</div>
            <div style="font-size:28px;font-weight:900;color:#FFC107">{len(holds)}</div>
            <div style="font-size:12px;color:#c8d4e8">{' · '.join(r['Ticker'] for r in holds)}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Stock Cards with CALL/PUT badge ──────────────────
        st.markdown("### All Picks — Individual Breakdown")
        cols_per_row = 5
        rows_data = [df.iloc[i:i+cols_per_row] for i in range(0, len(df), cols_per_row)]

        for row_df in rows_data:
            row_cols = st.columns(len(row_df))
            for col_obj, (_, row) in zip(row_cols, row_df.iterrows()):
                sc      = row["CFIS-X"]
                sc_c    = "#4CAF50" if sc >= 65 else ("#FFC107" if sc >= 45 else "#f44336")
                chg     = row["Chg %"]
                chg_c   = "#4CAF50" if chg >= 0 else "#f44336"
                p       = row["Price"]
                verdict = row.get("_verdict", "—")
                v_color = row.get("_v_color", "#FFC107")
                v_bg    = row.get("_v_bg",    "#2a2200")
                lo      = row.get("_lo_pct",  0)
                hi      = row.get("_hi_pct",  0)
                opt_rec = row.get("_opt_rec", "—")
                col_obj.markdown(f"""
                <div style="background:#1c2130;border-radius:12px;padding:14px;
                            border:2px solid {v_color};text-align:center;margin-bottom:8px">
                    <div style="background:{v_bg};border-radius:8px;padding:5px 0;
                                font-size:15px;font-weight:900;color:{v_color};margin-bottom:8px">
                        {verdict}
                    </div>
                    <div style="font-size:18px;font-weight:800;color:#ffffff">{row['Ticker']}</div>
                    <div style="font-size:10px;color:#b0bcd4;margin-bottom:6px">{row['Name']}</div>
                    <div style="font-size:14px;color:#ffffff">${p:.2f}
                        <span style="font-size:11px;color:{chg_c}"> {chg:+.1f}%</span>
                    </div>
                    <div style="margin:8px 0;padding:6px;background:#0e1117;border-radius:6px">
                        <div style="font-size:10px;color:#8a9bb5">CFIS-X &nbsp;·&nbsp; Conviction</div>
                        <div style="font-size:16px;font-weight:800;color:{sc_c}">{sc}
                            <span style="font-size:13px;color:#FFC107"> / {row['Conviction']}</span>
                        </div>
                    </div>
                    <div style="font-size:11px;color:{v_color};font-weight:700">{opt_rec}</div>
                    <div style="font-size:10px;color:#8a9bb5">15-Day: {lo:.1f}%–{hi:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

        # CFIS-X bar chart for theme
        fig_t = px.bar(
            df, x="Ticker", y="CFIS-X",
            color="CFIS-X",
            color_continuous_scale=["#f44336","#FFC107","#4CAF50"],
            range_color=[0, 100],
            title=f"{selected} — CFIS-X Scores",
            template="plotly_dark",
            text="CFIS-X",
            hover_data=["Name", "Opp", "Momentum"]
        )
        fig_t.update_traces(textposition="outside", textfont=dict(color="#ffffff"))
        fig_t.update_layout(height=360, margin=dict(t=50, b=0))
        st.plotly_chart(fig_t, use_container_width=True)

        # Opportunity vs Risk scatter
        fig_s = px.scatter(
            df, x="Risk", y="Opp", text="Ticker",
            color="CFIS-X",
            color_continuous_scale=["#f44336","#FFC107","#4CAF50"],
            range_color=[0, 100],
            title="Opportunity vs Risk — Size up where to enter",
            template="plotly_dark",
            size_max=14,
            hover_data=["Name", "CFIS-X", "Momentum"]
        )
        fig_s.update_traces(
            textposition="top center",
            marker=dict(size=12),
            textfont=dict(color="#ffffff", size=11)
        )
        fig_s.update_layout(
            height=420, margin=dict(t=50, b=0),
            xaxis_title="Risk Score (higher = safer)",
            yaxis_title="Opportunity Score"
        )
        st.plotly_chart(fig_s, use_container_width=True)

        # All themes — why each matters
        st.divider()
        st.markdown("### 🗺️ All Themes — Why They Matter")
        st.caption("Each theme represents a structural shift Louis tracks. The thesis is the investment logic. Switch above to deep-dive.")

        WHY_THEMES = {
            "🤖 AI Extended":        "AI is the largest capital reallocation event since the internet. Every industry is being re-platformed on compute. You don't trade AI — you own the infrastructure.",
            "⚡ Energy":              "AI needs power. Grids are maxed. Nuclear is back. Energy independence is national security. This is the most underpriced input cost in tech.",
            "🚀 Space Tech":         "Governments and private capital are racing for orbital control. Satellite broadband, launch economics, and lunar logistics are the new contested infrastructure.",
            "🦾 Robotics":           "Labour is scarce, populations are aging, and factories are reshoring. Robotics solves all three. Humanoids are the next platform after smartphones.",
            "🪙 Tokenized Finance":  "Stablecoins are clearing trillions. Real assets are moving on-chain. Institutional crypto custody is live. The financial rails are being rebuilt in real time.",
            "🌾 Future Food":        "Feeding 10B people on a warming planet with disrupted fertiliser supply is an engineering problem. Agtech, precision farming, and alternative protein are the solutions.",
        }

        for tname, tdata in THEMES.items():
            col = tdata["color"]
            border = tdata["border"]
            thesis = tdata["thesis"]
            tickers_str = " · ".join(tdata["tickers"][:5])
            why = WHY_THEMES.get(tname, "")
            icon = tname.split()[0]
            label = " ".join(tname.split()[1:])

            st.markdown(
                f'<div style="background:{col}15;border:1px solid {border}44;border-radius:12px;'
                f'padding:16px 20px;margin:8px 0">'
                f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">'
                f'<span style="font-size:28px">{icon}</span>'
                f'<div>'
                f'<div style="font-size:16px;font-weight:800;color:#ffffff">{label}</div>'
                f'<div style="font-size:11px;color:#8a9bb5;margin-top:2px">{tickers_str}</div>'
                f'</div>'
                f'</div>'
                f'<div style="font-size:13px;color:#e2e8f0;line-height:1.7;margin-bottom:10px">{why}</div>'
                f'<div style="background:{col}33;border-radius:8px;padding:8px 14px;'
                f'font-size:12px;color:#ffffff">'
                f'<strong>Thesis:</strong> {thesis}'
                f'</div>'
                f'</div>', unsafe_allow_html=True
            )

# ═══════════════════════════════════════════════════════════════
elif page == "4️⃣ Portfolio Commander":
    st.title("💼 Portfolio Commander™")
    st.caption("How should capital be allocated? Auto-constructed portfolios with position sizing.")

    with st.spinner(f"Scanning {len(FULL_UNIVERSE)} stocks for portfolio construction…"):
        try:
            all_opps = scan_opportunities(tuple(FULL_UNIVERSE))
        except Exception:
            all_opps = []

    if all_opps:
        port_type = st.radio("Portfolio Type", ["Aggressive", "Balanced", "Defensive", "Dividend & Legacy", "Future Economy"], horizontal=True, label_visibility="collapsed")

        if port_type == "Aggressive":
            picks = filter_opportunities(all_opps, "15d")[:15]
            st.subheader("🔥 Aggressive Portfolio — High Conviction Short-Term")
        elif port_type == "Balanced":
            picks = filter_opportunities(all_opps, "90d")[:15]
            st.subheader("⚖️ Balanced Portfolio — Quality + Momentum + Migration")
        elif port_type == "Defensive":
            picks = sorted(all_opps, key=lambda r: r["risk"] * 0.5 + r["quality"] * 0.5, reverse=True)[:15]
            st.subheader("🛡️ Defensive Portfolio — Risk-Off Conditions")
        elif port_type == "Dividend & Legacy":
            picks = filter_opportunities(all_opps, "legacy")[:15]
            st.subheader("🏛️ Dividend & Legacy Portfolio — 3-10 Year Wealth")
        else:
            picks = sorted(all_opps, key=lambda r: r["cm_score"] * 0.4 + r["conviction"] * 0.3 + r["bottleneck"] * 0.3, reverse=True)[:15]
            st.subheader("🌊 Future Economy Portfolio — AI, Energy, Robotics, Space")

        total_conviction = sum(p["conviction"] for p in picks)
        for i, p in enumerate(picks):
            if p["conviction"] >= 80:
                raw_wt = 12
            elif p["conviction"] >= 70:
                raw_wt = 7
            elif p["conviction"] >= 60:
                raw_wt = 4
            else:
                raw_wt = 2
            p["_weight"] = raw_wt

        total_wt = sum(p["_weight"] for p in picks) or 1
        for p in picks:
            p["_weight_pct"] = p["_weight"] / total_wt * 100

        for p in picks:
            conv_c = "#4CAF50" if p["conviction"] >= 65 else ("#FFC107" if p["conviction"] >= 45 else "#f44336")
            sig_c = p["signal_color"]
            wt = p["_weight_pct"]
            bn_tag = ' <span style="background:#1a3a1a;border:1px solid #4CAF50;border-radius:10px;padding:1px 6px;font-size:9px;color:#66d166">BN</span>' if p["is_bottleneck"] else ""
            st.markdown(f"""
            <div style="background:#161b27;border-radius:10px;padding:10px 16px;margin-bottom:5px;border-left:4px solid {sig_c};display:flex;align-items:center;gap:12px;flex-wrap:wrap">
                <div style="min-width:55px;font-size:15px;font-weight:900;color:#ffffff">{p['ticker']}{bn_tag}</div>
                <div style="min-width:50px;text-align:center">
                    <div style="font-size:18px;font-weight:900;color:{conv_c}">{p['conviction']:.0f}</div>
                    <div style="font-size:8px;color:#8a9bb5">CONV</div>
                </div>
                <div style="min-width:55px;text-align:center">
                    <div style="font-size:13px;font-weight:800;color:{sig_c}">{p['signal']}</div>
                </div>
                <div style="min-width:50px;text-align:center">
                    <div style="font-size:16px;font-weight:800;color:#FFC107">{wt:.1f}%</div>
                    <div style="font-size:8px;color:#8a9bb5">WEIGHT</div>
                </div>
                <div style="min-width:60px;text-align:center;font-size:12px;color:#e8ecf4">{p['theme_icon']} {p['theme'][:16]}</div>
                <div style="min-width:50px;text-align:center;font-size:13px;color:#e8ecf4">${p['price']:.2f}</div>
                <div style="flex:1;font-size:11px;color:#b0bcd4">{p['one_sentence'][:100]}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown("**Position Size Rules:** Conviction 90-100 = 10-15% · 80-89 = 5-10% · 70-79 = 3-5% · 60-69 = 1-3% · Below 60 = Observe")
    else:
        st.info("Loading portfolio data…")


elif page == "5️⃣ Validation Engine":
    st.title("✅ Validation Engine™")
    st.caption("Can CFIS prove itself? Tracking every stock from March 1, 2026 in 30-day performance windows.")

    val_tab1, val_tab2, val_tab3 = st.tabs(["📅 30-Day Period Tracker", "📊 Signal Intelligence", "🌊 Theme Performance"])

    # ── Scan all stocks with period data ─────────────
    with st.spinner(f"Scanning {len(FULL_UNIVERSE)} stocks with historical periods from March 1, 2026…"):
        try:
            val_rows, period_labels = scan_validation_periods(tuple(FULL_UNIVERSE), "2026-03-01")
        except Exception:
            val_rows, period_labels = [], []

    if not val_rows:
        st.warning("No validation data available. Try again in a moment.")
    else:
        total_scanned = len(val_rows)

        # ══════════════════════════════════════════════════
        # TAB 1: 30-DAY PERIOD TRACKER
        # ══════════════════════════════════════════════════
        with val_tab1:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0a0e17,#1a1040);border:1px solid #7c3aed;border-radius:14px;padding:20px;margin-bottom:16px">
                <div style="font-size:12px;color:#7c3aed;letter-spacing:2px;font-weight:700;margin-bottom:6px">PERFORMANCE VALIDATION — MARCH 1, 2026 TO TODAY</div>
                <div style="font-size:13px;color:#b0bcd4">Tracking {total_scanned} stocks across {len(period_labels)} periods of 30 days each. Current conviction scores vs actual price delivery.</div>
            </div>
            """, unsafe_allow_html=True)

            conv_filter = st.radio("Filter by Conviction", ["All", "80+ (Attack)", "60-79 (Accumulate)", "50-59 (Observe)", "Below 50 (Avoid)"], horizontal=True, key="val_conv_filter")

            if conv_filter == "80+ (Attack)":
                filtered_rows = [r for r in val_rows if r["conviction"] >= 80]
            elif conv_filter == "60-79 (Accumulate)":
                filtered_rows = [r for r in val_rows if 60 <= r["conviction"] < 80]
            elif conv_filter == "50-59 (Observe)":
                filtered_rows = [r for r in val_rows if 50 <= r["conviction"] < 60]
            elif conv_filter == "Below 50 (Avoid)":
                filtered_rows = [r for r in val_rows if r["conviction"] < 50]
            else:
                filtered_rows = val_rows

            filtered_rows = sorted(filtered_rows, key=lambda r: r["conviction"], reverse=True)
            st.markdown(f"**Showing {len(filtered_rows)} stocks** · Sorted by conviction")

            # ── Period header row ────────────────────────
            period_hdr = "".join(
                f'<div style="min-width:80px;text-align:center;font-size:10px;color:#FFC107;font-weight:700">{pl}</div>'
                for pl in period_labels
            )
            st.markdown(f"""
            <div style="background:#0e1320;border-radius:10px 10px 0 0;padding:10px 16px;margin-bottom:0;display:flex;align-items:center;gap:8px;border-bottom:1px solid #3a4460">
                <div style="min-width:55px;font-size:10px;color:#8a9bb5;font-weight:700">TICKER</div>
                <div style="min-width:50px;text-align:center;font-size:10px;color:#8a9bb5;font-weight:700">CONV</div>
                <div style="min-width:55px;text-align:center;font-size:10px;color:#8a9bb5;font-weight:700">SIGNAL</div>
                <div style="min-width:65px;text-align:center;font-size:10px;color:#8a9bb5;font-weight:700">MAR 1 $</div>
                <div style="min-width:65px;text-align:center;font-size:10px;color:#8a9bb5;font-weight:700">NOW $</div>
                <div style="min-width:65px;text-align:center;font-size:10px;color:#8a9bb5;font-weight:700">TOTAL</div>
                {period_hdr}
            </div>
            """, unsafe_allow_html=True)

            # ── Stock rows with period returns ───────────
            for r in filtered_rows:
                conv_c = "#4CAF50" if r["conviction"] >= 65 else ("#FFC107" if r["conviction"] >= 45 else "#f44336")
                total_c = "#4CAF50" if r["total_ret"] >= 0 else "#f44336"
                bn_tag = ' <span style="background:#1a3a1a;border:1px solid #4CAF50;border-radius:8px;padding:0 4px;font-size:8px;color:#66d166">BN</span>' if r.get("is_bottleneck") else ""

                period_cells = ""
                for p in r["periods"]:
                    if p["ret"] is not None:
                        pc = "#4CAF50" if p["ret"] >= 0 else "#f44336"
                        period_cells += f'<div style="min-width:80px;text-align:center;font-size:13px;font-weight:700;color:{pc}">{p["ret"]:+.1f}%</div>'
                    else:
                        period_cells += '<div style="min-width:80px;text-align:center;font-size:11px;color:#555">—</div>'

                st.markdown(f"""
                <div style="background:#161b27;padding:8px 16px;margin-bottom:2px;display:flex;align-items:center;gap:8px;border-left:3px solid {conv_c}">
                    <div style="min-width:55px;font-size:14px;font-weight:900;color:#ffffff">{r['ticker']}{bn_tag}</div>
                    <div style="min-width:50px;text-align:center">
                        <div style="font-size:16px;font-weight:900;color:{conv_c}">{r['conviction']:.0f}</div>
                    </div>
                    <div style="min-width:55px;text-align:center;font-size:12px;font-weight:700;color:{r['signal_color']}">{r['signal']}</div>
                    <div style="min-width:65px;text-align:center;font-size:12px;color:#e8ecf4">${r['base_price']:.2f}</div>
                    <div style="min-width:65px;text-align:center;font-size:12px;color:#e8ecf4">${r['current_price']:.2f}</div>
                    <div style="min-width:65px;text-align:center;font-size:14px;font-weight:800;color:{total_c}">{r['total_ret']:+.1f}%</div>
                    {period_cells}
                </div>
                """, unsafe_allow_html=True)

            st.divider()

            # ── Aggregate stats for filtered set ─────────
            if filtered_rows:
                avg_total = sum(r["total_ret"] for r in filtered_rows) / len(filtered_rows)
                avg_conv = sum(r["conviction"] for r in filtered_rows) / len(filtered_rows)
                winners = len([r for r in filtered_rows if r["total_ret"] > 0])
                win_rate = winners / len(filtered_rows) * 100
                best = max(filtered_rows, key=lambda r: r["total_ret"])
                worst = min(filtered_rows, key=lambda r: r["total_ret"])
                avg_c = "#4CAF50" if avg_total >= 0 else "#f44336"
                wr_c = "#4CAF50" if win_rate >= 60 else ("#FFC107" if win_rate >= 45 else "#f44336")

                st.markdown(f"""
                <div style="background:#161b27;border:1px solid #3a4460;border-radius:14px;padding:20px;margin-top:10px">
                    <div style="font-size:12px;color:#FFC107;letter-spacing:2px;font-weight:700;margin-bottom:14px">AGGREGATE PERFORMANCE — {conv_filter.upper()}</div>
                    <div style="display:flex;gap:16px;flex-wrap:wrap;justify-content:center">
                        <div style="text-align:center;min-width:100px">
                            <div style="font-size:28px;font-weight:900;color:{avg_c}">{avg_total:+.1f}%</div>
                            <div style="font-size:10px;color:#8a9bb5">AVG TOTAL RETURN</div>
                        </div>
                        <div style="text-align:center;min-width:100px">
                            <div style="font-size:28px;font-weight:900;color:{wr_c}">{win_rate:.0f}%</div>
                            <div style="font-size:10px;color:#8a9bb5">WIN RATE</div>
                        </div>
                        <div style="text-align:center;min-width:100px">
                            <div style="font-size:28px;font-weight:900;color:#FFC107">{avg_conv:.0f}</div>
                            <div style="font-size:10px;color:#8a9bb5">AVG CONVICTION</div>
                        </div>
                        <div style="text-align:center;min-width:100px">
                            <div style="font-size:28px;font-weight:900;color:#4CAF50">{best['ticker']}</div>
                            <div style="font-size:10px;color:#8a9bb5">BEST: {best['total_ret']:+.1f}%</div>
                        </div>
                        <div style="text-align:center;min-width:100px">
                            <div style="font-size:28px;font-weight:900;color:#f44336">{worst['ticker']}</div>
                            <div style="font-size:10px;color:#8a9bb5">WORST: {worst['total_ret']:+.1f}%</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Period-by-period aggregate ───────────
                st.markdown("#### 📈 Average Return by 30-Day Period")
                for pi, pl in enumerate(period_labels):
                    p_rets = [r["periods"][pi]["ret"] for r in filtered_rows if pi < len(r["periods"]) and r["periods"][pi]["ret"] is not None]
                    if p_rets:
                        p_avg = sum(p_rets) / len(p_rets)
                        p_wr = len([v for v in p_rets if v > 0]) / len(p_rets) * 100
                        p_c = "#4CAF50" if p_avg >= 0 else "#f44336"
                        pw_c = "#4CAF50" if p_wr >= 60 else ("#FFC107" if p_wr >= 45 else "#f44336")
                        st.markdown(f"""
                        <div style="background:#161b27;border-radius:8px;padding:8px 16px;margin-bottom:3px;display:flex;align-items:center;gap:16px">
                            <div style="min-width:90px;font-size:13px;font-weight:700;color:#FFC107">{pl}</div>
                            <div style="min-width:80px;text-align:center">
                                <div style="font-size:16px;font-weight:800;color:{p_c}">{p_avg:+.1f}%</div>
                                <div style="font-size:9px;color:#8a9bb5">AVG RETURN</div>
                            </div>
                            <div style="min-width:80px;text-align:center">
                                <div style="font-size:16px;font-weight:800;color:{pw_c}">{p_wr:.0f}%</div>
                                <div style="font-size:9px;color:#8a9bb5">WIN RATE</div>
                            </div>
                            <div style="min-width:60px;text-align:center;font-size:12px;color:#8a9bb5">{len(p_rets)} stocks</div>
                        </div>
                        """, unsafe_allow_html=True)

        # ══════════════════════════════════════════════════
        # TAB 2: SIGNAL INTELLIGENCE
        # ══════════════════════════════════════════════════
        with val_tab2:
            signal_counts = {}
            for r in val_rows:
                sig = r["signal"]
                signal_counts[sig] = signal_counts.get(sig, 0) + 1

            attack_n = signal_counts.get("Attack", 0)
            accum_n = signal_counts.get("Accumulate", 0)
            observe_n = signal_counts.get("Observe", 0)
            reduce_n = signal_counts.get("Reduce", 0)
            exit_n = signal_counts.get("Exit", 0)

            st.markdown(f"""
            <div style="background:#161b27;border:1px solid #3a4460;border-radius:14px;padding:20px;margin-bottom:16px">
                <div style="font-size:12px;color:#FFC107;letter-spacing:2px;font-weight:700;margin-bottom:12px">SIGNAL DISTRIBUTION — {total_scanned} STOCKS</div>
                <div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center">
                    <div style="background:#0a1a0a;border:1px solid #4CAF50;border-radius:10px;padding:14px 20px;text-align:center;min-width:110px">
                        <div style="font-size:28px;font-weight:900;color:#4CAF50">{attack_n}</div>
                        <div style="font-size:11px;color:#4CAF50;font-weight:700">ATTACK</div>
                        <div style="font-size:10px;color:#8a9bb5">{attack_n/total_scanned*100:.0f}%</div>
                    </div>
                    <div style="background:#0a1a1a;border:1px solid #06b6d4;border-radius:10px;padding:14px 20px;text-align:center;min-width:110px">
                        <div style="font-size:28px;font-weight:900;color:#06b6d4">{accum_n}</div>
                        <div style="font-size:11px;color:#06b6d4;font-weight:700">ACCUMULATE</div>
                        <div style="font-size:10px;color:#8a9bb5">{accum_n/total_scanned*100:.0f}%</div>
                    </div>
                    <div style="background:#1a1a0a;border:1px solid #FFC107;border-radius:10px;padding:14px 20px;text-align:center;min-width:110px">
                        <div style="font-size:28px;font-weight:900;color:#FFC107">{observe_n}</div>
                        <div style="font-size:11px;color:#FFC107;font-weight:700">OBSERVE</div>
                        <div style="font-size:10px;color:#8a9bb5">{observe_n/total_scanned*100:.0f}%</div>
                    </div>
                    <div style="background:#1a0a0a;border:1px solid #f44336;border-radius:10px;padding:14px 20px;text-align:center;min-width:110px">
                        <div style="font-size:28px;font-weight:900;color:#f44336">{reduce_n + exit_n}</div>
                        <div style="font-size:11px;color:#f44336;font-weight:700">REDUCE / EXIT</div>
                        <div style="font-size:10px;color:#8a9bb5">{(reduce_n+exit_n)/total_scanned*100:.0f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            selectivity = (1 - (attack_n + accum_n) / total_scanned) * 100 if total_scanned else 0
            sel_c = "#4CAF50" if selectivity >= 70 else ("#FFC107" if selectivity >= 50 else "#f44336")
            st.markdown(f"""
            <div style="background:#161b27;border-radius:10px;padding:14px 20px;margin-bottom:16px;display:flex;align-items:center;gap:16px">
                <div style="font-size:36px;font-weight:900;color:{sel_c}">{selectivity:.0f}%</div>
                <div>
                    <div style="font-size:14px;font-weight:700;color:#ffffff">Selectivity Score</div>
                    <div style="font-size:12px;color:#b0bcd4">% of universe CFIS does NOT recommend buying. Higher = more disciplined.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Signal vs Actual Returns ─────────────────
            st.markdown("### 📊 Signal Accuracy — Did Each Signal Deliver?")
            for sig_name, sig_color in [("Attack", "#4CAF50"), ("Accumulate", "#06b6d4"), ("Observe", "#FFC107"), ("Reduce", "#f44336"), ("Exit", "#f44336")]:
                sig_stocks = [r for r in val_rows if r["signal"] == sig_name]
                if not sig_stocks:
                    continue
                avg_ret = sum(r["total_ret"] for r in sig_stocks) / len(sig_stocks)
                wr = len([r for r in sig_stocks if r["total_ret"] > 0]) / len(sig_stocks) * 100
                r_c = "#4CAF50" if avg_ret >= 0 else "#f44336"
                w_c = "#4CAF50" if wr >= 60 else ("#FFC107" if wr >= 45 else "#f44336")
                correct = (sig_name in ("Attack", "Accumulate") and avg_ret > 0) or (sig_name in ("Reduce", "Exit") and avg_ret <= 0) or sig_name == "Observe"
                verdict = "✅ CORRECT" if correct else "❌ WRONG"
                v_c = "#4CAF50" if correct else "#f44336"
                st.markdown(f"""
                <div style="background:#161b27;border-radius:10px;padding:12px 16px;margin-bottom:5px;display:flex;align-items:center;gap:16px;border-left:4px solid {sig_color}">
                    <div style="min-width:90px;font-size:15px;font-weight:800;color:{sig_color}">{sig_name}</div>
                    <div style="min-width:40px;text-align:center;font-size:12px;color:#8a9bb5">{len(sig_stocks)} stocks</div>
                    <div style="min-width:80px;text-align:center">
                        <div style="font-size:18px;font-weight:900;color:{r_c}">{avg_ret:+.1f}%</div>
                        <div style="font-size:9px;color:#8a9bb5">AVG RETURN (MAR 1)</div>
                    </div>
                    <div style="min-width:80px;text-align:center">
                        <div style="font-size:18px;font-weight:900;color:{w_c}">{wr:.0f}%</div>
                        <div style="font-size:9px;color:#8a9bb5">WIN RATE</div>
                    </div>
                    <div style="font-size:13px;font-weight:700;color:{v_c}">{verdict}</div>
                </div>
                """, unsafe_allow_html=True)

            st.divider()

            # ── Conviction histogram ─────────────────────
            conv_buckets = {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "50-59": 0, "40-49": 0, "<40": 0}
            for r in val_rows:
                c = r["conviction"]
                if c >= 90: conv_buckets["90-100"] += 1
                elif c >= 80: conv_buckets["80-89"] += 1
                elif c >= 70: conv_buckets["70-79"] += 1
                elif c >= 60: conv_buckets["60-69"] += 1
                elif c >= 50: conv_buckets["50-59"] += 1
                elif c >= 40: conv_buckets["40-49"] += 1
                else: conv_buckets["<40"] += 1

            fig_conv = px.bar(
                x=list(conv_buckets.keys()), y=list(conv_buckets.values()),
                labels={"x": "Conviction Range", "y": "Stocks"},
                title="Conviction Score Distribution",
                template="plotly_dark",
                color=list(conv_buckets.values()),
                color_continuous_scale=["#f44336", "#FFC107", "#4CAF50"],
            )
            fig_conv.update_layout(height=300, margin=dict(t=50, b=0), showlegend=False, coloraxis_showscale=False)
            fig_conv.update_traces(texttemplate="%{y}", textposition="outside", textfont_color="#ffffff")
            st.plotly_chart(fig_conv, use_container_width=True)

        # ══════════════════════════════════════════════════
        # TAB 3: THEME PERFORMANCE
        # ══════════════════════════════════════════════════
        with val_tab3:
            st.markdown("### 🌊 Performance by Capital Migration Theme (Since March 1, 2026)")
            theme_perf = {}
            for r in val_rows:
                th = r["theme"]
                if th not in theme_perf:
                    theme_perf[th] = {"returns": [], "convictions": [], "icon": r["theme_icon"]}
                theme_perf[th]["returns"].append(r["total_ret"])
                theme_perf[th]["convictions"].append(r["conviction"])

            theme_rows_list = []
            for th, data in theme_perf.items():
                avg_r = sum(data["returns"]) / len(data["returns"])
                avg_c = sum(data["convictions"]) / len(data["convictions"])
                wr = len([v for v in data["returns"] if v > 0]) / len(data["returns"]) * 100
                best_r = max(data["returns"])
                worst_r = min(data["returns"])
                theme_rows_list.append({"theme": th, "icon": data["icon"], "avg_ret": avg_r, "avg_conv": avg_c, "win_rate": wr, "count": len(data["returns"]), "best": best_r, "worst": worst_r})

            theme_rows_list.sort(key=lambda x: x["avg_ret"], reverse=True)
            for tr in theme_rows_list:
                r_c = "#4CAF50" if tr["avg_ret"] >= 0 else "#f44336"
                w_c = "#4CAF50" if tr["win_rate"] >= 60 else ("#FFC107" if tr["win_rate"] >= 45 else "#f44336")
                st.markdown(f"""
                <div style="background:#161b27;border-radius:10px;padding:12px 16px;margin-bottom:5px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;border-left:4px solid {r_c}">
                    <div style="min-width:160px;font-size:14px;font-weight:700;color:#e8ecf4">{tr['icon']} {tr['theme']}</div>
                    <div style="min-width:40px;text-align:center;font-size:11px;color:#8a9bb5">{tr['count']} stocks</div>
                    <div style="min-width:80px;text-align:center">
                        <div style="font-size:18px;font-weight:800;color:{r_c}">{tr['avg_ret']:+.1f}%</div>
                        <div style="font-size:9px;color:#8a9bb5">AVG TOTAL RET</div>
                    </div>
                    <div style="min-width:80px;text-align:center">
                        <div style="font-size:16px;font-weight:800;color:{w_c}">{tr['win_rate']:.0f}%</div>
                        <div style="font-size:9px;color:#8a9bb5">WIN RATE</div>
                    </div>
                    <div style="min-width:60px;text-align:center">
                        <div style="font-size:14px;font-weight:700;color:#FFC107">{tr['avg_conv']:.0f}</div>
                        <div style="font-size:9px;color:#8a9bb5">AVG CONV</div>
                    </div>
                    <div style="min-width:60px;text-align:center">
                        <div style="font-size:12px;font-weight:700;color:#4CAF50">+{tr['best']:.1f}%</div>
                        <div style="font-size:9px;color:#8a9bb5">BEST</div>
                    </div>
                    <div style="min-width:60px;text-align:center">
                        <div style="font-size:12px;font-weight:700;color:#f44336">{tr['worst']:.1f}%</div>
                        <div style="font-size:9px;color:#8a9bb5">WORST</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.divider()

            # ── Top 10 best and worst since March 1 ──────
            st.markdown("### 🏆 Top 10 Best Performers Since March 1, 2026")
            top10 = sorted(val_rows, key=lambda r: r["total_ret"], reverse=True)[:10]
            for r in top10:
                conv_c = "#4CAF50" if r["conviction"] >= 65 else ("#FFC107" if r["conviction"] >= 45 else "#f44336")
                st.markdown(f"""
                <div style="background:#161b27;border-radius:8px;padding:8px 16px;margin-bottom:3px;display:flex;align-items:center;gap:14px">
                    <div style="min-width:55px;font-size:15px;font-weight:900;color:#ffffff">{r['ticker']}</div>
                    <div style="min-width:50px;text-align:center;font-size:16px;font-weight:900;color:{conv_c}">{r['conviction']:.0f}</div>
                    <div style="min-width:55px;text-align:center;font-size:12px;font-weight:700;color:{r['signal_color']}">{r['signal']}</div>
                    <div style="min-width:70px;text-align:center;font-size:16px;font-weight:800;color:#4CAF50">{r['total_ret']:+.1f}%</div>
                    <div style="font-size:12px;color:#8a9bb5">${r['base_price']:.2f} → ${r['current_price']:.2f}</div>
                    <div style="flex:1;font-size:11px;color:#b0bcd4">{r['theme_icon']} {r['theme']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("### 🚫 Top 10 Worst Performers Since March 1, 2026")
            bottom10 = sorted(val_rows, key=lambda r: r["total_ret"])[:10]
            for r in bottom10:
                conv_c = "#4CAF50" if r["conviction"] >= 65 else ("#FFC107" if r["conviction"] >= 45 else "#f44336")
                st.markdown(f"""
                <div style="background:#161b27;border-radius:8px;padding:8px 16px;margin-bottom:3px;display:flex;align-items:center;gap:14px">
                    <div style="min-width:55px;font-size:15px;font-weight:900;color:#ffffff">{r['ticker']}</div>
                    <div style="min-width:50px;text-align:center;font-size:16px;font-weight:900;color:{conv_c}">{r['conviction']:.0f}</div>
                    <div style="min-width:55px;text-align:center;font-size:12px;font-weight:700;color:{r['signal_color']}">{r['signal']}</div>
                    <div style="min-width:70px;text-align:center;font-size:16px;font-weight:800;color:#f44336">{r['total_ret']:+.1f}%</div>
                    <div style="font-size:12px;color:#8a9bb5">${r['base_price']:.2f} → ${r['current_price']:.2f}</div>
                    <div style="flex:1;font-size:11px;color:#b0bcd4">{r['theme_icon']} {r['theme']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.caption("⚠️ Returns measured from March 1, 2026 to today. Conviction scores are current (not historical snapshots). Future versions will store conviction at time of signal for true forward-looking validation.")


elif page == "6️⃣ Hunter Command by Louis Teo":
    st.title("🎯 CFIS Hunter™ Command Center by Louis Teo")
    st.caption("Capital Flow Hunting System — Not a screener. Not a valuation tool. A capital flow prediction engine.")

    st.markdown("""
    <div style="background:linear-gradient(135deg,#0a0a1e,#0a1a2e);border:1px solid #06b6d4;border-radius:14px;padding:20px;margin-bottom:16px">
        <div style="font-size:12px;color:#06b6d4;letter-spacing:2px;font-weight:700;margin-bottom:8px">CIO PHILOSOPHY</div>
        <div style="font-size:13px;color:#e8ecf4;line-height:2.0">
            Don't ask "Is this a good company?"<br>
            Ask: "Will large amounts of capital flow into this asset within the next 3, 6, 12 and 24 months?"<br>
            The system favors patience over activity. If nothing qualifies — that is the correct answer.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#161b27;border-radius:10px;padding:14px;margin-bottom:16px;display:flex;gap:20px;flex-wrap:wrap;justify-content:center;align-items:center">
        <div style="display:flex;gap:14px;align-items:center">
            <div style="text-align:center"><div style="background:#00E676;color:#000;font-weight:900;font-size:11px;padding:4px 14px;border-radius:12px">⚡ STRONG GO</div><div style="font-size:9px;color:#8a9bb5;margin-top:3px">Max 7</div></div>
            <div style="text-align:center"><div style="background:#4CAF50;color:#000;font-weight:900;font-size:11px;padding:4px 14px;border-radius:12px">🔥 GO</div><div style="font-size:9px;color:#8a9bb5;margin-top:3px">Max 7</div></div>
            <div style="text-align:center"><div style="background:#FFC107;color:#000;font-weight:900;font-size:11px;padding:4px 14px;border-radius:12px">🟡 WAIT</div><div style="font-size:9px;color:#8a9bb5;margin-top:3px">Top 20</div></div>
            <div style="text-align:center"><div style="background:#78909C;color:#000;font-weight:900;font-size:11px;padding:4px 14px;border-radius:12px">❌ PASS</div><div style="font-size:9px;color:#8a9bb5;margin-top:3px">Ignore</div></div>
        </div>
        <div style="border-left:1px solid #3a4460;padding-left:16px">
            <div style="font-size:10px;color:#8a9bb5;line-height:1.8">
                <span style="color:#00E676;font-weight:700">STRONG GO:</span> Hunter&gt;95 + Conv&gt;90 + CAP&gt;90 + Force&gt;90 + Timing&gt;85<br>
                <span style="color:#4CAF50;font-weight:700">GO:</span> Hunter&gt;90 + Conv&gt;80 + CAP&gt;85 + Force&gt;80 + Timing&gt;75<br>
                <span style="color:#FFC107;font-weight:700">WAIT:</span> Hunter&gt;80 but lacking Timing, Catalyst, Force or CAP confirmation
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📖 HOW TO READ THE SCORES — Interpretation Guide", expanded=False):
        st.markdown("""
        <div style="background:#0d1117;border-radius:12px;padding:20px;line-height:2.0">
            <div style="display:flex;gap:20px;flex-wrap:wrap">
                <div style="flex:1;min-width:280px">
                    <div style="font-size:13px;font-weight:800;color:#06b6d4;margin-bottom:8px">📊 HUNTER SCORE (Master Score)</div>
                    <div style="font-size:12px;color:#c9d1d9">
                        The composite score. Answers: <em>"Will capital flow into this stock?"</em><br>
                        <span style="color:#00E676">90+</span> = High conviction &nbsp;|&nbsp;
                        <span style="color:#4CAF50">80-89</span> = Watch closely &nbsp;|&nbsp;
                        <span style="color:#FFC107">60-79</span> = Average &nbsp;|&nbsp;
                        <span style="color:#78909C">&lt;60</span> = Weak
                    </div>
                </div>
                <div style="flex:1;min-width:280px">
                    <div style="font-size:13px;font-weight:800;color:#AB47BC;margin-bottom:8px">🎯 CONVICTION (Signal Confidence)</div>
                    <div style="font-size:12px;color:#c9d1d9">
                        <em>"How confident is the data behind the Hunter score?"</em><br>
                        High Hunter + Low Conviction = <span style="color:#f44336">dangerous</span> (thesis looks good but evidence is thin)<br>
                        High Hunter + High Conviction = <span style="color:#4CAF50">real signal</span> (multiple data sources agree)
                    </div>
                </div>
            </div>
            <div style="display:flex;gap:20px;flex-wrap:wrap;margin-top:16px">
                <div style="flex:1;min-width:180px">
                    <div style="font-size:13px;font-weight:800;color:#FFC107;margin-bottom:8px">💰 CAP (Capital Attraction — 20%)</div>
                    <div style="font-size:12px;color:#c9d1d9">
                        <em>"Is large capital likely to flow here?"</em><br>
                        <span style="color:#4CAF50">90+</span> = Capital actively migrating &nbsp;|&nbsp;
                        <span style="color:#78909C">&lt;70</span> = No flow signal
                    </div>
                </div>
                <div style="flex:1;min-width:180px">
                    <div style="font-size:13px;font-weight:800;color:#AB47BC;margin-bottom:8px">⚡ FORCE (Structural Catalysts — 20%)</div>
                    <div style="font-size:12px;color:#c9d1d9">
                        <em>"Are real forces pushing capital into this stock?"</em><br>
                        Analyst upgrades, insider buying, short squeeze, sector rotation<br>
                        <span style="color:#4CAF50">90+</span> = Multiple forces converging &nbsp;|&nbsp;
                        <span style="color:#78909C">&lt;70</span> = No catalyst
                    </div>
                </div>
                <div style="flex:1;min-width:180px">
                    <div style="font-size:13px;font-weight:800;color:#ef5350;margin-bottom:8px">👥 CROWD (Crowding — 10%, INVERSE)</div>
                    <div style="font-size:12px;color:#c9d1d9">
                        <strong style="color:#FFC107">Lower is better.</strong> <em>"Is everyone already in this trade?"</em><br>
                        <span style="color:#4CAF50">&lt;40</span> = Uncrowded, ideal &nbsp;|&nbsp;
                        <span style="color:#FFC107">60-70</span> = Getting crowded &nbsp;|&nbsp;
                        <span style="color:#f44336">80+</span> = Dangerous
                    </div>
                </div>
            </div>
            <div style="margin-top:16px;padding-top:12px;border-top:1px solid #21262d">
                <div style="font-size:12px;font-weight:700;color:#06b6d4;margin-bottom:6px">QUICK DECISION FRAMEWORK</div>
                <div style="font-size:12px;color:#c9d1d9">
                    ✅ <strong>Best setup:</strong> High Hunter + High CAP + High Force + Low Crowd = capital flowing, catalysts firing, nobody noticed yet<br>
                    ⚠️ <strong>Caution:</strong> High Hunter + Low Conviction = data incomplete, don't trust it<br>
                    🟡 <strong>Wait:</strong> High CAP + Low Force = capital wants to go there but no catalyst yet<br>
                    🔴 <strong>Late:</strong> High Force + High Crowd = catalyst exists but everyone already positioned<br>
                    ❌ <strong>Pass:</strong> Low Crowd + Low CAP = nobody cares and there's no reason to
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    cmd_tab1, cmd_tab2, cmd_tab3, cmd_tab4 = st.tabs(["📊 Command Center", "🔍 Deep Analysis", "🌐 Universe", "💰 Smart Money"])

    with cmd_tab1:
        if st.button(f"⚡ SCAN {len(FULL_UNIVERSE)} STOCKS", key="cmd_scan", type="primary", use_container_width=True):
            st.session_state["cmd_scan_triggered"] = True
        if not st.session_state.get("cmd_scan_triggered"):
            st.info("Click the button above to scan the global universe.")
        else:
          with st.spinner(f"Scanning {len(FULL_UNIVERSE)} stocks across global universe…"):
            try:
                all_opps = scan_opportunities(tuple(FULL_UNIVERSE))
                all_sorted = sorted(all_opps, key=lambda x: x["conviction"], reverse=True)

                go_stocks = [r for r in all_sorted if r.get("action") in ("STRONG GO", "GO")][:7]
                wait_stocks = [r for r in all_sorted if r.get("action") == "WAIT"][:20]
                top50 = all_sorted[:50]

                cal = check_hunter_calibration(all_sorted)
                if cal and cal.get("is_restrictive"):
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#2a1a0a,#3a2a0a);border:2px solid #FF9800;border-radius:14px;padding:20px;margin:12px 0">
                        <div style="font-size:14px;font-weight:900;color:#FF9800;letter-spacing:2px;text-align:center">⚠️ HUNTER ENGINE OVERLY RESTRICTIVE</div>
                        <div style="font-size:12px;color:#FFB74D;text-align:center;margin-top:8px;line-height:1.8">
                            Highest score in universe: <strong>{cal['max_score']:.0f}</strong> · Average: <strong>{cal['avg_score']:.0f}</strong> · Above 85: <strong>{cal['above_85']}/{cal['total']}</strong><br>
                            {'<br>'.join(cal['warnings'])}
                        </div>
                        <div style="font-size:11px;color:#8a9bb5;text-align:center;margin-top:8px">
                            This may indicate market-wide conditions are unfavorable, or scoring needs recalibration.
                            The system does NOT artificially create GO signals.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif cal and cal.get("is_generous"):
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#0a1a2a,#0a2a3a);border:2px solid #4FC3F7;border-radius:14px;padding:16px;margin:12px 0">
                        <div style="font-size:12px;font-weight:700;color:#4FC3F7;letter-spacing:2px;text-align:center">CALIBRATION NOTE: Average score {cal['avg_score']:.0f} above expected 60-75 range. Scoring may be too generous.</div>
                    </div>
                    """, unsafe_allow_html=True)

                # ── SECTION 1: GO ZONE ────────────────────────
                st.markdown("""
                <div style="background:linear-gradient(135deg,#0a1a0a,#0a2a0a);border:2px solid #4CAF50;border-radius:16px;padding:20px;margin:16px 0">
                    <div style="font-size:14px;font-weight:900;color:#4CAF50;letter-spacing:3px;text-align:center">🔥 GO ZONE — HIGHEST CONVICTION OPPORTUNITIES</div>
                    <div style="font-size:11px;color:#81C784;text-align:center;margin-top:4px">Top 7 stocks. Capital flow confirmed. Timing aligned.</div>
                </div>
                """, unsafe_allow_html=True)

                if not go_stocks:
                    max_hs = max(r["conviction"] for r in all_sorted) if all_sorted else 0
                    avg_hs = sum(r["conviction"] for r in all_sorted) / len(all_sorted) if all_sorted else 0
                    if max_hs < 70:
                        mkt_cond = "BEAR / RISK-OFF MARKET"
                        mkt_desc = "No stock in the universe scores above 70. Capital is leaving risk assets. This is a stay-in-cash environment."
                        mkt_color = "#f44336"
                    elif max_hs < 80:
                        mkt_cond = "BORING / CONSOLIDATING MARKET"
                        mkt_desc = "Top stocks score 70-80 but lack conviction. Market is consolidating — no clear direction yet. Watch for breakouts."
                        mkt_color = "#FFC107"
                    else:
                        mkt_cond = "EMERGING OPPORTUNITIES"
                        mkt_desc = "Some stocks near WAIT threshold. Catalysts forming but timing not confirmed. Stay alert."
                        mkt_color = "#29B6F6"
                    st.markdown(f"""
                    <div style="background:#161b27;border:1px solid #3a4460;border-radius:12px;padding:30px;text-align:center;margin:10px 0">
                        <div style="font-size:20px;font-weight:800;color:#78909C;letter-spacing:2px">NO GO CANDIDATES TODAY</div>
                        <div style="font-size:14px;font-weight:700;color:{mkt_color};margin-top:12px;letter-spacing:2px">📡 MARKET CONDITION: {mkt_cond}</div>
                        <div style="font-size:12px;color:#8a9bb5;margin-top:8px;max-width:600px;margin-left:auto;margin-right:auto">{mkt_desc}</div>
                        <div style="font-size:12px;color:#8a9bb5;margin-top:12px">Top Hunter: <strong style="color:{mkt_color}">{max_hs:.0f}</strong> · Average: <strong>{avg_hs:.0f}</strong> · Universe: {len(all_sorted)} stocks</div>
                        <div style="font-size:11px;color:#FFC107;margin-top:12px">This is acceptable. The system does NOT force trades. Patience is the edge.</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="display:flex;gap:6px;padding:8px 12px;background:#0d1117;border-radius:8px;margin-bottom:6px;font-size:10px;color:#8a9bb5;font-weight:700;letter-spacing:1px">
                        <div style="min-width:30px">#</div>
                        <div style="min-width:60px">TICKER</div>
                        <div style="flex:1">COMPANY</div>
                        <div style="min-width:55px;text-align:center">HUNTER</div>
                        <div style="min-width:55px;text-align:center">CONV</div>
                        <div style="min-width:50px;text-align:center">CAP</div>
                        <div style="min-width:50px;text-align:center">FORCE</div>
                        <div style="min-width:50px;text-align:center">TIMING</div>
                        <div style="min-width:65px;text-align:center">RETURN</div>
                        <div style="min-width:80px;text-align:center">ACTION</div>
                    </div>
                    """, unsafe_allow_html=True)
                    for i, r in enumerate(go_stocks, 1):
                        ret_c = "#4CAF50" if r["expected_ret"] > 0 else "#ef5350"
                        act = r.get("action", "GO")
                        act_c = r.get("action_color", "#4CAF50")
                        is_strong = act == "STRONG GO"
                        border_c = "#00E676" if is_strong else "#1B5E20"
                        rank_c = "#00E676" if is_strong else "#4CAF50"
                        st.markdown(f"""
                        <div style="display:flex;gap:6px;padding:10px 12px;background:#0a1a0a;border:1px solid {border_c};border-radius:8px;margin-bottom:4px;align-items:center">
                            <div style="min-width:30px;font-size:16px;font-weight:900;color:{rank_c}">{i}</div>
                            <div style="min-width:60px;font-size:14px;font-weight:800;color:#ffffff">{r['ticker']}</div>
                            <div style="flex:1;font-size:12px;color:#b0bcd4">{r['name']}</div>
                            <div style="min-width:55px;text-align:center;font-size:18px;font-weight:900;color:{rank_c}">{r['conviction']:.0f}</div>
                            <div style="min-width:55px;text-align:center;font-size:16px;font-weight:800;color:{rank_c}">{r.get('conviction_score',0):.0f}</div>
                            <div style="min-width:50px;text-align:center;font-size:14px;font-weight:700;color:#FFC107">{r.get('cap_score',0):.0f}</div>
                            <div style="min-width:50px;text-align:center;font-size:14px;font-weight:700;color:#AB47BC">{r.get('force_score',0):.0f}</div>
                            <div style="min-width:50px;text-align:center;font-size:14px;font-weight:700;color:#29B6F6">{r.get('timing_score',0):.0f}</div>
                            <div style="min-width:65px;text-align:center;font-size:14px;font-weight:700;color:{ret_c}">{r['expected_ret']:+.0f}%</div>
                            <div style="min-width:80px;text-align:center"><span style="background:{act_c};color:#000;font-weight:900;font-size:{'9' if is_strong else '10'}px;padding:3px 8px;border-radius:10px">{'⚡ STRONG GO' if is_strong else '🔥 GO'}</span></div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

                # ── SECTION 2: PATIENCE ZONE ──────────────────
                st.markdown("""
                <div style="background:linear-gradient(135deg,#1a1a0a,#2a2a0a);border:2px solid #FFC107;border-radius:16px;padding:20px;margin:16px 0">
                    <div style="font-size:14px;font-weight:900;color:#FFC107;letter-spacing:3px;text-align:center">🟡 PATIENCE ZONE — FUTURE OPPORTUNITIES</div>
                    <div style="font-size:11px;color:#FFD54F;text-align:center;margin-top:4px">Maximum 20 stocks. Thesis strong but timing, conviction, or capital flow not fully confirmed.</div>
                </div>
                """, unsafe_allow_html=True)

                if not wait_stocks:
                    st.info("No stocks in WAIT zone.")
                else:
                    for r in wait_stocks:
                        wait_reason = r.get("action_desc", "Awaiting catalyst confirmation")
                        st.markdown(f"""
                        <div style="display:flex;gap:8px;padding:10px 12px;background:#1a1a0a;border:1px solid #33291a;border-radius:8px;margin-bottom:4px;align-items:center">
                            <div style="min-width:60px;font-size:14px;font-weight:800;color:#ffffff">{r['ticker']}</div>
                            <div style="min-width:45px;text-align:center;font-size:16px;font-weight:900;color:#FFC107">{r['conviction']:.0f}</div>
                            <div style="min-width:45px;text-align:center;font-size:14px;font-weight:700;color:#FFC107">{r.get('conviction_score',0):.0f}</div>
                            <div style="flex:1;font-size:11px;color:#b0a87a">{r['name']} — {r.get('theme_icon','')} {r.get('theme','')}</div>
                            <div style="font-size:11px;color:#FFD54F;max-width:300px">{wait_reason}</div>
                            <div style="min-width:40px;text-align:center"><span style="background:#FFC107;color:#000;font-weight:900;font-size:10px;padding:3px 8px;border-radius:10px">WAIT</span></div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

                # ── SECTION 3: HUNTER UNIVERSE TOP 50 ─────────
                st.markdown("""
                <div style="background:linear-gradient(135deg,#0a0a1e,#0a1a2e);border:2px solid #06b6d4;border-radius:16px;padding:20px;margin:16px 0">
                    <div style="font-size:14px;font-weight:900;color:#06b6d4;letter-spacing:3px;text-align:center">🔭 HUNTER UNIVERSE — TOP 50 BY CAPITAL PROBABILITY</div>
                    <div style="font-size:11px;color:#4DD0E1;text-align:center;margin-top:4px">Global ranking by Hunter Score. Ranked by probability of future capital inflow.</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div style="display:flex;gap:6px;padding:8px 12px;background:#0d1117;border-radius:8px;margin-bottom:4px;font-size:9px;color:#8a9bb5;font-weight:700;letter-spacing:1px">
                    <div style="min-width:28px">#</div>
                    <div style="min-width:55px">TICKER</div>
                    <div style="flex:1">COMPANY</div>
                    <div style="min-width:50px;text-align:center">HUNTER</div>
                    <div style="min-width:50px;text-align:center">CONV</div>
                    <div style="min-width:50px;text-align:center">CAP</div>
                    <div style="min-width:50px;text-align:center">FORCE</div>
                    <div style="min-width:50px;text-align:center">CROWD</div>
                    <div style="min-width:65px;text-align:center">THEME</div>
                    <div style="min-width:50px;text-align:center">ACTION</div>
                </div>
                """, unsafe_allow_html=True)

                for i, r in enumerate(top50, 1):
                    hs_val = r["conviction"]
                    hc = "#00E676" if hs_val >= 95 else ("#4CAF50" if hs_val >= 90 else ("#FFC107" if hs_val >= 80 else "#78909C"))
                    act = r.get("action", "PASS")
                    act_c = r.get("action_color", "#78909C")
                    is_go = act in ("STRONG GO", "GO")
                    bg = "#0a1a0a" if is_go else ("#1a1a0a" if act == "WAIT" else "#0d1117")
                    act_label = "⚡ S-GO" if act == "STRONG GO" else act
                    st.markdown(f"""
                    <div style="display:flex;gap:6px;padding:6px 12px;background:{bg};border-radius:6px;margin-bottom:2px;align-items:center;border-left:3px solid {act_c}">
                        <div style="min-width:28px;font-size:12px;font-weight:700;color:#8a9bb5">{i}</div>
                        <div style="min-width:55px;font-size:12px;font-weight:800;color:#ffffff">{r['ticker']}</div>
                        <div style="flex:1;font-size:11px;color:#b0bcd4">{r['name']}</div>
                        <div style="min-width:50px;text-align:center;font-size:14px;font-weight:900;color:{hc}">{hs_val:.0f}</div>
                        <div style="min-width:50px;text-align:center;font-size:12px;font-weight:700;color:{hc}">{r.get('conviction_score',0):.0f}</div>
                        <div style="min-width:50px;text-align:center;font-size:12px;color:#FFC107">{r.get('cap_score',0):.0f}</div>
                        <div style="min-width:50px;text-align:center;font-size:12px;color:#AB47BC">{r.get('force_score',0):.0f}</div>
                        <div style="min-width:50px;text-align:center;font-size:12px;color:{'#4CAF50' if r.get('crowding_score',50)<60 else '#ef5350'}">{r.get('crowding_score',0):.0f}</div>
                        <div style="min-width:65px;text-align:center;font-size:10px;color:#8a9bb5">{r.get('theme_icon','')} {r.get('theme','')[:12]}</div>
                        <div style="min-width:50px;text-align:center"><span style="background:{act_c};color:#000;font-weight:900;font-size:9px;padding:2px 6px;border-radius:8px">{act_label}</span></div>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Command Center scan failed: {e}")

    with cmd_tab2:
        st.markdown("### 🔍 Deep Analysis — Single Stock Intelligence")
        hunter_ticker = st.text_input("Run CFIS Hunter on any ticker", placeholder="e.g. NVDA, SPCX, RKLB, ETN, SHOP, SONY", key="hunter_ticker")
        if hunter_ticker:
            hunter_ticker = hunter_ticker.upper().strip()
            with st.spinner(f"Running full Hunter + Capital Intelligence on {hunter_ticker}…"):
                try:
                    tk_obj = yf.Ticker(hunter_ticker)
                    info = tk_obj.info or {}
                    hist = tk_obj.history(period="1y")
                    if hist.empty:
                        st.error("No data available for this ticker.")
                    else:
                        scores = compute_all_scores(info, hist, None, None)
                        cm = compute_capital_migration(info, hist, hunter_ticker)
                        enriched = fetch_enriched_data(hunter_ticker)
                        hunter = compute_hunter(info, hist, scores, cm, enriched)
                        render_hunter(hunter, hunter_ticker, cm)

                        st.markdown("---")
                        with st.spinner("Running Capital Flow Intelligence…"):
                            ci = compute_capital_intelligence(hunter_ticker, info, hist, scores, cm, hunter)
                            render_capital_intelligence(ci, hunter_ticker, hunter)

                        st.markdown("---")
                        with st.spinner("Running Smart Money Pressure Map…"):
                            smp = compute_smart_money_pressure(hunter_ticker)
                            render_smart_money_pressure(smp, hunter_ticker)

                        dq = enriched.get("data_quality", 0)
                        sources = enriched.get("data_sources", [])
                        st.markdown(f"""
                        <div style="background:#0d1117;border:1px solid #21262d;border-radius:10px;padding:12px;margin-top:12px">
                            <div style="font-size:10px;color:#8b949e;letter-spacing:2px;font-weight:700;margin-bottom:6px">DATA QUALITY</div>
                            <div style="display:flex;gap:16px;align-items:center">
                                <div style="font-size:20px;font-weight:800;color:{'#4CAF50' if dq >= 70 else '#FFC107' if dq >= 40 else '#f44336'}">{dq}%</div>
                                <div style="font-size:11px;color:#8b949e">Sources: {', '.join(s.upper() for s in sources) if sources else 'yfinance only'}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error analyzing {hunter_ticker}: {e}")

    with cmd_tab3:
        st.markdown("### 🌐 Global Hunter Universe")
        st.markdown(f"""
        <div style="background:#161b27;border-radius:12px;padding:16px;margin-bottom:16px">
            <div style="font-size:12px;color:#06b6d4;font-weight:700;margin-bottom:8px">UNIVERSE COVERAGE</div>
            <div style="font-size:13px;color:#e8ecf4;line-height:1.8">
                <strong>Total Universe:</strong> {len(FULL_UNIVERSE)} stocks<br>
                <strong>Regions:</strong> USA, Canada, Europe, Japan, Singapore, Hong Kong, Asia<br>
                <strong>Filter:</strong> Market Cap &gt; USD 500M · Sufficient liquidity · Sufficient data<br>
                <strong>Themes:</strong> AI · Robotics · Energy · Nuclear · Space · Defense · Cybersecurity · Biotech · Digital Assets · Tokenization
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#161b27;border-radius:12px;padding:16px;margin-bottom:16px">
            <div style="font-size:12px;color:#FFC107;font-weight:700;margin-bottom:8px">INTELLIGENCE SOURCES — WEIGHTED</div>
            <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:8px">
                <div style="background:#0d1117;border-radius:8px;padding:8px 14px;text-align:center"><div style="font-size:18px;font-weight:900;color:#4FC3F7">30%</div><div style="font-size:9px;color:#8a9bb5">Institutional</div></div>
                <div style="background:#0d1117;border-radius:8px;padding:8px 14px;text-align:center"><div style="font-size:18px;font-weight:900;color:#FFA726">20%</div><div style="font-size:9px;color:#8a9bb5">Alt Data</div></div>
                <div style="background:#0d1117;border-radius:8px;padding:8px 14px;text-align:center"><div style="font-size:18px;font-weight:900;color:#AB47BC">15%</div><div style="font-size:9px;color:#8a9bb5">Options</div></div>
                <div style="background:#0d1117;border-radius:8px;padding:8px 14px;text-align:center"><div style="font-size:18px;font-weight:900;color:#66BB6A">15%</div><div style="font-size:9px;color:#8a9bb5">Fundamentals</div></div>
                <div style="background:#0d1117;border-radius:8px;padding:8px 14px;text-align:center"><div style="font-size:18px;font-weight:900;color:#FF7043">10%</div><div style="font-size:9px;color:#8a9bb5">News</div></div>
                <div style="background:#0d1117;border-radius:8px;padding:8px 14px;text-align:center"><div style="font-size:18px;font-weight:900;color:#EC407A">10%</div><div style="font-size:9px;color:#8a9bb5">Social</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#161b27;border-radius:12px;padding:16px">
            <div style="font-size:12px;color:#4CAF50;font-weight:700;margin-bottom:8px">ACTION ENGINE RULES</div>
            <div style="font-size:12px;color:#c9d1d9;line-height:2.0">
                <strong style="color:#4CAF50">🔥 GO</strong> — Hunter &gt; 92 + Conviction &gt; 85 + CAP &gt; 90 + Force &gt; 85 + Timing &gt; 80 + Crowding &lt; 70<br>
                <strong style="color:#FFC107">🟡 WAIT</strong> — Hunter &gt; 90 but timing insufficient, catalyst not mature, capital flow not confirmed<br>
                <strong style="color:#78909C">❌ PASS</strong> — Everything else. Not displayed in GO or WAIT zones.<br><br>
                <strong style="color:#FF9800">🔥 HUNT ALERT</strong> — CAP &gt; 90 + Force &gt; 85 + Timing &gt; 80 + Conviction &gt; 85 + Crowding &lt; 60
            </div>
        </div>
        """, unsafe_allow_html=True)

    with cmd_tab4:
        st.markdown("### 💰 Smart Money Pressure Map™")
        st.markdown("""
        <div style="background:#161b27;border-radius:12px;padding:16px;margin-bottom:16px">
            <div style="font-size:11px;color:#FF9800;letter-spacing:2px;font-weight:700;margin-bottom:8px">EVIDENCE-BASED PRESSURE DETECTION</div>
            <div style="font-size:12px;color:#c9d1d9;line-height:1.8">
                Detects institutional pressure, liquidity pressure, squeeze pressure, and hidden accumulation/distribution.<br>
                This module is <strong>evidence-based</strong>. It does not make conspiracy claims or accuse specific actors of manipulation.<br>
                The goal is to detect <strong>measurable pressure</strong> from 7 data components.
            </div>
        </div>
        """, unsafe_allow_html=True)

        smp_ticker = st.text_input("Analyze Smart Money Pressure", placeholder="e.g. NVDA, PLTR, RKLB", key="smp_ticker")
        if smp_ticker:
            smp_ticker = smp_ticker.upper().strip()
            with st.spinner(f"Running Smart Money Pressure Map on {smp_ticker}…"):
                try:
                    smp = compute_smart_money_pressure(smp_ticker)
                    render_smart_money_pressure(smp, smp_ticker)
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("---")
        st.markdown("#### Quick Scan — Top GO/WAIT Stocks")
        if st.button("Scan Smart Money for top opportunities", key="smp_scan"):
            with st.spinner("Scanning Smart Money Pressure for top-rated stocks…"):
                try:
                    all_opps = scan_opportunities(tuple(FULL_UNIVERSE))
                    top_tickers = [r["ticker"] for r in sorted(all_opps, key=lambda x: x["conviction"], reverse=True) if r.get("action") in ("STRONG GO", "GO", "WAIT")][:15]
                    if not top_tickers:
                        top_tickers = [r["ticker"] for r in sorted(all_opps, key=lambda x: x["conviction"], reverse=True)][:10]

                    smp_results = []
                    for t in top_tickers:
                        try:
                            smp = compute_smart_money_pressure(t)
                            smp_results.append(smp)
                        except Exception:
                            pass

                    smp_results.sort(key=lambda x: x["score"], reverse=True)

                    for smp in smp_results:
                        sc_color = {"Strong Accumulation": "#4CAF50", "Accumulation": "#66BB6A", "Squeeze Setup": "#FF9800",
                                    "Neutral": "#78909C", "Distribution": "#f44336", "Short Pressure": "#AB47BC", "Danger Zone": "#D32F2F"}.get(smp["signal"], "#78909C")
                        st.markdown(f"""
                        <div style="background:#161b27;border-radius:10px;padding:12px 16px;margin-bottom:6px;display:flex;align-items:center;gap:16px">
                            <div style="min-width:60px;font-size:16px;font-weight:900;color:#ffffff">{smp['ticker']}</div>
                            <div style="min-width:50px;text-align:center;font-size:22px;font-weight:900;color:{sc_color}">{smp['score']}</div>
                            <div style="min-width:120px"><span style="background:{sc_color}22;color:{sc_color};padding:3px 10px;border-radius:8px;font-size:11px;font-weight:700">{smp['signal'].upper()}</span></div>
                            <div style="flex:1;font-size:11px;color:#b0bcd4">{smp['evidence']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("""
        <div style="background:#0d1117;border:1px solid #21262d;border-radius:12px;padding:16px;margin-top:20px">
            <div style="font-size:10px;color:#FFC107;letter-spacing:2px;font-weight:700;margin-bottom:8px">METHODOLOGY</div>
            <div style="font-size:11px;color:#c9d1d9;line-height:2.0">
                <strong style="color:#FF7043">Dark Pool (20%)</strong> — Volume/price divergence, absorption patterns, block trades<br>
                <strong style="color:#FF9800">Off-Exchange (15%)</strong> — Volume trend analysis, 10d/30d averages, spike detection<br>
                <strong style="color:#AB47BC">Options Flow (20%)</strong> — Put/call ratios, OTM call volume, premium analysis<br>
                <strong style="color:#4FC3F7">Gamma/Dealer (15%)</strong> — Call/put walls, max pain, gamma exposure direction<br>
                <strong style="color:#f44336">Short Interest (15%)</strong> — Short float %, days to cover, squeeze setup detection<br>
                <strong style="color:#66BB6A">ETF Flow (10%)</strong> — Market cap/index eligibility, sector rotation, thematic exposure<br>
                <strong style="color:#FFC107">FTD/Settlement (5%)</strong> — Settlement stress signals from volume/price anomalies
            </div>
        </div>
        """, unsafe_allow_html=True)

