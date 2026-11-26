# Optional district heating dashboard

Home Assistant 2026.11.0 does not offer a dedicated district heating category in its Energy Dashboard setup wizard. This example uses only native dashboard cards and Recorder statistics, without additional integrations or a database.

## Installation

1. Configure the Salon Kaukolämpö integration.
2. In Settings > Devices & services > Entities, find the actual entity IDs for all eleven sensors. IDs in the example are illustrative English defaults, not guaranteed: language, renamed entities and multiple locations can change them. Replace all references with your own IDs.
3. Create a separate dashboard in Settings > Dashboards. Open it, enter edit mode, and open the Raw configuration editor from the menu.
4. Paste the contents of [district-heating-dashboard.yaml](district-heating-dashboard.yaml) into that new dashboard and save. Do not overwrite an existing dashboard you want to retain.

## Interpretation and limitations

The daily, weekly and monthly charts use the change statistic of the cumulative total energy sensor (TOTAL_INCREASING), not the sum of repeated hourly sensor states. They count changes recorded by Home Assistant; delayed samples may fall into a later calendar period than the original measurement. No backfill is performed. Initial readings establish a baseline; verify the first statistic and subsequent deltas in Developer tools > Statistics. Charts need time for statistics to accumulate and may initially be empty. Recorder must retain the sensor and its statistics.

The temperature and flow charts display recorded states, not guaranteed instantaneous values. Use the diagnostic timestamps and quality status to assess freshness. This dashboard is for monitoring, not safety or real-time control. LämpöVahti remains the source for official consumption history and billing.

This example requires field testing on Home Assistant 2026.11.0; it is not automatically installed and does not modify the integration or existing dashboards.

## Heat transfer card and localized dashboards

Choose district-heating-dashboard.yaml (English), district-heating-dashboard.fi.yaml (Finnish) or district-heating-dashboard.sv.yaml (Swedish). Copy the corresponding heat-transfer-en.svg, heat-transfer-fi.svg or heat-transfer-sv.svg into the HA configuration directory under www/salon_district_heating/. The card references /local/salon_district_heating/. If www is newly created, restart HA if necessary. Replace example entity IDs with actual IDs. The diagram is conceptual, not a hydraulic installation drawing. Values are delayed primary-side readings only. The original entities card remains as fallback. New cards and localized variants await field testing.
