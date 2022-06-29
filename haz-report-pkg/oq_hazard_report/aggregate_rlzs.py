import itertools
import ast

import numpy as np

from operator import mul
from functools import reduce

from oq_hazard_report.data_functions import weighted_quantile
from toshi_hazard_store.query_v3 import get_rlz_curves_v3, get_hazard_metadata_v3

inv_time = 1.0

def cache_realization_values(source_branches, loc, imt, vs30):
    values = {}
    for branch in source_branches:
        for res in get_rlz_curves_v3([loc], [vs30], None, branch['ids'], [imt]):
            key = ':'.join((res.hazard_solution_id,str(res.rlz))) #could use sort_key, but this simplifies
            values[key] = np.array(res.values[0].vals) #only one entry in res.values since query was for single imt

    return values

def build_rlz_table(branch, vs30):

    ids=branch['ids']
    rlz_sets = {}
    weight_sets = {}
    for meta in get_hazard_metadata_v3(ids, [vs30]):
        gsim_lt = ast.literal_eval(meta.gsim_lt)
        trts = set(gsim_lt['trt'].values())
        for trt in trts:
            rlz_sets[trt] = {}
            weight_sets[trt] = {}

    for meta in get_hazard_metadata_v3(ids, [vs30]):
        rlz_lt = ast.literal_eval(meta.rlz_lt)
        for trt in rlz_sets.keys():
            if trt in rlz_lt:
                gsims = set(rlz_lt[trt].values())
                for gsim in gsims:
                    rlz_sets[trt][gsim] = []

    for meta in get_hazard_metadata_v3(ids, [vs30]):
        rlz_lt = ast.literal_eval(meta.rlz_lt)
        gsim_lt = ast.literal_eval(meta.gsim_lt)
        hazard_id = meta.hazard_solution_id
        trts = set(gsim_lt['trt'].values())
        for trt in trts:
            for rlz, gsim in rlz_lt[trt].items():
                rlz_key = ':'.join((hazard_id,rlz))
                rlz_sets[trt][gsim].append(rlz_key)
                weight_sets[trt][gsim] = gsim_lt['weight'][rlz] # this depends on only one source per run and the same gsim weights in every run

    rlz_sets_tmp = rlz_sets.copy()
    weight_sets_tmp = weight_sets.copy()
    for k,v in rlz_sets.items():
        rlz_sets_tmp[k] = []
        weight_sets_tmp[k] = []
        for gsim in v.keys():
            rlz_sets_tmp[k].append(v[gsim])
            weight_sets_tmp[k].append(weight_sets[k][gsim])

    # for k,v in weight_sets.items():
    #     weight_sets_tmp[k] = list(v.values())    

    # breakpoint()    

    rlz_lists = list(rlz_sets_tmp.values())
    weight_lists = list(weight_sets_tmp.values())

    # print(rlz_lists)
    # print(weight_lists)

    # TODO: fix rlz from the same ID grouped together
    
    rlz_iter = itertools.product(*rlz_lists)
    rlz_combs = []
    for src_group in rlz_iter: # could be done with list comprehension, but I can't figure out the syntax?
        rlz_combs.append([s for src in src_group for s in src])

    # TODO: I sure hope itertools.product produces the same order every time
    weight_iter = itertools.product(*weight_lists)
    weight_combs = []
    for src_group in weight_iter: # could be done with list comprehension, but I can't figure out the syntax?
        weight_combs.append(reduce(mul, src_group, 1) )

    # for i in range(len(rlz_combs)):
    #     print(rlz_combs[i])
    #     print(weight_combs[i])


    return rlz_combs, weight_combs


def get_weights(branch, rlz_combs, vs30):

    weights = {}
    ids=branch['ids']
    for meta in get_hazard_metadata_v3(ids, [vs30]):
        rlz_lt = ast.literal_eval(meta.rlz_lt) #TODO should I be using this or gsim_lt?
        hazard_id = meta.hazard_solution_id

        for rlz,weight in rlz_lt['weight'].items():
            rlz_key = ':'.join((hazard_id,rlz))
            weights[rlz_key] = weight

    return weights


def prob_to_rate(prob):

    return -np.log(1-prob)/inv_time

def rate_to_prob(rate):

    return 1.0 - np.exp(-inv_time*rate)


def build_source_branch(values, rlz_combs):

    rate = np.zeros(next(iter(values.values())).shape)
    # branch_weights = []
    for i,rlz_comb in enumerate(rlz_combs):
        # branch_weight = 1
        for rlz in rlz_comb:
            rate += prob_to_rate(values[rlz])
            # branch_weight *= rlz_weights[rlz]
        prob = rate_to_prob(rate)
        # breakpoint()
        if i==0:
            prob_table = np.array(prob)
        else:
            prob_table = np.vstack((prob_table,np.array(prob)))
        # branch_weights.append(branch_weight)
    
    return prob_table


if __name__ == "__main__":

    # TODO: I'm making assumptions that the levels array is the same for every realization, imt, run, etc. 
    # If that were not the case, I would have to add some interpolation

    loc = "-41.300~174.780"
    vs30 = 750
    imt = 'PGA'
    # tid = 'CRUA'
    source_branches = [
        # dict(name='A', ids=['A_CRU', 'A_HIK', 'A_PUY'], weight=1.0),
        dict(name='B', ids=['B_CRU', 'B_HIK', 'B_PUY'], weight=1.0),
    ]

    #cache all realization values
    values = cache_realization_values(source_branches, loc, imt, vs30)
     

    # for each source branch, assemble the gsim realization combinations
    realization_table = np.array([]) 
    rlz_weights = {}
    for branch in source_branches:

        rlz_combs, weight_combs = build_rlz_table(branch, vs30)

         #set of realization probabilties for a single complete source branch
         #these can then be aggrigated in prob space (+/- impact of NB) to create a hazard curve
        branch_probs = build_source_branch(values, rlz_combs)
        # print(rlz_combs)
        # print(weight_combs)

        #TODO build up probabilities from other branches
    
    #TODO build up probabilities from other branches
    median = np.array([])
    for i in range(branch_probs.shape[1]):
        quantiles = weighted_quantile(branch_probs[:,i],[0.5],sample_weight=weight_combs)
        median = np.append(median,np.array(quantiles))

    # print(branch_probs)
    print(median)
    # print(values['A_CRU:7'])

