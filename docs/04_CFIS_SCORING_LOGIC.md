# 04 CFIS Scoring Logic

## Location

The CFIS scoring logic currently lives in `app.py`.

## 18 Categories

`app.py` defines `CATEGORIES`:

1. Future Civilization Exposure
2. Institutional Power
3. Sovereign Capital
4. Political Intelligence
5. ETF Gravity
6. Dark Pool Intelligence
7. Options Warfare
8. Insider Conviction
9. Leadership Intelligence
10. Economic Moat
11. Revenue Quality
12. Government Influence
13. War Chest
14. Fortress Balance Sheet
15. M&A Probability
16. Industry Dominance
17. Catalyst Calendar
18. Market Regime Intelligence

## Main Functions

- `compute_all_scores(info, hist, inst, maj)`
- `cfis_composite(scores)`
- `opportunity_score(cfis, info, hist)`
- `generate_outlooks(info, hist, score)`
- `cfis_projection(...)`
- `louis_intuition_engine(...)`
- `compute_hunter(...)`
- `compute_smart_money_pressure(...)`

## Do Not Break

- Category names.
- Weighting behavior.
- Existing score ranges.
- Existing page rendering that expects these keys.

## Planned

Extract pure scoring functions into a module only after adding small regression
tests or manual before/after checks.

