"""This package provides functions for plotting seismic hazard.

Modules:
    hazard_curve: Defines functions for plotting hazard curves and derived products
"""

from .disaggregation import plot_disagg_1d, plot_disagg_2d, plot_disagg_3d
from .hazard_curve import plot_hazard_curve, plot_uhs
from .hazard_map import plot_hazard_diff_map, plot_hazard_map
