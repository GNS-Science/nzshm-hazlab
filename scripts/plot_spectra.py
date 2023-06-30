import matplotlib.pyplot as plt
from pathlib import Path
from nzshm_common.location.location import location_by_id
from nzshm_common.location.code_location import CodedLocation
from nzshm_hazlab.store.curves import get_hazard
from nzshm_hazlab.plotting_functions import plot_spectrum






# ███╗░░░███╗░█████╗░██╗███╗░░██╗
# ████╗░████║██╔══██╗██║████╗░██║
# ██╔████╔██║███████║██║██╔██╗██║
# ██║╚██╔╝██║██╔══██║██║██║╚████║
# ██║░╚═╝░██║██║░░██║██║██║░╚███║
# ╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝╚═╝░░╚══╝

plot_title = 'SLT v8, GMCM v2'

# /home/chrisdc/NSHM/oqresults/Full_Models/SLT_v6_gmm_v0b/Compare/GMCM_corr')
hazard_model = dict(id='NSHM_v1.0.4',name='NSHM_v1.0.4')

PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
grid_res = 0.001

legend = False
vs30 = 150
fig_dir = Path('/home/chrisdc/NSHM/oqresults/Full_Models/SLT_v8_gmm_v2/Solo/Spectra/',f'vs30_{int(vs30)}')
imts = ['PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.7)','SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)', 'SA(4.0)', 'SA(5.0)', 'SA(6.0)','SA(7.5)', 'SA(10.0)']
# aggs = ["mean", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.5", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]
aggs = ["mean"]

location_ids = ['WLG']
locations = [CodedLocation(location_by_id(lid)['latitude'], location_by_id(lid)['longitude'],0.001) for lid in location_ids]
location_codes = [loc.code for loc in locations]

ylim = [0,5]

POES = [0.1,0.02]
INVESTIGATION_TIME = 50
bandws = {
            # '2.5,20,80,97.5':{'lower2':'0.025','lower1':'0.2','upper1':'0.8','upper2':'0.975'},
            # '1,10,90,99':{'lower2':'0.01','lower1':'0.1','upper1':'0.9','upper2':'0.99'}
            # '0.5,10,90,99.5':{'lower2':'0.005','lower1':'0.1','upper1':'0.9','upper2':'0.995'}
        }
bandw = False

inv_time = 50
# poes = [0.1,0.02]
poes = [0.86]

hazard_model['data'] = get_hazard(hazard_model['id'], vs30, locations, imts, aggs)


ref_lines = []
for poe in POES:
        ref_line = dict(type = 'poe',
                        poe = poe,
                        inv_time = INVESTIGATION_TIME)
        ref_lines.append(ref_line)


for location in locations:
    location_id = location_ids[locations.index(location)]
    print(f'plotting {location} ... ')
    for poe in poes:
        pt = (location_by_id(location_id)["latitude"], location_by_id(location_id)["longitude"])
        loc = location.code
        name = location_by_id(location_id)['name']

        fig, ax = plt.subplots(1,1)
        fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
        fig.set_facecolor('white')
        plot_spectrum(hazard_model['data'], loc, poe, inv_time, ax, bandw=bandw)
        title = f'{name} {poe*100:.0f}% in 50 years'
        plot_name = 'spectra_' + '_'.join( (name,str(poe)) ) + '.png'
        file_path = Path(fig_dir,plot_name) 
        ax.set_title(title)
        ax.set_ylim(ylim)
        plt.show()

