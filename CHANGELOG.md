# Changelog 

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