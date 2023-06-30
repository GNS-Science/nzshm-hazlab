from nzshm_common.location import CodedLocation
from nzshm_hazlab.store.curves import get_hazard
import matplotlib.pyplot as plt

locations = [CodedLocation(-37.2, 175, 0.001), CodedLocation(-37.1, 175.1, 0.001)]

imts = ['PGA', 'SA(0.5)', 'SA(1.5)', 'SA(3.0)']
vs30 = 400
model_id = 'NSHM_v1.0.4'
aggs = ['mean']

hazard = get_hazard(model_id, vs30, locations, imts, aggs)


fig, ax = plt.subplots(2,2)
for k, imt in enumerate(imts):

    i, j = (k%2, int(k/2))
    ind0 = (
        (hazard['lat'] == locations[0].code.split('~')[0]) & 
        (hazard['lon'] == locations[0].code.split('~')[1]) &
        (hazard['imt'] == imt)
    )
    ind1 = (
        (hazard['lat'] == locations[1].code.split('~')[0]) & 
        (hazard['lon'] == locations[1].code.split('~')[1]) &
        (hazard['imt'] == imt)
    )
    label0 = f"{locations[0].lat}, {locations[0].lon}"
    label1 = f"{locations[1].lat}, {locations[0].lon}"
    ax[i,j].loglog(hazard.loc[ind0,:]['level'].iloc[0], hazard.loc[ind0,:]['apoe'].iloc[0], label=label0)
    ax[i,j].loglog(hazard.loc[ind1,:]['level'].iloc[0], hazard.loc[ind1,:]['apoe'].iloc[0], label=label1)
    ax[i,j].set_xlim([1e-2, 5])
    ax[i,j].set_ylim([1e-6, 1e-1])
    ax[i,j].set_title(imt)
    ax[i,j].legend()
