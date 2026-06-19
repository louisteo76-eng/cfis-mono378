"""
Institutional Macro & Strategic Flow Layer.

Scores stocks across 5 structural dimensions that approximate how
institutional capital allocators (sovereign funds, pensions, macro desks)
evaluate strategic positioning:

  1. Government Strategic Alignment (25%)
  2. Geopolitical Trend Exposure (20%)
  3. Sovereign / Institutional Capital Direction (20%)
  4. Elite Knowledge / Future Technology Signals (20%)
  5. Financial System / Central Bank Signals (15%)

All scoring uses publicly available data (yfinance fundamentals, company
descriptions, sector/industry classification, news headlines when enriched
data is provided). Scores are heuristic proxies, not direct institutional
flow data — every output is tagged with source_type = "proxy" or "direct".

This module has NO Streamlit dependency and can be imported standalone.

Usage from app.py:
  from services.strategic_flow import compute_strategic_flow
  result = compute_strategic_flow("NVDA", info, hist, enriched)
"""

import logging
import math
from datetime import date

log = logging.getLogger("cfis.strategic_flow")


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _safe(info, *keys, default=None):
    for k in keys:
        v = info.get(k)
        if v is not None:
            try:
                f = float(v)
                if not math.isnan(f):
                    return f
            except (TypeError, ValueError):
                return v
    return default


def _clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def _keyword_hits(text, keywords):
    return sum(1 for kw in keywords if kw in text)


# ─────────────────────────────────────────────────────────────
# DIMENSION 1: GOVERNMENT STRATEGIC ALIGNMENT (25%)
# ─────────────────────────────────────────────────────────────

_GOV_KEYWORDS = {
    "industrial_policy": [
        "chips act", "inflation reduction act", "ira", "defense production act",
        "bipartisan infrastructure", "infrastructure investment", "build america",
        "industrial policy", "manufacturing incentive", "reshoring",
        "onshoring", "made in america", "buy american",
    ],
    "defense_national_security": [
        "defense", "pentagon", "department of defense", "darpa", "national security",
        "intelligence community", "homeland security", "nato", "aukus",
        "military", "weapons system", "missile", "submarine", "fighter jet",
        "drone", "uav", "electronic warfare", "cybersecurity", "classified",
    ],
    "energy_climate": [
        "clean energy", "renewable", "solar", "wind", "nuclear",
        "grid modernization", "energy storage", "battery", "hydrogen",
        "carbon capture", "electric vehicle", "ev", "charging",
        "department of energy", "doe", "nrc", "ferc",
    ],
    "critical_minerals": [
        "rare earth", "lithium", "cobalt", "uranium", "critical mineral",
        "strategic reserve", "mineral security", "mining", "processing",
        "refining", "supply chain security",
    ],
    "ai_infrastructure": [
        "artificial intelligence", " ai ", "data center", "cloud computing",
        "gpu", "semiconductor", "chip", "foundry", "advanced packaging",
        "export control", "entity list",
    ],
    "sanctions_trade": [
        "sanction", "tariff", "export control", "trade restriction",
        "entity list", "embargo", "trade war", "decoupling",
    ],
}

_GOV_SECTOR_BOOST = {
    "industrials": 10, "technology": 8, "energy": 12, "utilities": 8,
    "basic materials": 8, "healthcare": 5,
}

_GOV_INDUSTRY_BOOST = {
    "aerospace": 20, "defense": 25, "semiconductor": 18, "nuclear": 20,
    "solar": 15, "uranium": 18, "cybersecurity": 15, "rare earth": 20,
    "lithium": 15, "cobalt": 15, "data center": 15, "electric vehicle": 12,
    "grid": 12, "robotics": 10, "space": 15, "satellite": 12,
}


