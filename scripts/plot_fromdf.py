import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from nzshm_common.location.location import LOCATIONS_BY_ID
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids.region_grid import load_grid


from oq_hazard_report.plotting_functions import plot_hazard_curve_fromdf

PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
grid_res = 0.001

dtype = {'lat':str,'lon':str}

# fig_dir = Path('/home/chrisdc/NSHM/oqresults/full_lt/400')
# hc0 = '/home/chrisdc/NSHM/oqdata/df_0_aggregates.json'
# hc1 = '/home/chrisdc/NSHM/oqdata/df_1_aggregates.json'

# fig_dir = Path('/home/chrisdc/NSHM/oqresults/SBsource/400')
# hc0 = '/home/chrisdc/oqdata/tmp_data/SBsource_400_0_aggregates.json'
# hc1 = '/home/chrisdc/oqdata/tmp_data/SBsource_400_1_aggregates.json'

# fig_dir = Path('/home/chrisdc/NSHM/oqresults/full_gsim')
# hc0 = '/home/chrisdc/NSHM/oqdata/full_gsim/df_0_aggregates.json'
# hc1 = '/home/chrisdc/NSHM/oqdata/full_gsim/df_1_aggregates.json'

# fig_dir = Path('/home/chrisdc/NSHM/oqresults/full_lt/750')
# hc0 = '/home/chrisdc/df_0_aggregates.json'
# hc1 = '/home/chrisdc/df_1_aggregates.json'

# hazard_curves_0 = pd.read_json(hc0,dtype=dtype)
# hazard_curves_1 = pd.read_json(hc1,dtype=dtype)
# hazard_curves = pd.concat([hazard_curves_0, hazard_curves_1],ignore_index=True)

# fig_dir = Path('/home/chrisdc/NSHM/oqresults/full_gsim')
# json_file_path = '/home/chrisdc/NSHM/oqdata/full_gsim/allIMTs_moreAggs_all_aggregates.json'

# fig_dir = Path('/home/chrisdc/NSHM/oqresults/NB_test')
# json_file_path = '/home/chrisdc/NSHM/oqdata/NB_test/NB_test_nz34.json'

# fig_dir = Path('/home/chrisdc/NSHM/oqresults/TAG_final')
# json_file_path = '/home/chrisdc/NSHM/oqresults/TAG_final/data/TAG_final_NZ34_limited_all_aggregates.json'

# fig_dir = Path('/home/chrisdc/NSHM/oqresults/NB_Pois_N_sensitivity')
fig_dir = Path('/home/chrisdc/NSHM/oqresults/test_agg/NBsens_1_gt0')
json_file_path = '/home/chrisdc/NSHM/oqresults/NB_Pois_N_sensitivity/data/NBsens_1_nz34_all_aggregates.json'
# hazard_curves = pd.read_json(json_file_path,dtype=dtype)
hazard_curves = pd.read_json('/home/chrisdc/NSHM/oqresults/test_agg/data/NBsens_1_test_all_aggregates.json',dtype=dtype)

xlim = [1e-2,1e1]
ylim = [1e-6,1]


# locations = LOCATIONS_BY_ID.keys()
locations = ['AKL']
# locations = ['AKL','CHC','WLG','DUD','WHO']

imts = ['PGA','SA(0.5)','SA(1.5)']
POES = [0.1,0.02]
INVESTIGATION_TIME = 50
# aggs = ['0.1','0.2','0.5','0.8','0.9']
bandws = {
            '0.5,10,90,99.5':{'lower2':'0.005','lower1':'0.1','upper1':'0.9','upper2':'0.995'},
            # '1,10,90,99':{'lower2':'0.01','lower1':'0.1','upper1':'0.9','upper2':'0.99'},
            # '2.5,10,90,97.5':{'lower2':'0.025','lower1':'0.1','upper1':'0.9','upper2':'0.975'},
            # '5,10,90,95':{'lower2':'0.05','lower1':'0.1','upper1':'0.9','upper2':'0.95'},
        }




ref_lines = []
for poe in POES:
        ref_line = dict(type = 'poe',
                        poe = poe,
                        inv_time = INVESTIGATION_TIME)
        ref_lines.append(ref_line)

for imt in imts:
    for location in LOCATIONS_BY_ID.keys():
        for bounds,bandw in bandws.items():
            pt = (LOCATIONS_BY_ID[location]["latitude"], LOCATIONS_BY_ID[location]["longitude"])
            loc = CodedLocation(*pt).downsample(grid_res).code
            name = LOCATIONS_BY_ID[location]['name']

            fig, ax = plt.subplots(1,1)
            fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
            fig.set_facecolor('white')

            plot_hazard_curve_fromdf(hazard_curves, loc, imt, ax, xlim, ylim,central='mean',bandw=bandw,ref_lines=ref_lines)
            title = f'{name} {imt} {bounds}'
            plot_name = '_'.join( (name,imt,bounds) ) + '.png'
            file_path = Path(fig_dir,plot_name) 
            ax.set_title(title)
            plt.savefig(file_path)
            plt.close()

