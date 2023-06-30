import itertools

from typing import List, Tuple
from collections import namedtuple

import toshi_hazard_store
from nzshm_common.location.location import location_by_id, LOCATION_LISTS
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids.region_grid import load_grid

HazardEntry = namedtuple("HazardEntry", "hazard_id location vs30 imt agg")

def lat_lon(id):
    return (location_by_id(id)['latitude'], location_by_id(id)['longitude'])


def get_locations(location_names: List[str]) -> List[str]:

    locations: List[Tuple[float, float]] = []
    for location_spec in location_names:
        if '~' in location_spec:
            locations.append(location_spec)
        elif '_intersect_' in location_spec:
            spec0, spec1 = location_spec.split('_intersect_')
            loc0 = set(load_grid(spec0))
            loc1 = set(load_grid(spec1))
            loc01 = list(loc0.intersection(loc1))
            loc01.sort()
            locations += [CodedLocation(*loc, 0.001).code for loc in loc01]
        elif '_diff_' in location_spec:
            spec0, spec1 = location_spec.split('_diff_')
            loc0 = set(load_grid(spec0))
            loc1 = set(load_grid(spec1))
            loc01 = list(loc0.difference(loc1))
            loc01.sort()
            locations += [CodedLocation(*loc, 0.001).code for loc in loc01]
        elif location_by_id(location_spec):
            locations.append(
                CodedLocation(*lat_lon(location_spec), 0.001).code
                )
        elif LOCATION_LISTS.get(location_spec):
            location_ids = LOCATION_LISTS[location_spec]["locations"]
            locations += [CodedLocation(*lat_lon(id),0.001).code for id in location_ids]
        else:
            locations += [CodedLocation(*loc, 0.001).code for loc in load_grid(location_spec)]
    return locations

def check_db(hazard_ids, vs30s, locations, imts, aggs):

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
        "NSHM_v1.0.4_ST_cruNhi_iso",
        "NSHM_v1.0.4_ST_cruNlo_iso",
        "NSHM_v1.0.4_ST_crublo_iso",
        "NSHM_v1.0.4_ST_crubmid_iso",
        "NSHM_v1.0.4_ST_crubhi_iso",
        "NSHM_v1.0.4_ST_geologic_iso",
        "NSHM_v1.0.4_ST_geodetic_iso",
        "NSHM_v1.0.4_ST_TD_iso",
        "NSHM_v1.0.4_ST_HikNhi_iso",
        "NSHM_v1.0.4_ST_HikNmed_iso",
        "NSHM_v1.0.4_ST_HikNlo_iso",
        "NSHM_v1.0.4_ST_Hikblo_iso",
        "NSHM_v1.0.4_ST_Hikbmid_iso",
        "NSHM_v1.0.4_ST_Hikbhi_iso",
    ]
    vs30s = [400]
    location_names = ["NZ", "NZ_0_1_NB_1_1_intersect_NZ_0_2_NB_1_1"]
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
    entries_found = check_db(hazard_ids, vs30s, locations, imts, aggs)
    entries_missing = set(entries_expected).difference(set(entries_found))
    print(f"there are {len(entries_missing)} entries missing from the database")
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

    "NSHM_v1.0.4_ST_HikNmed_iso"
    "NSHM_v1.0.4_ST_HikNlo_iso"