def _score_government(info, search_text):
    s = 10
    reasons = []
    confidence = 30

    sector = (info.get("sector", "") or "").lower()
    industry = (info.get("industry", "") or "").lower()

    for key, boost in _GOV_SECTOR_BOOST.items():
        if key in sector:
            s += boost
            break

    for key, boost in _GOV_INDUSTRY_BOOST.items():
        if key in industry or key in sector:
            s += boost
            reasons.append(f"Industry aligned: {key}")
            confidence += 15
            break

    total_kw_hits = 0
    for category, keywords in _GOV_KEYWORDS.items():
        hits = _keyword_hits(search_text, keywords)
        total_kw_hits += hits
        if hits >= 4:
            s += 15
            reasons.append(f"{category}: {hits} keyword signals (strong)")
            confidence += 10
        elif hits >= 2:
            s += 8
            reasons.append(f"{category}: {hits} keyword signals")
            confidence += 5
        elif hits >= 1:
            s += 3

    mc = _safe(info, "marketCap", default=0) or 0
    if mc > 50e9 and total_kw_hits >= 3:
        s += 8
        reasons.append("Large cap + strategic sector = government procurement target")

    return {
        "score": _clamp(s),
        "reasons": reasons or ["No strong government alignment detected"],
        "confidence": min(confidence, 95),
        "source_type": "proxy",
        "evidence": "keyword scan of company description, sector, industry",
    }


# ─────────────────────────────────────────────────────────────
# DIMENSION 2: GEOPOLITICAL TREND EXPOSURE (20%)
# ─────────────────────────────────────────────────────────────

_GEOPOLITICAL_KEYWORDS = {
    "us_china": [
        "china", "chinese", "beijing", "huawei", "tencent", "alibaba",
        "us-china", "trade war", "decoupling", "entity list", "taiwan",
        "tsmc", "export control", "brics",
    ],
    "taiwan_semiconductor": [
        "taiwan", "tsmc", "semiconductor", "foundry", "chip",
        "advanced packaging", "euv", "lithography",
    ],
    "energy_security": [
        "opec", "oil", "natural gas", "lng", "pipeline", "refinery",
        "strategic petroleum", "energy independence", "energy security",
        "middle east", "persian gulf", "strait of hormuz",
    ],
    "defense_conflict": [
        "ukraine", "russia", "nato", "rearmament", "defense spending",
        "weapons", "ammunition", "drone warfare", "missile defense",
        "red sea", "houthi", "shipping disruption", "suez",
    ],
    "currency_liquidity": [
        "yen carry", "boj", "bank of japan", "dollar", "dxy",
        "fed funds", "liquidity", "quantitative", "swap line",
        "eurodollar", "treasury", "yield curve",
    ],
}

_GEOPOLITICAL_EXPOSURE = {
    "TSM":  {"score": 90, "dominant": "Taiwan semiconductor risk"},
    "ASML": {"score": 85, "dominant": "EUV monopoly + export controls"},
    "NVDA": {"score": 75, "dominant": "AI export controls + China revenue"},
    "AMD":  {"score": 65, "dominant": "AI chip competition + China restrictions"},
    "INTC": {"score": 70, "dominant": "CHIPS Act beneficiary + China decoupling"},
    "LMT":  {"score": 80, "dominant": "NATO rearmament + defense spending"},
    "RTX":  {"score": 75, "dominant": "NATO demand + missile defense"},
    "NOC":  {"score": 75, "dominant": "B-21 + nuclear deterrence"},
    "GD":   {"score": 70, "dominant": "Submarine + vehicle programs"},
    "CCJ":  {"score": 70, "dominant": "Uranium supply + nuclear restarts"},
    "XOM":  {"score": 60, "dominant": "Energy security + OPEC dynamics"},
    "CVX":  {"score": 60, "dominant": "Energy security + LNG"},
    "FSLR": {"score": 65, "dominant": "IRA + tariff protection"},
    "MP":   {"score": 70, "dominant": "Rare earth independence from China"},
}


