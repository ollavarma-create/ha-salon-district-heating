# Proposed Home Assistant integration architecture

**Status: design proposal — no implementation yet.**

## Scope

An unofficial Home Assistant custom integration for the LämpöVahti API, designed for one or more accessible district-heating locations.

## Proposed modules

- `custom_components/salon_district_heating/manifest.json` — integration metadata and dependencies
- `config_flow.py` — API-key entry and validation; secure Home Assistant config entry storage
- `api.py` — HTTP client, rate-limit/backoff handling, pagination, schema validation
- `coordinator.py` — shared polling and refresh orchestration
- `sensor.py` — entities per location and supported measurement
- `const.py` — constants and units
- `strings.json` / translations — user-facing labels
- `tests/` — API fixtures and integration tests with anonymized synthetic data

Names and structure may change during implementation.

## Entity design (candidate)

| Candidate entity | Source | Intended HA semantics | Caveat |
| --- | --- | --- | --- |
| Total energy | `reading_total` | Energy, kWh, cumulative meter | Only when non-null; confirm monotonic behavior/reset handling |
| Hourly energy | `consumption` | Energy, kWh per reported hour | Must not masquerade as lifetime total; validate statistics design |
| Supply temperature | `flow_temperature` | Temperature, °C | May be null |
| Return temperature | `return_temperature` | Temperature, °C | May be null |
| Flow rate | `flow` | Volume flow, m³/h | May be null |
| Reading quality | `status` | Diagnostic value | Distinguish `read` from `estimated` |
| Last reading time | `date` | Timestamp | Useful to detect stale data |

Unique IDs should be stable across restarts and include location ID plus entity key. Meter serial numbers should not appear in public logs.

## Data ingestion strategy

1. Authenticate and fetch all accessible locations, following pagination.
2. For each location, fetch a bounded UTC date range; follow all pages.
3. Maintain an idempotent key such as `(location_id, date)` for readings.
4. Store a sync cursor only after successful processing; consider a small overlap for `modified_since` to avoid missing equal-timestamp updates.
5. Poll conservatively because data is hourly. Confirm actual API publication latency before choosing a default.
6. Use retry/backoff for HTTP 429 and transient failures. Preserve the last good value while indicating stale/unavailable status appropriately.
7. Never treat `null` as zero, and never count the same interval twice.

## Historical data and Home Assistant statistics

The API explicitly supports historical ranges and modified records. However, Home Assistant's standard sensor state history is **not** a general-purpose bulk historical import API.

Before promising Energy Dashboard compatibility:
- Verify that `reading_total` is a suitable monotonically increasing energy total and determine reset behavior.
- Choose correct `device_class`, `state_class` and units only after validation.
- Determine whether to expose historical energy via an external statistics mechanism, a separate history view, or a documented limitation.
- Investigate how revisions to earlier intervals can be reconciled without double-counting or corrupting long-term statistics.
- Test DST boundaries while using UTC API timestamps.

## Security and privacy

- API keys must be stored in Home Assistant's config entry storage, not in repository files, examples, log messages or public diagnostics.
- Mask account addresses, location names and meter serial numbers in shared test fixtures.
- Avoid collecting analytics or sending data to third parties.
- API is read-only according to the supplied endpoint definitions; no control of heating equipment is implied.

## Open questions

- Exact time interval represented by each `date` value (start vs end of hour)
- Typical publication delay and historical retention
- Behavior when meter counters reset or equipment is replaced
- Semantics of historical corrections and null `modified_at`
- Whether measured vs estimated inclusion should be user-configurable
- Appropriate initial-history import mechanism and statistics correction behavior

## Localization and v0.1 acceptance criteria

English is the development and fallback language. Finnish (fi), Swedish (sv) and English (en) are mandatory for user-facing configuration, errors, entity names and documentation. Use translation keys and stable language-independent unique IDs. Automated tests must verify translation key parity. Use synthetic fixtures only. Initial polling target: 15 minutes, with a bounded overlapping UTC query window. Historical statistics import is deferred until timestamp semantics and correction handling are validated. Never infer instantaneous power from hourly energy or unverified flow semantics.
