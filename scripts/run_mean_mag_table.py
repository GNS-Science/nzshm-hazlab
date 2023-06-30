import csv
import itertools


from nzshm_common.location.location import LOCATION_LISTS
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.grids import load_grid
from toshi_hazard_store import model

from nzshm_hazlab.misc.mean_mag import get_mean_mags, all_clocations


def write_mean_mag_file(hazard_id, locations, vs30s, imts, poes, hazard_agg, filepath):

    records = []
    header = ['site code','site name', 'latitude', 'longitude', 'vs30', 'poe (% in 50 years)', 'imt', 'imtl (g)', 'mean magnitude']
    with open(filepath, 'w') as meanmag_file:
        writer = csv.writer(meanmag_file)
        writer.writerow(header)
        for disagg in get_mean_mags(hazard_id, locations, vs30s, imts, poes, hazard_agg):
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
    for loc, poe in itertools.product(locations, poes):
        if loc.code in all_clocations:
            id = LOCATION_LISTS['SRWG214']['locations'][all_clocations.index(loc.code)]
        else:
            id = loc.code
        records.append((id, poe))
    return records


# ███    ███  █████  ██ ███    ██ 
# ████  ████ ██   ██ ██ ████   ██ 
# ██ ████ ██ ███████ ██ ██ ██  ██ 
# ██  ██  ██ ██   ██ ██ ██  ██ ██ 
# ██      ██ ██   ██ ██ ██   ████ 

# mean_mag_filepath= Path(Path.home(), 'NSHM', 'Disaggs', 'mean_mags_hb.csv')
mean_mag_filepath = "./grid_mean_mag_86.csv"
hazard_id = "NSHM_v1.0.4_mag"
# hazard_id = "TEST"
imts = ['PGA']
vs30s = [275]
poes = [
    # model.ProbabilityEnum._2_PCT_IN_50YRS,
    # model.ProbabilityEnum._5_PCT_IN_50YRS,
    # model.ProbabilityEnum._10_PCT_IN_50YRS,
    # model.ProbabilityEnum._18_PCT_IN_50YRS,
    # model.ProbabilityEnum._39_PCT_IN_50YRS,
    # model.ProbabilityEnum._63_PCT_IN_50YRS,
    model.ProbabilityEnum._86_PCT_IN_50YRS,
]
grid_01 = set([CodedLocation(*pt, 0.001) for pt in load_grid('NZ_0_1_NB_1_1')])
grid_02 = set([CodedLocation(*pt, 0.001) for pt in load_grid('NZ_0_2_NB_1_1')])
# locations = list(grid_01.intersection(grid_02))
# locations = list(grid_01.difference(grid_02))
locations = list(grid_01)

# hazard_agg = model.AggregationEnum._90
hazard_agg = model.AggregationEnum.MEAN

poes_x = [poe.name.split('_')[1] for poe in poes]
records_expected = get_expected(locations, poes_x)
records_found = write_mean_mag_file(hazard_id, locations, vs30s, imts, poes, hazard_agg, mean_mag_filepath)

print('missing records')
records_missing = []
for record in records_expected:
    try:
        records_found.index(record)
    except ValueError:
        records_missing.append(record)
        print(record)