def _score_geopolitical(ticker, info, search_text):
    s = 10
    reasons = []
    confidence = 25
    t = ticker.upper()

    if t in _GEOPOLITICAL_EXPOSURE:
        known = _GEOPOLITICAL_EXPOSURE[t]
        s = max(s, known["score"])
        reasons.append(f"Known geopolitical exposure: {known['dominant']}")
        confidence = 70

    for theme, keywords in _GEOPOLITICAL_KEYWORDS.items():
        hits = _keyword_hits(search_text, keywords)
        if hits >= 4:
            s = max(s, 60)
            reasons.append(f"{theme}: {hits} signals (high exposure)")
            confidence = max(confidence, 55)
        elif hits >= 2:
            s = max(s, 35)
            reasons.append(f"{theme}: {hits} signals")
            confidence = max(confidence, 40)
        elif hits >= 1:
            s = max(s, 15)

    country = (info.get("country", "") or "").lower()
    if country in ("china", "taiwan", "russia", "israel", "saudi arabia"):
        s += 15
        reasons.append(f"Domiciled in geopolitically sensitive region: {country}")
        confidence += 10

    return {
        "score": _clamp(s),
        "reasons": reasons or ["Low geopolitical exposure"],
        "confidence": min(confidence, 95),
        "source_type": "proxy",
        "evidence": "keyword scan, known ticker map, country of domicile",
    }


# ─────────────────────────────────────────────────────────────
# DIMENSION 3: SOVEREIGN / INSTITUTIONAL CAPITAL DIRECTION (20%)
# ─────────────────────────────────────────────────────────────

_INSTITUTIONAL_THEMES = {
    "ai_data_centers": [
        "artificial intelligence", " ai ", "data center", "cloud", "gpu",
        "machine learning", "training", "inference", "foundation model",
    ],
    "defense_technology": [
        "defense", "military", "weapon", "drone", "cybersecurity",
        "surveillance", "intelligence", "satellite",
    ],
    "energy_security": [
        "nuclear", "uranium", "solar", "wind", "grid", "battery",
        "energy storage", "hydrogen", "lng", "natural gas", "baseload",
    ],
    "healthcare_resilience": [
        "biotech", "pharmaceutical", "drug discovery", "medical device",
        "diagnostics", "hospital", "telemedicine", "gene therapy",
        "longevity", "obesity",
    ],
    "infrastructure": [
        "infrastructure", "construction", "water", "utilities",
        "transportation", "highway", "bridge", "rail", "port",
    ],
    "critical_materials": [
        "rare earth", "lithium", "cobalt", "copper", "nickel",
        "critical mineral", "mining", "processing",
    ],
    "food_water_security": [
        "agriculture", "farming", "irrigation", "water treatment",
        "water purification", "food production", "fertilizer",
        "crop", "aquaculture",
    ],
}


def _score_institutional(ticker, info, search_text):
    s = 10
    reasons = []
    confidence = 25

    mc = _safe(info, "marketCap", default=0) or 0
    if mc > 200e9:
        s += 20
        reasons.append("Mega-cap: core sovereign/pension holding")
        confidence += 15
    elif mc > 50e9:
        s += 12
        reasons.append("Large-cap: institutional benchmark constituent")
        confidence += 10
    elif mc > 10e9:
        s += 5

    inst_pct = _safe(info, "heldPercentInstitutions", default=None)
    if inst_pct is not None:
        if inst_pct > 0.85:
            s += 15
            reasons.append(f"Institutional ownership {inst_pct*100:.0f}% — heavily held by funds")
            confidence += 15
        elif inst_pct > 0.70:
            s += 8
            reasons.append(f"Institutional ownership {inst_pct*100:.0f}%")
            confidence += 8

    matched_themes = []
    for theme, keywords in _INSTITUTIONAL_THEMES.items():
        hits = _keyword_hits(search_text, keywords)
        if hits >= 3:
            s += 10
            matched_themes.append(theme)
            confidence += 5
        elif hits >= 1:
            s += 4
            matched_themes.append(theme)

    if matched_themes:
        labels = [t.replace("_", " ").title() for t in matched_themes[:3]]
        reasons.append(f"Aligned with institutional themes: {', '.join(labels)}")

    div_yield = _safe(info, "dividendYield", default=0) or 0
    if div_yield > 0.02:
        s += 5
        reasons.append(f"Dividend yield {div_yield*100:.1f}% attracts income-mandate capital")

    return {
        "score": _clamp(s),
        "reasons": reasons or ["Limited institutional theme alignment"],
        "confidence": min(confidence, 95),
        "source_type": "proxy",
        "evidence": "market cap, institutional ownership %, theme keywords, dividend yield",
    }


