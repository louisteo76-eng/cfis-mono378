# 05 Ticker Universe

## Current Sources

Current ticker sources are split between `app.py` and `services/ticker_universe.py`.

Hardcoded universes include:

- `SP500_LIQUID`
- `FULL_UNIVERSE`
- `TOP_30_WHY`
- `TOP_30`
- `RADAR_UNIVERSE`
- `FRONTIER_UNIVERSE`
- `COMBO_UNIVERSE`
- `YEN_CARRY_VULNERABLE`

## FMP Full-Market Helper

Current code includes:

- `services/ticker_universe.fetch_us_universe(...)`
- `services/ticker_universe.build_scanner_universe(...)`
- `app.py` uses these service functions.

These functions call FMP stock screener for:

- NYSE
- NASDAQ
- AMEX

Current page scans are capped and do not process all 9000+ symbols inside
Streamlit page refresh.

## Target Universe

- NYSE
- NASDAQ
- AMEX
- ETFs

Target storage:

- Supabase `ticker_master` (migration ready: `database/migrations/001_ticker_master.sql`)

## Scanner Pipeline

```text
FMP (9000+ stocks) → ticker_universe.py → Supabase ticker_master (cache)
                                        ↓
                            build_scanner_universe() → 300 tickers max
                                        ↓
                            scan_opportunities() → signal_scanner.py → Supabase signal_table
                                        ↓
                            scan_or_load() → pages read stored signals or scan live
```

- `fetch_us_universe()`: Supabase first, FMP fallback
- `build_scanner_universe()`: curated FULL_UNIVERSE + FMP top market cap, capped at 300
- `scan_or_load()`: loads today's stored signals if available, else scans live
- Market Health search augmented with FMP/Supabase universe options
- `normalize_ticker_input()`: resolves company names and raw symbols

## Do Not Break

Do not remove hardcoded universes until the Supabase universe and signal scanner
are implemented and tested.
