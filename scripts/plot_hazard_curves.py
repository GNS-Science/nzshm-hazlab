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
xlim = [1e-4,1e1]
# xlim = [0,3]
ylim = [1e-8,1]

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

error_bounds = {'lower2':'0.01','lower1':'0.1','upper1':'0.9','upper2':'0.99'}
# error_bounds = {}
aggs = list(error_bounds.values()) + ['mean']

hazard_models = [
    dict(id='NSHM_v1.0.2', name='v1.0.2'),
    dict(id='NSHM_v1.0.4', name='v1.0.4'),
]

location_keys = ['WLG']
# location_keys = LOCATION_LISTS['NZ']['locations'].copy()
# if 'WRE' in location_keys:
#     location_keys.remove('WRE')
locations = [key_2_location(k) for k in location_keys]

# imts = ['PGA', 'SA(3.0)','SA(5.0)', 'SA(10.0)']
# imts = ['PGA','SA(0.5)', 'SA(1.5)', 'SA(3.0)', 'SA(5.0)', 'SA(10.0)']
imts = ['SA(1.5)']
# imts = ['SA(3.0)']
poes = [0.1, 0.02]
vs30 = 175 

for model in hazard_models:
    model['hcurves'] = get_hazard(model['id'], vs30, locations, imts, aggs)

for loc_key in location_keys:
    loc = key_2_location(loc_key)
    location_name = location_by_id(loc_key)['name'] if location_by_id(loc_key) else loc_key
    for imt in imts:
        fig, ax = plt.subplots(1,1)
        fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
        fig.set_facecolor('white')
        title = f'{location_name} {imt}, Vs30 = {vs30}m/s'
        for i, model in enumerate(hazard_models):
            plot_hazard_curve(
                model['hcurves'], loc, imt, ax, xlim, ylim,
                xscale=xscale,central='mean',
                ref_lines=ref_lines(poes),
                color=colors[i],
                custom_label=model['name'],
                title=title,
                bandw=error_bounds
            )

        fname = f'{location_name}_{imt}_{vs30}.png' 
        fig.savefig(Path(fig_dir, fname))
        # plt.close()

        fix, ax = plt.subplots(1,1)
        plot_diff(hazard_models[0]['hcurves'], hazard_models[1]['hcurves'], loc, imt, ax)

        plt.show()