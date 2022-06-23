import numpy as np
import time

from oq_hazard_report.hazard_data import HazardData

import runzi.automation.scaling.hazard_output_helper
from runzi.automation.scaling.toshi_api import ToshiApi
from runzi.automation.scaling.local_config import (API_KEY, API_URL)


def get_hazard_ids(gt_id):

    headers={"x-api-key":API_KEY}
    toshi_api = ToshiApi(API_URL, None, None, with_schema_validation=True, headers=headers)

    h = runzi.automation.scaling.hazard_output_helper.HazardOutputHelper(toshi_api)
    sub = h.get_hazard_ids_from_gt(gt_id)

    return list(sub.keys())


def weightedQuantile(values, quantiles, sample_weight=None, 
                      values_sorted=False, old_style=False):
    """ Very close to numpy.percentile, but supports weights.
    NOTE: quantiles should be in [0, 1]!
    :param values: numpy.array with data
    :param quantiles: array-like with many quantiles needed
    :param sample_weight: array-like of the same length as `array`
    :param values_sorted: bool, if True, then will avoid sorting of
        initial array
    :param old_style: if True, will correct output to be consistent
        with numpy.percentile.
    :return: numpy.array with computed quantiles.
    """
    values = np.array(values)
    quantiles = np.array(quantiles)
    if sample_weight is None:
        sample_weight = np.ones(len(values))
    sample_weight = np.array(sample_weight)
    assert np.all(quantiles >= 0) and np.all(quantiles <= 1), \
        'quantiles should be in [0, 1]'

    if not values_sorted:
        sorter = np.argsort(values)
        values = values[sorter]
        sample_weight = sample_weight[sorter]

    weighted_quantiles = np.cumsum(sample_weight) - 0.5 * sample_weight
    if old_style:
        # To be convenient with numpy.percentile
        weighted_quantiles -= weighted_quantiles[0]
        weighted_quantiles /= weighted_quantiles[-1]
    else:
        weighted_quantiles /= np.sum(sample_weight)
    return np.interp(quantiles, weighted_quantiles, values)

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
        quantiles = weightedQuantile(values[:,i],[0.5],sample_weight=weights)
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

        weights = np.append(weights,np.array(list(hd.rlz_lt['weight'].values())))
        
    # breakpoint()
    weights = weights/np.sum(weights)

    tic = time.perf_counter()
    median = np.array([])
    for i,level in enumerate(levels):
        quantiles = weightedQuantile(values[:,i],[0.5],sample_weight=weights)
        median = np.append(median,np.array(quantiles))
    toc = time.perf_counter()
    print(f'seconds to calculate median {toc-tic}')


    return median



if __name__ == "__main__":

    hazard_id = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAzOTU3' #get correct ID
    gt_id = 'R2VuZXJhbFRhc2s6MTA0MzQ2'
    # median_calc = aggrigate_realizations_1ID(hazard_id)
    median_indv = aggrigate_realizations_multID(gt_id)

    hd = HazardData(hazard_id)
    median_oq = np.array(hd.values(location=location,imt=imt,realization='0.5').vals)

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

