from pathlib import Path

import matplotlib.pyplot as plt
from nzshm_model import get_model_version, CURRENT_VERSION
import shapely

from solvis import CompositeSolution, mfd_hist, InversionSolution
from solvis.filter.rupture_id_filter import FilterRuptureIds



comp_soln_path = Path('/home/chrisdc/NSHM/DEV/APP/solvis-jupyterlab/WORKDIR/NSHM_v1.0.4_CompositeSolution.zip')
nz_poly_path = Path('/home/chrisdc/NSHM/DEV/nzshm-hazlab/scripts/NZ_poly.geojson')
slt = get_model_version(CURRENT_VERSION).source_logic_tree
comp_soln = CompositeSolution.from_archive(comp_soln_path, slt)

hik = comp_soln.get_fault_system_solution('HIK')
cru = comp_soln.get_fault_system_solution('CRU')
puy = comp_soln.get_fault_system_solution('PUY')

with nz_poly_path.open() as f:
    nz_poly = shapely.from_geojson(f.read())
print(nz_poly)


# useful function but requires users to pass a dataframe. maybe take an inversion (or model) as arg?
# Also, would be nice to be able to specify bins or bin spacing
mfd = mfd_hist(cru.model.ruptures_with_rupture_rates, "rate_weighted_mean")  
rate = mfd.to_numpy()
mag = [a.mid for a in mfd.index]
import numpy as np
crate = np.flip(np.flip(rate).cumsum())
for m, r in zip(mag, crate):
    print(m, r)
assert 0

rupture_ids = FilterRuptureIds(hik).for_polygon(nz_poly).for_magnitude(0, 8.0)
# rupture_ids = FilterRuptureIds(hik).for_polygon(nz_poly)
print(rupture_ids)

# returns a very usefule DataFrame with info about a rupture, but buried deep in API
# maybe the repr of an inversion (or model) should be a dataframe repr
print(hik.model.ruptures_with_rupture_rates)  
# doc states function not often used, but I think quite useful for creating new OQ input or ploting
# MFD. Also, could be non-static and use instace of inversion
hik_filt = InversionSolution.filter_solution(hik, rupture_ids) 
print(hik_filt.model.ruptures_with_rupture_rates)
