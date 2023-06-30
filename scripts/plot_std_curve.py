import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from nzshm_common.location.location import LOCATIONS_BY_ID
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids.region_grid import load_grid
from toshi_hazard_store.query_v3 import get_hazard_curves
import numpy as np


from oq_hazard_report.plotting_functions import plot_hazard_curve_fromdf

ARCHIVE_DIR = '/home/chrisdc/NSHM/oqdata/HAZ_CURVE_ARCHIVE'

def get_hazard(hazard_id, locs, vs30, imts, aggs, force=False):

    curves_filename = f'{hazard_id}-{vs30}.json'
    curves_filepath = Path(ARCHIVE_DIR,curves_filename)

    if curves_filepath.exists() and (not force):
        dtype = {'lat':str,'lon':str}
        hazard_model['data'] = pd.read_json(curves_filepath,dtype=dtype)
        return hazard_model['data']

    columns = ['lat', 'lon', 'imt', 'agg', 'level', 'hazard']
    index = range(len(locs) * len(imts) * len(aggs) * 29)
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

    hazard_curves.to_json(curves_filepath)
    return hazard_curves




# ███╗░░░███╗░█████╗░██╗███╗░░██╗
# ████╗░████║██╔══██╗██║████╗░██║
# ██╔████╔██║███████║██║██╔██╗██║
# ██║╚██╔╝██║██╔══██║██║██║╚████║
# ██║░╚═╝░██║██║░░██║██║██║░╚███║
# ╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝╚═╝░░╚══╝

plot_title = 'SLT v8, GMCM v2 sdev'
fig_dir = Path('/home/chrisdc/NSHM/oqresults/Full_Models/SLT_v8_gmm_v2/std')
hazard_models = [
    dict(id='SLT_v8_gmm_v2',name='SLT v8, GMCM v2'),
]

legend = False
vs30 = 400
imts = ['PGA','SA(0.5)', 'SA(1.5)', 'SA(3.0)']
aggs = ["std","mean", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.5", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]


locations = [f"{loc['latitude']:0.3f}~{loc['longitude']:0.3f}" for loc in LOCATIONS_BY_ID.values()] 

xscale = 'linear'
xlim = [0,5]
ylim = [0,5]


#=============================================================================================================================#



PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
grid_res = 0.001
colors = ['#1b9e77', '#d95f02', '#7570b3']

if not fig_dir.exists():
    fig_dir.mkdir()

for hazard_model in hazard_models:
    hazard_model['data'] = get_hazard(hazard_model['id'], locations, vs30, imts, aggs)

POES = [0.1,0.02]
INVESTIGATION_TIME = 50


ref_lines = []
for poe in POES:
    ref_line = dict(type = 'poe',
                    poe = poe,
                    inv_time = INVESTIGATION_TIME)
    ref_lines.append(ref_line)


for imt in imts:
    for location in LOCATIONS_BY_ID.keys():
        print(f'plotting {location} ... ')
        
        
        pt = (LOCATIONS_BY_ID[location]["latitude"], LOCATIONS_BY_ID[location]["longitude"])
        loc = CodedLocation(*pt,grid_res).downsample(grid_res).code
        name = LOCATIONS_BY_ID[location]['name']
        lat, lon = loc.split('~')

        fig, ax = plt.subplots(1,1)
        fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
        fig.set_facecolor('white')

        hd_filt = hazard_model['data'].loc[ (hazard_model['data']['imt'] == imt) & (hazard_model['data']['lat'] == lat) & (hazard_model['data']['lon'] == lon)]

        levels = hd_filt.loc[ hd_filt['agg'] == 'std']['level'].to_numpy(dtype='float64')
        values = hd_filt.loc[ hd_filt['agg'] == 'std']['hazard'].to_numpy(dtype='float64')
        ax.plot(levels,values)
        for ref_line in ref_lines:
            poe = ref_line['poe']
            inv_time = ref_line['inv_time']
            rp = -inv_time/np.log(1-poe)
        text = f'{poe*100:.0f}% in {inv_time:.0f} years (1/{rp:.0f})'
        ax.plot(xlim,[1/rp]*2,ls='--',color='dimgray',zorder=-1)
        ax.annotate(text, [xlim[1],1/rp], ha='right',va='bottom')

        ax.set_ylim(ylim)
        ax.set_xlim(xlim)
        ax.set_xlabel('Std of Shaking Intensity, %s [g]'%imt)
        ax.set_ylabel('Annual Probability of Exceedance')
        ax.grid(color='lightgray')

        title = f'{plot_title} {name} vs30={vs30} {imt}'
        plot_name = '_'.join( (name,str(vs30),imt) ) + '.png'
        file_path = Path(fig_dir,plot_name) 
        ax.set_title(title)
        plt.savefig(file_path)
        plt.close()

