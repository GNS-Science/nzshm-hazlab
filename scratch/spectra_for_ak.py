import pandas as pd

from nzshm_common.location.code_location import CodedLocation
from nzshm_common.location.location import location_by_id

from nzshm_hazlab.data_functions import compute_hazard_at_poe
from nzshm_hazlab.store.curves import get_hazard
from nzshm_hazlab.base_functions import period_from_imt, imt_from_period

def get_spectra_df(vs30s, poes, imts):

    dtype = {'lat':'str', 'lon':'str', 'poe': 'float', 'vs30': 'float', 'agg':'str', 'period': 'float64', 'imtl':'float64'}
    index = range(len(vs30s) * len(poes) * len(imts))
    return pd.DataFrame({c: pd.Series(dtype=t) for c, t in dtype.items()}, index=index)


hazard_model_id = 'NSHM_v1.0.4'
location_id = 'WLG'
location = CodedLocation(
    location_by_id(location_id)['latitude'],
    location_by_id(location_id)['longitude'],
    0.001
)
# imts = ['PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.7)','SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)', 'SA(4.0)', 'SA(5.0)', 'SA(6.0)','SA(7.5)', 'SA(10.0)']
era_measures_orig = [
    'PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)',
    'SA(0.5)', 'SA(0.7)', 'SA(1.0)', 'SA(1.5)', 'SA(2.0)',
    'SA(3.0)', 'SA(4.0)', 'SA(5.0)', 'SA(6.0)','SA(7.5)',
    'SA(10.0)'
]
era_measures_new = [
    "SA(0.15)",	"SA(0.25)", "SA(0.35)",	"SA(0.6)", "SA(0.8)",
    "SA(0.9)", "SA(1.25)", "SA(1.75)", "SA(2.5)", "SA(3.5)",
    "SA(4.5)"
]
imts = era_measures_orig + era_measures_new
periods = [period_from_imt(imt) for imt in imts]
periods.sort()
imts = [imt_from_period(period) for period in periods]

agg = 'mean'
vs30s = [150, 200, 225, 250, 275, 300, 350, 400, 500, 750,1000,1500]
lat, lon = location.code.split('~')
poes = [0.02, 0.10, 0.86]
inv_time = 50
spectra = get_spectra_df(vs30s, poes, imts)

ind = 0
for vs30 in vs30s:
    hazard_data = get_hazard(hazard_model_id, vs30, [location], imts, [agg])
    for poe in poes:
        hd_filt = hazard_data.loc[ (hazard_data['lat'] == lat) & (hazard_data['lon'] == lon)]
        for imt in imts:
            values = hd_filt.loc[(hd_filt['imt'] == imt) & (hd_filt['agg'] == agg),'apoe'].item()
            levels = hd_filt.loc[(hd_filt['imt'] == imt) & (hd_filt['agg'] == agg),'level'].item()
            imtl = compute_hazard_at_poe(levels,values,poe,inv_time)
            spectra.loc[ind, 'lat'] = lat
            spectra.loc[ind, 'lon'] = lon
            spectra.loc[ind, 'poe'] = poe
            spectra.loc[ind, 'vs30'] = vs30
            spectra.loc[ind, 'agg'] = agg
            spectra.loc[ind, 'period'] = period_from_imt(imt)
            spectra.loc[ind, 'imtl'] = imtl
            ind += 1

spectra.to_csv('wellington_spectra.csv')