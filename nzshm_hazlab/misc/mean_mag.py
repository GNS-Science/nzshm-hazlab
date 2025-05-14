
from nzshm_hazlab.disagg_data_functions import prob_to_rate
from toshi_hazard_store import model, query
from nzshm_common.location.code_location import CodedLocation
import numpy as np
from nzshm_common.location.location import location_by_id, LOCATION_LISTS


def lat_lon(id):
    return (location_by_id(id)['latitude'], location_by_id(id)['longitude'])

all_locations = [CodedLocation(*lat_lon(id), 0.001) for id in LOCATION_LISTS['SRWG214']['locations']]
all_clocations = [loc.code for loc in all_locations]

def get_mean_mag(disaggs, bins):
    disaggs = prob_to_rate(disaggs)
    return np.sum( disaggs / np.sum(disaggs) * bins[0] )


def get_mean_mags(hazard_id, locations, vs30s, imts, poes, hazard_agg):

    clocs = [loc.code for loc in locations]
    disaggs = query.get_disagg_aggregates(
        hazard_model_ids=[hazard_id],
        disagg_aggs = [model.AggregationEnum.MEAN],
        hazard_aggs = [hazard_agg],
        locs = clocs,
        vs30s = vs30s,
        imts = imts,
        probabilities = poes,
    )
    for disagg in disaggs:
        mean_mag = get_mean_mag(disagg.disaggs, disagg.bins)
        if disagg.nloc_001 in all_clocations:
            id = LOCATION_LISTS['SRWG214']['locations'][all_clocations.index(disagg.nloc_001)]
            name = location_by_id(id)['name']
        else:
            id = disagg.nloc_001
            name = disagg.nloc_001
        d = dict(
            id = id,
            name = name,
            lat = disagg.lat,
            lon = disagg.lon,
            vs30 = disagg.vs30,
            poe = disagg.probability.name.split('_')[1],
            imt = disagg.imt,
            imtl = f"{disagg.shaking_level:0.2e}",
            mag = mean_mag,
        )
        yield d
