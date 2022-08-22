import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from nzshm_common.location.location import LOCATIONS_BY_ID
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids.region_grid import load_grid
from toshi_hazard_store.query_v3 import get_hazard_curves


from oq_hazard_report.plotting_functions import plot_hazard_curve_fromdf

plot_title = 'SLT v7, GMCM EE'
fig_dir = Path('/home/chrisdc/NSHM/oqresults/Full_Models/SLT_v7_gmm_v1/Compare')
# /home/chrisdc/NSHM/oqresults/Full_Models/SLT_v6_gmm_v0b/Compare/GMCM_corr')
hazard_models = [
    # dict(id='SLT_v5_gmm_v0',name='full model'),
    
    # dict(id='SLT_v5_gmm_v0_ST_baseline',name='15km'),
    # dict(id='SLT_v5_gmm_v0_ST_10km',name='10km'),
    
    # dict(id='SLT_v5_gmm_v0_ST_NBnoNs',name='NB=true. Nscaling=false'),
    # dict(id='SLT_v5_gmm_v0_ST_NsnoNB',name='NB=false. Nscaling=true'),

    # dict(id='SLT_v5_gmm_v0_ST_baseline',name='NB=true. Nscaling=true'),
    # dict(id='SLT_v5_gmm_v0_ST_NBnoNs',name='NB=true. Nscaling=false'),
    
    # dict(id='SLT_v5_gmm_v0_ST_baseline',name='NB=true. Nscaling=true'),
    # dict(id='SLT_v5_gmm_v0_ST_NsnoNB',name='NB=false. Nscaling=true'),

    # dict(id='SLT_v5_gmm_v0_ST_Ncr',name='Rollins Scaling'),
    # dict(id='SLT_v5_gmm_v0_ST_Nrr',name='Rhoades and Rastin Scaling'),    

    # dict(id='SLT_v5_gmm_v0_ST_TI',name='Time Indepdendent'),
    # dict(id='SLT_v5_gmm_v0_ST_TD',name='Time Dependent'), 

    # dict(id='SLT_v5_gmm_v0',name='Full LT'),
    # dict(id='SLT_v5_gmm_v0_Scorr_v2',name='Correlated LT'),

    # dict(id='SLT_v5_gmm_v0',name='Full LT'),
    # dict(id='SLT_v5_gmm_v0_SRWG',name='SRWG'),

    # dict(id='SLT_v5_gmm_v0',name='SLT v5, GMCM v0'),
    # dict(id='SLT_v6_gmm_v0b',name='SLT v6, GMCM v0b'),

    # dict(id='SLT_v6_gmm_v0b',name='WITHOUT GMCM correlation'),
    # dict(id='SLT_v6_gmm_v0b_corr',name='WITH GMCM correlation'),

    dict(id='SLT_v6_gmm_v0b',name='SLT v6, GMCM v0b'),
    dict(id='SLT_v7_gmm_v1',name='SLT v7, GMCM EE'),



]


vs30 = 400
imts = ['PGA','SA(0.5)','SA(1.5)','SA(3.0)','SA(5.0)']

aggs = ['mean','0.01','0.1','0.9','0.99']


locations = [f"{loc['latitude']:0.3f}~{loc['longitude']:0.3f}" for loc in LOCATIONS_BY_ID.values()]

xscale = 'log'
xlim = [1e-2,1e1]
# xlim = [0,4]
ylim = [1e-6,1]


#=============================================================================================================================#

def get_hazard(hazard_id, locs, vs30, imts, aggs):

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

    return hazard_curves

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
bandws = {
            # '0.5,10,90,99.5':{'lower2':'0.005','lower1':'0.1','upper1':'0.9','upper2':'0.995'},
            '1.0,10,90,99':{'lower2':'0.01','lower1':'0.1','upper1':'0.9','upper2':'0.99'},
        }

ref_lines = []
for poe in POES:
        ref_line = dict(type = 'poe',
                        poe = poe,
                        inv_time = INVESTIGATION_TIME)
        ref_lines.append(ref_line)

for imt in imts:
    for location in LOCATIONS_BY_ID.keys():
        print(f'plotting {location} ... ')
        for bounds,bandw in bandws.items():
            pt = (LOCATIONS_BY_ID[location]["latitude"], LOCATIONS_BY_ID[location]["longitude"])
            loc = CodedLocation(*pt,grid_res).downsample(grid_res).code
            name = LOCATIONS_BY_ID[location]['name']

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


            plt.legend(handles,labels)
            title = f'{plot_title} {name} {imt} {bounds}'
            plot_name = '_'.join( (name,imt,bounds) ) + '.png'
            file_path = Path(fig_dir,plot_name) 
            ax.set_title(title)
            plt.savefig(file_path)
            plt.close()

