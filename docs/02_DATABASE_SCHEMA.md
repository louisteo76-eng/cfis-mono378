# 02 Database Schema

## Current State

Supabase is optional. The current checkout has:

- `services/supabase_client.py` — client factory, returns None when unconfigured
- `services/ticker_universe.py` — Supabase-first universe reads
- `services/signal_scanner.py` — signal storage and retrieval
- `database/__init__.py`
- `database/migrations/001_ticker_master.sql` — universe table schema
- `database/migrations/002_signal_table.sql` — daily scores table schema

To activate: create Supabase project, run both migrations in SQL editor,
add `SUPABASE_URL` and `SUPABASE_KEY` to `.streamlit/secrets.toml` or `.env`.

## Expected Tables

### `ticker_master`

Used by `services/ticker_universe.py`.

Expected columns:

- `symbol`
- `name`
- `sector`
- `industry`
- `market_cap`
- `exchange`
- `is_etf`
- `is_active`
- `source`
- `refreshed_at`
- `updated_at`

Purpose:

- Store NYSE, NASDAQ, AMEX, and ETF universe symbols from FMP.

### `signal_table`

Used by `services/signal_scanner.py`.

Expected fields from `_row_to_signal()` include:

- `symbol`
- `scan_date`
- `price`
- `cfis_score`
- `hunter_score`
- `conviction`
- `crowding`
- `cap_score`
- `force_score`
- `timing_score`
- `cm_score`
- `bottleneck`
- `theme`
- `mom_5d`
- `mom_15d`
- `proj_15d`
- `proj_30d`
- `proj_90d`
- `proj_direction`
- `proj_confidence`
- `action`
- `signal_zone`
- `classification`
- `risk_score`
- `quality_score`
- `data_quality`
- `created_at`

## Migration Rule

Do not change database schema without a migration file and documentation update.
