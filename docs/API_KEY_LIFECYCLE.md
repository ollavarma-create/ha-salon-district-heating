# API key lifecycle — planned

Portal expiry date is visible; no programmatic expiry endpoint or expiry-specific error code confirmed. Do not label all 401/403 as expiry. Preserve entity IDs and history during reauth; never log credentials. Consider optional user-entered expiry date, diagnostic date sensor and notices 30, 7 and 1 days before expiry. Reset expiry metadata on rotation. Translate EN/FI/SV. Test invalid credentials, successful reauth and transient errors separately. Not implemented.

Production validation: back up configuration, verify release, check entities and timestamps, validate dashboard assets and Energy Dashboard statistics, monitor overnight delayed batches and retain rollback path.
