import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from nzshm_common.location.location import LOCATIONS_BY_ID
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids.region_grid import load_grid
from toshi_hazard_store.query_v3 import get_hazard_curves
import time

from oq_hazard_report.plotting_functions import plot_hazard_curve_fromdf, plot_spectrum_fromdf

ARCHIVE_DIR = '/home/chrisdc/NSHM/oqdata/HAZ_CURVE_ARCHIVE'

def get_hazard(hazard_id, locs, vs30, imts, aggs, force=False):

    curves_filename = f'{hazard_id}-{vs30}.json'
    curves_filepath = Path(ARCHIVE_DIR,curves_filename)

    if curves_filepath.exists() and (not force):
        dtype = {'lat':str,'lon':str}
        hazard_data = pd.read_json(curves_filepath,dtype=dtype)
        return hazard_data
    
    res = next(get_hazard_curves([locs[0]], [vs30], [hazard_id], [imts[0]], [aggs[0]]))
    num_levels = len(res.values)

    columns = ['lat', 'lon', 'imt', 'agg', 'level', 'hazard']
    index = range((len(locs)-1) * len(imts) * len(aggs) * num_levels)
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

plot_title = 'SLT v8, GMCM v2'

# /home/chrisdc/NSHM/oqresults/Full_Models/SLT_v6_gmm_v0b/Compare/GMCM_corr')
hazard_model = dict(id='SLT_v8_gmm_v2_FINAL',name='SLT v8, GMCM v2')

PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
grid_res = 0.001

legend = False
vs30 = 150
fig_dir = Path('/home/chrisdc/NSHM/oqresults/Full_Models/SLT_v8_gmm_v2/Solo/Spectra/',f'vs30_{int(vs30)}')
imts = ['PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.7)','SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)', 'SA(4.0)', 'SA(5.0)', 'SA(6.0)','SA(7.5)', 'SA(10.0)']
aggs = ["mean", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.5", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]

locations = [f"{loc['latitude']:0.3f}~{loc['longitude']:0.3f}" for loc in LOCATIONS_BY_ID.values()]

ylim = [0,5]

POES = [0.1,0.02]
INVESTIGATION_TIME = 50
bandws = {
            # '2.5,20,80,97.5':{'lower2':'0.025','lower1':'0.2','upper1':'0.8','upper2':'0.975'},
            # '1,10,90,99':{'lower2':'0.01','lower1':'0.1','upper1':'0.9','upper2':'0.99'}
            '0.5,10,90,99.5':{'lower2':'0.005','lower1':'0.1','upper1':'0.9','upper2':'0.995'}
        }

inv_time = 50
# poes = [0.1,0.02]
poes = [0.02]

hazard_model['data'] = get_hazard(hazard_model['id'], locations, vs30, imts, aggs)


ref_lines = []
for poe in POES:
        ref_line = dict(type = 'poe',
                        poe = poe,
                        inv_time = INVESTIGATION_TIME)
        ref_lines.append(ref_line)


for location in LOCATIONS_BY_ID.keys():
    if (location != 'WLG'): continue
    print(f'plotting {location} ... ')
    for poe in poes:
        for bounds,bandw in bandws.items():
            pt = (LOCATIONS_BY_ID[location]["latitude"], LOCATIONS_BY_ID[location]["longitude"])
            loc = CodedLocation(*pt,grid_res).downsample(grid_res).code
            name = LOCATIONS_BY_ID[location]['name']

            fig, ax = plt.subplots(1,1)
            fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
            fig.set_facecolor('white')
            plot_spectrum_fromdf(hazard_model['data'], loc, poe, inv_time, ax, bandw=True)
            title = f'{name} {poe*100:.0f}% in 50 years {bounds}'
            plot_name = 'spectra_' + '_'.join( (name,str(poe),bounds) ) + '.png'
            file_path = Path(fig_dir,plot_name) 
            ax.set_title(title)
            ax.set_ylim(ylim)
            # plt.savefig(file_path)
            # plt.close()
            plt.show()

