import numpy as np
from toshi_hazard_store import model, query


def compute_hazard_at_poe(levels,values,poe,inv_time):

    rp = -inv_time/np.log(1-poe)
    haz = np.exp( np.interp( np.log(1/rp), np.flip(np.log(values)), np.flip(np.log(levels)) ) )
    return haz
        
    
def weighted_quantile(values, quantiles, sample_weight=None, 
                      values_sorted=False, old_style=False):
    """ Very close to numpy.percentile, but supports weights.
    NOTE: quantiles should be in [0, 1]!
    :param values: numpy.array with data
    :param quantiles: array-like with many quantiles needed. Can also be string 'mean' to calculate weighted mean
    :param sample_weight: array-like of the same length as `array`
    :param values_sorted: bool, if True, then will avoid sorting of
        initial array
    :param old_style: if True, will correct output to be consistent
        with numpy.percentile.
    :return: numpy.array with computed quantiles.
    """

    values = np.array(values)
    if sample_weight is None:
        sample_weight = np.ones(len(values))
    sample_weight = np.array(sample_weight)

    if quantiles == 'mean':
        return np.sum(sample_weight * values)


    quantiles = np.array(quantiles)

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

    

def calculate_agg(hazard_data, location, imt, agg):
    for irlz in range(hazard_data.nrlzs):
        if irlz == 0:
            levels = np.array(hazard_data.values(location=location,imt=imt,realization=irlz).lvls)
            values = np.array(hazard_data.values(location=location,imt=imt,realization=irlz).vals)
        else:
            values = np.vstack((values,np.array(hazard_data.values(location=location,imt=imt,realization=irlz).vals)))

    weights = np.array(list(hazard_data.rlz_lt['weight'].values()))
    agg_values = np.array([]) #TODO pre-allocate memory
    for i,level in enumerate(levels):
        quantiles = weighted_quantile(values[:,i],[agg],sample_weight=weights)
        agg_values = np.append(agg_values,np.array(quantiles))

    return agg_values
