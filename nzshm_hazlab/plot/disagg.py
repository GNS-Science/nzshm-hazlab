"""This module provides functions for plotting disaggregations."""

import copy
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

import numpy as np
from matplotlib import cm
from matplotlib.colors import ListedColormap

from nzshm_hazlab.plot.constants import DEFAULT_CMAP

if TYPE_CHECKING:
    import numpy.typing as npt
    from matplotlib.axes import Axes
    from nzshm_common import CodedLocation
    from toshi_hazard_store.model import ProbabilityEnum

    from nzshm_hazlab.data import Disaggregations


def _cmap():
    cmp = cm.get_cmap(DEFAULT_CMAP)
    white = np.array([1.0, 1.0, 1.0, 1.0])
    newcolors = cmp(np.linspace(0, 1, 256))
    newcolors[:5, :] = white
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
) -> 'Axes':
    bins, probs = disaggs.get_disaggregation(hazard_model_id, [dimension], imt, location, vs30, poe, agg)
    axes.bar(bins[dimension], probs, **kwargs)
    return axes


def _plot_2d(
    ax: 'Axes', dimensions: list[str], bins: dict[str, 'npt.NDArray'], probs: 'npt.NDArray', **kwargs: Any
) -> None:

    # put the probabilties axes in the correct order
    if dimensions[0] != list(bins.keys())[0]:
        z = probs
    else:
        z = probs.transpose()
    x, y = np.meshgrid(bins[dimensions[0]], bins[dimensions[1]])
    ax.pcolormesh(x, y, z, shading='auto', **kwargs)


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
    split_by_trt: bool = False,
    **kwargs: Any,
) -> tuple['Axes', ...]:
    if len(dimensions) != 2:
        raise ValueError("dimensions must have length of 2")
    if kwargs.get('shading'):
        raise KeyError("Cannot specify shading as a keyword argument.")

    keyword_args = kwargs.copy()
    if not keyword_args.get('cmap'):
        keyword_args['cmap'] = _cmap()

    # we don't want to have trt in the requested dimensions, as it can't
    # be plotted on as an axis on a 2d plot, so remove it
    dimensions_copy = copy.copy(dimensions)
    if 'trt' in dimensions_copy:
        dimensions_copy.pop(dimensions_copy.index('trt'))

    # but if we split by trt, we have to include it in the disaggregations
    dims = dimensions_copy + ['trt'] if split_by_trt else dimensions_copy
    bins, probs = disaggs.get_disaggregation(hazard_model_id, dims, imt, location, vs30, poe, agg)
    if split_by_trt:
        dim_trt = list(bins.keys()).index('trt')
        trts = bins.pop('trt')
        # move the trt axis to be first for easy indexing
        probs = np.moveaxis(probs, dim_trt, 0)
        qms = []
        axs = _split_axes(axes, len(trts))
        for i, trt in enumerate(trts):
            qms.append(_plot_2d(axs[i], dimensions_copy, bins, probs[i, ...], **keyword_args))
            axs[i].set_title(trt)
        return tuple(axs)

    _plot_2d(axes, dimensions_copy, bins, probs, **keyword_args)
    return (axes,)


def _split_axes(axes: 'Axes', n: int) -> list['Axes']:

    fig = axes.get_figure()
    pos = axes.get_position()
    axes.remove()

    gs = fig.add_gridspec(nrows=1, ncols=n)

    fig.subplots_adjust(left=pos.x0, right=pos.x1, bottom=pos.y0, top=pos.y1, wspace=0.05)

    axs = []
    for i in range(n):
        if i == 0:
            axs.append(fig.add_subplot(gs[i]))
        else:
            axs.append(fig.add_subplot(gs[i], sharey=axs[0]))

    return axs


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
    split_by_trt: bool = False,
    **kwargs: Any,
):
    pass
