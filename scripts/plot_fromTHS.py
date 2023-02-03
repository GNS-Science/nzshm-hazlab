import time
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from nzshm_common.location.location import LOCATIONS_BY_ID
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids.region_grid import load_grid
from toshi_hazard_store.query_v3 import get_hazard_curves


from nzshm_hazlab.plotting_functions import plot_hazard_curve_fromdf

ARCHIVE_DIR = '/home/chrisdc/NSHM/oqdata/HAZ_CURVE_ARCHIVE'
AGGS = ["mean", "cov", "std", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]
IMTS = ['PGA', 'SA(0.1)', 'SA(0.2)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.7)','SA(1.0)', 'SA(1.5)', 'SA(2.0)', 'SA(3.0)', 'SA(4.0)', 'SA(5.0)', 'SA(6.0)','SA(7.5)','SA(10.0)']


def get_hazard(hazard_id, locs, vs30, imts, aggs, force=False):


    curves_filename = f'{hazard_id}-{vs30}.json'
    curves_filepath = Path(ARCHIVE_DIR,curves_filename)

    if curves_filepath.exists() and (not force):
        dtype = {'lat':str,'lon':str}
        hazard_data = pd.read_json(curves_filepath,dtype=dtype)
        return hazard_data

    res = next(get_hazard_curves([locs[0]], [vs30], [hazard_id], [imts[0]], ['mean']))
    num_levels = len(res.values)

    columns = ['lat', 'lon', 'imt', 'agg', 'level', 'hazard']
    index = range(len(locs) * len(imts) * len(aggs) * num_levels)
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

    # hazard_curves.to_json(curves_filepath)
    return hazard_curves




# ███╗░░░███╗░█████╗░██╗███╗░░██╗
# ████╗░████║██╔══██╗██║████╗░██║
# ██╔████╔██║███████║██║██╔██╗██║
# ██║╚██╔╝██║██╔══██║██║██║╚████║
# ██║░╚═╝░██║██║░░██║██║██║░╚███║
# ╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝╚═╝░░╚══╝

plot_title = 'SLT v8, GMCM v2'
fig_dir = Path('/home/chrisdc/NSHM/oqresults/CompareRateCalc')
# /home/chrisdc/NSHM/oqresults/Full_Models/SLT_v6_gmm_v0b/Compare/GMCM_corr')
hazard_models = [
    # dict(id='SLT_v8_gmm_v1',name='SLT v8, GMCM EE'),
    # dict(id='SLT_v8_gmm_v2',name='SLT v8, GMCM v2'),
    # dict(id='SLT_v8_gmm_v2_FINAL',name='SLT v8, FINAL'),
    # dict(id='NSHM_v1.0.1',name='NSHM v1.0.1'),
    # dict(id='NSHM_v1.0.1_CRUsens_baseline', name='15km'),
    # dict(id='NSHM_v1.0.1_sens_jump10km', name='10km'),
    # dict(id='NSHM_v1.0.1_sens_jump5km', name='5km'),
    dict(id='NSHM_v1.0.2', name='v1.0.2'),
    dict(id='TEST', name='TEST'),
]

legend = True
force = True
vs30 = 400
imts = ['PGA']
aggs = ["std","cov","mean", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.5", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]
omit = ['WRE']
keep = ['WLG','AKL']
# keep = ['GIS', 'WHO', 'TEU']

locations = keep
location_codes = []
for loc in locations:
    if type(loc) is str:
        pt = (LOCATIONS_BY_ID[loc]["latitude"], LOCATIONS_BY_ID[loc]["longitude"])
        grid_res = 0.001
    else:
        pt = loc
        grid_res = 0.1
    location_codes.append(CodedLocation(*pt,grid_res).downsample(0.001).code)

aggs = ["mean", '0.05', '0.1', '0.9', '0.95']
imts = ["PGA"]

xscale = 'log'
xlim = [1e-2,1e1]
# xlim = [0,3]
ylim = [1e-6,1]
# ylim = [0,.0025]


#=============================================================================================================================#



PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
colors = ['#1b9e77', '#d95f02', '#7570b3']

if not fig_dir.exists():
    fig_dir.mkdir()

for hazard_model in hazard_models:
    hazard_model['data'] = get_hazard(hazard_model['id'], location_codes, vs30, imts, aggs, force=force)

POES = [0.1,0.02]
INVESTIGATION_TIME = 50
bandws = {
            '0.5,10,90,99.5':{'lower2':'0.05','lower1':'0.1','upper1':'0.9','upper2':'0.95'},
            # '10,20,80,90':{'lower2':'0.01','lower1':'0.1','upper1':'0.9','upper2':'0.99'},
        }

ref_lines = []
for poe in POES:
        ref_line = dict(type = 'poe',
                        poe = poe,
                        inv_time = INVESTIGATION_TIME)
        ref_lines.append(ref_line)

for imt in imts:
    for location in locations:
        print(f'plotting {location} ... ')
        if type(location) is str:
            pt = (LOCATIONS_BY_ID[location]["latitude"], LOCATIONS_BY_ID[location]["longitude"])
            name = LOCATIONS_BY_ID[location]['name']
            grid_res = 0.001
        else:
            pt = location
            name = str(pt)
            grid_res = 0.1
        loc = CodedLocation(*pt,grid_res).downsample(0.001).code

        for bounds,bandw in bandws.items():
            fig, ax = plt.subplots(1,1)
            fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
            fig.set_facecolor('white')

            handles = []
            labels = []
            for i, hazard_model in enumerate(hazard_models):
                handles.append(
                    plot_hazard_curve_fromdf(hazard_model['data'], loc, imt, ax, xlim, ylim,
                                                xscale=xscale,central='mean',
                                                bandw=bandw,ref_lines=ref_lines,
                                                color=colors[i]))
                labels.append(hazard_model['name'])


            if legend:
                plt.legend(handles,labels)
            title = f'{plot_title} {name} vs30={vs30} {imt} {bounds}'
            plot_name = '_'.join( (name,str(vs30),imt,bounds) ) + '.png'
            file_path = Path(fig_dir,plot_name) 
            ax.set_title(title)
            # plt.savefig(file_path)
            plt.show()
            # plt.pause(1)
            # time.sleep(5)
            # plt.close()

