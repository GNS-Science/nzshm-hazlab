import json
from pathlib import Path
import matplotlib.pyplot as plt
import oq_hazard_report.disagg_plotting_functions_old as dpf

from runzi.automation.scaling.toshi_api import ToshiApi
from runzi.automation.scaling.local_config import (API_KEY, API_URL, WORK_PATH)
from runzi.automation.scaling.hazard_output_helper import HazardOutputHelper

headers={"x-api-key":API_KEY}
toshi_api = ToshiApi(API_URL, None, None, with_schema_validation=True, headers=headers)


site_name = 'Kerikeri'
site_name = 'Franz Josef'
site_name = 'Tauranga'
site_name = 'Hamilton'
site_name = 'Auckland'
poe = 0.1
imt = 'SA(0.5)'
# imt = 'PGA'

disagg_result_file = Path('/home/chrisdc/NSHM/Disaggs/disagg_result.json')
with open(disagg_result_file,'r') as jsonfile:
    disaggs = json.load(jsonfile)


for disagg in disaggs['hazard_solutions']:
    if (disagg['site_name'] == site_name) & (disagg['imt'] == imt) & (disagg['poe'] == poe):
        print(site_name, poe, imt)
        print(disagg['hazard_solution_csv_archive_url'])
        # print(disagg)
        print(disagg['gsims'])
        print(disagg['source_ids'])
        print(disagg['location'])
        print(disagg['target_level'])
        hazard_solution_id = disagg['hazard_solution_id']
        break



h = HazardOutputHelper(toshi_api)
hazard_solutions = h.download_csv([hazard_solution_id],WORK_PATH)
csv_archive = list(hazard_solutions.values())[0]['filepath']
print(csv_archive)

assert 0

fig, ax = dpf.plot_disagg_trt(csv_archive)
ax.set_title(f'{site_name} {imt} {poe*100:.0f}% in 50')

mags,dists,rates_int,rates_slab,rates_cru = dpf.load_DMT_disagg(csv_archive)

Mags, Dists, Rates_int, Rates_slab, Rates_cru, Rates_tot = dpf.meshgrid_disaggs(mags,dists,rates_int,rates_slab,rates_cru)
fig, ax = dpf.plot_disagg2d(Mags, Dists, Rates_int, Rates_slab, Rates_cru, Rates_tot)
plt.suptitle(f'{site_name} {imt} {poe*100:.0f}% in 50')

fig, ax = dpf.plot_disagg(mags, dists, rates_int, rates_slab, rates_cru)