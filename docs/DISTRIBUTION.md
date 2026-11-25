# Distribution readiness

The integration is distributed as an unofficial community integration.
The initial compatibility target is Home Assistant 2026.11.0, pending testing.
HACS repository metadata and validation are prepared independently of measurement logic.

Before release:
- [x] Review Marketplace documentation for custom repository distribution.
- [x] Add original brand assets.
- [ ] Confirm CI passes after removing the brands validation exception.
- [ ] Verify brand image dimensions and repository description/topics.
- [x] Pin workflow actions to verified commit SHAs and migrate checkout/setup-python to Node.js 24.
- [ ] Review mutable upstream Docker images used by Hassfest and HACS.
- [x] Draft English, Finnish and Swedish manual installation instructions.
- [x] Document Marketplace installation in all three README files.
- [x] Configure weekly GitHub Actions-only Dependabot updates (one open version-update PR).
- [x] Configure weekly distribution validation; manual dispatch remains available.
- [ ] Field-test Marketplace installation instructions.
- [ ] Test installation and upgrade through the community distribution UI on the production system.
- [ ] Verify Energy Dashboard behavior.
- [ ] Publish a stable GitHub release and only then request catalog inclusion.

No historical import, tariff engine or separate database is required.

## Marketplace references

- https://contributors.home-assistant.io/marketplace/guides/integrations/
- https://contributors.home-assistant.io/marketplace/reference/repository-structure/
- https://contributors.home-assistant.io/marketplace/how-it-works/
- https://contributors.home-assistant.io/marketplace/reference/validation/
- https://contributors.home-assistant.io/core/integrations/categories/
