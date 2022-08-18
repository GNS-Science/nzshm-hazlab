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
        
        skip_col = 1 if header[0] == 'custom_site_id' else 0
        levels_OQ = [float(l[4:]) for l in header[3+skip_col:]]

        for row in reader:
            longitude = float(row[0+skip_col])
            latitude = float(row[1+skip_col])
            if (longitude==lon) & (latitude==lat):
                hazard_OQ = list( map(float,row[3+skip_col:]) )

    return levels_OQ, hazard_OQ



PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
grid_res = 0.001

lon = 174.77
lat = -36.87
site = 'Auckland'

# lon = 178
# lat = -38.65
# site = 'Gisborne'


imt = 'PGA'
agg = 'mean'


xlim = [1e-2,1e1]
ylim = [1e-6,1]

root_dir = Path('/home/chrisdc/NSHM/oqruns/backarc/output')
hazard_runs = [
                # {'name':'control','filepath':Path(root_dir,'control/hazard_curve-mean-PGA_16.csv')},
                {'name':'backarc flag','filepath':Path(root_dir,'./ba_some/hazard_curve-mean-PGA_18.csv')},
                {'name':'no backarc','filepath':Path(root_dir,'./ba_none/hazard_curve-mean-PGA_17.csv')},
                {'name':'format','filepath':Path(root_dir,'./format/hazard_curve-mean-PGA_20.csv')},
                
                ]
for hazard_run in hazard_runs:
    levels, values = read_csv(hazard_run['filepath'])
    hazard_run['values'] = values
    hazard_run['levels'] = levels

fig, ax = plt.subplots(1,1)
fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
fig.set_facecolor('white')

for hazard_run in hazard_runs:
    ls = '--' if hazard_run['name'] == 'format' else '-'
    # ls = '--' if hazard_run['name'] == 'no backarc' else '-'
    
    ax.plot(hazard_run['levels'], hazard_run['values'], ls=ls, lw=3,label=hazard_run['name'])



ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.grid(color='lightgray')

ax.set_xlabel('Shaking Intensity, %s [g]'%imt, fontsize=14)
ax.set_ylabel('Annual Probability of Exceedance', fontsize=14)
ax.set_title(f'{site} PGA', fontsize=16)
plt.legend()
plt.show()
