-- Migration 001: Create ticker_master table
-- Run this in the Supabase SQL editor to set up the universe table.

CREATE TABLE IF NOT EXISTS ticker_master (
    symbol       TEXT PRIMARY KEY,
    name         TEXT NOT NULL DEFAULT '',
    sector       TEXT,
    industry     TEXT,
    market_cap   BIGINT,
    exchange     TEXT NOT NULL,
    is_etf       BOOLEAN NOT NULL DEFAULT FALSE,
    is_active    BOOLEAN NOT NULL DEFAULT TRUE,
    source       TEXT NOT NULL DEFAULT 'fmp',
    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ticker_master_exchange
    ON ticker_master (exchange);

CREATE INDEX IF NOT EXISTS idx_ticker_master_market_cap
    ON ticker_master (market_cap DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_ticker_master_active
    ON ticker_master (is_active) WHERE is_active = TRUE;

COMMENT ON TABLE ticker_master IS
    'Master universe of US-listed stocks, refreshed from FMP. '
    'Used by the scanner pipeline to avoid hitting FMP on every page load.';
