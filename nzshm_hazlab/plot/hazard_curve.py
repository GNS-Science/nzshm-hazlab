from typing import TYPE_CHECKING

import nzshm_hazlab.plot.constants as constants

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.lines import Line2D
    from nzshm_common import CodedLocation

    from nzshm_hazlab.data import HazardCurves


def plot_hazard_curve(
    axes: "Axes",
    data: "HazardCurves",
    hazard_model_id: str,
    location: "CodedLocation",
    imt: str,
    vs30: int,
    aggs: list[str],
    **kwargs,  # color, linestyle, label, etc
) -> list['Line2D']:

    color = kwargs.pop("color", None)
    color = color if color else constants.DEFAULT_COLOR

    label = kwargs.pop("label", None)

    line_handles = []

    # if odd number of aggs, plot the centre as a thick line
    i_center = int(len(aggs) / 2)
    if len(aggs) % 2 == 1:
        levels, probs = data.get_hazard_curve(hazard_model_id, imt, location, aggs[i_center], vs30)
        lhs = axes.plot(levels, probs, lw=constants.LINE_WIDTH_CENTER, color=color, label=label, **kwargs)
        line_handles += lhs

    filled = False
    for i in range(1, i_center + 1):
        levels_low, probs_low = data.get_hazard_curve(hazard_model_id, imt, location, aggs[i_center - i], vs30)
        levels_high, probs_high = data.get_hazard_curve(hazard_model_id, imt, location, aggs[i_center + i], vs30)
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
    axes.set_xlabel("Shaking Intensity, %s [g]" % imt, fontsize=constants.AXIS_FONTSIZE)
    axes.set_ylabel("Annual Probability of Exceedance", fontsize=constants.AXIS_FONTSIZE)
    axes.tick_params(axis="both", which="major", labelsize=constants.TICK_FONTSIZE)
    axes.grid(color=constants.GRID_COLOR)

    return line_handles
