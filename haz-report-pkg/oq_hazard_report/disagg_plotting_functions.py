from dis import dis
import numpy as np
from pathlib import Path
import itertools
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
from matplotlib.colors import LightSource

MAGS = np.arange(5.25,10,.5)
DISTS = np.arange(5,550,10)
EPSS = np.arange(-3,5,2)
# EPSS = np.arange(-3.75,4.0,.5)
TRTS =  ['Active Shallow Crust', 'Subduction Interface', 'Subduction Intraslab']
AXIS_MAG = 0
AXIS_DIST = 1
AXIS_TRT = 2
AXIS_EPS = 3

CMAP = 'OrRd'
XLIM = (5,10)
YLIM = (0,350)
# YLIM = (0,600)
# >YLIM = (0,100)

cmp = cm.get_cmap(CMAP)
# white = np.array([cmp(0)[0], cmp(0)[1], cmp(0)[2], cmp(0)[3]])
white = np.array([1.0, 1.0, 1.0, 1.0])
newcolors = cmp(np.linspace(0,1,256))
newcolors[:5,:] = white
newcmp = ListedColormap(newcolors)

INV_TIME = 1.0

def prob_to_rate(prob):

    return -np.log(1 - prob) / INV_TIME


def rate_to_prob(rate):

    return 1.0 - np.exp(-INV_TIME * rate)


def assemble_disaggs(disagg):

    nmags = len(MAGS)
    ndists = len(DISTS)
    ntrts = len(TRTS)
    neps = len(EPSS)

    disaggs = np.empty((len(MAGS),len(DISTS),len(TRTS),len(EPSS)))
    for i, (imag, idist, itrt, ieps) in enumerate(itertools.product(range(nmags), range(ndists), range(ntrts), range(neps))):
        disaggs[imag,idist,itrt, ieps] = disagg[i]

    return disaggs

def plot_trt(fig, ax, disagg):

    disaggs = assemble_disaggs(disagg)
    disaggs_r = prob_to_rate(disaggs)
    # disagg_trt = rate_to_prob(np.sum(disaggs_r,axis=(AXIS_MAG,AXIS_DIST)) )
    disagg_trt_r = np.sum(disaggs_r,axis=(AXIS_MAG,AXIS_DIST,AXIS_EPS))
    # ax.bar(TRTS,disagg_trt/np.sum(disagg_trt) * 100)
    ax.bar(TRTS,disagg_trt_r/np.sum(disagg_trt_r) * 100)
    ax.set_ylim([0, 110])
    ax.set_ylabel('% Contribution to Hazard')


def plot_mag_dist_2d(fig, ax, disagg):

    disaggs = assemble_disaggs(disagg)
    disaggs_r = prob_to_rate(disaggs)

    # disagg_md = rate_to_prob(np.sum(disaggs_r,axis=AXIS_TRT))
    disagg_md_r = np.sum(disaggs_r,axis=(AXIS_TRT,AXIS_EPS))
    # disagg_md = disagg_md/np.sum(disagg_md) * 100
    disagg_md_r = disagg_md_r/np.sum(disagg_md_r) * 100
    x, y = np.meshgrid(MAGS,DISTS)
    # pcx = ax.pcolormesh(x,y,disagg_md.transpose(),vmin=0,vmax=np.max(disagg_md),shading='auto',cmap=CMAP)
    pcx = ax.pcolormesh(x,y,disagg_md_r.transpose(),vmin=0,vmax=np.max(disagg_md_r),shading='auto',cmap=newcmp)
    fig.colorbar(pcx,label=f'% Contribution to Hazard')
    ax.set_xlim(XLIM)
    ax.set_ylim(YLIM)
    ax.set_xlabel('Magnitude')
    ax.set_ylabel('Distance (km)')

