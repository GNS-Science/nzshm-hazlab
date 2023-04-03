import pandas as pd
from zipfile import ZIP_BZIP2, ZipFile
from pandas import DataFrame
from pathlib import Path
import math
from typing import List, Any
import os
from collections import namedtuple
from itertools import product
# import toshi_hazard_store
import numpy as np
from toshi_hazard_store import query

from nzshm_common.location.location import LOCATION_LISTS, location_by_id, LOCATIONS_BY_ID
from nzshm_common.grids import RegionGrid
from nzshm_common.location import CodedLocation

DTYPE = {'lat':'str', 'lon':'str', 'imt':'str', 'agg':'str', 'level':'str', 'apoe':'str'}
SITE_LIST = 'NZ_0_1_NB_1_1'
COLUMNS = ['lat', 'lon', 'imt', 'agg', 'level', 'apoe']
RESOLUTION = 0.001

RecordIdentifier = namedtuple('RecordIdentifier', 'location imt agg')

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def lat_lon(id):
    return location_by_id(id)['latitude'], location_by_id(id)['longitude']

def all_locations() -> List[CodedLocation]:
    """all locations in NZ35 and 0.1 deg grid"""

    locations_nz35 = [
        CodedLocation( *lat_lon(id), RESOLUTION)
        for id in LOCATION_LISTS["NZ"]["locations"]
    ]

    grid = RegionGrid[SITE_LIST]
    grid_locs = grid.load()
    locations_grid = [
        CodedLocation( *loc, RESOLUTION)
        for loc in grid_locs
    ]
    return locations_nz35 + locations_grid


def clean_df(hazard_curves: DataFrame) -> DataFrame:
    """remove NaNs"""

    return hazard_curves.dropna()


def get_hazard(
        hazard_id: str,
        vs30: int,
        locs: List[CodedLocation],
        imts: List[str],
        aggs: List[str],
        chunk_size: int=100,
) -> DataFrame:
    """download all locations, imts and aggs for a particular hazard_id and vs30."""

    loc_strs = [loc.downsample(RESOLUTION).code for loc in locs]
    naggs = len(aggs)
    nimts = len(imts)

    index = range(len(locs) * nimts * naggs)
    hazard_curves = pd.DataFrame({c: pd.Series(dtype=t) for c, t in DTYPE.items()}, index=index)
    ind = 0
    total_records = len(locs) * len(imts) * len(aggs)
    print(f'retrieving {total_records} records from THS')
    print_step = math.ceil(total_records / 10) 
    # for i,res in enumerate(toshi_hazard_store.query_v3.get_hazard_curves(loc_strs, [vs30], [hazard_id], imts, aggs)):
    for loc_chunks in chunks(loc_strs, chunk_size):
        for i,res in enumerate(query.get_hazard_curves(loc_strs, [vs30], [hazard_id], imts, aggs)):
            print(f'retrieved {i / total_records * 100:.0f}% of records from THS') if i%print_step == 0 else None
            lat = f'{res.lat:0.3f}'
            lon = f'{res.lon:0.3f}'
            hazard_curves.loc[ind,'lat'] = lat
            hazard_curves.loc[ind,'lon'] = lon
            hazard_curves.loc[ind,'imt'] = res.imt
            hazard_curves.loc[ind,'agg'] = res.agg
            hazard_curves.loc[ind,'level'] = np.array([float(item.lvl) for item in res.values])
            hazard_curves.loc[ind,'apoe'] = np.array([float(item.val) for item in res.values])
            ind += 1

    return hazard_curves

if __name__ == "__main__":

    # hazard_ids = [
    #     "NSHM_v1.0.4",
    # ]
    hazard_id = "NSHM_v1.0.4"
    vs30s = [275, 150, 400, 750, 175, 225, 375, 525]

    from nzshm_hazlab.store.levels import grid_locations, SITE_LIST

    imts = [
        'PGA', 'SA(0.1)', 'SA(0.15)', 'SA(0.2)', 'SA(0.25)',
        'SA(0.3)', 'SA(0.35)', 'SA(0.4)', 'SA(0.5)', 'SA(0.6)',
        'SA(0.7)', 'SA(0.8)', 'SA(0.9)', 'SA(1.0)', 'SA(1.25)',
        'SA(1.5)', 'SA(1.75)', 'SA(2.0)', 'SA(2.5)', 'SA(3.0)',
        'SA(3.5)', 'SA(4.0)', 'SA(4.5)', 'SA(5.0)', 'SA(6.0)',
        'SA(7.5)', 'SA(10.0)'
    ]
    aggs = ["mean"]
    locations = list(grid_locations(SITE_LIST)) +\
        [CodedLocation( *lat_lon(id), RESOLUTION) for id in LOCATIONS_BY_ID.keys()]
    
    for vs30 in vs30s:
        hazard = get_hazard(hazard_id, vs30, locations, imts, aggs)
        print(hazard)
        hazard = clean_df(hazard)
        print(hazard)
        break
