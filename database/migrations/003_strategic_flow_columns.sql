-- Migration 003: Add strategic flow columns to signal_table
-- Run this in the Supabase SQL editor after 002_signal_table.sql.

ALTER TABLE signal_table ADD COLUMN IF NOT EXISTS strategic_score NUMERIC;
ALTER TABLE signal_table ADD COLUMN IF NOT EXISTS strategic_label TEXT;
ALTER TABLE signal_table ADD COLUMN IF NOT EXISTS strategic_dominant TEXT;
ALTER TABLE signal_table ADD COLUMN IF NOT EXISTS strategic_capital_flow TEXT;
ALTER TABLE signal_table ADD COLUMN IF NOT EXISTS strategic_confidence NUMERIC;
ALTER TABLE signal_table ADD COLUMN IF NOT EXISTS strategic_themes TEXT;

CREATE INDEX IF NOT EXISTS idx_signal_strategic_score
    ON signal_table (scan_date, strategic_score DESC NULLS LAST);

COMMENT ON COLUMN signal_table.strategic_score IS
    'Institutional Macro & Strategic Flow composite score (0-100). '
    'Weighted across 5 dimensions: government alignment, geopolitical '
    'exposure, institutional capital direction, elite knowledge, '
    'financial system. Proxy-based unless enriched with live data.';
