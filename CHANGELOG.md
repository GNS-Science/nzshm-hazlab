# Changelog 

## [Unreleased]

### Changed
 - Migrate from Poetry to uv; replace flake8/black/isort with ruff
 - Upgrade lancedb 0.29.2 → 0.30.2 (fixes CreateEmptyTableRequest import error)

## [0.1.3] 2026-03-30

### Changed
 - latest toshi-hazard-store version
 - reinstated windows build in GHA test suite

## [0.1.2] 2026-03-27

### Changed
 - latest nzshm-common and nzshm-model versions
 - unpinned nzshm-common, nzshm-model, and toshi-hazard-store dependencies
 - updated setup.cfg to be compatible with latest tox

## [0.1.1] 2026-01-21

### Added
 - audit environment for tox

### Changed
 - update dependencies for new advisories

## [0.1.0] 2025-10-17

### Changed
 - Migrated pyproject.toml to PEP 508 as per poetry v2.2 docs.
 - Ensure CI/CD workflows use minimum install footprints

### Added
- Plotting functions for hazard maps.
- Plotting functions for disaggregations.
- Plotting functions for hazard curves and UHS.
- Load hazard grids (used for hazard maps) from DynamoDB version of toshi-hazard-store (to be deprecated).
- Load disaggregations from DynamoDB version of toshi-hazard-store (to be deprecated).
- Load disaggregations from OpenQuake csv output.
- Load hazard curves from DynamoDB version of toshi-hazard-store (to be deprecated).
- Load hazard curves from Arrow version of toshi-hazard-store.
- Load hazard curves from OpenQuake csv output.
- Create hazard curves from user-defined hazard model.