# ─────────────────────────────────────────────────────────────
# DIMENSION 4: ELITE KNOWLEDGE / FUTURE TECHNOLOGY SIGNALS (20%)
# ─────────────────────────────────────────────────────────────

_ELITE_KEYWORDS = {
    "academic_research": [
        "artificial intelligence", "quantum computing", "crispr", "gene editing",
        "fusion", "small modular reactor", "autonomous", "robotics",
        "brain-computer", "synthetic biology", "metamaterial",
        "graphene", "mRNA", "protein folding",
    ],
    "forum_signals": [
        "davos", "world economic forum", "bilderberg", "jackson hole",
        "g7", "g20", "imf", "world bank", "bis", "basel",
        "brookings", "cfr", "council on foreign relations",
        "atlantic council", "aspen", "milken", "abu dhabi",
        "cop28", "cop29", "munich security",
    ],
    "future_tech": [
        "humanoid robot", "autonomous vehicle", "self-driving",
        "space launch", "satellite constellation", "edge computing",
        "digital twin", "6g", "neuromorphic", "photonic",
        "solid state battery", "perovskite", "carbon nanotube",
        "nuclear fusion", "tokamak",
    ],
    "expo_conference": [
        "ces", "mobile world congress", "computex", "semicon",
        "defense expo", "air show", "farnborough", "idex",
        "gitex", "web summit", "collision",
    ],
}

_STRATEGIC_THEME_MAP = {
    "AI Compute":         ["artificial intelligence", " ai ", "gpu", "data center", "training", "inference"],
    "Semiconductors":     ["semiconductor", "chip", "foundry", "wafer", "fab", "lithography", "packaging"],
    "Nuclear Energy":     ["nuclear", "uranium", "reactor", "fission", "smr", "nrc"],
    "Grid Power":         ["grid", "utility", "baseload", "transmission", "transformer", "switchgear"],
    "Defense":            ["defense", "military", "weapon", "drone", "missile", "fighter"],
    "Cybersecurity":      ["cybersecurity", "cyber", "threat detection", "zero trust", "firewall", "siem"],
    "Space":              ["space", "satellite", "launch", "orbit", "rocket", "payload"],
    "Critical Minerals":  ["rare earth", "lithium", "cobalt", "uranium", "critical mineral", "mining"],
    "Water Security":     ["water", "desalination", "purification", "irrigation", "wastewater"],
    "Food Security":      ["agriculture", "crop", "fertilizer", "food production", "aquaculture"],
    "Biotech / Longevity":["biotech", "longevity", "gene therapy", "crispr", "mRNA", "drug discovery"],
    "Tokenized Finance":  ["blockchain", "digital asset", "tokeniz", "stablecoin", "defi", "cbdc"],
    "Private Credit":     ["private credit", "direct lending", "private debt", "mezzanine", "bdc"],
    "Robotics":           ["robot", "cobot", "automation", "actuator", "humanoid"],
    "Energy Security":    ["oil", "gas", "lng", "refinery", "pipeline", "energy independence"],
    "Shipping / Logistics":["shipping", "logistics", "freight", "container", "port", "supply chain"],
}


