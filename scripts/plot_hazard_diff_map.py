from pathlib import Path
import pandas as pd

from nzshm_hazlab.map_plotting_functions import plot_hazard_diff_map, get_poe_grid


def load_2010(vs30, poe, imt):
    haz_2010_dir = Path('/home/chrisdc/NSHM/DATA/2010_haz_map_data')
    haz_2010_filepath = Path(haz_2010_dir, f'hazard_map-mean_vs_{vs30}.csv')
    haz = pd.read_csv(str(haz_2010_filepath), header=1)
    if poe == 0.1:
        column_name = f'{imt}-0.002105'
    elif poe == 0.02:
        column_name = f'{imt}-0.000404'
    else:
        raise Exception('poe must be 0.1 or 0.02')

    keep_cols = {'lat', 'lon', column_name}
    haz = haz.drop(labels=set(haz.columns).difference(keep_cols), axis=1)
    haz = haz.pivot(index="lat", columns="lon")
    haz = haz.droplevel(0, axis=1)
    return haz

# MODEL PARAMETERS
# hazard_model1 = dict(id='NSHM_v1.0.3',name='v1.0.3')
# hazard_model1 = dict(id='SLT_v8_gmm_v2_FINAL',name='v1.0.0')
hazard_model1 = dict(id='NSHM_2010',name='2010')
hazard_model2 = dict(id='NSHM_v1.0.4',name='v1.0.4')
vs30 = 250
# imt =  'SA(5.0)' # 'PGA' # 'SA(5.0)' # 'SA(3.0)' 'SA(1.0)'
# imts = ['PGA', 'SA(0.5)', 'SA(1.0)', 'SA(3.0)']
imts = ['PGA']
agg = 'mean'
# poes = [0.02, 0.1]
poes = [0.1]

# DIFFERRENCE PARAMETERS
diff_type = 'ratio' #'sub' 
# diff_type = 'sub'

# MAP PARAMETERS
# climits = [-0.4, 0.4] # None # [0.6,1.1]
# climits = None
# climits = [0.95,1.05]
climits = [0.5, 5.0]
plot_faults = False
# contours = {'interval': 0.2, 'annotation': "0.2+f8p+v"}
contours = {'interval': 0.2, 'annotation': "0.2+f5p", 'label_placement':"d1.5c"}

# tics = ','.join([f'{0.1*x:0.1f}' for x in range(5,51)])
# contours = {'interval': tics,
            # 'annotation': tics + "+f8p+v"}
region = "165/180/-48/-34"
## region = "173/177/-43/-39"
plot_width = 10
dpi = None # 100
filetype = 'pdf'
font_size = 12 
fig_dir = Path('/home/chrisdc/Documents/My Papers/2022_NSHM_NZ_Overview')


for imt in imts:
    for poe in poes:
        filepath = Path(fig_dir, f'ratio_2022_2010_vs{vs30}_{imt}_{int(100*poe)}in50.pdf')

        grids = {}

        if hazard_model1['id'] == 'NSHM_2010':
            grids['model1'] = load_2010(vs30, poe, imt)
        else:
            grids['model1'] = get_poe_grid(hazard_model1['id'], vs30, imt, agg, poe)
        grids['model2'] = get_poe_grid(hazard_model2['id'], vs30, imt, agg, poe)

        font = f'{font_size}p'
        font_annot = f'{int(0.8*font_size)}p'
        projection = f'M{plot_width}c'


        #============================================================================================================
        full_dir = Path(fig_dir,f'{int(vs30)}')

        if diff_type == 'sub':
            legend_text = f'{imt} ({poe*100:.0f}% PoE in 50 years) - difference in g'
        elif diff_type == 'ratio':
            legend_text = f'{imt} ({poe*100:.0f}% PoE in 50 years) - ratio'
        fig = plot_hazard_diff_map(grids['model1'], grids['model2'],diff_type, dpi, climits, font, font_annot, plot_width, legend_text, region, plot_faults=plot_faults, contours=contours)
        # fig.savefig(str(filepath))

                    
                    