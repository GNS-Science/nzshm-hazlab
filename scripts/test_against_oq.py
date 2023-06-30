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

xlim = [1e-2,5]
xlim_res = [1e-4,5]
ylim = [1e-6,1]
# ylim_res = [-1, 1]
ylim_res = [0.99, 1.01]

def lat_lon(id):
    return (location_by_id(id)['latitude'], location_by_id(id)['longitude'])

def read_csv(csv_path, location):
    lat, lon = (location.lat, location.lon)
    with open(csv_path,'r') as csvfile:
        reader = csv.reader(csvfile)
        junk = next(reader)
        header = next(reader)
        levels_OQ = np.array([float(l[4:]) for l in header[4:]])
        for row in reader:
            longitude = float(row[1])
            latitude = float(row[2])
            if (longitude==lon) & (latitude==lat):
                hazard_OQ = np.array(list(map(float,row[4:]) ))

    return levels_OQ, hazard_OQ

def load_oq_hazard(oq_output_path, location):
    oq_hazard_mean_filepath = Path(oq_output_path, 'hazard_curve-mean-PGA_13.csv')
    oq_hazard_10_filepath = Path(oq_output_path, 'quantile_curve-0.1-PGA_13.csv')
    oq_hazard_90_filepath = Path(oq_output_path, 'quantile_curve-0.9-PGA_13.csv')
    levels_OQ, hazard_OQ_mean = read_csv(oq_hazard_mean_filepath, location)
    junk, hazard_OQ_10 = read_csv(oq_hazard_10_filepath, location)
    junk, hazard_OQ_90 = read_csv(oq_hazard_90_filepath, location)
    oq_hazard = {
        'levels': levels_OQ,
        'mean': hazard_OQ_mean,
        '0.1': hazard_OQ_10,
        '0.9': hazard_OQ_90,
    }
    return oq_hazard

def load_ths_hazard(model_id, location, vs30, imt, aggs):
    hazard_THS = get_hazard(model_id, vs30, [location], [imt], aggs)
    levels_THS = hazard_THS[hazard_THS['agg'] == 'mean']['level'].iloc[0]
    hazard_THS_mean = hazard_THS[hazard_THS['agg'] == 'mean']['apoe'].iloc[0]
    hazard_THS_10 = hazard_THS[hazard_THS['agg'] == '0.1']['apoe'].iloc[0]
    hazard_THS_90 = hazard_THS[hazard_THS['agg'] == '0.9']['apoe'].iloc[0]

    ths_hazard = { 
        'levels': levels_THS,
        'mean': hazard_THS_mean,
        '0.1': hazard_THS_10,
        '0.9': hazard_THS_90,
    }

    return ths_hazard

def plot_hcurves(fig, ax, ths_hazard, oq_hazard, location_name, labels):

    fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
    fig.set_facecolor('white')
    # ax.plot(oq_hazard['levels'], oq_hazard['mean'], lw=7, color=color_oq, label='OpenQuake')
    # breakpoint()
    ax.plot(ths_hazard['levels'], ths_hazard['mean'], lw=4, color=color_ths, label='This Study (THS)')
    ax.plot(oq_hazard['levels'], oq_hazard['mean'], lw=6, linestyle='--', color=color_oq, label='OpenQuake')

    ax.plot(ths_hazard['levels'], ths_hazard['0.1'], lw=2, color=color_ths)
    ax.plot(oq_hazard['levels'], oq_hazard['0.1'], linestyle='--', lw=4, color=color_oq)

    ax.plot(ths_hazard['levels'], ths_hazard['0.9'], lw=2, color=color_ths)
    ax.plot(oq_hazard['levels'] ,oq_hazard['0.9'], linestyle='--', lw=4, color=color_oq)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.grid(color='lightgray')
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
        ax.set_ylabel('apoe ratio [OQ / THS]', fontsize=fonts_axis_label)
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

location_ids = ['AKL', 'WLG', 'CHC', 'DUD']
model_id = 'TEST_AGAINST_OQ'
vs30 = 400
# lon = 174.78
# lat = -41.3
imt = 'PGA'
aggs = ['0.1', 'mean', '0.9']
color_oq = 'tab:blue'
color_ths = 'tab:orange'

oq_output_path = Path("/home/chrisdc/NSHM/oqruns/Test_Against_OQ/output")

ths_hazard = {}
oq_hazard = {}
fig, ax = plt.subplots(2,2)
for c, location_id in enumerate(location_ids):
    i = c%2
    j = int(c/2)
    location = CodedLocation(*lat_lon(location_id), 0.001)
    ths_hazard[location_id] = load_ths_hazard(model_id, location, vs30, imt, aggs)
    oq_hazard[location_id] = load_oq_hazard(oq_output_path, location)

    # labels = True if (i==1) & (j==0) else False
    labels = False
    plot_hcurves(fig, ax[i,j], ths_hazard=ths_hazard[location_id], oq_hazard=oq_hazard[location_id], location_name=location_by_id(location_id)['name'], labels=labels)
fig.supxlabel(f'Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
fig.supylabel('Annual Probability of Exceedance', fontsize=fonts_axis_label)


fig, ax = plt.subplots(2,2)
# aggs = ['mean', '0.1', '0.9']
aggs = ['mean']
oq_hazard_ = {'AKL': oq_hazard['AKL']}
for c, k in enumerate(oq_hazard.keys()):
    i = c%2
    j = int(c/2)
    # labels = True if (i==1) & (j==0) else False
    labels = False
    oq_hazard_ = {k: oq_hazard[k]}
    for agg in aggs:
        residuals = calculate_resduals(oq_hazard=oq_hazard_, ths_hazard=ths_hazard, agg=agg)
        # title = f'Resduals for {agg}'
        title = location_name=location_by_id(k)['name']
        label = agg
        plot_residuals(fig, ax[i,j], levels=residuals['levels'], residuals=residuals['residuals'], title=title, label=label, labels=labels)
fig.supxlabel('Shaking Intensity, %s [g]'%imt, fontsize=fonts_axis_label)
fig.supylabel('apoe ratio [OQ / THS]', fontsize=fonts_axis_label)
# ax.set_title('Probability Residuals')
# ax.legend()
plt.show()
