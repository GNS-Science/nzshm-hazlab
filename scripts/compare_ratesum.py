import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from nzshm_common.location.location import LOCATIONS_BY_ID
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids.region_grid import load_grid
from toshi_hazard_store.query_v3 import get_hazard_curves


from oq_hazard_report.plotting_functions import plot_hazard_curve_fromdf

ARCHIVE_DIR = '/home/chrisdc/NSHM/oqdata/HAZ_CURVE_ARCHIVE'

def get_hazard(hazard_id, loc, vs30, imt, agg):

    levels = []
    values = []
    res = next(get_hazard_curves([loc], [vs30], [hazard_id], [imt], [agg]))
    for value in res.values:
        levels.append(value.lvl)
        values.append(value.val)
    
    values = np.array(values)
    levels = np.array(levels)
    return levels, values



modelid_orig = 'SLT_v8_gmm_v2_FINAL'
# modelid_new = 'NSHM_v1.0.1'
modelids = ['NSHM_v1.0.1_hires_pt1', 'NSHM_v1.0.1_hires_pt0p5', 'NSHM_v1.0.1_hires_custom']
vs30 = 400
imts = ['SA(0.2)']
# aggs = ["mean", "0.005", "0.01", "0.025", "0.05", "0.1", "0.2", "0.5", "0.8", "0.9", "0.95", "0.975", "0.99", "0.995"]
# aggs = ["mean", "0.9", "0.95", "0.975", "0.99", "0.995"]
aggs = ["mean"]

location_id = "WLG"

xlim = [1e-4,1e1]
ylim = [1e-6,1]

#=============================================================================================================================#



PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
grid_res = 0.001


for imt in imts:
    pt = (LOCATIONS_BY_ID[location_id]["latitude"], LOCATIONS_BY_ID[location_id]["longitude"])
    loc_code = CodedLocation(*pt,grid_res).downsample(grid_res).code
    location_name = LOCATIONS_BY_ID[location_id]['name']

    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
    fig.set_facecolor('white')

    for id in modelids:
        for agg in aggs:
            # levels_orig, apoes_orig = get_hazard(modelid_orig, loc_code, vs30, imt, agg)
            levels_new, apoes_new = get_hazard(id, loc_code, vs30, imt, agg)
            # ax.plot(levels_orig, apoes_orig,'-o',label = f'orig {agg}')
            # ax.plot(levels_new, apoes_new,'-o', label = f'new {agg}')
            ax.plot(levels_new, apoes_new,'-o', label = f'mean, {id}')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_ylim(ylim)
    ax.set_xlim(xlim)
    ax.set_xlabel('Shaking Intensity, %s [g]'%imt)
    ax.set_ylabel('Annual Probability of Exceedance')
    ax.grid(color='lightgray')

    ax.legend()

    title = f'{location_name} vs30={vs30} {imt}'
    ax.set_title(title)
    plt.show()


