from typing import TYPE_CHECKING
import nzshm_hazlab.plot.constants as constants
import copy

if TYPE_CHECKING:
    from nzshm_hazlab.data import HazardCurves
    from nzshm_common import CodedLocation
    from matplotlib.axes import Axes

def plot_hazard_curve(
    axes: 'Axes',
    data: 'HazardCurves',
    hazard_model_id: str,
    location: 'CodedLocation',
    imt: str,
    vs30: int,
    aggs: list[str],
    **kwargs, # color, linestyle, label, etc
):

    kwargs_plot = copy.copy(kwargs)
    color = kwargs_plot.pop('color', None)
    color = color if color else constants.DEFAULT_COLOR

    # if odd number of aggs, plot the centre as a thick line, plot outer ones as faint lines
    i_center = int(len(aggs)/2)
    if len(aggs) % 2 == 1:
        levels, probs = data.get_hcurve(hazard_model_id, imt, location, aggs[i_center], vs30)
        axes.plot(levels, probs, lw=constants.LINE_WIDTH_CENTER, color=color)

    filled = False
    for i in range(i_center - 1):
        levels_low, probs_low = data.get_hcurve(hazard_model_id, imt, location, aggs[i], vs30)
        levels_high, probs_high = data.get_hcurve(hazard_model_id, imt, location, aggs[i_center + 1], vs30)
        axes.plot(levels_low, probs_low, lw=constants.LINE_WIDTH_BOUNDS, color=color)
        axes.plot(levels_high, probs_high, lw=constants.LINE_WIDTH_BOUNDS, color=color)

        if not filled:
            axes.fill_between(levels_low, probs_low, probs_high, alpha=constants.FILL_ALPHA, color=color)
            filled = True

    axes.set_xlabel('Shaking Intensity, %s [g]'%imt, fontsize=constants.AXIS_FONTSIZE)
    axes.set_ylabel('Annual Probability of Exceedance', fontsize=constants.AXIS_FONTSIZE)
    axes.tick_params(axis='both', which='major', labelsize=constants.TICK_FONTSIZE)
    axes.grid(color=constants.GRID_COLOR)

