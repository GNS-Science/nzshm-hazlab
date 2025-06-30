"""This module provides functions for plotting disaggregations."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Optional, Union, cast

import matplotlib
import numpy as np
from matplotlib import cm
from matplotlib.axes import Axes
from matplotlib.colors import LightSource, ListedColormap, Normalize
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.axes3d import Axes3D

from nzshm_hazlab.base_functions import prob_to_rate
from nzshm_hazlab.plot.constants import DEFAULT_CMAP

if TYPE_CHECKING:
    import numpy.typing as npt
    from matplotlib.collections import QuadMesh
    from nzshm_common import CodedLocation
    from toshi_hazard_store.model import ProbabilityEnum

    from nzshm_hazlab.data import Disaggregations


def _cmap():
    cmp = matplotlib.colormaps.get_cmap(DEFAULT_CMAP)
    white = np.array([1.0, 1.0, 1.0, 1.0])
    newcolors = cmp(np.linspace(0, 1, 256))
    newcolors[:5, :] = white
    return ListedColormap(newcolors)


def plot_disagg_1d(
    axes: 'Axes',
    data: 'Disaggregations',
    hazard_model_id: str,
    location: 'CodedLocation',
    imt: str,
    vs30: int,
    poe: 'ProbabilityEnum',
    agg: str,
    dimension: str,
    **kwargs: Any,
) -> 'Axes':
    """Make a bar plot of percent contribution to hazard along a given dimension.

    Args:
        axes: Axes on which to create the bar plot.
        data: The disaggregation data.
        hazard_model_id: The d of the hazard model to plot.
        location: The site location.
        imt: The intensity measure type to plot (e.g. "PGA", SA(1.0)")
        vs30: The site vs30 to plot.
        poe: The probabilty of exceedance on the mean hazard curve at which the disggregation is calcualted.
        agg: The aggregate statistic (e.g. 'mean' would plot the mean disaggregation and '0.5' would plot the
            median disaggregation)
        dimension: The disaggregation dimension (also known as the projection) to plot as the independent variable.
        kwargs: Any additional arguments to pass to the matplotlib plot function.

    Returns:
        The axes on which the bar plot was created.
    """
    bins, probs = data.get_disaggregation(hazard_model_id, [dimension], imt, location, vs30, poe, agg)
    rates_pct = prob_to_rate(probs, 1.0) / np.sum(probs) * 100
    axes.bar(bins[dimension], rates_pct, **kwargs)
    return axes


def _plot_2d(
    ax: 'Axes',
    dimensions: list[str],
    bins: dict[str, 'npt.NDArray'],
    probs: 'npt.NDArray',
    pct_lim: list[float],
    **kwargs: Any,
) -> 'QuadMesh':

    # put the probabilties axes in the correct order
    if dimensions[0] != list(bins.keys())[0]:
        z = probs
    else:
        z = probs.transpose()
    x, y = np.meshgrid(bins[dimensions[0]], bins[dimensions[1]])
    return ax.pcolormesh(x, y, z, shading='nearest', vmin=pct_lim[0], vmax=pct_lim[1], **kwargs)


def plot_disagg_2d(
    axes: Union['Axes', Sequence['Axes']],
    data: 'Disaggregations',
    hazard_model_id: str,
    location: 'CodedLocation',
    imt: str,
    vs30: int,
    poe: 'ProbabilityEnum',
    agg: str,
    dimensions: list[str],
    pct_lim: Optional[list[float]] = None,
    split_by_trt: bool = False,
    **kwargs: Any,
) -> tuple['Axes', ...]:
    """Make a 2D pseudocolor plot of percent contribution to hazard along two dimensions.

    Args:
        axes: Axes on which to create the bar plot. If split_by_trt is true, this must be a list of Axes objects
            with the number of elements equal to the number of tectonic tregion types.
        data: The disaggregation data.
        hazard_model_id: The d of the hazard model to plot.
        location: The site location.
        imt: The intensity measure type to plot (e.g. "PGA", SA(1.0)")
        vs30: The site vs30 to plot.
        poe: The probabilty of exceedance on the mean hazard curve at which the disggregation is calcualted.
        agg: The aggregate statistic (e.g. 'mean' would plot the mean disaggregation and '0.5' would plot
            the median disaggregation)
        dimensions: The disaggregation dimensions (also known as the projection) to use.
        pct_lim: The percent contribution limits for the colormap. Colormap will autoscale if not given.
        split_by_trt: If True, split the plots into seperate TRT (tectonic retion type) plots.
        kwargs: Any additional arguments to pass to the matplotlib plot function.

    Returns:
        Tuple of axes on which the plot(s) were created.

    Raises:
        ValueError: If demensions does not have len 2.
        ValueError: If pct_lim does not have len 2.
        ValueError: If split_by_trt and len(axes) does not match the number of TRTs
        TypeError: If split_by_trt and axes is not a Sequence.
        KeyError: If shading is given as a keword argument. Shading is always set to 'nearest'.
    """
    if len(dimensions) != 2:
        raise ValueError("Dimensions must have length of 2.")
    if 'trt' in dimensions:
        raise ValueError("Cannot specify trt as a dimension for 2d disaggregatin plot.")
    if kwargs.get('shading'):
        raise KeyError("Cannot specify shading as a keyword argument.")

    keyword_args = kwargs.copy()
    if not keyword_args.get('cmap'):
        keyword_args['cmap'] = _cmap()

    # if we split by trt, we have to include it in the retrieved disaggregations
    dims = dimensions + ['trt'] if split_by_trt else dimensions
    bins, probs = data.get_disaggregation(hazard_model_id, dims, imt, location, vs30, poe, agg)
    rates_pct = prob_to_rate(probs, 1.0) / np.sum(probs)

    # set the limits of the colormap
    if pct_lim is None:
        pct_lim = [0.0, rates_pct.max()]
    elif len(pct_lim) != 2:
        raise ValueError("pct_lim must have length of 2")

    if split_by_trt:
        if not isinstance(axes, (Sequence, np.ndarray)):
            raise TypeError("If split_by_trt is True, axes must be a sequence of Axes objects.")
        if len(axes) != len(bins['trt']):
            raise ValueError(
                "axes sequence must have the same number of elements as there are tectonic region types. "
                f"Number of TRTs {len(bins['trt'])}, length of axes {len(axes)}."
            )

        dim_trt = list(bins.keys()).index('trt')
        trts = bins.pop('trt')
        # move the trt axis to be first for easy indexing
        rates_pct = np.moveaxis(rates_pct, dim_trt, 0)
        for i, trt in enumerate(trts):
            pcx = _plot_2d(axes[i], dimensions, bins, rates_pct[i, ...], pct_lim, **keyword_args)
            axes[i].set_title(trt)
        fig = cast(Figure, axes[-1].get_figure())
        fig.colorbar(pcx, ax=axes[-1], label="% Contribution to Hazard")
        return tuple(axes)
    else:
        axes = cast(Axes, axes)

    pcx = _plot_2d(axes, dimensions, bins, rates_pct, pct_lim, **keyword_args)
    fig = cast(Figure, axes.get_figure())
    fig.colorbar(pcx, label="% Contribution to Hazard")
    return (axes,)


def plot_disagg_3d(
    fig: 'Figure',
    data: 'Disaggregations',
    hazard_model_id: str,
    location: 'CodedLocation',
    imt: str,
    vs30: int,
    poe: 'ProbabilityEnum',
    agg: str,
    dist_lim: Optional[list[float]] = None,
    mag_lim: Optional[list[float]] = None,
) -> 'Axes':
    """Make a 3D bar plot of percent contribution to hazard.

    The disaggregation will be plotted as a function of distance and magnitude colored by epislon.

    Args:
        fig: Figure on which to create the bar plot.
        data: The disaggregation data.
        hazard_model_id: The d of the hazard model to plot.
        location: The site location.
        imt: The intensity measure type to plot (e.g. "PGA", SA(1.0)")
        vs30: The site vs30 to plot.
        poe: The probabilty of exceedance on the mean hazard curve at which the disggregation is calcualted.
        agg: The aggregate statistic (e.g. 'mean' would plot the mean disaggregation and '0.5' would plot
            the median disaggregation)
        dist_lim: The distance plot limits.
        mag_lim: The magnitude plot limits.

    Returns:
        The axes on which the plot was created.
    """
    if dist_lim is None:
        dist_lim = [0, 350]
    if mag_lim is None:
        mag_lim = [5, 10]

    ax = cast(Axes3D, fig.add_subplot(1, 1, 1, projection='3d'))

    # calculate percent contribution to hazard
    bins, probs = data.get_disaggregation(hazard_model_id, ['mag', 'dist', 'eps'], imt, location, vs30, poe, agg)
    rates_pct = prob_to_rate(probs, 1.0) / np.sum(probs) * 100

    # construct light source and colormap
    ls = LightSource(azdeg=45, altdeg=10)
    cmp = matplotlib.colormaps.get_cmap('coolwarm')
    newcolors = cmp(np.linspace(0, 1, len(bins['eps'])))
    newcmp = ListedColormap(newcolors)
    norm = Normalize(vmin=-4, vmax=4)

    # move epsilon axis to last for easy indexing later
    dim_eps = list(bins.keys()).index('eps')
    rates_pct = np.moveaxis(rates_pct, dim_eps, -1)

    dind = bins['dist'] <= dist_lim[1]
    rates_pct = rates_pct[:, dind, :]
    dists = bins['dist'][dind]
    _xx, _yy = np.meshgrid(bins['mag'], dists)
    x, y = _xx.T.ravel(), _yy.T.ravel()
    width = 0.1
    depth = (dist_lim[1] - dist_lim[0]) / (mag_lim[1] - mag_lim[0]) * width

    bottom = np.zeros(x.shape)
    for i in range(len(bins['eps'])):
        z0 = bottom
        z1 = rates_pct[:, :, i].ravel()
        ind = z1 > 0.1
        if any(ind):
            ax.bar3d(x[ind], y[ind], z0[ind], width, depth, z1[ind], color=newcolors[i], lightsource=ls, alpha=1.0)
            bottom += rates_pct[:, :, i].ravel()

    deps = bins['eps'][1] - bins['eps'][0]
    fig.colorbar(
        cm.ScalarMappable(norm=norm, cmap=newcmp),
        ax=ax,
        ticks=(list(bins['eps'] - deps / 2) + [bins['eps'][-1] + deps / 2])[0:-1:2] + [bins['eps'][-1] + deps / 2],
        shrink=0.3,
        anchor=(0.0, 0.75),
        label='epsilon',
    )
    ax.set_xlim(mag_lim)
    ax.set_ylim(dist_lim)
    ax.view_init(elev=35, azim=45)

    return ax
