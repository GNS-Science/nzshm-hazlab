import itertools
import toml
from collections import namedtuple

from toshi_hazard_store import model, query


Gridded = namedtuple("Gridded", "vs30 imt poe agg")

site_list = "NZ_0_1_NB_1_1"
hazard_model_id = 'NSHM_v1.0.4'
aggs = ["mean", "cov", "0.05", "0.1", "0.2", "0.5", "0.8", "0.9", "0.95"]
# aggs = ["mean"]
# aggs = ["std", "mean", "cov"]
# vs30s = [400]
vs30s = [
    150,
    175,
    200,
    225,
    250,
    275,
    300,
    350,
    375,
    400,
    450,
    500,
    600,
    750,
    900,
    1000,
    1500
]

# imts = ["PGA"]
imts = ['PGA',
 'SA(0.1)',
 'SA(0.2)',
 'SA(0.3)',
 'SA(0.4)',
 'SA(0.5)',
 'SA(0.7)',
 'SA(1.0)',
 'SA(1.5)',
 'SA(2.0)',
 'SA(3.0)',
 'SA(4.0)',
 'SA(5.0)',
 'SA(6.0)',
 'SA(7.5)',
 'SA(10.0)'
 ]

# poes = [0.02, 0.10]
poes = [0.86]

grids_expected = []
for vs30, imt, poe, agg in itertools.product(vs30s, imts, poes, aggs):
    grids_expected.append(
        Gridded(vs30=vs30, imt=imt, poe=poe, agg=agg)
    )

grids_received = []
for ghaz in query.get_gridded_hazard([hazard_model_id], [site_list], vs30s, imts, aggs, poes):
    print(ghaz)
    grids_received.append(
        Gridded(vs30=ghaz.vs30, imt=ghaz.imt, poe=ghaz.poe, agg=ghaz.agg)
    )

print(f'expectd: {len(grids_expected)}')
print(f'received: {len(grids_received)}')

print('MISSING GRIDDED HAZARD')
disaggs_missing = set(grids_expected).difference(set(grids_received))
vs30s_missing = []
poes_missing = []
imts_missing = []
aggs_missing = []
for d in disaggs_missing:
    print(d)
    vs30s_missing.append(d.vs30)
    poes_missing.append(d.poe)
    imts_missing.append(d.imt)
    aggs_missing.append(d.agg)

# with open('missing_no_mean.tmol', 'w') as config_file:
#     d = dict(
#         hazard_model_ids = [hazard_model_id] * len(vs30s_missing),
#         site_list = site_list,
#         vs30s = vs30s_missing,
#         poes = list(set(poes_missing)),
#         imts = imts_missing,
#         aggs = aggs_missing,
#     )
    # toml.dump(d, config_file)

