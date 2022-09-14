import csv
import io
import pandas as pd
import numpy as np
from pathlib import Path

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






#================================================================================================================#
thp_id = 'SLT_v8_gmm_v2_FINAL'
fig_dir = Path('/home/chrisdc/NSHM/oqresults/Full_Models/SLT_v8_gmm_v2/Maps')

site_list = 'NZ_0_1_NB_1_1'
imts = ['PGA']
aggs = 'mean'
vs30s = [400]

#============================================================================================================

grid = RegionGrid[site_list]
grid_locs = grid.load()
l = grid_locs.index( (-34.7,172.7) )
grid_locs = grid_locs[0:l] + grid_locs[l+1:]

for vs30 in vs30s:
    hazard = get_hazard_grid(thp_id, vs30, site_list)
    print(f'vs30: {vs30}')
    for imt in imts:
        print(f'imt: {imt}')
        aggs = set(hazard['agg'])
        for agg in aggs:
            if (agg=='std') | (agg=='cov'): continue
            print(f'agg: {agg}')
            for loc in grid_locs:
                # print(f'loc: {loc}')
                lat, lon = loc
                fhazard = hazard.loc[(hazard['lat'] == lat) & (hazard['lon'] == lon) & (hazard['agg'] == agg) & (hazard['imt'] == imt)]
                assert fhazard.shape[0] == 1
                y = fhazard.iloc[0,5:].to_numpy(dtype='float64')
                dy = y[1:] - y[0:-1]
                if not all(dy<0):
                    print(f'increasing prob at {vs30}, {imt}, {loc}, {agg}')
                    levels = [float(c[4:]) for c in fhazard.columns[5:]]
                    print(f'levels: {levels}')
                    print(f'values: {y}')

            

