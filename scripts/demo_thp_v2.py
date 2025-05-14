from nzshm_common.location.location import LOCATION_LISTS, location_by_id
from nzshm_common.location import CodedLocation
from nzshm_hazlab.store.curves_v4 import get_hazard as get_hazard_v4, ArrowFS
from nzshm_hazlab.plotting_functions import plot_hazard_curve
import matplotlib.pyplot as plt

from nzshm_hazlab.locations import get_locations, lat_lon

CODED_LOCS = [CodedLocation(*lat_lon(key), 0.001) for key in LOCATION_LISTS["ALL"]["locations"]]

resolution = 0.001
INVESTIGATION_TIME = 50
PLOT_WIDTH = 12
PLOT_HEIGHT = 8.625
colors = ['k', '#1b9e77', '#d95f02', '#7570b3']
xscale = 'log'
xlim = [1e-2,1e1]
# xlim = [0,3]
ylim = [1e-8,1]


def location_2_dict(loc: CodedLocation) -> str:

    if loc in CODED_LOCS:
       ind = CODED_LOCS.index(loc)
       return location_by_id(LOCATION_LISTS["ALL"]["locations"][ind])
    return dict(
        id=loc.code,
        name=loc.code,
        latitude=loc.lat,
        longitude=loc.lon,
    )
    

def ref_lines(poes):
    refls = []
    for poe in poes:
        ref_line = dict(type = 'poe',
                        poe = poe,
                        inv_time = INVESTIGATION_TIME)
        refls.append(ref_line)
    return refls


error_bounds = {'lower2':'0.01','lower1':'0.1','upper1':'0.9','upper2':'0.99'}
aggs = list(error_bounds.values()) + ['mean']

location_codes = ["WLG"]
locations = get_locations(location_codes)

imts = ["PGA"]
poes = [0.1, 0.02]
fs_specs = dict(
    arrow_fs=ArrowFS.LOCAL,
    arrow_dir='/home/chrisdc/NSHM/DATA/toshi-hazard-store/AGG_BKUP',
    # arrow_dir='/home/chrisdc/mnt/glacier_data/toshi_hazard_store/AGG_FROM_F64'
)

# model_ids = ['NSHM_v1.0.4', 'DEMO_A']
# model_ids = ['NSHM_v1.0.4']
# model_ids = ['NSHM_2022_DEMO', 'HIGHEST_WEIGHT', 'CRUSTAL_ONLY']
model_ids = ['NSHM_2022_DEMO']
vs30 = 275

hazard_models = dict()
for model_id in model_ids:
    hazard_models[model_id] = get_hazard_v4(model_id, vs30, locations, imts, aggs, fs_specs)


for loc in locations:
    loc_dict = location_2_dict(loc)
    loc_key, loc_name = loc_dict["id"], loc_dict["name"]
    for imt in imts:
        fig, ax = plt.subplots(1,1)
        fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
        fig.set_facecolor('white')
        title = f'{loc_name} {imt}, Vs30 = {vs30}m/s'
        for i, (model_id, hazard) in enumerate(hazard_models.items()):
            lh, levels = plot_hazard_curve(
                hazard, loc, imt, ax, xlim, ylim,
                xscale=xscale,central='mean',
                ref_lines=ref_lines(poes),
                color=colors[i],
                custom_label=model_id,
                title=title,
                # bandw=error_bounds
            )
        plt.show()