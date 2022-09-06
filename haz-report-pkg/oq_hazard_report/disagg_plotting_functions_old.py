import matplotlib.pyplot as plt
import numpy as np
import csv
import io
from collections import namedtuple
from zipfile import ZipFile
from enum import Enum

class TrT(Enum):
    ASC = 'Active Shallow Crust'
    INT = 'Subduction Interface'
    SLAB = 'Subduction Intraslab'


def plot_disagg_trt(csv_archive, ax=None, short_names=False):
    hazard = {}
    with ZipFile(csv_archive) as zipf:
        with io.TextIOWrapper(zipf.open('Mag_Dist_TRT-0_1.csv'), encoding="utf-8") as mag_dist_TRT_file:
            disagg_reader = csv.reader(mag_dist_TRT_file)
            junk = next(disagg_reader)
            header = next(disagg_reader)
            DisaggData = namedtuple("DisaggData", header, rename=True)
            for row in disagg_reader:
                # print(trt,prob)
                disagg_data = DisaggData(*row)
                trt = disagg_data.trt
                prob = disagg_data.rlz0
                if not hazard.get(trt):
                    hazard[trt] = float(prob)
                else:
                    hazard[trt] += float(prob)

    total_hazard = sum(list(hazard.values()))
    for k,v in hazard.items():
        hazard[k] = hazard[k]/total_hazard
    print(hazard)

    if not ax:
        fig, ax = plt.subplots(1,1)
    else:
        fig = None
    haz = list(hazard.values())
    names = list(hazard.keys())
    if short_names:
        names = list(map(lambda x: TrT(x).name,names))
        # names = [TrT(n).name for n in names]
    ax.bar(names,haz)

    return fig, ax


def plot_disagg(mags, dists, rates_int, rates_slab, rates_cru):

    width = 0.1
    depth = 5

    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    fig.set_size_inches(8,8)    
    fig.set_facecolor('white')
    islab = rates_slab>0
    icru = rates_cru>0
    iint = rates_int>0
    ax.bar3d(mags[islab],dists[islab],np.zeros_like(rates_slab[islab]),width,depth,rates_slab[islab],color='tab:blue')
    # ax.bar3d(mags,dists,np.zeros_like(rates_slab),width,depth,rates_slab,color='tab:blue')
    slab_proxy = plt.Rectangle((0, 0), 1, 1, fc='tab:blue')
    ax.bar3d(mags[iint],dists[iint],rates_slab[iint],width,depth,rates_int[iint],color='tab:orange',label='interface')
    # ax.bar3d(mags,dists,rates_slab,width,depth,rates_int,color='tab:orange',label='interface')
    int_proxy = plt.Rectangle((0, 0), 1, 1, fc='tab:orange')
    ax.bar3d(mags[icru],dists[icru],rates_slab[icru]+rates_int[icru],width,depth,rates_cru[icru],color='tab:green',label='crustal')
    # ax.bar3d(mags,dists,rates_slab+rates_int,width,depth,rates_cru,color='tab:green',label='crustal')
    cru_proxy = plt.Rectangle((0, 0), 1, 1, fc='tab:green')
    ax.legend([slab_proxy,int_proxy,cru_proxy],['Slab','Interface','Crustal'])
    ax.set_xlabel('magnitude')
    ax.set_ylabel('distance (km)')

    return fig, ax


def load_DMT_disagg(csv_archive):

    with ZipFile(csv_archive) as zipf:
        with io.TextIOWrapper(zipf.open('Mag_Dist_TRT-0_1.csv'), encoding="utf-8") as mag_dist_TRT_file:
            disagg_reader = csv.reader(mag_dist_TRT_file)
            junk = next(disagg_reader)
            header = next(disagg_reader)
            DisaggData = namedtuple("DisaggData", header, rename=True)
            mags = []
            dists = []
            rates_slab = []
            rates_cru = []
            rates_int = []

            for row in disagg_reader:
                disagg_data = DisaggData(*row)

                mag = float(disagg_data.mag)
                dist = float(disagg_data.dist)
                rate = float(disagg_data.rlz0)
                trt = disagg_data.trt


                if trt == 'Active Shallow Crust':
                    mags.append(mag)
                    dists.append(dist)
                    rates_cru.append(rate)
                elif trt == 'Subduction Interface':
                    rates_int.append(rate)
                elif trt == 'Subduction Intraslab':
                    rates_slab.append(rate)

    mags = np.array(mags)
    dists = np.array(dists)
    rates_int = np.array(rates_int)
    rates_slab = np.array(rates_slab)
    rates_cru = np.array(rates_cru)

    return mags,dists,rates_int,rates_slab,rates_cru


def meshgrid_disaggs(mags,dists,rates_int,rates_slab,rates_cru):

    umags = list(set(mags))
    umags.sort()
    udists = list(set(dists))
    udists.sort()

    nmags = len(umags)
    ndists = len(udists)
    

    Mags = np.empty((ndists,nmags))
    Dists = np.empty((ndists,nmags))
    Rates_int = np.empty((ndists,nmags))
    Rates_slab = np.empty((ndists,nmags))
    Rates_cru = np.empty((ndists,nmags))
    Rates_tot = np.empty((ndists,nmags))

    for col,mag in enumerate(umags):
        for row,dist in enumerate(udists):

            Mags[row,col] = mag
            Dists[row,col] = dist
            ind = (mags==mag) & (dists==dist)
            Rates_int[row,col] = rates_int[ind]
            Rates_cru[row,col] = rates_cru[ind]
            Rates_slab[row,col] = rates_slab[ind]
            Rates_tot[row,col] = rates_int[ind] + rates_cru[ind] + rates_slab[ind]

    return Mags, Dists, Rates_int, Rates_slab, Rates_cru, Rates_tot


def plot_disagg2d(Mags, Dists, Rates_int, Rates_slab, Rates_cru, Rates_tot):

    fig, ax = plt.subplots(2,2)
    fig.set_size_inches(12,12)
    fig.set_facecolor('white')

    titles = np.array( (('Slab','Interface'),('Crustal','Total')) )
    xlim = (5,9)
    ylim = (0,400)
    cmap = 'OrRd'

    m = sum(sum(Rates_tot))
    Rates_int = Rates_int/m
    Rates_slab = Rates_slab/m
    Rates_cru = Rates_cru/m
    Rates_tot = Rates_tot/m
    

    pcm = ax[0,0].pcolormesh(Mags,Dists,Rates_slab,vmin=0,vmax=Rates_tot.max(),shading='auto',cmap=cmap)
    pcm = ax[1,0].pcolormesh(Mags,Dists,Rates_cru,vmin=0,vmax=Rates_tot.max(),shading='auto',cmap=cmap)
    pcm = ax[0,1].pcolormesh(Mags,Dists,Rates_int,vmin=0,vmax=Rates_tot.max(),shading='auto',cmap=cmap)
    pcm = ax[1,1].pcolormesh(Mags,Dists,Rates_tot,vmin=0,vmax=Rates_tot.max(),shading='auto',cmap=cmap)
    fig.colorbar(pcm,ax=ax)

    for a,title in zip(ax.flatten(),titles.flatten()):
        a.set_title(title)
        a.set_xlim(xlim)
        a.set_ylim(ylim)

    return fig, ax

