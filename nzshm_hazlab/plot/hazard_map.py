from typing import TYPE_CHECKING, Optional
import pandas as pd
from nzshm_common.grids import get_location_grid
import numpy as np
import cartopy.feature as cfeature
from cartopy.mpl.patch import geos_to_path
import matplotlib.path as mpath
import matplotlib.ticker as ticker


import cartopy.crs as ccrs
import matplotlib.pyplot as plt


if TYPE_CHECKING:
    from nzshm_hazlab.data import HazardGrids
    from toshi_hazard_store.model import ProbabilityEnum

def plot_hazard_map(hazard_grids: 'HazardGrids', hazard_model_id: str, grid_name: str, imt: str, vs30: int, poe: 'ProbabilityEnum', agg: str, clim: Optional[list[float]] = None, clip: bool=True):
    fig = plt.figure()
    ax = fig.add_subplot(projection=ccrs.TransverseMercator(central_latitude=0.0, central_longitude=173.0))
    ax.set_extent([165, 180, -48, -34], crs=ccrs.PlateCarree())

    locations = get_location_grid(grid_name)
    lons = [loc.lon for loc in locations]
    lats = [loc.lat for loc in locations]
    imtls = hazard_grids.get_grid(hazard_model_id, imt, grid_name, vs30, poe, agg)

    df = pd.DataFrame({'lat':lats, 'lon':lons, 'imtl':imtls})\
        .pivot(index='lat', columns='lon', values='imtl')
    IMTL = df.values
    LON, LAT = np.meshgrid(df.columns.to_numpy(), df.index.to_numpy())

    if clim is None:
        clim = [0.0, np.nanmax(IMTL)]

    # zorder is used to make the oceans clip the pcolormesh plot
    print(clim)
    mesh = ax.pcolormesh(LON, LAT, IMTL, transform=ccrs.PlateCarree(), vmin=clim[0], vmax=clim[1], cmap='inferno', zorder=10)

    if clip:
        ax.add_feature(cfeature.NaturalEarthFeature("physical", "ocean", "50m"), zorder=12)
        ax.add_feature(cfeature.BORDERS, linewidth=0.5)

    cax = ax.inset_axes([0.6, 0.1, 0.35, 0.07])
    cbar = fig.colorbar(mesh, cax=cax, orientation='horizontal', ticks=ticker.MultipleLocator(0.5))