# Distribution readiness

The integration is distributed as an unofficial community integration.
The initial compatibility target is Home Assistant 2026.11.0, pending testing.
HACS repository metadata and validation are prepared independently of measurement logic.

Before release:
- Verify the current Home Assistant community distribution mechanism and catalog requirements.
- Add original brand assets; remove the temporary brands validation exception when appropriate.
- Review and pin workflow actions to verified commit SHAs.
- Complete English, Finnish and Swedish installation instructions.
- Test installation and upgrade through the community distribution UI on the production system.
- Verify Energy Dashboard behavior.
- Publish a stable GitHub release and only then request catalog inclusion.

No historical import, tariff engine or separate database is required.