def _score_elite_knowledge(info, search_text):
    s = 10
    reasons = []
    confidence = 20

    for category, keywords in _ELITE_KEYWORDS.items():
        hits = _keyword_hits(search_text, keywords)
        if hits >= 3:
            s += 15
            reasons.append(f"{category.replace('_', ' ').title()}: {hits} signals (high alignment)")
            confidence += 10
        elif hits >= 1:
            s += 5
            confidence += 3

    matched_themes = []
    for theme_name, keywords in _STRATEGIC_THEME_MAP.items():
        hits = _keyword_hits(search_text, keywords)
        if hits >= 2:
            matched_themes.append(theme_name)

    if matched_themes:
        s += min(len(matched_themes) * 5, 20)
        reasons.append(f"Strategic themes: {', '.join(matched_themes[:5])}")
        confidence += min(len(matched_themes) * 3, 15)

    rg = _safe(info, "revenueGrowth", default=0) or 0
    if rg > 0.30:
        s += 8
        reasons.append(f"Revenue growth {rg*100:.0f}% suggests regime-shift adoption")
        confidence += 5

    return {
        "score": _clamp(s),
        "reasons": reasons or ["No strong elite/future tech alignment"],
        "confidence": min(confidence, 90),
        "source_type": "proxy",
        "evidence": "keyword scan of academic/forum/future tech themes + revenue growth",
        "themes": matched_themes,
    }


# ─────────────────────────────────────────────────────────────
# DIMENSION 5: FINANCIAL SYSTEM / CENTRAL BANK SIGNALS (15%)
# ─────────────────────────────────────────────────────────────

_FINANCIAL_SYSTEM_KEYWORDS = {
    "rate_regime": [
        "interest rate", "fed funds", "federal reserve", "monetary policy",
        "rate sensitive", "duration", "yield",
    ],
    "liquidity": [
        "liquidity", "quantitative", "balance sheet", "repo", "reverse repo",
        "money market", "bank reserve", "swap line", "tga",
    ],
    "bank_regulation": [
        "basel", "capital requirement", "stress test", "fdic",
        "systemically important", "g-sib", "leverage ratio",
        "risk-weighted", "tier 1", "cet1",
    ],
    "credit_risk": [
        "credit spread", "high yield", "investment grade", "default",
        "private credit", "direct lending", "leveraged loan",
        "distressed", "bankruptcy",
    ],
    "currency_carry": [
        "yen carry", "dollar index", "dxy", "emerging market",
        "fx", "currency", "capital flight", "devaluation",
    ],
}

_RATE_SENSITIVE_SECTORS = {
    "financial services": 20, "real estate": 18, "utilities": 15,
}


def _score_financial_system(info, search_text, hist=None):
    s = 15
    reasons = []
    confidence = 25

    sector = (info.get("sector", "") or "").lower()
    industry = (info.get("industry", "") or "").lower()

    for key, boost in _RATE_SENSITIVE_SECTORS.items():
        if key in sector:
            s += boost
            reasons.append(f"Rate-sensitive sector: {key}")
            confidence += 10
            break

    for category, keywords in _FINANCIAL_SYSTEM_KEYWORDS.items():
        hits = _keyword_hits(search_text, keywords)
        if hits >= 3:
            s += 12
            reasons.append(f"{category.replace('_', ' ').title()}: {hits} signals")
            confidence += 8
        elif hits >= 1:
            s += 4
            confidence += 3

    beta = _safe(info, "beta", default=None)
    if beta is not None:
        if beta > 1.5:
            s += 10
            reasons.append(f"High beta {beta:.2f} — amplifies macro/rate regime shifts")
            confidence += 5
        elif beta < 0.6:
            s += 5
            reasons.append(f"Low beta {beta:.2f} — defensive positioning in risk-off regime")

    debt_eq = _safe(info, "debtToEquity", default=None)
    if debt_eq is not None and debt_eq > 150:
        s += 8
        reasons.append(f"Debt/Equity {debt_eq:.0f}% — sensitive to rate/liquidity regime")
        confidence += 5

    if "bank" in industry or "insurance" in industry or "capital markets" in industry:
        s += 10
        reasons.append("Financial industry — directly exposed to Basel/regulatory regime")
        confidence += 10

    return {
        "score": _clamp(s),
        "reasons": reasons or ["Low financial system sensitivity"],
        "confidence": min(confidence, 90),
        "source_type": "proxy",
        "evidence": "sector classification, beta, debt/equity, keyword scan",
    }


