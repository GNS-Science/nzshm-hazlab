import numpy as np
from pathlib import Path
import itertools
import matplotlib.pyplot as plt

from nzshm_common.location.location import LOCATIONS_BY_ID

disagg_dir = Path('/home/chrisdc/NSHM/Disaggs/ReAggDisagg')

disagg_filenamess = [
    #AKL
    'deagg_-36.870~174.770_PGA_10.npy',
    'deagg_-36.870~174.770_PGA_2.npy',
    #WLG
    'deagg_-41.300~174.780_PGA_2.npy',
    'deagg_-41.300~174.780_PGA_10.npy',
    'deagg_-41.300~174.780_SA(1.5)_10.npy',
    'deagg_-41.300~174.780_SA(3.0)_10.npy',
    'deagg_-41.300~174.780_SA(1.5)_2.npy',
    'deagg_-41.300~174.780_SA(3.0)_2.npy',
    #CHC
    'deagg_-43.530~172.630_PGA_2.npy',
    'deagg_-43.530~172.630_PGA_10.npy',
    'deagg_-43.530~172.630_SA(1.5)_2.npy',
    'deagg_-43.530~172.630_SA(3.0)_2.npy',
    #DUD
    'deagg_-45.870~170.500_PGA_10.npy',
    'deagg_-45.870~170.500_PGA_2.npy',
]
fig_dir = Path('/home/chrisdc/NSHM/oqresults/Full_Models/SLT_v8_gmm_v2/Disaggs/')

cmap = 'OrRd'
xlim = (5,10)
ylim = (0,200)

ylim = dict(
    Auckland=(0,80),
    Christchurch=(0,200),
    Dunedin=(0,80),
    Wellington=(0,80),
)

vmax = dict(
    Auckland=13,
    Christchurch=17,
    Dunedin=11,
    Wellington=25,
)


for disagg_filename in disagg_filenamess:
    disagg_filepath = Path(disagg_dir,disagg_filename)
    junk, latlon, imt, poe = disagg_filepath.stem.split('_')
    # junk, latlon, imt, poe, junk2 = disagg_filepath.stem.split('_')
    lat,lon = latlon.split('~')
    poe = float(poe)

    site_name = [loc['name'] for loc in LOCATIONS_BY_ID.values() if (loc['latitude'] == float(lat)) & (loc['longitude'] == float(lon))][0]
    disagg = np.load(disagg_filepath)


    mags = np.arange(5.25,10,.5)
    # mags = np.arange(5.2395, 10.0, 0.499)
    # mags = np.arange(5.1,10,.2)
    # mags = np.arange(5.09745, 10.0, .1999)
    dists = np.arange(5,550,10)
    trts =  ['Active Shallow Crust', 'Subduction Interface', 'Subduction Intraslab']
    nmags = len(mags)
    ndists = len(dists)
    ntrts = len(trts)
    plot_title = f'{site_name} {imt} {int(poe)}% in 50yrs'

    axis_mag = 0
    axis_dist = 1
    axis_trt = 2

    disaggs = np.empty((len(mags),len(dists),len(trts)))
    for i, (imag, idist, itrt) in enumerate(itertools.product(range(nmags), range(ndists), range(ntrts))):
        disaggs[imag,idist,itrt] = disagg[i]
    

    disagg_trt = np.sum(disaggs,axis=(axis_mag,axis_dist))
    print(plot_title, sum(disagg_trt))
    fig, ax = plt.subplots(2,1,gridspec_kw={'height_ratios': [1, 2.5]})
    fig.set_size_inches(10,10)    
    fig.set_facecolor('white')
    ax[0].bar(trts,disagg_trt/sum(disagg_trt)*100)
    ax[0].set_title(plot_title)
    ax[0].set_ylim((0,100))
    ax[0].set_ylabel(f'% contribution to hazard')

    disagg_md = np.sum(disaggs,axis=axis_trt)
    disagg_md = disagg_md/np.sum(disagg_md) * 100
    x, y = np.meshgrid(mags,dists)
    # pcx = ax[1].pcolormesh(x,y,disagg_md.transpose(),vmin=0,vmax=np.max(disagg_md),shading='auto',cmap=cmap)
    pcx = ax[1].pcolormesh(x,y,disagg_md.transpose(),vmin=0,vmax=vmax[site_name],shading='auto',cmap=cmap)
    fig.colorbar(pcx,label=f'% contribution to hazard')
    ax[1].set_xlim(xlim)
    ax[1].set_ylim(ylim[site_name])
    ax[1].set_xlabel('Magnitude')
    ax[1].set_ylabel('Distance (km)')

    fig_name = f'disagg_{site_name}_{imt}_{int(poe)}.png'
    fig_filepath = Path(fig_dir,fig_name)
    plt.savefig(fig_filepath)
    plt.close()


# plt.show()
