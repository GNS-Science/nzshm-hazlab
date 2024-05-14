from typing import List
from math import log10
from pathlib import Path

import pygmt
import xarray as xr
import geopandas as gp

from xarray.core.dataarray import DataArray
from shapely.geometry import Polygon

from nzshm_common.location.location import location_by_id

from nzshm_hazlab.store.levels import get_hazard_at_poe
from nzshm_hazlab.data_functions import compute_hazard_at_poe

CPT_FILEPATH = Path('/tmp/tmp.cpt')

def clear_cpt():
    if CPT_FILEPATH.exists():
        CPT_FILEPATH.unlink()


def get_poe_grid(hazard_id, vs30, imt, agg, poe):

    haz_poe = get_hazard_at_poe(hazard_id, vs30, imt, agg, poe)
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

def load_trench_traces():
    coordinates_puys_left = [(163.995385286755749, -49.746055874119982 ), (163.737227866180717, -49.805821909874098), (163.562871413941537, -49.746056443094503), 
                    (163.71471876861159, -49.498891812758721 ), (163.858876465872726, -49.248349702508129 ), 
                    (163.931618297428429, -49.116363820497398), (164.004717364693306, -48.991042542835409), (164.355221015898451, -48.201286993498577), 
                        (164.390606971552558, -48.06027862150767), (164.425883105610438, -47.928102942464221), (164.474435458806596, -47.788680698809074), 
                        (164.871420336603308, -47.004764467549208), (164.920599509941923, -46.874701032660781), (165.078005264006691, -46.467114041939681), 
                        (165.129881884909707, -46.33760807649945), (165.216673178887277, -46.212006391502122), (165.328698339601488, -46.089471033126728), 
                        (165.460722247056282, -45.977679224703607), (165.622539324087654, -45.882273168397056), [ 166.236314812944158, -45.504115349644053 ], 
                        (166.385481683046322, -45.40811821136834), (167.082936434616897, -44.905887184335), (167.566419451572926, -44.627818801382475), 
                        (167.737067161616494, -44.538498286479388), (168.093943444516441, -44.368542578921023),]

    top_coordinates_hik = [( 179.991039006565757, -37.618044370211265), (179.767148228042657, -37.820100908104664), (179.163878548233839, -38.471805866839674),
                                (179.078511016805379, -38.727862268658619), (178.860521544240072, -39.469542889766601), 
                        (178.674169289399771, -39.776185668185832), (178.12595313797763, -40.72679653260148), (177.9770537347098, -40.97201052721168),
    (177.6882672514525, -41.285500279933636), (177.12562255010698, -41.63504081754063), (176.6857683947839, -41.791493039083534), 
                        (176.10417871996057, -41.95910793449036), (175.06702224524022, -42.36389784132952),(174.06702224524022, -42.8389784132952),]
    
    return top_coordinates_hik, coordinates_puys_left


