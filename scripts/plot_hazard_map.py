from pathlib import Path

from nzshm_hazlab.map_plotting_functions import plot_hazard_map, get_poe_grid

# MODEL PARAMETERS
hazard_model = dict(id='SLT_v8_gmm_v2_FINAL',name='v1.0.0')
hazard_model = dict(id='NSHM_v1.0.2',name='v1.0.2')
vs30 = 400
imt = 'SA(5.0)'
agg = 'mean'
poe = 0.02

# MAP PARAMETERS
acc_min = 0.01
acc_max = 1.0
climits = (acc_min, acc_max)
dpi = None # 100
filetype = 'pdf'
plot_width = 10
font_size = 12 
plot_faults = True
colormap = 'inferno' # 'viridis', 'jet', 'plasma', 'imola', 'hawaii'
region = None
fig_dir = Path('/home/chrisdc/NSHM/oqresults/Full_Models/SLT_v8_gmm_v2/Maps')

projection = f'M{plot_width}c'
font = f'{font_size}p'
font_annot = f'{int(0.8*font_size)}p'
grid = get_poe_grid(hazard_model['id'], imt, agg, poe, vs30)
#============================================================================================================
full_dir = Path(fig_dir,f'{int(vs30)}')

legend_text = f'{imt} ({poe*100:.0f}% PoE in 50)'
fig = plot_hazard_map(grid, colormap, dpi, climits, font, font_annot, plot_width, legend_text, region, plot_faults=plot_faults)