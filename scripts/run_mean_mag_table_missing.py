import csv
from pathlib import Path
import itertools

import numpy as np

from nzshm_common.location.location import location_by_id, LOCATION_LISTS
from nzshm_common.location.code_location import CodedLocation
from toshi_hazard_store import model, query

from nzshm_hazlab.disagg_data_functions import prob_to_rate
# from nzshm_hazlab.disagg_data_functions import calc_mean_disagg

def lat_lon(id):
    return (location_by_id(id)['latitude'], location_by_id(id)['longitude'])

all_locations = [CodedLocation(*lat_lon(id), 0.001) for id in LOCATION_LISTS['SRWG214']['locations']]
all_clocations = [loc.code for loc in all_locations]

def calc_mean_disagg(disagg, bins):

    AXIS_MAG = 0
    AXIS_DIST = 1
    AXIS_TRT = 2
    AXIS_EPS = 3

    disagg = prob_to_rate(disagg)
    return np.sum( disagg / np.sum(disagg) * bins[0] )
    # return np.sum(np.sum(disagg, axis = (AXIS_DIST, AXIS_TRT, AXIS_EPS) ) / np.sum(disagg) * bins[AXIS_MAG])

    # return np.sum(np.sum(disagg, axis = (AXIS_DIST, AXIS_TRT) ) / np.sum(disagg) * bins[AXIS_MAG])


def get_mean_mags(model_specs):

    for spec in model_specs:
        cloc = spec['location'].code

        disagg = query.get_one_disagg_aggregation(
            spec['hazard_id'],
            model.AggregationEnum.MEAN,
            model.AggregationEnum.MEAN,
            cloc,
            spec['vs30'],
            spec['imt'],
            spec['poe'],
        )
        if disagg: 
            mean_disagg = calc_mean_disagg(disagg.disaggs, disagg.bins)
            id = LOCATION_LISTS['SRWG214']['locations'][all_clocations.index(disagg.nloc_001)]
            d = dict(
                id = id,
                name = location_by_id(id)['name'],
                lat = location_by_id(id)['latitude'],
                lon = location_by_id(id)['longitude'],
                vs30 = disagg.vs30,
                poe = disagg.probability.name.split('_')[1],
                imt = disagg.imt,
                imtl = f"{disagg.shaking_level:0.2e}",
                mag = f"{mean_disagg:0.2f}",
            )
            yield d
        else:
            print(f'missing {spec}')

def write_mean_mag_file(specs, filepath):

    records = []
    header = ['site code','`site name', 'latitude', 'longitude', 'vs30', 'poe (% in 50 years)', 'imt', 'imtl (g)', 'mean magnitude']
    with open(filepath, 'w') as meanmag_file:
        writer = csv.writer(meanmag_file)
        writer.writerow(header)
        for disagg in get_mean_mags(specs):
            records.append((disagg['id'], disagg['poe']))
            writer.writerow(
                [
                    disagg['id'],
                    disagg['name'],
                    disagg['lat'],
                    disagg['lon'],
                    disagg['vs30'],
                    disagg['poe'],
                    disagg['imt'],
                    disagg['imtl'],
                    disagg['mag'],
                ]
            )
    return records

def get_expected(locations, poes):
    records = []
    for id, poe in itertools.product(locations, poes):
        records.append((id, poe))
    return records


# ███    ███  █████  ██ ███    ██ 
# ████  ████ ██   ██ ██ ████   ██ 
# ██ ████ ██ ███████ ██ ██ ██  ██ 
# ██  ██  ██ ██   ██ ██ ██  ██ ██ 
# ██      ██ ██   ██ ██ ██   ████ 

