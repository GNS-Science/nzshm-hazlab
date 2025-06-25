To use nzshm-hazlab you must first [install the library](./installation.md)

## Load Hazard Curves
```py
from nzshm_hazlab.data.hazard_curves import HazardCurves
from nzshm_hazlab.data.data_loaders import THSHazardLoader
from nzshm_common.location import CodedLocation, location_by_id
from nzshm_common.location.location import _lat_lon
from nzshm_hazlab.constants import RESOLUTION


hazard_model = "TEST_MODEL"
dataset_dir = "./toshi_hazard_store/AGG/"
loader = THSHazardLoader(dataset_dir=dataset_dir)
hazard_curves_NSHM22 = HazardCurves(loader=loader)

location_ids = ["WLG", "DUD", "CHC", "AKL"]
locations = [CodedLocation(*_lat_lon(_id), RESOLUTION) for _id in location_ids]

aggs = ["mean", "0.1"]
imts = ["PGA", "SA(1.0)"]
vs30s = [400]

for location in locations:
    for imt in imts:
        for vs30 in vs30s:
            levels, values = hazard_curves_NSHM22.get_hazard_curve(hazard_model, imts[0], locations[0], aggs[0], vs30s[0])
            print(levels, values)
            print('='*50)
```

## Load Disaggregation Matrix
```py
from nzshm_common.location import get_locations
from toshi_hazard_store.model import ProbabilityEnum

from nzshm_hazlab.data import Disaggregations
from nzshm_hazlab.data.data_loaders import OQCSVDisaggLoader

hazard_model = "31"
dataset_dir = "./data/csv_loader"
loader = OQCSVDisaggLoader(dataset_dir)
disaggs = Disaggregations(loader=loader)

location = get_locations(["WLG"])[0]
dimensions = ["mag", "dist"]
agg = "mean"
imt = "PGA"
vs30 = 400
poe = ProbabilityEnum._10_PCT_IN_50YRS

bin_centers, disagg_matrix =disaggs.get_disaggregations(hazard_model, dimensions, imt, location, agg, vs30, poe)
print(bin_centers)
print(disagg_matrix.shape)
```

## Plot Data
```py
from nzshm_hazlab.data.data_loaders import THSHazardLoader
from nzshm_hazlab.data.hazard_curves import HazardCurves
from nzshm_hazlab.plot import plot_hazard_curve, plot_uhs
from nzshm_common import CodedLocation
import matplotlib.pyplot as plt

hazard_model_id = "NSHM_v1.0.4"
dataset_dir = "./toshi_hazard_store/AGG/"
loader = THSHazardLoader(dataset_dir=dataset_dir)
hazard_curves_THSr4 = HazardCurves(loader=loader)
location_id = "WLG"
location = CodedLocation(-41.3, 174.78, 0.001)

# Plot a hazard curve with error bound estimates
aggs = ["0.1", "0.2", "mean", "0.8", "0.9"]
vs30 = 400
imt = "PGA"

fig, ax = plt.subplots(1,1)
fig.set_facecolor('white')
line_handles = plot_hazard_curve(ax, hazard_curves_THSr4, hazard_model_id, location, imt, vs30, aggs, label="PGA vs30=750")

# Plot UHS and error bound estimates as dashed lines
imts = ["PGA", "SA(0.2)", "SA(0.5)", "SA(1.0)", "SA(2.0)", "SA(3.0)", "SA(5.0)", "SA(10.0)"]
investigation_time = 50.0
poe = 0.1
agg = "mean"
fig, ax = plt.subplots(1,1)
fig.set_size_inches(PLOT_WIDTH,PLOT_HEIGHT)
fig.set_facecolor('white')
plot_uhs(ax, hazard_curves_NSHM22, hazard_model_dynamo, location, imts, poe, investigation_time, vs30, aggs, linestyle="--")
plt.show()
```