# 08 Do Not Break Rules

## Before Coding

1. Read `/docs`.
2. Explain planned changes before coding.
3. Preserve existing UI.
4. Never rebuild from scratch.
5. Make small safe changes.

## Hard Rules

- Do not break existing scoring logic.
- Do not break dashboard layout.
- Do not change database schema without migration.
- Do not break user custom settings.
- Do not expose API keys.
- Do not assume optional APIs are configured.
- Do not run 9000-symbol scans during Streamlit page refresh.
- Do not delete hardcoded lists before replacements are proven.
- Do not reverse existing extracted `services/` modules back into `app.py`.
- If docs and working tree disagree, inspect `git log --oneline -8` and update
  docs before coding.

## Coding Rules

- Modular design.
- Async API calls for new market-wide jobs.
- Cache responses.
- Handle errors clearly.
- Avoid duplicate code.
- Update docs after major changes.

## Financial Safety

This is an intelligence dashboard, not guaranteed investment advice. Avoid
language that promises profits or certainty.
