import os
from pathlib import Path
from nzshm_common.location.location import LOCATION_LISTS, location_by_id
from nzshm_common.location import CodedLocation
from nzshm_hazlab.store.curves import get_hazard, get_hazard_from_oqcsv
from nzshm_hazlab.plotting_functions import plot_hazard_curve
import matplotlib.pyplot as plt
from typing import Any

from nzshm_hazlab.locations import get_locations, lat_lon

CODED_LOCS = [CodedLocation(*lat_lon(key), 0.001) for key in LOCATION_LISTS["ALL"]["locations"]]

resolution = 0.001
INVESTIGATION_TIME = 50
PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
# colors = ['black', '#1b9e77', '#d95f02', '#7570b3','k']
colors = ['black', 'tab:orange', 'tab:green', 'tab:red', 'tab:blue']

xscale = 'log'
xlim = [1e-2,10]
# xlim = [0, 3.5]
# xlim = [0,3]
ylim = [1e-11, 1]

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


def location_2_dict(loc: CodedLocation) -> str:

    if loc in CODED_LOCS:
       ind = CODED_LOCS.index(loc)
       return location_by_id(LOCATION_LISTS["ALL"]["locations"][ind])
    return dict(
        id=loc.code,
        name=loc.code,
        latitude=loc.lat,
        longitude=loc.lon,
    )
    

def ref_lines(poes):
    refls = []
    for poe in poes:
        ref_line = dict(type = 'poe',
                        poe = poe,
                        inv_time = INVESTIGATION_TIME)
        refls.append(ref_line)
    return refls






error_bounds = {'lower2':'0.025','lower1':'0.1','upper1':'0.9','upper2':'0.975'}
# error_bounds = {}
# aggs = list(error_bounds.values()) + ['mean']
aggs = ['0.1', '0.5', '0.9', 'mean']
agg = 'mean'

hazard_models = [
    dict(id='NSHM_v1.0.4', name='NZ NSHM 2022 Official', type='thp'),
    # dict(id='/home/chrisdc/mnt/glacier_work/oqruns/otago/outputs/geodetic/', name='Otago IFM Geodetic', type='oq', run_num=12),
    # dict(id='/home/chrisdc/mnt/glacier_work/oqruns/otago/outputs/geologic/', name='Otago IFM Geologic', type='oq', run_num=13),
    # dict(id='/home/chrisdc/mnt/glacier_work/oqruns/otago/outputs/full_model/', name='NZ NSHM 2022', type='oq', run_num=19),
    dict(id='/home/chrisdc/mnt/glacier_work/oqruns/aecom_mismatch/output_prob/', name='Aecom files OQ v3.20.1', type='oq', run_num=25),
    # dict(id='/home/chrisdc/mnt/glacier_work/oqruns/aecom_mismatch/output_no_round_ref/', name='Aecom files OQ v3.20.1', type='oq', run_num=26),
    # dict(id='/home/chrisdc/mnt/glacier_work/oqruns/aecom_mismatch/output/', name='Aecom files OQ v3.20.1', type='oq', run_num=27),
    # dict(id='/home/chrisdc/mnt/glacier_work/oqruns/aecom_mismatch/output_400/', name='Aecom files OQ v3.20.1', type='oq', run_num=27),
    # dict(id='/home/chrisdc/mnt/glacier_work/oqruns/test-oq-versions/v3.20.1/', name='OQ-v3.20.1', type='oq', run_num=1),
    # dict(id='/home/chrisdc/mnt/glacier_work/oqruns/test-oq-versions/v3.21.0/', name='OQ-v3.21.0', type='oq', run_num=1),
    # dict(id='/home/chrisdc/mnt/glacier_work/oqruns/test-oq-versions/v3.22.1/', name='OQ-v3.22.1', type='oq', run_num=1),
    # dict(id='/home/chrisdc/mnt/glacier_work/oqruns/test-oq-versions/v3.23.1/', name='OQ-v3.23.1', type='oq', run_num=1),
]

# location_codes = ["TP"]
# locations = get_locations(location_codes)[0:1] + get_locations(["-44.3~170.8"])
# location_codes = ["WLG", "DUD", "CHC", "AKL"]
# location_codes = ["/home/chrisdc/NSHM/oqruns/RUNZI-MAIN-HAZARD/WeakMotionSiteLocs_SHORT.csv"]
# location_codes = ["-42.311~172.218", "-38.826~177.536", "-38.262~175.010"]
# location_codes = ["WLG"]
# location_codes = ["-34.500~173.000"]
# location_codes = ["DUD"]
# location_codes = ["-43.000~172.8"]
location_codes = ["-38.000~175.600"]
locations = get_locations(location_codes)

imts = ["PGA"]
poes = [0.1, 0.02]
vs30s = [500]
no_cache = True
fig_dir = Path('/home/chrisdc/NSHM/oqresults/32bit')
save_figs = False

if no_cache and os.environ.get('NZSHM22_HAZARD_STORE_LOCAL_CACHE'):
    del os.environ['NZSHM22_HAZARD_STORE_LOCAL_CACHE']

for model in hazard_models:
    model['hcurves'] = {}
    for vs30 in vs30s:
        if model['type'] == 'oq':
            model['hcurves'][vs30] = get_hazard_from_oqcsv(model['id'], imts, agg, model['run_num'])
        else:
            model['hcurves'][vs30] = get_hazard(model['id'], vs30, locations, imts, aggs)


for loc in locations:
    loc_dict = location_2_dict(loc)
    loc_key, loc_name = loc_dict["id"], loc_dict["name"]
    for imt in imts:
        for vs30 in vs30s:
            fig, ax = plt.subplots(1,1)
            fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
            fig.set_facecolor('white')
            # title = f'{loc_name} {imt}, Vs30 = {vs30}m/s'
            title = ''
            for i, model in enumerate(hazard_models):
                if model['type'] == 'oq':
                    error_bounds_tmp = dict()
                    linestyle = '--'
                else:
                    error_bounds_tmp = error_bounds
                    error_bounds_tmp = None
                    linestyle = '-'
                plot_hazard_curve(
                    model['hcurves'][vs30], loc, imt, ax, xlim, ylim,
                    xscale=xscale,
                    central=agg,
                    ref_lines=ref_lines(poes),
                    color=colors[i],
                    custom_label=model['name'],
                    title=title,
                    bandw=error_bounds_tmp,
                    linestyle=linestyle,
                )

            # fname = f'{location_name}_{imt}_{vs30}.png' 
            ax.set_title(loc_name)
            if save_figs:
                fname = f'{loc_key}_{imt}_{vs30}.png' 
                fig.savefig(Path(fig_dir, fname))
                plt.close()
            else:
                plt.show()

        # fix, ax = plt.subplots(1,1)
        # plot_diff(hazard_models[0]['hcurves'], hazard_models[1]['hcurves'], loc, imt, ax)
