import matplotlib.pyplot as plt

from nzshm_common.location.location import LOCATION_LISTS, location_by_id
from nzshm_common.location.code_location import CodedLocation
import nzshm_hazlab.disagg_plotting_functions as dpf
import nzshm_hazlab.disagg_data_functions as ddf
from toshi_hazard_store import model, query


hazard_model_id = 'NSHM_v1.0.4'
loc_key = 'WLG'
# loc_key = 'srg_163'
imt = 'SA(0.2)'
vs30 = 200
poe = model.ProbabilityEnum._2_PCT_IN_50YRS
hazard_agg = model.AggregationEnum.MEAN
xlim = (5, 10)
ylim = (0, 350)
xlim = None
ylim = None
title = f"{location_by_id(loc_key)['name']}, {imt}, {poe.name.split('_')[1]}% in 50 years, $V_{{s30}}$={vs30}m/s"
# title = ""

location = CodedLocation(location_by_id(loc_key)['latitude'], location_by_id(loc_key)['longitude'], 0.001).code
# location = "-45.400~170.400"

disagg = next(query.get_disagg_aggregates([hazard_model_id],[hazard_agg],[hazard_agg],[location],[vs30],[imt],[poe]))

fig, ax = plt.subplots(1,1)
fig.set_size_inches(8,6)    
fig.set_facecolor('white')

dpf.plot_mag_dist_2d(fig, ax, disagg.disaggs, disagg.bins, xlim, ylim)
ax.set_title(title)

# fig, ax = plt.subplots(2,3)
fig = plt.figure()
widths = [2,2,2]
heights = [1,2]
# gs = fig.add_gridspec(2, 3, hspace=0.1, wspace=0.05)
gs = fig.add_gridspec(2, 3, width_ratios=widths, height_ratios=heights, hspace=0.08, wspace=0.07)
ax = gs.subplots()
fig.set_size_inches(12,5)    
fig.set_facecolor('white')
dpf.plot_mag_dist_trt_2d_v2(fig, ax, disagg.disaggs, disagg.bins, xlim, ylim)
fig.suptitle(title, fontsize=12)


# fig, ax = plt.subplots(1,1)
# fig.set_size_inches(8,6)    
# fig.set_facecolor('white')
# dpf.plot_trt(fig, ax, disagg.disaggs, disagg.bins)
# ax.set_title(title, fontsize=12)

# fig, ax = plt.subplots(2,1)
# fig.set_size_inches(8,8)
# fig.set_facecolor('white')
# dpf.plot_trt(fig, ax[0], disagg.disaggs, disagg.bins)
# dpf.plot_mag_dist_2d(fig, ax[1], disagg.disaggs, disagg.bins, xlim, ylim)

plt.show()

def disagg_2d(disagg, bins):
    from nzshm_hazlab.disagg_data_functions import prob_to_rate
    import numpy as np

    TRTS =  ['Active Shallow Crust', 'Subduction Interface', 'Subduction Intraslab']
    AXIS_MAG = 0
    AXIS_DIST = 1
    AXIS_TRT = 2
    AXIS_EPS = 3

    disaggs_r = prob_to_rate(disagg)
    disagg_md_r = np.sum(disaggs_r,axis=(AXIS_TRT,AXIS_EPS))
    # disagg_md = disagg_md/np.sum(disagg_md) * 100
    disagg_md_r = disagg_md_r/np.sum(disagg_md_r) * 100
    x, y = np.meshgrid(bins[AXIS_MAG], bins[AXIS_DIST])

    return x, y, disagg_md_r.transpose()