"""
Louis Regeneration Index™ — Sidebar 9

"Leave Things Better Than You Found Them."

Symbol: The Banyan Tree™

This is a REFLECTION LAYER ONLY. It does NOT participate in trading
decisions. It does NOT override buy/sell signals, conviction scores,
position sizes, portfolio weights, or any other CFIS core engine output.

7 sub-modules, each scoring 0-100:
  1. Regeneration Score   (20%) — Does this company improve the future?
  2. Legacy Score         (20%) — Will this company still matter in 10 years?
  3. Stewardship Score    (15%) — Would I trust management with family wealth?
  4. First Principles     (15%) — Is the thesis supported by root causes?
  5. Community Impact     (10%) — Does this company strengthen society?
  6. Family Wealth Test   (10%) — Would 50% of family wealth go here for 10 years?
  7. Banyan Tree Index    (10%) — Deep roots, long life, generational value?

Composite: Louis Regeneration Index (0-100)
Action Signal: Observe / Learn / Accumulate / Build / Lead / Harvest / Protect
"""

import math
from datetime import date


# ── SECTOR REGENERATION MAP ──
# How much does this sector structurally improve the human condition?
_REGEN_SECTOR = {
    "Healthcare": 90, "Biotechnology": 90, "Drug Manufacturers": 85,
    "Medical Devices": 85, "Diagnostics & Research": 85,
    "Utilities": 80, "Utilities—Regulated Electric": 85,
    "Utilities—Regulated Water": 90,
    "Renewable Energy": 90, "Solar": 85, "Nuclear": 85,
    "Semiconductors": 75, "Semiconductor Equipment & Materials": 75,
    "Software—Infrastructure": 70, "Software—Application": 65,
    "Communication Equipment": 65, "Information Technology Services": 65,
    "Aerospace & Defense": 60,
    "Industrial": 70, "Farm & Heavy Construction Machinery": 80,
    "Electrical Equipment & Parts": 80,
    "Building Products & Equipment": 75,
    "Specialty Chemicals": 60, "Agricultural Inputs": 75,
    "Food Distribution": 80, "Packaged Foods": 65,
    "Banks": 55, "Capital Markets": 50, "Insurance": 55,
    "Financial Data & Stock Exchanges": 60, "Asset Management": 50,
    "Consumer Electronics": 55, "Internet Retail": 50,
    "Entertainment": 40, "Gambling": 20, "Tobacco": 15,
    "Oil & Gas": 45, "Oil & Gas E&P": 45,
}

# Industry keywords that signal regeneration
_REGEN_KEYWORDS = [
    "clean energy", "renewable", "solar", "wind", "nuclear", "water",
    "healthcare", "medical", "biotech", "diagnostics", "gene therapy",
    "education", "infrastructure", "grid", "power management",
    "agriculture", "food security", "precision farming",
    "recycling", "waste management", "sustainability",
    "semiconductor", "compute", "connectivity",
]

# Industry keywords that signal extraction
_EXTRACT_KEYWORDS = [
    "tobacco", "gambling", "casino", "alcohol", "weapons",
    "payday lending", "predatory", "fossil",
]

# Legacy durability indicators by sector
_LEGACY_SECTOR = {
    "Semiconductors": 85, "Software—Infrastructure": 80,
    "Healthcare": 85, "Utilities": 90,
    "Aerospace & Defense": 80, "Capital Markets": 70,
    "Banks": 75, "Consumer Electronics": 60,
    "Entertainment": 45, "Gambling": 30,
}


def _safe(info, *keys, default=0):
    for k in keys:
        v = info.get(k)
        if v is not None and v != "":
            try:
                return float(v) if not isinstance(v, str) else v
            except (ValueError, TypeError):
                return v
    return default


