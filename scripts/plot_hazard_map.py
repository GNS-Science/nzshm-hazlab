import json
import io
import csv
import pandas as pd
import numpy as np
from pathlib import Path
import geopandas as gp
from shapely.geometry import Polygon


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

def get_hazard_grid(thp_id, vs30, site_list, force=False):

    grid_filename = f'{thp_id}-{vs30}-{site_list}.json'
    grid_filepath = Path(ARCHIVE_DIR,grid_filename)

    if grid_filepath.exists() and (not force):
        hazard_data = pd.read_json(grid_filepath)
        return hazard_data
    
    resample = 0.1
    locations = []
    imts = ['PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.7)','SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)', 'SA(4.0)', 'SA(5.0)', 'SA(6.0)','SA(7.5)', 'SA(10.0)']
    aggs = ["mean", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.5", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]
    
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


def get_poe_grid(thp_id, site_list, imt, agg, poe, vs30):

    hazard = get_hazard_grid(thp_id, vs30, site_list)
    levels = np.array([float(col[4:]) for col in hazard.columns[5:]])
    hazard['haz-poe'] = np.nan
    for index, row in hazard.iterrows():
        values = row[5:-1].to_numpy(dtype='float64')
        hazard.loc[index,'haz-poe'] = compute_hazard_at_poe(levels,values,poe,50)

    haz_poe = hazard.loc[:,['agg','imt','lat','lon','haz-poe']]
    haz_poe  = haz_poe[ (haz_poe['imt'] == imt) & (haz_poe['agg'] == agg) ]

    haz_poe = haz_poe[['lat','lon','haz-poe']]

    haz_poe = haz_poe.pivot(index="lat", columns="lon")
    haz_poe = haz_poe.droplevel(0, axis=1)
    grid = xr.DataArray(data=haz_poe)


    return grid

#================================================================================================================#
thp_id = 'SLT_v8_gmm_v2'
fig_dir = Path('/home/chrisdc/NSHM/oqresults/Full_Models/SLT_v8_gmm_v2/Maps')

site_list = 'NZ_0_2_NB_1_1'
imt = 'PGA'
agg = 'mean'
poe = 0.02
vs30 = 400
region="165/180/-48/-34"
acc_max = 2

grid = get_poe_grid(thp_id, site_list, imt, agg, poe, vs30)
#============================================================================================================


fault_polygons = gp.read_file('/home/chrisdc/NSHM/DATA/Crustal_Rupture_Set_RmlsZToxMDAwODc=/fault_sections.geojson')
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
backarc_polygon = gp.GeoSeries([ba_poly])

fig = pygmt.Figure()
pygmt.config(FONT_ANNOT_PRIMARY = 14)
pygmt.makecpt(cmap = "jet", series=[0,acc_max,0.05])

fig.grdimage(grid=grid, region=region, projection="M15c", cmap = True, dpi = 100, frame = "a")
fig.coast(shorelines = True, water="white")
fig.basemap(frame=["a", f"+t{vs30}m/s {imt} {poe*100:.0f}% in 50 yrs"])
# fig.plot(data=fault_polygons)
# fig.plot(data=backarc_polygon, pen="1p,red")
fig.colorbar(frame=f'af+l"{imt} ({poe*100:.0f}% PoE in 50)"')
filepath = Path(fig_dir,f'{vs30}-{imt}-{poe}.png')
# fig.savefig(filepath)
fig.show()

