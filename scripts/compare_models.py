import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from nzshm_common.location.location import LOCATIONS_BY_ID
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids.region_grid import load_grid
from toshi_hazard_store.query_v3 import get_hazard_curves


from nzshm_hazlab.plotting_functions import plot_hazard_curve_fromdf, plot_spectrum_fromdf

AGGS = ["mean", "cov", "std", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]
IMTS = ['PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.7)','SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)', 'SA(4.0)', 'SA(5.0)', 'SA(6.0)','SA(7.5)','SA(10.0)']
VS30 = 400
POES = [0.1,0.02]
INVESTIGATION_TIME = 50
PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
FIG_DIR = "/home/chrisdc/NSHM/oqresults/hik_error"

def get_hazard(hazard_id, locs, vs30, imts, aggs):


    res = next(get_hazard_curves([locs[0]], [vs30], [hazard_id], [imts[0]], ['mean']))
    num_levels = len(res.values)

    columns = ['lat', 'lon', 'imt', 'agg', 'level', 'hazard']
    index = range(len(locs) * len(imts) * len(aggs) * num_levels)
    hazard_curves = pd.DataFrame(columns=columns, index=index)
    ind = 0
    for i,res in enumerate(get_hazard_curves(locs, [vs30], [hazard_id], imts, aggs)):
        lat = f'{res.lat:0.3f}'
        lon = f'{res.lon:0.3f}'
        for value in res.values:
            hazard_curves.loc[ind,'lat'] = lat
            hazard_curves.loc[ind,'lon'] = lon
            hazard_curves.loc[ind,'imt'] = res.imt
            hazard_curves.loc[ind,'agg'] = res.agg
            hazard_curves.loc[ind,'level'] = value.lvl
            hazard_curves.loc[ind,'hazard'] = value.val
            ind += 1

    return hazard_curves


def location_str(location_key):
    return f"{LOCATIONS_BY_ID[location_key]['latitude']:0.3f}~{LOCATIONS_BY_ID[location_key]['longitude']:0.3f}"


def plot_hcurve(loc_key, imt):

    plt.close()

    ref_lines = []
    for poe in POES:
            ref_line = dict(type = 'poe',
                            poe = poe,
                            inv_time = INVESTIGATION_TIME)
            ref_lines.append(ref_line)

    bounds = bandws['name']
    bandw = bandws['values']
    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
    fig.set_facecolor('white')

    handles = []
    labels = []
    for i, hazard_model in enumerate(hazard_models):
        handles.append(
            plot_hazard_curve_fromdf(hazard_model['data'], location_str(loc_key), imt, ax, xlim, ylim,
                                        xscale=xscale,central='mean',
                                        bandw=bandw,ref_lines=ref_lines,
                                        color=colors[i]))
        labels.append(hazard_model['name'])


    plt.legend(handles,labels)
    title = f"{LOCATIONS_BY_ID[loc_key]['name']} vs30={VS30} {imt} {bounds}"
    ax.set_title(title)

    plot_name = '_'.join( (LOCATIONS_BY_ID[loc_key]['name'],str(VS30),imt,bounds) ) + '.png'
    file_path = Path(FIG_DIR,plot_name) 
    # plt.savefig(file_path)
    fig.savefig(file_path)

    # plt.show()

    return fig, ax

def plot_spectra(loc_key, poe):

    plt.close()

    bounds = bandws['name']
    bandw = bandws['values']

    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
    fig.set_facecolor('white')

    handles = []
    labels = []
    for i, hazard_model in enumerate(hazard_models):
        handles.append(
            plot_spectrum_fromdf(hazard_model['data'], location_str(loc_key), poe, INVESTIGATION_TIME, ax, bandw=True, color=colors[i])
        )
        labels.append(hazard_model['name'])

    plt.legend(handles, labels)
    title = f'{LOCATIONS_BY_ID[loc_key]["name"]} {poe*100:.0f}% in 50 years {bounds}'
    ax.set_title(title)
    # ax.set_ylim(ylim)
    ax.set_yscale('log')
    ax.set_ylim([1e-2, 10])


    plot_name = 'spectra_log_' + '_'.join( (LOCATIONS_BY_ID[loc_key]['name'],str(poe),bounds) ) + '.png'
    file_path = Path(FIG_DIR,plot_name) 
    # plt.savefig(file_path)
    fig.savefig(file_path)

    # plt.show()

    return fig, ax

hazard_models = [
    dict(id='NSHM_v1.0.1',name='Origional Hik Geomoetry'),
    dict(id = "NSHM_v1.0.2", name = 'Corrected Hik Geometry'),
]

# location_keys = ['GIS', 'AKL', 'KKE']
location_keys = ['TRG']
location_strs =  [location_str(k) for k in location_keys]

for hazard_model in hazard_models:
    print(f'loading hazard model {hazard_model}')
    hazard_model['data'] = get_hazard(hazard_model['id'], location_strs, VS30, IMTS, AGGS)


# ========= HAZARD CURVES ============= #

# ---- parameters ---- #
imts = ["PGA", "SA(1.5)", "SA(3.0)", "SA(5.0)"]
bandws = {'name':'0.5,10,90,99.5', 'values':{'lower2':'0.05','lower1':'0.1','upper1':'0.9','upper2':'0.95'}}
colors = ['#1b9e77', '#d95f02', '#7570b3']
xscale = 'log'
xlim = [1e-2,1e1]
ylim = [1e-6,1]

# ---- plot ---- #

for loc_key in location_keys:
    print(f'plotting {loc_key} ... ')
    for imt in imts:
        print(f'plotting {imt}')
        fig, ax = plot_hcurve(loc_key, imt)


# ========= SPECTRA ============= #


# ---- parameters ---- #
# ylim = [0,5]
for loc_key in location_keys:
    print(f'plotting {loc_key} ... ')
    for poe in POES:
        print(f'plotting poe {poe}')
        fig, ax = plot_spectra(loc_key, poe)