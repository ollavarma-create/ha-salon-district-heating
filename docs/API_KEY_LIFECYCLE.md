# API key lifecycle — rc.2

Open https://salonkaukolampo.fi/asiakkaille/asiakasportaali/ → Kulutusraportit → LämpöVahti (https://lampovahti.salonkaukolampo.fi/login). Sign in, select Tilini in the left menu, scroll below password change to API, select Luo uusi avain. The portal shows expiration and last used dates. Copy the key privately and optionally enter the expiration date in HA. Existing entries can use Reconfigure to add or clear the date. Reauthentication accepts a replacement key and optional new expiry; omitting it clears the old date.

Repairs warnings at 30, 7, 1 and 0 days are advisory. The entered date never blocks polling. No expiry-specific API error or programmatic expiry endpoint is confirmed. Diagnostic sensors report entered expiry, remaining days, latest observed authentication result and last successful consumption request in the current runtime. No historical data import is planned. Tariffs remain separate work.

Field tests: upgrade existing entry, reconfigure date to today +31/30/7/1/0 days, clear date, verify Repairs and continued polling, test reauth with a replacement key, confirm existing entity IDs/history, check all languages. Restore actual date after testing. Production validation and rollback remain pending.
