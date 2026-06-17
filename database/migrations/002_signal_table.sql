-- Migration 002: Create signal_table for daily pre-computed scores
-- Run this in the Supabase SQL editor after 001_ticker_master.sql.

CREATE TABLE IF NOT EXISTS signal_table (
    id           BIGSERIAL PRIMARY KEY,
    symbol       TEXT NOT NULL REFERENCES ticker_master(symbol),
    scan_date    DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Price data
    price        NUMERIC,
    market_cap   BIGINT,

    -- CFIS scores
    cfis_score   NUMERIC,
    hunter_score NUMERIC,
    conviction   NUMERIC,
    crowding     NUMERIC,
    cap_score    NUMERIC,
    force_score  NUMERIC,
    timing_score NUMERIC,

    -- Capital migration
    cm_score     NUMERIC,
    bottleneck   NUMERIC,
    theme        TEXT,

    -- Momentum
    mom_5d       NUMERIC,
    mom_15d      NUMERIC,

    -- CFIS projections
    proj_15d     NUMERIC,
    proj_30d     NUMERIC,
    proj_90d     NUMERIC,
    proj_direction TEXT,
    proj_confidence NUMERIC,

    -- Hunter action
    action       TEXT,
    signal_zone  TEXT,
    classification TEXT,

    -- Quality
    risk_score   NUMERIC,
    quality_score NUMERIC,
    data_quality NUMERIC,

    -- Metadata
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (symbol, scan_date)
);

CREATE INDEX IF NOT EXISTS idx_signal_scan_date
    ON signal_table (scan_date DESC);

CREATE INDEX IF NOT EXISTS idx_signal_symbol_date
    ON signal_table (symbol, scan_date DESC);

CREATE INDEX IF NOT EXISTS idx_signal_hunter_score
    ON signal_table (scan_date, hunter_score DESC NULLS LAST);

COMMENT ON TABLE signal_table IS
    'Daily pre-computed CFIS scores per ticker. Written by the background '
    'scanner, read by the Streamlit dashboard to avoid live scanning.';