# ─────────────────────────────────────────────────────────────
# KNOWN TICKER OVERRIDES
# ─────────────────────────────────────────────────────────────

STRATEGIC_OVERRIDES = {
    "LMT":  {"floor": 75, "label": "Strategic Tailwind", "dominant": "Defense prime — NATO rearmament cycle"},
    "RTX":  {"floor": 72, "label": "Strategic Tailwind", "dominant": "Missile + engine demand — defense spend"},
    "NOC":  {"floor": 72, "label": "Strategic Tailwind", "dominant": "B-21 Raider + nuclear triad"},
    "GD":   {"floor": 68, "label": "Strategic Tailwind", "dominant": "Submarines + armored vehicles"},
    "TSM":  {"floor": 80, "label": "Strategic Tailwind", "dominant": "Geopolitical semiconductor chokepoint"},
    "ASML": {"floor": 78, "label": "Strategic Tailwind", "dominant": "EUV lithography monopoly"},
    "NVDA": {"floor": 82, "label": "Strategic Tailwind", "dominant": "AI compute monopoly + sovereign AI"},
    "AMD":  {"floor": 68, "label": "Strategic Tailwind", "dominant": "AI GPU challenger + data center"},
    "AVGO": {"floor": 70, "label": "Strategic Tailwind", "dominant": "Custom AI silicon + networking"},
    "INTC": {"floor": 65, "label": "Strategic Tailwind", "dominant": "CHIPS Act beneficiary — US fab capacity"},
    "CCJ":  {"floor": 68, "label": "Strategic Tailwind", "dominant": "Uranium supply chokepoint"},
    "MP":   {"floor": 70, "label": "Strategic Tailwind", "dominant": "Only US rare earth mine"},
    "FSLR": {"floor": 68, "label": "Strategic Tailwind", "dominant": "US solar manufacturing + IRA"},
    "VST":  {"floor": 65, "label": "Strategic Tailwind", "dominant": "AI power demand + grid baseload"},
    "OKLO": {"floor": 62, "label": "Strategic Tailwind", "dominant": "SMR + Altman-backed nuclear"},
    "SMR":  {"floor": 60, "label": "Strategic Tailwind", "dominant": "NRC-approved small modular reactor"},
    "RKLB": {"floor": 62, "label": "Strategic Tailwind", "dominant": "Space launch sovereignty"},
    "KTOS": {"floor": 60, "label": "Strategic Tailwind", "dominant": "Autonomous drone warfare"},
    "PLTR": {"floor": 72, "label": "Strategic Tailwind", "dominant": "DoD/IC AI platform — sovereign data"},
    "CRWD": {"floor": 68, "label": "Strategic Tailwind", "dominant": "Government cyber mandates"},
    "LHX":  {"floor": 65, "label": "Strategic Tailwind", "dominant": "Space ISR + electronic warfare"},
    "LDOS": {"floor": 65, "label": "Strategic Tailwind", "dominant": "Government IT backbone"},
    "NET":  {"floor": 58, "label": "Strategic Tailwind", "dominant": "Edge + zero trust cyber"},
    "LAC":  {"floor": 60, "label": "Strategic Tailwind", "dominant": "US lithium — Thacker Pass"},
    "REGN": {"floor": 60, "label": "Strategic Tailwind", "dominant": "Antibody platform — longevity capital"},
    "ISRG": {"floor": 62, "label": "Strategic Tailwind", "dominant": "Surgical robotics monopoly"},
    "AXON": {"floor": 60, "label": "Strategic Tailwind", "dominant": "Law enforcement tech — sticky gov contracts"},
}


# ─────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────

DIMENSION_WEIGHTS = {
    "government":        0.25,
    "geopolitical":      0.20,
    "institutional":     0.20,
    "elite_knowledge":   0.20,
    "financial_system":  0.15,
}