def _keyword_hits(text, keywords):
    if not text:
        return 0
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def score_regeneration(info, hist):
    """Module 1: Does this company improve the future?
    Evaluates: Human Health, Productivity, Education, Energy Security,
    Water Security, Infrastructure, Innovation, Community Value."""
    sector = str(_safe(info, "sector", "industry", default=""))
    industry = str(_safe(info, "industry", default=""))
    summary = str(_safe(info, "longBusinessSummary", default=""))

    base = _REGEN_SECTOR.get(sector, 50)
    base = _REGEN_SECTOR.get(industry, base)

    regen_hits = _keyword_hits(summary, _REGEN_KEYWORDS)
    extract_hits = _keyword_hits(summary, _EXTRACT_KEYWORDS)

    score = base + min(regen_hits * 3, 15) - min(extract_hits * 10, 30)

    rev_growth = _safe(info, "revenueGrowth", default=0)
    if rev_growth and rev_growth > 0.15:
        score += 5

    return max(0, min(100, round(score)))


def score_legacy(info, hist):
    """Module 2: Will this company still matter in 10 years?
    Evaluates: Long-Term Relevance, Durability, Competitive Moat,
    Adaptability, Leadership Quality."""
    sector = str(_safe(info, "sector", "industry", default=""))
    industry = str(_safe(info, "industry", default=""))
    mc = _safe(info, "marketCap", default=0)

    base = _LEGACY_SECTOR.get(sector, 55)
    base = _LEGACY_SECTOR.get(industry, base)

    # Large companies tend to persist
    if mc > 100e9:
        base += 15
    elif mc > 20e9:
        base += 8
    elif mc < 2e9:
        base -= 10

    # Profitability = durability
    gm = _safe(info, "grossMargins", default=0)
    if gm and gm > 0.60:
        base += 10
    elif gm and gm > 0.40:
        base += 5

    om = _safe(info, "operatingMargins", default=0)
    if om and om > 0.20:
        base += 5

    # Institutional ownership = staying power
    inst = _safe(info, "institutionHoldings", "heldPercentInstitutions", default=0)
    if inst and inst > 0.70:
        base += 5

    return max(0, min(100, round(base)))


def score_stewardship(info, hist):
    """Module 3: Would I trust management with my family's wealth?
    Evaluates: Capital Allocation, Governance, Balance Sheet Discipline,
    Shareholder Alignment, Ethical Conduct."""
    score = 50

    # Balance sheet discipline
    total_cash = _safe(info, "totalCash", default=0)
    total_debt = _safe(info, "totalDebt", default=0)
    if total_debt > 0 and total_cash > 0:
        if total_cash > total_debt:
            score += 15
        elif total_cash > total_debt * 0.5:
            score += 8
        elif total_debt > total_cash * 5:
            score -= 10

    dte = _safe(info, "debtToEquity", default=0)
    if dte and dte < 50:
        score += 8
    elif dte and dte > 200:
        score -= 10

    # FCF generation = capital discipline
    fcf = _safe(info, "freeCashflow", default=0)
    if fcf and fcf > 0:
        score += 10
    elif fcf and fcf < -1e9:
        score -= 10

    # Dividend = shareholder alignment
    div_yield = _safe(info, "dividendYield", default=0)
    if div_yield and div_yield > 0.01:
        score += 5

    # ROE = capital allocation skill
    roe = _safe(info, "returnOnEquity", default=0)
    if roe and roe > 0.20:
        score += 10
    elif roe and roe > 0.10:
        score += 5
    elif roe and roe < 0:
        score -= 10

    return max(0, min(100, round(score)))


