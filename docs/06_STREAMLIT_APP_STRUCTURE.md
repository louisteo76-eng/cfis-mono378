# 06 Streamlit App Structure

## Current Structure

The current app is still mostly one large file:

- `app.py`

Active service modules exist under `services/`, but page rendering and scoring
remain in `app.py`.

## Startup Flow

`app.py` currently:

1. Imports Streamlit, yfinance, pandas, Plotly, requests, XML, regex, JSON.
2. Loads `.env` through `python-dotenv`.
3. Imports `services.ticker_universe`, `services.data_providers`, and
   `services.signal_scanner`.
4. Clears Streamlit cache once per session.
5. Sets page config.
6. Shows login gate.
7. Renders world ticker tape.
8. Defines styles, scoring functions, universes, and page bodies.
9. Uses sidebar `st.radio` navigation.

## Navigation Pages

- Market Health
- Capital Migration
- Opportunity Engine
- Portfolio Commander
- Validation Engine
- Hunter Command by Louis Teo
- Options Intelligence by Louis Teo
- CFIS Frontier by Louis Teo

## Modularization Progress

Done:

1. API key handling — `_get_api_key()` with `.env` fallback
2. Data providers — `services/data_providers.py`
3. Ticker universe — `services/ticker_universe.py`
4. Supabase client — `services/supabase_client.py`
5. Signal scanner — `services/signal_scanner.py`
6. Database migrations — `database/migrations/`

Remaining:

1. components/login and market tape
2. scoring helpers extraction
3. page modules

Do not switch to native Streamlit pages unless requested.
