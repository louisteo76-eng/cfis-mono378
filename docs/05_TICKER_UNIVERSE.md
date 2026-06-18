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

Current live page scans are capped and do not process all 9000+ symbols inside
Streamlit page refresh. When Supabase has precomputed `signal_table` rows,
`scan_or_load()` can read up to `CFIS_STORED_SIGNAL_LIMIT` rows, default 9000.

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
                            build_scanner_universe() → live fallback cap
                                        ↓
                            scan_opportunities() → signal_scanner.py → Supabase signal_table
                                        ↓
                            scan_or_load() → pages read stored full-market signals or scan capped live fallback
```

- `fetch_us_universe()`: Supabase first, FMP fallback
- `build_scanner_universe()`: curated FULL_UNIVERSE + FMP top market cap, capped by `CFIS_LIVE_SCAN_LIMIT` for live scans
- `scan_or_load()`: loads today's stored signals if available, else scans live
- Market Health search augmented with FMP/Supabase universe options
- `normalize_ticker_input()`: resolves company names and raw symbols

## Limits

- `CFIS_LIVE_SCAN_LIMIT`: default `300`; protects Streamlit from full-market live scans.
- `CFIS_STORED_SIGNAL_LIMIT`: default `9000`; max stored rows to read from Supabase.

## Do Not Break

Do not remove hardcoded universes until the Supabase universe and signal scanner
are implemented and tested.
