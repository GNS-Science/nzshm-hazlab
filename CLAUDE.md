# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install (development)
uv sync --all-extras

# Run tests
uv run pytest tests/
uv run pytest tests/data/test_hazard_curves.py          # single file
uv run pytest tests/data/test_hazard_curves.py::test_uhs  # single test
uv run pytest -k keyword                                  # filter by keyword

# Tests with coverage report
uv run tox -e py311

# Format (ruff)
uv run tox -e format

# Lint + type check (ruff + mypy)
uv run tox -e lint

# Security audit
uv run tox -e audit

# Docs
mkdocs serve   # local preview
mkdocs build   # static build
```

Code style: line length 120, ruff formatting (quote-style=preserve), Google-style docstrings.

## Architecture

`nzshm_hazlab` is a library for retrieving and visualizing seismic hazard results from the New Zealand Seismic Hazard Model (NZSHM). It has no CLI — designed for use in Jupyter notebooks and Python scripts.

### Data layer (`nzshm_hazlab/data/`)

Three data classes handle retrieval and caching:

- **`HazardCurves`** — fetches hazard curves (IMTLs vs PoE) for a point; also computes UHS via interpolation
- **`HazardGrids`** — fetches IMTL values at a given PoE across a geographic grid (for hazard maps)
- **`Disaggregations`** — fetches and manages disaggregation matrices (TRT, magnitude, distance, epsilon)

All three use lazy loading and cache results in pandas DataFrames to avoid re-fetching.

### Loader protocol (`nzshm_hazlab/data/data_loaders/`)

Data classes accept any object implementing the relevant Protocol (`HazardLoader`, `GridLoader`, `DisaggLoader`). Four concrete loaders exist:

| Loader | Source | Notes |
|---|---|---|
| `THSHazardLoader` | toshi-hazard-store Arrow parquet dataset | Requires `THS_DATASET_AGGR_URI` env var |
| `THPHazardLoader` | toshi-hazard-post (dynamic aggregation) | Requires `THP_RLZ_DIR` env var; calculates on-the-fly from logic trees |
| `OQCSVHazardLoader` | OpenQuake CSV output files | Parses OQ output directly |
| `DynamoHazardLoader` | DynamoDB | Deprecated; will be removed in toshi-hazard-store v2 |

### Plot layer (`nzshm_hazlab/plot/`)

Pure functions that accept data from the data classes:

- `plot_hazard_curve()` / `plot_uhs()` — matplotlib semi-log and spectral plots
- `plot_hazard_map()` — geographic contour maps via cartopy
- `plot_disagg_1d/2d/3d()` — disaggregation visualizations

### Utilities (`nzshm_hazlab/base_functions.py`)

Stateless functions for seismic hazard math: PoE↔rate conversions (`prob_to_rate`, `rate_to_prob`), IMT string parsing (`period_from_imt`, `imt_from_period`), return period conversions (`rp_from_poe`, `poe_from_rp`), and `calculate_hazard_at_poe()` for interpolation.

### Environment variables

| Variable | Used by | Purpose |
|---|---|---|
| `THS_DATASET_AGGR_URI` | `THSHazardLoader` | Path/URI to toshi-hazard-store Arrow dataset |
| `THP_RLZ_DIR` | `THPHazardLoader` | Path/URI to realization dataset (local or S3) |
