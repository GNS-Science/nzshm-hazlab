import itertools
import os

from typing import List, Tuple
from collections import namedtuple

import toshi_hazard_store
from nzshm_common.location.location import location_by_id, LOCATION_LISTS
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids.region_grid import load_grid

from nzshm_hazlab.locations import get_locations

HazardEntry = namedtuple("HazardEntry", "hazard_id location vs30 imt agg")

def check_db(hazard_ids, vs30s, locations, imts, aggs, force=True):

    if force and os.environ.get('NZSHM22_HAZARD_STORE_LOCAL_CACHE'):
        del os.environ['NZSHM22_HAZARD_STORE_LOCAL_CACHE']

    hazard_entries = []
    i = 0
    total_expected = len(hazard_ids)*len(vs30s)*len(locations)*len(imts)*len(aggs)
    for vs30 in vs30s:
        for hazard_id in hazard_ids:
            for res in toshi_hazard_store.query_v3.get_hazard_curves(locations, [vs30], [hazard_id], imts, aggs):
                i += 1 
                print(f'record {i} of {total_expected}: {res.hazard_model_id}, {res.nloc_001}, {res.imt}, {res.agg})')
                hazard_entries.append(HazardEntry(res.hazard_model_id, res.nloc_001, res.vs30, res.imt, res.agg))

    return hazard_entries

def get_expected(hazard_ids, vs30s, locations, imts, aggs):

    hazard_entries = []
    for hazard_id, vs30, loc, imt, agg in itertools.product(hazard_ids, vs30s, locations, imts, aggs):
        hazard_entries.append(HazardEntry(hazard_id, loc, vs30, imt, agg))
    
    return hazard_entries

                
if __name__ == "__main__":
    hazard_ids = [
        "NSHM_v1.0.4",
    ]
    vs30s = [250, 400, 750]
    location_names = ["/home/chrisdc/NSHM/oqruns/RUNZI-MAIN-HAZARD/WeakMotionSiteLocs_SHORT.csv"]
    force = True
    print_missing = False
  
    # location_names = ["NZ"]
    # imts = ['PGA',
    #     'SA(0.2)',
    #     'SA(0.5)',
    #     'SA(1.0)',
    #     'SA(1.5)',
    #     'SA(3.0)',
    # ]
    imts = ["PGA"]
    # aggs = ["mean", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]
    aggs = ["mean"]
    
    locations = get_locations(location_names)

    entries_expected = get_expected(hazard_ids, vs30s, locations, imts, aggs)
    entries_found = check_db(hazard_ids, vs30s, locations, imts, aggs, force)
    entries_missing = set(entries_expected).difference(set(entries_found))
    print(f"there are {len(entries_missing)} entries of {len(entries_expected)} missing from the database")

    if print_missing:
        print("====MISSING ENTRIES====")
        for entry in entries_missing:
            print(entry)

        locations_missing = {hazard_id:[] for hazard_id in hazard_ids}
        for entry in entries_missing:
            locations_missing[entry.hazard_id].append(entry.location)
        for hazard_id in hazard_ids:
            locations_missing[hazard_id] = list(set(locations_missing[hazard_id]))

        for k,v in locations_missing.items():
            print(f'======== {k} =======')
            for loc in v:
                print(loc)
            junk = input('press any key to continue')
