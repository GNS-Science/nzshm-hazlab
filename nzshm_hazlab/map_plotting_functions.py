from typing import List
from math import log10

import pygmt
import xarray as xr
import geopandas as gp

from xarray.core.dataarray import DataArray
from shapely.geometry import Polygon

from nzshm_hazlab.store.levels import get_hazard_at_poe


def get_poe_grid(hazard_id, imt, agg, poe, vs30):

    haz_poe = get_hazard_at_poe(hazard_id, imt, agg, poe, vs30)
    haz_poe = haz_poe.pivot(index="lat", columns="lon")
    haz_poe = haz_poe.droplevel(0, axis=1)
    return xr.DataArray(data=haz_poe)


def load_polygons():

    faults = gp.read_file('/home/chrisdc/NSHM/DATA/Crustal_Rupture_Set_RmlsZToxMDAwODc=/fault_sections.geojson')
    ba_poly = Polygon(   [
                                (177.2, -37.715),
                                (176.2, -38.72),
                                (175.375, -39.27),
                                (174.25, -40),
                                (173.1, -39.183),
                                (171.7, -34.76),
                                (173.54, -33.22),
                                (177.2, -37.715),
                                ]
                            )
    backarc = gp.GeoSeries([ba_poly])
    hikurangi = gp.read_file('/home/chrisdc/NSHM/DATA/interface_polygons/subduction_polygon.geojson')
    puysegur = gp.read_file('/home/chrisdc/NSHM/DATA/interface_polygons/puysegur_polygon.geojson')

    return faults, backarc, hikurangi, puysegur


def plot_map(
        grid: DataArray,
        colormap,
        dpi,
        limits: List[float],
        font,
        font_annot,
        plot_width,
        legend_text,
        plot_faults=False
):

    pygmt.config(FONT_LABEL=font, FONT_ANNOT_PRIMARY=font_annot)

    projection = f'M{plot_width}c'
    region = "165/180/-48/-34"

    fig = pygmt.Figure()
            
    fig.grdimage(grid=grid, region=region, projection=projection, cmap = True, dpi = dpi, frame = "a")
    # fig.coast(shorelines = True, water="white", region=region, projection=projection, frame = "a")
    fig.coast(shorelines = True, water="white")
    # fig.basemap(frame=["a", f"+t{vs30}m/s {imt} {poe*100:.0f}% in 50 yrs"])
    fig.basemap(frame=["a"])
    if plot_faults:
        faults, backarc, hikurangi, puysegur = load_polygons()
        fig.plot(data=hikurangi,fill="220/220/220",transparency=60,pen="black")
        fig.plot(data=puysegur,fill="220/220/220",transparency=60,pen="black")
        fig.plot(data=faults)
        # fig.plot(data=backarc, pen="1p,red")
        # filepath = Path(full_dir,f'{hazard_model["id"]}-{vs30}-{imt}-{poe}_faults.{filetype}')
        # filepath = Path(full_dir,f'{hazard_model["id"]}-{vs30}-{imt}-{poe}.{filetype}')
            
    # fig.colorbar(xshift='40c', yshift='10c', position='+w27c/3c+h', frame=f'af+l"{imt} ({poe*100:.0f}% PoE in 50)"')#,position='+ef')
    fig.colorbar(frame=f'af+l"{legend_text}"')
            
    # fig.savefig(filepath)
    fig.show()

    return fig


def plot_hazard_map(
        grid: DataArray,
        colormap,
        dpi,
        limits: List[float],
        font,
        font_annot,
        plot_width,
        legend_text,
        plot_faults=False
):

    pygmt.makecpt(cmap = colormap, log=True, series=[log10(limits[0]), log10(limits[1]), 0.1])
    return plot_map(grid, colormap, dpi, limits, font, font_annot, plot_width, legend_text, plot_faults)


def plot_hazard_diff_map(
        grid1: DataArray,
        grid2: DataArray,
        diff_type,
        colormap,
        dpi,
        limits: List[float],
        font,
        font_annot,
        plot_width,
        legend_text,
        plot_faults=False
):

    if diff_type == 'sub':
        dgrid = grid1 - grid2
        pygmt.makecpt(cmap = "blue,white,red", series=f"{limits[0]}, 0, {limits[1]}", continuous=True)
    elif diff_type == 'ratio':
        dgrid = grid1/grid2
        pygmt.makecpt(cmap = "blue,white,red", series=f"{-1}, 0, {1}", continuous=True)
    else:
        raise Exception('diff type %s not recognized' % diff_type)

    return plot_hazard_map(dgrid, colormap, dpi, limits, font, font_annot, plot_width, legend_text, plot_faults)  
    