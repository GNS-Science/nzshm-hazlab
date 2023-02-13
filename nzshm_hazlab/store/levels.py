from pathlib import Path

import pandas as pd
from pandas import DataFrame

from nzshm_common.location import CodedLocation
from nzshm_common.grids import RegionGrid

from .curves import get_hazard, ARCHIVE_DIR
from nzshm_hazlab.data_functions import get_poe_df

POE_DTYPE = {'lat': float, 'lon': float, 'level': float}
RESOLUTION = 0.001
SITE_LIST = 'NZ_0_1_NB_1_1'
INV_TIME = 50

def grid_locations(site_list):

    grid = RegionGrid[site_list].load()
    for loc in grid:
        if loc[0] != -34.7 and loc[1] != 172.7:
            yield CodedLocation(loc[0], loc[1], RESOLUTION)


def poe_archive_filepath(hazard_id, imt, agg, poe, vs30):

    file_name = f'{hazard_id}-{imt}-{agg}-{poe}-{vs30}.bz2'
    return Path(ARCHIVE_DIR, file_name)


def save_hazard_poe(haz_poe: DataFrame, hazard_id, imt, agg, poe, vs30):

    haz_poe.to_json(poe_archive_filepath(hazard_id, imt, agg, poe, vs30))

    
def get_hazard_at_poe(hazard_id, imt, agg, poe, vs30):

    # fp = poe_archive_filepath(hazard_id, imt, agg, poe, vs30)
    # if fp.exists():
    #     print('loading hazard at poe from archive')
    #     return pd.read_json(fp, dtype = POE_DTYPE)
    # else:
    print('calculating hazard at poe')
    hazard = get_hazard(hazard_id, list(grid_locations(SITE_LIST)), vs30, [imt], [agg])
    haz_poe = get_poe_df(hazard, list(grid_locations(SITE_LIST)), imt, agg, poe, INV_TIME)
    # save_hazard_poe(haz_poe, hazard_id, imt, agg, poe, vs30)
    return haz_poe
