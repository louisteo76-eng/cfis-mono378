# CFIS-X Project Instructions

## Mission

Build a market-wide Capital Flow Intelligence System covering all US stocks.

This repository is currently a Streamlit/Python CFIS app. Treat the current
working tree as source of truth. Most UI and scoring logic is still in `app.py`,
but selected backend services have already been extracted.

## Current Stack

- Streamlit
- Python
- yfinance
- pandas
- Plotly
- requests
- FMP API
- Finnhub API
- Supabase optional storage through `services/supabase_client.py`

## Before Making Changes

1. Read `/docs` first.
2. Preserve existing UI.
3. Never rebuild from scratch.
4. Make small safe changes.
5. Explain changes before coding.

## Current / Target Folder Structure

- `app.py`
- `services/`
- `database/`
- `docs/`

Target folders still to introduce gradually if needed:

- `pages/`
- `components/`
- `utils/`

## Core Modules

- Dashboard
- Signal Engine
- Smart Money Pressure Map
- Frontier Forecast
- Louis Pick

## Ticker Universe

Target market coverage:

- NYSE
- NASDAQ
- AMEX
- ETF

Current implementation includes hardcoded universes plus `services/ticker_universe.py`,
which reads Supabase `ticker_master` first and falls back to FMP.

## Run Commands

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run Streamlit locally:

```bash
python3 -m streamlit run app.py
```

Run on local network:

```bash
python3 -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## Environment Variables

API keys must be stored only in `.env` or local Streamlit secrets. Do not expose
real keys in code, docs, commits, or chat.

Current code reads:

- `FMP_API_KEY`
- `FINNHUB_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

Current `app.py` also hardcodes `ACCESS_PASSWORD = "mono378"`; this is a known
weakness to fix safely later.

## Do Not Break

- Existing scoring logic.
- Dashboard layout.
- Database schema without migration.
- User custom settings.
- Existing hardcoded universes until replacements are proven.
- Current UI unless explicitly requested.

## Coding Rules

- Modular design.
- Async API calls for new market-wide jobs.
- Cache responses.
- Handle errors.
- Avoid duplicate code.
- Do not run 9000-symbol scans during Streamlit page refresh.

## Documentation Index

After major changes, update `/docs/*.md`.

- `docs/00_PROJECT_OVERVIEW.md`
- `docs/01_SYSTEM_ARCHITECTURE.md`
- `docs/02_DATABASE_SCHEMA.md`
- `docs/03_API_KEYS_AND_DATA_SOURCES.md`
- `docs/04_CFIS_SCORING_LOGIC.md`
- `docs/05_TICKER_UNIVERSE.md`
- `docs/06_STREAMLIT_APP_STRUCTURE.md`
- `docs/07_ROADMAP.md`
- `docs/08_DO_NOT_BREAK_RULES.md`
