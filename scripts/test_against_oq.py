import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from nzshm_common.location.code_location import CodedLocation
from nzshm_common.location.location import location_by_id
from nzshm_hazlab.store.curves import get_hazard

PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
fonts_axis_label = 14 
fonts_title = 12

xlim = [1e-4,5]
xlim_res = [1e-4,5]
ylim = [1e-6,1]
# ylim_res = [-1, 1]
ylim_res = [0.8, 1.1]

def lat_lon(id):
    return (location_by_id(id)['latitude'], location_by_id(id)['longitude'])

def read_csv(csv_path, location):
    lat, lon = (location.lat, location.lon)
    with open(csv_path,'r') as csvfile:
        reader = csv.reader(csvfile)
        junk = next(reader)
        header = next(reader)
        levels_OQ = np.array([float(l[4:]) for l in header[3:]])
        for row in reader:
            longitude = float(row[0])
            latitude = float(row[1])
            if (longitude==lon) & (latitude==lat):
                hazard_OQ = np.array(list(map(float,row[3:]) ))
    return levels_OQ, hazard_OQ

def load_oq_hazard(oq_output_path, location, imt, aggs):
    oq_id = sorted(Path(oq_output_path).glob("*csv"))[0].name.split('_')[-1][0:-4]
    oq_hazard = {}

    for agg in aggs:
        if agg == 'mean':
            oq_hazard_filepath = Path(oq_output_path, f'hazard_curve-{agg}-{imt}_{oq_id}.csv')
        else:
            oq_hazard_filepath = Path(oq_output_path, f'quantile_curve-{agg}-{imt}_{oq_id}.csv')
        levels, hazard = read_csv(oq_hazard_filepath, location)
        if 'levels' not in oq_hazard:
            oq_hazard['levels'] = levels
        oq_hazard[agg] = hazard
    return oq_hazard

def load_ths_hazard(model_id, location, vs30, imt, aggs):
    hazard_THS = get_hazard(model_id, vs30, [location], [imt], aggs)
    ths_hazard = {}
    for agg in aggs:
        if 'levels' not in ths_hazard:
            levels_THS = hazard_THS[hazard_THS['agg'] == agg]['level'].iloc[0]
            ths_hazard['levels'] = levels_THS
        ths_hazard[agg] = hazard_THS[hazard_THS['agg'] == agg]['apoe'].iloc[0]

    return ths_hazard

