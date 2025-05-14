import json
from pathlib import Path
import numpy as np
from nzshm_common.location import get_locations

imt = "PGA"
vs30 = 275
location_id = "WLG"
location_code = get_locations([location_id])[0].code
root_dir = Path('/home/chrisdc/mnt/glacier_data/branch_rlz')
weight_filepath = root_dir / f'weights_{imt}-{location_code}-{vs30}.npy'
hazcurves_filepath = root_dir / f'branches_{imt}-{location_code}-{vs30}.npy'
branch_data_filepath = root_dir / f'source_branches_{imt}-{location_code}-{vs30}.json'

weights = np.load(weight_filepath)
hazcurves = np.load(hazcurves_filepath)
with open(branch_data_filepath,'r') as bdfile:
    branch_data = json.load(bdfile)

n_branches_srm = len(branch_data)
n_branches_gmcm = len(branch_data[0]['weight_combs'])
branch_info = [None] * n_branches_srm * n_branches_gmcm

i = 0
for src_branch in branch_data:
    gsim_lookup = {}
    source_tags = src_branch['tags']
    for trt, gsim_ids in src_branch['rlz_sets'].items():
        for gsim, ids in gsim_ids.items():
            for id in ids:
                gsim_lookup[id] = {'trt':trt, 'gsim':gsim}
    for gmcm_branch in src_branch['rlz_combs']:

        sources = dict(
            cru = source_tags[0],
            hik = source_tags[1],
            puy = source_tags[2],
            slab = source_tags[3],
        )
        gsims = {gsim_lookup[id]['trt']:gsim_lookup[id]['gsim'] for id in gmcm_branch}
        branch_info[i] = {'sources':sources, 'gsims':gsims}
        i += 1


