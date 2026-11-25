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

## Observed energy resolution (2026-11-24)

A LämpöVahti hourly CSV export for 2026-11-23 contains 24 rows: four at 1 kWh and twenty at 2 kWh, totaling 44 kWh (mean hourly power 1.833 kW). No fractional kWh values occur. The API observations to date likewise show consumption and cumulative readings in multiples of 1000 Wh. This is evidence of an observed 1 kWh reporting increment, not proof of the meter's intrinsic accuracy or a guaranteed API resolution.

A plausible explanation is quantization of the cumulative meter reading before hourly differences are calculated. A constant actual power of 1.8 kW can therefore produce alternating reported hourly averages of 1 and 2 kW. The stage at which quantization occurs (meter, telemetry, backend or export) is unknown. Preserve API values without inventing additional precision. The hourly average power sensor represents reported hourly energy divided by one hour, not instantaneous power. Longer-period aggregation reduces the relative impact of cumulative-reading quantization, but does not establish billing accuracy.

Supply/return temperatures and volume flow could support an independent approximate thermal power estimate, but their sampling and aggregation semantics are unconfirmed. Do not substitute such estimates for measured energy or billing data. No additional power sensor is introduced by this documentation change.

Open questions: Is 1 kWh the intended reporting resolution? Can finer cumulative readings be exposed? Are temperatures and volume flow instantaneous samples or interval averages? The integration must remain usable even if these questions are not answered. Customer identifiers and raw customer exports are not published.

## Physical meter and intended use

The inspected installation uses a Kamstrup heat meter, visually identified as a MULTICAL 403 (model identification not independently verified), replaced with a 4G-based remote-reading installation in 2026 according to the owner. Its E1 display shows energy in MWh with three decimal places, corresponding to a 1 kWh display increment. This agrees with the observed CSV and API reporting increments. The exact meter configuration and remote-reading register resolution have not been verified and need not be assumed.

Manufacturer reference: [Kamstrup MULTICAL 403 Technical Description](https://productfinder.gwf.ch/uploads_productfinder/downloads/FILE100000166_C_ENpdf.pdf), section 3.2.3 (resolution). The reference is retained for further verification; no specific configuration code is asserted for this installation.

### User-facing limitation

Hourly energy and hourly average power are intended for monitoring and longer-period analysis. Observed 1 kWh reporting increments, hourly aggregation and delayed API completion make these values unsuitable as the sole input to real-time heating control, rapid feedback loops or safety functions. Resolution is not the same as metrological accuracy. Do not infer instantaneous power from hourly average power. Other API measurements also have unconfirmed sampling semantics.

Planned UI improvement: provide a concise informational notice during integration setup and in user documentation in English, Finnish and Swedish. Do not generate recurring warnings for normal quantization. Preserve existing sensor identifiers and raw reported values. This is a documentation-only change; the UI notice is not yet implemented.

## Alpha.4 display policy

The hourly energy and average power sensors expose the most recent API consumption consistent with consecutive hourly cumulative readings from the same meter. No interpolation or derived consumption is published. A separate consumption measurement time identifies the displayed value; measurement time continues to identify the latest API row. Data quality reports confirmed, pending, unverifiable or stale for the latest row. The held value expires after two hours from its measurement timestamp and is not carried across a meter change. This two-hour limit is a provisional UI policy, not an API guarantee. API retrieval failures retain Home Assistant's normal unavailable behavior. Hourly average power no longer requests measurement statistics because held values are not instantaneous samples. Existing historical statistics are not rewritten. Polling remains at :20/:30/:40/:50, stopping retries when the current row is consistent. The cumulative energy sensor is unchanged. Historical backfill remains out of scope.
