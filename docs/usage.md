To use nzshm-hazlab you must first [install the library](./installation.md)

## Load Hazard Curves
```py
from nzshm_hazlab.data.hazard_curves import HazardCurves
from nzshm_hazlab.data.data_loaders import THSHazardLoader
from nzshm_common.location import CodedLocation, location_by_id
from nzshm_common.location import get_locations


hazard_model = "TEST_MODEL"
dataset_dir = "./toshi_hazard_store/AGG/"
loader = THSHazardLoader(dataset_dir=dataset_dir)
hazard_curves_NSHM22 = HazardCurves(loader=loader)

location_ids = ["WLG", "DUD", "CHC", "AKL"]
locations = get_locations(location_ids)

aggs = ["mean", "0.1"]
imts = ["PGA", "SA(1.0)"]
vs30s = [400]

for location in locations:
    for imt in imts:
        for vs30 in vs30s:
            levels, values = hazard_curves_NSHM22.get_hazard_curve(hazard_model, imts[0], locations[0], vs30s[0], aggs[0])
            print(levels, values)
            print('='*50)
```

## Create Hazard Curves from User Defined Model (Logic Trees)
```py
from nzshm_hazlab.data.data_loaders import THPHazardLoader
from nzshm_hazlab.data import HazardCurves
from nzshm_model.logic_tree import SourceLogicTree, GMCMLogicTree

hazard_model_ths = "NSHM_v1.0.4"
slt = SourceLogicTree.from_json("srm_logic_tree.json")
gmcm = GMCMLogicTree.from_json("gmcm_logic_tree.json")
thp_loader = THPHazardLoader("NZSHM22", slt, gmcm)
hazard_curves = HazardCurves(loader=thp_loader)
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

bin_centers, disagg_matrix =disaggs.get_disaggregations(hazard_model, dimensions, imt, location, vs30, poe, agg)
print(bin_centers)
print(disagg_matrix.shape)
```


## Load a Hazard Grid
```py
from nzshm_common.grids import get_location_grid
from nzshm_hazlab.data import HazardGrids
from nzshm_hazlab.data.data_loaders import DynamoGridLoader
from toshi_hazard_store.model import ProbabilityEnum

loader = DynamoGridLoader()
hazard_grids = HazardGrids(loader=loader)

hazard_model_id = "NSHM_v1.0.4"
grid_name = "NZ_0_1_NB_1_1"
poe = ProbabilityEnum._2_PCT_IN_50YRS
agg = "mean"
imt = "SA(1.0)"
vs30 = 750

hazard_grid = hazard_grids.get_grid(hazard_model_id, imt, grid_name, vs30, poe, agg)
locations = get_location_grid('NZ_0_1_NB_1_1')
```

## Plot Hazard Curve and UHS
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


## Plot Disaggregations
```py
import matplotlib.pyplot as plt
from nzshm_common.location import get_locations
from toshi_hazard_store.model import ProbabilityEnum
from nzshm_hazlab.plot import plot_disagg_1d, plot_disagg_2d, plot_disagg_3d

from nzshm_hazlab.data import Disaggregations
from nzshm_hazlab.data.data_loaders import DynamoDisaggLoader

hazard_model = "NSHM_v1.0.4"
location = get_locations(["WLG"])[0]
dimensions = ["mag", "dist"]
agg = "mean"
imt = "PGA"
vs30 = 400
poe = ProbabilityEnum._10_PCT_IN_50YRS

loader = DynamoDisaggLoader()
disaggs = Disaggregations(loader=loader)
bin_centers, disagg_matrix = disaggs.get_disaggregation(hazard_model, dimensions, imt, location, vs30, poe, agg)

fig, ax = plt.subplots(1, 1)
ax = plot_disagg_1d(ax, disaggs, hazard_model, location, imt, vs30, poe, agg, dimension="trt")

fig, ax = plt.subplots(1, 1)
ax = plot_disagg_2d(ax, disaggs, hazard_model, location, imt, vs30, poe, agg, dimensions=["mag", "dist"])

fig, ax = plt.subplots(1, 3)
ax = plot_disagg_2d(list(ax), disaggs, hazard_model, location, imt, vs30, poe, agg, dimensions=["mag", "dist"], split_by_trt=True)

fig = plt.figure()
plot_disagg_3d(fig, disaggs, hazard_model, location, imt, vs30, poe, agg, dist_lim=[0, 70])

plt.show()
```

## Plot Hazard Maps
```py
from nzshm_hazlab.data import HazardGrids
from nzshm_hazlab.plot import plot_hazard_map, plot_hazard_diff_map
from nzshm_hazlab.data.data_loaders import DynamoGridLoader
from toshi_hazard_store.model import ProbabilityEnum
import matplotlib.pyplot as plt

loader = DynamoGridLoader()
hazard_grids = HazardGrids(loader=loader)

hazard_model_id = "NSHM_v1.0.4"
grid_name = "NZ_0_1_NB_1_1"
agg = "mean"
poe = ProbabilityEnum._10_PCT_IN_50YRS
imt = "PGA"
vs30 = 400
filepath = f"hazard_grid-{hazard_model_id}-{imt}-{grid_name}-{vs30}-{poe.name}-{agg}"

fig, ax = plot_hazard_map(hazard_grids, hazard_model_id, grid_name, imt, vs30, poe, agg, clim=[0, 1.5])
poe_split = poe.name.split('_') 
ax.set_title(f"{imt} {poe_split[1]}% in {poe_split[-1]}")

hgs = [hazard_grids, hazard_grids]
hmids = [hazard_model_id, hazard_model_id]
imts = ["PGA", "SA(1.0)"]
vs30s = [vs30, vs30]
poes = [poe, poe]
aggs = [agg, agg]
diff_type = 'sub'
fig, ax = plot_hazard_diff_map(hgs, hmids, grid_name, imts, vs30s, poes, aggs, diff_type=diff_type)
ax.set_title("subtraction")

diff_type = 'ratio'
fig, ax = plot_hazard_diff_map(hgs, hmids, grid_name, imts, vs30s, poes, aggs, diff_type=diff_type)
ax.set_title("ratio")


plt.show()
```