def compute_strategic_flow(ticker, info, hist, enriched=None):
    """Compute the Institutional Macro & Strategic Flow score for a ticker.

    Args:
        ticker: Stock symbol (e.g. "NVDA")
        info: yfinance .info dict
        hist: yfinance historical DataFrame
        enriched: Optional enriched data dict (news_headlines, etc.)

    Returns dict:
        score (0-100), label, themes, reasons, confidence (0-100),
        source_type ("proxy"|"direct"), updated_at, dimensions {},
        dominant_force, catalyst_window, policy_risk, capital_flow
    """
    enriched = enriched or {}
    t = ticker.upper()

    summary = (info.get("longBusinessSummary", "") or "").lower()
    sector = (info.get("sector", "") or "").lower()
    industry = (info.get("industry", "") or "").lower()
    headlines = " ".join(enriched.get("news_headlines", [])).lower()
    search_text = " ".join([summary, sector, industry, headlines])

    d1 = _score_government(info, search_text)
    d2 = _score_geopolitical(t, info, search_text)
    d3 = _score_institutional(t, info, search_text)
    d4 = _score_elite_knowledge(info, search_text)
    d5 = _score_financial_system(info, search_text, hist)

    dimensions = {
        "government": d1,
        "geopolitical": d2,
        "institutional": d3,
        "elite_knowledge": d4,
        "financial_system": d5,
    }

    raw_score = (
        d1["score"] * DIMENSION_WEIGHTS["government"] +
        d2["score"] * DIMENSION_WEIGHTS["geopolitical"] +
        d3["score"] * DIMENSION_WEIGHTS["institutional"] +
        d4["score"] * DIMENSION_WEIGHTS["elite_knowledge"] +
        d5["score"] * DIMENSION_WEIGHTS["financial_system"]
    )

    if t in STRATEGIC_OVERRIDES:
        override = STRATEGIC_OVERRIDES[t]
        raw_score = max(raw_score, override["floor"])

    score = _clamp(round(raw_score, 1))

    if score >= 65:
        label = "Strategic Tailwind"
    elif score >= 40:
        label = "Neutral"
    else:
        label = "Strategic Headwind"

    if t in STRATEGIC_OVERRIDES:
        label = STRATEGIC_OVERRIDES[t].get("label", label)

    all_reasons = []
    for dim in dimensions.values():
        all_reasons.extend(dim.get("reasons", []))

    themes = d4.get("themes", [])

    avg_confidence = sum(d["confidence"] for d in dimensions.values()) / len(dimensions)

    any_direct = any(d.get("source_type") == "direct" for d in dimensions.values())
    source_type = "direct" if any_direct else "proxy"

    dominant_dim = max(dimensions, key=lambda k: dimensions[k]["score"])
    dominant_labels = {
        "government": "Government Strategic Alignment",
        "geopolitical": "Geopolitical Trend Exposure",
        "institutional": "Institutional Capital Direction",
        "elite_knowledge": "Elite Knowledge / Future Tech",
        "financial_system": "Financial System / Central Bank",
    }

    catalyst_window = ""
    if t in STRATEGIC_OVERRIDES:
        catalyst_window = STRATEGIC_OVERRIDES[t].get("dominant", "")

    policy_risk = 0
    if d1["score"] > 60:
        policy_risk = min(100, d1["score"] - 10)

    if score >= 65:
        capital_flow = "Strong Inflow"
    elif score >= 45:
        capital_flow = "Building"
    elif score >= 25:
        capital_flow = "Neutral"
    else:
        capital_flow = "No Signal"

    return {
        "score": score,
        "label": label,
        "themes": themes,
        "reasons": all_reasons,
        "confidence": round(avg_confidence),
        "source_type": source_type,
        "updated_at": date.today().isoformat(),
        "dimensions": dimensions,
        "dominant_force": dominant_labels.get(dominant_dim, "Unknown"),
        "catalyst_window": catalyst_window,
        "policy_risk": policy_risk,
        "capital_flow": capital_flow,
    }