def plot_map(
        grid: DataArray,
        dpi,
        font,
        font_annot,
        plot_width,
        legend_text,
        region = None,
        plot_cities=None,
        plot_faults=False,
        plot_trenches=False,
        contours=None,
        text='',
):

    pygmt.config(FONT_LABEL=font, FONT_ANNOT_PRIMARY=font_annot)
    # pygmt.config()

    projection = f'M{plot_width}c'
    if not region:
        region = "165/180/-48/-34"

    fig = pygmt.Figure()
    fig.basemap(frame=["WSne", "xa5f1", "ya2f1"],region=region, projection=projection )

    if grid is None:
        # fig.coast(shorelines = True, water="white", frame = "a", projection=projection, region=region)
        fig.coast(shorelines = True, water="white", projection=projection, region=region)
        faults, backarc, hikurangi, puysegur = load_polygons()
        fig.plot(data=hikurangi,fill="220/220/220",transparency=30,pen="black")
        fig.plot(data=puysegur,fill="220/220/220",transparency=30,pen="black")
        fig.plot(data=faults, pen="red")
        if text:
            fig.text(text=text["text"], x=text["x"], y=text["y"], font="10p,Helvetica-Bold")
        # fig.basemap(frame=["a"])

        if plot_cities:
            names = [location_by_id(city)['name'] for city in plot_cities] 
            lats = [location_by_id(city)['latitude'] for city in plot_cities] 
            lons = [location_by_id(city)['longitude'] for city in plot_cities] 
            lats_txt = [lat + 0.15 for lat in lats]
            lons_txt = [lon + 0.2 for lon in lons]
            fig.plot(x=lons, y=lats, style="c0.2c", fill="white", pen="black")
            fig.text(text=names, x=lons_txt, y=lats_txt, justify="BL", fill="211", font="8p", clearance="20%/20%+tO")

        fig.show()
        return fig
            
    fig.grdimage(grid=grid, region=region, projection=projection, cmap = str(CPT_FILEPATH), dpi = dpi)
    if contours:
        fig.grdcontour(grid=grid, annotation=contours['annotation'], interval=contours['interval'], label_placement=contours['label_placement'])
    fig.coast(shorelines = True, water="white", region=region, projection=projection)

    if plot_faults:
        faults, backarc, hikurangi, puysegur = load_polygons()
        fig.plot(data=hikurangi,fill="220/220/220",transparency=60,pen="black")
        fig.plot(data=puysegur,fill="220/220/220",transparency=60,pen="black")
        fig.plot(data=faults)
        # fig.plot(data=backarc, pen="1p,red")
        # filepath = Path(full_dir,f'{hazard_model["id"]}-{vs30}-{imt}-{poe}_faults.{filetype}')
        # filepath = Path(full_dir,f'{hazard_model["id"]}-{vs30}-{imt}-{poe}.{filetype}')

    if plot_trenches:
        hikurangi_trench, puysegur_trench = load_trench_traces()
        fig.plot(data=hikurangi_trench, pen="1.5p,black", fill = "black", style="f0.9c/0.2c+r+t")
        fig.plot(data=puysegur_trench, pen="1.5p,black", fill = "black", style = "f0.9c/0.2c+r+t")
    
    if plot_cities:
        names = [location_by_id(city)['name'] for city in plot_cities] 
        lats = [location_by_id(city)['latitude'] for city in plot_cities] 
        lons = [location_by_id(city)['longitude'] for city in plot_cities] 
        lats_txt = [lat + 0.15 for lat in lats]
        lons_txt = [lon + 0.2 for lon in lons]
        fig.plot(x=lons, y=lats, style="c0.2c", fill="white", pen="black")
        fig.text(text=names, x=lons_txt, y=lats_txt, justify="BL", fill="211", font="8p", clearance="20%/20%+tO")
            
    if text:
        fig.text(text=text["text"], x=text["x"], y=text["y"], font="10p,Helvetica-Bold")
    font = f'{int(int(font[:-1])*0.8)}p,Helvetica-Bold'
    font_annot = font
    pygmt.config(FONT_LABEL=font, FONT_ANNOT_PRIMARY=font_annot)
    clength = (4.5/10) * plot_width
    fig.colorbar(frame=f'af+l"{legend_text}"', position=f"n0.5/0.07+w{clength}c/6%+h+ml", )
    image_width= (3/10) * plot_width
    # position = f"g167/-35+w{image_width}c+jCM"
    position = f"n0.1/0.85/+w{image_width}c"
    imagefile = "/home/chrisdc/NSHM/DEV/nzshm-hazlab/images/NSHM_logo_blue.png"
    # imagefile = "/home/chrisdc/Downloads/gmt-logo.png"
    # fig.image(imagefile=imagefile, position=position)
    # fig.basemap(frame="a")

    # fig.savefig(filepath)
    # fig.show()

    return fig


def plot_hazard_map(
        grid: DataArray,
        colormap,
        dpi,
        climits: List[float],
        font,
        font_annot,
        plot_width,
        legend_text,
        region=None,
        plot_cities=None,
        plot_faults=False,
        plot_trenches=False,
        text='',
):

    clear_cpt()
    if grid is not None:
        pygmt.config(COLOR_NAN='white')
        pygmt.makecpt(cmap = colormap, log=True, series=[log10(climits[0]), log10(climits[1]), 0.1], output=str(CPT_FILEPATH), overrule_bg=True)
    return plot_map(grid, dpi, font, font_annot, plot_width, legend_text,
                    region=region, plot_cities=plot_cities, plot_faults=plot_faults, plot_trenches=plot_trenches, text=text)


def plot_hazard_diff_map(
        grid1: DataArray,
        grid2: DataArray,
        diff_type,
        dpi,
        climits: List[float],
        font,
        font_annot,
        plot_width,
        legend_text,
        region=None,
        plot_faults=False,
        plot_trenches=False,
        contours=None,
):


    if diff_type == 'sub':
        dgrid = grid2 - grid1
        if not climits:
            max_diff = max(abs(float(dgrid.min())), abs(float(dgrid.max())))
            climits = (-max_diff, max_diff)
        pygmt.makecpt(cmap = "blue,white,red", series=f"{climits[0]},0.0,{climits[1]}", continuous=True, output=str(CPT_FILEPATH))
    elif diff_type == 'ratio':
        if not climits:
            raise Exception('color bar limits must be set when plotting ratio map')
        dgrid = grid2/grid1
        pygmt.makecpt(cmap = "blue,white,red", series=f"{climits[0]},1.0,{climits[1]}", continuous=True, output=str(CPT_FILEPATH))
    else:
        raise Exception('diff type %s not recognized' % diff_type)

    return plot_map(dgrid, dpi, font, font_annot, plot_width, legend_text, region, plot_faults, plot_trenches, contours=contours)  
    