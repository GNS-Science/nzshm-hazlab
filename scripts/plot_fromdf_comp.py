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

# fig_dir = Path('/home/chrisdc/NSHM/oqresults/TD_sensitivity')
# fig_dir = Path('/home/chrisdc/NSHM/oqresults/Poly_sensitivity')

# json_file_path_TI = '/home/chrisdc/NSHM/oqresults/TD_sensitivity/data/TI_sensivitiy_all_aggregates.json'
# hazard_curves_TI = pd.read_json(json_file_path_TI,dtype=dtype)

# json_file_path_TD = '/home/chrisdc/NSHM/oqresults/TD_sensitivity/data/TD_sensivitiy_all_aggregates.json'
# hazard_curves_TD = pd.read_json(json_file_path_TD,dtype=dtype)

# json_file_path_zeroPoly = '/home/chrisdc/NSHM/oqresults/Poly_sensitivity/data/poly0_nz34_all_aggregates.json'
# hazard_curves_zeroPoly = pd.read_json(json_file_path_zeroPoly,dtype=dtype)

colors = ['#1b9e77', '#d95f02', '#7570b3']

# fig_dir = Path('/home/chrisdc/NSHM/oqresults/C_sensitivity')
# labels = ['C = 4.1', 'C = 4.2','C = 4.3']
# hcurves = [pd.read_json('/home/chrisdc/NSHM/oqresults/C_sensitivity/data/C4p1_nz34_all_aggregates.json',dtype=dtype),
#             pd.read_json('/home/chrisdc/NSHM/oqresults/NB_Pois_N_sensitivity/data/basline_NBandNs_C4p2_nz34_all_aggregates.json',dtype=dtype),
#             pd.read_json('/home/chrisdc/NSHM/oqresults/C_sensitivity/data/C4p3_nz34_all_aggregates.json',dtype=dtype),
# #         ]

fig_dir = Path('/home/chrisdc/NSHM/oqresults/NB_Pois_N_sensitivity')
# labels = ['NB and N scaling', 'N scaling only','NB only']
labels = ['NB and N scaling', 'NB only']
hcurves = [pd.read_json('/home/chrisdc/NSHM/oqresults/NB_Pois_N_sensitivity/data/basline_NBandNs_C4p2_nz34_all_aggregates.json',dtype=dtype),
            # pd.read_json('/home/chrisdc/NSHM/oqresults/NB_Pois_N_sensitivity/data/NBsens_2_nz34_all_aggregates.json',dtype=dtype),
            pd.read_json('/home/chrisdc/NSHM/oqresults/NB_Pois_N_sensitivity/data/NBsens_3_nz34_all_aggregates.json',dtype=dtype),
        ]



# fig_dir = Path('/home/chrisdc/NSHM/oqresults/MaxJump_sensitivity')
# labels = ['10km','15km']
# hcurves = [
#             pd.read_json('/home/chrisdc/NSHM/oqresults/MaxJump_sensitivity/data/MaxJump10_nz34_all_aggregates.json',dtype=dtype),
#             pd.read_json('/home/chrisdc/NSHM/oqresults/NB_Pois_N_sensitivity/data/basline_NBandNs_C4p2_nz34_all_aggregates.json',dtype=dtype),
#         ]


xlim = [1e-2,1e1]
ylim = [1e-6,1]


LOCATIONS_BY_ID['RGN'] = dict(latitude=-37.8, longitude=174.8, name='Raglan', id='RGN')
locations = ['AKL','CHC','WLG','DUD','WHO','ZQN','KBZ','GMN']

imts = ['PGA','SA(0.5)','SA(1.5)','SA(3.0)']
POES = [0.1,0.02]
INVESTIGATION_TIME = 50
# bandw = {'lower2':'0.005','lower1':'0.1','upper1':'0.9','upper2':'0.995'}
bandw = {'lower2':'0.1','lower1':'0.2','upper1':'0.8','upper2':'0.9'}
# bandw = None

ref_lines = []
for poe in POES:
        ref_line = dict(type = 'poe',
                        poe = poe,
                        inv_time = INVESTIGATION_TIME)
        ref_lines.append(ref_line)

for imt in imts:
    for location in LOCATIONS_BY_ID.keys():
        pt = (LOCATIONS_BY_ID[location]["latitude"], LOCATIONS_BY_ID[location]["longitude"])
        loc = CodedLocation(*pt).downsample(grid_res).code
        name = LOCATIONS_BY_ID[location]['name']

        fig, ax = plt.subplots(1,1)
        fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
        fig.set_facecolor('white')

        handles = []
        for i,hcurve in enumerate(hcurves):
            handles.append(plot_hazard_curve_fromdf(hcurve, loc, imt, ax, xlim, ylim,central='mean',bandw=bandw,ref_lines=ref_lines,color=colors[i]))
        
        
        plt.legend(handles,labels)
        # ax.set_xscale('linear')
        # ax.set_xlim((0,5))
        title = f'{name} {imt} 60% 80%'
        plot_name = 'comp_80_60_' + '_'.join( (name,imt) ) + '.png'
        file_path = Path(fig_dir,plot_name) 
        ax.set_title(title)
        plt.savefig(file_path)
        plt.close()

