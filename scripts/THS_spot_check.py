from toshi_hazard_store.query_v3 import get_hazard_curves
from nzshm_common.location.location import LOCATIONS_BY_ID
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids import RegionGrid
import numbers


def spot_check(hazard_id, vs30):

    imts = ['PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.7)','SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)', 'SA(4.0)', 'SA(5.0)', 'SA(6.0)','SA(7.5)', 'SA(10.0)']
    aggs = ["mean", "cov", "std", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.5", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]
    
    locations = []
    resample = 0.1
    site_list = 'NZ_0_1_NB_1_1'
    grid = RegionGrid[site_list]
    grid_locs = grid.load()
    grid_loc = grid_locs[-1]
    loc = CodedLocation(*grid_loc, resolution=0.001)
    locations.append(loc.resample(0.001).code)

    city_loc = list(LOCATIONS_BY_ID.values())[-1]
    locations.append(CodedLocation( city_loc['latitude'], city_loc['longitude'], resolution=0.001 ).resample(0.001).code)

    i = 0
    for res in get_hazard_curves(locations, [vs30], [hazard_id], imts, aggs):
        lat = f'{res.lat:0.3f}'
        lon = f'{res.lon:0.3f}'
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

    
                

hazard_id = 'SLT_v8_gmm_v2_FINAL'
vs30s = [400,750,250,600,350,175,300,450,375,275,225,200,150]

for vs30 in vs30s:
    spot_check(hazard_id,vs30)

