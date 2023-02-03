import pandas as pd
from zipfile import ZIP_BZIP2, ZipFile
from pandas import DataFrame
from pathlib import Path
from typing import List, Any
import os
from toshi_hazard_store.query_v3 import get_hazard_curves

from nzshm_common.location.location import LOCATIONS_BY_ID
from nzshm_common.grids import RegionGrid
from nzshm_common.location import CodedLocation
from nzshm_hazlab.plotting_functions import plot_hazard_curve_fromdf

ARCHIVE_DIR = Path(os.environ['HAZARD_CURVE_ARCHIVE'])
assert ARCHIVE_DIR.exists()
DTYPE = {'lat':str,'lon':str}
SITE_LIST = 'NZ_0_1_NB_1_1'
IMTS = ['PGA', 'SA(0.2)', 'SA(0.5)', 'SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)', 'SA(5.0)', 'SA(10.0)']
AGGS = ["mean", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.5", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]

def all_locations() -> List[str]:
    locations_nz35 = [
        CodedLocation( loc['latitude'], loc['longitude'], 0.001).code
        for loc in LOCATIONS_BY_ID.values()
    ]

    grid = RegionGrid[SITE_LIST]
    grid_locs = grid.load()
    locations_grid = [
        CodedLocation( *loc, 0.001).code
        for loc in grid_locs
    ]
    return locations_nz35 + locations_grid


def archive_filepath(hazard_id: str, vs30: int) -> Path:
    return Path(ARCHIVE_DIR, f'{hazard_id}-{vs30}.bz2')

def download_hazard(hazard_id: str, vs30: int) -> None:
    """download all locations, imts and aggs for a particular hazard_id and vs30. Save in DataFrame written to disk"""

    hazards = get_hazard_curves(
        hazard_model_ids=[hazard_id],
        vs30s = [vs30],
        locs = all_locations()[:1],
        imts = IMTS,
        aggs = AGGS,
    )
    imts = set() 
    aggs = set()
    for res in hazards:
        imts.add(res.imt)
        aggs.add(res.agg)

    nlevels = len(res.values)
    naggs = len(aggs)
    nimts = len(imts)

    columns = ['lat', 'lon', 'imt', 'agg', 'level', 'hazard']
    index = range(len(all_locations()) * nimts * naggs * nlevels)
    hazard_curves = pd.DataFrame(columns=columns, index=index)
    ind = 0
    for i,res in enumerate(get_hazard_curves(all_locations(), [vs30], [hazard_id], IMTS, AGGS)):
        print(f'retrieving record {i} from THS') if i%10000 == 0 else None
        lat = f'{res.lat:0.3f}'
        lon = f'{res.lon:0.3f}'
        for value in res.values:
            hazard_curves.loc[ind,'lat'] = lat
            hazard_curves.loc[ind,'lon'] = lon
            hazard_curves.loc[ind,'imt'] = res.imt
            hazard_curves.loc[ind,'agg'] = res.agg
            hazard_curves.loc[ind,'level'] = value.lvl
            hazard_curves.loc[ind,'hazard'] = value.val
            ind += 1

    hazard_curves.to_json(archive_filepath(hazard_id, vs30))


def hazard_from_archive(
        hazard_id: str,
        vs30: int,
        locations: List[CodedLocation],
        imts: List[str],
        aggs: List[str]
) -> DataFrame:
    """open the DataFrame archive and pull out the requested data"""

    lats = [loc.code.split('~')[0] for loc in locations]
    lons = [loc.code.split('~')[1] for loc in locations]

    hdf = pd.read_json(archive_filepath(hazard_id, vs30), dtype=DTYPE)
    hdf = hdf.loc[hdf['lat'].isin(lats)]
    hdf = hdf.loc[hdf['lon'].isin(lons)]
    hdf = hdf.loc[hdf['agg'].isin(aggs)]
    hdf = hdf.loc[hdf['imt'].isin(imts)]

    return hdf
            

def get_hazard(
        hazard_id: str,
        locs: List[CodedLocation],
        vs30: int,
        imts: List[str],
        aggs: List[str],
        force: Any = False
) -> DataFrame:

    if force or not archive_filepath(hazard_id, vs30).exists():
        download_hazard(hazard_id, vs30)

    return hazard_from_archive(hazard_id, vs30, locs, imts, aggs) 


if __name__ == "__main__":

    hazard_ids = [
        "NSHM_v1.0.1_CRUsens_baseline",
        "NSHM_v1.0.1_sens_jump5km",
        "NSHM_v1.0.1_sens_jump10km",
        "NSHM_v1.0.1_sens_jump10km_iso",
        "NSHM_v1.0.1_sens_jump5km_iso",
        "NSHM_v1.0.1_CRUsens_baseline_iso",
    ]
    hazard_ids = hazard_ids[1:]

    keep = ['WLG','AKL','CHC']
    locations = [CodedLocation(loc['latitude'], loc['longitude'], 0.001) for loc in LOCATIONS_BY_ID.values() if loc['id'] in keep]
    for id in hazard_ids:
        print(f'working on {id}')
        # hazard_curves = get_hazard(id, locations, 400, ['PGA', 'SA(0.5)' ], ['mean'])
        download_hazard(id, 400)