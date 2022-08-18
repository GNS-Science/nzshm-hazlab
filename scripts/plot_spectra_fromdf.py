import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from nzshm_common.location.location import LOCATIONS_BY_ID
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids.region_grid import load_grid

from oq_hazard_report.plotting_functions import plot_hazard_curve_fromdf, plot_spectrum_fromdf

PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
grid_res = 0.001

dtype = {'lat':str,'lon':str}

fig_dir = Path('/home/chrisdc/NSHM/oqresults/TAG_final/spectra')
json_file_path = '/home/chrisdc/NSHM/oqresults/TAG_final/data/FullLT_allIMT_nz34_all_aggregates.json'
hazard_curves = pd.read_json(json_file_path,dtype=dtype)

xlim = [1e-2,1e1]
ylim = [1e-6,1]


# Raglan = (-37.824589, 174.893949)
# LOCATIONS_BY_ID['RGN'] = dict(latitude=-37.8, longitude=174.8, name='Raglan', id='RGN')
# locations = ['AKL','CHC','WLG','DUD','RGN']
locations = ['AKL','CHC','WLG','DUD']

imts = ['PGA','SA(0.5)','SA(1.5)']
POES = [0.1,0.02]
INVESTIGATION_TIME = 50
# aggs = ['0.1','0.2','0.5','0.8','0.9']
bandws = {
            # '2.5,20,80,97.5':{'lower2':'0.025','lower1':'0.2','upper1':'0.8','upper2':'0.975'},
            # '1,10,90,99':{'lower2':'0.01','lower1':'0.1','upper1':'0.9','upper2':'0.99'}
            '0.5,10,90,99.5':{'lower2':'0.005','lower1':'0.1','upper1':'0.9','upper2':'0.995'}
        }

inv_time = 50
poes = [0.1,0.02]


ref_lines = []
for poe in POES:
        ref_line = dict(type = 'poe',
                        poe = poe,
                        inv_time = INVESTIGATION_TIME)
        ref_lines.append(ref_line)


for location in LOCATIONS_BY_ID.keys():
    for poe in poes:
        for bounds,bandw in bandws.items():
            pt = (LOCATIONS_BY_ID[location]["latitude"], LOCATIONS_BY_ID[location]["longitude"])
            loc = CodedLocation(*pt).downsample(grid_res).code
            name = LOCATIONS_BY_ID[location]['name']

            fig, ax = plt.subplots(1,1)
            fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
            fig.set_facecolor('white')

            plot_spectrum_fromdf(hazard_curves, loc, poe, inv_time, ax, bandw=True)
            title = f'{name} {poe*100:.0f}% in 50 years {bounds}'
            plot_name = 'spectra_' + '_'.join( (name,str(poe),bounds) ) + '.png'
            file_path = Path(fig_dir,plot_name) 
            ax.set_title(title)
            plt.savefig(file_path)
            plt.close()

