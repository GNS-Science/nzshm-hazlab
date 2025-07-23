"""This module provides functions for plotting hazard curves and derived products."""

from typing import TYPE_CHECKING, Any

import nzshm_hazlab.plot.constants as constants
from nzshm_hazlab.base_functions import convert_poe

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.lines import Line2D
    from nzshm_common import CodedLocation

    from nzshm_hazlab.data import HazardCurves

PERIOD_MIN = 0.01


def _center_out(length):
    """Yield the indicies going out from the center of a list of len length.

    This is used to plot error bound estimates in the plotting functions.
    """
    center = length // 2
    left = center - 1
    if length % 2 == 1:
        right = center + 1
    else:
        right = center

    for i in range(center):
        yield (left, right)
        left -= 1
        right += 1


def plot_hazard_curve(
    axes: "Axes",
    data: "HazardCurves",
    hazard_model_id: str,
    location: "CodedLocation",
    imt: str,
    vs30: int,
    aggs: list[str],
    **kwargs: Any,  # color, linestyle, label, etc
) -> list['Line2D']:
    """Plot hazard curves with optional error bound estimates.

    If more than one item is passed to aggs they will be treated as error bound estimates. The
    area between the inner values will be shaded and outer values will be plotted with a thin line.
    If an odd number of aggs is provided, the centre value will be plotted as a thick line; this is
    usually a central value such as the mean or 50th percentile aggregate. See example.

    Args:
        axes: Handle of axes to plot to.
        data: The hazard curve data.
        hazard_model_id: The id of the hazard model to plot.
        location: The site location.
        imt: The intensity measure type to plot (e.g. "PGA", SA(1.0)")
        vs30: The site vs30 to plot.
        aggs: The aggregate statistics to plot (e.g. "mean", "0.1")
        kwargs: Any additional arguments to pass to the matplotlib plot function.

    Returns:
        The handles of the plotted lines.

    Example:
        This will plot the mean hazard curve along with 60% and 80% confidence intervals as dashed
        lines and label the curve "PGA vs30=400".
        ```py
        >>> from nzshm_hazlab.data.data_loaders import THSHazardLoader
        >>> from nzshm_hazlab.data.hazard_curves import HazardCurves
        >>> from nzshm_hazlab.plot import plot_hazard_curve
        >>> from nzshm_common import CodedLocation
        >>> import matplotlib.pyplot as plt

        >>> hazard_model_id = "NSHM_v1.0.4"
        >>> loader = THSHazardLoader()
        >>> hazard_curves = HazardCurves(loader=loader)
        >>> location_id = "WLG"
        >>> location = CodedLocation(-41.3, 174.78, 0.001)

        >>> aggs = ["0.1", "0.2", "mean", "0.8", "0.9"]

        >>> fig, ax = plt.subplots(1,1)
        >>> line_handles = plot_hazard_curve(
                ax, hazard_curves, hazard_model_id, location, "PGA", 400, aggs, label="PGA vs30=400", linestyle="--"
            )
        ```
    """
    color = kwargs.pop("color", None)
    color = color if color else constants.DEFAULT_COLOR

    label = kwargs.pop("label", None)

    line_handles = []

    # if odd number of aggs, plot the centre as a thick line
    i_center = int(len(aggs) / 2)
    if len(aggs) % 2 == 1:
        levels, probs = data.get_hazard_curve(hazard_model_id, imt, location, vs30, aggs[i_center])
        lhs = axes.plot(levels, probs, lw=constants.LINE_WIDTH_CENTER, color=color, label=label, **kwargs)
        line_handles += lhs

    filled = False
    for left, right in _center_out(len(aggs)):
        levels_low, probs_low = data.get_hazard_curve(hazard_model_id, imt, location, vs30, aggs[left])
        levels_high, probs_high = data.get_hazard_curve(hazard_model_id, imt, location, vs30, aggs[right])
        lhs = axes.plot(levels_low, probs_low, lw=constants.LINE_WIDTH_BOUNDS, color=color, **kwargs)
        line_handles += lhs

        lhs = axes.plot(
            levels_high,
            probs_high,
            lw=constants.LINE_WIDTH_BOUNDS,
            color=color,
            **kwargs,
        )
        line_handles += lhs

        if not filled:
            axes.fill_between(
                levels_low,
                probs_low,
                probs_high,
                alpha=constants.FILL_ALPHA,
                color=color,
            )
            filled = True

    axes.set_xscale("log")
    axes.set_yscale("log")

    return line_handles


