# Distribution readiness

The integration is distributed as an unofficial community integration.
The initial compatibility target is Home Assistant 2026.11.0, pending testing.
HACS repository metadata and validation are prepared independently of measurement logic.

Before release:
- [ ] Verify the current Home Assistant community distribution mechanism and catalog requirements.
- [x] Add original brand assets.
- [ ] Verify whether the temporary brands validation exception can be removed.
- [x] Pin workflow actions to verified commit SHAs and migrate checkout/setup-python to Node.js 24.
- [ ] Review mutable upstream Docker images used by Hassfest and HACS.
- [x] Draft English, Finnish and Swedish manual installation instructions.
- [ ] Verify community distribution installation instructions.
- [ ] Test installation and upgrade through the community distribution UI on the production system.
- [ ] Verify Energy Dashboard behavior.
- [ ] Publish a stable GitHub release and only then request catalog inclusion.

No historical import, tariff engine or separate database is required.
