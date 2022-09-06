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


# [X] wrong disagg retrieved by end-user

site = 'AKL'
site_name = 'Kerikeri'
poe = 0.1
imt = 'SA(0.5)'

disagg_result_file = Path('/home/chrisdc/NSHM/Disaggs/disagg_result.json')
with open(disagg_result_file,'r') as jsonfile:
    disaggs = json.load(jsonfile)


for disagg in disaggs['hazard_solutions']:
    if (disagg['site_name'] == site_name) & (disagg['imt'] == imt) & (disagg['poe'] == poe):
        print(site_name, poe, imt)
        print(disagg['hazard_solution_csv_archive_url'])
        print(disagg)
        break


csv_archive = Path('/home/chrisdc/NSHM/Disaggs/rlz_output/openquake_csv_archive-T3BlbnF1YWtlSGF6YXJkVGFzazoxMDg5NTM=.zip')

hazard = {}
           

with ZipFile(csv_archive) as zipf:
    with io.TextIOWrapper(zipf.open('Mag_Dist_TRT-0_1.csv'), encoding="utf-8") as mag_dist_TRT_file:
        disagg_reader = csv.reader(mag_dist_TRT_file)
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

# plt.show()

slab_fn = '/home/chrisdc/NSHM/Disaggs/config/sources/slab_source_locations.txt'
lons = []
lats = []
with open(slab_fn,'r') as slab_file:
    for line in slab_file:
        lon,lat = line.split(' ')
        lon = float(lon)
        lat = float(lat)
        if lon<0:
            # print(lon)
            lon = lon+360

        lons.append(lon)
        lats.append(lat)
        # print(lon,lat)




fig, ax = plt.subplots(1,1)
fig.set_size_inches(8,8)
fig.set_facecolor('white')
nz = geopandas.read_file('/home/chrisdc/NSHM/DATA/nz-coastlines-and-islands-polygons-topo-150k/nz-coastlines-and-islands-polygons-topo-150k.shp')

nz.boundary.plot(ax=ax)
ax.plot(lons,lats,'r.')
# ax.plot([178],[-36],'ro')

# ax.set_xlim([165,183])
# ax.set_ylim([-48,-33])


# slab only
mag_dist_fn = '/home/chrisdc/NSHM/Disaggs/oqdata/dis_slab/Mag_Dist-0_44.csv'
with open(mag_dist_fn,'r') as csvfile:
    disagg_reader = csv.reader(csvfile)
    junk = next(disagg_reader)
    header = next(disagg_reader)
    DisaggData = namedtuple("DisaggData", header, rename=True)
    mags = []
    dists = []
    rates = []
    for row in disagg_reader:
            disagg_data = DisaggData(*row)

            mag = float(disagg_data.mag)
            dist = float(disagg_data.dist)
            rate = float(disagg_data.rlz0)

            mags.append(mag)
            dists.append(dist)
            rates.append(rate)

mags = np.array(mags)
dists = np.array(dists)
rates = np.array(rates)
width = 0.1
depth = 10

fig = plt.figure()
ax = fig.add_subplot(111,projection='3d')
fig.set_size_inches(8,8)
fig.set_facecolor('white')
ax.bar3d(mags,dists,np.zeros_like(rates),width,depth,rates)


# full disagg
mag_dist_fn = '/home/chrisdc/NSHM/Disaggs/rlz_output/Mag_Dist_TRT-0_1.csv'
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
            mags.append(mag)
            dists.append(dist)

            if trt == 'Active Shallow Crust':
                rates_cru.append(rate)
                rates_slab.append(0.0)
                rates_int.append(0.0)
            elif trt == 'Subduction Interface':
                rates_int.append(rate)
                rates_slab.append(0.0)
                rates_cru.append(0.0)
            elif trt == 'Subduction Intraslab':
                rates_slab.append(rate)
                rates_int.append(0.0)
                rates_cru.append(0.0)


mags = np.array(mags)
dists = np.array(dists)
rates_int = np.array(rates_int)
rates_slab = np.array(rates_slab)
rates_cru = np.array(rates_cru)
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
plt.show()
# plt.close()