mean_mag_filepath= Path(Path.home(), 'NSHM', 'Disaggs', 'mean_mags_srwg214_p90.csv')
specs = [
    # dict(
    #     location = CodedLocation(*lat_lon('srg_148'), 0.001),
    #     hazard_id = 'NSHM_v1.0.2',
    #     vs30 = 275,
    #     imt = 'PGA',
    #     poe = model.ProbabilityEnum._2_PCT_IN_50YRS,
    # ),
    # dict(
    #     location = CodedLocation(*lat_lon('srg_149'), 0.001),
    #     hazard_id = 'NSHM_v1.0.2',
    #     vs30 = 275,
    #     imt = 'PGA',
    #     poe = model.ProbabilityEnum._2_PCT_IN_50YRS,
    # ),
    # dict(
    #     location = CodedLocation(*lat_lon('srg_156'), 0.001),
    #     hazard_id = 'NSHM_v1.0.2',
    #     vs30 = 275,
    #     imt = 'PGA',
    #     poe = model.ProbabilityEnum._2_PCT_IN_50YRS,
    # ),
    # dict(
    #     location = CodedLocation(*lat_lon('srg_188'), 0.001),
    #     hazard_id = 'NSHM_v1.0.2',
    #     vs30 = 275,
    #     imt = 'PGA',
    #     poe = model.ProbabilityEnum._2_PCT_IN_50YRS,
    # ),
    # dict(
    #     location = CodedLocation(*lat_lon('srg_149'), 0.001),
    #     hazard_id = 'NSHM_v1.0.2_MAGDISTRTONLY',
    #     vs30 = 275,
    #     imt = 'PGA',
    #     poe = model.ProbabilityEnum._5_PCT_IN_50YRS,
    # ),
    # dict(
    #     location = CodedLocation(*lat_lon('srg_188'), 0.001),
    #     hazard_id = 'NSHM_v1.0.2_MAGDISTRTONLY',
    #     vs30 = 275,
    #     imt = 'PGA',
    #     poe = model.ProbabilityEnum._5_PCT_IN_50YRS,
    # ),

    dict(
        location = CodedLocation(*lat_lon('srg_29'), 0.001),
        hazard_id = 'NSHM_v1.0.2_MAGONLY_P90',
        vs30 = 275,
        imt = 'PGA',
        poe = model.ProbabilityEnum._2_PCT_IN_50YRS,
    ),
    dict(
        location = CodedLocation(*lat_lon('srg_29'), 0.001),
        hazard_id = 'NSHM_v1.0.2_MAGONLY_P90',
        vs30 = 275,
        imt = 'PGA',
        poe = model.ProbabilityEnum._5_PCT_IN_50YRS,
    ),
    dict(
        location = CodedLocation(*lat_lon('srg_29'), 0.001),
        hazard_id = 'NSHM_v1.0.2_MAGONLY_P90',
        vs30 = 275,
        imt = 'PGA',
        poe = model.ProbabilityEnum._10_PCT_IN_50YRS,
    ),
    dict(
        location = CodedLocation(*lat_lon('srg_29'), 0.001),
        hazard_id = 'NSHM_v1.0.2_MAGONLY_P90',
        vs30 = 275,
        imt = 'PGA',
        poe = model.ProbabilityEnum._18_PCT_IN_50YRS,
    ),
    dict(
        location = CodedLocation(*lat_lon('srg_29'), 0.001),
        hazard_id = 'NSHM_v1.0.2_MAGONLY_P90',
        vs30 = 275,
        imt = 'PGA',
        poe = model.ProbabilityEnum._39_PCT_IN_50YRS,
    ),
    dict(
        location = CodedLocation(*lat_lon('srg_29'), 0.001),
        hazard_id = 'NSHM_v1.0.2_MAGONLY_P90',
        vs30 = 275,
        imt = 'PGA',
        poe = model.ProbabilityEnum._63_PCT_IN_50YRS,
    ),
    dict(
        location = CodedLocation(*lat_lon('srg_29'), 0.001),
        hazard_id = 'NSHM_v1.0.2_MAGONLY_P90',
        vs30 = 275,
        imt = 'PGA',
        poe = model.ProbabilityEnum._86_PCT_IN_50YRS,
    ),
]

records_found = write_mean_mag_file(specs, mean_mag_filepath)
# poes_x = ('2', '5', '10', '18', '39', '63', '86')
# records_expected = get_expected(LOCATION_LISTS['SRWG214']['locations'], poes_x)

# print('missing records')
# for record in records_expected:
#     try:
#         records_found.index(record)
#     except ValueError:
#         print(record)