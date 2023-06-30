import json
import numpy as np

weight_filepath = '/home/chrisdc/NSHM/branch_explorer/weights_PGA--41.300~174.780-250.npy'
hazcurves_filepath = '/home/chrisdc/NSHM/branch_explorer/branches_PGA--41.300~174.780-250.npy'
branch_data_filepath = '/home/chrisdc/NSHM/branch_explorer/source_branches_PGA--41.300~174.780-250.json'

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


