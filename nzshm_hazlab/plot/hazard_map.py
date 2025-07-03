from typing import TYPE_CHECKING, Optional, Literal, get_args
from collections.abc import Sequence
import pandas as pd
from nzshm_common.grids import get_location_grid
import numpy as np
import cartopy.feature as cfeature
import matplotlib.ticker as ticker


import cartopy.crs as ccrs
import matplotlib.pyplot as plt


if TYPE_CHECKING:
    from nzshm_hazlab.data import HazardGrids
    from toshi_hazard_store.model import ProbabilityEnum
    from nzshm_common import CodedLocation
    import numpy.typing as npt
    from cartopy.mpl.geoaxes import GeoAxes
    from matplotlib.figure import Figure


def get_2d_grid(
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
    locations = get_location_grid(grid_name)
    imtls = hazard_grids.get_grid(hazard_model_id, imt, grid_name, vs30, poe, agg)
    LON, LAT, IMTL = get_2d_grid(locations, imtls)
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

    if diff_type not in get_args(Diff):
        raise ValueError(f"diff type must be one of {get_args(Diff)}")

    locations = get_location_grid(grid_name)

    imtls: list['npt.NDArray'] = []
    for hg, hmid, imt, vs30, poe, agg in zip(hazard_grids, hazard_model_ids, imts, vs30s, poes, aggs):
        imtls.append(hg.get_grid(hmid, imt, grid_name, vs30, poe, agg))
    if len(imtls) != 2:
        raise ValueError("Must specify two hazard grids to plot.")


    imtl_diff = imtls[1] - imtls[0] if diff_type == 'sub' else imtls[1] / imtls[0]
    LON, LAT, IMTL = get_2d_grid(locations, imtl_diff)

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
    tick_multiple = round((clim[1] - clim[0])/3, 1)
    fig.colorbar(mesh, cax=cax, orientation='horizontal', ticks=ticker.MultipleLocator(tick_multiple))
    return fig, ax


# def plot_hazard_map_plotly(
#     hazard_grids: 'HazardGrids',
#     hazard_model_id: str,
#     grid_name: str,
#     imt: str,
#     vs30: int,
#     poe: 'ProbabilityEnum',
#     agg: str,
#     clim: Optional[list[float]] = None,
#     clip: bool = True,
# ):
#     locations = get_location_grid(grid_name)
#     imtls = hazard_grids.get_grid(hazard_model_id, imt, grid_name, vs30, poe, agg)
#     lons = [loc.lon for loc in locations]
#     lats = [loc.lat for loc in locations]
#     df = pd.DataFrame({'lat': lats, 'lon': lons, 'imtl': imtls})

#     # fig = px.density_map(df, lat='lat', lon='lon', z='imtl', radius=10,
#     #                     center=dict(lat=0, lon=180), zoom=0,
#     #                     map_style="open-street-map")
#     fig = px.scatter_map(df, lat='lat', lon='lon', color='imtl')
#     return fig
