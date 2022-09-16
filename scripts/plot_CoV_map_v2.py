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

def compute_cov_at_poe(levels,values_mean,values_cov,poe,inv_time):

    rp = -inv_time/np.log(1-poe)
    try:
        target_level = np.exp( np.interp( np.log(1/rp), np.flip(np.log(values_mean)), np.flip(np.log(levels)) ) )
    except:
        breakpoint()
    return np.exp( np.interp(np.log(target_level),np.log(levels),np.log(values_cov)) )


def get_hazard_grid(thp_id, vs30, site_list, force=False):

    grid_filename = f'{thp_id}-{vs30}-{site_list}.json'
    grid_filepath = Path(ARCHIVE_DIR,grid_filename)
    if grid_filepath.exists() and (not force):
        hazard_data = pd.read_json(grid_filepath)
        return hazard_data
    
    resample = 0.1
    locations = []
    imts = ['PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.7)','SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)', 'SA(4.0)', 'SA(5.0)', 'SA(6.0)','SA(7.5)', 'SA(10.0)']
    aggs = ["mean", "cov", "std", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.5", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]
    
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


def get_poe_grid(thp_id, site_list, imt, poe, vs30):

    hazard = get_hazard_grid(thp_id, vs30, site_list)
    hazard_mean = hazard[ (hazard['agg'] == 'mean') & (hazard['imt'] == imt) ]
    hazard_cov = hazard[ (hazard['agg'] == 'cov') & (hazard['imt'] == imt) ]
    levels = np.array([float(col[4:]) for col in hazard.columns[5:]])
    hazard_cov['haz-poe'] = np.nan
    for index, row in hazard_cov.iterrows():
        values_cov = row[5:-1].to_numpy(dtype='float64')
        ind = (hazard_mean['imt'] == row['imt']) & (hazard_mean['lat'] == row['lat']) & (hazard_mean['lon'] == row['lon']) & (hazard_mean['vs30'] == row['vs30'])
        values_mean = hazard_mean[ind].iloc[0,5:].to_numpy(dtype='float64')
        hazard_cov.loc[index,'haz-poe'] = compute_cov_at_poe(levels,values_mean,values_cov,poe,50)

    haz_poe = hazard_cov.loc[:,['lat','lon','haz-poe']]
    # haz_poe  = haz_poe[ (haz_poe['imt'] == imt) ]

    # haz_poe = haz_poe[['lat','lon','haz-poe']]

    haz_poe = haz_poe.pivot(index="lat", columns="lon")
    haz_poe = haz_poe.droplevel(0, axis=1)
    grid = xr.DataArray(data=haz_poe)


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
thp_id = 'SLT_v8_gmm_v2_FINAL'
fig_dir = Path('/home/chrisdc/NSHM/oqresults/Full_Models/SLT_v8_gmm_v2/Maps')

site_list = 'NZ_0_1_NB_1_1'
# imts = ['PGA','SA(0.5)','SA(1.5)']
imts = ['PGA']
# imts = ['SA(3.0)']
agg = 'mean'
# poes = [0.02, 0.1]
poes = [0.1]
vs30s = [400]

plot_faults = False
colormap = 'jet' # 'viridis', 'jet', 'plasma', 'imola', 'hawaii'
filename_ext = '_' + colormap

region="163/185/-50/-24" if plot_faults else "165/180/-48/-34"



#============================================================================================================

for vs30 in vs30s:
    for imt in imts:
        for poe in poes:
            full_dir = Path(fig_dir,f'{int(vs30)}')
            filepath = Path(full_dir,f'{thp_id}-CoV-{vs30}-{imt}-{poe}.png')

            grid = get_poe_grid(thp_id, site_list, imt, poe, vs30)
            print(f'cov min and max = {float(grid.min())}, {float(grid.max())}')
fig = pygmt.Figure()
pygmt.config(FONT_ANNOT_PRIMARY = 14)
#series = [float(grid.min()), float(grid.max()), 0.1] #0.4,1.7,0.1]
series = [0,1,0.05]
pygmt.makecpt(cmap = colormap, series=series)

fig.grdimage(grid=grid, region=region, projection="M15c", cmap = True, dpi = 100, frame = "a")
fig.coast(shorelines = True, water="white")
fig.basemap(frame=["a", f"+tCoV {vs30}m/s {imt} {poe*100:.0f}% in 50 yrs"])
fig.colorbar(frame=f'af+l"CoV ({imt} {poe*100:.0f}% PoE in 50)"')#,position='+ef')

# fig.savefig(filepath)
fig.show()

