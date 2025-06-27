"""This module provides functions for plotting disaggregations."""

from typing import TYPE_CHECKING, Any
from collections.abc import Sequence
import matplotlib.collections
import matplotlib.container
import numpy as np
from matplotlib.colors import ListedColormap
from nzshm_hazlab.plot.constants import DEFAULT_CMAP
from matplotlib import cm
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable

if TYPE_CHECKING:
    import matplotlib
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from nzshm_common import CodedLocation
    from nzshm_hazlab.data import Disaggregations
    from toshi_hazard_store.model import ProbabilityEnum

def _cmap():
    cmp = cm.get_cmap(DEFAULT_CMAP)
    white = np.array([1.0, 1.0, 1.0, 1.0])
    newcolors = cmp(np.linspace(0,1,256))
    newcolors[:5,:] = white
    return ListedColormap(newcolors)

def plot_disagg_1d(
    axes: 'Axes',
    disaggs: 'Disaggregations',
    hazard_model_id: str,
    location: 'CodedLocation',
    imt: str,
    vs30: int,
    poe: 'ProbabilityEnum',
    agg: str,
    dimension: str,
    **kwargs: Any, 
) -> 'matplotlib.container.BarContainer':
    bins, probs = disaggs.get_disaggregation(hazard_model_id, [dimension], imt, location, vs30, poe, agg)
    return axes.bar(bins[dimension], probs, **kwargs)


def plot_disagg_2d(
    axes: 'Axes',
    disaggs: 'Disaggregations',
    hazard_model_id: str,
    location: 'CodedLocation',
    imt: str,
    vs30: int,
    poe: 'ProbabilityEnum',
    agg: str,
    dimensions: Sequence[str],
    split_by_trt: bool=False,
    **kwargs: Any, 
) -> tuple['matplotlib.collections.QuadMesh', ...]:
    if len(dimensions) != 2:
        raise ValueError("dimensions must have length of 2")
    if kwargs.get('shading'):
        raise KeyError("Cannot specify shading as a keyword argument.")

    keyword_args = kwargs.copy()
    if not keyword_args.get('cmap'):
        keyword_args['cmap'] = _cmap()

    # we don't want to have trt in the requested dimensions, as it can't be plotted on as an axis on a 2d plot, so remove it
    # TODO: make a copy of dimensions
    if 'trt' in dimensions:
        dimensions.pop(dimensions.index('trt'))
    
    # but if we split by trt, we have to include it in the disaggregations
    # dims = dimensions + ['trt'] if split_by_trt else dimensions
    dims = dimensions
    bins, probs = disaggs.get_disaggregation(hazard_model_id, dims, imt, location, vs30, poe, agg)
    # dim_trt = list(bins.keys()).find('trt')

    # put the probabilties axes in the correct order
    if dimensions[0] != list(bins.keys())[0]:
        z = probs
    else:
        z = probs.transpose()
    x, y = np.meshgrid(bins[dimensions[0]], bins[dimensions[1]])

    if split_by_trt:
        qms = []
        divider = make_axes_locatable(axes)
        ax1 = divider.append_axes("left", size="100%", pad=0.1, sharey=axes)
        ax3 = divider.append_axes("right", size="100%", pad=0.1, sharey=axes)
        qms.append(ax1.pcolormesh(x, y, z, shading='auto', **keyword_args))
        qms.append(ax3.pcolormesh(x, y, z, shading='auto', **keyword_args))
        qms.append(axes.pcolormesh(x, y, z, shading='auto', **keyword_args))
        return tuple(qms)
    
    return (axes.pcolormesh(x, y, z, shading='auto', **keyword_args), )

def plot_disagg_3d(
    axes: 'Axes',
    disaggs: 'Disaggregations',
    hazard_model_id: str,
    location: 'CodedLocation',
    imt: str,
    vs30: int,
    poe: 'ProbabilityEnum',
    agg: str,
    dimensions: Sequence[str],
    split_by_trt: bool=False,
    **kwargs: Any, 
):
    pass