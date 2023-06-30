import itertools
from pathlib import Path

from nzshm_common.location.location import LOCATION_LISTS
from nzshm_hazlab.map_plotting_functions import plot_hazard_map, get_poe_grid

# MODEL PARAMETERS
# hazard_model = dict(id='SLT_v8_gmm_v2_FINAL',name='v1.0.0')
hazard_model = dict(id='NSHM_v1.0.4',name='v1.0.4')
vs30s = [250]
# imts = ['PGA', 'SA(0.5)', 'SA(1.0)', 'SA(3.0)']
imts = ['PGA']
agg = 'mean'
# poes = [0.02, 0.1]
poes = [0.1]

# MAP PARAMETERS
climits_small = (0.1, 2.5)
climits_large = (0.5, 5)
dpi = None # 100
filetype = 'pdf'
plot_width = 10
font_size = 10 #12 
plot_faults = True
colormap = 'inferno' # 'viridis', 'jet', 'plasma', 'imola', 'hawaii'
## region = None
region = "165/180/-50/-34"
fig_dir = Path('/home/chrisdc/Documents/My Papers/2022_NSHM_NZ_Overview')
# cities = ["AKL", "WLG", "CHC", "srg_164", "DUD"]
cities = ["AKL", "HLZ", "NPL", "WLG", "NPE", "CHC", "DUD", "TEU"]
# cities = [loc for loc in LOCATION_LISTS['NZ']['locations']]
# cities = []

projection = f'M{plot_width}c'
font = f'{font_size}p'
font_annot = f'{int(0.8*font_size)}p'

for vs30, imt, poe in itertools.product(vs30s, imts, poes):
    grid = get_poe_grid(hazard_model['id'], vs30, imt, agg, poe)
    if float(grid.max()) < 2.5:
        climits = climits_small
    else:
        climits = climits_large

    # grid = None
    #============================================================================================================
    filename = Path(fig_dir, f"hazardmap_{vs30}_{imt}_{int(poe*100)}.pdf")

    legend_text = f'{imt} ({poe*100:.0f}% PoE in 50 years)'
    fig = plot_hazard_map(grid, colormap, dpi, climits, font, font_annot, plot_width, legend_text,
                          region, plot_cities=cities, plot_faults=plot_faults)
    # fig.savefig(str(filename))