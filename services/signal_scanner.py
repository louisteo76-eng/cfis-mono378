"""
Signal scanner — store and retrieve pre-computed CFIS scores.

The scoring logic itself stays in app.py for now. This module handles:
  - Writing scan results to Supabase signal_table
  - Reading the latest signals so pages skip live scanning
  - Checking whether today's scan is already done

Usage from app.py:
  from services.signal_scanner import save_scan_results, load_latest_signals

  # After scan_opportunities() completes:
  save_scan_results(rows)

  # On page load (instead of scanning):
  signals = load_latest_signals(limit=300)
"""

import logging
from datetime import date, datetime, timezone

from services.supabase_client import get_supabase_client

log = logging.getLogger("cfis.scanner")

SIGNAL_TABLE = "signal_table"


def _row_to_signal(row):
    """Convert a _build_row() dict to a signal_table record."""
    return {
        "symbol": row["ticker"],
        "scan_date": date.today().isoformat(),
        "price": row.get("price"),
        "cfis_score": row.get("cfis"),
        "hunter_score": row.get("conviction"),
        "conviction": row.get("conviction_score"),
        "crowding": row.get("crowding_score"),
        "cap_score": row.get("cap_score"),
        "force_score": row.get("force_score"),
        "timing_score": row.get("timing_score"),
        "cm_score": row.get("cm_score"),
        "bottleneck": row.get("bottleneck"),
        "theme": row.get("theme"),
        "mom_5d": row.get("mom_5"),
        "mom_15d": row.get("mom_15"),
        "proj_15d": row.get("proj_15d"),
        "proj_30d": row.get("proj_30d"),
        "proj_90d": row.get("proj_90d"),
        "proj_direction": row.get("proj_direction"),
        "proj_confidence": row.get("proj_confidence"),
        "action": row.get("action"),
        "signal_zone": row.get("signal"),
        "classification": row.get("classification"),
        "risk_score": row.get("risk"),
        "quality_score": row.get("quality"),
        "data_quality": row.get("data_quality", 0),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def save_scan_results(rows):
    """Write scan_opportunities() output to Supabase signal_table.

    Upserts on (symbol, scan_date) so re-running the same day updates
    rather than duplicates. Silently skips if Supabase is not configured.
    Returns number of rows saved.
    """
    client = get_supabase_client()
    if client is None or not rows:
        return 0

    signals = []
    for r in rows:
        try:
            signals.append(_row_to_signal(r))
        except Exception:
            continue

    if not signals:
        return 0

    chunk_size = 500
    total = 0
    try:
        for i in range(0, len(signals), chunk_size):
            chunk = signals[i:i + chunk_size]
            client.table(SIGNAL_TABLE).upsert(
                chunk, on_conflict="symbol,scan_date"
            ).execute()
            total += len(chunk)
        log.info("Saved %d signals for %s", total, date.today().isoformat())
    except Exception as e:
        log.warning("Signal save failed after %d rows: %s", total, e)
    return total


def load_latest_signals(scan_date=None, limit=300):
    """Read the most recent signals from Supabase.

    Returns list of dicts matching _build_row() key names so existing
    page code can consume them directly. Returns [] if Supabase is not
    configured or has no data for the requested date.
    """
    client = get_supabase_client()
    if client is None:
        return []

    if scan_date is None:
        scan_date = date.today().isoformat()

    try:
        result = (
            client.table(SIGNAL_TABLE)
            .select("*")
            .eq("scan_date", scan_date)
            .order("hunter_score", desc=True)
            .limit(limit)
            .execute()
        )
        data = getattr(result, "data", None) or []
        if not data:
            return []
        log.info("Loaded %d signals for %s", len(data), scan_date)
        return [_signal_to_row(s) for s in data]
    except Exception as e:
        log.warning("Signal read failed: %s", e)
        return []


def _signal_to_row(s):
    """Convert a signal_table record back to _build_row() format."""
    return {
        "ticker": s["symbol"],
        "name": s["symbol"],
        "price": s.get("price", 0),
        "theme": s.get("theme", ""),
        "theme_icon": "📊",
        "cfis": s.get("cfis_score", 0),
        "conviction": s.get("hunter_score", 0),
        "signal": s.get("signal_zone", ""),
        "signal_color": "#78909C",
        "classification": s.get("classification", ""),
        "bottleneck": s.get("bottleneck", 0),
        "cm_score": s.get("cm_score", 0),
        "narrative": 0,
        "mom_15": s.get("mom_15d", 0),
        "mom_5": s.get("mom_5d", 0),
        "expected_ret": s.get("proj_30d", 0),
        "proj_15d": s.get("proj_15d", 0),
        "proj_30d": s.get("proj_30d", 0),
        "proj_90d": s.get("proj_90d", 0),
        "proj_direction": s.get("proj_direction", ""),
        "proj_confidence": s.get("proj_confidence", 0),
        "is_bottleneck": False,
        "one_sentence": "",
        "risk": s.get("risk_score", 50),
        "quality": s.get("quality_score", 50),
        "cap_score": s.get("cap_score", 0),
        "force_score": s.get("force_score", 0),
        "crowding_score": s.get("crowding", 100),
        "timing_score": s.get("timing_score", 0),
        "conviction_score": s.get("conviction", 0),
        "action": s.get("action", "PASS"),
        "action_color": "#78909C",
        "action_icon": "❌",
        "action_desc": "",
        "hunt_alert": False,
        "data_quality": s.get("data_quality", 0),
    }


def has_todays_scan():
    """Check whether signal_table has data for today."""
    client = get_supabase_client()
    if client is None:
        return False
    try:
        result = (
            client.table(SIGNAL_TABLE)
            .select("id", count="exact")
            .eq("scan_date", date.today().isoformat())
            .limit(1)
            .execute()
        )
        count = getattr(result, "count", 0) or 0
        return count > 0
    except Exception:
        return False