def score_first_principles(info, hist):
    """Module 4: Is the thesis supported by root causes rather than market noise?
    Evaluates: Economic Drivers, Technology Drivers, Demographic Drivers,
    Resource Drivers, Incentive Structures."""
    score = 50
    summary = str(_safe(info, "longBusinessSummary", default=""))

    # Structural demand keywords (root causes, not hype)
    structural = [
        "infrastructure", "essential", "critical", "regulated",
        "government contract", "monopoly", "sole source", "patent",
        "demographic", "aging", "population", "mandate",
        "national security", "defense", "utility", "water",
        "grid", "baseload", "supply chain",
    ]
    hype = [
        "disruptive", "revolutionary", "game-changing", "moonshot",
        "metaverse", "web3", "nft", "meme",
    ]

    struct_hits = _keyword_hits(summary, structural)
    hype_hits = _keyword_hits(summary, hype)

    score += min(struct_hits * 4, 20)
    score -= min(hype_hits * 8, 20)

    # Revenue stability = root cause demand
    rev_growth = _safe(info, "revenueGrowth", default=0)
    if rev_growth and 0.05 < rev_growth < 0.40:
        score += 10
    elif rev_growth and rev_growth > 0.80:
        score -= 5

    # Institutional ownership = sophisticated demand validation
    inst = _safe(info, "institutionHoldings", "heldPercentInstitutions", default=0)
    if inst and inst > 0.80:
        score += 8
    elif inst and inst > 0.60:
        score += 4

    return max(0, min(100, round(score)))


def score_community_impact(info, hist):
    """Module 5: Does this company strengthen society?
    Evaluates: Job Creation, Productivity Enhancement, Social Utility,
    Economic Contribution."""
    sector = str(_safe(info, "sector", "industry", default=""))
    industry = str(_safe(info, "industry", default=""))
    summary = str(_safe(info, "longBusinessSummary", default=""))
    employees = _safe(info, "fullTimeEmployees", default=0)

    # Base from sector contribution to society
    community_map = {
        "Healthcare": 85, "Utilities": 85,
        "Industrials": 75, "Technology": 60,
        "Basic Materials": 65, "Consumer Defensive": 70,
        "Financial Services": 55, "Communication Services": 50,
        "Consumer Cyclical": 50, "Energy": 55,
        "Real Estate": 50,
    }
    base = community_map.get(sector, 50)

    # Employment scale
    if employees and employees > 100000:
        base += 12
    elif employees and employees > 20000:
        base += 8
    elif employees and employees > 5000:
        base += 4

    # Community keywords
    community_kw = [
        "community", "education", "health", "safety", "clean",
        "sustainable", "employment", "training", "infrastructure",
        "rural", "underserved", "access",
    ]
    base += min(_keyword_hits(summary, community_kw) * 3, 12)

    return max(0, min(100, round(base)))


def score_family_wealth_test(info, hist):
    """Module 6: If 50% of family wealth had to be invested for 10 years,
    would this qualify? Pass / Borderline / Fail."""
    score = 0

    mc = _safe(info, "marketCap", default=0)
    if mc > 50e9:
        score += 20
    elif mc > 10e9:
        score += 12
    elif mc < 2e9:
        score -= 5

    # Profitability
    om = _safe(info, "operatingMargins", default=0)
    if om and om > 0.20:
        score += 15
    elif om and om > 0.10:
        score += 8
    elif om and om < 0:
        score -= 10

    # Balance sheet
    total_cash = _safe(info, "totalCash", default=0)
    total_debt = _safe(info, "totalDebt", default=0)
    if total_debt == 0 or (total_cash > total_debt * 0.5):
        score += 15
    elif total_debt > total_cash * 5:
        score -= 10

    # FCF
    fcf = _safe(info, "freeCashflow", default=0)
    if fcf and fcf > 1e9:
        score += 15
    elif fcf and fcf > 0:
        score += 8
    elif fcf and fcf < 0:
        score -= 10

    # Dividend history = commitment
    div_yield = _safe(info, "dividendYield", default=0)
    if div_yield and div_yield > 0.015:
        score += 8

    # Institutional ownership
    inst = _safe(info, "institutionHoldings", "heldPercentInstitutions", default=0)
    if inst and inst > 0.70:
        score += 8

    # Price stability (low beta = family-grade)
    beta = _safe(info, "beta", default=1)
    if beta and beta < 0.8:
        score += 10
    elif beta and beta > 1.5:
        score -= 8

    final = max(0, min(100, round(50 + score)))

    if final >= 70:
        label = "✅ PASS"
    elif final >= 50:
        label = "⚠️ BORDERLINE"
    else:
        label = "❌ FAIL"

    return final, label


