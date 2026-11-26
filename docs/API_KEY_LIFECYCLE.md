# API key lifecycle — rc.3

Open https://salonkaukolampo.fi/asiakkaille/asiakasportaali/ → Kulutusraportit → LämpöVahti (https://lampovahti.salonkaukolampo.fi/login). Sign in, select Tilini in the left menu, scroll below password change to API, select Luo uusi avain. The portal shows expiration and last used dates. Copy the key privately and optionally enter the expiration date in HA. Existing entries can use Reconfigure to add or change the date, or enable the explicit removal switch. Removal takes precedence over the calendar value; an omitted date without removal preserves the previous date. Reauthentication accepts a replacement key and optional new expiry; omitting it clears the old date.

Repairs warnings at 30, 7, 1 and 0 days are advisory. The entered date never blocks polling. No expiry-specific API error or programmatic expiry endpoint is confirmed. Diagnostic sensors report entered expiry, remaining days, latest observed authentication result and last successful consumption request in the current runtime. No historical data import is planned. Tariffs remain separate work.

Field tests: upgrade existing entry, reconfigure date to today +31/30/7/1/0 days, clear date, verify Repairs and continued polling, test reauth with a replacement key, confirm existing entity IDs/history, check all languages. Restore actual date after testing. Production validation and rollback remain pending.

## Field validation — 2026-11-26

Fedora HA 2026.11.0 Marketplace upgrade to rc.2 succeeded; 15 entities and existing dashboard visible. Finnish Repairs warnings at 30, 7 and 0 days observed. Diagnostics showed accepted authentication, 728 remaining days and a recent successful request. Calendar widget did not allow clearing a selected date; reconfigure label showed raw key and success message was English. rc.3 adds explicit removal, a custom translated success reason and localized form labels (already present in rc.2; runtime translation loading must be retested). Dashboard examples now include API diagnostics. Pending: removal and issue cleanup in HA, one-day warning, midnight transition, continued polling after entered expiry, reauthentication and language checks.
