# from toshi_hazard_store.query_v3 import get_hazard_curves
import toshi_hazard_store
from nzshm_common.location.location import location_by_id, LOCATION_LISTS
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids import RegionGrid
import numbers
import random

def spot_check(hazard_id, vs30, location_ids=None, site_list_name=None, num=1):

    imts = ['PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.7)','SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)', 'SA(4.0)', 'SA(5.0)', 'SA(6.0)','SA(7.5)', 'SA(10.0)']
    imts_new = ["SA(0.15)",	"SA(0.25)", "SA(0.35)",	"SA(0.6)", "SA(0.8)", "SA(0.9)", "SA(1.25)", "SA(1.75)", "SA(2.5)", "SA(3.5)", "SA(4.5)"] 

    aggs = ["mean", "cov", "std", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.5", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]

    imts = imts_new
    aggs = aggs[:1]

    def rand_inds(length, k):
        return random.sample(range(length), k=k)

    def lat_lon(id):
        return (location_by_id(id)['latitude'], location_by_id(id)['longitude'])

    locations = []
    if site_list_name:    
        grid = RegionGrid[site_list_name]
        grid_locs = grid.load()
        grid_locs = [grid_locs[i] for i in rand_inds(len(grid_locs), num)]
        locations += [CodedLocation(*loc, 0.001).code for loc in grid_locs]
    
    if location_ids:
        id_locs = [CodedLocation(*lat_lon(id), 0.001).code for id in location_ids]
        id_locs = [id_locs[i] for i in rand_inds(len(id_locs), num)]
        locations += id_locs


    print(locations)
    print(f'testing {len(locations)} locations, {len(aggs)} aggregates, and {len(imts)} IMTs, for {hazard_id}, vs30 = {vs30}')
    i = 0
    for res in toshi_hazard_store.query_v3.get_hazard_curves(locations, [vs30], [hazard_id], imts, aggs):
        lat = f'{res.lat:0.3f}'
        lon = f'{res.lon:0.3f}'
        print(res.lat, res.lon, res.imt, res.agg)
        try:
            assert res.imt
            assert res.agg
            for value in res.values:
                assert isinstance(value.lvl, numbers.Number)
                assert isinstance(value.val, numbers.Number)
        except AssertionError as err:
            print(f'{err}: hazard ID {hazard_id}, vs30 {vs30} missing values(s)')
            print(f'lat {lat}')
            print(f'lon {lon}')
            print(f'agg {res.agg}')
            print(f'imt {res.imt}')
            print(f'level {value.lvl}')
            print(f'value {value.val}')
            raise
        i += 1

    try:
        assert i == len(imts)*len(aggs)*len(locations)
    except AssertionError as err:
        print(f'{err}: hazard ID {hazard_id}, vs30 {vs30} missing value(s). Expected {len(imts)*len(aggs)*len(locations)} got {i}')
        raise

    
                
if __name__ == "__main__":
    hazard_id = 'NSHM_v1.0.4'
    vs30s = [
        # 150,
        # 175,
        # 225,
        275,
        # 375,
        # 525,
        # 750,
    ]

    # ids = ['srg_142', 'srg_186']
    # locations = {loc['id']:loc for loc in LOCATIONS_SRWG214_BY_ID.values() if loc['name'] in filter_names_present}
    for vs30 in vs30s:
        spot_check(hazard_id,vs30, location_ids=LOCATION_LISTS['SRWG214']['locations'], num=3)
        # spot_check(hazard_id,vs30, location_ids=ids, num=len(ids))

