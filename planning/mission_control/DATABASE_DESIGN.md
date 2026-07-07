# Database Design

## Event Sourcing
- No relational DB for live state. State is derived from Event Sourcing logs in `.aetheris/state/` and SQLite (`webhook_validator.db` for specifics).
- Append-only journals for execution history.