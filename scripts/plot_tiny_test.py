from asyncore import read
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import csv
from matplotlib.collections import LineCollection

def read_csv(csv_path):
    with open(csv_path,'r') as csvfile:
        reader = csv.reader(csvfile)
        junk = next(reader)
        header = next(reader)
        levels_OQ = [float(l[4:]) for l in header[3:]]
        for row in reader:
            longitude = float(row[0])
            latitude = float(row[1])
            if (longitude==lon) & (latitude==lat):
                hazard_OQ = list( map(float,row[3:]) )

    return levels_OQ, hazard_OQ



PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
grid_res = 0.001

lon = 174.78
lat = -41.3
imt = 'PGA'
agg = 'mean'

xlim = [1e-2,1e1]
ylim = [1e-6,1]

ths_hazard_json = Path('/home/chrisdc/NSHM/oqruns/tiny_test/output/tiny_test_all_aggregates.json')
dtype = {'lat':str,'lon':str}
ths_hazard = pd.read_json(str(ths_hazard_json))

oq_hazard_mean = Path('/home/chrisdc/NSHM/oqruns/tiny_test/output/hazard_curve-mean-PGA_9.csv')
oq_hazard_10 = Path('/home/chrisdc/NSHM/oqruns/tiny_test/output/quantile_curve-0.1-PGA_9.csv')
oq_hazard_90 = Path('/home/chrisdc/NSHM/oqruns/tiny_test/output/quantile_curve-0.9-PGA_9.csv')
levels_OQ, hazard_OQ_mean = read_csv(oq_hazard_mean)
junk, hazard_OQ_10 = read_csv(oq_hazard_10)
junk, hazard_OQ_90 = read_csv(oq_hazard_90)

levels_THS = list(set(ths_hazard['level']))
levels_THS.sort()

hazard_THS_mean = ths_hazard.loc[ (ths_hazard['lat'] == lat) & (ths_hazard['lon'] == lon) & (ths_hazard['imt'] == imt) & (ths_hazard['agg'] == agg),'hazard'].to_numpy()
hazard_THS_10 = ths_hazard.loc[ (ths_hazard['lat'] == lat) & (ths_hazard['lon'] == lon) & (ths_hazard['imt'] == imt) & (ths_hazard['agg'] == '0.1'),'hazard'].to_numpy()
hazard_THS_90 = ths_hazard.loc[ (ths_hazard['lat'] == lat) & (ths_hazard['lon'] == lon) & (ths_hazard['imt'] == imt) & (ths_hazard['agg'] == '0.9'),'hazard'].to_numpy()

fig, ax = plt.subplots(1,1)
fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
fig.set_facecolor('white')
ax.plot(levels_OQ,hazard_OQ_mean,lw=6,color='#D81B60',label='Mean: oq-engine')
ax.plot(levels_THS,hazard_THS_mean,lw=3,color='#1E88E5',label='Mean: toshi-hazard-store')

ax.plot(levels_OQ,hazard_OQ_10,linestyle='--',lw=5,color='#D81B60',label='p10: oq-engine')
ax.plot(levels_THS,hazard_THS_10,linestyle='--',lw=3,color='#1E88E5',label='p10: toshi-hazard-store')


ax.plot(levels_OQ,hazard_OQ_90,linestyle='--',lw=5,color='#D81B60',label='p90: oq-engine')
ax.plot(levels_THS,hazard_THS_90,linestyle='--',lw=3,color='#1E88E5',label='p90: toshi-hazard-store')

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.grid(color='lightgray')

ax.set_xlabel('Shaking Intensity, %s [g]'%imt, fontsize=14)
ax.set_ylabel('Annual Probability of Exceedance', fontsize=14)
ax.set_title('Wellington PGA', fontsize=16)


fig, ax = plt.subplots(1,1)
fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
fig.set_facecolor('white')

rlz_curves_file = '/home/chrisdc/NSHM/oqruns/tiny_test/output/hazard_-41.300~174.780_PGA.npy'
rlz_curves = np.load(rlz_curves_file)
num_rlz = rlz_curves.shape[0]
segs = np.zeros((num_rlz,29,2))
segs[:,:,0] = levels_THS
segs[:,:,1] = rlz_curves
line_segments = LineCollection(segs,linewidths=0.25,alpha=0.5)
ax.add_collection(line_segments)
ax.plot(levels_THS,hazard_THS_mean,lw=5,color='r')
ax.set_xlabel('Shaking Intensity, %s [g]'%imt, fontsize=14)
ax.set_ylabel('Annual Probability of Exceedance', fontsize=14)
ax.set_title('Wellington PGA', fontsize=16)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.grid(color='lightgray')

plt.legend()
plt.show()
