import math
import json
import io
import csv
import pandas as pd
import numpy as np
from pathlib import Path
import geopandas as gp
from shapely.geometry import Polygon
import geojson


import pygmt
import xarray as xr

from nzshm_common.grids import RegionGrid
from nzshm_common.location import CodedLocation
from toshi_hazard_store import model, query_v3



ARCHIVE_DIR = '/home/chrisdc/NSHM/oqdata/HAZ_GRID_ARCHIVE'

def compute_hazard_at_poe(levels,values,poe,inv_time):

    rp = -inv_time/np.log(1-poe)
    haz = np.exp( np.interp( np.log(1/rp), np.flip(np.log(values)), np.flip(np.log(levels)) ) )
    return haz

def compute_poe_at_level(levels,values,target_level):

    return np.interp(target_level,levels,values)
    

def get_hazard_grid(thp_id, vs30, site_list, force=False):

    grid_filename = f'{thp_id}-{vs30}-{site_list}.json'
    grid_filepath = Path(ARCHIVE_DIR,grid_filename)

    if grid_filepath.exists() and (not force):
        hazard_data = pd.read_json(grid_filepath)
        return hazard_data
    
    resample = 0.1
    locations = []
    imts = ['PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.7)','SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)', 'SA(4.0)', 'SA(5.0)', 'SA(6.0)','SA(7.5)', 'SA(10.0)']
    # imts = ['PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.7)','SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)']
    aggs = ["std","mean", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.5", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]
    
    grid = RegionGrid[site_list]
    grid_locs = grid.load()
    for gloc in grid_locs:
        loc = CodedLocation(*gloc, resolution=0.001)
        loc = loc.resample(float(resample)) if resample else loc
        locations.append(loc.resample(0.001).code)

    haggs = query_v3.get_hazard_curves(locations, [vs30], [thp_id], imts=imts, aggs=aggs)
    tmpcsv = io.StringIO()
    model_writer = csv.writer(tmpcsv)
    model_writer.writerows(list(model.HazardAggregation.to_csv(haggs)))
    tmpcsv.seek(0)
    # now build a dataframe
    df = pd.read_csv(tmpcsv)
    df.to_json(grid_filepath)
    
    return df


def get_cov_grid(thp_id, site_list, imt, agg, poe, vs30):

    hazard = get_hazard_grid(thp_id, vs30, site_list)
    hazard_mean = hazard[ hazard['agg'] == 'mean' ]
    hazard_std = hazard[ hazard['agg'] == 'std' ]
    levels = np.array([float(col[4:]) for col in hazard.columns[5:]])
    hazard_cov = hazard_mean.copy()
    hazard_cov['cov'] = np.nan

    for (imean, row_mean),(istd,row_std) in zip(hazard_mean.iterrows(),hazard_std.iterrows()):
        values_mean = row_mean[5:].to_numpy(dtype='float64')
        values_std = row_std[5:].to_numpy(dtype='float64')
        values_cov = values_std/values_mean
        level_at_poe = compute_hazard_at_poe(levels,values_mean,poe,50)
        hazard_cov.loc[imean,'cov'] = np.interp(level_at_poe,levels,values_cov)
        # hazard_cov.loc[imean,'cov'] = np.exp(np.interp(np.log(level_at_poe),np.log(levels),np.log(values_cov)))


    haz_cov = hazard_cov.loc[:,['agg','imt','lat','lon','cov']]
    haz_cov  = haz_cov[ (haz_cov['imt'] == imt) & (haz_cov['agg'] == 'mean') ]

    haz_cov = haz_cov[['lat','lon','cov']]

    haz_cov = haz_cov.pivot(index="lat", columns="lon")
    haz_cov = haz_cov.droplevel(0, axis=1)
    grid = xr.DataArray(data=haz_cov)

    return grid

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

#================================================================================================================#
thp_id = 'SLT_v8_gmm_v2'
fig_dir = Path('/home/chrisdc/NSHM/oqresults/Full_Models/SLT_v8_gmm_v2/Maps')

site_list = 'NZ_0_2_NB_1_1'
# imts = ['PGA','SA(0.5)','SA(1.5)','SA(3.0)']
imts = ['PGA']
 
poes = [0.02, 0.1]
vs30s = [400]

plot_faults = True
colormap = 'jet'

region="165/180/-48/-34"
series = {
    0.02: [0.5,1.5,0.02],
    0.1: [0.25,1.2,0.02],
}
dv = 0.1

#============================================================================================================

for vs30 in vs30s:
    for imt in imts:
        for poe in poes:
            full_dir = Path(fig_dir,f'{int(vs30)}')
            filepath = Path(full_dir,f'{thp_id}-CoV-{vs30}-{imt}-{poe}.png')

            cov = get_cov_grid(thp_id, site_list, imt, 'mean', poe, vs30)
            print(f'cov min and max = {float(cov.min())}, {float(cov.max())}')
            fig = pygmt.Figure()
            pygmt.config(FONT_ANNOT_PRIMARY = 14)
            vmin = math.floor(float(cov.min())*10.0)/10.0
            vmax = math.ceil(float(cov.max())*10.0)/10.0
            # series = [vmin,vmax,dv]
            series = [0.4,1.7,0.1]
            pygmt.makecpt(cmap = colormap, series=series)

            fig.grdimage(grid=cov, region=region, projection="M15c", cmap = True, dpi = 100, frame = "a")
            fig.coast(shorelines = True, water="white")
            fig.basemap(frame=["a", f"+tCoV {vs30}m/s {imt} {poe*100:.0f}% in 50 yrs"])


            fig.colorbar(frame=f'af+l"CoV ({imt} {poe*100:.0f}% PoE in 50)"')#,position='+ef')

            fig.savefig(filepath)
            fig.show()

