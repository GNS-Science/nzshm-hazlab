import numpy as np
from pathlib import Path
import itertools
import matplotlib.pyplot as plt

from nzshm_common.location.location import LOCATIONS_BY_ID

disagg_dir = Path('/home/chrisdc/NSHM/Disaggs/')

disagg_filenamess = [
    'deagg_-43.530~172.630_PGA_0.1.npy',
    'deagg_-45.870~170.500_PGA_0.1.npy',
    'deagg_-41.300~174.780_PGA_0.1.npy',
    'deagg_-41.300~174.780_PGA_0.02.npy',
    'deagg_-43.530~172.630_PGA_0.02.npy',
    'deagg_-45.870~170.500_PGA_0.02.npy',
    # 'deagg_-41.300~174.780_PGA_0.1_highres.npy',
]
fig_dir = Path('/home/chrisdc/NSHM/oqresults/Full_Models/SLT_v8_gmm_v2/Disaggs')

cmap = 'OrRd'
xlim = (5,10)
ylim = (0,100)


for disagg_filename in disagg_filenamess:
    disagg_filepath = Path(disagg_dir,disagg_filename)
    # junk, latlon, imt, poe, junk2 = disagg_filepath.stem.split('_')
    junk, latlon, imt, poe = disagg_filepath.stem.split('_')
    lat,lon = latlon.split('~')
    poe = float(poe)

    site_name = [loc['name'] for loc in LOCATIONS_BY_ID.values() if (loc['latitude'] == float(lat)) & (loc['longitude'] == float(lon))][0]
    disagg = np.load(disagg_filepath)


    mags = np.arange(5.25,10,.5)
    # mags = np.arange(5.1,10,.2)
    dists = np.arange(5,550,10)
    trts =  ['Active Shallow Crust', 'Subduction Interface', 'Subduction Intraslab']
    nmags = len(mags)
    ndists = len(dists)
    ntrts = len(trts)
    plot_title = f'{site_name} {imt} {int(poe*100)}% in 50yrs'

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
    ax[0].bar(trts,disagg_trt/sum(disagg_trt))
    ax[0].set_title(plot_title)
    ax[0].set_ylim((0,1))

    disagg_md = np.sum(disaggs,axis=axis_trt)
    disagg_md = disagg_md/np.sum(disagg_md)
    x, y = np.meshgrid(mags,dists)
    pcx = ax[1].pcolormesh(x,y,disagg_md.transpose(),vmin=0,vmax=0.1,shading='auto',cmap=cmap)
    fig.colorbar(pcx)
    ax[1].set_xlim(xlim)
    ax[1].set_ylim(ylim)
    ax[1].set_xlabel('Magnitude')
    ax[1].set_ylabel('Distance (km)')

    fig_name = plot_title = f'disagg_{site_name}_{imt}_{int(poe*100)}.png'
    fig_filepath = Path(fig_dir,fig_name)
    plt.savefig(fig_filepath)
    plt.close()


# plt.show()
