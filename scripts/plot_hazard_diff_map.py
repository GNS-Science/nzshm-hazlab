from pathlib import Path

from nzshm_hazlab.map_plotting_functions import plot_hazard_diff_map, get_poe_grid

# MODEL PARAMETERS
hazard_model1 = dict(id='NSHM_v1.0.2',name='v1.0.2')
hazard_model2 = dict(id='NSHM_v1.0.3',name='v1.0.3')
vs30 = 400
# imt =  'SA(5.0)' # 'PGA' # 'SA(5.0)' # 'SA(3.0)' 'SA(1.0)'
imt = 'PGA'
# imt = "SA(3.0)"
agg = 'mean'
poe = 0.1

# DIFFERRENCE PARAMETERS
diff_type = 'ratio' #'sub' 
# diff_type = 'sub'

# MAP PARAMETERS
# climits = [-0.4, 0.4] # None # [0.6,1.1]
# climits = None
climits = [0.7,1.3]
plot_faults = False
region = "165/180/-48/-34"
plot_width = 10
dpi = None # 100
filetype = 'pdf'
font_size = 12 
fig_dir = Path('/home/chrisdc/NSHM/oqresults/Full_Models/SLT_v8_gmm_v2/Maps')

grids = {}
grids['model1'] = get_poe_grid(hazard_model1['id'], vs30, imt, agg, poe)
grids['model2'] = get_poe_grid(hazard_model2['id'], vs30, imt, agg, poe)
font = f'{font_size}p'
font_annot = f'{int(0.8*font_size)}p'
projection = f'M{plot_width}c'


#============================================================================================================
full_dir = Path(fig_dir,f'{int(vs30)}')

if diff_type == 'sub':
    legend_text = f'{imt} ({poe*100:.0f}% PoE in 50) - difference in g'
elif diff_type == 'ratio':
    legend_text = f'{imt} ({poe*100:.0f}% PoE in 50) - ratio'
plot_hazard_diff_map(grids['model1'], grids['model2'],diff_type, dpi, climits, font, font_annot, plot_width, legend_text, region, plot_faults=plot_faults)

                
                    