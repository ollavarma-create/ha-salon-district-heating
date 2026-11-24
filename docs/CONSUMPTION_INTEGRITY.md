# Delayed hourly consumption — field observations

On 2026-11-24 (Europe/Helsinki, UTC+02), three successive hourly records initially reported zero consumption despite an increased cumulative meter reading. Later requests returned nonzero consumption without a change to modified_at or status (read).

For the 12:00 local record, consumption was zero at 12:26, 12:30 and 12:31, and matched the cumulative difference at 12:40. The exact transition time is unknown. Identifiers and absolute meter readings are omitted.

## Alpha.3 policy

- Poll at minute 20, then 30, 40 and 50 only if the latest hourly record is missing or consumption is pending, with existing jitter.
- Compare consecutive hourly records from the same meter. The assumption that consumption describes the preceding interval is supported by observations but awaits provider confirmation.
- A mismatch suppresses the hourly energy and average power values (unknown), without changing the original API row or the other sensors.
- A genuine zero with unchanged cumulative reading is consistent.
- Missing predecessor, missing cumulative readings, meter changes and decreasing totals are unverifiable; valid API consumption is retained in these cases.
- Revisit pending records in the existing 48-hour overlap and log observed completion delay. This does not backfill Home Assistant history or persist pending tracking across restarts.
- Do not rely on modified_at alone for revision detection.

The provider's internal processing schedule and modified_at semantics remain unconfirmed. No customer identifiers, credentials or raw customer records are included in tests.

## Incremental synchronization experiment (2026-11-24)

Two requests for the same location were made after the 12:00 local (10:00 UTC) record had completed. With modified_since=2026-11-24T10:15:00Z, five records were returned, including the 10:00 UTC record with consumption=1000 Wh. With modified_since=2026-11-24T10:30:00Z, four records were returned and the 10:00 UTC record was absent. Its modified_at remained 2026-11-24T10:15:25.513917Z despite the observed consumption change between 12:31 and 12:40 local time.

This confirms that a client advancing its incremental synchronization cutoff beyond the original timestamp can miss a later consumption revision. The filter itself behaves as documented (modified_at >= cutoff); the observed timestamp does not reflect the consumption revision. The provider's internal implementation and intended semantics remain unconfirmed. Retain the overlapping date-range polling strategy. Historical backfill remains outside alpha.3 scope.
