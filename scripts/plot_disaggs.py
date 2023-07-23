import matplotlib.pyplot as plt

from nzshm_common.location.location import LOCATION_LISTS, location_by_id
from nzshm_common.location.code_location import CodedLocation
import nzshm_hazlab.disagg_plotting_functions as dpf
import nzshm_hazlab.disagg_data_functions as ddf
from toshi_hazard_store import model, query


hazard_model_id = 'NSHM_v1.0.4'
loc_key = 'AKL'
imt = 'PGA'
vs30 = 400
poe = model.ProbabilityEnum._10_PCT_IN_50YRS
hazard_agg = model.AggregationEnum.MEAN
xlim = (5, 10)
ylim = (0, 120)
xlim = None
ylim = None
title = f"{location_by_id(loc_key)['name']}, {imt}, {poe.name.split('_')[1]}% in 50 years, $V_{{s30}}$={vs30}m/s"

location = CodedLocation(location_by_id(loc_key)['latitude'], location_by_id(loc_key)['longitude'], 0.001).code

disagg = next(query.get_disagg_aggregates([hazard_model_id],[hazard_agg],[hazard_agg],[location],[vs30],[imt],[poe]))

# fig, ax = plt.subplots(1,1)
# fig.set_size_inches(8,6)    
# fig.set_facecolor('white')

# dpf.plot_mag_dist_2d(fig, ax, disagg.disaggs, disagg.bins, xlim, ylim)
# ax.set_title(title)

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

