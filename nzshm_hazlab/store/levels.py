from pathlib import Path
import time

import pandas as pd
from pandas import DataFrame
import numpy as np

from nzshm_common.location import CodedLocation
from nzshm_common.grids import RegionGrid

from nzshm_hazlab.store.curves import get_hazard_v1, get_hazard
from nzshm_hazlab.data_functions import get_poe_df, compute_hazard_at_poe
from toshi_hazard_store import query


POE_DTYPE = {'lat': float, 'lon': float, 'level': float}
RESOLUTION = 0.001
SITE_LIST = 'NZ_0_1_NB_1_1'
INV_TIME = 50

def grid_locations(site_list):

    grid = RegionGrid[site_list].load()
    for loc in grid:
        yield CodedLocation(loc[0], loc[1], RESOLUTION)


# def poe_archive_filepath(hazard_id, imt, agg, poe, vs30):

#     file_name = f'{hazard_id}-{imt}-{agg}-{poe}-{vs30}.bz2'
#     return Path(ARCHIVE_DIR, file_name)


# def save_hazard_poe(haz_poe: DataFrame, hazard_id, imt, agg, poe, vs30):

#     haz_poe.to_json(poe_archive_filepath(hazard_id, imt, agg, poe, vs30))

    
def get_hazard_at_poe(hazard_id, vs30, imt, agg, poe):

    ghaz = next(query.get_gridded_hazard([hazard_id], [SITE_LIST], [vs30], [imt], [agg], [poe]))
    grid = RegionGrid[SITE_LIST]
    locations = list(
        map(lambda grd_loc: CodedLocation(grd_loc[0], grd_loc[1], resolution=grid.resolution), grid.load())
    )
    lat = [loc.lat for loc in locations]
    lon = [loc.lon for loc in locations]
    haz_poe = pd.DataFrame( data={'lat': lat, 'lon': lon, 'level': ghaz.grid_poes})
    return haz_poe

    # fp = poe_archive_filepath(hazard_id, imt, agg, poe, vs30)
    # if fp.exists():
    #     print('loading hazard at poe from archive')
    #     return pd.read_json(fp, dtype = POE_DTYPE)
    # else:
    # print('calculating hazard at poe')
    # hazard = get_hazard(hazard_id, vs30, list(grid_locations(SITE_LIST)), [imt], [agg])
    # hazard = get_hazard_v1(hazard_id, vs30, list(grid_locations(SITE_LIST)), [imt], [agg])
    # haz_poe = get_poe_df(hazard, list(grid_locations(SITE_LIST)), imt, agg, poe, INV_TIME)
    # save_hazard_poe(haz_poe, hazard_id, imt, agg, poe, vs30)

    # haz_poe = pd.DataFrame(
    #     columns = ['lat', 'lon', 'level'],
    #     index = range(len(list(grid_locations(SITE_LIST)))),
    #     dtype='float64'
    # )
    # ind = 0
    # tic = time.perf_counter()
    # loc_strs = [loc.code for loc in grid_locations(SITE_LIST)]
    # for loc in grid_locations(SITE_LIST):
    #     if ind%100 == 0:
    #         toc = time.perf_counter()
    #         print(f'time to load 100 sites {toc-tic:.1f} seconds')
    #         tic = time.perf_counter()
    #     res = next(query.get_hazard_curves([loc.code], [vs30], [hazard_id], [imt], [agg]))
    #     levels = np.array([float(item.lvl) for item in res.values])
    #     values = np.array([float(item.val) for item in res.values])
    #     hazard = compute_hazard_at_poe(levels, values, poe, INV_TIME)
    #     haz_poe.loc[ind, 'lat'] = loc.lat
    #     haz_poe.loc[ind, 'lon'] = loc.lon
    #     haz_poe.loc[ind,'level'] = hazard
    #     ind += 1
        
    return haz_poe
