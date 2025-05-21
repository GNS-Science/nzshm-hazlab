# nzshm_hazlab
Python tools for post processing and visualizing hazard results for the NZSHM project.

[![pypi](https://img.shields.io/pypi/v/nzshm-hazlab.svg)](https://pypi.org/project/nzshm-hazlab/)
[![python](https://img.shields.io/pypi/pyversions/nzshm-hazlab.svg)](https://pypi.org/project/nzshm-hazlab/)
[![Build Status](https://github.com/GNS-Science/nzshm-hazlab/actions/workflows/dev.yml/badge.svg)](https://github.com/GNS-Science/nzshm-hazlab/actions/workflows/dev.yml)
[![codecov](https://codecov.io/gh/GNS-Science/nzshm-hazlab/branch/main/graphs/badge.svg)](https://codecov.io/github/GNS-Science/nzshm-hazlab)

## Features

nzshm-hazlab can retrieve "aggregate" hazard curves (mean and fractiles), display them with matplotlib, and calculate derivative products such as uniform hazard spectra (UHS).

Hazard curves can be retrieved from
- toshi-hazard-store databases
- OpenQuake output files
- PLANNED FEATURE: plot aggregate curves generated on-the-fly with toshi-hazard-post

![hazard curve](docs/figs/hazard_curve_example.png)

## Install

See [Installation](docs/installation.md) instructions.