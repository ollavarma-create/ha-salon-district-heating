# Distribution readiness

The integration is distributed as an unofficial community integration.
The initial compatibility target is Home Assistant 2026.11.0, successfully tested for initial Marketplace installation on Fedora Docker.
HACS repository metadata and validation are prepared independently of measurement logic.

Before release:
- [x] Review Marketplace documentation for custom repository distribution.
- [x] Add original brand assets.
- [x] Confirm CI passes after removing the brands validation exception.
- [ ] Verify brand image dimensions and repository description/topics.
- [x] Pin workflow actions to verified commit SHAs and migrate checkout/setup-python to Node.js 24.
- [ ] Review mutable upstream Docker images used by Hassfest and HACS.
- [x] Draft English, Finnish and Swedish manual installation instructions.
- [x] Document Marketplace installation in all three README files.
- [x] Configure weekly GitHub Actions-only Dependabot updates (one open version-update PR).
- [x] Configure weekly distribution validation; manual dispatch remains available.
- [x] Field-test Marketplace installation instructions (custom repository, default branch commit).
- [ ] Test installation and upgrade through the community distribution UI on the production system.
- [x] Verify Energy Dashboard setup categories: no dedicated district heating category in 2026.11.0.
- [ ] Verify named pre-release selection and update mechanism.
- [ ] Verify restart and long-term energy statistics.
- [ ] Develop and test a name-independent dashboard generator; verify stable sensor-role lookup and multiple locations.
- [ ] Publish a stable GitHub release and only then request catalog inclusion.

No historical import or external database is required. Optional tariff estimates use Home Assistant storage.

## Acceptance checkpoint — 2026-11-25

- Published v0.1.0-rc.1 as a pre-release, tag and manifest verified at commit 6b34edfc.
- Clean Docker test instance on Fedora, HA 2026.11.0, localhost port 8125. GitHub device authorization showed public data only (HACS OAuth application).
- Marketplace recognized the custom repository and installed commit 6b34edf, matching the RC code. Named pre-release selection is not yet verified.
- Integration configuration succeeded; all eleven sensors displayed values. Local integration icon rendered, Marketplace listing icon did not.
- Observed confirmed and pending quality states; pending retained the preceding confirmed hourly value with its own timestamp.
- Optional dashboard example rendered successfully after adapting entity IDs to the area-prefixed IDs assigned by HA. Temperature history appeared. Daily/weekly/monthly statistics were not yet populated.
- Energy Dashboard wizard has electricity, solar, battery, gas, water and individual electrical devices, but no district heating category. Do not misclassify heat as electricity or gas.
- Keep the clean test instance running for statistics and logs. Production deployment remains pending. Utility clarification remains pending; observed behavior is documented and no further measurement logic changes are required for v0.1.0.
- Do not publish authentication codes, IP addresses, API keys or customer identifiers in screenshots.

## Marketplace references

- https://contributors.home-assistant.io/marketplace/guides/integrations/
- https://contributors.home-assistant.io/marketplace/reference/repository-structure/
- https://contributors.home-assistant.io/marketplace/how-it-works/
- https://contributors.home-assistant.io/marketplace/reference/validation/
- https://contributors.home-assistant.io/core/integrations/categories/

## v0.1.0 release checkpoint

RC.5 was field-tested on Fedora with 28 entities, dashboards, key expiry warnings and accumulating cost estimates. Production installation, real calendar tariff transition and named stable release installation remain to be verified. No dedicated Energy Dashboard district heating category is claimed.
