from asyncore import read
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import csv
from matplotlib.collections import LineCollection
from nzshm_common.location.location import LOCATIONS_BY_ID

def read_csv(csv_path):
    with open(csv_path,'r') as csvfile:
        reader = csv.reader(csvfile)
        junk = next(reader)
        header = next(reader)
        levels_OQ = [float(l[4:]) for l in header[3:]]
        hazard_OQ = {}
        for row in reader:
            longitude = float(row[0])
            latitude = float(row[1])
            sl = [v['name'] for v in LOCATIONS_BY_ID.values() if f"{v['latitude']:.3f}" == f"{latitude:.3f}"]
            if sl:
                site = [v['name'] for v in LOCATIONS_BY_ID.values() if f"{v['latitude']:.3f}" == f"{latitude:.3f}"][0]
                hazard_OQ[site] = list( map(float,row[3:]) )

    return levels_OQ, hazard_OQ



PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
grid_res = 0.001

lon = 174.77
lat = -36.87
imt = 'PGA'
agg = 'mean'

xlim = [1e0,2e1]
ylim = [1e-7,1e-4]


oq_hazard = Path('/home/chrisdc/NSHM/oqruns/wings/output/bg_nz34/hazard_curve-mean-PGA_13.csv')
levels_bg, hazard_OQ_bg = read_csv(oq_hazard)

fig, ax = plt.subplots(1,1)
fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
fig.set_facecolor('white')
exclude_list = ['Wellington','Whakatane','Levin','Christchurch','Invercargill','Hanmer Springs','Gisborne','Haast','Palmerston North']
for k,v in hazard_OQ_bg.items():
    if k not in exclude_list:
        ax.plot(levels_bg,v,lw=2,label=k)


ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.grid(color='lightgray')

ax.set_xlabel('Shaking Intensity, %s [g]'%imt, fontsize=14)
ax.set_ylabel('Annual Probability of Exceedance', fontsize=14)
ax.set_title('Auckland PGA', fontsize=16)
plt.legend()
plt.show()
