from dis import dis
import numpy as np
from pathlib import Path
import itertools
import matplotlib.pyplot as plt

MAGS = np.arange(5.25,10,.5)
DISTS = np.arange(5,550,10)
TRTS =  ['Active Shallow Crust', 'Subduction Interface', 'Subduction Intraslab']
AXIS_MAG = 0
AXIS_DIST = 1
AXIS_TRT = 2

CMAP = 'OrRd'
XLIM = (5,10)
YLIM = (0,200)

def assemble_disaggs(disagg):

    nmags = len(MAGS)
    ndists = len(DISTS)
    ntrts = len(TRTS)

    disaggs = np.empty((len(MAGS),len(DISTS),len(TRTS)))
    for i, (imag, idist, itrt) in enumerate(itertools.product(range(nmags), range(ndists), range(ntrts))):
        disaggs[imag,idist,itrt] = disagg[i]

    return disaggs

def plot_trt(fig, ax, disagg):

    disaggs = assemble_disaggs(disagg)
    
    disagg_trt = np.sum(disaggs,axis=(AXIS_MAG,AXIS_DIST))
    ax.bar(TRTS,disagg_trt/sum(disagg_trt)*100)


def plot_mag_dist_2d(fig, ax, disagg):

    disaggs = assemble_disaggs(disagg)

    disagg_md = np.sum(disaggs,axis=AXIS_TRT)
    disagg_md = disagg_md/np.sum(disagg_md) * 100
    x, y = np.meshgrid(MAGS,DISTS)
    pcx = ax.pcolormesh(x,y,disagg_md.transpose(),vmin=0,vmax=np.max(disagg_md),shading='auto',cmap=CMAP)
    fig.colorbar(pcx,label=f'% contribution to hazard')
    ax.set_xlim(XLIM)
    ax.set_ylim(YLIM)
    ax.set_xlabel('Magnitude')
    ax.set_ylabel('Distance (km)')