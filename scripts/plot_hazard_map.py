import json
import io
import csv
import pandas as pd
import numpy as np
from pathlib import Path

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

def get_hazard_grid(thp_id, site_list, force=False):

    grid_filename = '-'.join( (thp_id,site_list) ) + '.json'
    grid_filepath = Path(ARCHIVE_DIR,grid_filename)

    if grid_filepath.exists() and (not force):
        hazard_data = pd.read_json(grid_filepath)
        return hazard_data
    
    resample = 0.1
    locations = []
    vs30s = [400]
    imts = ['PGA','SA(0.5)','SA(1.5)']
    aggs = ['mean','0.005','0.1','0.2','0.5','0.8','0.9','0.995']
    grid = RegionGrid[site_list]
    grid_locs = grid.load()
    for gloc in grid_locs:
        loc = CodedLocation(*gloc, resolution=0.001)
        loc = loc.resample(float(resample)) if resample else loc
        locations.append(loc.resample(0.001).code)

    haggs = query_v3.get_hazard_curves(locations, vs30s, [thp_id], imts=imts, aggs=aggs)

    tmpcsv = io.StringIO()
    model_writer = csv.writer(tmpcsv)
    model_writer.writerows(list(model.HazardAggregation.to_csv(haggs)))
    tmpcsv.seek(0)
    # now build a dataframe
    df = pd.read_csv(tmpcsv)
    df.to_json(grid_filepath)
    
    return df


def get_poe_grid(thp_id, site_list, imt, agg, poe):

    hazard = get_hazard_grid(thp_id, site_list)
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
# thp_id_TI = 'SLT_v5_gmm_v0_ST_TI'
# thp_id_TD = 'SLT_v5_gmm_v0_ST_TD'
thp_id = 'SLT_v7_gmm_v1'

site_list = 'NZ_0_2_NB_1_1'
imt = 'PGA'
agg = 'mean'
poe = 0.1

# grid_TI = get_poe_grid(thp_id_TI, site_list, imt, agg, poe)
# grid_TD = get_poe_grid(thp_id_TD, site_list, imt, agg, poe)

grid = get_poe_grid(thp_id, site_list, imt, agg, poe)


# grid_ratio = grid_TD/grid_TI

#============================================================================================================

fig = pygmt.Figure()
pygmt.config(FONT_ANNOT_PRIMARY = 14)
# pygmt.makecpt(cmap = "jet", series=[0,.4,0.01])
# pygmt.makecpt(cmap = "jet", series=[0,1.25,0.02])
pygmt.makecpt(cmap = "jet", series=[0,2,0.05])
# pygmt.makecpt(cmap = "jet", series=[0.5,2,0.1])

fig.grdimage(grid=grid, projection="M15c", cmap = True, dpi = 100, frame = "a")
fig.coast(shorelines = True, water="white")
fig.basemap(frame=["a", f"+t{imt} {poe*100:.0f}% in 50 yrs"])
fig.colorbar(frame=f'af+l"{imt} ({poe*100:.0f}% PoE in 50)"')
fig.show()


# fig = pygmt.Figure()
# pygmt.config(FONT_ANNOT_PRIMARY = 14)


# fig.basemap(region=[160,185,-48,-33],frame=["a", "+t2010"])

# pygmt.makecpt(cmap = "jet", series=[0,1.5,0.1])
# # fig.grdimage(grid=grid, projection="M15c", cmap = True, dpi = 100, frame = "a")

# fig.coast(shorelines = True, water="white")

# fig.colorbar(frame='af+l"PGA (10% PoE in 50)"')
# fig.show()
