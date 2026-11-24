# LämpöVahti API: data and endpoint reference

Source: the LämpöVahti **OpenAPI 3.0.3** specification exported from the official Swagger documentation (reviewed 2026-11-23). This file documents the API contract, **not** verified live responses.

Official documentation: https://api-lampovahti.salonkaukolampo.fi/external/api/docs/

## Base URL and authentication

The specification declares `servers: [{url: /external/api}]`, relative to the documentation host:

`https://api-lampovahti.salonkaukolampo.fi/external/api`

Send the account's key as `X-API-Key: <your_key>`. Do not embed keys in source code or issue reports.

Published rate limits: **60 requests/minute** and **10,000 requests/day** per key. Exceeding limits returns **HTTP 429**.

## GET /v1/locations/

Returns locations accessible to the API key. Query parameters:

| Parameter | Type | Meaning |
| --- | --- | --- |
| `page` | integer | Pagination page |
| `page_size` | integer | 1–2000; default 200 |

Response is paginated with `count`, `next`, `previous`, and `results`. Each location has:

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | integer | Location ID |
| `name` | string | Location name |
| `address` | string | Street address |
| `postal_code` | string | Postal code |
| `city` | string | City |

Treat location fields as private customer data.

## GET /v1/consumptions/

Returns **hourly** meter readings for accessible locations.

| Parameter | Type | Meaning |
| --- | --- | --- |
| `start` | string | UTC ISO 8601 range start; required unless `modified_since` supplied |
| `end` | string | UTC ISO 8601 **exclusive** range end; required unless `modified_since` supplied |
| `location_id` | integer | Optional; omit for all accessible locations |
| `modified_since` | string | UTC ISO 8601 timestamp; rows with `modified_at >=` value, ordered by `modified_at` ascending; removes requirement for start/end |
| `status` | string | `read` only by default; `estimated` also includes gap-filled interpolated rows |
| `page` | integer | Default 1 |
| `page_size` | integer | 1000–50000; default 10000 |

**Important:** `status=estimated` includes both measured and interpolated records; it is not an estimated-only filter.

Response: `count` (integer), `next` (URI or null), `previous` (URI or null), `results` (array of consumption rows). Follow `next` to avoid silently dropping data.

### Consumption row

| Field | OpenAPI type | Unit / semantics |
| --- | --- | --- |
| `location_id` | integer | Location ID |
| `date` | string | UTC ISO 8601 timestamp |
| `consumption` | integer | Energy consumption, **Wh** |
| `reading_total` | number or null | Cumulative meter reading, **Wh**; null for smoothed rows |
| `flow_temperature` | number or null | Supply temperature, **°C**; null for smoothed rows |
| `return_temperature` | number or null | Return temperature, **°C**; null for smoothed rows |
| `flow` | number or null | Flow rate, **m³/h**; null for smoothed rows |
| `serial_number` | string | Meter serial; empty when unavailable |
| `status` | `read` or `estimated` | Actual or gap-filled interpolated |
| `modified_at` | string or null | UTC ISO 8601 last-change timestamp |

All fields above are marked required in the schema, including those whose values may be null.

### Example requests (no secrets)

```bash
# Supply your key through an environment variable in your own shell.
curl --fail-with-body \
  -H "X-API-Key: ${LAMPOVAHTI_API_KEY}" \
  "https://api-lampovahti.salonkaukolampo.fi/external/api/v1/locations/"

curl --fail-with-body \
  -G -H "X-API-Key: ${LAMPOVAHTI_API_KEY}" \
  --data-urlencode "start=2026-01-01T00:00:00Z" \
  --data-urlencode "end=2026-01-02T00:00:00Z" \
  "https://api-lampovahti.salonkaukolampo.fi/external/api/v1/consumptions/"
```

These commands are illustrative and have not been tested against an authenticated account.

## Integration implications

- Convert **Wh to kWh** where appropriate for Home Assistant; never relabel without converting.
- Do not equate an hourly Wh value with instantaneous kW without explicit interval handling.
- Handle nullable temperatures, flow and cumulative readings without replacing missing values with zero.
- Track actual vs interpolated values and avoid implying estimates are direct measurements.
- Preserve UTC timestamps internally; display local time through Home Assistant.
- Handle `modified_since` inclusivity (`>=`) with idempotent upserts and a safe overlap.
- Confirm how historical revisions should be reflected in Home Assistant statistics before implementation.
- Verify interval timestamp meaning, retention limits, data latency and API error behavior with real responses.

## Authenticated field validation (2026-11-24)

Both endpoints returned HTTP 200 with X-API-Key authentication. A missing credential returned HTTP 401. A 24-hour UTC range returned 24 consecutive hourly records, all marked read, with all measurement fields populated. Cumulative readings increased consistently with hourly consumption. Observed energy values were quantized in 1000 Wh steps; this is an observation, not a guaranteed resolution. Most modification timestamps were about 15 minutes after the reading timestamp, with some delayed batch updates. Pagination envelope was confirmed, but multi-page traversal was not exercised. Timestamp interval meaning, flow averaging, retention and reset behavior remain open. No real customer identifiers or readings are included in fixtures.
