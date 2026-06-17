"""
Supabase client factory.

Returns None when credentials are not configured, so callers can
fall back to direct API sources (FMP, yfinance) without crashing.
"""

import logging
import os

log = logging.getLogger("cfis.supabase")

_client = None
_init_attempted = False


def _get_key(name):
    """Read a config value: Streamlit secrets first, then os.environ."""
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            val = st.secrets.get(name, "")
            if val:
                return val
    except Exception:
        pass
    return os.environ.get(name, "")


def get_supabase_client():
    """Return a cached Supabase client, or None if not configured."""
    global _client, _init_attempted
    if _init_attempted:
        return _client
    _init_attempted = True

    url = _get_key("SUPABASE_URL")
    key = _get_key("SUPABASE_KEY")
    if not url or not key:
        log.info("Supabase not configured (SUPABASE_URL / SUPABASE_KEY missing) — using FMP fallback")
        return None

    try:
        from supabase import create_client
        _client = create_client(url, key)
        log.info("Supabase client initialized")
    except ImportError:
        log.warning("supabase package not installed — pip install supabase")
    except Exception as e:
        log.warning("Supabase client init failed: %s", e)

    return _client