def plot_mag_dist_trt_2d(fig, ax, disagg):

    disaggs = assemble_disaggs(disagg)
    disaggs_r = prob_to_rate(disaggs)
    disaggs_trt0_r = prob_to_rate(disaggs.copy()[:,:,0,:])
    disaggs_trt1_r = prob_to_rate(disaggs.copy()[:,:,1,:])
    disaggs_trt2_r = prob_to_rate(disaggs.copy()[:,:,2,:])

    disagg_md_trt0_r = np.sum(disaggs_trt0_r,axis=(AXIS_EPS-1))
    disagg_md_trt1_r = np.sum(disaggs_trt1_r,axis=(AXIS_EPS-1))
    disagg_md_trt2_r = np.sum(disaggs_trt2_r,axis=(AXIS_EPS-1))

    disagg_md_trt0_r = disagg_md_trt0_r/np.sum(disaggs_r) * 100
    disagg_md_trt1_r = disagg_md_trt1_r/np.sum(disaggs_r) * 100
    disagg_md_trt2_r = disagg_md_trt2_r/np.sum(disaggs_r) * 100

    vmax = max(np.max(disagg_md_trt0_r), np.max(disagg_md_trt1_r), np.max(disagg_md_trt2_r))

    x, y = np.meshgrid(MAGS,DISTS)
    pcx = ax[0].pcolormesh(x,y,disagg_md_trt0_r.transpose(),vmin=0,vmax=vmax,shading='auto',cmap=newcmp)
    pcx = ax[1].pcolormesh(x,y,disagg_md_trt1_r.transpose(),vmin=0,vmax=vmax,shading='auto',cmap=newcmp)
    pcx = ax[2].pcolormesh(x,y,disagg_md_trt2_r.transpose(),vmin=0,vmax=vmax,shading='auto',cmap=newcmp)
    ax[0].set_title(TRTS[0])    
    ax[1].set_title(TRTS[1])    
    ax[2].set_title(TRTS[2])    
    fig.colorbar(pcx,label=f'% Contribution to Hazard')

    for a in ax:
        a.set_xlim(XLIM)
        a.set_ylim(YLIM)
    ax[0].set_xlabel('Magnitude')
    ax[0].set_ylabel('Distance (km)')



def plot_single_mag_dist_eps(fig, ax, disagg, ylim):

    ls = LightSource(azdeg=45, altdeg=10)

    cmp = cm.get_cmap('coolwarm')
    newcolors = cmp(np.linspace(0,1,len(EPSS)))
    newcmp = ListedColormap(newcolors)
    norm = Normalize(vmin=-4, vmax=4)
    
    dind = DISTS <= ylim[1]
    dists = DISTS[dind]
    _xx, _yy = np.meshgrid(MAGS, dists)
    x, y = _xx.T.ravel(), _yy.T.ravel()
    width = 0.1    
    depth = (ylim[1]-ylim[0])/(XLIM[1] - XLIM[0]) * width


    
    disaggs = assemble_disaggs(disagg)
    disaggs_mde_r = np.sum(prob_to_rate(disaggs),axis=AXIS_TRT) / np.sum(prob_to_rate(disaggs)) * 100

    disaggs_mde_r = disaggs_mde_r[:,dind,:]
    bottom = np.zeros( x.shape )
    for i in range(len(EPSS)):
        z0 = bottom
        z1 = disaggs_mde_r[:,:,i].ravel()
        ind = z1 > 0.1
        if any(ind):
            ax.bar3d(x[ind], y[ind], z0[ind], width, depth, z1[ind], color=newcolors[i], lightsource=ls, alpha=1.0)
            bottom += disaggs_mde_r[:,:,i].ravel()

    # cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=newcmp), ticks=EPSS, shrink = 0.3, anchor=(0.0,0.75),label='epsilon')
    # cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=newcmp), ticks=list(EPSS-1) + [EPSS[-1]+1], shrink = 0.3, anchor=(0.0,0.75),label='epsilon')
    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=newcmp),
        ticks=(list(EPSS-0.25) + [EPSS[-1]+0.25])[0:-1:2] + [EPSS[-1]+0.25],
        shrink = 0.3, anchor=(0.0,0.75),
        label='epsilon')
    ax.set_xlabel('Magnitude')
    ax.set_ylabel('Distance (km)')
    ax.set_zlabel('% Contribution to Hazard')
    ax.set_xlim(XLIM)
    ax.set_ylim(ylim)
    ax.view_init(elev=35,azim=45)
    ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))

    # plt.show()
    
    



def plot_mag_dist_eps(fig, disagg, ylim=None):

    ax = fig.add_subplot(1,1,1,projection='3d')
    if not ylim: ylim = YLIM
    plot_single_mag_dist_eps(fig, ax,disagg, ylim=ylim)


    