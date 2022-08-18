from dis import dis
import json
import geopandas
import csv
import io
from pathlib import Path
from zipfile import ZipFile
from collections import namedtuple
import matplotlib.pyplot as plt
import numpy as np

import oq_hazard_report.disagg_plotting_functions as dpf
import oq_hazard_report.disagg_data_functions as ddf


def plot_disagg(mags, dists, rates_int, rates_slab, rates_cru):

    width = 0.1
    depth = 20

    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    fig.set_size_inches(8,8)
    fig.set_facecolor('white')
    islab = rates_slab>0
    icru = rates_cru>0
    iint = rates_int>0
    ax.bar3d(mags[islab],dists[islab],np.zeros_like(rates_slab[islab]),width,depth,rates_slab[islab],color='tab:blue')
    slab_proxy = plt.Rectangle((0, 0), 1, 1, fc='tab:blue')
    ax.bar3d(mags[iint],dists[iint],rates_slab[iint],width,depth,rates_int[iint],color='tab:orange',label='interface')
    int_proxy = plt.Rectangle((0, 0), 1, 1, fc='tab:orange')
    ax.bar3d(mags[icru],dists[icru],rates_slab[icru]+rates_int[icru],width,depth,rates_cru[icru],color='tab:green',label='crustal')
    cru_proxy = plt.Rectangle((0, 0), 1, 1, fc='tab:green')
    ax.legend([slab_proxy,int_proxy,cru_proxy],['Slab','Interface','Crustal'])
    ax.set_xlabel('magnitude')
    ax.set_ylabel('distance (km)')

    return fig, ax


def load_disagg(csv_file_name):

    with open(mag_dist_fn,'r') as csvfile:
        disagg_reader = csv.reader(csvfile)
        junk = next(disagg_reader)
        header = next(disagg_reader)
        DisaggData = namedtuple("DisaggData", header, rename=True)
        mags = []
        dists = []
        rates_slab = []
        rates_cru = []
        rates_int = []

        for row in disagg_reader:
            disagg_data = DisaggData(*row)

            mag = float(disagg_data.mag)
            dist = float(disagg_data.dist)
            rate = float(disagg_data.rlz0)
            trt = disagg_data.trt


            if trt == 'Active Shallow Crust':
                mags.append(mag)
                dists.append(dist)
                rates_cru.append(rate)
                # rates_slab.append(0.0)
                # rates_int.append(0.0)
            elif trt == 'Subduction Interface':
                rates_int.append(rate)
                # rates_slab.append(0.0)
                # rates_cru.append(0.0)
            elif trt == 'Subduction Intraslab':
                rates_slab.append(rate)
                # rates_int.append(0.0)
                # rates_cru.append(0.0)

    mags = np.array(mags)
    dists = np.array(dists)
    rates_int = np.array(rates_int)
    rates_slab = np.array(rates_slab)
    rates_cru = np.array(rates_cru)

    return mags,dists,rates_int,rates_slab,rates_cru






# origional full disagg
mag_dist_fn = '/home/chrisdc/NSHM/Disaggs/rlz_output/Mag_Dist_TRT-0_1.csv'
mags,dists,rates_int,rates_slab,rates_cru = load_disagg(mag_dist_fn)
# fig, ax = plot_disagg(mags, dists, rates_int, rates_slab, rates_cru)
# ax.set_title('Origional')

# mag_dist_fn = '/home/chrisdc/NSHM/Disaggs/oqdata/Disagg_orig_gsim_LT/Mag_Dist_TRT-0_47.csv'
# mags,dists,rates_int,rates_slab,rates_cru = load_disagg(mag_dist_fn)
# fig, ax = plot_disagg(mags, dists, rates_int, rates_slab, rates_cru)
# ax.set_title('Re-Run Origional')

# mag_dist_fn = '/home/chrisdc/NSHM/Disaggs/oqdata/Disagg_AG2020/Mag_Dist_TRT-0_48.csv'
# mags,dists,rates_int,rates_slab,rates_cru = load_disagg(mag_dist_fn)
# fig, ax = plot_disagg(mags, dists, rates_int, rates_slab, rates_cru)
# ax.set_title('Stafford2022, AG2020')


Mags, Dists, Rates_int, Rates_slab, Rates_cru, Rates_tot = ddf.meshgrid_disaggs(mags,dists,rates_int,rates_slab,rates_cru)
fig, ax = dpf.plot_disagg2d(Mags, Dists, Rates_int, Rates_slab, Rates_cru, Rates_tot)
plt.suptitle(f'AKL SA(0.5) 10% in 50')


hazard = {}
with open('/home/chrisdc/NSHM/Disaggs/oqdata/Disagg_orig_gsim_LT_new_slab/TRT-0_49.csv','r') as TRTfile:
    disagg_reader = csv.reader(TRTfile)
    junk = next(disagg_reader)
    header = next(disagg_reader)
    DisaggData = namedtuple("DisaggData", header, rename=True)
    for row in disagg_reader:
        # print(trt,prob)
        disagg_data = DisaggData(*row)
        trt = disagg_data.trt
        prob = disagg_data.rlz0
        if not hazard.get(trt):
            hazard[trt] = float(prob)
        else:
            hazard[trt] += float(prob)

total_hazard = sum(list(hazard.values()))
for k,v in hazard.items():
    hazard[k] = hazard[k]/total_hazard
print(hazard)

fig, ax = plt.subplots(1,1)
haz = list(hazard.values())
names = list(hazard.keys())
ax.bar(names,haz)

















