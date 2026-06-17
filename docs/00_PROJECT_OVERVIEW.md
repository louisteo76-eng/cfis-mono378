# 00 Project Overview

## Mission

CFIS-X is intended to become a market-wide Capital Flow Intelligence System
covering US stocks across NYSE, NASDAQ, AMEX, and ETFs.

## Current Reality

The app is a monolithic Streamlit file with a growing service layer:

- Main file: `app.py` (~10,000 lines)
- Dependency file: `requirements.txt`
- Root instructions: `CLAUDE.md`
- Service modules: `services/` (data_providers, ticker_universe, signal_scanner, supabase_client)
- Database: `database/migrations/` (001_ticker_master.sql, 002_signal_table.sql)
- Documentation: `docs/`

## Current Features In `app.py`

- Login gate with hardcoded `ACCESS_PASSWORD`.
- World index ticker tape.
- 18-category CFIS-X scoring model.
- Stock analyzer / Market Health.
- Capital Migration.
- Opportunity Engine.
- Portfolio Commander.
- Validation Engine.
- Hunter Command by Louis Teo.
- Options Intelligence.
- CFIS Frontier.
- Reddit/social topic scanning.
- FMP/Finnhub/SEC/Finviz enrichment helpers.

## Current Stack

- Python
- Streamlit
- yfinance
- pandas
- Plotly
- requests

Planned/in-progress stack additions:

- Supabase (client ready, migrations written, not yet activated)
- async API layer
- background scanner jobs

## Known Weaknesses

- `app.py` is very large and mixes UI, scoring, data access, and business logic.
- Access password is hardcoded.
- Supabase is not yet activated (needs project + keys in secrets).
- Some scans still rely on fixed hardcoded universes as fallback.

## Recent Improvements

- API keys centralized via `_get_api_key()` — reads Streamlit secrets first,
  falls back to `.env` via python-dotenv.
- Data providers extracted to `services/data_providers.py` with retry and logging.
- Ticker universe extracted to `services/ticker_universe.py` — FMP with Supabase
  cache layer.
- Signal scanner in `services/signal_scanner.py` — auto-saves scan results to
  Supabase, pages use `scan_or_load()` to read stored signals when available.
- Market Health search expanded with FMP/Supabase universe options.
