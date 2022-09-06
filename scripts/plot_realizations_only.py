import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import math
from nzshm_common.location.location import LOCATIONS_BY_ID
from nzshm_common.location.code_location import CodedLocation
from matplotlib.collections import LineCollection

def compute_hazard_at_poe(levels,values,poe,inv_time):

    rp = -inv_time/np.log(1-poe)
    haz = np.exp( np.interp( np.log(1/rp), np.flip(np.log(values)), np.flip(np.log(levels)) ) )
    return haz, 1/rp

def get_branch_inds(levels, branch_probs, target_prob, target_level, num_branches):
    
    nbranches = branch_probs.shape[0]
    dists = np.empty((nbranches,))
    min_dist = math.inf
    for i in range(nbranches):
        rlz_level, rlz_prob = compute_hazard_at_poe(levels,branch_probs[i,:],poe,inv_time)
        dists[i] = abs(rlz_level - target_level)
        # if dist < min_dist:
        #     nearest_rlz = i
        #     min_dist = dist
        #     nearest_level = rlz_level

    # return nearest_rlz
    sorter = np.argsort(dists)
    return sorter[:num_branches]




def load_data(filepaths):

    dtype = {'lat':str,'lon':str}

    data = {}

    with open(source_branches_filepath,'r') as source_file:
        data['source_branches'] = json.load(source_file)

    with open(source_leaves_filepath,'r') as source_file:
        data['source_leaves'] = json.load(source_file)

    with open(grouped_source_leaves_filepath,'r') as source_file:
        data['grouped_source_leaves'] = json.load(source_file)

    data['weights'] = np.load(weights_filepath,allow_pickle=True)
    data['branch_probs'] = np.load(branch_probs_filepath,allow_pickle=True)
    data['agg_hcurves']  = pd.read_json(agg_filepath,dtype=dtype)

    return data


def get_agg_poe(agg_hcurves, ocation, imt, agg):
    pt = [(loc['latitude'], loc['longitude']) for loc in LOCATIONS_BY_ID.values() if loc['id']==location][0]
    ll = CodedLocation(*pt,0.001).downsample(point_res).code
    lat, lon = ll.split('~')


    
    levels = list(set(agg_hcurves['level']))
    levels.sort()
    levels = np.array(levels)

    apoe = agg_hcurves.loc[ (agg_hcurves['lat']==lat) & 
                            (agg_hcurves['lon']==lon) & 
                            (agg_hcurves['agg']==agg)  & 
                            (agg_hcurves['imt']==imt) , 'hazard'].to_numpy()

    return levels, apoe



# title = 'Realizations: Rhoades and Rastin'
# branch_probs_filepath = '/home/chrisdc/NSHM/oqresults/tmp/realizations_Nrr.npy'

# title = 'Realizations: Rollins'
# branch_probs_filepath = '/home/chrisdc/NSHM/oqresults/tmp/realizations_Ncr.npy'

# title = 'Realizations: geologic, TI, N2.7, b0.823 C4.2 s0.59'
# fn = 'b0823.png'
# branch_probs_filepath = '/home/chrisdc/NSHM/oqresults/tmp/realizations_Nrr_wings1.npy'

# title = 'Realizations: geologic TI, N3.4, b0.959 C4.2 s0.59'
# fn = 'b0959.png'
# branch_probs_filepath = '/home/chrisdc/NSHM/oqresults/tmp/realizations_Nrr_wings2.npy'

title = 'Realizations: geologic, TI, N4.6, b1.089 C4.2 s0.59'
fn = 'b1089.png'
branch_probs_filepath = '/home/chrisdc/NSHM/oqresults/tmp/realizations_Nrr_wings3.npy'



branch_probs = np.load(branch_probs_filepath,allow_pickle=True)


xlim = [1e-2,1e1]
ylim = [1e-7,1e0]
imt = 'PGA'
location = 'AKL'
point_res = 0.001
poe = 0.1
inv_time = 50
agg = 'mean'
# num_branches = 96228
num_branches = 11

data = {}
dtype = {'lat':str,'lon':str}
agg_filepath = '/home/chrisdc/NSHM/oqresults/TAG_final/data/FullLT_allIMT_nz34_all_aggregates.json'
data['agg_hcurves']  = pd.read_json(agg_filepath,dtype=dtype)
levels, apoe = get_agg_poe(data['agg_hcurves'],location, imt, agg)



fig, ax = plt.subplots(1,1)
fig.set_size_inches(8,8)    
fig.set_facecolor('white')
segs = np.zeros((num_branches,29,2))
segs[:,:,0] = levels
segs[:,:,1] = branch_probs[:num_branches,:]
line_segments = LineCollection(segs,linewidths=2.0,alpha=1.0)
ax.add_collection(line_segments)

ax.set_xscale('log')
ax.set_yscale('log')
ax.grid(color='lightgray')
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_title(title)

plt.savefig(fn)