def score_banyan_tree(info, hist):
    """Module 7: The Banyan Tree Index™
    Deep Roots, Long Life, Protection, Growth, Generational Value.
    Does this company grow stronger over time, support surrounding
    ecosystems, benefit future generations, compound value sustainably?"""
    score = 50

    # Deep roots: long operating history via market cap stability
    mc = _safe(info, "marketCap", default=0)
    if mc > 100e9:
        score += 12
    elif mc > 20e9:
        score += 6

    # Growth: revenue + earnings momentum
    rev_growth = _safe(info, "revenueGrowth", default=0)
    eg = _safe(info, "earningsGrowth", default=0)
    if rev_growth and rev_growth > 0.10:
        score += 8
    if eg and eg > 0.10:
        score += 5

    # Protection: moat indicators
    gm = _safe(info, "grossMargins", default=0)
    if gm and gm > 0.60:
        score += 10
    elif gm and gm > 0.40:
        score += 5

    # Compounding: ROE + FCF
    roe = _safe(info, "returnOnEquity", default=0)
    if roe and roe > 0.20:
        score += 8
    elif roe and roe > 0.10:
        score += 4

    fcf = _safe(info, "freeCashflow", default=0)
    if fcf and fcf > 0:
        score += 5

    # Ecosystem support: employee count + dividend
    employees = _safe(info, "fullTimeEmployees", default=0)
    if employees and employees > 50000:
        score += 5

    div_yield = _safe(info, "dividendYield", default=0)
    if div_yield and div_yield > 0.01:
        score += 5

    return max(0, min(100, round(score)))


def compute_regeneration_index(info, hist):
    """Compute the full Louis Regeneration Index™.

    Returns dict with all 7 sub-scores, composite index, and action signal.
    This function is COMPLETELY INDEPENDENT of all CFIS core engines.
    It does NOT read or modify any existing score.
    """
    regen = score_regeneration(info, hist)
    legacy = score_legacy(info, hist)
    stewardship = score_stewardship(info, hist)
    first_principles = score_first_principles(info, hist)
    community = score_community_impact(info, hist)
    family_wealth, family_label = score_family_wealth_test(info, hist)
    banyan = score_banyan_tree(info, hist)

    # Composite: weighted average
    composite = round(
        regen * 0.20 +
        legacy * 0.20 +
        stewardship * 0.15 +
        first_principles * 0.15 +
        community * 0.10 +
        family_wealth * 0.10 +
        banyan * 0.10
    )
    composite = max(0, min(100, composite))

    # Regeneration Action Signal
    if composite >= 85:
        action = "🌳 LEAD"
        action_desc = "Exceptional long-term conviction"
        action_color = "#00C853"
    elif composite >= 75:
        action = "🏗️ BUILD"
        action_desc = "Strong long-term conviction"
        action_color = "#4CAF50"
    elif composite >= 65:
        action = "📈 ACCUMULATE"
        action_desc = "Gradual positioning"
        action_color = "#8BC34A"
    elif composite >= 55:
        action = "📖 LEARN"
        action_desc = "Study further"
        action_color = "#FFC107"
    elif composite >= 45:
        action = "👁️ OBSERVE"
        action_desc = "Insufficient clarity"
        action_color = "#FF9800"
    elif composite >= 35:
        action = "🌾 HARVEST"
        action_desc = "Take gains responsibly"
        action_color = "#FF5722"
    else:
        action = "🛡️ PROTECT"
        action_desc = "Preserve capital"
        action_color = "#f44336"

    return {
        "regeneration": regen,
        "legacy": legacy,
        "stewardship": stewardship,
        "first_principles": first_principles,
        "community_impact": community,
        "family_wealth": family_wealth,
        "family_wealth_label": family_label,
        "banyan_tree": banyan,
        "composite": composite,
        "action": action,
        "action_desc": action_desc,
        "action_color": action_color,
        "updated_at": date.today().isoformat(),
    }
