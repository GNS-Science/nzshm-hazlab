"""This module provides functions for plotting hazard maps."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal, Optional, get_args

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from nzshm_common.grids import get_location_grid

if TYPE_CHECKING:
    import numpy.typing as npt
    from cartopy.mpl.geoaxes import GeoAxes
    from matplotlib.figure import Figure
    from nzshm_common import CodedLocation
    from toshi_hazard_store.model import ProbabilityEnum

    from nzshm_hazlab.data import HazardGrids


def _get_2d_grid(
    locations: list['CodedLocation'], imtls: 'npt.NDArray'
) -> tuple['npt.NDArray', 'npt.NDArray', 'npt.NDArray']:
    lons = [loc.lon for loc in locations]
    lats = [loc.lat for loc in locations]
    df = pd.DataFrame({'lat': lats, 'lon': lons, 'imtl': imtls}).pivot(index='lat', columns='lon', values='imtl')
    IMTL = df.values
    LON, LAT = np.meshgrid(df.columns.to_numpy(), df.index.to_numpy())
    return LON, LAT, IMTL


def plot_hazard_map(
    hazard_grids: 'HazardGrids',
    hazard_model_id: str,
    grid_name: str,
    imt: str,
    vs30: int,
    poe: 'ProbabilityEnum',
    agg: str,
    cmap: str = 'inferno',
    clim: Optional[list[float]] = None,
    ll_lim: Optional[list[float]] = None,
) -> tuple['Figure', 'GeoAxes']:
    """Create a hazard map.

    This function will plot the hazard level (imtl) at a particular probability for all locations in a grid
    of geographic points.

    Args:
        hazard_grids: The HazardGrids object that retrieves/stores the hazard data.
        hazard_model_id: The identifier of the hazard model. Specific use will depend on the DataLoader type.
        imt: The intesity measure type (e.g. "PGA", "SA(1.0)").
        grid_name: A grid name from nzshm_common. Use nzshm_common.grids.get_location_grid_names() to find a
            list of valid grid names.
        vs30: The vs30 of the sites.
        poe: Probability of exceedance
        agg: The statistical aggregate curve (e.g. "mean", "0.1") where fractions represent fractile curves.
        cmap: The colormap. See the matplotlib documentation on available colormaps.
        clim: The limits of the color map. Default is [0, max(imtl)].
        ll_lim: The longitude and latitude plot limtis. Default is [165, 180, -48, -34].

    Returns:
        Tuple of figure and axes objects on which the plot is created.
    """
    locations = get_location_grid(grid_name)
    imtls = hazard_grids.get_grid(hazard_model_id, imt, grid_name, vs30, poe, agg)
    LON, LAT, IMTL = _get_2d_grid(locations, imtls)
    if clim is None:
        clim = [0.0, imtls.max()]

    if ll_lim is None:
        ll_lim = [165, 180, -48, -34]
    return plot_grid_map(LON, LAT, IMTL, cmap, clim, ll_lim)


Diff = Literal['sub', 'ratio']


def plot_hazard_diff_map(
    hazard_grids: Sequence['HazardGrids'],
    hazard_model_ids: Sequence[str],
    grid_name: str,
    imts: Sequence[str],
    vs30s: Sequence[int],
    poes: Sequence['ProbabilityEnum'],
    aggs: Sequence[str],
    diff_type: Diff,
    cmap: str = 'inferno',
    clim: Optional[list[float]] = None,
    ll_lim: Optional[list[float]] = None,
) -> tuple['Figure', 'GeoAxes']:
    """Create a hazard difference map.

    This function will plot the difference or ratio of hazard levels (imtl). The map will be the ratio of the
    1st to the 0th or difference between the 1st and the 0th elements of the arguments passed. The 0th grid is
    retrieved using the 0th element of the Sequence type arguments and the 1st grid is retrieved using the 1st element.

    Args:
        hazard_grids: The HazardGrids objects that retrieves/stores the hazard data.
        hazard_model_ids: The identifiers of the hazard model. Specific use will depend on the DataLoader type.
        imts: The intesity measure types (e.g. "PGA", "SA(1.0)").
        grid_name: A grid name from nzshm_common. Use nzshm_common.grids.get_location_grid_names() to find a
            list of valid grid names.
        vs30s: The vs30s of the sites.
        poes: Probabilities of exceedance
        aggs: The statistical aggregate curves (e.g. "mean", "0.1") where fractions represent fractile curves.
        diff_type: Plot the difference ("sub") or ratio ("ratio") of the hazard grids.
        cmap: The colormap. See the matplotlib documentation on available colormaps.
        clim: The limits of the color map. Default is [0, max(imtl)].
        ll_lim: The longitude and latitude plot limtis. Default is [165, 180, -48, -34].

    Returns:
        Tuple of figure and axes objects on which the plot is created.
    """
    if diff_type not in get_args(Diff):
        raise ValueError(f"diff type must be one of {get_args(Diff)}")

    locations = get_location_grid(grid_name)

    imtls: list['npt.NDArray'] = []
    for hg, hmid, imt, vs30, poe, agg in zip(hazard_grids, hazard_model_ids, imts, vs30s, poes, aggs):
        imtls.append(hg.get_grid(hmid, imt, grid_name, vs30, poe, agg))
    if len(imtls) != 2:
        raise ValueError("Must specify two hazard grids to plot.")

    imtl_diff = imtls[1] - imtls[0] if diff_type == 'sub' else imtls[1] / imtls[0]
    LON, LAT, IMTL = _get_2d_grid(locations, imtl_diff)

    if clim is None:
        maxabs = abs(imtl_diff).max()
        if diff_type == 'sub':
            clim = [-maxabs, maxabs]
        else:
            clim = [0, maxabs]

    if ll_lim is None:
        ll_lim = [165, 180, -48, -34]
    return plot_grid_map(LON, LAT, IMTL, cmap, clim, ll_lim)


def plot_grid_map(
    lon: 'npt.NDArray',
    lat: 'npt.NDArray',
    data: 'npt.NDArray',
    cmap: str,
    clim: list[float],
    ll_lim: list[float],
) -> tuple['Figure', 'GeoAxes']:
    """Low level function for plotting grid data on a map.

    This function is used by the higher level hazard map plotting functions.

    Args:
        lon: Array of longitudes.
        lat: Array of latitudes.
        data: Array of data to plot as color.
        cmap: The name of the colormap to use.
        clim: The limits of the colormap.
        ll_lim: The longitude and latitude limits, e.g. [165, 180, -48, -34]

    Returns:
        Tuple of figure and axes objects on which the plot is created.
    """
    coastline_resolution = '50m'

    fig = plt.figure()
    ax: 'GeoAxes' = fig.add_subplot(projection=ccrs.TransverseMercator(central_latitude=0.0, central_longitude=173.0))
    ax.set_extent(ll_lim, crs=ccrs.PlateCarree())

    # zorder is used to make the oceans clip the pcolormesh plot
    zorder = 10
    mesh = ax.pcolormesh(
        lon, lat, data, transform=ccrs.PlateCarree(), vmin=clim[0], vmax=clim[1], cmap=cmap, zorder=zorder
    )
    zorder += 1
    ax.add_feature(
        cfeature.NaturalEarthFeature("physical", "ocean", coastline_resolution), color='aliceblue', zorder=zorder
    )
    zorder += 1
    ax.coastlines(resolution=coastline_resolution, zorder=zorder)
    zorder += 1
    ax.add_feature(cfeature.BORDERS, linewidth=2, zorder=zorder)
    zorder += 1
    ax.gridlines(draw_labels=["bottom", "left"], xlocs=list(range(165, 185, 5)), zorder=zorder)
    zorder += 1
    cax = ax.inset_axes([0.6, 0.1, 0.35, 0.07], zorder=zorder)
    tick_multiple = round((clim[1] - clim[0]) / 3, 1)
    fig.colorbar(mesh, cax=cax, orientation='horizontal', ticks=ticker.MultipleLocator(tick_multiple))
    return fig, ax
