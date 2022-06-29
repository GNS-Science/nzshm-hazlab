import numpy as np
import time

from oq_hazard_report.hazard_data import HazardData
from oq_hazard_report.data_functions import weighted_quantile

import runzi.automation.scaling.hazard_output_helper
from runzi.automation.scaling.toshi_api import ToshiApi
from runzi.automation.scaling.local_config import (API_KEY, API_URL)


def get_hazard_ids(gt_id):

    headers={"x-api-key":API_KEY}
    toshi_api = ToshiApi(API_URL, None, None, with_schema_validation=True, headers=headers)

    h = runzi.automation.scaling.hazard_output_helper.HazardOutputHelper(toshi_api)
    sub = h.get_hazard_ids_from_gt(gt_id)

    return list(sub.keys())




location = 'WLG'
imt = 'PGA'

def aggrigate_realizations_1ID(hazard_id):

    hd = HazardData(hazard_id)
    for irlz in range(hd.nrlzs):
        if irlz == 0:
            levels = np.array(hd.values(location=location,imt=imt,realization=irlz).lvls)
            values = np.array(hd.values(location=location,imt=imt,realization=irlz).vals)
        else:
            values = np.vstack((values,np.array(hd.values(location=location,imt=imt,realization=irlz).vals)))

    weights = np.array(list(hd.rlz_lt['weight'].values()))
    median = np.array([])
    for i,level in enumerate(levels):
        # quantiles = weighted_quantile(values[:,i],[0.5],sample_weight=weights)
        quantiles = weighted_quantile(values[:,i],'mean',sample_weight=weights)
        median = np.append(median,np.array(quantiles))

    return median


def aggrigate_realizations_multID(gt_id):

    hazard_ids = get_hazard_ids(gt_id)
    weights = np.array([])
    for i,hazard_id in enumerate(hazard_ids):
        hd = HazardData(hazard_id)
        
        for irlz in range(hd.nrlzs):
            if irlz == 0 and i == 0:
                levels = np.array(hd.values(location=location,imt=imt,realization=irlz).lvls)
                values = np.array(hd.values(location=location,imt=imt,realization=irlz).vals)
            else:
                values = np.vstack((values,np.array(hd.values(location=location,imt=imt,realization=irlz).vals)))
        breakpoint()
        weights = np.append(weights,np.array(list(hd.rlz_lt['weight'].values())))
        
    weights = weights/np.sum(weights)

    tic = time.perf_counter()
    median = np.array([])
    for i,level in enumerate(levels):
        # quantiles = weighted_quantile(values[:,i],[0.5],sample_weight=weights)
        quantiles = weighted_quantile(values[:,i],'mean',sample_weight=weights)
        median = np.append(median,np.array(quantiles))
    toc = time.perf_counter()
    print(f'seconds to calculate median {toc-tic}')


    return median



if __name__ == "__main__":

    hazard_id = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzOTU3' #get correct ID
    gt_id = 'R2VuZXJhbFRhc2s6MTA0MzQ2'
    median_calc = aggrigate_realizations_1ID(hazard_id)
    median_indv = aggrigate_realizations_multID(gt_id)

    hd = HazardData(hazard_id)
    median_oq = np.array(hd.values(location=location,imt=imt,realization='mean').vals)

    print('=========== median from oq-engine: ==============')
    print(median_oq)

    print('=========== median from rlz of single job: ==============')
    print(median_calc)

    print('=========== % difference: ==============')
    print(100*(median_calc-median_oq)/median_oq)

    print('=========== median from individual jobs: ==============')
    print(median_indv)

    print('=========== % difference: ==============')
    print(100*(median_indv-median_oq)/median_oq)

