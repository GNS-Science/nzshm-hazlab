import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from nzshm_common.location.location import LOCATIONS_BY_ID
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids.region_grid import load_grid
from toshi_hazard_store.query_v3 import get_hazard_curves


from oq_hazard_report.plotting_functions import plot_hazard_curve_fromdf

plot_title = 'SLT v5, GMCM v0'
data_filepath = Path('/home/chrisdc/NSHM/oqdata/SRWG/hazard_data.json')
hazard_id = 'SLT_v5_gmm_v0_SRWG'

locations = [f"{loc['latitude']:0.3f}~{loc['longitude']:0.3f}" for loc in LOCATIONS_BY_ID.values()]
vs30s = [150, 200, 250, 300, 350, 400, 450, 750]
imts = ['PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.7)', 'SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)', 'SA(4.0)', 'SA(5.0)', 'SA(6.0)', 'SA(7.0)']
aggs = ['mean', '0.001', '0.01', '0.05', '0.1', '0.2', '0.25', '0.3', '0.4', '0.5', '0.6', '0.7', '0.75', '0.8', '0.9', '0.99']


#=============================================================================================================================#

def get_hazard(hazard_id, locs, vs30s, imts, aggs):

    columns = ['lat', 'lon', 'vs30', 'imt', 'agg', 'level', 'hazard']
    index = range(len(locs) * len(imts) * len(aggs) * len(vs30s) *  37)
    hazard_curves = pd.DataFrame(columns=columns, index=index)

    ind = 0
    for i,res in enumerate(get_hazard_curves(locs, vs30s, [hazard_id], imts, aggs)):
        lat = f'{res.lat:0.3f}'
        lon = f'{res.lon:0.3f}'
        vs30 = res.vs30
        print(f'lat: {lat}, lon: {lon}, vs30: {vs30}, imt: {res.imt}')
        for value in res.values:
            hazard_curves.loc[ind,'lat'] = lat
            hazard_curves.loc[ind,'lon'] = lon
            hazard_curves.loc[ind,'vs30'] = vs30
            hazard_curves.loc[ind,'imt'] = res.imt
            hazard_curves.loc[ind,'agg'] = res.agg
            hazard_curves.loc[ind,'level'] = value.lvl
            hazard_curves.loc[ind,'hazard'] = value.val
            ind += 1

    return hazard_curves


hazard_curves = get_hazard(hazard_id, locations, vs30s, imts, aggs)
hazard_curves.to_json(data_filepath)
    
