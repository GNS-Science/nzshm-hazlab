import os
from pathlib import Path
from nzshm_common.location.location import LOCATION_LISTS, location_by_id
from nzshm_common.location import CodedLocation
from nzshm_hazlab.store.curves import get_hazard
from nzshm_hazlab.plotting_functions import plot_hazard_curve
import matplotlib.pyplot as plt
from typing import Any



resolution = 0.001
INVESTIGATION_TIME = 50
PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
colors = ['#1b9e77', '#d95f02', '#7570b3','k']
xscale = 'log'
xlim = [1e-2,1e1]
# xlim = [0,3]
ylim = [1e-6,1]

def plot_diff(model0, model1, loc, imt, ax):

    lat, lon = loc.code.split('~')
    m0 = model0[(model0['lat'] == lat) & (model0['lon'] == lon) & (model0['imt'] == imt) & (model0['agg'] == 'mean')]
    m1 = model1[(model0['lat'] == lat) & (model1['lon'] == lon) & (model1['imt'] == imt) & (model1['agg'] == 'mean')]

    x = m0['level'].to_numpy()
    y0 = m0['apoe'].to_numpy()
    y1 = m1['apoe'].to_numpy()
    breakpoint()
    ax.plot(x,(y1-y0)/y0)
    ax.grid(color='lightgray')
    ax.set_xscale('log')

def key_2_location(key: Any) -> CodedLocation:

    if '~' in key:
        lat, lon = map(float, key.split('~'))
        location = CodedLocation(lat, lon, resolution)
    elif location_by_id(key):
        location = CodedLocation(
            location_by_id(key)['latitude'],
            location_by_id(key)['longitude'],
            resolution
        )
    elif type(key) == tuple:
        location = CodedLocation(key[0], key[1], resolution)
    else:
        raise Exception('key %s not a useable type' % key)
    
    return location

def ref_lines(poes):
    refls = []
    for poe in poes:
        ref_line = dict(type = 'poe',
                        poe = poe,
                        inv_time = INVESTIGATION_TIME)
        refls.append(ref_line)
    return refls

fig_dir = Path('/home/chrisdc/NSHM/oqresults/v1.0.3')

# error_bounds = {'lower2':'0.01','lower1':'0.1','upper1':'0.9','upper2':'0.99'}
error_bounds = {}
aggs = list(error_bounds.values()) + ['mean']

hazard_models = [
    # dict(id='NSHM_v1.0.2', name='v1.0.0'),
    # dict(id='TEST', name='TEST'),
    # dict(id='NSHM_v1.0.4_mcverry', name='SRM22 + McVerry'),
    # dict(id='NSHM_v1.0.4', name='NZ NSHM 2022'),
    # dict(id='NSHM_v1.0.4_ST_cruNlo', name='Crustal s = 0.66'),
    # dict(id='NSHM_v1.0.4_ST_cruNmid', name='Crustal s = 1.0'),
    # dict(id='NSHM_v1.0.4_ST_cruNhi', name='Crustal s = 1.41'),
    # dict(id='NSHM_v1.0.4_ST_subNlo', name='Hikurangi s = 0.42'),
    # dict(id='NSHM_v1.0.4_ST_subNmid', name='Hikurangi s = 1.0'),
    # dict(id='NSHM_v1.0.4_ST_subNhi', name='Hikurangi s = 1.58'),
    # dict(id='NSHM_v1.0.4_ST_allNlo', name='lower N scaling'),
    # dict(id='NSHM_v1.0.4_ST_allNmid', name='mid N scaling'),
    # dict(id='NSHM_v1.0.4_ST_allNhi', name='upper N scaling'),
    # dict(id='NSHM_v1.0.1_CRUsens_baseline_iso', name='Crustal baseline Iso'),
    # dict(id='NSHM_v1.0.1_CRUsens_baseline', name='Crustal baseline'),
    # dict(id='NSHM_v1.0.1_sens_nopaleo', name='No Paleo'),
    # dict(id='NSHM_v1.0.1_sens_nopaleo_iso', name='No Paleo Iso'),
    dict(id='NSHM_v1.0.4_ST_crubhi_iso', name='CRU b high'),
    dict(id='NSHM_v1.0.4_ST_geologic_iso', name='Geologic'),
    dict(id='NSHM_v1.0.4_ST_geodetic_iso', name='Geodetic'),

]

# location_keys = ['WLG','AKL','CHC','DUD']
# location_keys = ['srg_164']
# location_keys = ["GIS", "NPE"]
location_keys = ["WLG"]


# gisbourne =  CodedLocation(-38.65,178.0,0.001)
# napier = CodedLocation(-39.5,176.9,0.001)
# locations = [gisbourne, napier]
# coded_locations = [CodedLocation(-37.2, 175, 0.001), CodedLocation(-37.1, 175.1, 0.001)]
coded_locations = []
locations = [key_2_location(k) for k in location_keys] + coded_locations

imts = ["PGA"]
poes = [0.1, 0.02]
# vs30s = [250, 400]
vs30s = [400]
no_cache = False

if no_cache and os.environ.get('NZSHM22_HAZARD_STORE_LOCAL_CACHE'):
    del os.environ['NZSHM22_HAZARD_STORE_LOCAL_CACHE']

for model in hazard_models:
    model['hcurves'] = {}
    for vs30 in vs30s:
        model['hcurves'][vs30] = get_hazard(model['id'], vs30, locations, imts, aggs)

for loc_key in location_keys:
# for loc in locations:
    loc = key_2_location(loc_key)
    location_name = location_by_id(loc_key)['name'] if location_by_id(loc_key) else loc_key
    # location_name = loc.code
    for imt in imts:
        for vs30 in vs30s:
            fig, ax = plt.subplots(1,1)
            fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
            fig.set_facecolor('white')
            title = f'{location_by_id(loc_key)["name"]} {imt}, Vs30 = {vs30}m/s'
            for i, model in enumerate(hazard_models):
                plot_hazard_curve(
                    model['hcurves'][vs30], loc, imt, ax, xlim, ylim,
                    xscale=xscale,central='mean',
                    ref_lines=ref_lines(poes),
                    color=colors[i],
                    custom_label=model['name'],
                    title=title,
                    bandw=error_bounds
                )

            # fname = f'{location_name}_{imt}_{vs30}.png' 
            fname = f'{loc_key}_{imt}_{vs30}.png' 

        # fig.savefig(Path(fig_dir, fname))
        # plt.close()

        # fix, ax = plt.subplots(1,1)
        # plot_diff(hazard_models[0]['hcurves'], hazard_models[1]['hcurves'], loc, imt, ax)

            plt.show()