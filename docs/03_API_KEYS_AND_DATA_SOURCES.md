# 03 API Keys And Data Sources

## Current Key Handling

All API keys are read through `_get_api_key()` in `app.py` and
`_get_key()` in `services/supabase_client.py`:

1. Try `st.secrets` (Streamlit Cloud / `.streamlit/secrets.toml`)
2. Fall back to `os.environ` (loaded from `.env` via python-dotenv)

Keys used:

- `FMP_API_KEY` — required for market universe and enrichment
- `FINNHUB_API_KEY` — required for recommendations, insider, news, earnings
- `SUPABASE_URL` — optional, enables cached universe and stored signals
- `SUPABASE_KEY` — optional, paired with SUPABASE_URL

Missing keys trigger a one-time sidebar warning on app load.
Data providers in `services/data_providers.py` log warnings on failure.

## Current Data Sources

### yfinance

Used for:

- ticker info
- price history
- options chains
- world index ticker tape

### FMP

Used for:

- profile
- key metrics
- US exchange screener in `services/ticker_universe.py`
- Market Health search universe expansion

All FMP/Finnhub/EDGAR/Finviz calls go through `services/data_providers.py`
which adds retry (1 retry on network error), timeout handling, and logging.

### Finnhub

Used for:

- recommendations
- insider transactions
- news
- earnings calendar

### Supabase

Used for:

- `ticker_master`
- `signal_table`

Config:

- `SUPABASE_URL`
- `SUPABASE_KEY`

### SEC EDGAR

Used for:

- company facts
- CIK lookup

### Finviz

Used by scraping quote pages.

### Reddit RSS

Used for ticker and macro/social topic scans.

## Do Not Expose

- Real FMP keys.
- Real Finnhub keys.
- Supabase service keys.
- `.env`.
- `.streamlit/secrets.toml`.
