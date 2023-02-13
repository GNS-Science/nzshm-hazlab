from pathlib import Path

from nzshm_hazlab.map_plotting_functions import plot_hazard_diff_map, get_poe_grid

# MODEL PARAMETERS
hazard_model1 = dict(id='SLT_v8_gmm_v2_FINAL',name='v1.0.0')
hazard_model2 = dict(id='NSHM_v1.0.2',name='v1.0.2')
vs30 = 400
imt =  'PGA' # 'SA(5.0)' # 'SA(3.0)' 'SA(1.0)'
agg = 'mean'
poe = 0.02

# DIFFERRENCE PARAMETERS
diff_type = 'sub' # 'ratio'

# MAP PARAMETERS
climits = None # [0.6,1.1]
plot_faults = False
region = "170/180/-42/-34"
plot_width = 10
dpi = None # 100
filetype = 'pdf'
font_size = 12 
fig_dir = Path('/home/chrisdc/NSHM/oqresults/Full_Models/SLT_v8_gmm_v2/Maps')

grids = {}
grids['model1'] = get_poe_grid(hazard_model1['id'], imt, agg, poe, vs30)
grids['model2'] = get_poe_grid(hazard_model2['id'], imt, agg, poe, vs30)
font = f'{font_size}p'
font_annot = f'{int(0.8*font_size)}p'
projection = f'M{plot_width}c'


#============================================================================================================
full_dir = Path(fig_dir,f'{int(vs30)}')

if diff_type == 'sub':
    legend_text = f'{imt} ({poe*100:.0f}% PoE in 50) - difference'
elif diff_type == 'ratio':
    legend_text = f'{imt} ({poe*100:.0f}% PoE in 50) - ratio'
plot_hazard_diff_map(grids['model1'], grids['model2'],diff_type, dpi, climits, font, font_annot, plot_width, legend_text, region, plot_faults=plot_faults)

                
                    