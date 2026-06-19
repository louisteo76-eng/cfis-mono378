# 09 Institutional Macro & Strategic Flow

## What This Layer Does

Scores every stock across 5 structural dimensions that approximate how
institutional capital allocators (sovereign wealth funds, pension funds,
macro hedge funds) evaluate strategic positioning before retail investors
notice the flow.

The goal is to detect **why** capital may move — not just that it moved.

## The 5 Dimensions

| # | Dimension | Weight | What It Detects |
|---|-----------|--------|-----------------|
| 1 | Government Strategic Alignment | 25% | CHIPS Act, IRA, defense spend, critical minerals, AI infra, sanctions, reshoring |
| 2 | Geopolitical Trend Exposure | 20% | US-China tension, Taiwan risk, NATO rearmament, energy security, currency regimes |
| 3 | Sovereign / Institutional Capital Direction | 20% | Sovereign wealth themes, pension allocation, infrastructure, mega-cap gravity |
| 4 | Elite Knowledge / Future Tech Signals | 20% | Academic research trends, Davos/WEF/Basel themes, expo signals, tech regime shifts |
| 5 | Financial System / Central Bank Signals | 15% | Rate regime, Basel rules, credit spreads, liquidity, yen carry, bank regulation |

## Output Structure

```python
{
    "score": 0-100,           # Composite strategic flow score
    "label": "Strategic Tailwind" | "Neutral" | "Strategic Headwind",
    "themes": [...],          # Matched strategic themes (e.g. "AI Compute", "Defense")
    "reasons": [...],         # Human-readable reasons for the score
    "confidence": 0-100,      # How reliable the signal is
    "source_type": "proxy",   # Always "proxy" until live data is added
    "updated_at": "2026-06-18",
    "dimensions": {...},      # Per-dimension breakdown
    "dominant_force": "...",  # Strongest dimension
    "capital_flow": "Strong Inflow" | "Building" | "Neutral" | "No Signal",
}
```

## Data Sources: Direct vs Proxy

| Source | Type | What It Provides |
|--------|------|-----------------|
| yfinance `.info` (sector, industry, summary) | **Proxy** | Company description keyword scanning |
| yfinance `.info` (marketCap, beta, debtToEquity, institutionalHoldings) | **Direct** | Quantitative fundamentals |
| Enriched news headlines | **Proxy** | Keyword scanning of recent news |
| Known ticker overrides | **Proxy** | Curated expert assessment of strategic positioning |

**Current state: all scoring is proxy-based.** No live institutional flow
data, no real-time policy tracking, no actual sovereign fund holdings data.

## Strategic Theme Map

16 themes are tracked via keyword matching:

AI Compute, Semiconductors, Nuclear Energy, Grid Power, Defense,
Cybersecurity, Space, Critical Minerals, Water Security, Food Security,
Biotech / Longevity, Tokenized Finance, Private Credit, Robotics,
Energy Security, Shipping / Logistics

## Known Ticker Overrides

~27 strategically significant tickers have floor scores to prevent
keyword-scanning limitations from under-scoring known strategic assets
(e.g. LMT, TSM, NVDA, PLTR, CCJ, MP, FSLR).

Overrides set a **floor** — if the heuristic score is higher, the
heuristic wins. They never cap scores.

## Known Limitations

1. **This is NOT Bridgewater / Aladdin.** Those systems use proprietary
   datasets, real-time macro models, 40+ years of calibrated indicators,
   and hundreds of researchers. This layer uses publicly available data
   and keyword heuristics as a proxy.

2. **No live policy tracking.** The system cannot detect a new executive
   order or tariff announcement in real-time. It relies on company
   descriptions and cached news headlines.

3. **No real institutional flow data.** We infer institutional interest
   from market cap, ownership percentages, and sector alignment — not
   from actual 13F filings, sovereign fund disclosures, or dark pool data.

4. **Keyword matching is imprecise.** A company mentioning "china" in its
   supply chain risk section scores the same as one with actual China
   revenue. Context is lost.

5. **No temporal decay.** A keyword hit from a 5-year-old company
   description is weighted the same as yesterday's news headline.

6. **Known ticker overrides are manually maintained.** They can become
   stale if geopolitical conditions change.

7. **Confidence scores are heuristic.** They indicate data density, not
   statistical confidence.

## How to Improve Later

| Improvement | Impact | Difficulty |
|-------------|--------|------------|
| Add FMP/Finnhub news sentiment scoring | Upgrade proxy → semi-direct | Medium |
| Add 13F institutional holdings analysis | Real ownership data | Medium |
| Add FRED macro indicators (rates, spreads, dollar index) | Direct macro data | Low |
| Add congressional trade disclosures | Elite signal, direct | Medium |
| Add real-time policy/sanctions API | Direct policy tracking | High |
| Add NLP entity extraction instead of keyword matching | Better precision | High |
| Add temporal weighting (recent > old) | Reduce stale signals | Medium |

## Integration Points

- **`_build_row()`** in `app.py` calls `compute_strategic_flow()` for every
  scanned ticker and adds 6 fields to the opportunity row.
- **`signal_scanner.py`** persists and restores the strategic fields via
  Supabase `signal_table`.
- **Migration `003_strategic_flow_columns.sql`** adds the columns.
- **No existing score formulas are changed.** The strategic score is
  additive — it does not modify Hunter, CFIS, Conviction, or any other
  existing score.

## Module Location

`services/strategic_flow.py` — no Streamlit dependency, importable standalone.

## Do Not Break

- Existing CFIS/Hunter/Conviction scoring logic.
- Existing UI layout.
- Existing signal_table schema (migration is additive only).
- Existing hardcoded universes.