def plot_hcurves(fig, ax, ths_hazard, oq_hazard, aggs, location_name, labels, legend=False):

    fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
    fig.set_facecolor('white')
    # ax.plot(oq_hazard['levels'], oq_hazard['mean'], lw=7, color=color_oq, label='OpenQuake')
    # breakpoint()
    for i, agg in enumerate(aggs):
        if i == 0:
            ax.plot(ths_hazard['levels'], ths_hazard[agg], lw=1, color=color_ths, label='THP')
            ax.plot(oq_hazard['levels'], oq_hazard[agg], lw=2, linestyle='--', color=color_oq, label='OQ')
        else:
            ax.plot(ths_hazard['levels'], ths_hazard[agg], lw=1, color=color_ths)
            ax.plot(oq_hazard['levels'], oq_hazard[agg], lw=2, linestyle='--', color=color_oq)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.grid(color='lightgray')

    if legend:
        ax.legend(handlelength=5)

    if labels:
        ax.set_xlabel('Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
        ax.set_ylabel('Annual Probability of Exceedance', fontsize=fonts_axis_label)

    ax.set_title(f'{location_name}', fontsize=fonts_title, loc='left')


def calculate_resduals(oq_hazard, ths_hazard, agg):
    levels = np.array([])
    residuals = np.array([])
    for location_id in oq_hazard.keys():
        levels = np.hstack((levels, oq_hazard[location_id]['levels']))
        residuals = np.hstack(
            (
                residuals,
                # (oq_hazard[location_id][agg] - ths_hazard[location_id][agg])/oq_hazard[location_id][agg] * 100.0
                (oq_hazard[location_id][agg] / ths_hazard[location_id][agg])
            )
        )

    return {'levels': levels, 'residuals': residuals}

def get_all_residuals(oq_hazard, ths_hazard, agg, location_ids):
   pass 
    # levels = []
    # residuals = []
    

def plot_residuals(fig, ax, levels, residuals, title, label, labels):

    fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
    fig.set_facecolor('white')

    ax.plot(levels, residuals, linestyle='none', marker='o', markersize = 7, label=label)
    if labels:
        ax.set_xlabel('Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
        ax.set_ylabel('APOE ratio [traditional / new]', fontsize=fonts_axis_label)
    ax.grid(color='lightgray')
    ax.set_title(title, fontsize=fonts_title, loc='left')

    ax.set_xscale('log')
    ax.set_xlim(xlim_res)
    ax.set_ylim(ylim_res)


# ███    ███  █████  ██ ███    ██ 
# ████  ████ ██   ██ ██ ████   ██ 
# ██ ████ ██ ███████ ██ ██ ██  ██ 
# ██  ██  ██ ██   ██ ██ ██  ██ ██ 
# ██      ██ ██   ██ ██ ██   ████ 

# location_ids = ['AKL', 'WLG', 'CHC', 'DUD']
location_ids = ['AKL', 'WLG', 'KKE', 'WHO']
# model_id = 'TEST_AGAINST_OQ_V2'
model_id = 'NSHM_v1.0.4'
vs30 = 750
# lon = 174.78
# lat = -41.3
imt = 'SA(3.0)'
aggs = ['mean', '0.01', '0.05', '0.1', '0.2', '0.5', '0.8', '0.9', '0.95', '0.99']
color_oq = 'tab:blue'
color_ths = 'tab:orange'

# oq_output_path = Path("/home/chrisdc/NSHM/oqruns/Test_Against_OQ_v2/output_userates")
oq_output_path = Path("/home/chrisdc/mnt/glacier/oqruns/full-model/output/site36_750")

ths_hazard = {}
oq_hazard = {}
fig, ax = plt.subplots(2,2)
for c, location_id in enumerate(location_ids):
    i = c%2
    j = int(c/2)
    location = CodedLocation(*lat_lon(location_id), 0.001)
    ths_hazard[location_id] = load_ths_hazard(model_id, location, vs30, imt, aggs)
    oq_hazard[location_id] = load_oq_hazard(oq_output_path, location, imt, aggs)

    # labels = True if (i==1) & (j==0) else False
    labels = False
    legend = True if c==0 else False
    plot_hcurves(fig, ax[i,j], ths_hazard=ths_hazard[location_id],
                 oq_hazard=oq_hazard[location_id],
                 aggs=aggs,
                 location_name=location_by_id(location_id)['name'],
                 labels=labels, legend=legend)
fig.supxlabel(f'Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
fig.supylabel('Annual Probability of Exceedance', fontsize=fonts_axis_label)


fig, ax = plt.subplots(2,2)
aggs = ['mean']
for c, k in enumerate(oq_hazard.keys()):
    i = c%2
    j = int(c/2)
    # labels = True if (i==1) & (j==0) else False
    labels = False
    for agg in aggs:
        residuals = calculate_resduals(oq_hazard={k: oq_hazard[k]}, ths_hazard=ths_hazard, agg=agg)
        # title = f'Resduals for {agg}'
        title = location_name=location_by_id(k)['name']
        label = agg
        plot_residuals(fig, ax[i,j], levels=residuals['levels'], residuals=residuals['residuals'], title=title, label=label, labels=labels)
fig.supxlabel('Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
fig.supylabel('APOE ratio [traditional / new]', fontsize=fonts_axis_label)
# ax.set_title('Probability Residuals')
# ax.legend()
plt.show()
