import csv
from pathlib import Path
from collections import namedtuple

import pandas as pd
import numpy as np

from nzshm_common.location.code_location import CodedLocation
from nzshm_hazlab.locations import get_locations
from nzshm_hazlab.store.curves import get_hazard
from nzshm_hazlab.data_functions import compute_hazard_at_poe
from nzshm_hazlab.base_functions import period_from_imt, imt_from_period


# location_list = ["/home/chrisdc/NSHM/oqruns/RUNZI-MAIN-HAZARD/WeakMotionSiteLocs_SHORT.csv"]
location_list = ["TP"]
locations = get_locations(location_list)
hazard_model_id = "NSHM_v1.0.4"
vs30s = [
    250,
    150,
    175,
    200,
    225,
    275,
    300,
    350,
    375,
    400,
    450,
    500,
    600,
    750,
    900,
    1000,
    1500,
]
imts = ['PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.7)',
        'SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)', 'SA(4.0)', 'SA(5.0)', 'SA(6.0)','SA(7.5)', 'SA(10.0)']
# aggs = ["mean", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]
aggs = ["0.05", "0.1", "mean", "0.9", "0.95"]
# poes = [0.02, 0.1]
# poes = [0.033, 0.154, 0.222, 0.395]
poes = [0.86]
INV_TIME = 50
DTYPE = {'lat':'str', 'lon':'str', 'poe': 'str', 'agg':'str', 'imt':'str', 'acc':'str'}

n_records = len(locations) * len(aggs) * len(imts)

# download curves
hazard_curves = {}
for vs30 in vs30s:
    hazard_curves[vs30] = get_hazard(hazard_model_id, vs30, locations, imts, aggs)
    if (hazard_curves[vs30].shape[0] != n_records) or (hazard_curves[vs30]['apoe'].isnull().any()):
        warn = f"WARNING: vs30 {vs30} is missing {n_records - hazard_curves[vs30].shape[0]} records"
        raise Exception(warn)


# calculate UHS
uhs = {}
index = range(len(locations) * len(aggs) * len(poes))
for vs30 in vs30s:
    hazard_curves[vs30]['location_code'] = hazard_curves[vs30]['lat'] + '~' + hazard_curves[vs30]['lon']
    uhs[vs30] = pd.DataFrame({c: pd.Series(dtype=t) for c, t in DTYPE.items()}, index=index)
    idx = 0
    for agg in aggs:
        for loc in locations:
            ind = (hazard_curves[vs30]['location_code'] == loc.code) & (hazard_curves[vs30]['agg'] == agg)
            lat, lon = loc.code.split('~')
            levels = hazard_curves[vs30][ind]['level'].iloc[0]
            imt = list(hazard_curves[vs30][ind]['imt'])
            apoe = np.empty((len(imt), len(hazard_curves[vs30][ind]['apoe'].iloc[0])))
            for i in range(len(imt)):
                apoe[i,:] = hazard_curves[vs30][ind]['apoe'].iloc[i]
            
            period = np.array([period_from_imt(im) for im in imt])
            sorter = np.argsort(period)
            apoe = apoe[sorter, :]
            period = period[sorter]
            imt = [imt_from_period(p) for p in period]
            for poe in poes:
                uhs[vs30].loc[idx, 'lat'] = lat
                uhs[vs30].loc[idx, 'lon'] = lon
                uhs[vs30].loc[idx, 'poe'] = poe
                uhs[vs30].loc[idx, 'agg'] = agg
                uhs[vs30].loc[idx, 'imt'] = np.array(imt)
                uhs[vs30].loc[idx, 'acc'] = compute_hazard_at_poe(levels, apoe, poe, INV_TIME)
                idx += 1

for vs30 in vs30s:
    uhs[vs30][imts] = pd.DataFrame(uhs[vs30].acc.tolist(), index=uhs[vs30].index)
    uhs[vs30].drop(labels = ['imt', 'acc'], axis=1, inplace=True)
    uhs[vs30].sort_values(by=['lat', 'lon','poe','agg'], inplace=True)

    hazard_curves[vs30][levels] = pd.DataFrame(hazard_curves[vs30].apoe.tolist(), index=hazard_curves[vs30].index)
    hazard_curves[vs30].drop(labels = ['level', 'apoe', 'location_code'], axis=1, inplace=True)

# add to csvs
for vs30 in vs30s:
    for imt in imts:
        filename = f'hazard_curves_{vs30}_{imt}.csv'
        ind = hazard_curves[vs30]['imt'] == imt
        hazard_curves[vs30][ind].to_csv(filename, index=False)

    for poe in poes: 
        filename = f'uhs_{vs30}_{poe}.csv'
        ind = uhs[vs30]['poe'] == poe
        uhs[vs30][ind].to_csv(filename, index=False)

# hazard curves
# location, IMT, apoe at level0, apoe at level1, apoe at level2, . . .
# one file for each IMT. include all locations. name file for IMT

# UHS 
# location, poe in 50, acc at IMT0, acc at IMT1, . . . 

# add csv to zip?