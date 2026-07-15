# Changelog 

## [Unreleased]

### Changed
 - deps: patch upgrades (22 pkgs, incl. security fixes: authlib, pip, soupsieve, tornado, uv)
 - deps: minor upgrades (60 pkgs, incl. security fixes: bleach, idna, joserfc, jupyter-server, jupyterlab, mistune, msgpack, nltk, pillow, urllib3); widened cartopy constraint to `<0.26.0`
 - deps: major upgrades: mypy 1.20→2.2, numpy 1.26→2.0 (widened to `<3`), pandas 2.3→3.0 (widened to `<4`), toshi-hazard-post 0.7.1→0.7.3, numba/llvmlite (unblocked by numpy 2.x), cryptography (security fix GHSA-537c-gmf6-5ccf), lxml, pymdown-extensions (security fix GHSA-62q4-447f-wv8h), rpds-py, smart-open, tzdata
 - deps: matplotlib held at 3.10.9 and constrained to `<3.11.0` — 3.11 changes plot rendering enough to break image-comparison baselines

## [0.1.4] 2026-05-06

### Changed
 - Migrate from Poetry to uv; replace flake8/black/isort with ruff
 - hatch-vcs for versioning
 - gate releases requiring update to CHANGELOG
 - git hook requiring update to CHANGELOG

 ### Removed
 - bump2version

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