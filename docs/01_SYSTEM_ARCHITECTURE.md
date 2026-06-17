# 01 System Architecture

## Current Architecture

```text
app.py
  -> Streamlit UI
  -> scoring functions
  -> hardcoded universes
  -> yfinance
  -> services/data_providers.py
  -> services/ticker_universe.py
  -> services/signal_scanner.py
  -> services/supabase_client.py
```

There is a partial service layer. Most UI and scoring logic still lives in
`app.py`.

## Current Page Navigation

`app.py` uses a custom `st.radio` sidebar with these pages:

1. Market Health
2. Capital Migration
3. Opportunity Engine
4. Portfolio Commander
5. Validation Engine
6. Hunter Command by Louis Teo
7. Options Intelligence by Louis Teo
8. CFIS Frontier by Louis Teo

## Current Service Modules

- `services/data_providers.py`: FMP, Finnhub, SEC EDGAR, Finviz wrappers with
  retry/error logging.
- `services/ticker_universe.py`: reads Supabase `ticker_master` first, falls
  back to FMP exchange screener, and builds capped scanner universes.
- `services/signal_scanner.py`: saves `scan_opportunities()` rows into
  `signal_table` and loads latest signals back into app-compatible rows.
- `services/supabase_client.py`: optional Supabase client factory.

## Database Migrations

- `database/migrations/001_ticker_master.sql`: master universe table.
- `database/migrations/002_signal_table.sql`: daily pre-computed CFIS scores.

Not yet activated — requires Supabase project + keys in secrets.

## Target Architecture

```text
app.py
pages/
components/
services/
database/
utils/
```

Target backend flow:

```text
FMP universe
  -> ticker_master in Supabase
  -> daily signal engine
  -> signal_table
  -> Streamlit dashboard reads cached/stored signals
```

## Rule

Move toward the target architecture gradually. Do not rebuild from scratch and
do not redesign the UI while extracting modules.
