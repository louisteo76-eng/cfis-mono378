# 07 Roadmap

## Done

- API keys centralized with `.env` fallback and missing-key warnings.
- Data providers extracted to `services/data_providers.py` with retry/logging.
- Ticker universe extracted to `services/ticker_universe.py` (FMP + Supabase).
- Supabase client factory in `services/supabase_client.py`.
- Signal scanner in `services/signal_scanner.py` — auto-save + load.
- Database migrations: `001_ticker_master.sql`, `002_signal_table.sql`.
- 4 pages switched to `scan_or_load()` (stored signals when available).
- Market Health search expanded with FMP/Supabase universe.
- `services/` and `database/` directories created.

## Immediate

- Preserve UI.
- Keep `services/` as the collaboration baseline; do not collapse back.
- Keep page scans capped at 300.
- Activate Supabase: create project, run migrations, add keys to secrets.
- Verify `scan_or_load()` works end-to-end with Supabase.

## Market-Wide Scanner

- Activate Supabase `ticker_master` with weekly FMP refresh.
- Load NYSE, NASDAQ, AMEX, and ETF symbols.
- Build async daily scanner when synchronous signal path is stable.
- Make all pages read stored signals by default.

## Modularization

- Create `components/` (login, market tape).
- Create `utils/`.
- Extract scoring helpers from `app.py`.
- Extract page modules.
- Move code in small PR-sized steps.

## Not Current Yet

- User accounts.
- Cloud multi-user auth.
- Broker trading.
- True institutional dark pool feed.
- True ETF flow feed.
- Fully database-backed dashboard.