def plot_uhs(
    axes: "Axes",
    data: "HazardCurves",
    hazard_model_id: str,
    location: "CodedLocation",
    imts: list[str],
    poe: float,
    inv_time: float,
    vs30: int,
    aggs: list[str],
    **kwargs: Any,  # color, linestyle, label, etc
) -> list['Line2D']:
    """Plot uniform hazard spectra curves with optional error bound estimates.

    If more than one item is passed to aggs they will be treated as error bound estimates. The
    area between the inner values will be shaded and outer values will be plotted with a thin line.
    If an odd number of aggs is provided, the centre value will be plotted as a thick line; this is
    usually a central value such as the mean or 50th percentile aggregate. See example.

    Args:
        axes: Handle of axes to plot to.
        data: The hazard curve data.
        hazard_model_id: The id of the hazard model to plot.
        location: The site location.
        imts: The periods as IMTs (e.g. ["PGA", SA(1.0)", "SA(2.0)"])
        poe: The proability of exceedance at which to calculate the UHS.
        inv_time: The investigation time for the poe.
        vs30: The site vs30 to plot.
        aggs: The aggregate statistics to plot (e.g. "mean", "0.1")
        kwargs: Any additional arguments to pass to the matplotlib plot function.

    Returns:
        The handles of the plotted lines.

    Example:
        This will plot the mean UHS curve along with 60% and 80% confidence intervals as dashed lines
        and label the curve "vs30=400".
        ```py
        >>> from nzshm_hazlab.data.data_loaders import THSHazardLoader
        >>> from nzshm_hazlab.data.hazard_curves import HazardCurves
        >>> from nzshm_hazlab.plot import plot_uhs
        >>> from nzshm_common import CodedLocation
        >>> import matplotlib.pyplot as plt

        >>> hazard_model_id = "NSHM_v1.0.4"
        >>> loader = THSHazardLoader()
        >>> hazard_curves = HazardCurves(loader=loader)
        >>> location_id = "WLG"
        >>> location = CodedLocation(-41.3, 174.78, 0.001)

        >>> aggs = ["0.1", "0.2", "mean", "0.8", "0.9"]
        >>> imts = ["PGA", "SA(0.2)", "SA(0.5)", "SA(1.0)", "SA(2.0)", "SA(3.0)", "SA(5.0)", "SA(10.0)"]

        >>> fig, ax = plt.subplots(1,1)
        >>> line_handles = plot_uhs(
                ax, hazard_curves, hazard_model_id, location, imts, 400, aggs, label="vs30=400", linestyle="--"
            )
        ```
    """
    color = kwargs.pop("color", None)
    color = color if color else constants.DEFAULT_COLOR

    label = kwargs.pop("label", None)

    line_handles = []

    apoe = convert_poe(poe, inv_time, 1.0)

    # if odd number of aggs, plot the centre as a thick line
    i_center = int(len(aggs) / 2)
    if len(aggs) % 2 == 1:
        periods, imtls = data.get_uhs(hazard_model_id, apoe, imts, location, vs30, aggs[i_center])
        lhs = axes.plot(periods, imtls, lw=constants.LINE_WIDTH_CENTER, color=color, label=label, **kwargs)
        line_handles += lhs

    filled = False
    for left, right in _center_out(len(aggs)):
        periods_low, imtls_low = data.get_uhs(hazard_model_id, apoe, imts, location, vs30, aggs[left])
        periods_high, imtls_high = data.get_uhs(hazard_model_id, apoe, imts, location, vs30, aggs[right])
        lhs = axes.plot(periods_low, imtls_low, lw=constants.LINE_WIDTH_BOUNDS, color=color, **kwargs)
        line_handles += lhs

        lhs = axes.plot(
            periods_high,
            imtls_high,
            lw=constants.LINE_WIDTH_BOUNDS,
            color=color,
            **kwargs,
        )
        line_handles += lhs

        if not filled:
            axes.fill_between(
                periods_low,
                imtls_low,
                imtls_high,
                alpha=constants.FILL_ALPHA,
                color=color,
            )
            filled = True

    return line_handles
