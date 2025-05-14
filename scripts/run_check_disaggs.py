import itertools
from collections import namedtuple

import matplotlib.pyplot as plt

from toshi_hazard_store import model, query
from nzshm_common.location.code_location import CodedLocation
from nzshm_common.location.location import location_by_id, LOCATION_LISTS


DisaggDef = namedtuple("DisaggDef", "vs30 imt poe location")

hazard_model_id = 'NSHM_v1.0.4'
hazard_agg = model.AggregationEnum.MEAN
vs30s = [750]
imts = ["PGA", "SA(0.2)", "SA(0.5)", "SA(1.5)", "SA(3.0)"]
# imts = ["PGA", "SA(0.2)", "SA(0.5)", "SA(1.5)"]
# imts = ["SA(3.0)"]
poes = [
    # model.ProbabilityEnum._05_PCT_IN_50YRS,
    model.ProbabilityEnum._2_PCT_IN_50YRS,
    model.ProbabilityEnum._5_PCT_IN_50YRS,
    model.ProbabilityEnum._10_PCT_IN_50YRS,
    model.ProbabilityEnum._18_PCT_IN_50YRS,
    model.ProbabilityEnum._39_PCT_IN_50YRS,
    model.ProbabilityEnum._63_PCT_IN_50YRS,
    model.ProbabilityEnum._86_PCT_IN_50YRS,
]

location_ids = LOCATION_LISTS['NZ']['locations'] + ['srg_164']
# location_ids = ['srg_164']
locations = [CodedLocation(location_by_id(lid)['latitude'], location_by_id(lid)['longitude'],0.001) for lid in location_ids]

disaggs = query.get_disagg_aggregates(
    [hazard_model_id],
    [hazard_agg],
    [hazard_agg],
    [loc.code for loc in locations],
    vs30s,
    imts,
    poes,
)

disaggs_expected = []
for vs30, imt, poe, location in itertools.product(vs30s, imts, poes, locations):
    disaggs_expected.append(
        DisaggDef(vs30=vs30, imt=imt, poe=poe, location=location)
    )

disaggs_received = []
for disagg in disaggs:
    disaggs_received.append(
        DisaggDef(vs30=disagg.vs30, imt=disagg.imt, poe=disagg.probability, location=CodedLocation( *map(float,disagg.nloc_001.split('~')), 0.001))
    )



print(f'expectd: {len(disaggs_expected)}')
print(f'received: {len(disaggs_received)}')

print('MISSING DISAGGS')
disaggs_missing = set(disaggs_expected).difference(set(disaggs_received))
locs_missing = []
for d in disaggs_missing:
    location_id = location_ids[locations.index(d.location)]
    locs_missing.append(location_id)
    print(location_id, d)

locs_missing = set(locs_missing)
print(locs_missing)